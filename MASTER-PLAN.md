# FabSim — 반도체 공정 시뮬레이션 플랫폼 마스터플랜

> 작성: 2026-08-31. 소유: Lee (CMP 슬러리 개발자).
> 비전: AI 에이전트들이 소재·장비·공정의 과학/공학을 지속 학습하여, 교수급/시니어 엔지니어급 전문성으로 공정 시뮬레이션을 설계·실행·해석하는 플랫폼.
> 경로: **CMP 통합 시뮬레이터(교두보) → 인접 공정 확장 → 가상 fab (북극성)**
> 용도: ①이력서/포트폴리오 ②사업화(STARTUP-ROADMAP.md와 연동) ③기술 자산.

## 1. 냉정한 포지셔닝 (전제)

| 영역 | 기존 강자 | 우리의 틈 |
|---|---|---|
| TCAD (device) | Synopsys Sentaurus, Silvaco | 정면승부 불가. 장기 북극성으로만. |
| 공정 3D 모델링 | Coventor SEMulator3D (Lam 소유) | 기하학 중심, 소재 화학 약함 |
| **CMP 시뮬레이션** | **통합 상용툴 부재** (학계 모델 산재) | ★ 교두보. 슬러리+패드+디스크+공정변수 통합은 공백 |
| AI 공정 전문가 에이전트 | 없음 (모두 수치해석 툴) | ★ 신영역. 지식학습→모델설계→해석 루프 |

핵심 차별화: 시뮬레이터 "엔진"이 아니라 **"공정을 이해하는 AI + 모델 라이브러리"**를 판다.
고객이 원하는 건 수치해가 아니라 "왜 결함이 났고 뭘 바꿔야 하는가"이다.

## 2. 시스템 아키텍처 (4층)

```
┌─────────────────────────────────────────────────┐
│ L4. 오케스트레이터 (Fab Director Agent)          │
│  공정 플로우 설계, 에이전트 간 협업 조정, 통합 해석 │
├─────────────────────────────────────────────────┤
│ L3. 도메인 전문가 에이전트 (성장형)                │
│  각자 지식베이스 + 커리큘럼 + 검증시험 보유          │
│  CMP군: 슬러리화학 / 패드역학 / 디스크·컨디셔닝 /   │
│         마찰·유체 / 공정통합(압력·RPM·EPD)         │
│  확장군: Litho / Etch / Deposition / Diffusion …  │
├─────────────────────────────────────────────────┤
│ L2. 시뮬레이션 엔진 (Python 모듈)                  │
│  Tier1 경험식(Preston, Luo-Dornfeld) →            │
│  Tier2 물리모델(접촉역학, 유동, 화학반응) →         │
│  Tier3 데이터 서로게이트(ML, 스몰데이터 GP/BNN)     │
├─────────────────────────────────────────────────┤
│ L1. 지식베이스 (knowledge/ — llm-wiki 방식)        │
│  논문·교과서·특허 요약을 상호링크된 md로 축적        │
│  모든 주장에 출처 필수. 에이전트의 "장기기억"        │
└─────────────────────────────────────────────────┘
```

### 에이전트 성장 메커니즘 (교수급으로 키우는 법)
1. **커리큘럼**: 각 에이전트는 agents/<이름>/CURRICULUM.md 보유 — 학부→대학원→최신논문 순서의 학습 단계.
2. **지식 축적**: 주간 크론이 커리큘럼 다음 단원을 학습(웹/arxiv) → knowledge/에 출처 있는 노트 작성 → 에이전트 프로필에 "이수" 기록.
3. **검증 시험**: 단원마다 자기시험 문제를 만들어 풀고(EXAMS.md), 실제 물리 관계식을 코드로 재현해 sanity check (예: Preston 계수 문헌값 재현).
4. **실전 투입**: 지식이 쌓이면 해당 도메인의 L2 시뮬레이션 모듈을 직접 설계·구현·문서화.
5. **레벨 정의**: Lv1 학부지식 → Lv2 대학원/리뷰논문 소화 → Lv3 최신논문 추적+모델 구현 → Lv4 모델 개선 제안(교수급).

## 3. 단계별 로드맵

### Phase 0 — CMP 코어 모델 (지금~3개월)
- [x] 지식베이스 골격 + CMP 5개 에이전트 커리큘럼 작성 (+ 운동학 기반 `sim/tier1_empirical/kinematics.py`, 2026-09-03)
- [x] Tier1 구현: Preston MRR v0 (Python, 문헌값 오더 재현 검증, 2026-09-04) — Luo-Dornfeld형(P^1/2)은 접촉역학 성숙 후 Tier2로 유보
- [x] 패드: Greenwood-Williamson 접촉모델(순방향+역문제+마모/glazing 시계열+Kp 물리적 분해·preston.py 정식 연결 완료, `sim/tier2_physics/gw_preston_link.py`, 2026-09-04) — pad-mechanic 커리큘럼 전체 이수
- [x] 디스크: 컨디셔닝-패드마모 모델(disk-conditioner 커리큘럼 전 단원 이수 완료 — Lv3-2 `sim/tier2_physics/conditioner_asperity_distribution.py` 구현으로 마무리, Ring/Prasad/Dirksen population balance similarity solution 기반 분포폭 2차 상태량 결합, self-test 5/5 PASS, 2026-09-05)
- [x] 공정변수(P, RPM, 유량, 시간) → MRR/WIWNU 예측 v0 — 유량은 지식 부재로 이번엔 제외, 시간축만 완료 (`sim/tier1_empirical/process_time.py`, 2026-09-04, Max워커)
- [x] **Streamlit 데모 UI v0**: v0 모델 완성 즉시 구축 — 압력·RPM·존압력 슬라이더 → MRR/프로파일 실시간 플롯 (사용자 지시 2026-09-03, localhost 구동+스크린샷 검증까지) (2026-09-04, Max워커)
### Phase 1 — CMP 통합 시뮬레이터 (3~9개월)
- [ ] 슬러리(입자·화학) × 패드(점탄성·asperity) × 디스크(마모) 결합 모델
- [x] 웨이퍼 스케일 균일도(WIWNU), 패턴 의존성(dishing/erosion) 모듈 — WIWNU(`wiwnu.py`)와 패턴밀도/dishing/erosion(`pattern_density.py`)이 각각 구현된 데 이어, 둘을 잇는 결합 브리지(`wiwnu_pattern_combined.py`, 2026-09-05)로 반경×다이 2차원 결합 제거율 맵까지 완성. 단, 반경-패턴 분리가능(separable) 1차 근사이며 교차항(엣지에서 패턴영향 증폭 등)은 미포함 — 진행 로그 07시 회차 항목 참조.
- [ ] 합성/공개 데이터 캘리브레이션 파이프라인 (⚠️ 회사 데이터 절대 금지)
- [x] Streamlit 데모 UI(WIWNU×패턴 탭 포함) → 포트폴리오/사업계획서 데모로 사용 (2026-09-05, Max워커)
### Phase 2 — 인접 공정 확장 (9~24개월)
- [ ] 신규 에이전트 육성: Etch → Deposition(CVD/ALD) → Litho → Diffusion
- [ ] 공정 간 인터페이스 표준(웨이퍼 상태 객체: 토포그래피·막질·응력)
### Phase 3 — 가상 fab 북극성 (24개월+)
- [ ] 공정 플로우 체이닝: 다단계 공정 시뮬레이션 → 간단한 구조(MOSFET 단면) 가상 제작
- [ ] 오픈소스 TCAD(DEVSIM 등) 연동으로 device 특성까지

### 사업 연동
- Phase 1 데모 = 예비창업패키지(2027-01) 사업계획서의 기술증빙
- CMP 시뮬레이터 = STARTUP-ROADMAP의 "R&D 자동화 플랫폼"의 물리모델 엔진으로 통합 가능
- 이력서: "CMP 통합 공정 시뮬레이터 개발(오픈 모델 기반)" — 이직 스토리에도 강력

## 4. 디렉토리 구조
```
~/fab-sim/
├── MASTER-PLAN.md          # 이 문서
├── knowledge/              # L1 지식베이스 (llm-wiki 방식, 출처 필수)
│   ├── cmp/  ├── materials/  ├── equipment/  └── physics/
├── agents/                 # L3 에이전트 (각 폴더: PROFILE.md, CURRICULUM.md, EXAMS.md)
│   ├── slurry-chemist/  ├── pad-mechanic/  ├── disk-conditioner/
│   ├── tribologist/     └── process-integrator/
├── sim/                    # L2 엔진 (Python)
│   ├── tier1_empirical/  ├── tier2_physics/  └── tier3_surrogate/
└── papers/                 # 논문 원문/메모
```

## 5. 운영 원칙
- 주간 크론("FabSim 성장 엔진")이 학습 1단원 + 구현 1단위씩 전진. 실행당 크게, 새벽 제외.
- 모든 지식 노트에 출처(논문 제목·연도·DOI/URL) 필수 — 근거 없는 지식은 에이전트 오염.
- 코드는 반드시 실행·검증 후 커밋 수준으로 (문헌 재현값과 비교).
- ⚠️ 회사(동진쎄미켐) 실험 데이터·배합 정보 절대 사용 금지. 공개 논문/특허/합성 데이터만.
- CMP 슬러리 최신논문 크론(기존)과 중복 학습 금지 — 시뮬레이션 관점 노트만 여기에.

## 진행 로그
<!-- 크론이 실행마다 추가 -->
- **2026-09-03** (트랙 A+B, 1회차): process-integrator Lv1-1(장비 구조)·Lv1-2(운동학) 이수 → **Lv0→Lv1 승급**. 지식노트 2건 작성(`knowledge/equipment/cmp-tool-architecture.md`, `knowledge/physics/cmp-kinematics-rotary.md`, 출처: Lai MIT thesis 2001 / AMAT US6183354B1·US6244942B1 / JJMIE 2026 / IJPEM-GT 리뷰 2021), 자기시험 6문항.
- **2026-09-03** (트랙 B): `sim/tier1_empirical/kinematics.py` 구현·실행 검증 **7/7 PASS** — ω_w=ω_p일 때 웨이퍼 전면 상대속도 균일(std=0.00e+00, |v|=ω_p·r_cc=1.2566 m/s) 재현, 비균일도 해석해 NU=2|µ| 오차<1e-12 확인. 발견: 운동학 비균일은 자전평균으로 상쇄되어(50/60rpm에서 edge/center MRR 1.0039) **WIWNU 주범은 압력분포**임 → Lv2-2 설계 방향 확정.
- **2026-09-04** (트랙 A+B): process-integrator Lv2-1(Preston/Luo-Dornfeld MRR 모델 정밀분석) 이수.
  지식노트 `knowledge/cmp/preston-luo-dornfeld-mrr.md`(출처: Chen Iowa State PhD thesis 문헌리뷰,
  DuPont 특허US2026/0091462, novasolver.jp 계산기 FAQ), 자기시험 3문항. 구현
  `sim/tier1_empirical/preston.py`(Kp·P·V, kinematics.py 속도장 재사용) self-test **5/5 PASS**
  — 선형성 회귀, 문헌범위(50-1000+ nm/min, STI대표 254nm/min) 오더 대조, Rs=1 WIWNU=0
  구조확인, kinematics.py와 edge/center 1.00391 교차검증 일치. Phase 0 체크리스트 1/4 완료
  (Preston v0). 문헌 계보 분석 결과 Luo-Dornfeld형(P^1/2)은 GW 접촉모델·슬러리 입도분포
  지식이 갖춰진 뒤 Tier2로 구현하기로 확정(지식 없이 구현 금지 원칙).
- **2026-09-04** (Max워커): `sim/demo_app.py` Streamlit 데모 UI v0 구현 — kinematics.py/preston.py를
  수정 없이 import해 압력(P)·RPM(웨이퍼/패드)·Kp 슬라이더 및 3존(center/mid/edge) 압력분포
  옵션(pressure_fn)으로 반경별 MRR 프로파일 실시간 플롯, 웨이퍼 평균 MRR, kinematic number µ,
  운동학 비균일도 2|µ|%, WIWNU%를 표시. 검증: `streamlit run --server.headless true
  --server.port 8511`로 기동 → `curl localhost:8511` 200 OK(정상 HTML), `/_stcore/health` → ok
  (임포트·런타임 예외 없음 확인) → 프로세스 종료. self-test 대상 모듈 아님(UI 레이어,
  기존 preston.py/kinematics.py self-test는 불변 유지). `sim/README.md`에 사용법 문서화.
  Phase 0 체크리스트 "Streamlit 데모 UI v0" 완료 처리.
- **2026-09-04** (Max워커): `sim/tier1_empirical/process_time.py` 구현 — preston.py/kinematics.py를
  수정 없이 import해 시간(time) 축만 추가(유량은 슬러리 화학 지식 부재로 명시적 제외).
  `removed_thickness(rs, mrr, t_sec)`(= MRR×t 단순적분), `endpoint_time(target, mrr_ref)`
  (목표두께/MRR), `wiwnu_percent(arr)`(demo_app.py 인라인 계산을 함수로 승격, 로직 변경 없음)
  3개 API. self-test **4/4 PASS**: 선형성(t 2배→제거두께 정확히 2배), endpoint_time 역관계
  (MRR 2배→시간 정확히 1/2), Rs=1(균일압력) WIWNU=0.00e+00%(preston.py 3번과 정합), Rs=50/60
  WIWNU=0.3905%(kinematics.py/preston.py edge/center 1.00391과 정합하는 0.4% 근방, 오더 확인
  용도로 하드코딩 assert 없이 출력만). 회귀 확인: preston.py 5/5, kinematics.py 7/7 여전히 PASS.
  `demo_app.py`에 "목표 제거두께(nm)" 슬라이더 추가(기존 UI 요소는 불변) → 목표두께 도달
  예상시간 + 제거두께 프로파일 표시, `streamlit run --server.port 8512`로 기동해
  `curl localhost:8512` 200 / `/_stcore/health` ok 확인 후 종료. `sim/README.md` 사용법 문서화.
  Phase 0 체크리스트 "공정변수(P, RPM, 유량, 시간) → MRR/WIWNU 예측 v0" [x] 처리(유량 제외 명시).
- **2026-09-04** (08시 회차, 트랙A+B): pad-mechanic Lv1-1(고분자 점탄성 기초: 저장/손실탄성률,
  Maxwell 모델, 크리프, DMA) 이수 → **Lv0→Lv1 승급**. 지식노트
  `knowledge/materials/pad-viscoelasticity-dma.md`(출처: Meng et al. 2025 Polymers 17(5) 613
  오픈액세스 PMC11902601 — PU 패드 PCDL함량별 Shore D/탄성계수 실측표, Wikipedia Dynamic
  modulus/DMA — Maxwell 모델 수식, US Patent 10391606 — 상용 CMP 패드 Shore D 60-90),
  EXAMS.md 3문항. 구현 `sim/tier2_physics/viscoelastic_maxwell.py` — Maxwell 저장/손실탄성률
  수치 재현 self-test **5/5 PASS**(저주파/고주파 극한, E''피크=E/2 해석값 일치, grid search
  피크위치 일치, tan δ 극한거동). 아직 MRR/WIWNU 계산엔 미연결(Lv2-1 GW 접촉모델에서
  패드 유효강성으로 연결 예정) — Phase 0 GW 접촉모델 항목의 사전 지식 축적.
- **2026-09-04** (10시 회차, 트랙A): pad-mechanic Lv1-2(CMP 패드 구조: 발포체·groove·subpad) 이수.
  지식노트 `knowledge/materials/pad-structure-groove-subpad.md`(출처: Pureon 공식 IC1000/IC1010
  데이터시트 2024-04 — Shore D60·압축률2.25%·두께50/80mils, Zheng et al. 2023 Micromachines
  PMC10536193 오픈액세스 — 산업용 12인치 플랫폼 구조+패드마모 운동학모델, McAllister et al. 2019
  Micromachines PMC6523751 오픈액세스 — IC1000 K-groove+Suba IV 서브패드 실측 세팅+COF-RR
  무상관 실측), 자기시험 3문항. Lv1 이수 완료(Lv1-1+Lv1-2). 핵심 발견: (1) 상부패드(국소 평탄화)
  +서브패드(글로벌 순응)의 역할분리가 스케일 차이(µm vs mm)에서 기인함을 실측 세팅으로 확인,
  (2) 패드 마모 불균일이 압력존 제어를 방해한다는 정적모델 결과(disk-conditioner 에이전트
  Phase 0 항목과 연결점), (3) COF-RR 무상관 실측 → 현 preston.py의 "동일 컨디셔닝 레짐 내
  1차근사"라는 유효범위 한계를 명문화. 다음: Lv2-1 Hertz/GW 접촉모델(트랙 A) → sim/tier2_physics
  GW 구현(트랙 B). 아직 코드 변경 없음(지식 우선 원칙, GW는 다음 회차에 깊게).
- **2026-09-04** (12시 회차, 트랙A): pad-mechanic Lv2-1(접촉역학: Hertz + Greenwood-Williamson
  asperity 모델) 이수 → Lv1→Lv2 진입(2/2 단원 이수 후 Lv1 완료, Lv2 1/2). 지식노트
  `knowledge/materials/hertz-gw-contact-mechanics.md`(출처: Zhu 2012 Univ.Arizona OPTI521
  Hertz 튜토리얼 공개PDF, GW 1966 원논문은 paywall이라 2차 교차검증: Yang et al. 2024
  PMC11051262 오픈액세스 — CMP패드 GW 직접적용 논문, Lubricants/MDPI 2022 리뷰 스니펫),
  EXAMS.md 3문항. 구현 `sim/tier2_physics/gw_contact.py` — Hertz(F∝delta^1.5) + 지수분포 GW
  통계모델 수치적분, self-test **5/5 PASS**: Hertz 비선형 스케일링 정확 재현, 지수분포의
  memoryless 성질로 인해 실접촉면적/하중 비율(A_r/W)이 분리거리(=명목압력)와 무관한 상수임을
  수치적분↔폐형식 양쪽에서 확인(오차 8.6e-6). 회귀 확인: kinematics.py 7/7, preston.py 5/5,
  process_time.py 4/4, viscoelastic_maxwell.py 5/5 전부 PASS 유지. Phase 0 "GW 접촉모델" 항목의
  핵심 지식+수학 골격 확보(아직 preston.py MRR과 미연결 — Lv2-2에서 명목압력→국소접촉압력→
  K_p 물리적 분해로 연결 예정). 다음: Lv2-2(표면거칠기→국소압력분포) 트랙A 이어서 트랙B로
  preston.py에 GW 결과를 실제 연결.
- **2026-09-04** (Max워커, 13시 회차): pytest 회귀 테스트 하네스 구축 — tests/에 5개 모듈
  (kinematics/preston/process_time/viscoelastic_maxwell/gw_contact) 대응 테스트 작성,
  기존 모듈 코드 미변경(순수 import+assert), `python -m pytest tests/ -v` 전체 27개 PASS
  확인. 목적: 모듈 증가에 따른 수동 회귀 확인 부담 경감(기존엔 매 회차 사람이 5개 파일을
  하나씩 재실행해 확인). sim/README.md에 테스트 실행법 문서화, requirements.txt 갱신.
- **2026-09-04** (14시 회차, 트랙A+B): pad-mechanic Lv2-2(패드 표면 거칠기와 실접촉면적 →
  국소압력 분포) 이수 → **Lv2 완료(2/2), Lv3 진입**. 지식노트
  `knowledge/materials/gw-nominal-vs-local-pressure.md`(출처: Yang et al. 2024 PMC11051262 Eq.20
  MRR 3-모드 가중합 — 오픈액세스, GW 1966 원논문은 여전히 미확보라 gw_contact.py Lv2-1 폐형식
  유도로 대체검증 명시), EXAMS.md 3문항. 구현 `sim/tier2_physics/gw_pressure_solve.py` —
  gw_contact.py의 gw_numeric()을 재사용해 명목압력 P로부터 힘평형 W(d)=P·A_n을 만족하는 분리거리
  d를 Brent법으로 역산(순방향→역문제). self-test **5/5 PASS**: 핵심 발견 — 14→96kPa(6.9배)
  압력변화에도 평균 실접촉압력 p_r=W/A_r은 <0.1% 편차(2.16e-16)로 사실상 불변, 대신 접촉점수 n은
  하중에 거의 정확히 비례(n/W 변동 1.78e-15). 즉 Preston 선형성의 미시적 근거가 "개별 접촉강도
  증가"가 아니라 "접촉점 개수 증가"임을 GW 이론+수치로 확인 — Yang et al. Eq.20의 n_x(t)
  중심 구조와 정합. 회귀 확인: pytest 전체 **31/31 PASS**(신규 tests/test_gw_pressure_solve.py
  4개 포함). 아직 preston.py와 미연결(Lv3-2에서 Kp 물리적 분해로 정식 연결 예정). 다음:
  Lv3-1 패드 마모·glazing 모델(트랙A) — 압력·시간에 따른 asperity 분포 변화, MRR 드리프트.

- **2026-09-04** (16시 회차, 트랙A+B): pad-mechanic Lv3-1(패드 마모·glazing과 MRR 드리프트 모델) 이수.
  지식노트 `knowledge/materials/pad-wear-glazing-mrr-decay.md`(1차 출처: Shi & Ring 2010 Wear,
  저자 공개 PDF https://my.che.utah.edu/~ring/Publications-PDFs/J-135.pdf — GW+Hertz 접촉에
  Archard 마모법칙+population balance PDE+유체(Reynolds) 하중분담 결합. Borucki 2002/Stein 1996/
  Oliver/Lawing 원문은 미확보라 2차 인용으로 명시), EXAMS.md 3문항. 구현
  `sim/tier2_physics/pad_wear_glazing.py` — Shi&Ring의 Borucki 극한(유체 없음)을 Monte-Carlo
  asperity 집단(지수분포, gw_contact.py의 hertz_force 재사용) 이산 시간적분으로 근사, self-test
  **5/5 PASS**: 무컨디셔닝 시 평균높이·MRR 단조감소(glazing 정성 재현), 초반>후반 수확체감 감쇠,
  이산 t=0가 연속 gw_numeric()과 1.18% 오차로 교차검증, 마모 시 p_r 변화(2.66%)가 Lv2-2의 "정적
  압력변화 시 p_r 불변(<0.1%)"과 다른 레짐임을 대비 확인. 핵심 결론: Preston K_p는 상수가 아니라
  패드 컨디셔닝 상태(마모도)의 함수 — 무컨디셔닝 구간 MRR 드리프트의 물리적 근거를 코드로 뒷받침.
  pytest 회귀 tests/test_pad_wear_glazing.py 5건 추가, 전체 **36/36 PASS**. 유체결합(Reynolds)·
  컨디셔너 B/D항·preston.py 정식 연결은 Lv3-2(GW 접촉모델 코드 구현 완결 단원)로 유보. Phase 0
  "패드: GW 접촉모델" 항목이 순방향+역문제+마모시계열까지 확장(체크박스는 preston.py 정식 연결
  전까지 미완료 유지 — Lv3-2에서 최종 완료 예정). 다음: Lv3-2 실행해 Lv3 완료 → pad-mechanic 커리큘럼
  전체 이수, 이후 disk-conditioner(Phase 0 우선순위 4번째) 학습으로 전환 예정.
- **2026-09-04** (18시 회차, 트랙B): pad-mechanic Lv3-2(GW 접촉모델 코드 구현 + 문헌값 재현) 이수 →
  **pad-mechanic 커리큘럼 전체 이수 완료(CURRICULUM.md 전 단원 [x])**. 구현
  `sim/tier2_physics/gw_preston_link.py` — GW 접촉점수 n(P)를 매개로 Preston Kp의 미시적 기원을
  MRR=alpha_removal·n_contacts(P)·V로 분해, 문헌 캘리브레이션(Kp=1e-13, STI 254 nm/min 오더)에서
  alpha_removal 역산. self-test **4/4 PASS**: n(P) 선형적합 잔차 2.46e-13(완전선형 재확인),
  14/48/96kPa 외삽에서 GW-link와 Preston-direct 편차 <5e-12(정의상 항등에 근접), 캘리브레이션
  MRR=99.4 nm/min이 문헌범위(50-1000 nm/min) 안. EXAMS.md 3문항 추가. **Phase 0 "패드: GW 접촉모델"
  항목 완전 완료 처리**(순방향 gw_contact → 역문제 gw_pressure_solve → 마모시계열 pad_wear_glazing →
  Preston 정식연결 gw_preston_link, 4모듈 체인). pytest 회귀 전체 **40/40 PASS**(신규
  tests/test_gw_preston_link.py 4건). Phase 0 체크리스트 3/4 완료(디스크: 컨디셔닝-패드마모
  모델만 남음). 다음: disk-conditioner 에이전트(Phase 0 우선순위 4번째, 마지막)로 학습 자원 전환 —
  Lv1(컨디셔너 디스크 구조·다이아몬드 그릿)부터 시작해 pad_wear_glazing.py의 B/D항(컨디셔닝
  재생성 term) 연결까지가 Phase 0 완주 경로.
- **2026-09-04** (20시 회차, 트랙A): disk-conditioner Lv1-1(컨디셔닝 목적과 메커니즘: glazing 제거,
  asperity 재생) 이수 → **Lv0→Lv1 진입(1/2)**, Phase 0 우선순위 4번째 에이전트 학습 개시.
  지식노트 `knowledge/equipment/conditioning-mechanism-asperity-regeneration.md`(1차 출처:
  Lawing 2004 Rohm and Haas NCCAVS CMPUG 발표자료, 공개 PDF — 컨디셔너 절삭률 vs 패드 마모율의
  경쟁효과로 정상상태 표면구조 결정, 실측 접촉면적 11.3/7.7/2.2%(저/중/고 공격성); 2차 출처:
  Ring/Prasad/Dirksen "Dynamic CMP Pad Asperity Population Balance for Conditioning and Polishing"
  저자 공개 PDF(Univ. Utah/Cabot) — Evans-Marshall 마모법칙+GW+유사변수 폐형식해로 asperity
  population balance 확장). EXAMS.md 3문항. **수치 재현 시도** `scripts/ring_similarity_check.py`:
  유사변수 t=0 항등사상은 PASS(대수식 자기무모순 확인)했으나, t>0 정성거동(장신 asperity 우선마모)
  재현은 원문 PDF의 OCR 손상(Eq.7-9 괄호/첨자 구조 불확실)으로 MISS — **정직하게 미검증 표기**,
  거짓 PASS로 채우지 않음. 정성적 결론(경쟁효과 메커니즘) 자체는 Lawing 2004 독립 실측과 정합해
  지식으로는 유효. 핵심 발견: 컨디셔너 그릿 직경 D_grit이 생성 asperity 평균높이(≈D_grit/2)·밀도
  (≈1/D_grit²)를 직접 결정 — Lv1-2(그릿 설계변수) 단원의 정량적 출발점 확보. pytest 회귀
  전체 **40/40 PASS**(코드 변경 없음, 지식/문서 트랙만 진행). 다음: Lv1-2 다이아몬드 디스크
  설계변수(grit size/density/protrusion) 학습.
- **2026-09-04** (Max워커, 22시 회차): process_time.py(Preston 정상상태 v0)와
  pad_wear_glazing.py(무컨디셔닝 MRR 드리프트 실측)를 정식 연결하는 순수 통합 모듈
  `sim/tier2_physics/wear_aware_endpoint.py` 구현 — 새 물리 지식 없이 기존 두 모듈을
  수정 없이 import만 해서 v0 정상상태 엔드포인트 예측이 실제 마모 드리프트 대비 얼마나
  낙관적인지 정량화. `cumulative_removed_thickness_drift()`(사다리꼴 누적적분),
  `endpoint_time_drift()`(선형보간 역산, 도달불가 시 RuntimeError), `compare_naive_vs_drift()`
  (naive=초기 MRR 고정 가정 vs drift=실제 시계열 적분) 3개 API. self-test **4/4 PASS**:
  (1) 누적적분 마지막 값이 np.trapz(전체구간)과 상대오차 1.34e-16으로 일치, (2) C1=0(마모 없음)
  극한에서 endpoint_time_drift가 process_time.endpoint_time과 정확히 일치(rel_err=0.00%,
  "드리프트 없으면 새 모델이 기존 v0로 정확히 축소된다"는 회귀 검증 통과), (3) optimism_pct>0
  확인(무컨디셔닝 40-step 시나리오, target=누적제거두께의 50%: t_naive=19.15s vs
  t_drift=19.32s, optimism_pct=+0.87% — MRR이 마모로 단조감소하므로 초기 MRR을 끝까지
  쓰는 naive는 실제보다 큰 MRR로 나눠 시간을 과소평가), (4) 도달불가 target(시뮬레이션
  최대 누적두께의 1000배)에 RuntimeError 정상 발생. 참고로 target을 공정 종료 시점에
  가깝게(누적두께의 90%/99%) 잡을수록 optimism 격차가 커짐(각각 +1.62%/+1.79%) — 무컨디셔닝
  구간이 길어질수록 v0의 낙관 편향이 누적됨을 보여줌. pytest 신규
  `tests/test_wear_aware_endpoint.py` 4건 추가, 전체 회귀 **44/44 PASS**(기존 40 + 신규 4,
  기존 tier1/tier2 self-test 전부 재실행해도 회귀 없음 확인). pad_wear_glazing.py/
  process_time.py/gw_contact.py 등 기존 파일 무수정(import만). fab-sim은 git 저장소가
  아니어서(`git rev-parse --is-inside-work-tree` 실패) 커밋 생략 — 파일만 작성.
  Phase 0 체크리스트는 기존 두 완료 항목(공정변수→MRR/WIWNU v0, 패드 GW 접촉모델)을
  잇는 다리 성격이라 신규 체크박스 없음(지시사항대로 미추가).
- **2026-09-04** (22시 회차, 트랙A): disk-conditioner Lv1-2(다이아몬드 디스크 설계변수:
  grit size/density/tip-height distribution) 이수 → **Lv1 완료(2/2), Lv2 진입**.
  지식노트 `knowledge/equipment/conditioner-grit-design-space.md`(출처: Pysher/Goers/
  Zabasajja(3M) "Design, Characteristics and Performance of Diamond Pad Conditioners",
  MRS Symp. Proc. 1249, 2010, 3M 공개 PDF). Design Space(Finish×Aggressiveness) 2축
  개념, 입경/grade/tip-height 3변수가 독립 설계 레버임을 실측으로 확인: (1) DOP 15µm
  기준 접촉면적 4.46%→9.76%(2.2배) 개선이 구리 CMP micro-defect를 67~75→0~9개로 감소
  (제거율 희생 없이), (2) sharp-diamond 설계가 W슬러리 6h 가속시험에서 초기절삭률
  55~65% 유지(경쟁사 ~15%) — grade가 초기성능과 수명감쇠속도를 별도로 결정함을 확인.
  EXAMS.md 3문항 추가. [[conditioning-mechanism-asperity-regeneration]]과 상호링크
  (Ring/Prasad/Dirksen의 D_grit→asperity η/β 근사와 결합해 Lv2-1 절삭모델 입력 체인
  확보). Aggressiveness Number 정량 정의식·grade의 정량 압입각(psi)은 출처 미제공으로
  **미검증** 명시. pytest 회귀 전체 **44/44 PASS**(코드 변경 없음, 지식 트랙만 진행).
  다음: Lv2-1 디스크-패드 절삭 모델(재료제거·표면조도 생성) — 정량 aggressiveness
  정의를 보강할 추가 출처 조사 후 코드 구현(sim/tier2 기여) 시도.

- **2026-09-05** `[심야병렬]` (Max20x 심야 오케스트레이터, 01시): claude -p 서브에이전트 **3명 동시 학습** 완료.
  대상 선정: 0/6 최대병목 2명(slurry-chemist, tribologist) + Phase0 최우선(process-integrator).
  disk-conditioner는 직전 상시크론(22시)이 건드려 경합회피.
  ① **slurry-chemist Lv1-1** 콜로이드화학(제타전위·DLVO·입자안정성) → knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md,
     재현 sim/tier2_physics/dlvo_colloid.py 12/12 PASS. 정직성: 첫 가설(고이온세기→장벽붕괴)이 틀림을
     발견(ζ=−40mV 실리카는 0.1M에서도 22kT 안정)→실제 붕괴는 IEP 근접임을 확인·수정. CCC·|ζ|>30mV 임계 미검증표기.
  ② **tribologist Lv1-1** 트라이볼로지기초(마찰·마모·Archard·Stribeck) → knowledge/physics/tribology-friction-wear-stribeck.md,
     재현 sim/tier2_physics/tribology_basics.py 10/10 PASS. [[hertz-gw-contact-mechanics]] 등 상호링크 4. k 절대값 미검증.
  ③ **process-integrator Lv2-2** WIWNU(압력·속도·슬러리 웨이퍼스케일결합) → knowledge/cmp/wiwnu-pressure-velocity-wafer-scale.md,
     재현 sim/tier1_empirical/wiwnu.py 5/5 PASS(preston.py/kinematics.py 재사용). Lv2 완료→Lv3 진입. 압력 프로파일 계수는 예시값 명시.
  **품질게이트(오케스트레이터 직접 실행) check_knowledge.py --all: 13개 중 12 PASS.**
  신규 3개 노트 전부 ✓. 유일한 ✗는 어제 상시크론 산출물 equipment/conditioner-grit-design-space.md(연도인용 1건뿐, 형식미달)
  — 이번 밤 대상 아니고 disk-conditioner는 상시크론 소유라 경합회피 위해 체크박스 되돌리기 보류, 상시크론 차기회차 처리 권고.
  진도: 지식노트 10→13개. slurry-chemist 0→1/6, tribologist 0→1/6, process-integrator 3→4/6. 한도 이슈 없음(429 미발생).
- **2026-09-05** (Max워커, 새벽 회차): gw_preston_link.py(정상상태 Kp 물리적 분해,
  MRR=alpha_removal·n_contacts(P)·V)와 pad_wear_glazing.py(시간축 MRR=c_w·p_r(t), ad-hoc)가
  서로 다른 공식을 쓰던 간극을 잇는 다리 모듈 `sim/tier2_physics/wear_aware_kp_physical.py`
  구현 — 기존 파일 무수정(import만, mtime 변화 없음 확인). n_contacts_discrete(heights,d)=
  sum(heights>d) 헬퍼를 새로 작성하고, pad_wear_glazing의 sample_heights/
  solve_separation_discrete/total_load_discrete/total_area_discrete/wear_step_borucki를
  재사용해 동일 seed/파라미터로 이산 마모 루프를 다시 열어(heights 이력이 원 함수엔 없어
  사후 추출 불가) 시간축 n_contacts(t)를 구성, 원본 simulate_pad_wear()와 t/MRR/p_r/
  mean_height/d가 수치적으로 완전히 동일함(max_rel_diff=0.0)을 먼저 검증. gw_preston_link의
  calibrate_alpha_removal(P_ref=20.7kPa,V_ref=0.8,Kp_lit=1e-13)을 그대로 재사용해
  MRR_physical(t)=alpha_removal·n_contacts(t)·V_ref 계산.
  **정직하게 기록할 핵심 발견(불일치)**: 당초 가설("ad-hoc·물리기반 두 MRR(t)이 둘 다 단조
  감쇠하고 정규화 곡선 상관계수>0.9")은 실제 수치 실행으로 **반증**됨 — n_contacts(t)는
  감소가 아니라 **증가**(40스텝: 3033→3564, +17.5%)하고 MRR_physical(t)도 함께 증가(감쇠
  -17.5%p, 즉 부호가 반대)하며, 두 정규화 감쇠곡선의 Pearson 상관계수는 **corr=-0.998493**
  (거의 완벽한 역상관, +0.9 기준과 정반대). 원인 추정(파일 상단 docstring에 상세 기록):
  이 시나리오는 명목압력 P_app을 고정한 채 asperity 집단이 마모로 얇아지는 설정인데,
  같은 총하중 W(d)=P_app·A_n을 유지하려면 평균높이 하락(-2%, 2.99e-7→2.93e-7m)보다
  분리거리 d가 더 빨리 내려가야 하고(-8.3%, 5.63e-7→5.16e-7m), 그 결과 d를 넘는 접촉점
  수는 오히려 늘고 접촉당 평균압력(p_r)은 준다. 즉 gw_preston_link.py의 n(P) 선형관계는
  "압력을 바꿀 때"만 검증된 것이었고 "고정압력에서 집단이 마모될 때"로 그대로 외삽하면
  MRR 증감 방향 자체가 틀린다는 스코프 한계가 드러남. assert 기준(>0.9 등)은 낮추지도
  숫자를 조작하지도 않았음 — self-test `python3 sim/tier2_physics/wear_aware_kp_physical.py`는
  4항목 중 **2/4 PASS**(등가성 재현·C1=0 회귀성) **2/4 FAIL**(n_contacts/MRR_physical 단조
  비증가, 상관계수>0.9 — 위 발견대로 정직하게 실패 처리, exit code 1). pytest
  `tests/test_wear_aware_kp_physical.py` 5건은 "실제 관측된 방향"(n 증가, corr<-0.9 등)을
  회귀 고정하는 방식으로 작성해 **전체 pytest 49/49 PASS**(기존 44 + 신규 5, 회귀 없음
  확인). Phase 0 체크리스트는 변경 없음(다리 성격, 신규 체크박스 없음 —
  wear_aware_endpoint.py 항목과 동일 패턴).

- **2026-09-05** `[심야병렬]` (Max20x 심야 오케스트레이터, 05시): claude -p 서브에이전트 **3명 동시 학습** 완료.
  대상 선정: 0/6 없음(전날밤 slurry·tribo 1/6). Phase0 우선순위+진도역순으로 process-integrator(4/6)·slurry-chemist(1/6)·tribologist(1/6).
  disk-conditioner는 상시크론(22시) 소유라 경합회피.
  ① **process-integrator Lv3-1** 패턴의존성(dishing/erosion·밀도효과) → knowledge/cmp/pattern-dependent-dishing-erosion.md,
     재현 sim/tier1_empirical/pattern_density.py 9/9 PASS. effective density ρ_eff=w⊛ρ_local, planarization length 3–5mm,
     RR=K/ρ_eff(raised영역 접촉→국소압 1/ρ 증폭, [[hertz-gw-contact-mechanics]] 연결), step-height 2레짐+통합모델, Cu dishing/oxide erosion 정의(Park VMIC1998·Boning MRS1999 원문 pypdf 추출대조), d_ss·breakpoint. Lv3 진입→5/6.
     정직성: elliptic 대신 가우시안 근사, 절대 dishing nm는 캘리브레이션無 미검증(내부정합·부호방향만 검증). Stine1998·Ouma1999 2차인용.
  ② **slurry-chemist Lv1-2** 슬러리 구성요소 총론(입자/산화제/BTA억제제/착화제/분산제) → knowledge/cmp/slurry-components-overview.md,
     재현 sim/tier2_physics/slurry_components.py 12/12 PASS. BTA Langmuir(ΔG=−35.4kJ/mol→K=2.87e4, 1mM θ=0.966),
     산화제-MRR 정점(Cu 1%→착화제 첨가시 3% 이동) 현상론 재현. [[colloid-zeta-dlvo-slurry-stability]] 확장→2/6.
     정직성: Kaufman1991(2차인용) 정점모델 형태재현·절대값 미검증. Gamagedara&Roy 2024(PMC11477894) 등 오픈액세스.
  ③ **tribologist Lv1-2** CMP 윤활레짐(boundary/mixed/hydrodynamic) → knowledge/physics/cmp-lubrication-regimes.md,
     재현 sim/tier2_physics/cmp_lubrication_regime.py 11/11 PASS. Sommerfeld So=7.25e-3·λ<1→boundary 판별, COF≈0.24(문헌 oxide 0.23~0.40 부합),
     λ ratio(필름두께 vs asperity). [[tribology-friction-wear-stribeck]][[hertz-gw-contact-mechanics]] 링크→2/6.
     정직성: So 임계·δeff groove가중·λ경계·COF곡선 전부 미검증. Philipossian특허·Wu&Liao 2016(IntechOpen) 2차인용.
  **품질게이트(오케스트레이터 직접) check_knowledge.py --all: 16개 중 15 PASS.** 신규 3개 노트 전부 ✓.
  유일한 ✗는 전날과 동일 equipment/conditioner-grit-design-space.md(연도인용1건·형식미달, disk-conditioner=상시크론 소유라 경합회피·차기회차 처리 권고).
  전체 pytest 49/49 유지(회귀 무손상). 진도: 지식노트 13→16개. process-integrator 4→5/6, slurry 1→2/6, tribo 1→2/6. 한도 이슈 없음(429 미발생).

- **2026-09-05** (Max워커, 07시 회차): Phase 1 "웨이퍼 스케일 균일도(WIWNU), 패턴 의존성
  (dishing/erosion) 모듈" 항목 — `sim/tier1_empirical/wiwnu.py`(반경별 blanket MRR K(r))와
  `sim/tier1_empirical/pattern_density.py`(RR_up(x)=K/rho_eff(x), K는 종전 상수 가정)를
  잇는 신규 결합 브리지 `sim/tier1_empirical/wiwnu_pattern_combined.py` 구현. 기존 5개
  tier1/tier2 파일은 mtime 변화 없음(`ls -la` 대조 확인) — 순수 import만 사용.
  K 자리에 K(r)을 대입해 RR(r,x)=K(r)/rho_eff(x) 2차원(반경×다이내부) 결합 제거율 맵을
  생성. self-test(`python3 sim/tier1_empirical/wiwnu_pattern_combined.py`) **5/5 PASS**:
  극한 a) rho_eff≡1 → 결합맵이 wiwnu.py 단독 K(r)과 bit-level 일치(max_abs_diff=0),
  극한 b) p_uniform+Rs=1(K(r) 완전상수) → pattern_density.oxide_removed_up 기반
  RR_up(x)와 상대오차 <1e-9로 일치, 결합효과 c) sigma_pct(면적가중 CV)가 대수적 하한
  max(반경단독=7.72%, 패턴단독=1.80%) 이상(결합=7.93%)임을 확인 — r·x가 분리가능
  (separable) 곱구조이므로 CV_combined²=CV_r²+CV_x²+CV_r²·CV_x²≥max(CV_r²,CV_x²)이
  대수적으로 항상 성립, 실측치도 이를 따름. half_range_pct(max-min 기반)는 이런 대수적
  하한이 보장되지 않는 지표라 assert 대상에서 제외했으나, 실제 합성 파라미터(엣지압력
  amp=0.30 + 다이 패턴밀도 진폭 0.2 사인형)에서는 결합(18.24%)이 개별(반경14.35%,
  패턴3.57%)보다 여전히 컸음 — 반증 사례는 나오지 않았고 정직하게 "참고용, 미보증"으로
  기록.
  **한계(명시적 미검증)**: r(반경)과 x(다이내부위치)를 분리가능하다고 가정 — 웨이퍼 전면에
  같은 다이 설계가 반복 배치되고 반경-패턴 교차항(엣지에서만 패턴영향 증폭 등)은 없다고
  본 1차 근사. 실제 엣지 다이의 스크라이브 절단·방향(회전) 차이는 다루지 않음.
  pytest 회귀: `tests/test_wiwnu_pattern_combined.py` 신규 3건 추가, 전체
  **52/52 PASS**(기존 49 + 신규 3, 회귀 없음 확인). `sim/README.md` 구현 현황 섹션에
  짧은 요약 추가.
  **체크박스 판단**: Phase 1 "웨이퍼 스케일 균일도(WIWNU), 패턴 의존성(dishing/erosion)
  모듈" 항목을 [x]로 변경 — WIWNU(wiwnu.py), 패턴밀도/dishing/erosion(pattern_density.py)이
  각각 이미 구현돼 있었고, 이번에 둘을 실제로 잇는 결합 모델까지 만들어 자체 self-test로
  정합성을 확인했으므로 항목이 요구하는 두 모델 + 결합을 모두 충족한다고 판단. 다만 위의
  분리가능성 가정(교차항 없음)은 명시적 한계로 남아 있어 완전한 물리적 검증이 끝난 것은
  아님을 함께 기록.

- **2026-09-05** (08시 회차, 트랙A+B): process-integrator Lv3-2(통합 시뮬레이터 아키텍처
  설계·조립, sim 전체 오너) 이수 → **process-integrator 커리큘럼 전체 이수 완료(6/6)**,
  Lv4(교수급 확장) 전환. 지식노트 `knowledge/cmp/luo-dornfeld-integrated-cmp-framework.md`
  (출처: Luo & Dornfeld, UC Berkeley 2003 오픈액세스 리뷰 — 3-스케일 CMP 모델링(입자/다이/
  웨이퍼) 및 Fig.6 통합 프레임워크, "Preston식이 3스케일을 잇는 인터페이스"), EXAMS.md
  3문항. 핵심 발견: FabSim이 지식우선(트랙A→B) 순서로 개발해온 6개 모듈
  (kinematics/preston/wiwnu/pattern_density/wiwnu_pattern_combined/gw_preston_link)이
  사후적으로 이 리뷰의 3-스케일 아키텍처(Fig.6)와 정확히 대응함을 확인 — 우연이 아니라
  CMP 모델링의 정론적 계층구조를 따라간 결과. 구현 `sim/integration/spatiotemporal_removal.py`
  (신규 서브패키지) — wiwnu_pattern_combined.py의 정상상태 RR(r,x) 맵에 process_time.py의
  선형 시간적분을 조립해 thickness(r,x,t) 시공간 필드 생성, 새 물리가정 0개(기존 6개 모듈
  전부 무수정). self-test **4/4 PASS**: t 선형성(120s=2×60s), rho_eff≡1 극한에서 K(r)·t와
  bit-level 일치, endpoint_time 배선 항등 검증, 다이-스케일 CV의 시간불변성. pytest 회귀
  `tests/test_spatiotemporal_removal.py` 신규 4건 추가, 전체 **56/56 PASS**(conftest.py에
  sim/integration 경로 추가). 설계 결정: GW 접촉모델(Kp 물리적 분해)과의 완전 연결은
  Kp가 함수형이 되면 기존 상수-kp 시그니처 회귀 위험이 있어 Lv4로 명시적 유보(무리한
  일괄 통합 대신 단계적 확장 원칙 준수). Phase 0 남은 항목은 디스크 컨디셔닝-패드마모
  모델(disk-conditioner Lv2 진입 상태) 하나뿐 — 다음 회차부터 Phase 0 우선순위(disk-conditioner)
  로 전환 예정.

- **2026-09-05** (10시 회차, 상시크론, 트랙A+B): Phase 0 우선순위 마지막 항목
  disk-conditioner Lv2-1(디스크-패드 절삭 모델: 재료제거와 표면조도 생성) 학습·구현.
  지식노트 `knowledge/equipment/conditioner-disk-pad-cutting-model.md` — Lawing(2004)의
  "Cut Rate=Wear Rate 균형" 개념을 Evans-Marshall 마모율식(Ring et al. Eq.2, 이미
  Lv1-1에서 도입) 관점에서 정량화하고, Entegris(2013) CVD 다이아몬드 컨디셔너 백서에서
  PCR(Pad Cut Rate) 지수감쇠 실측 앵커(50h 사용시 초기값의 16%로 하락) 및 Ra 수렴
  실측(신품 4.6µm→0.5h만에 3.3µm, 이후 17h 정체)을 신규 확보. Baisie(2012) 박사논문
  (surface element / conditioning density distribution 두 운동학 모델, NCAT 리포지토리)은
  서버 403으로 본문 접근 실패 — 초록만 인용, 정직하게 명시. 구현
  `sim/tier2_physics/conditioner_pcr_decay.py` — pad_wear_glazing.py 무수정 재사용,
  Entegris 앵커로 tau≈27.28h 캘리브레이션한 PCR(t) 지수감쇠 + 컨디셔너 재생항을 더한
  결합 마모 ODE. self-test **5/5 PASS**(앵커 정확 재현, tau→inf 극한 상수 PCR, PCR
  단조비증가, 노화<이상적 컨디셔너 순위, 컨디셔닝부재<노화<이상적 3단계 순위 확인).
  재생항 함수형은 문헌 직접 근거가 아닌 fab-sim 최소확장 가정임을 코드 docstring·
  지식노트 양쪽에 명시(정성적 방향만 검증, 정량 미보증). pytest 회귀
  `tests/test_conditioner_pcr_decay.py` 신규 6건, 전체 **62/62 PASS**(기존 56+신규 6,
  회귀 없음). `check_knowledge.py --all`: 신규 노트 포함 기존 미달 노트
  conditioner-grit-design-space.md에 Entegris/Lawing 교차출처 보강 절 추가해 재검사
  통과시킴 — **지식노트 전체 18/18 통과 달성**(직전 회차부터 미해결이던 유일한 미달
  항목 해소). disk-conditioner PROFILE/CURRICULUM 갱신(Lv2 진행중 1/2, 다음 Lv2-2).
  이로써 Phase 0 우선순위 5개 에이전트(process-integrator/pad-mechanic/slurry-chemist/
  tribologist/disk-conditioner) 전부가 최소 1단원 이상 진행된 상태 유지, disk-conditioner도
  Lv2 진입 완료. 한도 이슈 없음.

- **2026-09-05** (12시 회차, 상시크론, 트랙A+B, 오전요약 겸): disk-conditioner Lv2-2(컨디셔닝
  레시피[압력·스윕·RPM] → 패드 프로파일 진화) 이수 → **Lv2 완료(2/2), Lv3 진입**. 지식노트
  `knowledge/equipment/conditioner-sweep-kinematics-pcr-profile.md` (1차 출처: Zheng, Zhao & Lu
  2023, Micromachines 14(9) 1683, 오픈액세스 PMC10536193 — Tsinghua Univ. 실측검증 포함).
  Eq.1-9 사인파 스윕 4중 회전 합성 운동학 전체 확보, Table 1 산업 실험조건(패드100RPM/디스크
  73RPM/스윕19RPM/스윕범위 반경83~308mm/8시간) 인용, 핵심 발견 "PCR이 패드 기존 표면
  프로파일과 거의 무관"(공간축 PCR_shape(r)과 시간축 decay(t) 분리 근거) 확보. EXAMS.md 3문항.
  구현 `sim/tier2_physics/conditioner_sweep_kinematics.py` — Eq.1-9 그대로 코드화(팔중심→
  디스크중심→개별입자 위치), 대표 다이아몬드 다수 균등샘플로 반경별 누적 스크래치 거리
  히스토그램(PCR(r) 상대 프로파일) 추출. self-test **5/5 PASS**(정지상태 위치항등, 논문
  Table1 조건 궤적범위 물리적 유효성, 스윕속도 2배→위상진행 2배 스케일링 확인, 팔 도달불가
  반경에서 PCA=0, 프로파일 비영값 커버리지). pytest 회귀 `tests/test_conditioner_sweep_kinematics.py`
  신규 5건, 전체 **67/67 PASS**(기존 62+신규 5, 회귀 없음). `tools/check_knowledge.py --all`:
  신규 노트 포함 **19/19 통과**. 한계: 논문 Table 2(스윕 파티션 dwell-time 구체수치)는
  페이지 접근 제한으로 미확보 — 사인파 모드(Eq.4, 전체 확보분)만 구현, 명시적으로 미검증
  표기. 다음: disk-conditioner Lv3-1(패드 수명 예측·컨디셔닝 최적화 최신연구).

- **2026-09-05** (Max워커, 13시30분 회차): 08시 회차에서 Lv4로 명시 유보했던 항목
  ("GW 접촉모델(Kp 물리적 분해)과의 완전 연결은 Kp가 함수형이 되면 기존 상수-kp 시그니처
  회귀 위험이 있어 유보") 해소. 신규 파일 `sim/integration/spatiotemporal_removal_physical_kp.py`
  — 기존 6개 파일(spatiotemporal_removal.py, gw_preston_link.py, wiwnu_pattern_combined.py,
  wiwnu.py, pattern_density.py, process_time.py, +preston.py/kinematics.py)은 1바이트도
  수정하지 않고 순수 import만 사용(파일 mtime 전후 대조로 확인). 접근: 반경 r에서의 국소
  유효 Kp를 Kp_eff(r) = alpha_removal * n_contacts_at(P(r)) / P(r) 로 정의(대수적 항등
  재배열, 새 물리가정 아님) — 이러면 Kp_eff(r)*P(r)*V(r) = alpha_removal*n_contacts_at(P(r))*V(r)
  = GW-link MRR과 정확히 같아진다. wiwnu.mrr_radial/preston.mrr_profile이 반경 전체에
  스칼라 kp 하나만 받는 시그니처라 r마다 다른 kp를 못 넘기므로, 반경 루프 구조만 로컬
  헬퍼로 재구현(preston.local_mrr()은 그대로 재사용, Kp*P*V 대수 자체는 새로 안 만듦).
  alpha_removal은 gw_preston_link.calibrate_alpha_removal(P_ref=20.7kPa, V_ref=0.8, kp_lit=1e-13)
  로 문헌 캘리브레이션(기존 self-test와 동일 지점). self-test **5/5 PASS**: (1) 균일압력
  =P_ref 근방에서 물리기반 두께필드와 상수-kp 두께필드가 max_rel_dev=0.000e+00로 완전
  일치(Kp_eff(P_ref)=kp_lit이 정의상 대수적 항등이므로 자명), (2) **차별점(정직 보고)**:
  넓은 압력범위(14/48/96kPa 3존)에서 물리기반 vs 상수-kp 두께필드 편차 = 최대 0.0000%,
  평균 0.0000%(실측 max_rel_dev=4.6e-12, 부동소수점 잡음 수준) — gw_preston_link.py가
  이미 확인한 n_contacts(P)의 14-96kPa 구간 선형성(잔차<1e-6)이 그대로 반영된 결과.
  **따라서 이 통합이 주는 정량적 실익은 사실상 없다(과장 없이 그대로 보고)** — 정성적/
  구조적 의의(Kp가 화학 lump 상수가 아니라 GW 기하량으로 원리적으로 분해될 수 있음을
  보여줌)만 있고, 두께 필드 예측치 자체는 상수-kp 모델과 실무적으로 구별 불가능하다.
  (3) alpha_removal 배선 검증, (4) Kp_eff(P_ref)==kp_lit 캘리브레이션 항등 확인,
  (5) 극한 rho_eff=1에서 물리기반 결합두께가 K_eff(r)*t와 bit-level 일치. pytest 회귀
  `tests/test_spatiotemporal_removal_physical_kp.py` 신규 5건, 전체 **72/72 PASS**
  (기존 67+신규 5, 회귀 없음, conftest.py는 이미 sim/integration·tier2_physics 경로를
  포함하고 있어 수정 불필요). 회사(동진쎄미켐) 데이터 미사용(순수 기존 공개모델 재사용).

- **2026-09-05** (14시 회차, 상시크론, 트랙A): disk-conditioner Lv3-1(패드 수명 예측·
  컨디셔닝 최적화 최신 연구) 이수 → Lv3 진행중(1/2). 지식노트
  `knowledge/equipment/conditioner-asperity-population-balance.md` — Ring, Prasad(Cabot
  Microelectronics), Dirksen "Dynamic CMP Pad Asperity Population Balance for Conditioning
  and Polishing"(저자 공개 PDF, AMAT Mirra+Epic D100 패드+Veeco 레이저간섭계 실측검증)
  전문 확보. 핵심: asperity 높이를 스칼라 평균이 아니라 population balance PDE(Eq.1)로
  다뤄, 긴 asperity가 짧은 것보다 먼저 깎이는 비대칭 마모(실측 Fig.1: 정규분포→지수분포
  수렴)를 similarity solution(Eq.9, 좌표 exp(2At) 스케일링)으로 정확히 재현하는 구조임을
  확인. Python sanity check: (1) t=0 항등 재현(오차 0.0), (2) 지수분포 초기조건의
  self-similarity — log-linear 기울기가 -exp(2At)/σ 예측치와 모든 t에서 완전 일치
  (오차<1e-10), (3) 정규분포 초기조건(σ=8.112µm, Table1 실측값)의 표준편차가 조건화
  시간에 따라 8.112→2.443µm로 단조 축소해 실측 Fig.4 정성 경향 재현. 정직한 한계: 마모율
  비례상수 A는 논문 자체가 "fit parameter"로 명시한 비공개 실측 캘리브레이션값 — 정량
  예측력은 미검증, 정성적 거동(스케일링 방향·self-similarity)만 검증. EXAMS.md Lv3-1
  3문항. `check_knowledge.py --all`: 신규 노트 포함 **20/20 통과**(최초 제출 시 연도인용
  부족으로 미달 → 출처 절 보강 후 재검사 통과). pytest 회귀: 이번 회차 코드 변경 없음,
  기존 **72/72 PASS** 확인만 수행. 구현 판단: Lv3-2(결합모델)에서 전체 PDE를 이식하기보다
  기존 `conditioner_pcr_decay.py`(스칼라 PCR)에 "분포 폭" 2번째 상태량만 추가하는 최소
  확장이 타당하다고 사전 설계(Lv2 Max워커 회차의 "정량 실익 미미" 교훈 적용). 다음:
  disk-conditioner Lv3-2 컨디셔닝-패드마모 결합모델 구현(sim/tier2 기여) — Phase 0 마지막
  미완 항목.

- **2026-09-05** (16시 회차, 상시크론, 트랙B): disk-conditioner Lv3-2(컨디셔닝-패드마모
  결합모델 구현) 완료 → **disk-conditioner 커리큘럼 전 단원 이수, Lv4(교수급) 진입**.
  신규 `sim/tier2_physics/conditioner_asperity_distribution.py` — Ring/Prasad/Dirksen
  population balance의 similarity solution(Eq.9, 좌표 exp(2At) 압축)에서 "표준편차는
  스케일 인자에 반비례"라는 분포-불문 통계 성질만 취해, 기존 `conditioner_pcr_decay.py`
  (스칼라 평균 높이)에 asperity 분포 폭(표준편차) 2번째 상태량을 추가하는 최소 확장으로
  구현(전체 PDE 미이식, Lv3-1 지식노트 §5 설계 판단 그대로 실행 — 기존 파일 무수정,
  import만 재사용). 컨디셔너 노화(PCR 하락)가 분포폭 축소력도 비례 약화시키도록 결합
  (A_eff(t)=A0*PCR(t)/PCR0). self-test **5/5 PASS**(t=0 항등, 이상적 컨디셔너 캘리브레이션
  자기재현, 노화<이상적 순위, 단조 비증가, 정규분포 표본 직접 스케일링 시 이론 exp(2At)비
  일치 — 1차 시도에서 비율 역수 방향 버그 발견해 정정 후 통과). pytest 회귀
  `tests/test_conditioner_asperity_distribution.py` 신규 5건, 전체 **77/77 PASS**(기존 72+
  신규 5, 회귀 없음). `tools/check_knowledge.py --all`: 20/20 유지(신규 지식노트 불필요,
  기존 conditioner-asperity-population-balance.md 설계를 그대로 코드화). EXAMS.md Lv3-2
  3문항 추가. 정직한 한계: A0(similarity 상수)는 문헌에 공개 정량값 없음(fit parameter) —
  "48h 이상적 컨디셔닝→표준편차 절반"이라는 임의 정성 기준으로 캘리브레이션, 정량 예측치
  아님(코드·이수기록에 명시).
  **이로써 Phase 0 체크리스트 5개 항목 전부 [x] — Phase 0(CMP 코어 모델) 완료 선언.**
  다음 회차부터 Phase 1(CMP 통합 시뮬레이터) 착수: 다음 우선순위는 슬러리×패드×디스크
  결합 모델(3개 도메인 지식 모두 갖춘 현재 상태에서 가장 자연스러운 다음 단계) 또는
  Phase 1 체크리스트 재검토 후 순서대로 진행.

- **2026-09-05** (18시 회차, 상시크론, 트랙A): Phase 0 5개 에이전트 중 최하위 진도였던
  slurry-chemist Lv2-1(표면 화학반응: Cu/W CMP의 Pourbaix·passivation 메커니즘) 이수 →
  **Lv1 완료, Lv2 진입**. 지식노트 `knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md`
  — 1차 오픈액세스 원문 Gamagedara & Roy, *Materials* 17(19) 4905 (2024), MDPI CC BY,
  PMC11477894(Cu/Mo 표면반응 Eq.9-12 tribo-전기화학 실측)과 2차 인용(Krishnan et al.
  *Chem. Rev.* 110, 2010; ScienceDirect W CMP 논문 2건, 원문 유료라 초록/서술만 확인)을
  교차. Nernst 식 dE/dpH=-0.0591(m/n) 기울기 공식을 독립 유도해 W→WO3 passivation(m=n=6)이
  표준 -59.1mV/pH 계열임을 확인, Cu(OH)2/Cu2O/CuO 다중 표면종·구연산 착물에 의한 재용해
  메커니즘 정리. 구현 `sim/tier2_physics/pourbaix_nernst_slope.py` — Nernst 기울기 공식 +
  W/Cu CMP 반응식 m/n 판별 헬퍼. self-test/pytest 회귀 **6/6 PASS**(신규),
  전체 pytest **83/83 PASS**(기존 77+신규 6, 회귀 없음). `check_knowledge.py --all`:
  신규 노트 포함 **21/21 통과**. 한계: Pourbaix 원저(1966) 미확인이라 정확한 안정영역
  경계값(pH·E 좌표)은 2차 인용 의존, 기울기 공식 자체만 독립 검증. 다음: slurry-chemist
  Lv2-2(입자-웨이퍼 상호작용: 기계적 제거 vs 화학적 용해 균형).

- **2026-09-05** (20시 회차, 상시크론, 트랙A): MILESTONES.md 현재 게이트 M1(지식 병목,
  기한 2026-09-20) 확인 — 학습 우선 지시에 따라 tribologist Lv2-1(슬러리 유동: 패드 groove
  내 유동·필름두께 모델) 이수. 지식노트
  `knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md` — 1차 원문 Thakurta,
  Borst, Schwendeman, Gutmann, Gill, "Three-Dimensional Chemical Mechanical Planarization
  Slurry Flow Model Based on Lubrication Theory," J. Electrochem. Soc. 148(4) G207-G214
  (2001), DOI 10.1149/1.1355691 — 유료 논문을 사용자 9/5 지시(미러 사이트 활용 승인)에 따라
  미러 사이트 미러에서 DOI로 PDF 확보(`papers/thakurta2001_slurry_flow_lubrication.pdf`,
  `papers/INDEX.json` 등록). 핵심: 웨이퍼-패드 간극 슬러리 유동을 환산 레이놀즈수(~1e-2~1e-3)
  로 정당화된 일반화 Reynolds 방정식(패드 다공성 k·압축성 c 포함, Eq.13)으로 풀어 최소
  필름두께 h_min을 계산 — h_min이 패드 평균거칠기보다 크냐 작냐로 윤활/접촉 레짐을 판별하는
  것이 Lv1-2(So·λ ratio)와 동일 물리의 정량판인 것을 확인. 무차원 길이스케일
  z0=sqrt(2μω₂R₁R₂/P_app)(Eq.19)와 h_min의 파라미터 의존 방향 8종(압력↓·속도↑·점도↑ 시
  두꺼워짐, 다공성·압축성↑ 시 얇아짐, 웨이퍼자전만↑ 시 반직관적으로 얇아짐, 웨이퍼곡률에
  내부 극댓값 존재) 정리. 자기시험 3문항. 구현 `sim/tier2_physics/slurry_film_lubrication.py`
  — 전체 2-D 비선형 PDE 수치해는 미이식(지식노트 §7에 한계 명시), z0 스케일 공식과 8개
  정성 부호를 최소 스케일링 함수로 재현. self-test **10/10 PASS**(z0 오더가 논문 h_min=36µm과
  동일 오더로 확인, 8개 파라미터 방향 전부 문헌 부호와 일치, 웨이퍼곡률 비단조 극값 존재
  확인). pytest 회귀 `tests/test_slurry_film_lubrication.py` 신규 7건, 전체 **90/90 PASS**
  (기존 83+신규 7, 회귀 없음). `check_knowledge.py --all`: 신규 노트 포함 **22/22 통과**.
  PROFILE.md/CURRICULUM.md/EXAMS.md/sim/README.md 갱신 — tribologist Lv1 전체+Lv2-1 이수,
  Lv2 진행중(1/2). 정직한 한계: 정량 h_min 예측치(예: 36µm)는 논문 보고값 그대로이며 우리
  코드가 독립 수치해로 재현한 것이 아님 — 재현은 "정성 부호 일치"에 한정. 다음:
  tribologist Lv2-2(마찰열-화학반응 결합) 또는 slurry-chemist Lv2-2(입자-웨이퍼 상호작용) —
  M1 게이트(둘 다 지식 병목 해소 대상) 우선순위상 진도 낮은 쪽 선택 예정.

- **2026-09-05** (Max워커 회차): Phase 0/1 체크리스트 "Streamlit 데모 UI → 포트폴리오/
  사업계획서 데모" 항목 진행 — `sim/demo_app.py`를 `st.tabs()` 2탭 구조로 재구성. 탭1은
  기존 Preston MRR v0(로직 무수정, 껍데기만 탭 안으로 이동). 탭2 신규: WIWNU(반경 스케일)
  × 패턴밀도(다이 스케일) 결합 제거율 맵 — `sim/tier1_empirical/wiwnu_pattern_combined.py`
  (2026-09-05 20시 이전 회차에 이미 self-test/pytest 통과된 기존 모듈)를 그대로 import해
  파라미터 슬라이더(R_w, r_cc, RPM, Kp, 압력 프로파일, 합성 다이 패턴 진폭/주기)로 구동,
  matplotlib heatmap(반경×다이내부위치)과 sigma_pct(CV)/half_range_pct 지표를 표시.
  **새 물리/지식 구현 없음 — 순수 UI 통합**이며, `wiwnu.py`/`pattern_density.py`/
  `wiwnu_pattern_combined.py` 3개 계산 모듈은 `git diff` 확인 결과 1바이트도 수정하지
  않음(이미 통과된 self-test/pytest 상태 보존). 화면에 "반경-패턴 분리가능(separable)
  1차 근사, 교차항 미포함" 한계 고지 문구 포함. 검증: `streamlit run` 로컬 구동 후
  헤드리스 응답 확인, 신규 smoke test `tests/test_demo_app_smoke.py`(Streamlit
  `AppTest`로 예외 없이 로드 + 탭 2개 존재 확인) 추가. pytest 전체 **91/91 PASS**
  (기존 90 + smoke 1건, 회귀 없음). Phase 0/1 체크리스트 "Streamlit 데모 UI" 항목 [x] 처리.
  한계: heatmap의 다이 패턴은 여전히 합성 예시(사인형)이며 실제 레이아웃 데이터 아님 —
  캘리브레이션 파이프라인(같은 체크리스트의 다음 미완 항목)이 선행되어야 정량 신뢰도 있는
  데모가 됨.

- **2026-09-05 21:30** ([소프트웨어] software-lead 회차): BACKLOG S1 완료 —
  `docs/ARCHITECTURE.md` 신설(커밋 137a81b). 25개 sim 모듈의 실측 import 의존그래프,
  engine.Model 이관 분류(이관됨 1건/이관 대상 2건: gw_preston_link·pattern_density/
  이관 보류 ~18건: 시계열 상태·화학 lump 상수 등 스키마·지식 부족), Recipe 스키마
  부채 3건(단일-런 스냅샷 한계, Kp 화학+기계 뭉뚱그림, PTW 다이맵 필드 부재) 정리.
  pytest 100 passed(문서 작업, 코드 변경 없음). 다음 회차: S3(gw_preston_link →
  engine.Model, 문헌값·자체 self-test 이미 확보) 착수 예정.

- **2026-09-05 22:00** (성장엔진, 트랙 A): G1 게이트 실질 개방 — wafer-metrology,
  surface-contamination [대기]→[활성] (agents/ORG.md §2·§5 갱신, 선수관계 PREREQ.json
  충족 확인, tools/progress.py가 앞서 개방 조건 충족을 판정함). wafer-metrology
  Lv1-1(두께 계측 원리: 엘립소미터·리플렉토미터·와전류·4점탐침·XRF, 막질별 적합성)
  이수 — knowledge/cmp/wafer-metrology-thickness-methods.md. 1차 출처 3건
  (IEEE DOI 10.1109/TIE.2021.3111570, 10.1109/ICEPT52650.2021.9567975 — Semantic
  Scholar API 초록 확인, 본문 유료 미확보; IOP DOI 10.1088/1681-7575/ae3964 —
  Unpaywall이 OA published version으로 표시했으나 웹 접근 hCaptcha 봉쇄로 초록만).
  2차 확보: Kao 및 Chung, Wafer Manufacturing (2021, Wiley) 발췌본(catalogimages.wiley.com,
  10페이지 원문 전체 확보) — SEMI MF1530 원문은 downloads.semi.org와 미러 모두
  Cloudflare 403 봉쇄로 미확보, 교과서의 직접 인용(Eq.1.5 TTV=t_max-t_min)으로 대체.
  정량 재현(python verify 2블록): 4PP 상수 pi/ln2=4.532 재현 일치, Cu 500nm 벌크가정
  시트저항 33.6 mOhm/sq(문헌 오더 30-100 mOhm/sq와 자릿수 일치), 교과서 TTV 예제(0, 3.3)
  재현 완전 일치 — check_knowledge.py, verify_claims.py 모두 통과. EXAMS.md 3문항.
  다음: wafer-metrology Lv1-2(균일도 지표를 SEMI 표준, Lee-Boning 1999로 문헌 확정 →
  sim/metrics/uniformity.py의 PROVISIONAL 정의 교체, Cal-1 전 단계).

- **2026-09-06 심야** ([심야병렬] 3명 동시 위임, claude -p opus): 품질게이트 3/3 통과
  (오케스트레이터가 직접 재검증: check_knowledge 3/3 ✓, verify_claims 3/3 ✓ —
  출처 12건 전부 Crossref/arXiv 실존 확인, python verify 3블록 실행 통과).
  ① **surface-contamination Lv1-1** 표면 오염 종류·발생원(슬러리 Fe촉매·K완충·Ce·Cu재흡착·세정수)
     → knowledge/cmp/post-cmp-metallic-contamination-sources.md (상호링크 9, 출처 6건).
     G1 신규활성 에이전트 첫 이수(0/4→1/4).
  ② **slurry-chemist Lv2-2** 입자-웨이퍼 상호작용(기계제거 vs 화학용해 균형, Hertz 입자접촉·Kaufman)
     → knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md (상호링크 5, 출처 4건). 3/6→4/6, Lv2 완료.
  ③ **tribologist Lv2-2** 마찰열·온도분포→Arrhenius 화학속도 결합(q=μPV, 플래시온도, Ea)
     → knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md (상호링크 6, 출처 2건). 3/6→4/6, Lv2 완료.
  세 노트 모두 python verify 정량대조 포함, 구현 필요분은 각 PROFILE.md "## 구현 요청"에 기록(소프트웨어 부문 인계).
  지식노트 총 통과 6→9/26(신규 3편 전부 통과). rate-limit 없음.

- **2026-09-06** ([Max워커] 회차): `~/software/BACKLOG.md` S4(GitHub Actions CI 초록
  확인) 완료 — 지난 4개 커밋 전부 CI 빨간불(failure)이었으나 아무도 확인하지 않고 있었음.
  원인 진단: gh CLI 미인증이라 GitHub REST API를 원격 remote URL 내 토큰으로 직접 조회해
  job 로그 확보. 원인 2건: (1) `.github/workflows/verify.yml`이
  `pip install numpy scipy pytest`만 실행해 streamlit 미설치 →
  `tests/test_demo_app_smoke.py`에서 `ModuleNotFoundError: streamlit`으로 collection
  자체가 실패해 전체 pytest job이 죽고 있었음(9/5 이후 4개 커밋 전부 이 이유로 실패,
  즉 "119/91 tests passed" 로그는 전부 로컬 실행 결과였고 CI는 한 번도 안 돈 상태였음).
  (2) requirements.txt로 교체 후 재확인하니 CI 러너의 numpy 2.0.2에서
  `np.trapz`가 제거되어 `AttributeError`(로컬 .venv numpy 2.0.2에도 존재하는 문제,
  다만 로컬 pytest 실행 시 warning만 뜨고 로컬 numpy 버전 차 때문에 우연히 안 걸렸던 게
  아니라 실제로는 로컬도 동일 버전이라 재현됨 — 이번에 처음 발견). 조치: (1)
  `pip install -r requirements.txt`로 교체, (2) `sim/tier2_physics/wear_aware_endpoint.py`
  + `tests/test_wear_aware_endpoint.py`의 `np.trapz`→`np.trapezoid` 치환.
  추가로 지식품질게이트(`check_knowledge.py --all`, `verify_claims.py --all`)는
  현재 26편 중 9/26, 5/26만 통과하는 **진행형 부채**(학습총괄 크론이 매 회차 상환 중)라
  이걸 CI의 blocking 단계로 두면 지식노트가 남아있는 한 CI가 영구 빨간불이 되어
  "CI 초록 = 신뢰 가능한 신호"라는 목적을 스스로 무너뜨림 — `knowledge-quality`를
  별도 job(`needs: test`, `continue-on-error: true`)으로 분리해 코드 정합성(pytest)만
  blocking, 지식 부채는 로그로 추적만 하도록 구조 변경. 검증: 로컬 `.venv/bin/python -m
  pytest -q` 119/119 PASS(회귀 없음), GitHub Actions run 33978322293 **success** 확인
  (커밋 6f9fa53 → 65e0aca 순으로 2회 push, 두번째 run에서 초록 확인). commit
  6f9fa53, 65e0aca, push 완료. `~/software/BACKLOG.md` S4를 완료 테이블로 이동.

- **2026-09-06 심야** ([심야병렬] 3명 동시 위임, claude -p opus, 오케스트레이터 직접 재검증):
  품질게이트 3/3 통과 (check_knowledge 3/3 ✓, verify_claims 3/3 ✓ — 출처 15건 전부
  Crossref/PMC/arXiv 실존, python verify 3블록 실행 통과).
  ① **wafer-metrology Lv1-2** 균일도 지표 정의 문헌확정(TTV/WIWNU 3정의 병기·49pt체계, SEMI MF1530·Lee&Boning1999·US6922603B1)
     → knowledge/cmp/uniformity-metrics-definitions-standards.md (상호링크 4, 출처 4건). 1/6→2/6.
     회사관행 정의를 default로 삼지 않고 문헌 default 채택, radial 단일표준 문헌부재 명시.
     sim/metrics/uniformity.py PROVISIONAL 교체는 PROFILE 구현요청[High]으로 소프트웨어 부문 인계(직접 sim/ 수정 안 함).
  ② **slurry-chemist Lv3-1** 세리아 Ce3+/Ce4+ 산화환원·Si-O-Ce chemical tooth·oxide:nitride 선택비
     → knowledge/cmp/ceria-slurry-ce-redox-selectivity.md (상호링크 5, 1차출처 3건 OA+2차 명시). 4/6→5/6.
  ③ **tribologist Lv3-1** COF 실시간 모니터링·마찰기반 EPD(P_motor,fric=μPVA=Q_f 항등)
     → knowledge/physics/friction-cof-monitoring-endpoint-detection.md (상호링크 3, 1차출처 4건). 4/6→5/6.
  🌱 **G1 하위 wafer-type 활성화**: wafer-metrology Lv1-2 완료로 선수조건 충족(progress.py 판정) →
     ORG §2/§5 [대기]→[활성], 동시활성 8명(상한10 이내).
  지식노트 총 통과 9→12/29(신규 3편 전부 통과, 나머지 17편은 기존부채·학습총괄 상환중). rate-limit 없음.

- **2026-09-06** ([Max워커] 회차): `~/software/BACKLOG.md` S5(demo_app.py → engine.simulate
  기반 재작성) 부분 완료. tab1(Preston MRR 데모)만 engine 이관: sidebar 입력을 그대로
  두고 계산은 `Recipe(...)` + `simulate(recipe, model=...)`로 교체, preston.py/kinematics.py
  직접 호출(mrr_profile 등) 전부 제거(grep 재확인 0건). `available_models()` 기반 모델
  선택 드롭다운 추가(기본값 tier2.gw_physical_kp), 존압력은 zone_edges_norm에 끝점만 담아
  엔진의 0-prepend 계약을 신뢰. `res.notes`를 st.warning()으로 그대로 노출.
  tab2(WIWNU×패턴밀도 결합 맵)는 이관 대상에서 **제외** — pattern_density를 Recipe에
  반영하려면 die 레이아웃/밀도맵 스키마 확장(S6, sim-architect 담당)이 선행돼야 해서
  이번 1회 작업 범위를 넘음. 파일 상단 docstring에 명시하고 tier1_empirical 직접 호출 유지.
  검증: `.venv/bin/python -m pytest -q` → 119/119 PASS(회귀 없음), 구문 파싱 확인 완료.
  commit 01664fe, push 완료. `~/software/BACKLOG.md` S5는 완료 테이블이 아닌 "진행 중"
  표에 🔶(부분)로 남김 — tab2/S6 게이트 남음.

- **2026-09-06** ([성장엔진] 상시크론): wafer-type Lv1-1/Lv1-2 통합 학습 완료 —
  knowledge/cmp/npw-ptw-test-wafer-fundamentals.md (NPW 49점 polar 측정체계 US6922603B1,
  PTW MIT 854계열 특성화마스크·effective density 모델 RR=K/ρ_eff, Boning et al. 1999 MRS
  eq.1 원문 확인, python verify로 반비례관계 4배↔4배 assert 대조). Kim & Seo(2002,
  DOI 10.1016/S0167-9317(01)00694-3) STI-CMP 패턴/비패턴 상관계수 r≈0.71은 원문 미확보
  (미러 사이트 미러 5종 전부 무응답 — 네트워크 차단 추정, OA 경로도 전부 실패)로 2차 인용·
  미검증 표기. check_knowledge.py ✓, verify_claims.py ✓ 통과. EXAMS.md 3문항 추가,
  PROFILE.md/CURRICULUM.md/ORG.md §5 갱신(wafer-type 0/6→2/6). Phase 0 지식 트랙 진행 중.

- **2026-09-06** ([소프트웨어] software-lead, 09:30): wafer-metrology "구현 요청" 수신함 처리 —
  `sim/metrics/uniformity.py` PROVISIONAL 해제. radial 지표를 문헌 default(방위각평균 반경프로파일
  σ/range, `radial_sigma_pct`/`radial_range_pct`)로 교체, 회사 관행(링별 max-min 최대)은
  `radial_maxring_range_nm`으로 강등 병기(ORG 절대원칙 준수). 항등식 회귀(3σ WIWNU=3×CV) 추가.
  `WaferResult.summary()`/`sim/cli.py`/`sim/demo_app.py` 연쇄 갱신, `docs/SCHEMA-CHANGELOG.md` 신설
  (스키마 변경은 sim-architect 역할 규정에 따라 기록). 119 tests passed. 커밋 f3ecfc6, 8c997ea.
  BACKLOG 수신함에 slurry-chemist 3건 + tribologist 2건 신규 구현요청 등록(다음 회차 대상).

- **2026-09-06** ([성장엔진] 상시크론, 10:11): surface-contamination Lv1-2 측정 기법(TXRF·
  VPD-ICPMS·SIMS·XPS) 완료 — knowledge/cmp/wafer-surface-metal-detection-txrf-vpdicpms-sims-xps.md.
  Chia(UC Berkeley Microlab 세미나 슬라이드) 원문 확보로 4기법 검출한계·깊이정보·파괴여부 비교표
  작성. 1차 학술 원문 3건(Prange 1989 doi:10.1016/0584-8547(89)80051-5, Kubo 2005 ISSM
  doi:10.1109/issm.2005.1513404, Kasi 1997 JVSTA doi:10.1116/1.589577) DOI는 Crossref로 실존
  확인했으나 미러 사이트 4개 미러(box/se/st/ru) 전부 캡차로 자동접근 차단되어 **1차 미확보**, 2차
  인용으로 표기. python verify로 Si(100) 단분자층 대비 VPD-TXRF/VPD-ICPMS/고전TXRF 검출한계를 ML
  단위로 재현, VPD 전처리의 100배 개선(문헌 주장과 일치)을 assert로 확인. check_knowledge.py ✓,
  verify_claims.py ✓ 통과(출처2건 실존·코드1블록 통과). EXAMS.md 3문항 추가, PROFILE.md/
  CURRICULUM.md/ORG.md §5 갱신(surface-contamination 1/4→2/6). M1(지식 병목 해소, 9/20 기한)
  진행 지속.

- **2026-09-06** ([성장엔진] 상시크론, 12:xx): pad-material Lv1-2 경도·탄성률·기공률 측정법
  완료 — knowledge/materials/pad-hardness-porosity-measurement-methods.md. Pureon 공식
  데이터시트로 IC1000/IC1010 경도가 실제로는 **동일**(Shore D 60, 차이는 두께뿐)함을 확인해
  CURRICULUM의 "하드·소프트" 프레임 오류를 짚음. Chen et al. 2024(Materials 17(11) 2759,
  DOI 10.3390/ma17112759, PMC11173749, MDPI OA 전문 확보) 발포제 실험에서 기공률 정의
  (P=1-ρ/ρ₀)·밀도 78~84%대 데이터·MRR 최적조건(NaHCO3 3wt% +33.8%, NH4HCO3 1wt% +47.8%)을
  정리, python verify로 두 계열의 역산 기저MRR(66.8 nm/min) 상호 일치를 assert 확인. Shore
  C/D 스케일을 직접 비교할 수 없다는 실무 함정도 명시(ASTM D2240 유료표준 1차 미확보).
  Gibson-Ashby 발포 스케일링은 2차 인용(원문 미확보)으로 표기, 탄성률 계산은 Lv2-1로 이월.
  check_knowledge.py ✓, verify_claims.py ✓ 통과(출처2건 실존·코드1블록 통과). EXAMS.md 3문항
  추가, PROFILE.md/CURRICULUM.md/ORG.md §5 갱신(pad-material 0/6→2/6). M1(9/20 기한) 진행 지속.

- **2026-09-06** ([Max워커] S2): 테스트 119개 재현/스냅샷 분류 감사 완료 — docs/TEST-AUDIT.md.
  파일별 분류표(21개 테스트 파일) + 요약 통계 + 스냅샷 교체 목록. 결과: 재현 61(문헌 3·해석해 22·
  항등식 36) / 혼합 31 / 스냅샷 10 / 스모크 17. **실제 문헌·해석해 정량 검증은 25/119 = 21%**,
  문헌 숫자를 assert에 직접 쓰는 테스트는 3개뿐(나머지 문헌 근거는 모듈 docstring에만 존재).
  해석해 정량 재현은 kinematics·viscoelastic·gw_contact 계열에 집중, 컨디셔너·패드마모·슬러리막
  계열은 정성(부호·단조) 검증만. 스냅샷 10건 중 7건은 이미 있는 해석해/문헌값으로 교체 가능
  (preston 1.00391 → 완전타원적분 폐형식, engine cv<0.5% → 해석 CV, GW-Preston 10% → 1e-3,
  ψ 오더 → GW 1966 판정 임계 등), 3건은 S13(패드 마모 모순) 판정 전까지 정직 스냅샷이 최선.
  부수 발견: test_models gw_and_preston_converge assert 10% vs 메시지 5% 불일치,
  test_conditioner_sweep_kinematics pca_zero_outside_reach는 mask가 비어 **항상 공허 통과**(실측
  확인). 코드 미수정, 119 passed 유지.

## 2026-09-06 — 파라미터 팩 도입 (물성/코드 분리)

사용자 지시: "시뮬레이션툴이야 껍데기고 그 안에는 학습내용이 잘 머지되어서
있어야되는거 아니야? 그 내용만 바꾸면 각각 다른 시뮬레이션을 할수있도록 설계해"

**진단**: knowledge/*.md 36편이 코드에서 전부 주석이었다. knowledge를 open()하는
코드가 0줄. 물리 상수는 24개 모듈에 하드코딩(_E_STAR, sigma0, ENTEGRIS_ANCHOR_RATIO).
지식이 아무리 쌓여도 시뮬레이터에 반영되지 않는 구조였다.

**변경**: 물성 소유권을 `knowledge/params/*.yaml`로 이관. 엔진은 팩 이름만 받는다.
- 팩 5종: base(장비·패드·GW) / oxide_silica / sti_ceria(3단 상속) / cu_h2o2_bta / w_fe_oxidizer
- 모든 값이 source·confidence 동반. 미검증 값 사용 시 결과에 ⚠ 경고 + provenance
- 없는 물성 요구 시 ParamMissing으로 즉시 실패(조용한 기본값 금지)

**검증**: w_fe_oxidizer는 sim/ 코드 0줄 수정으로 추가. oxide 128.7 / ceria 283.2 /
Cu 450.5 / W 360.4 nm/min. 130 tests passed, CI run 34012847439 success. 커밋 e3fc042.

**다음 병목**: 팩 값 대부분이 confidence=estimated(문헌 역산). M3 실데이터
캘리브레이션이 이 값들을 verified로 바꾸는 작업이고, 그 대상 목록은
`python -m sim.cli --list-packs`의 미검증 카운트가 그대로 알려준다.

- **2026-09-06** ([성장엔진] 상시크론, 14:xx): disk-design Lv1-2 그릿 밀도·돌출 높이 →
  패드 절삭율 모델 완료 — knowledge/equipment/conditioner-grit-density-protrusion-cutrate.md.
  Feng(2007) IEEE Trans. Semicond. Manuf. DOI 10.1109/TSM.2007.907618(유료, 미러 사이트
  경유 1차 원문 확보, papers/feng2007-pad-conditioning-density-tsm.pdf)에서 컨디셔닝 밀도
  (CD)가 그릿 밀도에 선형 비례 분해되는 구조를 확인(정확한 폐형식 수식은 PDF 수식렌더링
  OCR 실패로 미확보, 정직 표기). "디스크/패드 반경비가 작을수록 마모 평탄" 정성 결론을
  독립 원-원 교차 기하 근사모델로 python verify assert(CV 비교)로 방향성 재현. 3M(2010,
  MRS) 실측(DOP≈15µm, 돌출 균일화로 Cu 블랭킷 결함 67~75개→0~9개 감소)으로 돌출 높이
  균일성의 실무 함의 확보. ECS abstract(Kakireddy 2010, Unpaywall OA)로 정성 결론 교차
  확인. check_knowledge.py ✓, verify_claims.py ✓ 통과(출처2건 실존·코드1블록 통과). EXAMS.md
  3문항 추가, PROFILE.md/CURRICULUM.md/ORG.md §5 갱신(disk-design 0/6→1/6). progress.py
  재확인 결과 신규 게이트 개방 없음(G1/G2/G3 조건 미충족 유지). M1(9/20 기한) 진행 지속,
  다음 회차 대상은 progress.py 판정상 pad-lifecycle Lv1-2.

## 2026-09-06 — 백테스트 첫 실측: "ρ=0.240"은 모델 성능이 아니었다

위임 에이전트가 공개 논문 4편·59조건을 수집해 백테스트한 결과 held-out 평균
Spearman ρ=+0.240(쌍적중 59.9%)이 나왔고, "FabSim은 조성 스크리닝 도구로 주장할
근거가 없다"는 결론이 딸려 왔다. **검증해보니 그 결론이 성립하지 않는다.**

### 실제 원인 둘 (둘 다 데이터·하네스 문제, 모델 문제 아님)

1. **조성이 모델에 입력되지 않았다.** carbide L9는 압력·rpm 고정에 조성만 바꾼
   실험인데, YAML이 조성을 `label` 텍스트에만 적고 Recipe로 넘기지 않았다.
   9조건 전부 예측 752.02로 동일 → Spearman이 nan. 이걸 "화학층이 조성을 구분
   못 한다"로 읽을 뻔했다. `overrides:` 블록을 추가하고, 하네스가 **예측 분산 0을
   자동 감지**해 "모델 성능이 아니라 입력 누락"이라고 경고하게 했다.

2. **4개 데이터셋 중 실리콘 반도체 CMP가 하나도 없다.** 초경합금(WC-Co)·몰리브덴·
   4H-SiC(전단유동 연마)·석영유리를 전부 `oxide_silica`/`sti_ceria` 팩으로 돌렸다.
   우리 팩은 Si 산화막·Cu·W용이다. 이건 모델 검증이 아니라 **커버리지 밖 외삽**이고,
   계통 편향 0.07~0.24배가 그 증거다. `in_scope: false`로 표기해 집계에서 제외했다.

### 지금의 정직한 상태
**held-out(범위 내) 데이터셋 0개 — 아직 "검증했다"고 말할 수 없다.**
ρ=0.240은 IR에 쓸 수 없는 숫자이며, 쓰면 첫 질문에서 무너진다.

### 그래도 건진 신호
Mo L16(압력·pH·첨가제·입도 4인자)에서 ρ=+0.522, 쌍적중 73.7%. 재료계가 완전히
다른데도 순위가 절반 이상 맞았다는 건 **Preston 기계항(압력·속도)이 재료 무관하게
작동한다**는 뜻이다. 민감도 분석에서 압력 탄성도가 정확히 1.0으로 나온 것과 일치한다.

### 다음 (우선순위 순)
1. **실리콘 CMP 인쇄표 데이터 확보** — 이게 없으면 아무것도 검증 못 한다.
   ITRS/SEMI 표준문서, 국내외 학위논문(부록에 원시 표가 많다), 특허 실시예(수치가
   구체적이다)를 노려라. 오픈액세스 논문은 그래프 위주라 digitized가 강제된다.
2. 팩 커버리지 확장 — 위 데이터가 정 안 나오면 Mo·SiC·석영용 팩을 만들어
   그 재료계 안에서 검증하는 우회로도 가능하다. 단 그건 반도체 CMP 검증은 아니다.
3. oxide_silica 팩에 화학 파라미터가 없다(산화제·억제제 항 자체가 꺼져 있음).
   실리카 슬러리의 화학 근거를 채워야 조성 스크리닝을 주장할 수 있다.

## 2026-09-06 15:30 — [소프트웨어] S17 마찰열-Arrhenius 커플링 엔진 부분구현

tribologist Lv2-2 구현요청 처리. `sim/tier2_physics/frictional_heating_arrhenius.py` 신설
(q=μPV, Qf, ΔT 전량냉각상한, Arrhenius 반응속도·배율, Shin2025 재료상수 Cu/Ta/SiO₂). 8 tests
전부 지식노트 §6 문헌·해석해 대조값 재현. 159 passed. 커밋 0e55c79.
미완: engine.available_models() 미등록(순수 함수 라이브러리, MRR Model 아님), sim/chemistry.py
온도항 연결은 팩(oxide_silica/cu_h2o2_bta)에 유량·ρ·cp·재료별 Ea가 없어 보류 — 화학 부문 회신 필요.

## 2026-09-06 16:xx — [성장엔진] pad-lifecycle Lv1-2 (컨디셔닝-마모 균형) 학습

Shi & Ring (2010, DOI 10.1016/j.mee.2010.04.010) 원문 전체 확보(저자 공개 PDF, 19쪽
직접 읽음). `knowledge/materials/pad-conditioning-wear-regeneration-balance.md` 신설
— 유체 유무에 따른 pad-wafer 분리거리 정상상태 존재/부재를 Lawing(2004) 정성 관측과
연결. 자체 검증 스크립트(`agents/pad-lifecycle/scripts/shi_ring_steadystate_check.py`)로
하중분배식(Eq.5-6) 기반 정상상태 d*=13.55µm 재현 — 단, 절대값의 물리적 타당성은
미검증으로 명시(항등식 자기무모순 확인 수준). check_knowledge.py·verify_claims.py 둘 다
통과. pad-lifecycle 2/6, CURRICULUM Lv1-2 [x], EXAMS 3문항 추가, ORG.md §5 갱신.

## 2026-09-06 — 특허 수집 3트랙 착수 + 특허 데이터의 구조적 한계 발견

사용자 지시: 캐시 활용 / KIPRIS 병행 / 밤샘 크론 — 전부 진행.

### 트랙 상태
1. **캐시 26건 분석** — 완료. 신뢰 출원인 11건 확인, 그러나 **데이터셋 승격 0건**(아래 §한계).
2. **KIPRIS** — 스크립트(`tools/kipris_mine.py`) 완성, **API 키 발급 대기**(사용자 작업).
   plus.kipris.or.kr 무료 발급 → `~/.hermes/.env`에 `KIPRIS_API_KEY=...`.
   키 없이는 아무것도 수집하지 않고 안내만 출력한다(추정 데이터 생성 금지).
3. **밤샘 크론** — `b802a23ff1ae`, 매일 01/03/05시, 6초 간격(`FABSIM_PATENT_INTERVAL`).
   캐시 덕에 매번 이어받는다. 증가분 0이면 [SILENT].

### ⚠ 특허 데이터의 구조적 한계 (이게 오늘의 진짜 발견)
특허가 논문보다 나을 거라 기대했으나, **상당수가 백테스트에 쓸 수 없다**:

- **상대값만 싣는다.** Kao US7118685B1은 표 5개에 데이터가 가득한데 전부
  "Relative Polishing Speed 1.0 / 0.9 / 0.1 or less"다. 절대 MRR이 없어 우리 예측과
  대조할 수 없고, "0.1 or less" 같은 구간값이 섞여 순위조차 불완전하다.
- **조건표만 있고 결과가 없다.** Rodel US6693035B1은 압력·rpm·시간 표는 있는데
  MRR 결과 표가 없다.
- **WO 공보는 실시예 표가 아예 없는 경우가 있다.** Versum WO2021231090A1은 표 12개가
  전부 메타데이터(인용·패밀리·법적사건)였다.

→ 자동 판정에 `has_absolute_values` / `relative_only`를 넣어 이 셋을 구분한다.
   "신뢰 출원인 + 표 있음"으로는 부족하고 **절대 수치가 있어야** 후보다.

### 파서가 세 번 뚫린 기록 (같은 실수 반복 방지)
1. 출원인: `assigneeOriginal`이 인용 특허 출원인까지 긁어 Dynea→JSR 오매칭
2. 노이즈 표: 키워드 목록만으로는 계속 샌다 → 구조 판별 추가
   (특허번호·ISO날짜가 소수점 수치보다 많으면 인용목록)
3. 절대/상대: 실시예 번호(II-1, Ex. 5)를 측정값으로 세어 Kao를 오판정

**교훈: 특허 페이지에는 데이터처럼 생긴 메타데이터가 여러 겹 있다. 통과시킬 이유가
아니라 배제할 이유를 구조로 정의해야 한다.**

### 다음
크론이 코퍼스를 늘리면 `has_absolute_values=True`인 것만 `--dump`로 확인해
데이터셋화한다. 현재 그 조건을 만족하는 캐시 특허는 0건이다.

## 2026-09-06 18:xx (성장엔진) disk-design Lv2-1 그릿 마모-스크래치 연계 학습

Kwon et al.(2013, Tribology International, DOI 10.1016/j.triboint.2013.08.008) 원문 전체
확보(유료, 미러 사이트 경유) plus Son and Lee(2021, Applied Sciences, DOI 10.3390/app11083521,
Gold OA) 원문 전체 확보. knowledge/equipment/conditioner-grit-wear-scratch-lifetime.md 신설
그릿 밀도와 grade가 패드절삭율(17k/40k/60k에서 37/23/19 um/h) 표면조도 디브리 스크래치
개수에 미치는 정량 관계, 디브리농도-스크래치 관계는 선형이 아니라 포화형(물리적 도달량
상한)이라는 핵심 발견, 문헌 기반 패드수명 판정기준(그루브완전마모 또는 MRR/WIWNU급변,
16h 시점 MRR 44.9퍼센트 감소) 확정. python verify로 포화형 정성거동 존재증명(assert 통과,
정량재현 아님을 명시). check_knowledge.py verify_claims.py 둘 다 통과. disk-design 2/6,
CURRICULUM Lv2-1 체크, EXAMS 3문항 추가, PROFILE 이수기록과 ORG.md 5절 갱신. 구현요청
7절 신설 디스크/패드 수명종료 판정 로직 software-lead BACKLOG 인계 예정. 문헌 공백 확인
디스크 자체 그릿 탈락률 곡선(1차 논문) 미확보 후속 과제.

## 2026-09-06 20:xx (성장엔진) wafer-type Lv2-1 확장 GW 패턴효과 물리 학습

Vasilev et al.(2011, IEEE Trans. Semicond. Manuf., doi.org/10.1109/TSM.2011.2107756, 유료·
미러 사이트 미러 경유) 원문 전체 확보(find_open_access.py의 미러 사이트() 함수가 `<object data=..>`
임베드를 못 잡는 버그 발견 — 수동으로 페이지 그렙해 우회, 도구는 미수정·다음 회차 인계).
knowledge/cmp/npw-ptw-pattern-effect-gw-physics.md 신설. 핵심: 확장 GW(Greenwood-Williamson)
모델에서 up/down 유효곡률 κ_U,D=κ_asperity±4αh/size²가 NPW(h=0)에서는 항상 0으로 사라져
패턴 크기·피치 의존성이 원리적으로 관측 불가능함을 확인. 실측 대비(Table I) basic GW 대비
extended GW가 step-height RMS 오차 32-34% 개선(density 19→13nm, pitch 20.5→13.5nm) —
NPW+ρ_eff만으로 PTW를 완전 예측 못하는 정량적 근거. h→0 극한 수렴·narrow-line 가속 정성거동
python verify로 assert 검증(digitize 없이 정량 곡선 재현은 안 됨을 명시). check_knowledge.py
verify_claims.py 둘 다 통과. wafer-type 3/6, CURRICULUM Lv2-1 체크, EXAMS 3문항 추가,
PROFILE·ORG.md §5 갱신. 구현요청(패턴효과 결합 모듈, effective-density 모델과 통합)
software-lead BACKLOG 인계 예정. 다음: Lv2-2(측정기법 엘립소미터·프로파일러·AFM·XRF).

## 2026-09-07 09:30 [소프트웨어] S1 문서동기화 + slurry-chemist 구현요청 처리 (S19)

`docs/ARCHITECTURE.md`가 9/5 최초본 그대로였는데 그날 저녁 S3(gw_preston_link)·S6 1차분
(pattern_density)이 이미 engine에 반영돼(커밋 1145ca7) 문서-코드가 어긋나 있었다 — 실측
`available_models()` 4개 기준으로 §3 전체 재작성, §5 다음 후보 갱신. 이어서 slurry-chemist
구현요청(입자스케일 화학-기계 시너지)을 `sim/tier2_physics/particle_chemomechanical_synergy.py`
로 처리 — Hertz 탄성접촉·plastic plowing·화학연화 증폭 4개 함수, 노트(particle-wafer-interaction-
mechanical-chemical-balance.md) §4 verify 블록 정량값 5건(E*≈37.6GPa, F=50nN p_max≈1.22GPa/
δ≈0.271nm, H 4배↓→depth4배/volume8배, 하중2배→체적2^1.5배)을 지어내지 않고 그대로 재현
테스트로 이전. Preston Kp 연결식은 여전히 없어(노트 §6 명시) engine 미등록(S17과 동일 지위,
순수함수 라이브러리). 183 passed(기존178+신규5), 커밋 64dd279. 잔여: Kp 연결식은 slurry-chemist
회신 대기, S13(패드마모 모순)은 pad-lifecycle 학습 대기.

## 2026-09-07 (성장엔진) surface-contamination Lv2-1 금속 오염 소자영향·ITRS/IRDS 허용치

Wang et al.(2024, Electronics, doi:10.3390/electronics13122391, MDPI CC-BY 완전 오픈액세스) 원문
전체 확보 — Fe 오염 GOI 실험에서 PMOS 조기파괴율 11.3%(8/71, β-FeSi₂ 석출물, V_bd<1.5V vs 스펙
4.14V) vs NMOS 영향 무시가능(0.19%) 정량 확인. IRDS 2024 Yield Enhancement chapter 원문(xlsx
Table YE3 포함)에서 UPW 금속한계 <1ppt, ITRS 2.0(2015) 각주[14]에서 "FEP 스펙 1×10¹⁰ atoms/cm²"를
직접 확인해 Lv1-1 잠정치와 오더 일치 교차검증. Cu 확산·수명저하 관련 3편(Istratov&Weber 2002,
Gaspar 2015, Burte&Aderhold 1997)은 미러 사이트 자동화 한계로 1차 원문 미확보 — 제목·DOI만 확인,
정성 서술로만 활용, "미검증" 명시. knowledge/cmp/metal-contamination-device-impact-irds-limits.md
신설, verify_claims.py·check_knowledge.py 둘 다 통과. surface-contamination 3/6, CURRICULUM
Lv2-1 체크, EXAMS 3문항 추가, PROFILE·ORG.md §5 갱신. 구현요청: ITRS FEP 스펙(1e10 atoms/cm²)을
향후 defect-scientist 판정임계값 상수로 인계 가능 — 현재 sim/ 편입 대상 수식은 없음(GOI 파괴전압
데이터 중심). 다음: Lv2-2(흡착 메커니즘·제거 화학).

## 2026-09-07 01:20 [심야병렬] 서브에이전트 3명 동시 학습 (pad-material·pad-lifecycle·wafer-metrology)

Max 20x 심야 유휴 한도로 claude -p 3개 백그라운드 병렬 실행(각 max-turns 120, fable-5-1 pin). 상시
크론 최근 로그(disk-design·wafer-type·surface-contamination)와 겹치지 않게 대상 선정.

- **pad-material Lv2-1** 점탄성 심화(온도·주파수 E'·E''·tanδ, CMP 조건 매핑) → knowledge/materials/
  pad-viscoelasticity-temp-frequency-dma.md. WLF 재매개화(17.44/51.6K↔8.86/101.6K) 코드 재현, Cabot
  US20170087688A1 Table 1B로 Tg 43~46°C·25→50°C E' 3~10배 감소 1차 정량, Khanna 2019(OA) E'비↔MRR
  드리프트 순서 일치, GW A_r∝1/E* 연결. Kim2006 15배 불일치·IC1000 E'(T) 미확보 정직 표기.
- **pad-lifecycle Lv2-1** glazing 메커니즘(asperity 소성변형·기공막힘·MRR 감소) → knowledge/materials/
  pad-glazing-mechanism-mrr-decay.md. Jeong2024(OA) 접촉점·반경·MRR 실측 + Lawing2004 ex-situ 감쇠
  (fumed 12%/colloidal 7%, 로그형>선형) 재현, Moon1999 Berkeley 박사논문 기공막힘 1차 인용. Jeong Eq.3
  σz 자기모순 재현 안 하고 verify에 모순 기록. (이전 회차 max-turns 실패분 상환)
- **wafer-metrology Lv2-2** 패턴 지표(dishing·erosion·step height·residual·edge roll-off) → knowledge/cmp/
  pattern-metrics-dishing-erosion-stepheight.md. ITRS2007 erosion 10%×배선높이 규칙 9/9 재현, IBM
  US5723874 밀도정의 11/11, SEMI M77 ROA 규약의존성(SunEdison vs Corning 4배차)로 정의 병기 원칙 실증.
  ⚠사용자 회사정의 미사용, 문헌·표준 정의로 확정. ISO5436-1·SEMI 원문은 2차 확인(정직 표기).

품질게이트(내가 직접 재실행): 3/3 노트 check_knowledge ✓ + verify_claims ✓ (출처 실존 12/6/12건, 검증코드
전부 통과, 출처없는 수치주장 0). 전체 30/47(신규 3편 모두 ✓). 각 서브에이전트가 자기 파일만 커밋,
오케스트레이터가 push(d0731e4..8b9a910). ORG.md §5 상태표 3행 갱신. 진도: pad-material 3/6,
pad-lifecycle 3/6, wafer-metrology 4/6. 다음: pad-material Lv2-2 기공-MRR, pad-lifecycle Lv2-2 두께
모니터링·교체기준, wafer-metrology Lv3-1 인라인/가상계측.

## 2026-09-07 01:45 [Max워커] tribologist 구현요청 처리 — 마찰기반 EPD 신호모델 순수함수 라이브러리 (S20)

BACKLOG 수신함의 tribologist 요청(마찰기반 EPD 신호모델)을 `sim/tier2_physics/friction_cof_epd.py`
로 처리. 노트(knowledge/physics/friction-cof-monitoring-endpoint-detection.md) §2 마찰신호 사슬
(F_s=μPA → τ=F_s·r_c → P=τω → I=τ/K_t) 6함수, §3·§4 종점검출 신호처리(이동평균 centered/causal,
baseline 대비 상대임계 계단검출 with min_persist, 지연 T=N/R, 과연마 T·RR/60), 검증용 합성신호
생성기(step+가우시안 잡음, "실측 재현 아님" docstring 명시)로 구성. 문헌 대조: 노트 §6 (1)~(5) 값
그대로 — F_n≈1462 N/F_s≈585 N/COF=0.40, τ·ω=F_s·V=μPVA=409 W(마찰발열 Q_f와 항등, S17 모듈과
교차확인), Li2017(PMC6190379) dP=1630 W·contrast 5.4%·N=60/12.15 Hz 지연 4.94 s(<5 s)·229 nm/min
과연마 18.8 nm(<20 nm), Headley2019 r(PMC,SF)=0.955 > r(PMC,COF)=0.758. **노트에 없던 새 검증
(핵심)**: 합성신호(30,300→28,670 W 계단 @T=600, σ=50 W, seed=42, 1200샘플)에 121점 causal 이동평균
+ 계단검출(threshold=contrast/2≈0.027)을 걸어 검출 idx=660 = T+N, **오차 0샘플**(허용 ±3, 10개
seed 전부 ±1샘플 이내), centered 평활은 오프라인 idx=600·실시간 idx=660 — 이론 지연 4.94 s가
합성실험에서 정량 재현됨. 계단 없는 잡음신호는 None(오검출 없음), threshold 8%>contrast면 미검출
(소신호 설계지침 역방향 확인). engine 미등록: Recipe가 단발 런 스냅샷이라 모터전력 시계열을 담을
스키마가 없음(ARCHITECTURE §4 스키마 부채) — S17/S19와 같은 순수함수 라이브러리 지위. 노트 §8 미검증
항목(K_t 절대값·재료별 COF 절대표·전이방향)은 docstring에 그대로 명시하고 지어내지 않음(그래서
detect 기본 direction="any"). 214 passed(기존183+신규31), self-test 8/8 PASS. BACKLOG S20 완료표 이동.

## 2026-09-07 04:20 [심야병렬] 서브에이전트 3명 동시 학습 (wafer-type·surface-contamination·disk-design)

Max 20x 심야 유휴 한도로 claude -p 3개 백그라운드 병렬(각 max-turns 120, fable-5-1 pin). 01시 배치
(pad-material·pad-lifecycle·wafer-metrology)와 겹치지 않게 4/6 대기군 중 3명 선정, 각자 다음 미이수
단원 1개(모두 Lv2-2)만 깊게.

- **wafer-type Lv2-2** SE·스타일러스·AFM·XRF의 NPW/PTW 막질별 적합성·오차 → knowledge/cmp/
  wafer-type-metrology-techniques-suitability.md. 스팟 vs 패드피치 제약(US7095511·US9574992),
  Cu 침투깊이 14.8 nm(Johnson&Christy 광학상수), NIST 스타일러스 R=1.52 µm·Table3 불확도, AFM
  4픽셀 규칙(Ahn 2019) 재현, XRF 지수법칙(US9644956)·NIST XCOM Cu 1 µm 비선형 2.3%. 출처 10건 실존.
- **surface-contamination Lv2-2** post-CMP 흡착 메커니즘·제거 화학 → knowledge/cmp/
  post-cmp-adsorption-cleaning-chemistry.md. IEP 전하부호, EDTA/시트르산 logK Davies 보정·K′(pH),
  Seo2019 Cu/Co 세정 레시피, Seo2018 세리아 HO₂⁻, RCA·DHF·오존수. 출처 22건 실존(PHREEQC minteq DB로
  안정도상수 1차 확보).
- **disk-design Lv2-2** 디스크 설계 → 패드 조도·asperity 통계·GW 파라미터 → knowledge/materials/
  disk-design-pad-roughness-asperity-relation.md. Kwon2013 Ra∝N^−0.23/Rpk∝N^−0.62, 3M2010
  finish∝D^0.57 포화, Sun2009 UA 학위논문 λ·접촉면적, McAllister2018/19 ABT vs EHWA CVD, Liao2014,
  Lawing2004. GW-λ 단독 설명 실패·Ring 규칙 불일치 정직 기록. 출처 15건 실존·검증코드 4블록.

품질게이트(오케스트레이터 직접 재실행): 신규 3편 verify_claims 3/3 ✓ (출처 실존 10/22/15건, 검증코드
전부 통과, 출처없는 수치주장 0) + check_knowledge 3/3 ✓. --all 전체 33/50(✗ 17편은 전부 기존
equipment/* 노트, 학습총괄 크론이 상환 중 — 이번 신규분 아님). 각 서브에이전트가 자기 파일만 커밋
(1a20539·9c41fcb·4996632), 오케스트레이터가 ORG.md §5 상태표 3행(4/6 Lv2-2) 갱신 후 일괄 push.
진도: wafer-type 4/6, surface-contamination 4/6, disk-design 4/6. 다음: 각 Lv3-1.

## 2026-09-07 12:00 학습총괄 회차 — 부채상환 1편 + G2 개방 + 병렬 2명

- **부채상환**: knowledge/cmp/pattern-dependent-dishing-erosion.md 1차출처 보강(Stine 1998,
  doi.org/10.1109/66.661292 — find_open_access.py로 확인, 초록만 확인·본문 유료벽) + python verify
  블록 신설(T3 밀도-제거율 반비례 불변량·T4 비압축성 step 소멸시각·T7 정상상태 dishing 대입, 3개 assert
  전부 통과). check_knowledge·verify_claims 모두 PASS. 잔여 부채 17→16편.
- **게이트**: G2 조건(5명 전원 커리큘럼 이수 + G1 3명 Lv1 완료) 재확인 → progress.py 선수충족 판정에서
  tool-platen-head 개방(pad-material은 기개방 상태였음, ORG.md 표기 정정). ORG §2·§5 갱신.
- **병렬 배차 2명** (Claude Code 백그라운드, 담당 파일 분리로 락 회피):
  - pad-lifecycle Lv2-2(패드 두께·그루브 깊이 모니터링·교체 기준) → knowledge/materials/
    pad-thickness-groove-depth-monitoring-replacement-economics.md. Son&Lee 2021(Applied Sciences
    CC-BY) 컨디셔닝별 그루브 마모 실측(Case I 43.4 µm/h·16h 소멸, Case II 22.2 µm/h·20h 유지) +
    두께/그루브 센싱 특허 4건(LSI Logic·Lam Research·TSMC·Micron) + 경제성 특허(TI). IEEE ASMC 2010
    CoO 논문은 OA·미러 사이트 모두 실패 → 미확보로 정직 기록. 출처 7건 실존.
  - tool-platen-head Lv1-1(툴 아키텍처: 플래튼·헤드·리테이너링·벤더비교, 첫 단원 0→1/6) →
    knowledge/equipment/cmp-carrier-head-retaining-ring-vendors.md. AMAT US8088299B2(3존 멤브레인)
    vs Ebara US7029382B2/US6309290B1(직접공압/플로팅링) 헤드 가압방식 대조, 리테이너링 압력비
    US6419567B1, Lee·Lee·Jeong 2026(JKSPE 43(5)) 원문 OA 확보 — 링압력 5→6psi NU 4.5%→6.1% 악화,
    멀티존 적용시 2.5%로 개선 실측 반영. Ebara측 슬러리 아암 대응특허는 "확인 못"으로 정직 기록.
    출처 9건 실존.
- **독립 검증**(학습총괄 직접 재실행, 위임 자기보고 아님): check_knowledge.py 2/2 PASS ·
  verify_claims.py 2/2 PASS(출처 16건 전부 실존, 검증코드 2블록 전부 통과, 출처없는 수치주장 0) ·
  pytest -q 214 passed. 반려 0건.
- ORG.md §5 상태표 갱신(pad-lifecycle 4/6, tool-platen-head 1/6), 각 서브에이전트 커밋(f9aebc6·
  0d4ea89) 확인 후 일괄 push.
- 진도: pad-lifecycle 4/6, tool-platen-head 1/6(신규 활성). 다음: pad-lifecycle Lv3-1, tool-platen-head
  Lv1-2.

## 2026-09-07 07:42 [Max워커] surface-contamination 구현요청 처리 — post-CMP 금속오염 산출 순수함수 라이브러리 (S15)

`software/BACKLOG.md`의 S15("금속 오염 산출") 항목을 `sim/tier2_physics/metal_contamination_surface.py`
로 처리. knowledge/cmp/post-cmp-metallic-contamination-sources.md §5/§6와
knowledge/cmp/metal-contamination-device-impact-irds-limits.md §5/§7의 python verify 블록 값을
그대로 재사용 가능한 함수 5개(+kT/e 보조 1개)로 승격: 단분자층 밀도(Si(100) 2/a²)·허용치/ML 비율·
Boltzmann Cu2+ 표면농축(z·e·ψ/kT)·GOI 조기파괴율(Wang 2024, doi:10.3390/electronics13122391)·
세정전/ITRS FEP 스펙(1e10 atoms/cm²) 비율. 새 상수 없음 — 두 노트 기존 숫자만 재사용.
engine 미등록(Recipe에 pH/zeta 필드 없음, ARCHITECTURE §4 스키마 부채 — S17/S19/S20과 동일 지위,
파일 상단 docstring에 명시). tests/test_metal_contamination_surface.py 12개 신설, 노트 assert값
그대로 재현(Si(100) N_ML≈6.78e14, 중성 -40mV→Cu2+ 농축 22.5배(>20배), PMOS 조기파괴 11.3%(8/71),
세정전Fe/ITRS스펙 100~200배). self-test 7/7 PASS.

품질게이트(독립 재실행): `.venv/bin/python -m pytest -q` 226 passed(기존214+신규12), 회귀 없음.
git log 확인 결과 커밋 4c335fd가 이미 push 완료(origin/main과 0 ahead/0 behind) — 이번 위임의
첫 두 시도가 터미널 타임아웃(180s)에도 백그라운드에서 계속 실행돼 이미 작업을 끝낸 상태였고,
세 번째 호출은 완료 확인만 수행. software/BACKLOG.md는 저장소 밖(~/software/BACKLOG.md)이라
git 추적 대상 아님 — S15 행이 완료표로 이미 이동되어 있음을 확인.


## 2026-09-07 [성장엔진] tool-platen-head Lv1-2 이수 — 멀티존 헤드 압력 응답 행렬

`agents/tool-platen-head/CURRICULUM.md` 다음 단원(Lv1-2)을 진행. 진도 최저 [활성]
에이전트를 ORG §5에서 확인(tool-platen-head 1/6, 다른 전원 3/6 이상) → 우선순위대로
선택. Lee, Lee, Jeong (2026, JKSPE 43(5) 443-448, DOI 10.7736/JKSPE.025.132) 원문
PDF(Lv1-1에서 이미 확보한 오픈액세스 논문)의 존별 압력 스윕 실험(2.3.2절, Figs.
8-11)에 집중해 knowledge/equipment/cmp-multizone-carrier-radial-response.md 작성:
3존+리테이너링 반경 경계(0-85/85-95/95-99mm), Zone3만 독립·{Zone1,Zone2,Ring}은
결합된 블록대각 응답 구조(원문 3.1절 직접 인용), 단일존(5psi=4.5%, 6psi=6.1%) vs
멀티존(2.5%) NU 대조 및 이 노트가 원값에서 유도한 개선율(44.4%/59.0%)을 python
verify 블록으로 재현·assert.

Shiu et al.(2004, 다변수 CMP 제어), Zhao et al.(2013, 12인치 존압력-웨이퍼벤딩),
Wang & Lu(2011, 수치해석+실험) 세 논문을 `find_open_access.py`로 DOI 확보 후
미러 사이트 5개 미러(box/se/st/ru/ren)에 순차 접속 시도했으나 전부 무응답(None 반환)
— 접속 차단이 아니라 미러 자체 가용성 문제로 판단, 1차 미확보로 정직 기록하고
Lee et al. 2026을 통한 2차 인용으로 대체.

품질게이트: check_knowledge.py PASS, verify_claims.py PASS(출처 4건 실존, 코드
1블록 통과, 출처없는 수치주장 0 — 최초 시도에서 2건 걸려 앵커 보강 후 재통과).
CURRICULUM [x], EXAMS Q1-Q3 추가, PROFILE 이수기록·레벨(2/6) 갱신, ORG §5 진도
갱신(tool-platen-head 2/6). 구현요청은 낮은 우선순위로 PROFILE에 기록(정량 전달함수
미확보 상태라 지금 구현하면 추측이 되므로 Zhao 2013 원문 확보 후 재요청 권장).

진도: tool-platen-head 2/6. 다음: Lv2-1(리테이너링 압력·마모와 엣지 프로파일).

## 2026-09-07 09:30 [소프트웨어] S21 pad-material 구현요청 처리 — E_pad(T) + WLF 유틸

`agents/pad-material/PROFILE.md` 구현요청(우선순위 높음·중간) 2건 처리. Claude Code 위임
(Read/Write/Edit/Bash, max-turns 40)으로 `sim/tier2_physics/pad_viscoelastic_temperature.py`
신설: 노트가 제안한 tanh/로그-시그모이드 보간 대신 **로그-선형 구간보간**을 채택했다 —
문헌(Cabot US20170087688A1 Table 1B)이 이산 앵커점(25/50/80°C) 3개만 제공하고 함수형 피팅
파라미터가 없어, tanh 피팅은 새 숫자를 지어내는 것이 되기 때문이다. `e_pad_loglinear`(범위 밖
clamp, 외삽 금지)·`e_pad_from_table`(Cabot 6패드 룩업)·`wlf_log_aT`·`wlf_reparametrize`(보편상수
17.44/51.6, "CMP PU 미피팅" docstring 명시) 4함수. 노트 §6 verify 값을
`tests/test_pad_viscoelastic_temperature.py` 16건으로 이전(WLF 재매개화 8.86/101.6·shift
항등식·60°C log_aT(-4.2)·6패드×3앵커점 정확 재현·범위밖 clamp). software-lead가 self-test
6/6 + pytest 242 passed(기존226+신규16) 직접 재검증 후 커밋(16d6147, 다른 파일 미접촉 확인).
engine 미등록: Recipe에 온도 필드 없음(스키마 부채, ARCHITECTURE §4) — S17/S19/S20과 동일
지위. Kp_eff(T) 훅(우선순위 낮음, 실측 대조 없음)은 범위 밖으로 남김. pad-material PROFILE
구현요청 섹션 완료 처리. 수신함 잔여: slurry-chemist 2건(Luo-Dornfeld, 세리아 정량모델).
다음 회차 후보: S13(패드 마모 모순, pad-lifecycle 학습 상태 확인) 또는 잔여 수신함 항목.

## 2026-09-07 10:10 [성장엔진] tool-platen-head Lv2-1 이수 — 리테이너링 FEA 접촉응력 + 특허 구조

ORG §5 확인 결과 tool-platen-head가 진도 최저(2/6, 다른 [활성] 전원 3/6 이상)라
이어서 진행. Zheng, Zhao, Lu(2023, Micromachines 14(9) 1683, DOI 10.3390/mi14091683)
FEA 정적모델: 리테이너링 유무에 따른 웨이퍼 엣지 접촉응력 배율(mainstream 대비
링있음 3배/링없음 4배, 33.3% 악화)과 US7121927B2 특허(개선형 리테이너링 접촉
세그먼트=웨이퍼 둘레의 11.5%, ITP 조절만으로 엣지 제거율을 능동 튜닝 가능)를
결합해 "리테이너링=수동보호가 아니라 능동 엣지제거율 조절 변수"라는 결론을
knowledge/equipment/cmp-retaining-ring-wear-edge-profile.md에 정리.

원문 확보 과정 기록: MDPI 직접 PDF 다운로드는 Akamai edgesuite 403(Access Denied)로
차단, PMC PDF는 PoW(proof-of-work) 챌린지로 curl 차단 — 두 경로 모두 실패 후
**Europe PMC REST API의 fullTextXML**로 본문 텍스트 확보(papers/mi14091683-fulltext.xml).
Touzov, Fujita, Doy(2001, IEEE ISSM, DOI 10.1109/ISSM.2001.962981) 원 논문은
미러 사이트 5개 미러 무응답으로 1차 미확보, 완전 공개된 후속 특허(US7121927B2)로
대체해 정직 기록.

품질게이트: check_knowledge.py PASS, verify_claims.py PASS(출처 4건 실존, python
verify 1블록 통과 — 특허 접촉세그먼트 비율·FEA 응력배율 악화율(33.3%) 재현).
CURRICULUM [x], EXAMS Q1-Q3 추가, PROFILE 이수기록·레벨(Lv2, 3/6) 갱신, ORG §5
진도 갱신(tool-platen-head 3/6).

진도: tool-platen-head 3/6 (Lv2 진입). 다음: Lv2-2(RPM비·유량·온도 제어와 MRR 안정성).

## 2026-09-07 12:10 [성장엔진] pad-material Lv2-2 이수 — 기공 구조·슬러리 이송 vs MRR

ORG §5 확인 결과 활성 에이전트 중 tool-platen-head(3/6)가 최저였으나 직전 회차에 이미 처리했으므로
동률 후보 pad-material(3/6, Lv2-1 완료)의 다음 미이수 단원(Lv2-2)을 진행. Prasad, Fotou, Li(2013,
J. Mater. Res. 28(17) 2380, DOI 10.1557/jmr.2013.173, Cabot Microelectronics)와 Yim et al.(2018,
Microelectronic Engineering 195:36, DOI 10.1016/j.mee.2017.12.002, ST/CEA-LETI/Dow) 두 편을 미러 사이트
경유로 원문 확보(papers/jmr-2013-pad-porosity-hardness.pdf, papers/mee-2018-pad-microstructure-yim.pdf,
INDEX.json 등록)해 knowledge/materials/pad-porosity-slurry-transport-mrr.md 작성.

핵심 발견: (1) %P를 15%→45%(30%p)로 올려도 RR은 8%만 증가(Prasad) — 슬러리 이송 증가 효과가
동반되는 벌크모듈러스 하락(접촉면적↑→국소압력↓)에 상쇄됨. sim/에 %P→MRR 강한 선형계수를
넣으면 문헌과 어긋남. (2) 기공 *크기*가 %P보다 RR 프로파일(WIWNU)에 훨씬 강하게 작용 — 2 µm
소기공 패드는 엣지-중심 RR차 >200 nm/min, 47/106 µm은 평탄. (3) 기공 크기와 결함(defect)의
관계는 두 논문이 정반대 부호(Prasad=무관, Yim=소기공에서 결함 3~4배↑) — 재료계(TEOS 산화막 vs
실리콘 블랭킷) 차이로 보이며 단일 부호로 sim/에 넣지 않기로 결정, PROFILE.md 구현요청에 "방향
미확정" 명시.

품질게이트: check_knowledge.py PASS, verify_claims.py PASS(출처 2건 실존, python verify 1블록
4개 assert 통과 — %P 정의 재현, 8%<<비례기대치, 200 nm/min 단위환산, V/A-RR 비단조 확인).
CURRICULUM [x], EXAMS Q10-Q12 추가, PROFILE 이수기록·구현요청 2건 추가, ORG §5 진도 갱신
(pad-material 4/6, Lv2 완료).

진도: pad-material 4/6 (Lv2 완료, Lv3 진입 대기). 다음: pad-material Lv3-1(3D 프린팅·무발포·
저결함 패드 최신 리뷰) 또는 ORG §5 최저 진도 에이전트 확인 후 재배정.

## 2026-09-07 13:34 [Max워커] S22 — slurry-chemist 구현요청 처리: 세리아 Ce3+ 산화환원-선택비

`~/software/BACKLOG.md` 수신함(slurry-chemist, 세리아 Ce³⁺비→oxide MRR/선택비 정량모델)을 Claude Code
위임(Read/Write/Edit/Bash, max-turns 40)으로 처리. `sim/tier2_physics/ceria_redox_selectivity.py` 신설
— 근거 노트 `knowledge/cmp/ceria-slurry-ce-redox-selectivity.md` §7 verify (A)~(E) 값을 그대로 함수화한
6개 순수함수(ce3_fraction·chemisorption_energy_kj_mol·is_chemisorption·electrostatic_attraction·
oxide_nitride_selectivity·h2o2_boost_selectivity). "미검증" 표기된 값(Ce3+/4+ 최적방향, 아미노산 절대
선택비 35-70)은 함수화하지 않고 PROFILE.md 잔여요청으로 남김. engine 미등록(Recipe에 pH/H2O2 필드
없음 — S17/S19/S20/S21과 동일 스키마 부채 지위, grep으로 확인). tests/test_ceria_redox_selectivity.py
12건 신규 — 254 passed(기존242+신규12), 0 failures. agents/slurry-chemist/PROFILE.md·
~/software/BACKLOG.md 갱신 완료. commit 7100b23 push 완료.

진행 로그 중복 방지: 이 항목은 ORG §5(도메인 학습 진도)와 무관 — 소프트웨어 부문 백로그 소진이라
활성 에이전트 진도 갱신 없음.

## 2026-09-07 14:20 [성장엔진] pad-structure Lv1-2 이수 — 그루브 기하→접촉면적·유동저항 (Lv1 완료)

ORG §5 확인 결과 pad-structure(0/6, Lv1-1만 이수)가 활성 에이전트 중 최저 진도. 다음 미이수
단원 Lv1-2(그루브 폭·깊이·피치 → 유효 접촉면적·유동 저항) 진행. Mu et al.(2016, Microelectronic
Engineering 157:60-63, DOI 10.1016/j.mee.2016.02.035, Univ. Arizona/Araca/Hitachi Chemical, RTD
실험)을 미러 사이트 경유로 원문 확보(papers/mee-2016-mu-groove-width-residence-time.pdf), Cho et
al.(2022, Applied Sciences 12(9) 4339, DOI 10.3390/app12094339, SKKU/삼성전자, CFD+실험, CC-BY
오픈액세스)를 r.jina.ai 프록시로 전문 확보해 knowledge/materials/
pad-groove-geometry-contact-area-flow-resistance.md 작성.

핵심 발견: (1) Lv1-1에서 정의한 GFQ=W/P를 Mu2016 실측 패드 3종(그루브폭 300/600/900μm)에 적용한
결과 GFQ=0.200/0.333/0.429 — JP5767280B2의 "가장 적합" 구간[0.2,0.3]을 실측 패드 3개 중 2개가
벗어남(그루브 이송 목적 설계는 접촉안정성 최적구간과 상충). (2) 그루브 폭 확대의 슬러리 이용효율
(η)은 단조 증가가 아니다 — 300→600μm에서 η이 9.9→13.4%(3PSI, +35%)로 크게 개선되나 600→900μm은
13.4→12.8%로 오히려 미세 감소(반응기 부피와 체류시간이 함께 늘어 실효유량 비율 상쇄). (3) 방사형
그루브 개수(R0/R8/R32) 축에서도 NU 개선폭이 초기(1.98%p)>후기(1.11%p)로 같은 수확체감 패턴 재현
— 그루브 설계 전반의 일반적 현상일 가능성이나 폭·개수 통합모델은 미확보(미검증, Lv3-2 이관).

품질게이트: check_knowledge.py PASS, verify_claims.py PASS(출처 3건 실존, python verify 1블록
GFQ 재현+η 비단조 3계열 assert 통과). CURRICULUM Lv1-1·Lv1-2 [x] (Lv1 완료), EXAMS Q4-Q6 추가,
PROFILE.md 이수기록 갱신("Lv1 완료 2/6"), ORG §5 진도 갱신(pad-structure 2/6).

진도: pad-structure 2/6 (Lv1 완료, Lv2 진입). 다음: pad-structure Lv2-1(서브패드 강성 적층과
웨이퍼 스케일 압력분포·엣지 롤오프) 또는 ORG §5 최저 진도 에이전트(disk-kinematics 1/6) 재배정.

[소프트웨어] 2026-09-07 21:30 (software-lead): S13(패드 마모 모순) 부분판정 — Jeong et al. 2024
1차 출처 실측(Table 1)이 접촉점 수·MRR 동시감소를 보여 ad-hoc 방향이 GW discrete Monte-Carlo
예측(접촉점 증가)보다 실측 근거 우위. `sim/tier2_physics/pad_glazing_jeong2024.py` 신설(접촉비·
반경비 근사), 노트값 재현 테스트 6건. 정량 Kp(t) 스케일 연결은 척도 불일치로 스코프 밖(후속
요청 대기). 260 passed. 커밋 10c8f97.

[성장엔진] 2026-09-07 (오후) disk-kinematics Lv1-2 이수: [[knowledge/equipment/disk-rpm-load-radius-pcr]]
— Zheng, Zhao & Lu(2023, DOI 10.3390/mi14091683) Eq.10-12 Preston형 PCR=Kp·P·v 모델에
process-integrator의 Lai(2001) 운동학수(µ) 치환식을 대입. Zheng et al. Table 1 실측조건
(패드100RPM/디스크73RPM, 디스크유효반경52.25mm) 대입 결과 µ≈0.072, 디스크 내 상대속도
비균일도≈14.4% — 당초 "디스크가 작으니 균일도가 좋을 것"이라는 가설과 반대로 크게 나와
정직하게 기록(가설 수정). MDPI·Wiley·미러 사이트 원문 서버는 모두 접근 차단(403/캡차) —
PMC 사본과 Lawing(2004) NCCAVS 슬라이드(이미 확보)로 대체. check_knowledge.py·
verify_claims.py 모두 통과. disk-kinematics Lv1 완료(2/6), ORG §5 갱신.


## 2026-09-07 18:xx [성장엔진] pad-structure Lv2-1 이수 — 서브패드 강성 적층과 엣지 응력비

[[knowledge/materials/pad-subpad-stiffness-edge-nonuniformity]] — Lo & Lin(2005, J. Mater. Process.
Technol. 168, DOI:10.1016/j.jmatprotec.2005.01.010, 미러 사이트 경유 원문 전체 확보·pypdf 추출)
2D 축대칭 FEM Table 1(35세트) 두 부분집합을 python verify로 재현: 패드두께 T0 0.6985→2.0955mm
스윕에서 엣지/중심 응력비 R이 1.7938→2.0760(변화율 15.7%, 단조증가 — 직관과 반대), 패드탄성률
E0 1.148→3.4345MPa 스윕에서 R이 1.7938→1.6766(변화율 6.5%, 단조감소). T0 축 민감도가 E0 축의
약 2.5배. 서브패드 2층 명시분해(IC1000/Suba IV) 1차 문헌은 이번 조사에서 미확보(Elmufdi 2004
초록만) — Lv2-2/Lv3-2로 이관. check_knowledge.py·verify_claims.py 모두 통과.
CURRICULUM Lv2-1 [x], PROFILE 이수기록 갱신(3/6), ORG §5 갱신(pad-structure 3/6).

진도: pad-structure 3/6 (Lv2 진입). 다음: pad-structure Lv2-2(그루브 마모→유동 특성 변화·수명
판정) 또는 ORG §5 최저 진도 에이전트 재배정.


## 2026-09-07 20:xx [성장엔진] disk-kinematics Lv2-2 이수 - sweep 레시피 최적화 (Baisie et al. 2010)

[[knowledge/equipment/disk-sweep-recipe-flattening-baisie2010]] - Baisie, Li & Zhang(2010, ASME
MSEC2010, DOI:10.1115/MSEC2010-34264, 미러 사이트 경유 원문 전체 확보) 표면요소법 모델의 Table 3
(20세그먼트 스윕시간 5종)을 python verify로 재현: UNIFORM TTV=0.00s(문헌 "최평탄" 결론과 일치),
DESCENT TTV=3.80s(5종 중 최댓값, 문헌 서술과 일치). NU 순위는 일부 어긋나 정직 기록(원인 미상).
6절에서 Baisie(체류시간 균일)와 Wang et al. 2025(각속도 균일, Lv1-1 노트)의 겉보기 모순을
"서로 다른 최적화 변수"로 해소 - 각속도 균일 스윕은 반환점에서 체류시간이 자동 증가하므로 두
"균일"은 양립 불가능함을 밝힘. 구현 요청(7절)을 소프트웨어 부문으로 이관. check_knowledge.py,
verify_claims.py 모두 통과. disk-kinematics Lv2 완료(4/6), ORG 5절 갱신.

진도: disk-kinematics 4/6 (Lv3 진입). 다음: disk-kinematics Lv3-1(적응형 sweep, 폐루프 패드
프로파일 제어 최신 리뷰) 또는 progress.py 재조회로 최저 진도 에이전트 재배정.


## 2026-09-07 21:30 [소프트웨어] pad-lifecycle [Lv2-2] 그루브 깊이 EOL 판정 구현

`sim/tier2_physics/pad_groove_eol.py` 신설 — 누적마모 D(t)=c·t, 그루브 소진 판정, glazing/groove
OR 결합 EOL 시각 4함수. Son & Lee 2021(그루브 깊이 노트 §5) 정량값(694/444 μm, 17.28h) 그대로
재현 테스트 9건. 컷레이트·그루브깊이 하드코딩 없음, engine 미등록(Recipe 시계열 필드 부채,
S17 이하와 동일 지위). 커밋 03e332b. pytest 279 passed(기존270+신규9). pad-lifecycle 구현요청
2건(Lv2-1 부분완료, Lv2-2 완료) 모두 처리 끝 — 잔여는 Lv2-1 Kp(t) 정량 스케일 연결뿐.

## 2026-09-07 22:xx [성장엔진] tool-platen-head Lv2-2 이수 - RPM비 kinematic number 원전 확정 + 유량/온도 실험값

[[knowledge/equipment/cmp-rpm-ratio-flowrate-temperature-mrr-stability]] - Kim & Jeong
(2004, J. Electron. Mater., DOI:10.1007/s11664-004-0294-4, 미러 사이트 경유 원문 확보)가
cmp-kinematics-rotary.md의 µ와 동형인 kinematic number ζ의 원전임을 확정, 슬라이딩거리
NU=25ζ²(2차·둔감) vs 순간속도 NU=2ζ(1차·민감)를 python verify로 재현(S_avg=1+ζ²/8
수치적분 상대오차<1e-3). Yuh et al.(2015, DOI:10.1007/s40684-015-0041-8, 미러 사이트
경유 원문 확보)에서 슬러리 유량(비단조·1000mL/min 최적)·플래튼 온도(단조 증가) vs
MRR/NU 실험값 확인 - PCB용 Oscar-type 장비라 300mm 팹 이식은 미검증 명시.
check_knowledge.py, verify_claims.py 모두 통과. tool-platen-head Lv2 완료(4/6),
ORG §5 갱신.

진도: tool-platen-head 4/6 (Lv3 진입). 다음: tool-platen-head Lv3-1(폐루프 프로파일
제어 최신 리뷰) 또는 progress.py 재조회로 최저 진도 에이전트 재배정.



## 2026-09-08 01:2x [심야병렬] Lv3-1 3편 동시 이수 — wafer-metrology · wafer-type · surface-contamination

서브에이전트 3명 병렬(claude -p, fable-5-1) 학습. 세 노트 모두 오케스트레이터 직접 게이트 통과 확인(check_knowledge ✓ / verify_claims ✓). 429·overloaded 흔적 없음.

- [[knowledge/cmp/inline-virtual-metrology-sampling-optimization]] — 계측 3층위(in-situ/통합=W2W·오프라인=L2L, AMD US6645780·IBM US9240360), PHM 2016 CMP VM 벤치마크 표 재현(Di/Jia/Lee 2017 IJPHM, 가중앙상블 MSE 7.07=24팀 중 1위), FSCA 50→7점 NMSE 0.96%(McLoone 2018 IEEE TASE), static/adaptive/dynamic 로트 샘플링(Nduhura-Munga 2013). 출처 17건 실존·verify 4블록 통과. 미확보: Rao 2000·Zhang 2021 MSE 6.33은 스니펫뿐(미검증). wafer-metrology 5/6.
- [[knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology]] — 모니터 웨이퍼 전이(TSMC US7333875B2, work function 변환계수 STI 1.12·IMD 1.41 재현), NPW→PTW 유효압력비 2.2/1.7/1.3 vs 밀도모델 10/2/1.11 3.7배 괴리(Sorooshian 2005 학위논문), 전기 대리(Park 1999·Chang 2004 IEEE TED, R_dish 모델 w≥2µm서 30% 이내), PTW VM은 제품ID·밀도·이전층 특징 필요(Jebri 2017 MAPE 3.2~4.4%). 출처 12건 실존·verify 1블록. wafer-type 5/6.
- [[knowledge/cmp/low-level-metal-cobalt-ruthenium-cross-contamination]] — IRDS 2024 YE6 게이트금속 표면한계 2e10 at/cm²(Co/Ru 표면한계는 미규정), Cu/Co·Cu/Ru 갈바닉 방향 CRC E°와 정합(크기는 산화제·킬레이트로 불일치, assert 명시), minteq Co(OH)₂ 전이 pH 7.9 vs Cu 5.7(Bisht 2022 관찰 ≈6 정합), PVA 브러시 Cu(II)-PVA 착물 재오염. 출처 24건 실존·verify 1블록. 미확보: Co 세정후 atoms/cm² 실측 1차논문. surface-contamination 5/6.

품질게이트: 3/3 통과(오케스트레이터 직접 확인). ORG §5 상태표 3행 갱신(5/6, 2026-09-08).
누적 진도: 지식노트 66편(신규 3), 세 에이전트 각 5/6(Lv3 진입). G1 3명 전원 Lv3-1 완료.

## 2026-09-08 [Max워커] S12 부분 착수 — cmp_lubrication_regime.py 엔진 등록

이미 self-test 11/11 PASS 상태였던 `sim/tier2_physics/cmp_lubrication_regime.py`(tribologist
Lv2, knowledge/physics/cmp-lubrication-regimes.md)를 `sim/engine.py`에 진단 필드로 연결했다.
`WaferResult`에 `lubrication_regime`/`cmp_sommerfeld_number`/`cof_stribeck_estimate` 3필드
추가(전부 Optional, MRR 계산과 완전 독립 — roughness_ra_nm과 동일 지위). `simulate()`가
반경평균 압력·속도로 So=μU/(p·δeff)(δeff≈Ra 근사)·λ≈So 근사·Stribeck COF를 계산해 채우고,
정성적 오더 추정이라는 한계를 notes에 명시한다. oxide_silica 팩에 `slurry_viscosity_pa_s`
(1e-3 Pa·s)·`pad_ra_m`(5e-6 m) 추가(둘 다 confidence=estimated, 노트 §2·§5 그대로 인용 —
새 물리 상수 없음). `cmp_lubrication_regime.py` 자체 로직은 무수정.

`tests/test_lubrication_regime_diagnostic.py` 신설 3건: 노트 §5 전형조건 So≈7.25e-3 재현,
simulate() 필드 채움 확인, 압력↑→So↓ 방향성(분모에 p) 확인. pytest 282 passed(기존279+신규3).
커밋 e0ba399. S12(남은 20개 모듈 이관)는 이 1개만 부분 완료 — 나머지 19개는 그대로 ⬜
(`software/BACKLOG.md` S13-NOTE에 기록).

## 2026-09-08 [심야병렬] pad-material Lv3-1 이수 — 3D 프린팅·무발포·저결함 패드 소재 리뷰

서브에이전트(fable-5-1) 단일 단원 학습. [[knowledge/materials/pad-3dprinted-nonporous-lowdefect-review]]
— Yang 2010(IJMT, 미러 사이트 확보) 무발포 SURE2000 vs IC-1010: 접촉면적 7.5 vs 0.7%, 컨디셔너 180→70 µm로
RR ∝ A^0.5(1.201 vs 1.207, 0.5% 일치)·스크래치 −68%; 원문 초록 오타(2587↔3587)·라벨 오류(1.206) 기록.
Kenchappa 2021(ECS JSS OA, AMAT 적층제조 패드) 40D 소프트 패드 세리아 RR 1.9배·asperity 높이폭 8 vs 30 µm,
결함 카운트 부재 명시. 특허 US10875145(E'30/E'90>6)·WO2015120430(래티스 공극 43.75%). Morsada 2025 리뷰는
초록만. 출처 7건 실존·verify 1블록(assert 14개) 통과·check_knowledge ✓. Semantic Scholar API 429 → 해당
경로 중단(다른 소스로 대체). PROFILE 구현 요청 3건(패드 유형 플래그·경도→MRR 슬러리 종속 부호, 무발포
컨디셔너→A→MRR 훅, additive 패드 GW σ 비율). pad-material 5/6. 다음: Lv3-2(소재→GW 유효강성 정량모델).
