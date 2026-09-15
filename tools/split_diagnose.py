"""C4(계열 혼재)로 잡힌 계열에서 **무엇이 무리를 가르는가**를 찾는다.

왜 이 단계가 필요한가
────────────────────
"배율이 두 무리로 갈린다"는 증상이다. 그냥 둘로 쪼개면 그것은 데이터 분할이
아니라 **잔차 기준 분할**이고, 곧 피팅이다.

정당한 분할이 되려면 무리를 가르는 것이 **물리적 좌표**여야 한다:
pH 가 갈랐다면 "산성/알칼리에서 다른 메커니즘"이라는 뜻이고, 그건 계열을
갈라야 할 실제 이유가 된다. 아무 좌표와도 안 맞으면 분할하지 않는다.
"""
import sys
import pathlib
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                    # noqa: E402
from validation.backtest import run_all               # noqa: E402
from tools.outlier_rules import bimodal_scale_split   # noqa: E402


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "us20110186542a1"
    rs = [r for r in run_all() if target in r.dataset]
    if not rs:
        print(f"'{target}' 데이터셋을 찾지 못했다")
        return 1
    r = rs[0]

    p = np.asarray(r.predicted, dtype=float)
    o = np.asarray(r.observed, dtype=float)
    rows = getattr(r, "rows", []) or []
    sp = bimodal_scale_split(p, o)
    if sp is None:
        print("이 계열은 bimodal 이 아니다 — 분할 대상 아님")
        return 0
    lo_i, hi_i, msg = sp
    print("=" * 80)
    print(f"{r.dataset}")
    print("=" * 80)
    print(msg)
    print()

    def flat(i: int) -> dict:
        if i >= len(rows) or not isinstance(rows[i], dict):
            return {}
        s = dict(rows[i])
        ov = s.get("overrides")
        if isinstance(ov, dict):
            s.update(ov)
        return s

    # 두 무리를 가르는 좌표를 찾는다 — 완전히 분리되는 변수만 인정한다.
    #
    # ⚠ 출력 변수(실측 MRR 등)는 후보에서 **반드시 제외**한다.
    #   실측값이 무리를 가른다는 것은 동어반복이다: 배율 = 실측/예측 이므로
    #   실측이 크면 배율도 크다. 이것을 "물리 좌표가 갈랐다"로 읽으면
    #   어떤 계열이든 항상 분할 정당으로 판정된다 — 실제로 그렇게 나왔다.
    #   분할을 정당화하는 것은 **입력** 좌표여야 한다.
    OUTPUT_KEYS = {
        "mrr_nm_per_min", "mrr_nm_per_hour", "measured_mrr_nm_per_hour",
        "measured_mrr", "removal_rate", "mrr", "observed",
        "uniformity_pct", "selectivity",
    }

    def _is_output(k: str) -> bool:
        kl = k.lower()
        return (kl in OUTPUT_KEYS
                or "mrr" in kl or "removal_rate" in kl or "measured" in kl)

    keys = set()
    for i in range(len(rows)):
        keys |= {k for k, v in flat(i).items()
                 if isinstance(v, (int, float)) and not isinstance(v, bool)
                 and not _is_output(k)}

    print("무리를 가르는 좌표 후보 (완전 분리만 인정)")
    found = []
    for k in sorted(keys):
        a = [float(flat(i)[k]) for i in lo_i if k in flat(i)]
        b = [float(flat(i)[k]) for i in hi_i if k in flat(i)]
        if not a or not b:
            continue
        if max(a) < min(b) or max(b) < min(a):
            found.append(k)
            print(f"  ✅ {k:24s} 낮은무리={sorted(set(a))}  높은무리={sorted(set(b))}")
    if not found:
        print("  (없음)")

    print()
    print("라벨로 확인")
    for tag, idx in (("낮은 배율 무리", lo_i), ("높은 배율 무리", hi_i)):
        print(f"  {tag}:")
        for i in idx:
            lab = rows[i].get("label", "?") if i < len(rows) else "?"
            print(f"    · {lab}")

    print()
    print("=" * 80)
    if found:
        print(f"""판정: **분할 정당**. {', '.join(found)} 이(가) 두 무리를 완전히 가른다.
  잔차로 자른 것이 아니라 물리 좌표가 자른 것이므로, 이 계열은 서로 다른
  조건의 두 계열로 취급해야 한다.""")
    else:
        print("""판정: **분할 금지**. 어떤 물리 좌표도 두 무리를 가르지 못한다.
  이 상태에서 쪼개면 잔차 기준 분할이고, 그것은 피팅이다.
  남겨서 모델 갭으로 다뤄야 한다.""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
