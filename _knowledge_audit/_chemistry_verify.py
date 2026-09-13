"""chemistry.md 본문의 모든 수치 주장을 재현하는 단일 검증 스크립트.

이 파일은 지식감사 산출물(_knowledge_audit/chemistry.md)의 부속이다.
본문에 숫자를 쓰기 전에 반드시 여기서 나온 값을 옮긴다 — 기억이나 추정으로 쓰지 않는다.

실행: python3 _knowledge_audit/_chemistry_verify.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "sim" / "tier2_physics"))

import particle_chemomechanical_synergy as PS  # noqa: E402
import pourbaix_nernst_slope as PN  # noqa: E402
import slurry_components as SC  # noqa: E402
import competitive_metal_langmuir as CL  # noqa: E402

R = 8.314462618      # J/(mol K)
F = 96485.33212      # C/mol
T = 298.15           # K

CHECKS: list[tuple[str, bool, str]] = []


def ck(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond), detail))


# ═══════════════════════════════════════════════ A1. Langmuir 포화 함정
K = SC.K_from_dG_ads(-35.4e3, T)          # 문헌값 차용 ΔG_ads → K [L/mol]
ck("A1.0 ΔG_ads=-35.4 kJ/mol → K", abs(K - 2.868e4) / 2.868e4 < 0.01, f"K={K:.4g} L/mol")

C_list = [1e-5, 1e-4, 1e-3, 2e-3, 5e-3]
theta = [SC.langmuir_coverage(c, K) for c in C_list]
ck("A1.1 θ 단조증가", all(theta[i] < theta[i + 1] for i in range(len(theta) - 1)),
   ", ".join(f"{c*1e3:g}mM→{t:.4f}" for c, t in zip(C_list, theta)))
ck("A1.2 C=1/K 에서 θ=1/2", abs(SC.langmuir_coverage(1.0 / K, K) - 0.5) < 1e-12,
   f"C_half=1/K={1e6/K:.1f} µM")

# 고농도 포화: (1-θ)는 C^-1 로 붕괴 → 잔여율을 선형으로 쓰면 분해능 소멸
slope = (math.log(1 - SC.langmuir_coverage(2e-3, K))
         - math.log(1 - SC.langmuir_coverage(1e-3, K))) / math.log(2.0)
ck("A1.3 θ→1 극한에서 d ln(1-θ)/d ln C → -1", abs(slope + 1.0) < 0.03, f"slope={slope:.4f}")

lin_ratio = (1 - SC.langmuir_coverage(2e-3, K)) / (1 - SC.langmuir_coverage(1e-3, K))
k_inh = 3.0
exp_ratio = (math.exp(-k_inh * SC.langmuir_coverage(2e-3, K))
             / math.exp(-k_inh * SC.langmuir_coverage(1e-3, K)))
ck("A1.4 (1-θ) 선형형은 2배 농도에 ~2배 응답(하한 클램프에서 죽는다)",
   abs(lin_ratio - 0.509) < 0.01, f"(1-θ) 비 = {lin_ratio:.4f}")
ck("A1.5 exp(-kθ) 형은 같은 구간 응답이 5% 미만 = 사실상 평평",
   abs(exp_ratio - 1.0) < 0.05, f"exp 비 = {exp_ratio:.4f} (k={k_inh})")

# Frumkin 협동성: f>0 이면 포화가 더 급격
def C_of_theta(th: float, f: float) -> float:
    return th / ((1 - th) * math.exp(2 * f * th))


r_lang = C_of_theta(0.6, 0.0) / C_of_theta(0.4, 0.0)
r_frum = C_of_theta(0.6, 1.5) / C_of_theta(0.4, 1.5)
ck("A1.6 Langmuir θ 0.4→0.6 농도폭 = 2.25배", abs(r_lang - 2.25) < 1e-9, f"{r_lang:.4f}")
ck("A1.7 Frumkin f>0은 더 가파름(협동 흡착)", r_frum < r_lang, f"f=1.5 → {r_frum:.4f}배")

# 경쟁 Langmuir: 총 피복률 ≤ 1, 그리고 성분 추가는 기존 성분을 밀어낸다
one = CL.competitive_langmuir_surface({"A": (1e6, 1e-6)}, pH=4.0)
two = CL.competitive_langmuir_surface({"A": (1e6, 1e-6), "B": (1e5, 1e-5)}, pH=4.0)
ck("A1.8 경쟁 흡착 총 θ ≤ 1", 0 <= two["_theta"] <= 1, f"Θ={two['_theta']:.4f}")
ck("A1.9 경쟁종 추가 → 기존종 피복 감소(자리 경쟁)", two["A"] < one["A"],
   f"σ_A {one['A']:.3g} → {two['A']:.3g} sites/cm²")

# ═══════════════════════════════════════════════ A2. 산화제 단봉
def f_ox(x: float, n: float) -> float:
    """FabSim 현 구현(SC.mrr_oxidizer)의 정규화형. x = C/C_peak."""
    return ((n + 1.0) * x) / (1.0 + n * x ** ((n + 1.0) / n))


ck("A2.1 C→0 에서 0 (기계 바닥값 없음)", f_ox(1e-12, 2.0) < 1e-10, f"{f_ox(1e-12, 2.0):.3g}")
ck("A2.2 C=C_peak 에서 정확히 1", abs(f_ox(1.0, 2.0) - 1.0) < 1e-12)
dec = (math.log(f_ox(100.0, 2.0)) - math.log(f_ox(10.0, 2.0))) / math.log(10.0)
ck("A2.3 C→∞ 점근 기울기 = -1/n", abs(dec + 1.0 / 2.0) < 0.01, f"n=2 → slope {dec:.4f}")

floor = 0.15
ck("A2.4 mech_floor 결합 시 C=0 값 = floor", abs(floor + (1 - floor) * f_ox(1e-12, 2.0) - floor) < 1e-9)

# 단봉의 1차원리 유도: 막 성장만으로는 단봉이 안 나온다는 반증
def mrr_film_only(C: float, Kox: float = 20.0, k_L: float = 1.0, L_c: float = 0.3) -> float:
    """θ_ox(피복)×기계관통효율 exp(-L/L_c), L ∝ C. 경도 경로 없음."""
    th = Kox * C / (1 + Kox * C)
    return th * math.exp(-k_L * C / L_c)


grid = np.logspace(-3, 2, 400)
v_film = np.array([mrr_film_only(c) for c in grid])
i_film = int(np.argmax(v_film))
ck("A2.5 (반증) 피복×관통감쇠만으로도 내부 정점이 생김 — 단봉 자체는 약한 주장",
   0 < i_film < len(grid) - 1, f"argmax C={grid[i_film]:.4g}")


def mrr_hardness(C: float, Kox: float = 20.0, H_m: float = 2.0, H_f0: float = 0.4,
                 L_d: float = 2.0, L_c: float = 0.3, k_L: float = 1.0) -> float:
    """경도 경로로 유도한 단봉: MRR ∝ θ_ox · H_eff^(-3/2).

    H_eff = H_film(L) + (H_metal - H_film(L))·exp(-L/L_c),  H_film(L) = H_f0(1 + L/L_d)
    - 저농도: 막이 얇아 H_eff ≈ H_metal(경질) → MRR 작음, θ_ox도 작음
    - 고농도: 막이 두꺼워지며 치밀화(H_film↑) → H_eff↑ → MRR 감소
    """
    th = Kox * C / (1 + Kox * C)
    L = k_L * C
    H_f = H_f0 * (1 + L / L_d)
    H_eff = H_f + (H_m - H_f) * math.exp(-L / L_c)
    return th * H_eff ** -1.5


v_h = np.array([mrr_hardness(c) for c in grid])
i_h = int(np.argmax(v_h))
ck("A2.6 경도경로 모델은 내부 정점(단봉)을 낸다", 0 < i_h < len(grid) - 1,
   f"argmax C={grid[i_h]:.4g}, MRR={v_h[i_h]:.4g}")
asym = ((math.log(mrr_hardness(1e5)) - math.log(mrr_hardness(1e4)))
        / (math.log(1e5) - math.log(1e4)))
ck("A2.7 하강 가지 점근 기울기 → -3/2 (H_eff ∝ C 이므로)", abs(asym + 1.5) < 0.01,
   f"slope={asym:.4f}")
ck("A2.8 C→0, C→∞ 양끝에서 MRR→0 (물리적으로 타당)",
   mrr_hardness(1e-9) < 1e-6 and mrr_hardness(1e6) < 1e-3,
   f"C→0 {mrr_hardness(1e-9):.3g}, C→∞ {mrr_hardness(1e6):.3g}")

# ═══════════════════════════════════════════════ A3. pH 정점형 / IEP 창
def charge_sign(iep: float, pH: float) -> int:
    return 1 if pH < iep else (-1 if pH > iep else 0)


iep_particle, iep_wafer = 6.8, 2.5
attract = [pH for pH in np.arange(0.5, 14.0, 0.1)
           if charge_sign(iep_particle, pH) * charge_sign(iep_wafer, pH) < 0]
ck("A3.1 정전 인력창 = 두 IEP 사이 구간뿐",
   abs(min(attract) - 2.6) < 0.15 and abs(max(attract) - 6.7) < 0.15,
   f"창 = pH {min(attract):.1f}–{max(attract):.1f} (IEP {iep_wafer}/{iep_particle})")
ck("A3.2 두 IEP가 같으면 인력창 소멸(정점 거동 사라짐)",
   not any(charge_sign(5.0, pH) * charge_sign(5.0, pH) < 0 for pH in np.arange(0.5, 14, 0.1)))

nernst_mV = R * T / F * math.log(10) * 1000
ck("A3.3 표면전하 pH 기울기 상한 = 2.303RT/F", abs(nernst_mV - 59.16) < 0.05,
   f"{nernst_mV:.4f} mV/pH")

# ═══════════════════════════════════════════════ A4. Nernst / Pourbaix
ck("A4.1 dE/dpH = -(2.303RT/F)(m/n), m=n → -59.16 mV/pH",
   abs(PN.nernst_ph_slope(1, 1) * 1000 + 59.16) < 0.01)
ck("A4.2 m=2n → 기울기 2배", abs(PN.nernst_ph_slope(2, 1) - 2 * PN.nernst_ph_slope(1, 1)) < 1e-15,
   f"{PN.nernst_ph_slope(2, 1)*1000:.2f} mV/pH")
ck("A4.3 m/n 비만 중요(반응식 배율 불변)",
   abs(PN.nernst_ph_slope(6, 6) - PN.nernst_ph_slope(1, 1)) < 1e-15)
try:
    PN.nernst_ph_slope(1, 0)
    ck("A4.4 n=0(산-염기 반응)은 기울기 미정의로 거부", False, "예외 안 남")
except ValueError:
    ck("A4.4 n=0(산-염기 반응)은 기울기 미정의로 거부", True, "ValueError 발생")

# 활동도 항: log a 가 10배 변하면 경계가 (k/n) 만큼 이동
k_n = R * T / F * math.log(10)
shift = k_n / 2.0
ck("A4.5 n=2 경계선의 log a 1단위 이동 = 29.6 mV", abs(shift * 1000 - 29.58) < 0.05,
   f"{shift*1000:.2f} mV/decade")

# ═══════════════════════════════════════════════ A5. Butler-Volmer / 갈바닉
alpha, i0 = 0.5, 1e-6


def bv(eta: float, a: float = alpha, j0: float = i0) -> float:
    return j0 * (math.exp(a * F * eta / (R * T)) - math.exp(-(1 - a) * F * eta / (R * T)))


def bv_lin(eta: float, j0: float = i0) -> float:
    return j0 * F * eta / (R * T)


e1 = abs(bv(0.001) - bv_lin(0.001)) / abs(bv_lin(0.001))
e2 = abs(bv(0.050) - bv_lin(0.050)) / abs(bv_lin(0.050))
ck("A5.1 |η|≪RT/F 극한에서 선형(α 무관)", e1 < 1e-3, f"η=1 mV 상대오차 {e1:.2e}")
ck("A5.2 η=50 mV에서는 선형근사가 이미 16% 틀림", 0.1 < e2 < 0.3, f"상대오차 {e2:.3f}")
# α 의존은 1차항에서만 사라진다. 2차항이 (2α-1)Fη/(2RT) 비율로 남으므로
# α=0.2 vs 0.8 의 차이는 η에 **선형**으로 커진다 — "선형영역에서 α가 안 보인다"는
# 흔한 서술은 1차 근사에서만 참이다. 임의 허용오차 대신 해석식과 대조한다.
def _alpha_spread(eta: float) -> float:
    return abs(bv(eta, 0.2) - bv(eta, 0.8)) / abs(bv(eta, 0.5))


def _alpha_spread_analytic(eta: float, a: float = 0.8) -> float:
    """1차항 소거 후 남는 2차항 비: 2·|(2α-1)|·Fη/(2RT)."""
    return 2 * abs((2 * a - 1) * F * eta / (2 * R * T))


_sp = [(e, _alpha_spread(e), _alpha_spread_analytic(e)) for e in (1e-4, 1e-3, 1e-2)]
ck("A5.3 α 의존은 1차항까지만 사라지고 2차항에 (2α-1)Fη/2RT 로 잔존(η에 선형)",
   all(abs(num - ana) / ana < 0.01 for _, num, ana in _sp),
   "; ".join(f"η={e*1e3:g} mV → 수치 {n*100:.3f}% / 해석 {a*100:.3f}%" for e, n, a in _sp))
tafel = 2.302585 * R * T / (alpha * F) * 1000
ck("A5.4 Tafel 기울기 b = 2.303RT/(αF), α=0.5 → 118 mV/dec", abs(tafel - 118.3) < 0.1,
   f"{tafel:.2f} mV/decade")
b_a = b_c = 0.118
B = b_a * b_c / (2.302585 * (b_a + b_c))
ck("A5.5 Stern-Geary B = b_a b_c /(2.303(b_a+b_c)) ≈ 26 mV", abs(B - 0.02562) < 1e-4,
   f"B={B*1000:.2f} mV")


def mixed_potential(E_a: float, E_c: float, i0a: float, i0c: float,
                    a: float = 0.5, A_a: float = 1.0, A_c: float = 1.0) -> tuple[float, float]:
    """혼합전위 이론(Wagner-Traud): 총 양극전류 + 총 음극전류 = 0 을 만족하는 E_mix."""
    lo, hi = min(E_a, E_c) - 0.5, max(E_a, E_c) + 0.5

    def net(E: float) -> float:
        return (A_a * bv(E - E_a, a, i0a)) + (A_c * bv(E - E_c, a, i0c))

    for _ in range(300):
        mid = (lo + hi) / 2
        if net(mid) > 0:
            hi = mid
        else:
            lo = mid
    E = (lo + hi) / 2
    return E, A_a * bv(E - E_a, a, i0a) / A_a   # 양극 금속의 전류밀도


E_a, E_c = -0.10, 0.40     # 일반 이종금속 쌍: ΔE = 0.50 V
res = {}
for ratio in (0.1, 1.0, 10.0, 100.0):
    res[ratio] = mixed_potential(E_a, E_c, 1e-6, 1e-6, A_c=ratio)
ck("A5.6 E_mix가 두 평형전위 사이에 놓인다",
   all(E_a < res[r][0] < E_c for r in res),
   ", ".join(f"A_c/A_a={r}→{res[r][0]:+.4f} V" for r in res))
# ⚠ 교과서적 "면적비 법칙 i_a ∝ A_c/A_a"는 **음극이 분극되지 않을 때만** 선형이다.
# 두 반응이 모두 Tafel 거동이면 E_mix가 같이 움직여 지수가 b_c/(b_a+b_c)로 깎인다.
# 대칭(α=0.5, b_a=b_c)이면 지수 = 1/2 → 면적비 10배에 전류밀도 √10배뿐이다.
# (첫 작성 시 ×10을 기대해 FAIL 났고, 그게 바로 흔한 오해였다.)
_exp_area = (math.log(res[100.0][1] / res[1.0][1]) / math.log(100.0))
ck("A5.7 면적비 법칙 지수 = b_c/(b_a+b_c); 대칭 Tafel이면 1/2 (×10 아님)",
   abs(_exp_area - 0.5) < 0.02,
   f"A_c/A_a 1→10→100: i_a {res[1.0][1]:.4g} → {res[10.0][1]:.4g} → {res[100.0][1]:.4g} A/cm², "
   f"실측 지수 {_exp_area:.4f}")
_dE = (res[100.0][0] - res[1.0][0]) / 2.0
ck("A5.7b E_mix는 면적비 1 decade당 b_c·(b_a/(b_a+b_c)) = 59 mV 이동",
   abs(_dE * 1000 - 59.16) < 1.0, f"{_dE*1000:.2f} mV/decade")
ck("A5.8 ΔE=0 이면 갈바닉 구동 전류 0",
   abs(mixed_potential(0.0, 0.0, 1e-6, 1e-6)[1]) < 1e-12)


def mrr_faraday(i_A_cm2: float, M_g_mol: float, n: int, rho_g_cm3: float) -> float:
    """Faraday 환산: [A/cm²]·[g/mol] / ([-]·[C/mol]·[g/cm³]) = cm/s."""
    return i_A_cm2 * M_g_mol / (n * F * rho_g_cm3)


v_nm_min = mrr_faraday(1e-3, 60.0, 2, 9.0) * 1e7 * 60
ck("A5.9 Faraday 차원검사: 1 mA/cm² → nm/min 오더(수십)", 5 < v_nm_min < 100,
   f"M=60 g/mol, n=2, ρ=9 g/cm³ → {v_nm_min:.2f} nm/min")

# ═══════════════════════════════════════════════ A6. 화학-기계 시너지
amp = PS.chemomechanical_amplification(2.0e9, 0.5e9, 50e-9, 50e-9)
ck("A6.1 H 4배 연화 → 압입깊이 4배", abs(amp["depth_ratio"] - 4.0) < 1e-9, str(amp["depth_ratio"]))
ck("A6.2 H 4배 연화 → 제거체적 4^1.5 = 8배", abs(amp["volume_ratio"] - 8.0) < 1e-9,
   str(amp["volume_ratio"]))
expo = math.log(amp["volume_ratio"]) / math.log(4.0)
ck("A6.3 지수 = 3/2 (유도값, 튜닝 아님)", abs(expo - 1.5) < 1e-9, f"{expo:.6f}")
d1, A1 = PS.plastic_plowing(50e-9, 50e-9, 1e9)
d2, A2 = PS.plastic_plowing(100e-9, 50e-9, 1e9)
ck("A6.4 하중 2배 → 체적 2^1.5배 (하중과 경도가 같은 지수로 들어간다)",
   abs(A2 / A1 - 2 ** 1.5) < 1e-9, f"{A2/A1:.4f}")
ck("A6.5 H→0 극한에서 체적 발산 = 클램프 필요(비물리)",
   PS.plastic_plowing(50e-9, 50e-9, 1e6)[1] > 1e3 * A1,
   "H를 1000배 낮추면 체적 3.2e4배")

# ═══════════════════════════════════════════════ A7. 식별 불가능성(파라미터 상관)
def resid_inhib(C: float, K_ads: float, k: float) -> float:
    return math.exp(-k * (K_ads * C / (1 + K_ads * C)))


C_scan = np.array([0.5e-3, 1e-3, 2e-3, 5e-3])
C_ref = 1e-3
base = np.array([resid_inhib(c, 2.87e4, 3.0) / resid_inhib(C_ref, 2.87e4, 3.0) for c in C_scan])
fam = []
for K2 in np.logspace(3, 6, 150):
    for k2 in np.linspace(0.3, 12, 150):
        p = np.array([resid_inhib(c, K2, k2) / resid_inhib(C_ref, K2, k2) for c in C_scan])
        if np.sqrt(np.mean((np.log(p) - np.log(base)) ** 2)) < 0.01:
            fam.append((K2, k2))
fam_a = np.array(fam)
corr_inhib = float(np.corrcoef(np.log10(fam_a[:, 0]), fam_a[:, 1])[0, 1])
ck("A7.1 (K_ads, k_inhib)는 4점 MRR 스캔으로 식별 불가 — 1% 내 동등해가 광범위",
   len(fam_a) > 100 and corr_inhib > 0.8,
   f"동등해 {len(fam_a)}개, K {fam_a[:,0].min():.3g}–{fam_a[:,0].max():.3g} L/mol, "
   f"k {fam_a[:,1].min():.2f}–{fam_a[:,1].max():.2f}, corr(log10 K, k) = {corr_inhib:+.3f}")

fam2 = []
b_ox = np.array([f_ox(c, 2.0) for c in (0.5, 1.0, 2.0, 3.0)])
b_ox = b_ox / b_ox[1]
for Cp in np.linspace(0.5, 2.5, 100):
    for n in np.linspace(0.5, 6, 100):
        p = np.array([f_ox(c / Cp, n) for c in (0.5, 1.0, 2.0, 3.0)])
        p = p / p[1]
        if np.sqrt(np.mean((np.log(p) - np.log(b_ox)) ** 2)) < 0.02:
            fam2.append((Cp, n))
fam2_a = np.array(fam2)
corr_ox = float(np.corrcoef(fam2_a[:, 0], fam2_a[:, 1])[0, 1])
ck("A7.2 (C_peak, n)은 상대적으로 잘 식별됨 — 정점 위치가 곡선 형상에 강하게 각인",
   fam2_a[:, 0].max() - fam2_a[:, 0].min() < 0.3,
   f"동등해 {len(fam2_a)}개, C_peak {fam2_a[:,0].min():.3f}–{fam2_a[:,0].max():.3f}, "
   f"n {fam2_a[:,1].min():.2f}–{fam2_a[:,1].max():.2f}, corr = {corr_ox:+.3f}")

# ═══════════════════════════════════════════════ 출력
if __name__ == "__main__":
    n_pass = sum(1 for _, ok, _ in CHECKS if ok)
    print(f"=== chemistry.md verify: {n_pass}/{len(CHECKS)} PASS ===")
    for name, ok, detail in CHECKS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if detail:
            print(f"       {detail}")
    sys.exit(0 if n_pass == len(CHECKS) else 1)
