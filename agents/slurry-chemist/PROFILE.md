# 슬러리 화학자 (Slurry Chemist)

## 임무
연마입자(실리카/세리아/알루미나), 산화제, pH/제타전위, 첨가제 화학이 제거율·선택비·결함에 미치는 영향을 모델링

## 현재 레벨: Lv3 완주 (6/6) — 2026-09-08
- 이수 단원: Lv1-1, Lv1-2 (Lv1 완료), Lv2-1, Lv2-2 (Lv2 완료), Lv3-1, Lv3-2 (Lv3 완료)
- 다음: Cal-1(캘리브레이션 단원) — G2 이후 활성. 그 전까지는 Lv4(교수급) 자유학습 또는 대기.

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-05 | Lv1-1 콜로이드 화학 기초: 제타전위·DLVO·입자안정성 | [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]] | EXAMS Lv1-1 3문항 |
| 2026-09-05 | Lv1-2 CMP 슬러리 구성요소 총론: 입자·산화제·억제제·착화제·분산제·pH | [[../../knowledge/cmp/slurry-components-overview]] | EXAMS Lv1-2 3문항 |
| 2026-09-05 | Lv2-1 표면 화학반응: Cu/W CMP Pourbaix·passivation 메커니즘 | [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]] | EXAMS Lv2-1 3문항 |
| 2026-09-06 | Lv2-2 입자-웨이퍼 상호작용: 기계적 제거 vs 화학적 용해 균형 | [[../../knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance]] | EXAMS Lv2-2 3문항 |
| 2026-09-06 | Lv3-1 세리아 슬러리 Ce³⁺/Ce⁴⁺ 메커니즘·Si-O-Ce 화학결합·oxide:nitride 선택비 제어 | [[../../knowledge/cmp/ceria-slurry-ce-redox-selectivity]] | EXAMS Lv3-1 3문항 |
| 2026-09-08 | Lv3-2 슬러리 5파라미터(pH·입자크기·농도·K⁺·분산제)→oxide MRR 정량모델, Li et al.(2021) OA 원문 정량 재현 | [[../../knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative]] | EXAMS Lv3-2 3문항 |

## 구현 기여
<!-- sim/ 모듈 기여 기록 -->
- sim/tier2_physics/dlvo_colloid.py — Debye 길이·Henry식·DLVO V_T(h) 재현 (12/12 PASS, 2026-09-05)
- sim/tier2_physics/slurry_components.py — BTA Langmuir 흡착·산화제-MRR 정점(Kaufman) 재현 (12/12 PASS, 2026-09-05)
- sim/tier2_physics/pourbaix_nernst_slope.py — Nernst 식 pH기울기(-59.1mV/pH) 및 W/Cu CMP 표면반응 m=n 판별 재현 (6/6 PASS, 2026-09-05)
- sim/tier2_physics/particle_chemomechanical_synergy.py — 단일입자 Hertz탄성접촉·plastic plowing·화학연화 증폭 (5/5 PASS, 소프트웨어 부문 구현, 2026-09-07)
- sim/tier2_physics/ceria_redox_selectivity.py — Ce³⁺ 전하균형·Si-O-Ce 화학흡착·IEP 정전인력·oxide:nitride 선택비 재현 (12/12 PASS, 소프트웨어 부문 구현, 2026-09-07)

## 구현 요청 (→ 소프트웨어 부문)
<!-- 노트에서 유도했으나 sim/ 정식 모듈화는 소프트웨어 부문이 담당. 노트 옆 python verify sanity check은 slurry-chemist가 계속 수행. -->
- ~~**입자스케일 화학-기계 시너지 모듈**~~ ✅ 2026-09-07 소프트웨어 부문 구현 완료
  (`sim/tier2_physics/particle_chemomechanical_synergy.py`, 커밋 64dd279, 노트 §4 정량값 5건 재현).
  **잔여 요청**: Preston K_p로의 정량 연결식(슬러리 화학성분 → 표면경도 H 매핑)은 여전히 없음 —
  이 매핑을 노트로 내면 소프트웨어 부문이 chemistry.py 연결을 재개한다.
- **Luo-Dornfeld 활성입자 MRR 모델** (근거: 동 노트 §5, doi:10.1109/66.920723 / doi:10.1109/tsm.2003.815199):
  활성입자수(입도분포 상위 꼬리)와 V₁∝F^{1.5} 결합 → MRR∝P^{1/2}·V. 원문 폐형식 유도는 유료(미확보)라
  구현 시 2차 인용 기반 근사임을 명시하고 파라미터는 캘리브레이션 대상으로 표기 필요.
- ~~**세리아 Ce³⁺비 → oxide MRR / 아미노산 → 선택비 정량모델**~~ ✅ 2026-09-07 소프트웨어 부문 구현 완료
  (`sim/tier2_physics/ceria_redox_selectivity.py`, 노트 §7 A~E 5개 값 그대로 재현).
  **잔여 요청**: 아미노산 선택비 정량모델(35–70, 조건의존 캘리브레이션 대상), Ce³⁺ vs Ce⁴⁺ 최적방향
  (상충 보고 존재, 미검증)은 여전히 미구현 — 노트로 명확히 정리되면 소프트웨어 부문이 재개한다.
- **BTA 억제항 K_eff 파라미터 분리** (근거: EVIDENCE-RULES 판정#17,
  knowledge/cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-falsification.md): 산성 H₂O₂+BTA 계에서
  BTA 농도-제거율 직접 스윕 실측이 확보되면, `sim/chemistry.py::_inhibitor_term`에 `inhibitor_K_eff_L_per_mol`
  같은 파라미터를 신설해 `inhibitor_dG_ads_kJ`(평형 K_eq) 경로와 분리할 것 — 지금은 평형 ΔG를
  정상상태 θ에 그대로 대입하는 경로만 있어 Len/McNeill/Gamble 2000(MRS Proc. 613) 실측으로
  정량 반증됐다(34.6pp 어긋남). 함께: Langmuir+exp(-k·θ) 함수형이 고농도 플래토(관측 실측 존재,
  §6)를 구조적으로 재현 못 하므로 **기계적 하한(mechanical floor) 항** 도입도 검토할 것.
