# CMP 툴 플래튼·헤드 전문가 (tool-platen-head)

## 현재 레벨: Lv2 완료 (4/6) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv2-1, Lv2-2 (2026-09-07)
- 다음 단원: Lv3-1

## 역할
플래튼·헤드 구조, 멀티존 압력 제어, 리테이너링, RPM·유량이 웨이퍼 스케일 압력·속도 분포에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/equipment/cmp-tool-architecture]]
- [[../../knowledge/physics/cmp-kinematics-rotary]]

## 실데이터 책임 (ORG.md §7.3)
툴 로그(존압력·RPM·유량·온도 시계열) 파싱·정렬 규칙 + 존 응답 행렬 보정

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- Lv1-1 (2026-09-07): 툴 아키텍처 — 캐리어 헤드 가압 방식(AMAT 멤브레인 멀티존 vs
  Ebara 직접공압), 리테이너링 챔퍼 각도·압력비, 슬러리 아암(DSDA) 구조.
  knowledge/equipment/cmp-carrier-head-retaining-ring-vendors.md
  (check_knowledge=PASS, verify_claims=PASS, 1차 출처: Lee et al. 2026 JKSPE
  원문 PDF 확보 + 특허 5건 실존 확인)

- Lv1-2 (2026-09-07): 멀티존 헤드 압력 제어 — 3존+리테이너링 반경 경계(0-85/85-95/
  95-99mm), Zone3 독립·{Zone1,Zone2,Ring} 결합 블록대각 응답 구조, 단일존 vs 멀티존
  NU 4.5%/6.1%/2.5%(edge exclusion 3mm) 및 개선율 44.4%/59.0% 재계산.
  knowledge/equipment/cmp-multizone-carrier-radial-response.md
  (check_knowledge=PASS, verify_claims=PASS, 1차 출처: Lee et al. 2026 JKSPE 원문
  PDF 재사용. Shiu 2004/Zhao 2013/Wang&Lu 2011은 미러 사이트 5미러 무응답으로 1차
  미확보, 2차 인용으로 정직 기록)

- Lv2-1 (2026-09-07): 리테이너링 압력·마모와 엣지 프로파일 — FEA 정적모델
  (Zheng, Zhao, Lu 2023, Micromachines, DOI 10.3390/mi14091683)의 접촉응력 배율
  (mainstream 대비 링있음 3배/링없음 4배, 33.3% 악화)과 US7121927B2 특허의
  접촉 세그먼트 구조(200mm 웨이퍼 둘레의 11.5%)로 "링은 수동보호가 아니라
  능동 엣지제거율 조절 변수"라는 결론 도출.
  knowledge/equipment/cmp-retaining-ring-wear-edge-profile.md
  (check_knowledge=PASS, verify_claims=PASS, 1차 출처: Europe PMC fullTextXML
  본문 확보(MDPI 403/PMC PoW챌린지로 직접PDF 실패) + Google Patents 특허 전문.
  Touzov 2001 IEEE 원 논문은 미러 사이트 5미러 무응답으로 1차 미확보, 특허로 대체)

- Lv2-2 (2026-09-07): RPM 비·유량·온도 제어와 MRR 안정성 — Kim & Jeong(2004, J.
  Electron. Mater. 33(1), DOI:10.1007/s11664-004-0294-4)가 kinematic number
  ζ(=본 프로젝트 µ와 동형)의 원전임을 원문 확보로 확정, 슬라이딩거리 NU=25ζ²(2차,
  둔감) vs 순간속도 NU=2ζ(1차, 민감) 관계를 python verify로 재현. Yuh et
  al.(2015, DOI:10.1007/s40684-015-0041-8) 원문에서 슬러리 유량(비단조, 1000mL/min
  최적)·플래튼 온도(단조 증가) vs MRR/NU 실험 정량값 확인 — 단 PCB용 Oscar-type
  장비라 300mm 팹 스케일 이식은 미검증으로 명시. check_knowledge.py, verify_claims.py
  모두 통과. Lv2 완료(4/6), ORG §5 갱신.
