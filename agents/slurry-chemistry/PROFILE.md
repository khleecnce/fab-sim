# 슬러리 화학 전문가 (slurry-chemistry)

## 현재 레벨: Lv3 진행 — 활성화 게이트는 agents/ORG.md §4
- 부모: slurry-chemist (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1(산화제 화학 E°·분해·금속적합성), Lv1-2(억제제·킬레이트 흡착·안정도상수), Lv2-1(pH·이온강도→ζ·용해율·선택비·Pourbaix 재해석), Lv2-2(정지층 선택비 설계 원리 — oxide:nitride/Cu:barrier/W:oxide), Lv3-1(코발트·루테늄 착화제·무산화제 슬러리 — χ 숨은 드라이버)
- 다음 단원: Lv3-2

## 역할
산화제·억제제·킬레이트·pH 완충·계면활성제가 막질별 용해·패시베이션·선택비를 어떻게 정하는가

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]
- [[../../knowledge/cmp/slurry-components-overview]]

## 실데이터 책임 (ORG.md §7.3)
화학 스펙(농도·pH·산화제 종류) → 화학 상수 매핑 + 실측 MRR과의 잔차 정의

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 구현 요청 (sim/ 코딩은 직접 하지 않음 — 오케스트레이터/구현 담당에게)
- **[P2] 산화제 종류별 산화력 스케일러**: 현재 파라미터 팩(cu_h2o2_bta.yaml, w_fe_oxidizer.yaml)은
  산화제 "종류"를 문자열로만 갖고 산화력 차이를 반영 못 한다. E°(산화제)−E°(금속) 셀전위를
  화학 배수의 열역학 상한 힌트로 넣는 스케일러 제안.
  - 무엇을: `oxidizer_Ecell_V` 필드(=E°_ox − E°_metal) 추가, MRR 화학층 배수의 방향성 가중에 사용.
  - 근거노트: knowledge/cmp/oxidizer-redox-potential-decomposition-metal-suitability.md §2·§5.1
  - 검증문헌값: H₂O₂→W +1.866 V, IO₃⁻→W +1.175 V, Fe³⁺→W +0.861 V; Fe³⁺→Cu +0.429 V (Vanýsek CRC)
  - 우선순위: P2 (열역학은 상한만 정함 — 실 MRR은 속도론·passivation이 지배하므로 단독으론 예측 불가, Cal 단원에서 실측 잔차와 결합해야 의미).
- **[P3] H₂O₂ pot-life/현장혼합 플래그**: 산화제가 H₂O₂이고 Fe/Cu 촉매 공존 시 Fenton 분해로
  유효농도가 시간에 따라 감소 → 시뮬레이션에 "현장혼합 가정(t=0 농도 사용)" 명시 플래그.
  - 근거노트: 같은 노트 §3·§5.2 (De Laat & Gallard 1999, doi.org/10.1021/es981171v)
  - 우선순위: P3 (정량 붕괴상수 미확보 — 현재는 경고성 플래그만).
- **[P2] 킬레이트 조건부 안정도상수 → Cu 용해율 스케일러**: 킬레이트 농도·pH로 유리 Cu²⁺ 대비 총 용해 Cu 배수를
  `1 + K₁·α_L·[L] + β₂·(α_L·[L])²`로 계산해 화학 용해항 가중에 사용. α_L은 리간드 pKa로 정하는 배위형 분율.
  - 무엇을: 파라미터 팩에 `chelator`, `chelator_conc_M`, 리간드별 log K/pKa 테이블(글리신 logK₁=8.57·logβ₂=15.7,
    시트르산 CuCit⁻ logK=7.57·pKa 3.13/4.76/6.40) 추가, 조건부 상수로 용해율 스케일러 산출.
  - 근거노트: knowledge/cmp/inhibitor-chelator-adsorption-isotherm-passivation.md §5·§7
  - 검증문헌값: MINTEQ v4 DB(papers/phreeqc-minteq.v4.dat); 0.01 M 글리신·pH7 → 용해 Cu ~1.4×10⁶배 증대.
  - 우선순위: P2 (I=0 상수라 이온강도 조건보정(Davies) 필요 — Lv2-1 이후 결합).
- **[P3] 억제제 피복률 θ → 정적식각 억제인자**: BTA/TTA 농도 → Langmuir/Frumkin θ → 정적식각 억제(1−θ 근사).
  - 무엇을: `inhibitor_conc_M`·`K_ads`(또는 ΔG_ads)·Frumkin `f`로 θ 계산, 정적식각항에 (1−θ) 가중.
  - 근거노트: 같은 노트 §3·§7. 검증: 1 mM BTA에서 θ=0.966(ΔG=−35.4 kJ/mol 기준).
  - 우선순위: P3 (ΔG 절대값 2차 인용·f 미확보 — IE≈θ 근사는 계 의존, Cal 단원에서 실측 잔차와 결합).
- **[P2] ζ(pH, I)·Debye(z) 콜로이드 상태 스케일러**: 슬러리 pH·이온강도·반대이온 원자가 z로 (a) 표면전하 부호=sign(IEP−pH),
  (b) Debye 길이 κ⁻¹=0.304/√I (I=½Σcᵢzᵢ²), (c) Schulze–Hardy 정성 응집위험(CCC∝z⁻⁶)을 산출해 결함/부착 위험 플래그·MRR 정전항 가중에 사용.
  - 무엇을: 파라미터 팩에 `slurry_pH`·`ionic_strength_M`·`counterion_valence`·재료별 `IEP` 테이블 추가; ζ 부호/κ⁻¹/응집위험을 진단 필드로.
  - 근거노트: knowledge/cmp/ph-ionic-strength-zeta-dissolution-selectivity-pourbaix.md §2·§3·§7 verify1-3
  - 검증문헌값: IEP 실리카2.5·세리아8·Si₃N₄9(Dandu 2009)·Al₂O₃8.5·TiO₂5.5(Sun 2007); κ⁻¹ 0.96 nm@0.1M·9.62 nm@0.001M(1:1); 3가/1가 CCC ~1/729.
  - 우선순위: P2 (실리카 비-DLVO 안정성 예외 있음 — 정성 위험 플래그로만; 절대 CCC·ζ 절대값은 미검증이라 방향 가중에 국한).
- **[P2] 정지층 쌍 Class 자동분류 + W:oxide 완충능 위험 플래그**: 두 막질의 E°(산화환원 축 유무)로 Class A(유전막쌍)/B(금속-유전막쌍)/C(금속쌍)를
  자동 판정하는 룩업함수, Class B(W:oxide 등)에는 별도로 "슬러리 완충능이 금속 자가산성화(예: W 분말 pH 6.6→2.5)를
  버티는가"를 블랭킷 선택비와 독립된 위험 플래그로 추가 — 블랭킷 선택비만으로는 패턴 침식을 예측 못 함(EP3597711B1 실측).
  - 무엇을: 파라미터 팩에 재료쌍 `redox_axis` 불리언 테이블(SiO2/Si3N4=False, W/Ta/Cu/Co=True), Class B 쌍에는
    `buffer_capacity_flag`(완충제 pKa·농도 vs 예상 자가산성화 강도)를 추가.
  - 근거노트: knowledge/cmp/stop-layer-chemistry-design-principles-oxide-nitride-cu-barrier-w-oxide.md §3·§4·§6
  - 검증문헌값: EP3597711B1 Table 4 — pH_after_W 2.07→9.53에서 침식 69.3→0.3 nm(231배), 블랭킷선택비-침식 상관 ρ≈0.09(무상관).
  - 우선순위: P2 (Class 분류 자체가 이 노트의 해석적 제안 — 문헌 표준분류 아님. EP3597711B1 상관관계는 다변수 실험이라 인과관계 미확정).
- **[P2] χ에 착화제(complexing agent) 농도 항 추가 — 산화제 항에 곱셈으로 결합**: 현재 χ 파라미터 팩(cu_h2o2_bta.yaml,
  w_fe_oxidizer.yaml)은 드라이버로 `oxidizer_wt_pct`·`slurry_ph`를 선언하고도 실제 항은 `oxidizer` 하나뿐이라 `slurry_ph`가
  죽어있다. Ru(EDA)·Co(시트르산) 문헌이 공통으로 보이는 것은 착화제가 **산화제가 만든 산화물에만 반응**한다는 곱셈 게이트다.
  - 무엇을: 파라미터 팩에 `complexing_agent_conc_mM`(+ 종류별 리간드 식별자) 필드 추가, `chi = oxidizer_term(oxidizer_wt_pct) *
    complexing_term(complexing_agent_conc_mM)` 형태로 곱셈 결합(가법 금지 — oxidizer=0이면 complexing_term 효과가 사실상 사라져야 함).
    `slurry_ph`는 (a) 기존 산화물 안정성 경로(이미 반영), (b) 착화제 이온화 분율 경로(신규, pKa 기반) 두 갈래로 재배선.
  - 근거노트: knowledge/slurry/cobalt-ruthenium-complexing-agent-oxidizer-free-chi-driver.md §3·§4·§6
  - 검증문헌값: Xu 2022(Ru, DOI:10.1039/d1ra08243d) — 기준 산화제 농도에서 EDA 0→40mM 배수 3.23배(116→375 Å/min),
    oxidizer=0에서는 EDA 스윕해도 48~67 Å/min 요동만(단조증가 없음). Popuri 2017(Co, DOI:10.1149/2.0111709jss) — 시트르산
    100mM 초과부터 RR 포화(자체 반포화농도 존재, 정확한 K_half는 미확보).
  - 우선순위: P2 (곱셈 구조·포화 존재는 두 독립 재료계에서 확증됐으나 함수형 자체는 각 논문 4점 내외 최소자승/정성 서술 —
    Cal 단원에서 실측 잔차와 결합 필요).
- **[P2] `oxidizer_mech_floor` φ를 재료(금속종)별로 분리**: 현재 φ=0.14는 전 팩 공통 상수(W계 단일 출처 중앙값)인데, Ru계
  실측(무산화제 EDA 스윕)은 φ=0.41~0.58로 자릿수가 다르다. 귀금속에 가까운 Ru의 산화물(RuO2·2H2O, 다공질)이 W/Cu의
  치밀한 부동태막보다 원래 무르다는 화학적 이유가 있어, 단일 상수로 뭉개면 Ru계 무산화제 조건 MRR을 과소평가한다.
  - 무엇을: `oxidizer_mech_floor`를 팩(재료종) 단위 필드로 분리 — 현재 W/Cu 공통값(0.14)은 유지하고, Ru 계열 팩이
    생기면 별도 φ_Ru 범위(0.41~0.58)를 그 팩 전용값으로 사용.
  - 근거노트: 같은 노트 §3 verify1·§5
  - 검증문헌값: Xu 2022 Fig.1–2(48·67·116 Å/min), 기존 W값 US20110186542A1(0.117~0.189, 평균 0.142).
  - 우선순위: P2 (Ru 전용 파라미터 팩이 아직 없다면 이 항목은 팩 신설 시점까지 대기 — 우선순위는 팩 신설 여부에 종속).
- **[변경 없음] psi/cu_h2o2_bta·psi/w_fe_oxidizer — `inhibitor_strength_k` 승격 근거 미확보(3회차 종결)**:
  - 팩: cu_h2o2_bta / 키: inhibitor_strength_k
    현재 3.0 (unverified) → 제안 없음 (등급 변경 불가)
    근거: 산성 H₂O₂+BTA 계 농도 스윕 1차 문헌(Kim 2008 DOI:10.1143/jjap.47.108, Kondo 2000
    DOI:10.1143/jjap.39.6216)이 IOP 구매페이지+미러 사이트 차단으로 구조적 접근불가(1·2·3회차 공통 확인),
    로컬 특허 코퍼스 73건 전문에도 BTA 농도 스윕 실시예 0건 +
    knowledge/cmp/psi-inhibitor-strength-k-primary-source-verification.md §2
    ⚠ _ref 짝: 해당 없음(값 자체를 못 바꿔서 함께 옮길 것도 없음).
  - 팩: w_fe_oxidizer / 키: inhibitor_strength_k
    현재 2.117 (unverified) → 제안 없음 (등급 변경 불가 — 오히려 반증이 강화됨)
    근거: Lee & Seo 2022(DOI:10.3390/app12031227) Fig.4b 3점으로 (K,k) 전 파라미터 공간을
    스윕해도 실측을 못 재현(함수형 자체 반증, psi-inhibitor-strength-k-grade-ruling.md §A.3) +
    대체 폐형식(Frumkin 등온식 등) 1차 문헌도 미확보 +
    knowledge/cmp/psi-inhibitor-strength-k-primary-source-verification.md §3
    ⚠ _ref 짝: 해당 없음.
  - 다음 회차 지침: 위 두 팩 모두 **동일 경로 재시도 금지**(psi-inhibitor-strength-k-primary-source-verification.md
    §5 반복 금지 목록). 남은 방향은 (a) `corpus.py harvest patents`로 Rohm and Haas/Air Products/
    Hitachi Chemical 특허를 신규 수확 후 재검색, (b) CMP 범위를 벗어난 일반 부식과학 Frumkin
    협동흡착 문헌 탐색(스코프 확인 필요), (c) 비자동 경로(저자 직접 연락) — 모두 자동화된 질의
    검색으로는 소진됐다.

## 이수 기록
- 2026-09-10 Lv1-1 산화제 화학 완료 — knowledge/cmp/oxidizer-redox-potential-decomposition-metal-suitability.md
  (verify_claims ✓ 출처1·코드3블록, check_knowledge ✓). 1차: Vanýsek CRC E° 표(직접판독),
  McAllister 2019 UA 학위논문(papers/), De Laat & Gallard 1999(doi 10.1021/es981171v).
- 2026-09-10 Lv1-2 억제제·킬레이트 흡착·안정도상수 완료 — knowledge/cmp/inhibitor-chelator-adsorption-isotherm-passivation.md
  (verify_claims ✓ 출처4·코드3블록, check_knowledge ✓). 1차/근거: MINTEQ v4 열역학 DB(papers/phreeqc-minteq.v4.dat,
  Cu-glycinate logK₁=8.57·logβ₂=15.7, Cu-citrate logK=7.57), popuri2017(doi 10.1149/2.0111709jss, OA 전문),
  Aksu&Doyle 2001/2002(doi 10.1149/1.1344532·1.1474436, 본문 미독), Antonijevic&Petrovic 2008 리뷰(papers/, OA).
  핵심: 억제제=표면 흡착(θ, Langmuir→Frumkin 협동성) vs 킬레이트=용액 착화(log K); 0.01M 글리신 pH7이 Cu 용해 ~1.4e6배 증대.
- 2026-09-11 Lv2-1 pH·이온강도→ζ·용해율·선택비(Pourbaix 재해석) 완료 — knowledge/cmp/ph-ionic-strength-zeta-dissolution-selectivity-pourbaix.md
  (verify_claims ✓ 출처3·코드3블록, check_knowledge ✓). 1차: Sun 2007 UA 학위논문(papers/, PZC 표·IEP 실리카2.5/Cu(OH)₂9.5·실리카 이온강도 안정성 반례),
  Dandu 2009(doi:10.1149/1.3230624, papers/, 세리아8/실리카2/질화막9 IEP→oxide:nitride 선택비~175). 보조: Choi 2004(doi:10.1149/1.1738472),
  Srinivasan 2015 STI 리뷰(doi:10.1149/2.0071511jss, papers/). 핵심: "charge"의 두 그림(ζ vs Pourbaix) 독립 축 분리; Debye 원자가 확장(z:z→1/z)·
  Schulze–Hardy z⁻⁶(3가 1/729); ζ 부호 정합(세리아+·실리카−)이 STI 선택비를 켠다. Lv1-2 예고한 "I=0 상수→이온강도 보정" 연결.
- 2026-09-12 Lv2-2 정지층 선택비 설계 원리(oxide:nitride·Cu:barrier·W:oxide) 완료 — knowledge/cmp/stop-layer-chemistry-design-principles-oxide-nitride-cu-barrier-w-oxide.md
  (verify_claims ✓ 출처4·코드3블록, check_knowledge ✓). 신규 1차: EP3597711 B1(Versum Materials US LLC/현 Merck, freepatentsonline
  전문 확보 — papers/ep3597711b1-versum-w-cmp-reduced-oxide-erosion.txt, INDEX 등록). 재인용(기존 검증 노트에서): Kaufman et al. 1991
  (doi:10.1149/1.2085434, 재료선택비 vs 지형선택비 정의), Dandu 2009·Li&Babu 2001·Nishizawa 2010(film-cu-barrier·film-nitride 노트 경유).
  핵심: Kaufman 이분법(재료 vs 지형 선택비)을 축1로, "두 막질의 산화환원 축 공유 여부"를 축2(이 노트의 제안)로 삼아 세 정지층
  쌍을 Class A(oxide:nitride, 축0)/B(W:oxide, 축1)/C(Cu:barrier, 축2)로 분류. EP3597711B1 Table 4 재현으로 "블랭킷 재료선택비는
  패턴 침식의 필요조건이지 충분조건이 아니다"(선택비-침식 상관 ρ≈0.09 vs 완충pH-침식 상관 ρ≈−0.82)를 정량 반증 — W가 스스로
  만드는 국소 자가산성화를 완충능으로 이기는 것이 Class B 고유의 설계축임을 신규 1차 근거로 확립.
- 2026-09-14 Lv3-1 코발트·루테늄 신규 화학·무산화제 슬러리 완료 — knowledge/slurry/cobalt-ruthenium-complexing-agent-oxidizer-free-chi-driver.md
  (verify_claims ✓ 출처3·코드3블록, check_knowledge ✓). 신규 1차: Xu, Ma, Liu, Tan et al. 2022(RSC Adv. 12, 228,
  DOI:10.1039/d1ra08243d, 로컬 papers/xu2021-ru-eda-cmp-d1ra08243d.pdf 재사용) — Ru CMP에서 EDA 착화제가 산화물에만
  반응하는 곱셈 게이트임을 CMP·전기화학·XPS로 정량. Popuri, Sagi, Alety et al. 2017(ECS JSST 6(9) P594, DOI:10.1149/2.0111709jss,
  papers/popuri2017-jsst-co-citric-acid-cmp.pdf — Lv1-2가 pKa만 인용했던 논문에서 RR/DR 정량치 신규 추출) — Co CMP에서
  시트르산의 같은 문법(산화물 특이성·자체 포화·과잉산화제 억제) 및 무산화제 기계 하한(참고치, pH 교란 있음). 핵심: χ 드라이버로
  선언만 되고 죽어있던 `slurry_ph`는 사실 착화제 이온화 분율 경로가 파라미터 팩에 없어서 죽어있는 것이었고(oxidizer_wt_pct
  하나만 항으로 산다는 기존 관측의 원인 규명), 착화제는 가법이 아니라 산화제 항에 곱하는 게이트여야 하며(oxidizer=0에서
  EDA 스윕해도 RR 요동만·단조증가 없음, floor_frac 0.41~0.58), `oxidizer_mech_floor` φ=0.14(W계 단일출처)는 Ru계에서
  자릿수가 다른 값(0.41~0.58)이 나와 재료별 분리가 필요함을 신규 1차 근거로 확립.
- 2026-09-15 Lv3-2 화학 조성 → 용해율·패시베이션 상수 정량모델(ψ `inhibitor_strength_k`, 3회차 종결) —
  knowledge/cmp/psi-inhibitor-strength-k-primary-source-verification.md (verify_claims ✓ 출처12·코드1블록,
  check_knowledge ✓). 신규: Kondo et al. 2000(DOI:10.1143/jjap.39.6216, JJAP — IOP 구매페이지로
  Kim 2008과 동형 접근불가 확인), 로컬 특허 코퍼스 73건 전문 전수 확인(BTA 언급 15건, 농도 스윕
  실시예 0건, US20110165777A1은 BTA=100ppm 고정 확인), npj Mater. Degrad. 2020(DOI:10.1038/s41529-020-00139-0,
  CC-BY 확보 — FeCl₃ PCB 에칭계라 부적격 확인). 핵심: 선행 두 노트([[../../knowledge/cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]],
  [[../../knowledge/cmp/psi-inhibitor-strength-k-grade-ruling]])가 남긴 두 좁은 표적(특허 실시예·대체
  폐형식)을 각각 소진 확인 — cu_h2o2_bta·w_fe_oxidizer 모두 `inhibitor_strength_k=unverified` 불변,
  값도 불변. 이번 회차의 산출은 "확보"가 아니라 "3회차에 걸친 탐색 공간 소진의 정직한 확인"이다
  (반복 금지 목록을 노트 §5에 남김).
(이후 크론이 갱신)
