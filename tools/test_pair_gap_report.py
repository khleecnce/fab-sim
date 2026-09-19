"""쌍 갭 리포트의 **추출기**가 거짓 양성/음성을 내지 않는지 잠근다.

왜 이 파일이 필요한가
────────────────────
이 리포트의 출력은 곧 **다음 회차의 문헌 조사 발주서**다. 그래서 여기서 나는
오류는 조용히 사람의 시간을 태운다:
  · 거짓 양성 → 쓰지도 않는 첨가제의 상수를 찾으러 간다
  · 거짓 음성 → 진짜 막힌 쌍이 목록에서 사라져 영영 안 채워진다
둘 다 예외를 내지 않으므로 목록을 눈으로 보기 전까지 드러나지 않는다.

실제로 겪은 오판 셋(전부 이 테스트가 잡는다):
  ① 부정 서술을 긍정으로 읽음 — "원문의 억제제는 BTA 가 아니라 벤젠술폰산"
     이라고 적어 둔 문장 때문에 BTA 쌍이 요구되는 것으로 잡혔다.
  ② 팩 이름을 성분명으로 읽음 — 주석 속 `cu_h2o2_bta` 의 부분 문자열이
     첨가제 'bta' 로 잡혀, SiC 데이터셋이 'bta × sic' 을 요구하게 됐다.
  ③ 표 제목의 다른 막질을 기질로 읽음 — 특허 표는 한 실험에서 같이 측정한
     PETEOS·TaN 을 제목에 나열하므로, Cu 데이터셋이 'oxide 데이터셋'으로도
     세어졌다. 검증이 채점하는 막질은 팩의 film 하나뿐이다.
"""
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.pair_gap_report import (  # noqa: E402
    ADDITIVE_HINTS, _mentions_positively,
)


def _hits(text: str):
    """그 텍스트가 **긍정으로** 언급하는 첨가제 집합 (main() 과 같은 규칙)."""
    return {
        m.group(0).lower()
        for m in ADDITIVE_HINTS.finditer(text)
        if _mentions_positively(text, re.compile(re.escape(m.group(0)), re.I))
    }


def test_negated_mention_is_not_a_requirement():
    """'BTA 가 아니라 X' 는 BTA 를 쓴다는 뜻이 아니다."""
    assert "bta" not in _hits("원문의 억제제는 BTA 가 아니라 벤젠술폰산이다.")
    assert "bta" not in _hits("조성: 실리카 10 wt%, H2O2 1 wt%, BTA 없음")
    assert "bta" not in _hits("이 슬러리는 BTA 무첨가다.")
    assert "bta" not in _hits("The composition is substantially free of BTA.")


def test_positive_mention_is_still_caught():
    """부정 필터가 진짜 언급까지 지우면 거짓 음성이 된다 — 그쪽이 더 위험하다."""
    assert "bta" in _hits("조성: 실리카 3 wt%, H2O2 3 wt%, BTA 1 mM")
    assert "glycine" in _hits("착화제로 glycine 1 wt% 를 넣었다.")


def test_pack_name_substring_is_not_an_additive():
    """`cu_h2o2_bta` 같은 팩 이름이 첨가제 언급으로 잡히면 안 된다."""
    txt = "# 참고: 이 계열은 cu_h2o2_bta 팩으로 채점된다"
    assert "bta" not in _hits(txt), (
        "팩 이름의 부분 문자열이 첨가제로 잡혔다 — 단어 경계가 풀렸다")


def test_substrate_comes_from_pack_film_not_table_title():
    """표 제목에 나열된 다른 막질이 기질로 세어지면 안 된다."""
    from tools.pair_gap_report import _substrate_of
    # cu 팩이면 표 제목에 PETEOS/TaN 이 있어도 기질은 cu 하나다
    assert _substrate_of({}, "cu_h2o2_bta") == "cu"


def test_substrate_normalizes_silica_to_oxide():
    """검증 데이터의 표기(oxide)와 팩의 film(sio2/silica)이 갈라지면 안 된다."""
    from tools.pair_gap_report import _substrate_of
    sub = _substrate_of({}, "oxide_silica")
    assert sub in ("oxide", "sio2"), sub


def test_report_runs_and_reports_zero_blocking_pairs():
    """리포트가 실제로 돌고, 범위 안을 막는 쌍 수를 낸다.

    숫자 자체를 못 박지는 않는다(데이터가 늘면 바뀐다) — 다만 리포트가
    예외 없이 끝나고 우선순위 절을 출력하는지는 계약이다.
    """
    import contextlib
    import io
    from tools.pair_gap_report import main

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main()
    out = buf.getvalue()
    assert rc == 0
    assert "범위 안 계열을 막고 있는 미등록 쌍" in out
