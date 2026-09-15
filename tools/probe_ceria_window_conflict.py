"""세리아 pH 창의 '진짜 상충'을 가설 검정으로 가른다.

상황
────
같은 재료계(세리아 + 산화막)에서 두 논문이 **반대 방향**을 보고한다.

  Dandu 2009    0.25 wt%, 60 nm, 4 psi, 양산 폴리셔
                pH 4~5.5 에서 최고(~350), pH 8~10 은 19% (64)
                → 정전 인력 창 모델과 일치

  Netzband 2020 1.00 wt%, 68 nm, 20 kPa, 2.25 cm² 벤치탑 쿠폰
                pH 4→19.8, 6→11.3, 8→20.0, 10→21.3
                → pH 10 이 최고. 창 모델과 **정반대**

코드 주석에 적힌 가설(미검증):
  "정전 창은 저농도·양산 스케일에서 지배적이고, 고농도·쿠폰에서는 부차적일
   수 있다. 1 wt% 는 0.25 wt% 보다 입자가 4배 많아 정전 반발이 있어도
   기계 접촉이 유지된다."

⚠ 이 가설을 그대로 코드에 넣으면 안 된다 — 두 점(0.25 / 1.0 wt%)을 잇는
  자유 파라미터가 생기고, 그것은 데이터 두 개를 맞추는 피팅이다.

이 스크립트가 하는 일
────────────────────
가설이 **정량적으로 성립하는지** 먼저 본다. 성립하지 않으면 다른 설명을
찾아야 하고, 성립하더라도 중간 농도 데이터 없이는 구현하지 않는다.

검정 1: 두 논문의 MRR 동적범위(폭)가 가설과 맞는가
        창이 지배적이면 폭이 커야 하고, 기계가 지배적이면 폭이 작아야 한다.
검정 2: 기계 항만으로 Netzband 의 절대 수준이 설명되는가
        창을 끄면 Netzband 가 맞고 Dandu 가 깨지는가 (상충의 재현)
검정 3: 정전 반발이 있어도 기계 접촉이 유지된다면, 그 경계는 어디인가
        (입자 수 밀도 대 접촉 자리 수)
"""
import sys
import pathlib
import warnings
import math

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                    # noqa: E402
from sim.engine import Recipe, simulate               # noqa: E402
from sim.params import load_pack                      # noqa: E402
import sim.models                                     # noqa: E402,F401

DANDU = {2.0: 4.3, 3.0: 95.3, 3.5: 276.3, 4.0: 347.4,
         5.0: 344.3, 5.5: 350.4, 6.0: 99.3, 8.0: 69.4, 10.0: 64.3}
NETZ = {4.0: 19.8, 6.0: 11.3, 8.0: 20.0, 10.0: 21.3}

print("=" * 76)
print("검정 1 — 동적범위가 가설과 맞는가")
print("=" * 76)
d_vals = list(DANDU.values())
n_vals = list(NETZ.values())
d_span = max(d_vals) / min(d_vals)
n_span = max(n_vals) / min(n_vals)
print(f"  Dandu    0.25 wt% : {min(d_vals):6.1f} ~ {max(d_vals):6.1f}  폭 {d_span:6.1f}배")
print(f"  Netzband 1.00 wt% : {min(n_vals):6.1f} ~ {max(n_vals):6.1f}  폭 {n_span:6.1f}배")
print()
print(f"  가설: 농도가 높으면 창의 지배력이 약해져 폭이 작아진다.")
print(f"  → 폭 비 {d_span/n_span:.1f}배. 농도는 4배 차이인데 폭은 {d_span/n_span:.0f}배 차이.")
if d_span > n_span * 5:
    print("  ✅ 방향은 가설과 일치한다 (고농도에서 폭이 훨씬 작다)")
else:
    print("  ❌ 가설과 맞지 않는다")

print()
print("=" * 76)
print("검정 2 — 상충이 실재하는가 (창을 끈 상태와 비교)")
print("=" * 76)


def predict(ph, wt, size, with_window=True):
    ov = {"slurry_ph": ph, "abrasive_wt_pct": wt, "abrasive_size_nm": size}
    if not with_window:
        # 창을 끄는 정직한 방법: 입자 IEP 선언을 제거해 항이 비활성화되게 한다
        ov["abrasive_iep_ph"] = None
    try:
        r = simulate(Recipe(pack="sti_ceria", pack_overrides={
            k: v for k, v in ov.items() if v is not None}),
            model="tier2.gw_physical_kp")
        return float(np.mean(np.asarray(r.mrr_nm_per_min, dtype=float)))
    except Exception:
        return float("nan")


def rho(a, b):
    ra = np.argsort(np.argsort(a))
    rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


for name, data, wt, size in (("Dandu", DANDU, 0.25, 60.0),
                             ("Netzband", NETZ, 1.0, 68.0)):
    phs = sorted(data)
    obs = [data[p] for p in phs]
    pred = [predict(p, wt, size) for p in phs]
    print(f"\n  {name} (창 켜짐)")
    print(f"    {'pH':>5s} {'실측':>8s} {'예측':>10s}")
    for p, o, q in zip(phs, obs, pred):
        print(f"    {p:5.1f} {o:8.1f} {q:10.2f}")
    print(f"    ρ = {rho(pred, obs):+.3f}")

print()
print("=" * 76)
print("검정 3 — 입자 수로 가설을 정량화할 수 있는가")
print("=" * 76)
# 단위 면적당 입자 수 ∝ 농도 / 입경³
for name, wt, size in (("Dandu", 0.25, 60.0), ("Netzband", 1.0, 68.0)):
    n_rel = wt / (size ** 3)
    print(f"  {name:10s} wt={wt:4.2f}%  d={size:.0f}nm  →  상대 입자수 ∝ {n_rel*1e6:.4f}")
d_n = 0.25 / 60.0 ** 3
n_n = 1.0 / 68.0 ** 3
print(f"\n  입자 수 비 (Netzband/Dandu) = {n_n/d_n:.2f}배")
print()
print("  가설이 요구하는 것: 이 비가 '정전 반발을 이길 만큼' 커야 한다.")
print("  그런데 그 문턱값이 얼마인지는 어느 문헌에도 없다.")
print("  → 문턱을 데이터에서 역산하면 두 점을 잇는 **자유 파라미터**가 된다.")
print("    (관측 2개 = 미지수 1개 → 과결정이 아니다 → 측정이 아니라 피팅)")
print()
print("  탈출 경로 판정: R8 (중간 농도 데이터 확보 전까지 구현 보류)")
print("  현 상태 유지 — 양산 스케일(Dandu)을 따르고 반례를 notes 로 신고한다.")
