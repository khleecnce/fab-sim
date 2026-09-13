# FabSim 수요측 조사 — 누가 돈을 내는가

> 2026-09-13 작성. 조사 대상: CMP 전용 물리기반 시뮬레이터(조성→MRR·균일도·결함 예측)의
> **구매자 세그먼트와 지불의사(WTP)**.
> 전제: 낙관적 서술 금지. 근거 없으면 `미확인`으로 표기한다.

---

## 0. 결론 먼저 (읽기 싫으면 여기까지만)

**현 시점에서 이 제품을 "돈 내고 사겠다"는 구매자의 직접 증거는 하나도 찾지 못했다.
지불의사 증거: 미확인.**

그리고 그 이유는 시장조사 실패가 아니라 **제품 상태** 때문이다.
자체 백테스트(`validation/RESULTS.md`, 2026-09-06)가 held-out 3개 데이터셋에서
**Spearman ρ=+0.240, 쌍별 순위 적중 59.9%**를 기록했다. 동전 던지기 50%와의 차이가
10%p다. POSITIONING.md가 스스로 정의한 최소 판매 요건("순위만 맞히면 스크리닝 도구로
쓸모 있다")을 **현재 미달**한다. 진단도 명확하다 — tier2 물리가 순위 관점에서 Preston과
ρ=+1.000으로 동일하고, 정작 실측을 지배하는 인자는 pH·첨가제·입도(=화학)인데 모델 입력에
없다.

따라서 수요 조사의 정직한 답은 이렇다:

> **지금 팔 물건이 없다. 구매자 유무를 논하기 전에 예측력이 먼저다.**
> 예측력이 생겨도 독립 SW 사업의 경로는 좁고, 가장 현실적인 수익화는
> "SW 라이선스"가 아니라 **서비스·장비 결합** 또는 **전략적 인수**다.

수익화 판정: **현 상태 상용화 불가 / 포트폴리오 가치는 별개로 높음**

---

## 1. 구매자 세그먼트 6개 — 하나씩 죽여가며 본다

### S1. 한국·중국 중견 CMP 슬러리 소재사 R&D팀 ★가장 유력

| 항목 | 내용 |
|---|---|
| 대표 기업 | KC Tech, Soulbrain, 동진쎄미켐, SK엔펄스(SKC), Ace Nanochem, KPX Chemical, Hubei Dinglong, Anji Microelectronics |
| 근거 | QY Research / Semiconductor Insight 산업 리포트의 CMP 슬러리 벤더 리스트 [1][2] |
| 왜 유력한가 | ① 상위 5사(Entegris·Resonac·Fujimi·DuPont·Merck)가 시장의 65~68%를 먹고 있고 [1][2], 나머지가 기술로 비벼야 하는 위치 ② 사내 전산화학 조직이 없을 가능성이 높음(미확인, 아래 참조) ③ 한국 소부장 국산화 정책자금이 붙어 있음 [3][4] |
| 치명적 약점 | **이들이 시뮬레이션 SW에 예산을 배정한 사례를 찾지 못했다 — 미확인.** 중소 소재사 R&D 예산에서 SW 라이선스는 통상 장비·인건비·시험웨이퍼 뒤 순위. 확인된 공개 구매 사례 0건 |

**이 세그먼트가 유력한 이유는 "증거가 있어서"가 아니라 "다른 세그먼트가 더 명확히
안 되기 때문"이다.** 소거법의 결과지 긍정적 증거가 아니다.

### S2. 글로벌 슬러리 대기업 (Entegris·Fujimi·Resonac·DuPont·Merck) — ✗ 안 산다

**이미 사내에 만들고 있다. 이게 가장 확실한 부정 증거다.**

- Entegris 공식 블로그: "DFT와 MD 기반 전산화학으로 3D 나노구조용 화학 배합 개발을
  지원하고 있다"고 명시 [5]
- Entegris 채용공고 `Senior Director, Computational Sciences & Digital Engineering`:
  "enterprise Digital Design & Material Innovation Center" 구축, FEM/CFD + 원자단위
  모델링 + AI/ML 팀을 대만·싱가포르·인도·미국·한국에 분산 배치, **500~1,000명 규모
  엔지니어 조직으로 확산** 경험 요구 [6]
- 같은 회사 `Senior Scientist, Computational Materials Solutions` 채용도 진행 중 [7]

즉 업계 1위는 이 문제를 **사서 푸는 게 아니라 조직을 만들어 푼다.** 경력 3.7년
개인이 만든 외부 툴이 이 조직의 구매 결정을 통과할 가능성은 낮다고 보는 게 정직하다.
(반대로 이건 **취업 시장 신호로는 최상급**이다 — §5 참조)

### S3. 팹의 CMP 공정팀 (삼성·SK하이닉스·마이크론·TSMC) — ✗ 구매축이 다르다

- 팹이 쓰는 CMP 시뮬레이션은 **레이아웃(GDSII) 입력 기반 DFM**이다. Cadence CMP
  Predictor가 대표이고, TSMC의 45nm DFM 인증 플로우에 정식 등재됐다 [8][9]
- 팹의 소재 승인은 예측이 아니라 **절차**다. 공개된 자격화 프로토콜은 blanket →
  patterned → product wafer 3단계이고, 선단 로직 기준 총 16~28주가 걸린다 [10]
  (출처 주의: 슬러리 벤더 마케팅 블로그. 수치는 참고용, 1차 출처 미확인)
- 시뮬레이터가 아무리 정확해도 이 절차는 안 없어진다. POSITIONING.md §3의 자기 진단이
  맞다

### S4. SiC·GaN·유리기판 등 신규 기판 업체 — △ 유일하게 "공백"이 실재

- SiC CMP는 실제로 미해결 문제다: 화학적 불활성 때문에 MRR이 통상 <200 nm/h 수준이고,
  산화가 율속단계다 [11]. Fujimi조차 "1.5 μm/h 달성"을 논문으로 발표하는 수준 [12]
- 기존 CMP 모델(실리콘/Cu 기준)이 이 영역을 커버 못 한다 → POSITIONING.md가 말한
  "진짜 공백"은 여기가 맞다
- **그러나 우리 백테스트에서 SiC 데이터셋 성적이 가장 나쁘다.** `sic2023_shear_rheological_L9`
  ρ=+0.200, 쌍적중 55.6%, "스크리닝 불가" 판정. 지배 인자가 입도인데 모델에 입도-MRR
  항이 없다 [13]. 공백이 있다는 것과 우리가 그 공백을 메운다는 건 다른 얘기다

### S5. CMP 서비스·장비 업체 (Araca Inc 등) — △ 고객이 아니라 경쟁자이자 벤치마크

Araca는 이 시장의 **실측 데이터 포인트**로서 가장 값지다.

- 2004년 설립, 애리조나대 캠퍼스 기반, **직원 14명** [14][15]
- 사업: 소모재 분석/기능 테스트, 공정 공동개발, 센서 장착 R&D 폴리셔(APD-800/RDP-500,
  현장 20+대 / 70+대), 교육과정, `Araca Insights` 데이터 분석 SW [14][16]
- 고객: "leading IC makers, consumables suppliers, OEMs, government labs, universities" [14]

**해석 — 이게 이 조사에서 가장 중요한 발견이다.**

CMP 소모재 스크리닝 시장에서 20년 넘게 살아남은 회사가 **직원 14명**이고,
매출 구조는 SW 라이선스가 아니라 **장비 + 실험 서비스 + 교육**이다. 심지어 Araca의
소프트웨어(`Araca Insights`)는 예측 시뮬레이터가 아니라 **데이터 관리·분석 툴**이다 —
즉 이 도메인의 베테랑(전 Intel 재료기술 매니저, 논문 180편)조차 "예측"이 아니라
"측정과 정리"를 팔고 있다.

이건 두 가지를 시사한다:
1. CMP R&D 스크리닝에 **돈을 쓰는 고객은 실재한다** (Araca가 20년 생존)
2. 그러나 그들이 사는 건 **예측 SW가 아니라 실측 서비스**다

### S6. 대학·연구소 — ✗ 시장이 아니다

지불능력 낮고 무료 대안(논문 모델 직접 구현) 존재. 인용·레퍼런스 확보용으로는 가치
있으나 매출원은 아니다.

---

## 2. 지불의사(WTP) 증거 — 직접 증거 0, 간접 증거만

### 찾은 것

| 근거 | 수치 | 해석 |
|---|---|---|
| Cadence의 Praesagus 인수 (2006) | **$25.8M** [17][18] | CMP 모델링 전문 스타트업의 실제 가격표. 단 이건 **레이아웃 기반 DFM**이고 우리 입력축과 다름. 2000년 설립→2006년 매각, MIT 기술 기반 |
| Lam Research의 Coventor 인수 (2017) | 금액 비공개 [19] | 공정 시뮬레이션(SEMulator3D)의 엑싯 경로가 **장비사**임을 확인. POSITIONING.md §7의 주장은 사실에 부합 |
| Schrödinger 소프트웨어 사업 | 2024 Q4 SW 매출 $79.7M, **활성 고객 1,752사**, 상위 10사가 SW 매출의 ~39% [20][21] | 물리기반 시뮬레이션 SW가 **연 수억 달러 규모로 팔리는 산업은 제약/바이오**다. 소재·반도체 소모재가 아니다 |
| 선단 팹 CMP 소모재 신규 공급사 자격화 비용 | 12~24개월, **$500K~$2M** [10] | "고객이 이미 다른 방식으로 돈을 쓰고 있다"는 POSITIONING.md §1 논리의 유일한 정량 근거 후보. **단 출처가 슬러리 판매사 블로그이므로 신뢰도 낮음** |
| CMP 슬러리+패드 세계 시장 | 2024년 $3,181M (슬러리가 66%) [1] | 고객 지갑 크기. **SW 시장 크기가 아니다.** POSITIONING.md §6이 이미 경고한 함정 |

### 못 찾은 것 (= 전부 미확인)

- ❌ CMP 조성 예측 SW의 실제 판매 가격 — **미확인**
- ❌ 슬러리 소재사가 시뮬레이션 SW를 구매한 공개 사례 — **미확인**
- ❌ "데모 사이클 1회당 비용" 1차 출처 — **미확인** (벤더 블로그 추정치만 존재)
- ❌ FabSim 같은 조성입력형 CMP 시뮬레이터의 직접 경쟁 제품 — **존재 자체가 미확인**
  (= 공백일 수도, 시장이 없어서 아무도 안 만든 것일 수도. 현 데이터로는 구분 불가)

**마지막 항목을 오독하지 마라.** "경쟁자가 없다"는 좋은 신호가 아니다.
CMP는 40년 된 성숙 공정이고, MIT Boning 그룹·Araca·Entegris 사내조직·수백 편의 논문이
붙어 있는 영역이다. 이 사람들이 다 못 만든 게 아니라 **만들 수 있었어도 상품이 안 됐을
가능성**을 먼저 배제해야 한다. 우리 백테스트 ρ=+0.240은 오히려 후자를 지지하는 증거다.

---

## 3. 수익화 경로 3개와 각각의 현실성

### 경로 A. SW 라이선스 (시트 단가 × 시트 수) — 현실성 낮음

- 선례 부재: CMP 조성 예측 SW의 판매 사례 미확인
- 구매 주체 불명확: 소재사 R&D팀의 SW 예산 존재 여부 미확인
- 대기업 고객은 사내 조직으로 대체 [5][6]
- 중소 고객은 지불능력 제약
- **전제 조건: 백테스트 쌍적중률이 최소 80% 이상으로 올라가야 대화 자체가 시작된다**

### 경로 B. 서비스·컨설팅 결합 (Araca 모델) — 현실성 중간, 단 천장이 낮다

- Araca가 20년간 검증한 모델. **단 직원 14명이 천장이다** [15]
- 시뮬레이터는 서비스의 **차별화 요소**로 쓰고, 과금은 프로젝트 단위
- 장점: 예측력 100%가 아니어도 판매 가능(전문가 해석이 갭을 메움)
- 단점: 사람이 곧 매출 → 확장 불가. "사업화"라기보다 **1인 컨설팅 개업**에 가깝다
- 개인 입장에서는 **가장 낮은 리스크의 실제 수익 경로**

### 경로 C. 전략적 인수 (EDA·장비·소재 대기업) — 현실성 낮음, 그러나 유일한 큰 엑싯

- 선례: Praesagus→Cadence $25.8M [17], Coventor→Lam [19]
- 단 두 사례 모두 **팀 + 고객 + 검증된 제품**이 있었다. Praesagus는 TSMC 인증 플로우에
  등재된 상태였다 [9]
- 현재 FabSim은 세 가지 다 없음
- **가장 정직한 평가: 이 경로는 지금 논할 단계가 아니다**

### 자금원(매출 아님): 국책과제

- CMP 슬러리 관련 소부장 국책과제가 실재하고 계속 발주된다 [3][4]
- 중소기업 전략기술 로드맵(2024)에 **"디지털 트윈 기반 CMP 공정 가상 시뮬레이션으로
  최적 소재·공정조건 설계"**가 기술개발 논의 항목으로 명시돼 있다 [22]
  → **정부 문서가 이 방향을 인정한 유일한 공식 근거.** 과제 수주 명분으로 쓸 수 있다
- 단 이건 **고객 수요가 아니라 정책 수요**다. 매출로 착각하면 안 된다

---

## 4. 가장 큰 리스크 — 우선순위대로

1. **예측력 미달 (현재 진행형, 최대 리스크)**
   백테스트 ρ=+0.240 / 쌍적중 59.9%. 스스로 세운 최소 요건 미달. 진단상 병목은
   계산이 아니라 **입력에 화학이 없다**는 것 [13]. 이걸 못 고치면 나머지 논의는 무의미
2. **"시장이 없어서 아무도 안 만든 것"일 가능성**
   40년 성숙 공정 + 정상급 연구그룹 다수 + 경쟁 제품 부재 = 공백이 아니라 **묘지**일
   수 있다. 반증 방법: 소재사 R&D 실무자 10명 인터뷰(현재 0명 수행)
2b. **대기업 고객의 사내 대체** — Entegris가 이미 전사 모델링 센터를 세우는 중 [6]
3. **WTP 직접 증거 전무** — 조사로 안 나온다. 고객 대화로만 나온다
4. **고객 데이터 접근 차단** — 조성은 소재사의 핵심 IP. 온프레미스 설계 필수
   (POSITIONING.md §4-3이 이미 지적)

---

## 5. 그래서 뭘 해야 하나 — 두 목적을 분리하라

사용자의 목적은 ①이직 포트폴리오 ②사업화 두 개다. **이 둘은 지금 요구사항이 다르고,
①은 이미 상당히 달성돼 있지만 ②는 아직 출발선 근처다.**

### ① 이직 포트폴리오 — 가치 높음, 이미 작동 중

- Entegris가 **"실험 데이터 + 모델링 + AI로 발견을 가속한 경험"**, **"모델 캘리브레이션·
  검증·불확실성 정량화"**를 명시적으로 요구하는 포지션을 열어놨다 [7]. 요구 경력
  1~3년 — **사용자의 3.7년과 정확히 겹친다**
- 아이러니하게도 **백테스트가 나쁜 것 자체가 포트폴리오로는 강점**이다. ρ=+0.240을
  그대로 기록하고, 진단으로 "우리 tier2는 순위상 Preston과 동일하다"까지 도달한
  문서는 **검증 능력의 증거**다. 대부분의 지원자 포트폴리오에는 검증 자체가 없다
- 권장: `validation/RESULTS.md`를 숨기지 말고 **전면에 내세워라**

### ② 사업화 — 아직 아니다. 다음 게이트 2개

**게이트 1 (기술).** 백테스트 쌍적중률 **80% 이상**을 held-out에서 달성.
못 하면 사업화 중단. 현재 필요한 것은 마케팅이 아니라 pH·첨가제·입도 항의 도입.

**게이트 2 (수요).** 소재사 CMP R&D 실무자 **10명 인터뷰**. 질문은 하나로 좁힌다:
> "후보 조성 20개를 계산으로 5개까지 줄여주는 도구가 있다면, 연간 얼마까지 쓰겠습니까?
> 그 예산은 누구 주머니에서 나옵니까?"

**이 질문에 대한 답이 나오기 전까지 IR 덱·TAM·가격표는 전부 허구다.**
현재 인터뷰 수행 건수: **0.**

---

## 출처

[1] QY Research, "CMP Slurry and Pads — Global Market Share and Ranking, 2025-2031",
    https://www.qyresearch.com/reports/3430258/cmp-slurry-and-pads (2024년 $3,181M, 상위 5사 68%)
[2] Semiconductor Insight, "CMP Polishing Slurry Market 2025",
    https://semiconductorinsight.com/report/cmp-polishing-slurry-market/ (상위 5사 ~65%)
[3] 디지털투데이, "반도체 소재 업계, HBM 핵심 CMP 슬러리 기술 속속 국산화", 2024-06-04,
    https://www.digitaltoday.co.kr/news/articleView.html?idxno=519893
[4] RnDcircle 국가R&D과제 DB, "반도체 화학기계적 연마용 슬러리 개발 및 실증평가",
    https://app.rndcircle.io/gov-grant/999248b2-0450-4c86-bbaf-9e088e627c91
[5] Entegris Blog, "Achieving the Third Dimension Through Molecular Modeling",
    https://blog.entegris.com/achieving-the-third-dimension-through-molecular-modeling
[6] Entegris 채용공고, "Senior Director, Computational Sciences & Digital Engineering",
    https://www.qarera.com/job/936288
[7] Entegris 채용공고, "Senior Scientist, Computational Materials Solutions",
    https://www.remoterocketship.com/us/company/entegris/jobs/senior-scientist-computational-materials-solutions-united-states-remote/
[8] Cadence 10-K (FY2007), DFM 제품 목록 중 "Cadence CMP Predictor",
    https://content.edgar-online.com/ExternalLink/EDGAR/0000950134-08-003361.html
[9] EDN, "How low can you go? A look at 45-nm-IC-design challenges"
    (CPTA가 CMP 시뮬레이션용으로 Cadence CMP Predictor를 인증),
    https://www.edn.com/how-low-can-you-go-a-look-at-45-nm-ic-design-challenges/
[10] JEES(슬러리 벤더) 기술 블로그, "How to Select a Copper CMP Slurry" 및
    "Top CMP Materials Suppliers 2026", https://jeez-semicon.com/blog/
    ⚠ **벤더 마케팅 콘텐츠. 수치(16~28주, $500K~$2M, 12~24개월)는 1차 출처 미확인**
[11] Advanced Materials Interfaces, "Chemical–Mechanical Polishing of 4H Silicon
    Carbide Wafers", 2023, https://advanced.onlinelibrary.wiley.com/doi/10.1002/admi.202202369
[12] Fujimi, "Fujimi's New SiC CMP Slurry Development", ECS Meeting Abstracts MA2019-01,
    https://iopscience.iop.org/article/10.1149/MA2019-01/17/1043
[13] 자체 산출물: `/Users/khleecnce/fab-sim/validation/RESULTS.md` (2026-09-06 백테스트)
[14] Araca Inc 공식 사이트, https://aracainc.com/ (설립 2004, 고객군, 서비스 범위)
[15] LinkedIn 기업 페이지, Araca Inc — 직원 14명, https://linkedin.com/company/aracainc
    ⚠ LinkedIn 추정치
[16] Philipossian et al., "CMP Knowledge Foundry and Big Data Analytics", NCCAVS CMPUG 2021,
    https://nccavs-usergroups.avs.org/wp-content/uploads/2021/11/CMPUG1021-6-AracaInc-Philipossian.pdf
[17] EE Times, "Cadence bought DFM startup Praesagus for $26 million",
    https://www.eetimes.com/cadence-bought-dfm-startup-praesagus-for-26-million/
[18] Cadence SEC Form S-8 (2006-03-17 합병계약), https://www.sec.gov/Archives/edgar/data/813672/000095013406005971/f18967sv8.htm
[19] Lam Research IR, "Lam Research Completes Acquisition of Coventor", 2017-08-31,
    https://investor.lamresearch.com/2017-08-31-Lam-Research-Completes-Acquisition-of-Coventor,-a-Leader-in-Simulation-and-Modeling-Solutions
[20] Schrödinger 2024 Q4/FY 실적 발표, https://ir.schrodinger.com/press-releases/news-details/2025/Schrdinger-Reports-Strong-Fourth-Quarter-and-Full-Year-2024-Financial-Results/default.aspx
[21] Reportify, Schrödinger 2024 10-K 요약 (활성 고객 1,752사, 상위 10사 ~39%),
    https://reportify.ai/filings/1092360562832183296
[22] 중소기업 전략기술 로드맵 2024, 디지털 트윈 기반 CMP 공정 시뮬레이션 항목,
    https://smroadmap.smtech.go.kr/mpsvc/dtrprt/mpsvcDtrprtDetail.do?cmYyyy=2024&cmIdx=3691
