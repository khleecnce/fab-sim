"""패드 경도 지수가 유도되는 값인가 — 코드에 박힌 −1.5 를 검증한다.

현 상태
──────
sim/factors.py 에 `terms["pad_hardness"] = (h/h_ref) ** (-1.5)` 로
**지수가 리터럴로 박혀** 있다. 같은 유형의 결함을 이미 여러 번 고쳤다:
지수는 고르는 값이 아니라 계산되는 값이다.

−1.5 는 어디서 오는가
────────────────────
GW 접촉에서 실접촉 면적은 A_r ∝ P/H 이다(소성) 또는
A_r ∝ (P/E*)^(2/3)·… (탄성). 제거는 실접촉 면적에 비례하므로
경도 의존은 레짐이 정한다:

    소성 접촉:  A_r ∝ H^-1        → n_H = -1
    탄성 접촉:  A_r ∝ E*^(-2/3)   → n_H = -2/3   (E* 로 표현)

−1.5 는 이 둘 어느 쪽도 아니다. 그리고 우리 5팩은 전부 **탄성**으로
판정돼 있다(χ=1, α=2/3). 그렇다면 −1.5 는 탄성 레짐과 모순이다.

⚠ 더 근본적인 문제: Shore D 는 경도의 **대리지표**이고 압입경도(GPa)와
  비선형 관계다. 코드 주석도 그 사실을 적어 두었다. 그러면
  (Shore D 비)^n 은 (경도 비)^n 이 아니다 — 지수를 아무리 잘 골라도
  물리적으로 옳은 식이 되지 않는다.

이 스크립트는 판정한다:
  ① −1.5 가 어느 레짐에서도 나오지 않는가
  ② 레짐에서 유도한 지수로 바꾸면 무엇이 달라지는가
  ③ Shore D → 압입경도 환산 없이 이 항을 쓸 수 있는가
"""
import sys
import pathlib
import warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                    # noqa: E402
from sim.engine import Recipe, simulate               # noqa: E402
from sim.params import load_pack                      # noqa: E402
from sim.regime_adapter import derive_regime          # noqa: E402
import sim.models                                     # noqa: E402,F401

PACKS = ["oxide_silica", "sti_ceria", "cu_h2o2_bta",
         "w_fe_oxidizer", "sic_ceria_h2o2"]

print("=" * 76)
print("① 각 팩의 접촉 레짐 — 경도 지수는 여기서 나와야 한다")
print("=" * 76)
# ⚠ derive_regime 은 튜플을 돌려준다 — getattr 로 읽으면 전부 None 이 되고
#   "레짐 판정 실패"로 오독한다. exponents_for 가 구조화된 결과를 준다.
from sim.regime_adapter import exponents_for as _exp      # noqa: E402
for p in PACKS:
    pk = load_pack(p)
    try:
        res = _exp(pk, 3.0)
    except Exception as e:                                  # noqa: BLE001
        print(f"  {p:16s} 판정 불가: {type(e).__name__}: {e}")
        continue
    reg = res.get("regime")
    print(f"  {p:16s} α={reg.alpha:.4f}  χ={reg.chi:.4f}  "
          f"n_C={res['n_conc']:+.4f}  ({res['confidence']})")

print()
print("=" * 76)
print("② 레짐에서 유도되는 경도 지수 vs 코드에 박힌 값")
print("=" * 76)
print("""
  GW 접촉에서 제거는 실접촉 면적에 비례한다.
    소성 (α=1.5) : A_r ∝ P/H          → n_H = -1
    탄성 (α=2/3) : A_r ∝ (P/E*)^(2/3) → n_H = -2/3

  코드에 박힌 값 : n_H = -1.5
  → 두 레짐 어느 쪽도 아니다. 우리 5팩은 전부 탄성이므로
    유도값은 -2/3 ≈ -0.667 이어야 한다.
""")

print("=" * 76)
print("③ 지수를 바꾸면 무엇이 달라지는가 (민감도)")
print("=" * 76)


def mrr(pack, ov):
    r = simulate(Recipe(pack=pack, pack_overrides=ov),
                 model="tier2.gw_physical_kp")
    return float(np.mean(np.asarray(r.mrr_nm_per_min, dtype=float)))


pk = load_pack("cu_h2o2_bta")
h0 = float(pk.get("pad_hardness_shore_d"))
print(f"  기준 Shore D = {h0}")
print(f"  {'ShoreD':>8s} {'현재(-1.5)':>12s} {'유도(-2/3)':>12s} {'비':>8s}")
for h in (40.0, 50.0, 60.0, 70.0, 80.0):
    cur = (h / h0) ** (-1.5)
    der = (h / h0) ** (-2.0 / 3.0)
    print(f"  {h:8.0f} {cur:12.4f} {der:12.4f} {cur/der:8.3f}")

print()
print("  Shore D 40→80 (2배) 구간에서")
print(f"    현재 지수: {(80/40)**(-1.5):.4f} 배  (2.83배 차이)")
print(f"    유도 지수: {(80/40)**(-2/3):.4f} 배  (1.59배 차이)")
print()
print("  → 현재 지수는 패드 경도 효과를 **1.8배 과대평가**한다.")
print("    이것이 금속계에서 기계 항이 화학 항을 누르는 원인 중 하나다.")

print()
print("=" * 76)
print("④ 더 근본적인 문제 — 단위가 맞지 않는다")
print("=" * 76)
print("""
  n_H 는 **압입경도 H(GPa)** 에 대한 지수다. 그런데 코드는
  Shore D 비를 그 자리에 넣는다. Shore D ↔ GPa 는 비선형이므로

      (Shore D 비)^n  ≠  (경도 비)^n

  지수를 -2/3 으로 고쳐도 이 불일치는 남는다. 즉 이 항은
  '지수가 틀린 것'이 아니라 **입력 물리량이 틀린 것**이다.

  탈출 경로 판정(sim/unknown_router.py):
    R1 소거    — 불가. 경도는 팩마다 다르므로 약분되지 않는다.
    R6 대응관계 — Shore D → E 환산식이 문헌에 있으나(Qi 2003),
                 코드 주석이 이미 3가지 이유로 신뢰 불가를 적어 두었다.
    R8 측정명세 — 패드 압입경도(GPa) 직접 측정. 나노인덴테이션 표준 절차.

  → R8 이 정직한 답이다. 그때까지 이 항은 '순위 한정'으로 표시해야 한다.
""")
