"""응답 지도 계약 테스트 — 형상 분류와 판정 규칙이 흔들리지 않게 못 박는다.

여기서 지키는 계약은 셋이다(전부 실제로 틀렸던 적이 있는 지점):
  1. 정점을 단조로 부르면 안 된다 — 소재 개발자에게 틀린 방향을 가리킨다.
  2. 모델과 문헌은 **같은 x 구간**에서 비교해야 한다. 구간이 다르면 가짜 충돌이 난다.
  3. 캘리브레이션 출처·교란(다인자 동시변화) 데이터셋은 판정에서 빠져야 한다.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.response_map import (  # noqa: E402
    classify, verdict_of, literature_evidence, pooled, Evidence,
)


def test_classify_monotonic_and_peak():
    xs = [1, 2, 3, 4, 5, 6, 7]
    assert classify(xs, [1, 2, 3, 4, 5, 6, 7])[0] == "up"
    assert classify(xs, [7, 6, 5, 4, 3, 2, 1])[0] == "down"
    # 정점: 안쪽이 양 끝보다 확실히 높다
    assert classify(xs, [1, 3, 6, 9, 6, 3, 1])[0] == "peak"
    assert classify(xs, [9, 6, 3, 1, 3, 6, 9])[0] == "valley"


def test_classify_flat_is_not_a_direction():
    """무반응은 방향이 아니다 — 'up'으로 새면 미구현 축이 정상으로 보인다."""
    assert classify([1, 2, 3, 4], [5.0, 5.0, 5.0, 5.0])[0] == "flat"
    assert classify([1, 2, 3, 4], [5.0, 5.001, 5.0, 5.002])[0] == "flat"


def test_peak_needs_margin_over_endpoints():
    """안쪽 점이 끝점과 거의 같으면 정점이 아니다 — 노이즈를 정점이라 부르지 않는다."""
    shape, _ = classify([1, 2, 3, 4, 5], [1.0, 1.5, 1.51, 3.0, 5.0])
    assert shape == "up"


def test_verdict_peak_vs_monotonic_is_conflict():
    """가장 위험한 고장: 정점 거동을 단조로 근사 → pH 12.5를 과대평가한다."""
    assert verdict_of("up", "peak") == "CONFLICT"
    assert verdict_of("down", "up") == "CONFLICT"
    assert verdict_of("up", "valley") == "CONFLICT"
    assert verdict_of("peak", "peak") == "AGREE"
    # 포화와 단조 증가는 실무 판단이 같다
    assert verdict_of("saturating", "up") == "AGREE"


def test_verdict_flat_with_literature_is_dead_not_agree():
    assert verdict_of("flat", "up") == "DEAD"
    assert verdict_of("flat", "unknown") == "BLANK"
    assert verdict_of("up", "unknown") == "NO-DATA"


def test_calibration_and_confounded_are_excluded_from_verdict():
    """자기 답안지 채점과 교란 데이터로 '문헌이 확인함'이라 말하면 안 된다."""
    def mk(**kw):
        base = dict(key="slurry_ph", dataset="x", pack="p", n=5, shape="peak",
                    span=2.0, x_lo=1, x_hi=5, xs=[1, 2, 3, 4, 5], ys=[1, 2, 3, 2, 1],
                    confounded=False, n_varying=1, in_scope=True, calib=False,
                    read="table")
        base.update(kw)
        return Evidence(**base)
    assert mk().usable()
    assert not mk(calib=True).usable()
    assert not mk(confounded=True, n_varying=3).usable()
    assert not mk(in_scope=False).usable()
    assert pooled([mk(calib=True)], "slurry_ph", "p") is None


def test_pooling_normalizes_absolute_scale():
    """논문마다 장비·막질이 달라 MRR 절대값이 다르다 — 정규화 없이 풀링하면
    형상이 아니라 논문 간 오프셋을 보게 된다."""
    ev = literature_evidence()
    for e in ev:
        # 각 데이터셋은 자기 중앙값으로 나뉘어 있으므로 중앙값 근처에 1.0이 있다
        assert min(e.ys) <= 1.0 <= max(e.ys) + 1e-9


def test_real_datasets_produce_usable_evidence():
    """실제 데이터셋에서 단독 변화 인자가 하나 이상 잡혀야 한다 —
    전부 교란으로 빠지면 이 도구가 아무것도 판정하지 않는다."""
    ev = literature_evidence()
    assert any(e.usable() for e in ev)
    keys = {e.key for e in ev if e.usable()}
    assert "slurry_ph" in keys


# ── 2026-09-15 판정#42: 교란 탐지가 FACTORS 키만 보던 결함 ────────────────
def test_confound_detection_sees_non_factor_inputs():
    """교란 판정은 '모델이 아는 축'이 아니라 '실험에서 변한 축' 기준이어야 한다.

    US9200180B2 TABLE 3은 실리카 0.5→20 wt%(abrasive_wt_pct — FACTORS에 없는 키)와
    pH 9.2→10.0을 **동시에** 움직인 표다. 이전 구현은 FACTORS 키만 훑어서 pH가
    단독 변화한 것으로 오인했고, 그 결과 cu_h2o2_bta/pH에 존재하지 않는
    DEAD 갭이 4회차 연속 최상위(score 95)로 올라왔다.
    """
    ev = {(e.dataset, e.key): e for e in literature_evidence()}
    e = ev.get(("us9200180b2_cu_abrasive_series", "slurry_ph"))
    assert e is not None
    assert e.confounded, "실리카 농도가 같이 변하는데 단독 증거로 잡혔다"
    assert not e.usable()


def test_quarantined_datasets_are_not_evidence():
    """qa_loop가 격리한 데이터셋이 응답 판정에서만 살아 있으면 안 된다.

    backtest.py는 quarantine.json을 적용하는데 response_map은 안 봤다 —
    같은 데이터가 한 도구에는 부적격, 다른 도구에는 적격이면 랭킹 전체를 못 믿는다.
    """
    import json as _json
    qf = ROOT / "validation" / "quarantine.json"
    if not qf.exists():
        return
    q = set(_json.loads(qf.read_text(encoding="utf-8")).keys())
    if not q:
        return
    for e in literature_evidence():
        if e.dataset in q:
            assert e.quarantined and not e.usable()


def test_full_cross_doe_yields_controlled_strata():
    """완전교차 DOE는 통째로 버리지 말고 '나머지 고정' 층에서 단독 증거를 뽑아야 한다.

    US9499721B2는 실리카 6수준 × 압력 4수준이다. 층(실리카 고정) 안에서 압력은
    단독으로 변하므로 통제된 증거다 — 이전 구현은 이걸 교란으로 버렸다.
    """
    ev = {(e.dataset, e.key): e for e in literature_evidence()}
    e = ev.get(("us9499721b2_teos_colloidal_silica_pressure_conc", "pressure_psi"))
    assert e is not None
    assert not e.confounded and e.usable()
    assert e.shape == "up"
