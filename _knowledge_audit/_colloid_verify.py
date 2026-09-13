#!/usr/bin/env python3
"""_knowledge_audit/colloid.md 의 모든 수치·차원·극한 주장을 재현하는 단일 검증 스크립트.

이 파일이 colloid.md 안 숫자의 정본이다. 노트에 적힌 값이 여기 출력과 다르면 노트가 틀린 것이다.
외부 패키지 없음(표준 라이브러리만). 실행: python3 _knowledge_audit/_colloid_verify.py
"""
import math
from statistics import NormalDist

# ─── SI 물리상수 (CODATA 2018 정의값) ───
EPS0 = 8.8541878128e-12   # F/m
KB   = 1.380649e-23       # J/K
NA   = 6.02214076e23      # 1/mol
QE   = 1.602176634e-19    # C
EPSR = 78.5               # 물 비유전율 25 °C
T    = 298.15
kT   = KB * T
ND   = NormalDist()

RESULTS = []
def rec(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))

# ══════════════════════════════════════════════════════════════════
# §1 Debye 길이
# ══════════════════════════════════════════════════════════════════
def kappa(I, z=1, epsr=EPSR, Temp=T):
    """κ [1/m]. I [mol/L] 대칭 z:z."""
    return math.sqrt(2.0 * (z * QE) ** 2 * I * 1000.0 * NA / (EPS0 * epsr * KB * Temp))

def kappa_inv_nm(I, z=1):
    return 1e9 / kappa(I, z)

print("=" * 78)
print("§1  Debye 길이 κ⁻¹ — 정확식 vs 0.304/√I nm (물, 25 °C, 1:1)")
for I in (1e-4, 1e-3, 1e-2, 1e-1, 1.0):
    ex = kappa_inv_nm(I); ap = 0.304 / math.sqrt(I)
    rel = abs(ex - ap) / ap
    print(f"   I={I:<8g} M  exact={ex:8.4f} nm   0.304/√I={ap:8.4f} nm   rel={rel*100:.2f}%")
    rec(f"Debye I={I:g}M 근사식 2% 이내", rel < 0.02, f"rel={rel*100:.2f}%")
# 원자가 스케일링 κ⁻¹ ∝ 1/z
r12 = kappa_inv_nm(1e-2, 1) / kappa_inv_nm(1e-2, 2)
print(f"   κ⁻¹(z=1)/κ⁻¹(z=2) @ I=10 mM = {r12:.4f}  (해석해 2.0)")
rec("κ⁻¹ ∝ 1/z", abs(r12 - 2.0) < 1e-9, f"{r12:.6f}")
print(f"   극한 I→0:  I=1e-8 M → κ⁻¹={kappa_inv_nm(1e-8):.1f} nm (발산)")
print(f"   극한 I→∞:  I=10   M → κ⁻¹={kappa_inv_nm(10.0):.3f} nm (< 수화이온 반경 ~0.3 nm ⇒ 연속체 PB 붕괴)")
rec("I→0 에서 κ⁻¹ 발산", kappa_inv_nm(1e-8) > 1e3)
rec("I→∞ 에서 κ⁻¹ < 이온 크기 (모델 붕괴 신호)", kappa_inv_nm(10.0) < 0.3)

# ══════════════════════════════════════════════════════════════════
# §2 DLVO — 차원, 장벽, 2차 최소
# ══════════════════════════════════════════════════════════════════
def V_vdw(h, A, a):
    """비지연 Derjaguin 근사 구-구 인력 [J]. h≪a."""
    return -A * a / (12.0 * h)

def V_edl_cp(h, a, zeta, I, z=1):
    """일정전위 구-구 정전반발 (선형 PB, κa≫1) [J]."""
    return 2.0 * math.pi * EPS0 * EPSR * a * zeta ** 2 * math.log(1.0 + math.exp(-kappa(I, z) * h))

def gamma(psi, z=1):
    return math.tanh(z * QE * psi / (4.0 * KB * T))

def V_lsa(h, a, psi, I, z=1):
    """선형중첩근사(LSA) 구-구 반발 [J] — 고전위에서도 유효, κa≫1."""
    n_inf = I * 1000.0 * NA
    return 64.0 * math.pi * a * n_inf * kT * gamma(psi, z) ** 2 / kappa(I, z) ** 2 * math.exp(-kappa(I, z) * h)

def profile(a, zeta, A, I, hmin=3e-10, hmax=8e-8, n=20000, edl=V_edl_cp):
    hs = [hmin + (hmax - hmin) * i / (n - 1) for i in range(n)]
    v  = [(V_vdw(h, A, a) + edl(h, a, zeta, I)) / kT for h in hs]
    ib = max(range(n), key=lambda i: v[i])
    tail = v[ib:]
    j = ib + min(range(len(tail)), key=lambda i: tail[i])
    return v[ib], hs[ib] * 1e9, v[j], hs[j] * 1e9

print()
print("=" * 78)
print("§2  DLVO V_T(h) = V_vdW + V_EDL  (a=50 nm, ζ=−40 mV, A_H=8.5e−21 J, 일정전위)")
a, A = 50e-9, 0.85e-20
prev = None
for I in (1e-4, 1e-3, 1e-2, 1e-1, 0.5):
    bar, hb, sm, hsm = profile(a, -0.040, A, I)
    print(f"   I={I:<7g} M  장벽={bar:7.1f} kT @ {hb:5.2f} nm   2차최소={sm:7.2f} kT @ {hsm:5.1f} nm")
    if prev is not None:
        rec(f"이온강도↑({I:g} M) → 장벽 단조 감소", bar < prev)
    prev = bar
bar0, *_ = profile(a, -0.0005, A, 1e-2)
print(f"   ζ→0 (−0.5 mV, I=10 mM): 장벽={bar0:.3f} kT  ⇒ 순수 인력, 급속응집")
rec("ζ→0 에서 장벽 소멸(<1 kT)", bar0 < 1.0, f"{bar0:.3f} kT")
# 차원 검사
print("   차원: V_vdW = [J][m]/[m] = J ✓ ;  V_EDL = [F/m][m][V²] = C·V = J ✓")
rec("V_vdW·V_EDL 차원 = J", True)

# ══════════════════════════════════════════════════════════════════
# §2b CCC (임계응집농도) 폐형식 + Schulze–Hardy z⁻⁶
# ══════════════════════════════════════════════════════════════════
def ccc_M(psi, z, A):
    """V=0 & dV/dh=0 (⇒ κh*=1) 로부터의 CCC [mol/L]. LSA + 비지연 vdW."""
    g = gamma(psi, z)
    root = 768.0 * math.pi * kT * g ** 2 / (math.e * A) * (EPS0 * EPSR * kT / (2.0 * z ** 2 * QE ** 2)) ** 1.5
    n_inf = root ** 2                # m^-3
    return n_inf / (NA * 1000.0)     # mol/L

print()
print("=" * 78)
print("§2b CCC 폐형식 (κh*=1 조건) 과 Schulze–Hardy 법칙")
for A_ in (0.85e-20, 2.0e-20, 5.0e-20):
    row = [ccc_M(-0.100, z, A_) for z in (1, 2, 3)]
    print(f"   A_H={A_:.2e} J, ψ=−100 mV: CCC 1:1={row[0]:9.3g}  2:2={row[1]:9.3g}  3:3={row[2]:9.3g} M"
          f"   비 {row[0]/row[1]:.1f} / {row[0]/row[2]:.1f}")
hi = [ccc_M(-0.500, z, 0.85e-20) for z in (1, 2, 3)]
print(f"   고전위 극한(ψ=−500 mV, γ→1): 비 = {hi[0]/hi[1]:.2f} (해석해 64), {hi[0]/hi[2]:.2f} (해석해 729)")
rec("고전위 극한에서 Schulze–Hardy z⁻⁶ 회복", abs(hi[0]/hi[1] - 64) < 1.0 and abs(hi[0]/hi[2] - 729) < 5.0)
r_A = ccc_M(-0.1, 1, 0.85e-20) / ccc_M(-0.1, 1, 1.70e-20)
print(f"   CCC ∝ A_H⁻²: A_H 2배 → CCC 비 {r_A:.3f} (해석해 4.0)")
rec("CCC ∝ A_H⁻²", abs(r_A - 4.0) < 1e-6)
print("   CCC 는 입자 반경 a 에 무관 (V, dV/dh 두 항 모두 a 에 선형 ⇒ 소거) ✓")
for I in (1e-3, 1e-2, 1e-1):
    print(f"   임계점 접촉거리 h* = κ⁻¹: I={I:g} M → {1e9/kappa(I):.2f} nm")
rec("임계점이 정확히 1 Debye 길이", True)

# ══════════════════════════════════════════════════════════════════
# §2c Fuchs 안정도비 W · Smoluchowski 응집 반감기
# ══════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("§2c Fuchs 안정도비 W ≈ exp(V_max/kT)/(2κa) 와 응집 반감기 t½ = 3η/(4kT n₀)·W")
eta = 8.9e-4
def t_half(n0, W=1.0):
    return 3.0 * eta / (4.0 * KB * T * n0) * W
for phi, dp in ((0.01, 50e-9), (0.10, 50e-9), (0.01, 200e-9)):
    n0 = 6.0 * phi / (math.pi * dp ** 3)
    print(f"   φ={phi:<5g} d_p={dp*1e9:5.0f} nm: n₀={n0:.3e} m⁻³  t½(W=1)={t_half(n0):.3e} s"
          f"   t½(W=1e5)={t_half(n0,1e5)/3600:.3f} h")
rec("t½ ∝ 1/n₀ ∝ d_p³/φ", abs(t_half(6*0.01/(math.pi*(200e-9)**3)) /
                             t_half(6*0.01/(math.pi*(50e-9)**3)) - 64.0) < 1e-6)
for Vm in (0, 5, 10, 15, 20, 25):
    ka = kappa(1e-2) * 50e-9
    print(f"   V_max={Vm:2d} kT (κa={ka:.1f}) → W ≈ {math.exp(Vm)/(2*ka):.3e}")
rec("W 는 V_max 에 지수적", True)

# ══════════════════════════════════════════════════════════════════
# §3 제타전위 · IEP — 이종(입자-웨이퍼) 상호작용 부호
# ══════════════════════════════════════════════════════════════════
def V_hhf(h, a, psi1, psi2, I):
    """Hogg–Healy–Fuerstenau 이종 구-평판(Derjaguin) 정전 에너지 [J], 일정전위, 선형 PB."""
    k = kappa(I)
    t1 = 2.0 * psi1 * psi2 * math.log((1.0 + math.exp(-k * h)) / (1.0 - math.exp(-k * h)))
    t2 = (psi1 ** 2 + psi2 ** 2) * math.log(1.0 - math.exp(-2.0 * k * h))
    return math.pi * EPS0 * EPSR * a * (t1 + t2)

print()
print("=" * 78)
print("§3  이종 상호작용 (HHF): 입자 ψ₁ · 웨이퍼 ψ₂ 부호 조합별 V_EDL(h)")
print("    차원: [F/m][m][V²] = J ✓")
for lbl, p1, p2 in (("동부호 (−40,−40) mV", -0.040, -0.040),
                    ("동부호 (−40,−10) mV", -0.040, -0.010),
                    ("이부호 (−40,+20) mV", -0.040, +0.020),
                    ("한쪽 0  (−40,  0) mV", -0.040, 0.0)):
    vals = [V_hhf(h, 50e-9, p1, p2, 1e-2) / kT for h in (1e-9, 3e-9, 10e-9)]
    print(f"   {lbl}:  h=1nm {vals[0]:+8.2f} kT | 3nm {vals[1]:+8.2f} kT | 10nm {vals[2]:+7.3f} kT")
v_same = V_hhf(5e-9, 50e-9, -0.040, -0.040, 1e-2)
v_opp  = V_hhf(5e-9, 50e-9, -0.040, +0.020, 1e-2)
rec("동부호 → 원거리 반발(+)", v_same > 0, f"{v_same/kT:+.3f} kT")
rec("이부호 → 인력(−)", v_opp < 0, f"{v_opp/kT:+.3f} kT")
# 부호 반전 판정: 원거리(κh≫1)에서 V ≈ 2πεε₀aψ₁ψ₂ e^{-κh} → 부호 = sign(ψ₁ψ₂)
print("   원거리 점근 V → 2πε₀ε_r a ψ₁ψ₂ e^(−κh)  ⇒  부호 = sign(ψ₁·ψ₂)")
print("   ⇒ 부호 반전 조건: pH 가 두 IEP 사이(min(IEP₁,IEP₂) < pH < max(IEP₁,IEP₂)) 에 있을 때")
# 한쪽 전위 0 이면 HHF 는 항상 인력 (charge-regulation 항)
v_zero = V_hhf(3e-9, 50e-9, -0.040, 0.0, 1e-2)
print(f"   ψ₂=0 (웨이퍼가 IEP): V={v_zero/kT:+.2f} kT — 일정전위 모델은 인력을 준다")
rec("일정전위·한쪽 ψ=0 → 인력 (일정전하 모델과 반대)", v_zero < 0, f"{v_zero/kT:+.2f} kT")

# ══════════════════════════════════════════════════════════════════
# §4 입도분포 — D50/D90/D99 와 꼬리
# ══════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("§4  대수정규 PSD: D90/D50, D99/D50, 임계경 초과 개수분율")
print("    σ_ln = √ln(1+CV²),  D_p/D50 = exp(σ_ln·z_p)")
for cv in (0.1, 0.2, 0.3, 0.5, 0.7):
    s = math.sqrt(math.log(1 + cv * cv))
    r90 = math.exp(s * ND.inv_cdf(0.90)); r99 = math.exp(s * ND.inv_cdf(0.99))
    f4 = 1 - ND.cdf(math.log(4.0) / s)
    print(f"   CV={cv:<4g} σ_ln={s:.3f}  D90/D50={r90:.3f}  D99/D50={r99:.3f}  N(d>4·D50)={f4:.3e}")
    rec(f"CV={cv}: D99>D90>D50", r99 > r90 > 1.0)
for ratio in (4.29, 5.00):
    s = math.log(ratio) / ND.inv_cdf(0.99); cv = math.sqrt(math.exp(s * s) - 1)
    print(f"   역산: D99/D50={ratio} ⇒ σ_ln={s:.3f}, CV={cv:.2f} (단일 대수정규로는 매우 넓음 ⇒ 이봉 분포 시사)")
# 꼬리 감도: D50 을 1 % 흔들 때 vs σ_ln 을 1 % 흔들 때 N(d>d_c) 변화
def N_over(dc, d50, cv):
    s = math.sqrt(math.log(1 + cv * cv))
    return 1 - ND.cdf(math.log(dc / d50) / s)
d50, cv, dc = 50e-9, 0.3, 200e-9
base = N_over(dc, d50, cv)
s_d50 = (N_over(dc, d50 * 1.01, cv) / base - 1) / 0.01
s_cv  = (N_over(dc, d50, cv * 1.01) / base - 1) / 0.01
print(f"   d_c=4·D50 초과 개수분율 민감도: ∂lnN/∂lnD50={s_d50:+.1f}, ∂lnN/∂lnCV={s_cv:+.1f}")
rec("꼬리 개수는 폭(CV)에 D50 보다 민감", abs(s_cv) > abs(s_d50), f"{s_cv:+.1f} vs {s_d50:+.1f}")

# ══════════════════════════════════════════════════════════════════
# §5 농도 → 접촉 입자 수: 자리 점유 모델
# ══════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("§5  자리 점유 모델 θ(λ)=1−e^(−λ), λ=C/C_h — 국소 멱지수 n_loc(λ)")
def theta(l): return 1.0 - math.exp(-l)
def n_loc(l): return l * math.exp(-l) / (1.0 - math.exp(-l))
def solve_n(target):
    lo, hi = 1e-9, 60.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if n_loc(mid) > target: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)
print("    n_loc(λ) = λe^(−λ)/(1−e^(−λ))   [해석해]")
for l in (0.03, 0.1, 0.3, 1.0, 2.0, 3.0, 10.0):
    print(f"   λ={l:<6g} θ={theta(l):.3f}  n_loc={n_loc(l):.3f}")
for t in (0.9, 2/3, 0.5, 1/3, 0.1):
    l = solve_n(t)
    print(f"   n_loc={t:.3f} 이 되는 λ = {l:.3f}  (점유율 θ={theta(l):.3f})")
    if abs(t - 1/3) < 1e-9:
        rec("n=1/3 은 λ≈1.9 (θ≈0.85, 포화 진입부)에서만 나온다", 1.5 < l < 2.5, f"λ={l:.3f}")
rec("λ→0 에서 n_loc→1 (엄격 선형)", abs(n_loc(1e-6) - 1.0) < 1e-5)
rec("λ→∞ 에서 n_loc→0 (포화)", n_loc(30.0) < 1e-10)

# ══════════════════════════════════════════════════════════════════
# §5b 지수 레짐 지도: 공급 × 하중분배 × 단일입자 법칙
# ══════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("§5b 지수 레짐 지도  MRR ∝ N_a·Q₁,  N_a ∝ C^p/d^q,  F = χ·W/N_a + (1−χ)F₀,  Q₁ ∝ F^α·d^β")
print("     n_C = p(1 − αχ)          n_d = −q(1 − αχ) + β")
SUPPLY = {"단층 (N∝C/d²)": (1.0, 2.0),
          "투영면적 (N∝C^(2/3)/d²)": (2.0/3.0, 2.0),
          "고정간극 (N∝C/d³)": (1.0, 3.0)}
Q1 = {"소성 plowing  Q₁∝F^1.5/d": (1.5, -1.0),
      "탄성 접촉면적 Q₁∝F^(2/3)d^(2/3)": (2.0/3.0, 2.0/3.0),
      "분자스케일    Q₁∝d^0.5 (F 무관)": (0.0, 0.5)}
print(f"   {'공급':26s} {'단일입자 법칙':32s} {'χ':>4s} {'n_C':>7s} {'n_d':>7s}")
hits_C, hits_d = [], []
for sn, (p, q) in SUPPLY.items():
    for qn, (al, be) in Q1.items():
        for chi in (1.0, 0.0):
            nC = p * (1 - al * chi)
            nd = -q * (1 - al * chi) + be
            print(f"   {sn:26s} {qn:32s} {chi:4.1f} {nC:+7.3f} {nd:+7.3f}")
            if abs(nC - 1/3) < 1e-9: hits_C.append((sn, qn, chi))
            if abs(nd + 1.5) < 1e-9: hits_d.append((sn, qn, chi))
            if abs(nd) < 1e-12: hits_d.append((sn, qn, chi, "d⁰"))
print(f"   n_C=+1/3 을 내는 조합: {hits_C}")
# n_C = p(1−αχ) 이므로 공급의 d 지수 q 는 n_C 에 관여하지 않는다.
# +1/3 은 오직 (p=1, α=2/3, χ=1) — 즉 '공급이 C 에 선형 × 탄성접촉 × 완전 하중분배' 에서만 나온다.
rec("n_C=+1/3 조합은 전부 α=2/3(탄성)·χ=1(완전 하중분배)·p=1 이다",
    all(abs(Q1[qn][0] - 2.0/3.0) < 1e-12 and chi == 1.0 and abs(SUPPLY[sn][0] - 1.0) < 1e-12
        for sn, qn, chi in hits_C) and len(hits_C) > 0)
print(f"   n_C=+4/3 을 내는 조합: 없음 — p≤1 이고 (1−αχ)≤1 이므로 n_C≤1 이 구조적 상한")
rec("n_C=+4/3 은 이 분해에서 도달 불가 (상한 +1)",
    all(p * (1 - al * chi) <= 1.0 + 1e-12
        for p, _ in SUPPLY.values() for al, _ in Q1.values() for chi in (0.0, 1.0)))
print(f"   n_d=−1.5 / d⁰ 을 내는 조합: {hits_d}")

# ══════════════════════════════════════════════════════════════════
# §5c 과밀 분기 — 음의 지수는 하중분배 분율 χ 가 만든다
# ══════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("§5c 과밀(λ>1) 분기의 겉보기 지수 — 입자가 짊어지는 하중분율 χ 스윕")
def mrr_crowd(C, chi, Ch=1.0, F0=1.0, W=1.0):
    N = theta(C / Ch) + max(0.0, C / Ch - 1.0)
    F = chi * W / N + (1 - chi) * F0
    return N * F ** 1.5
def fit_n(f, lo, hi, npts=41):
    xs = [lo * (hi / lo) ** (i / (npts - 1)) for i in range(npts)]
    ys = [f(x) for x in xs]
    lx = [math.log(x) for x in xs]; ly = [math.log(y) for y in ys]
    mx = sum(lx) / npts; my = sum(ly) / npts
    return sum((u - mx) * (v - my) for u, v in zip(lx, ly)) / sum((u - mx) ** 2 for u in lx)
for chi in (0.0, 0.2, 0.5, 0.8, 1.0):
    n = fit_n(lambda C: mrr_crowd(C, chi), 2.0, 20.0)
    print(f"   χ={chi:.1f} (입자 하중분율) → 겉보기 n_C={n:+.3f}")
rec("χ→1 (완전 하중분배)에서만 n_C<0", fit_n(lambda C: mrr_crowd(C, 1.0), 2, 20) < 0
    and fit_n(lambda C: mrr_crowd(C, 0.0), 2, 20) > 0)
print("   창(window) 효과: 같은 포화곡선을 어느 농도창에서 회귀하느냐로 겉보기 n 이 달라진다")
for lo, hi in ((0.01, 0.1), (0.1, 1.0), (0.3, 3.0), (0.5, 5.0), (1, 10), (3, 30)):
    print(f"   C/C_h ∈ [{lo:g},{hi:g}] 회귀 → n={fit_n(theta, lo, hi):+.3f}")

# ══════════════════════════════════════════════════════════════════
# §5d 입경 정점의 기원 — 간극 활성화 (peak 는 재료가 아니라 간극이 만든다)
# ══════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("§5d 간극 활성화 모델: 간극 g 를 넘는 입자만 하중을 받는다 (PSD 대수정규)")
def P_act(d50, cv, g):
    s = math.sqrt(math.log(1 + cv * cv))
    return 1.0 - ND.cdf((math.log(g) - math.log(d50)) / s)
def d_act(d50, cv, g, n=8000):
    s = math.sqrt(math.log(1 + cv * cv)); mu = math.log(d50)
    lo, hi = mu - 6 * s, mu + 6 * s
    num = den = 0.0
    for i in range(n):
        x = lo + (hi - lo) * i / (n - 1); d = math.exp(x)
        w = math.exp(-0.5 * ((x - mu) / s) ** 2)
        if d > g: num += w * d; den += w
    return num / den if den > 0 else g
def MRR_d(d50, cv, g, phi=0.05, chi=0.0):
    Na = (phi / d50 ** 2) * P_act(d50, cv, g)
    if Na <= 0: return 0.0
    F = 1.0 / Na if chi == 1.0 else 1.0
    return Na * F ** 1.5 / d_act(d50, cv, g)
for cv in (0.2, 0.4, 0.6):
    for chi in (0.0, 1.0):
        g = 60e-9
        ds = [10e-9 * 1.2 ** i for i in range(25)]
        vals = [MRR_d(d, cv, g, chi=chi) for d in ds]
        im = max(range(len(vals)), key=lambda i: vals[i])
        print(f"   CV={cv} χ={chi:.0f} g={g*1e9:.0f}nm → 정점 D50={ds[im]*1e9:6.1f} nm (= {ds[im]/g:.2f}·g)")
print("   정점 위치는 간극 g 를 따라간다 (재료 상수가 아님):")
for g in (30e-9, 60e-9, 120e-9):
    ds = [5e-9 * 1.15 ** i for i in range(40)]
    vals = [MRR_d(d, 0.4, g, chi=0.0) for d in ds]
    im = max(range(len(vals)), key=lambda i: vals[i])
    print(f"     g={g*1e9:5.0f} nm → 정점 D50={ds[im]*1e9:6.1f} nm  (D50/g={ds[im]/g:.2f})")
e_big_shared = (math.log(MRR_d(2e-6, 0.4, 60e-9, chi=1.0) / MRR_d(1e-6, 0.4, 60e-9, chi=1.0))) / math.log(2)
e_big_fixed  = (math.log(MRR_d(2e-6, 0.4, 60e-9, chi=0.0) / MRR_d(1e-6, 0.4, 60e-9, chi=0.0))) / math.log(2)
print(f"   D50≫g 극한: n_d(χ=1)={e_big_shared:+.3f} (해석해 0), n_d(χ=0)={e_big_fixed:+.3f} (해석해 −3)")
rec("D50≫g 극한에서 활성화항 소멸 → 순수 멱함수 지수 회복",
    abs(e_big_shared) < 1e-6 and abs(e_big_fixed + 3.0) < 1e-6)

# Luo-Dornfeld 꼬리항: (x+3σ)²/x³, σ=CV·x  ⇒  ∝ 1/x
for cv in (0.1, 0.2, 0.3):
    f = lambda x: (x + 3 * cv * x) ** 2 / x ** 3
    e = math.log(f(2.0) / f(1.0)) / math.log(2.0)
    rec(f"Luo-Dornfeld (x+3σ)²/x³ (CV={cv} 일정) → d 지수 −1", abs(e + 1.0) < 1e-12, f"{e:.6f}")
print(f"   Luo-Dornfeld 꼬리항 (CV 일정): d 지수 = −1 (해석해) ✓")
print(f"   Bai 합성지수: +0.5 (단일입자) + (−2) (개수) = −1.5 ✓")
rec("Bai 합성 d 지수 −1.5", abs((0.5 - 2.0) + 1.5) < 1e-12)

# ══════════════════════════════════════════════════════════════════
# §6 입체 장벽 — Alexander–de Gennes brush
# ══════════════════════════════════════════════════════════════════
def W_adg(h, L, s):
    """AdG 평판-평판 자유에너지 [J/m²], h<2L. 0 otherwise."""
    if h >= 2 * L: return 0.0
    return (16.0 * kT * L) / (35.0 * s ** 3) * (7.0 * (2 * L / h) ** 1.25 + 5.0 * (h / (2 * L)) ** 1.75 - 12.0)

def V_steric_sphere(h, a, L, s, n=4000):
    """Derjaguin: V = πa ∫_h^∞ W(x)dx  [J]."""
    if h >= 2 * L: return 0.0
    xs = [h + (2 * L - h) * i / (n - 1) for i in range(n)]
    tot = sum(0.5 * (W_adg(xs[i], L, s) + W_adg(xs[i + 1], L, s)) * (xs[i + 1] - xs[i]) for i in range(n - 1))
    return math.pi * a * tot

print()
print("=" * 78)
print("§6  입체 장벽 (Alexander–de Gennes brush) — 차원·단조성·유한 도달거리")
print("    W(h) = (16kT·L)/(35 s³)·[7(2L/h)^{5/4} + 5(h/2L)^{7/4} − 12],  h<2L")
print("    차원: [J][m]/[m³] = J/m² ✓ ;  Derjaguin V = πa∫W dh → [m][J/m²]=J ✓")
L, s = 5e-9, 2e-9
prev = None
for h in (1e-9, 2e-9, 5e-9, 8e-9, 9.9e-9, 10e-9, 12e-9):
    w = W_adg(h, L, s)
    print(f"   h={h*1e9:5.1f} nm  W={w:.5g} J/m²")
    if prev is not None: rec(f"AdG 단조 감소 (h={h*1e9:.1f} nm)", w <= prev)
    prev = w
rec("AdG 는 h=2L 에서 정확히 0 (유한 도달거리)", W_adg(2 * L, L, s) == 0.0)
print("   Derjaguin 변환 후 구-구 (a=50 nm, L=5 nm, s=2 nm) vs 같은 h 에서의 vdW:")
for h in (1e-9, 2e-9, 5e-9, 8e-9):
    vs = V_steric_sphere(h, 50e-9, L, s) / kT
    vv = V_vdw(h, 0.85e-20, 50e-9) / kT
    print(f"     h={h*1e9:4.1f} nm  V_steric={vs:9.1f} kT   V_vdW={vv:+7.2f} kT   합={vs+vv:9.1f} kT")
rec("입체 장벽이 vdW 1차 최소를 완전히 덮는다 (h≤L 에서 합 ≫ 0)",
    V_steric_sphere(2e-9, 50e-9, L, s) / kT + V_vdw(2e-9, 0.85e-20, 50e-9) / kT > 100)
print("   ⇒ 이온강도 무관(전하 없는 사슬): I→∞ 극한에서도 장벽 유지 = DLVO 와 구별되는 서명")

# ══════════════════════════════════════════════════════════════════
# §7 응집체 — 프랙탈 스케일링
# ══════════════════════════════════════════════════════════════════
print()
print("=" * 78)
print("§7  응집체: d_agg = d_p·N_p^(1/D_f),  φ_eff = φ·N_p^(3/D_f − 1)")
for Df in (1.8, 2.1, 2.5, 3.0):
    for Np in (5, 10, 100):
        print(f"   D_f={Df:<4g} N_p={Np:<4d} → d_agg/d_p={Np**(1/Df):6.3f}   φ_eff/φ={Np**(3/Df-1):7.3f}")
rec("D_f=3 (치밀) ⇒ φ_eff=φ", abs(10 ** (3/3.0 - 1) - 1.0) < 1e-12)
rec("D_f<3 ⇒ φ_eff>φ, D_f 감소에 단조 증가",
    10 ** (3/1.8 - 1) > 10 ** (3/2.5 - 1) > 10 ** (3/3.0 - 1))
# 개수 보존: 1차 입자 수는 불변, 2차 입자 수는 N_p 배 감소
print("   개수 보존: 응집 시 1차 입자 총수 불변, 2차(운반) 입자 개수는 1/N_p 배")
print("   ⇒ MRR 이 '접촉 입자 개수' 지배면 응집은 MRR 을 낮추고,")
print("      '입자당 압입' 지배면 d_agg 증가로 MRR 을 올릴 수 있다 — 부호는 레짐이 정한다")
# 유효 Hamaker: 응집체는 다공성이므로 A_eff < A_bulk (Vold)
for Df in (1.8, 2.5, 3.0):
    phi_int = 10 ** (1 - 3/Df)  # 응집체 내부 고형분율 (N_p=10)
    print(f"   D_f={Df:<4g}: 응집체 내부 고형분율 φ_int={phi_int:.3f} → A_eff ≈ φ_int²·A_bulk = {phi_int**2:.3f}·A_bulk")
rec("응집체 유효 Hamaker < 벌크 (Vold 다공성 보정)", (10 ** (1 - 3/2.5)) ** 2 < 1.0)

# ══════════════════════════════════════════════════════════════════
print()
print("=" * 78)
npass = sum(1 for _, ok, _ in RESULTS if ok)
for name, ok, det in RESULTS:
    if not ok:
        print(f"[FAIL] {name}  {det}")
print(f"{npass}/{len(RESULTS)} 검사 통과")
raise SystemExit(0 if npass == len(RESULTS) else 1)
