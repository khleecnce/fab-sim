# 커리큘럼 — 종말점 검출 전문가 (tool-endpoint)

> 규칙: 순서대로 학습. 단원마다 ①출처 있는 지식노트(knowledge/) ②자기시험 3문항+답(EXAMS.md) ③가능하면 수식의 코드 재현.
> 유료 논문은 미러 사이트 활용(사용자 지시 9/5). 출처 없는 수치는 '미검증' 표기.

- [x] Lv1-1 EPD 원리별 비교: 광학(반사율/간섭)·모터전류(마찰)·와전류(금속 두께)
- [x] Lv1-2 신호 처리: 노이즈·필터·알고리즘·오버폴리시 제어
- [x] Lv2-1 막질별 EPD 적합성과 한계(투명막·다층) — 2026-09-11. 지식노트 [[../../knowledge/equipment/epd-film-type-suitability-transparent-multilayer-limits]]
- [x] Lv2-2 EPD 트레이스 → 제거량·잔막 역산 방법 — 2026-09-12. 지식노트 [[../../knowledge/equipment/epd-trace-removal-remaining-thickness-inversion]]
- [ ] Lv3-1 최신 리뷰: ML 기반 EPD, 인시츄 계측 통합
- [ ] Lv3-2 EPD 신호 → 제거량 모델 (sim/tier2, 기존 wear_aware_endpoint 확장)

## 캘리브레이션 단원 (ORG.md §7.3 — Lv2 완료 후, G2 이후 활성)
- [ ] Cal-1 EPD 트레이스 실데이터 스키마 + 역산 보정

## 확장 (Lv4 — 교수급)
- 최신 논문 상시 추적, 기존 모델의 한계 지적 및 개선 제안
- 부모·형제 에이전트와의 결합 모델 설계 리뷰
