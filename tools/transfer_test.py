"""처음 보는 계열의 절대 MRR 을 맞출 수 있는가 — Leave-One-Series-Out.

왜 학습곡선으로는 답이 안 되는가
────────────────────────────────
tools/calibration_curve.py 의 "5점 투입 → 14.8%" 는 **그 계열에서 뽑은 5점**으로
그 계열의 나머지를 맞춘 값이다. 증명하는 것은 "고객이 자기 장비 데이터를 주면
그 장비에 맞춰진다"까지다.

"데이터를 많이 넣으면 예측하는 모델인가"는 다른 질문이다. 그렇다면
**그 계열 데이터가 0점일 때** 맞아야 한다. 안 그러면 새 조성마다 먼저 실험을
해야 하고, 그것은 예측이 아니라 사후 보정이다.

측정 방법
─────────
계열 하나를 완전히 빼고 **나머지 전 계열로만** 축척을 학습한 뒤 빼놓은 계열의
절대 MRR 을 예측한다. 그 계열 데이터는 한 점도 쓰지 않는다.

  H0 전이 없음  : 축척 1.0 (물리 그대로)
  H1 전역 상수  : 다른 계열들의 배율 기하평균 하나
  H2 조건부     : 같은 팩(재료계)의 배율만 평균

H1/H2 가 H0 보다 크게 낫고 오차가 실용 수준(≤30%)이면 "데이터를 넣으면
예측된다". 셋이 비슷하거나 전부 크면 **축척은 전이되지 않는다** — 그때는
절대값 예측이 계열별 실측을 요구한다는 뜻이고, 정직하게 그렇게 말해야 한다.

⚠ 결과가 나쁘게 나와도 기준을 낮추지 마라. 이 시험의 목적은 제품이 무엇을
  할 수 있고 무엇을 못 하는지 **말할 수 있게** 하는 것이다.
"""
import pathlib
import sys
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                     # noqa: E402
from validation.backtest import run_all                # noqa: E402


def main() -> int:
    rows = []
    for r in run_all():
        p = np.asarray(r.predicted, dtype=float)
        o = np.asarray(r.observed, dtype=float)
        m = np.isfinite(p) & np.isfinite(o) & (p > 0) & (o > 0)
        if m.sum() < 3 or not getattr(r, "in_scope", True):
            continue
        rows.append((r.dataset, getattr(r, "pack", ""), p[m], o[m]))

    if not rows:
        print("범위 안 계열이 없다")
        return 1

    print("=" * 88)
    print("처음 보는 계열의 절대 MRR 예측 — Leave-One-Series-Out")
    print("=" * 88)
    print("⚠ 빼놓은 계열의 데이터는 **한 점도** 쓰지 않는다.")
    print()

    logscale = {name: float(np.mean(np.log(o / p))) for name, pack, p, o in rows}
    packof = {name: pack for name, pack, _, _ in rows}

    print(f"{'계열':44s} {'H0 물리':>9s} {'H1 전역':>9s} {'H2 동일팩':>9s}")
    agg = defaultdict(list)
    for name, pack, p, o in rows:
        others = {k: v for k, v in logscale.items() if k != name}
        same = {k: v for k, v in others.items() if packof.get(k) == pack}

        def err(s_log: float) -> float:
            return float(np.mean(np.abs(p * np.exp(s_log) - o) / o) * 100)

        e0 = err(0.0)
        e1 = err(float(np.mean(list(others.values())))) if others else float("nan")
        e2 = err(float(np.mean(list(same.values())))) if same else float("nan")
        agg["H0"].append(e0)
        for k, v in (("H1", e1), ("H2", e2)):
            if np.isfinite(v):
                agg[k].append(v)
        f = lambda x: f"{x:8.0f}%" if np.isfinite(x) else "       -"  # noqa: E731
        print(f"{name[:44]:44s} {f(e0)} {f(e1)} {f(e2)}")

    print()
    print("-" * 88)
    print("중앙값 (평균은 극단값에 끌려가므로 중앙값으로 본다)")
    for k in ("H0", "H1", "H2"):
        if agg[k]:
            n_ok = sum(1 for x in agg[k] if x <= 30)
            print(f"  {k}: 중앙 {np.median(agg[k]):7.0f}%   "
                  f"(±30% 이내 {n_ok}/{len(agg[k])}개)")

    cands = [np.median(agg[k]) for k in ("H0", "H1", "H2") if agg[k]]
    best = min(cands)
    print()
    print("=" * 88)
    print("판정")
    print()
    print(f"  처음 보는 계열에서 절대 MRR 오차 중앙값 = {best:.0f}%")
    print()
    if best <= 30:
        print("  ✅ 전이된다 — 데이터를 모으면 새 계열도 절대값 예측이 된다.")
    else:
        print("  ❌ 전이되지 않는다 — 축척이 계열마다 독립이다.")
        print("     데이터를 더 넣는 것으로는 **처음 보는 조성의 절대값**을 못 맞춘다.")
        print()
        print("  ⚠ 그러나 '장비 차이라서 어쩔 수 없다'로 닫지 마라. 같은 재료계 안에서")
        print("    실측이 수십~수백 배 갈리면 그것은 장비가 아니라 **조성이 만든 차이**이고,")
        print("    모델이 설명해야 할 대상이다. 어느 화학 항이 비어 있는지 확인하라")
        print("    (tools/pair_gap_report.py).")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
