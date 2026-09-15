"""배율이 **조성축**으로 설명되는가 — 공정조건이 아니라면 다음은 조성이다.

앞선 진단(tools/scale_origin_audit.py)의 결과
──────────────────────────────────────────
공정조건과 배율의 로그상관이 전부 ±0.12 이하였다(psi +0.120, rpm -0.095,
sfr +0.065). 즉 **장비 차이로는 설명되지 않는다.**

같은 재료계 안에서 배율이 최대 313배 흩어진다. 그렇다면 남은 후보는
"모델이 이미 보고 있지만 **기준점이 어긋난** 조성축" 또는
"모델이 아직 안 보는 조성축" 둘 중 하나다.

이 도구가 가르는 법
──────────────────
각 계열의 조성 중앙값과 배율의 로그상관을 본다.

  · 상관이 강하다  → 그 축의 **지수나 기준점**이 틀렸다. 모델은 그 축을
                     보고 있는데 반응 크기가 어긋나는 것이다. 고칠 수 있다.
  · 상관이 약하다  → 그 축은 원인이 아니다.

⚠ 상관이 강하다고 그 축의 계수를 데이터에 맞추면 안 된다. 그것은 회귀다.
  상관은 **어디를 들여다볼지** 가리키는 지표일 뿐이고, 고치는 근거는
  그 축의 물리(유도된 지수·문헌 기준점)여야 한다.
"""
import pathlib
import sys
import warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                     # noqa: E402
from validation.backtest import run_all                # noqa: E402

# 모델이 이미 보고 있는 조성축들 (물질명 아님 — 축 이름)
AXES = ["abrasive_wt_pct", "abrasive_size_nm", "oxidizer_wt_pct",
        "slurry_ph", "inhibitor_mM", "pressure_psi", "rpm_platen"]


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
    print("배율이 어느 조성축과 연동되는가")
    print("=" * 92)
    print("⚠ 공정조건 상관은 이미 ±0.12 이하로 확인됐다 — 장비 차이가 아니다.")
    print()
    print(f"{'축':22s} {'로그상관':>9s} {'n':>4s}  해석")
    hits = []
    for k in AXES:
        pairs = [(r[k], r["scale"]) for r in rows
                 if r.get(k) and r[k] > 0 and r["scale"] > 0]
        if len(pairs) < 5:
            print(f"{k:22s} {'표본부족':>9s} {len(pairs):4d}")
            continue
        x = np.log([a for a, _ in pairs])
        y = np.log([b for _, b in pairs])
        c = float(np.corrcoef(x, y)[0, 1])
        # 기울기 = 그 축의 '겉보기 지수 오차'
        slope = float(np.polyfit(x, y, 1)[0])
        tag = ("🔴 강함 — 이 축의 지수/기준점을 의심하라" if abs(c) >= 0.6 else
               "🟡 중간" if abs(c) >= 0.4 else "· 약함")
        print(f"{k:22s} {c:+9.3f} {len(pairs):4d}  {tag}  (기울기 {slope:+.2f})")
        if abs(c) >= 0.4:
            hits.append((k, c, slope, len(pairs)))

    print()
    print("-" * 92)
    if hits:
        print("들여다볼 축")
        for k, c, slope, n in sorted(hits, key=lambda x: -abs(x[1])):
            print(f"  · {k}: 상관 {c:+.3f}, 기울기 {slope:+.2f} (n={n})")
            print(f"      → 배율이 이 축에 {'증가' if slope > 0 else '감소'}하며 "
                  f"따라간다. 모델이 그 축을 **과소**{'평가' if slope > 0 else ''}"
                  f"{'평가' if slope < 0 else ''}하고 있을 수 있다.")
        print()
        print("  ⚠ 상관이 강하다고 계수를 데이터에 맞추지 마라 — 그것은 회귀다.")
        print("    상관은 어디를 볼지 가리킬 뿐이고, 고치는 근거는 그 축의")
        print("    물리(유도된 지수·문헌 기준점)여야 한다.")
    else:
        print("어느 조성축도 배율을 설명하지 못한다.")
        print("  → 남은 후보는 **모델이 아직 안 보는 축**이다(첨가제 종류,")
        print("    막질 표면 상태, 패드·컨디셔닝 이력 등).")
        print("  → 이 경우 절대값 전이는 현재 구조로 불가능하며, 제품은")
        print("    '순위 스크리닝 + 계열별 캘리브레이션'으로 정직하게 말해야 한다.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
