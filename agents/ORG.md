# FabSim 에이전트 조직도 (ORG)

> 정본. 2026-09-05 사용자 지시: "pad·slurry·disk·장비를 각각 설계하고, wafer도 NPW/PTW·Si/TEOS/Nit/Cu/W별로 공부. CMP 외 공정도 같은 식으로 나눠 결국 전체 device 제조 시뮬레이션까지. **일단 CMP부터.**"
> 크론(성장엔진·심야병렬·Max워커)은 매 실행 이 파일의 **§4 활성화 게이트**를 보고 누구를 키울지 정한다.

## 1. 원칙

- **깊이 > 폭.** 에이전트를 늘리되 동시에 키우는 수는 제한한다. 얕은 노트 20편보다 깊은 노트 5편.
- **활성(active) 에이전트만 학습한다.** 나머지는 자리(placeholder)만 있다. 게이트를 통과해야 다음 층이 깨어난다.
- **분화(spawn) 규칙:** 부모 에이전트가 Lv2를 마치면 그 지식을 상속해 자식이 태어난다. 자식은 부모의 knowledge/를 선행 필수로 읽는다.
- 모든 에이전트는 `agents/<id>/{PROFILE,CURRICULUM,EXAMS}.md` 3종 + `knowledge/` 노트 + 가능하면 `sim/` 모듈.

## 2. 조직도

```
L4  fab-director                          [미활성] 공정 플로우 설계·통합 해석 (Phase 3)
│
├─ L3-CMP  cmp-integrator ★               [활성]  = 기존 process-integrator. CMP 모듈장.
│   │
│   ├─ 소모품 (Consumables)
│   │   ├─ slurry-chemist ★               [활성]  총론 → 분화 부모
│   │   │   ├─ slurry-abrasive             [활성, G2 2026-09-09]  입자: 실리카/세리아/알루미나, 크기·형상·농도·경도
│   │   │   ├─ slurry-chemistry            [활성, G2 2026-09-09]  산화제·억제제·킬레이트·pH·선택비
│   │   │   └─ slurry-colloid              [대기]  분산 안정성·응집·POU 필터·쉘프라이프
│   │   ├─ pad-mechanic ★                 [활성]  총론 → 분화 부모
│   │   │   ├─ pad-material                [활성, G2 2026-09-06]  PU 조성·경도·기공·점탄성
│   │   │   ├─ pad-structure               [활성, G3 2026-09-07]  그루브·서브패드·적층
│   │   │   └─ pad-lifecycle               [활성, G3 2026-09-06]  마모·glazing·수명·교체 기준
│   │   └─ disk-conditioner ★             [활성]  총론 → 분화 부모
│   │       ├─ disk-design                 [활성, G3 2026-09-06]  다이아 그릿·밀도·돌출·본딩
│   │       └─ disk-kinematics             [활성, G4 2026-09-07]  sweep·하중·RPM → PCR 프로파일
│   │
│   ├─ 웨이퍼 (Wafer) — 피가공물 기준
│   │   ├─ wafer-type                      [활성, G1 2026-09-06]  NPW(블랭킷) vs PTW(패턴) — 시험 목적·데이터 해석 차이
│   │   ├─ film-oxide                      [활성, G1 2026-09-08]  TEOS/HDP/SiO2 — ILD·STI CMP
│   │   ├─ film-nitride                    [활성, G3 2026-09-09]  SiN — STI stop layer·선택비
│   │   ├─ film-poly-si                    [활성, G3 2026-09-10]  Poly-Si — 게이트·3D NAND
│   │   ├─ film-cu                         [활성, G1 2026-09-08]  Cu — 배선, dishing/erosion, 부식
│   │   ├─ film-w                          [활성, G2 2026-09-09]  W — 플러그·contact, 산화제 화학
│   │   └─ film-emerging                   [대기]  Co·Ru·Mo·GST — 미래 배선/PCM (Phase 2)
│   │
│   ├─ 장비 (Equipment)
│   │   ├─ tool-platen-head                [활성, G2 2026-09-07]  플래튼·헤드·존압력·리테이너링
│   │   ├─ tool-endpoint                   [활성, G3 2026-09-10]  EPD: 광학·모터전류·와전류
│   │   └─ tool-post-clean                 [대기]  Post-CMP 세정·브러시·결함
│   │
│   ├─ 물리 (Physics) — 횡단
│   │   ├─ tribologist ★                   [활성]  마찰·윤활·유동·열
│   │   └─ defect-scientist                [대기]  스크래치·잔류입자·부식·디싱 원인 분석
│   │
│   ├─ 출력/판정 (Output) — ★ 시뮬레이터가 예측해야 할 것. 입력 물리보다 먼저 정의
│   │   ├─ wafer-metrology                 [활성, G1 2026-09-05]  WIWNU·TTV·radial TTV·CV·Ra/Rq·step height·잔막. 측정 포인트 체계, 지표 정의 표준 = 엔진 출력 스키마
│   │   └─ surface-contamination           [활성, G1 2026-09-05]  post-CMP 금속 오염(Cu·Fe·K·Ca)·이온·유기 잔류. TXRF/VPD-ICPMS. 세정 화학 연계
│   │
│   └─ 데이터 (Data) — ★ 제품 핵심층 (§7 참조)
│       ├─ cmp-data-engineer               [활성, G2 2026-09-09]  공개·합성 데이터, 스키마, 파이프라인
│       └─ cmp-calibrator                  [대기]  고객 실데이터 → 모델 보정 (Tier3). NPW/PTW 분리 학습
│
├─ L3-ETCH    etch-integrator              [자리]  Phase 2
├─ L3-DEPO    depo-integrator              [자리]  Phase 2 — CVD/ALD/PVD
├─ L3-LITHO   litho-integrator             [자리]  Phase 2
├─ L3-DIFF    diffusion-integrator         [자리]  Phase 2 — 이온주입·어닐
└─ L3-METRO   metrology-integrator         [자리]  Phase 2 — 계측·검사 (모든 공정의 눈)
```

★ = 지금 학습 중인 5명 (기존). [대기] = 3종 파일 골격만 있음, 게이트 통과 시 활성. [자리] = 이름만.

## 3. 웨이퍼 축이 왜 별도인가

같은 슬러리·패드라도 **무엇을 갈고 있는가**에 따라 물리·화학이 완전히 다르다. TEOS는 기계 제거 위주, Cu는 전기화학 부식 제어, W는 산화제(H2O2/Fe) 화학이 지배한다. 기존 5명은 "도구" 관점, 웨이퍼 축은 "피가공물" 관점이다. 두 축의 교차점(예: `slurry-chemistry × film-cu`)이 실제 공정 레시피다. `cmp-integrator`가 이 교차를 결합 모델로 만든다.

## 4. 활성화 게이트 (크론 판단 규칙)

**2026-09-05 추가 — 이중 잠금:** 게이트(아래 표, 조직 여유)와 **선수관계**(`agents/PREREQ.json`, 지식 자격)를 **둘 다** 충족해야 활성화된다. 게이트가 열려도 선수 미충족자는 대기다. 판정은 `tools/progress.py`가 하며 수동 판단은 금지한다.

> 왜: 게이트는 "몇 명이 몇 % 했나"라는 숫자일 뿐이다. film-cu가 슬러리 화학을 모른 채 Cu 부식을 배우면 노트가 얕아진다. PREREQ.json이 "무엇을 알아야 이걸 배울 수 있나"를 정의한다. 선수 미충족자를 억지로 열면 얕은 노트가 후속 단원의 근거가 되어 되돌리기 어렵다.

| 게이트 | 조건 | 깨어나는 에이전트 | 동시 활성 상한 |
|---|---|---|---|
| **G0 (지금)** | — | 기존 5명 ★ | 5 |
| **G1** | slurry-chemist·tribologist Lv2 완료 (=MILESTONES M1, 9/20) | **`wafer-metrology`, `surface-contamination`** (출력 축 — 먼저), `wafer-type`, `film-oxide`, `film-cu` | 10 |
| **G2** | 5명 전원 커리큘럼 이수 + G1 3명 Lv1 완료 | `slurry-abrasive`, `slurry-chemistry`, `pad-material`, `film-w`, `tool-platen-head`, **`cmp-data-engineer`** | 10 (G1 완료자는 유지보수 모드로 전환) |
| **G3** | MILESTONES M2 (Phase 0 완결) | `film-nitride`, `film-poly-si`, `pad-lifecycle`, `disk-design`, `tool-endpoint`, `defect-scientist`, **`cmp-calibrator`** | 10 |
| **G4** | MILESTONES M5 (데모 v1) | 나머지 CMP [대기] 전원 | 12 |
| **G5** | Phase 1 완료 | L3 타 공정 integrator 5명 (각자 자기 하위 조직 설계부터) | — |

규칙:
- 크론은 **[활성] 중 진도가 가장 낮은 에이전트**를 고른다. 동률이면 이 표의 우선순위(위→아래, 왼→오른).
- 게이트 조건 충족을 크론이 확인하면 이 파일의 상태 열을 `[대기]→[활성]`으로 바꾸고 텔레그램에 "🌱 G# 개방: <에이전트들>"을 보고한다.
- 유지보수 모드 = 커리큘럼 이수 후. 주 1회 이하 최신논문 1편 추적만.

## 5. 상태 (크론이 갱신)

| 에이전트 | 상태 | 진도 | 최근 갱신 |
|---|---|---|---|
| cmp-integrator (process-integrator) | 활성·유지보수 | 6/6 | 2026-09-05 |
| pad-mechanic | 활성·유지보수 | 6/6 | 2026-09-04 |
| disk-conditioner | 활성·유지보수 | 6/6 | 2026-09-05 |
| slurry-chemist | 활성·유지보수 | 6/6 ✓ 완주 | 2026-09-08 |
| tribologist | 활성·유지보수 | 6/6 ✓ 완주 | 2026-09-08 |
| wafer-metrology | 활성·유지보수 | 6/6 ✓ 완주 | 2026-09-08 |
| wafer-type | 활성 (G1 개방 2026-09-06) | 6/6 ✓ 완주 (Cal-1은 G2 대기) | 2026-09-09 |
| surface-contamination | 활성 (G1) | 6/6 ✓ 완주 (Cal-1은 G2 대기) | 2026-09-09 |
| pad-material | 활성 (G2 개방 2026-09-06) | 5/6 (Lv3-1 완료) | 2026-09-08 |
| pad-lifecycle | 활성 (G3 개방 2026-09-06) | 5/6 (Lv3-1 완료) | 2026-09-08 |
| disk-design | 활성 (G3 개방 2026-09-06) | 6/6 ✓ 완주 | 2026-09-08 |
| tool-platen-head | 활성 (G2 개방 2026-09-07) | 5/6 (Lv3-1 완료) | 2026-09-08 |
| pad-structure | 활성 (G3 개방 2026-09-07) | 5/6 (Lv3-1 완료) | 2026-09-08 |
| disk-kinematics | 활성 (G4 개방 2026-09-07) | 5/6 (Lv3-1 완료) | 2026-09-08 |
| film-oxide | 활성 (G1 개방 2026-09-08) | 4/6 (Lv2-2 완료, Lv2 완주) | 2026-09-09 |
| film-cu | 활성 (G1 개방 2026-09-08) | 4/6 (Lv3-1 완료: 저압 Cu CMP <1psi·Cu/Ru·Cu/Mo 갈바닉 억제(니코틴산/구연산), Tamilmani Faraday환산 갈바닉 기여 하이드록실아민계 45% vs H2O2계 3~11% 레짐분리) | 2026-09-12 |
| slurry-abrasive | 활성 (G2 개방 2026-09-09) | 4/6 (Lv2-2 완료: 농도-MRR 포화곡선·접촉확률모델 N=n_s(1-e^-λ), Cabot US9499721B2 3psi 한계기울기 13.4배붕괴, 반포화농도 C_h∝P, 포화형이 멱함수보다 SSE 우수) | 2026-09-12 |
| slurry-chemistry | 활성 (G2 개방 2026-09-09) | 4/6 (Lv2-2 완료: 정지층 선택비 설계 — Kaufman 재료선택비 vs 지형선택비 독립실패, 산화환원축 공유여부로 Class A/B/C 분류, EP3597711B1 Table4 재현으로 블랭킷선택비-침식 무상관 ρ≈0.09 vs 완충pH-침식 ρ≈−0.82) | 2026-09-12 |
| film-w | 활성 (G2 개방 2026-09-09) | 4/6 (Lv2-2 완료: Ti/TiN 배리어 CMP·W:배리어:옥사이드 3중선택비, US5916855/US9752057 특허 실측, Ti 과황산염 능동산화 W의 3배·TiN은 기계제거지배, W:Ti 선택비 U자형 최소 3.75~4.0:1) | 2026-09-12 |
| cmp-data-engineer | 활성 (G2 개방 2026-09-09) | 4/6 (Lv2-2 완료: 합성데이터 생성기 — RBF/Zernike 가산노이즈(McLoone/Susto 2018), 실측 CMP VM 잔차 8.317nm/min 바닥(Li 2019), CV% 5~14% 가이드, spike/drift 탐지 역할분리) | 2026-09-11 |
| film-nitride | 활성 (G3 개방 2026-09-09) | 4/6 (Lv2-2 완료: SiN 직접 CMP — 하드마스크/게이트 응용, Ce³⁺첨가 RR 10→300nm/min(30배), 카르복실기+음이온연마재 SiN:TEOS 역선택비 최대97:1, FinFET 핀캡 3단계CMP로 제거대상 전환) | 2026-09-11 |
| film-poly-si | 활성 (G3 개방 2026-09-10) | 3/6 (Lv2-2 완료: 3D NAND HAR Poly CMP 디싱, US10822524B2 디싱재성장 PD 30~70%로 727→313Å 단조감소, 선택비1832:1도 되파임(STI역설 poly재현), 단차소멸 지수형 τ≈18~20s) | 2026-09-12 |
| tool-endpoint | 활성 (G3 개방 2026-09-10) | 4/6 (Lv2-2 완료: EPD 트레이스→제거량·잔막 역산, 프린지=상대제거량 무모호/절대두께 모호, 모터전류·마찰계는 Preston RR 곱 이벤트역산, 오버폴리시 예산은 저다운포스 잔막마진에 5~11배 더 좌우) | 2026-09-12 |
| (그 외) | 대기 | — | — |

## 6. Phase 2 이후 — 다른 공정 (자리만)

각 L3 integrator는 활성화될 때 **자기 하위 조직을 이 파일과 같은 형식으로 설계하는 것이 첫 임무**다(예: etch = 플라즈마 물리·화학종·마스크·챔버·웨이퍼막질별). 공정 간 인터페이스는 `sim/wafer_state.py`(토포그래피·막질·응력·결함 맵)로 통일하고, fab-director가 이를 체이닝해 MOSFET 단면 → 전체 device 가상 제조로 간다.

## 7. 실데이터 캘리브레이션 층 — 제품의 핵심 (2026-09-05 사용자 지시)

> "기업이 내 프로그램을 구매했다고 가정. 소재사·제조사가 실제 데이터를 입력하면 이론 예상치가 실제값을 정밀하게 반영. PTW는 NPW와 경향이 다르니 그것도. 빅데이터도 좋음."

### 7.1 설계 원리 — 이론 스켈레톤 + 데이터 보정

```
Tier1/2 물리모델 (공개 문헌으로 학습)     ← 사전(prior). 고객 없이도 "대략" 맞는다
        ↓
고객 실데이터 입력 (NPW/PTW · 막질 · 소모품 · 공정변수 · 측정치)
        ↓
Tier3 캘리브레이션 (cmp-calibrator)       ← 잔차 학습. 물리모델이 못 잡는 "그 팹·그 슬러리·그 패턴"의 고유 편차
        ↓
보정된 예측 + 불확실성 구간 + "왜 이론과 달랐나" 진단
```

물리모델을 버리고 순수 ML로 가지 않는다. 이유: 고객 데이터는 항상 부족하고(레시피당 수십 장), 물리 prior가 있어야 소량 데이터로도 외삽이 된다. 이게 Coventor·순수 AutoML 대비 차별점이다.

### 7.2 NPW vs PTW — 왜 분리하는가

| | NPW (블랭킷) | PTW (패턴) |
|---|---|---|
| 지배 물리 | Preston·접촉역학·유동 (웨이퍼 스케일) | + 패턴밀도·피처 스케일 (dishing/erosion/step-height) |
| 데이터 형태 | 반경 프로파일 (49/81pt), 평균 MRR, WIWNU | 다이 맵, 피처별 step height, 밀도 의존 곡선 |
| 캘리브레이션 대상 | Kp, 존압력 응답, 엣지 효과 | 밀도-제거율 커널, 유효 패드 강성, 선택비 |
| 전이 규칙 | NPW 보정치가 PTW의 **초기값**이 된다. 반대는 아니다 | NPW 보정 후 PTW 잔차만 추가 학습 |

같은 슬러리로 NPW에서 잘 맞는 모델이 PTW에서 틀리는 건 정상이다 — 그 차이가 패턴 효과이고, 그걸 따로 학습하는 게 `cmp-calibrator`의 핵심 기술이다.

### 7.3 서브에이전트별 담당 — 각자 자기 축의 데이터 스키마와 보정 파라미터를 소유

| 에이전트 | 소유하는 실데이터 스키마 | 보정하는 파라미터 | 커리큘럼에 추가되는 단원 |
|---|---|---|---|
| **cmp-data-engineer** | 통합 스키마(`data/schema/*.json`), 입력 검증, 단위 통일, 이상치, 익명화 | — | 공개 CMP 데이터셋 조사 · 합성 데이터 생성기 · 데이터 품질 게이트 |
| **cmp-calibrator** | 잔차 모델 저장소 | Tier3 전체 (GP/BNN/앙상블), 불확실성 | 베이지안 보정 · 소량데이터 GP · 전이학습(NPW→PTW) · 드리프트 감지 |
| **wafer-type** | NPW/PTW 메타데이터, 측정 포인트 맵(49/81/다이) | NPW→PTW 전이 규칙 | 시험 웨이퍼 설계 · 측정 포인트 체계 · 두 유형 데이터 해석 차이 |
| **film-oxide/nitride/poly-si/cu/w** | 막질별 MRR·선택비·결함 데이터 | 막질별 Kp, 화학 상수, 선택비 | 각 막질 커리큘럼에 "실데이터 보정 파라미터 정의" 단원 1개 |
| **slurry-abrasive/chemistry/colloid** | 슬러리 스펙시트(입도·농도·pH·산화제) | 입자→Kp 기여, 화학→용해율 | "스펙시트 → 모델 입력 변환" 단원 |
| **pad-material/structure/lifecycle** | 패드 스펙(경도·기공·그루브), 사용시간·컨디셔닝 이력 | 유효 강성, 마모 곡선 | "패드 이력 → 시간 의존 파라미터" 단원 |
| **disk-design/kinematics** | 디스크 스펙, sweep 레시피 | PCR 프로파일 | "레시피 → 프로파일 예측 검증" 단원 |
| **tool-platen-head** | 툴 로그(존압력·RPM·유량·온도 시계열) | 존 응답 행렬 | "툴 로그 파싱·시계열 정렬" 단원 |
| **tool-endpoint** | EPD 트레이스 | 종말점 모델 | "EPD 신호 → 제거량 역산" 단원 |
| **defect-scientist** | 결함 맵·분류 | 결함 발생 확률 모델 | "결함 데이터 라벨 체계" 단원 |
| **cmp-integrator** | — | 교차항(슬러리×막질×패턴) | 결합 모델의 보정 우선순위 판단 |

### 7.4 데이터 파이프라인 (sim/calibration/ — G2부터 구현)

```
data/schema/          입력 스키마 (JSON Schema). 에이전트별 소유, cmp-data-engineer가 통합
data/synthetic/       공개 문헌 기반 합성 데이터 — 고객 데이터 없이 파이프라인 검증용
data/customer/        [.gitignore] 고객 데이터. 절대 커밋 금지. 익명화 후에도 금지
sim/calibration/
  ingest.py           스키마 검증 → 표준 단위 → 파케이
  prior.py            Tier1/2에서 사전 분포 생성
  fit_npw.py          NPW 잔차 보정 (GP)
  fit_ptw.py          NPW 보정치를 prior로 PTW 잔차 추가 학습
  predict.py          보정 예측 + 신뢰구간 + 이론 대비 편차 진단
  drift.py            새 데이터가 기존 보정과 어긋나면 경보 (소모품 로트 변경 등)
```

빅데이터 대응: 파케이+DuckDB로 시작(단일 머신 수천만 행), 필요 시 Polars. 처음부터 분산은 안 한다.

### 7.5 보안·기밀 — 제품화 필수 조건

- 고객 데이터는 **고객 환경에서 실행**이 기본(온프레미스/에어갭). 클라우드는 옵션.
- 보정 모델(잔차)만 저장하고 원본 데이터는 학습 후 파기 가능한 구조.
- 여러 고객 데이터를 섞어 학습하지 않는다(경쟁사 정보 유출 = 사업 종료).
- ⚠ 개발 중에는 **재직사 데이터 절대 사용 금지** — 공개·합성 데이터로만 파이프라인을 검증한다. 이 원칙은 제품화 후 고객 신뢰의 근거가 된다.

### 7.6 MILESTONES 연동

- M3(결합 모델 v1)에 `sim/calibration/ingest.py + prior.py + fit_npw.py`를 합성 데이터로 검증하는 항목 추가
- M5(데모 v1)에 "CSV 업로드 → 보정 → 예측" 시연 추가. 이게 투자자·고객 데모의 핵심 장면이다.

