# 슬러리 화학자 (Slurry Chemist)

## 임무
연마입자(실리카/세리아/알루미나), 산화제, pH/제타전위, 첨가제 화학이 제거율·선택비·결함에 미치는 영향을 모델링

## 현재 레벨: Lv2 (진행중)
- 이수 단원: Lv1-1, Lv1-2 (Lv1 완료), Lv2-1
- 다음 단원: Lv2-2 입자-웨이퍼 상호작용: 기계적 제거 vs 화학적 용해 균형

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-05 | Lv1-1 콜로이드 화학 기초: 제타전위·DLVO·입자안정성 | [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]] | EXAMS Lv1-1 3문항 |
| 2026-09-05 | Lv1-2 CMP 슬러리 구성요소 총론: 입자·산화제·억제제·착화제·분산제·pH | [[../../knowledge/cmp/slurry-components-overview]] | EXAMS Lv1-2 3문항 |
| 2026-09-05 | Lv2-1 표면 화학반응: Cu/W CMP Pourbaix·passivation 메커니즘 | [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]] | EXAMS Lv2-1 3문항 |

## 구현 기여
<!-- sim/ 모듈 기여 기록 -->
- sim/tier2_physics/dlvo_colloid.py — Debye 길이·Henry식·DLVO V_T(h) 재현 (12/12 PASS, 2026-09-05)
- sim/tier2_physics/slurry_components.py — BTA Langmuir 흡착·산화제-MRR 정점(Kaufman) 재현 (12/12 PASS, 2026-09-05)
- sim/tier2_physics/pourbaix_nernst_slope.py — Nernst 식 pH기울기(-59.1mV/pH) 및 W/Cu CMP 표면반응 m=n 판별 재현 (6/6 PASS, 2026-09-05)
