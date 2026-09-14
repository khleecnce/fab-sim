# FabSim 트라이볼로지 계열 모듈 — 이론식·출처 추출 보고

(코드 독스트링에서 실제 확인된 식만 기재. self-test 실행 결과 병기.)

---

## 1. tribology_basics.py — Archard 마모식 · Hersey/Sommerfeld 수 · Stribeck 곡선

**목적**: 트라이볼로지 3대 기초식(Archard, Hersey/Sommerfeld, Stribeck)을 수치로 재현·검증.

**지배방정식**
- Archard 마모부피: `V = k·W·L/H`
- Archard 마모깊이(면적당): `V/A = k·P·L/H` → **Preston 식과 구조 동일, Kp ≈ k/H**
- Hersey 수: `H_num = η·N/P`
- CMP Sommerfeld 수: `So = η·V/(P·δ_eff)` (무차원)
- 정성 Stribeck: `f = exp(-α·H)`, α=50 → `COF = f·μ_bl + (1-f)·(c_hydro·H) + μ_floor`
  (μ_bl=0.15, c_hydro=0.02, μ_floor=0.001)

**기호**: k 무차원 마모계수 / W 수직하중[N] / L 미끄럼거리[m] / H 경도[Pa] / P 명목압력[Pa] /
η 점도[Pa·s] / N 속도(회전수 1/s 또는 선속도) / V 상대속도[m/s] / δ_eff 유효막두께[m] / f 고체-고체 접촉분율.

**입력→출력**: (k,W,L,H)→V[m³]; (k,P,L,H)→깊이[m]; (η,V,P,δ_eff)→So; H_num→COF.

**출처 (독스트링 '지식 근거' 원문)**
- J.F. Archard (1953) *J. Appl. Phys.* 24, 981. V = k·W·L/H
  (2차 검증: DoITPoMS 'Wear' TLP, Cambridge; Encyclopedia MDPI "Archard's Law" 2024)
- Stribeck/Hersey: STLE Lubrication Fundamentals (2022); tribonet.org
- CMP Sommerfeld: Wu & Liao (2016) IntechOpen ch.52631; Philipossian CMP Stribeck

**가정·한계**: Hersey 수는 관례에 따라 차원이 달라져 무차원이 아닐 수 있음(오더 확인용).
Sommerfeld는 문헌마다 표기 상이 — 차원상 `ηV/(Pδ_eff)` 채택. Stribeck 모델은 **정성 모델**이고
α=50은 정성 파라미터. 10/10 PASS (예: CMP 전형조건 So≈1e-3, Stribeck COF 최소점 내부 존재).

---

## 2. cmp_lubrication_regime.py — 윤활 레짐 판별 (Stribeck/Sommerfeld/λ)

**목적**: CMP 조건이 경계/혼합/유체윤활 중 어디인지 So와 λ로 판정.

**지배방정식**
- 유효 유체두께: `δ_eff = α·Ra + (1-α)·δ_groove`
- **CMP Sommerfeld: `So = μ·U/(p·δ_eff)`**
- 유체역학 특성길이: `ℓ_hd = μ·U/p` [m] → 항등식 `So = ℓ_hd/δ_eff`
- **막두께비 λ = h_film/σ**
- **레짐 경계: λ<1 boundary, 1≤λ<3 mixed, λ≥3 hydrodynamic(full-film)**
- 정성 COF: `f = exp(-α_tr·So)` (α_tr=40) → `COF = f·μ_bl + (1-f)·c_hydro·So + floor`
  (μ_bl=0.30, c_hydro=8.0, floor=0.002)

**기호**: μ 슬러리 점도[Pa·s] / U 상대속도[m/s] / p 압력[Pa] / Ra 패드 raised 평균거칠기[m] /
δ_groove groove 깊이[m] / α raised(접촉)면적 비율(0~1) / σ 합성 RMS 거칠기[m] / h_film 최소유체막두께[m].

**핵심 논증(독스트링)**: ℓ_hd = μU/p 는 CMP 전형조건에서 ~수십 nm 로 Ra(~µm)보다 2~3오더 작다
→ λ ≪ 1 → boundary/mixed. δ_eff ≈ σ 일 때 So ≈ ℓ_hd/σ ≈ λ.

**실측 재현(self-test 실행)**: μ=1e-3 Pa·s, U=0.75 m/s, p=3 psi(20.7 kPa), Ra=5 µm →
**So=7.25e-3, ℓ_hd=36.3 nm, λ=7.25e-3 → boundary, COF≈0.24** (문헌 oxide CMP 0.23~0.40 범위 내). 10/10 PASS.

**출처 (원문)**
- CMP Sommerfeld: Philipossian et al., US20110076924A1 "Method of determining the lubrication mechanism in CMP" (Google Patents, 공개); Wu & Liao (2016) IntechOpen ch.52631 (오픈액세스)
- λ 경계: Bhushan, *Introduction to Tribology* 2013; tribonet.org — **2차 인용, 경계값은 관례**
- CMP COF 오더 oxide ~0.23–0.40 (boundary): "Physics of the COF in CMP" (ResearchGate 315672761 스니펫, **2차 인용**)

**한계**: groove 가중항 관례는 문헌마다 상이 — **미검증**. λ 경계값 1/3은 관례.

---

## 3. friction_cof_epd.py — 마찰기반 종점검출(EPD) 신호모델 ★COF↔모터전류 사슬

**목적**: 전단력→토크→모터동력/전류 사슬과 계단검출(EPD) 알고리즘, 검출지연·과연마 산술.

**마찰신호 사슬 (노트 §2)**
- 수직력 `F_n = P·A` [N]
- 전단력 `F_s = μ·P·A` [N] (**Amontons 법칙**)
- **COF `μ = F_s/F_n`** ← 힘센서법 EPD의 산출식
- 플래튼 저항토크 `τ = F_s·r_c` [N·m]
- 모터 마찰동력 `P_motor = τ·ω` [W]
- **모터전류 `I = τ/K_t` [A]** (DC/BLDC 비례식)

**핵심 항등식(독스트링 §2)**: `τ·ω = F_s·r_c·(V/r_c) = F_s·V = μ·P·V·A = q·A = Q_f`
→ **모터가 마찰을 이기며 쓰는 동력 == 계면 마찰발열**. 즉 EPD 신호와 발열이 같은 물리량의 두 얼굴이다.
(self-test §6(2): P=3psi, A=π·0.15², V=0.70 m/s, μ=0.4, r_c=0.20 m → τ, P_fric = Q_f ≈ 수백 W, 일치 오차<1e-6)

**종점검출 신호처리 (§3, §4)**
- 계단 대비: `ΔP = baseline - after`, `contrast = ΔP/baseline`
- 이동평균: 창 길이 `window = 2N+1`; centered `y[i]=mean(x[i-N:i+N+1])`, causal `y[i]=mean(x[i-2N:i+1])`
- 계단검출: `baseline = mean(x[:w])`, `threshold = threshold_fraction·|baseline|`, 편차가 임계 초과 상태가 min_persist 샘플 지속되는 첫 인덱스
- **검출지연 `T = N/R` [s]**
- **과연마 `= T·RR/60` [nm]**
- 설계지침: `threshold_fraction ≈ contrast/2` (≈0.027) — 평활 후 계단 50% 교차점 포착

**기호**: A 웨이퍼 면적[m²] / r_c 웨이퍼 중심의 플래튼축 기준 반경[m] / ω 각속도[rad/s] /
K_t 모터 토크상수[N·m/A] / N half_span[샘플] / R 샘플링 주파수[Hz] / RR 제거율[nm/min].

**문헌 재현값 (self-test 8/8 PASS)**
- Li 2017: 30,300 → 28,670 W ⇒ **ΔP=1630 W, contrast≈5.4%**
- N=60(121점 MA), R=12.15 Hz ⇒ **지연 4.94 s (<5 s)**, TEOS RR=229 nm/min ⇒ **과연마 18.8 nm (<20 nm)**
- 합성신호 종단검증: causal MA 검출 idx == T+N (±3 샘플)로 이론지연 재현; 계단 없는 잡음 → None(오검출 0)
- Headley 2019: r(PMC,전단력)=0.955 (R²=0.916) > r(PMC,COF)=0.758 (R²=0.608)

**출처 (원문)**
- Li, Lu, Luo, *Micromachines* 8(6) 177, 2017, doi 10.3390/mi8060177, PMC6190379
- Headley et al., *ECS JSST* 8(10) P634, 2019, doi 10.1149/2.0251910jss — 특정 툴/슬러리 케이스평균

**가정·한계 (독스트링 그대로)**
- K_t, r_c, 플래튼/캐리어 토크분배, baseline(베어링·리테이너링·컨디셔너)은 모두 **장비 종속·절대값 미검증**. `motor_current()`는 비례식만 제공, 절대전류 예측 안 함.
- 재료별 COF 절대값 표 1차 미확보. μ=0.4는 W CMP boundary 대표값(0.1~0.7) **가정**이며 전이방향(상승/하강)의 정량 대소는 미검증 → 그래서 `detect_step_transition()` 기본 방향이 **"any"**.
- Li 2017 값은 해당 툴/스택(Cu/Ti/TEOS) 실측 — 소신호(~5%)·지연-과연마 구조만 일반화 가능.
- `synthetic_transition_signal()`은 **실측 재현이 아님** — 알고리즘 검증용 합성신호(이상 계단 + 가우시안 백색잡음).
- Recipe가 단발 런 스냅샷이라 시계열 스키마가 없어 **engine.py/models.py 미등록** 순수함수 라이브러리.

---

## 4. frictional_heating_arrhenius.py — 마찰열 → 계면온도 → Arrhenius 화학반응속도 ★커플링 경로

**목적**: "온도가 화학반응속도(→화학 MRR)를 몇 배 바꾸는가"만 답하는 순수 함수 묶음.

**커플링 사슬 (q → Q_f → ΔT → T_ss → 반응속도 배율)**
1. 마찰 열유속: **`q = μ·P·V` [W/m²]**
2. 마찰동력: `Q_f = q·A` [W]
3. 온도상승 **상한**: `ΔT = Q_f/(ṁ·c_p)`, `ṁ = ρ·flow` — 마찰열 전량이 슬러리 유량으로 제거된다는 에너지균형
4. 정상상태 온도: `T_ss = T_ref + ΔT`
5. Arrhenius 속도: **`RR = A·exp(-Ea/RT)`**, 코드상 `exp(lnA)·exp(-Ea/(R·T))`
6. **속도 배율: `RR(T2)/RR(T1) = exp[(Ea/R)·(1/T1 - 1/T2)]`** — lnA가 상쇄되어 배율은 빈도인자와 무관

**기호**: μ COF[-] / P 압력[Pa] / V 상대속도[m/s] / A 면적[m²] / ρ 슬러리 밀도[kg/m³] /
c_p 비열[J/kg·K] / flow 유량[m³/s] / Ea 활성화에너지[J/mol] / R = 8.314 J/(K·mol) / T [K].

**문헌 상수 (Shin et al. 2025, 재현 검증용 참조표)**
| 재료 | Ea [J/mol] | lnA |
|---|---|---|
| SiO₂ | 8.75e3 | 9.7 |
| Ta | 29.9e3 | 18.1 |
| Cu | 151.7e3 | 66.3 |

패드 열전도도 `k_pad = 0.02 W/m·K` (Shin et al. 2025).

**출처 (원문)**
- 지식 근거: knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md §2-4-6
- Arrhenius 상수: **Shin et al. 2025, *Materials* 18(19) 4461, DOI 10.3390/ma18194461**

**가정·한계 (독스트링 그대로)**
- 절대 온도값 T_ss는 **"슬러리 전량냉각 상한"이라는 명시된 근사**(§6 (2)). 실제 삼분배(슬러리/웨이퍼/패드) 비율은 **미검증** — 노트 §7에 그대로 남김.
- μ·P·V를 어디서 가져올지는 **호출자(엔진/chemistry.py) 책임**. 이 모듈은 Recipe/팩을 모르며 입력값을 검증하지 않는다.
- 참조표 dict는 chemistry.py/pack에서 쓰지 않는다(코드가 진실의 원천이 되어 팩을 우회하지 않도록).

> **면접용 한 문장**: μ가 Stribeck/실측에서 정해지면 q=μPV로 열유속이 나오고, 에너지균형으로 ΔT가 나오며,
> Arrhenius 지수항이 ΔT를 화학 MRR 배율로 바꾼다 — 즉 마찰계수가 기계 MRR뿐 아니라 **화학 MRR의 온도 레버**이기도 하다.

---

## 5. cmp_theta_steady_state_heat_balance.py — Θ 정상상태 열저항 네트워크

**목적**: 마찰열 Q_f의 슬러리/패드/공기(+웨이퍼) 분배와 계면 온도상승 ΔT_ss 계산.

**지배방정식 (전기회로 유사 — 병렬 열컨덕턴스)**
```
Q_f = (G_slurry + G_pad + G_air + G_wafer)·ΔT   ⇒  ΔT_ss = Q_f / ΣG
Q_f      = μ·P·A·V                       [W]    (White 2003 Eq.1-3: P_mech = c_f·P_r·A·v)
G_slurry = ṁ·c_p = ρ·flow·c_p            [W/K]  (White 2003 Eq.9, R_s = 1/(ṁc_p))
G_pad    = k_pad·A_heated/L_pad          [W/K]  (White 2003 Eq.4-5)
G_air    = h_air·A_exposed               [W/K]
h_air    = a·k_air·sqrt(Ω/ν_air)         [W/m²K] (Nu_r = h·r/k = a·Re_r^0.5, Re_r = Ω·r²/ν)
G_wafer  = A_wafer / R''_path,  R''_path = t_Si/k_Si + t_film/k_film + t_bladder/k_bladder
A_heated(고리) = π[(r_cc+r_w)² − (r_cc−r_w)²] = 4π·r_cc·r_w
전량슬러리 상한 ΔT = Q_f / G_slurry
```
층류에서 b=0.5이므로 **h는 반경 무관**(반경 상쇄).

**상수**: k_pad=0.02 W/m·K (Shin 2025 / White Eq.5) / a=0.3286 (Harmand 2013 Table 1, n=0 정확해, Pr=0.71) /
Re 층류 상한 1.8e5 / k_air=0.026, ν_air=1.5e-5 (@300K) / k_Si=142 W/m·K / t_Si 725 µm(200mm)·775 µm(300mm) /
k_PU film 0.0216 W/m·K / k_bladder 0.026(공기)·0.61(물).

**출처 (원문)**
- **White, Melvin, Boning, *J. Electrochem. Soc.* 150(4) G271 (2003), DOI 10.1149/1.1560642** — 원문 확보(papers/white2003-jes-...pdf)
- **Harmand et al., *Int. J. Thermal Sci.* 67 (2013) 1-30, arXiv:1305.2882** — 회전원판 층류, Nu_r = a·Re_r^0.5, 등온 원판 a=0.3286
- **Shin et al., *Materials* 18(19) 4461 (2025), DOI 10.3390/ma18194461** — k_pad≈0.02, 실측 ΔT(Fig.7a: ~20.5→~35.5 °C, 90 s)
- Glassbrenner & Slack, *Phys. Rev.* 134 A1058 (1964), doi:10.1103/PhysRev.134.A1058 — 순수 Si k @300K
- SEMI M1 (웨이퍼 공칭 두께); Sparks, NBSIR 82-1664 (1982), doi:10.6028/nbs.ir.82-1664 Table 4 (PU 폼 k)

**재현 검증 (12/12 PASS)**: White Eq.3 P_mech 320.95 W(c_f=.25)/231.11 W(c_f=.18);
Eq.5 q_cond=41.44 W; Eq.9 ṁc_p=17.40 W/K; Eq.10 ΔT 10.97/16.07 °C;
네트워크 ΔT_ss vs 실측 9.1 °C ±30%; h ∝ sqrt(Ω) 및 93 rpm/r=0.25 m 층류 h≈7 W/m²K;
Shin 조건 3분배 = 슬러리 지배(>60%)/패드 10~30%/공기 <15%.

**가정·한계 (§8.5 정직 기록)**
1. 웨이퍼/헤드 전도는 White 2003을 따라 무시(블래더 단열) — White 실측이 예측보다 17% 낮은 잔차가 이 항일 수 있음.
2. 슬러리 경로는 "출구 슬러리가 패드 온도까지 데워진다"는 완전 열교환 가정(ṁc_p 한계).
3. L_pad는 데이터시트 두께(IC1000 50 mil=1.27 mm) — 유효 전도길이가 더 짧으면 G_pad는 커짐.
4. 세 싱크(공급 슬러리·플래튼·공기)가 모두 같은 온도 T_0라는 병렬 결합 가정.
5. k_film 기본값은 단열 PU 폼 값이라 **하한 앵커** — G_wafer 기본 반환은 하한 추정.
6. 이 모듈은 Θ의 confidence를 올리지 않는다 — **진단 필드 전용**.
7. §9.4: 웨이퍼 채널은 총 컨덕턴스의 2.5~8.6%뿐이고 채널 추가 시 ΔT가 오히려 내려가 Shin 실측(15 K)과 더 벌어짐 → 잔차 원인 아님(방향 검사로 명시).

---

## 6. particle_chemomechanical_synergy.py — 단일 입자 접촉역학 + 화학-기계 시너지

**목적**: 연마입자 1개의 Hertz 탄성접촉·소성 plowing과, 화학연화(H↓)가 제거체적을 몇 배 키우는지 정량화.

**지배방정식**
- 등가탄성계수: `1/E* = (1-ν₁²)/E₁ + (1-ν₂²)/E₂`
- Hertz 탄성접촉: `a = (3FR/4E*)^(1/3)`, `δ = a²/R`, `p_max = 0.4·(E*²F/R²)^(1/3)`
- 소성 plowing: `F = H·π·a_p²` ⇒ `a_p = sqrt(F/(πH))`, `δ_p = a_p²/(2R) = F/(2πRH)`,
  홈 단면적 `A_f = (4/3)·sqrt(2R)·δ_p^1.5`
- 시너지 증폭: `depth_ratio = δ_soft/δ_hard`, `volume_ratio = A_soft/A_hard`
  → **δ ∝ 1/H, A_f ∝ H^-1.5** (H 4배↓ → 깊이 4배, 체적 8배), 하중 2배 → 체적 2^1.5배

**기호**: F 입자당 하중[N] / R 입자 반경[m] / E* 등가탄성계수[Pa] / a 접촉반경[m] / δ 압입깊이[m] /
p_max 최대 접촉응력[Pa] / H 경도[Pa] / A_f plowing 홈 단면적[m²].

**재현값 (5/5 PASS)**: E*(SiO₂-SiO₂, E=73 GPa, ν=0.17)=37.6 GPa; F=50 nN, R=50 nm →
p_max≈1.22 GPa, δ≈0.271 nm (접촉응력 GPa 오더, 압입 sub-nm 오더).

**출처**: knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md §2(Hertz), §3(탄성/소성 전이), §4(화학연화→plowing 체적 증폭).

**가정·한계 (독스트링 그대로)**
- 입자당 하중 F(수 nN~수백 nN)는 활성입자 통계에서 나오는 값 — 오더만 채택, 절대값은 실측 캘리브레이션 대상, **미검증**.
- 경도 H(SiO₂ 8-9 GPa, Cu 1-2 GPa, 연화막 <1 GPa)는 나노압입 **2차 인용 오더값**. §4 시너지 배수는 H 비율에 대한 해석적 결과라 정확하지만 실제 연화 정도는 슬러리별 미검증.
- **Luo-Dornfeld MRR ∝ P^0.5·V의 지수는 원문(유료) 폐형식 유도를 직접 재현 못함** — DOI 실존확인 + 2차 인용만. 이 모듈은 미시 구성요소(단일입자 소성 plowing)만 독립 재현.
- A_f 근사(구형 압자, δ≪R)는 **절삭효율 1**(파낸 것 전부 제거) 가정 — ploughing vs cutting 구분 미해결.
- Preston Kp로의 정량 연결식 없음 → engine/models.py 미등록.

---

## 7. electrical_thickness_extraction.py — Cu CMP 잔류두께의 전기적(선저항) 추출

**목적**: 선저항 R에서 Cu 잔류두께를 역산하고, 라이너 병렬·dishing 보정 오차를 정량화.

**지배방정식**
- 기본: `R = Rs·L/W`, `T = ρ·L/(R·W)`
- **라이너 보정: `T_M = ρ_Cu·L/(R·(W - 2·T_L)) + T_L`**
- 라이너 병렬 저항비: `R_L/R_Cu = (ρ_L/ρ_Cu)·(A_Cu/A_L)`,
  `A_Cu = (T_M - T_L)(W - 2T_L)`, `A_L = 2·T_M·T_L + (W - 2T_L)·T_L`
- 라이너 무시 시 상대오차: `1/(1 + R_L/R_Cu)`
- **dishing 저항증가율 [%]: `100·(1/(1 - seg/(w·t)) - 1)`**,
  `seg = R_d²·asin(w/2R_d) - (w·R_d/2)·sqrt(1-(w/2R_d)²)` (원호 segment 면적)

**기호·단위**: R[Ω] / L, W, T_L, T_M, w, t, R_d [µm] / ρ [µΩ·cm].
단위 변환: 1 µΩ·cm = 1e-2 Ω·µm (코드에 1e-2 계수로 반영).

**재현값 (8/8 PASS)**: W=0.35 µm, T_M≈4000 Å, T_L=250 Å, ρ_L=100 µΩ·cm(최악) → R_L/R_Cu≈200,
라이너 무시 오차 <0.5%(ρ_Cu 1.7·2.0) / 2.2에서 경계 초과. dishing: w=5 µm → 모델 11.6% vs 문헌 9.39%(30% 이내);
표 I w≥2 µm 전부 30% 이내; **w=0.4 µm는 모델 범위 밖**(모델 0.067% vs 문헌 1.14%).

**출처 (원문)**
- Park, Tugbawa, Boning, Chung et al., "Electrical Characterization of Copper Chemical Mechanical Polishing," *Proc. CMP-MIC* (1999) — eq.1-3, §V.A
- Chang, Cao, Spanos, "Modeling the Electrical Effects of Metal Dishing Due to CMP for On-Chip Interconnect Optimization," *IEEE TED* 51(10) 1577-1583 (2004), doi 10.1109/TED.2004.834898 — 표 I, Fig.6 segment 모델, 최소제곱 추출 R_dish ≈ 40 µm

**한계**: 라이너 병렬 저항을 무시하는 근사(R_L/R_Cu ≥ 100이면 안전). segment 모델은 미세선폭(w<2 µm)에서 문헌과 괴리 — 코드가 "모델 밖"으로 명시. Recipe에 전기 테스트 스키마가 없어 engine 미등록.

---

## 8. wear_aware_endpoint.py — 패드 마모 드리프트를 반영한 엔드포인트 시간 적분

**목적**: 정상상태 가정(MRR 일정)이 무컨디셔닝 장시간 폴리싱에서 얼마나 낙관적인 엔드포인트를 내는지 정량화.

**지배방정식**
- v0(정상상태): `removed = MRR·t`, `t_endpoint = target/MRR_ref`
- 드리프트 인지: 누적 제거두께를 **사다리꼴 적분** `cum[i] = Σ ½(MRR[k+1]+MRR[k])·Δt`
- 엔드포인트: cum이 target에 도달하는 시각을 **선형보간**(`np.interp`)
- 낙관도: `optimism_pct = (t_drift - t_naive)/t_naive × 100`, `t_naive = endpoint_time(target, MRR[0])`

**기호**: target_thickness [m] / t [s] / MRR [m/s].

**입력→출력**: pad_wear_glazing.simulate_pad_wear()의 (t, MRR(t)) 시계열 + 목표두께 → t_drift, t_naive, optimism_pct.

**출처**: 새 물리 지식 없음 — pad_wear_glazing.py(Shi & Ring, *Wear* 2010)와 process_time.py(Preston)의 기존 검증 결과를 이어붙인 통합 모듈.

**검증 (4/4)**: 누적적분 = np.trapezoid 일치(rel_err<1e-9); C1=0(마모 없음) 극한에서 process_time.endpoint_time으로 정확히 축소;
MRR이 단조 감소하므로 **optimism_pct > 0**(naive가 항상 빨리 끝난다고 낙관); 도달 불가 target은 RuntimeError.

**한계**: MRR(t)의 절대 스케일은 pad_wear_glazing의 c_w(임의 상수, 물리 캘리브레이션 아님)에 의존 — 정성적 방향성만 유효.

---

## 9. wear_aware_kp_physical.py — ad-hoc MRR vs GW 물리분해 MRR 교차검증 (★반증 기록)

**목적**: 마모 시간축 MRR 드리프트를, GW 기반 물리적 Preston 분해로 재계산해 형태 일치 여부를 검증.

**두 공식**
- ad-hoc (pad_wear_glazing): `MRR(t) = c_w · p_r(t)`, `p_r = W/A_r` (평균 실접촉압력)
- 물리기반 (gw_preston_link): `MRR = α_removal · n_contacts(P) · V`,
  `α_removal = Kp_lit·P_ref / n_contacts(P_ref)` (문헌 역산), `Kp_physical := α_removal·(dn/dP)`
- 접촉점수: `n_contacts(heights, d) = Σ 1[heights > d]`

**하부 이산 마모 루프 (pad_wear_glazing 함수 재사용)**
- 높이 분포: `φ(z) = β·exp(-βz)` (지수분포, β=1/0.3 µm)
- Hertz: `F = (4/3)E*·sqrt(R)·δ^1.5`, `A = π·R·δ`, δ = max(z−d, 0)
- 하중평형으로 분리거리 d 결정: `W(d) = P_app·A_n` (brentq)
- **Archard 마모(유체 없는 Borucki 극한): `dz/dt = -C1·sqrt(max(z-d,0))`** (오일러 적분)

**캘리브레이션 상수**: P_ref=20.7 kPa, V_ref=0.8 m/s, Kp_lit=1e-13 m²/N (STI 254.05 nm/min).

**출처**
- Preston 캘리브레이션: preston.py 문헌값 Kp=1e-13 m²/N, STI 254.05 nm/min (ACS Langmuir 2026 baseline 인용)
- n(P) 선형성: Yang et al. 2024 Eq.20 (knowledge/materials/gw-nominal-vs-local-pressure.md §3)
- 마모 모델: Shi & Ring, "CMP pad wear and polish-rate decay modeled by asperity population balance with fluid effect," *Wear* (2010) — 저자 공개 PDF. 인용된 Borucki(2002)/Stein et al.(1996)/Oliver/Lawing 원문은 **미확보(2차 인용, 미검증)**

**★결과 — 당초 가설이 반증됨 (숫자 조작 없이 정직 기록, self-test FAIL 유지)**
- `n_contacts(t)`는 감소가 아니라 **증가**: n[0]=3033 → n[-1]=3564 (40스텝, +17.5%) → MRR_physical도 증가
- ad-hoc MRR(t)=c_w·p_r(t)는 여전히 단조 **감소**
- 정규화 곡선 Pearson 상관계수 **corr ≈ -0.998** (거의 완벽한 역상관)
- **원인**: 명목압력 P_app 고정 + asperity 집단이 마모로 줄어드는 시나리오. 힘평형 W(d)=P_app·A_n을 유지해야 하므로 평균 높이 하락(2.99e-7→2.93e-7 m, -2%)보다 분리거리 d가 더 빨리 내려가고(5.63e-7→5.16e-7 m, -8.3%), 접촉점 수 n은 늘고 접촉당 압력 p_r은 준다.
- **스코프 한계 노출**: `MRR = α_removal·n(P)·V`는 "**압력을 바꿀 때**"의 관계식이고 "**집단이 마모될 때**"는 검증 범위 밖 — 시간축에 그대로 외삽하면 정성적으로 틀린 방향(MRR 증가)을 예측한다.
- 회귀성 검증: C1=0 극한에서 n_contacts(t) 상수(PASS), 새 루프가 원본 simulate_pad_wear()와 수치적으로 동일 재현(rel_diff<1e-12, PASS).

**추가 가정**: α_removal은 정상상태(P 고정, 마모 없음) 캘리브레이션 상수를 시간축에 적용하는 근사 — "화학/재료 lump 상수는 마모 상태와 무관"이라는 암묵 가정이며 이 모듈에서 검증하지 않음(명시).

---

# 면접용 3대 추적 요약

## A. COF 정의 → EPD(모터전류) 연결 사슬
```
μ (Stribeck/실측)
 → F_s = μ·P·A         (Amontons, friction_cof_epd)
 → τ  = F_s·r_c        (플래튼 저항토크)
 → P_motor = τ·ω  /  I = τ/K_t
 → 이동평균(2N+1) 평활 → baseline 대비 threshold_fraction 계단검출
 → 지연 T = N/R → 과연마 = T·RR/60
```
역방향으로 힘센서에서 **COF = F_s/F_n**을 직접 산출한다. 재료 전이 시 μ가 바뀌면 τ·ω가 바뀌고 모터전력에 계단이 생기는 것이 EPD의 원리다.
Li 2017 실측 기준 계단은 baseline의 **5.4%**뿐이라 임계값을 contrast/2≈0.027로 두고, 121점 MA가 4.94 s 지연 → 229 nm/min에서 18.8 nm 과연마.
Headley 2019는 **전단력(r=0.955)이 COF(r=0.758)보다 PMC와 더 강하게 상관**한다고 보고 — 신호로는 COF보다 생 전단력이 낫다.

## B. Stribeck 윤활 영역 판정 기준
- **Sommerfeld: So = μ·U/(p·δ_eff)**, `δ_eff = α·Ra + (1-α)·δ_groove` (Philipossian US20110076924A1; Wu & Liao 2016)
- **Hersey: η·N/P** (차원 관례 상이 — 오더 확인용)
- **λ = h_film/σ** → **λ<1 경계윤활 / 1≤λ<3 혼합 / λ≥3 유체윤활** (Bhushan 2013, 관례값)
- 항등식 `So = ℓ_hd/δ_eff`, `ℓ_hd = μU/p`
- CMP 전형조건(1 mPa·s, 0.75 m/s, 3 psi, Ra 5 µm): **ℓ_hd=36.3 nm ≪ Ra → So=λ=7.25e-3 → boundary, COF≈0.24** (문헌 oxide CMP 0.23~0.40과 부합)
→ **결론: CMP는 거의 항상 경계/혼합 윤활 영역이며, 이것이 CMP COF가 0.2~0.4로 큰 이유다.**

## C. 마찰 → 온도 → 화학 커플링 경로
```
q = μ·P·V            [W/m²]  마찰 열유속
Q_f = q·A = τ·ω      [W]     ← EPD 모터동력과 동일한 물리량
ΔT = Q_f/(ṁ·c_p)             (슬러리 전량냉각 상한)
또는 ΔT_ss = Q_f/(G_slurry + G_pad + G_air [+G_wafer])   (White 2003 열저항 네트워크)
T_ss = T_ref + ΔT
RR(T2)/RR(T1) = exp[(Ea/R)(1/T1 − 1/T2)]                 (Shin 2025 Ea)
```
Ea가 클수록 온도 민감도가 크다: **Cu(151.7 kJ/mol) ≫ Ta(29.9) ≫ SiO₂(8.75)** — 같은 ΔT에서 Cu 화학속도가 압도적으로 크게 변한다.
Shin 2025 조건 분배는 **슬러리 >60% / 패드 전도 10~30% / 공기 <15%** → 슬러리 유량이 계면 온도의 지배 인자.
