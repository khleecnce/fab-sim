# CMP 공정 시뮬레이션 — 경쟁 지형과 공백

> 조사일: 2026-09-13. 조사자: 리서치 에이전트.
> 원칙: 확인된 것만 쓴다. 확인 못 한 건 **미확인**이라고 쓰고 왜 못 했는지 남긴다.
> 이 문서는 `POSITIONING.md`의 §2 주장("입력축이 다르다")을 검증·반박하는 용도다.

---

## 0. 결론 먼저 (냉정하게)

1. **"슬러리 조성을 입력으로 받아 MRR·균일도를 계산해주는 상용 소프트웨어"는
   공개 웹에서 확인되지 않는다.** 즉 직접 경쟁자 **0건 (확인된 범위 내)**.
2. **그러나 "경쟁자가 없다"는 좋은 소식이 아닐 수 있다.** 20년간 MIT·Praesagus·
   Cadence·Siemens·Lam이 CMP 모델링에 돈을 넣었는데도 전부 **레이아웃(GDSII) →
   토포그래피** 축으로 수렴했다. 조성축을 아무도 안 한 게 아니라, **상품화 가능한
   수준으로 못 한 것**일 가능성을 배제할 수 없다. 이건 §5에서 따로 다룬다.
3. **가장 위협적인 인접자는 EDA가 아니라 Araca Inc.** — 소모품 R&D 고객
   (슬러리·패드 업체)을 이미 장비+데이터분석 소프트웨어로 잡고 있다. 고객이 같다.
4. 경쟁 축은 "SW vs SW"가 아니라 **"SW vs 실험(데모 평가)"** 이다. 진짜 경쟁자는
   Araca APD-800 같은 R&D 폴리셔와 소재사 내부 DOE 프로세스다.

---

## 1. 카테고리 지도

CMP "시뮬레이션"이라는 단어는 서로 다른 4개 시장을 가리킨다. 섞으면 안 된다.

| 축 | 입력 | 출력 | 고객 | 대표 도구 |
|---|---|---|---|---|
| **A. DFM / 다이스케일** | GDSII 레이아웃, 패턴밀도 | dishing·erosion·두께 핫스팟 | 칩 설계자 | Cadence Pegasus CMP, Siemens Calibre CMPAnalyzer |
| **B. 피처스케일 토포그래피 (Process TCAD)** | 공정 스텝 시퀀스 | 3D 구조 형상 | 공정 통합 엔지니어 | Lam SEMulator3D, Synopsys Sentaurus Topography, Silvaco Victory, ViennaPS |
| **C. 장비/유동 CFD** | 패드·리테이너 형상, 유량 | 슬러리 유동장, 입자 궤적, 체류시간 | 장비/공정 연구자 | COMSOL 모델, 학술 CFD 논문 |
| **D. 소모품·레시피 설계 (FabSim 목표)** | **조성·패드·디스크·장비조건** | MRR 반경프로파일, WIWNU, 결함경향 | **소재사 R&D** | **상용 제품 미확인** |

FabSim은 D다. A·B·C는 인접이지 경쟁이 아니다 — **단, 심사위원·면접관은 이걸
구분 못 한다.** 그게 실질 리스크다(§6).

---

## 2. 상용 도구 (8개 확인)

### 2.1 Cadence Pegasus CMP Predictor / CMP Process Optimizer (CCPO) — 축 A
- 입력: 전체 레이어 스택 레이아웃. 출력: 멀티레이어 두께·토포그래피, CMP 핫스팟,
  CMP-aware RC 추출. FEOL/MOL/BEOL + 웨이퍼 스케일 예측.
- 출처: https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/silicon-signoff/pegasus-dfm.html
- **계보 주의**: 원천은 MIT 출신 스타트업 **Praesagus**(2000 설립, Taber Smith).
  2006-03 Cadence가 **$25.8M**에 인수. 출처: EE Times
  https://www.eetimes.com/cadence-bought-dfm-startup-praesagus-for-26-million/ ,
  SEC S-8 https://www.sec.gov/Archives/edgar/data/813672/000095013406005971/f18967sv8.htm
- 실측 캘리브레이션 능력 있음: 2015 Applied Materials와 공동개발 프로그램(압력·폴리시
  시간·균일도 등 **공정 파라미터** 최적화). 출처: PRNewswire 2015-06-22.
  2019 Toshiba Memory가 CCPO로 **실리콘 대비 95.7% 정확도** 달성 발표.
  출처: https://sst.semiconductor-digest.com/2019/02/cadence-cmp-process-optimizer-...
- ⚠ **FabSim 차별점을 "실데이터 캘리브레이션"이라 말하면 여기서 즉사한다.**
  슬러리는 여전히 계수 안에 흡수된다(조성이 입력 변수로 노출된다는 근거 미발견).

### 2.2 Siemens EDA — Calibre CMPAnalyzer + Calibre CMP ModelBuilder — 축 A
- CMP 모델 빌드 → 멀티레이어 풀칩 시뮬 → 핫스팟 검출 → Calibre YieldEnhancer
  SmartFill로 더미필 최적화 → Calibre xRC와 연동해 타이밍 검증.
- 출처: https://www.siemens.com/en-us/products/ic/calibre-design/design-for-manufacturing/cmp-analyzer/
  , 백서 "Building CMP models for CMP simulation and hotspot detection"
  https://resources.sw.siemens.com/en-US/technical-paper-building-cmp-models-for-cmp-simulation-and-hotspot-detection/
- 명백히 설계자 툴. 소재사 R&D 구매 대상 아님.

### 2.3 Lam Research (구 Coventor) SEMulator3D — 축 B
- 복셀 기반 물리 구동 3D 공정 모델링, 전체 플로우 모사. CMP는 플로우 중 한 스텝.
- 출처: https://www.lamresearch.com/product/semulator3d/
- **하이브리드 본딩 CMP 사례 확인**: 3D CMP 모델을 실험 데이터로 캘리브레이션 후
  "pad, slurry, process conditions and pattern density"를 최적화했다는 IEEE 논문
  존재. 출처: https://ieeexplore.ieee.org/document/10564950 (ECTC 2024)
  → ⚠ **여기가 FabSim 주장에 가장 아픈 지점이다.** "슬러리"가 최적화 대상으로
  등장한다. 다만 초록만으로는 슬러리가 **조성 수준 물리 입력**인지 아니면
  **레이블링된 계수 세트**인지 판별 불가 → **미확인**. 전문 확보 필요.
- 참고: Coventor는 2017년 Lam Research에 인수됨(업계 공지 사실, 다만 이 조사에서
  1차 출처 재확인 실패 → **1차 출처 미확인**).

### 2.4 Synopsys Sentaurus Topography — 축 B
- deposition/etch/spin-on-glass/reflow/**CMP**의 2D·3D 형상 변화 시뮬.
- ⚠ 공식 문구가 CMP를 "**emulates**"라고 명시한다(반면 etch는 "simulates").
  즉 **CMP는 물리 모델이 아니라 기하학적 평탄화 연산**에 가깝다.
- 출처: https://www.synopsys.com/manufacturing/tcad/process-simulation/sentaurus-topography.html
  및 데이터시트 https://www.synopsys.com/content/dam/synopsys/silicon/datasheets/sentaurus_ds.pdf

### 2.5 Silvaco Victory Process — 축 B
- 위 3사와 동급의 closed-source 공정 TCAD로 ViennaPS 논문이 비교군으로 지목.
- 출처: ViennaPS 논문(SoftwareX 2025) 비교 문단.
- CMP 모델 상세는 이번 조사에서 확인 못 함 → **미확인**.

### 2.6 COMSOL Multiphysics — 축 C
- 공식 모델 라이브러리에 "Modeling of Flow Field and Abrasive Particles in CMP
  Equipment" 존재. 리테이닝 링 내부 유동장 + 연마입자 궤적, frozen rotor.
- 출처: https://www.comsol.com/model/modeling-of-flow-field-and-abrasive-particles-in-chemical-mechanical-polishing-cmp-equipment-140171
- MRR을 예측하지 않는다. 유동만. **보완재이지 경쟁자 아님.**

### 2.7 Araca Inc. — **축 D 인접, 가장 위협적**
- 미국 Tucson, 2004 설립. Fujikoshi(일본)와 공동 제조하는 R&D 폴리셔
  **APD-800 Prime® / RDP-800 계열 / RDP-500®** 판매. 현장 설치 **APD-800 Prime
  20대+, RDP-500 70대+**.
- 스펙: 1,000~2,300 Hz 전단력·수직력 센서, 패드 표면 IR 온도, 10존 컨디셔너 스윕,
  2계통 슬러리 공급, **AMAT Reflexion LK®의 dwell time·컨디셔닝 존을 모사**.
- 소프트웨어: **FSX®** (force acquisition + 분석: COF, Stribeck+ 곡선, FFT,
  directivity, kinetic curve, EPD) + 신규 **Araca Insights®** 데스크톱 앱
  (완전 오프라인, Win/mac/Linux, "Data Stays in Your Fab").
- 고객: "IC makers, **consumables suppliers**, OEMs, 정부연구소, 대학".
- 출처: https://aracainc.com/ , https://aracainc.com/pages/polishers.html ,
  APD-800 Prime 브로슈어 https://aracainc.com/docs/polishers/APD-800-Prime-Brochure-2023.pdf ,
  CMPUG 발표 https://nccavs-usergroups.avs.org/wp-content/uploads/2021/11/CMPUG1021-6-AracaInc-Philipossian.pdf
- **왜 위협인가**: 고객이 동진쎄미켐 같은 소모품 업체로 FabSim과 **정확히 같다**.
  그리고 Araca의 답은 "시뮬레이션 말고 **싸고 표준화된 실험**"이다. CMPUG 자료의
  입출력 리스트(입력: 패드/슬러리/디스크/링 타입 A·B·C… 출력: MRR·WIWNU·dishing·
  erosion·pad-wafer 접촉면적·asperity 곡률)는 FabSim 출력과 거의 겹친다.
  차이는 **A·B·C 라벨 vs 조성 수치**. 즉 Araca는 "측정", FabSim은 "계산".
- ⚠ Araca가 물리 모델을 소프트웨어로 파는지는 **미확인**. FSX/Insights는
  현재까지 확인된 범위에서 **데이터 분석 도구이지 예측 시뮬레이터가 아니다.**
- 주: Ara Philipossian(Araca CEO, 前 U. Arizona)은 CMP 트라이볼로지 문헌의 주요
  저자다. **FabSim이 인용하는 마찰·Stribeck 물리의 상당 부분이 이 사람 논문이다.**
  = 그가 마음먹으면 가장 빨리 같은 걸 만들 수 있는 사람이다.

### 2.8 Citrine Informatics — 축 D 인접, 방법론이 다름
- 소재·화학 조성 최적화 AI 플랫폼. GEMD 데이터모델 + random forest 불확실도 +
  sequential learning. **반도체 포토리소 조성** 고객 사례 공개(400 실험 중 상위 9개
  전부 AI 제안). 실험 횟수 50~80% 감소 주장.
- 출처: https://citrine.io/platform/ , 사례 PDF
  https://citrine.io/wp-content/uploads/2024/07/Case-Study-Semiconductors.pdf ,
  플랫폼 논문 https://arxiv.org/html/2607.25039v2
- **FabSim과 같은 문제(조성→성능, 실험 횟수 감축)를 다른 방법(데이터 기반 SL)으로
  푼다.** 물리 모델이 없어도 되고, 대신 고객 데이터가 필요하다.
- ⚠ 이게 실질적 대안 위협이다. 소재사 임원 입장에서 "물리 모델 만들자"보다
  "Citrine 깔고 우리 DOE 데이터 먹이자"가 **의사결정이 훨씬 쉽다.** CMP 전용은
  아니지만 CMP 슬러리에 못 쓸 이유가 없다. Citrine이 CMP 슬러리 사례를 공개한
  적이 있는지는 **미확인**.

---

## 3. 학술·오픈소스 (5건 확인)

### 3.1 ViennaPS (TU Wien) — 오픈소스, C++/Python, MIT 계열 라이선스
- Level-set + Monte Carlo ray tracing 피처스케일 토포그래피. GDSII 임포트, VTK 출력,
  GPU(OptiX) 가속. Etch/depo/ALD/DRIE/산화 모델 다수.
- **CMP는 "geometrical algorithms … boolean operations and chemical mechanical
  planarization have been implemented"** — 즉 **순수 기하학적 잘라내기**.
  물리 없음. 슬러리 없음.
- 출처: https://github.com/ViennaTools/ViennaPS ,
  https://www.iue.tuwien.ac.at/viennacl0 , SoftwareX 논문
  https://doi.org/10.1016/j.softx.2025.102453
- **시사점**: 가장 활발한 오픈소스 공정 시뮬레이터조차 CMP를 물리로 안 푼다.
  → FabSim의 공백 주장을 **뒷받침하는 가장 강한 1차 증거**. 동시에 ViennaPS 팀이
  CMP 물리 모듈을 추가하면 무료 경쟁자가 하루아침에 생긴다는 뜻이기도 하다.

### 3.2 MIT Boning 그룹 계열 패턴밀도 모델
- Praesagus의 원천 기술(semiengineering 기업 프로필에 "Technology originated from
  MIT" 명시). 출처: https://semiengineering.com/entities/praesagus-inc/
- 공개 논문 다수이나 **패키징된 소프트웨어로는 유통되지 않음**. 입력은 패턴밀도.

### 3.3 원자/양자 스케일 시뮬레이션 (MD, ReaxFF, DFT)
- CMP 표면화학·입자-표면 상호작용 리뷰 2025. 출처:
  https://www.sciencedirect.com/science/article/pii/S2666523925001278
- 스케일이 nm·ns. **웨이퍼 반경 프로파일로 올라오지 못한다.** FabSim의 파라미터
  근거로 쓸 수는 있어도 경쟁자는 아니다.

### 3.4 CFD 기반 슬러리 유동/체류시간
- 예: 슬러리 체류시간 → 스크래치 결함 상관. 출처:
  https://www.sciencedirect.com/science/article/pii/S0263876223000266
- 단발 논문. 제품 아님.

### 3.5 ML 기반 CMP (virtual metrology, MRR 실시간 예측)
- CMP ML 리뷰 2025: https://www.sciencedirect.com/science/article/pii/S1474034625005567
- 실시간 MRR 추정(CIRP Annals 2024): https://www.sciencedirect.com/science/article/abs/pii/S0007850624000416
- 물리 기반 슬러리 온도·평균입경 추정을 센서 데이터에 보조 입력으로 쓰는 virtual
  metrology(J. Intell. Manuf. 2025): https://ideas.repec.org/a/spr/joinma/v36y2025i3d10.1007_s10845-024-02335-0.html
- ⚠ **이 흐름이 FabSim의 진짜 학술적 경쟁자다.** 방향은 정반대:
  FabSim은 "웨이퍼 깎기 전에 계산", 이쪽은 "깎는 중에 센서로 추정".
  고객이 원하는 게 후자라면 FabSim의 전제가 흔들린다.

---

## 4. 사망한 선례 — 반드시 먼저 꺼낼 것

| 회사 | 결말 | 시사점 |
|---|---|---|
| **Praesagus** (2000~2006) | Cadence에 $25.8M 인수 | CMP 모델링 단독 카테고리는 존속 못 함. 엑싯은 인수. |
| **UbiTech** (2004~) | 독립 존속 실패 (POSITIONING.md §7) | 동일 |
| DeepChip 업계 증언 | "*Almost every fab I know has their own internal CMP models. All the other players that used to be in this space disappeared. This is too esoteric...*" 출처: http://www.deepchip.com/items/0453-06.html | **팹은 자체 모델을 갖고 있다.** 외부 CMP 모델 벤더는 반복적으로 소멸했다. |

이 DeepChip 인용은 **가장 불편하지만 가장 중요한 증거**다. "아무도 안 만든 공백"이
아니라 **"만들었다가 다 죽은 자리"**일 수 있다. IR에서 이걸 먼저 꺼내고 반박하지
않으면, 아는 심사위원이 대신 꺼낸다.

반박 논거(정직한 버전):
- 죽은 회사들은 전부 **칩 설계자(축 A)**에 팔았다. 그 시장은 EDA 스위트에 흡수됐다.
- FabSim 고객은 **소재사 R&D(축 D)**로, EDA 스위트 번들에 들어갈 이유가 없다.
- 2006년 대비 달라진 것: SiC·GaN·유리기판·하이브리드본딩 등 **기존 모델이 아예 없는
  신규 CMP 재료**, 소재 국산화 정책자금, ML 처방설계 연구 급증.
- ⚠ 다만 "팹이 내부 모델을 갖고 있다"는 부분은 반박되지 않는다. 팹뿐 아니라
  **대형 슬러리 업체(CMC, Fujimi, DuPont/Qnity, Entegris)도 내부 모델을 갖고 있을
  가능성이 높다.** 이건 비공개라 확인 불가 → **미확인. 이 문서의 가장 큰 사각지대.**

---

## 5. 공백 (Gap) — 확인된 것

### 5.1 가장 큰 공백: **조성이 입력 변수인 CMP 예측 도구가 없다**
확인된 모든 상용 도구에서 슬러리는 다음 중 하나다:
- (a) 캘리브레이션 계수에 흡수 — Cadence, Siemens
- (b) 이름표(슬러리 A/B/C) — Araca 실험 플랫폼
- (c) 아예 없음 — Sentaurus(기하 emulate), ViennaPS(boolean)
- (d) 유동장 안의 입자로만 존재, MRR과 무관 — COMSOL

**"pH 0.2 올리면 MRR이 어떻게 되나"에 답하는 상용 소프트웨어는 이번 조사에서
발견되지 않았다.** 이게 FabSim의 존재 이유다.

### 5.2 2차 공백: 소모품 사양이 입력이 아니다
패드 경도·기공률·그루브·돌기밀도, 컨디셔너 그릿·하중·스윕 — 이것들이 **설계 변수로
노출되는 툴**이 없다. Araca가 실험으로 다루고, Cadence/Siemens는 계수로 흡수한다.

### 5.3 3차 공백: 신규 재료
SiC·유리기판·하이브리드본딩 CMP는 기존 패턴밀도 모델의 가정(damascene Cu/oxide)이
안 맞는다. 학계는 리뷰 단계(RSC 2025, SiC CMP). 상용 모델 **미확인**.

### 5.4 공백이 아닌 것 (착각 금지)
- 다이스케일 dishing/erosion → **Cadence·Siemens가 20년째 한다. 건드리지 마라.**
- 3D 구조 형상 → **SEMulator3D 영역.**
- 슬러리 유동 CFD → **COMSOL이 예제로 배포한다.**
- 팹 스케줄링/물류 → 애초에 다른 시장.

---

## 6. 리스크 (포장 없이)

| # | 리스크 | 심각도 | 근거 |
|---|---|---|---|
| R1 | **공백이 "불가능해서 비어 있는" 것일 수 있다** | 치명 | Praesagus/UbiTech 소멸, DeepChip 증언. 20년간 자본이 들어갔는데 조성축 제품이 안 나온 것은 강한 부정 신호다. |
| R2 | **SEMulator3D가 이미 슬러리를 다룰 수 있다** | 높음 | ECTC 2024 하이브리드본딩 논문에서 "pad, slurry, process conditions" 최적화 언급. 전문 미확인 → **확인 필수 액션** |
| R3 | **Araca가 같은 고객을 이미 쥐고 있다** | 높음 | 90대+ 설치 기반, 소모품 업체 고객, 오프라인 분석 SW 신제품 출시. 물리 모델 추가는 그들에게 어렵지 않다. |
| R4 | **Citrine형 데이터 기반 접근이 더 쉬운 대안** | 중~높음 | 물리 모델 없이 조성 최적화를 이미 상용화. 소재사가 "물리"보다 "우리 데이터"를 선호할 수 있다. |
| R5 | **대형 슬러리사 내부 툴의 존재 여부 불명** | 중 | 비공개. 확인 불가. 있으면 FabSim의 차별성이 크게 줄어든다. |
| R6 | **ViennaPS가 CMP 물리 모듈을 추가** | 중~낮음 | 오픈소스, 활발한 개발, TU Wien. 그날 FabSim의 "유일함"은 끝난다. 다만 그들 관심은 etch/plasma다. |
| R7 | **1인 개발 + 절대값 미검증** | 높음 | rho=0.95는 순위상관이고 절대값 없음. 고객·심사위원이 "몇 % 맞나"를 물으면 답이 없다. 이건 경쟁이 아니라 제품 성숙도 문제. |

---

## 7. 확인 못 한 것 (정직하게 나열)

- SEMulator3D CMP 모델의 **입력 파라미터 목록** — 문서가 라이선스 뒤에 있음.
  ECTC 2024 논문(IEEE 10564950) 전문 확보가 다음 액션.
- Silvaco Victory Process의 CMP 모델 상세.
- 대형 슬러리사(CMC Materials/Entegris, Fujimi, DuPont→Qnity, 삼성/하이닉스 내부)의
  사내 시뮬레이터 존재 여부. **원리적으로 웹에서 확인 불가.**
- 한국 국내 CMP 시뮬레이션 SW 벤더 — 검색 백엔드 오류로 한국어 검색 미완.
  **재조사 필요.**
- Citrine의 CMP 슬러리 적용 사례 유무.
- Araca Insights의 예측 기능 포함 여부.
- Coventor→Lam 인수(2017) 1차 출처.

---

## 8. 권고 (실행 가능한 것만)

1. **ECTC 2024 논문(IEEE 10564950) 전문을 구해라.** R2가 해소되거나 확정된다.
   이 한 편이 FabSim 포지셔닝 전체의 생사를 가른다.
2. **Araca를 경쟁자가 아니라 보완재로 프레이밍하라.** "APD-800으로 5점을 측정하고,
   FabSim으로 나머지 195점을 계산한다." 실제로 Araca 데이터 포맷을 읽는 임포터를
   만들면 설득력이 산다. (그들 고객 = 우리 고객)
3. **경쟁 슬라이드에 §4 사망 선례를 직접 넣어라.** 숨기면 심사위원이 꺼낸다.
4. **Citrine 대비 우위를 명확히 하라** — "데이터가 없어도 (외삽 가능한 물리로)
   시작할 수 있다"가 유일한 답이다. 이건 백테스트로만 증명된다.
5. **§5.4를 절대 건드리지 마라.** dishing/erosion 다이스케일에 손대는 순간
   Cadence와 비교당하고 진다.
6. 한국어/국내 경쟁 재조사.

---

## 부록: 출처 목록

| 항목 | URL |
|---|---|
| Cadence Pegasus DFM (CMP Predictor) | https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/silicon-signoff/pegasus-dfm.html |
| Cadence×AMAT CMP 공동개발 2015 | https://www.prnewswire.com/news-releases/cadence-and-applied-materials-collaborate-on-joint-development-program-to-optimize-planarization-process-through-advanced-cmp-modeling-300102289.html |
| Toshiba Memory CCPO 95.7% | https://sst.semiconductor-digest.com/2019/02/cadence-cmp-process-optimizer-enables-toshiba-memory-to-accelerate-delivery-of-advanced-3d-flash-memory-devices/ |
| Praesagus 인수 $25.8M | https://www.eetimes.com/cadence-bought-dfm-startup-praesagus-for-26-million/ |
| Praesagus SEC S-8 | https://www.sec.gov/Archives/edgar/data/813672/000095013406005971/f18967sv8.htm |
| Praesagus 기업 프로필(MIT 출신) | https://semiengineering.com/entities/praesagus-inc/ |
| DeepChip 업계 증언 | http://www.deepchip.com/items/0453-06.html |
| Siemens Calibre CMPAnalyzer | https://www.siemens.com/en-us/products/ic/calibre-design/design-for-manufacturing/cmp-analyzer/ |
| Siemens CMP 모델빌딩 백서 | https://resources.sw.siemens.com/en-US/technical-paper-building-cmp-models-for-cmp-simulation-and-hotspot-detection/ |
| Lam SEMulator3D | https://www.lamresearch.com/product/semulator3d/ |
| 하이브리드본딩 CMP 모델 (ECTC 2024) | https://ieeexplore.ieee.org/document/10564950 |
| Synopsys Sentaurus Topography | https://www.synopsys.com/manufacturing/tcad/process-simulation/sentaurus-topography.html |
| Sentaurus TCAD 데이터시트 | https://www.synopsys.com/content/dam/synopsys/silicon/datasheets/sentaurus_ds.pdf |
| ViennaPS GitHub | https://github.com/ViennaTools/ViennaPS |
| ViennaPS CMP=boolean 언급 | https://www.iue.tuwien.ac.at/viennacl0 |
| ViennaPS SoftwareX 논문 | https://doi.org/10.1016/j.softx.2025.102453 |
| COMSOL CMP 유동/입자 모델 | https://www.comsol.com/model/modeling-of-flow-field-and-abrasive-particles-in-chemical-mechanical-polishing-cmp-equipment-140171 |
| Araca Inc. | https://aracainc.com/ |
| Araca 폴리셔/트라이보미터 | https://aracainc.com/pages/polishers.html |
| APD-800 Prime 브로슈어 | https://aracainc.com/docs/polishers/APD-800-Prime-Brochure-2023.pdf |
| Araca CMPUG 발표(입출력 리스트) | https://nccavs-usergroups.avs.org/wp-content/uploads/2021/11/CMPUG1021-6-AracaInc-Philipossian.pdf |
| Citrine Platform | https://citrine.io/platform/ |
| Citrine 반도체 조성 사례 | https://citrine.io/wp-content/uploads/2024/07/Case-Study-Semiconductors.pdf |
| Citrine 플랫폼 논문 | https://arxiv.org/html/2607.25039v2 |
| CMP ML 리뷰 2025 | https://www.sciencedirect.com/science/article/pii/S1474034625005567 |
| CMP 원자/양자 시뮬 리뷰 2025 | https://www.sciencedirect.com/science/article/pii/S2666523925001278 |
| 실시간 MRR 예측 (CIRP 2024) | https://www.sciencedirect.com/science/article/abs/pii/S0007850624000416 |
| CMP virtual metrology (JIM 2025) | https://ideas.repec.org/a/spr/joinma/v36y2025i3d10.1007_s10845-024-02335-0.html |
| 슬러리 체류시간 CFD | https://www.sciencedirect.com/science/article/pii/S0263876223000266 |
| SiC CMP 리뷰 (RSC 2025) | https://pubs.rsc.org/tc/article/13/46/22921/316007/Advances-and-challenges-in-chemical-mechanical |
