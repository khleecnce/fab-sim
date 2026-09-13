# CMP 지식 전수감사 — 패턴 평탄화·균일도·소모품 수명 축

> 작성: 2026-09-13 · 범위: 패턴밀도→유효압력, 단차 동역학, 디싱/에로전, WIWNU,
> 엣지효과, 패드 수명, 컨디셔닝, 균일도 지표 정의
> 원칙: 제품명·고객 조건 없이 일반 변수로만 서술한다. 각 식은 "산화막을 금속막으로
> 바꿔도 성립하는가"를 통과한 것만 본문에 두고, 막종에 종속된 것은 명시적으로
> "막종 종속"이라 적는다. 값은 지어내지 않는다 — 못 찾은 것은 **미확보**로 적는다.

---

## 0. 공통 기호·단위 표 (전 축 공용)

| 기호 | 의미 | SI 단위 | 비고 |
|---|---|---|---|
| $P_{app}$ | 인가(명목) 압력 = 하중/명목접촉면적 | Pa | 공정 레시피 값 |
| $P_{eff}$ | 유효(국소) 압력 — 실제로 피처가 받는 압력 | Pa | 관측량이 아니라 모델 산물 |
| $V$ | 패드-웨이퍼 상대속도 | m·s⁻¹ | 회전식에서 위치·시간 함수 |
| $K_p$ | Preston 계수 | Pa⁻¹ (= m²·N⁻¹) | lump 상수 |
| $K$ | blanket(비패턴) 제거율 | m·s⁻¹ | $K=K_p P_{app} V$ |
| $\rho_{pattern}$, $\rho_0$ | 국소 설계 패턴밀도 (up area 면적분율) | – (0~1) | 레이아웃에서 계산 |
| $\rho_{eff}$ | 유효 패턴밀도 (필터 가중평균) | – (0~1) | |
| $h_{step}$, $z_1$ | 국소 단차 (up−down 높이차); $z_1$은 초기값 | m | |
| $w$, $s$ | 라인폭, 스페이스 | m | |
| $L_{PL}$ | 평탄화 길이 (planarization length) | m | 필터 특성길이 |
| $D$ | 디싱 깊이 | m | |
| $E$ | 에로전 (막 전체 감소량) | m | |
| $t$ | 시간 (문맥별: 연마시간 / 패드 사용시간) | s 또는 h | **축마다 자릿수가 다르다 — §6 주의** |
| $F_c$ | 컨디셔너 하중 | N | |
| $s_{sweep}$ | 컨디셔너 스윕률 | 왕복·min⁻¹ 또는 rad·s⁻¹ | |
| $\sigma_z$ | 패드 asperity 높이 표준편차 | m | |
| $\eta$ | asperity 면밀도 | m⁻² | |
| $\beta_a$ | asperity 곡률반경 | m | |
| $E^*$ | 등가 탄성계수 | Pa | $1/E^*=(1-\nu_1^2)/E_1+(1-\nu_2^2)/E_2$ |

**차원 검사 기준식**: Preston $\dot z = K_p P V$ → $[\mathrm{m\,s^{-1}}] = [\mathrm{Pa^{-1}}][\mathrm{Pa}][\mathrm{m\,s^{-1}}]$ ✓.
아래 모든 축의 차원 검사는 이 항등에 귀착시켜 수행했다.
1차 출처: F. W. Preston, "The Theory and Design of Plate Glass Polishing Machines,"
*J. Soc. Glass Technol.* **11**, 214–257 (1927). ⚠ **원문 미확보** — 학회(sgt.org) 유료 아카이브,
HathiTrust 스캔본 접근 제한. 제목·권·쪽수는 학회 스토어 서지로 확인. 2차 인용 상태.

---

## 1. 패턴밀도 → 유효압력

### 1.1 모델식

**(a) 순수 하중전달(1/ρ) 모델 — Stine/Ouma/Boning 밀도모델의 기반 가정**

패드가 볼록(up) 영역만 접촉한다고 하면, 같은 총하중이 면적분율 $\rho$ 위에만 실린다:

$$P_{eff}(x,y) = \frac{P_{app}}{\rho_{eff}(x,y)}, \qquad
\dot z_{up} = \frac{K}{\rho_{eff}(x,y)}$$

**(b) 유효밀도 = 레이아웃 ⊗ 가중필터 (Boning 필터 개념의 핵심)**

$$\rho_{eff}(x,y) = \big(w_{filt} * \rho_{pattern}\big)(x,y), \qquad \iint w_{filt}\,dA = 1$$

필터 $w_{filt}$는 "패드가 하중을 얼마나 멀리 퍼뜨리는가"의 임펄스응답이고, 그 특성길이가
$L_{PL}$이다. 물리적 근거는 국소 하중을 받는 탄성 반무한체의 변형 프로파일이다
(반경 $a$ 원형 하중, 완전 타원적분 형태):

$$w_{max}=\frac{2(1-\nu^2)qa}{E},\qquad w(a)=\frac{4(1-\nu^2)qa}{\pi E},\qquad \frac{w(a)}{w_{max}}=\frac{2}{\pi}$$

**$L_{PL}$의 공식 정의: 상대 가중치가 피크의 $2/\pi$로 떨어지는 폭 $L=2a$.**
결정적 성질 — **변형의 "모양"은 $E,\nu$에 무관하고 하중 면적 $a$에만 의존**한다.
따라서 재료상수는 크기만 정하고, 모양은 고정한 채 길이 하나만 캘리브레이션하면 된다.

### 1.2 단위·차원 검사

| 항 | 단위 | 검사 |
|---|---|---|
| $\rho_{eff}$ | – | 필터 정규화 $\iint w=1$ → 균일 밀도 입력 시 동일 출력 (편향 0) |
| $K/\rho_{eff}$ | m·s⁻¹ | ✓ 무차원으로 나누므로 제거율 차원 유지 |
| $w_{max}$ | $\frac{[\,-\,][\mathrm{Pa}][\mathrm{m}]}{[\mathrm{Pa}]}=[\mathrm{m}]$ | ✓ 변형은 길이 |
| 컨볼루션 | $[-]\times[\mathrm{m^{-2}}]\times[\mathrm{m^2}]=[-]$ | ✓ |

실행 확인(본 감사): 밀도 1e-6 / 0.01 / 0.1 / 0.5 / 0.9 / 1.0에서 $P_{eff}/P_{app}$ =
1e6 / 100 / 10 / 2 / 1.11 / 1.00 — 산술 항등, 아래 §1.4에서 이 극한이 왜 파탄인지 다룬다.

### 1.3 유도 가정과 깨지는 조건

| # | 가정 | 깨지는 조건 |
|---|---|---|
| A1 | 패드는 down area에 전혀 닿지 않는다 (비압축성 극한) | 단차가 패드 접촉높이 이하로 줄면 즉시 깨짐 → §2의 압축성 레짐 |
| A2 | 하중은 up area에 **균등** 재분배 | 피처 스케일이 asperity 스케일(오더 10⁻⁵ m)보다 작으면 단독으로 압력을 못 받고 이웃과 중첩된다 — 이 중첩 때문에 $1/\rho$가 성립 |
| A3 | $\rho_{eff}$는 막두께에 무관 (프로파일 직선 근사) | 측벽 경사가 큰 구조, 리플로우/보이드가 있는 막 |
| A4 | 필터는 선형·시불변·등방 | 패드 이방성(그루브 방향), 국소 소성변형 |
| A5 | 측면 증착 보정은 선폭에 bias $B$를 더하는 것으로 충분 | 컨포멀/비컨포멀 증착이 섞인 스택 (bias 부호가 막종 종속) |

### 1.4 극한 거동 — 물리적 타당성 판정

- $\rho\to 1$: $P_{eff}\to P_{app}$, $\dot z\to K$. **타당** (패턴이 없는 blanket과 같아짐).
- $\rho\to 0$: $P_{eff}\to\infty$. **비물리적 발산.** 실제로는 (i) 필터 컨볼루션이 $\rho_{eff}$의
  하한을 만들고(고립 피처도 이웃의 가중을 받음), (ii) 피처가 소성변형·패드 침하로 압력을
  스스로 제한한다. 즉 $1/\rho$는 **고밀도 쪽에서만 안전한 근사**다.
- 저밀도 과대예측은 실측으로 확인된다: 밀도 10 / 50 / 90 %에서 유효압력/인가압력 실측비가
  약 2.2 / 1.7 / 1.3배인데, $1/\rho$ 모델은 10 / 2 / 1.11배를 예측한다 —
  **저밀도에서 4배 이상 과대예측**(Sorooshian 2005 §3.3, 아래 출처). 이것이
  "왜 낮은 밀도에서 압력이 집중되는가"의 답이자 동시에 "얼마나 집중되는지는 $1/\rho$가 아니다"의 답이다.
  물리적 이유: 패드는 강체가 아니라 유한 강성을 가진 탄성체라, 저밀도 영역에서 피처 사이로
  **내려앉아(bending) down area가 하중 일부를 지지**하기 시작한다. 하중 전달 경로가 열리는 순간
  $1/\rho$의 전제 A1이 깨진다.

### 1.5 1차 출처

| 항목 | 출처 | 확보 상태 |
|---|---|---|
| 밀도모델 $\dot z = K/\rho$, 필터 개념, 타원 가중함수, $L_{PL}$의 $2/\pi$ 정의 | D. O. Ouma, *Modeling of Chemical Mechanical Polishing for Dielectric Planarization*, Ph.D. thesis, MIT EECS, 1999. hdl.handle.net/1721.1/9704 | **1차 확보** (`papers/ouma1999-mit-thesis-cmp-dielectric-planarization.pdf`, 229쪽 스캔) |
| 저널판 | Ouma, Boning, Chung et al., *IEEE Trans. Semicond. Manuf.* **15**(2), 232–244 (2002). DOI 10.1109/66.999598 | 서지만 확인, 본문 유료 **미확보** |
| 기본모델 제안 | Stine, Ouma, Divecha, Boning et al., *IEEE Trans. Semicond. Manuf.* **11**(1), 129–140 (1998). DOI 10.1109/66.661292 | 초록만, 본문 유료 **미확보** → Ouma 논문 식 5.1–5.3을 정본으로 사용(2차 인용 아님) |
| $L_{PL}\propto E_{pad}$, blanket rate 무관 | Xie, Park, Lee, Tugbawa, Cai, Boning, "Re-examining the Physical Basis of Pattern Density and Step Height CMP Models," MRS Spring 2003 | **1차 확보** (PDF), DOI 없음(학회록) |
| 유효압력 실측비(10/50/90 % → 2.2/1.7/1.3) | Sorooshian, Ph.D. dissertation, Univ. of Arizona (2005), §3.3 Tables 3.3–3.6 | **1차 확보** (`papers/sorooshian2005-dissertation-ua.pdf`) |

### 1.6 파라미터 분류

| 파라미터 | 분류 |
|---|---|
| $\rho_{pattern}(x,y)$ | **독립 측정 가능** (레이아웃 GDS에서 직접 계산, 오차원 없음) |
| $K$ | **독립 측정 가능** (blanket 웨이퍼 제거율 실측) |
| $L_{PL}$ | **피팅 필요** (밀도 특성화 마스크 + 잔막 실측 SSE 최소화). 필터 종류가 다르면 숫자를 직접 비교하면 안 된다 — 정사각=변, 원통=지름, 가우시안=1차 모멘트, 타원=$2/\pi$ 폭으로 정의가 서로 다름 |
| 필터 형태 | **문헌값 차용** (타원형이 RMS 최소라는 Ouma 표 5.3 결과) |
| bias $B$ | **독립 측정 가능** (단면 SEM/TEM), 부호는 증착방식 종속 |

### 1.7 FabSim 현 구현과의 차이

- `sim/tier1_empirical/pattern_density.py` — 가우시안 커널만 구현. **타원(완전 타원적분) 커널 미구현.**
  Ouma 표 5.3 기준 타원 42 Å vs 가우시안 56 Å RMS이므로, 현 구현은 원 모델보다 정확도가 낮은
  근사를 쓰고 있다(다만 오더·평활성은 재현).
- `sim/tier2_physics/npw_ptw_effective_pressure.py` — Sorooshian 실측표를 **조회만** 하고
  보간·외삽을 금지(ValueError)한다. 즉 FabSim은 "$1/\rho$가 저밀도에서 4배 과대예측"이라는
  사실을 **알고는 있으나 보정식으로 갖고 있지 않다.** 표 밖 밀도에 대해 쓸 수 있는 연속
  보정함수가 없는 것이 현재 최대 갭.
- `sim/tier1_empirical/wiwnu_pattern_combined.py` — $RR(r,x)=K(r)/\rho_{eff}(x)$로 반경축과
  다이축을 **분리가능(separable)** 곱으로 결합. 교차항(엣지에서만 패턴 영향이 증폭되는 비선형)은
  없음을 모듈 docstring이 명시.

---

## 2. 단차 감소 동역학과 평탄화 길이

### 2.1 모델식 — 두 레짐 + 통합

**(a) 비압축성 패드 (Ouma 식 5.2–5.3; Grillaert 계열)** — 단차는 **선형**으로 감소:

$$\dot z_{up}=\frac{K}{\rho_{eff}},\qquad \dot z_{down}=0
\;\Longrightarrow\;
h_{step}(t)=z_1-\frac{K}{\rho_{eff}}\,t \quad (t<t_c),\qquad
t_c=\frac{\rho_{eff}\,z_1}{K}$$

즉 up은 $K/\rho$로 깎이고 down은 0으로 깎이므로 단차 감소율이 $K/\rho_{eff}$로 일정하고,
$t_c$에서 정확히 소멸한다. 막두께 폐형해:

$$z(t)=\begin{cases} z_0 - K t/\rho_{eff} & t<t_c\\[2pt] z_0 - z_1 - K t + \rho_{eff} z_1 & t>t_c\end{cases}$$

**(b) 압축성 패드 (Burke; Tseng 계열)** — 단차 축소율이 남은 단차에 비례 → **지수 감쇠**:

$$\frac{dh_{step}}{dt}=-\frac{h_{step}}{\tau}\;\Rightarrow\;h_{step}(t)=h_c\exp\!\big(-(t-t_c)/\tau\big)$$

**(c) 통합모델 (Smith et al., MRS99 eq.4)** — 큰 단차 동안 (a), 접촉높이 $h_1$ 이하에서 (b)로 전이:

$$h_1=a_1+a_2\exp(-\rho_{eff}/a_3)$$

**(d) 공간축 — 평탄화 길이**: 계단형 밀도 경계에서 두께 천이 폭이 $L_{PL}$이다.
$$\Delta\rho=\rho_{max}-\rho_{min}\ \ (L_{PL}\uparrow \Rightarrow \Delta\rho\downarrow),\qquad
\mathrm{TIR}=\Delta\rho\cdot z_1$$
$$t_{lp}=\frac{\rho_{max} z_1}{K},\qquad H_0=H_{target}+z_1(1+\Delta\rho)$$

### 2.2 단위·차원 검사

| 식 | 좌변 | 우변 | 판정 |
|---|---|---|---|
| $t_c=\rho z_1/K$ | s | $[-]\cdot\mathrm{m}/(\mathrm{m\,s^{-1}})=\mathrm{s}$ | ✓ |
| $h=h_c e^{-(t-t_c)/\tau}$ | m | m · (무차원) | ✓, $\tau$[s] |
| $\mathrm{TIR}=\Delta\rho z_1$ | m | $[-]\cdot$m | ✓ |
| $h_1=a_1+a_2e^{-\rho/a_3}$ | m | $a_1,a_2$[m], $a_3$[–] | ✓ |

수치 검사(본 감사 실행): 식 5.3의 두 레짐이 $t_c$에서 연속(불연속 < 3.3e-5 Å, 부동소수 잔차),
선형 레짐 기울기 $dz/d\rho = z_1$ 재현(7500.000000000001 vs 7500) — **PASS**.

### 2.3 유도 가정과 깨지는 조건

| # | 가정 | 깨지는 조건 |
|---|---|---|
| B1 | (a)에서 down area 제거율 = 0 | 패드 강성이 낮거나 단차가 작을 때 — 실제로 $h_1$ 아래에서 항상 깨짐 |
| B2 | $K$가 시간에 대해 상수 | 패드 마모 드리프트(§6) 또는 슬러리 소모. **장시간 폴리시에서 반드시 깨진다** |
| B3 | $\rho_{eff}$가 시간에 무관 | 오버폴리시로 up 면적이 변형되는 구간 |
| B4 | 모델이 넓은 제거량 범위에서 유효 | Ouma 원문이 명시: 초기 2 µm 막에서 1.5 µm 제거 후 **모델 붕괴**(원인 미해결, 저자는 "이미 평탄화된 저지대에 압력을 덜 주는 효과 누적"으로 추정) |

### 2.4 극한 거동

- $h_{step}\to 0$: (a)는 $t_c$에서 **유한 시간에 정확히 0**, (b)는 $t\to\infty$에서 점근적으로만 0.
  둘 다 물리적으로 방어 가능하지만 **의미가 다르다** — (a)는 "완전 평탄화 시점"이 정의되고
  그 이후 blanket 레짐으로 넘어간다. 실제 실험에서 단차가 완전히 0이 되지 않는 관측은 (b) 쪽을 지지.
- $t\to\infty$: (a)는 선형 레짐 $z=z_0-z_1-Kt+\rho z_1$ → 두께가 계속 선형 감소하고
  **밀도 간 두께차(=TIR)는 더 이상 변하지 않는다**. 이것이 "$t_{lp}$ 이후 더 깎아도 TIR 불변"의 근거.
  물리적으로 타당 — 국소 평탄화가 끝나면 전 영역이 같은 $K$로 깎이므로 차이가 보존된다.
- $\rho\to 0$ (고립된 큰 필드): $t_c\to 0$ — 즉시 국소평탄, 이후 선형 레짐. 타당.

### 2.5 ⚠ 흔한 오류의 정정

**"단차가 $\exp(-x/L_{PL})$로 감쇠한다"는 식은 어느 1차 출처에도 없다.**
- 시간축: 비압축성에서는 **선형**, 압축성에서는 $\exp(-t/\tau)$ — **시간의 지수이지 거리의 지수가 아니다.**
- 공간축: 밀도 경계 천이는 타원 가중함수(완전 타원적분)의 컨볼루션이고, 가우시안 근사 시
  $\exp(-x^2/2\sigma^2)$ 형태다. **1차 지수 $\exp(-x/L_{PL})$는 출처 불명 — 채택하지 않는다.**

### 2.6 1차 출처

- Ouma 1999 thesis 5.1절(식 5.1–5.3), 7.1절(식 7.1–7.6) — **1차 확보**.
- D. Boning et al., "Pattern Dependent Modeling for CMP Optimization and Control," MRS Spring 1999 —
  **1차 확보**(PDF). 통합모델 eq.4 ($h_1=a_1+a_2e^{-\rho/a_3}$)의 출처.
- Burke(VMIC 1991) 지수 단차감쇠 원안, Tseng, Grillaert(CMP-MIC 1998), Smith et al. —
  ⚠ **전부 원문 미확보.** MRS99 / MIT thesis 계열의 재서술을 통한 **2차 인용**임을 명시한다.
  (Grillaert 계열은 KU Leuven Lirias에 "Modelling the influence of pad bending on the planarization
  performance during CMP" 레코드가 존재하는 것만 확인 — 본문 미확보.)

### 2.7 파라미터 분류

| 파라미터 | 분류 |
|---|---|
| $z_1$ (초기 단차) | **독립 측정 가능** (증착 직후 프로파일러/AFM) |
| $K$ | **독립 측정 가능** |
| $L_{PL}$ | **피팅 필요** — 밀도 마스크 특성화. 절차: PL 초기값 → $\rho_{eff}$ 계산 → 식 5.3 두께 예측 → 실측과 SSE → 갱신 반복. 데이터 요건: 계단형 밀도 마스크, 블록당 ≥3점, **up area만 측정**, 중심 die 1개 |
| $\tau$ (압축성 시상수) | **피팅 필요** |
| $a_1,a_2,a_3$ (접촉높이) | **피팅 필요** — 특성화 마스크 없이는 값이 없다 |

### 2.8 FabSim 현 구현과의 차이

- `pattern_density.py`에 비압축성 단차 소멸($t_c$)·압축성 지수감쇠·접촉높이 $h_1(\rho)$ 모두 구현,
  self-test 통과. **차이는 커널 형태뿐**(§1.7).
- 식 7.1–7.6(TIR↔증착량 설계식)은 **미구현** — 지식노트에만 있고 코드 경로가 없다.

---

## 3. 디싱 / 에로전

### 3.1 정의 (막종 무관하게 성립하는 형태로)

- **디싱 $D$**: 평탄화 후 기준면(주변 유전체 표면)과 **매립 피처 내부 최저점** 사이의 수직거리.
  피처가 오목하게 파인 깊이.
- **에로전 $E$**: 증착 시 두께와 CMP 후 두께의 차 — 피처 어레이 위 막이 통째로 얇아진 양
  (보통 인접 비패턴 필드 대비 측정).
- **총 손실 = 필드 손실 + 국소 에로전 + 디싱**. 셋 다 오버폴리시 시간에 대해 단조 증가.

### 3.2 지배 모델식 — 정상상태 디싱 (removal-rate diagram)

디싱이 깊어질수록 피처 재료의 제거율은 (패드 접촉 상실로) 감소하고, 주변 재료의 제거율은
증가한다. 둘이 같아지는 지점이 그 구조에서 관측되는 **최대 디싱**:

$$r_{feature}(D)=r_{f,0}\Big(1-\frac{D}{d_{max}}\Big),\qquad
r_{surround}(D)=\frac{r_{s,0}}{1-\rho}\big(1+bD\big),\qquad
r_{feature}(D_{ss})=r_{surround}(D_{ss})$$

**압력 보존에서 기울기를 고정한 닫힌 해 (Tugbawa 2002, eq. 3.39–3.42)** — 위 식의 $b$를
자유 파라미터로 두지 않고 $\rho/((1-\rho)d_{max})$로 **고정**한 결과:

$$\boxed{D_{ss}=\frac{d_{max}(r_f-r_s)(1-\rho)}{r_f(1-\rho)+r_s\rho}},\qquad
\tau_D=\frac{d_{max}(1-\rho)}{r_f(1-\rho)+r_s\rho}$$
$$D(t)=D_2 e^{-(t-t_3)/\tau_D}+D_{ss}\big(1-e^{-(t-t_3)/\tau_D}\big)$$
$$\dot E_{ss}=Y_1=\frac{r_f r_s}{r_f(1-\rho)+r_s\rho},\qquad
E(t)=Y_1 (t-t_3)+Y_2(D_{ss}-D_2)\big(e^{-(t-t_3)/\tau_D}-1\big)$$

$d_{max}$는 형상 종속 경험식: $d_{max}=B\,w^{\alpha}s^{\beta}$ (스페이스 포화 $s\ge s_l$에서 $s\to s_l$),
엣지 라운딩 승수 $\psi(s)=C e^{-s/s_c}+1$.

### 3.3 지배 인자 / 선택비와의 관계

| 인자 | 방향 | 근거 |
|---|---|---|
| 선택비 $r_f/r_s$ | $D_{ss}\propto (r_f-r_s)$ → **선택비가 클수록 디싱↑, 에로전↓** | 위 $D_{ss}$, $Y_1$ 식. $r_f=r_s$면 $D_{ss}=0$(본 감사 수치 확인) |
| 패턴밀도 $\rho$ | $D_{ss}$는 $\rho$↑에서 감소, $Y_1$(에로전 속도)은 $\rho$↑에서 **단조 증가** | $Y_1(\rho\to0)=r_s$, $Y_1(\rho\to1)=r_f$ (본 감사: 300 → 3000, $r_f$=3000·$r_s$=300 기준) |
| 라인폭 $w$ / 스페이스 $s$ | $d_{max}\propto w^\alpha s^\beta$ → 넓은 피처·넓은 스페이스일수록 디싱↑ | 경험식 |
| 오버폴리시 시간 | 디싱은 $\tau_D$로 **포화**, 에로전은 **선형 무한 증가** | 위 $D(t)$, $E(t)$ |
| 상호작용 거리 | 금속계 damascene의 상호작용 거리는 유전체(mm 오더)보다 **수십 배 짧다** — 즉 feature-level 모델이 die-level보다 중요해진다 | Park VMIC98 |

**핵심 비대칭**: 디싱은 자기제한적(포화), 에로전은 비제한적(선형). 따라서 오버폴리시 시간은
디싱이 아니라 **에로전이 결정**한다. 그리고 클리어링을 위해 오버폴리시가 불가피하므로
**디싱/에로전은 원리적으로 0이 될 수 없다.**

### 3.4 차원 검사

$[D_{ss}] = \dfrac{[\mathrm{m}][\mathrm{m\,s^{-1}}][-]}{[\mathrm{m\,s^{-1}}]}=[\mathrm{m}]$ ✓ ·
$[\tau_D]=\dfrac{[\mathrm{m}][-]}{[\mathrm{m\,s^{-1}}]}=[\mathrm{s}]$ ✓ ·
$[Y_1]=\dfrac{[\mathrm{m\,s^{-1}}]^2}{[\mathrm{m\,s^{-1}}]}=[\mathrm{m\,s^{-1}}]$ ✓ ·
$[b]=\mathrm{m^{-1}}$ (고정형 $\rho/((1-\rho)d_{max})$와 일치) ✓

### 3.5 가정과 깨지는 조건

| # | 가정 | 깨지는 조건 |
|---|---|---|
| C1 | 제거율이 디싱 깊이에 **선형** 의존 | 깊은 디싱에서 슬러리 유동·접촉이 비선형이 되는 영역 |
| C2 | 정적 식각(화학적 용해)이 없다 | 화학 공격성이 큰 슬러리 — 디싱 **하한**이 $D_{ss}$가 아니라 식각률로 정해진다(모델 범위 밖) |
| C3 | 장거리 높이차 항 없음 | 오버폴리시가 길어지면 모델이 **과대예측**(원저자 §4.2 명시) |
| C4 | $\rho$가 시간불변 | 배리어 클리어 전후로 유효 밀도가 바뀌는 구간 |

### 3.6 극한 거동

- $\rho\to 0$: $D_{ss}\to d_{max}(r_f-r_s)/r_f$ (유한, 본 감사 수치 1800 Å) — 고립 피처의 최대 디싱. 타당.
- $\rho\to 1$: $D_{ss}\to 0$ — 주변 재료가 없으므로 디싱을 정의할 기준면이 사라진다. 수식상 0은 **정의 퇴화**이지 물리적 "평탄"이 아님에 주의.
- $t\to\infty$: $D\to D_{ss}$ (포화), $E\to\infty$ (선형). 위 비대칭과 일치.
- $r_f\to r_s$ (선택비 1): $D_{ss}=0$ — 타당(같은 속도로 깎이면 단차가 안 생긴다).

### 3.7 1차 출처

| 항목 | 출처 | 확보 |
|---|---|---|
| 닫힌 시간해 eq.3.37–3.49 | T. Tugbawa, Ph.D. thesis, MIT EECS, 2002, *Chip-Scale Modeling of Pattern Dependencies in Copper CMP* | **1차 확보** (`papers/tugbawa2002-thesis-mit-chip-scale-cu-cmp.pdf`) |
| 디싱/에로전 정의, 피치·스페이스 트렌드, 상호작용 거리 | T. Park, T. Tugbawa, J. Yoon, D. Boning et al., VMIC 1998 | **1차 확보** (`papers/park1998-vmic-cu-damascene.pdf`) |
| removal-rate diagram, 정상상태 디싱 개념 | Boning et al., MRS Spring 1999, Fig.13 | **1차 확보** |
| 금속 CMP 정상상태 디싱의 독립 계보 | N. Elbel, B. Neureither, B. Ebersberger, P. Lahnor, "Tungsten Chemical Mechanical Polishing," *J. Electrochem. Soc.* **145**(5) (1998). DOI 10.1149/1.1838533 | 서지·DOI 확인, 본문 유료 **미확보** (미러 사이트 미러 3곳 무응답, 2026-09-13). **2차 인용** |
| 디싱/에로전 측정 구조 | US5723874 (dishing/erosion monitor), US7197726B2 (test structures) | **1차 확보** (특허 전문) |

### 3.8 파라미터 분류

| 파라미터 | 분류 |
|---|---|
| $r_f$, $r_s$ (블랭킷 유효 제거율) | **독립 측정 가능** — FabSim은 기본값을 두지 않고 호출자가 명시하도록 강제(옳은 설계) |
| $\rho$ | **독립 측정 가능** (레이아웃) |
| $d_{max}$, $B,\alpha,\beta,s_l$ | **피팅 필요** — 장비·슬러리·마스크 종속. 문헌 표 값을 그대로 쓰면 안 된다 |
| $C, s_c$ (엣지 라운딩) | **피팅 필요** |
| $\tau_D$, $Y_1$ | **유도값** — 자유 파라미터 아님(위 식으로 결정) |

### 3.9 FabSim 현 구현과의 차이

- `cu_dishing_erosion_tugbawa.py` — eq.3.37–3.42, 3.46, 3.49 그대로 구현. 캘리브레이션 상수가
  특정 장비·슬러리·마스크 전용임을 docstring이 경고하고 있음(양호).
- `pattern_density.py::steady_state_dishing` — 유전체 쪽 기울기 $b$를 **자유 파라미터**로 둔
  구버전. Tugbawa eq.3.33은 이를 압력 보존에서 **고정**한다. 두 구현이 **공존**하며 대체되지 않았다 →
  **호출부에서 어느 쪽을 쓰는지 혼동될 위험**이 현재 갭.
- 정적식각(SER) 하한(가정 C2)은 **미구현**.

---

## 4. 웨이퍼 내 균일도 (WIWNU) — 운동학 기여 vs 압력장 기여의 분리

### 4.1 모델식

$$\mathrm{MRR}(r)=K_p\cdot P(r)\cdot \big\langle |v(r,\theta)|\big\rangle_\theta$$

**곱 구조**이므로 두 기여를 분리해 각각 평가할 수 있다.

**(a) 운동학(속도) 기여.** 회전식 CMP에서 웨이퍼 자전으로 반경 $r$의 점은 $\theta$ 전구간을
균일하게 훑는다. 순간 상대속도는 반경에 따라 다르지만 **자전 평균으로 거의 상쇄**된다.
$\omega_{wafer}=\omega_{platen}$이면 상대속도가 **위치에 완전 무관**해지고 속도 기여는 정확히 0이 된다.

**(b) 압력장 기여.** 멤브레인 존압 분포 + 리테이너링/엣지효과가 수 %급 비균일을 만든다.

**분리 판정(FabSim 자체 시뮬레이션, 문헌 수치 아님)**: 속도만(균일 압력, 전형 RPM비)
half-range **0.195 %** vs 압력만(엣지 압력 +30 % 집중, 속도 균일) **14.11 %** — 약 **70배**.
→ **WIWNU의 주범은 압력장**이며, 운동학은 2차 효과다. 이 결론은 $P\cdot V$가 곱이라는
구조에서 강화된다: 속도가 균일해지는 조건에서 MRR 반경 프로파일은 **순수하게 $P(r)$을 따른다.**

**(c) 결합 시 지표의 대수적 성질.** 반경(r)과 다이 내부(x)가 분리가능한 곱이면
$$\mathrm{CV}^2_{comb}=\mathrm{CV}_r^2+\mathrm{CV}_x^2+\mathrm{CV}_r^2\mathrm{CV}_x^2\ \ge\ \max(\mathrm{CV}_r^2,\mathrm{CV}_x^2)$$
즉 CV(=1σ 지표)는 **결합하면 반드시 커진다**. 반면 half-range는 max/min 두 점에만 의존하므로
이런 하한 보장이 없다 — 지표 선택이 결론을 바꾼다.

### 4.2 차원 검사

$[\mathrm{MRR}]=[\mathrm{Pa^{-1}}][\mathrm{Pa}][\mathrm{m\,s^{-1}}]=[\mathrm{m\,s^{-1}}]$ ✓.
지표는 전부 무차원(%)이며 면적가중 평균은 $dA\propto r\,dr$를 써야 한다 —
균일가중을 쓰면 외곽 annulus의 면적 우세를 놓쳐 WIWNU를 과소평가한다.
검증 앵커: 선형 반경 프로파일 $P=P_c+(P_e-P_c)(r/R_w)$의 면적가중 평균 해석해
$\bar P=P_c+\frac23(P_e-P_c)$, half-range $=(P_e-P_c)/(2\bar P)$ = **18.75 %**
(FabSim 수치 18.72 %, 상대오차 0.16 %).

### 4.3 가정과 깨지는 조건

| # | 가정 | 깨지는 조건 |
|---|---|---|
| D1 | 축대칭 ($\theta$ 의존 무시) | 캐리어 기울기, 슬러리 공급 편심, 패드 국소 마모 → azimuthal 성분 발생 |
| D2 | $K_p$가 반경에 무관 | 슬러리 막두께·체류시간의 반경 비균일(중앙 결핍/엣지 과잉), 반경별 온도 구배 |
| D3 | 속도 평균이 완전한 $\theta$ 평균 | 연마시간이 자전 주기의 정수배가 아닐 때(짧은 스텝에서 잔차) |
| D4 | 반경축과 다이축이 분리가능 | 엣지 다이가 스크라이브에 잘리거나, 엣지에서만 패턴 영향이 증폭되는 비선형 결합 |

### 4.4 극한 거동

- $\omega_{wafer}\to\omega_{platen}$: 속도 기여 → 0, WIWNU는 순수 압력장. **구조적으로 타당**.
- $P(r)\equiv$ const 이고 속도 균일: WIWNU → 0 (FabSim self-test에서 <1e-9 %). 타당.
- 엣지 압력 집중 진폭 → 0: WIWNU가 단조 감소해 0으로 수렴. 타당.

### 4.5 1차 출처

| 항목 | 출처 | 확보 |
|---|---|---|
| "WIWNU 산업 표준 없음" | W. Lee, D. Boning et al., "A study of within-wafer non-uniformity metrics," IWSTM 1999. DOI **10.1109/IWSTM.1999.773193** | DOI 실존 확인, IEEE 유료 + 미러 사이트 미러 차단 → **1차 미확보**, 초록만 |
| half-range 정의 | J. Luo & D. Dornfeld, "Wafer-Scale CMP Modeling of Within-Wafer Non-Uniformity" (escholarship) | PDF 바이너리 **본문 미확보**, 스니펫만 |
| 탄성 패드 변형 기반 wafer-scale 압력해 | Fu & Chandra, *J. Electron. Mater.* **30**, 400–408 (2001). DOI **10.1007/s11664-001-0051-x** | Springer 유료 **미확보** |
| 멀티존 캐리어 압력 제어 | US6558232, US6966822 (multi-pressure zone loading) | 특허 공개문 확인 |

### 4.6 파라미터 분류

| 파라미터 | 분류 |
|---|---|
| $\omega$비, $r_{cc}$(중심거리), $R_w$ | **독립 측정 가능** (장비 설정값) |
| $K_p$ | **피팅 필요** (blanket 실측에서 역산) |
| $P(r)$ 형상 (엣지 집중 진폭 $A$, 지수 $n$) | **피팅 필요** — 문헌은 **형상만** 제공하고 계수는 주지 않는다. FabSim은 이를 "예시값"으로 명시 |
| 존 압력 세팅 | **독립 측정 가능** (레시피) |

### 4.7 FabSim 현 구현과의 차이

- `sim/tier1_empirical/wiwnu.py` — $P(r)$을 **주입받는 프레임**만 제공한다. 압력 프로파일을
  탄성/굽힘 FEM으로 **푸는 경로는 없다** (1차 FEM 계산 아님). 이것이 구조적 최대 갭:
  현재 WIWNU 예측은 "압력 프로파일을 가정하면 지표가 나온다" 수준이지
  "장비 설정 → 압력 프로파일"의 전달함수가 없다.
- 존압 민감도 "엣지존 +1 %p당 ΔWIWNU ≈ 0.49 %p"는 **합성 예시**이며 절대값 미검증.

---

## 5. 엣지 효과 — 리테이너링과 엣지 배제

### 5.1 모델식

**(a) 강체 플랫펀치 해 (상한 근사).** 강체 원형 펀치가 탄성 반무한체를 누를 때:
$$\frac{p(r)}{\bar p}=\frac{1}{2\sqrt{1-(r/R_w)^2}}\quad\Rightarrow\quad p(r\to R_w)\to\infty$$

본 감사 수치(300 mm 웨이퍼, $R_w=150$ mm, 정규화 형태 $1/\sqrt{1-(r/R_w)^2}$):
엣지에서 10 / 5 / 1 / 0.5 / 0.1 mm 지점 발산 배율 = **2.79 / 3.91 / 8.67 / 12.26 / 27.39배**.
→ 실무 리테이너링 갭 스케일(0.1–0.5 mm)에서 이미 수배~수십배. **강체 근사는 과도하게
발산하므로 그대로 쓰면 안 되고, 이것이 탄성 패드 모델(Fu–Chandra, Boning 계열)이
필요한 정량적 이유다.**

**(b) 리테이너링의 역할.** 링이 웨이퍼 바깥 패드를 **선(先)가압**해 특이점을 완화한다.
정적 FEA(12인치 플랫폼)의 정량 결론은 **상대 배율**로만 보고된다:
mainstream 대비 중심부 일부 노드 ≈2배, 엣지부 링 있음 ≈3배 → **링 없음 ≈4배**
(즉 링 제거 시 엣지 응력집중 33 % 악화). Preston에 의해 이 응력비가 그대로 국소 제거율 급증
(= 엣지 오버폴리시)으로 이어진다.

**(c) 엣지 배제 영역(edge exclusion).** 지표 계산에서 제외하는 웨이퍼 최외곽 링 폭 $e$.
표준이 정의하는 것은 값이 아니라 **개념(FQA, fixed quality area)**이다 —
SEMI MF1530은 "데이터 수집은 전체 FQA에 대해 수행해야 한다"고만 규정하고 FQA 폭 자체는
당사자 합의 사항으로 둔다. 따라서 **$e$는 물리 상수가 아니라 보고 규약**이다.

**엣지 보정 레버 3가지**: ① 링압을 캐리어압에 맞춤, ② 웨이퍼-링 갭 최소화,
③ 엣지존 멤브레인 압력 하향. (갭은 "최대화하거나 완전히 없애는" 양극단이 유리하다는
보고가 있음 — 중간 갭이 최악.)

### 5.2 차원 검사

$p(r)/\bar p$ 무차원 ✓. 특이점은 $r=R_w$에서 적분 가능한(integrable) 발산이므로
총 하중은 유한하다 — 즉 수학적으로는 모순이 없고, 물리적으로만 비현실적이다.

### 5.3 가정과 깨지는 조건

| # | 가정 | 깨지는 조건 |
|---|---|---|
| E1 | 웨이퍼가 강체 | 300 mm 웨이퍼(두께 오더 10⁻⁴ m)는 패드 위에서 실제로 휜다 → 항상 깨짐, 상한 근사로만 사용 |
| E2 | 패드가 선형 탄성 반무한체 | 패드 두께가 유한(오더 10⁻³ m)하고 점탄성. 서브패드가 있으면 2층 문제 |
| E3 | 링과 웨이퍼가 동일 평면 | 링 자체가 마모되어 단차가 생기면 갭 형상이 시간 함수가 됨 |
| E4 | 링압 = 캐리어압 | 실제로는 독립 제어. 표준형 링은 **항상 엣지 저제거율**을 주고, 접촉 구조를 바꾸면(접촉 세그먼트 총길이를 둘레의 약 11.5 %로 축소) 엣지 제거율을 높게/같게/낮게 **모두** 만들 수 있다 |

### 5.4 극한 거동

- $r\to R_w$ (강체): $p\to\infty$ — **비물리적**. 탄성 완충으로 유한해져야 함. 위 (a)의 수치가 그 파탄을 정량화한다.
- 링압 → 0: 링이 없는 것과 같아짐 → 엣지 응력집중 악화(3배→4배). 타당.
- 갭 → 0: 압력장이 연속이 되어 특이점 소멸. 타당.
- 엣지 배제 $e$ → 0: 엣지 롤오프가 지표에 포함되어 **WIWNU가 커진다** → 지표 인용 시
  **$e$ 병기는 필수**. (문헌 스니펫: 3 mm·5 mm 배제에서 WIWNU ≈4 %, 5 mm 저압에서 ≈3.8 % —
  ⚠ **미검증**, 독립 재현 없음.)

### 5.5 1차 출처

| 항목 | 출처 | 확보 |
|---|---|---|
| 링 유/무 접촉응력 비율(2배/3배/4배) | P. Zheng, D. Zhao, X. Lu, "Prediction of Pad Wear Profile and Simulation of Its Influence on Wafer Polishing," *Micromachines* **14**(9), 1683 (2023). DOI **10.3390/mi14091683** | **1차 확보** (Europe PMC fullTextXML, CC-BY). 절대 응력값(MPa)은 그래프에만 있어 **미확보** |
| 링 구조로 엣지 제거율 능동 조절, 접촉 11.5 % | US7121927B2, "Retaining ring structure for edge control during chemical mechanical polishing" | **1차 확보** (특허 전문) |
| 엣지 gap·패드강성·링압 상호작용 | Boning 그룹, "CMP at the Wafer Edge...," *MRS Proc.* **867**, W5.1 (2004) | 스니펫만, **본문 미확보** |
| 엣지 배제 리테이너링 원 연구 | Touzov, Fujita, Doy, IEEE ISSM 2001. DOI 10.1109/ISSM.2001.962981 | IEEE 유료 + 미러 사이트 미러 무응답 → **미확보** |
| FQA 개념 | SEMI MF1530-0707 (Reapproved 1018) §7.1.5.2 | **1차 확보** (§8 참조) |

### 5.6 파라미터 분류

| 파라미터 | 분류 |
|---|---|
| 갭 폭, 링 접촉면적비 | **독립 측정 가능** (하드웨어 치수) |
| 링압, 캐리어압 | **독립 측정 가능** (레시피) |
| 패드·서브패드 $E,\nu$ | **독립 측정 가능** (DMA/압축시험) |
| 엣지 압력 프로파일 계수 | **피팅 필요** — FEM 또는 실측 역산 |
| 엣지 배제 $e$ | **보고 규약** (합의 사항, 물리 파라미터 아님) |

### 5.7 FabSim 현 구현과의 차이

- 엣지 압력 프로파일은 `wiwnu.py`의 `p_edge_concentration(p0, amp, n)` = $P_0[1+A(r/R_w)^n]$
  **형상 주입형**. 링압·갭을 입력으로 받는 물리 전달함수 **없음**.
- 링 마모에 따른 갭 시간 변화 **미구현**.
- 엣지 배제 폭이 지표 계산에 파라미터로 노출되어 있지 않다 → §8 지표와의 결합 갭.

---

## 6. 패드 수명 — 글레이징에 의한 MRR 드리프트

### ⚠ 6.0 시간축이 세 개다 (혼동 금지)

| 축 | 스케일 | 메커니즘 | 대표 관측 |
|---|---|---|---|
| (i) 단발 연마 내부 | 분 (10⁰–10¹ min) | asperity 소성변형·접촉수 감소 | 접촉점 수 10분에 −49 %, MRR −17 % |
| (ii) 컨디셔닝 중단 후 | 분~수십 분 | 순수 마모 누적 | 31 min에 −7 %~−36 % (슬러리 종속) |
| (iii) 패드 누적 사용 | 시간 (10¹ h) | 다회 컨디셔닝의 **불균일 마모 누적** | 16–20 h에 −7.4 %~−44.9 % |

**(i)과 (iii)은 자릿수가 3자리 다르다.** 한 축의 계수를 다른 축에 쓰면 안 된다.

### 6.1 모델식

**(a) GW + Archard 마모 (미시 기반).** asperity 높이분포 $\phi(z,t)$, 분리거리 $d(t)$:
$$L_i=\tfrac43 E^*\sqrt{\beta_a}\,\delta_i^{3/2},\qquad A_i=\pi\beta_a\delta_i,\qquad \delta_i=\max(z_i-d,0)$$
$$\frac{dz}{dt}=-k_w\frac{L}{A}V \;\propto\; -C_1\sqrt{\delta}\qquad(\text{Archard})$$
하중평형 $\sum L_i = P_{app}A_n$이 매 순간 $d(t)$를 결정한다.

**(b) Population balance (거시).**
$$\frac{\partial\phi}{\partial t}+\frac{\partial}{\partial z}\!\left(\phi\,\frac{dz}{dt}\right)=B-D$$
$B$ = 컨디셔너에 의한 asperity 생성, $D$ = 소멸. 컨디셔닝 없음 = $B=D=0$.

**(c) 유체 분담 — self-limiting의 근거.**
$$P_{app}=P_a(d)+P_f(d),\qquad P_f=\frac{D_w\mu V}{4d^2}$$
**무유체 극한**: $d\to 0$까지 마모가 계속된다(정상상태 없음).
**유체 포함**: $P_f(d^*)=P_{app}$, $P_a(d^*)=0$인 유한한 $d^*$로 수렴 → **마모가 스스로 멈춘다.**
즉 패드에는 두 종류의 정상상태가 있다 — 컨디셔닝에 의한 **능동 균형**과
유체윤활에 의한 **수동 자기제한**. 저압·고속일수록 후자의 기여가 커진다.

**(d) MRR 연결.**
$$\mathrm{MRR}(t)=c_w\,\frac{P_a(t)}{A_c(t)}$$
**비자명한 함의**: MRR은 명목압력이 아니라 "asperity가 지지하는 압력 대 실접촉면적의 비"로
결정된다. 마모가 진행되면 이 비 자체가 변하므로 **Preston의 $K_p$는 상수가 아니라
패드 상태의 함수**다. 이것이 "$K_p$를 소모품 수명축에 놓아야 하는" 이론적 근거.

### 6.2 왜 **로그 감쇠**가 나오는가

컨디셔닝 중단 후 제거율은 경험적으로 $\mathrm{MRR}(t)=a-b\ln t$ 형태로 잘 맞는다.
본 감사에서 공개 실측 데이터(31 min, 11점)에 세 형태를 적합해 $R^2$를 직접 비교했다:

| 적합 형태 | $R^2$ |
|---|---|
| $\mathrm{MRR}=a-b\ln t$ (**로그**) | **0.977** |
| $\ln \mathrm{MRR}=a-bt$ (지수) | 0.862 |
| $\mathrm{MRR}=a-bt$ (선형) | 0.817 |

→ 로그형이 명확히 우세. **물리적 이유(세 겹)**:
1. **마모율이 국소 접촉압에 비례하고, 접촉압은 마모가 진행될수록 스스로 낮아진다.**
   높은 asperity가 먼저 깎이면(높은 것이 국소압이 크므로) 남은 집단의 높이편차가 줄고,
   하중이 더 많은 접촉점에 분산되어 접촉당 압력이 감소한다. 감쇠 구동력이 감쇠 결과에
   반비례하면 $\dot y \propto -1/t$ 꼴이 되고, 적분하면 $\ln t$가 나온다.
2. **하중 보존 제약이 감쇠를 억제한다.** $\sum L_i = $ const를 유지해야 하므로,
   집단이 얇아지면 $d$가 더 빨리 내려가 접촉점 수가 **오히려 늘고** 접촉당 압력은 준다.
   지수 감쇠는 "감쇠율 ∝ 현재값"을 요구하는데, 이 재분배가 그 비례성을 깨서 감쇠를 늦춘다.
3. **유체 분담이 후반부 마모를 추가로 억제**한다(위 (c)). 긴 꼬리를 만든다 = 로그.

⚠ 정직 기록: 위 $R^2$ 비교는 **하나의 공개 데이터셋(눈금 판독값)**에 대한 것이다.
"로그가 물리적으로 필연"이라는 증명이 아니라 "이 데이터에서 로그가 가장 잘 맞는다"이다.

### 6.3 차원 검사

| 항 | 검사 |
|---|---|
| $L=\frac43E^*\sqrt{\beta_a}\delta^{3/2}$ | $[\mathrm{Pa}][\mathrm{m}^{1/2}][\mathrm{m}^{3/2}]=[\mathrm{N}]$ ✓ |
| $A=\pi\beta_a\delta$ | $[\mathrm{m}][\mathrm{m}]=[\mathrm{m^2}]$ ✓ |
| $P_f=D_w\mu V/(4d^2)$ | $\frac{[\mathrm{m}][\mathrm{Pa\,s}][\mathrm{m\,s^{-1}}]}{[\mathrm{m^2}]}=[\mathrm{Pa}]$ ✓ |
| $\mathrm{MRR}=c_wP_a/A_c$ | $A_c$가 **면적분율(무차원)**일 때만 $[c_w]=\mathrm{m\,s^{-1}Pa^{-1}}$로 닫힌다. $A_c$를 면적[m²]으로 해석하면 차원이 깨진다 — **표기 함정** |
| $a-b\ln t$ | $\ln$의 인수는 반드시 $t/t_0$로 무차원화해야 한다. $b$[m·s⁻¹], $t_0$는 암묵 상수 — **문헌이 이를 생략하는 경우가 많다** |

### 6.4 가정과 깨지는 조건

| # | 가정 | 깨지는 조건 |
|---|---|---|
| F1 | asperity 높이분포가 지수/가우시안 | 컨디셔닝 중단 시 분포 **고단부에 2차 피크**가 자라 단봉 가정이 깨진다 |
| F2 | Archard 계수가 시간 상수 | 슬러리 잔류물 응착층·기공 폐색이 생기면 마모 모드가 바뀜 |
| F3 | glazing = 기계적 평탄화만 | 실제로는 (a) 소성 평탄화 + (b) 기공 막힘 + (c) 잔류물층의 **중첩**. (b)(c)의 정량 실측은 **미확보** |
| F4 | 패드 표면이 반경 균일 | (iii) 축에서 지배 인자는 시간이 아니라 **반경별 마모 균일성** — 같은 시간에도 감소폭이 6배 차이 |
| F5 | 슬러리 무관 | 응집성 강한 연마입자계는 감쇠가 4~5배 심함 — glazing은 순수 기계가 아님 |

### 6.5 극한 거동

- $t\to 0$: MRR = 초기값. 단, 실측은 **초기에 오히려 상승 후 하강**하는 비단조 거동을 보인다
  (높이 감소로 접촉당 힘이 주는 것을 **곡률반경 증가가 보상**하기 때문). 단조감소만 예측하는
  모델은 이 초기 상승을 재현하지 못한다.
- $t\to\infty$ (무유체): $d\to0$ — **비물리적**(패드가 무한 마모). 모델 파탄.
- $t\to\infty$ (유체 포함): $d\to d^*$ 유한, 마모 정지. **타당**.
- 컨디셔닝 $\to$ 항상 on: 정상상태 분포 유지, MRR 드리프트 0. 타당.

### 6.6 1차 출처

| 항목 | 출처 | 확보 |
|---|---|---|
| population balance + 유체효과, $P_f$, Eq.15 | H. Shi, T. A. Ring, "CMP pad wear and polish-rate decay modeled by asperity population balance with fluid effect," *Microelectron. Eng.* **87**, 2368–2375 (2010). DOI **10.1016/j.mee.2010.04.010** | **1차 확보** (저자 공개 PDF, `papers/ring2010_polish_rate_decay_fluid.pdf`) |
| 접촉점 수 $N(t)$·평균 곡률반경 $\mu_R(t)$ 실측, 초기 MRR 상승 | S. Jeong, Y. Shin, J. Jeong, S. Jeong, H. Jeong, "Novel Probability Density Function of Pad Asperity by Wear Effect over Time in CMP," *Materials* **17**(8), 1817 (2024). DOI **10.3390/ma17081817** | **1차 확보** (CC-BY, PDF+XML) |
| "로그 감쇠", 슬러리 종속, 접촉면적-제거율 최대점 | A. S. Lawing, "Pad Conditioning Effects in CMP," NCCAVS CMPUG 2004 발표자료 | **1차 확보** (공개 PDF). 피어리뷰 아님 |
| 패드 누적 사용시간 (iii) 축 | J. Son, H. Lee, "Contact-Area-Changeable CMP Conditioning for Enhancing Pad Lifetime," *Appl. Sci.* **11**(8), 3521 (2021). DOI **10.3390/app11083521** | DOI·OA 상태만 확인, 원문 PDF **미확보** — 제3자 기술문서 재인용. **2차 인용** 명시 |
| Borucki 원 모델 | Borucki, *J. Eng. Math.* **43**, 105 (2002). DOI 10.1023/A:1020305108358 | DOI 실존만, 본문 **미확보** → Shi&Ring 재서술로 **2차 인용** |
| Stein et al. (1996) 실측 MRR 감쇠 | *J. Electron. Mater.* **25**(10), 1623 | **미확보**, 2차 인용 |

### 6.7 파라미터 분류

| 파라미터 | 분류 |
|---|---|
| $E^*$, $\nu$ | **독립 측정 가능** (DMA, 압축시험) |
| $\sigma_z$, $\eta$, $\beta_a$ | **독립 측정 가능** (공초점현미경·간섭계 표면측정) |
| $\mu$ (슬러리 점도), $V$, $P_{app}$, $D_w$ | **독립 측정 가능** |
| $k_w$ / $C_a$ (마모계수) | **피팅 필요**. 유체 포함 시 더 작은 값으로 같은 마모량을 재현한다 |
| $c_w$ (MRR 스케일) | **피팅 필요** |
| 로그 감쇠 $a,b$ | **피팅 필요**, 슬러리·컨디셔너 조합마다 다름 |

### 6.8 FabSim 현 구현과의 차이 (가장 중요한 갭)

1. **`pad_wear_glazing.py`는 유체항 없음** — Borucki 극한(무유체)만 구현. 따라서 §6.5의
   "$d\to0$ 비물리적 발산" 영역에 들어갈 수 있다. 정상상태 $d^*$가 없다.
2. **`wear_aware_kp_physical.py`가 기록한 모순(정직 기록, 값 조작 없음)**:
   고정 명목압력 + 마모 진행 시나리오에서 접촉점 수 $n(t)$가 **증가**(+17.5 %)하고,
   그 결과 $\mathrm{MRR}=\alpha\,n(t)V$ 공식은 MRR **증가**를 예측한다.
   반면 ad-hoc $\mathrm{MRR}=c_w p_r(t)$는 감소를 예측한다 — 두 곡선 상관 **−0.998**.
   원인은 두 공식이 **서로 다른 독립변수를 바꾼 실험**에서 유도되었기 때문이다
   ($n(P)$는 "집단 고정, P 변화", 마모는 "P 고정, 집단 변화"). self-test는 FAIL을 그대로 출력.
   → **현재 FabSim에는 마모 시간축에서 신뢰할 수 있는 MRR 공식이 확정되어 있지 않다.**
3. **실측 방향과의 불일치**: Jeong 2024 실측은 접촉점 수가 **감소**한다. FabSim의 GW
   Monte-Carlo는 **증가**를 낸다. `pad_glazing_jeong2024.py`는 실측 방향을 별도로 재현하지만
   `relative_mrr_proxy`는 피크 시점(t≈7 min vs 실측 2–3 min)과 t=10 min 상대값이 실측과 어긋난다
   (모듈 docstring에 정직 기록). **정량 캘리브레이션에 사용 금지 상태.**
4. **`wear_aware_endpoint.py`** — MRR(t)를 사다리꼴 적분해 엔드포인트 이동을 정량화.
   구조는 옳고 ($C_1=0$에서 정상상태 모듈로 정확히 환원, 상대오차 <1 %),
   다만 입력 MRR(t)가 위 2·3의 문제를 그대로 물려받는다.
5. **로그 감쇠 형태가 코드에 없다** — `sim/factors.py::_f_stab`는 단발 연마 내부 축(분 단위)만
   반응하고 `pad_usage_hours`(시간 단위)는 드라이버로 선언만 되어 있고 실제로 반응하지 않는다(PARTIAL).

---

## 7. 컨디셔닝 — 재생 기구, 컨디셔너 노화, 스윕 궤적

### 7.1 모델식

**(a) Cut Rate = Wear Rate 정상상태.** 패드 표면 상태는 두 경쟁 과정의 균형점:
$$\mathrm{CR}=\mathrm{WR}\ \Rightarrow\ \frac{\partial\phi}{\partial t}=0$$
$\mathrm{CR}<\mathrm{WR}$ → severe glazing, $\mathrm{CR}>\mathrm{WR}$ → 고유구조 유지(안정).
population balance 관점에서 **CR = $B$항, WR = $D$항**이며 Lawing의 정성 균형과 정확히 동치.

**(b) 마모/절삭 공통 법칙 (Evans–Marshall 소성변형형).**
$$\dot h=\frac{1}{2}\,\frac{P_n V \cot(\psi/2)}{H_{pad}^2\,A}$$
웨이퍼-패드(WR)와 컨디셔너-패드(CR)에 **같은 형태**로 적용되고, 차이는 **압입자 형상**뿐이다:
다이아몬드는 $\cot(\psi/2)$가 크고 곡률반경 $\beta$가 작아 같은 하중·속도에서 $\mathrm{CR}\gg\mathrm{WR}$.
→ **in-situ 컨디셔닝에서는 컨디셔너 절삭이 지배적**이라는 결론의 정량 근거.

**(c) 컨디셔너 그릿 → 생성되는 asperity 통계 (설계 연결점).**
$$\eta\propto \frac{1}{D_{grit}^2},\qquad \bar z\propto \frac{D_{grit}}{2},\qquad \beta_a\propto D_{grit}$$

**(d) 컨디셔너 자체의 노화 — PCR 감쇠.**
$$\mathrm{PCR}(t)=\mathrm{PCR}_\infty+\big(\mathrm{PCR}_0-\mathrm{PCR}_\infty\big)e^{-t/\tau_{PCR}},\qquad
\tau_{PCR}=\frac{-t_{anchor}}{\ln(\text{ratio})}$$
공개 산업 앵커(50 h에 초기값의 16 %에서 교체, $\mathrm{PCR}_\infty\approx0$ 근사)로
$\tau_{PCR}=27.28$ h (본 감사 재계산). 개선 설계군은 10–50 h 동안 PCR·Ra가 "안정"이라
보고되므로 $\tau_{PCR}\to\infty$ 극한으로 모델링한다.

**(e) 활성 그릿 비율.** 돌출 높이가 $[h_{lo},h_{hi}]$ 균일분포이고 침투깊이 $\delta$이면
$$f_{active}=\frac{\delta}{h_{hi}-h_{lo}},\qquad N_{eff}=f_{active}N_{total}$$
돌출 높이가 단일값이면 $f_{active}\approx1$.

**(f) 스윕 궤적 → 반경방향 절삭 분포 (왜 스윕이 프로파일을 만드는가).**
4중 회전 합성(패드 자전 $n_p$ + 팔 스윕 $n_a$ + 디스크 자전 $n_d$ + 입자 반경위치 $R_i$):
$$\alpha(T)=\alpha_0-\tfrac{2n_p}{60}\pi T$$
$$\beta(T)=\beta_s-\tfrac12\beta_{max}\cos\!\Big(\arccos\tfrac{2(\beta_0-\beta_s)}{\beta_{max}}+\tfrac{2n_a}{60}\pi T\Big)+\tfrac12\beta_{max}$$
$$\theta_i(T)=\theta_{i0}+\tfrac{2n_d}{60}\pi T$$
$$\mathbf{x}_i(T)=R_p\hat u(\alpha)+R_a\hat u(\alpha+\beta)+R_i\hat u(\alpha+\beta+\theta_i)$$
Preston형 $\mathrm{PCA}=k\,F_c\,s$이고 하중 $F_c$가 반경에 대해 거의 균일하므로,
**반경별 절삭량은 거의 전적으로 누적 스크래치 거리 $s(r)$가 결정**한다:
$$\mathrm{PCR}(r)\;\propto\; s(r)=\sum_i \int |\dot{\mathbf x}_i|\,\mathbb{1}\big[|\mathbf x_i(T)|\in r\text{-bin}\big]\,dT$$
**원리 한 줄**: 스윕은 반경별 **체류시간(dwell time)** 분포를 만들고, 체류시간 × 국소 상대속도가
곧 반경별 절삭 분포다. 스윕 모드(사인파 vs 선형)·범위를 바꾸는 것이 패드 프로파일을
제어하는 1차 레버다. 실측 보고: **PCR 결과는 패드의 기존 표면 프로파일과 거의 무관**하다
→ 마모가 진행돼도 같은 PCR(r) 형상을 재사용할 수 있다(최소한 그루브 깊이 규모에서).

### 7.2 차원 검사

| 식 | 검사 |
|---|---|
| $\dot h=\frac12 P_nV\cot(\psi/2)/(H^2A)$ | $\frac{[\mathrm{N}][\mathrm{m\,s^{-1}}]}{[\mathrm{Pa}]^2[\mathrm{m^2}]}=\frac{\mathrm{N\,m\,s^{-1}}}{\mathrm{N^2 m^{-4}\cdot m^2}}=\mathrm{m^3\,N^{-1}s^{-1}}$ ✗ — **차원이 닫히지 않는다.** 원문이 "비례상수(order-1)는 fit parameter"라 명시하므로, 이 식은 **차원 일치 관계식이 아니라 스케일링 관계**로 읽어야 한다. 실무상 $P_n$을 압력[Pa]으로, $A$를 무차원 면적비로 두면 닫히지만 **원문 표기로는 확정 불가 — 미검증** |
| $\mathrm{PCA}=kF_cs$ | $s$[m], $F_c$[N]이면 $[k]=\mathrm{m^{-1}N^{-1}\cdot m}$… Preston형으로 쓰려면 $P$[Pa]·$s$[m]이어야 $[k]=\mathrm{Pa^{-1}}$로 §0과 동일해진다. **하중이 아니라 압력으로 쓸 것** |
| $\tau_{PCR}=-t/\ln(\text{ratio})$ | [h]/무차원 = [h] ✓ |
| $f_{active}=\delta/(h_{hi}-h_{lo})$ | m/m = 무차원 ✓ |
| 궤적식 | 각도[rad], 위치[m] ✓ (본 감사: 팔 중심 궤적 반경이 $R_p$로 고정됨을 오차 <1e-9로 확인) |

### 7.3 가정과 깨지는 조건

| # | 가정 | 깨지는 조건 |
|---|---|---|
| G1 | 웨이퍼-패드와 컨디셔너-패드에 **같은** 마모법칙이 적용된다 | ⚠ 이는 원문의 명시적 서술이 아니라 FabSim 지식노트의 정합적 추론 — **미검증 가정** |
| G2 | 컨디셔닝 하중이 스윕 반경에 균일 | 팔 강성·관성으로 스윕 반전점에서 하중이 변동 |
| G3 | PCR(r) 형상이 패드 상태에 무관 | 그루브가 사라지는 EOL 근방, 국소 깊은 마모가 생긴 패드 |
| G4 | 그릿 돌출 높이 분포가 균일분포 | 실제 전착 디스크는 히스토그램이 비균일. CVD 패턴형은 단일 높이 |
| G5 | 침투깊이 $\delta$가 알려져 있다 | $\delta$는 하중·패드 경도의 함수이며 **가정값, 미검증** — FabSim은 기본값을 두지 않고 인자로만 받는다(옳은 설계) |
| G6 | PCR 감쇠가 단일 지수 | 앵커가 2차 인용이고 곡률 형태 미확인 |

### 7.4 극한 거동

- $F_c\to 0$: CR → 0 → WR이 이기고 severe glazing. 타당.
- $F_c$ 증가: **임계 하중**이 존재해, 그 이상에서는 제거율이 **포화**한다(고유구조가 복원되면
  추가 컨디셔닝이 표면을 더 바꾸지 않는다). 즉 $\partial(\text{MRR})/\partial F_c \to 0$. 타당.
- $t_{cond}\to\infty$: PCR → $\mathrm{PCR}_\infty$. $\mathrm{PCR}_\infty=0$이면 컨디셔너가
  완전 소진 → 무컨디셔닝 극한(§6)으로 연속적으로 환원. **두 모델이 이 극한에서 이어지는 것이
  구조적 정합성의 증거.**
- 스윕 범위 → 0 (한 반경에 고정): $s(r)$가 델타함수형 → 국소 깊은 홈. 타당(실제 실패 모드).
- 스윕률 $s_{sweep}\to\infty$: 체류시간이 균등해져 PCR(r)이 평탄화. 타당.
- 표면 거칠기 $Ra(t)$: 신품 패드에서 급락 후 **0.5 h 이내 평형**, 이후 17 h 동안 오차범위 내 유지
  → break-in 시상수가 매우 짧다(분 오더). 이후 정체는 CR=WR 균형점 도달로 해석.

### 7.5 1차 출처

| 항목 | 출처 | 확보 |
|---|---|---|
| CR=WR 균형, 공격성별 접촉면적(11.3/7.7/2.2 %), 로그 감쇠 | Lawing, NCCAVS CMPUG 2004 | **1차 확보**, 피어리뷰 아님 |
| Evans–Marshall 마모율, population balance 폐형식해, 그릿→asperity 통계 | T. A. Ring, A. Prasad, J. A. Dirksen, "Dynamic CMP Pad Asperity Population Balance for Conditioning and Polishing" (저자 공개 PDF; CMP-MIC Conf. Proc. 21, 2008로 인용됨) | **1차 확보**(PDF), **DOI 없음** |
| 스윕 운동학 Eq.1–9, PCR(r), 패드 프로파일 무관성 | Zheng, Zhao, Lu, *Micromachines* **14**(9), 1683 (2023). DOI 10.3390/mi14091683 | **1차 확보**. Table 2 이후(스윕 파티션·스플라인 수치)는 **미확보** |
| 스윕 프로파일이 TTV/Bow/NU에 미치는 영향 | E. A. Baisie, Z. C. Li, X. H. Zhang, MSEC2010-34264. DOI **10.1115/msec2010-34264** | **1차 확보** (9쪽) |
| PCR 지수 감쇠 앵커 (50 h → 16 %), Ra 수렴 | Entegris application note (2013), 자료번호 4435-7548ENT-1213 | **1차 확보**(공개 백서). 단 그 수치는 문서가 재인용한 Palmgren 2004(CMP-MIC) — **원문 미확보, 2차 인용** |
| 그릿 높이 분포, CVD 단일 높이 | Kim & Kang, *Int. J. Mach. Tools Manuf.* **51**, 565–568 (2011). DOI 10.1016/j.ijmachtools.2011.02.008 | 서지 확인, 수치는 노트 경유 |
| 활성 팁 비 | Tsai et al., *Math. Probl. Eng.* **2014**, 913812. DOI 10.1155/2014/913812 | **1차 확보** |
| 컨디셔닝된 패드 표면 정량 청구 | US6899612 | 특허 전문 확인 |

### 7.6 파라미터 분류

| 파라미터 | 분류 |
|---|---|
| $n_p,n_a,n_d$, 스윕 범위·모드, $F_c$ | **독립 측정 가능** (레시피/장비) |
| $R_p,R_a$, 디스크 반경, 그릿 피치/폭/돌출 | **독립 측정 가능** (하드웨어 측정) |
| $H_{pad}$, $E_{pad}$ | **독립 측정 가능** |
| $\cot(\psi/2)$ (압입자 각) | **문헌값 차용** (그릿 형상 분류에서) |
| 침투깊이 $\delta$ | **피팅 필요** (하중·경도 함수, 미검증) |
| $\tau_{PCR}$ | **피팅 필요** — 현 앵커는 **2차 인용** |
| asperity 재생항 계수 $C_{1,cond}$ 및 그 함수형 $\sqrt{z_0-z}$ | **FabSim이 세운 최소 확장 가정** — 문헌에서 가져온 식이 **아니다**. 방향성만 검증됨 |

### 7.7 FabSim 현 구현과의 차이

- `conditioner_sweep_kinematics.py` — Eq.1–9 구현. 단, 실제 배치 패턴 대신 **디스크 반경 균등샘플
  대표 입자**로 근사. 논문의 8 h 스케일 대신 self-test는 수십~수백 초만 시뮬레이션 → 형상의
  정성적 특징만 확인. **PCR(r) 절대 프로파일은 미검증.**
- `conditioner_pcr_decay.py` — 재생항 $+C_{1,cond}(\mathrm{PCR}(t)/\mathrm{PCR}_0)\sqrt{z_0-z}$는
  **문헌 식이 아니라 FabSim의 가정**임을 docstring이 명시. self-test는 정성적 순위만 검증.
- `conditioner_asperity_distribution.py` — 유사변수 스케일링 $z\to(z-d)e^{2At}+d$ 구현.
  캘리브레이션 상수 $A_0$는 "48 h에 표준편차 절반"이라는 **임의 정성 기준**에서 역산
  (문헌에 공개 $A$값 없음). **정량값 미보증.**
- `disk_active_grit_fraction.py` — 균일분포/단일높이만. `"measured histogram"` 옵션은
  실측 데이터가 없어 `NotImplementedError`.
- **전체 갭**: 컨디셔너-패드-웨이퍼 3자 결합 시뮬레이션(=$B$항이 있는 population balance)은
  아직 없다. 현재는 무컨디셔닝 극한(§6)과 PCR 감쇠(§7)가 별도 모듈로 있고,
  $\mathrm{PCR}(r,t)=\mathrm{PCR}_{shape}(r)\cdot\mathrm{decay}(t)$ 형태의 2차원 결합이
  **후보로만 제안**되어 있다.

---

## 8. 균일도 지표 정의 — 표준/문헌 기준

### 8.1 표준이 실제로 정의하는 것 (SEMI MF1530 원문 직접 확인)

이번 감사에서 **SEMI MF1530-0707 (Reapproved 1018) 전문(4쪽)을 실제로 확보·판독**했다
(downloads.semi.org는 Cloudflare 봉쇄이나, 공개 미러 PDF에서 §1–§10 본문을 읽었다).
확인한 내용:

- **§2.1 Scope**: 비접촉·비파괴로 두께와 평탄도를 측정하는 방법. 물리적 기준면 불필요.
- **§2.3**: 이 방법은 **뒷면이 이상적으로 평탄하다고 가정**했을 때의 앞면 평탄도를 측정한다
  (자유형상(free-form shape)은 측정하지 않는다). ← TTV 정의의 핵심 전제.
- **§6.3**: 대향 프로브 쌍의 변위값으로 **두께 데이터 배열 $t[x,y]$** 를 구성.
- **§5.1 + Table 1**: 평탄도 파라미터 약어는 **SEMI M1 Appendix 1(Flatness Decision Tree)** 에
  정의되며, MF1530은 그 표를 재수록한다:

| 약어 | Method | Reference Surface | Reference Plane | Construction Area | Parameter |
|---|---|---|---|---|---|
| **GBIR** | Global | Back | Ideal back surface | Entire FQA | Range (TIR) |
| GF3R / GF3D | Global | Front | Three-Point | – | Range / Deviation |
| GFLR / GFLD | Global | Front | Least squares | Entire FQA | Range / Deviation |
| SBIR / SBID | Site | Back | Ideal back surface | Entire FQA | Range / Deviation |
| **SFQR / SFQD** | Site | Front | Least squares | **Site** | Range / Deviation |
| SFSR / SFSD | Site | Front | Least squares | Subsite | Range / Deviation |

- **NOTE 1 (원문)**: "The most commonly specified flatness measurements for advanced IC production …
  are **SFQR** with a site size of either 26 mm × 8 mm or 25 mm × 8 mm and **GBIR (TTV)**."
  → **표준 문헌이 명시적으로 GBIR ≡ TTV라고 적는다.** 이것이 TTV의 1차 표준 근거다.
- **§7.1.4 / §7.1.5.3.5**: 데이터 보고 분해능 및 변위 분해능 **10 nm 이하**.
- **NOTE 2**: site flatness는 인접점 간격 **2 mm 이하**를 권고, 각 site 모서리·경계에 데이터가
  있을 것 — 그래야 유효 측정영역이 site 크기와 같아진다.
- **§7.1.5.3.6**: 프로브 센서 크기 4 mm × 4 mm (또는 합의값).
- **§8.2**: 기준 웨이퍼는 "TTV value와 flatness value"로 규정 — 표준 본문이 TTV를 용어로 사용.

⚠ **MF1530 본문에는 TTV의 대수식($t_{max}-t_{min}$)이 직접 인쇄되어 있지 않다.**
표준은 TTV를 **GBIR = 전체 FQA에 대한 Range(TIR)** 로 정의하며, 이것이 곧 최대−최소다.
명시적 수식은 SEMI M1 Appendix 1 또는 M59 용어집 소관 — **M1/M59 원문은 미확보.**

### 8.2 정의 표

$$\boxed{\mathrm{TTV}\;(\equiv\mathrm{GBIR})=t_{max}-t_{min}}\quad[\mathrm{m}]$$
$$\mathrm{CV}=100\cdot\frac{\sigma}{\bar t}\ [\%]\qquad
\mathrm{WIWNU}_{3\sigma}=100\cdot\frac{3\sigma}{\bar t}\ [\%]\qquad
\mathrm{WIWNU}_{hr}=100\cdot\frac{t_{max}-t_{min}}{2\bar t}\ [\%]$$

| 지표 | 정의식 | 출처 | 표준 지위 |
|---|---|---|---|
| TTV / GBIR | $t_{max}-t_{min}$ (전체 FQA, 이상 평탄 뒷면 기준, Range) | **SEMI MF1530 §5.1 Table 1 + NOTE 1** (원문 확인) | **표준** |
| SFQR | site 내 최소자승 기준면에 대한 Range | SEMI MF1530 Table 1 / SEMI M1 App.1 | **표준** |
| CV | $\sigma/\bar t$ | 통계 표준 정의 | 표준(통계) |
| WIWNU 3σ | $3\sigma/\bar t$ | **US6922603B1** 특허 명세: "the 3-sigma uniformity metric is … 3 times the standard deviation … divided by the mean thickness … 0% being ideal"이며 "**the 3-sigma metric is also often referred to as the WIWNU metric**" | 산업 관행(특허 명세가 1차) |
| WIWNU 1σ | $\sigma/\bar t$ | Kumar 2019 (IMAPS). DOI 10.4071/2380-4505-2019.1.000450 | 문헌 변형 |
| WIWNU half-range | $(t_{max}-t_{min})/(2\bar t)$ | Luo & Dornfeld (escholarship) | 문헌 변형 |
| radial | 방위각 평균 반경프로파일 $\bar t(r)$의 σ 또는 range / mean | Boning 그룹 variation decomposition | **단일 표준식 없음** |

**핵심 사실 3가지**
1. **WIWNU에는 산업 표준이 없다.** 정의가 갈리므로 값을 인용할 때 **정의식 병기는 필수**.
   문헌 자체가 3σ/range의 이상점 취약성을 인정하고 강건 지표를 모색해 왔다.
2. **CV ≡ 1σ WIWNU**는 수학적으로 동일하다. 3σ WIWNU = 3 × CV.
   (본 감사 재확인: 항등식 3건 모두 오차 <1e-12.)
3. **TTV는 본래 기판 두께 편차 지표**다. CMP 문맥에서 "TTV"라 하면 잔막 또는 제거두께의
   max−min을 뜻하는 **차용**인 경우가 많다 — 코드·보고서는 **"무엇의 max−min인가"**
   (기판/잔막/제거량)를 항상 명시해야 한다. 표준이 이를 구분해 주지 않는다.

### 8.3 차원 검사

TTV [m] ✓ · CV, WIWNU [%] 무차원 ✓ ·
면적가중 평균은 $\bar t=\int t\,r\,dr/\int r\,dr$ — 균일가중을 쓰면 정의가 달라진다(§4.2).
$\sigma$의 ddof는 문헌이 명시하지 않는 경우가 많다 → **모집단 σ(ddof=0)을 default**로 두고
소표본($n<10$) 보고 시 ddof를 메타데이터로 남긴다.

### 8.4 가정과 깨지는 조건

| # | 가정 | 깨지는 조건 |
|---|---|---|
| H1 | 뒷면이 이상적으로 평탄(척에 완전 흡착) | MF1530 §2.3이 명시한 전제. 뒷면 이물/흡착 불량 시 무효 |
| H2 | 측정점이 웨이퍼를 대표 | 49점 polar 배열(중심 1 + 8 + 16 + 24)은 관행이지 표준이 아님 |
| H3 | 엣지 배제 폭이 고정 | $e$를 줄이면 롤오프가 포함되어 WIWNU가 커진다 → **$e$ 병기 필수**(§5.4) |
| H4 | 분포가 단봉·대칭 | half-range는 max/min 두 점에만 의존 → **이상점 1개에 크게 반응**. 본 감사 재확인: 이상점 주입 시 Δhalf-range > Δ3σ |
| H5 | 축대칭 | radial 지표의 전제. azimuthal 성분이 크면 링 평균이 정보를 지운다 |

### 8.5 극한 거동

- $n\to\infty$ (측정점 무한): TTV는 **단조 증가**(max/min이 계속 갱신됨), CV는 수렴.
  → **TTV/half-range는 측정점 수에 의존하는 지표**이고 σ형은 아니다. 지표 비교 시 치명적.
- $\sigma\to0$: 모든 지표 → 0. 타당.
- 이상점 1개: σ형은 $1/\sqrt n$ 희석, range형은 희석 없음. **range형이 구조적으로 취약.**

### 8.6 1차 출처

| 항목 | 출처 | 확보 |
|---|---|---|
| GBIR≡TTV, SFQR, FQA, 분해능 10 nm, site 2 mm 권고 | **SEMI MF1530-0707 (Reapproved 1018)**, "Test Method for Measuring Flatness, Thickness, and Total Thickness Variation on Silicon Wafers by Automated Noncontact Scanning". 원래 ASTM F1530-94로 발행 | ✅ **1차 확보** (공개 미러 PDF 4쪽 전문 판독, 2026-09-13). downloads.semi.org는 Cloudflare 봉쇄 |
| 평탄도 파라미터 정의의 정본 | **SEMI M1** Appendix 1 (Flatness Decision Tree), **SEMI M59** (Terminology for Silicon Technology), **SEMI M20** (Wafer Coordinate System), **SEMI MF1390** (Warp) | MF1530 §4.1이 참조 문서로 명시 — **원문 미확보**, 제목·역할만 확인 |
| 3σ WIWNU = "the WIWNU metric", 49점 polar 배열(1+8+16+24), annular vs azimuthal 분류 | **US6922603B1** | **1차 확보** (특허 전문) |
| "WIWNU 표준 없음" | Lee & Boning, IWSTM 1999. DOI 10.1109/IWSTM.1999.773193 | **미확보**(유료+미러 사이트 차단), 초록만 |
| 1σ형 | Kumar 2019. DOI 10.4071/2380-4505-2019.1.000450 | PDF 바이너리 **미확보**, 스니펫 |
| half-range형 | Luo & Dornfeld (escholarship) | **미확보**, 스니펫 |
| 강건 지표 대안 | IEMT 1995. DOI 10.1109/iemt.1995.526193 | **미확보** |

### 8.7 파라미터 분류

지표에는 피팅 파라미터가 없다. 대신 **보고 규약 파라미터**가 있고, 이것들이 값을 바꾼다:

| 규약 | 성격 |
|---|---|
| 엣지 배제 폭 $e$ | **합의 사항** — 반드시 병기 |
| 측정점 수·배열 | **합의 사항** — TTV/half-range는 점 수에 의존 |
| ddof (0 or 1) | **합의 사항** — default 0 |
| 링 수 $n_{rings}$ | **합의 사항** — radial 지표 값을 바꾼다 |
| site 크기 | **표준이 예시 제공** (26×8 mm 또는 25×8 mm) |

### 8.8 FabSim 현 구현과의 차이

- `sim/metrics/uniformity.py` — TTV, CV, WIWNU 3종(3σ/half-range/1σ=CV), radial 2종을 **모두 병기**
  출력. 회사 관행식(`radial_maxring_range`)은 문헌 근거가 약함을 명시하고 **별도 필드**로 분리.
  → **정의 처리 방침은 문헌·표준과 정합.** 이 축은 현재 FabSim에서 가장 건전한 부분이다.
- **갭 1**: `definition` 문자열이 TTV 출처를 "SEMI MF1530"으로만 적는다.
  이번 감사로 확인한 정확한 근거는 **MF1530 §5.1 Table 1의 GBIR 행 + NOTE 1**이며,
  수식 자체의 정본은 **SEMI M1 Appendix 1**이다 → 출처 표기를 정밀화할 수 있다.
- **갭 2**: **SFQR/SBIR 등 site 기반 지표가 구현되어 있지 않다.** 표준이 "advanced IC production에서
  가장 흔히 규정되는 것"이라 명시한 지표가 빠져 있다 — 패턴 웨이퍼 축을 다루려면 필요.
- **갭 3**: 엣지 배제 폭 $e$가 지표 함수의 인자로 노출되어 있지 않다(§5.7과 동일 갭).
- **갭 4**: 측정점 수 의존성(§8.5)이 출력 메타데이터에 없다 — TTV를 서로 다른 점 수로 비교하면
  체계적 편향이 생기는데 이를 경고하는 장치가 없다.

---

## 9. 축 간 결합 구조 요약

```
                      [패드 상태 축]  §6 glazing / §7 conditioning
                              │  Kp = Kp(패드 상태, t)
                              ▼
  레이아웃 ρ_pattern ──(§1 필터 L_PL)──▶ ρ_eff ──▶ P_eff = P_app/ρ_eff
                                                        │
        장비(존압·링압·갭) ──(§5)──▶ P(r) ────────┐      │
        운동학(ω비) ──(§4)──▶ <|v|>_θ ────────────┤      │
                                                  ▼      ▼
                                     MRR(r, x) = Kp·P(r)·V(r) / ρ_eff(x)
                                                  │
                    ┌─────────────────────────────┼─────────────────────┐
                    ▼                             ▼                     ▼
             §2 단차/TIR                    §3 디싱/에로전          §8 지표(TTV/WIWNU)
```

**분리 가능성**: 반경축(§4,5)과 다이축(§1,2,3)은 1차 근사에서 **분리 가능한 곱**으로 결합한다
(FabSim `wiwnu_pattern_combined.py`가 이를 구현). 교차항(엣지에서만 패턴 영향이 증폭되는 비선형)은
**현재 모델에 없고 검증도 되지 않았다.**

**시간축**: 패드 상태(§6,7)는 위 전체 구조의 $K_p$를 시간 함수로 만든다.
$K_p$가 상수라는 Preston의 전제가 소모품 수명 축에서 깨지는 것이 이 절의 핵심이며,
FabSim은 이를 **알고는 있으나 신뢰 가능한 $K_p(t)$ 공식을 확정하지 못한 상태**다(§6.8).

---

## 10. 미확보·미검증 목록 (정직 표기)

| # | 항목 | 상태 |
|---|---|---|
| 1 | Preston 1927 원문 | **미확보** — 학회 유료, HathiTrust 제한. 2차 인용 |
| 2 | SEMI M1 Appendix 1, M59, M20, MF1390 | **미확보** — MF1530이 참조하는 정본. 제목·역할만 확인 |
| 3 | Stine 1998 (DOI 10.1109/66.661292) | 본문 **미확보** (IEEE 유료). Ouma thesis를 정본으로 대체 |
| 4 | Ouma 2002 저널판 (DOI 10.1109/66.999598) | 본문 **미확보**. thesis가 정본 |
| 5 | Burke (VMIC 1991), Tseng, Grillaert (CMP-MIC 1998), Smith et al. | 전부 **미확보** — MRS99/MIT 계열 재서술 통한 **2차 인용** |
| 6 | Elbel et al. 1998 (DOI 10.1149/1.1838533) | 서지만. 미러 사이트 미러 3곳 무응답(2026-09-13). **2차 인용** |
| 7 | Lee & Boning IWSTM 1999 (WIWNU 표준 부재의 1차 근거) | **미확보** — IEEE 유료 + 미러 사이트 차단 |
| 8 | Fu & Chandra 2001/2002 (탄성/점탄성 wafer-scale 압력해) | **미확보** — Springer 유료 |
| 9 | Luo & Dornfeld (half-range 정의), Boning variation decomposition | **미확보** — PDF 바이너리, 스니펫만 |
| 10 | Touzov 2001 (엣지 배제 리테이너링 원 연구) | **미확보** |
| 11 | Borucki 2002, Stein 1996, Oliver, Li 1995, McGrath & Davis 2004 | 전부 **미확보** — Shi&Ring / Moon 경유 **2차 인용** |
| 12 | Palmgren 2004 (PCR 50 h → 16 % 앵커의 원출처) | **미확보** — Entegris 문서가 재인용. $\tau_{PCR}=27.28$ h는 2차 인용 기반 |
| 13 | Son & Lee 2021 원문 PDF | **미확보** — MDPI 봇 차단. 제3자 기술문서 재인용 |
| 14 | Zheng 2023 절대 응력값(MPa), Table 2 이후 스윕 파티션 수치 | **미확보** — 그래프/뒷부분 |
| 15 | glazing의 (b) 기공 폐색률·(c) 잔류물층 두께 정량 | **미확보** — 1차 출처에 수치 없음. 정성 서술만 |
| 16 | Evans–Marshall 마모율식의 차원 정합 | **미검증** — 원문 표기로는 차원이 닫히지 않는다(§7.2). 스케일링 관계로만 사용 |
| 17 | 컨디셔너 재생항 $\sqrt{z_0-z}$ 함수형 | **FabSim 가정** — 문헌 식 아님. 방향성만 검증 |
| 18 | $A_0$ (asperity 유사변수 스케일 계수) | **임의 정성 기준**(48 h에 σ 절반)에서 역산. 문헌에 공개값 없음 |
| 19 | edge exclusion별 WIWNU 수치(3/5 mm ≈4 %) | **미검증** — 스니펫 인용, 독립 재현 없음 |
| 20 | $1/\rho$의 저밀도 과대예측을 보정하는 **연속 함수** | **부재** — 실측 표만 있고 모델이 없다. 가장 실용적인 갭 |

---

## 11. 감사 결론 — 우선순위별 갭

**P1 (모델이 틀리거나 없는 것)**
1. §6.8-2 — 마모 시간축에서 MRR 공식이 확정되지 않음. 두 후보가 **정반대 부호**를 예측하고
   self-test가 FAIL로 남아 있다. 소모품 수명 예측 전체가 이 위에 서 있다.
2. §1.7 — $1/\rho$의 저밀도 과대예측 보정식 부재. 표 조회만 가능하고 외삽 금지 상태.
3. §4.7 — "장비 설정 → 압력 프로파일 $P(r)$"의 전달함수 부재. WIWNU 예측이 가정 주입에 의존.

**P2 (근사가 원 모델보다 낮은 것)**
4. §1.7 — 타원 커널 미구현(가우시안 근사). RMS 42 → 56 Å 상당의 정확도 손실.
5. §3.9 — 디싱 모델 두 버전($b$ 자유 vs 고정)이 공존. 호출부 혼동 위험.
6. §6.8-1 — 유체 분담항 미구현 → 무유체 극한의 비물리적 발산 가능.

**P3 (보고·규약)**
7. §8.8 — SFQR 등 site 지표 미구현, 엣지 배제 폭 미노출, 측정점 수 의존성 경고 없음.
8. §2.8 — TIR↔증착량 설계식(7.1–7.6) 코드 경로 없음.
