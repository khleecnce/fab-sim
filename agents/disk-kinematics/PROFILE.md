# 컨디셔닝 운동학 전문가 (disk-kinematics)

## 현재 레벨: Lv3-2 이수 — 활성화 게이트는 agents/ORG.md §4
- 부모: disk-conditioner (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1, Lv2-2 (2026-09-07), Lv3-1 (2026-09-08), Lv3-2 (2026-09-13)
- Lv3 완료 — 다음은 Cal-1(캘리브레이션, ORG.md §7.3, G2 이후 활성) 또는 Lv4 확장

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
- 2026-09-13 Lv3-2 이수: [[../../knowledge/equipment/disk-kinematics-sweep-pcr-prediction-model]]
  — Lv1-1~Lv3-1을 통합한 예측 모델: 스윕 레시피 dwell 비율 {f_i} → PCR(r) 형상 → 누적 패드
  두께 H(r,T)=k·P·f_i·T(선형시간, Zheng et al. Eq.12 근거) → Ring et al. asperity population
  balance를 반경의존형 A(r)=A0·f_i/f̄로 확장 결합. Zheng, Zhao & Lu(2023, DOI 10.3390/mi14091683,
  PMC10536193) Table 2의 실측 13-partition dwell표(Sinusoidal vs Adjusted)를 코드로 재현해
  TTV 83.2%·NU 86.9% 개선을 정량화(논문은 정성 서술만 제공, 본 노트가 처음 수치화) — 단
  Adjusted 모드도 Baisie(2010) 이상균일에 22.5% 미달로 완전히 도달 못 함을 정직하게 기록.
  population balance 결합(반환점 narrowing 3.65배 빠름)은 모델 내적 일관성 검증(독립 실측
  대조 아님)임을 명시. in-situ/ex-situ 누적 조건화 도즈 비율 3.33배는 Jeong et al.(2022) 표를
  이 노트의 T 입력으로 환산한 파생계산. check_knowledge·verify_claims 모두 통과(출처 4건 API
  실존 확인, verify 3블록 PASS). Lv3 완료 — sim/ 구현은 아래 `## 구현 요청` 참조.
(이후 크론이 갱신)

## 구현 요청 (소프트웨어 부문, sim/ 코딩은 disk-kinematics 담당 아님 — 2026-09-13 지시)

**근거 노트**: [[../../knowledge/equipment/disk-kinematics-sweep-pcr-prediction-model]]

**무엇을**: 스윕 레시피 → 반경별 PCR·패드 두께 프로파일 예측기.
- **입력**: 반경 partition별 체류시간 비율 벡터 `{f_i}` (Σf_i=1), 하중 P, 총 조건화시간 T,
  (선택) partition↔반경 매핑 방식(등반경/등각 — 근거 노트 §8에서 등반경으로 가정, 미확정).
- **출력**:
  1. `PCR_shape(r_i) = f_i` (정규화 형상함수, 절대 k·P 상수는 미보정이므로 상대 프로파일만)
  2. `H(r_i, T) = k·P·f_i·T` (누적 패드 두께손실, k는 호출자가 캘리브레이션 값 주입)
  3. (선택 확장) `η_z(z, r_i, t) = η_z0((z+d)·exp(2·A(r_i)·t) − d)`, `A(r_i)=A0·f_i/f̄` —
     반경별 asperity 높이분포 시간진화(Ring et al. population balance의 반경의존 확장).
- **검증에 쓸 문헌값**: 근거 노트 §3(Zheng et al. Table 2 실측 dwell표, TTV/NU 개선율
  83.2%/86.9%), §4(narrowing 속도 비율 3.65배, 모델 내적 일관성), §5(in-situ/ex-situ 도즈
  비율 3.33배).
- **우선순위**: 중간 — Cal-1(ORG.md §7.3, 실측 패드 두께 프로파일로 절삭모델 보정) 착수 전에
  이 예측기가 먼저 있어야 실측-예측 대조가 가능하다.
- **한계 승계**: k(Preston 상수)·A0(population balance fit) 절대값은 어느 문헌도 제공하지
  않으므로, 이 예측기는 태생적으로 **상대 형상/비율 예측기**다 — 절대 수치 예측을 기대하는
  호출부가 있다면 그 기대 자체를 재검토해야 한다.
