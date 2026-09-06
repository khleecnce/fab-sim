# 컨디셔너 디스크 설계 전문가 (disk-design)

## 현재 레벨: Lv1 진행중 — 활성화 게이트는 agents/ORG.md §4
- 부모: disk-conditioner (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-06)
- 다음 단원: Lv1-2

## 역할
다이아몬드 그릿 크기·밀도·돌출 높이·본딩(전착/브레이징/CVD)이 패드 절삭율·asperity 재생·수명에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/equipment/conditioner-grit-design-space]]
- [[../../knowledge/equipment/conditioner-disk-pad-cutting-model]]

## 실데이터 책임 (ORG.md §7.3)
디스크 스펙시트 → 절삭 모델 입력 변환 + 실측 패드 마모율 잔차

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- 2026-09-06 Lv1-1 다이아몬드 그릿 규격(메시·형상·품질)과 본딩 기술 비교 — 지식노트
  [[../../knowledge/equipment/diamond-grit-mesh-bonding]] (check_knowledge.py,
  verify_claims.py 통과), 자기시험 3문항(EXAMS.md) 작성 완료.
  핵심: 브레이징(US8104464B2, NICROBRAZ LM 합금, <1,100°C, 화학결합) vs 전착
  (JP4508514B2, Ni 설파메이트 도금, 1~2 A/dm², 볼록돌기 구조로 protrusion을 종래
  5~30%에서 30~150%로 확장하며 패드 제거율 변동계수를 약 2.5배 개선) 정량 비교 확보.
  미해결: 브레이징 계면 결합강도 정량치(전단강도 등) — Lv2에서 DOI
  10.1016/j.diamond.2021.108239로 보강 예정.
