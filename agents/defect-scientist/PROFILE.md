# CMP 결함 과학자 (defect-scientist)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-13)
- 다음 단원: Lv1-2 스크래치 물리(대입자·패드 파편·디스크 그릿 탈락)

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
