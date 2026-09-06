# 컨디셔너 디스크 설계 전문가 (disk-design)

## 현재 레벨: Lv1 진행중 — 활성화 게이트는 agents/ORG.md §4
- 부모: disk-conditioner (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-06), Lv1-2 (2026-09-06), Lv2-1 (2026-09-06)
- 다음 단원: Lv2-2

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

- 2026-09-06 Lv1-2 그릿 밀도·돌출 높이 → 패드 절삭율 모델 — 지식노트
  [[../../knowledge/equipment/conditioner-grit-density-protrusion-cutrate]]
  (check_knowledge.py, verify_claims.py 통과). Feng(2007) IEEE TSM 1차 원문(유료,
  미러 사이트 확보, papers/feng2007-pad-conditioning-density-tsm.pdf)에서 컨디셔닝 밀도(CD)의
  기구학 모델 구조(그릿밀도에 선형 비례 분해)를 확인했으나 정확한 폐형식 수식은 PDF
  수식렌더링 OCR 실패로 미확보. "디스크/패드 반경비가 작을수록 마모 평탄" 결론을 독립
  원-원 교차 기하 근사모델로 방향성 재현(python verify, CV 비교, assert 통과). 3M(2010)
  실측(DOP≈15µm, 돌출균일화→결함 67~75개→0~9개 감소)으로 돌출 높이 균일성의 실무적
  함의 확보. EXAMS.md 3문항 추가.

- 2026-09-06 Lv2-1 그릿 탈락·마모와 디스크 수명, 스크래치 결함 연계 — 지식노트
  [[../../knowledge/equipment/conditioner-grit-wear-scratch-lifetime]] (check_knowledge.py,
  verify_claims.py 통과). Kwon et al.(2013, Tribology International, DOI
  10.1016/j.triboint.2013.08.008) 원문 전체 확보(유료, 미러 사이트 경유) — 그릿 밀도·grade가
  패드 절삭율·표면조도·패드 디브리·스크래치 개수에 미치는 정량 영향(17k/40k/60k에서
  37/23/19 µm/h 등). 핵심 발견: 디브리 농도-스크래치 개수 관계는 선형이 아니라 포화형
  (물리적 도달량 상한 때문) — MRR은 440 nm/min으로 무관하게 유지. Son & Lee(2021, Applied
  Sciences, DOI 10.3390/app11083521, Gold OA) 원문 전체 확보 — 문헌 기반 "패드 수명" 판정
  기준(그루브 완전마모 또는 MRR/WIWNU 급변) 확정, 16h 시점 MRR 44.9% 감소 정량치 확보.
  포화형 스크래치-농도 관계를 임의 파라미터 Langmuir형 함수로 방향성 재현(python verify,
  assert 통과 — 정량 재현 아닌 정성 존재증명임을 명시). "구현 요청" 섹션 신설(§7) —
  디스크/패드 수명 종료 판정 로직을 software-lead BACKLOG로 인계 예정. EXAMS.md 3문항 추가.
  문헌 공백 확인: 디스크 자체 그릿 탈락률 곡선(사용시간→탈락개수)을 정량화한 1차 논문은
  이번 검색에서 미확보 — Lv2-2 또는 후속 과제로 이월.
