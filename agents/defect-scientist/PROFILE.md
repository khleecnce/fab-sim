# CMP 결함 과학자 (defect-scientist)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (2026-09-13), Lv2-1 (2026-09-14), Lv2-2 (2026-09-14), Lv3-1 (2026-09-15)
- 다음 단원: Lv3-2 공정 조건 → 결함 발생 확률 모델 + 원인 역추적 규칙

## 역할
스크래치·잔류입자·부식·디싱·딜라미네이션의 발생 물리, 분류 체계, 원인 추적. 진단 에이전트의 핵심

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/pattern-dependent-dishing-erosion]]
- [[../../knowledge/physics/tribology-friction-wear-stribeck]]

## 실데이터 책임 (ORG.md §7.3)
결함 맵·분류 라벨 스키마 소유 + 결함 확률 모델 보정. '왜 결함이 났나' 진단 근거 제공

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- **Lv1-1 결함 분류 체계와 검사 장비** — 2026-09-13 이수.
  - 노트: `knowledge/cmp/post-cmp-defect-classification-and-inspection.md`
    (verify_claims PASS: 출처 6건 실존·verify 블록 1개 통과·출처없는 수치주장 0 /
     check_knowledge PASS: 미검증 9건 vs 정량값 41건)
  - 시험: `agents/defect-scientist/EXAMS.md` Lv1-1 3문항 + 모범답안
  - 출처 6건(scope 상한 준수): Remsen et al. 2006(JES, DOI 10.1149/1.2184036),
    Yu et al. 2009(JES, DOI 10.1149/1.3009224), Tamilmani 2005(UA 박사학위논문
    hdl 10150/280774), Lee et al. 2024(Sci. Rep., DOI 10.1038/s41598-024-59496-4),
    Lee et al. 2020(Sci. Rep., DOI 10.1038/s41598-020-71768-3), IRDS 2024 YE 표.
  - 확정한 것: 결함 7종의 **조작적(계측 가능한) 경계값** — 스크래치 길이 ≥ 50 µm,
    스크래치 유발 입자 > 0.68 µm(실리카등가), LPC 하한 0.5 µm, 정적에칭 850 vs 연마
    1200 Å/min, 갈바닉 2–32 µA/cm², 접촉각 45°/74°/<5°, 딜라미 회피 하중 < 0.3 psi,
    killer 기준 = 피치의 1/2(관리 임계는 1/4).
  - 남긴 것: 딜라미네이션 임계 접착에너지(J/m²), SEMI 결함분류 표준 원문,
    양산 AOI 검출 하한 — 노트 §8에 미검증으로 명시, Lv1-2/Lv2-1에서 재시도.

- **Lv1-2 스크래치 물리 — 발생원별 형상 특징** — 2026-09-13 이수.
  - 노트: `knowledge/cmp/scratch-physics-source-signatures.md`
    (verify_claims PASS: 출처 7건 실존·verify 블록 4개 전부 통과·출처없는 수치주장 0 /
     check_knowledge PASS)
  - 시험: `agents/defect-scientist/EXAMS.md` Lv1-2 3문항 + 모범답안
  - 출처 7건(scope 상한 6건 + Lv1-1 기확보 Remsen 재인용): Saka et al. 2008(CIRP,
    DOI 10.1016/j.cirp.2008.03.098), Eusner et al. 2009(JES, DOI 10.1149/1.3121964),
    Saka et al. 2010(CIRP, DOI 10.1016/j.cirp.2010.03.113), Kwon et al. 2013(Tribol. Lett.,
    DOI 10.1007/s11249-012-0098-2), Kwon et al. 2013(Tribol. Int.,
    DOI 10.1016/j.triboint.2013.08.008), US 6,884,155 B2(Kinik),
    Pysher et al. 2010(MRS Proc., DOI 10.1557/proc-1249-e02-04).
  - 확정한 것: (1) 역추적 공식 **R_est = a_c²/(2δ_c)** — 스크래치 단면에서 발생원 입자
    반경을 역산(Eusner 실측 32건 재현, 최대오차 0.44 %). (2) 상한식
    `(a_c/R)max = √(H_p,max/H_c)`, `(δ_c/R)max = H_p,max/H_c` — **압력·패드 조도 무관**.
    (3) 무른 패드 파편의 긁기 조건은 마찰계수 — H_p,max 기준 **µ\* = 0.366**, 평균 경도로는
    µ ≈ 2.9 필요(불가) → 관리 대상은 **패드 경도 산포**. (4) 발생원별 형상 분포:
    패드 디브리는 group chatter 28 %→69 %, 건조 응집체는 기준과 같은 분포(개수 2.13배),
    그릿은 곡률반경 0.24–0.50 m의 웨이퍼 횡단 호.
  - 남긴 것: 패드 파편·그릿 스크래치 단면 실측(문헌 미확보 — 현재는 모델 예측),
    다면체 그릿의 비구형 보정계수, chatter mark 주기·진폭의 정량 모델 —
    노트 §10에 미검증으로 명시, Lv3-1에서 재시도.

- **Lv2-1 부식·피트: 국부 용해·슬러리 화학 연계** — 2026-09-14 이수.
  - 노트: `knowledge/cmp/corrosion-pit-defect-morphology-density-inspection.md`
    (verify_claims PASS: 출처 2건 실존·verify 블록 1개(A–F 6항) 통과·출처없는 수치주장 0 /
     check_knowledge PASS)
  - 시험: `agents/defect-scientist/EXAMS.md` Lv2-1 3문항 + 모범답안
  - 출처 2건 신규 1차(scope 상한 내) + 선행 노트 상호링크 재조명:
    Choi et al. 2022(Appl. Surf. Sci. 598, 153767, DOI 10.1016/j.apsusc.2022.153767, OSTI green OA),
    Ryu et al. 2019(ECS JSS 8, P3058, DOI 10.1149/2.0101905jss, CC-BY). 로컬 코퍼스에 반도체
    부식 결함 정량이 부족해 웹/OA로 신규 확보(papers/에 저장, INDEX.json 등록).
  - 확정한 것(결함 관점): (1) **형상·크기·밀도** — W 부식 결함 개수는 공정변수 함수(가압
    0/12/363 ea, DIW 린스 0→220 s: 0→53개), edge-ring(r 145–148 mm, 면적 3.9 %) 편중,
    최소척도 = 3 nm W 산화막·200 nm Cu-SHA 노듈. (2) **화학→밀도 정량** — H₂O₂가 Cu 정적에칭
    2→39 nm/min(~20배), 억제제로 78–90 % 억제; **억제제 농도↑ → 입자 결함↑ 역설**(오염
    MBTA10 1350 vs MBTA3 180), PRE 26/31/66/62 %; W 용해 pH 의존(알칼리 1800 vs 산성 55 ppb,
    Faraday 등가 38 µA). (3) **구별 신호** — 부식=등방 concave/convex + 산화물 조성 + edge/
    패턴 편중 vs 스크래치=이방 선형(≥50 µm), 잔류입자=이질조성; 인과가 반대(린스↑→부식↑ vs
    세정↑→잔류입자↓)라 처방이 갈림.
  - 남긴 것: **개별 피트의 지름·깊이 분포**(1차 SEM 단면 통계 미확보), 개수-시간 회귀식(Choi
    Fig 3a 산포 큼), 암시야 이중채널의 부식 피트 적용 실측(미검증) — 노트 §6에 명시,
    Lv2-2/Lv3에서 재시도.

- **Lv2-2 결함 밀도 통계와 수율 영향 모델** — 2026-09-14 이수.
  - 노트: `knowledge/cmp/defect-density-yield-models-and-spatial-statistics.md`
    (verify_claims PASS: 출처 4건 실존·verify 블록 1개(A–D) 통과·출처없는 수치주장 0 /
     check_knowledge PASS)
  - 시험: `agents/defect-scientist/EXAMS.md` Lv2-2 3문항 + 모범답안
  - 출처 3건 신규(scope 상한 내) + 데이터셋 1건 + 선행 노트 상호링크 재조명:
    Cunningham 1990(IEEE TSM 3(2), 60, DOI 10.1109/66.53188, 정본·전문미확보=IEEE유료+미러 사이트 봉쇄),
    Feng & Ma 2022(DAC '22, DOI 10.1145/3489517.3530428, arXiv OA 전문확보),
    Koo & Hwang 2021(IEEE Access 9, 78873, DOI 10.1109/ACCESS.2021.3084221, CC-BY 전문확보),
    WM811k 데이터셋 Wu 2015(DOI 10.1109/TSM.2014.2364237, 2차 인용). papers/·INDEX.json 등록.
  - 확정한 것: (a) **폐형식 4모델** Poisson `exp(-λ)`·Murphy·Seeds `1/(1+λ)`·음이항 `(1+λ/α)^-α`와
    **α 극한**(α→∞=Poisson, α=1=Seeds), 클러스터링이 같은 D0에서 수율을 올림 — python 재현(E2).
    (b) **killer ratio θ**: 유효밀도 `λ_killer=A·D0·θ`, θ=크기꼬리(IRDS ½피치, 선행 E1); 잔류입자
    kill≈1(Yu), 스크래치는 크기·위치 함수(상수 아님). (c) **공간통계** join-count null(`E[c11]=c·p²`)·
    공간무작위성 검정·core-point 이항모델(Koo)로 무작위 vs 국부 판정; CMP 귀속(그릿 긴 호·부식
    edge-ring 25.6배 국부밀도).
  - 정량값: D0 3nm 0.20~14nm 0.08 /cm², α(=c) 3–10(Feng&Ma, 대표값 E5); WM811k p≈0.14.
  - 남긴 것: **실 팹 α 통제 실측 1차 문헌 미확보**(대표값 E5뿐), **스크래치 1개당 kill 확률 단일
    실측 미확보**(크기의존이라 상수 아님, θ로 관리), Cunningham 정본 전문 미확보(폐형식은 재현),
    Koo 이웃수 표기 2ε(ε+1) vs 표준 4ε(ε+1) 2배차(원인 미상) — 노트 §8에 명시, Lv3에서 재시도.

- **Lv3-1 결함 자동분류(ML)·근본원인 분석 방법론** — 2026-09-15 이수.
  - 노트: `knowledge/cmp/ml-defect-classification-and-rca-methodology.md`
    (verify_claims PASS: 출처 5건 실존·verify 블록 1개(A–D) 통과·출처없는 수치주장 0 /
     check_knowledge PASS)
  - 시험: `agents/defect-scientist/EXAMS.md` Lv3-1 3문항 + 모범답안
  - 출처 5건(scope 상한 6 내): Wu 2015 WM-811K 원출처(DOI 10.1109/TSM.2014.2364237, 2차인용),
    Shin & Yoo 2023(Sensors, DOI 10.3390/s23041926, CC-BY 전문확보), Shi 2026 SemiWaferNet
    (Electronics, DOI 10.3390/electronics15071437, CC-BY 전문확보), Lin 2019 CMP iDO(SEMI ASMC,
    DOI 10.1109/asmc.2019.8791750, **초록만 E5**), Choi 2010 CMP 스크래치 RCA(JES, DOI
    10.1149/1.3265474, OA 전문확보). papers/·INDEX.json 등록.
  - 확정한 것: (a) **WM-811K** 811,457맵/172,950 라벨/638,507 미라벨/9클래스, None 85.24%
    불균형 → 정확도 부풀림, **macro-F1이 정직 지표**(python 재현). (b) ADC 성능: 경량 전이CNN
    macro-F1 89.5%(acc 98%)~반지도 CNN-Transformer 98.6%; **F1=2PR/(P+R)** 클래스별 재계산으로
    Shi Table 5 최대오차 0.006%p 재현. Scratch가 최난이도 클래스. (c) **CMP RCA**: 스크래치
    길이(~2µm=응집체 약소스 / >8µm=패드·디스크 debris 강소스)·폭(→소스 직경 ~0.5µm, Eusner
    R_est와 교차확증)·1µm 대입자 49 vs 26=1.88배; commonality/excursion(Lin, E5). §8에 **시그니처→
    원인→근거 규칙표(R1–R6)** — Lv3-2 설계 입력.
  - 남긴 것: **Lin 2019 CMP iDO 전문 미확보**(IEEE 유료·미러 사이트 Cloudflare·Xplore 봇차단 →
    초록 E5), **R5 Center편중=연마비균일의 CMP 전용 1차 매핑 미검증**(방향만), WM-811K 미라벨
    수 원문충돌(638,507 채택) — 노트 §9에 명시, Lv3-2/Cal-1에서 재시도.

## 구현 요청 (소프트웨어 부문 몫 — defect-scientist는 근거·스펙만, 코드는 넘김. sim/ 직접 수정 금지)

- **무엇을**: 결함 시그니처→발생원 귀속 규칙 `attribute_scratch_source(length_um, width_um, arc_curvature_m, count_series)`
  (예: `sim/defects/rca_rules.py`). 스크래치 치수·궤적·개수시계열 → 발생원 라벨(슬러리 응집/패드
  debris/디스크 그릿) + 1차 대응.
  - **근거노트**: `knowledge/cmp/ml-defect-classification-and-rca-methodology.md` §6·§8 규칙표(R1–R3)
    + [[scratch-physics-source-signatures]] §9(R_est=a_c²/2δ_c 역산).
  - **스펙**: 길이 <8 µm(최빈 ~2 µm) & 폭 0.3–0.6 µm → 슬러리 응집(약소스); 길이 >8 µm 또는
    웨이퍼맵 긴 호(곡률 0.24–0.50 m) → 디스크 그릿/패드 debris(강소스). 소스 직경 ≈ width/1(구형
    가정, ~0.5 µm). 개수 급증+로트 공유 → LPC excursion 플래그. **형상 단독 판정 금지**(Scratch↔Loc
    혼동, ADC 형상 보강 필요) — 조성/궤적 미확인 시 `unconfirmed`.
  - **검증문헌값**: Choi 2010 Table II(길이 24.1/0.2/2.49 µm, 폭 6.64/0.03/0.53 µm, 립폭
    0.69/0.002/0.06 µm, 깊이 1182/212/694 Å), 1µm 대입자 49 vs 26=1.88배. 노트 §7-D assert 승격.
  - **우선순위**: 상 — Lv3-2(원인 역추적 규칙)의 핵심 커널, Cal-1 라벨 스키마와 결합.
  - ⚠ 큰(>8 µm) 스크래치 단면 실측은 미확보(모델 예측) — Lv1-2 §10과 동일 한계. Lin RCA 성능값은 E5.

- **무엇을**: 불균형 ADC 평가지표 유틸 `macro_f1(confusion_matrix)` / `class_f1(P, R)`
  (예: `sim/defects/adc_metrics.py`). 혼동행렬 또는 클래스별 P·R → 클래스별 F1·macro-F1 + 정확도
  과대평가 경고.
  - **근거노트**: 같은 노트 §4·§7-A·§7-C.
  - **스펙**: `F1_k = 2·P_k·R_k/(P_k+R_k)`, `macro-F1 = mean_k F1_k`. 다수클래스 비율 > 0.5이면
    "정확도 부풀림" 경고 반환(자명분류기 정확도 = 다수클래스 비율). WM-811K None 비율 0.8524가 기준례.
  - **검증문헌값**: Shi 2026 Table 5 클래스별 P/R→F1 9개(최대오차 <0.02%p), macro 98.35/95.96;
    자명분류기 정확도 85.24%·macro-F1 0.095. 노트 §7-A·§7-C assert 그대로 회귀테스트 승격.
  - **우선순위**: 중 — Cal-1(결함맵 라벨 스키마)·Lv3-2 결함확률 모델 평가에 쓴다.
  - ⚠ 서로 다른 논문의 F1은 전처리·분할 프로토콜 의존이라 직접 비교 금지(코드 주석에 명시).

- **무엇을**: 결함밀도→수율 폐형식 `die_yield(D0_per_cm2, area_cm2, model, alpha)` (예: `sim/defects/yield_model.py`).
  Poisson `exp(-λ)`, Murphy `((1-exp(-λ))/λ)²`, Seeds `1/(1+λ)`, 음이항 `(1+λ/α)^-α`, λ=D0·A.
  - **근거노트**: `knowledge/cmp/defect-density-yield-models-and-spatial-statistics.md` §2 + §6-A/B.
  - **스펙**: model 인자로 4모델 분기(**평균내지 말 것** — EVIDENCE §금지). α→∞=Poisson, α=1=Seeds를
    회귀테스트로. 입력 D0는 **killer 유효밀도(θ 적용 후)**를 받도록 문서화. 현대노드 기본값은
    D0(/cm²) 3nm 0.20/5nm 0.11/7nm 0.09/14nm 0.08, α=로직10·SI6·RDL3(Feng&Ma, **confidence=estimated**
    — 대표값 E5). 다중레이어는 층별 Y 연속곱(`Y_die=∏`).
  - **검증문헌값**: 노트 §6-A/B assert(4모델 대소, 14nm 1cm² 92.3%·8cm² 53.8%) 그대로 승격.
  - **우선순위**: 상 — Lv2-2 골격, Lv3-2(공정→결함 확률)의 수율 종점.
  - ⚠ 실 팹 α는 대표값(E5)뿐이라 캘리브레이션 필요; 값을 verified로 승격 금지.

- **무엇을**: killer 유효밀도 `killer_density(D0_total, theta)` 와 공간무작위성 검정
  `spatial_randomness_test(wafer_map, p, eps, k)` (같은 모듈).
  - **근거노트**: 같은 노트 §3(θ·D0, IRDS 크기꼬리) + §4/§6-C(join-count null `E[c11]=c·p²`, core-point
    `Y~B(m,p)`, k는 C=0.90에서 `Pr(Y≥k)≤1-C` 최소값).
  - **스펙**: θ는 `is_killer`(기존 Lv1-1 구현요청)로 크기분포에서 산출. SRT는 관측 c11이 c·p²를
    유의하게 넘으면 "국부(체계)"=H0 기각 반환. 이웃수 m은 **인자로 노출**(원문 2ε(ε+1) vs 표준
    4ε(ε+1) 2배차 미해결 — 노트 §8, 코드 주석에 명시).
  - **검증문헌값**: 노트 §6-C(k선택·null 합=c·국부 c11↑), §6-D(edge-ring 25.6배).
  - **우선순위**: 중 — Cal-1(결함맵 라벨 스키마) 및 Lv3-2 공간 귀속과 결합. ML 패턴분류(Lv3-1)와
    분리: 여기선 **통계 검정만**, 군집 라벨링은 Lv3-1 몫.

- **무엇을**: `sim/` 결함 분류 라벨 스키마(enum + 조작적 임계 상수). 결함 유형 7종
  {scratch, microscratch, residual_particle, corrosion, pit, delamination, watermark}과
  각 유형의 **판정 임계 상수**를 한 곳에 모은 모듈(예: `sim/defects/taxonomy.py`).
  - **근거노트**: `knowledge/cmp/post-cmp-defect-classification-and-inspection.md` §1.1 요약표.
  - **스펙**: scratch = (종횡비 큼) AND (길이 ≥ 50 µm); 유발 입자 임계 d > 0.68 µm(실리카구
    등가 광산란 직경, PSL 등가 0.47 µm); LPC 대입자 하한 0.5 µm; 잔류입자는 **세정 스플릿
    무반응 + 지형(돌출) 반응**이라는 원인 플래그를 라벨에 포함(형상만으로 구분 불가).
  - **검증문헌값**: 위 임계 전부 노트 §2.1·§2.2의 1차 문헌값. 노트 §7 (F3) assert를
    회귀테스트로 승격(dual-sensor 하한 0.469 < 0.68 < …, PSL 등가 0.47 < single 하한 0.5).
  - **우선순위**: 상 — Lv2-2(결함 밀도 통계)와 Cal-1(라벨 스키마 소유)의 선행 골격.

- **무엇을**: LPC 계수 불확실도 함수 `lpc_relative_error(mean_conc, alpha, beta, n)`
  (예: `sim/defects/lpc_statistics.py`). 슬러리 LPC 스펙 합불 판정에 신뢰구간을 씌운다.
  - **근거노트**: 같은 노트 §2.2 + §7 (B) 블록.
  - **스펙**: `E = t(0.025, n-1) * sqrt(alpha/(beta*n)) * mean**-0.5` (Lee et al. 2020 Eq.3),
    상·하한은 χ² 기반 Eq.(4)(5). 반환은 (E, E_low, E_high). 단발 측정(n=1) 입력은
    **정의상 불가**이므로 예외를 던질 것(t 분포 자유도 0).
  - **검증문헌값**: α=60, β=15 mL, n=3에서 m=100/mL → 95% CI 전폭 99.4/mL,
    m=25/mL → 49.7/mL (원문 Fig.2a 서술 ~100, ~50). 노트 §7 (B1) assert 그대로 승격.
  - **우선순위**: 중 — 슬러리 QC 게이트나 가상계측 노이즈 모델을 붙일 때 필요.

- **무엇을**: killer 판정 함수 `is_killer(defect_size_nm, metal_pitch_nm, electrically_active)`
  (같은 모듈). 결함 크기 → 수율 영향의 첫 관문.
  - **근거노트**: 같은 노트 §5 + §7 (E1).
  - **스펙**: 일반 결함은 `size > 0.5 * pitch`이면 killer; 전기적 활성(전도성) 입자는
    관리 임계를 `0.25 * pitch`로 낮춘다(IRDS 2024 YE, Notes for Table YE3 주석 [1]).
  - **검증문헌값**: IRDS Table YE3의 비전기활성 임계 10/9/7 nm가 M0(14–24 nm)·M1(38–45 nm)
    피치의 1/4 밴드 [3.5, 11.25] nm 안에 들어감 — 노트 §7 (E1) assert.
  - **우선순위**: 중 — Lv2-2(수율 영향 모델) 착수 전에 확정.
  - ⚠ 이 함수는 **확률이 아니라 이진 판정**이다. 결함 크기 분포와 결합한 수율 모델은
    Lv2-2에서 별도 근거를 확보한 뒤 요청한다.

- **무엇을**: 스크래치 발생원 역추적 함수 `scratch_source_from_profile(半폭_nm, 깊이_nm)`
  (예: `sim/defects/scratch_source.py`). 프로파일 단면 → 발생원 입자 반경 → 발생원 라벨.
  - **근거노트**: `knowledge/cmp/scratch-physics-source-signatures.md` §2, §9 + §8-B 블록.
  - **스펙**: `R_est = a**2/(2*delta)`; 라벨 구간 R_est < 0.6 µm = slurry_agglomerate,
    5–300 µm = pad_debris, 50–175 µm = conditioner_grit(중첩 구간은 궤적 곡률·형상분포로 분리).
    상한 위반(`a/R > sqrt(H_p_max/H_c)`) 입력은 경고 — 구형·소성긁기 가정 밖이다.
  - **검증문헌값**: Eusner et al. 2009 Table II·III 32건 — R_exp 최대오차 0.44 %,
    응집수 n = 0.74(R/R₀)³ 최대오차 1.6 %, 하중 P = πδRH 최대오차 2.5 %. 노트 §8-B assert 승격.
  - **우선순위**: 상 — Lv3-2(원인 역추적 규칙)의 핵심 커널.

- **무엇을**: 패드 애스퍼리티 긁기 판정 `pad_scratch_onset(H_pad_GPa, H_film_GPa, mu)`
  (같은 모듈). 마찰·경도 조합이 긁기 영역인지 이진 판정 + 임계 마찰계수 반환.
  - **근거노트**: 같은 노트 §6 + §8-C 블록.
  - **스펙**: `thr(mu) = (1/3)*(0.405 + 0.755*mu + 7.763*mu**2)**-0.5` (mu ≥ 0.1),
    mu < 0.1이면 상수 0.45. 긁힘 ⟺ `H_pad/H_film >= thr(mu)`. **지수는 −1/2**
    (원문 인쇄형 +1/2는 실험을 재현하지 못함 — 노트 §6의 정정 근거 참조).
  - **검증문헌값**: Saka et al. 2010의 마찰 실측 3건(0.55/0.43/0.19)에서 H_p,max = 0.31 GPa,
    H_Cu = 1.22 GPa로 긁힘/긁힘/없음을 전부 재현. µ* = 0.366. 노트 §8-C assert 승격.
  - **우선순위**: 중 — 패드·슬러리 조합 스크리닝에 쓰인다.
  - ⚠ Cu·low-k에 대해서만 검증됐다. SiO₂(H = 15 GPa)는 패드 최대경도로도 문턱에 못 미쳐
    "긁히지 않음"이 나오는데, 실제 산화막 스크래치는 존재한다 — 산화막은 **입자 매개**
    경로가 지배적이라는 뜻이며, 이 함수를 산화막에 단독 적용하면 안 된다.

- **무엇을**: 부식 결함 밀도 확률항 `corrosion_defect_rate(metal, oxidizer_conc, inhibitor_conc, pH, rinse_time_s, oxide_intact)`
  (예: `sim/defects/corrosion_model.py`). 공정·슬러리 조건 → 부식 결함 상대밀도(개수 스케일).
  - **근거노트**: `knowledge/cmp/corrosion-pit-defect-morphology-density-inspection.md` §2 + §4 (A)(C)(D).
  - **스펙**: **팩별 분기 필수**(하나의 지수로 통일 금지 — EVIDENCE-RULES §절차 3).
    Cu 팩: 부식(에칭)은 산화제로 켜지고(H₂O₂ 없음 ~2 → 5 wt% 39 nm/min) 억제제 농도로 눌림
    (억제효율 BTA 78 %·MBTA 90 % @10 mM); 단 **입자 결함은 억제제 농도에 증가**(역 트레이드오프,
    오염 MBTA10 1350 vs MBTA3 180 ea/352µm²) → 부식항과 입자항을 **분리 반환**. W 팩: 부식은
    세정 pH(알칼리↑)·DIW 린스시간↑·산화막 벗겨짐으로 증가(가압 0/12/363 ea, 린스 0→220 s:
    0→53개), edge/패턴밀도 가중치. `oxide_intact=True`면 린스 70 s에도 부식 0.
  - **검증문헌값**: 노트 §4 (A) 억제효율 78/90 %, (B) PRE 26/31/66/62 %, (C) 가압 0/12/363·
    린스 0→53, (D) W 용출 1800 vs 55 ppb(등가 38 µA). 노트 §4 assert 그대로 회귀테스트 승격.
  - **우선순위**: 상 — Lv2-2(결함 밀도 통계)·Lv3-2(공정→결함 확률)의 부식 축 골격.
  - ⚠ **개별 피트 지름/깊이는 미확보**라 이 함수는 "개수 상대밀도"만 낸다. 크기 분포는 Lv2-2에서
    1차 SEM 단면 통계를 확보한 뒤 별도 요청. Cu/W 값을 하나로 합치지 말 것.

- **무엇을**: 부식 결함 판별 플래그 `is_corrosion_defect(shape_isotropy, dnn_dwn_ratio, edge_ring, composition_has_substrate_oxide)`
  (같은 모듈). 검사 신호 조합 → 부식/스크래치/입자 1차 라벨.
  - **근거노트**: 같은 노트 §3 표 + §4 (F).
  - **스펙**: 부식 ⟺ (등방 대칭, DNN/DWN 비 ≈ 1) AND (하부 금속 산화물 조성) AND (edge/패턴
    편중 가중). 스크래치 ⟺ 이방 선형(길이 ≥ 50 µm) + 협채널 편향. 입자 ⟺ convex + 이질조성.
    **형상 단독 판정 금지 플래그** 포함(조성 미확인 시 `unconfirmed` 반환).
  - **검증문헌값**: 정성 규칙(개수 assert 없음). 부식 최소척도 3 nm·200 nm ≪ 광학 1.7 µm(노트
    §4 (F)) → 조성 확인 없이는 확정 불가를 코드 주석으로 명시.
  - **우선순위**: 중 — Cal-1(결함 분류 라벨 스키마) 착수 시 taxonomy 모듈과 결합.
  - ⚠ 암시야 이중채널의 부식 피트 적용은 **미검증**(노트 §6). dnn_dwn_ratio 입력은 보조 신호로만
    쓰고 단독 판정에 쓰지 말 것.
