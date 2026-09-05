# 슬러리 화학자 (Slurry Chemist)

## 임무
연마입자(실리카/세리아/알루미나), 산화제, pH/제타전위, 첨가제 화학이 제거율·선택비·결함에 미치는 영향을 모델링

## 현재 레벨: Lv3 (진행중)
- 이수 단원: Lv1-1, Lv1-2 (Lv1 완료), Lv2-1, Lv2-2 (Lv2 완료), Lv3-1
- 다음 단원: Lv3-2 슬러리 파라미터 → MRR 정량모델 구현 (sim/tier2 기여)

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-05 | Lv1-1 콜로이드 화학 기초: 제타전위·DLVO·입자안정성 | [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]] | EXAMS Lv1-1 3문항 |
| 2026-09-05 | Lv1-2 CMP 슬러리 구성요소 총론: 입자·산화제·억제제·착화제·분산제·pH | [[../../knowledge/cmp/slurry-components-overview]] | EXAMS Lv1-2 3문항 |
| 2026-09-05 | Lv2-1 표면 화학반응: Cu/W CMP Pourbaix·passivation 메커니즘 | [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]] | EXAMS Lv2-1 3문항 |
| 2026-09-06 | Lv2-2 입자-웨이퍼 상호작용: 기계적 제거 vs 화학적 용해 균형 | [[../../knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance]] | EXAMS Lv2-2 3문항 |
| 2026-09-06 | Lv3-1 세리아 슬러리 Ce³⁺/Ce⁴⁺ 메커니즘·Si-O-Ce 화학결합·oxide:nitride 선택비 제어 | [[../../knowledge/cmp/ceria-slurry-ce-redox-selectivity]] | EXAMS Lv3-1 3문항 |

## 구현 기여
<!-- sim/ 모듈 기여 기록 -->
- sim/tier2_physics/dlvo_colloid.py — Debye 길이·Henry식·DLVO V_T(h) 재현 (12/12 PASS, 2026-09-05)
- sim/tier2_physics/slurry_components.py — BTA Langmuir 흡착·산화제-MRR 정점(Kaufman) 재현 (12/12 PASS, 2026-09-05)
- sim/tier2_physics/pourbaix_nernst_slope.py — Nernst 식 pH기울기(-59.1mV/pH) 및 W/Cu CMP 표면반응 m=n 판별 재현 (6/6 PASS, 2026-09-05)

## 구현 요청 (→ 소프트웨어 부문)
<!-- 노트에서 유도했으나 sim/ 정식 모듈화는 소프트웨어 부문이 담당. 노트 옆 python verify sanity check은 slurry-chemist가 계속 수행. -->
- **입자스케일 화학-기계 시너지 모듈** (근거: [[../../knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance]] §4):
  단일입자 소성 접촉 δ_p=F/(2πR·H), plowing 홈 단면 A_f∝R^{1/2}·H^{-1.5} → 화학연화(H↓)의 마모체적 증폭을
  Preston K_p의 화학성분으로 연결. 입력: 입자반경 R, 입자당 하중 F, 표면경도 H(슬러리 화학→H 매핑). 출력: 입자당 제거체적률.
  (현재 노트 verify 블록에 sanity check 존재 — GPa 접촉응력·8배 시너지 재현 PASS. 정식 sim/tier2 모듈화 요청.)
- **Luo-Dornfeld 활성입자 MRR 모델** (근거: 동 노트 §5, doi:10.1109/66.920723 / doi:10.1109/tsm.2003.815199):
  활성입자수(입도분포 상위 꼬리)와 V₁∝F^{1.5} 결합 → MRR∝P^{1/2}·V. 원문 폐형식 유도는 유료(미확보)라
  구현 시 2차 인용 기반 근사임을 명시하고 파라미터는 캘리브레이션 대상으로 표기 필요.
- **세리아 Ce³⁺비 → oxide MRR / 아미노산 → 선택비 정량모델** (근거: [[../../knowledge/cmp/ceria-slurry-ce-redox-selectivity]] §2·§5):
  입력: 산소공공 x(→Ce³⁺ 분율 f=2x, 전하균형), H₂O₂ 농도(catalase-mimetic Ce³⁺ 재생), pH(세리아 IEP 6.8·
  실리카 IEP 2.5 정전인력), 아미노산·계면활성제 농도(nitride 억제). 출력: oxide MRR·oxide:nitride 선택비.
  검증 문헌값: 선택비 59–80(Hwang & Kim 2024, doi:10.3390/polym16060844), H₂O₂ 0.5wt%→MRR 5.5배·선택비
  1:1→3:1(Netzband & Dunn 2020, doi:10.1149/2162-8777/ab8393). 우선순위: 중(Lv3-2 파라미터→MRR 모델에 흡수).
  주의: Ce³⁺ vs Ce⁴⁺ 최적방향은 상충 보고 존재(미검증), 아미노산 선택비 절대값은 조건의존 캘리브레이션 대상.
