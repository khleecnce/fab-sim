"""Θ 정상상태 열저항 네트워크 — 마찰열 Q_f의 슬러리/패드/공기 3분배와 계면 온도상승 ΔT_ss.

지식 근거: knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md §8
1차 문헌: White, Melvin, Boning, J. Electrochem. Soc. 150(4) G271 (2003),
          DOI 10.1149/1.1560642 — 원문 확보(papers/white2003-jes-dynamic-thermal-behavior-cmp.pdf)
          Harmand et al., Int. J. Thermal Sci. 67 (2013) 1-30, arXiv:1305.2882 — 회전원판 층류
          Nu_r = a·Re_r^0.5, 등온 원판 a=0.3286 (Pr=0.71 공기, 정확 자기상사해, Table 1 n=0)
          Shin et al., Materials 18(19) 4461 (2025), DOI 10.3390/ma18194461 — k_pad≈0.02 W/m·K,
          실측 ΔT(Fig.7a: ~20.5 → ~35.5 °C, 90 s)

계약 (엔진과의 경계):
  이 모듈은 "정상상태에서 마찰열 Q_f가 어느 경로로 얼마씩 빠져나가고, 그 결과 계면이
  공통 싱크(슬러리 공급온도 = 플래튼 = 주변공기라는 가정) 대비 몇 K 오르는가"만 답한다.
  Q_f(=μ·P·A·V)를 어디서 가져올지는 호출자 책임이다. Recipe/팩을 모른다.

  전기회로 유사(열저항 네트워크, White 2003 §"Dynamic Thermal Model"):
    Q_f = G_slurry·ΔT + G_pad·ΔT + G_air·ΔT       ⇒  ΔT_ss = Q_f / (G_slurry + G_pad + G_air)
    G_slurry = ṁ·c_p                 [W/K]  슬러리 엔탈피 수송 (White 2003 Eq.9, R_s = 1/(ṁc_p))
    G_pad    = k_pad·A_heated/L_pad  [W/K]  패드 두께 방향 전도 (White 2003 Eq.4-5)
    G_air    = h_air·A_exposed       [W/K]  회전 패드 → 공기 대류, h_air = a·k_air·sqrt(Ω/ν_air)
                                            (Harmand 2013 Eq.10, 층류 b=0.5 ⇒ h는 반경 무관)
  세 싱크가 모두 같은 온도 T_0(공급 슬러리·플래튼·공기)라는 가정하의 병렬 결합이다.

  ⚠ 정직 기록 (노트 §8.5): (1) 웨이퍼/헤드 전도는 White 2003을 따라 무시(블래더 단열) —
  White 실측이 예측보다 17% 낮은 잔차가 이 항일 수 있다. (2) 슬러리 경로는 "출구 슬러리가
  패드 온도까지 데워진다"는 완전 열교환 가정(ṁc_p 한계). (3) L_pad는 데이터시트 두께(IC1000
  50 mil=1.27 mm)이며, 열이 실제 흐르는 유효 길이가 그보다 짧으면 G_pad는 커진다. 따라서
  이 모듈은 Θ의 confidence를 올리지 않는다 — 진단 필드 전용(engine.py S12 배당 패턴).

함수:
  friction_power_w(mu, P_pa, A_m2, V_mps)                     -> Q_f [W]
  slurry_conductance_w_k(flow_m3_s, rho, cp)                  -> ṁ·c_p [W/K]
  pad_conduction_conductance_w_k(k_pad, A_heated_m2, L_pad_m) -> k·A/L [W/K]
  rotating_disk_h_air(omega_rad_s, k_air, nu_air, a)          -> h [W/m²K]
  heated_annulus_area_m2(r_cc_m, r_wafer_m)                   -> 웨이퍼가 쓸고 가는 패드 고리 면적
  steady_state_heat_balance(...)                              -> HeatBalanceResult (ΔT_ss, 3분배)
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict

# ── 문헌 상수 (재현·기본값용; 팩이 값을 주면 호출자가 덮어쓴다) ─────────────
PAD_THERMAL_CONDUCTIVITY_W_MK = 0.02     # Shin et al. 2025 (White 2003 Eq.5도 0.02 사용)
NU_LAMINAR_COEFF_ISOTHERMAL_AIR = 0.3286  # Harmand et al. 2013 Table 1, n=0 정확해 (Pr=0.71)
RE_LAMINAR_LIMIT = 1.8e5                  # Harmand 2013 §2.1: 층류 상한 1.8e5~3.6e5 (보수적 하한)
AIR_K_W_MK = 0.026                        # 공기 열전도도 @~300 K (표준 물성표)
AIR_NU_M2_S = 1.5e-5                      # 공기 동점성계수 @~300 K
WATER_RHO_KG_M3 = 1000.0
WATER_CP_J_KGK = 4180.0


def friction_power_w(mu: float, pressure_pa: float, area_m2: float, velocity_mps: float) -> float:
    """마찰동력 Q_f = μ·P·A·V [W] (White 2003 Eq.1-3: P_mech = c_f·P_r·A·v)."""
    return mu * pressure_pa * area_m2 * velocity_mps


def slurry_conductance_w_k(flow_m3_s: float, rho_kg_m3: float = WATER_RHO_KG_M3,
                           cp_j_kgk: float = WATER_CP_J_KGK) -> float:
    """슬러리 엔탈피 수송 컨덕턴스 ṁ·c_p [W/K] (White 2003 Eq.9, R_s = (ṁc_p)^-1)."""
    if flow_m3_s <= 0:
        raise ValueError("슬러리 유량이 0 이하 — 컨덕턴스 정의 불가")
    return rho_kg_m3 * flow_m3_s * cp_j_kgk


def pad_conduction_conductance_w_k(k_pad_w_mk: float, area_heated_m2: float,
                                   pad_thickness_m: float) -> float:
    """패드 두께 방향 전도 컨덕턴스 k·A/L [W/K] (White 2003 Eq.4)."""
    if pad_thickness_m <= 0:
        raise ValueError("패드 두께가 0 이하")
    return k_pad_w_mk * area_heated_m2 / pad_thickness_m


def rotating_disk_reynolds(omega_rad_s: float, radius_m: float,
                           nu_m2_s: float = AIR_NU_M2_S) -> float:
    """국소 회전 레이놀즈수 Re_r = Ω·r²/ν (Harmand 2013)."""
    return omega_rad_s * radius_m ** 2 / nu_m2_s


def rotating_disk_h_air(omega_rad_s: float, k_air_w_mk: float = AIR_K_W_MK,
                        nu_air_m2_s: float = AIR_NU_M2_S,
                        a: float = NU_LAMINAR_COEFF_ISOTHERMAL_AIR) -> float:
    """회전원판 층류 대류계수 h = a·k·sqrt(Ω/ν) [W/m²K].

    Nu_r = h·r/k = a·Re_r^0.5 = a·r·sqrt(Ω/ν)  ⇒  h = a·k·sqrt(Ω/ν) (반경 상쇄,
    Harmand 2013 "층류에서 국소 h는 반경 무관"). 이 상관식은 공기(Pr≈0.71) 정지유체 속
    자유 회전원판의 것이며, 여기서는 **패드→공기** 채널에만 쓴다(같은 유체 — Pr 전이 없음).
    """
    if omega_rad_s <= 0:
        return 0.0
    return a * k_air_w_mk * math.sqrt(omega_rad_s / nu_air_m2_s)


def heated_annulus_area_m2(r_cc_m: float, r_wafer_m: float) -> float:
    """웨이퍼(반경 r_w, 중심거리 r_cc)가 한 회전에 쓸고 가는 패드 고리 면적
    π[(r_cc+r_w)² − (r_cc−r_w)²] = 4π·r_cc·r_w (White 2003 "ring 2 in~10 in" 방식)."""
    r_in = max(r_cc_m - r_wafer_m, 0.0)
    r_out = r_cc_m + r_wafer_m
    return math.pi * (r_out ** 2 - r_in ** 2)


@dataclass
class HeatBalanceResult:
    friction_power_w: float
    G_slurry_w_k: float
    G_pad_w_k: float
    G_air_w_k: float
    delta_T_ss_k: float
    delta_T_all_slurry_upper_bound_k: float
    h_air_w_m2k: float
    reynolds_edge: float
    laminar: bool

    @property
    def G_total_w_k(self) -> float:
        return self.G_slurry_w_k + self.G_pad_w_k + self.G_air_w_k

    def partition(self) -> Dict[str, float]:
        """정상상태 열 3분배 비율(합=1): 슬러리 / 패드 전도 / 공기 대류."""
        G = self.G_total_w_k
        return {"slurry": self.G_slurry_w_k / G, "pad": self.G_pad_w_k / G,
                "air": self.G_air_w_k / G}

    def describe(self) -> str:
        p = self.partition()
        return (f"Q_f={self.friction_power_w:.0f} W, G=(slurry {self.G_slurry_w_k:.2f} + "
                f"pad {self.G_pad_w_k:.2f} + air {self.G_air_w_k:.2f}) W/K → "
                f"ΔT_ss={self.delta_T_ss_k:.1f} K (전량슬러리 상한 "
                f"{self.delta_T_all_slurry_upper_bound_k:.1f} K); 분배 슬러리 {p['slurry']:.0%}/"
                f"패드 {p['pad']:.0%}/공기 {p['air']:.0%}")


def steady_state_heat_balance(Q_f_w: float, flow_m3_s: float, area_heated_m2: float,
                              pad_thickness_m: float, omega_platen_rad_s: float,
                              area_exposed_m2: float, pad_radius_m: float,
                              k_pad_w_mk: float = PAD_THERMAL_CONDUCTIVITY_W_MK,
                              rho_slurry: float = WATER_RHO_KG_M3,
                              cp_slurry: float = WATER_CP_J_KGK) -> HeatBalanceResult:
    """Q_f = (G_slurry + G_pad + G_air)·ΔT_ss 를 풀어 ΔT_ss와 3분배를 돌려준다.

    area_heated_m2: 패드 전도 면적(웨이퍼가 쓸고 가는 고리, White 2003).
    area_exposed_m2: 공기에 노출된 가열 패드 면적(고리 − 웨이퍼 footprint 권장).
    pad_radius_m: 층류 판정용 최외곽 반경(Re_r 최대).
    """
    G_s = slurry_conductance_w_k(flow_m3_s, rho_slurry, cp_slurry)
    G_p = pad_conduction_conductance_w_k(k_pad_w_mk, area_heated_m2, pad_thickness_m)
    h = rotating_disk_h_air(omega_platen_rad_s)
    G_a = h * area_exposed_m2
    Re_edge = rotating_disk_reynolds(omega_platen_rad_s, pad_radius_m)
    dT = Q_f_w / (G_s + G_p + G_a)
    return HeatBalanceResult(friction_power_w=Q_f_w, G_slurry_w_k=G_s, G_pad_w_k=G_p,
                             G_air_w_k=G_a, delta_T_ss_k=dT,
                             delta_T_all_slurry_upper_bound_k=Q_f_w / G_s,
                             h_air_w_m2k=h, reynolds_edge=Re_edge,
                             laminar=Re_edge < RE_LAMINAR_LIMIT)


# ── self-test: 문헌값 재현 ────────────────────────────────────────────────
def _self_test() -> bool:
    results = []
    IN = 0.0254
    # --- Test 1: White 2003 Eq.1-3 마찰동력 (8 in 웨이퍼, 6 psi, 3.14 ft/s, c_f 0.25/0.18) ---
    A8 = math.pi * (4 * IN) ** 2
    v = 3.14 * 0.3048
    P6 = 6 * 6894.757
    Q_hi = friction_power_w(0.25, P6, A8, v)
    Q_lo = friction_power_w(0.18, P6, A8, v)
    ok = abs(Q_hi - 320.95) < 2.0 and abs(Q_lo - 231.11) < 2.0
    results.append(("White 2003 Eq.3 P_mech 320.95 W(c_f .25) / 231.11 W(c_f .18)", ok,
                    f"{Q_hi:.2f} W / {Q_lo:.2f} W"))
    # --- Test 2: White 2003 Eq.5 패드 전도 41.44 W (k=.02, A=.19 m², ΔT=14 K, L=1.27 mm) ---
    G_p = pad_conduction_conductance_w_k(0.02, 0.19, 1.27e-3)
    q_cond = G_p * 14.0
    ok = abs(q_cond - 41.44) < 0.5
    results.append(("White 2003 Eq.5 q_cond = 41.44 W", ok, f"{q_cond:.2f} W (G_pad={G_p:.3f} W/K)"))
    # --- Test 3: White 2003 Eq.9 슬러리 컨덕턴스 17.40 W/K (4.17 mL/s, ρ 1.04, c_p 4.01) ---
    G_s = slurry_conductance_w_k(4.17e-6, 1040.0, 4010.0)
    ok = abs(G_s - 17.40) < 0.05
    results.append(("White 2003 Eq.9 ṁc_p = 17.40 W/K", ok, f"{G_s:.3f} W/K"))
    # --- Test 4: White 2003 Eq.10 에너지균형 ΔT_slurry 10.97 °C(232 W) / 16.07 °C(321.9 W) ---
    dT_lo = (232.0 - 41.44) / 17.40
    dT_hi = (321.9 - 41.44) / 17.40
    ok = abs(dT_lo - 10.97) < 0.05 and abs(dT_hi - 16.07) < 0.05
    results.append(("White 2003 Eq.10 ΔT 10.97 / 16.07 °C", ok, f"{dT_lo:.2f} / {dT_hi:.2f} °C"))
    # --- Test 5: 병렬 네트워크로 White 조건 자체정합 풀이 — 실측 9.1 °C와 ±30% 이내 ---
    # White 툴: 플래튼 1 rpm → G_air ≈ 0 (White도 무시). 싱크 공통 T_0 가정.
    r = steady_state_heat_balance(232.0, 4.17e-6, 0.19, 1.27e-3, 2 * math.pi / 60,
                                  0.19 - A8, 0.30, rho_slurry=1040.0, cp_slurry=4010.0)
    ok = abs(r.delta_T_ss_k - 9.1) / 9.1 < 0.30 and r.G_air_w_k < 0.5
    results.append(("네트워크 ΔT_ss(White 232 W) vs 실측 9.1 °C ±30%", ok,
                    f"ΔT_ss={r.delta_T_ss_k:.2f} K, G_air={r.G_air_w_k:.3f} W/K"))
    # --- Test 6: Harmand 2013 — h ∝ sqrt(Ω), 반경 무관; 93 rpm 250 mm 패드 층류 ---
    w93 = 93 * 2 * math.pi / 60
    h1, h2 = rotating_disk_h_air(w93), rotating_disk_h_air(2 * w93)
    Re = rotating_disk_reynolds(w93, 0.25)
    ok = abs(h2 / h1 - math.sqrt(2)) < 1e-9 and Re < RE_LAMINAR_LIMIT and 5 < h1 < 10
    results.append(("h_air ∝ sqrt(Ω), Re_r(93 rpm, r=0.25 m) 층류, h≈7 W/m²K", ok,
                    f"h={h1:.2f} W/m²K, Re_edge={Re:.2e}"))
    # --- Test 7: Shin 2025 조건 3분배 — 슬러리가 지배(>60%), 패드 전도 10~30%, 공기 <15% ---
    A200 = math.pi * 0.1 ** 2
    A_ring = heated_annulus_area_m2(0.14, 0.1)
    Qf = friction_power_w(0.30, 2 * 6894.757, A200, w93 * 0.14)
    s = steady_state_heat_balance(Qf, 150e-6 / 60, A_ring, 1.27e-3, w93, A_ring - A200, 0.25)
    p = s.partition()
    ok = p["slurry"] > 0.6 and 0.1 < p["pad"] < 0.3 and p["air"] < 0.15
    results.append(("Shin 2025 조건 3분배: 슬러리 지배, 패드 10~30%, 공기 <15%", ok, s.describe()))
    # --- Test 8: 네트워크 ΔT_ss < 전량슬러리 상한 (병렬 경로가 있으니 항상) ---
    ok = s.delta_T_ss_k < s.delta_T_all_slurry_upper_bound_k
    results.append(("ΔT_ss < 전량슬러리 상한", ok,
                    f"{s.delta_T_ss_k:.1f} < {s.delta_T_all_slurry_upper_bound_k:.1f} K"))

    print("=== cmp_theta_steady_state_heat_balance.py self-test ===")
    n_pass = 0
    for name, ok, detail in results:
        n_pass += bool(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}\n    {detail}")
    print(f"\n{n_pass}/{len(results)} PASS")
    return n_pass == len(results)


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_test() else 1)
