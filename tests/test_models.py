"""등록 모델 계약 검증 — 물리 재정의가 아니라 '엔진에 제대로 붙었나'를 본다."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sim.models  # noqa: F401  (등록 부작용)
from sim.engine import Recipe, simulate, available_models

MODELS = ["tier1.preston_radial", "tier2.gw_physical_kp",
          "tier2.wear_aware", "tier1.pattern_density"]


def test_all_models_registered():
    for m in MODELS:
        assert m in available_models(), f"{m} 미등록 — models.py register_all 확인"


@pytest.mark.parametrize("model", MODELS)
def test_model_runs_and_shapes(model):
    r = Recipe(n_points=41, time_s=60)
    res = simulate(r, model=model)
    assert res.mrr_nm_per_min.shape == (41,)
    assert np.all(np.isfinite(res.mrr_nm_per_min))
    assert np.all(res.mrr_nm_per_min > 0), "MRR이 음수/0 — 물리적으로 불가"
    assert res.model == model


@pytest.mark.parametrize("model", MODELS)
def test_pressure_monotonic(model):
    """압력이 오르면 MRR도 오른다 (Preston 계열 공통 성질)."""
    lo = simulate(Recipe(pressure_psi=2.0), model=model).metrics.mean_nm
    hi = simulate(Recipe(pressure_psi=4.0), model=model).metrics.mean_nm
    assert hi > lo, f"{model}: 압력↑인데 MRR이 안 올랐다 ({lo:.1f} → {hi:.1f})"


def test_gw_and_preston_converge():
    """GW 물리 모델과 Preston 상수 모델이 같은 자릿수로 수렴해야 한다.

    근거: knowledge/materials/gw-nominal-vs-local-pressure — 서로 다른 미시가정
    (선형 P vs GW n(P))에서 출발해도 예측이 수렴하는 것이 pad-mechanic Lv3-2의
    핵심 주장이다. 이 테스트가 그 주장의 회귀 방어선이다.
    """
    r = Recipe(pressure_psi=3.0)
    p = simulate(r, model="tier1.preston_radial").metrics.mean_nm
    g = simulate(r, model="tier2.gw_physical_kp").metrics.mean_nm
    rel = abs(g - p) / p
    assert rel < 0.10, f"GW와 Preston이 {rel*100:.1f}% 벌어짐 — 5% 이내여야 한다 ({p:.1f} vs {g:.1f})"


def test_ptw_pattern_raises_mrr():
    """PTW: 패턴 밀도가 낮을수록 up-area 압력이 올라 MRR 증가."""
    dense = simulate(Recipe(wafer="PTW", meta={"pattern_density": "1.0"}),
                     model="tier1.pattern_density").metrics.mean_nm
    sparse = simulate(Recipe(wafer="PTW", meta={"pattern_density": "0.3"}),
                      model="tier1.pattern_density").metrics.mean_nm
    assert sparse > dense * 2, "ρ=0.3이면 ρ=1.0의 약 3.3배여야 한다"


def test_ptw_model_ignores_npw():
    """NPW에 패턴 모델을 써도 패턴 효과가 적용되면 안 된다."""
    npw = simulate(Recipe(wafer="NPW", meta={"pattern_density": "0.2"}),
                   model="tier1.pattern_density").metrics.mean_nm
    base = simulate(Recipe(wafer="NPW"), model="tier2.gw_physical_kp").metrics.mean_nm
    assert abs(npw - base) < 1e-6, "NPW인데 패턴 보정이 적용됐다"


def test_pattern_density_clamps_and_warns():
    """ρ가 너무 낮으면 발산 대신 클램프하고 경고한다."""
    res = simulate(Recipe(wafer="PTW", meta={"pattern_density": "0.02"}),
                   model="tier1.pattern_density")
    assert any("클램프" in n for n in res.notes), "저밀도 경고가 없다"
    assert res.metrics.mean_nm < 2000, "1/ρ 발산을 막지 못했다"


def test_wear_model_reports_unresolved_contradiction():
    """패드 마모 모순을 숨기지 않고 보고하는가 (할루시네이션 방지 계약)."""
    res = simulate(Recipe(meta={"pad_hours": "100"}), model="tier2.wear_aware")
    assert any("정반대" in n or "corr=-0.998" in n for n in res.notes), \
        "미해결 모순을 보고하지 않았다 — 모르는 것을 아는 척하면 안 된다"
    base = simulate(Recipe(), model="tier2.gw_physical_kp").metrics.mean_nm
    assert abs(res.metrics.mean_nm - base) < 1e-6, \
        "모순이 미해결인데 시간 보정을 적용했다"


def test_ptw_without_pattern_model_warns():
    """PTW인데 패턴 모델을 안 쓰면 엔진이 경고해야 한다."""
    res = simulate(Recipe(wafer="PTW"), model="tier1.preston_radial")
    assert any("패턴 모델을 쓰지 않았다" in n for n in res.notes)


@pytest.mark.parametrize("model", MODELS)
def test_zone_pressure_applied(model):
    """멀티존 헤드 압력이 실제로 반영되는가 (엣지 존만 올림 → TTV 증가)."""
    flat = simulate(Recipe(n_points=81), model=model).metrics.ttv_nm
    zoned = simulate(Recipe(n_points=81,
                            zone_pressures_psi=[3.0, 3.0, 4.5],
                            zone_edges_norm=[0.5, 0.8, 1.0]),
                     model=model).metrics.ttv_nm
    assert zoned > flat, f"{model}: 존압력을 바꿨는데 TTV가 안 변했다"
