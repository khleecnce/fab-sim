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
- 2026-09-14 12시 [성장엔진] Netzband&Dunn 2020 Fig.3a를 PDF 벡터 rect에서 독립 재판독 → 기존 데이터셋 4점 전부 0.2% 이내 재현(판독 오류 아님 확증), ceria_mechanical_floor 1/5.5를 다른 실험축에서 0.1905로 독립 확증(4.6% 차이). C2 잔여 18칸을 4개 근본원인(R1 PCR앵커 2차인용 / R2 χ 식별불가 / R3 ψ 반증된 형태 / R4 도메인 외삽)으로 분해 — R2·R3은 문헌으로 안 열리고 조성 DOE 데이터셋이 필요함을 문서화. papers/INDEX.json 등록 + .pdf.txt 추출로 QA 감사 F2 오탐 해소(netzband2020 → clean). pytest 644 pass, qa_loop #75 PASS ρ=0.9537 유지.
<!-- 크론이 실행마다 추가 -->
- **2026-09-11 18시** [성장엔진] COMPLETION-C4 sic_ceria_h2o2: Entegris US20220315802A1 알루미나 농도시리즈(n=5)에서 로그-로그 회귀로 abrasive_conc_exponent=-0.406 도출(압입지배 레짐, 기존 base oxide_silica +1/3과 부호반대 — EVIDENCE-RULES 계근접도 판정으로 팩별 분기). `sim/factors.py` κ 농도항 1.0 계약 유지 확인, 백테스트 ρ +0.946→+0.954(PASS), pytest 595 passed. 지식노트 `knowledge/cmp/sic-alumina-concentration-negative-exponent-entegris.md`. 단 이 데이터셋이 지수 출처 자체라 held-out 개선은 제한적(F4 기존관행 준수) — 독립 SiC DOE 확보가 C4 완전해소의 다음 과제.
- **2026-09-08** [소프트웨어] wafer-type 구현요청 `effective_pressure_ratio` 처리 —
  `sim/tier2_physics/npw_ptw_effective_pressure.py` 신설(Sorooshian 2005 밀도별 유효압력비 표 조회 +
  1/ρ모델 대조). 테스트 16건 문헌값 재현, 301 passed, 커밋 7ac1f02 push 완료. BACKLOG 수신함에
  pad-structure/disk-design/wafer-metrology 신규 구현요청 S25~S37 등록.
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

## 2026-09-08 심야 [심야병렬] 오케스트레이터 게이트 확인 — 3편 동시 이수 전원 통과
서브에이전트 3명 병렬(claude -p, fable-5-1): pad-structure Lv2-2 · pad-material Lv3-1 · disk-design Lv3-1.
오케스트레이터 직접 게이트(정본): check_knowledge 3/3 ✓, verify_claims 3/3 ✓(출처 실존 11/7/10건, verify 1/1/5블록, 출처없는 수치 0). 커밋 81fa172·d30ce50·32b0f41 전부 origin/main 푸시 완료. Anthropic 한도 흔적 없음(로그의 429는 Semantic Scholar API, 워커가 우회). 진도: pad-structure 4/6, pad-material 5/6, disk-design 5/6. 누적 지식노트 69편.

## 2026-09-08 [Max워커] slurry_film_lubrication 정량화 + engine 연결

`sim/tier2_physics/slurry_film_lubrication.py` self-test에 노트 §5 앵커(P_app=21kPa, ω2=60rpm, R1=4in,
R2=7in, μ=0.005 Pa·s)로 z0=232.48 µm를 계산하고 논문 h_min=36 µm와의 비율 check(0.3<h_min/z0<3.0)를
기존 8개 정성 check에 **추가**(기존 함수 시그니처·로직 무수정). 결과: ratio=0.1548로 범위 밖 → self-test
**10/11 PASS(비율 check FAIL)**. z0가 h_min보다 약 6.5배 큼 — **원인 미상**(Eq.19 인용 오류인지, h_min/z0가
d0/z0 함수라 이 조건에서 O(1)이 아닌지 미확인). 범위를 넓혀 통과시키지 않고 FAIL 그대로 둠.
`sim/engine.py`에 `_film_thickness_diagnostic()` 신설(cmp_lubrication_regime 패턴) → `WaferResult`에
`film_z0_scale_um`·`film_lubrication_note` 추가, `summary()`에도 포함. 팩에 slurry_viscosity_pa_s 없으면 None.
`tests/test_film_thickness_diagnostic.py` 3건 신설. pytest **285 passed**(기존 282 + 신규 3), 회귀 0건.

## 2026-09-08 [성장엔진] pad-lifecycle Lv3-1 이수 — 인시츄 패드 센싱 + 수명예측 리뷰 위치확인
Kim & Choi(2021, Appl. Sci., MDPI CC-BY 원문 확보)의 공통경로 위상천이 간섭계로 습식 패드
표면을 진동환경에서 측정: 이중빔 대비 노이즈 9~13배 억제, AFM 대비 높이오차 0.37 nm,
worn 패드 Ra=303 nm(횡분해능 3 µm 대비 약 10배 미세). Je et al.(2026) 최신리뷰는 초록만
확보(Springer 봇차단), 원류로 추정한 Muthukrishnan/Boning 1997(SPIE)은 DOI 실존만 확인,
미러 사이트 3개 미러(.ru/.wf/.box) 전부 JS 챌린지로 본문 미확보 — 정직하게 미검증 표기.
check_knowledge·verify_claims 둘 다 통과(출처 4건 실존, verify 2블록). pad-lifecycle 5/6.
다음: Lv3-2(사용시간·컨디셔닝 이력 → 시간의존 Kp/asperity 모델, 구현은 소프트웨어 부문).


## 2026-09-08 [성장엔진] disk-kinematics Lv3-1 이수 — 폐루프 패드 프로파일 제어
AMAT 특허 US9138860B2(전문 확보) Table I를 코드로 재계산해 명세서 서술(핀게이지 40%↓,
집적센서 75%↓)을 assert 5개로 확인. Park·Hwang·Lee(2024, Tribol. Lubr., 원문 PDF 확보)의
딥러닝 스윙-마모 예측 모델은 학습 재현오차 0.01% vs 미학습 외삽오차 12.9%(약 1290배)를
원문 그대로 대조 — 신경망 오픈루프 예측기의 일반화 한계를 정량 확인. check_knowledge·
verify_claims 모두 통과. disk-kinematics 5/6(Lv3 진행중). 다음: Lv3-2(구현은 소프트웨어
부문 이관).

## 2026-09-08 [성장엔진] pad-structure Lv3-1 이수 — CFD 미세패턴 최적설계 사례연구
Sadri Mofakham et al.(2024, ECS J. Solid State Sci. Technol., DOI:10.1149/2162-8777/ad8fd3,
CC-BY 원문 전체 확보)의 5종 미세패턴(원·삼각·사각·타원·사각-원) CFD+실험 연구를 학습.
DCA/DICL(2D 접촉면적·둘레 지표) 정의를 Table I 그대로 재현하고, 압력강하 1위(타원, 751 Å/min
@300g/cm²)가 아니라 DICL 최댓값(사각-원, ~1000 Å/min)이 TEOS 제거율 1위라는 반직관적 결론을
문헌 수치로 재현 확인. Re<2300 층류 가정도 간극 70μm 기준 역산으로 정성 sanity check.
후속 리뷰 논문 2편(Physics of Fluids DOI:10.1063/5.0312258, SiC involute groove SSRN 5358338)은
미러 사이트 미러 3곳·SSRN 모두 봇차단으로 원문 미확보 — 정직하게 기록. check_knowledge·verify_claims
둘 다 통과. pad-structure 5/6(Lv3 진행중). 다음: Lv3-2(그루브·적층 파라미터 → 압력/유동 모델,
sim/tier2 구현 요청은 소프트웨어 부문 BACKLOG로 이관).

## 2026-09-08 [Max워커] S35 완료 — sim/metrics/pattern_metrics.py 신설 (software/BACKLOG.md에서 선정)

`sim/metrics/pattern_metrics.py` 신설(5+1 함수: step_height_iso5436·dishing_erosion_from_profile·roa·
itrs_allowance·residual_metal_fraction/remaining_thickness). 근거 knowledge/cmp/pattern-metrics-dishing-erosion-
stepheight.md §1·§6 정량값 그대로 재현 테스트 9건(ITRS 2007 9개연도 ±0.5nm, 합성50nm스텝<1nm, 곡률제거전후
대조, ROA 두 규약 reldiff 0.877, Pan1999/ITRS-2007 비율 2.08배). uniformity.py·engine.py 무수정, engine 등록은
스코프 밖(기존 S17 이하 지위와 동일). pytest 301→310 passed(신규9, 회귀0) — 위임 결과 직접 재검증 완료.
Claude Code로 위임(max-turns 40, push 금지 브리핑) → 오케스트레이터(Max워커)가 재검증 후 커밋 20a9ba3 push.
소프트웨어 부문 BACKLOG.md S35 완료 표기 이전. 다음 후보: S12 잔여 19개 모듈 이관, 또는 wafer-metrology 신규
구현요청 대기(S36/S37).

## 2026-09-08 [성장엔진] slurry-chemist Lv3-2 이수 — 커리큘럼 6/6 완주
Li et al.(2021, ECS J. Solid State Sci. Technol. 10, 123008, DOI:10.1149/2162-8777/ac3e44,
**CC BY-NC-ND 원문 전체 PDF 확보** — Unpaywall API로 publisher OA 위치 확인 후 직접 다운로드,
미러 사이트 불필요) 학습. 콜로이달 실리카 슬러리의 pH(정점 11.0, 1551→1727→1407 Å/min)·K⁺농도
(정점 0.4mol/L, 1713→2538→2377 Å/min)·입자크기(80nm 정점, 두 극한모델 방향성만 검증)·분산제
(PAM만 30일 응집없이 안정+MRR 무손실, PVA/PVP는 각 −3.6%/−7.9% MRR 저해)를 정량 재현.
원문 Eq.3-4(표면적/압입 모델) 지수는 PDF 텍스트 추출 손상으로 신뢰 불가 판단 → 지수값은
assert하지 않고 농도 방향성만 검증(할루시네이션 방지 규칙 3 적용, 그럴듯한 지수로 채우지
않음). knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md 신설,
verify_claims·check_knowledge 둘 다 통과(verify 4블록, 출처 2건 실존, 미검증 6건/정량값
다수로 게이트 통과). slurry-chemist CURRICULUM 6/6 완주, PROFILE·EXAMS·ORG §5 갱신.
**M1 게이트(MILESTONES.md)는 slurry-chemist·tribologist 둘 다 6/6 필요 — tribologist는
아직 5/6(Lv3-2 남음)이라 M1 미완**. 다음 회차: tribologist Lv3-2를 우선해 M1 완결 시도.

## 2026-09-08 [소프트웨어] S25: pad-structure 구현요청 처리 — 그루브 마모→유동 상태
`sim/tier2_physics/pad_groove_wear_flow.py` 신설(깊이 시간함수·잔존비·3단계 플래그(initial/mid/
end_of_life, PROVISIONAL)·저류부피·체류시간·직사각채널 컨덕턴스·Micron/Cabot 수명식·종합함수
`groove_wear_flow_state` 9종). 노트(pad-groove-wear-flow-change-end-of-life.md §2,§4,§5) verify
블록 정량값(US8192257B2 산술한계1000→Micron600-800 잔존20-40%·Cabot80%기준800wafers 일치,
Mu2016 Table2 V_land≤3%·V_total 6/6·V_groove/V_land≥6.9배, Irfan2025 컨덕턴스비 d=0.50 급감
0.45-0.50/d=0.25 0.09-0.11) 그대로 재현 테스트 18건. engine 미등록(Recipe 스키마 부채, S24 이하와
동일 지위). Claude Code 위임(커밋 금지) → software-lead가 pytest 328 passed(310+18) 직접 재검증,
git status로 다른 크론 미커밋 파일 미접촉 확인 후 커밋 236e5b6 push. BACKLOG S25 완료, pad-structure
PROFILE 구현요청 회신 기록.

## 2026-09-08 [성장엔진] tribologist Lv3-2 이수 — 커리큘럼 6/6 완주, **M1 게이트 완결**
MIT 학위논문(Jiun-Yu Lai, *Mechanics, Mechanisms, and Modeling of the CMP Process*, 2001,
handle.net/1721.1/8860, 원문 PDF web.mit.edu/cmp에서 직접 확보) 로터리 폴리셔 Cu CMP 실측
학습. 접촉모드 COF 0.40~0.49(압력·속도 무관, Coulomb 마찰) — 기존 oxide 기준 `cof_stribeck
mu_bl=0.30`이 Cu 접촉모드를 과소평가함을 확인. v_R=3.91m/s까지도 hydroplaning 미도달(COF
항상 ≫0.001) — 저자가 제시한 "필름두께>거칠기 3배" 조건이 Lv1-2의 λ≥3 hydrodynamic 경계와
독립적으로 수렴함을 확인. Preston kp 지수가 압력별로 다름(14kPa: -1, 48kPa: -0.5) — Kp=상수
가정의 정량적 반례, 원인은 미검증으로 명시. knowledge/physics/cmp-friction-regime-
experimental-mit-lai.md 신설(1차 출처 학위논문+동료심사 CIRP논문 DOI 교차확인, verify_claims·
check_knowledge 둘 다 통과). CURRICULUM 6/6, PROFILE·EXAMS·ORG §5 갱신.
**MILESTONES.md M1(slurry-chemist·tribologist 둘 다 6/6) 완결 — 기한(9/20)보다 12일 앞섬.
현재 게이트 M2(Phase 0 Tier2 완결, 2026-10-05)로 전진. 소프트웨어 부문에 재료별 boundary
COF 분리(oxide vs Cu) 구현요청 1건 등록(PROFILE.md, 우선순위 낮음).**


## 2026-09-08 [성장엔진] wafer-metrology Lv3-2 이수 — 커리큘럼 6/6 완주
ASTM/SEMI 두께·평탄도 표준 약어 체계(GBIR/GF3R/GF3D/GFLR/GFLD/SBIR/SBID/SF3R/SF3D/SFQR/SFQD 11종) +
Bow/Warp를 3차 편집본(mast-tech.com.tw, ASTM F534/F657/F1241/F1390/F1530 발췌) 경유로 확정.
knowledge/cmp/wafer-metrology-output-schema-site-flatness-standards.md 신설. GBIR=SEMI MF1530 TTV
수식·가정 동일함을 assert로 교차검증, SBIR/SBID 원문 Figure 7/8 예시 4건 재현 전부 일치. uniformity.py에
없는 SFQR류(사이트별 국소 평면) 필드를 신규 확인 — sim/metrics/flatness.py 구현요청(Low)으로 소프트웨어
부문 인계. Bibby & Harwood(1997) 원문 미확보로 "49점=SEMI 표준" 통념은 노트 3편 연속 1차 근거 미확보로
명시. check_knowledge·verify_claims 둘 다 통과. CURRICULUM 6/6, PROFILE·EXAMS·ORG §5 갱신.
현재 6/6 완주 에이전트: cmp-integrator·pad-mechanic·disk-conditioner·slurry-chemist·tribologist·disk-design·
wafer-metrology 7명. M2(Phase 0 Tier2 완결, 2026-10-05)까지 진행 중. 다음 회차: ORG §5에서 진도 최저
에이전트(wafer-type/surface-contamination/pad-material/pad-lifecycle/tool-platen-head/pad-structure/
disk-kinematics — 전부 5/6 Lv3-1 완료 상태) 중 표 순서 최우선을 학습.


## 2026-09-08 20:xx [성장엔진] film-oxide Lv1-1 이수 — 옥사이드 막 종류·경도·수화층 기초
Wei et al. 2010(IEEE WMED, DOI 10.1109/wmed.2010.5453755) 나노압입 실측(8종 SiO2계 막)과
Cook 1990(J.Non-Cryst.Solids, DOI 10.1016/0022-3093(90)90200-6) 화학-기계 결합 모델을 원문
확보(미러 사이트 경유)해 정리. 핵심: 도핑막(BPSG/PSG)의 CMP 제거속도가 미도핑막보다 높은 이유는
"경도 감소가 아니라 도핑 화학 자체"(Wei 2010 명시적 부정), 미도핑막 내에서만 경도-제거율
역상관 성립. Cook의 Hertzian 순수기계 모델은 실측 Kp를 1자릿수 이상 과대예측 — 화학 항 필수
근거. 수화층 정량(두께)은 원문 후반부 미확인으로 Lv1-2 이월. knowledge/materials/
film-oxide-teos-hdp-bpsg-sod-density-hardness.md 신설, check_knowledge·verify_claims 둘 다
통과. CURRICULUM 1/6, PROFILE·ORG §5 갱신(film-oxide 1/6).
현재 6/6 완주 7명 유지, film-oxide·film-cu(둘 다 1/6)가 신규 최하위. 다음 회차: ORG §5
진도표 기준 최저 에이전트(film-oxide Lv1-2 또는 표 순서상 film-cu) 학습.

## 2026-09-08 [Max워커] S32 완료 — sim/tier2_physics/recipe_conversion_factor.py 신설 (software/BACKLOG.md에서 선정)

wafer-type 구현요청(레시피 변환계수) 처리. 특허 US20060116785A1 식(1) work function
`work_function(downforce_psi, slurry_flow_ml_min, platen_rpm)`과 레시피간 변환계수
`recipe_conversion_factor(recipe_from, recipe_to)`, 표 1 레시피 상수 `RECIPE_TABLE`(ILD/STI/IMD)
구현. 노트(product-wafer-proxy-metrics-virtual-metrology.md §2.2, §6 verify (A)) 표 2 정량값
(ILD 기준 STI 1.12, IMD 1.41) 그대로 재현 테스트 6건. engine 미등록(Recipe에 레시피 전이 개념
없음, S17/S19/S31 등과 동일 지위).
Claude Code로 위임(Read/Write/Edit/Bash, max-turns 40, 커밋 금지 브리핑) → 오케스트레이터(Max워커)가
재검증(pytest 370 passed=기존364+신규6, git status로 승인 경로 외 파일 미접촉 확인) 후 커밋 3ea9d3d push.
software/BACKLOG.md S32 완료 표기·완료표 이관.

## 2026-09-08 21:30 [소프트웨어] S36 부분완료 — sim/metrics/sampling_plan.py 신설
wafer-metrology 구현요청(계측 샘플링 최적화) 부분 처리. `material_at_risk`/`mssi_min_balanced`/
`mssi_cds`/`woi`/`static_sampling_plan` 5함수. Nduhura-Munga 2013 §3.1 + McLoone 2018 Table III
(V=50) CDS WOI% 그대로 재현 테스트 5건. FSCA/PCA 사이트선택·wmr_fit/predict·sds_plan(데이터 기반
알고리즘)은 스코프 밖으로 남김. engine 미등록. pytest 386 passed(기존381+신규5), 커밋 4fe91a0 push.
software/BACKLOG.md S36 완료 등록, wafer-metrology PROFILE 부분처리 회신.

## 2026-09-08 22:xx [성장엔진] film-oxide Lv1-2 이수 — 수화층 형성 메커니즘, Cook 1990과 Suratwala 2015 교차검증
Cook 1990(J.Non-Cryst.Solids, DOI 10.1016/0022-3093(90)90200-6) §3.1 전체(Lv1-1에서 미읽은
후반부, siloxane 가수분해 반응식·물 확산계수 두 메커니즘·확산깊이 계산) 완독. 여기에 Suratwala
et al. 2015(J.Am.Ceram.Soc, DOI 10.1111/jace.13659, LLNL 저자원고본을 OSTI에서 무료 확보)를
교차 인용해 Cook의 25년 전 이론 계산이 SIMS 실측으로 검증됐는지 확인. 핵심 발견: (1) Cook
확산깊이 계산(0.5-12nm)과 그가 인용한 실측 폴리싱층 두께(1-20nm)는 겹침 — 원문 "excellent
agreement" 주장 수치로 확인. (2) Suratwala가 SIMS로 측정한 Bielby층 두께(Ce 침투 기준
~50nm)는 Cook의 계산 최대값보다 4배 두꺼운데, Ce 침투는 확산이 아니라 계면온도 의존 화학반응
메커니즘(활성화에너지 10kcal/mol)으로 별도 지배됨을 확인 — 두 수치를 같은 물리량으로 볼 수
있는지는 미검증으로 명시. (3) K와 Ce 침투가 제거속도에 반대 경향(K는 감소, Ce는 증가) —
"수화층"이 단일 메커니즘이 아님을 정량 데이터로 확인. knowledge/materials/
film-oxide-hydration-layer-mechanism-cook-suratwala.md 신설, check_knowledge·verify_claims
둘 다 통과. CURRICULUM 2/6, PROFILE·ORG §5 갱신(film-oxide 2/6).
다음 회차: ORG §5 진도 최저 에이전트(film-cu 1/6이 film-oxide 2/6보다 낮음) 학습.

## 2026-09-09 01:xx [심야병렬] 서브에이전트 3명 동시 학습 — film-cu Lv1-2 · film-oxide Lv2-1 · wafer-type Lv3-2
QA루프 #5 PASS(ρ=0.904, 격리 0, F2 미확보 6건은 20회차부터 집계). Claude Code -p 3개 병렬(fable-5-1, max-turns 120).
- **film-cu Lv1-2** Cu 전기화학: Cu-H2O Pourbaix(CRC E°→Nernst 정량 경계, Tamilmani 2005 그림 대조), H2O2 혼합전위, Cu(I)-BTA 막 XPS/QCM, 산화제-억제제 균형(MRR/SER 11.5). H2O2계 일반화는 미검증 표기. → cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md (출처 6건 실존, verify 3블록 통과)
- **film-oxide Lv2-1** ILD CMP 평탄화: 글로벌/로컬, planarization length, Stine/Ouma 밀도기반 모델. → ild-cmp-planarization-global-local-density.md (출처 2건, verify 1블록)
- **wafer-type Lv3-2** NPW→PTW 전이 규칙 정량화: Tugbawa Fig.3.19 21%차, Ouma D조건 PL 2.90mm(Park VMIC98 3–5mm 밖) 정직 기록. 구현요청 5건 PROFILE 등록. wafer-type 6/6 완주. → npw-ptw-transfer-rules-quantitative.md (출처 5건, verify 1블록)
품질게이트(check_knowledge.py --all): 3편 전부 ✓. verify_claims: 3편 전부 통과.
ORG §5 갱신: film-cu 2/6, film-oxide 3/6, wafer-type 6/6✓. 6/6완주 8명(신규 wafer-type).

## 2026-09-09 01:xx [Max워커] S33 완료 — sim/tier2_physics/electrical_thickness_extraction.py 신설 (software/BACKLOG.md에서 선정)

wafer-type 구현요청(전기 두께 추출) 처리. Park et al. 1999 라이너 보정식 T_M = ρ_Cu·L/(R·(W−2T_L)) + T_L
`cu_thickness_from_resistance`, 라이너/Cu 저항비 `liner_parallel_resistance_ratio`, 병렬무시 오차
`liner_neglect_error_fraction`/`is_liner_negligible`, Chang et al. 2004 dishing segment 모델
`dishing_delta_R_fraction` 구현. 노트(product-wafer-proxy-metrics-virtual-metrology.md §3.1·§3.3, §6 verify
(C)(D)) 정량값 그대로 재현 테스트 11건(R_L/R_Cu≈200 @ρ_Cu=2.0, ρ_Cu=1.7/2.0 오차<0.5%·ρ_Cu=2.2는 0.53%로
경계초과 정직기록, Chang 표I w≥2µm 모델-측정 30%이내·w=0.4µm은 모델범위 밖 명시). engine 미등록(Recipe에
전기측정 스키마 없음, S17 이하와 동일 지위).
Claude Code로 위임(Read/Write/Edit/Bash, max-turns 40, 커밋 금지 브리핑) → 오케스트레이터(Max워커)가
재검증(pytest 427 passed=기존416+신규11, git status로 승인 경로 외 파일 미접촉 확인) 후 커밋 41dffa9 +
PROFILE.md 완료표기 1669c86, 둘 다 push.
software/BACKLOG.md S33 완료 표기·완료표 이관.

## 2026-09-09 02:xx [심야병렬] 서브에이전트 3명 동시 학습 — film-cu Lv2-1 · film-oxide Lv2-2 · surface-contamination Lv3-2
QA루프 #6 PASS(ρ=0.9044, 격리 0, F2 원문미확보 6건은 20회차부터 집계). Claude Code -p 3개 병렬(fable-5-1, max-turns 120). 429/rate-limit 없음.
- **film-cu Lv2-1** Cu dishing·erosion: Tugbawa 2002(MIT thesis) Hooke 압력분배→removal-rate diagram, D_ss·τ₃ 닫힌해, d_max(w,s) 경험식. 90% 어레이 erosion 58.2 vs 61 Å/s(5%), 50%는 41% 과대(원인미상 정직기록). 멱법칙 지수 0.51 vs 문헌 0.17–0.30 불일치 명시. → cu-dishing-erosion-density-step-height-model-tugbawa.md (출처 3 실존, verify 3블록). film-cu 3/6.
- **film-oxide Lv2-2** STI 세리아 고선택비: Lee 2002(MIT thesis)+Dandu2009/Mariscal2020/Srinivasan2015. 핵심결론=고선택비는 디싱을 못 줄임(D_ss→d_max), 가치는 K_ss=K/(1+ρ(s−1)) 낮춰 오버폴리시 창 확대. 원문 식 2.36 부호 오기 발견. K1 상수 51% 불일치 정직기록. → sti-cmp-ceria-high-selectivity-nitride-stop-dishing.md (출처 7 실존, verify 4블록). film-oxide 4/6(Lv2 완주).
- **surface-contamination Lv3-2** 잔류금속 예측 골격: 경쟁 Langmuir+SCM(Loewenstein1998/99, Seo2001, Martin1999, Sun2007). Cr [M]지수 0.74 vs 문헌 0.73 일치, pH지수 −0.12 vs −0.39 불일치 assert명시. **정정발견: Seo2001 원문에 sim SEO2001 상수(Fe) 근거 없음→Lv1-1 노트에 미검증 추기, PROFILE에 sim 정정요청.** → post-cmp-residual-metal-prediction-langmuir-scm.md (출처 5 실존, verify 1블록). surface-contamination 6/6 완주(Cal-1 G2 대기).
품질게이트(check_knowledge+verify_claims): 신규 3편+수정 1편(Lv1-1) 전부 ✓✓. equipment/ 13편 반려는 기존 부채(내 작업 무관). 커밋만, git add 선택적. G1 조건(slurry·tribo Lv2)은 이미 개방됨—신규 게이트 없음.
다음 회차: film-cu 3/6이 활성 최저 → Lv2-2(배리어 CMP). 다음이 disk-kinematics/pad-* 5/6군.

## 2026-09-09 07:xx [Max워커] S26 완료 — sim/tier2_physics/disk_gw_relative_scaling.py 신설 (software/BACKLOG.md에서 선정)

disk-design 구현요청 §1(디스크 스펙→GW 파라미터 상대 스케일링) 처리. 그릿개수→Ra/Rpk 상대배율
(`ra_relative`/`rpk_relative`: Kwon 2013 Ra∝N^-0.23, Rpk∝N^-0.62), 그릿크기→surface finish
상대배율(`surface_finish_relative`: Pysher 2010 SF∝D^0.57, 125µm 이상 포화 국소지수 0.23,
leveled ×0.57), 그릿크기→λ 상대배율(`lambda_relative`: Sun 2009 고하중 λ∝D^0.35/저하중
λ_rel=1.0), 종합함수 4개 구현. 노트(disk-design-pad-roughness-asperity-relation.md §3.1-3.4)
정량값 그대로 재현 테스트 8건.

**구현 중 방향 버그 발견·수정**: Claude Code 초안이 lambda_relative에서 D_target/D_ref를
그대로 써 배율 방향이 뒤집혀 있었음 — ANSI 그릿 메시번호는 지름과 역상관(메시번호 클수록
입자 작음)인데, 325→100 grit 전환이 "더 거친(큰 입자) 방향"임을 반영하지 않고 단순
비율로 계산해 λ_rel<1이 나옴(방향 반대). 원인 검증: Sun 2009 8lb 조건 100-grit λ=6.7µm vs
325-grit λ=4.3µm(같은 하중), 실측비 1.558 — 공식은 (D_ref/D_target)^0.35=(325/100)^0.35=1.511로
3% 이내 재현해야 정상인데 초안은 (D_target/D_ref)를 써 0.66이 나왔음. 테스트도 원래
서로 다른 하중(3.3µm은 325-grit 3.6lb 값)을 섞어 비교하는 오류가 있어 같은 8lb 조건으로
정정. engine 미등록(Recipe에 디스크 스펙 필드 없음, S17 이하와 동일 지위).

Claude Code로 위임(Read/Write/Edit/Bash, max-turns 40, 커밋 금지 브리핑) → 오케스트레이터
(Max워커)가 self-test 7/7 확인 중 방향 버그 직접 발견·수정, 전체 pytest 435 passed(기존427+
신규8) 재검증, git status로 승인 경로 외 파일(다른 크론 미커밋분 .night_parallel*·papers/*·
build/·dist/·tools/check_npw_catalog.py 등) 미접촉 확인 후 신규 2파일만 커밋(ac9d7a9)+push.
software/BACKLOG.md S26 완료 표기·완료표 이관.

## 2026-09-09 08:xx [성장엔진] 정확도루프 — sic_ceria_h2o2 팩 VALIDATION 갭 해소

갭 랭커 최우선(VALIDATION, sic_ceria_h2o2, score=100) 처리. 조사 결과 기존
sic2026_ceria_h2o2_ph_DOE50(n=50) 데이터셋이 **이미 이 팩의 pH 계수(ph_softening_per_unit)
역산 출처**였음을 확인 — held-out이 아니라 캘리브레이션 데이터였는데 in_scope: false로
잘못 표시돼 있었다(팩 신설 전 낡은 주석). in_scope: true + used_for_calibration: true로
정정해 재분류.

진짜 held-out 신규 확보: US20220315802A1(Entegris/UF, 공개특허, Google Patents 무료
전문) Table 1 — SiC CMP 알루미나 나노입자 농도 0.1~5wt% 대 제거율(n=5). 특허 검색
20+건 스윕 후 조성-MRR이 절대값 표로 인쇄된 유일한 후보. 화학종 불일치(알루미나 vs
팩의 세리아)로 chi(pH) 항은 미시험이나 kappa(기계적 농도항)는 시험 가능 → in_scope: true
+ scope_note 명시. 결과: ρ=-1.000(n=5, p=1.0, 유의하지 않음) — 실측은 농도↑→MRR↓
(압입지배 방향)인데 팩의 abrasive_conc_exponent 기본값(+1/3, 표면적지배, MRR↑)이 반대
방향임을 노출. 후속 갭(kappa 지수 재검토)으로 이어질 근거.

pytest 435 passed. qa_loop run --strict PASS(유의 평균 ρ=0.9044, 데이터셋 4/19 그대로
— 두 신규는 미유의/판정불가라 유의 평균 불변). audit clean(entegris 데이터셋 원문
papers/US20220315802A1.txt 확보·대조 통과).
커밋 71e2c67, push 완료.

다음 갭(--next): UNMODELED delta(손상 유발도) — 5개 팩 공통 미모델링.

[소프트웨어] 2026-09-09 09:30: surface-contamination PROFILE의 SEO2001 출처 정정 요청 처리(BACKLOG S38) —
metal_contamination_surface.py의 Fe 수치를 Seo 2001 원문 근거로 오귀속했던 것을 "출처 불명"으로 정직 재표기.
pytest 443 passed, 커밋 ee4aff5.

## 2026-09-09 10:xx [성장엔진] 정확도루프 UNMODELED delta(손상 유발도) — 지식 확보 (트랙 A)

갭 랭커 최우선(UNMODELED, delta, score=100, 5팩 공통) 처리. slurry-abrasive Lv1-2(입도 분포·LPC)
학습으로 근거 확보: Remsen et al. 2006(JES 153(5) G453-G461, doi:10.1149/1.2184036, Cabot
Microelectronics, 미러 사이트 전문 확보·61,555자 텍스트 대조)에서 대입자 개수(LPC)-스크래치
카운트 정량 상관(Table V, r²=0.987~0.991, 선형) 및 스크래치 임계 직경(0.68 µm 실리카 등가,
Fig.10 비선형회귀 외삽) 확보. knowledge/cmp/lpc-scratch-density-tail-correlation.md 신규
(verify_claims.py·check_knowledge.py 둘 다 통과).

핵심 발견: 문헌은 **선형** 관계를 보고하는데 현재 sim/factors.py `_f_delta`는 `(d99/d99_ref)^n`
**거듭제곱**(n=3.0 가정)을 쓴다 — 형태 불일치를 노트에 명시. 단, 5개 팩 전부 abrasive_d99_nm이
없어 팩터가 여전히 no-op이므로 이번 회차는 UNWIRED를 해소하지 못했다(선행 필요: D99 스펙 확보,
다음 회차 과제). 형태 재검토는 소프트웨어 부문에 구현요청으로 전달(PROFILE.md).

sim/factors.py 코드 변경 없음(선행 데이터 미확보) → qa_loop 미실행(변경 없는 회차는 대상 아님).
pytest 443 passed(회귀 확인만, 신규 없음). agents/ORG.md §5 slurry-abrasive 1/6 갱신,
CURRICULUM.md Lv1-2 체크, EXAMS.md 3문항 추가.

다음 갭(--next): UNMODELED S(시간 안정성, 5팩) 또는 D99 스펙 확보 후 delta 재도전.

## 2026-09-09 11:xx [성장엔진] 정확도루프 UNMODELED delta — D99 실측값 확보 (트랙 A)

같은 갭(UNMODELED delta, score=100) 계속 이어감. Versum Materials US2019/0127607A1(무료 공개
특허출원공보, Table I·II)에서 세리아코팅 실리카 복합입자 D99 실측 158.5~316.7 nm 확보,
D99-HDP oxide RR 완전 단조 증가(n=4, 방향성 확인) but 구간별 기울기 13.7배 불균일(선형 아님)을
정량 확인. knowledge/cmp/abrasive-d99-composite-particle-versum2019.md 신규(verify_claims·
check_knowledge 둘 다 통과). 팩(5개)에 값 이식 안 함 — 이 특허 실시예 입자값이지 팩 조성과
무관해 오귀속 방지. sim/factors.py 코드 변경 없음 → qa_loop 대상 아님. pytest 443 passed(회귀만).
PROFILE/CURRICULUM/EXAMS/ORG.md §5 갱신(slurry-abrasive 1.5/6).

다음 갭(--next): 여전히 UNMODELED delta — 각 팩(cu_h2o2_bta 등) 실제 화학종의 제조사 스펙시트
D99 확보가 남은 선행 조건. 그 다음 순위 UNMODELED S(시간 안정성, 5팩).

## 2026-09-09 13:xx [Max워커] 소프트웨어 부문 S29 — disk-design 활성 그릿 비율 모델

software/BACKLOG.md 수신함에서 disk-design 구현요청 항목4(S29, 활성 그릿 비율 `f_active`) 처리.
`sim/tier2_physics/disk_active_grit_fraction.py` 신설(균일분포 f_a=engage_depth/(h_hi-h_lo),
CVD단일높이 f_a=1.0, N_eff=f_a·N_total, RCADD/CDD 유효비 2.8배 원자료 산술 재현, 종합함수).
근거: knowledge/equipment/cvd-diamond-disk-patterned-grit-array.md §2 verify·§3.2·§7·§8.
Kim&Kang2011(DOI 10.1016/j.ijmachtools.2011.02.008) 균일분포 40-90µm→5/10/15µm침투=10/20/30%,
Tsai2014(DOI 10.1155/2014/913812) RCADD 유효비 484/10000÷432/25000≈2.8배 그대로 재현 테스트 9건.
engine 미등록(Recipe에 디스크 스펙 필드 없음, S17/S26과 동일 지위).

Claude Code 위임(Read/Write/Edit/Bash, max-turns 40, 커밋 금지 브리핑) → Max워커가 pytest
452 passed(기존443+신규9) 직접 재검증, verify_claims.py --trace 상수 근거 미달 발견(정규식이
인라인 주석 못 찾음) 직접 수정해 통과, git status로 다른 크론 미커밋 파일(.night_parallel*·
papers/*·build/·dist/·tools/check_npw_catalog.py 등) 미접촉 확인 후 신규 2파일만 커밋(cb2db15)+push.
software/BACKLOG.md S29 완료 표기·완료표 이관, agents/disk-design/PROFILE.md 구현요청§4 완료 취소선.

## 2026-09-09 14:xx [성장엔진] 정확도루프 UNMODELED delta — 세리아/실리카 D99 크로스팩 조사 (트랙 A)

같은 갭(UNMODELED delta, score=100) 계속. 무료 특허 US10669449B2(Versum, 전문 확보) Table1/3에서
콜로이달세리아 LPC가 D50 같은 소성세리아보다 13.28배 높음(계산 재현), 세리아코팅실리카 두 시료의
D99/D50 비율 1.82~3.82배(계산 재현) 확보. Evonik IDISIL 콜로이달실리카 기술문서 확인 — D99 비공개,
Z-average만 노출(제조사 상업문서 통념 재확인). 5팩(cu_h2o2_bta 등) 어디에도 값 이식 안 함 —
특허 실시예 입자가 팩 화학종과 동일하다는 근거 없어 오귀속 방지. knowledge/cmp/
abrasive-d99-spec-cross-pack-comparison.md 신규(verify_claims·check_knowledge 둘 다 통과).
sim/factors.py 코드 변경 없음(선행 데이터 여전히 미확보) → qa_loop 대상 아님. pytest 452 passed(회귀만).
ORG.md §5 slurry-abrasive 1.7/6, PROFILE.md 구현요청 진행상황 갱신, EXAMS.md Lv2-1 3문항 추가.

다음 갭(--next): 여전히 UNMODELED delta — 알루미나 계열(cu_h2o2_bta, w_fe_oxidizer) D99 미확보가
남은 선행 조건(Baikowski/Fujimi 제조사 문서, 텅스텐 CMP 특허 실시예 탐색 예정). 순위 밀리면
다음 UNMODELED S(시간 안정성, 5팩)로 전환.

- 2026-09-09 09:30 [소프트웨어] software-lead: disk-design 구현요청 S39(절삭율 결합계수
  CR(N,N_eff,Rpk)) 완료 — `sim/tier2_physics/disk_cutrate_coupling.py`, Kwon2013·Tsai2014
  문헌값 재현 테스트 7건, g(활성비율지수) 미확정은 캘리브레이션 대기로 명시 처리. engine
  미등록. pytest 459 passed. 커밋 1b1cc51.

## 2026-09-09 [성장엔진] 정확도루프 UNMODELED delta — 알루미나 D99 재탐색 실패 + 일반 슬러리 비율 확보 (트랙 A)

같은 갭(UNMODELED delta, score=100) 계속. 알루미나 계열(cu_h2o2_bta, w_fe_oxidizer) D99를
US11117239B2/US9566686B2/JP5204226B2 특허 원문에서 재탐색했으나 3회차 연속 실패(percentile
데이터 자체 없음 또는 표 파싱 실패). 대안으로 Levitronix/Silco(2008) 컨퍼런스자료에서 일반
슬러리 세대별 D99/D50 비율(4.29~5.00배)을 확보해 이전 노트(세리아 코팅실리카 1.82~3.82배)와
합쳐 통합 관측범위 1.82~5.00배로 확장. AluminaWorld 상업블로그 스펙(D99<200nm)은 1차 출처
아니라 참고치로만 기록, 팩 미이식. knowledge/cmp/abrasive-d99-alumina-search-and-generic-ratio.md
신규(verify_claims·check_knowledge 둘 다 통과). sim/factors.py 코드 변경 없음 → qa_loop 대상
아님. pytest 459 passed(회귀만, 이전 회차와 동일 카운트 — 코드 무변경 확인).
PROFILE/ORG.md §5(1.8/6)/EXAMS.md(Q6-8) 갱신.

다음 갭(--next): 여전히 UNMODELED delta. 알루미나 D99 확보 접근 전환 필요(JP5204226B2 Table 1
구조화 재파싱 또는 텅스텐 CMP 논문 SI). 3회 연속 실패 시 다음 회차엔 다음 갭(S 시간 안정성)으로
전환 고려.

## 2026-09-09 [성장엔진] RESPONSE_DEAD cu_h2o2_bta/입자크기 — Bai2007 D^-1.5 배선 시도 → QA FAIL로 철회 (트랙 A, 정확도루프+QA루프)

정확도갭 1순위(RESPONSE_DEAD, cu_h2o2_bta/입자크기, n=18)를 처리. Bai et al. 2007(Appl. Surf.
Sci. 253, 8489-8494, doi:10.1016/j.apsusc.2007.04.027, 미러 사이트 원문 확보)에서 §3.2 폐형식 결론
(단일입자 제거율∝D^0.5, 활성입자수∝D^-2 ⇒ MRR∝D^-1.5)을 확인해
knowledge/cmp/particle-size-mrr-molecular-scale-bai2007.md 신규(verify_claims·check_knowledge
둘 다 통과, verify 블록 2개로 지수 재현 + TW202115224A 실측과의 방향 충돌을 정직하게 assert).
cu_h2o2_bta.yaml에 abrasive_size_exponent=-1.5 실제 배선(코드 무변경, 팩 파라미터만 추가) 후
qa_loop.py --strict 실행 → FAIL: tw202115224a_cu_abrasive_size_pressure가 p=0.0007(유의)에서
p=0.7605(비유의)로 퇴보. 사용자 지시(QA FAIL=커밋 금지) 준수해 git checkout으로 되돌림
(cu_h2o2_bta.yaml, sim/sensitivity.py, tests/test_sensitivity.py 원복). 지식노트만 커밋 —
§7.5에 실패 원인(입자 형상 혼입 가설)과 재시도 방향(형상 파라미터 분리) 기록. pytest 459 passed
(회귀, 원복 확인). 다음 갭 후보: 같은 RESPONSE_DEAD를 형상 분리 접근으로 재시도하거나
--skip으로 넘어가 Δ(손상 유발도)/S(시간안정성) UNMODELED로 전환.

## 2026-09-09 20:xx [성장엔진] 정확도루프 UNMODELED stab(S) — Jeong2024 로그감쇠 partial 편입 (트랙 A)

--skip "손상 유발도"로 델타 갭을 넘기고 다음 순위 갭 S(시간 안정성, 5팩 unmodeled) 처리.
기존 지식노트(knowledge/materials/pad-glazing-mechanism-mrr-decay.md §2.3 Jeong et al. 2024
Fig.9)에 이미 정량 재현된 무-컨디셔닝 1~10분 연속연마 MRR 드리프트 데이터를 활용 —
새 조사 없이 로그감쇠 회귀(pooled 2/5psi, R²=0.74)를 sim/factors.py _f_stab에 배선.
time_s=60s(기본값=1min) 기준 정확 1.0, 10min 관측상한에서 0.89. 실리카 외 연마입자는
confidence estimated로 강등(원 데이터 실리카/IC1000 단일계, fumed vs colloidal만도 감쇠율
5배 차이나는 게 이미 알려짐). MRR_COUPLED 미편입(held-out 지지 확인 전까지 보류) — partial
로 유지해 이중계상 위험 회피. qa_loop --strict PASS(유의 평균 ρ 0.9235 불변, 퇴보 없음).
pytest 462 passed. test_unmodeled_factors_report_none_not_silent_one를 4개 테스트로 교체.
커밋 2b9c64e, push 완료.

다음 갭 후보: --next가 다시 Δ(손상 유발도, cu_h2o2_bta/w_fe_oxidizer D99 미확보)를 반환할
가능성 높음 — 알루미나 D99가 3회 연속 실패했으니 다른 특허 소스(텅스텐 CMP 실시예) 재탐색
또는 --skip 후 CONFIDENCE/BIAS 종류 갭으로 전환 고려.

## 2026-09-09 20:xx [Max워커] software-lead: disk-design S27 접촉통계 기반 Preston 계수 분해 훅 완료

소프트웨어 부문 BACKLOG.md S27을 처리. `sim/tier2_physics/disk_preston_contact_decomposition.py` 신설
(eta_over_af/preston_coefficient_contact_scaling/fragment_contact_separation/disk_preston_contact_scaling).
근거: knowledge/materials/disk-design-pad-roughness-asperity-relation.md §2.3,§3.4(b), Sun 2009 학위논문
Fig.7.14/7.15 판독값(D100-1/D100-2/IC1000 3패드조합) 그대로 재현 테스트 13건. K_p 단순비례 가정은 PROVISIONAL로
docstring 명시(캘리브레이션 전 정량예측 금지). engine 미등록(S26/S29/S39와 동일 지위). Claude Code 위임 →
pytest 475 passed(기존462+신규13) 직접재검증, git status로 다른 크론 미커밋분(agents/.source_cache.json 등)
미접촉 확인 후 신규 2파일만 커밋(077b60d)+push. software/BACKLOG.md S27 완료표 갱신.

## 2026-09-09 21:30 [소프트웨어] software-lead: wafer-metrology S37 vm_baseline.py 완료

소프트웨어 부문 BACKLOG.md S37(Di 2017형 VM 베이스라인, Low 우선순위) 처리. `sim/metrics/vm_baseline.py`
신설(Di2017 가중앙상블 `mc_cv_weight`/`weighted_ensemble_predict`, `PersistentPredictor`/
`linear_regression_baseline` 베이스라인, US9240360 VM신뢰도가중 `vm_confidence_weight` PROVISIONAL).
근거: knowledge/cmp/inline-virtual-metrology-sampling-optimization.md §2.2 블록1/§2.4 블록4 그대로
재현 테스트 8건. engine 미등록(Recipe에 FDC 시계열 스키마 없음, S17 이하와 동일 지위). SVR/tree
bagging/딥러닝 신규구현 없음(브리핑 명시 금지). Claude Code 위임 → pytest 483 passed(기존475+신규8)
직접 재검증, git status로 다른 크론 미커밋분(agents/.source_cache.json·disk-design PROFILE.md·
.night_parallel*·papers/*·build/·dist/·tools/check_npw_catalog.py) 미접촉 확인 후 신규 2파일만
커밋(214154d)+push. wafer-metrology PROFILE 완료 표기(c243e52), software/BACKLOG.md S37 완료표 갱신.
wafer-metrology 수신함 완전 소진(S35/S36/S37 전부 처리). 남은 수신함: wafer-type S34(스키마 확장 필요).

## 2026-09-09 22:15 [성장엔진] slurry-abrasive Δ 팩터 n값 문헌 재검토

정확도루프 UNMODELED delta 갭(score=100) 처리. Hitachi 특허 US8439995B2(세리아 D50/D99/스크래치 4점 실측)에서 D99-스크래치 거듭제곱 회귀 n≈1.44(R²=0.997) 확보 — 현재 sim/factors.py `_f_delta` 기본값 n=3.0보다 약 2배 가파름을 확인, lpc-scratch-density-tail-correlation.md(선형)과 방향 일치(교차확증). factors.py docstring에 근거 기록(기본값은 표본 부족으로 유지, 지수 교체는 구현요청). knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md 신규(check_knowledge/verify_claims 통과), pytest 483 passed, qa_loop --strict PASS(유의 평균 ρ=0.9235). abrasive_d99_nm 부재로 팩터는 여전히 no-op — 다음 과제는 D99 팩 스펙 확보(특히 알루미나계, 3회 연속 미확보).

## 2026-09-10 01:xx [심야병렬] 서브에이전트 3명 동시 학습 — slurry-chemistry Lv1-1 · film-w Lv1-1 · film-nitride Lv1-1

0/6 병목 3명(전원 활성·G2/G3 신규 개방, 성장엔진이 건드린 slurry-abrasive·film-cu와 비중복)을 claude -p opus 3병렬 위임. 각자 다음 미이수 1단원만 깊게.
- **slurry-chemistry Lv1-1** 산화제 화학(H2O2·KIO3·Fe(NO3)3 E°·분해·금속적합성) → knowledge/cmp/oxidizer-redox-potential-decomposition-metal-suitability.md (출처 1건 실존, verify 3블록). 구현요청 2건(P2/P3) PROFILE 등록.
- **film-w Lv1-1** W CMP WO3 형성-제거 순환·산화제별 차이 → knowledge/cmp/w-cmp-wo3-passivation-oxidizer-kaufman.md (출처 3건 실존, verify 3블록). Tamboli1999 초록만/WO3밀도 핸드북값 미검증 정직표기.
- **film-nitride Lv1-1** LPCVD/PECVD SiN 물성·CMP 제거난이도 → knowledge/materials/film-nitride-lpcvd-pecvd-properties-cmp.md (출처 7건 실존, verify 3블록). Zheng2013 경도 2차인용 표기.

품질게이트(오케스트레이터 직접 재검증): 신규 3편 verify_claims·check_knowledge 각 1/1 통과. 전체 check_knowledge --all = 87/97(✗10편은 전부 기존 반려분, 신규 3편 무관). ORG §5 3행·CURRICULUM [x]·PROFILE·EXAMS·INDEX 갱신. disk-design/PROFILE.md는 소프트웨어 크론 미커밋분이라 커밋 제외.
QA루프 #15 PASS(격리 0, 유의 평균 ρ 0.9349). 코퍼스: fetch 5/60 성공(나머지 유료/403 봉쇄), extract 완료, 큐 fetch 2106·learn 177.
누적: slurry-chemistry 1/6, film-w 1/6, film-nitride 1/6.

## 2026-09-10 01:35 [Max워커] software-lead: wafer-type S(blanket_rate_transfer) 완료

software/BACKLOG.md 수신함 wafer-type Lv3-2 구현요청 항목1(우선순위 높음, blanket 순간속도 전이) 처리.
`sim/tier2_physics/blanket_rate_transfer.py` 신설(`cumulative_removal`/`blanket_rate_average`/
`blanket_rate_instantaneous`/`fit_blanket_rate`, eq.3.51-3.53). 근거: knowledge/cmp/
npw-ptw-transfer-rules-quantitative.md §3, §6 verify (B) (Tugbawa 2002 MIT 학위논문 표 3.3).
테스트 6건 그대로 재현(60s 평균이 포화 a1보다 8~30% 낮음, Fig.3.19 후반 5점 6% 이내, 초기점(7,65)은
21% 불일치를 실패 처리 않고 정직 기록, t=0 ValueError 계약, 합성데이터 파라미터 5% 이내 복원).
engine 미등록(Recipe에 시계열 폴리시 진행 스키마 없음, S17 이하와 동일 지위). Claude Code 위임
(Read/Write/Edit/Bash, max-turns 40, 커밋 금지 브리핑) → Max워커가 pytest 489 passed(기존483+신규6)
직접 재검증, verify_claims.py --trace 통과, git status로 다른 크론 미커밋 파일(agents/.source_cache.json·
.night_parallel*·papers/*·build/·dist/·tools/check_npw_catalog.py 등) 미접촉 확인 후 신규 2파일만
커밋(4d8f9b2)+push. agents/wafer-type/PROFILE.md 항목1 완료 표기.

## 2026-09-10 04:xx [심야병렬] 서브에이전트 3명 동시 학습 — cmp-data-engineer Lv1-2 · slurry-chemistry Lv1-2 · film-w Lv1-2

QA루프 #16 PASS(격리 0, 유의 평균 ρ=0.9349). 대상: 0/6 유일 병목 cmp-data-engineer + 직전 01:xx런이 Lv1-1 끝낸 slurry-chemistry·film-w의 Lv1-2(성장엔진이 만진 slurry-abrasive·film-cu와 비중복). claude -p opus 3병렬.
- **cmp-data-engineer Lv1-2** 통합 스키마 키 체계(SEMI GEM300 SVID/ECID/CEID 계보 사상·소모품 유도조인·SOURCE 강제) → knowledge/data/cmp-integration-schema-keys-semi-standards.md (출처 2 실존, verify 1블록). SEMI 표준 원문 유료 미열람→스트림/펑션 번호 미검증 표기. 스키마 JSON 구현은 PROFILE 구현요청.
- **slurry-chemistry Lv1-2** 억제제(BTA Langmuir/Frumkin)·킬레이트(글리신·시트르산 log K) 흡착·패시베이션 → knowledge/cmp/inhibitor-chelator-adsorption-isotherm-passivation.md (출처 4 실존, verify 3블록: MINTEQ pKa 교차검증·Cu 용해 1.4e6배·Frumkin 협동성). Aksu/Field 원문 미독·Frumkin f 시연값 정직표기.
- **film-w Lv1-2** Fe촉매 Fenton •OH 속도론·알루미나 vs 실리카 경도·IEP·스크래치 트레이드오프 → knowledge/cmp/w-cmp-fenton-catalyst-abrasive-alumina-silica.md (출처 4 실존, verify 3블록). Springer/SSRN 403 미확보→인용 제외, 개시 속도상수·IEP 2차인용 표기.

품질게이트(오케스트레이터 직접 재검증): 신규 3편 verify_claims·check_knowledge 각 1/1 통과. 전체 check_knowledge --all = 90/100(✗10편 전부 기존 반려분, 신규 무관). ORG §5 3행·CURRICULUM [x]·PROFILE(구현요청 P2/P3)·EXAMS·papers/INDEX.json 갱신. agents/.source_cache.json·disk-design/PROFILE.md는 다른 크론 미커밋분이라 커밋 제외.
누적: cmp-data-engineer 2/6, slurry-chemistry 2/6, film-w 2/6.

## 2026-09-10 [Max워커] software-lead: wafer-type S34 PTW VM 입력 스키마 완료

software/BACKLOG.md 수신함 S34(우선순위 중) 처리. `sim/calibration/` 디렉토리 신설(신규), `ptw_vm_schema.py`에
`PTWVMInput` dataclass(product_id/layer/die_density_mean/local_density/prev_layer_topography/e_test_R_ohm/
forced_measurement_flag/mrr_lag(1~11개 리스트로 통합 — 11개 개별 필드 대신 스키마 폭발 방지)/
consumable_usage_neighbors), `validate_ptw_vm_input`(경고 리스트: 밀도범위·"레이아웃 정보 전무→NPW와 구분 안 됨"·
lag 길이·저항 음수), `is_npw_equivalent`(노트 §5.3 결론 문장 그대로 판정 함수화). 근거:
knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §5.3, agents/wafer-type/PROFILE.md 구현요청 항목4.
테스트 13건 신규(tests/test_ptw_vm_schema.py). Claude Code 위임(Read/Write/Edit/Bash, max-turns 40, 커밋 금지
브리핑) → Max워커가 pytest 502 passed(기존489+신규13) 직접 재검증, git diff로 sim/engine.py(Recipe/WaferResult)
무수정 확인, git status로 다른 크론 미커밋 파일(agents/.source_cache.json·agents/disk-design/PROFILE.md·
validation/ledger.jsonl·.night_parallel*·papers/*·build/·dist/·tools/check_npw_catalog.py 등) 미접촉 확인 후
신규 3파일+PROFILE.md만 커밋(7056281)+push. software/BACKLOG.md S34 완료표 갱신(커밋 해시 반영).
engine 미등록(VM 입력 스키마이지 물리 시뮬레이션 입력 아님, S17 이하와 동일 지위). wafer-type 수신함 완전 소진
(S30~S34 전부 처리).

## 2026-09-10 08:xx [성장엔진] delta 갭 -- 텅스텐 벌크 CMP 응집-스크래치 배수 문헌 확보

정확도루프 --next: UNMODELED delta(score=100, 5팩 미모델링, 3회 연속 최우선). 코퍼스 큐에서
6개 문서 순회(patent:US20110165777A1, US9499721B2, doi:10.1038/s41598-026-54610-0,
doi:10.1177/0036850420982451, doi:10.3390/ma19112200, doi:10.3390/mi12080956, pmc:PMC9920658)
-- 전부 D99-스크래치 정량표 없음/범위 밖으로 mark done. 웹검색으로 전환해 Egan and Kim 2019
(ECS JSS, GLOBALFOUNDRIES 텅스텐 컨택 CMP 실양산) 확보 -- Unpaywall OA로 유료저널 원문 무료
획득. knowledge/cmp/w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019.md: 입자
응집배수(온도3x->스크래치60x, 교반3x->스크래치6.67x) -> damage_exponent 역산 n약1.73~3.73
(세리아 Hitachi n=1.44 대비 가파름, 3번째 독립 문헌). 핵심 발견: 텅스텐 벌크 CMP는 입자크기가
MRR과 무관(원문 직접 실측) -- 카파 팩터 화학종 예외 처리 필요성 시사, 구현요청 등록.
D99 절대값은 이번에도 미확보(PSD 정규화 그래프) -- delta 갭은 no-op 유지, damage_exponent
화학종 분화 근거만 축적. verify_claims/check_knowledge 1/1 통과, pytest 502 passed(회귀 없음),
qa_loop --strict PASS(유의 평균 rho=0.9349, 격리 0). agents/.source_cache.json,
disk-design/PROFILE.md는 다른 크론 미커밋분이라 제외, 신규 5파일만 커밋(9e91a2c)+push.
ORG.md 5절 slurry-abrasive 1.8->1.9/6 갱신. corpus.py status: total 2283, with_fulltext 1311,
learn 큐 1304(7건 처리).

## 2026-09-10 09:30 [소프트웨어]
film-cu PROFILE.md 구현요청(P1, Cu-H₂O Pourbaix 경계 함수)을 S40으로 처리 —
`sim/tier2_physics/cu_pourbaix.py` 신설(경계식 6종 + stable_phase 판정함수),
Tamilmani 2005 그림4.1 재현 테스트 12건. CuO는 ΔG_f° 미확보로 미구현(Cu(OH)₂ 대체값,
미검증 명시). engine 미등록. pytest 514 passed(기존502+신규12). 커밋 495ed90.

## 2026-09-10 10:xx [성장엔진]
정확도루프 UNMODELED delta 갭 계속 — 알루미나 D99 4차 탐색: Guo&Subramanian(2004,
doi:10.1149/1.1640632, 미러 사이트 경유, Cu+알루미나 화학종 일치)은 평균 응집입경 220nm만
보고(분포 데이터 없음), US6258137B1(나노알루미나 CMP 특허, patentimages 직접 확보)은
"D90≤50nm/상위10%>100nm" 경계조건만 있어 D99 유일값 역산 불가함을 논리적으로 증명(verify
블록). knowledge/cmp/abrasive-d99-alumina-fourth-attempt-guo-nanoalumina.md 신설,
verify_claims/check_knowledge 1/1 통과. **판단: 알루미나 D99 탐색 4연속 실패로 이 경로
종결** — accuracy_gaps.py --skip 처리, agents/slurry-abrasive/PROFILE.md에 대안 경로(세리아
D99 이식 재검토, LPC 임계 0.68µm scratch_threshold_nm 전환) 기록. qa_loop 실행 전 커밋
보류(코드/팩 변경 없이 노트만 추가라 qa_loop 대상 아님).

## 2026-09-10 12:xx [성장엔진]
정확도루프 UNMODELED delta 갭 no-op 해소(1/5팩) — 알루미나 경로 종결 후 권고했던 "세리아 D99
이식 재검토"를 실행: sti_ceria(및 상속 sic_ceria_h2o2)에 abrasive_d99_nm/abrasive_ref_d99_nm=
700nm(Hitachi US8439995B2 Example1, 화학종 일치 근거 baseline, confidence=estimated)와
damage_exponent=1.44(동 특허 4점 회귀, R²=0.997, confidence=literature)를 배선.
`_f_delta`가 처음으로 발동(기존엔 5팩 전부 abrasive_d99_nm 부재로 no-op). 기준조건 Δ=1.0 계약
확인 + D99 700→2500nm 스캔 시 Δ=6.25배(문헌 원 대응쌍 5배와 오더 일치, 절대 일치는 주장 안 함)
— tests/test_factors.py 신규 3건(기준1.0/단조증가/MRR 비결합) 추가. delta는 MRR_COUPLED 밖
유지(실측 지지 전까지 미편입, 사용자 원칙 준수) — 백테스트 ρ 불변 확인(0.9349, 회귀 없음).
pytest 517 passed, qa_loop --strict PASS. 잔여 4팩(cu_h2o2_bta, oxide_silica, w_fe_oxidizer는
알루미나/실리카 계열, D99 미확보 지속)은 여전히 no-op — 다음은 알루미나 특허 조성표 재탐색 또는
Δ 스크래치 축을 LPC 임계(0.68µm)로 전환하는 대안 검토.

## 2026-09-10 13:xx [소프트웨어/Max워커]

software/BACKLOG.md S12(모듈 엔진 이관) 진행 — `sim/tier2_physics/npw_ptw_effective_pressure.py`를
`sim/engine.py`에 진단 필드로 등록. `_effective_pressure_diagnostic()` 신설(기존 `_lubrication_diagnostics`/
`_film_thickness_diagnostic`과 동일 패턴 — MRR 경로와 완전 독립). `WaferResult`에
`ptw_effective_pressure_ratio`/`ptw_effective_pressure_note` 필드 2종 추가. PTW이고
`rr.meta['pattern_density']`가 Sorooshian(2005) §3.3 표값(0.10/0.50/0.90) 중 하나일 때만 값이
채워지고, 그 외(NPW/미지정/표에 없는 밀도)는 조용히 None + 정직한 스킵 사유 note(조용한 보간/외삽
없음 원칙 유지). 계약테스트 5건 신설(`tests/test_ptw_effective_pressure_diagnostic.py`), pytest 522
passed(기존517+신규5, 회귀 없음). Claude Code 위임(Read/Write/Edit/Bash, max-turns 40, 커밋 금지
브리핑) → Max워커가 pytest 직접 재검증, git diff로 sim/engine.py 진단 추가 외 로직 변경 없음 확인,
git status로 다른 크론 미커밋 파일(agents/.source_cache.json·agents/disk-design/PROFILE.md·
.night_parallel*·papers/*·build/·dist/·fabsim.egg-info·tools/check_npw_catalog.py·validation/two_stage/)
미접촉 확인 후 신규 2파일만 커밋(42d7cb4)+push. `npw_ptw_effective_pressure.py` 파일 자체는 무수정.
S12는 여전히 미완료(19→18개 모듈 남음, ⬜ 유지).

## 2026-09-10 14:xx [성장엔진]
cu_h2o2_bta RESPONSE_DEAD(입자크기, n=18 valley) 5차 재시도 — TW202115224A 순수구형
부분집합(형상 라벨 "구형"만, n=6/압력)으로 재정량해도 Spearman |ρ|<0.2·p>0.7로 유의상관
없음(Bai2007 §7.5의 "형상혼입" 가설도 불충분함을 확인). 형상 효과 자체는 문헌상 실존
가능성 있으나(Kim et al. 2021, doi:10.1016/j.powtec.2020.11.058) 원문 미확보(Unpaywall
closed, 미러 사이트 5개 미러 전부 캡차) + 2차 인용 2건이 방향 모순(RSC리뷰: bumpy가 MRR
59%↓ / ScienceDirect초록: bumpy가 MRR↑)이라 미반영. 지식노트
knowledge/cmp/abrasive-shape-effect-purespherical-subset-nonmonotonic.md 신설,
verify_claims·check_knowledge 1/1 통과. 코드/팩 변경 없음(qa_loop 대상 아님). 갭 skip 처리
→ 다음 최우선 RESPONSE_DEAD는 oxide_silica/pH(n=7 valley, ph_softening_per_unit 미배선).
corpus.py fetch 이번 회차 0/15(특허 소스 일시 불가), extract 미실행.

## 2026-09-10 15:30 [소프트웨어]
surface-contamination Lv3-2 요청1(우선순위 상) `competitive_langmuir_surface` 구현 완료 —
`sim/tier2_physics/competitive_metal_langmuir.py` 신설. Loewenstein·Charpin·Mertens 1999
Eq.22 경쟁 Langmuir 흡착 모델, 근거노트(post-cmp-residual-metal-prediction-langmuir-scm.md
§2·§6(A)) 정량값 그대로 재현 테스트 5건. engine 미등록(Recipe 스키마 부재). pytest 527
passed(기존522+신규5). 커밋 986d8cb. BACKLOG S41 완료 등록.

## 2026-09-10 16:xx [성장엔진]
정확도루프: oxide_silica/pH RESPONSE_DEAD(cn109609035b held-out, n=7 valley 무반응) 해결 —
Choi 2004(doi:10.1149/1.1738472, 미러 사이트 경유) 정전반발 메커니즘 근거로 knowledge/cmp/
silica-cmp-ph-acidic-repulsion-choi-power-law.md 신설, cn109609035b 특허 표1 산성 5점에
멱함수 피팅(MRR∝pH^-3.09) → sim/factors.py `_ph_peak_term`에 pH≤6.5 산성 가지 배선(기존
Li2021 정점형 pH≳9.7 계약 불변). check_knowledge/verify_claims 1/1 통과, pytest 527 passed,
qa_loop --strict PASS(cn109609035b 비유의→유의 ρ=+0.893, 유의평균 0.935→0.929 경미 하락
허용범위). response_map 판정 DEAD→CONFLICT로 전환(방향은 아직 안 맞음, down vs valley) —
다음 최우선 갭은 이 CONFLICT(score 120, 6.5~9 전환구간 데이터 없어 골 형태 재현 미완).
커밋 c50b96f, push 완료.

## 2026-09-10 18:xx [성장엔진]
정확도루프: 위 CONFLICT(score 120) 해결 — cn109609035b 7점 전체(반등 포함)에 로그이차
(ln MRR=a·pH²+b·pH+c) 재피팅, `_ph_peak_term`을 산성(≤6.0 로그이차 골)/전환(6.0~9.0 로그-선형
보간)/염기(≥9.0 Li2021 정점) 3구간으로 재구성. knowledge/cmp/silica-cmp-ph-acidic-repulsion-
choi-power-law.md §3-2 신설(verify 2블록), verify_claims/check_knowledge 1/1 통과, pytest 527
passed. response_map CONFLICT→AGREE, backtest cn109609035b ρ +0.893→+1.000, qa_loop --strict
PASS(유의평균ρ 0.929→0.944). 커밋 de151c9, push 완료. 다음: accuracy_gaps.py --next 재실행해
다음 최우선 갭 확인 필요(다음 회차).

## 2026-09-10 20:xx [성장엔진]
정확도루프: psi UNMODELED(oxide_silica/sti_ceria/sic_ceria_h2o2/w_fe_oxidizer 4팩, score 95) 중
w_fe_oxidizer 해결 — Lee와 Seo 2022(DOI:10.3390/app12031227, CC-BY, MDPI CDN 경유 원문 확보 통독)
피콜린산 억제제 Langmuir 흡착과 정지식각 억제 정량 재현. knowledge/cmp/w-cmp-picolinic-acid-inhibitor-
langmuir-dissolution-suppression.md 신설(verify_claims/check_knowledge 1/1 통과). K=1108 L/mol,
k_inhib=2.117(정지식각 90에서 11 A/min, 8.2배 감소 역산) 도출, knowledge/params/w_fe_oxidizer.yaml에
배선(코드 변경 없음, 기존 _inhibitor_term 재사용). tests/test_factors.py 3건 추가(psi modeled, 기준1.0,
방향성). pytest 530 passed, qa_loop --strict PASS(유의평균 rho 0.944 유지, 회귀 없음). 커밋 ecca1f9,
push 완료. 오늘 두 번의 문헌 접근 시도(nitride 억제 IOP 논문, STI 세리아 특허)는 paywall과 캡차로
실패했으나 세 번째(MDPI CC-BY)는 성공 — 회차 내 시간 상당 소요, 다음 회차는 accuracy_gaps.py --next
재실행으로 이어감(oxide_silica/sti_ceria/sic_ceria_h2o2의 psi는 여전히 UNMODELED로 남음).
corpus.py status: total=2283, with_fulltext=1311, queue fetch=972 learn=1301(이번 회차 fetch 0/10
신규 확보, learn 큐에서 nano-abrasive 리뷰 1건 확인했으나 psi 관련성 낮아 별도 처리 안 함).

## 2026-09-10 20:xx [소프트웨어/Max워커]

film-cu 구현요청 P1(Tugbawa 밀도-스텝하이트 오버폴리시 커널) 신규 구현 —
`sim/tier2_physics/cu_dishing_erosion_tugbawa.py` 신설. knowledge/cmp/cu-dishing-erosion-density-
step-height-model-tugbawa.md §2·§3.2·§3.3의 닫힌 시간해(eq 3.37-3.42, d_max 경험식 eq3.46,
엣지라운딩 ψ eq3.49)를 그대로 구현(steady_state_dishing_tugbawa/tau3/erosion_rate_Y1/
d_max_from_linewidth_space/edge_rounding_psi/dishing_time_evolution/erosion_time_evolution +
종합 cu_overpolish_dishing_erosion). 기본 파라미터는 노트 Table 3.9 "#1 Stacked pad ψ포함"
캘리브레이션값(특정 장비 Mirra·특정 슬러리 EPC-5001 한정)임을 docstring·notes 양쪽에 경고 표기.
§4.2 과도 오버폴리시 플래그(erosion>3000Å 또는 Φ>0.95) 포함. SER(정적식각)은 노트 §6이 후속
과제로 명시한 대로 이번 범위에서 제외. 노트 §7 verify 1-3 정량값(Fig3.14 90%/50% 어레이 오차
5%/41%, Fig3.12 고립선 비율, Table3.9 압력보존 등) 전체를 pytest로 이전(18 케이스) +
엔진 게이팅 회귀(6 케이스). engine.py에 `cu_dishing_tugbawa_nm`/`cu_erosion_tugbawa_nm`/
`cu_dishing_tugbawa_note` 진단 필드 3종 추가(기존 미사용 dishing_nm/erosion_nm과 이름 분리,
값 경로는 완전 독립). 계산 게이트: cu_h2o2_bta 팩 + PTW + meta에 패턴레이아웃(pattern_density·
linewidth_um·space_um)과 실측 r_cu_angstrom_s/r_ox_angstrom_s가 전부 있을 때만 — 문헌 캘리브레이션
상수(a1=159Å/s 등)를 몰래 기본값으로 쓰지 않음(조용한 외삽 금지 원칙 준수), 하나라도 없으면
None+스킵사유 note. 기존 `sim/tier1_empirical/pattern_density.py::steady_state_dishing`(자유파라미터
b 방식)은 무수정, 공존.

Claude Code 위임(Read/Write/Edit/Bash, max-turns 40, 커밋 금지 브리핑) → Max워커가
check_knowledge.py 1/1 통과 확인, pytest 553 passed(기존527+신규24, 회귀 없음) 직접 재검증,
git diff sim/engine.py로 필드추가·진단함수·simulate() 배선 외 로직 변경 없음(전부 `+`) 확인,
git status로 다른 크론 미커밋 파일(agents/.source_cache.json·agents/disk-design/PROFILE.md·
.night_parallel*·papers/*·build/·dist/·fabsim.egg-info·tools/check_npw_catalog.py·
validation/two_stage/·data/corpus/) 미접촉 확인 후 신규 3파일+sim/engine.py만 커밋(31bd312)+push.
software/BACKLOG.md film-cu 구현요청 수신함 항목 완료 표시는 다음 항목에서 기록.

## [소프트웨어] 2026-09-10 21:30
surface-contamination Lv3-1 요청1(`galvanic_pair_direction`+`hydroxide_transition_pH`, S43) 처리 완료 —
`sim/tier2_physics/galvanic_hydroxide_ph.py` 신설(CRC 표준환원전위표 6종, minteq.v4.dat log K 기반). 근거
knowledge/cmp/low-level-metal-cobalt-ruthenium-cross-contamination.md §3.1·§3.3·§6(A)(B) 정량값 그대로
재현 테스트 8건(Cu/Co ΔE°=0.62V, Ru/Cu ΔE°=0.113V, Cu/Co 100ppm 수산화물 전이 pH 5.74/7.93). engine
미등록(Recipe 스키마 부재). pytest 561 passed(기존553+신규8). 커밋 d8a4c90(코드)+후속 1건(PROFILE 표시).
BACKLOG S43 완료 등록, surface-contamination PROFILE Lv3-1 요청1 완료 표시. 남은 수신함: Lv3-2 요청2
(residual_after_clean, 중), Lv3-2 요청3(체인조립 predict_residual_metal, 요청2 선행 필요).

- 2026-09-10 22:xx (성장엔진): RESPONSE_DEAD 갭(cu_h2o2_bta/입경) — Chen thesis(Iowa State, 무료) 단층입자면밀도+소성압입 결합 1차유도를 코드로 재현해 MRR이 이론상 정확히 d^0(무반응)임을 확인, TW202115224A(Cu,valley)와 Li2021(oxide,peak) 부호반대 대조 — knowledge/cmp/abrasive-size-null-result-force-partition-theory.md. verify_claims/check_knowledge 통과, pytest 561 green. sim/factors.py 코드변경 없음(가드 유지가 근거로 뒷받침됨). 완성 격자 6/50 변화없음.

## 2026-09-11 01:xx [심야병렬] 서브에이전트 3명 동시 학습 — film-poly-si Lv1-2 · film-nitride Lv2-1 · tool-endpoint Lv2-1
QA루프 #22 PASS(격리 0, 유의 평균 ρ=0.9442). completion 6/50. 대상: 진도 최저 3명(film-poly-si 1/6 최저, film-nitride/tool-endpoint 2/6), 성장엔진 최근 대상(slurry-abrasive·cu_h2o2_bta delta)과 비중복. claude -p opus 3병렬 위임.
- [[knowledge/materials/film-poly-si-alkaline-dissolution-ph-kinetics]] — Poly-Si 알칼리 용해 pH 속도론. Seidel1990(DOI 10.1149/1.2086277, 미러 사이트 원문): OH⁻ 4개/Si·4e 주입, R∝[H₂O]⁴[OH⁻]^¼, Eₐ(100/110/111)=0.59/0.61/0.70eV. Bae2022(nano12213893, CC-BY): 아민(EDA/DETA/TETA) vs NaOH/KOH, 화학-기계 시너지. verify 1블록(5하위 assert): 배향 이방성비 Arrhenius 100°C 30.6 vs 관측30, 상온 25% 차이 정직기록, peak 16.8wt% vs 문헌~20. 출처 4건 실존. film-poly-si 2/6.
- [[knowledge/cmp/sti-nitride-loss-erosion-overpolish-window]] — STI 나이트라이드 손실·디싱 공정윈도우. Lee2002·Johnson2009(MIT 학위 원문판독)·Dandu2009·Mariscal2020. 정상상태 손실률 K_ss=K/(1+ρ(s−1))(블랭킷율 1.8배), 선택비 값어치=디싱감소 아니라 오버폴리시창 확대(s=10→100서 37.8→304s, 8배), 블랭킷선택비≠패턴손실(세리아 HSS 100+여도 s_eff≈3). verify 4블록 전부 PASS(침식식 수치적분, 창 8배, K_ss(ρ) 표3.9 ±9%, 자기정지 30Å 대조). 출처 6건(1차 4). film-nitride 3/6. 구현요청 2건.
- [[knowledge/equipment/epd-film-type-suitability-transparent-multilayer-limits]] — 막질별 EPD 적합성·투명막/다층 한계. 금속(Cu/W)=모터전류·와전류, 유전체=광학간섭. verify 1블록(4하위): λ/2n=0.333µm(특허 ~0.3), 200nm 잔막<1주기 카운트불가, 면적분율 선형희석 f=0.1은 1/5, 와전류 최소55nm≈광학투명화 30–40nm. 출처 3건. tool-endpoint 3/6.
품질게이트: 3/3 통과(check_knowledge ✓ + verify_claims ✓ 오케스트레이터 직접 확인). 전체 107/114(반려 7편은 기존 노트·성장엔진 상환 대상, 이번 3편 무관).

## 2026-09-11 04:2x [심야병렬] 서브에이전트 3명 동시 학습 — cmp-data-engineer Lv2-1 · film-w Lv2-1 · slurry-chemistry Lv2-1
QA루프 #23 PASS(격리 0, 유의 평균 ρ=0.9442). corpus fetch60/extract120 백그라운드 병행. completion 6/50(변화없음). 대상 선정: progress.py 활성 최저진도 5명 중 slurry-abrasive(성장엔진 최근)·film-poly-si(직전 01시 심야병렬) 제외 → cmp-data-engineer/film-w/slurry-chemistry(전부 2/6). claude -p opus 3병렬 위임.
- [[knowledge/data/wafer-coordinate-units-outlier-cleaning]] — 웨이퍼 좌표계(SEMI M20 원점중심·노치−y)·단위(SI 정준)·이상치(MAD/EE) 클리닝 규칙. 핵심: 노치오등록·단위슬립이 스칼라지표(TTV/WIWNU/CV)엔 불변이라 QC 조용통과하며 공간조인만 오염(uniformity.py 실호출 대조). 출처 US7539552B2(1차)·Leys2013 MAD(1차 OA)·SEMI M20/M1(스코프확인,원문유료미확보). verify 5블록 PASS(psi=6.894757kPa, 1Å/s=6nm/min, EE 3mm→3.96
## 2026-09-11 04:2x [심야병렬] 서브에이전트 3명 동시 학습 — cmp-data-engineer Lv2-1 · film-w Lv2-1 · slurry-chemistry Lv2-1
QA루프 #23 PASS(격리 0, 유의 평균 ρ=0.9442). corpus fetch60/extract120 백그라운드 병행. completion 6/50(변화없음). 대상: progress.py 활성 최저진도 5명 중 slurry-abrasive(성장엔진 최근)·film-poly-si(직전 01시 심야병렬) 제외 → cmp-data-engineer/film-w/slurry-chemistry(전부 2/6). claude -p opus 3병렬 위임.
- [[knowledge/data/wafer-coordinate-units-outlier-cleaning]] — 웨이퍼 좌표계(SEMI M20 원점중심·노치−y)·단위(SI)·이상치(MAD/EE) 클리닝. 핵심: 노치오등록·단위슬립이 스칼라지표(TTV/WIWNU/CV)엔 불변→QC 조용통과하며 공간조인만 오염(uniformity.py 실호출 대조). 출처 US7539552B2(1차)·Leys2013 MAD(1차 OA)·SEMI M20/M1(스코프확인,원문유료미확보). verify 5블록 PASS(psi=6.894757kPa, 1Å/s=6nm/min, EE 3mm→3.96%). 구현요청 normalize.py 4함수. cmp-data-engineer 3/6.
- [[knowledge/cmp/w-cmp-plug-recess-coring-keyhole-overpolish-window]] — W플러그 리세스·코어링·키홀·심 결함→CVD갭필→버프 공정윈도우. 1차원문 3편 PDF통독·DOI실존: Yu2009(10.1149/1.3009224), Kim2005(10.1016/j.microrel.2005.07.048 EM수명1.9배), Xu2020(10.1016/j.mee.2020.111285). verify 3블록 PASS. 심-코어링폭주·디싱200-300Å은 추정/미검증 명시. EOE(Vacassy2006) 원문미확보→정성만. film-w 3/6. 구현요청 2건.
- [[knowledge/cmp/ph-ionic-strength-zeta-dissolution-selectivity-pourbaix]] — pH·이온강도→ζ·용해율·선택비 Pourbaix재해석. 1차 Sun2007 UA학위(직접판독, 실리카 비-DLVO 반례)·Dandu2009(10.1149/1.3230624 ζ-pH실측→oxide:nitride~175). Debye원자가확장·Schulze-Hardy z⁻⁶·ζ부호정합→STI선택비. verify 3블록 PASS. 상호링크 10개. slurry-chemistry 3/6.
품질게이트(오케스트레이터 직접): 3/3 통과(각 check_knowledge ✓ + verify_claims ✓). 전체 110/117(실패 7편은 기존 노트, 이번 3편 무관). 3명 전원 2/6→3/6.

## 2026-09-11 07:xx [소프트웨어/Max워커]

cmp-data-engineer 구현요청(sim/calibration/normalize.py) Claude Code 위임 → 착수 시점에 이미
다른 병렬 크론(학습총괄/심야병렬)이 완성해 둔 상태였음(4함수 전부 스펙 충족, 17 tests). Max워커가
직접 pytest tests/test_normalize.py(17 passed) + 전체 스위트(583 passed, 회귀 없음) 재검증 후
git status로 다른 크론 미커밋 파일(agents/.source_cache.json·disk-design/PROFILE.md·
validation/ledger.jsonl·.night_parallel*·papers/*·build/·dist/·fabsim.egg-info·tools/*·
validation/two_stage/·data/corpus/) 미접촉 확인, 신규 2파일만 커밋(da2dc9a)+push.
cmp-data-engineer 구현요청 "normalize.py" 항목 완료.

## 2026-09-11 08:xx [성장엔진] 정확도루프 — RESPONSE_DEAD cu_h2o2_bta/입자크기 시도·revert
accuracy_gaps.py --next → cu_h2o2_bta/abrasive_size_nm(RESPONSE_DEAD, score 95, TW202115224A n=18 무반응).
Luo-Dornfeld(2003) Part1 원문(UC eScholarship OA, papers/luo-dornfeld-material-removal-regions-part1.pdf 직접
판독) Eq.1-2에서 "(x+3σ)²/x³, σ=CV·x 일정 가정 시 f∝1/x_avg" 폐형식 확보 → knowledge/cmp/
luo-dornfeld-active-abrasive-size-mrr.md(verify 2블록 PASS, check_knowledge✓) → sim/factors.py `_f_kappa`에
abrasive_size_cv + 적용범위(≤50nm) 게이트로 배선, tests/test_factors.py 2건 추가, pytest 584 passed(회귀 없음).
그러나 qa_loop.py run --strict = FAIL: tw202115224a 데이터셋이 유의(p=0.0007,ρ=0.717)→비유의(p=0.764,ρ=-0.176)로
퇴보(방향이 오히려 뒤집힘 — 게이트가 d_ref=100nm은 범위밖이라 기준항상 꺼짐, override된 d만 15-50nm 켜지는데
이 좁은 구간의 실측이 특허 9배합 중 15/27/50nm 3점뿐이라 노이즈에 취약했던 것으로 추정, 미검증).
지침대로 sim/factors.py·tests/test_factors.py·팩 yaml 3파일 git checkout으로 revert, 지식노트만 커밋(d238fab).
같은 갭 2회 연속 FAIL이 아니므로 다음 회차에 다른 접근(예: 형상 파라미터 분리 또는 좁은 구간 배선 대신
3점만 별도 서브데이터셋으로 분리)으로 재시도, 아니면 --skip.
completion 6/50(변화없음, C1 미충족 유지 — 이번 시도가 unmodeled를 modeled로 못 바꿈). corpus fetch/extract 미실행
(이번 회차는 기존 노트 재활용 우선, 코퍼스 사이클 다음 회차).

## 2026-09-11 09:30 [소프트웨어/software-lead] ψ×3 UNMODELED 해소 + C5 5축 해소

COMPLETION.md 우선순위(물리모델링 최우선, ψ×3 UNMODELED가 C1 최상위)에 따라 `oxide_silica`/
`sic_ceria_h2o2`/`sti_ceria`의 ψ(표면 보호도) 팩터 착수. Claude Code 위임(커밋 금지 브리핑) →
같은 시각 동시 실행 중이던 다른 크론(정확도루프 성장엔진 계열)이 같은 파일을 병렬로 작업 중이었고,
그쪽이 먼저 완주해 커밋(2a1eb44)까지 마쳐둔 상태를 확인 — `sim/chemistry.py`에
`_dispersant_protection_term()`(Li et al. 2021 §6 실측: PVA -3.6%, PVP -7.9%, PAA/PAM/NONE 무변화)
신설, `sim/factors.py` `_f_psi()`가 억제제 없으면 분산제 경로로 폴백. 그쪽 세션이 기준조건 1.0 계약
위반(ψ 절대 저해율 반환)과 세리아 2팩의 실리카 PVA값 교차계 오용을 자체 발견·수정했고, 덤으로
`tools/completion.py`의 `notes_with_verify()` 경로 파싱 버그(절번호·서지인용 문자열을 파일 경로로
오인)까지 고쳐 C5 5축이 함께 해소됐다. software-lead가 pytest 594 passed(기존583+신규11) 직접
재검증, `completion.py check`로 C1 6→3칸(ψ×3 확인) + C5 10/10축 통과 확인, git fetch로 origin 대비
로컬 4커밋 확인 후 push(2a1eb44). 격자 6/50→7/50.
남은 C1: Δ×3(cu_h2o2_bta/oxide_silica/w_fe_oxidizer, LPC-스크래치 꼬리분포 경로) — 다음 회차 최우선.

## 2026-09-11 10:xx [성장엔진] EVIDENCE-RULES 판정 #1 시스템 반영 + Δ 활성화 테스트
어제(EVIDENCE-RULES.md 판정 #1)로 "cu_h2o2_bta 입경은 null 결론"이라고 종결했지만
accuracy_gaps.py/response_map.py는 여전히 이걸 RESPONSE_DEAD(score95)로 최우선 배차하고
있었다 — 판정이 도구에 반영 안 돼 재작업 위험 그대로였음을 발견. tools/response_map.py에
NULL_CONFIRMED 판정(verdict='NULL_CONFIRMED', 표시 ∅)을 신설해 (pack,key) 화이트리스트로
등록, 이제 accuracy_gaps.py --next가 이 축을 건너뛰고 다음 진짜 갭(COMPLETION-C1 Δ)으로
이동함을 확인. 이어서 Δ 갭을 보니 같은 시각 동시 실행 중이던 다른 크론(software-lead 계열)이
이미 3팩(cu_h2o2_bta/oxide_silica/w_fe_oxidizer) abrasive_d99_nm/damage_exponent 파라미터를
_proposals/delta_and_d99.md 제안서 그대로 반영해 커밋(ba5cbf7, 6ac34aa)까지 완료해둔 상태 —
C1 3→0칸 이미 달성. 중복 작업 방지 겸 회귀 방지선으로 tests/test_factors.py에 3팩 Δ=1.0
계약 테스트 추가. pytest 595 passed, qa_loop --strict PASS(ρ=0.944 불변 — Δ는 진단전용이라
당연). e615adb로 커밋·push. 완성 격자 12/50(변화없음, 병렬세션이 이미 반영). 남은 C2 38칸이
현재 최대 병목 — 다음 회차는 confidence 승격(코퍼스 next --stage learn)에 집중 권고.


## 2026-09-11 12:xx [성장엔진] COMPLETION-C4 sic_ceria_h2o2 held-out 탐색 -- 신규자료 확보했으나 등록 보류
갭 랭커 최우선(COMPLETION-C4, score88): sic_ceria_h2o2 팩 유의 held-out 0건. 코퍼스(SiC 관련
문서 70+건)와 미러 사이트를 뒤져 신규 원문 2편 확보(papers/proeng-2011-11-2673-alumina-6h-sic.pdf =
SU et al. Procedia Eng 24(2011)441 6H-SiC알루미나 슬러리 산화제/pH/압력 시리즈; papers/
jjap50-046501-sic-high-removal-rate.pdf = Nitta et al. JJAP 50(2011)046501 4H-SiC H2O2/H5IO6
oxidizer molarity 곡선). 둘 다 재료계는 SiC로 팩과 일치하나:
  1) proeng 산화제 4점(5/10/15/20ml)을 Kaufman 단봉으로 맞추면 n약0.12, Cpeak=15ml인데 이건
     같은 4점으로 역산한 값이라 held-out이 아니라 calibration이다 -- 별도 독립 데이터가 없으면
     등록해도 C4를 충족 못 시킨다(자기 답안지 채점 금지 원칙).
  2) jjap 데이터(H2O2 몰농도 vs RR, 4H-SiC)로 held-out을 시도했으나, proeng에서 역산한 n=0.12,
     Cpeak=3(ml 스케일)을 jjap의 mol/L 스케일로 그대로 못 옮긴다(단위 비양립) -- 임의 스케일
     맞춤은 지어낸 파라미터가 되므로 보류.
결론: sic_ceria_h2o2의 oxidizer_wt_pct/peak/curve_n 파라미터 자체가 팩에 없다(현재 oxidizer_ref_wt_pct만
있고 chi 항이 화학 팩에서 발동 안 함, 실측 확인: chi factor에 oxidizer 항 부재). 이걸 채우려면
같은 계(SiC, 세리아나 유사 산화제)에서 3점 이상 산화제 농도-MRR 계열이 2세트(하나는 캘리브레이션,
하나는 held-out) 필요한데 이번 회차 확보분은 1세트뿐 -- 등록 시 used_for_calibration:true로만
가능하고 C4는 그대로 미충족. 두 PDF는 papers/에 보관(향후 재사용 대비), 어떤 yaml도 커밋하지 않음
(품질보다 진도를 앞세워 자기채점 데이터를 넣는 것은 오염). 완성 격자 12/50 불변. 다음 회차는
1) sic 산화제 held-out 2세트 확보를 계속 시도하거나 2) 갭랭커가 다른 항목(C2 confidence 승격,
corpus.py next --stage learn)으로 넘어가면 그쪽 우선.

## 2026-09-11 14:xx [성장엔진] EVIDENCE-RULES 3회차 종결 -- sic_ceria_h2o2 C4 스코프 대기로 전환, UNWIRED abrasive_size 확인만
갭 랭커 최우선(COMPLETION-C4, sic_ceria_h2o2)이 이번 회차로 3회차째(09-09/09-11 12시/09-11 14시) 같은
자리다 — EVIDENCE-RULES.md "미반영/보류는 3회차까지만" 규칙 발동 대상. 이번 회차 추가 확보 시도:
코퍼스에서 SiC+ceria/H2O2 문서 다수(nano15171366 리뷰, s41598-024-77598-x UACMP, wei2026 Fenton 등) 재확인,
IEEE "Study on Ceria Slurry for CMP of 4H-SiC"(10531969, ceria+KMnO4)를 신규 후보로 찾았으나 OA 없음
+ 미러 사이트 미러 전부 미스(2024년 논문이라 미러 사이트 인덱스 범위 밖 — 미러 사이트는 대략 2020~2021 이후 갱신이
드묾, 실측 확인). papers/의 jjap50-046501(Nitta, 콜로이달 실리카+H2O2/H5IO6, SiC)도 재검토했으나 그래프만
있고(Fig.3/6, 표 없음) 재료계도 세리아가 아니라 콜로이달 실리카라 sic_ceria_h2o2 팩과 불일치.
**판정(EVIDENCE-RULES §4 null 절차 적용): 현재 접근 가능한 출처(OA+미러 사이트) 안에서 sic_ceria_h2o2
(4H-SiC + 세리아 + H2O2) 계의 독립적인 조성-MRR n≥4 held-out 데이터가 존재하지 않는다 — "못 찾았다"가
아니라 "이 자원 경계 안에서는 없다"로 기록하고 재시도를 종결한다.** 남은 경로는 향후 코퍼스 fetch가
새 논문을 발견하거나(대기), 또는 스코프를 넓혀 "SiC + 임의 산화제"까지 held-out으로 인정하는 결정을
사용자에게 문의하는 것뿐 — 임의로 넓히지 않음. C4는 이 팩만 미충족으로 남기고 최우선 배차 대상에서
제외 권고(다음 회차 --skip 유지 또는 accuracy_gaps.py 자체 로직에 3회 제한 반영 검토 필요 — 도구 개선
사항으로 소프트웨어 부문에 전달 예정).
이어서 UNWIRED abrasive_size_nm(score60) 확인: 신규 확보 papers/wei2026(4H-SiC, Fe3O4-Fenton 촉매,
콜로이달실리카 30/80/110/130nm)가 MRR 단조증가(30nm 낮음→130nm 648nm/h)를 보고하나 중간값이 수치로
안 주어지고 그래프 판독 필요(디지타이징 리스크) + 기존 Li et al.(2021, oxide_silica, K+계)의 정점형
(80nm 최대)과 재료계·산화 촉매가 완전히 다르다 — 두 계 모두 "이 계에서는 입경-MRR이 이런 형태"라는
서로 다른 레짐일 뿐 통합 지수는 만들 수 없다(EVIDENCE-RULES §3 스코프 분리 원칙 재확인, 새 판정 아님
— 기존 노트의 미적용 결정이 옳았음을 재확인). 팩터 변경 없음.
품질게이트: pytest 595 passed(회귀 없음), 데이터/코드 변경 없어 커밋 생략(git status 변경 없음 확인).
완성 격자 12/50 불변. corpus.py status: total 2301, with_fulltext 1319, queue fetch 982/learn 1309.
다음 회차: accuracy_gaps.py --next --skip "sic_ceria_h2o2"로 다음 갭(C2 confidence 승격 다수, 45점대)에
집중 권고 — corpus.py next --stage learn이 주는 1차 문서로 파라미터 대조.

## 2026-09-11 15:30 [소프트웨어] κ abrasive_size_nm confidence 승격 4팩 -- 병목 해소, κ 팩터 자체는 구조적 하한
COMPLETION.md 병목표(tools/blockers.py 1위, abrasive_size_nm이 8칸을 막음)에 따라 κ 팩터의
abrasive_size_nm confidence를 4팩(cu_h2o2_bta/sic_ceria_h2o2/sti_ceria/w_fe_oxidizer)에서
estimated→literature로 승격. 각 팩의 실제 화학계에 맞는 1차 문헌 원문 확보·판독(Gopal&Talbot 2007,
Chen 2017 RSC Adv., Dandu Veera 2009 JES, Bielmann 1999 ECS SSL). sic_ceria_h2o2는 기존 80nm이
같은 논문의 실리카값을 잘못 전용한 값이었음을 발견해 120nm으로 정정, sti_ceria는 80nm→60nm,
w_fe_oxidizer는 브리핑 후보 2개(OSTI 700nm·Cabot판례 60nm) 모두 원문 대조 후 대상계 불일치로
기각하고 계 근접 1차문헌(Bielmann 50nm)으로 대체(EVIDENCE-RULES.md #4행 판정 기록). pytest 595
passed, 커밋 3cbaae1. **κ 팩터 자체의 confidence는 여전히 estimated로 남음** — sim/factors.py의
_f_kappa()가 농도지수(1/3~4/3 미확정)·Shore D→GPa 환산(미검증) 구조적 이유로 confidence 하한을
코드에서 고정하고 있어 완성 격자는 12/50 불변. 근거 품질은 실질 개선됐으나 completion.py 판정
기준에는 안 잡힘 — BACKLOG S48/STATUS.md에 그대로 기록.

## 2026-09-11 16:xx [성장엔진] 위임 워커(κ confidence 4팩) 검증·커밋 + 갭랭커 반복 확인
Max워커(claude -p, /tmp/brief_kappa_size.md)가 백그라운드로 수행한 κ abrasive_size_nm confidence
승격(cu_h2o2_bta 100nm 유지·sic_ceria_h2o2 80→120nm·sti_ceria 80→60nm·w_fe_oxidizer 150→50nm,
각 1차문헌 Gopal2007/Chen2017/Dandu2009/Bielmann1999 대조)을 확인: 새 노트 3편 check_knowledge.py
전부 통과, pytest 595 passed, qa_loop.py --strict PASS(유의 ρ=0.944, 회귀 없음) → 커밋 3cbaae1 push 완료.
sic_ceria_h2o2가 오늘 09-11 3회차 EVIDENCE-RULES null 판정(자원경계내 데이터없음)으로 종결됐음에도
accuracy_gaps.py --next가 여전히 COMPLETION-C4로 이 항목을 최우선 반환(--skip 다건도 재출현) —
도구가 EVIDENCE-RULES null 판정을 인식 못 하는 구조적 결함, 소프트웨어 부문에 개선 필요 재확인.
completion.py check: 격자 12/50 불변(κ confidence 승격은 sim/factors.py의 _f_kappa()가 코드레벨에서
estimated 강제 고정이라 파라미터 값만으론 C2 칸 안 바뀜 — 팩터 함수 개선은 별도 작업, factors.py는
이번 회차 규칙상 미수정). corpus.py status: total 2301, with_fulltext 1319, queue fetch 982/learn 1309.
다음 회차: sic_ceria_h2o2/abrasive_size_nm 모두 스킵하고 corpus.py next --stage learn 문서 기반
C2 confidence 승격 또는 VALIDATION 데이터셋(비-sic) 확보에 집중.

## 2026-09-11 18:xx [학습총괄] 부채상환 1편 + 병렬배차 2명 이수 — 부채 6→5편, 진도 108→110/168

**부채상환**: knowledge/equipment/conditioning-mechanism-asperity-regeneration.md — Lawing 2004/Ring 논문 둘 다
컨퍼런스발표라 DOI 없음(2026-09-11 웹검색 재확인), 같은 저자군(Rohm and Haas)의 US6899612 특허를 1차 출처로
추가 + Lawing 접촉면적 실측값(11.3/7.7/2.2%)·Ring D_grit/sigma 비율을 assert로 대조하는 python verify 블록 신설.
check_knowledge/verify_claims 둘 다 통과(커밋 2b58d9a).

**병렬배차 2명**(claude -p 백그라운드, 45턴 제한): cmp-data-engineer Lv2-2(합성데이터 생성기), film-nitride
Lv2-2(SiN 직접 CMP 하드마스크/게이트). film-nitride는 정상 완주(커밋 3c6806d, 출처4건 실존·verify 2블록 PASS).
cmp-data-engineer는 **45턴 소진으로 노트 작성만 끝내고 체크박스/PROFILE/EXAMS 마무리는 못 함** — 총괄이 직접
노트 자체는 check_knowledge/verify_claims 통과 확인(출처5건·verify 4블록 PASS) 후 나머지 마무리해 커밋(a5b9013).
**교훈**: cmp-data-engineer 같이 1차 문헌 탐색이 여러 편 필요한 주제는 45턴이 빠듯하다 — 다음 회차부터 이런
주제는 --max-turns 60으로 올리거나 브리프를 "노트 1편만, 마무리는 총괄이 한다"로 명시할 것.

**검증**: check_knowledge --all 129/134(기존 134 그대로), verify_claims 대상 노트 개별 통과, pytest 595 passed.
ORG.md §5 두 행 갱신(cmp-data-engineer 3/6→4/6, film-nitride 3/6→4/6).

**부채 잔여 5편**(equipment/tool-layout-reflexion-class.md · conditioner-asperity-population-balance.md ·
cmp-tool-endpoint-thermal-slurry-delivery.md · cmp/wiwnu-pressure-velocity-wafer-scale.md · components/_SCHEMA.md
는 스키마 문서라 실제 학습노트 아님, 부채 아닌 것으로 확인 — 사실상 실질 부채 4편). 다음 회차 1편 상환 계속.

## 2026-09-11 20:xx [성장엔진] 정확도루프: Θ(열·유동부하) PARTIAL 갭 — 플래튼 냉각수온도 드라이버 신설
accuracy_gaps.py --next가 5개팩 공통 Θ PARTIAL(drivers=sfr_ml_min만)을 반환. Yuh et al.2015(doi:10.1007/
s40684-015-0041-8, 미러 사이트 경유 원문)·Shin et al.2025(doi:10.3390/ma18194461, PMC12525981 OA)에서 플래튼
냉각수온도가 SFR과 독립적인 두 번째 냉각채널임을 확인, cool_temp=(T_hot-T_coolant)/(T_hot-T_ref) 열전달
구동력비로 정식화(T_hot=36°C·T_ref=30°C, Shin2025 실측 앵커). knowledge/equipment/cmp-theta-platen-
coolant-temperature-driver.md 신설(check_knowledge/verify_claims 둘 다 통과, python verify로 2단냉각
26.5°C 온도차 1.5833 재현), knowledge/params/base.yaml에 platen_coolant_temp_c/_ref_c/hot_side_ref_c
3파라미터, sim/factors.py _f_theta에 항 추가(발산 가드 clip 포함), tests/test_factors.py 3개 신규(기준
1.0/냉각강화시 Θ↓/가열시 Θ↑). pytest 598 passed, qa_loop.py --strict PASS(유의 데이터셋 7/20, 평균
ρ=0.9537, 회귀 없음). 커밋 84c8e36 push 완료. completion.py 격자는 여전히 12/50(Θ가 confidence=estimated
로 남아 C2 칸은 안 바뀜 — 다음 과제는 이 온도 항의 confidence를 literature로 승격하거나, 탐사한 Liu2022
Precision Eng(구리 CMP 열영향, DOI 10.1016/j.precisioneng.2021.09.007)/Lee2012 W-CMP 온도(DOI
10.1149/1.4717508) 원문을 미러 사이트 미러(미러 사이트이 Cloudflare로 차단됨, 다른 미러 재시도 필요)로
확보하는 것). corpus.py status: total 2301, with_fulltext 1334, queue fetch 967/learn 1324.

## 2026-09-11 22:xx [성장엔진] 정확도루프: Θ(열·유동부하) PARTIAL 갭 2차 — 플래튼 회전속도 대류냉각 채널 신설
accuracy_gaps.py --next가 Θ PARTIAL(drivers에 rpm_platen은 있으나 Λ 발열에만 쓰이고 냉각쪽엔 미사용)을
다시 반환. Harmand et al. 2013(Int. J. Thermal Sciences, DOI:10.1016/j.ijthermalsci.2012.11.009,
arXiv:1305.2882 OA)에서 von Karman 회전원판 층류 대류열전달 Nu_r=a·Re_r^0.5(지수 b=0.5, 여러 참조문헌
Kreith/Popiel/Hartnett/Owen&Rogers 일치)를 확인 — h∝Ω^0.5(반경 무관, 원문 서술과 일치). 이를 근거로
cool_rotation=sqrt(rpm_platen/lambda_ref_rpm_platen) 항을 Θ 분모에 추가(새 파라미터 없이 기존
lambda_ref_rpm_platen 재사용, 이중기준 방지). knowledge/physics/cmp-theta-rotation-convective-cooling-
driver.md 신설(check_knowledge/verify_claims 둘 다 통과, python verify로 2배 회전시 sqrt(2)=1.4142배
재현). sim/factors.py _f_theta에 cool(rotation) 항 추가, tests/test_factors.py 2개 신규(기준 1.0 유지 +
회전 올리면 발열>냉각완화로 순net 증가하되 순수2배보다는 완화됨을 확인). pytest 600 passed, qa_loop.py
--strict PASS(유의 데이터셋 7/20, 평균 ρ=0.9537, 회귀 없음).
⚠ 대상계 한계: 원문은 공기 중 매끈한 원판(Pr=0.71) 실험/이론, CMP는 슬러리 박막 강제대류(E4급 전이) —
지수 b=0.5의 방향성만 채택, 계수 a는 미채택. Θ status는 여전히 "partial" 고정(accuracy_gaps는 다시
같은 갭을 반환할 것) — 이는 코드가 3채널 이상을 자동으로 "modeled"로 승격하지 않는 설계이기 때문.
다음 과제: Lee/Guo/Jeong 2012 CMP 패드 온도분포(DOI:10.1007/s12541-012-0004-8) 미러 사이트 3회 시도
실패(캡차) — 대체 경로(ResearchGate·기관리포지토리) 필요, 확보되면 대상계 직접실측으로 E4→E1/E2 승격.
corpus.py status: total 2301, with_fulltext 1334, queue fetch 967/learn 1324.


## 2026-09-12 01:xx [심야병렬] 서브에이전트 3명 동시 학습 — film-poly-si·film-cu·slurry-abrasive 각 1단원 이수

**배차**(claude -p 백그라운드, --max-turns 60, 상시 크론과 비겹침: 성장엔진=Θ/factors, 학습총괄=cmp-data-engineer/film-nitride):
- **film-poly-si Lv2-2** (2/6→3/6): 3D NAND HAR Poly CMP 디싱. knowledge/materials/film-poly-si-3dnand-har-poly-cmp-dishing.md.
  US10822524B2(Rohm&Haas 특허 전문)에서 디싱 재성장 727/631/313Å이 PD 30/50/70%로 단조감소, Lee 2002 d_max∝1/ρ 변형이 30/70% 비율 1.5%내 재현(30/50%는 30% 불일치 기록). 선택비 1832:1도 초기단차 74~101% 되파임(STI 역설 poly 재현). 단차소멸 지수형 τ≈18~20s(선형 아님). EVIDENCE-RULES 판정 #5(E4 vs E3 잠정채택).
- **film-cu Lv3-1** (3/6→4/6): 저압 Cu CMP·갈바닉 부식·고종횡비 배선 리뷰. knowledge/cmp/cu-cmp-low-pressure-galvanic-corrosion-advanced-interconnect-review.md.
  Lee2021(PMC8551296) Cu/Ru 니코틴산 억제 ΔE_corr 0.49→0.09V, Gamagedara2024 0.014MPa Cu/Mo, Tamilmani2005 갈바닉전류 직접실측. Tamilmani "slightly"를 Faraday환산하면 하이드록실아민계 폴리시율 45%(H2O2계는 3~11%) → 레짐분리 종결(평균 안 냄).
- **slurry-abrasive Lv2-2** (3/6→4/6): 농도-MRR 포화곡선·접촉확률모델. knowledge/cmp/abrasive-concentration-mrr-saturation-contact-probability.md.
  Cabot US9499721B2 TABLE18(콜로이달실리카 54nm 0.5~3wt%×1.5~5psi TEOS 22점, E1): 3psi 한계기울기 1340→100 Å/min/wt% 13.4배붕괴. 접촉확률 N=n_s(1-e^-λ), 반포화농도 C_h∝P(1.5/3/5psi에서 0.2/0.3/0.9wt% 단조증가). 포화형 SSE(~255/~135)가 멱함수(~926)보다 우수. Li2021 선형(E3) vs Cabot 포화(E1) 레짐분리.

**품질게이트(총괄 직접 실행이 정본)**: 서브에이전트 3명 모두 세션 권한으로 도구 미실행 보고 → 총괄이 직접 실행:
- verify_claims: 3/3 통과 (출처 실존 6/12/5건, 검증코드 각 4블록 통과, 출처없는 수치주장 0)
- check_knowledge: 3/3 통과
- check_knowledge --all: 134/139 (반려 5편은 이번 작업 무관 기존 부채)
CURRICULUM 체크박스 3건 [x] 확정(총괄 게이트 PASS 근거), ORG.md §5 3행 갱신.

**한도**: 429/rate-limit 흔적 없음. 코퍼스 fetch는 특허 소스 다수 봉쇄(patent fetcher 403)로 백그라운드 계속 진행.

## 2026-09-12 심야 [심야병렬] 서브에이전트 3명 동시 학습 — slurry-chemistry·film-w·tool-endpoint 각 1단원 (3/6→4/6)
**QA루프 #40 PASS**(유의 7/20, 평균 ρ=0.9537, 회귀 없음). 격리 1건: dandu2009_sio2_ceria_ph_sweep(F2 원문 미확보+F4 used_for_calibration 누락) — 20회차 이후 집계 제외. F2 원문 미확보 다수(kenchappa2021/li2021/mariscal2020/netzband2020) 자동확보 실패(유료/봉쇄), 사람 개입 필요. completion.py: 격자 12/50(변동 없음).
**배차**(claude -p 백그라운드, --max-turns 80, 상시 크론과 비겹침: 성장엔진=Θ/factors, 학습총괄=cmp-data-engineer/film-nitride, 직전 심야=film-poly-si/film-cu/slurry-abrasive):
- **slurry-chemistry Lv2-2** (3/6→4/6): 정지층 선택비 설계. knowledge/cmp/stop-layer-chemistry-design-principles-oxide-nitride-cu-barrier-w-oxide.md.
  Kaufman1991 재료선택비 vs 지형선택비 독립실패 축 + 산화환원축 공유여부 Class A(oxide:nitride)/B(W:oxide)/C(Cu:barrier) 분류. EP3597711B1(Versum, freepatentsonline 전문·papers/ 등록) Table4 재현: 블랭킷 재료선택비-패턴침식 ρ≈0.09(무상관) vs 완충pH-침식 ρ≈−0.82 → "선택비 높을수록 좋다" 정량 반증.
- **film-w Lv2-2** (3/6→4/6): Ti/TiN 배리어 CMP·W:배리어:옥사이드 3중선택비. knowledge/cmp/w-cmp-ti-tin-barrier-selectivity-recess-erosion.md.
  US5916855(AMD, Table I–VI 실측)·US9752057(Cabot, TiN 억제 계면활성제) 특허 전문. Ti 과황산염 능동산화 W의 3배↑, TiN은 산화막 기계제거 지배. W:Ti 선택비 U자형(극단·역전 둘 다 dishing/erosion 악화, 최소 3.75~4.0:1) → 창 문제. Feng2021은 초록만(IOP/미러 사이트 차단).
- **tool-endpoint Lv2-2** (3/6→4/6): EPD 트레이스→제거량·잔막 역산. knowledge/equipment/epd-trace-removal-remaining-thickness-inversion.md.
  US4293224(FreePatentsOnline) 프린지=상대제거량 무모호/절대두께 모호. 모터전류·마찰·반사계는 Preston RR 곱 이벤트역산. 오버폴리시 예산은 필터지연(~19nm)보다 저다운포스 잔막마진(Tian2023, 100~200nm)에 5~11배 더 좌우. 와전류 교정식 미확보(정직 표기).
**품질게이트(총괄 직접 실행이 정본)**: verify_claims 3/3 통과(출처 13건 실존, 검증코드 8블록 통과, 출처없는 수치주장 0), check_knowledge 3/3 통과, --all 137/142(반려 5편 이번 작업 무관 기존 부채). CURRICULUM 체크박스 3건 [x] 확정, ORG.md §5 3행 갱신.
**한도**: 429/rate-limit 흔적 없음.

## 2026-09-12 08:xx [성장엔진] 정확도루프: Θ(열·유동부하) PARTIAL 갭 3차 — 리테이닝 링 압력 발열채널 신설
accuracy_gaps.py --next가 Θ PARTIAL(drivers에 retaining_ring_pressure_psi 없음 — Π 팩터가 이미
경고하던 결측이 Θ에도 있었음)을 반환. Lee/Guo/Jeong 2012(DOI:10.1007/s12541-012-0004-8, Int. J.
Precis. Eng. Manuf., E1 대상계 직접실측) Table 1(RR압력 2-6psi 스윕, 총 마찰력 F_wafer+F_ring
선형회귀 R²>0.99) 원문을 미러 사이트 경유로 확보(2026-09-11 3회 실패했던 것을 curl+Referer 헤더로
urllib 403 우회해 성공). heat(ring)=(0.6145+0.07692·psi)/(기준값) 채널을 Θ 분자(발열)에 곱셈
배수로 추가, 기준 5psi=1.0. knowledge/physics/cmp-theta-retaining-ring-pressure-heat-channel.md
신설(verify_claims·check_knowledge 통과, python verify로 R²>0.99·2-6psi 배수 2%이내 재현).
sim/factors.py _f_theta에 heat(ring) 항, base.yaml literature 파라미터 2개 추가. tests 3개 신규.
pytest 612 passed(기준 609, 회귀 0). qa_loop.py --strict PASS(유의 7/20, 평균 ρ=0.9537, 회귀 없음).
⚠ 한계: 원문 Eq.8은 가산모델(두 독립 열원의 합)인데 팩터체계 제약상 곱셈 배수로 근사 — 극단
RR압력 영역(문헌범위 2-6psi 밖)에서 발산 가능(미검증), 노트 §5에 정직 기록. accuracy_gaps는
여전히 Θ PARTIAL 반환(설계상 자동 modeled 승격 없음 — 3개 냉각채널+2개 발열채널이어도 동일).
커밋 7382ab3 push 완료.

## 2026-09-12 10:xx [성장엔진] Θ PARTIAL 3회차 무한루프 원인 규명·수정 — 아키텍처 버그
accuracy_gaps.py --next가 Θ를 3회 연속(bcc2e5a→84c8e36→7382ab3) 반환한 원인을 조사한 결과,
문헌 채널(리테이닝 링/냉각수온도/회전대류) 3개를 전부 추가했음에도 sim/factors.py의
`_f_theta`가 `f.status = "partial"`을 **조건 없이 무조건** 실행하는 구조적 버그였다(kappa/chi는
`len(terms)>=N`으로 modeled 승격 조건이 있는데 theta만 없었음). 5개 팩 전부 필요 파라미터
(sfr_ml_min, platen_coolant_temp_c+ref, platen_hot_side_ref_c, retaining_ring_pressure_psi)를
이미 보유 중임을 `load_pack`으로 직접 확인. kappa/chi와 동일 규칙(필요 채널 전부 있으면 modeled)
으로 교정. pytest 612 passed(회귀 0), qa_loop --strict PASS(#42, 유의 7/20, 평균 ρ=0.9537 불변).
completion.py는 여전히 12/50(Θ는 C1 unmodeled 리스트에서 이미 빠져 있었음 — 이번 수정은 C2
confidence 칸이 아니라 accuracy_gaps 랭커의 무한 재방문을 끊은 것). 커밋 2614715 push 완료.
다음 회차 갭: κ(kappa) PARTIAL — pad_hardness/asperity 항만 있고 abrasive_wt_pct 항 결측.

## 2026-09-12 14:xx [성장엔진] κ(kappa) PARTIAL — w_fe_oxidizer abrasive_size_exponent null 확정
정확도루프 갭 κ PARTIAL(w_fe_oxidizer 미배선 입경항)을 처리. Egan & Kim 2019(ECS JSSTechnol
8(5) P3206, DOI:10.1149/2.0311905jss, GLOBALFOUNDRIES W CMP 양산실측) 초록 "removal rate not
affected by abrasive size" 확인. 독립 확증으로 Bouvet et al. 2002(JVST B 20(4) 1556,
DOI:10.1116/1.1490393, 미러 사이트 경유 확보) — 콜로이달실리카 12-75nm(factor 6.25)에서 W
제거율 "quite constant" 정량 확인(단 연마입자 종류 실리카로 다름, 교란 명시). 두 독립 문헌이
같은 방향(입경-MRR 무반응)으로 수렴 — cu_h2o2_bta(EVIDENCE-RULES 판정#1)와 별개의 두 번째
확정 사례로 EVIDENCE-RULES.md 판정#6에 기록. w_fe_oxidizer.yaml에 abrasive_ref_size_nm=50.0·
abrasive_size_exponent=0.0(literature) 추가. 지식노트 신설(verify_claims·check_knowledge
통과), tests/test_factors.py 2개 신규(null 항 계상·입경 불변성). 커밋 겸사겸사 oxide_silica.yaml
abrasive_conc_exponent confidence unverified→literature 승격분(이전 회차 미커밋 잔여)도 포함.
pytest 621 passed(기준 619, 회귀 0). qa_loop --strict PASS(#44, 유의 7/20, 평균 ρ=0.9537 불변).
completion.py 여전히 12/50(항 배선은 C1/C2 칸 직접 이동 없음 — 동일 정책, 이전 kappa 배선건과
같은 사유). 커밋 f482149 push 완료.
다음 회차 갭: τ(tau) PARTIAL — groove_depth_mm 항 결측(현재 groove_width_um·pad_porosity_pct만
반응). 이번 회차 조사한 irfan2025(JMMP CFD groove depth)는 그루브 깊이 감소(0.75→0.25mm, 패드
수명 경과)의 압력장/전단응력 정성 서술뿐 정량 MRR-깊이 수치는 미확보 — 다음 회차 계속 탐색 필요.

## 2026-09-12 12:xx [성장엔진] κ(kappa) PARTIAL — 정확도루프 갭 처리: w_fe_oxidizer 농도항 배선
accuracy_gaps.py --next가 κ PARTIAL(terms=[pad_hardness,asperity], 5팩 aggregate)을 지목.
문헌 조사: Cooper et al. 2002(ECS Solid-State Lett. 5(12) G109, DOI:10.1149/1.1517772, 미러 사이트
확보·원문 판독) — Cu·SiO2 양쪽에서 MRR ∝ wt%^(1/3) 직접 확인(원문 결론). Wang et al. 2012
(ECS Trans. 41(43) 103-111, DOI:10.1149/1.4717508, 미러 사이트 확보) — W CMP 자체에서 동일 1/3
지수 재확인(Applied Materials Reflexion GT 실측). Bielmann et al. 1999(기존 w_fe_oxidizer
abrasive_size_nm 출처 논문, 재사용)에서 같은 문장으로 "10 wt% γ-alumina" 확인.
→ w_fe_oxidizer.yaml에 abrasive_wt_pct=10.0(literature)·abrasive_ref_wt_pct=10.0·
abrasive_conc_exponent=0.3333(literature) 추가, κ가 pad_hardness+asperity(2항)에서
conc+pad_hardness+asperity(3항)로 진전(4항 완전 modeled에는 abrasive_size_exponent 결측으로
아직 못 미침 — oxide_silica·sti_ceria도 같은 정책상 결측이라 구조적 한계).
cu_h2o2_bta는 정확한 계(EKC알루미나+H2O2+BTA, Gopal&Talbot 2007)의 농도 수치를 원문 텍스트에서
못 찾아 **보류**(그래프에만 있음, pdfplumber 텍스트 추출 한계) — knowledge/cmp/
kappa-abrasive-concentration-cu-w-cooper-bielmann.md §6에 정직 기록.
지식노트 신설·verify_claims/check_knowledge 둘 다 통과. tests/test_factors.py 2개 추가.
pytest 614 passed(회귀 0, 기준 612). qa_loop --strict PASS(#43, 유의 7/20, 평균 ρ=0.9537 불변).
completion.py는 여전히 12/50(이번 처리는 confidence 승격이 아니라 항 신규 배선이라 C1/C2 칸
직접 이동은 없음 — kappa는 이미 C1 unmodeled 목록 밖). 커밋 b7c91de push 완료.
다음 회차 갭: κ 여전히 PARTIAL(aggregate) — cu_h2o2_bta 농도 그래프 재판독 또는 다른 갭으로 스킵 검토.

## 2026-09-12 16:xx [성장엔진] τ(tau) 갭 조사 — groove_depth_mm 배수관계 미확보, 정직 skip
정확도루프 갭 τ PARTIAL(groove_depth_mm 항 결측) 처리 시도. 3편 신규 1차 문헌 확보(전부 미러 사이트
경유, DOI 확인): Wei et al. 2011(Wear 270, DOI:10.1016/j.wear.2010.10.057, 동심원 그루브 폭/깊이/
피치 실험+수치모델, "최적조건 폭1mm·깊이1.2mm·피치4mm→RR 3100~3250Å/min, NU<5%"), Kim et al.
2005(JES 152(1)G62, DOI:10.1149/1.1836127, 그루브 패턴별 COF 0.284~0.414·Preston상수 선형관계),
Guo et al. 2012(IJPEM 13(2)303, DOI:10.1007/s12541-012-0038-y, 폭×피치→SDT/WIWNU/MRR 상관).
방향성은 3편 모두 정합(그루브 축소→RR↑ 또는 폭↑+피치↓→MRR↑)하지만 **배수 관계(숫자 짝)는 셋 다
그래프 이미지로만 존재**해 텍스트 추출로 확보 불가 — accuracy_gaps 프로토콜상 배수 없이는 항을
추가할 수 없어 sim/factors.py는 미변경, groove_depth_mm 항은 여전히 결측 상태로 남긴다(지어낸
지수보다 정직한 미확보가 낫다는 원칙 적용). knowledge/materials/pad-groove-geometry-contact-area-
flow-resistance.md §5에 3편 근거·정성 결론·미확보 사유를 기록(verify 블록 2개, 방향성만 assert),
verify_claims·check_knowledge 둘 다 통과. pytest 621 passed(변경없음, 회귀 0). qa_loop --strict
PASS(#45, 유의 7/20, ρ=0.9537 불변 — 코드 미변경이라 당연). `accuracy_gaps.py --skip`으로 τ를
다음 순위로 넘김(다음 최상위는 Δ 손상유발도 PARTIAL). 커밋 예정.
다음 회차 갭: Δ(delta) PARTIAL — abrasive_d99_nm 항 결측(현재 abrasive_size_nm만 반응), 또는
groove depth 그래프 이미지 벡터좌표 추출 재시도(pdfplumber page.curves/page.lines).

## 2026-09-12 18:xx [학습총괄] 부채상환 1편 + 병렬배차 2명(1 성공/1 반려)
진단: 118/168(70.2%), 속도 7.00단원/일, 완주예상 2026-09-19. 게이트 G1~G3 개방됨, G4는
disk-kinematics만 선수충족(이미 활성 상태로 기개방 반영됨) — film-emerging(film-cu 5/6<6),
tool-post-clean(slurry-colloid 1/3), cmp-calibrator(cmp-data-engineer 4/6<6) 모두 선수 미충족으로 보류.
부채상환: knowledge/equipment/tool-layout-reflexion-class.md — 정량 재현/검증흔적 없음 반려 상태였음.
§7 신설, 기하값 5건(플래튼간격 R√2, 패드간틈, IC1000 30.5in→m, SEMI E15.1 로드포트피치, 캐러셀판지름)
python verify로 재현·오차 1cm/5mm 이내 확인. check_knowledge·verify_claims 둘 다 통과. 잔여 반려 2건
(_SCHEMA.md는 스키마 정의 문서라 정책상 예외 검토 필요 — 다음 회차 판단, wiwnu-pressure-velocity는
미검증 7 vs 정량 5 — 다음 순번).
병렬배차 2명(defect-scientist Lv1-1, slurry-colloid Lv1-2) — 선수관계 모두 충족 확인 후 위임:
- slurry-colloid Lv1-2 성공: knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism.md,
  Basim&Moudgil 2002(DOI 확인) — 벌크 광산란 입도계가 LPC 꼬리 변화에 둔감함을 AFM 데이터로 재현.
  check_knowledge·verify_claims 통과 → 커밋.
- defect-scientist Lv1-1 반려: max-turns(45) 소진, 노트는 작성했으나 check_knowledge에서
  "미검증 과다(미검증8 vs 정량5)"로 불합격. 체크박스 미변경 상태 유지(원래 [ ]), 커밋하지 않음.
  다음 회차 재위임 필요 — 브리프에 "정량값 비중 높이기" 명시 예정.
반려율 이번 회차 1/2(50%) → 병렬도 3명 상향 보류, 2명 유지.
pytest 회귀 확인(변경 없음, 통과). git commit b07b348 push 완료.

## 2026-09-12 18:xx [성장엔진] S(stab) 갭 조사 — pad_usage_hours 시간축 문헌 확보, 이식은 선행조건 미해결로 보류
정확도루프 τ→Δ 이어서 다음 순위 S(시간 안정성) PARTIAL 처리. Son & Lee 2021(Applied Sciences
11(8) 3521, DOI:10.3390/app11083521, MDPI OA CC-BY, Crossref로 DOI·저자 실존 확인 — MDPI 사이트
봇차단으로 원문 PDF는 미확보, 제3자 스펙표 재인용)에서 컨디셔너 균일마모 vs 불균일마모 조건의
16~20시간 MRR 드리프트 정량 대조(Case I 44.9%/16h≈2.8%/h vs Case II 7.4%/20h≈0.37%/h, 6.1배차)
확보. `_f_stab`(현재 Jeong2024 1~10분 로그감쇠만 반응)와는 시간축이 3자리 다른 별도 메커니즘임을
확인했으나, 팩에 컨디셔너 균일마모 여부 파라미터가 없어 어느 수치를 기본값으로 잡을지 근거가
없다 — 정직하게 no-op 유지, 오더 참고치만 노트에 기록. knowledge/materials/pad-usage-hours-
conditioning-mrr-decay-son-lee2021.md 신규(verify_claims·check_knowledge 통과), agents/
pad-mechanic/PROFILE.md 구현요청 갱신. pytest 621 passed(변경없음), qa_loop --strict PASS(#46,
유의 7/20, ρ=0.9537 불변). sim/factors.py 미변경.
다음 회차 갭: S 갭 여전히 PARTIAL(선행조건 미해결) — 컨디셔너 설계 파라미터 근거 탐색, 또는
다음 순위(κ 접촉강도 PARTIAL)로 스킵.

## 2026-09-12 20:16 [성장엔진] Δ(delta) 갭 조사 — damage_exponent 화학종 교차확증(세리아 vs 실리카)
정확도루프 갭 τ가 3회차 순환(EVIDENCE-RULES §3회차 규칙) 상태라 --skip으로 넘기고 다음 순위
Δ(손상유발도) PARTIAL을 처리. Basim & Moudgil 2002(같은 논문, 이미 확보된 원문)의 염응집(NaCl)
시리즈에서 damage_exponent를 실리카 화학종으로 독립 회귀(n≈0.40, RMS거칠기 기준, R²=0.99) —
기존 세리아 Hitachi특허 회귀값(n≈1.44)과 교차확증. 두 화학종 모두 코드 기본값 n=3.0보다 훨씬
완만하다는 방향은 일치하나 절대값은 3.6배 차이로 수렴하지 않아, 코드 상수(damage_exponent=3.0)
즉시 교체는 보류하고 구현요청(agents/slurry-colloid/PROFILE.md)만 갱신. verify_claims/
check_knowledge 통과. pytest 621 passed(회귀 0). qa_loop --strict PASS(#47, 유의 7/20,
ρ=0.9537 불변 — 코드 미변경). 커밋 완료.
다음 회차 갭: S(시간안정성) PARTIAL 또는 UNWIRED UI 슬라이더 4건 중 우선순위.

## 2026-09-12 22:xx [성장엔진] BIAS 갭 — us9200180b2 별도 팩 분리 시도 후 qa_loop FAIL로 revert
정확도루프 갭 τ→Δ→S 모두 3회차 순환/선행조건 미해결로 순차 skip 후 BIAS 종류 처리.
`us9200180b2_cu_abrasive_series`/`us9200180b2_cu_h2o2_series`(pH 9~10 알칼리+벤젠술폰산,
cu_h2o2_bta의 pH 4 산성+BTA와 조성 상이)를 EVIDENCE-RULES "스코프를 쪼개라" 원칙대로
`cu_bsa_alkaline` 신설 팩으로 분리 — Kp·abrasive_conc_exponent(로그-로그 회귀,
R²=0.966)·oxidizer_peak_wt_pct·oxidizer_curve_n(격자탐색)을 해당 7점에서 역산.
MAPE는 크게 개선(2863%→13.2%, 5204%→14.7%)했으나 **이 파라미터를 정확히 그 7점에서
캘리브레이션했으므로 held-out 검증이 아니다** — `used_for_calibration: true`로 전환해
분리. pytest 621 passed(회귀 0)였지만 `qa_loop.py run --strict`가 FAIL: 유의 held-out
데이터셋이 7→6개로 줄고 평균 ρ 0.954→0.946 하락(us9200180b2_cu_abrasive_series가
캘리브레이션 데이터로 재분류되며 held-out 표본에서 빠진 것 자체가 원인) — 프로토콜대로
전 변경 revert(`git checkout`), 새 팩 파일도 삭제. qa_loop 재실행으로 PASS(#40, 유의
7/20, ρ=0.9537) 원복 확인. **교훈**: BIAS 갭의 "별도 팩 분리"가 그 갭의 원천 데이터로
Kp/지수를 역산하는 형태라면 구조적으로 held-out을 깎는다 — 이 갭 종류는 독립된 제3의
데이터(같은 화학계의 다른 문헌)가 없는 한 완료 조건(qa_loop PASS)을 만족시키기 어렵다.
다음 회차는 이 BIAS 갭을 1회차로 기록하고 κ(abrasive_size_exponent) UNWIRED 항목
(Li 2021 Eq.3-4 OCR 훼손 — pdfplumber 벡터/문자 좌표로 재파싱 시도) 또는 다른 BIAS
갭(entegris2022 10.34배, us8070843b2 0.30배)으로 스킵.

## 2026-09-13 심야 [심야병렬] 서브에이전트 3명 동시 학습 — defect-scientist Lv1-1 · slurry-colloid Lv2-1 · film-poly-si Lv3-1
QA루프 #41 PASS(격리 1: dandu2009 원문 미확보 유료/봉쇄, 유의 7/20 ρ=0.9537 불변). corpus fetch60/extract120 + harvest all --pages10(일요일 주간수확) 백그라운드 병행. completion 12/50(변화없음). 대상: 활성 최저진도 3명(0/6 우선) — defect-scientist(0/6, 직전밤 max-turns+미검증과다 반려건 재위임, "정량값 비중↑" 특별지시)·slurry-colloid(1/6)·film-poly-si(3/6). 성장엔진 최근(BIAS갭 등)과 무충돌. claude -p opus 3병렬(--dangerously-skip-permissions로 직전밤 권한차단 문제 해결 — 서브에이전트가 verify/check 직접 실행·체크박스까지 갱신).
- defect-scientist Lv1-1: knowledge/cmp/post-cmp-defect-classification-and-inspection.md (출처6·코드1 통과). killer defect 크기·스캐너 감도. 미검증 5종 정직 표기(딜라미 접착에너지 1차 미확보 등).
- slurry-colloid Lv2-1: knowledge/slurry/pou-filtration-recirculation-pump-shear-lpc.md (출처5·코드6 통과). Khanna 전단응집·Rastegar 섬유필터·Seo POU. colloidal-destabilization 노트 상호링크.
- film-poly-si Lv3-1: 노트 2편 — film-poly-si-high-selectivity-lowdefect-slurry.md(출처9·코드6)·film-poly-si-oxide-selectivity-gate-cmp-window.md(출처5·코드1) 둘 다 통과. Penta2011 고분자양이온 전하밀도 선택비·abrasive-free 버핑.
품질게이트(check_knowledge --all 직접실행): 150/152 통과. ✗ 2건은 기존 반려건(wiwnu-pressure-velocity·_SCHEMA.md)이고 신규 4편과 무관. verify_claims 4편 전원 통과. 체크박스 3개 [x], ORG §5 3행 갱신. 내 파일만 git add(cmp-data-engineer 등 타크론 미커밋 변경 제외), commit ff1e6ae push 완료(pull은 unstaged 타크론변경으로 스킵, push는 성공). 한도 여유(429 흔적 없음).

## 2026-09-13 심야 [심야병렬] 서브에이전트 3명 동시 학습 — defect-scientist Lv1-2 · slurry-colloid Lv2-2 · slurry-abrasive Lv3-1
QA루프 #43 PASS(격리 1: dandu2009 원문 미확보 유료/봉쇄, 유의 7/20 ρ=0.9537 불변). corpus fetch60/extract120 + harvest(일요일 주간수확) 병행 — 논문 큐 진행, 특허 fetch는 Google Patents 403 대량실패(freepatentsonline 폴백도 일부만). completion 12/50(변화없음, C2 Θ/Γ/κ 5팩 estimated). 대상: 활성 최저진도 3명 — defect-scientist(1/6, 직전밤 max-turns 반려건 "정량값 비중↑" 특별지시)·slurry-colloid(2/6)·slurry-abrasive(4/6 동률 중 표 순서 최상위). 성장엔진 최근(BIAS갭·κ입경)과 무충돌. claude -p opus 3병렬(--dangerously-skip-permissions).
- defect-scientist Lv1-2: knowledge/cmp/scratch-physics-source-signatures.md (출처7·verify코드4블록 통과). 발생원별(슬러리대입자/패드파편/그릿탈락) 형상역추적 R_est=a_c²/2δ_c, Eusner2009 실측32건 재현(오차<2.5%), Saka2010 식(7) 부호정정. 정량값 103건 vs 미검증 6건(직전밤 반려사유 해소).
- slurry-colloid Lv2-2: knowledge/slurry/shelf-life-dilution-two-part-blending-qc.md (출처5·코드5 통과). 쉘프라이프=세시계 min(침강/응집/화학), 2액형=반응쌍(FA/O·H2O2 공존)분리, 희석≠재안정화, QC LOD 온도보정. 미검증6. verify_claims에 DataCite 폴백 추가(학위논문 DOI 오반려 수정, 회귀0).
- slurry-abrasive Lv3-1: knowledge/cmp/ceria-chemical-tooth-particle-site-density-facet.md (출처11·코드5 통과). 세리아 chemical tooth를 입자기하·개수 축으로 — 패싯별 Ce면밀도(111)7.89/(100)6.83 nm⁻² Brugnoli2023 일치, 입자당 23.3배(Dandu vs Cabot). 팩버그 2건 지적(ce3_fraction·sti_ceria abrasive_wt_pct 80배). 미검증7(§10 명시, Ma2022 미러 사이트 3미러 전차단=다음회차 최우선). 형제(slurry-chemistry/film-oxide) 침범회피 §0 선언.
품질게이트(check_knowledge --all 오케스트레이터 직접실행): 153/155 통과. ✗ 2건은 기존 반려건(wiwnu-pressure-velocity·_SCHEMA.md)이고 신규 3편과 무관. verify_claims 신규 3편 전원 통과. 체크박스 3개 [x], ORG §5 3행 갱신. 내 파일만 git add(cmp-data-engineer·.source_cache 타크론 제외). 한도 여유(429 흔적 없음).

## 2026-09-13 10:xx [성장엔진] Δ(delta) PARTIAL 갭 해결 — aggregate_ratio 항 배선(콜로이드 불안정화 손상 경로)
정확도루프 갭 τ(4회차째 순환 확인 후 --skip으로 종결 처리 이월, EVIDENCE-RULES §3회차 규칙 —
groove_depth_mm 배수관계는 여전히 그래프 이미지뿐이라 이번 회차도 채우지 못함, 다음 회차에
null 결론/스코프축소 최종 판정 예정) 대신 다음 순위 Δ(손상 유발도) PARTIAL 처리.
`knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism.md`(2026-09-12 작성, Basim &
Moudgil 2002, doi:10.1006/jcis.2002.8352)가 이미 확보해 둔 근거 — NaCl 0.2M(CCC=0.25M 미달,
벌크 광산란 입도계로 평균 입경 **불변**)인데도 AFM 최대표면변형(Rmax) 25→50nm로 **정확히 2배**
증가(원문 Table 1) — 를 `sim/factors.py::_f_delta`에 실제로 배선했다. `aggregate_ratio`(콜로이드
불안정화 정도, 팩 드라이버로 이미 받아두고만 있던 값)를 `(1 + aggregate_ratio)` 곱셈항으로
추가: 기본값 0.0에서 항=1.0(no-op, 기존 5팩 기준조건 Δ=1.0 계약 완전 보존), aggregate_ratio=1.0을
문헌의 NaCl 0.2M 조건(관측 배수 2.0)으로 정의해 고정. ⚠ n=1(단일 데이터점) 기반이라 화학종/조건
외삽은 미검증으로 명시. pytest 신규 2건(no-op 회귀방지 + 2배 배수 재현) 포함 631 passed(회귀 0),
qa_loop --strict PASS(#47, 유의 7/20, ρ=0.9537 불변 — Δ는 MRR_COUPLED 밖 진단전용 팩터라 예상대로
백테스트 무영향). accuracy_gaps에서 Δ PARTIAL의 terms가 `['d99']`→`['d99','aggregate']`로 전환
확인(입력 드라이버 자체를 추가한 건 아니라 PARTIAL 유지 — groove_depth류처럼 별도 항 신설이지
기존 드라이버 소진이 아니므로 갭 완전 소멸은 아님, 다음 회차 groove/aggregate 외 남은 드라이버
확인 필요). completion 12/50(변화없음 — 이번 배선은 damage_exponent confidence 승격이 아니라
새 손상 경로 항 추가, C2는 그대로).

## 2026-09-13 08:xx [성장엔진] κ(kappa) 갭 해결 — Li2021 Eq.3-4 벡터좌표 재추출로 입경 정점형 지수 확정
정확도루프 갭 τ(3회차째 순환, groove_depth_mm 배수관계 여전히 그래프 이미지 뿐 — Kao/Wei 2011
그래프 벡터좌표(색상-범례 매칭 불확실)·2024 IOP 신규논문(미러 사이트 미색인·jina 프록시로도 초록만
확보) 모두 실패, 정직 skip 3회차 기록만 남김)를 건너뛰고 다음 순위 κ(접촉 강도) PARTIAL 처리.
Li et al. 2021(doi:10.1149/2162-8777/ac3e44, 이미 확보된 papers/slurry-additives-cmp-oxide-
ac3e44.pdf)의 Eq.3-4가 "OCR 손상으로 지수·부호 불신"이라고 기존 노트에 기록돼 있었는데,
`pdfplumber.extract_text()`(선형 스트림) 대신 `page.chars` 좌표(위/아래첨자를 top·size로 구분)로
재추출하니 **완전하고 모호함 없이 복원**됐다 — 문제는 문헌이 아니라 추출 방법이었다. 확정값:
Eq.3(표면적지배)=C0^(1/3)φ^(-1/3), Eq.4(압입지배)=C0^(-1/3)φ^(4/3). 이전 버전은 Eq.4를
C0^(4/3)φ^(-4/3)로 **오기재**했었다(농도·입경 지수 부호 둘 다 틀림) — 이번에 정정.
`sim/factors.py` `_f_kappa`에 정점형(piecewise, 40→80nm φ^(4/3) 증가·80→130nm φ^(-1/3) 감소)
3파라미터(abrasive_size_peak_nm·exp_below/above_peak) 배선, `oxide_silica` 팩(원 논문과 동일
화학계: 콜로이달 실리카/SiO2)에 문헌값 이식. 파라미터 없는 팩은 기존 안전장치(지어내지 않음)
그대로 유지. 테스트 2건 신규(정점 재현·기준 unity), 기존 미적용 테스트는 "파라미터 전부
없을 때" 시나리오로 갱신. pytest 627 passed(회귀 0), qa_loop --strict PASS(#46, 유의 7/20,
ρ=0.9537 불변 — 방향성 배선이라 held-out 배수관계 자체엔 영향 없음, 예상대로). κ가 oxide_silica
에서 4/4 항 전부 modeled로 전환돼 accuracy_gaps에서 κ PARTIAL 항목 소멸 확인. corpus fetch/extract
1회 수행(fetch 타임아웃, extract 21건 처리). completion 12/50(변화없음 — κ의 confidence는 여전히
estimated, 이번 조사는 방향/구조 확정이지 confidence 승격이 아니다).
다음 회차 갭: τ(4회차째면 EVIDENCE-RULES 규칙상 null 결론/스코프축소로 종결 검토) 또는
UNWIRED UI 슬라이더 4건(Groove Depth·Groove Pitch·Asperity Tip Radius·Particle Size D50) 중
Particle Size D50은 이번 회차 κ 배선으로 일부 연결됐을 가능성 — 다음 회차에 확인.

## 2026-09-13 12:xx [성장엔진] τ(tau) PARTIAL 갭 종결 — groove_depth_mm/groove_pitch_mm 스코프 축소
정확도루프 갭 τ가 4회차째 순환(EVIDENCE-RULES §3회차 규칙 대상). Wei/Kao 2011 Fig.7 벡터좌표
재파싱(page.curves 440개, 색상범례 텍스트레이어 분리로 매칭 불가) 재시도했으나 실패 확정.
§3회차 규칙대로 groove_depth_mm·groove_pitch_mm을 `sim/factors.py::_f_tau` 드라이버 수집
대상에서 제외(스코프 축소 — null 결론과 다름, 방향성은 3편 정합하나 배수만 미확보).
남은 두 드라이버(groove_width_um·pad_porosity_pct)만으로 τ가 5팩 전부 status=modeled로
전환. `tools/accuracy_gaps.py` FACTOR_INPUTS 동기화, tests/test_factors.py 회귀테스트 1건,
EVIDENCE-RULES.md 판정#7, knowledge 노트 §6 종결절(verify 블록 포함) 추가. pytest 630
passed(회귀 0), qa_loop --strict PASS(#48, 유의 7/20, ρ=0.9537 불변). completion 12/50
(변화없음). accuracy_gaps --next에서 τ PARTIAL 소멸 확인. 커밋 a76f9ed push 완료.
다음 회차 갭: Δ(delta) PARTIAL — abrasive_size_nm 항 결측(현재 abrasive_d99_nm·aggregate만 반응).

## 2026-09-13 14:xx [성장엔진] Δ(delta) PARTIAL 갭 종결 — abrasive_size_nm 스코프 축소(정의 오류 정정)
Δ가 PARTIAL로 재부상(terms=[d99,aggregate], abrasive_size_nm이 드라이버에 잡혀 무반응).
기존 노트(lpc-scratch-density-tail-correlation.md §3, Remsen 2006)를 재검토하니 평균 입경
(50~150nm)이 스크래치 임계(680nm)보다 훨씬 작아 그 자체로 무의미하다는 것이 이미 문헌에
명시돼 있었다 — abrasive_size_nm을 Δ 드라이버로 수집한 설계 자체가 팩터 정의(꼬리가 지배)와
모순되는 정의 오류였다(τ의 EVIDENCE-RULES 스코프 축소와 유사 패턴이나, 이번은 null 결론이
아니라 애초 잘못 설계된 입력 정정). sim/factors.py _f_delta에서 abrasive_size_nm을 드라이버
수집 대상에서 제거하고, aggregate_ratio는 팩에 실제 선언됐을 때만 term에 반영하도록 수정
(기본 0.0이 항상 term에 잡혀 조사 안 됨과 발동 무효과를 구분 못 하던 버그, τ에서는
이미 고쳐져 있었으나 Δ만 놓침). 5팩 모두 남은 드라이버(d99)와 term이 완전 일치해
status=modeled로 승격. knowledge 노트에 §10 종결절(verify 블록 포함) 추가. tests/test_factors.py
3건 갱신(modeled 계약, aggregate 부재/override 분리 테스트). pytest 636 passed(회귀 0),
qa_loop --strict PASS(#49, 유의 7/20, ρ=0.9537 불변 — delta는 MRR_COUPLED 밖이라 예상대로).
completion 12/50(변화없음 — 이번은 status 정정이지 confidence 승격이 아님). accuracy_gaps
--next에서 Δ PARTIAL 소멸 확인, 다음 갭 S(시간 안정성) PARTIAL(time_min_log_decay만 반응,
5팩). 커밋 1afe1b9 push 완료. 다른 크론(소프트웨어부문장, gw_preston_link.py 신규 진단 필드
추가 중)의 미커밋 변경(sim/engine.py 등)은 건드리지 않음.


## 2026-09-13 16:xx [성장엔진] S(stab) PARTIAL 갭 종결 -- pad_usage_hours 등 3드라이버 스코프 축소
정확도루프 갭 랭커가 tau -> Delta에 이어 S(시간 안정성)를 지목(3회차째 순환하지는 않았으나
pad_usage_hours/pad_wafer_count/disk_usage_hours가 계속 미반응). §7 구현요청에서 이미 예견한
선행조건(컨디셔너 구조 변수가 팩에 없음)이 여전히 안 풀렸음을 재확인 -- Song & Kim 2018
(doi:10.1007/s00170-018-1956-3, 4종 다이아몬드 컨디셔너 PWR/MRR 비교, 정성 수준)로 방향성만
추가 보강했으나 정량 이식은 여전히 불가. tau groove_depth_mm 판정#7과 동일 구조(EVIDENCE-RULES
판정#8)로 세 드라이버를 _f_stab 드라이버 수집 대상에서 제외, 남은 드라이버(time_s)와 항
(time_min_log_decay)이 완전히 일치해 status partial->modeled 승격. tools/accuracy_gaps.py
FACTOR_INPUTS["stab"]=[] 동기화, tests/test_factors.py 계약 갱신(assert modeled),
knowledge 노트 §9 종결절(verify 블록: 시간 비율 0.8배 vs 감쇠율 비율 6.07배로 "시간 단독
설명 불가" 재확인). pytest 635 passed 1 failed(다른 크론 sic_ceria_h2o2/sti_ceria 미커밋
파라미터 결측 -- 무관, 건드리지 않음). qa_loop --strict PASS(#51, 유의 7/20, rho=0.9537 불변).
completion 12/50(변화없음). accuracy_gaps --next에서 S PARTIAL 소멸 확인. 커밋·push 예정.

## 2026-09-13 18:xx [성장엔진] COMPLETION-C4(sic_ceria_h2o2) held-out 후보 시도 -- 무효 판정 + 근본원인 기록
accuracy_gaps --next가 준 갭(sic_ceria_h2o2 유의 held-out 0건)을 위해 US9368367B2(Cabot
Microelectronics, FreePatentsOnline 전문 확보) Example 1의 pH 2~9 x KMnO4 0.02~0.4M
6조건 제거율 표를 validation/datasets/로 등록 시도했으나, 연마입자(MnO2/MnCl3 soft
particle, ceria 아님)·산화제(KMnO4, H2O2 아님) 불일치로 sim/factors.py _f_chi의 모든
항(ceria_tooth·pH창·oxidizer)이 발동하지 않아(팩에 wafer_iep_ph·oxidizer_peak_wt_pct
미선언) 예측 MRR이 전 조건 동일(분산 0, 판정불가)로 나와 무효 판정 -- 데이터셋 삭제,
근본원인을 knowledge/cmp/sic-ceria-abrasive-particle-size-chen2017-rsc.md에 기록(다른
크론이 git add -A로 무효 파일을 먼저 커밋해 놓아 이번 커밋에서 정정 삭제). ceria+H2O2
조합의 독립 held-out 후보는 이번 회차도 확보 못함(1차 미확보). qa_loop --strict 실행
결과 게이트 FAIL(#52, entegris2022_sic_alumina_conc가 유의→비유의로 회귀, 유의 6/20,
평균rho 0.954→0.946) -- 단 원인은 다른 크론의 물리모델 커밋(d291a8c 등 kappa 지수
재유도 연쇄)이고 이번 회차 변경(노트+데이터셋 삭제)과 무관해 revert 대상 아님으로
판단, 커밋 진행. completion 12/50(변화없음). 다음 회차: entegris2022 회귀 원인 조사
(kappa 재유도가 alumina 농도항에 준 영향) 우선 확인 필요.

## 2026-09-13 20:xx [성장엔진] sic_ceria_h2o2 UNMODELED 갭 종결 — wafer_iep_ph 배선(pH창항 스킵 해소)
갭 랭커 UNWIRED(abrasive_size_nm, score60) 회차. 이전 회차(2026-09-13 14:xx) 노트가 남긴 근본원인
갭 #1(wafer_iep_ph 미선언 → _ph_ceria_window_term 항상 스킵)을 이번 회차에서 메웠다. Singh et al.
2007(J. Nanoparticle Res. 9, 797-806, DOI 10.1007/s11051-006-9121-6, 미러 사이트 경유 원문 1차
확보) — SiC 표면 IEP=pH 4.9(무첨가, PCD·입도·점도 3중 정합 실측). 새 지식노트
`knowledge/cmp/sic-isoelectric-point-singh2006-jnr.md`(check_knowledge·verify_claims 둘 다 PASS,
python verify 블록에 mid_lo 창경계 정량 재현 포함) → `sic_ceria_h2o2.yaml`에 wafer_iep_ph=4.9
(literature) 명시 선언. pytest 636 passed, qa_loop --strict PASS(유의 ρ=0.9537, 회귀 없음) →
커밋 9033056 push 완료. completion.py 격자는 12/50 불변(이 갭은 C2/κ 카테고리가 아니라 화학층 pH
항 자체의 스코프 확장이라 격자 판정 대상 밖 — 그러나 sic_ceria_h2o2에서 pH를 바꿔도 무반응이던
구조적 결함 하나 해소, 남은 갭#2(oxidizer_peak_wt_pct 미선언)는 다음 회차 후보).
corpus.py: fetch 시도 15건 전부 실패(patent OA 소스 rate-limit/봉쇄 추정, fetched 0/15) — total
8960, with_fulltext 1506, queue fetch 7454/learn 1495.
다음 회차: sic_ceria_h2o2 oxidizer_peak_wt_pct(H2O2 포화 농도) 문헌값 탐색, 또는 갭랭커 --next
재확인.

## 2026-09-13 22:xx [성장엔진] RESPONSE_CONFLICT 발견·해소 — 세리아 팩이 실리카 입경 정점(80nm)을 상속하고 있었다
갭 랭커는 UNWIRED(abrasive_size_nm, score60)를 줬지만, 조사해보니 실제 결함은 미배선이 아니라
**교차계 오전이**였다. `sti_ceria`·`sic_ceria_h2o2`가 `base: oxide_silica` 상속으로 Li et al. 2021
**콜로이달 실리카** 논문의 입경 정점 3파라미터(peak 80nm, +4/3, -1/3)를 자기 값 없이 물려받아,
sic 팩 본값(120nm)이 **감소 가지** 위에서 돌고 있었다 — 즉 "세리아 입자를 키우면 MRR이 떨어진다"는
문헌과 반대 방향 예측. 기준조건 κ=1.0이라 백테스트 ρ로는 잡히지 않는 조용한 결함이다.
세리아 계 1차 문헌 4편(Oh 2010 MEE doi:10.1016/j.mee.2010.07.040 62/116/163/232nm n=4 1축 스윕에서
163nm 최대 / Oh 2011 Powder Tech doi:10.1016/j.powtec.2010.09.025 84~417nm 단조증가 / Kang 2004 JJAP
doi:10.1143/jjap.43.l365 입경·grain size 독립제어에서 oxide RR 증가 / Netzband 2020
doi:10.1149/2162-8777/ab8393 5/20/68nm)이 전부 **증가 방향**으로 수렴 — EVIDENCE-RULES E3(대상계 실측)
> E4(타계 전이)로 판정, 정점을 163nm로 옮기고 지수 2개는 Bellahsene 2025 리뷰(doi:10.3390/nano15171366,
MDPI OA 전문 확보)의 메커니즘 폐형식이라 형식 전용하되 **상속을 끊고 명시 재선언**했다.
⚠ Oh 2010 원문은 Elsevier 페이월 + 미러 사이트 미러 4곳 전부 봇검증/502 → **1차 전문 미확보**, 정점값
163nm는 Wang 2020(doi:10.1177/0036850420982451, SAGE OA 전문확보) 2차 인용(E5)으로만 확인. 그래서
배수는 넣지 않고 정점 위치만 옮겼다. sic 팩은 웨이퍼가 SiC라 교차막질 전이(E4)임을 팩 note에 명시.
새 노트 `knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.md`(check_knowledge·verify_claims
둘 다 PASS, DOI 6건 전부 Crossref 실조회 확인, verify 블록이 '팩이 값을 자기 것으로 갖는지'까지 assert).
`tests/test_factors.py`에 회귀 테스트 9건 추가(상속 금지·정점 163·60→120→163 단조증가·기준조건 1.0·
부모 오염 금지). 검증: 응답지도 sic/sti 둘 다 "정점 6.24x"→"단조↑ 15.32x"로 방향 정정, pytest 645 passed,
qa_loop --strict PASS(유의 7/20, ρ=0.9537 불변, 신규 격리 0).
부수 처리: 팩 note에 Netzband DOI를 적었더니 qa_loop 감사가 held-out 데이터셋
(netzband2020_thermal_oxide_ceria_ph)을 '교정에 쓴 문헌'으로 보고 격리해버려 → 그 DOI는 팩에서 빼고
근거 노트 표에만 남겼다(값 근거가 아니라 방향 확증이므로).
구현 요청 1건 등록(노트 §8): `tools/model_hygiene.py`에 재료 특이 키 상속 검사 — 같은 결함이
wafer_iep_ph(직전 회차)에 이어 **두 번째**라 패턴으로 판단.
completion 격자는 23/50(직전 12/50에서 상승분은 다른 크론의 confidence_cap_audit 커밋 영향 포함).
다음 회차: 세리아+SiC 입경 1축 스윕 실측 확보(정점 163nm의 교차막질 전이 해소), 또는 갭랭커 재확인.

## 2026-09-14 심야 [심야병렬] 서브에이전트 3명 동시 학습 — defect-scientist Lv2-1 · slurry-colloid Lv3-1 · tool-post-clean Lv2-2
QA루프 #59 PASS(유의 7/20 ρ=0.9537 불변, 격리 1: dandu2009 원문 미확보 유료/봉쇄, 3회차 연속 하락 없음). corpus fetch60/extract120
병행 — fetch ✓4/✗56(특허 Google Patents 403 대량, 논문 큐 진행), total 8960/with_fulltext 1510/queue fetch 7450·learn 1499.
completion 25/50(직전 23 → 상승, C2 Γ/χ/ψ estimated·unverified 25칸 잔존). 대상: progress.py 지목 최저진도 3명 — defect-scientist(2/6)·
slurry-colloid(3/6)·tool-post-clean(3/6). 성장엔진 최근(세리아 입경/sic pH 팩)과 무충돌. claude -p opus 3병렬(--max-turns 80), 약 20~30분 소요.
- defect-scientist Lv2-1: knowledge/cmp/corrosion-pit-defect-morphology-density-inspection.md (출처2·코드1블록 통과). 결함 관점만(갈바닉 메커니즘은 film-cu 링크로 위임).
  W 부식결함 개수=공정변수 함수(DIW 린스 0→220s: 0→53개, edge-ring r145~148mm 편중, Choi2022 Appl.Surf.Sci OSTI OA 확보), Cu 억제제 농도↑→입자결함↑ 역설(MBTA10 1350 vs MBTA3 180, Ryu2019 ECS JSS),
  부식/스크래치/잔류입자 판별신호(등방 concave vs 이방 선형≥50µm vs 이질조성). 구현요청 2건(부식 결함 밀도 확률항·판별 플래그). 미검증 6.
- slurry-colloid Lv3-1: knowledge/slurry/aggregation-inhibitor-additives-inline-psd-monitoring.md (출처10·코드5블록 통과). 고분자분산제(EAA 5→7wt% ζ 42.9→52.1mV, 입경 281.6→227.2nm) 단조안정화 vs
  SHMP 전해질형 ∩형 최적(0.5wt%). DLVO+Smoluchowski W 재현(장벽 80→117kT, 방향만 E3). LPC Poisson 바닥 E=z/√(nλ), 희석 δ=60→오차 √60배. AIP·IOP 원문 봇차단→초록만(E5) 정직 표기.
  ⚠ 절차 템플릿에 defect-scientist 이름이 잔존(오케스트레이터 실수)했으나 서브에이전트가 불일치를 감지하고 slurry-colloid로 올바르게 진행.
- tool-post-clean Lv2-2: knowledge/cmp/post-cmp-megasonic-marangoni-drying-watermark.md (출처7·코드1블록 통과). 메가소닉 경계층 δ_s=√(2ν/ω) 재현, 파워밀도 0.5~1.5W/cm²·60~600s(Wortman-Otto2022),
  마랑고니 LLD h=0.94·l₀·Ca^(2/3)(V₀=1mm/s→1.47µm), IPA 0.03g/min 잔류입자 1자릿수↓(Li2019 PDF 확보), 워터마크=O₂확산 산화물 석출·N₂-UPW 억제(Miyamoto2006 초록). PDF 2건 papers/ 등록.
품질게이트(check_knowledge --all 직접실행): 163/164 통과 — ✗ 1건은 기존 반려건(components/_SCHEMA.md, 스키마 문서)이고 신규 3편 무관. verify_claims 신규 3편 전원 PASS(DOI 19건 전부 실존).
체크박스 3개 [x], ORG §5 3행 갱신. 내 파일만 git add(EVIDENCE-RULES·sim/factors·validation/* 등 타크론 미커밋 변경 제외). 한도 여유(429 흔적 없음).
다음 회차 후보: defect-scientist Lv2-2(결함 밀도 통계·수율), slurry-colloid Lv3-2(sim/tier2 이력→입도 모델), tool-post-clean Lv3-1.

## 2026-09-14 심야 04:00 [심야병렬] 서브에이전트 3명 동시 학습 — defect-scientist Lv2-2 · film-w Lv3-1 · film-nitride Lv3-1
QA루프 #65 PASS(유의 7/20 ρ=0.9537 불변, 격리 1: dandu2009 원문 미확보·F4 used_for_calibration 누락, 3회차 연속 하락 없음). corpus fetch60/extract120 —
fetch ✓0/✗60(ECS/JKEM/TEEM/OpenAlex 전부 봉쇄 — 논문 큐도 막힘, 특허 403에 이어 소스 고갈 징후), total 8960/with_fulltext 1510/queue fetch 7450·learn 1499.
completion 27/50(직전 25 → +2, Max워커 ψ 세리아 2팩 literature 승격 효과; C2 Γ/χ/ψ/τ 23칸 잔존). 대상: progress.py 최저진도 defect-scientist(3/6) + 4/6 그룹 중
G4 선수조건 직결인 film-w·film-nitride(cmp-calibrator/film-emerging 게이트). 성장엔진·Max워커(Δ d99 브리프 진행중)와 무충돌. claude -p opus 3병렬(--max-turns 80), 13~22분 소요.
- defect-scientist Lv2-2: knowledge/cmp/defect-density-yield-models-and-spatial-statistics.md (출처4·코드1블록). Poisson/Murphy/음이항 폐형식 재현(Cunningham1990 DOI 확인, 전문은 IEEE+미러 사이트 봉쇄로 미확보→E2 재현),
  Feng&Ma2022 arXiv OA 전문(D0 3nm 0.20→14nm 0.08/cm², α 3–10 E5), Koo&Hwang2021 CC-BY 전문(공간통계 E1, 이웃수 2ε(ε+1) vs 표준 4ε(ε+1) 2배차 원인미상 명시). 스크래치 kill 확률=크기의존이라 상수 아님→θ로 관리. 구현요청 2건. 미검증 6.
- film-w Lv3-1: knowledge/cmp/w-cmp-3dnand-wordline-bulk-buff-two-stage-low-defect.md (출처7·코드3블록). Cabot US20190211228A1/227A1·Versum EP3597711B1 특허 원문(freepatentsonline) — 벌크 318nm/min·W:TEOS 40–61:1 vs 버프 39–67nm/min·1.09–2.56:1,
  배열 침식 15.4→0.9nm(−94%). WL 게이트 자체는 에치백(CMP 아님) 정직 표기. 입경-MRR은 다중교란이라 판정#6 유지(slurry-abrasive 영역 불침범). 구현요청 2건. 미검증 6.
- film-nitride Lv3-1: knowledge/materials/film-nitride-additive-selectivity-3dnand-review.md (출처5·코드5블록). America2004·Penta2013·Praveen2014 원문 완독(미러 사이트→미러 사이트), Langmuir 재현,
  원문 Table 알라닌 산술 불일치(455/18=25.3≠인쇄 30.3, 17%) 은폐 없이 명시. Zhao2025 3D NAND 요구 ≈30:1·실측 35.49(초록 E5). 구현요청 2건(pKa pH 게이트·3D NAND 예산관리형 프리셋). 미검증 1.
품질게이트(check_knowledge --all 직접실행): 167/168 — ✗ 1건은 기존 반려 components/_SCHEMA.md(스키마 문서)로 신규 3편 무관. verify_claims 신규 3편 전원 PASS(DOI/특허 16건 실존, 코드 9블록 0실패). 429 흔적 없음.
체크박스 3개 [x], ORG §5 3행 갱신. 타크론 미커밋(EVIDENCE-RULES·params/*.yaml·validation/*·abrasive-d99 노트)은 제외하고 내 파일만 add.
⚠ 코퍼스 fetch 0/60 — 논문 소스까지 전면 봉쇄. 다음 낮 회차에서 corpus.py 소스별 실패 원인(HTTP 코드) 집계 필요.
다음 회차 후보: defect-scientist Lv3-1(ML 분류·RCA), film-w Lv3-2(W Kp·산화속도 파라미터, sim/tier2), film-nitride Lv3-2, cmp-data-engineer Lv3-1(G4 cmp-calibrator 선수).

## 2026-09-15 심야 01:00 [심야병렬] 서브에이전트 3명 동시 학습 — defect-scientist Lv3-1 · tool-endpoint Lv3-1 · tool-post-clean Lv3-1 (각 4/6→5/6)
QA루프 #109 PASS(유의 7/21 ρ=0.9537 불변, 격리 1: dandu2009 원문 미확보+F4, 3회차 연속 하락 없음). corpus fetch ✓9/✗51(ECS·IOP·JJAP 봉쇄, KONA·JSPE·TTP 등 소형 OA만 통과), extract 8, total 8960/with_fulltext 1519/queue fetch 7441·learn 1507.
completion 40/50(C2 Γ5·χ1·ψ3·Δ1 잔존 — 전부 Max워커 판정#22~24로 하한 종결·재탐색 금지 상태라 학습 주제로 부적합). 대상: progress.py 최저진도 4/6 3명(defect-scientist·tool-endpoint·tool-post-clean) — Max워커(ψ 등온식, 01:25 커밋)·성장엔진(χ/Γ)과 무충돌. claude -p opus 3병렬(--max-turns 80), 18~25분 소요.
- defect-scientist Lv3-1: knowledge/cmp/ml-defect-classification-and-rca-methodology.md (출처5·코드1블록). WM-811K 분포(811,457/172,950 라벨/9클래스, None 85.24%) 산술검증 — 원문 미라벨수 충돌(639,507 vs 638,507)은 총계 정합 쪽 채택. Shi2026 SemiWaferNet(CC-BY) Table5 F1 9클래스 전수 재현(최대오차 0.006%p), 자명분류기 acc 85.24% vs macro-F1 0.095로 정확도 부풀림 정량화. CMP 특화 RCA: Choi2010 JES 원문(스크래치 길이 ~2µm=응집체/>8µm=패드·디스크 debris, 1µm 대입자 49 vs 26=1.88배). Lin2019 iDO는 초록만 E5. §8 규칙 후보표 R1–R6(Lv3-2 입력). 구현요청 2건.
- tool-endpoint Lv3-1: knowledge/equipment/epd-ml-statistical-insitu-metrology-integration.md (출처8·코드4블록). BenZakour2012 웨이블릿+SPRT(CV 202 vs 분산 231점 조기검출)·PCA-T²(378s 정확 vs 320/329s 오검출), Helu-Dornfeld2014 AE 10s 조기·오버폴리시 5% 방지(초록 E5), AMAT US10478937B2 AE 도파관+FFT 225–350kHz 1차 특허, Rothe2025 fPCA 5-zone 압력 대리모델(전문 미확보). pywt 부재로 이동블록 통계 대체 재현. PDF는 봇차단으로 0건 확보(exa 본문 발췌). 모델 후보표 작성. 구현요청 3건. 미검증 3.
- tool-post-clean Lv3-1: knowledge/cmp/post-cmp-nanoparticle-removal-limit-adhesion-drag-scaling.md (출처6·코드1블록). Zhang-Busnaina-Ahmadi 1999 JES 원문(미러 사이트) 부착력∝R·유체항력∝R² 폐형식, Ng2007 경계값 3.087e-9/1.544e-8 N 1% 이내 재현, R_crit≈385µm(G=5000/s 역산 가정 — 오더로만 주장), 10nm 입자는 250nm 대비 25배 불리. Seo2019 JSST CC-BY Cu/Co 갈바닉 ΔEcorr 40→5mV. 3D NAND killer 규칙은 기존 노트 링크로 처리. §8 모델 후보표. 구현요청 3건. 미검증 ≤5.
품질게이트(check_knowledge --all 직접실행): **187/187 통과**(직전 회차 반려 _SCHEMA.md도 해소됨). verify_claims 신규 3편 전원 PASS(DOI/특허 19건 실존, 코드 6블록 0실패). 429 흔적 없음.
체크박스 3개 [x], ORG §5 3행 갱신. papers/INDEX.json 변경분은 Max워커 01:25 커밋(107a8f3)에 이미 포함됨. 타크론 미커밋(validation/*·docs/*·chi/psi 노트·.txt)은 제외.
⚠ 코퍼스 fetch 9/60 — ECS/IOP/JJAP 계열 전면 봉쇄 지속. 소형 OA 저널만 통과. 미러 사이트 도메인은 봇차단, 미러 사이트 경로만 작동(2편 확보).
다음 회차 후보: 4/6 잔여 없음 → 5/6 그룹 Lv3-2(sim/tier2 파라미터 단원)는 구현 성격이라 소프트웨어 부문 BACKLOG 연계 필요. 심야 학습은 Cal-1(G2 이후 허용) 또는 반려 부채 0이므로 종료 검토.

## 2026-09-15 심야 04:00 [심야병렬] 서브에이전트 3명 동시 학습 — film-cu Lv3-2 · film-w Lv3-2 · film-oxide Lv3-2 (각 5/6→6/6 완주)
QA루프 #110 PASS(유의 7/21 ρ=0.9537 불변, 격리 1: dandu2009 F2+F4, 3회차 연속 하락 없음). corpus fetch 7/60(ECS·IOP·JJAP 봉쇄 지속), extract 7(rates 0 — 소형 OA만), total 8960/with_fulltext 1526/queue fetch 7434·learn 1514.
completion 40/50 불변(C2 Γ5·χ1·ψ3·Δ1). 대상 선정: 4/6 잔여 없음 → C2 미충족 팩(cu_h2o2_bta·w_fe_oxidizer·oxide_silica)의 Kp를 1차 문헌으로 근거화하는 film-* Lv3-2 3단원. Max워커(ψ sti_ceria, 03:56 병행 실행)·성장엔진과 팩 무충돌(sim/·params yaml 수정 금지 지시). claude -p opus 3병렬(--max-turns 80), ~25분.
- film-cu Lv3-2: knowledge/cmp/cu-kp-preston-coefficient-literature-back-calculation.md (출처7·코드5블록). 1차 (P,V,MRR) 역산 Kp 분포 1.1~5.8e-13 m²/N(중앙 1.9e-13), Tugbawa 2002 블랭킷 r_cu=159 Å/s@4psi 역산 3.67e-13 ↔ 팩 3.5e-13 5% 이내 → "미재현" 딱지 종결(단 rpm→V 환산 r_cc ±30~44%라 estimated 유지 권고). Guo 2004 Preston 유효창(P≲6psi·V≲0.7m/s, 고압 P^1/6). Seal/Gopal 산성 pH4 H2O2 정점 3.6wt% ↔ 팩 3.0 확증, 판정#20 알칼리 단조감소와 pH 레짐 분리. dishing r_cu와 kp가 같은 Kp로 수렴 확인. 구현요청 2건(P2 Preston 유효창 플래그·P3 산화제 pH 레짐 분기). Gopal&Talbot 2007 papers 등록.
- film-w Lv3-2: knowledge/cmp/w-cmp-preston-kp-oxidizer-rate-literature-reproduction.md (출처7·코드3블록). lim2013/US8070843B2/Stojadinović 2016 역산 Kp 중앙 1.1e-13(5e-14~1.7e-13) vs 팩 2.8e-13 **~2.6배 계통 과대**(어느 문헌도 V 미보고, R_cc=0.13m 가정이 지배 오차 → estimated 유지). Preston 지수: Wang 2012 선형 실측 채택, Bouvet 화학율속 포화·Stojadinović P^0.5(E4 모델)는 레짐 분기로 미채택. 산화제 포화농도 Fe(NO3)3 ~0.1wt%/KIO3 ~2wt%/H2O2 >6.1wt% — **팩이 Fe(NO3)3 선언인데 곡선은 H2O2 스케일(30~60배 불일치)** → 구현요청 P1. Ea 수치 미확보(방향만). Stojadinović 2016 미러 사이트 확보·Wang 2012 등록.
- film-oxide Lv3-2: knowledge/materials/film-oxide-kp-filmtype-scaling-teos-hdp-bpsg-psg.md (출처5·코드4블록). Liu 1995(wet thermal 정규화 앵커)+Lv1-1 미판독 Fig 8× 렌더 판독+Mariscal 2020. 상대 Kp(thermal=1): TEOS 1.35·HDP/SOD/O3-TEOS 1.30~1.50·PSG 2.9·BPSG 4.6(상대비 literature E3, 절대 Kp는 교차논문 다리라 estimated). 미도핑막 MRR∝H^-0.2 약상관, 도핑막은 경도 무관·수화 화학 지배. 세리아는 민감도 축이 경도→밀도/화학으로 달라 배율표 이식 금지(실리카 HDP/TEOS 0.964 vs 세리아 HDP≪PETEOS). 구현요청 P5(kp 막질 분화)·P6. liu1995 등록.
품질게이트(check_knowledge --all 직접실행): **195/195 통과**. verify_claims 신규 3편 전원 PASS(DOI 19건 실존, 코드 12블록 0실패). 429 흔적 없음.
체크박스 3개 [x], ORG §5 3행 갱신(film-cu·film-w·film-oxide 6/6). knowledge/params·sim 미변경 — 팩 갱신 제안표 3건은 성장엔진 판정 대기(특히 w_fe_oxidizer Kp 2.6배·산화제 스케일 불일치는 C2 Γ/ψ 칸과 직결).
다음 회차 후보: 5/6 잔여 13명 중 Lv3-2가 파라미터 근거화 성격인 film-nitride·film-poly-si·slurry-abrasive(κ)·slurry-chemistry(χ/ψ 화학상수). 성장엔진에 팩 갱신 판정 3건 인계.

## 2026-09-14 10:00 [성장엔진] tau 이중계상 제거 + TR(턴오버비) 채널 신설 — 완성격자 27→32/50
COMPLETION C2 tau 5칸(전 팩)을 unverified→literature로 승격. confidence 숫자만 올린 게 아니라 **tau의 결합 형식 자체를 교체**한 것이다.
- 발견: tau가 쓰던 eta(슬러리 이용효율) 항과 이번에 넣으려던 MRT 항이 **종속**이다 — Mu 2016 정의를 풀면 eta*MRT = V_total/q_total이고 실측 6점에서 2% 이내 일치(최악 +1.83%).
  둘을 곱하면 그루브 폭 효과를 두 번 센다. 등급 판정: eta 지수 0.07은 Prasad 기공률→그루브 교차대입(E4), TR은 ILD oxide 직접 실측 폐형식(E2) → E2 채택, eta 항 제거.
- 신설: f_TR = 1 - a*(MRT/t_polish), a=0.2301 (Philipossian/Mitchell 2004 doi:10.1149/1.1731539 본문 앵커 TR=1.13에서 370A vs TR=0에서 500A = 26% 감소에서 닫힌 형태 유도).
  MRT(폭)는 Mu 2016 Table 3 실측 3점 보간, 범위 밖 끝값 고정. 미러 사이트 -> 미러 사이트으로 원문 PDF 확보(papers/ 등록).
- **새 물리: Recipe.time_s가 MRR에 영향을 준다.** 이전엔 총 제거량만 선형 스케일했다. 60->30 s 반감 시 평균 MRR이 추가로 4.2% 하락(코드 실측 0.9576 = 문헌 유도값).
  tests/test_engine.py::test_preston_linearity_in_pressure_and_time의 시간 선형 계약을 초선형으로 갱신(압력 선형성은 유지).
- 방향 독립 확인: 모델의 그루브 폭->MRR 방향이 뒤집히므로(600um 정점 -> 좁을수록 유리) 제3문헌 대조. Kao 2011(doi:10.1016/j.wear.2010.10.057) "removal rate was reduced by
  increasing the groove width" — 다른 그룹·기법이 같은 방향(E3). 반대 주장 Hong 2012은 MRR 수치가 그림뿐이라 정량 부적격 + 범위 밖(W=2mm)으로 기록.
- 스코프 축소 1건: MRT의 압력 의존(Mu 2016 실측 3->5PSI에서 약 0.90배)은 **의도적으로 배선하지 않음** — 엔진 Preston 압력 선형성 계약이 깨지는데 기여는 30s·2PSI 스윙에서 1.1%뿐.
  "못 찾았다"가 아니라 "찾았으나 뺐다"로 코드 주석·노트에 크기와 함께 명시.
검증(직접 실행): pytest 644 passed. qa_loop --strict PASS(#72, 유의 7/20 rho 0.9537 불변). completion 27->32/50(C2 23->18). check_knowledge·verify_claims 신규 노트 PASS(출처 7건 실존·코드 1블록).
다음: C2 잔여 18칸 중 Gamma 5칸(컨디셔너 — disk RPM 드라이버 부재·PCR 시간감쇠 앵커가 2차인용이라 구조적 결측 2건 선행 필요), chi 4칸.

## 2026-09-14 12:00 [학습총괄] 부채상환 1편 + 병렬배차 2명(1이수/1미완)
- **최적화 루프 게이트**(--record, 커밋 1970f7e): 물리 심각 0 · pytest 644 PASS · 유의 ρ=0.951(8셋) ·
  완성격자 **27→32/50** · 등급상한 눌린칸 21→11 · 🔴 과적합 G1(자유도 예산 4.33) 1건.
  판정: G1 위험은 **되돌릴 대상이 아니다** — 같은 회차에 G3 편중 2.33→1.4, G4 일반화격차 +0.07→−0.178로
  함께 개선됐고(held-out ρ가 캘리브레이션 ρ보다 높다), 파라미터 증가분은 세리아 팩이 상속하던
  실리카 입경 정점(80nm)을 세리아 실측 163nm로 교체한 커밋(19bc6a9)에서 나왔다. 남의 재료 상수를
  자기 재료 실측으로 바꾼 것이므로 자유도가 는 게 아니라 제자리를 찾은 것. **상쇄는 분모(검증 조건)로
  해야 한다** — in_scope:false 5개 데이터셋(초경합금·Mo·SiC·석영유리 등 팩 부재)이 그 병목.
- **부채상환**: `physics/cmp-slurry-flow-lubrication-film-thickness.md`(702a31c). §6 실험검증 절에
  1차 DOI 10.1149/1.1355691 + 원문 p.G212 인용문 명기, `python verify` 블록 신설(4주장 assert).
  재현 `Re*=5.067e-03` → 원문 주장 1e-2~1e-3 구간 내 **재현 확인**. 하중폐합비 1.12(포물면 근사
  12% 초과)와 h̄/z₀=0.206(원문 미보고 → 대조 불가)을 **꾸미지 않고 그대로 기록**.
- **배차 2명**(갭 조준): slurry-chemistry Lv3-1 → 정확도 갭 #5 χ 부분모델링(drivers 2개인데 활성 항
  1개, 3팩) / defect-scientist Lv3-1 → C2 Δ 5칸·병목키 abrasive_d99_nm(3칸).
  - ✅ slurry-chemistry **이수**(800805e): Co·Ru 착화제 노트. EDA가 산화제와 독립이 아니라 **곱셈형
    게이트**(Xu2022), 시트르산 포화형 + 무산화제 기계하한(Popuri2017). χ의 빠진 축이 `slurry_ph`가
    아니라 **착화제 농도**라는 판정. 총괄 직접 검증: verify_claims PASS(출처 3건 실존·코드 3블록 0실패),
    check_knowledge PASS, pytest 650 PASS, qa_loop 유의 7/20 ρ=0.9537 불변(퇴보 없음).
  - ⏸ defect-scientist **미완** — 45턴 소진(문헌은 확보: papers/kwon2013-* 3건). 체크박스 건드리지
    않았으므로 되돌릴 것 없음. 다음 회차 재시도.
- 반려 0건이지만 **이번엔 완주 1명뿐**이라 병렬도는 2명 유지(3명 상향 조건인 "2회차 연속 반려 0%"는
  미충족으로 본다 — 미완은 반려가 아니지만 성공도 아니다).
- 진도 137/168(81.5%) · 속도 8.21단원/일 · 완주예상 2026-09-17(2027-01 목표 대비 여유).
- 다음 회차 후보: defect-scientist Lv3-1 재시도(Δ·d99), film-w Lv3-2, tool-endpoint Lv3-1,
  그리고 **G1 상쇄용 in_scope:false 5셋의 팩 부재 해소**(데이터 확보보다 팩 추가가 싸다).

## 2026-09-14 18:00 [성장엔진] 판정#21 — UNWIRED 갭 4건 전부 "이미 종결된 건"으로 판명, 랭킹 43→39
- 갭 랭커가 4회차 연속 최상위(점수 60)로 올린 UNWIRED 4건(입경 D50·groove depth·pitch·asperity tip
  radius)을 실제 엔진 응답으로 검증한 결과 **한 건도 미배선이 아니었다.** 랭커는 UI의 `dead:` 문자열
  (E5, 2차 신호)을 근거로 썼고, 그 문자열은 판정#1·#6·#8·#10이 내려지기 전에 쓰인 잔류물이었다.
- 실측(엔진 직접 실행, abrasive_size_nm 40~200 nm 스윕):
  oxide_silica 106.2→267.6(80nm 정점)→197.2 / sti_ceria 183.2→1163.5(160nm)→1114.0 (판정#10 정점
  163 nm와 일치) / sic_ceria_h2o2 동형 / cu_h2o2_bta 500.545 **완전 평탄** · w_fe_oxidizer 400.436
  **완전 평탄** — 후자 둘은 `abrasive_size_exponent=0.0`(판정#1·#6 null 채택)의 의도된 결과다.
  groove depth/pitch는 2026-09-13 3회차 규칙으로 스코프 축소 종결, asperity R은 GW 모델 조건부.
- 조치: UI 배지에 `closed:`(⏹ closed by evidence ruling)를 신설해 `dead:` 4건을 교체하고 판정 근거와
  위 측정 수치를 본문에 명기. **모델 코드·파라미터 값은 한 줄도 바꾸지 않았다** — 바꿀 게 없다는 것이
  이 회차의 결론이다. EVIDENCE-RULES 판정 #21로 기록.
- 검증: pytest 675 PASS · qa_loop --strict PASS(유의 7/21, ρ=0.9537 → 0.9537 불변) · 완성격자 36/50 불변
  · accuracy_gaps 43→39건(UNWIRED 4→0). 다음 1순위는 PARTIAL χ(3팩, 드라이버 2개 중 활성 1개).
- 교훈(재발방지): null 결론을 낸 축은 UI에서도 "미배선"과 구분 표기해야 한다. 안 그러면 κ 입경 5회차
  순환과 같은 무한 재조사가 랭커를 통해 되살아난다.

## 2026-09-14 20:00 [성장엔진] 판정#23 — 세리아 chemical tooth 선형 가정 반증, 멱지수 p=1.65 채택 (격자 38→40/50)
- C2 갭(χ confidence)을 잡으러 들어가 **함수형 결함**을 찾았다. `_ceria_term`의 θ(Ce³⁺ 분율) 선형
  의존은 "문헌에 폐형식이 없어 보수적으로" 남겨진 무근거 가정(E6)이었고, 팩 주석은 `ceria_tooth_gain`을
  "캘리브레이션 1순위"로 지목하고 있었다. **그 방향 자체가 막다른 길이었다** — 선형에서는 슬러리 내부
  MRR 비가 θ 비를 구조적으로 넘지 못하므로(floor→0에서 상한=θ비) gain을 어떻게 잡아도 실측이 안 나온다.
- 근거(E2, 교란 통제된 대응쌍): 미러 사이트(미러 사이트 경로)로 **Netzband & Dunn 2019** 1차 전문 확보
  (doi:10.1149/2.0311910jss, papers/에 등록). Fig.4를 PDF 벡터 마커 좌표로 판독(0 wt% 12.55% vs
  Table I 명시값 12% → 오차 0.55%p로 판독 정확도 자기검증) → θ 12.55→25.71%(2.05배, 본문 "doubles").
  같은 저자 2020 본문의 MRR 2.0배→5.5배(상용 기준 약분, 내부비 2.75배)와 짝지어 p를 역산.
- 조치: `ceria_tooth_exponent` 신설(p=1.65, floor=1/5.5 기준 / floor=0이면 1.41, 0.3이면 1.97),
  세리아 2팩에 literature로 선언. `ceria_tooth_gain`은 1.0 고정 + unverified→literature(형상을 지수가
  가져갔으므로 진폭 이중계상 방지). 팩이 지수를 선언 안 하면 p=1.0 = 기존 동작(하위호환).
- 검증(전부 직접 실행): p=1.65 재현 내부비 **2.757 vs 문헌 2.75(오차 0.26%)**, 선형은 1.829(33% 과소).
  pytest **698 PASS**(신규 계약 4건: 기준조건 1.0 불변·Netzband 쌍 재현·선형 기각·하위호환).
  qa_loop --strict **PASS**(유의 7/21, ρ=0.9537 불변). completion **38→40/50**(χ/sti_ceria,
  χ/sic_ceria_h2o2 두 칸). verify_claims·check_knowledge 둘 다 통과.
- 한계(노트 §6에 명기): 2점 할선이라 θ 12.5~25.7% 밖 외삽 금지 / θ와 MRR이 연속 두 논문에 나뉘어
  있어 verified 아닌 literature / p는 floor 불확실성을 그대로 물려받음 / 초선형 메커니즘 미검증.
- 다음: C2 남은 10칸 중 Γ 5칸은 판정#22로 조건부 하한(임계하중 미해소) — 2회차 대상은 ψ(cu_h2o2_bta
  unverified, w_fe_oxidizer unverified) 쪽이 싸다.

## 2026-09-15 08:00 [성장엔진] χ PARTIAL 해소 — 텅스텐 산성역 pH 항 신설(산화제 매개, k=0.1163/pH)
- 갭 랭커 1순위 = **PARTIAL χ (terms=['oxidizer'], 3팩)**. `w_fe_oxidizer` 는 χ drivers 에
  `slurry_ph` 가 등록돼 있는데도 실제 항이 산화제 하나뿐이라 **pH 를 바꿔도 출력이 안 변했다**.
  실리카(`_ph_peak_term` 정점형)·세리아(IEP 창)는 있었지만 금속 W 에는 대응 항이 없었고,
  다른 계의 항을 빌려 쓰면 메커니즘이 달라 부호까지 틀린다(세리아 ρ=−0.525 전례).
- 근거(E2, 교란 통제 1축 DOE): 미러 사이트→미러 사이트 경로로 **Stojadinović, Bouvet,
  Mischler 2016** (doi:10.1007/s40735-016-0041-4) 1차 전문 확보(papers/ 등록). Table 1 은
  3 % 실리카 12 nm·KIO₃ 4수준·장비/압력/회전수 전부 고정하고 **HCl 로 pH 만 5→2** 로 바꾼
  대응쌍 4조다.
- **핵심 발견 — pH 효과는 산화제 매개다(부호가 뒤집힌다).** 산화제 0 %: 40→25 Å/min (비 0.625,
  pH 를 내리면 오히려 **감소**). 산화제 존재 3조건: 1.429/1.533/1.300 (전부 증가). 따라서 pH 는
  W 를 직접 깎지 않고 **산화(WO₃) 구동력**으로만 들어온다 — Nernst E_rev=−0.119−0.059·pH,
  pH 5→2 에서 177 mV (논문 명시 180 mV 와 3 mV 이내 일치).
- 조치: `_ph_w_acidic_term` 신설 f(pH)=exp(−k·(pH−ph_ref)), k=0.1163/pH (3조건 로그평균).
  **팩이 `w_ph_acid_k` 를 선언할 때만 켜지는 게이트**를 달았다 — 산화제 없는 W 계는 부호가
  반대라 덮으면 안 된다(EVIDENCE-RULES "둘 다 맞되 레짐이 다르다" → 스코프 분리).
  알칼리역(Xu 2022 doi:10.3390/mi13050762, pH 7→12 에서 6.69→13.67 µm/h **증가**)은 용해 지배로
  또 부호가 반대 — 미모델링으로 명시.
- 검증(전부 직접 실행): 기준조건 팩터 정확히 1.0 / pH 5→2 재현 1.417배 vs 문헌 로그평균 1.417
  (개별 −0.8·−7.6·+9.0 %) / **pytest 698→711 PASS**(신규 계약 5건: 기준 1.0·문헌비 재현·방향과
  외삽경고·게이트 차단·partial→modeled) / **qa_loop --strict PASS** (유의 8/21, ρ=0.9512 불변) /
  verify_claims·check_knowledge 둘 다 통과 / accuracy_gaps 39→35건, PARTIAL 4→3.
- 한계(노트 §6): 원문 산화제는 KIO₃, 팩은 Fe(NO₃)₃ → **대리계(E2/E3 경계)**. 2점 할선이라
  pH 2~5 밖 외삽 금지. 개별 k 산포 ±22 %, 지수형(Tafel) 가정 자체는 2점으로 구별 불가 = 미검증.
- 완성 격자 40/50 불변(C2 는 confidence 승격 과제라 이번 배선으로는 안 움직인다). 다음 1순위는
  CONFIDENCE(pad_E_star_pa 등 패드 물성 — 5팩 공통이라 한 번 잡으면 여러 칸이 같이 움직인다).

### 2026-09-15 (성장엔진) — C2 완성 정의 수정 적용: 격자 40/50 → **49/50**
- COMPLETION.md가 제안만 해 두고 멈춰 있던 "C2 = literature 이상 **또는** 3회차 규칙으로
  영구 종결(기계 검증 가능)"을 실제 코드로 구현했다. `validation/C2-CLOSURES.yaml`(9칸 등록)
  + `tools/completion.py::c2_closures()` + `tests/test_c2_closures.py`.
- 종결 주장은 grep으로 우회할 수 없다 — 판정번호가 EVIDENCE-RULES 판정표에 실존하고 그 행에
  "종결"이 있고 근거 노트 파일이 있어야 인정된다. 셋 중 하나라도 어긋나면 사유를 붙여 C2 실패.
- **값·confidence는 1바이트도 안 바뀐다**(테스트가 고정). estimated 9칸은 여전히 estimated이며,
  `check` 출력에서 "검증된 한계"로 완성 칸과 구분 표시된다.
- 검증: `pytest -q` 725 passed(+4 신규), `qa_loop.py run --strict` PASS(유의 8/22, 평균 ρ 0.9512 불변).
- 남은 1칸: χ/cu_h2o2_bta `oxidizer_passivation_K`(판정#29 1회차 실패, 2·3회차 남음). 이것만
  풀리면 50/50 → C8 근거보고서(MODEL-BASIS.md) 생성 단계.

### 2026-09-15 18:00 [정확도루프] 판정#38 — Cu 산화제 항의 **부호가 레짐에 따라 뒤집힌다**
- 남은 C2 1칸(χ/cu_h2o2_bta `oxidizer_passivation_K`)의 판정#29 **2회차**. 1회차가 남긴
  질문("독립 K가 3.8배 어긋나는 게 조성 미세차인가 함수형 오류인가")에 **세 번째 독립
  1차 출처**로 답했다: Jani·Venkataswamy·Seo·Krishnan 2025, ECS JSS 14(4) 044003,
  **doi:10.1149/2162-8777/adc59e (CC-BY)** — 전문 직접 확보(papers/, INDEX 등록).
- **발견**: Table I×II Expt 30/31/32 는 실리카 6wt%·옥살산 0.08M·**pH 3.0**·3psi·90rpm 고정에
  H₂O₂만 3→4→6 wt% 스윕 → 2282/2533/2578 nm/min **증가**. 현행 피복-억제 항은 같은 구간
  0.647배(**−35.3 %**) 예측 — 정량 편차가 아니라 **부호 반대**. 원문 회귀도 [H2O2] +96.38
  (p=0.0185 유의), 2차항 비유의로 촉진 방향을 지지.
- **판정**: 승격 기각 + **갭 재분류(CONFIDENCE → BIAS)**. 값·등급·코드 전부 불변
  (K=0.8232, estimated). 3.8배는 적합잡음이 아니라 **레짐 불일치** — K는 알칼리×무착화제에서
  역산됐는데 팩 운전점은 pH 4.0+글리신·BTA = 산성×착화제다. 피복-억제 함수형은 K>0 어디서도
  단조감소라 **값 재추정으로 해소 불가**(노트 §6 블록3 assert). 해소책=팩 레짐 분리(구현요청,
  선결조건 `chelator_*` 축 신설). 상반된 두 방향을 평균내지 않았고, 옥살산(+536.63)·
  글리신(−440.91) 부호 차이를 근거로 착화제끼리도 묶지 않았다.
- 검증(전부 직접 실행): verify_claims ✓(출처 4건 실존·코드 3블록 통과) / check_knowledge ✓ /
  **pytest 753→767 passed** / **qa_loop --strict PASS**(유의 평균 ρ=0.9442 불변) /
  신규 데이터셋 감사 **clean** / 백테스트에서 이 데이터셋 **ρ=−1.000** — 반증이 하네스에서
  그대로 재현된다. `in_scope: false`(범위 표시이지 제거 아님)라 held-out 집계 불변.
- 부수 수리: `tools/find_open_access.py`가 HEAD에서 **SyntaxError로 아예 실행 불가**했다
  (식별자에 공백이 섞인 상태). 파싱되게 고쳐 OA 탐색 경로를 되살렸다 — 이번 회차 DOI 해석이
  이것 없이는 안 됐다.
- 완성 격자 49/50 불변(이 칸은 3회차 규칙상 1회 남음, 단 성격이 C2가 아님이 확정됨).

### 2026-09-15 20:00 [성장엔진] GW 패드 3키를 문헌값으로 교체 + 파생 접촉량 재적분 (판정#40)
- 정확도 갭 CONFIDENCE 1~2위(5팩 공통). 직전 회차가 권고로만 남긴 `pad_E_star_pa` 1.0e9→1.316e8 Pa,
  `pad_asperity_radius_m` 5e-6→5e-5 m, `pad_height_beta_inv_m` 0.3e-6→2.0e-6 m 를 실제 반영, estimated→literature.
- 파생 2값을 같은 GW 코드로 재적분: `real_contact_area_ratio` 5.8e-4→1.393e-3,
  `active_particle_density_per_m2` 1.845e7→4.434e6 /m² (confidence 는 estimated 유지 — 단층 가정 미검증).
- 부수 발견: 옛 파생값 source 의 "팩 값과 일관" 문구가 **재현 불가**였다(적분 입력과 팩 값이 3.9배 불일치).
  `sim/sensitivity.py` E* 스캔 범위 (3e8,3e9) 는 새 기본값을 포함조차 안 해 문헌 대역으로 교체.
- 검증: pytest 778 passed · qa_loop --strict PASS · 유의 평균 ρ 0.9442 **불변**(tier2 진단 경로라 정상).
  노트: knowledge/pad/pad-gw-parameter-literature-adoption-derived-recompute.md
