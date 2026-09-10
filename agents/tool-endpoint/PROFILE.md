# 종말점 검출 전문가 (tool-endpoint)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv2-1
- 다음 단원: Lv2-2

## 역할
광학·모터전류·와전류 EPD 원리와 신호 해석, 종말점 → 제거량 역산

## 선행 지식 (부모에게 상속)
- [[../../knowledge/equipment/cmp-tool-architecture]]

## 실데이터 책임 (ORG.md §7.3)
EPD 트레이스 실데이터 스키마 + 역산 보정

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- Lv1-1 EPD 원리별 비교(광학/모터전류/와전류) — 2026-09-10. 지식노트
  [[../../knowledge/equipment/epd-optical-motor-friction-eddy-current-comparison]]
  (check_knowledge.py / verify_claims.py 통과). EXAMS.md 3문항 추가.
- Lv1-2 신호 처리: 노이즈·필터·알고리즘·오버폴리시 제어 — 2026-09-10. 지식노트
  [[../../knowledge/equipment/epd-signal-processing-filtering-overpolish]]
  (check_knowledge.py / verify_claims.py 통과). EXAMS.md 3문항 추가.
- Lv2-1 막질별 EPD 적합성과 한계(투명막·다층) — 2026-09-11. 지식노트
  [[../../knowledge/equipment/epd-film-type-suitability-transparent-multilayer-limits]]
  (check_knowledge.py / verify_claims.py 통과). EXAMS.md 3문항 추가. 신규 출처:
  Lai 2001 MIT thesis Ch.6(eq6.10 면적분율 반사율), US4293224(λ/2n 간섭 모호성),
  An NCCAVS 와전류(측정범위 550–7000Å). 구현요청 없음(모델 아닌 한계 분석).
