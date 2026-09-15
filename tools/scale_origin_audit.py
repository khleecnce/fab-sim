"""전이가 안 되는 남은 이유를 **계열 배율의 분해**로 찾는다.

왜 이 진단인가
─────────────
알칼리 항을 넣어 순위(ρ=+1.000)는 맞췄는데 전이 오차는 80% 그대로다.
순위가 맞는데 절대값이 안 맞는다는 것은 **각 계열의 배율이 서로 다르다**는
뜻이고, 그 배율이 무엇으로 설명되는지가 남은 질문이다.

배율이 갈리는 원인은 세 가지뿐이다:
  (a) 장비·측정계 차이     → 모델이 설명할 수 없다(Kp 는 원래 그 계의 값)
  (b) 모델이 안 보는 조성축 → **모델이 설명해야 한다**
  (c) 단위·전사 오류        → 데이터를 고쳐야 한다

(a)면 전이는 원리적으로 불가능하고 제품 포지션을 그렇게 말해야 한다.
(b)면 아직 할 일이 있다. 둘을 가르려면 **같은 장비**로 측정된 계열들끼리
배율이 모이는지 보면 된다.

판정: 같은 공정조건(압력·rpm·유량)을 쓰는 계열끼리 배율이 모이면 (b)다.
      같은 장비인데도 흩어지면 (a)이거나 아직 못 본 조성축이 있다.
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
        conds = getattr(r, "rows", []) or []
        # 공정조건 지문 — 장비가 같으면 대개 같다
        def med(key):
            vals = []
            for c in conds:
                f = dict(c)
                ov = f.get("overrides")
                if isinstance(ov, dict):
                    f.update(ov)
                v = f.get(key)
                if isinstance(v, (int, float)):
                    vals.append(float(v))
            return float(np.median(vals)) if vals else None

        rows.append({
            "name": r.dataset,
            "pack": getattr(r, "pack", ""),
            "scale": float(np.exp(np.mean(np.log(o[m] / p[m])))),
            "psi": med("pressure_psi"),
            "rpm": med("rpm_platen"),
            "sfr": med("sfr_ml_min"),
            "n": int(m.sum()),
        })

    print("=" * 96)
    print("계열 배율의 정체 — 장비 차이인가, 모델이 못 본 조성축인가")
    print("=" * 96)
    print(f"{'계열':42s} {'배율':>10s} {'psi':>5s} {'rpm':>5s} {'sfr':>6s} {'팩':16s}")
    for r in sorted(rows, key=lambda x: x["scale"]):
        f = lambda v, w, d=1: (f"{v:{w}.{d}f}" if v is not None else " " * w)  # noqa: E731
        print(f"{r['name'][:42]:42s} {r['scale']:10.4g} "
              f"{f(r['psi'],5)} {f(r['rpm'],5,0)} {f(r['sfr'],6,0)} {r['pack'][:16]:16s}")

    print()
    print("-" * 96)
    print("① 팩(재료계)별 배율 산포 — 같은 재료계 안에서도 갈리는가")
    bypack = defaultdict(list)
    for r in rows:
        bypack[r["pack"]].append(r["scale"])
    for pk, vals in sorted(bypack.items()):
        if len(vals) < 2:
            print(f"  {pk:18s} n=1  (비교 불가)")
            continue
        spread = max(vals) / min(vals)
        print(f"  {pk:18s} n={len(vals)}  배율 {min(vals):.3g} ~ {max(vals):.3g}  "
              f"**산포 {spread:.0f}배**")

    print()
    print("-" * 96)
    print("② 공정조건이 배율을 설명하는가 (로그 상관)")
    for key in ("psi", "rpm", "sfr"):
        pairs = [(r[key], r["scale"]) for r in rows if r[key] and r["scale"] > 0]
        if len(pairs) < 4:
            print(f"  {key}: 표본 부족")
            continue
        x = np.log([p[0] for p in pairs])
        y = np.log([p[1] for p in pairs])
        c = float(np.corrcoef(x, y)[0, 1])
        print(f"  {key}: 로그상관 {c:+.3f}  (n={len(pairs)})")

    print()
    print("=" * 96)
    spreads = {pk: max(v) / min(v) for pk, v in bypack.items() if len(v) > 1}
    worst = max(spreads.values()) if spreads else float("nan")
    print(f"""판정 근거

  같은 재료계 안에서 배율이 최대 **{worst:.0f}배** 흩어진다.

  이 폭이 장비 차이로 설명되려면 공정조건과 상관이 있어야 하는데
  위 ②가 그것을 보여준다. 상관이 약하면 남은 것은
  **모델이 아직 안 보는 조성축**이고, 그것이 다음 작업 대상이다.

  ⚠ 여기서 배율을 계열별 상수로 흡수하면 안 된다 — 그 상수는 물리가
    아니라 그 데이터셋의 지문이 되고, 처음 보는 조성에서 쓸 수 없다.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
