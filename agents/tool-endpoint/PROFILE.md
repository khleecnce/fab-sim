# 종말점 검출 전문가 (tool-endpoint)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv2-2
- 다음 단원: Lv3-1

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
- Lv2-2 EPD 트레이스 → 제거량·잔막 역산 방법 — 2026-09-12. 지식노트
  [[../../knowledge/equipment/epd-trace-removal-remaining-thickness-inversion]]
  (check_knowledge.py / verify_claims.py 통과). EXAMS.md 3문항 추가. 핵심: 간섭 프린지
  카운팅은 절대두께는 몰라도 "변화량(제거량)"은 무모호(US4293224 서론 재해석) — Lai(2001)의
  면적분율 반사(단조함수)는 원리상 카운팅 불가. 모터전류/마찰/반사는 "시각"만 주므로
  Preston $RR$을 곱해야 제거량이 나옴([[../../knowledge/cmp/preston-luo-dornfeld-mrr]] 연결).
  오버폴리시 예산은 필터지연분(~19nm, Lv1-2 재사용)보다 저다운포스 잔막마진(Tian 2023,
  100~200nm)이 5~11배 커서 지배적임을 수치로 확인. 와전류 정량 교정식은 문헌 미확보로
  솔직하게 미검증 처리(IEEE TIM 2022 논문 발견했으나 OA/미러 사이트 모두 실패).

## 구현 요청
- sim/tier2 wear_aware_endpoint(향후 Lv3-2 대상)가 "검출시각→제거량" 환산을 붙일 때
  `removed = RR*(t_detect + t_overpolish)` 골격을 쓰고, `t_overpolish`를 (i) 필터지연항
  (Lv1-2 §3 공식 재사용)과 (ii) 공정 안전마진항(막질별 상수, 이 노트 §5)으로 분리해서
  넣기를 제안한다 — 두 항의 물리적 기원이 다르므로 하나의 튜닝 상수로 뭉치면 안 된다.
