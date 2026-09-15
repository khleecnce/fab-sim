"""배율-조성 상관을 **팩 안에서** 다시 본다 — 재료계가 섞이면 대리지표가 잡힌다.

왜 한 단계 더 필요한가
─────────────────────
전 계열을 섞어 보면 slurry_ph 가 배율과 -0.611 로 잡힌다. 그런데 재료계마다
운전 pH 대역이 다르다(금속계는 알칼리, 산화막계는 중성~알칼리, SiC 계는 산성).
따라서 pH 는 **"어느 재료계인가"의 대리지표**일 수 있고, 그러면 pH 항을
고치는 것은 엉뚱한 곳을 고치는 일이다.

가르는 법: **같은 팩 안에서** 상관이 유지되는가.
  · 유지되면 → 그 축이 진짜 원인이다.
  · 사라지면 → 재료계 간 차이였고, 고칠 곳은 그 축이 아니라 팩 분리·
              또는 재료계별로 다른 상수다.

⚠ 팩 안 표본이 3~6개로 작다. 상관값을 유의성으로 읽지 말고 **방향 일치**만
  본다. 여러 팩에서 같은 방향이 반복되면 그것이 신호다.
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

AXES = ["abrasive_wt_pct", "abrasive_size_nm", "oxidizer_wt_pct", "slurry_ph"]


def main() -> int:
    rows = []
    for r in run_all():
        p = np.asarray(r.predicted, dtype=float)
        o = np.asarray(r.observed, dtype=float)
        m = np.isfinite(p) & np.isfinite(o) & (p > 0) & (o > 0)
        if m.sum() < 3 or not getattr(r, "in_scope", True):
            continue
        conds = getattr(r, "rows", []) or []
        rec = {"name": r.dataset, "pack": getattr(r, "pack", ""),
               "scale": float(np.exp(np.mean(np.log(o[m] / p[m]))))}
        for k in AXES:
            vals = []
            for c in conds:
                f = dict(c)
                ov = f.get("overrides")
                if isinstance(ov, dict):
                    f.update(ov)
                v = f.get(k)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    vals.append(float(v))
            rec[k] = float(np.median(vals)) if vals else None
        rows.append(rec)

    print("=" * 92)
    print("팩 안에서도 상관이 유지되는가 — 대리지표 판별")
    print("=" * 92)
    print("⚠ 팩 안 표본이 작다. 상관값이 아니라 **방향 일치**를 본다.")
    print()

    bypack = defaultdict(list)
    for r in rows:
        bypack[r["pack"]].append(r)

    direction = defaultdict(list)
    for pk, items in sorted(bypack.items()):
        if len(items) < 3:
            print(f"■ {pk}  (n={len(items)} — 상관 불가)")
            continue
        print(f"■ {pk}  (n={len(items)})")
        for k in AXES:
            pairs = [(r[k], r["scale"]) for r in items
                     if r.get(k) and r[k] > 0 and r["scale"] > 0]
            if len(pairs) < 3:
                continue
            x = np.log([a for a, _ in pairs])
            y = np.log([b for _, b in pairs])
            if np.std(x) < 1e-9:
                print(f"    {k:20s} 축이 고정 — 상관 불가")
                continue
            c = float(np.corrcoef(x, y)[0, 1])
            direction[k].append(np.sign(c))
            print(f"    {k:20s} {c:+.3f}  (n={len(pairs)})")
        print()

    print("-" * 92)
    print("축별 방향 일치도 (여러 팩에서 같은 부호가 반복되면 신호)")
    for k, signs in sorted(direction.items()):
        if not signs:
            continue
        neg = sum(1 for s in signs if s < 0)
        pos = sum(1 for s in signs if s > 0)
        agree = max(neg, pos) / len(signs)
        tag = ("🔴 일관" if agree >= 0.8 and len(signs) >= 3 else
               "🟡 부분" if agree >= 0.7 else "· 불일치 → 대리지표 의심")
        print(f"  {k:20s} 음 {neg} / 양 {pos} (팩 {len(signs)}개)  {tag}")

    print()
    print("=" * 92)
    print("""해석 규칙

  · 여러 팩에서 **같은 부호**가 반복되면 그 축이 진짜 원인이다
    → 그 축의 지수·기준점을 물리 근거로 재검토한다.
  · 팩마다 부호가 갈리면 전체 상관은 **재료계 차이의 대리지표**였다
    → 고칠 곳은 그 축이 아니라 재료계별 상수(Kp·기준 조성)다.
  · 축이 팩 안에서 고정이면 애초에 그 팩에서는 원인일 수 없다.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
