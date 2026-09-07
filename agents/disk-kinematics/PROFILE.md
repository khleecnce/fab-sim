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
- 2026-09-07 Lv2-1 이수: [[../../knowledge/equipment/disk-insitu-exsitu-conditioning-mrr-stability]]
  — in-situ(연마 중 동시 컨디셔닝) vs ex-situ(별도 사이클) 비교. Jeong et al.(2022, ASPEN 원문
  PDF 확보) §2.2 표: 압력 2/3/4/5psi → 최소 회복 컨디셔닝시간 10/30/60/180초(5:2 배율=18배).
  5psi·10분 폴리싱 사이클 기준 ex-situ 처리량손실 23.1%(파생계산, 미검증 표기) vs in-situ 구조적
  손실 0%. Prasad et al.(2011, 초록만)의 in-situ→패드디브리스→스크래치 증가 소견과 Son & Lee
  (2021, 초록만)의 패드수명 1.67배(12h→20h+) 정황 증거를 "2차 인용·미검증"으로 명확히 구분해
  기록. check_knowledge.py·verify_claims.py 통과(verify 1블록 PASS, 출처 4건 실존 확인).
(이후 크론이 갱신)
