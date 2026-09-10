# 슬러리 화학 전문가 (slurry-chemistry)

## 현재 레벨: Lv1 진행 — 활성화 게이트는 agents/ORG.md §4
- 부모: slurry-chemist (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1(산화제 화학 E°·분해·금속적합성), Lv1-2(억제제·킬레이트 흡착·안정도상수), Lv2-1(pH·이온강도→ζ·용해율·선택비·Pourbaix 재해석)
- 다음 단원: Lv2-2

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
(이후 크론이 갱신)
