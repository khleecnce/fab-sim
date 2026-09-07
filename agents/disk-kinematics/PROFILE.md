# 컨디셔닝 운동학 전문가 (disk-kinematics)

## 현재 레벨: Lv1-2 이수 (Lv1 완료) — 활성화 게이트는 agents/ORG.md §4
- 부모: disk-conditioner (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (2026-09-07)
- 다음 단원: Lv2-1 (인시츄 vs 엑스시츄 컨디셔닝과 MRR 안정성)

## 역할
sweep 프로파일·하중·RPM·체류시간이 패드 반경별 컨디셔닝 밀도(PCR)와 프로파일에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/equipment/conditioner-sweep-kinematics-pcr-profile]]

## 실데이터 책임 (ORG.md §7.3)
sweep 레시피 + 실측 패드 두께 프로파일 → 절삭 모델 보정

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- 2026-09-07 Lv1-1 이수: [[../../knowledge/equipment/conditioner-sweep-algorithm-trajectory-density]]
  — 정속 각속도(톱니파) 스윕의 반환점 밀도발산 해석모델. 1차 출처 Wang, Lian, Lin & Tsai (2025,
  DOI 10.18494/sam5844), 상호비교 Zheng, Zhao & Lu (2023, PMC10536193). check_knowledge.py·
  verify_claims.py 통과(verify 1블록 PASS, 출처 2건 실존 확인).
- 2026-09-07 Lv1-2 이수: [[../../knowledge/equipment/disk-rpm-load-radius-pcr]] — Preston형
  PCR=Kp·P·v 모델(Zheng, Zhao & Lu 2023 Eq.10-12)에 process-integrator의 Lai(2001) 운동학수
  치환식(µ, 비균일도=2|µ|)을 대입. Zheng et al. Table 1 실측조건(패드100/디스크73RPM) 대입 결과
  µ≈0.072, 디스크 내 비균일도≈14.4%로 계산 — 당초 "매우 작을 것" 가설을 정직하게 수정해 기록.
  check_knowledge.py·verify_claims.py 통과(verify 1블록 PASS, 출처 2건 실존 확인). Lv1 완료.
(이후 크론이 갱신)
