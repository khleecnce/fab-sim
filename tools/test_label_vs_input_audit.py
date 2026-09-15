"""라벨과 전달값의 어긋남이 다시 생기지 않게 고정한다.

이 테스트가 존재하는 이유
────────────────────────
us20110186542a1 에서 H2O2 와 pH 가 **라벨 문자열에만** 있고 overrides 에
없었다. 세 조건이 모델 입장에서 완전히 같은 입력이었고, 같은 입력에 다른
실측값이 오니 배율이 3.5배로 갈렸다.

이 결함이 위험한 이유는 조용하기 때문이다:
  · 모델은 같은 값을 세 번 예측한다 (예외 없음)
  · 검증은 "모델이 그 축을 못 맞춘다"고 읽는다 (원인 오진)
  · 물리를 고치려 들면 있지도 않은 결함을 쫓는다

실제로 이 오진 때문에 산화제 floor 를 문헌 조사하려던 참이었다.
축을 전달하자 ρ 가 +0.961(p=0.000)로 올라 결함이 데이터 쪽이었음이 밝혀졌다.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.label_vs_input_audit import DATASET_DIR, scan   # noqa: E402

# 범위 밖(in_scope: false) 데이터셋은 팩 커버리지 밖이라 축이 전달되지
# 않아도 검증 결론이 바뀌지 않는다. 다만 **범위 안**은 용납하지 않는다.
KNOWN_OUT_OF_SCOPE = {
    "mo2026_double_sided_L16",
    "carbide2023_slurry_composition_L9",
}


def _in_scope(path: pathlib.Path) -> bool:
    import yaml
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return bool(raw.get("in_scope", True))


def test_no_label_only_axis_in_scoped_datasets():
    """범위 안 데이터셋에서 라벨에만 있는 축이 있으면 실패다.

    이 테스트가 잡는 것은 모델 결함이 아니라 **검증의 눈가림**이다.
    축이 전달되지 않으면 그 축의 검증 결과는 무의미하다.
    """
    offenders = []
    for path in sorted(DATASET_DIR.glob("*.yaml")):
        if path.stem in KNOWN_OUT_OF_SCOPE or not _in_scope(path):
            continue
        probs = scan(path)
        if probs:
            offenders.append((path.stem, probs))

    assert not offenders, "라벨에만 있고 모델에 전달되지 않는 축:\n" + "\n".join(
        f"  {name}: {'; '.join(p)}" for name, p in offenders
    )


def test_audit_actually_detects_a_planted_defect():
    """감사기가 침묵하는 것이 '깨끗함'인지 '못 봄'인지 구분한다.

    감사기 자체가 고장나면 위 테스트가 항상 통과한다. 결함을 심어
    실제로 검출되는지 확인한다.
    """
    import tempfile
    import textwrap

    body = textwrap.dedent("""
        source: 합성 데이터 (테스트용)
        in_scope: true
        pack: w_fe_oxidizer
        conditions:
          - label: "H2O2 0%"
            pressure_psi: 3.0
            mrr_nm_per_min: 10.0
            overrides: {sfr_ml_min: 200.0}
          - label: "H2O2 3%"
            pressure_psi: 3.0
            mrr_nm_per_min: 200.0
            overrides: {sfr_ml_min: 200.0}
    """)
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "planted.yaml"
        p.write_text(body, encoding="utf-8")
        probs = scan(p)
    assert probs, "심어 놓은 결함(H2O2 미전달)을 감사기가 놓쳤다"
    assert any("oxidizer_wt_pct" in s for s in probs)


def test_audit_does_not_fire_when_axis_is_passed():
    """정상 데이터셋에서 거짓 경보를 내지 않는다.

    거짓 경보가 나면 이 감사기는 곧 무시당하고, 그러면 없는 것과 같다.
    """
    import tempfile
    import textwrap

    body = textwrap.dedent("""
        source: 합성 데이터 (테스트용)
        in_scope: true
        pack: w_fe_oxidizer
        conditions:
          - label: "H2O2 0%"
            pressure_psi: 3.0
            mrr_nm_per_min: 10.0
            overrides: {oxidizer_wt_pct: 0.0, sfr_ml_min: 200.0}
          - label: "H2O2 3%"
            pressure_psi: 3.0
            mrr_nm_per_min: 200.0
            overrides: {oxidizer_wt_pct: 3.0, sfr_ml_min: 200.0}
    """)
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "clean.yaml"
        p.write_text(body, encoding="utf-8")
        probs = scan(p)
    assert not probs, f"정상 데이터셋에 거짓 경보: {probs}"
