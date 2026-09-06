"""엔진 + 지표 회귀. 물리 재정의 없이 계약(스키마·단조성·정의)만 검증."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.engine import Recipe, simulate, available_models  # noqa: E402
from sim.metrics.uniformity import compute_metrics, compute_metrics_points  # noqa: E402


def test_models_registered():
    assert "tier1.preston_radial" in available_models()


def test_simulate_shapes_and_units():
    r = Recipe(n_points=81, time_s=60)
    res = simulate(r)
    assert res.radius_m.shape == (81,) == res.mrr_nm_per_min.shape == res.removed_nm.shape
    assert np.all(res.mrr_nm_per_min > 0)
    # 60초 = 1분이므로 removed == mrr
    assert np.allclose(res.removed_nm, res.mrr_nm_per_min)
    assert res.remaining_nm is None
    assert res.metrics.n_points == 81


def test_preston_linearity_in_pressure_and_time():
    a = simulate(Recipe(pressure_psi=2.0, time_s=30)).removed_nm
    b = simulate(Recipe(pressure_psi=4.0, time_s=30)).removed_nm
    c = simulate(Recipe(pressure_psi=2.0, time_s=60)).removed_nm
    assert np.allclose(b, 2 * a, rtol=1e-9)
    assert np.allclose(c, 2 * a, rtol=1e-9)


def test_uniform_pressure_gives_low_nonuniformity():
    # 자전 평균으로 운동학 비균일은 작다 (process-integrator 판단: edge/center ≈ 1.004)
    m = simulate(Recipe(edge_pressure_amp=0.0)).metrics
    assert m.cv_pct < 0.5, m.cv_pct


def test_edge_pressure_increases_ttv():
    flat = simulate(Recipe(edge_pressure_amp=0.0)).metrics.ttv_nm
    edge = simulate(Recipe(edge_pressure_amp=0.3)).metrics.ttv_nm
    assert edge > flat * 3


def test_remaining_and_overpolish_note():
    res = simulate(Recipe(initial_thickness_nm=100.0, time_s=60))
    assert res.remaining_nm is not None
    assert any("오버폴리시" in n for n in res.notes)


def test_ptw_and_film_notes_are_honest():
    """모르는 것을 모른다고 말하는지.

    ⚠ 2026-09-06 파라미터 팩 도입으로 이 테스트의 의미가 하나 바뀌었다.
    예전에는 film='cu'로 돌려도 산화막 Kp를 그대로 써서 "막질별 Kp 미분화"라고
    경고했다. 이제는 팩(cu_h2o2_bta)이 Cu Kp를 실제로 갖고 있으므로 그 경고는
    사실이 아니다 — 대신 그 값이 estimated(미재현)라는 경고가 나와야 한다.
    """
    res = simulate(Recipe(pack="cu_h2o2_bta", wafer="PTW"))
    assert res.dishing_nm is None and res.metal_contamination is None
    assert any("PTW" in n for n in res.notes)
    # 막질은 팩이 정한다 — 레시피에 안 써도 cu가 되어야 한다
    assert res.film == "cu"
    # Cu Kp는 문헌 역산(estimated)이므로 정직하게 미검증 경고가 붙어야 한다
    assert any("미검증" in n and "kp_m_per_pa" in n for n in res.notes), res.notes


def test_metric_definitions():
    r = np.linspace(0, 0.147, 81)
    v = np.linspace(500, 520, 81)
    m = compute_metrics(r, v)
    assert m.ttv_nm == pytest.approx(20)
    assert m.cv_pct == pytest.approx(np.std(v) / np.mean(v) * 100)
    assert m.wiwnu_halfrange_pct == pytest.approx(20 / (2 * np.mean(v)) * 100)
    assert len(m.ring_ttv_nm) == 8
    assert m.radial_maxring_range_nm == pytest.approx(max(m.ring_ttv_nm))
    # 문헌 항등식 (uniformity-metrics-definitions-standards.md §2·§3)
    assert m.wiwnu_3sigma_pct == pytest.approx(3 * m.cv_pct)  # US6922603B1: 3σ = 3×1σ
    assert m.cv_pct == pytest.approx(m.sigma_nm / m.mean_nm * 100)  # CV ≡ 1σ WIWNU


def test_points_and_profile_agree():
    th = np.linspace(0, 2 * np.pi, 81, endpoint=False)
    rr = np.linspace(0, 0.147, 81)
    v = np.linspace(500, 520, 81)
    a = compute_metrics(rr, v)
    b = compute_metrics_points(rr * np.cos(th), rr * np.sin(th), v)
    assert a.ttv_nm == pytest.approx(b.ttv_nm) and a.radial_maxring_range_nm == pytest.approx(b.radial_maxring_range_nm)
