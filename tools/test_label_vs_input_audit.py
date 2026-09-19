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

# 구조 검사(라벨 종류 > 고유 입력 종류)가 새로 드러낸 **미모델링 축** 부채.
# ⚠ 이것은 면제가 아니라 **기한 있는 기록**이다. 여기 있는 동안 그 데이터셋의
#   순위·절대값 지표는 구조적으로 달성 불가능하므로 성능 근거로 쓰면 안 된다.
#   해소 경로는 둘뿐이다: ①그 축을 모델에 넣는다 ②그 축이 고정인 부분집합만 남긴다.
#   (us20110165777a1 은 ②로 이미 해소했다 — 계면활성제 0 ppm 4점만 남겼다.)
KNOWN_UNMODELED_LABEL_AXES = {
    # 연마입자 제조사(Nalco/Fuso)와 형상(구형/누에고치형)이 라벨에서 구분되는데
    # 모델에 그 축이 없다. 같은 입경·같은 압력이면 모델은 두 배합을 같게 본다.
    # 형상 인자는 아직 어느 팩에도 없으므로 데이터가 아니라 모델의 갭이다.
    "tw202115224a_cu_abrasive_size_pressure",
    # 벤젠술폰산 농도를 스윕하는데 모델에 그 축이 없다. 이 파일은 채점용이
    # 아니라 **기록용**이며 `validation_use: none` 으로 집계에서 빠져 있다
    # (그 축이 Cu MRR 을 2.4배 움직인다는 1차 증거를 보존한다).
    "us9200180b2_cu_benzenesulfonic_series",
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
        if path.stem in KNOWN_UNMODELED_LABEL_AXES:
            # 미모델링 축 부채는 위에 기록돼 있다. 다만 **그 종류만** 넘어간다 —
            # 같은 파일에서 다른 결함(🔴 이름 있는 축 미전달 등)이 나오면 실패다.
            probs = [p for p in probs if "고유 입력" not in p]
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


def _write(tmpdir, body: str):
    import pathlib as _p
    p = _p.Path(tmpdir) / "x.yaml"
    p.write_text(body, encoding="utf-8")
    return p


def test_declared_exclusion_silences_header_only_mention():
    """같은 논문의 **다른 실험** 축을 헤더에 설명한 것은 결함이 아니다.

    단, 산문이 아니라 `excluded_axes:` 필드 + 사유로 선언했을 때만 면제한다.
    """
    import tempfile
    import textwrap

    body = textwrap.dedent("""
        source: 합성 데이터 (테스트용)
        in_scope: true
        pack: sti_ceria
        excluded_axes:
          oxidizer_wt_pct: 같은 논문의 다른 Figure 변수이고 이 실험 슬러리에는 없다.
        # 헤더 설명: 같은 논문 Fig.1a 는 H2O2 0 wt% ~ 5 wt% 를 다룬다.
        conditions:
          - label: "pH 4"
            pressure_psi: 3.0
            mrr_nm_per_min: 10.0
            overrides: {slurry_ph: 4.0}
          - label: "pH 8"
            pressure_psi: 3.0
            mrr_nm_per_min: 20.0
            overrides: {slurry_ph: 8.0}
    """)
    with tempfile.TemporaryDirectory() as d:
        probs = scan(_write(d, body))
    assert not probs, f"선언된 제외축인데 신고했다: {probs}"


def test_exclusion_cannot_silence_a_varying_label_axis():
    """면제가 진짜 결함까지 덮으면 감사기를 무력화하는 도구가 된다.

    라벨에서 값이 **변하는데** 전달되지 않는 경우(🔴)는 어떤 선언으로도
    면제되지 않아야 한다 — 그 축의 검증 결과가 실제로 무의미해지기 때문이다.
    """
    import tempfile
    import textwrap

    body = textwrap.dedent("""
        source: 합성 데이터 (테스트용)
        in_scope: true
        pack: w_fe_oxidizer
        excluded_axes:
          oxidizer_wt_pct: 면제해 달라는 그럴듯한 사유
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
        probs = scan(_write(d, body))
    assert probs, "라벨에서 변하는 축의 미전달이 선언으로 덮였다 — 면제 범위 초과"
    assert any(s.startswith("🔴") for s in probs)


def test_exclusion_without_reason_is_not_an_exclusion():
    """사유 없는 선언은 면제가 아니다 — 사유를 못 쓰면 면제 대상이 아니다."""
    import tempfile
    import textwrap

    body = textwrap.dedent("""
        source: 합성 데이터 (테스트용)
        in_scope: true
        pack: sti_ceria
        excluded_axes:
          oxidizer_wt_pct: ""
        # 헤더 설명: H2O2 5 wt% 실험도 같은 논문에 있다.
        conditions:
          - label: "pH 4"
            pressure_psi: 3.0
            mrr_nm_per_min: 10.0
            overrides: {slurry_ph: 4.0}
          - label: "pH 8"
            pressure_psi: 3.0
            mrr_nm_per_min: 20.0
            overrides: {slurry_ph: 8.0}
    """)
    with tempfile.TemporaryDirectory() as d:
        probs = scan(_write(d, body))
    assert probs, "빈 사유로도 면제됐다 — 선언만으로 감사기를 끌 수 있다"


# ──────────────────────────────────────────────────────────────
# 구조 검사 — 이름이 등록되지 않은 축도 잡는가
#
# 위의 모든 케이스는 `LABEL_TO_KEY` 에 이름이 있는 축을 다룬다. 그래서 표에
# 없는 새 축(계면활성제·입자 제조사 등)이 라벨에서 변하면 감사기가 0건을
# 돌려주고 '깨끗함'을 보고한다 — 통과가 아니라 **사각지대**다.
# 실측: 계면활성제 0/250/2000 ppm 을 바꾸는 12조건이 모델 입장에서 고유입력
# 7종으로 뭉쳐 ρ=-0.243 이 나왔는데 위 검사 전부가 침묵했다.
# ──────────────────────────────────────────────────────────────

def test_structure_check_catches_an_unnamed_axis():
    """표에 이름이 없는 축의 전달 누락도 잡아야 한다."""
    import tempfile
    import textwrap

    body = textwrap.dedent("""
        source: 합성 데이터 (테스트용)
        in_scope: true
        pack: w_fe_oxidizer
        conditions:
          - label: "H2O2 1 wt%, 계면활성제 0 ppm"
            mrr_nm_per_min: 16.0
            overrides: {oxidizer_wt_pct: 1.0}
          - label: "H2O2 1 wt%, 계면활성제 250 ppm"
            mrr_nm_per_min: 12.1
            overrides: {oxidizer_wt_pct: 1.0}
          - label: "H2O2 3 wt%, 계면활성제 0 ppm"
            mrr_nm_per_min: 15.8
            overrides: {oxidizer_wt_pct: 3.0}
    """)
    with tempfile.TemporaryDirectory() as d:
        probs = scan(_write(d, body))
    assert any("고유 입력" in p for p in probs), (
        f"이름이 등록되지 않은 축의 전달 누락을 놓쳤다: {probs}")


def test_structure_check_ignores_observed_values():
    """관측값이 시그니처에 섞이면 모든 조건이 고유해져 검사가 자기 무력화된다.

    아래 두 조건은 입력이 같고 **관측값만 다르다**. 그래도 잡혀야 한다 —
    안 잡히면 관측값이 시그니처에 들어갔다는 뜻이고, 그 순간 이 검사는
    영원히 0건만 돌려준다(첫 구현이 정확히 이 함정에 빠졌다).
    """
    import tempfile
    import textwrap

    body = textwrap.dedent("""
        source: 합성 데이터 (테스트용)
        in_scope: true
        pack: w_fe_oxidizer
        conditions:
          - label: "배합 A"
            mrr_nm_per_min: 10.0
            overrides: {oxidizer_wt_pct: 1.0}
          - label: "배합 B"
            mrr_nm_per_min: 250.0
            overrides: {oxidizer_wt_pct: 1.0}
    """)
    with tempfile.TemporaryDirectory() as d:
        probs = scan(_write(d, body))
    assert any("고유 입력" in p for p in probs), (
        f"관측값이 시그니처에 섞여 검사가 무력화됐다: {probs}")


def test_structure_check_stays_silent_when_every_label_has_its_own_input():
    """거짓 경보 방지 — 조용해야 할 때 조용한지도 함께 잠근다."""
    import tempfile
    import textwrap

    body = textwrap.dedent("""
        source: 합성 데이터 (테스트용)
        in_scope: true
        pack: w_fe_oxidizer
        conditions:
          - label: "H2O2 1 wt%"
            mrr_nm_per_min: 10.0
            overrides: {oxidizer_wt_pct: 1.0}
          - label: "H2O2 3 wt%"
            mrr_nm_per_min: 20.0
            overrides: {oxidizer_wt_pct: 3.0}
          - label: "H2O2 5 wt%"
            mrr_nm_per_min: 30.0
            overrides: {oxidizer_wt_pct: 5.0}
    """)
    with tempfile.TemporaryDirectory() as d:
        probs = scan(_write(d, body))
    assert not probs, f"정상 데이터셋에 거짓 경보: {probs}"
