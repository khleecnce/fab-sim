# Post-CMP 표면 오염 전문가 (surface-contamination)

## 현재 레벨: Lv2 (진행) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (Lv1 완료), Lv2-1, Lv2-2 (Lv2 완료)
- 다음 단원: Lv3-1 (최신 리뷰: 저농도 금속 잔류 제어, Co/Ru 신소재 오염, 세정 후 재오염)

## 역할
CMP 후 웨이퍼 표면에 남는 금속 이온(Cu·Fe·K·Ca·Al)·이온성 잔류·유기 잔류의 발생원·측정·허용치·제거. 세정 화학과 슬러리 화학의 연결고리

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]
- [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]]

## 실데이터 책임 (ORG.md §7.3)
고객 TXRF/ICPMS 데이터 스키마 + 슬러리 로트별 오염 기여 보정 파라미터

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
| 단원 | 노트 | 검증 | 이수일 |
|---|---|---|---|
| Lv1-1 표면 오염 종류와 발생원 | [[../../knowledge/cmp/post-cmp-metallic-contamination-sources]] | verify_claims PASS(출처6건 실존) · check_knowledge PASS · §6 verify PASS | 2026-09-06 |
| Lv1-2 측정 기법 TXRF·VPD-ICPMS·SIMS·XPS | [[../../knowledge/cmp/wafer-surface-metal-detection-txrf-vpdicpms-sims-xps]] | verify_claims PASS(출처2건 실존·코드1블록 통과) · check_knowledge PASS | 2026-09-06 |
| Lv2-1 금속 오염이 소자에 미치는 영향(ITRS/IRDS 허용치) | [[../../knowledge/cmp/metal-contamination-device-impact-irds-limits]] | verify_claims PASS(출처4건 실존·코드1블록 통과) · check_knowledge PASS | 2026-09-07 |
| Lv2-2 흡착 메커니즘과 제거 화학(IEP·킬레이트 logK·DHF·오존수·RCA·막질별 레시피) | [[../../knowledge/cmp/post-cmp-adsorption-cleaning-chemistry]] | verify_claims PASS(출처22건 실존·코드1블록 통과) · check_knowledge PASS · §6 verify (A)Davies (B)K′(pH) (C)IEP 부호 PASS | 2026-09-07 |

## 구현 요청 (소프트웨어 부문)
- 현재 없음. Lv1-1은 발생원 분류·정성 모델 중심이라 sim/ 편입 대상 수식 없음. (Cu²⁺ Boltzmann 정전흡착 정량 모델은 Lv2-2 세정화학에서 흡착등온선으로 확장 시 재검토.)
- Lv1-2도 측정기법 비교·검출한계 계산이 중심이라 sim/ 편입 대상 수식 없음. TXRF/VPD-ICPMS/SIMS/XPS 검출한계 오더 비교표는 향후 cmp-data-engineer가 §7.3 고객 데이터 스키마 설계 시 "어떤 기법으로 측정된 값인지" 태그가 필요하다는 근거로 참조할 것.
- Lv2-1도 GOI 파괴전압 데이터·ITRS/IRDS 허용치 표가 중심이라 sim/ 편입 대상 수식은 없음. 다만
  §5의 "1×10¹⁰ atoms/cm² = ITRS FEP 스펙"은 향후 defect-scientist가 결함/수율 진단 모델을 만들
  때 판정 임계값 상수로 참조할 근거가 된다 — 구현 시점에 이 노트를 인용할 것.
- ~~**[Lv2-2 요청 1 · 우선순위 중] `chelation_conditional_logK(ligand, metal, pH, I)`** — 순수함수. 입력: 리간드(EDTA/시트르산)·금속(Fe³⁺/Cu²⁺/Ca²⁺)·pH·이온세기. 내부: (1) MINTEQ `minteq.v4.dat`(NIST46.2 태그) I=0 logK와 양성자화 logβₙ 테이블, (2) Davies 식(A=0.509)으로 I 보정, (3) Ringbom α_H로 조건부 K′(pH). 근거노트: knowledge/cmp/post-cmp-adsorption-cleaning-chemistry.md §4·§6(A)(B). 검증문헌값: Fe–EDTA logK(I=0.1)=25.1, Cu–EDTA 18.7~18.8 (Kontoghiorghes 2020 PMC7349684, Palden 2020 PMC9057912) — Davies 예측 25.13/18.79로 0.05 이내. K′(pH) 단조증가·Fe>Cu>Ca 순서·pH3 시트르산–Ca logK′<0 을 테스트로. 용도: Lv3-2 잔류금속 예측 모델의 "유리 이온 분율" 입력.~~ ✅ 2026-09-07 완료 — `sim/tier2_physics/chelation_surface_charge.py` (커밋해시는 나중에 채움, S23)
- ~~**[Lv2-2 요청 2 · 우선순위 중] `oxide_surface_charge_sign(oxide, pH)` + IEP 테이블** — SiO₂ 2.0(Brugnoli 2023 PMC10116594), CeO₂ 6.8(동, 실측범위 5.21–9.40 Ederer 2025 PMC12519946), α-Al₂O₃ 9.5(Zhang 2024 PMC11462379). 반환: 부호(+/0/−)와 pH−IEP. Lv1-1 Boltzmann 정전흡착(§6(C))의 ζ 부호 입력으로 연결하고, 슬러리(colloid-zeta 노트)와 세정 pH에서 입자–웨이퍼 정전 인력/반발 판정에 공용. 근거노트 §3·§6(C). 검증: DHF 0.5 wt% pH≈1.90(HF pKa 3.17)에서 세 산화물 +, pH 11에서 모두 −, pH 5에서 CeO₂+/SiO₂−.~~ ✅ 2026-09-07 완료 — `sim/tier2_physics/chelation_surface_charge.py` (커밋해시는 나중에 채움, S23)
- (주의) 두 함수 모두 금속 가수분해·수산화물 침전·박막 실제 IEP는 미반영 — 노트 §7 한계 그대로 docstring에 명기할 것.
