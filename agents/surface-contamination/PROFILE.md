# Post-CMP 표면 오염 전문가 (surface-contamination)

## 현재 레벨: Lv2 (진행) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (Lv1 완료), Lv2-1
- 다음 단원: Lv2-2 (흡착 메커니즘과 제거 화학: 제타전위·pH·킬레이트·희석 HF·오존수)

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

## 구현 요청 (소프트웨어 부문)
- 현재 없음. Lv1-1은 발생원 분류·정성 모델 중심이라 sim/ 편입 대상 수식 없음. (Cu²⁺ Boltzmann 정전흡착 정량 모델은 Lv2-2 세정화학에서 흡착등온선으로 확장 시 재검토.)
- Lv1-2도 측정기법 비교·검출한계 계산이 중심이라 sim/ 편입 대상 수식 없음. TXRF/VPD-ICPMS/SIMS/XPS 검출한계 오더 비교표는 향후 cmp-data-engineer가 §7.3 고객 데이터 스키마 설계 시 "어떤 기법으로 측정된 값인지" 태그가 필요하다는 근거로 참조할 것.
- Lv2-1도 GOI 파괴전압 데이터·ITRS/IRDS 허용치 표가 중심이라 sim/ 편입 대상 수식은 없음. 다만
  §5의 "1×10¹⁰ atoms/cm² = ITRS FEP 스펙"은 향후 defect-scientist가 결함/수율 진단 모델을 만들
  때 판정 임계값 상수로 참조할 근거가 된다 — 구현 시점에 이 노트를 인용할 것.
