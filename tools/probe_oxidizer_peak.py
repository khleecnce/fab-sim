"""산화제 실패의 진짜 원인을 가른다.

가설 A: 형태(단봉)가 단조 감소를 못 만든다 → **반증됨**.
        peak 를 0.5~1.0 으로 두면 감소가 나온다.

가설 B: 형태는 되는데 **정점 농도를 계가 아니라 팩이 고정**하고 있다.
        cu_h2o2_bta 의 peak=3.0 은 '착화제가 있을 때' 값이라고 노트에 적혀 있다.
        그런데 검증 데이터셋 두 개는 착화제 조건이 서로 다르다.
        즉 한 팩의 고정 peak 로 두 계를 동시에 맞출 수 없다.

이 스크립트는 B를 검증한다: 데이터셋별로 최적 peak 가 다른가?
다르다면 peak 는 '팩 상수'가 아니라 **조성에서 계산되어야 할 값**이다.
"""
import sys, pathlib, warnings, itertools
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml
import numpy as np
from sim.chemistry import _oxidizer_term
from sim.params import load_pack, Param


def setval(pk, key, val):
    pk.params[key] = Param(key=key, value=val, source="probe", confidence="estimated")


def load_series(name):
    d = yaml.safe_load(open(ROOT / "validation" / "datasets" / f"{name}.yaml"))
    pts = []
    for c in d["conditions"]:
        o = c.get("overrides", {})
        if "oxidizer_wt_pct" in o:
            pts.append((float(o["oxidizer_wt_pct"]), float(c["mrr_nm_per_min"])))
    return d.get("pack"), pts


def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    if len(set(a)) < 2 or len(set(b)) < 2:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


SETS = ["us20110165777a1_cu_h2o2_series", "us9200180b2_cu_h2o2_series",
        "us8070843b2_w_h2o2_series"]

print("=== 데이터셋별로 '가장 잘 맞는 정점 농도'를 따로 찾으면? ===")
print("(peak 를 격자탐색해 순위상관이 최대가 되는 값)\n")
best = {}
for name in SETS:
    pack, pts = load_series(name)
    if len(pts) < 3:
        print(f"{name}: 점 부족({len(pts)})")
        continue
    Cs = [p[0] for p in pts]; Ys = [p[1] for p in pts]
    rows = []
    for peak in np.arange(0.3, 15.01, 0.1):
        pred = []
        ok = True
        for C in Cs:
            pk = load_pack(pack)
            setval(pk, "oxidizer_peak_wt_pct", float(peak))
            setval(pk, "oxidizer_wt_pct", C)
            v = _oxidizer_term(pk, [])
            if v is None:
                ok = False; break
            pred.append(v)
        if not ok:
            continue
        r = spearman(pred, Ys)
        if not np.isnan(r):
            rows.append((r, float(peak)))
    if not rows:
        print(f"{name}: 계산 불가"); continue
    rows.sort(reverse=True)
    top_r, top_peak = rows[0]
    # 현재 팩 값으로는?
    pk = load_pack(pack)
    cur_peak = float(pk.get("oxidizer_peak_wt_pct"))
    pred_cur = []
    for C in Cs:
        p2 = load_pack(pack); setval(p2, "oxidizer_wt_pct", C)
        pred_cur.append(_oxidizer_term(p2, []))
    r_cur = spearman(pred_cur, Ys)
    best[name] = (top_peak, top_r, cur_peak, r_cur)
    trend = "감소" if Ys[0] > Ys[-1] else "증가"
    print(f"{name}")
    print(f"   관측 경향 : {trend}  (C {Cs[0]}→{Cs[-1]}, MRR {Ys[0]:.1f}→{Ys[-1]:.1f})")
    print(f"   현재 peak : {cur_peak:5.2f} → ρ={r_cur:+.3f}")
    print(f"   최적 peak : {top_peak:5.2f} → ρ={top_r:+.3f}")
    print()

print("=" * 70)
if len(best) >= 2:
    peaks = {k: v[0] for k, v in best.items()}
    cu = [v for k, v in peaks.items() if "cu" in k]
    print("데이터셋별 최적 정점 농도:")
    for k, v in peaks.items():
        print(f"   {k[:44]:46s} {v:5.2f} wt%")
    spread = max(peaks.values()) / max(min(peaks.values()), 1e-9)
    print(f"\n최대/최소 비 = {spread:.1f}배")
    if spread > 2.0:
        print("→ 같은 팩(또는 같은 산화제)인데 계마다 정점이 다르다.")
        print("  **peak 는 팩에 적어 넣을 상수가 아니라 조성에서 계산될 값이다.**")
    if len(cu) >= 2 and max(cu) / max(min(cu), 1e-9) > 1.5:
        print(f"\n⚠ 같은 막질(구리)끼리도 최적 peak 가 {min(cu):.2f} vs {max(cu):.2f} 로 갈린다.")
        print("  → 막질만으로도 결정되지 않는다. 첨가제(억제제/착화제)가 정점을 옮긴다.")
