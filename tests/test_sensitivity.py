"""민감도·기여 분해 계약 테스트.

사용자 지시(2026-09-06): "각 요소를 나눠서 적용... 각각의 요소가 얼마나 performance
기여에 영향을 주는지, 변화시켰을때 어떻게 바뀔건지 예측해"

이 파일이 지키는 것: **민감도 0의 서로 다른 의미가 뒤섞이지 않는가.**
0이 '영향 없음'/'이미 최적'/'모델 한계'/'미구현' 중 무엇인지 구분하지 못하면
사용자가 "이 손잡이는 쓸모없다"고 정반대로 오판한다.
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sim.engine import Recipe, simulate  # noqa: E402
import sim.models  # noqa: E402,F401
from sim.sensitivity import (FACTORS, CANCELLED_BY_CALIBRATION,  # noqa: E402
                             decompose, elasticity, rank_factors)

BY_KEY = {f.key: f for f in FACTORS}
CU = Recipe(pack="cu_h2o2_bta", time_s=60)


# ── 물리 구조가 지수로 재현되는가 ───────────────────────────
def test_preston_pressure_elasticity_is_unity():
    """Preston MRR = Kp·P·V ⟹ 압력 탄성도는 정확히 1.0.

    이건 튜닝 결과가 아니라 물리 구조다. 1이 아니면 모델이 깨진 것이다.
    """
    s = elasticity(CU, BY_KEY["pressure_psi"], metric="mrr")
    assert s is not None
    assert s.elasticity == pytest.approx(1.0, abs=0.02)
    assert s.stable


def test_velocity_elasticity_is_near_unity():
    """속도도 Preston상 선형. 플래튼 회전수가 상대속도를 지배한다."""
    s = elasticity(CU, BY_KEY["rpm_platen"], metric="mrr")
    assert s is not None
    assert 0.8 < s.elasticity < 1.2


# ── 민감도 0의 네 가지 의미 ─────────────────────────────────
def test_optimum_is_not_confused_with_no_effect():
    """산화제가 정점에 앉아 있으면 1차 민감도는 0이지만 '영향 없음'이 아니다.

    회귀 방어: 두 상태가 똑같이 0.000으로 보이는데 의미는 정반대다.
    실제로 산화제가 '미모델링'으로 오진됐었다(2026-09-06).
    """
    # 팩 기본값(3.0)이 곧 정점이라 여기서 재면 1차가 0
    s = elasticity(CU, BY_KEY["oxidizer_wt_pct"], metric="mrr")
    assert s is not None
    assert abs(s.elasticity) < 1e-3
    assert s.curvature < 0, "정점이면 2차 도함수가 음수여야 한다"
    assert s.at_optimum()
    assert "정점" in s.direction()


def test_oxidizer_sensitivity_revives_off_peak():
    """정점을 벗어나면 민감도가 살아나고, 부호가 Kaufman 단봉을 따라야 한다."""
    low = Recipe(pack="cu_h2o2_bta", time_s=60,
                 pack_overrides={"oxidizer_wt_pct": 1.0})
    high = Recipe(pack="cu_h2o2_bta", time_s=60,
                  pack_overrides={"oxidizer_wt_pct": 6.0})
    s_low = elasticity(low, BY_KEY["oxidizer_wt_pct"], metric="mrr")
    s_high = elasticity(high, BY_KEY["oxidizer_wt_pct"], metric="mrr")
    assert s_low.elasticity > 0.1, "정점 아래면 더 넣을수록 좋아야 한다"
    assert s_high.elasticity < -0.1, "정점 위면 더 넣을수록 나빠야 한다"


def test_pad_properties_are_flagged_as_cancelled_not_irrelevant():
    """패드 물성이 0으로 나오는 건 모델 구조 문제이지 '무관'이 아니다.

    GW alpha 역산이 n_contacts 변화를 정확히 상쇄한다(E* 0.5/1/2 GPa에서
    n=6357/3179/1589인데 MRR은 셋 다 99.36으로 동일). 실측 2점이 있어야 풀린다.
    """
    s = elasticity(CU, BY_KEY["pad_E_star_pa"], metric="mrr")
    assert s is not None
    assert abs(s.elasticity) < 1e-6
    assert s.factor.key in CANCELLED_BY_CALIBRATION
    assert s.direction() == "상쇄됨"
    assert "캘리브레이션" in s.note or "실측" in s.note


def test_unmodeled_factors_say_so_explicitly():
    """엔진이 안 쓰는 인자는 그 사실을 명시해야 한다 — 침묵은 거짓말이다."""
    s = elasticity(CU, BY_KEY["abrasive_size_nm"], metric="mrr")
    assert s is not None
    assert s.direction() == "미모델링"
    assert s.note and ("연결" in s.note or "않" in s.note)


# ── 레버리지: 탄성도만으로는 부족하다 ───────────────────────
def test_leverage_accounts_for_practical_range():
    """탄성도가 같아도 조절 가능 폭이 크면 레버리지가 커야 한다.

    압력(1.5~5.0psi)과 플래튼rpm(30~120)은 둘 다 탄성도 ~1.0이지만
    회전수의 조절 폭이 넓어 실무 영향력이 더 크다.
    """
    p = elasticity(CU, BY_KEY["pressure_psi"], metric="mrr")
    v = elasticity(CU, BY_KEY["rpm_platen"], metric="mrr")
    assert p.elasticity == pytest.approx(v.elasticity, abs=0.05), "탄성도는 비슷해야"
    assert v.leverage > p.leverage, "조절 폭이 넓은 쪽이 레버리지가 커야 한다"


def test_ranking_puts_actionable_factors_first():
    """순위 1위는 실제로 돌릴 수 있는 인자여야 한다(레버리지 0이 위로 오면 안 됨)."""
    ranked = rank_factors(CU, metric="mrr")
    assert ranked[0].leverage > 0
    assert ranked[-1].leverage == pytest.approx(0.0, abs=1e-6)


# ── 지표 간 상충 ────────────────────────────────────────────
def test_mrr_and_uniformity_can_disagree():
    """같은 인자가 MRR과 균일도에 반대로 작용할 수 있어야 한다.

    이 상충을 못 보면 "MRR 올리는 법"만 알려주고 고객의 진짜 합격 기준
    (균일도)을 망치는 도구가 된다.
    """
    pairs = []
    for f in FACTORS:
        a = elasticity(CU, f, metric="mrr")
        b = elasticity(CU, f, metric="ttv")
        if a and b and abs(a.elasticity) > 1e-3:
            pairs.append((a.elasticity, b.elasticity))
    assert pairs, "비교할 인자가 없다"
    assert any(x > 0 and y < 0 for x, y in pairs), \
        "MRR↑ + TTV↓ (양쪽 개선) 조합이 하나는 있어야 한다"


# ── 기여 분해 ───────────────────────────────────────────────
def test_decomposition_accounts_for_total_change():
    """요소별 배수의 곱 × 상호작용 잔차 = 전체 변화."""
    mod = Recipe(pack="cu_h2o2_bta", time_s=60, pressure_psi=4.5,
                 pack_overrides={"inhibitor_mM": 0.3})
    contribs, total, _ = decompose(mod)
    assert contribs, "바뀐 인자가 있는데 기여가 비었다"
    prod = 1.0
    for c in contribs:
        prod *= c.factor_x
    assert prod == pytest.approx(total, rel=0.02), \
        f"기여 곱({prod})이 전체 변화({total})와 안 맞는다"


def test_decomposition_separates_domains():
    """기계 변경과 화학 변경이 각각 자기 영역으로 분류돼야 한다."""
    mod = Recipe(pack="cu_h2o2_bta", time_s=60, pressure_psi=4.5,
                 pack_overrides={"inhibitor_mM": 0.3})
    contribs, _, _ = decompose(mod)
    domains = {c.domain for c in contribs}
    assert "mechanical" in domains and "chemical" in domains


def test_pack_override_actually_changes_result():
    """pack_overrides가 실제로 먹혀야 한다.

    회귀 방어: oxidizer_ref_wt_pct가 팩에 없으면 로더가 '현재 농도'로 폴백해
    항상 자기 자신과 비교하게 되고 배수가 영원히 1.0이 된다(실제 발생).
    """
    import numpy as np
    base = float(np.mean(simulate(CU).mrr_nm_per_min))
    off = float(np.mean(simulate(Recipe(
        pack="cu_h2o2_bta", time_s=60,
        pack_overrides={"oxidizer_wt_pct": 9.0})).mrr_nm_per_min))
    assert off != pytest.approx(base, rel=1e-6), \
        "산화제를 3배로 올렸는데 MRR이 그대로다 — override가 안 먹고 있다"
