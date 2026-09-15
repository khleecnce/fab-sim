"""죽은 축 수리 결과 확인 — 입력을 바꾸면 실제로 반응하는가."""
import sys
import pathlib
import warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent  # tools/ 의 부모
sys.path.insert(0, str(ROOT))

import numpy as np
from sim.engine import Recipe, simulate
import sim.models  # noqa: F401


def m(pack, ov):
    r = simulate(Recipe(pack=pack, pack_overrides=ov),
                 model="tier2.gw_physical_kp")
    return float(np.mean(np.asarray(r.mrr_nm_per_min, dtype=float)))


print("수리 후 반응 확인 (값이 서로 달라야 정상)")
a = [round(m("cu_h2o2_bta", {"abrasive_size_nm": d}), 3)
     for d in (50.0, 100.0, 200.0)]
b = [round(m("oxide_silica", {"oxidizer_wt_pct": c}), 3)
     for c in (0.0, 3.0, 6.0)]
c_ = [round(m("sic_ceria_h2o2", {"oxidizer_wt_pct": c}), 3)
      for c in (0.0, 3.0, 6.0)]
print(f"  ① cu 입경 50/100/200nm : {a}  {'✅' if len(set(a))>1 else '❌ 여전히 죽음'}")
print(f"  ② oxide 산화제 0/3/6   : {b}  {'✅' if len(set(b))>1 else '⚠ 불변(기준 0 이면 정상)'}")
print(f"  ③ sic 산화제 0/3/6     : {c_}  {'✅' if len(set(c_))>1 else '❌ 여전히 죽음'}")

print()
print("기준 배수 (1.000000 이어야 Kp 이중계상 없음)")
bad = 0
for p in ["oxide_silica", "sti_ceria", "cu_h2o2_bta",
          "w_fe_oxidizer", "sic_ceria_h2o2"]:
    r = simulate(Recipe(pack=p))
    mm = 1.0
    for k, f in r.factors.items():
        if f.mrr_coupled and f.value is not None:
            mm *= f.value
    ok = abs(mm - 1.0) < 1e-6
    bad += 0 if ok else 1
    print(f"  {p:16s} {mm:.6f}  {'✅' if ok else '🔴'}")
sys.exit(1 if bad else 0)
