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
| 2026-09-15 | Lv2 부록 — ψ 흡착보호 3상수(K/n/k) 1차 출처(Park 2003) 재대조·Hill n=4.62 반증 시도, confidence=estimated 유지 판정 | [[../../knowledge/cmp/psi-shield-hill-constants-ceria-primary-source]] | EXAMS Lv2 부록 3문항 |
| 2026-09-19 | C2 완성격자 — χ `sic_alumina_kmno4` 산화제 형상(`oxidizer_langmuir_K`) 종게이트 통과: Gong 2024 L25 직교표(같은 논문, 이미 인용 중) 주효과평균 5점에서 K=2.28(1/wt%) 역산, status partial→modeled. held-out 상충 발견(§구현 요청) | [[../../knowledge/chemistry/sic-kmno4-oxidant-adsorption-kinetics]] | check_knowledge·verify_claims 통과 |

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
- **ψ 산화막 흡착보호 n 파라미터의 물리적 의미 재검토** (근거:
  knowledge/cmp/psi-shield-hill-constants-ceria-primary-source.md §4·§5): `shield_hill_n`은
  산화막 데이터 단독으로는 비식별(n=4~20에서 SSE 변화 <15%)임이 확인됐다. 현재 값(4.62)은
  질화막 브랜치(shield_nitride_hill_n)와의 공유-n 결합회귀에서 나온 것으로, "두 막질이
  독립적으로 같은 협동성에 도달"이라는 물리적 해석은 반증됐다. sim/chemistry.py나 향후
  모델에서 이 n을 "흡착 협동성의 물리 상수"로 취급하지 말고 곡선-형태 파라미터로만
  쓸 것 — 소프트웨어 부문에 특별한 구현 변경을 요청하지는 않으나(현재 엔진 사용 방식이
  이미 배수 계산용이라 문제 없음), 향후 n을 다른 계로 전이하거나 "협동성"을 해석적으로
  사용하는 확장을 설계할 경우 이 캐비어트를 반드시 검토할 것.
- **`sic_alumina_kmno4` 산화제축 활성화가 깬 테스트 2건 + held-out 오염** (근거:
  knowledge/chemistry/sic-kmno4-oxidant-adsorption-kinetics.md §1·§4, 2026-09-19):
  이번 회차에 `oxidizer_langmuir_K`/`oxidizer_langmuir_species=KMnO4`를 자기선언해
  종 게이트(sim/chemistry.py::_oxidizer_species_gate_ok)를 의도적으로 통과시켰다
  (χ status partial→modeled, 근거는 이 팩과 재료계가 완전히 일치하는 Gong et al.
  2024 doi:10.3390/ma17030679 Table 2 의 L25 직교표 KMnO4 주효과평균 5점). 이 변경이
  `tests/test_factors.py`의 두 테스트를 **의도대로** 깼다(`sim/` 은 이 임무 범위 밖이라
  직접 고치지 않았다):
    1. `test_oxidizer_shape_is_not_transferred_across_oxidizer_species` — 이 테스트는
       "sic_alumina_kmno4는 KMnO4 농도에 반응하지 않는다"를 종 게이트가 살아있다는
       증거로 썼다. 이제 이 팩은 **자기 종의 K로 정당하게 반응해야 한다** — 이 테스트를
       삭제하거나, 종 불일치가 여전히 남아 있는 다른 팩(또는
       `_oxidizer_species_gate_ok()` 직접 단위테스트)으로 대상을 옮겨야 한다.
    2. `test_sic_kmno4_ph_floor_reference_unity_unaffected_by_oxidizer` — "기준 pH에서는
       oxidizer_wt_pct 를 무엇으로 바꿔도 χ=1.0" 이라 주장하지만, 이제 오직제 항 자체가
       활성이라 **기준 오직제 농도(4.0 wt%)에서만** χ=1.0 이 성립한다(다른 농도에서는
       의도적으로 달라져야 정상). 어서션을 `oxidizer_wt_pct=4.0` 한 점만 남기거나,
       "pH 항만" 분리해서 검증하도록 다시 짜야 한다.
  **추가로**: `validation/datasets/gong2024_4hsic_alumina_kmno4_L25.yaml`(현재
  `used_for_calibration: false`)가 이번에 K 를 역산한 바로 그 논문·표라 더 이상 이 팩의
  독립 held-out이 아니다 — `used_for_calibration: true`로 갱신하고,
  `knowledge/cmp/sic-alumina-kmno4-L25-heldout-diagnosis.md`의 "KMnO4 축이 죽어
  있다" 서술도 갱신 필요(pH 축은 여전히 죽어 있으므로 그 부분만 남긴다). 이 파일들도
  이번 임무의 담당 범위 밖이라 손대지 않았다.
- **BTA 억제항 K_eff 파라미터 분리** (근거: EVIDENCE-RULES 판정#17,
  knowledge/cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-falsification.md): 산성 H₂O₂+BTA 계에서
  BTA 농도-제거율 직접 스윕 실측이 확보되면, `sim/chemistry.py::_inhibitor_term`에 `inhibitor_K_eff_L_per_mol`
  같은 파라미터를 신설해 `inhibitor_dG_ads_kJ`(평형 K_eq) 경로와 분리할 것 — 지금은 평형 ΔG를
  정상상태 θ에 그대로 대입하는 경로만 있어 Len/McNeill/Gamble 2000(MRS Proc. 613) 실측으로
  정량 반증됐다(34.6pp 어긋남). 함께: Langmuir+exp(-k·θ) 함수형이 고농도 플래토(관측 실측 존재,
  §6)를 구조적으로 재현 못 하므로 **기계적 하한(mechanical floor) 항** 도입도 검토할 것.
