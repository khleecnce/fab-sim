"""abrasive_mechanics 검증 — 이론이 알려진 지수를 재현하는가.

이 테스트가 확인하는 것은 "우리 데이터에 맞는가"가 아니라
**"3인자 분해가 문헌의 갈라진 답들을 전부 설명하는가"**다.
문헌이 서로 다른 지수를 보고했다면, 각각이 이 지도의 어느 좌표인지
말할 수 있어야 한다. 말할 수 없으면 분해가 틀린 것이다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.abrasive_mechanics import (  # noqa: E402
    ALPHA_ELASTIC, ALPHA_MOLECULAR, ALPHA_PLASTIC, LoadRegime,
    occupancy_exponent, occupancy_ratio, resolve_regime,
)

FAIL = []


def check(name, got, want, tol=1e-6):
    ok = abs(got - want) <= tol
    print(f"  {'✅' if ok else '❌'} {name}: {got:+.4f} (기대 {want:+.4f})")
    if not ok:
        FAIL.append(name)


print("① 3인자 분해가 문헌의 갈라진 지수를 좌표로 설명하는가")
print("   (감사 colloid.md §5.3 전수표와 대조)")

# 단층 공급(p=1, q=2) + 탄성 접촉 + 완전 하중분배 → 흔히 '표면적 지배'라 불리는 1/3
r = LoadRegime(chi=1.0, alpha=ALPHA_ELASTIC, beta=0.0, p=1.0, q=2.0)
check("탄성+완전분배 n_C", r.n_conc, 1.0 / 3.0)
check("탄성+완전분배 n_d", r.n_size, -2.0 * (1.0 - ALPHA_ELASTIC))

# 같은 조합에서 하중분배가 없으면 → 선형
r0 = LoadRegime(chi=0.0, alpha=ALPHA_ELASTIC, beta=0.0, p=1.0, q=2.0)
check("탄성+분배없음 n_C", r0.n_conc, 1.0)

# 소성 + 완전 분배 → 음의 지수 (과밀 레짐의 서명)
# 소성 plowing 의 단일입자 법칙은 Q₁ ∝ F^1.5 / d 이므로 크기 지수 β = −1.
# (감사표의 n_d 값이 이 β 를 전제한다 — β=0 으로 두면 표와 어긋난다)
BETA_PLOWING = -1.0
rp = LoadRegime(chi=1.0, alpha=ALPHA_PLASTIC, beta=BETA_PLOWING, p=1.0, q=2.0)
check("소성+완전분배 n_C", rp.n_conc, -0.5)
check("소성+완전분배 n_d", rp.n_size, 0.0)

# 소성 + 분배 없음 → 선형, 크기는 -3
rp0 = LoadRegime(chi=0.0, alpha=ALPHA_PLASTIC, beta=BETA_PLOWING, p=1.0, q=2.0)
check("소성+분배없음 n_C", rp0.n_conc, 1.0)
check("소성+분배없음 n_d", rp0.n_size, -3.0)

# 분자 스케일(하중 무관) → χ와 무관하게 선형, n_d = -2 + 0.5
rm = LoadRegime(chi=1.0, alpha=ALPHA_MOLECULAR, beta=0.5, p=1.0, q=2.0)
check("분자스케일 n_C", rm.n_conc, 1.0)
check("분자스케일 n_d", rm.n_size, -1.5)
rm0 = LoadRegime(chi=0.0, alpha=ALPHA_MOLECULAR, beta=0.5, p=1.0, q=2.0)
check("분자스케일 χ무관", rm0.n_conc, rm.n_conc)

print()
print("② 구조적 상한 — n_C ≤ 1 을 넘는 조합이 존재하는가 (전수)")
worst = -9.9
import itertools
for chi in [i / 20 for i in range(21)]:
    for alpha in (ALPHA_MOLECULAR, ALPHA_ELASTIC, ALPHA_PLASTIC):
        for p in (1.0, 2.0 / 3.0, 0.5):
            worst = max(worst, LoadRegime(chi, alpha, 0.0, p, 2.0).n_conc)
ok = worst <= 1.0 + 1e-9
print(f"  {'✅' if ok else '❌'} 전수 최대 n_C = {worst:.4f} ≤ 1")
if not ok:
    FAIL.append("상한")
print(f"  → 문헌의 4/3 = {4/3:.4f} 는 이 분해 안에서 도달 불가 "
      f"({'확인' if 4/3 > worst else '반증됨'})")

print()
print("③ 지수가 농도의 함수 — 단일 지수가 근사인 이유")
for lam, want in [(0.03, 0.985), (0.1, 0.951), (1.0, 0.582),
                  (2.0, 0.313), (3.0, 0.157)]:
    got = occupancy_exponent(lam, 1.0)
    ok = abs(got - want) < 0.002
    print(f"  {'✅' if ok else '❌'} λ={lam:<5g} n_loc={got:.3f} (감사표 {want})")
    if not ok:
        FAIL.append(f"n_loc({lam})")
# 1/3 이 나오는 지점
lo, hi = 0.01, 60.0
for _ in range(200):
    mid = (lo + hi) / 2
    if occupancy_exponent(mid, 1.0) > 1 / 3:
        lo = mid
    else:
        hi = mid
print(f"  → n=1/3 이 나오는 지점 λ≈{lo:.2f} (점유율 "
      f"{(1-2.718281828**-lo)*100:.0f}%) — 포화 진입부")

print()
print("④ 극한 거동")
r = resolve_regime(area_pressure_exponent=1.0, contact_stress_pa=1e9,
                   surface_hardness_pa=5e9, gap_m=1e-7, d_p_m=1e-7)
print(f"  판정: χ={r.chi:.2f} α={r.alpha:.3f} p={r.p:.2f} → n_C={r.n_conc:+.3f}")
check("포화비 C=0", occupancy_ratio(0.0, 4.0, 2.0), 0.0)
check("포화비 C=C_ref", occupancy_ratio(4.0, 4.0, 2.0), 1.0)
_or = lambda c: occupancy_ratio(c, 4.0, 2.0) or 0.0
mono = all(_or(c) < _or(c + 0.1) for c in [0.5, 1, 2, 4, 8])
print(f"  {'✅' if mono else '❌'} 포화비가 농도에 단조증가")
if not mono:
    FAIL.append("단조성")
unknown = resolve_regime()
print(f"  {'✅' if unknown.confidence == 'unverified' else '❌'} "
      f"입력이 없으면 등급 unverified (실제 {unknown.confidence})")
if unknown.confidence != "unverified":
    FAIL.append("미판정 등급")

print()
print("=" * 62)
if FAIL:
    print(f"❌ 실패 {len(FAIL)}건: {FAIL}")
    sys.exit(1)
print("✅ 전부 통과 — 3인자 분해가 문헌의 갈라진 지수를 좌표로 설명한다")
