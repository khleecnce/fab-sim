# 컨디셔닝 운동학 전문가 (disk-kinematics)

## 현재 레벨: Lv3-1 이수 — 활성화 게이트는 agents/ORG.md §4
- 부모: disk-conditioner (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1, Lv2-2 (2026-09-07), Lv3-1 (2026-09-08)
- 다음 단원: Lv3-2 (sweep 레시피 → PCR·패드 프로파일 예측 모델, sim/tier2)

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
- 2026-09-07 Lv2-2 이수: [[../../knowledge/equipment/disk-sweep-recipe-flattening-baisie2010]]
  — Baisie, Li & Zhang(2010, ASME MSEC2010, DOI 10.1115/MSEC2010-34264, 미러 사이트 경유
  원문 전체 확보) 표면요소법 모델. Table 3(20세그먼트 스윕시간 프로파일 5종) 원자료로
  Python 재현: UNIFORM 프로파일 TTV=0.00s(문헌 결론 "최평탄"과 일치), DESCENT TTV=3.80s
  (문헌 서술 "최고 TTV"와 일치). 단, ASCENT/CONVEX의 NU 순위는 문헌 서술과 어긋나
  정직하게 기록(단순 체류시간 프록시의 한계). §6에서 본 논문의 "체류시간 균일"과 Wang
  et al.(2025, Lv1-1 노트)의 "각속도 균일"이 서로 다른 최적화 변수임을 밝혀 겉보기
  모순을 해소. 구현요청(§7)을 PROFILE에 등록(소프트웨어 부문 이관). check_knowledge.py·
  verify_claims.py 모두 통과. Lv2 완료.
- 2026-09-08 Lv3-1 이수: [[../../knowledge/equipment/disk-kinematics-closed-loop-adaptive-sweep]]
  — 폐루프 패드 프로파일 제어. AMAT 특허 US9138860B2(전문 확보, Google Patents)의 Table I를
  코드로 재계산해 명세서 서술("핀게이지 40%↓, 집적센서 75%↓")을 assert 5개로 확인(정확히
  40.0%·79.2% 등 실측). Park·Hwang·Lee(2024, Tribol. Lubr., DOI 10.9725/kts.2024.40.2.67,
  원문 PDF 확보)의 딥러닝 스윙-마모 예측 모델은 학습 재현오차 0.01% vs 미학습 외삽오차
  12.9%(약 1290배 차이)를 원문 그대로 대조 — 신경망 오픈루프 예측기의 일반화 한계를 정량
  확인. 폐루프(역방향)와 Baisie et al. 표면요소법(정방향)의 관계를 §2에서 명시적으로 정리.
  MRS 원논문(1249-E02-02)은 Cambridge/Springer 봇차단으로 본문 미확보, 특허로 대체 —
  동일 여부는 미검증으로 명시. check_knowledge·verify_claims 모두 통과(출처 2건 API 실존
  확인, verify 2블록 PASS). Lv3-2(모델 구현) 남음 — 구현은 소프트웨어 부문 이관.
(이후 크론이 갱신)
