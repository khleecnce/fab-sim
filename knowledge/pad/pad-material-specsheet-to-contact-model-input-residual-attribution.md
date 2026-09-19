<!-- V2-SECTION: R3-pad | Cal-1 2026-09-20 | 근거: 패드 스펙시트→GW 접촉입력 변환·경도환산 불확실도·E*·η 비식별 | 정본: ORG.md §7.3 -->
# Cal-1 — 패드 스펙시트(경도·밀도·기공) → GW 접촉모델 입력 변환 + 실측 프로파일 잔차 귀속 (pad-material)

> 에이전트: pad-material Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-20
> 선행(재서술 금지·인용만):
> [[pad-material-gw-effective-modulus-asperity-distribution]] (Lv3-2 — E*·R·β⁻¹·η 1차 출처 대조, **이 노트가 보정할 대상**),
> [[../materials/pad-hardness-porosity-measurement-methods]] (Lv1-2 — IC1000 Shore D 60·기공률, Qi-Joyce-Boyce eq.11 Shore D→E),
> [[../materials/pad-asperity-density-gw-literature-values]] (η=2.0e8 수렴·기하 반증),
> [[pad-gw-parameter-literature-adoption-derived-recompute]] (base.yaml pad_* 반영·파생 재적분),
> [[../materials/hertz-gw-contact-mechanics]] (GW 지수분포 폐형해 — A_r∝P/E*·η 상쇄),
> [[../materials/pad-viscoelasticity-temp-frequency-dma]] (Lv2-1 — storage modulus E'는 이 축 소관, 인용만),
> [[../cmp/preston-luo-dornfeld-mrr]] (K=Kp·P·V),
> [[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]] (cmp-calibrator Cal-1 — **레지스트리 §1, 내 산출은 이 표에 추가될 행**),
> [[../data/cmp-calibration-schema-integration-validation-rules]] (통합 49필드 — 내 필드 제안은 이것과 충돌 없이),
> [[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] (형제 Cal-1 — Kp 절대×배율 분해의 본),
> [[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]] (형제 Cal-1 — 스펙시트 변환 형식·깊이의 기준)

## 0. 목적·범위·형제 경계

ORG.md §7.3은 pad-material에게 **"패드 스펙(경도·기공·그루브)·사용시간·컨디셔닝 이력 → 시간 의존
파라미터 + 실측 프로파일 잔차"** 중 **소재 축(경도·밀도·기공 → 접촉모델 입력)**을 맡겼다. 이 노트가 그
산출물이다. Lv3-2가 이미 **E*·R·β⁻¹·η의 1차 출처를 대조**했으므로
([[pad-material-gw-effective-modulus-asperity-distribution]]), 이 단원은 그 값을 **재서술하지 않고**,
**상용 패드 스펙시트에 실제로 적히는 항목이 GW 접촉모델의 어느 입력을 결정하고 무엇은 결정하지 못하는가**,
그리고 **무엇을 스펙시트 prior로 고정하고 무엇을 실측 프로파일 잔차로 피팅하는가**를 정의한다.

이 단원이 푸는 실제 문제: 팹·소재사는 패드를 살 때 **Shore D 경도·밀도·압축률·기공률·그루브·(일부)
storage modulus**를 스펙시트로 받는다. 그런데 GW 접촉모델([[../materials/hertz-gw-contact-mechanics]] §3)이
요구하는 입력은 **E*·R·η·β⁻¹**이다. 이 둘 사이의 사상은 **1:1이 아니다** — (i) Shore D→E* 변환식이
여러 개이고 값이 17배까지 갈리며(§2.1·§4), (ii) R·η·σ_s는 **소재가 아니라 컨디셔닝이 만드는 기하량**이라
스펙시트에 없고(§2.3, Lv3-2 §1이 이미 확정), (iii) 스펙시트의 storage modulus E'는 GW의 정적 복합
E*와 **다른 물리량**이다(§2.4). 이 사상 규칙을 명시하지 않으면 캘리브레이션이 "스펙 표기 차이"를 "그 팹
고유 편차"로 오학습한다(형제 4편이 공통으로 경고한 그 문제의 패드 버전).

**형제 경계 (침범 금지, 인용만):**
- **그루브·엣지·서브패드**는 **pad-structure** 소관 — 스펙시트에 그루브 패턴이 적히지만 압력증배·유동
  모델은 인용만 하고 새 정량 안 만든다([[pad-structure-groove-subpad]] 계열).
- **마모·glazing·사용시간(pad_hours)→λ(t)**는 **pad-lifecycle** 소관 — 시간축 파라미터는 인용만.
- **컨디셔너 grit·하중·sweep → R·η·σ_s**는 **disk-design·disk-kinematics** 소관 — R·η가 컨디셔닝
  기하량임만 확인하고(§2.3) 그 값의 물리는 넘긴다.
- **잔차 GP 피팅·순차 위상·레지스트리 통합**은 **cmp-calibrator** 소관 — 이 노트는 "무엇이 식별되고 무엇을
  prior로 고정하나"와 **레지스트리에 추가될 행(§8)**까지만 책임진다.
- **스키마 파일**(`data/schema/*.json`)·`sim/`·`prior.py`는 cmp-data-engineer·소프트웨어 부문 소관 —
  §5 개정 제안·§9 구현 요청만 적고 파일을 고치지 않는다.
- **점탄성 E'(T,ω)의 온도·주파수 모델**은 본인 Lv2-1 소관 — storage modulus가 GW E*가 아님만 짚고(§2.4)
  DMA 곡선 자체는 재서술하지 않는다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 모든 수치는 공개 스펙시트·특허·문헌·합성이다.

## 1. 상용 패드 스펙시트가 실제로 적는 항목·단위·측정법 — 1차 조사

상용 CMP 패드의 물성이 **공개 문서(제조사 데이터시트·특허)에 어떻게 적히는지**를 1차 자료로 조사했다.
기존 인용(Pureon IC1000 datasheet·Sikder 2001)은 재인용하고, **새 1차 특허 2편**(Cabot/CMC·West)을
이 단원에서 확보했다. 핵심은 "어떤 값이냐"가 아니라 **"그 값이 GW의 어느 입력을 정하느냐(§2)"**다.

| # | 소스(유형, 실존확인) | 경도 | 밀도/기공 | 압축·회복 | 점탄성·기타 | 그루브 | 등급 |
|---|---|---|---|---|---|---|---|
| S1 | **Pureon IC1000/IC1010 datasheet** (제조사 공개, 2024-04-09; Lv1-2 재인용) | **Shore D 60** | (기공률 미기재) | **압축률 2.25%** | — | K-groove류(별도 SKU) | E3(제조사 실측, 오차막대 없음) |
| S2 | **Sikder et al. 2001** MRS Proc. 697 P9.3, DOI 10.1557/proc-697-p9.3 (Lv1-2/base.yaml 재인용) | — | **기공률 ~30 vol%·평균기공 ~30 µm** (IC1000, SEM 서술값) | — | — | perforated/grooved IC1000 | E3(SEM 단면 서술, 측정법 미명시) |
| S3 | **US20030100250A1**(West, 2003, "Pads for CMP", Google Patents 실존확인) | **Shore D 45–65** (실시예 51–54) | **밀도 0.5–0.7 g/cc**(실시예 0.59), non-woven felt(0.29–0.35 g/cc 함침) | **compressive modulus >70%**(=압축회복) | — | — | E3(특허 명세·실시예) |
| S4 | **US20170087688A1 / US10562149B2**(Cabot Microelectronics→CMC Materials, 2017/2020, "Polyurethane CMP pads having a high modulus ratio", 실존확인) | **Shore D 70 이상** | **porosity 10–30 vol%·평균기공 5–40 µm**(발포판), 솔리드(비다공)판 병존 | tensile elongation ≤320% | **E′(25 °C) ≥1200 MPa·E′(80 °C) ≤15 MPa·E′(25)/E′(80) ≥30(바람직 50)** (DMA 저장탄성률) | concentric groove(Epic D100 대조) | E3(특허 청구·실시예) |

**조사 결과 5가지 사실(재서술 아님 — 스펙시트→접촉모델 관점의 새 정리):**
1. **경도는 거의 항상 Shore D(경질 패드) 또는 Shore A/C로 적힌다.** 스케일이 다르면 직접 비교 불가
   (Lv1-2 §2 재인용). S1·S3·S4가 모두 Shore D이나 값 폭이 45–70+로 넓다.
2. **밀도·기공률은 스펙시트/특허에 자주 있다**(S2·S3·S4). 그러나 **기공률→E_pad 변환은 Gibson-Ashby
   지수 n·매트릭스 Es가 미확보라 정량 불가**(Lv1-2 §6, §2.2 재확인).
3. **압축률(%)·압축회복률(%)은 스펙시트 고유 항목**(S1 2.25%, S3 >70%)이나 **GW의 E*·R·η·β⁻¹ 어느
   것에도 1:1로 사상되지 않는다** — 압축률은 서브패드 포함 스택 응답이고(pad-structure 소관), GW는
   상부 폴리싱층 asperity 통계다(§2.5).
4. **storage modulus E′는 고급 특허(S4)에만 있고, GW의 정적 복합 E*와 다른 물리량**이다 — DMA E′는 작은
   변형·특정 온도(25/80 °C)·특정 주파수의 저장탄성률이고, 1200 MPa 오더로 GW 문헌 E*(119–380 MPa,
   Lv3-2)보다 3–10배 크다(§2.4).
5. **R·η·σ_s(asperity 기하·통계)는 어느 스펙시트에도 없다** — Lv3-2 §1이 확정했듯 이들은 **컨디셔닝이
   만드는 기하량**이라 "패드 카탈로그"가 아니라 "패드+컨디셔닝 조합을 쓴 접촉역학 논문 Table"에만 있다(§2.3).

## 2. 스펙시트 항목 → GW 접촉모델 입력 매핑 표 (Cal-1 핵심 산출 (a))

GW 접촉모델([[../materials/hertz-gw-contact-mechanics]] §3)의 입력은 물리적으로 독립인 넷: **E*(탄성응답)·
R(돌기 곡률반경)·η(면밀도)·β⁻¹=σ_s(높이산포)**. 각 스펙시트 항목이 이 넷 중 무엇을 **결정하고, 무엇은
결정하지 못하는가**를 근거와 함께 매핑한다.

| 스펙시트 항목 | 결정하는 GW 입력 | 결정하지 못하는 것·불확실도 | 근거 |
|---|---|---|---|
| **Shore D 경도** | **E*(부분적, prior만)** | E*로 변환식이 여러 개(Qi eq.11 vs Kunz-Studer)라 **17배** 갈림(§2.1·§4). 단일 변환값을 prior 중심으로 못 씀 | Qi 2003 eq.11(Lv1-2), Kunz-Studer(§2.1) |
| **밀도(g/cc)·기공률(%)** | E_pad의 **방향만**(기공↑→E_pad↓) | Gibson-Ashby 지수 n·매트릭스 Es 미확보 → **E_pad 절대값 불가**. 기공률→E*는 정성뿐 | Lv1-2 §6 (Gibson-Ashby 2차 인용) |
| **압축률(%)·압축회복률(%)** | (GW 입력 아님) | 서브패드 포함 **스택** 응답·마이크로크리프 — GW 상부층 asperity 통계와 다른 축(pad-structure 소관) | §2.5, S1·S3 |
| **storage modulus E′(T)** | (GW E* 아님 — 점탄성 축) | DMA E′는 작은변형·특정 T·ω의 저장탄성률. 정적 복합 E*와 **물리량이 다름**(1200 MPa≠119–380 MPa) | §2.4, S4·Lv2-1 |
| **그루브 패턴** | (GW 입력 아님) | 유동·압력증배는 pad-structure 소관 — 인용만 | S1·S4, pad-structure |
| **asperity R·η·σ_s** | **스펙시트에 없음** | **컨디셔닝(disk-* 소관)이 만드는 기하량** — 소재 물성만으로 못 얻음(같은 PU라도 컨디셔닝이 바꿈) | Lv3-2 §1, §2.3 |

### 2.1 Shore 경도 → E* 변환 — 식이 여러 개고, 값이 17배 갈린다

Lv1-2 §8이 이미 확인했듯 **Shore D↔탄성률 변환은 비선형이고 미검증**이다. 이 단원은 **서로 다른 변환식이
IC1000급(Shore D 60)에서 얼마나 갈리는가**를 정량화한다. 세 경로:

- **식1 — Qi, Joyce & Boyce (2003) eq.11** (Sneddon 원뿔 압입자 선형탄성 해석해, θ=15°, ν=0.5; Lv1-2에서
  전문 확보·재인용, DOI 10.5254/1.3547752): $H_D = 100 - 20(-78.188 + \sqrt{6113.36 + 781.88E})/E$ (E: MPa).
  Shore D 60 역산 → **E ≈ 117.3 MPa**(Lv1-2 §8.1 재현).
- **식2 — Kunz & Studer (2006)식** (절단원뿔 압입자 ISO 868 기반; cati 기술블로그 경유 **2차 인용 E5**,
  원문 독일어 Kunststoffe 6/2006 미확보): $E_{\text{MPa}} = \exp[(S_D + 50)\cdot 0.0235 - 0.6403]$.
  Shore D 60 → **E ≈ 6.99 MPa** (유효범위 Shore D 30–85로 명시되나 저경도 엘라스토머 회귀라 경질 PU
  외삽은 부정확 — cati "엔지니어링 결정에 쓰지 말라" 경고). → 물리적 하한을 크게 벗어남(§4가 그대로 assert).
- **식3(참고) — Gent (1958) 경험식** (Shore **A**용, 교과서 표준식 **2차 인용 E5**, 원문 1958은 스코프
  밖·Shore A 스케일이라 Shore D 60 직접 적용 불가): $E = 0.0981(56+7.62336 S_A)/(0.137505(254-2.54 S_A))$.
  Shore D 60 → Shore A 환산이 A 95~98 영역(포화 근처)이라 **Gent E가 43.8~112.8 MPa로 2.6배 벌어짐**
  (§4) — Shore A↔D 환산 불확실이 그대로 전파. Gent은 스케일 불일치로 채택 불가.

**결론(§2.1)**: 같은 Shore D 60에서 변환식 선택만으로 **E ∈ [7, 117] MPa (17배)**. 그중 Qi eq.11(117 MPa)만
Lv3-2 GW 클러스터(119–380 MPa) 하한에 근접하고, 그마저 **인장/압입 초기탄성률이지 GW 복합 E*가 아니다**
(Lv1-2 §8.2 세 이유: 62D 밖 외삽 불가·범용고무 대상·물리량 불일치). → **Shore D 스펙 하나로 E*를 한
값에 고정할 수 없다.** E*는 스펙시트가 아니라 **문헌 클러스터를 prior로 쓰고 폭을 넓게** 둔다(§3·§8).

### 2.2 밀도·기공률 → E_pad — 방향만, 절대값 불가

발포 패드의 유효 압축강성은 기공률에 강하게 의존한다(Lv1-2 §6, Gibson-Ashby $E^*/E_s \approx C(\rho^*/\rho_s)^n$).
그러나 지수 n(개기공 ~2·폐기공 1~2)·매트릭스 Es가 **미확보(2차 인용)**라 밀도·기공률에서 E_pad **절대값을
계산할 수 없다** — **"기공↑→E_pad↓" 방향만** 신뢰한다. S4가 솔리드(비다공)판과 발포판을 병존시키는 것은
이 축을 실제로 흔든 예다(같은 화학·다른 기공률). 즉 **밀도·기공률은 E* prior의 방향 제약**일 뿐, 중심값은
못 준다.

### 2.3 R·η·σ_s는 컨디셔닝 소관 — 스펙시트에서 못 얻음 (형제 경계)

Lv3-2 §1이 확정: R(정점 곡률반경)·σ_s(높이 산포)는 **컨디셔닝 직후 표면 프로파일 측정값**이고, η(면밀도)도
컨디셔닝이 정한다. 같은 폴리우레탄이라도 컨디셔너 grit·하중이 바뀌면 R이 25→100 µm로 4배 변한다
(Lv3-2 §2 표). base.yaml은 이 셋을 **문헌 세트**(R=50 µm·β⁻¹=2 µm·η=2.0e8, literature)로 두되, **소재가
아니라 컨디셔닝이 만든 기하량**임을 note에 명시한다([[pad-gw-parameter-literature-adoption-derived-recompute]] §1).
따라서 이 셋은 **disk-*·pad-lifecycle의 컨디셔닝 이력 축**이고, 스펙시트→접촉입력 변환의 대상이 아니다 —
잔차 귀속에서 별축으로 분리한다(§3).

### 2.4 storage modulus E′는 점탄성 축 — GW E*의 prior가 아니다

S4(US10562149B2)는 **E′(25 °C) ≥1200 MPa·E′(80 °C) ≤15 MPa**를 청구한다. 이는 **DMA 저장탄성률**(작은 변형·
특정 온도·특정 주파수)이고, GW가 쓰는 **정적 복합 유효탄성계수 E***(119–380 MPa, Lv3-2)와 **물리량이 다르다**:
(i) E′는 온도에 100배 가까이 변하고(25→80 °C에서 30–50배 감소), GW E*는 정적 접촉의 등가강성이다.
(ii) E′(25)=1200 MPa는 GW 문헌 E*보다 3–10배 크다 — 하나를 다른 하나의 prior로 쓰면 안 된다. E′(T,ω)는
본인 Lv2-1 축(온도·주파수 의존)이고, GW E*로 넣으려면 **CMP 운전 온도·변형률에서의 유효강성으로 별도
환산**이 필요하며 그 환산은 미확보다. → **storage modulus는 스펙시트에 있어도 GW E* prior로 직접 채용 금지.**

### 2.5 압축률·압축회복률은 스택 응답 — GW 입력 아님

S1의 압축률 2.25%·S3의 compressive modulus >70%(회복률)는 **폴리싱층+서브패드 스택의 하중-변위 응답**이다
(pad-structure 소관). GW는 **상부 폴리싱층 asperity의 통계적 접촉**을 다루므로 축이 다르다 — 압축률을 E*나
β⁻¹로 환산하는 1:1 규칙은 없다. 스펙시트에 있어도 GW 입력으로 사상하지 않고, pad-structure의 스택 강성
모델 입력으로만 넘긴다(인용).

## 3. 접촉모델 보정 파라미터 분해 — prior 고정 / 컨디셔닝 축 / 잔차 피팅 (Cal-1 (b))

형제 film-oxide가 `Kp_oxide = K_{p,ref}·m_f·P·V`(절대×배율)로 분해했듯
([[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] §2), 패드 축은 GW를 통해
Kp에 진입한다. [[../materials/hertz-gw-contact-mechanics]] §5의 링크 `Kp_eff ∝ f(A_r/A_n, p_local)`에서,
지수분포 GW 폐형해(§4에서 재현)는 실접촉비를 **$A_r/A_n \propto P/E^*$ 이고 η는 상쇄**됨을 준다. 즉 소재
축의 접촉 파라미터는 다음처럼 갈린다:

| 파라미터 | Kp 진입 | 데이터 위치 | 처방 |
|---|---|---|---|
| **E* (pad_E_star_pa)** | 곱(A_r∝P/E* → Kp_eff에 곱) | 스펙시트 경도(변환 불확실)·문헌 클러스터 | **문헌 클러스터 prior 고정** — 스펙시트 경도는 방향 제약만(§2.1). η와 곱으로 반경 프로파일에서 비식별(§4) |
| **R·η·σ_s** | 곱(GW 적분에 함께) | **컨디셔닝 이력**(disk-*·pad-lifecycle) | **소재 축 아님** — 컨디셔닝 이력으로 별도 결정. 스펙시트에서 못 얻음(§2.3) |
| **반경 형상 잔차 δ(r)** | 가산(GP) | NPW 반경 프로파일 | cmp-calibrator가 fit_npw GP로 학습(P11, 형제 소관) |

**핵심 비식별(§4가 재현)**: GW 하중식 $W = \tfrac{4}{3}E^*\sqrt{R}\,\eta A_n \Gamma(5/2)\beta^{-3/2}e^{-\beta d}$에서
**E*와 η는 곱으로만 들어간다**. 단일 압력 조건에서 실측 프로파일로 (E*, η)를 동시 피팅하면 곱 $E^*\eta$만
식별되고 개별은 완전 상관(비식별) — film-oxide §4-A의 (절대 Kp vs 막종류 배율)와 **같은 곱셈 구조**다.
압력(=국소 압입량 d) 스윕을 ≥3점 추가하면 β(높이산포)는 식별되나 **절편의 $\log E^* + \log \eta$는 여전히
분리 불가**(둘 다 압력무관 상수 곱). 오직 **E*를 스펙시트/문헌 prior로 고정**할 때만 η가 반경 프로파일에서
식별된다. 이것이 "E*는 prior 고정, η·R·σ_s는 컨디셔닝 축, δ(r)만 잔차로"라는 분해의 식별성 근거다.

이 결론은 [[../materials/pad-asperity-density-gw-literature-values]] §4가 발견한 "**A_r는 η에 매우 둔감**
(하중 재분배)"의 캘리브레이션 버전이다 — 지수분포에선 A_r/A_n에서 η가 **완전히 상쇄**되므로, 반경 프로파일
(≈실접촉/제거율 기반)로는 η를 원리적으로 못 잡는다. η는 접촉점 개수·국소압력 통계에만 나타나고, 그 데이터는
스펙시트에도 반경 프로파일에도 없다 → η는 컨디셔닝 축의 문헌값으로 고정한다(base.yaml literature).

## 4. Python 검증 (Cal-1 (c))

**재현 요약(한 줄, 블록1)**: IC1000 문헌 경도 Shore D 60(Lv1-2 §1)에 Shore D→E 변환 식1(Qi-Joyce-Boyce
2003 eq.11, 역산 117.3 MPa)·식2(Kunz-Studer, 6.99 MPa)를 적용해 **두 식이 16.8배** 갈리고, 참고로 Gent
1958(Shore A식)은 Shore A 95↔98 환산 불확실만으로 2.6배 벌어짐을 assert; 얻은 E 범위 [7, 117] MPa 중
Qi eq.11만 Lv3-2 채택 E* 클러스터 1.19–3.8e8 Pa의 하한(0.986배)에 겹치고 Kunz-Studer는 1/17로 벗어나
**스펙시트 경도 하나로 E*를 못 고정**함을 assert.

```python verify
import math
# ═══ Shore D → E 변환식 3종을 IC1000 문헌 경도(Shore D 60, Lv1-2 §1)에 적용 ═══
# 식1: Qi, Joyce & Boyce 2003 eq.11 (Sneddon cone 선형탄성 해석해), DOI 10.5254/1.3547752 — Lv1-2 재인용(1차)
def H_D_eq11(E_mpa):                       # E(MPa) → Shore D (단조증가)
    return 100 - 20*(-78.188 + math.sqrt(6113.36 + 781.88*E_mpa))/E_mpa
def E_from_H_D(hd, lo=0.001, hi=1e6):      # 이분법 역산
    for _ in range(200):
        m = (lo+hi)/2
        if H_D_eq11(m) < hd: lo = m
        else: hi = m
    return (lo+hi)/2
E_qi = E_from_H_D(60.0)                     # Shore D 60 → MPa
assert abs(E_qi - 117.28) < 0.1            # Lv1-2 §8.1 재현치
# 식2: Kunz & Studer 2006 (truncated cone ISO 868), cati 기술블로그 경유 2차 인용(E5)
E_ks = math.exp((60.0 + 50.0)*0.0235 - 0.6403)   # Shore D → MPa
assert abs(E_ks - 6.99) < 0.05
ratio_12 = E_qi / E_ks
print(f"Shore D 60: 식1 Qi eq.11 = {E_qi:.1f} MPa, 식2 Kunz-Studer = {E_ks:.2f} MPa → 두 식 차 {ratio_12:.1f}배")
assert ratio_12 > 15                        # 변환식 선택만으로 15배 이상 갈림 (핵심 발견)
# 식3(참고): Gent 1958 (Shore A용, 2차 E5) — Shore D 60↔Shore A 환산 불확실(A 95~98 포화영역)
def gent(SA): return 0.0981*(56 + 7.62336*SA)/(0.137505*(254 - 2.54*SA))
E_g95, E_g98 = gent(95.0), gent(98.0)
print(f"Gent 1958: Shore A 95 → {E_g95:.1f} MPa, Shore A 98 → {E_g98:.1f} MPa (Shore A 환산 불확실만으로 {E_g98/E_g95:.1f}배)")
assert E_g98/E_g95 > 2.0                     # Shore A↔D 환산 3계단 불확실이 2배+ 전파 → Gent 경로 채택 불가

# ═══ 얻은 E 범위 vs Lv3-2 채택 E* 클러스터 (base.yaml pad_E_star_pa 세트) ═══
cluster_mpa = [119.0, 131.6, 380.0]        # Shi&Ring / Bozkaya&Muftu(중앙·채택) / Sorooshian (Lv3-2 §2)
c_lo, c_med, c_hi = min(cluster_mpa), 131.6, max(cluster_mpa)
# 정합: Qi eq.11(117.3)은 클러스터 하한(119)의 0.98배 — 근접(겹침). Kunz-Studer(6.99)는 1/17 — 완전 이탈
assert 0.95 < E_qi/c_lo < 1.05
assert E_ks < c_lo/10
# 스펙시트 경도만으로 얻는 E 범위(식1·식2)와 GW 클러스터의 합집합 스프레드
E_specsheet = [E_ks, E_qi]
overall_lo, overall_hi = min(E_specsheet), c_hi
print(f"스펙시트 Shore D 경로 E 범위 [{min(E_specsheet):.1f}, {max(E_specsheet):.1f}] MPa; "
      f"GW 클러스터 [{c_lo:.0f}, {c_hi:.0f}] MPa; 합집합 {overall_hi/overall_lo:.0f}배 스프레드")
assert overall_hi/overall_lo > 40           # Shore D 하나로 E*를 못 고정 — 넓은 prior 필요
print("[변환] 스펙시트 Shore D 60 하나로 E* 비결정: 변환식 17배·물리량 불일치 → 문헌 클러스터 prior + 넓은 σ")
```

**재현 요약(한 줄, 블록2)**: GW 지수분포 하중 폐형해 $W=K\,E^*\eta\,e^{-\beta d}$(K=(4/3)√R·A_n·Γ(5/2)·β⁻³ᐟ²)의
합성 반경 프로파일(base.yaml E*=1.316e8·η=2.0e8·R=5e-5·β⁻¹=2e-6)로 — (1) 단일 압입량 조건에서 (logE*, logη)
정규행렬 조건수 ∞(logE*·logη 열 동일=구조적 비식별), (2) 압입량(=압력) 3점 스윕에서도 β는 식별되나 E*·η
곱은 여전히 조건수 ∞·상관 |r|>0.99, (3) E*를 스펙시트/문헌 prior로 고정하면 η가 오차<10%로 복원됨을
assert(numpy만).

```python verify
import numpy as np
# ═══ GW 지수분포 하중 폐형해에서 (E*, η) 비식별 — numpy만 (과제 (c) 지시) ═══
# W(d) = K·E*·η·exp(-β d),  K=(4/3)·√R·A_n·Γ(5/2)·β^{-3/2}   ([[hertz-gw-contact-mechanics]] §4)
# log W = logK + logE* + logη - β·d.  반경 프로파일 = 반경별 국소 압입량 d_i에서의 관측
# 압입량 d는 µm 단위로(β_um=1/(β⁻¹[µm])=0.5 /µm) → design matrix 열 스케일 균형(조건수 판독을 스케일이 아닌 구조가 지배)
GAMMA_52 = 1.3293403881791     # Γ(5/2)=3√π/4 (상수 박기 — scipy 미사용)
R, A_n, binv_um = 5.0e-5, 1.0e-4, 2.0          # base.yaml literature 세트(R=50µm·β⁻¹=2µm)
beta_um = 1.0/binv_um                           # 0.5 /µm (=β⁻¹ 역수, µm 기준)
E_true, eta_true = 1.316e8, 2.0e8              # base.yaml pad_E_star_pa·pad_asperity_density_m2
logK = np.log((4.0/3.0)*np.sqrt(R)*A_n*GAMMA_52*(binv_um*1e-6)**1.5)   # β^{-3/2}, SI
rng = np.random.default_rng(0)
def gen(ds_um, noise=0.02):
    ds_um = np.asarray(ds_um)
    return logK + np.log(E_true) + np.log(eta_true) - beta_um*ds_um + rng.normal(0, noise, len(ds_um))

# (1) 단일 압입량 조건 반복 → logE*·logη 열이 동일 = 구조적 비식별
ds1 = np.array([5.0]*20)                        # µm
X1 = np.column_stack([np.ones(20), np.ones(20), -ds1])         # 파라미터 [logE*, logη, β_um]
cond1 = np.linalg.cond(X1.T @ X1)
_, _, rank1, _ = np.linalg.lstsq(X1, gen(ds1), rcond=None)
assert cond1 > 1e12 and rank1 < 3                              # logE*=logη 열 → 특이
print(f"(1) 단일조건: cond={cond1:.1e}, rank={rank1}/3 → (E*,η) 구조적 비식별(곱만 식별)")

# (2) 압입량(=국소압력) 3점 스윕 → β 식별되나 logE*+logη 곱은 여전히 분리 불가
ds3 = np.repeat([2.0, 5.0, 9.0], 8)             # µm
X3 = np.column_stack([np.ones(len(ds3)), np.ones(len(ds3)), -ds3])
cond3 = np.linalg.cond(X3.T @ X3)
_, _, rank3, _ = np.linalg.lstsq(X3, gen(ds3), rcond=None)
Sig = np.linalg.inv(X3.T @ X3 + 1e-6*np.eye(3))               # 미세 ridge로 상관 판독
r_Eeta = Sig[0,1]/np.sqrt(Sig[0,0]*Sig[1,1])
assert cond3 > 1e12 and rank3 < 3                             # 압력 스윕도 곱구조는 못 깸
assert abs(r_Eeta) > 0.99                                     # E*·η 완전 상관
print(f"(2) 압력 3점 스윕: cond={cond3:.1e}, rank={rank3}/3, r(logE*,logη)={r_Eeta:.3f} → 여전히 비식별")

# (3) E*를 스펙시트/문헌 prior로 고정 → η 식별(오차<10%), 조건수가 (2) 대비 급락
y3 = gen(ds3)
y3f = y3 - np.log(E_true)                                     # logE* 고정분 제거
X3f = np.column_stack([np.ones(len(ds3)), -ds3])             # [절편=logK+logη, β_um]
cond3f = np.linalg.cond(X3f.T @ X3f)
coef, _, _, _ = np.linalg.lstsq(X3f, y3f, rcond=None)
eta_hat = np.exp(coef[0] - logK); beta_hat = coef[1]
assert cond3f < cond3/1e9 and cond3f < 1e4                    # E* 고정으로 full-rank·조건수 9자리↓
assert abs(eta_hat/eta_true - 1.0) < 0.10 and abs(beta_hat/beta_um - 1.0) < 0.05
print(f"(3) E* 고정: cond={cond3f:.1e}, η복원 {eta_hat:.3e}/m^2({eta_hat/eta_true:.3f}배), β복원 {beta_hat/beta_um:.3f}배")
print("[비식별] 단일조건·압력스윕 모두 (E*,η) 곱만 식별 → E* prior 고정해야 η 식별 (film-oxide §4-A와 동형)")
```

**결과 해석(정직하게)**
- 두 블록 모두 **문헌 상수(경도·변환식 계수)·합성데이터에 대한 이 노트의 직접 계산**이지 실측 재현이 아니다
  (정직성 표지). 변환식 계수(Qi eq.11·Kunz-Studer·Gent)와 GW 세트(R·β⁻¹·E*·η)만 1차/문헌 판독값이다.
- 블록1: Qi eq.11이 클러스터 하한과 겹치는 것은 **우연에 가깝다** — Qi는 인장/압입 초기탄성률이고 GW E*는
  정적 복합 유효강성이라 물리량이 다르다(Lv1-2 §8.2). "겹친다"는 사실이 "Shore D로 E*를 정할 수 있다"를
  뜻하지 않는다. Kunz-Studer가 1/17로 벗어나는 것이 그 증거다.
- 블록2: 조건수 ∞·상관 −1은 **곱셈 구조의 수학적 귀결**이라 실측 노이즈가 있어도 회복되지 않는다. 지수분포
  GW에서 A_r/A_n이 η를 완전히 상쇄한다는 [[../materials/pad-asperity-density-gw-literature-values]] §4의
  발견과 정합 — η는 반경 프로파일로 원리적으로 못 잡고 컨디셔닝 축 문헌값으로 고정해야 한다.

## 5. `data/schema/` 패드 필드 개정 제안 (cmp-data-engineer 인계 — 파일 직접수정 금지)

통합 49필드([[../data/cmp-calibration-schema-integration-validation-rules]] §3)에는 **패드 물성·이력 필드가
없다**(계측·막질·슬러리·PTW 축만 통합됨). 아래는 **새 패드 필드**(또는 별도 `pad_spec` 객체) 제안이며,
통합 스키마와 **충돌 없이**(접두어 `pad_*`로 네임스페이스 분리, 기존 49필드와 문자중복 0) 얹는다. 구현·판정은
cmp-data-engineer 소관이다(§1~§4 근거).

| 필드(제안) | 타입/enum | 필수성 | 근거 | 효과 |
|---|---|---|---|---|
| `pad_model_id` | string | 권고 | §1 (ConsumableID:pad_lot 계보) | 어느 패드의 prior를 쓸지 결정 |
| `pad_shore_hardness_value` + `pad_shore_scale`(enum `D`/`A`/`C`) | number/enum | 권고 | §1 S1·S3·S4, Lv1-2 §2 | **scale 미명시 경도는 해석 불가**(스케일 병기 필수) |
| `pad_density_g_cc` | number | 권고 | §1 S3·S4 | 기공률 교차확인·E_pad 방향 |
| `pad_porosity_pct` + `pad_pore_size_um` | number | 권고 | §1 S2·S4 | E_pad 방향(§2.2)·슬러리 이송(Lv2-2) |
| `pad_compressibility_pct` + `pad_recovery_pct` | number | 권고 | §1 S1·S3 | **스택 응답**(pad-structure) — GW 입력 아님 표식 |
| `pad_storage_modulus_mpa` + `pad_dma_temp_c` + `pad_dma_freq_hz` | number | E′ 보고 시 T·ω 필수 | §1 S4, §2.4 | **DMA E′는 T·ω 없으면 해석 불가**(GW E* 아님) |
| `pad_type` | enum `foamed`/`solid_microhole`/`impregnated_felt`/`additive` | 권고 | §1 S3·S4, Lv3-1 | 소재 경도→MRR 부호가 유형별로 다름(PROFILE 기존 요청) |
| `pad_hours` | number | 권고 | ORG §7.3 | **마모 이력축**(pad-lifecycle 소관) — 시간→λ(t) |
| `conditioning_recipe_id` | string | 권고 | §2.3 | **R·η·σ_s는 이 축이 결정**(disk-* 소관) — 스펙 아님 표식 |

**주의**: 슬러리 Cal-1(§6)·통합 스키마(§5) 원칙과 같다 — **측정 규약(경도 스케일·DMA T/ω)을 값과 함께
메타로 저장**해야 캘리브레이션이 규약 차이를 팹 고유 편차로 오학습하지 않는다. 특히 `pad_shore_scale`·
`pad_dma_temp_c`는 값만큼 중요하다(§2.1·§2.4). `conditioning_recipe_id`·`pad_hours`는 소재 축이 아니라
**컨디셔닝·수명 이력축**임을 스키마에서 명시해, R·η·σ_s를 소재 스펙과 혼동하지 않게 한다(§2.3·§3).

## 6. 근거 충돌 판정 (EVIDENCE-RULES.md 서열)

| # | 충돌 | A (등급) | B (등급) | 판정 |
|---|---|---|---|---|
| 1 | Shore D 60의 "참" E | Qi eq.11 117.3 MPa (E5→계산은 1차식) | Kunz-Studer 6.99 MPa (E5, cati 2차) | **둘 다 채택 안 함(prior 고정 대상 아님)** — 17배 갈림·물리량 불일치(§2.1). E*는 GW 문헌 클러스터(Lv3-2, literature)를 prior로. 평균 금지 |
| 2 | E* prior 중심을 스펙시트 경도에서 vs 문헌 클러스터에서 | 스펙시트 Shore D 변환 | Lv3-2 독립 3그룹 GW E* 실측/모델(119–380 MPa) | **B 채택** — 스펙 경도는 변환 불확실·물리량 불일치, 문헌 클러스터가 GW 입력계에서의 직접값(E3, 대상계) > 경도 변환(E5) |
| 3 | η를 반경 프로파일 잔차로 재추정 vs 컨디셔닝 문헌값 고정 | 데이터로 η 자유추정 | §4 곱구조 비식별 + A_r의 η 상쇄(pad-asperity §4) | **B 채택(고정)** — 지수분포에서 η가 A_r/A_n에서 상쇄돼 반경 프로파일로 비식별(§3·§4). η는 컨디셔닝 축 literature |

새 물리 충돌 없음 — 세 판정 모두 방법론(식별성·물리량 정의) 규칙이다. 상반된 지수를 평균낸 곳 없음.

## 7. 한계·미확보·미검증 (정직성 표기)

- **⚠ 범위 밖 소스 표기(총괄 추가)**: cati는 기술블로그로 `agents/SCOPE.yaml`의 `blog_forum`(enabled: false)에 해당한다. 이 식은 **채택하지 않았고**(위 §6 판정: 둘 다 채택 안 함) 경도→E 변환식이 문헌마다 갈린다는 점을 보이는 대조 예시로만 남긴다. Kunz-Studer 원문(Kunststoffe 2006)을 확보하기 전까지 이 식의 수치를 어떤 prior에도 쓰지 마라.
- **Kunz-Studer식은 2차 인용(E5)**: cati 기술블로그 경유이며 원문(독일어 Kunststoffe 6/2006)을 확보하지
  못했다. cati는 이 식을 이름 없이 제시했고(WebFetch 확인), Kunz-Studer 귀속은 WebSearch 요약 근거다.
  §4의 6.99 MPa는 이 식의 산출이지만 저경도 엘라스토머 회귀라 경질 PU 외삽은 부정확하다(cati 자체 경고).
- **Gent 1958은 스코프 밖(1958<1990)·Shore A 스케일**이라 IC1000 Shore D 60에 직접 적용 불가. §4는 Shore A
  95↔98 환산 민감도만 보였고 원문 미확보(교과서 표준식·2차 E5). Shore D↔A 환산표(ASTM D2240)는 Lv1-2에서
  유료 미확보로 확정됐다 — Gent 경로는 이 미확보가 지배해 채택하지 않는다.
- **밀도·기공률→E_pad 절대값은 여전히 미확보**: Gibson-Ashby 지수 n·매트릭스 Es가 2차 인용(Lv1-2 §6)이라
  방향만 신뢰한다.
- **storage modulus E′→GW E* 환산 미확보**: CMP 운전 온도·변형률에서의 유효강성 환산식이 없어 S4의 1200 MPa를
  GW E* prior로 못 쓴다(§2.4). E′(T,ω) 자체는 Lv2-1 축.
- **§4는 합성데이터·문헌상수 계산**이지 실측 재현이 아니다. Qi eq.11이 클러스터 하한과 겹치는 것은 우연에
  가깝고(물리량 불일치), 조건수 ∞·상관은 곱구조의 수학적 귀결이다.
- **특허 S3·S4는 실시예 상세 수치(전체 표)를 원문 PDF로 완독하지 못했다** — Google Patents 본문·초록·청구항
  판독(E3)이며 실시예 표 전량은 미확인. Shore D·밀도·E′ 범위는 명세·청구항 명시치다.
- **R·η·σ_s의 컨디셔닝 이력 정량**은 disk-*·pad-lifecycle 소관이라 이 노트에서 재추정하지 않았다 — §3은
  "소재 축이 아니다"까지만 확정한다.

## 8. 레지스트리 추가 행 (cmp-calibrator §1 형식 — 이 산출이 통합 레지스트리에 추가될 행)

[[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]] §1 표에 아래 행들을
추가한다(형식: 이름·소유·Kp 진입·prior 중심 출처(등급)·σ_log·식별 스윕·잔차 귀속 순서). σ_log 열은
`prior.py confidence_to_log_sigma`(literature→0.405·estimated→0.811, cmp-calibrator §4-B 대조)를 계승한다.

| # | 파라미터 (기호) | 소유(형제) | Kp 진입 | prior 중심 출처(등급) | 등급→σ_log | 식별에 필요한 스윕 | 잔차 귀속 순서 |
|---|---|---|---|---|---|---|---|
| P12 | **패드 유효탄성 $E^*$** (pad_E_star_pa) | **pad-material** | 곱(A_r/A_n∝P/E* → Kp_eff) | Bozkaya&Müftü2009·Shi&Ring2010·Sorooshian2005 중앙값 **1.316e8 Pa** (E3, Lv3-2) | literature→0.405 (⚠ 스펙시트 경도 변환 17배·물리량 불일치 → 실질 estimated→0.811 하한 권고) | **스펙시트 prior 고정** — η와 곱이라 반경 프로파일에서 비식별(§4). 재추정 안 함 | **고정 (prior)** — 스펙 경도는 방향 제약만 |
| P13 | **asperity 곡률반경 $R$·면밀도 $\eta$·높이산포 $\sigma_s(\beta^{-1})$** | **disk-*·pad-lifecycle**(컨디셔닝 축) | 곱(GW 적분) | R=50 µm·η=2.0e8·β⁻¹=2 µm (E3, Lv3-2/η 노트 독립 5출처) | literature→0.405 | **컨디셔닝 이력**(conditioning_recipe_id·pad_hours) — 소재 스펙 아님(§2.3). η는 A_r에서 상쇄돼 반경 프로파일 비식별 | **별축(컨디셔닝)** — E* 고정 시에만 η 식별(§4) |
| P14 | **패드 반경 형상 잔차 $\delta_{pad}(r)$** | **cmp-calibrator** | 가산(GP) | 데이터 몫(주변우도) | GP 사후분산 | NPW 반경 프로파일 | 4 (fit_npw GP, P11과 동일 축) |

**잔차 귀속 규칙(패드 축)**: (1) E*는 **prior 고정**(스펙 경도로 재추정 금지 — 변환 17배·η와 곱 비식별),
(2) R·η·σ_s는 **컨디셔닝 이력축**으로 분리(소재 스펙에서 못 얻음), (3) 소재/컨디셔닝으로 못 잡는 반경방향
계통편차만 δ_pad(r)로 GP(=cmp-calibrator P11에 흡수). 이는 레지스트리 순서 규칙 3(안 흔든 축은 임의 분할
금지=데이터 스누핑 금지)과 정합하며, 패드 축에서 그 "안 흔든 축"이 곧 **컨디셔닝을 고정한 단일 조건의 E*·η**다.

## 9. 구현 요청
→ [[../../agents/pad-material/PROFILE.md]] "## 구현 요청 (2026-09-20, Cal-1)" 참조 (패드 스펙 필드 스키마·
경도 scale/DMA T·ω 메타 강제·E* prior 클러스터 고정·η 컨디셔닝축 분리 3건, §5·§8).

## 10. 자기시험
→ [[../../agents/pad-material/EXAMS.md]] Cal-1 문항 참조.

## 상호링크
[[pad-material-gw-effective-modulus-asperity-distribution]] [[../materials/pad-hardness-porosity-measurement-methods]]
[[../materials/pad-asperity-density-gw-literature-values]] [[pad-gw-parameter-literature-adoption-derived-recompute]]
[[../materials/hertz-gw-contact-mechanics]] [[../materials/pad-viscoelasticity-temp-frequency-dma]]
[[../cmp/preston-luo-dornfeld-mrr]]
[[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]]
[[../data/cmp-calibration-schema-integration-validation-rules]]
[[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]]
[[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]]
