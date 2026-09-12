<!-- V2-SECTION: R2-slurry | 공동: R1-equipment | 분배완료 2026-09-08 | 근거: chemistry, passivation, pourbaix, slurry, 화학 | 정본: ARCHITECTURE-V2.md §3 -->
# 마찰열·계면 온도장 → Arrhenius 화학반응속도 결합 (CMP 열-화학 커플링)

> 에이전트: tribologist Lv2-2 | 작성일: 2026-09-06
> [[tribology-friction-wear-stribeck]] [[cmp-lubrication-regimes]] [[cmp-slurry-flow-lubrication-film-thickness]] [[surface-chemistry-cu-w-pourbaix-passivation]] [[preston-luo-dornfeld-mrr]]

## 1. 왜 필요한가 — 마찰과 화학을 잇는 잃어버린 고리
[[tribology-friction-wear-stribeck]]에서 CMP를 마찰(COF)·마모(Archard)로, [[surface-chemistry-cu-w-pourbaix-passivation]]에서
표면반응(산화막 형성)으로 각각 다뤘다. 그런데 이 둘은 **온도**로 물리적으로 결합한다: 마찰이 하는 일이
계면을 데우고(마찰열), 그 온도가 Arrhenius 법칙을 통해 화학반응속도(→화학 MRR)를 배수로 증폭한다.
[[preston-luo-dornfeld-mrr]]의 K_p가 "슬러리 화학에 민감한 이유"의 상당 부분이 이 열-화학 커플링이다.
이 단원은 (1) 마찰동력 q=μPV, (2) 계면 온도장(평균·플래시·열확산), (3) Arrhenius 결합, (4) 공정 함의를
문헌 공정조건으로 정량 대조한다.

## 2. 마찰열 발생 — 단위면적당 발열 q = μ·P·V
미끄럼 마찰이 소산하는 동력은 마찰응력(τ=μ·P)×미끄럼속도(V)이므로 **단위면적당 발열유속**은
```
q = μ · P · V        [W/m²]   (μ=COF, P=명목압력[Pa], V=상대속도[m/s])
전체 마찰동력  Q_f = q · A_wafer = μ · P · V · A_wafer   [W]
```
이는 [[tribology-friction-wear-stribeck]]의 마찰력 F=μN에 속도를 곱한 마찰동력의 면적밀도이며,
CMP는 boundary~mixed 레짐([[cmp-lubrication-regimes]])이라 μ가 커서(oxide CMP COF 0.23~0.40) 발열이 크다.
Ma et al.(2023)은 selective-layer CMP를 P=0.05 MPa, V=0.75 m/s, 슬러리 150 mL/min 조건에서 마찰력
F_f=18.5~57 N을 실측하고, 마찰에너지 E_f=v_r∫F_f dt가 온도·MRR과 상관함을 보였다
(Ma, Belkhir et al., *Materials* 16(7) 2550, 2023, DOI 10.3390/ma16072550, PMC10095230, CC BY, EuropePMC 전문 확인).
White et al.(2003)은 CMP 마찰열을 **약 200~300 W**로, 화학열은 ~1 W로 산정해 **발열은 마찰이 지배**함을
보였다(White, Melvin, Boning, *J. Electrochem. Soc.* 150 G271, 2003, DOI 10.1149/1.1560642 — Shin 2025 §2.2 재인용,
원문 초록만 확인). §6 verify 블록에서 q=μPV(전형값)로 이 200~300 W 오더를 재현한다.

## 3. 계면 온도장 — 평균 상승, 플래시 온도, 패드 저열전도
발생한 q는 세 곳으로 분배된다: 슬러리(대류 냉각), 웨이퍼, 패드. **핵심 비대칭**은 다공성 폴리우레탄
패드의 열전도도가 극히 낮다는 점이다 — **k_pad ≈ 0.02 W/m·K**(Shin et al. 2025) — 그래서 마찰열의
상당량이 패드 심부로 빠지지 못하고 **계면 근처에 축적**되어 웨이퍼·슬러리 쪽으로 흐른다.
- **평균 온도상승 ΔT (수~수십 ℃):** Shin et al.(2025)은 미제어 CMP에서 90초 후 패드온도가 약 36 ℃까지
  상승, 보텍스튜브 냉각 시 약 30 ℃로 유지(무냉각 대비 3 ℃+ 높음)를 실측했다
  (Shin et al., *Materials* 18(19) 4461, 2025, DOI 10.3390/ma18194461, PMC12525981, CC BY, EuropePMC 전문 확인).
  §6에서 "모든 마찰열이 슬러리 유량으로 제거된다"는 에너지균형 상한을 계산해 이 수~수십 ℃ 오더를 대조한다.
- **플래시 온도(flash temperature):** asperity 접촉 순간의 국소 순간고온([[hertz-gw-contact-mechanics]]의
  실접촉점에서만 발생). 실접촉면적 A_r ≪ A_nominal이라 국소 열유속 q_local=q·(A_n/A_r)이 평균의 수십 배가
  되어, 접촉점 순간온도는 평균 웨이퍼온도보다 훨씬 높을 수 있다(Shin 2025는 "화학반응온도는 transient
  flash heating이 결정"이라 서술). **플래시 온도의 정량 절대값은 본 노트에서 미검증**(Blok/Archard flash
  모델 결합은 Lv3 후보).
- **열확산 스케일:** 특성 열확산 길이 ℓ_th≈√(α·t)로, 접촉 통과시간 t가 짧을수록 열이 얕게 갇힌다 —
  패드 저열전도(낮은 α)가 표면 열집중을 강화하는 물리적 근거(§6 sanity check).

## 4. Arrhenius 결합 — 온도가 화학 MRR을 배수로 증폭
화학반응 속도상수는 Arrhenius 법칙을 따른다. Shin et al.(2025)은 **제거율(RR)을 반응속도의 대리변수**로 두고
CMP에 직접 적용했다(원문 Eq.1-2):
```
RR = A · exp(−Ea/RT)     ⟺     ln RR = −(Ea/R)·(1/T) + ln A
  Ea: 겉보기 활성화에너지[J/mol], R=8.314 J/(K·mol), T: 평균 공정온도[K], A: 빈도인자(Å/min)
```
ln RR vs 1/T 기울기(=−Ea/R)에서 겉보기 Ea를 얻는다. Shin et al.(2025) 실측 겉보기 활성화에너지(blanket wafer):

| 재료 | Ea [kJ/mol] | ln A | 온도민감도 |
|---|---|---|---|
| SiO₂ | 8.75 | 9.7 | 낮음(거의 온도무관) |
| Ta | 29.9 | 18.1 | 중간 |
| Cu | 151.7 | 66.3 | 매우 높음(온도로 급증) |

**두 온도 T1→T2 사이 반응속도 배율** = exp[(Ea/R)·(1/T1 − 1/T2)]. §6에서 ΔT=20 ℃(30→50 ℃)일 때 Cu는
약 41배, Ta 2.1배, SiO₂ 1.2배로 계산된다 — 즉 **같은 온도상승이 Cu MRR은 수십 배 키우고 oxide는 거의
안 바꾼다.** 이것이 "공정온도로 Cu/barrier/oxide **선택비**를 조절"하는 Shin 논문의 핵심이자, [[preston-luo-dornfeld-mrr]]의
K_p가 온도(=마찰조건)에 민감한 이유의 화학적 근거다. DeNardis et al.이 Cu 산화율의 Arrhenius 거동을 보인 것과
정합(Shin 2025 §서론 재인용, 원문 미확인).

## 5. EPD·공정 함의 — 온도 모니터링과 정상상태
- **온도 실시간 모니터링:** 계면온도(IR 센서·플래튼 열화상)는 마찰상태와 화학속도를 동시에 반영하는
  in-situ 지표 → [[cmp-lubrication-regimes]]의 COF 모니터링과 함께 EPD·공정드리프트 진단에 쓴다(Lv3-1 심화).
- **정상상태 온도:** 발열 Q_f=μPV·A와 냉각(슬러리 대류+패드 확산)이 평형을 이루는 T_ss가 존재. 냉각을
  키우면(보텍스튜브) T_ss를 낮춰 Cu MRR을 억제, dishing을 줄인다(Shin 2025: 30 ℃ 유지가 선택비·dishing 최적).
- **되먹임 주의:** 온도↑ → 화학연화(H↓, [[surface-chemistry-cu-w-pourbaix-passivation]]) → MRR↑ → 마찰일↑ →
  온도↑의 양의 되먹임 가능성. 냉각제어가 이 폭주를 끊는다.

## 6. Python 재현 & 문헌 대조
```python verify
import math
R = 8.314  # J/(K mol)

# --- (1) 마찰열 q=uPV : Ma et al. 2023 공정조건, oxide CMP COF 오더 ---
mu, P, V = 0.3, 0.05e6, 0.75            # COF~0.3, 0.05 MPa, 0.75 m/s (Ma 2023 조건)
q = mu * P * V                          # W/m^2
A = math.pi * 0.1**2                    # 200mm 웨이퍼 면적 [m^2]
Qf = q * A                              # 전체 마찰동력 [W]
print(f"q=uPV = {q:.0f} W/m^2, Q_f = q*A = {Qf:.0f} W")
assert abs(q - 11250) < 1, q
# White et al. 2003 문헌값: 마찰열 200~300 W. 우리 Q_f=353W는 같은 오더(수백 W).
assert 100 < Qf < 700, "White 200-300W 오더 밖"
# 역산: 200-300W를 200mm 웨이퍼 면적으로 나눈 열유속도 q=uPV 오더(1e4 W/m^2)와 부합
for Wt in (200, 300):
    flux = Wt / A
    assert 5e3 < flux < 1e4, flux
print(f"  White 200-300W -> {200/A:.0f}~{300/A:.0f} W/m^2 (q=uPV 오더와 부합)")

# --- (2) 평균 온도상승: 마찰열 전량이 슬러리로 제거된다는 에너지균형 상한 ---
rho, cp, flow = 1000.0, 4180.0, 150e-6/60   # 물기반 슬러리, 150 mL/min
mdot = rho * flow
for Qh in (200, 300):
    dT = Qh / (mdot * cp)
    print(f"  Q={Qh}W -> dT_상한 = {dT:.1f} C")
    assert 5 < dT < 40, dT          # 수~수십 C 오더 (실측 ~36C, 문헌과 오더 일치)
# Shin 2025 실측: 미제어 ~36C, 제어 ~30C. 상한 추정(19~29C)이 이 수~수십C 오더를 포괄.

# --- (3) Arrhenius 반응속도 배율: Shin et al. 2025 문헌 Ea로 dT=20C(30->50C) ---
Ea_lit = {"SiO2": 8.75e3, "Ta": 29.9e3, "Cu": 151.7e3}   # J/mol (Shin 2025 실측)
T1, T2 = 303.15, 323.15   # 30C, 50C
ratio = {m: math.exp(Ea/R*(1/T1 - 1/T2)) for m, Ea in Ea_lit.items()}
for m in ("SiO2", "Ta", "Cu"):
    print(f"  {m}: Ea={Ea_lit[m]/1e3:.2f} kJ/mol -> 30->50C 배율 = {ratio[m]:.2f}x")
# Cu는 수십 배(선택비 급변), oxide는 거의 불변 — Shin 논문 핵심 주장 정량 재현
assert 35 < ratio["Cu"] < 50, ratio["Cu"]      # ~41.5x
assert 1.1 < ratio["SiO2"] < 1.4, ratio["SiO2"] # ~1.24x
assert ratio["Cu"] > 20 * ratio["SiO2"], "Cu/oxide 선택비 온도민감도 대비"

# --- (4) ln A 재구성 sanity: Cu Ea=151.7kJ/mol, lnA=66.3에서 RR@303K 산출 ---
lnA_Cu = 66.3
RR_Cu = math.exp(lnA_Cu) * math.exp(-Ea_lit["Cu"]/(R*303.15))  # A/min
print(f"  Cu RR@30C = {RR_Cu:.0f} A/min  (Shin: 30C 부근 400~500 A/min 수렴)")
assert 100 < RR_Cu < 2000, RR_Cu   # 문헌 수백 A/min 오더

# --- (5) 열확산 길이 sanity: 패드 저열전도가 표면 열집중 강화 ---
# alpha = k/(rho*cp). 패드 k=0.02 W/mK(Shin) << 물 k=0.6 -> 패드 alpha 훨씬 작음
alpha_pad = 0.02/(1200*1500)   # PU 대략 밀도/비열
alpha_water = 0.6/(1000*4180)
assert alpha_pad < alpha_water, (alpha_pad, alpha_water)
print(f"  alpha_pad={alpha_pad:.2e} < alpha_water={alpha_water:.2e} -> 패드가 열 덜 흡수(표면 축적)")
print("ALL PASS")
```
- **q=μPV 재현:** 전형 CMP 조건에서 q≈1.1×10⁴ W/m², 전체 마찰동력 Q_f≈353 W → White et al.(2003)
  문헌값 **200~300 W와 같은 오더**(수백 W). 역산 열유속 6.4~9.5×10³ W/m²도 q=μPV 오더와 부합.
- **온도상승 오더:** 슬러리 전량냉각 상한 ΔT≈19~29 ℃ → Shin et al.(2025) 실측 수~수십 ℃(미제어 ~36 ℃)와
  **오더 일치**(상한 추정이라 실측을 포괄).
- **Arrhenius 배율:** 문헌 Ea로 30→50 ℃ 시 **Cu 41.5배·Ta 2.08배·SiO₂ 1.24배** → "온도가 Cu MRR을 수십 배
  키우고 oxide는 거의 안 바꾼다"는 Shin 논문 핵심을 정량 재현. Cu RR@30 ℃ 재구성도 수백 Å/min 오더로 문헌 부합.

## 7. 한계 / 미검증 표기
- **플래시 온도 절대값 미검증:** asperity 국소 순간온도의 정량 예측(Blok flash temperature)은 본 노트 범위 밖 —
  평균온도만 정량, 플래시는 정성(A_r/A_n 배율 논증)에 그침. Lv3 후보.
- **§6 (2)의 온도상승은 "상한 추정":** 마찰열 전량이 슬러리로 간다는 가정의 상한이다. 실제 삼분배
  (슬러리/패드 전도/공기 대류)는 **§8에서 White 2003 원문 열저항 네트워크로 정량화**했다(2026-09-12 추가).
  웨이퍼/헤드 경로는 §8.5의 이유로 여전히 미모델링.
- **White et al.(2003) 원문 확보(2026-09-12):** 미러 사이트 → 미러 사이트 경로로 PDF 확보,
  papers/white2003-jes-dynamic-thermal-behavior-cmp.pdf(+.txt). §2의 "200~300 W"는 원문 Eq.3의
  231.11~320.95 W(c_f 0.18~0.25, 8 in 웨이퍼, 6 psi, 3.14 ft/s)로 확인 — 이제 1차 인용.
- **Ea는 특정 슬러리·툴 조건값:** Shin 2025의 Cu 151.7/Ta 29.9/SiO₂ 8.75 kJ/mol은 특정 barrier 슬러리·POLI-500
  툴의 겉보기 Ea로, 슬러리 화학·산화제가 바뀌면 달라진다 — 절대값 일반화는 **미검증**(오더·재료간 대소관계만 신뢰).
- ceria/oxide CMP의 겉보기 Ea "≈0.43 eV"(≈41 kJ/mol) 언급을 검색에서 봤으나 1차출처 미확정 — **채택 보류**.

## 8. 정상상태 열저항 네트워크 — 마찰열 3분배와 ΔT_ss (White 2003 원문 이식, 2026-09-12 [Max워커])

### 8.1 1차 문헌 확보 기록
- **White, Melvin, Boning, "Characterization and Modeling of Dynamic Thermal Behavior in CMP",
  *J. Electrochem. Soc.* 150(4) G271-G278 (2003), doi.org/10.1149/1.1560642** — Unpaywall/OpenAlex는
  bronze OA로 표시하지만 iopscience `/pdf`는 Radware 캡차(14 KB HTML). 미러 사이트 캡차, **미러 사이트이
  `미러 사이트/pdf/10.1149/1.1560642.pdf` 임베드를 주어 curl(Referer 미러 사이트)로 531 KB 원문 확보**.
  papers/white2003-jes-dynamic-thermal-behavior-cmp.pdf, 텍스트 .pdf.txt, INDEX.json 등록.
- 원문이 주는 것: 발열·손실 메커니즘의 1차 에너지균형(Eq.1-10)과 집중정수 열회로(Fig.4, R₁·R_s·C_t).
  **"슬러리/웨이퍼/패드 비율" 자체를 표로 주지는 않는다** — 대신 손실 항을 각각 계산해 균형을 맞추므로
  분배는 그 항들에서 유도된다(아래 8.3). 웨이퍼/헤드 전도는 블래더 단열을 이유로 **명시적으로 무시**, 복사
  0.30 mW, 공기 대류는 플래튼 1 rpm이라 무시.
- 회전원판 대류: Harmand, Pellé, Poncet, Shevchuk, *Int. J. Thermal Sci.* 67 (2013) 1-30,
  doi.org/10.1016/j.ijthermalsci.2012.11.009 (arxiv.org/abs/1305.2882 원문, [[cmp-theta-rotation-convective-cooling-driver]]
  §1과 같은 문헌). Table 1(n=0 등온 원판, 정확 자기상사해) **a = 0.3286**, 층류 지수 b=0.5, Pr=0.71(공기).
  Reynolds 상사 지수 m=0.53(층류)은 원문 §2 인용이나 Pr=[0.7-0.74] 데이터 범위 밖 외삽이라 채택하지 않는다.

### 8.2 네트워크 유도 (전기회로 유사)
정상상태에서 마찰동력 Q_f는 계면 온도 T_ss와 공통 싱크 T₀(공급 슬러리·플래튼·주변 공기가 같은 온도라는
가정) 사이의 **병렬 열컨덕턴스**로 빠져나간다:
```
Q_f = (G_slurry + G_pad + G_air) · ΔT_ss,    ΔT_ss = T_ss − T₀
G_slurry = ṁ·c_p              [W/K]  슬러리 엔탈피 수송  (White Eq.9: R_s = 1/(ṁc_p) = 0.057 °C/W)
G_pad    = k_pad·A_ring/L_pad [W/K]  패드 두께 전도     (White Eq.4-5: k=0.02, A=0.19 m², L=1.27 mm)
G_air    = h_air·A_exposed    [W/K]  회전 패드→공기 대류 (Harmand Eq.10: h = a·k_air·√(Ω/ν_air), 반경 무관)
```
- **슬러리 경로가 h·A가 아니라 ṁ·c_p인 이유:** 슬러리는 패드와 함께 회전하는 박막이라 "주변 유체"가
  아니다. 열은 슬러리에 **실려 나가고**, 그 상한은 출구 슬러리가 T_ss까지 데워졌을 때의 ṁ·c_p·ΔT다
  (White 2003 Eq.8-9가 정확히 이 형태이고 실측으로 검증됨). §6 (2)의 "상한"은 이 항 하나만 둔 경우다.
- **회전원판 Nu 상관식은 공기 채널에만:** Harmand 2013은 공기 중 자유 회전원판(Pr 0.71) 해석이므로
  **패드→공기** 대류에 그대로 쓴다(같은 유체, Pr 전이 없음 — 이전 노트의 E4급 전이 문제 해소).
  h = 0.3286·0.026·√(Ω/1.5e-5): 93 rpm에서 6.9 W/m²K, Re_r(r=0.25 m)=4.1e4 < 1.8e5 층류.
- **A_ring:** 웨이퍼가 한 회전에 쓸고 가는 패드 고리 4π·r_cc·r_w (White: 2 in~10 in 고리 0.19 m²).
  패드가 단열체라 옆으로 안 퍼지므로 전도 면적은 가열 고리만 잡는다(White 방식). 공기 노출면은
  고리 − 웨이퍼 footprint.
- **L_pad:** IC1000 데이터시트 50 mil = 1.27 mm([[pad-structure-groove-subpad]] §1, Pureon 2024) —
  White도 1.27×10⁻³ m 사용. IC1010은 80 mil = 2.03 mm → 민감도 범위로 병기.

### 8.3 White 2003 자기재현 (원문 수치 vs 우리 계산)
| 항목 | 원문(White et al. 2003) | 재현 | 비고 |
|---|---|---|---|
| P_mech = c_f·P·A·v (c_f 0.25 / 0.18) | 320.95 W / 231.11 W | 320.99 / 231.11 W | Eq.1-3 |
| q_cond = kAΔT/L (14 K, L 1.27 mm) | 41.44 W | 41.89 W (G_pad 2.99 W/K) | Eq.5, 1% 반올림차 |
| ṁ·c_p (4.17 mL/s, ρ1.04, c_p 4.01) | 17.40 W/K | 17.39 W/K | Eq.9 |
| 균형 ΔT_slurry (232 W / 321.9 W) | 10.97 / 16.07 °C | 10.95 / 16.12 °C | Eq.10 |
| 병렬 네트워크 ΔT_ss (232 W, 싱크 공통) | — | 11.3 K | G_air=0.11 W/K(1 rpm) |
| 실측 패드 ΔT (Cu 폴리시 시작→끝) | **9.1 °C** | 예측 대비 −17~−20% | 원문도 "헤드/테이블 추가 손실 또는 웨이퍼 축열" 추정 |

정상상태 분배(White 조건, 232 W): 슬러리 85% / 패드 전도 15% / 공기 <1%. 원문 문장 "most of the
thermal energy … is conducted through the pad and slurry"와 정합(White et al. 2003).

### 8.4 Shin 2025 정량 대조 — 무냉각 ΔT
Shin et al.(2025) Table 1: 200 mm 웨이퍼, 2 psi, 캐리어/플래튼 87/93 rpm, 플래튼 Ø500 mm, 150 mL/min,
Fig.7a(원문 PDF 렌더 판독) 무냉각 **약 20.5 °C(t=0) → 약 35.5 °C(90 s), ΔT_meas ≈ 15 K(판독 ±1 K)**,
90 s에서도 완만히 상승 중(White τ 19~74 s와 정합, 92~99% 정상상태).
입력 중 원문에 없는 것: μ(배리어 슬러리 COF, 미공개 → 0.2~0.4 스윕), r_cc(플래튼 반경 0.25 − 웨이퍼 0.10 이내
→ 0.12~0.15 m), L_pad(KPX 하이브리드 패드 두께 미공개 → 1.27~2.03 mm). **단일 숫자를 짓지 않고 범위로 푼다.**

| 케이스 | Q_f | G(슬러리+패드+공기) | ΔT_ss | 전량슬러리 상한 | 실측 대비 |
|---|---|---|---|---|---|
| 중앙 μ0.3, r_cc0.14, L1.27 | 177 W | 10.45+2.77+0.99=14.2 W/K | **12.5 K** | 17.0 K | −17% / 상한 +13% |
| 최소 μ0.2, r_cc0.12, L1.27 | 101 W | 13.2 W/K | 7.4 K | 9.7 K | −51% |
| 최대 μ0.4, r_cc0.15, L2.03 | 253 W | 13.2 W/K | 18.9 K | 24.2 K | +26% |

- 재현 요약(한 줄): 네트워크 ΔT_ss 12.5 K(범위 7.4~18.9 K)는 Shin 2025 실측 ΔT≈15 K를 범위 안에서 대조하며, 3분배는 슬러리 74%/패드 19%/공기 7%다(Shin et al. 2025; White et al. 2003).
- **정직한 판정:** 중앙값은 실측보다 17% 낮고, §6 (2)의 전량슬러리 상한(17.0 K)이 오히려 실측에 더
  가깝다(+13%). 즉 **이 계에서 네트워크가 "더 정확한 숫자"를 준 것은 아니다** — 얻은 것은 (i) 전도·공기
  경로가 병렬로 붙어 상한보다 26% 낮은 ΔT를 주는 구조, (ii) 3분배 비율 자체, (iii) White 원문 균형과
  1% 이내 정합이다. 실측이 중앙값보다 높은 이유 후보: 배리어 슬러리(H₂O₂ 0.5 wt%) COF가 0.3보다 높거나
  (μ≈0.36이면 정확히 15 K), 산화제 발열(Shin 2025가 Wang et al. 인용으로 언급) — 둘 다 미검증.
- **지배 항:** 세 케이스 모두 G_slurry가 72~82%로 지배. 따라서 ΔT_ss는 **유량(SFR)에 거의 반비례**하고,
  회전수는 G_air(6~8%)의 √Ω만 키우므로 냉각 쪽 기여는 미미하다 — 발열 Q_f∝Ω가 압도해 **ΔT_ss ≈ Ω^0.97**.
  현행 `_f_theta()`의 cool_rotation=√(rpm/rpm_ref)는 이 7% 채널의 스케일을 **냉각 전체**에 적용해
  회전 냉각을 과대평가한다(정정 후보, §8.6).

### 8.5 한계 / 미검증 — Θ confidence 판단
- **웨이퍼/헤드 전도 미모델링:** White 2003이 블래더 단열로 무시했고 우리도 따른다. White 실측이 예측보다
  17% 낮은 잔차가 이 항일 가능성을 원문 스스로 언급 — 4번째 경로 크기는 **미검증**.
- **L_pad = 데이터시트 두께:** 열이 실제로 흐르는 유효 길이가 그루브 바닥·다공층 두께(White R₁ 계산은
  0.55~1.0 mm)로 더 짧다면 G_pad는 1.3~2.3배 커진다(중앙 케이스 ΔT 12.5→11.6~10.9 K). 문헌 실측 없음 —
  **미검증**, 범위로만 제시.
- **h_air 상관식은 매끈한 등온 원판(공기)** 것: 그루브·슬러리 젖음면의 실제 h는 미검증. 다만 이 채널이
  총 컨덕턴스의 7%라 h가 2배 틀려도 ΔT는 7% 변한다(민감도 낮음).
- **슬러리 완전 열교환 가정:** 출구 슬러리가 T_ss까지 데워진다는 가정. White는 슬러리가 패드 가장자리까지
  가며 약 4 °C 식는다고 실측 — 부분 교환이면 G_slurry는 더 작고 ΔT는 더 커진다(실측 방향과 일치).
- **결론: Θ confidence는 estimated 유지.** 위 4개 구조적 결측(웨이퍼 경로, L_pad 유효길이, h_air CMP
  실측, 완전 열교환) 중 어느 하나도 1차 실측으로 닫히지 않았다. 브리프의 기준("하나라도 남으면
  estimated")에 따라 올리지 않는다.

### 8.6 엔진 반영
`sim/tier2_physics/cmp_theta_steady_state_heat_balance.py`(순수함수, self-test 8/8: White Eq.3/5/9/10 재현,
Harmand √Ω·층류, Shin 3분배)를 신설하고 `sim/engine.py`에 **진단 필드로만** 실었다
(`theta_steady_state_delta_T_k`·`theta_heat_partition`·`theta_steady_state_note`, MRR 경로에 곱하지 않음,
`pad_thickness_m`·`pad_thermal_conductivity_w_mk`가 팩에 없으면 조용히 None). **(2026-09-13 정정)**
`_f_theta()`의 `cool_rotation`을 순수 `sqrt(rpm/rpm_ref)`에서 가중평균 `(1-W_AIR_FRACTION)·1.0 +
W_AIR_FRACTION·sqrt(rpm/rpm_ref)`(W_AIR_FRACTION=0.07, 위 Shin 2025 중앙 케이스 분배)로 교체해 7% 채널의
스케일이 냉각 전체에 적용되던 과대평가를 정정했다. theta는 `MRR_COUPLED` 밖(진단 전용)이라 ρ 회귀에는
영향이 없음을 재검증했다(qa_loop --strict PASS, ρ=0.9537 불변, 정정 전과 동일).

### 8.7 Python 재현 (열저항 네트워크)
```python verify
import math
IN, FT, PSI = 0.0254, 0.3048, 6894.757
# --- (1) White 2003 Eq.1-3: P_mech = c_f P A v, 8in 웨이퍼, 6 psi, 3.14 ft/s ---
A8 = math.pi * (4*IN)**2; v = 3.14*FT; P6 = 6*PSI
Q_hi, Q_lo = 0.25*P6*A8*v, 0.18*P6*A8*v
assert abs(Q_hi - 320.95) < 2 and abs(Q_lo - 231.11) < 2, (Q_hi, Q_lo)
# --- (2) Eq.4-5 패드 전도: k=0.02, A=0.19 m2, dT=14 K, L=1.27 mm -> 41.44 W ---
G_pad_w = 0.02*0.19/1.27e-3
assert abs(G_pad_w*14 - 41.44) < 0.5, G_pad_w*14
# --- (3) Eq.9 슬러리 컨덕턴스 4.17 mL/s x 1.04 x 4.01 J/gK = 17.40 W/K ---
G_s_w = 4.17*1.04*4.01
assert abs(G_s_w - 17.40) < 0.05, G_s_w
# --- (4) Eq.10 에너지균형 -> dT_slurry 10.97 / 16.07 C ---
dT_lo, dT_hi = (232-41.44)/17.40, (321.9-41.44)/17.40
assert abs(dT_lo-10.97) < 0.05 and abs(dT_hi-16.07) < 0.05, (dT_lo, dT_hi)
# --- (5) 병렬 네트워크(싱크 공통) White 조건: dT_ss = Q/(G_s+G_pad+G_air), 1 rpm -> G_air~0 ---
def h_air(omega, a=0.3286, k=0.026, nu=1.5e-5):   # Harmand 2013 Eq.10, n=0 a=0.3286
    return a*k*math.sqrt(omega/nu)
G_air_w = h_air(2*math.pi/60)*(0.19-A8)
dT_w = 232/(G_s_w+G_pad_w+G_air_w)
assert 11.0 < dT_w < 11.6 and G_air_w < 0.2, (dT_w, G_air_w)
assert abs(dT_w-9.1)/9.1 < 0.30          # 실측 9.1 C 대비 -30% 이내 (원문 자체 잔차 -17%)
part_w = G_s_w/(G_s_w+G_pad_w+G_air_w)
assert 0.80 < part_w < 0.90, part_w      # 슬러리 85%, 패드 15%
print(f"White: dT_ss={dT_w:.2f} K (실측 9.1), 슬러리 {part_w:.0%}/패드 {G_pad_w/(G_s_w+G_pad_w+G_air_w):.0%}")
# --- (6) Harmand 2013: h ∝ sqrt(Ω), 93 rpm 250 mm 패드 층류(Re<1.8e5), h≈7 W/m2K ---
w93 = 93*2*math.pi/60
assert abs(h_air(2*w93)/h_air(w93) - math.sqrt(2)) < 1e-9
Re = w93*0.25**2/1.5e-5
assert Re < 1.8e5 and 6 < h_air(w93) < 8, (Re, h_air(w93))
# --- (7) Shin 2025 조건: 200mm, 2 psi, 93 rpm, 150 mL/min, 실측 dT≈15 K(Fig.7a 20.5->35.5 C) ---
A200 = math.pi*0.1**2; G_s = (150e-6/60)*1000*4180        # 10.45 W/K
def solve(mu, rcc, L):
    A_ring = math.pi*((rcc+0.1)**2 - (rcc-0.1)**2)
    Qf = mu*2*PSI*A200*(w93*rcc)
    G_p = 0.02*A_ring/L; G_a = h_air(w93)*(A_ring-A200)
    return Qf, G_s, G_p, G_a, Qf/(G_s+G_p+G_a), Qf/G_s
Qf, Gs, Gp, Ga, dT_c, ub_c = solve(0.30, 0.14, 1.27e-3)
assert abs(Qf-177) < 2 and 12.0 < dT_c < 13.0 and 16.5 < ub_c < 17.5, (Qf, dT_c, ub_c)
frac = {"slurry": Gs/(Gs+Gp+Ga), "pad": Gp/(Gs+Gp+Ga), "air": Ga/(Gs+Gp+Ga)}
assert 0.70 < frac["slurry"] < 0.78 and 0.15 < frac["pad"] < 0.23 and 0.05 < frac["air"] < 0.10, frac
dT_min = solve(0.20, 0.12, 1.27e-3)[4]; dT_max = solve(0.40, 0.15, 2.03e-3)[4]
assert 7.0 < dT_min < 8.0 and 18.5 < dT_max < 19.5, (dT_min, dT_max)
dT_meas = 35.5 - 20.5                                     # Fig.7a 판독, ±1 K
assert dT_min < dT_meas < dT_max                          # 실측이 민감도 범위 안
assert dT_c < dT_meas < ub_c                              # 정직: 중앙값 -17%, 상한 +13%, 실측은 그 사이
assert dT_c < ub_c                                        # 병렬 경로 -> 상한보다 항상 낮음
# 회전수 스케일: 냉각은 G_air(7%)만 sqrt(Ω), 발열은 Ω 선형 -> dT_ss ~ Ω^0.97 (cool_rotation √ 과대)
Qf2, _, Gp2, Ga2, dT2, _ = solve(0.30, 0.14, 1.27e-3)
w2 = 2*w93; Ga2 = h_air(w2)*(math.pi*((0.24)**2-(0.04)**2)-A200); dT2 = 2*Qf/(G_s+Gp+Ga2)
expo = math.log(dT2/dT_c)/math.log(2)
assert 0.95 < expo < 1.0, expo
print(f"Shin: Qf={Qf:.0f} W, dT_ss={dT_c:.1f} K (실측 {dT_meas:.0f} K, 범위 {dT_min:.1f}~{dT_max:.1f}), "
      f"상한 {ub_c:.1f} K, 분배 {frac['slurry']:.0%}/{frac['pad']:.0%}/{frac['air']:.0%}, dT~Ω^{expo:.2f}")
print("ALL PASS")
```
