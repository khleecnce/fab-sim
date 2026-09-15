# 신소재 CMP 전문가 (film-emerging)

## 현재 레벨: Lv1 (진행) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2
- 다음 단원: Lv1-3 (CURRICULUM.md 참조)

## 역할
Co·Ru·Mo 배선, GST(PCM), 고유전체 등 차세대 막질의 CMP — Phase 2

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]

## 실데이터 책임 (ORG.md §7.3)
신소재 실데이터 스키마 초안

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록

### Lv1-1 — Co 배선 CMP: 부식 민감성, 갈바닉, 억제제 화학 (2026-09-16)
- 노트: `knowledge/materials/film-co-interconnect-cmp-corrosion-galvanic-inhibitor.md`
- 게이트: `verify_claims.py` **PASS**(출처 9건 실존 · 검증코드 7블록 전부 실행 통과 · 출처없는 수치주장 0),
  `check_knowledge.py` **PASS**
- 자기시험: `EXAMS.md` Lv1-1 3문항 + 모범답안
- 확보 문헌 5건(전부 papers/ + INDEX.json 등록):
  `huang2019-npjmatdeg-pourbaix-magnetic-transition-metals.pdf`(10.1038/s41529-019-0088-z),
  `gamagedara2025-electrochem-cu-co-galvanic-tribo.pdf`(10.3390/electrochem6020015),
  `gamagedara2026-electrochem-mo-imidazole-galvanic.pdf`(10.3390/electrochem7010006),
  `cheng2024-apsusc-bta-derivatives-cobalt-cmp.pdf`(10.1016/j.apsusc.2024.161684),
  `yan2023-ecsjss-5mbta-cobalt-copper-cmp-preprint.pdf`(10.1149/2162-8777/accd99)
- 핵심 획득:
  1. Co 부동태 창 폭 0.7 pH 단위(10.3~11.0)이고 Co CMP pH(8.0/8.5/10.0)는 전부 창 밖 → **Co의 부동태는
     열역학이 아니라 억제제 흡착이 공급한다**.
  2. 갈바닉 폐형식 식 (15) 확보. **ΔE_corr 단독 판정은 말론산 반례로 반증**(ΔE_corr −21%인데 i_g +13%).
  3. 정지 PDP ΔE_corr는 연마 중 대비 3.6배 과대평가(0.507 → 0.142 V).
  4. Co 표면 Langmuir 재현: K_ads 474/476/622 M⁻¹, ΔG°_ads −25.21/−25.23/−25.89 kJ/mol(TTA만 원문과 3.00 어긋남).
  5. 판정 #17(평형 θ ≠ 정상상태 MRR)이 **Co라는 세 번째 막질**에서 독립 재현.
  6. **미확보(빈칸)**: Co/Ru 커플의 실측 ΔE_corr — Lv1-2 최우선 과제.

### Lv1-2 — Ru·Mo CMP: 난용해 금속의 산화제 화학, RuO₄ 생성창, 갈바닉 (2026-09-16)
- 노트: `knowledge/materials/film-ru-mo-cmp-oxidizer-chemistry-ruo4-galvanic.md`
- 게이트: `verify_claims.py` **PASS**(출처 8건 실존 · 검증코드 6블록 전부 실행 통과 · 출처없는 수치주장 0),
  `check_knowledge.py` **PASS**
- 자기시험: `EXAMS.md` Lv1-2 3문항 + 모범답안
- 확보 문헌 6건(4건 papers/ + INDEX.json, 1건 OA HTML, +CRC·[R26] 교차링크):
  `cui2013-jsst-ru-oxidizers-colloidal-silica.pdf`(10.1149/2.030301jss),
  `cui2012-jes-ru-oxide-species-periodate-ph.pdf`(10.1149/2.103203jes),
  `peethala2011-esl-cu-ru-galvanic-kio4.pdf`(10.1149/1.3589308),
  `cheng2017-jss-cu-ru-galvanic-ig-inhibitors.pdf`(10.1149/2.0181701jss),
  `he2018-jss-mo-kio3-acidic-passivation.pdf`(10.1149/2.0061806jss),
  Xu 2022 RSC Adv(10.1039/d1ra08243d, OA HTML·PDF 미확보)
- 핵심 획득:
  1. **Ru 산화제 적합성은 E° 스칼라로 못 정한다** — 연마율 정점은 최강 산화제가 아니라 E°≈1.6 V의 NaIO₄·NaClO
     (Ru를 비고체 RuO₄ 영역으로 미는 것). K₂S₂O₈(1.96 V)은 정점의 3%.
  2. **RuO₄(휘발·독성, 융점 25.4 °C) 억제창 = 알칼리 pH ≳ 9**(이온화로 휘발성 상실). Ru 팩에 pH 하한 제약 필요.
  3. **Mo는 W형(MoO₃/Mo₂O₅ 부동태 있음)** — Ru·Co와 갈림. MoO₄²⁻ 용해의 산성부동태/알칼리용해 pH 스위치.
  4. **갈바닉 양극이 커플마다 다르다**: Co/Cu→Co, Ru/Cu→Cu(540→20 mV, i_g KIO₄>H₂O₂), Mo/Cu→Mo(116/270 mV).
  5. **연마의 ΔE_corr 부호가 금속마다 반대**: Co/Cu −72%(축소) vs Mo/Cu +133%(확대) → 축소계수 금속별로.
  6. **Mo/KIO₃ 산화제–MRR은 Hill n≈4 협동형**(C₅₀≈0.044 M) — 판정#20 Langmuir(n=1) 이식하면 SSE 52배 악화.
  7. **Co/Ru 실측 ΔE_corr는 전수 탐색 후 부재**(Lv1-1 빈칸 종결) — Cu/Ru·Cu/Co·Ru/TiN만 존재. 열역학 상한
     0.735 V는 공정 예측값 아님.

## 구현 요청 (소프트웨어 부문 — sim/ 은 이 에이전트가 건드리지 않는다)

### [P5] Ru 산화제항 — E° 스칼라 금지, "Pourbaix 목적영역" 게이트로 (Lv1-2 §3)
- **무엇을**: Ru 팩(신설 시)의 산화제 적합성을 산화제 E° 하나가 아니라, **Ru를 RuO₄/RuO₄⁻ 비고체역으로 미는
  산화제만 활성**으로 판정하는 이산 게이트(oxidizer∈{NaIO₄, NaClO}=활성, 그 외=저연마)로 넣을 것. 추가로 **pH ≳ 9
  알칼리 제약**(RuO₄ 휘발 회피)을 필수 필드로.
- **근거노트**: `film-ru-mo-cmp-oxidizer-chemistry-ruo4-galvanic.md` §3. **검증문헌값**(노트 §3.2 verify 블록):
  NaIO₄ ~1290 vs K₂S₂O₈ ~40 Å/min(E° 단조 반증), 정점 E°≈1.6 V. **회귀 테스트**: E° 최대 산화제에 최대 MRR을
  배정하는 구현은 여기서 자동 실패해야 한다.
- **우선순위**: 중간(Ru 팩 신설 시점). 단 산화제–농도 스윕 1차 데이터가 없어 Ru의 연속 농도곡선은 미확보.

### [P6] Mo 팩 — W 팩 원형 + Hill 산화제항(n 자유) + pH 스위치 (Lv1-2 §4·§6)
- **무엇을**: Mo 팩을 W 팩([[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]) 원형으로 하되,
  산화제–MRR을 판정#20의 Langmuir(n=1)가 아니라 **Hill θ=(KC)ⁿ/(1+(KC)ⁿ), n 자유파라미터**로 둘 것.
  MoO₄²⁻ 용해의 pH 의존(산성 부동태/알칼리 용해)을 산화제항과 결합.
- **근거·검증문헌값**(노트 §6 verify): Hill n≈4.2(SSE 1.5) vs Langmuir n=1(SSE 79) → **52배 차**, C₅₀≈0.044 M,
  RR_max≈54 nm/min, 0.05/0.03 M 비 1.58. Mo Ecorr/icorr(§4.2 Table): pH2·0.1M RR90.2/SER2.2(41배).
  **회귀 테스트**: Langmuir(n=1) 단독 구현은 Mo/KIO₃ 5점에서 SSE가 Hill 대비 10배 이상 나빠야(정상).
- **우선순위**: 중간. n의 정확값(4.2)은 5점 적합이라 미검증 — status=modeled, confidence=estimated로.

### [P7] 갈바닉 커플 방향·연마 부호를 금속별 부호표로 (Lv1-2 §5)
- **무엇을**: 갈바닉 입력에 커플별 **양극 지정**(Co/Cu→Co, Ru/Cu→Cu, Mo/Cu→Mo)과 **연마 축소계수 부호**를
  금속별로 둘 것. [P2](Lv1-1)의 "hold→polish 축소계수"를 금속 무관 상수로 두면 Mo에서 부호가 틀린다.
- **근거·검증문헌값**(노트 §5.1·5.3): Ru/Cu ΔE_corr 540→20 mV, i_g KIO₄ 8.48>H₂O₂ 4.16 µA/cm²([Che17] 직접측정);
  Mo/Cu ΔE_corr hold116→polish270 mV(+133%, Co/Cu −72%와 반대).
- **우선순위**: 높음(갈바닉 결함 예측의 부호 오류 방지). [P1](Lv1-1)의 i_g 폐형식과 짝.

> 근거노트는 전부 `knowledge/materials/film-co-interconnect-cmp-corrosion-galvanic-inhibitor.md`.

### [P1] 갈바닉 전류밀도 항 — ΔE_corr 스칼라를 4입력 폐형식으로 교체
- **무엇을**: 갈바닉 부식 지표를 `ΔE_corr` 하나가 아니라 아래 폐형식으로 계산하는 함수를 Tier2에 추가.
  ```
  i_g(A) = exp(ΔE_corr/β_ca) · [i_corr(C)·S_c/S_a]^(β_c/β_ca) · [i_corr(A)]^(β_a/β_ca)
  β_ca = β_c(C) + β_a(A),  ΔE_corr = E_corr(C) − E_corr(A)
  ```
- **근거**: Gamagedara & Roy 2025, *Electrochem* 6(2) 15, DOI 10.3390/electrochem6020015 식 (12)–(15).
- **검증문헌값**(노트 §4.2–4.3 verify 블록에 이미 assert로 박혀 있음):
  ΔE_corr(hold) = 0.507 / 0.401 / 0.349 / 0.044 V (슬러리 I~IV),
  i_g(hold, F) = 55.1 / 62.2 / 21.1 / 6.60 µA·cm⁻²,
  **필수 회귀 테스트**: 구현한 함수가 슬러리 II에서 "ΔE_corr 감소 + i_g 증가"를 재현해야 한다
  (ΔE_corr만 쓰는 구현은 여기서 부호가 틀리므로 자동 검출된다).
- **우선순위**: **높음**. 현재 코드에 갈바닉 항 자체가 없고, 있더라도 ΔE_corr 단독이면 착화제 레시피에서 틀린다.
- **주의**: β_c, β_a 실측값은 [R25]에 표로 없다. 우리가 역산한 **lumped β_ca = 0.165 V는 유효값**이므로
  파라미터 팩에 `status: modeled, confidence: literature`로 넣고 실측 Tafel 표를 확보하면 교체한다.

### [P2] 정지/연마 조건 구분 플래그 — 문헌 ΔE_corr에 축소계수를 강제
- **무엇을**: 갈바닉 입력에 `measured_under: hold | polish` 필드를 두고, `hold`면 축소계수를 곱해 쓰게 한다.
- **근거·검증문헌값**: 같은 논문 Table 2. 슬러리 I에서 정지 0.507 V → 연마중 0.142 V(**−72%, 3.57배**).
  슬러리 II 0.401 → 0.047(−88%), III 0.349 → 0.105(−70%), IV 0.044 → 0.042(−5%).
  축소율이 슬러리마다 다르므로 **고정계수 하나로 넣지 말 것** — 첨가제가 적을수록 축소가 크다.
- **우선순위**: 중간. [P1]과 같이 들어가야 의미가 있다.

### [P3] Co 파라미터 팩의 χ 항 — `inhibitor_conc` 없이는 정의되지 않게 만들 것
- **무엇을**: Co 팩(신설 시)의 χ 드라이버에 억제제 농도를 **필수 필드**로 두고, Langmuir θ를 계산하되
  그 θ를 **SER(화학)에만 강하게, MRR(기계)에는 약하게** 거는 이중 경로로 분리.
- **근거**: Cheng 2025, *Appl. Surf. Sci.* 682, 161684, DOI 10.1016/j.apsusc.2024.161684.
- **검증문헌값**: pH 8, 3 wt% SiO₂ + 0.5 wt% H₂O₂ + 0.15 wt% 글리신 기준,
  K_ads(5CBTA/BTA/TTA) = 474 / 476 / 622 M⁻¹, ΔG°_ads = −25.21 / −25.23 / −25.89 kJ·mol⁻¹,
  η(3/6/9 mM, TTA) = 68.18 / 87.62 / 91.71 %, I_corr 334.25 → 27.70 µA·cm⁻²,
  **9 mM TTA에서 MRR 132.64 nm/min · SER 0.79 nm/min**(= 이중 경로 분리의 앵커).
- **우선순위**: 중간(Co 팩 신설 시점에 맞춰). 단 `exp(−k·θ)` 단일 경로로 구현하면 판정 #17·#24와 같은
  구조적 반증을 Co에서도 반복하게 된다 — **반드시 이중 경로로 설계할 것**.

### [P4] 억제효율의 측정법 출처를 파라미터에 남길 것 (PDP vs EIS)
- **무엇을**: 억제 관련 파라미터에 `measured_by: PDP | EIS` 메타필드 추가, 두 출처의 값을 섞지 못하게 검증.
- **근거·검증문헌값**: 같은 논문·같은 조건(9 mM TTA)에서 EIS R_p는 33.80 → 1114.01 Ω·cm²(**33.0배**)인데
  PDP I_corr은 334.25 → 27.70 µA·cm⁻²(**12.1배**) — Stern–Geary B 불변 가정이 **2.7배** 어긋난다.
- **우선순위**: 낮음(데이터 위생). 그러나 문헌 수집이 늘수록 섞일 위험이 커진다.
