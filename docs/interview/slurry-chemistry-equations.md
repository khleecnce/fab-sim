# FabSim 슬러리 화학·전기화학 모듈 — 이론식과 출처 (코드 확인본)

> 모든 수식·상수·출처는 `~/fab-sim/sim/` 소스에서 직접 읽은 것만 옮겼다. 추정·보완 없음.

---

## 1. `sim/tier2_physics/dlvo_colloid.py` — DLVO 콜로이드 상호작용·Debye 길이·제타전위

**목적:** 실리카 슬러리의 입자간 총 상호작용 에너지 곡선 V_T(h)와 Debye 길이, Henry 식 제타전위 역산을 재현하고, 이온세기·제타전위 변화가 분산 안정성에 미치는 정성 거동을 검증.

### 지배방정식 (코드 그대로)

| 항 | 식 | 코드 |
|---|---|---|
| Debye 길이(정확식) | kappa^2 = 2*(z*e)^2 * I * 1000 * N_A / (eps0*eps_r*k_B*T), kappa^-1 = 1/kappa | `debye_length_nm` |
| Debye 길이(근사) | kappa^-1 [nm] = 0.304 / sqrt(I)  (물, 25°C, 1:1) | `debye_length_approx_nm` |
| van der Waals 인력 | **V_vdW(h) = -A*a / (12*h)** | `V_vdW` |
| 전기이중층 반발 | **V_edl(h) = 2*pi*eps0*eps_r*a*zeta^2 * ln(1 + exp(-kappa*h))** | `V_edl` |
| 총 상호작용 | **V_T(h) = V_vdW(h) + V_edl(h)**, 출력은 V_T/kT | `V_total_profile` |
| Henry 제타 역산 | **zeta = 3*eta*mu_E / (2*eps0*eps_r*f(ka))** | `henry_zeta_from_mobility` |

### 기호·단위
- `h`: 입자 표면간 거리 [m] (스캔 범위 3e-10 ~ 4e-8 m, 4000점)
- `a`: 입자 반경 [m] (self-test 실리카 50 nm)
- `A`: Hamaker 상수 [J] (실리카-물-실리카 0.85e-20 J, "문헌 오더")
- `zeta`: 제타전위 [V] (self-test -40 mV ~ -10 mV)
- `I`: 이온세기 [mol/L]; `z`: 대칭 z:z 전해질 원자가
- `eps0 = 8.8541878128e-12 F/m`, `eps_r = 78.5` (물 25°C), `k_B = 1.380649e-23 J/K`, `N_A = 6.02214076e23`, `q_e = 1.602176634e-19 C`
- `mu_E`: 전기영동 이동도 [m²/(V·s)], `eta = 8.9e-4 Pa·s`(물), `f(ka)`: Henry 함수 — Smoluchowski 1.5 / Hückel 1.0
- 에너지는 전부 kT 단위로 환산해 보고

### 입력 → 출력 경로 (응집/안정성 판정까지)
1. 이온세기 I → Debye 길이 kappa^-1 → EDL 반발의 감쇠거리 결정
2. (a, zeta, A, I) → V_T(h) 곡선 → 요약 3값 산출: `barrier_kT`(곡선 최댓값 = 에너지 장벽), `barrier_h_nm`, `sec_min_kT`/`sec_min_h_nm`(장벽 바깥쪽 구간의 최솟값 = 2차 최소)
3. 판정 논리는 self-test에 명시적 검사로 박혀 있다:
   - I=1 mM에서 장벽 > 15 kT → 분산 안정
   - I 1 mM → 10 mM → 100 mM 로 갈수록 장벽 **단조 감소**, 2차 최소 **단조 심화(더 음수)**
   - 같은 I=10 mM에서 zeta만 -40 → -20 → -10 mV로 낮추면 장벽 단조 붕괴, -10 mV에서 장벽 < 5 kT = "사실상 소멸"
   - 이유는 코드 주석에 명시: **V_edl ∝ zeta²** 이므로 IEP 근접 시 장벽이 급감
4. 정량 zeta가 없을 때의 대체 경로 — `stability_qualitative(pH, abrasive_iep_ph, wafer_iep_ph=None)`:
   - |pH − IEP| < 1.0 → risk="high", ≥ 2.0 → "low", 그 사이 "medium"
   - wafer IEP 거리는 note에만 참고 기재, **위험도 분류에 반영하지 않음**(입자-웨이퍼 결합 정량화 문헌 없음)

### 출처 (docstring '지식 근거')
- Debye 길이 0.304/sqrt(I) nm: **Israelachvili, "Intermolecular and Surface Forces" 3rd ed. (2011)** 표준식, 2차 인용. 앵커 대조값은 dispersion.com 튜토리얼 "~1 nm @ 0.1 M, ~10 nm @ 0.001 M"
- Henry 식: Malvern ELS overview PDF (macro.lsu.edu)
- 구-구 정전반발 일정전위형: **arXiv:1009.6150**
- 내부 노트: `knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md` (§2 "|zeta|≥30 mV 안정, <15 mV 응집", §5 IEP 서술)

### 가정·한계 (코드에 명시된 것)
- V_vdW는 **Derjaguin 소분리 근사**(retardation 무시, h→0에서 발산)
- V_edl은 **일정전위(constant-potential) Derjaguin 근사**, 동일 구-구, 대칭 전해질
- `stability_qualitative`의 임계 1.0/2.0은 **미검증(arbitrary)** — "|zeta| 기준을 pH 거리로 대략 치환한 것뿐, 정량 매핑 문헌은 없다"고 docstring이 자인
- 이 함수는 zeta 절대값을 계산하지 않는다(팩에 실측 zeta 없음)

---

## 2. `sim/tier2_physics/cu_pourbaix.py` — Cu–H2O Pourbaix 경계선

**목적:** CRC 표준전위표 6개 반쪽반응에서 Cu-H2O 전위-pH 도표 경계선을 Nernst 식으로 직접 유도하고 (pH, E)로부터 안정상을 판정.

### 상수
`K_NERNST = 0.05916 V` = (RT/F)·ln10 @25°C, `pKw = 14.00`

CRC 'Electrochemical Series'(Vanysek) 값 [V vs SHE]:
`E0(Cu²⁺/Cu)=0.3419`, `E0(Cu⁺/Cu)=0.521`, `E0(Cu²⁺/Cu⁺)=0.153`, `E0(Cu2O 알칼리형)=-0.360`, `E0(Cu(OH)2 알칼리형)=-0.222`, `E0(2Cu(OH)2/Cu2O 알칼리형)=-0.080`

### 경계식 (코드 그대로)

| 경계 | 식 | 기울기 |
|---|---|---|
| Cu²⁺/Cu 수평선 | **E = 0.3419 + (k/2)·log a_Cu** | 0 (pH 무관) |
| Cu/Cu2O | E0_acid = -0.360 + 14k = 0.4682 V, **E = 0.4682 − k·pH** | **−59.16 mV/pH** |
| Cu²⁺/Cu2O | E0 = 2·0.3419 − 0.4682 = 0.2156 V, **E = 0.2156 + k·pH + k·log a_Cu** | **+59.16 mV/pH** |
| Cu/Cu²⁺/Cu2O 삼중점 | **pH = (E0_Cu2_Cu − E0_Cu2_Cu2O − (k/2)·log a_Cu)/k** | — |
| Cu²⁺/Cu(OH)2 수직선 | log Ksp = −2(E0_Cu2_Cu − E0_CuOH2_alk)/k = **−19.06**, **pH = (log Ksp + 2·pKw − log a_Cu)/2** | 수직(전위 무관) |
| Cu2O/Cu(OH)2 | E0 = −0.080 + 14k = 0.748 V, **E = 0.748 − k·pH** | **−59.16 mV/pH** |
| Cu⁺ 불균화 | **log K = (E0_Cu1_Cu − E0_Cu2_Cu1)/k ≈ +6.22** (2Cu⁺ = Cu + Cu²⁺) | — |

### 기호
`k = 0.05916 V/decade`, `log a_Cu` = 용존 Cu 이온 활동도 로그(기본 −4, 부식공학 관례), `E` [V vs SHE], `pH` 무차원.

### 입력 → 출력
`stable_phase(pH, E_V, log_a_cu=-4.0)` → "Cu" / "Cu2+" / "Cu2O" / "Cu(OH)2 (CuO 자리 대용, 미검증)"
판정 순서: (1) 삼중점 pH 기준으로 저전위측 경계(저pH는 Cu²⁺/Cu 수평선, 고pH는 Cu/Cu2O 경사선) 아래면 금속 Cu(면역 영역) → (2) 그 위에서 pH가 Cu²⁺/Cu(OH)2 수직선보다 낮으면 Cu²⁺(부식 영역) → (3) 그 외 Cu2O 또는 Cu(OH)2(부동태 영역).

### 출처
- **CRC 'Electrochemical Series' (Vanysek)**, `papers/crc-vanysek-electrochemical-series.pdf` — 1차 표값
- **Tamilmani 2005, University of Arizona 학위논문 (hdl 10150/280774) 그림 4.1** — 대조 판독값. 검증 허용오차 ±0.03 V / ±0.15 pH
  - 검증 실적: log a=−4 → 0.2236 V(판독 0.22), pH8 → −0.005 V(판독 0.00), pH13 → −0.301 V(판독 −0.30), 삼중점 pH 4.14(판독 ~4.2)
- 내부 노트: `knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md` §2, §7

### 한계 (docstring 명시)
- **CuO 경계는 구현하지 않았다** — CRC 표에 CuO 반쪽반응이 없어 ΔG_f°를 1차값으로 확보 못함. 준안정 Cu(OH)2 경계를 대용으로 쓰고 모듈 전체에서 "Cu(OH)2 (CuO 자리 대용, 미검증)"으로만 표기. 실제 CuO 수직선(그림 4.1 판독 pH≈5.65) 대비 계산값 6.47은 방향(더 높은 pH)만 검증됨.
- 활동도계수 1 가정(농도=활동도), 25°C 고정.

---

## 3. `sim/tier2_physics/pourbaix_nernst_slope.py` — Nernst pH 기울기 일반식

**목적:** 임의 산화환원 반응의 전위-pH 경계 기울기를 계수(m, n)만으로 계산하고, CMP 표면반응이 표준 −59.1 mV/pH 계열인지 판별.

### 지배방정식
반응 `a·Ox + m·H⁺ + n·e⁻ = b·Red (+H2O)` 에 대해
```
E = E0 − (0.0591/n)·log([Red]^b/[Ox]^a) − (0.0591·m/n)·pH      (25°C)
dE/dpH = −0.0591·(m/n)   [V/pH]
```
코드 상수 `RT_F_LN10_25C = 0.05916` → m=n=1이면 **−59.16 mV/pH**, m=2n이면 **−29.58 mV/pH**(절반). n=0이면 ValueError(수직선, 기울기 미정의).

`is_self_limiting_type()` = (m == n): "금속 1개당 H⁺/OH⁻ 1개, 전자 1개" 비율 → 치밀한 화학양론적 산화막(WO3, Cu(OH)2) 형성 = 전형적 passivation 계열.

### 부호화된 CMP 표면반응 (`CMP_SURFACE_REACTIONS`)
| 반응 | m | n | 기울기 | source (코드 그대로) |
|---|---|---|---|---|
| W + 2H2O → WO3 + 6H⁺ + 6e⁻ (WO3 passivation, 산성) | 6 | 6 | −59.16 mV/pH | Krishnan et al. Chem. Rev. 2010 (2차 인용) |
| Cu + 2OH⁻ → Cu(OH)2 + 2e⁻ (Eq.9) | 2 | 2 | −59.16 | Gamagedara & Roy, Materials 17(19) 4905 (2024), PMC11477894 |
| 2Cu + 2OH⁻ → Cu2O + H2O + 2e⁻ (Eq.10) | 2 | 2 | −59.16 | 동일 |
| Cu(OH)2 → CuO + H2O (탈수, 산-염기형) | 0 | 0 | Nernst 미적용 | 동일 |

기울기는 **비율 m/n에만 의존** — (6,6)과 (1,1)이 같은 값(self-test로 확인).

추가 명제 함수: `mo_cu_w_oxidizer_peak_shift_direction(with_complexing_agent)` → 착화제 있으면 "peak shifts to higher oxidizer concentration"(재용해가 과-passivation 억제 → MRR-산화제 정점 고농도 이동).

### 출처·한계
- 일반형은 표준 전기화학 교과서(**Bard & Faulkner** 류)로 독립 유도 — Pourbaix Atlas 1966 원저는 유료 미확인
- 반응식 계수는 knowledge 노트 §3-4의 2차 인용, Gamagedara & Roy 2024가 1차
- Eq.9/10은 OH⁻ 형태 표기이며 H2O = H⁺ + OH⁻ 등가 변환으로 H⁺ 계수 2로 간주(코드 주석에 명시)

---

## 4. `sim/tier2_physics/competitive_metal_langmuir.py` — 경쟁 Langmuir 흡착 (post-CMP 잔류 금속)

**목적:** 세정액 중 여러 금속이온이 웨이퍼 표면 흡착 자리를 H⁺와 함께 경쟁할 때의 잔류 면밀도 산출.

### 지배방정식 (Loewenstein·Charpin·Mertens 1999 Eq.22)
```
sigma_i = sigma0 · K_i·[M_i] / ( 1 + K_H·[H⁺] + Σ_j K_j·[M_j] )
[H⁺] = 10^(−pH)
Theta = Σ_i sigma_i / sigma0        (총 점유율, 0~1)
```

### 기호·단위
- `sigma_i`: 금속 i의 표면 면밀도 [sites/cm²] / `sigma0`: 총 흡착자리 밀도, 기본 **3.0e12 sites/cm²** (Cr³⁺ 단독 적합 pH 3, 20°C, 2 min 절편의 역수)
- `K_i`: 금속 i 흡착평형상수 [L/mol] — `K_Cr = 1e6`("about 1e6", 오더값)
- `K_H`: 양성자 경쟁상수 [L/mol], 기본 **1e3**("probably ~1e3", 오더값)
- `C_i`: 유리(free) 금속 농도 [mol/L]

### 입력 → 출력
입력 `metals = {이름: (K_i, C_i_free)}` + `pH` → 출력 `{이름: sigma_i [sites/cm²], "_theta": Theta}`. 모든 금속이 **공통 분모(경쟁항)를 공유**하므로 한 금속의 농도 증가가 다른 금속 흡착을 밀어낸다. pH가 낮을수록 K_H·[H⁺]가 커져 금속 흡착이 억제된다.

### 출처
**Loewenstein, Charpin, Mertens (1999) Eq.22**. 내부 노트 `knowledge/cmp/post-cmp-residual-metal-prediction-langmuir-scm.md` §2·§6(A)·§8.

### 한계 (docstring에 자인)
- **오더값 검증 라이브러리** — 정밀 예측을 주장하지 않음. K_i 표가 없어 Cr 하나만 문헌값, 나머지는 K_Cr 대입 근사.
- **재현 성적이 반쪽이다**: Cr의 [M] 농도 지수 0.74가 문헌 Table VI의 0.73과 0.01 이내로 재현되지만, **pH 지수는 모델 −0.12 vs 문헌 −0.39로 3배 어긋난다**(9종 타금속 경쟁항과 K_H가 오더값이기 때문). 즉 농도 의존성은 잡고 pH 의존성은 못 잡는다.
- engine.py/models.py에 등록하지 않는 순수 함수 — Recipe에 pH·이온농도 필드가 없음(스키마 부채).

---

## 5. `sim/tier2_physics/ceria_redox_selectivity.py` — 세리아 Ce³⁺/Ce⁴⁺ 산화환원과 oxide:nitride 선택비

**목적:** 세리아 슬러리의 산소공공→Ce³⁺ 활성점 생성, Si-O-Ce 화학흡착 판정, 세리아-실리카 정전인력, 산화막:질화막 선택비를 각각 독립 함수로 재현.

### 지배방정식

| 함수 | 식 | 의미 |
|---|---|---|
| `ce3_fraction(x)` | **f = 2x** | CeO_{2−x}의 산소공공 x → Ce³⁺ 분율. 전하중립 유도: 4(1−f) + 3f = 2(2−x) ⇒ f = 2x. (O²⁻ 하나 이탈 → 남은 2전자가 이웃 Ce⁴⁺ 둘을 Ce³⁺로 환원) |
| `chemisorption_energy_kj_mol(ev)` | **E[kJ/mol] = E[eV] × 96.485** | DFT 흡착에너지 단위환산 |
| `is_chemisorption(E, thr=-40.0)` | **E < −40 kJ/mol → 화학흡착** | 물리흡착 경계 −20~−40 kJ/mol |
| `electrostatic_attraction(iep_ceria, iep_silica, pH)` | **sign(IEP − pH) 의 곱** → −1(인력)/0/+1(반발) | pH < IEP → 양전하 |
| `oxide_nitride_selectivity(oxide_mrr, nitride_mrr)` | **S = MRR_oxide / MRR_nitride** | |
| `h2o2_boost_selectivity(S0, boost=3.0)` | **S = S0 × 3.0** | H2O2 첨가 배율 |

### 기호·수치
- `x`: 산소공공 화학량 [무차원], `f`: Ce³⁺ 분율 [0~1]
- `EV_TO_KJ_MOL = 96.485`
- 규산(H4SiO4) DFT 흡착에너지: **세리아(111)면 −1.15 eV, (100)면 −2.67 eV → −111 ~ −258 kJ/mol** ⇒ 물리흡착 경계를 크게 벗어나 화학흡착으로 판정
- IEP: 세리아 6.7–7.8(호출측이 6.8 전달), 실리카 2–3(2.5 전달) — **기본 상수로 박지 않고 인자로 노출**
- 작동 pH 대략 4–6에서 세리아(+)·실리카(−) 반대부호 → 정전인력

### 입력 → 출력 (메커니즘 체인)
산소공공 x → Ce³⁺ 분율 f=2x (활성점 밀도) → Si-O-Ce 화학결합(−111~−258 kJ/mol, 화학흡착 판정) + pH·IEP에 의한 정전인력(접촉 확률) → oxide MRR → nitride MRR 대비 선택비. H2O2 0.5 wt% 첨가 시 표면 Ce³⁺% 최대 → **oxide MRR 5.5배, 선택비 1:1 → 3:1**.

### 출처
- Ce³⁺ 전하균형·H2O2 효과: **Netzband & Dunn 2020, ECS J. Solid State Sci. Technol. 9, 044002, doi:10.1149/2162-8777/ab8393** (OA)
- DFT 화학흡착: **Brugnoli et al., "New Atomistic Insights on the CMP of Silica Glass with Ceria Nanoparticles," Langmuir 39(16), 2023, doi:10.1021/acs.langmuir.3c00304** (PMC10116594, OA)
- 정전인력: Cambridge JMR, **doi:10.1557/JMR.2005.0176** 계열
- 선택비 원자료: **Hwang & Kim 2024, Polymers 16, 844, doi:10.3390/polym16060844** (PMC10974854, OA) — 소포폴리머별 oxide(PETEOS)/nitride MRR로 선택비 59–80 재현(BYK 5558/83 = 67, G-336 5417/68 = 80)
- 내부 노트: `knowledge/cmp/ceria-slurry-ce-redox-selectivity.md` §2–§5, §7

### 한계 (docstring 명시, "지어내지 않음")
- **Ce³⁺ vs Ce⁴⁺ 최적 방향은 계·목적별 상충 보고 존재 → 정량 최적비는 함수화하지 않았다**
- 아미노산·계면활성제 절대 선택비(35–70)는 슬러리·패드·압력 의존 캘리브레이션 대상이라 미검증 → 함수화 안 함. Hwang & Kim 2024 원자료 기반 59–80만 재현
- IEP는 2차 인용 범위
- engine 미등록 순수 함수(Recipe에 pH·H2O2 농도 필드 없음)

---

## 6. `sim/tier2_physics/chelation_surface_charge.py` — 킬레이트 조건부 안정도상수·산화물 표면전하·DHF pH

**목적:** post-CMP 세정 화학 — 이온세기·pH 보정된 킬레이트 착화 능력, 유리 금속이온 분율, 산화물 표면전하 부호, 희석 HF의 평형 pH.

### 지배방정식

| 함수 | 식 |
|---|---|
| Davies 이온세기 보정 | **logK(I) = logK0 − A·f(I)·(zM² + zL² − zML²)**, **f(I) = √I/(1+√I) − 0.3·I**, A = 0.509 |
| Ringbom 부산물함수 | **log α_H(pH) = log10( 1 + Σ_n 10^(β_n − n·pH) )** |
| 조건부 안정도상수 | **log K'(pH, I) = logK(I) − log α_H(pH)** |
| 유리 금속이온 분율 | **α_free = 1 / (1 + K'·C_L)** = 1/(1 + 10^logK' · C_L) |
| 산화물 표면전하 부호 | **pH < IEP → '+', pH = IEP → '0', pH > IEP → '−'** |
| DHF 약산 평형 | C_HF = wt%/100 × 1000 / 20.01, **[H⁺] = (−Ka + √(Ka² + 4·Ka·C_HF))/2**, pH = −log10[H⁺] |

### 기호·참조표
- `zM`: 금속 전하, `zL`: 리간드 전하(EDTA⁴⁻ = −4, Cit³⁻ = −3), `zML = zM + zL`
- I=0 logK (USGS PHREEQC `minteq.v4.dat`, NIST46.2 태그): EDTA — Fe³⁺ 27.7, Cu²⁺ 20.5, Ca²⁺ 12.42 / 시트르산 — Fe³⁺ 13.1, Cu²⁺ 7.57(출처태그 SCD2.62, IUPAC SC-Database), Ca²⁺ 4.87
- 양성자화 log β_n: EDTA [10.948, 17.221, 20.34, 22.5, 24.0], Cit [6.396, 11.157, 14.285]
- IEP: SiO2 2.0, CeO2 6.8, Al2O3 9.5. CeO2 실측범위 5.21–9.40
- HF pKa = 3.17, MW 20.01 g/mol

### 입력 → 출력
(리간드 종류, 금속, pH, I) → logK'(pH,I) → (킬레이트 농도 C_L와 함께) → 유리 금속이온 분율.
검증된 거동: **선택성 Fe³⁺ > Cu²⁺ > Ca²⁺가 모든 pH·리간드에서 유지**; pH↑ → α_H→1 → logK' 단조증가; pH 3 시트르산-Ca는 logK' < 0(착화 사실상 불가); **pH 11·50 mM에서 유리 Cu²⁺ 분율 < 1e-5**(EDTA·시트르산 모두). DHF 0.5 wt% → C_HF ≈ 0.25 M → **pH ≈ 1.90**, 그 pH에서 SiO2/CeO2/Al2O3 전부 '+'; pH 11에서 전부 '−'; pH 5에서 CeO2(+)/SiO2(−) 이부호.

Davies 보정 검증: I=0.1에서 Fe-EDTA 27.7→25.13, Cu-EDTA 20.5→18.79 (문헌 25.1 / 18.75와 0.3 log 단위 이내).

### 출처
- 안정도상수: **USGS PHREEQC `minteq.v4.dat`** (NIST46.2 태그) / Cu-Cit은 SCD2.62
- 문헌 대조값(I=0.1): **Kontoghiorghes 2020 Table 3**, **Palden 2020** 평균
- IEP: **Brugnoli 2023**(SiO2 2.0, CeO2 6.8), **Zhang 2024**(Al2O3 9.5, 세척 후), **Ederer 2025 Table 2**(CeO2 합성법별 실측 5.21–9.40)
- 유리 Cu²⁺ 억제 조건: **Seo 2019**(킬레이트 50 mM, pH 11)
- Davies A = 0.509는 교과서 상수
- 내부 노트: `knowledge/cmp/post-cmp-adsorption-cleaning-chemistry.md` §3·§4·§6

### 한계 (docstring 명시)
- **K'(pH)는 리간드 양성자화만 보정한다** — 금속 가수분해·수산화물 침전·혼합 착물·HCit⁻ 착물 무시 ⇒ `free_metal_fraction()`의 알칼리 영역 값은 **실제보다 덜 억제되게 나오는 상한 추정**
- 기본값 I=0.0은 노트 §6(B)가 실제로 검증한 경로(Davies 미체이닝). **I>0을 명시 전달해 얻는 K'(pH,I)는 노트가 검증하지 않은 외삽**
- Ca-EDTA logK(I=0.1)의 OA 대조값 미확보 — Davies 예측 10.71은 검증 불가
- IEP는 벌크 분말·유리 표면값 — CMP 후 실제 박막(TEOS/HDP/low-k)의 IEP·ζ(pH) 곡선 미확보. **부호만 판정하고 |ζ| 크기는 다루지 않는다**

---

## 7. `sim/tier2_physics/galvanic_hydroxide_ph.py` — 갈바닉 부식 방향·수산화물 전이 pH

**목적:** 이종금속 접촉 시 어느 쪽이 양극(용해)인지 판정하고, 금속 수산화물 석출 시작 pH를 계산.

### 지배방정식
```
갈바닉: 표준환원전위가 더 낮은(비한) 쪽이 anode
        ΔE0 = E0(cathode, 귀한 쪽) − E0(anode, 비한 쪽)   (항상 양수)

수산화물: M(OH)2 + 2H⁺ = M²⁺ + 2H2O
        pH* = ( log K − log10(C) ) / 2
```

### 기호·표값
- `E0` [V vs SHE], CRC 'Electrochemical Series'(Vanysek): **Co −0.28, Cu 0.3419, Ru 0.455, Ti −1.630, Ta2O5/Ta −0.750, WO3/W −0.090**
- `log K` (minteq.v4.dat PHASES, NIST46.4 태그): **Cu 8.674, Co 13.094**
- `C` [mol/L] — ppm→mol/L 환산은 호출자 책임

### 입력 → 출력
(금속 A, 금속 B) → `{anode, cathode, delta_E0_V}`. 검증 예: **Cu-Co → anode Co, ΔE0 ≈ 0.6219 V**; **Ru-Cu → anode Cu, ΔE0 ≈ 0.1131 V**.
(금속, 몰농도) → 수산화물 석출 개시 pH*.

### 출처
- CRC 'Electrochemical Series' (Vanysek) §3.1
- `minteq.v4.dat` PHASES (NIST46.4) §3.3
- 내부 노트: `knowledge/cmp/low-level-metal-cobalt-ruthenium-cross-contamination.md` §3.1·§3.3·§6

### 한계 (docstring 명시)
- **ΔE_corr(실제 부식전위차) 크기는 표준전위로 예측 불가** — Lee 2021은 4배, Seo 2019는 1/15로 어긋남. **방향(anode/cathode)만 신뢰할 것**
- 금속 가수분해·수산화물 침전·박막 실제 IEP 미반영

---

## 8. `sim/tier2_physics/metal_contamination_surface.py` — post-CMP 금속 오염 산출

**목적:** 표면 금속 면밀도를 단분자층·소자스펙 기준으로 환산하고, 제타전위에 의한 Cu²⁺ 정전농축과 GOI 조기파괴율을 산출.

### 지배방정식

| 함수 | 식 |
|---|---|
| 단분자층 밀도 | **N_ML = 2 / a²** (Si(100), 단위면적 a²당 2원자) |
| 단분자층 분율 | **frac = 허용치 / N_ML** [ML] (×1e6 → ppm ML) |
| 열전압 | **kT/e [mV] = 25.69 × T/298.15** |
| Boltzmann 표면과잉 | **n_surf/n_bulk = exp( −z·ψ / (kT/e) )**, ψ ≈ ζ |
| GOI 조기파괴율 | **n_fail / n_total** |
| 스펙 배율 | **precmp / spec** |

### 기호·수치
- `a = 5.431e-8 cm`(Si 격자상수 5.431 Å) → **N_ML ≈ 6.78e14 atoms/cm²**
- 허용치 **1e10 atoms/cm²** (ITRS 2.0 각주[14] FEP 스펙) → **≈1.5e-5 ML ≈ 15 ppm ML**
- `z = +2`(Cu²⁺), `kT/e = 25.69 mV @298.15 K`
- 대표 ζ(SiO2, IEP≈2): IEP 0 mV, 약산성 −20, 중성 −40, 약알칼리 −60 mV
- 검증: ζ=0 → 배율 1; **ζ=−40 mV(중성) → 약 22배 농축**; pH↑ → |ζ|↑ → 농축 단조증가

### 입력 → 출력
pH → ζ 부호·크기 → Cu²⁺ 표면농축 배율. 면밀도 → 단분자층 분율 / ITRS 스펙 배율(세정 전 W-CMP Fe 1~2e12 → **100~200배 초과**). Fe 오염 PMOS GOI: **8/71 = 0.1127 (11.3%) 조기파괴(V_bd < 1.5 V, β-FeSi₂ 석출물)**, V_bd 스펙 4.14 V(=1.8 V × 2.3), 무오염 기준 5.16 V.

### 출처
- **Wang et al. 2024, Electronics 13(12) 2391, doi:10.3390/electronics13122391** (MDPI CC-BY, 원문 전체 확보) — GOI 실험
- **ITRS 2.0 (2015) 각주[14]** FEP 표면금속 스펙 1E10 atoms/cm² (1차 확정)
- 내부 노트: `knowledge/cmp/post-cmp-metallic-contamination-sources.md` §5·§6, `knowledge/cmp/metal-contamination-device-impact-irds-limits.md` §2·§5·§7

### 한계 (docstring이 자체 정정한 것 포함)
- **`SEO2001` 딕셔너리의 Fe 수치(세정 전 1.5e12, 세정 후 1e11)는 출처 불명·미검증 오귀속** — 2026-09-09 원문 확보 결과 Seo et al. 2001(doi:10.1023/A:1011242900843)은 KOH 슬러리 산화막 CMP의 K·Ca 잔류를 다루며 **Fe 수치가 본문에 없다**. 값은 오더 감각용으로 남기되 **Seo 2001을 근거로 인용 금지**
- Boltzmann은 균일 확산이중층 근사 — **pH 의존 방향만 검증**, 실라놀 특이(화학)흡착·착화제 경쟁이 겹치는 절대 흡착량 자리수는 미검증
- Wang 2024는 폴리실리콘 게이트 기원 의도적 Fe 오염 — CMP 슬러리 기원 표면 Fe와 동일 기구인지 미검증
- IRDS 노드·금속종별 정확 표값 미확보

---

## 9. `sim/tier2_physics/slurry_components.py` — BTA Langmuir 흡착 + 산화제-MRR 단봉 곡선

**목적:** (A) 부식억제제 BTA의 Langmuir 흡착등온선·억제효율, (B) 산화제 농도-MRR 정점 거동.

### (A) BTA Langmuir 흡착
```
theta = K·C / (1 + K·C)                (단분자층 피복률)
dG_ads = −R·T·ln(55.5·K)               (수용액 흡착 관례, 55.5 mol/L = 물의 몰농도)
K = exp(−dG_ads/(R·T)) / 55.5          (역변환)
IE ≈ theta                             (억제효율 ≈ 피복률)
```
- `C` [mol/L], `K` [L/mol], `dG_ads` [J/mol], `R = 8.314462618 J/(mol·K)`, `C_water = 55.5 mol/L`, T=298.15 K
- 검증: dG_ads = **−35.4 kJ/mol** → K ≈ 1e4~1e5 L/mol(1e3~1e6 범위 확인); C = 1/K에서 θ=0.5; **1 mM BTA에서 IE > 0.9**
- 출처: BTA가 Langmuir 등온선을 따르고 dG0_ads ≈ **−35.4 kJ/mol** (2차 인용, `knowledge/cmp/slurry-components-overview.md` §4). **부호(음수)와 크기(물리흡착~화학흡착 경계 −20~−40 kJ/mol)만 검증, 절대값 미검증**

### (B) 산화제 농도 vs MRR
```
레거시 단봉(Kaufman 현상론):
  MRR(C) = mrr_peak · (n+1)·x / ( 1 + n·x^((n+1)/n) ),   x = C/C_peak
  → C=0에서 0, C=C_peak에서 정확히 최대(미분=0이 x=1에서 성립하도록 지수 (n+1)/n 사용), 이후 완만 감소. n↑ → 감소 완만.

권장 포화형(판정#19 이후):
  theta(C) = K·C / (1 + K·C)      C [wt%], K [1/wt%]
```
- Kaufman 경쟁 구도: (i) 산화제가 무른 산화막(WO3/Cu2O 등) 형성 → 기계연마로 제거 vs (ii) 과도 산화막이 표면을 보호(passivation)해 제거 지연 ⇒ 단봉 곡선
- 문헌 앵커(정성): **Cu MRR은 ~1% H2O2에서 최대, 이후 감소; 글리신(착화제) 첨가 시 최대점이 ~3% H2O2로 이동** (Cambridge MRS OPL, 2차 인용). self-test가 이 이동을 재현
- 출처: **Kaufman 1991** 경쟁모델(현상론적 근사), `knowledge/cmp/slurry-components-overview.md`

### 한계
- `mrr_oxidizer()`는 "단봉+정점이동" 형태를 재현하는 **현상론 모델**이며 특정 데이터 피팅이 아니다(디지털화 데이터 미확보). **정량 절대값 미검증**
- **판정#19**(`knowledge/cmp/chi-oxidizer-curve-exponent-identifiability.md`): (n, C_peak)는 정점 아래 관측만으로는 **완전축퇴(식별 불가)**. 그래서 자유 파라미터가 K 하나뿐인 `oxidizer_coverage_langmuir()`가 신규 경로 — 관측 2점(C=0, C=C_ref)만으로 완전 식별. 물리적 근거: 산화제의 표면 흡착·산화막 형성은 가용 산화 사이트가 유한한 **포화형 표면반응**(정점형 부동태화가 아님)
- IE ≈ θ는 "피복률이 그대로 부식전류 억제율로 근사되는 통상 가정"

---

## 10. `sim/oxidizer_regime.py` — 산화제 농도-제거율 **부호**를 계산하는 층

**목적:** 같은 산화제·같은 막질에서 특허마다 반대 부호가 나오는 문제를, 물질명이 아닌 두 측정량의 경쟁으로 판정.

### 지배방정식 (트라이보코로전, Stojadinović–Mischler)
```
(A)  MRR ∝ Q(C) / sqrt( H_film(C) )

(B)  d ln MRR / d ln C = e_Q(C) − ½·e_H(C)
     ⇒ sign(dMRR/dC) = sign( e_Q − ½·e_H )

Langmuir 포화:  Q(C) = Q_max·C/(C + K_sat)
                e_Q(C) = d ln Q/d ln C = K_sat / (C + K_sat)

정점 조건 e_Q(C*) = ½·e_H  ⇒   C* = K_sat · (2/e_H − 1)
```

### 기호·단위
- `Q(C)`: 부동태화 전하밀도(막이 얼마나 자라는가, 산화제가 결정)
- `H_film(C)`: 막의 기계적 강도(얼마나 벗기기 어려운가)
- `e_Q = d ln Q/d ln C` [무차원, ≥0, 포화하며 0으로 수렴] — C≪K_sat → 1, C=K_sat → 0.5, C≫K_sat → 0
- `e_H = d ln H_film/d ln C` [무차원, 농도 무관 상수로 취급]
- `K_sat` [wt%]: 부동태막이 절반 포화하는 농도 — **전위계단법 Q(C) 곡선에서 읽는다**
- `e_H` 측정: **AFM 마모깊이 대 농도 기울기의 음수로 대용 측정 가능**

### 판정 규칙
- **e_H = 2가 부호 반전 임계** — 이 값은 (A)의 √에서 나온다(강도 효과가 제곱근으로 약화되므로, 생성이 최대로 기여해도(e_Q=1) 강도가 두 배로 자라면 진다)
- e_H ≤ 0 → C* = ∞ (관측 구간에서 증가형) / e_H = 1 → C* = K_sat / e_H ≥ 2 → C* 없음(전 구간 감소형)
- `_classify`: 관측 구간 양 끝 기울기 부호로 (+,+) 증가형 / (+,−) 단봉형 / (−,−) 감소형
- **핵심 통찰**: 증가형과 감소형은 다른 함수가 아니라 **정점 C*가 관측 구간의 오른쪽/왼쪽에 있는 것**. 본래 모든 계가 단봉형

### 입력 → 출력
팩의 `oxidizer_saturation_wt_pct`(=K_sat)와 `film_hardness_elasticity`(=e_H) → `OxidizerRegime(peak_wt_pct=C*, e_Q_at_ref, e_H, behavior, basis, notes)`. **두 값이 없으면 추정하지 않고 None 반환**("지어낸 값으로 부호를 정하면 그것은 예측이 아니라 창작이다").

### 출처
`_knowledge_audit/oxidizer_sign.md` (1차 출처 15건, DOI 전건 확인). 골격은 **Kaufman 순환 + Stojadinović–Mischler 트라이보코로전**.

### 한계
- **절대 MRR 예측을 하지 않는다** — 원 모델조차 실측 대비 한 자릿수 과대(저자 자인, 활성 입자 피복률을 1로 가정한 탓). 이 모듈은 **부호와 순위만** 다룸
- "산화막이 모재보다 무르면 증가형" 같은 **정적 비율 규칙은 문헌이 지지하지 않는다** — (B)가 요구하는 것은 비율이 아니라 농도에 대한 도함수

---

## 11. `sim/chemistry.py` — 화학-기계 결합층 (조성 → MRR 배수)

**목적:** 슬러리 조성 변화를 **기준 조성 대비 상대 MRR 배수**로 변환해 기계 모델(GW 접촉·Preston)에 넘긴다.

### 결합 원리 (물리적 통로)
```
소성 압입   δ_p = F / (2πR·H)            ∝ H⁻¹
plowing 홈  A_f = (4/3)·√(2R)·δ_p^1.5    ∝ H⁻¹·⁵
⇒ 화학 조건 → 유효 경도비 (H_eff/H_0) → MRR 배수 = (H_0/H_eff)^1.5
SOFTENING_EXPONENT = 1.5  (plowing 기하에서 유도, 튜닝 파라미터 아님)
```
- `F`: 입자 하중 [N], `R`: 입자 반경 [m], `H`: 경도 [Pa]
- 근거: `knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md` §4 (verify PASS) — 화학적 연화로 H를 4배 낮추면 제거 체적은 4^1.5 = **8배**

### ⚠ 이중 계상 회피 계약 (2026-09-06 실제 사고)
팩의 `kp_m_per_pa`는 **이미 BTA가 든 실제 슬러리의 문헌 MRR에서 역산한 값**이다. 거기에 절대 억제항을 또 곱해 Cu MRR이 450 → 22.5 nm/min로 20배 떨어졌다. 그래서 모든 항이 **factor = f(현재 조성)/f(기준 조성)** 형태이고, 기준 조성에서 정확히 1.0이 된다.

### 항별 식

**(1) 산화제 `_oxidizer_term`** — 세 경로
```
Langmuir 촉진 (권장, 판정#19):  f(C) = φ + (1−φ)·θ(C)/θ(C_ref)
Langmuir 억제 (판정#20):        f(C) = φ + (1−φ)·(1−θ(C))/(1−θ(C_ref))
레거시 Kaufman 단봉(하위호환):   f = [φ+(1−φ)·MRR(C)] / [φ+(1−φ)·MRR(C_ref)]
θ(C) = K·C/(1+K·C)
```
- `φ` = 기계 하한(mechanical floor), 기본 **0.15**. 산화제 농도가 0이어도 연마입자가 하중을 받아 순수 기계 제거가 남으므로 가산 하한을 둔다
- φ 근거(`_knowledge_audit/oxidizer_floor.md` §4 규칙 R1~R3): **독립 금속막 4계에서 관측 대역 0.12~0.27로 수렴**, 금속 종류·pH 2~9·착화제 유무를 바꿔도 유지. 연마입자를 빼면 0.02로 떨어지고 경질 연마재·고하중에서 0.28~0.37 → **φ를 움직이는 것은 화학이 아니라 기계 경로의 세기**
- 적용 한계(R4): 생성 산화물이 모재보다 단단하고 착화제가 없어 φ>1이 되는 계에서는 이 결합식을 쓰면 안 된다
- 실사용 예: `w_fe_oxidizer.yaml`의 K=0.549550이 폐형식 유도(f(0)=φ, f(C_ref)=1)로 결정됨; `cu_h2o2_bta`는 억제 경로

**(2) 억제제 `_inhibitor_term`**
```
θ = K·C/(1+K·C)
잔여 제거가능률 = exp( −k_inhib · θ )
factor = exp(−k_inhib·θ(C)) / exp(−k_inhib·θ(C_ref))
K = exp(−dG_ads/(RT))/55.5  (inhibitor_dG_ads_kJ) 또는 팩의 K 직접
k_inhib 기본 3.0 (inhibitor_strength_k)
```
- **왜 (1−θ)를 안 쓰는가**: BTA 1 mM에서 θ=0.97 → (1−θ)=0.03이 하한 0.05에 걸려 **2 mM과 5 mM의 구분이 사라졌다**(배수가 1.000으로 완전히 평평). Langmuir는 단분자층이라 θ→1에서 포화되는 게 맞지만, 실제 억제 강도는 피복률만이 아니라 **막의 치밀도·재생속도**에도 달려 고농도에서도 계속 세진다 → 지수 감쇠로 대체
- **`k_inhib`는 문헌값이 없어 팩에서 받고 confidence=unverified** — 순위(더 넣으면 덜 깎인다)는 보존, 절대값은 캘리브레이션 대상

**(3) 분산제 `_dispersant_protection_term`** — 실측 테이블 상대비
`DISPERSANT_MRR_RELATIVE`: NONE 1.0, PAA 1.0("negligible"), PAM 1.0("hardly changed"), **PVA 2604/2700 = −3.6%**, **PVP 2486/2700 = −7.9%**
- 출처: **Li et al. 2021, ECS J. Solid State Sci. Technol. 10, 123008** §6 실측 — 30 wt% SiO2 콜로이달 실리카(80 nm, pH 11.0, 0.32 M K⁺, 기본 MRR 2700 Å/min)
- 반드시 `DISPERSANT_MRR_RELATIVE[kind]/DISPERSANT_MRR_RELATIVE[ref_kind]` 비율로 반환(2026-09-11 절대값 반환으로 기준조건 단위성 테스트 FAIL한 사고 있음)

**(4) 세리아 chemical tooth `_ceria_term`**
```
f(θ) = floor + a·(θ/θ_ref)^p,    a = (1 − floor)·gain
floor = ceria_mechanical_floor, 기본 1/5.5 ≈ 0.18
θ = ce3_fraction, θ_ref 기본 0.15
p = ceria_tooth_exponent, 기본 1.0(하위호환), 세리아 팩 권장 ≈ 1.65
```
- **왜 순수 비례가 아닌가(2026-09-13 정정)**: 이전 형태 `1 + gain·(f/f_ref − 1)`은 gain=1, f→0에서 정확히 0이 되어 "활성점 없으면 제거율 0"을 주장했는데 물리적으로 거짓 — 활성점이 없어도 입자는 단단한 산화물이라 기계 경로가 남는다. floor는 Netzband 5.5배에서 역산(1/5.5)
- **왜 선형(p=1)이 아닌가(2026-09-14, EVIDENCE-RULES 판정#23)**: 같은 저자·같은 입자(Ce1, 58~68 nm)·같은 실험계에서 H2O2 한 축만 바꾼 **교란 통제 대응쌍(근거등급 E2)**
  - **Netzband & Dunn 2019, ECS JSS 8, P629, doi:10.1149/2.0311910jss** Fig.4 + Table I: Ce³⁺% 0 wt%에서 12%(Table I), 0.5 wt%에서 25.7%(판독) → **θ 비 2.05배**
  - **Netzband & Dunn 2020, ECS JSS 9, 044001, doi:10.1149/2162-8777/ab8393**: 같은 슬러리가 H2O2 무첨가 상용 대비 2.0배, 0.5 wt%에서 5.5배 → **MRR 비 2.75배**
  - 선형이면 MRR 비가 θ 비(2.05)를 넘을 수 없다 → **선형 반증**. 역산: floor=0 → p = ln2.75/ln2.05 = **1.41**, floor=1/5.5 → p = **1.65**
  - 한계(자인): (a) θ와 MRR이 같은 표가 아니라 연속 두 논문 — 동일 입자 로트 보장은 본문 서술에 의존 (b) 2점이므로 p는 할선이지 국소 기울기 아님 (c) 2019 논문 자체는 "Ce³⁺ 자리 수가 반응속도를 직접 정하지 않고 확률을 높인다"고 서술 — 초선형 메커니즘(활성점 군집·협동)은 미확인
- **abrasive == 'ceria'일 때만 적용**. 실리카에 쓰면 안 된다(메커니즘이 다름)

**(5) pH 연화 `_ph_softening_term`**
```
H/H0 = max( 1 − k·(pH − pH_ref), 0.2 )
factor = (H/H0)^(−1.5)
```
- `ph_softening_per_unit`(=k)이 팩에 없으면 **아예 적용하지 않는다**. "가장 약한 항" — 선형 가정, 미검증

**(6) 종합 `chemistry_factor(pack)`**
`factor = Π(각 항)`. 항이 하나도 없으면 factor=1.0, `active=False`로 "화학층 비활성"을 notes에 명시(조용히 1.0을 쓰면 "화학을 반영했다"는 거짓말이 된다). 항이 2개 이상이면 **"화학 항들을 독립으로 보고 곱했다. pH-흡착, 산화제-세리아 산화환원 같은 커플링은 미모델링"** 경고를 남긴다.

### 정직성 규약 (docstring)
- 모든 계수는 팩에서 온다 — 코드에 화학 상수를 박지 않는다
- **절대값을 주장하지 않는다.** 이 층이 내는 것은 "기준 조건 대비 몇 배"이고 기준 조건 자체는 캘리브레이션 대상
- 목표는 **순위(A 조성 vs B 조성)**이지 절대 MRR이 아니다 (POSITIONING.md §3: 데모 대체가 아니라 스크리닝)

---

## 부록 — 면접 답변용 축약 체인

| 물리 이론 | 핵심식 | FabSim 모듈 | 1차 출처 |
|---|---|---|---|
| DLVO | V_T = −Aa/(12h) + 2πε₀ε_r a ζ² ln(1+e^{−κh}) | `dlvo_colloid` | Israelachvili 2011 |
| Debye 차폐 | κ⁻¹ = 0.304/√I nm | `dlvo_colloid` | 동상 |
| Henry 전기영동 | ζ = 3ηµ_E/(2ε₀ε_r f(κa)) | `dlvo_colloid` | Malvern ELS |
| Nernst/Pourbaix | dE/dpH = −0.0591·m/n | `pourbaix_nernst_slope`, `cu_pourbaix` | CRC Vanysek, Tamilmani 2005, Gamagedara&Roy 2024 |
| 갈바닉 | ΔE0 = E0_c − E0_a | `galvanic_hydroxide_ph` | CRC Vanysek |
| 수산화물 용해도 | pH* = (logK − logC)/2 | `galvanic_hydroxide_ph` | minteq.v4.dat |
| Langmuir 흡착 | θ = KC/(1+KC), ΔG = −RT ln(55.5K) | `slurry_components`, `chemistry` | Kaufman 1991, BTA −35.4 kJ/mol |
| 경쟁 Langmuir | σ_i = σ₀K_i[M_i]/(1+K_H[H⁺]+ΣK_j[M_j]) | `competitive_metal_langmuir` | Loewenstein 1999 Eq.22 |
| Davies + Ringbom | logK' = logK(I) − log α_H(pH) | `chelation_surface_charge` | NIST46.2 / minteq |
| 세리아 산화환원 | f = 2x, S = MRR_ox/MRR_nit | `ceria_redox_selectivity` | Netzband&Dunn 2020, Brugnoli 2023, Hwang&Kim 2024 |
| 트라이보코로전 | sign(dMRR/dC) = sign(e_Q − ½e_H), C* = K_sat(2/e_H − 1) | `oxidizer_regime` | Stojadinović–Mischler |
| 화학-기계 결합 | MRR 배수 = (H₀/H_eff)^1.5 | `chemistry` | plowing 기하 A_f ∝ H^−1.5 |
