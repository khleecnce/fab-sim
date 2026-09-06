# 커리큘럼 — Post-CMP 표면 오염 전문가 (surface-contamination)

> 규칙: 순서대로 학습. 단원마다 ①출처 있는 지식노트(knowledge/) ②자기시험 3문항+답(EXAMS.md) ③가능하면 수식의 코드 재현.
> 유료 논문은 미러 사이트 활용(사용자 지시 9/5). 출처 없는 수치는 '미검증' 표기.

- [x] Lv1-1 표면 오염 종류와 발생원: 슬러리 유래(Fe 촉매·K 완충제·Ce)·패드/디스크 유래·배선 금속(Cu) 재흡착·세정수 유래  <!-- 이수 2026-09-06, knowledge/cmp/post-cmp-metallic-contamination-sources.md -->

- [x] Lv1-2 측정 기법: TXRF·VPD-ICPMS·SIMS·XPS — 검출 한계(atoms/cm²)·막질별 적합성·샘플링 위치  <!-- 이수 2026-09-06, knowledge/cmp/wafer-surface-metal-detection-txrf-vpdicpms-sims-xps.md -->
- [x] Lv2-1 금속 오염이 소자에 미치는 영향: Cu 확산·게이트 산화막 열화·수명 저하 — 허용치 근거(ITRS/IRDS) <!-- 이수 2026-09-07, knowledge/cmp/metal-contamination-device-impact-irds-limits.md -->
- [x] Lv2-2 흡착 메커니즘과 제거 화학: 제타전위·pH·킬레이트(시트르산·EDTA)·희석 HF·오존수 — 막질별 세정 레시피  <!-- 이수 2026-09-07, knowledge/cmp/post-cmp-adsorption-cleaning-chemistry.md -->
- [ ] Lv3-1 최신 리뷰: 저농도 금속 잔류 제어, Co/Ru 신소재 오염, 세정 후 재오염(cross-contamination)
- [ ] Lv3-2 슬러리 조성·세정 조건 → 잔류 금속 농도 예측 모델 골격 (sim/tier2) + 문헌값 대조

## 캘리브레이션 단원 (ORG.md §7.3 — Lv2 완료 후, G2 이후 활성)
- [ ] Cal-1 고객 TXRF/ICPMS 데이터 스키마 + 슬러리 로트별 오염 기여 보정 파라미터

## 확장 (Lv4 — 교수급)
- 최신 논문 상시 추적, 기존 모델의 한계 지적 및 개선 제안
- 부모·형제 에이전트와의 결합 모델 설계 리뷰
