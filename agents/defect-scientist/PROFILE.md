# CMP 결함 과학자 (defect-scientist)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (2026-09-13)
- 다음 단원: Lv2-1 부식·피트: 갈바닉·국부 용해, 슬러리 화학 연계

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

## 구현 요청 (소프트웨어 부문 몫 — defect-scientist는 근거·스펙만, 코드는 넘김. sim/ 직접 수정 금지)

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
