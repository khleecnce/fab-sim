"""이상치 판정 규칙이 **실제로 판정하는지** 고정한다.

이 테스트가 존재하는 이유
────────────────────────
첫 구현에서 251점이 전부 C5("설명 불가")로 떨어졌다. 그것은 "모델 갭이
251개"가 아니라 **규칙이 아무 입력도 못 보고 있다**는 뜻이었다
(BacktestResult 에 pack·rows 가 없었다).

0건 출력은 "검사했고 깨끗하다"와 "검사를 못 했다"를 구분해주지 않는다.
감시기의 침묵이 거짓 안심이 되는 전형적 형태다. 그래서 규칙이
**알려진 케이스를 실제로 잡는지** 테스트로 박아 둔다.
"""
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.outlier_rules import (                      # noqa: E402
    bimodal_scale_split, classify_point,
)


def test_c1_catches_nonpositive_observation():
    """실측 MRR 이 0 이하면 물리적으로 불가능하다 — 제거."""
    v = classify_point(pred=100.0, obs=0.0)
    assert v.code == "C1"
    assert v.removed


def test_c1_catches_broken_prediction_and_says_it_is_a_bug():
    """예측이 0 이하인 것은 이상치가 아니라 버그다.

    이 구분이 중요하다: 데이터를 지우고 넘어가면 계산 경로의 결함이 남는다.
    """
    v = classify_point(pred=0.0, obs=100.0)
    assert v.code == "C1"
    assert any("버그" in n for n in v.notes)


def test_c2_catches_ph_outside_declared_gate():
    """Cu pH 항의 게이트는 산성 가지(2~6)다. pH 10 은 부호가 반대인 가지다.

    실제 데이터(lee2021, pH 10)가 순위는 ρ=+1.000 인데 MAPE 4037% 였다 —
    "방향은 맞고 축척은 근거 없음"의 교과서적 형태다.
    """
    v = classify_point(pred=100.0, obs=20.0,
                       inputs={"slurry_ph": 10.0}, pack="cu_h2o2_bta")
    assert v.code == "C2"
    assert v.removed


def test_c2_does_not_fire_inside_the_gate():
    """게이트 안에서는 발동하지 않아야 한다 — 안 그러면 정상 데이터를 버린다."""
    v = classify_point(pred=100.0, obs=20.0,
                       inputs={"slurry_ph": 4.0}, pack="cu_h2o2_bta")
    assert v.code != "C2"


def test_c2_gate_is_pack_scoped():
    """Cu 게이트를 다른 팩에 적용하면 안 된다 — 산화막은 알칼리에서 정상이다."""
    v = classify_point(pred=100.0, obs=20.0,
                       inputs={"slurry_ph": 10.0}, pack="oxide_silica")
    assert v.code != "C2"


def test_c3_routes_unknown_pair_to_rank_only():
    """재료쌍 상수가 없으면 절대값을 계산할 근거가 없다 — 순위만 유지."""
    v = classify_point(pred=100.0, obs=20.0,
                       note_text="🔴 (nicotinic_acid × cu) 쌍의 ΔG 가 표에 없다.")
    assert v.code == "C3"
    assert v.action == "rank_only"
    assert not v.removed          # 지우지 않는다


def test_c5_is_kept_not_removed():
    """설명할 수 없는 이상치는 **남긴다.**

    제거하면 지표는 오르고 모델은 그대로다. 이 테스트가 그 유혹을 막는다.
    """
    v = classify_point(pred=1000.0, obs=1.0)     # 잔차 극단이지만 사유 없음
    assert v.code == "C5"
    assert v.action == "keep"
    assert not v.removed


def test_residual_size_alone_never_removes():
    """잔차가 크다는 것만으로는 절대 제거되지 않는다.

    크기는 증상이고 원인이 아니다. 잔차 기준 제거를 허용하면
    그 순간 지표가 선별의 결과가 된다.
    """
    for factor in (10.0, 100.0, 10_000.0):
        v = classify_point(pred=1.0 * factor, obs=1.0)
        assert not v.removed, f"잔차 {factor}배가 제거를 유발했다"


def test_bimodal_split_detects_two_scale_groups():
    """배율이 갈리면 분할 후보로 잡는다."""
    pred = [1.0] * 8
    obs = [0.06, 0.063, 0.065, 0.062, 0.35, 0.36, 0.358, 0.355]
    sp = bimodal_scale_split(pred, obs)
    assert sp is not None
    lo, hi, msg = sp
    assert len(lo) == 4 and len(hi) == 4
    assert "갈린다" in msg


def test_bimodal_split_ignores_ordinary_scatter():
    """측정 산포 정도로는 분할하지 않는다 — 안 그러면 모든 계열이 쪼개진다."""
    pred = [1.0] * 8
    obs = [0.30, 0.32, 0.29, 0.31, 0.33, 0.30, 0.28, 0.34]
    assert bimodal_scale_split(pred, obs) is None


def test_backtest_result_carries_inputs_for_rule_evaluation():
    """BacktestResult 가 pack·rows 를 들고 있어야 규칙이 판정할 수 있다.

    이 필드가 없어 규칙이 전부 C5 로 떨어진 전례가 있다.
    필드를 되돌리면 이 테스트가 잡는다.
    """
    from validation.backtest import BacktestResult
    f = BacktestResult.__dataclass_fields__
    assert "pack" in f, "pack 이 없으면 게이트 판정(C2)이 불가능하다"
    assert "rows" in f, "rows 가 없으면 조건 입력을 볼 수 없다"
