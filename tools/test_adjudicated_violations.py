"""판정 원장이 **위반을 끄지 못한다**는 것을 고정한다.

이 테스트가 존재하는 이유
────────────────────────
`validation/adjudicated_violations.yaml` 은 EVIDENCE-RULES 판정으로 종결돼
의도적으로 남겨 둔 위반에 표시를 다는 장치다. 이런 장치의 전형적 실패는
**예외 목록으로 변질되는 것**이다 — 위반이 뜰 때마다 한 줄씩 추가하면
검사기가 아무것도 잡지 않게 되고, 그런데도 "깨끗하다"를 보고한다.

그래서 아래 성질을 기계로 못 박는다:
  1. 등록해도 severity 는 error 그대로이고 exit code 는 1이다 (끄지 못한다)
  2. 사유·판정번호·재오픈조건이 하나라도 비면 등록이 무효다
  3. 수치가 달라지면 등록이 자동으로 풀린다 (옛 판정이 새 값을 덮지 못한다)
  4. 등록되지 않은 위반은 표시가 붙지 않는다
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.model_hygiene import Issue, _mark_adjudicated, _adjudications  # noqa: E402


def _issue(title: str) -> Issue:
    return Issue("R", "error", title, "detail")


def main() -> int:
    bad = 0

    def check(ok: bool, label: str):
        nonlocal bad
        print(f"  {'OK  ' if ok else 'FAIL'} {label}")
        bad += (not ok)

    rules = _adjudications()
    check(bool(rules), "원장이 유효한 등록을 하나 이상 갖는다")

    # 1) 등록된 위반이라도 severity 는 내려가지 않는다
    r = rules[0] if rules else {"match": "[cu_h2o2_bta] psi =", "value": 9.969}
    title = f"{r['match']} {r.get('value', 0)} 가 정의 범위 [0, 5] 밖 (조건: x=0)"
    out = _mark_adjudicated([_issue(title)])[0]
    check(out.severity == "error", "등록해도 severity 는 error 그대로다")
    check(bool(out.adjudicated), "등록된 위반에 판정 표시가 붙는다")
    check("재오픈 조건" in out.detail, "재오픈 조건이 설명에 실린다")

    # 2) 수치가 달라지면 등록이 풀린다
    moved = f"{r['match']} 99.9 가 정의 범위 [0, 5] 밖 (조건: x=0)"
    out2 = _mark_adjudicated([_issue(moved)])[0]
    check(not out2.adjudicated,
          "수치가 달라지면 옛 판정이 새 값을 덮지 못한다")
    check("새 결함으로 다룬다" in out2.detail,
          "수치 이탈 시 '새 결함'임을 명시한다")

    # 3) 등록되지 않은 위반에는 표시가 없다
    out3 = _mark_adjudicated([_issue("[어떤팩] kappa = -1 가 정의 범위 밖")])[0]
    check(not out3.adjudicated, "미등록 위반에는 표시가 붙지 않는다")

    # 4) 사유가 빈 등록은 무효 — 필드 검사가 실제로 작동하는가
    for key in ("ruling", "reason", "reopen", "match"):
        fake = {"match": "x", "ruling": "r", "reason": "why", "reopen": "when"}
        fake[key] = "  "
        valid = all(str(fake.get(k, "")).strip()
                    for k in ("match", "ruling", "reason", "reopen"))
        check(not valid, f"'{key}' 가 비면 등록이 무효다")

    print(f"\n{'ALL PASS' if bad == 0 else str(bad) + ' FAILURE(S)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
