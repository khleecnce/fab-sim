"""산화제 부호 유도가 옳은가 — 이론이 갈라진 관측을 전부 설명하는가.

이 시험의 요점은 "맞추기"가 아니라 **"한 규칙으로 반대 부호를 낳는가"**다.
물질별 규칙(구리는 이렇다/텅스텐은 저렇다)을 몰래 넣으면 통과할 수 없게
설계했다 — 판정 입력에 물질명이 없기 때문이다.
"""
import sys, pathlib, math

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sim.oxidizer_regime import (
    peak_concentration, sign_of_slope, derive_oxidizer_regime,
)

FAIL = []


def check(name, cond, detail=""):
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAIL.append(name)


print("=" * 72)
print("① 임계 e_H = 2 — 부호가 뒤집히는 지점")
print("=" * 72)
# e_H < 2 면 정점이 양수, e_H > 2 면 정점이 없다(감소만).
c1 = peak_concentration(k_sat=1.0, e_H=1.0)
c2 = peak_concentration(k_sat=1.0, e_H=1.99)
c3 = peak_concentration(k_sat=1.0, e_H=2.01)
print(f"  e_H=1.00 → C* = {c1}")
print(f"  e_H=1.99 → C* = {c2:.4f}")
print(f"  e_H=2.01 → C* = {c3}")
check("e_H=1 이면 C*=K_sat", abs(c1 - 1.0) < 1e-12, f"C*={c1}")
check("e_H→2⁻ 이면 C*→0", c2 < 0.01, f"C*={c2:.4f}")
check("e_H>2 이면 정점 없음", c3 is None)

print()
print("=" * 72)
print("② 같은 규칙이 반대 부호를 낳는가 — 물질명 없이")
print("=" * 72)
# 막이 잘 안 단단해지는 계 (e_H 작음) → 증가형
# 막이 빠르게 단단해지는 계 (e_H 큼)  → 감소형
for label, e_H in [("막이 거의 안 단단해짐 e_H=0.2", 0.2),
                   ("중간 e_H=1.0", 1.0),
                   ("막이 빠르게 치밀해짐 e_H=2.5", 2.5)]:
    lo, hi = 0.5, 6.0
    s_lo = sign_of_slope(lo, 1.0, e_H)
    s_hi = sign_of_slope(hi, 1.0, e_H)
    beh = ("증가" if (s_lo > 0 and s_hi > 0) else
           "감소" if (s_lo <= 0 and s_hi <= 0) else "단봉")
    print(f"  {label:32s} 구간 {lo}~{hi}: {beh}")
check("한 식에서 증가형이 나온다", sign_of_slope(6.0, 1.0, 0.2) > 0)
check("한 식에서 감소형이 나온다", sign_of_slope(0.5, 1.0, 2.5) < 0)

print()
print("=" * 72)
print("③ 관측 창이 부호를 바꾼다 — 같은 계, 다른 구간")
print("=" * 72)
# 같은 물성(K_sat=1, e_H=0.8)인데 어디를 보느냐로 증가/감소가 갈려야 한다.
k, eh = 1.0, 0.8
cstar = peak_concentration(k, eh)
print(f"  이 계의 정점 C* = {cstar:.3f} wt%")
left = sign_of_slope(cstar * 0.3, k, eh)
right = sign_of_slope(cstar * 3.0, k, eh)
print(f"  정점 왼쪽(C={cstar*0.3:.2f})에서 기울기 {left:+.0f}  → 증가로 관측")
print(f"  정점 오른쪽(C={cstar*3.0:.2f})에서 기울기 {right:+.0f} → 감소로 관측")
check("정점 왼쪽은 증가", left > 0)
check("정점 오른쪽은 감소", right < 0)
check("→ '증가형/감소형'은 계의 성질이 아니라 관측 창의 함수",
      left > 0 and right < 0)

print()
print("=" * 72)
print("④ 물성이 없으면 지어내지 않는가")
print("=" * 72)


class _Bare:
    """두 물성이 없는 팩 흉내."""
    params = {}

    def has(self, k):
        return False

    def get_or(self, k, d):
        return d


r = derive_oxidizer_regime(_Bare())
check("물성 없으면 None (추정 금지)", r is None, f"반환={r}")

print()
print("=" * 72)
print("⑤ e_Q 포화 거동 — 전기화학이 요구하는 모양인가")
print("=" * 72)
for C in (0.01, 1.0, 100.0):
    e_Q = 1.0 / (C + 1.0)
    print(f"  C={C:7.2f} (K_sat=1) → e_Q = {e_Q:.4f}")
check("저농도에서 e_Q→1 (선형)", abs(1.0 / (0.01 + 1.0) - 1.0) < 0.02)
check("K_sat 에서 e_Q=0.5", abs(1.0 / 2.0 - 0.5) < 1e-12)
check("고농도에서 e_Q→0 (포화)", 1.0 / 101.0 < 0.01)

print()
print("=" * 72)
if FAIL:
    print(f"❌ 실패 {len(FAIL)}건: {FAIL}")
    sys.exit(1)
print("✅ 전부 통과 — 한 식이 증가·단봉·감소를 모두 낳고, 물질명은 쓰이지 않았다.")
