# 자기시험 — 컨디셔닝 운동학 전문가 (disk-kinematics)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1 컨디셔너 sweep 운동학: 아암 각속도·체류시간 → 반경별 궤적 밀도

**Q1. 아암이 정속 각속도(톱니파, dθ/dt=일정)로 왕복 스윕할 때도 반경 방향 궤적밀도가
균일하지 않은 이유는 무엇인가?**

A1. 각속도가 일정해도 팔-각도 θ와 패드-중심 기준 반경 r 사이의 사상이 비선형(코사인법칙
r(θ)=sqrt(L²+R_arm²−2·L·R_arm·cosθ))이기 때문이다. dr/dθ가 θ=0(팔이 패드중심 쪽을 정면으로
향하는 반환점 부근)에서 0에 가까워지므로, 그 반경대에 머무는 시간(밀도)이 상대적으로 커진다.
θ-공간에서는 시간이 균등 분배돼도 r-공간으로 사상하면 비균일해진다.
출처: [[../../knowledge/equipment/conditioner-sweep-algorithm-trajectory-density]] §3(b),
기하 파라미터는 Wang, Lian, Lin & Tsai (2025, DOI 10.18494/sam5844) Table 1 기반(단, L·R_arm은
논문 미공개 예시값).

**Q2. 사인파(sinusoidal) 스윕에서 위치 x(t)=A·sin(θ), θ=ωt(각속도 일정)일 때 시간-평균 위치
밀도 p(x)의 폐형식은? 그리고 이 분포가 반환점(x=±A)에서 어떤 거동을 보이는가?**

A2. p(x) = 1/(π·sqrt(A²−x²)), −A<x<A (아크사인 분포). x→±A(스윕 진폭의 끝, 반환점)에서
분모가 0으로 가 발산한다 — 아암이 반환점 근처에서 국소적으로 느려지므로(dx/dθ→0) 그 위치의
체류시간(밀도)이 커진다. 본 노트의 verify 블록에서 A=34°(Wang et al. 2025 Table 1 아암
오실레이션 진폭)로 수치적분 히스토그램과 폐형식을 대조(median 상대오차 ≈0.029, 반환점
근접/중심 밀도비 ≈3.20)해 확인했다.
출처: [[../../knowledge/equipment/conditioner-sweep-algorithm-trajectory-density]] §3(a) —
아크사인 분포 자체는 조화진동 표준 결과이며, 스윕 진폭 파라미터는 Wang et al.(2025)에서 인용.

**Q3. Zheng, Zhao & Lu (2023)의 사인파 스윕 방식과 Wang, Lian, Lin & Tsai (2025)의 톱니파
스윕 방식은 궤적밀도 도출 방법론에서 각각 어떤 접근을 쓰며, 두 접근이 공통으로 시사하는
결론은 무엇인가?**

A3. Zheng et al.(2023, PMC10536193)은 4중 회전 합성 좌표계로 각 다이아몬드의 절대궤적을
시간에 대해 적분하고 격자(grid)에 스크래치 거리를 누적하는 몬테카를로/격자 적산 방식으로
PCR(r)을 구한다. Wang et al.(2025, DOI 10.18494/sam5844)은 GPU가속 2D 히스토그램(임팩트
밀도)과 정규화 중첩면적비(NAR) 지표로 다이아몬드 개수별 균일도를 정량화한다. 두 방법 모두
시뮬레이션/적산 기반이라 반환점 밀도발산의 "원인"은 명시하지 않지만, 결과적으로 Wang et al.
결론(4)("정속 스윕은 패드 중심을 과다 컨디셔닝, 3구간 가변속 전략 필요")이 공통 시사점이다 —
왕복형 스윕은 스윕 알고리즘(사인파/톱니파)과 무관하게 반환점 근방에 궤적밀도가 몰리므로,
균일 마모를 위해서는 반환점 근처에서 각속도를 오히려 높이는 가변속 프로파일이 필요하다.
출처: [[../../knowledge/equipment/conditioner-sweep-algorithm-trajectory-density]] §2, §4, §5;
[[../../knowledge/equipment/conditioner-sweep-kinematics-pcr-profile]] (Zheng et al. 2023 방법론).

## Lv1-2 하중·RPM·디스크 반경이 PCR 프로파일에 미치는 영향

**Q1. Zheng et al.(2023) Eq.11의 PCR=Kp·P·v 모델에서, 하중 P와 상대속도 v는 PCR의 공간분포에
각각 어떻게 기여하는가?**

A1. P는 선형 상수배로만 곱해지며(균일압력 가정 시 반경 의존 없음), 공간(반경·각도)분포는
전적으로 v(디스크-패드 상대속도)의 공간 함수 형태로 결정된다. 따라서 균일압력 조건에서
PCR의 반경 프로파일 모양은 v(r,θ)의 프로파일과 동형이다.
출처: [[../../knowledge/equipment/disk-rpm-load-radius-pcr]] §2 (Zheng, Zhao & Lu 2023, DOI
10.3390/mi14091683, Eq.10-12).

**Q2. Lai(2001) 치환식을 Zheng et al.(2023) Table 1 실측 RPM 조건(패드100/디스크73 RPM, 디스크
유효반경 52.25mm, r_cc≈195.5mm 근사)에 대입하면 운동학수 µ와 디스크 내 상대속도 비균일도는
얼마로 계산되며, 이 값이 "Rs≠1이면 균일도가 나빠진다"는 방향성 가설과 어떻게 부합/불일치하는가?**

A2. µ≈0.0722, 비균일도(v_max−v_min)/(ω_p·r_cc) ≈14.4%. 당초 "디스크가 패드보다 훨씬 작으므로
µ가 매우 작을 것"이라 예상했으나 실제 계산 결과 R_disk/r_cc≈0.267이 작지 않아 µ가 예상보다
커졌다 — 방향성(Rs≠1→불균일 증가)은 맞지만 크기(14%)는 "미미하다"고 볼 수 없는 수준으로,
당초 가설을 정직하게 수정해야 했다.
출처: [[../../knowledge/equipment/disk-rpm-load-radius-pcr]] §4 verify 블록(직접 계산, r_cc는
논문 미기재로 근사 가정 — 미검증 전제 포함).

**Q3. Rs=ω_d/ω_p=1(디스크-패드 동속)일 때 µ와 디스크 내 상대속도 비균일도는 이론상 어떤 값이
되며, 그 물리적 의미는 무엇인가?**

A3. µ=0, 비균일도=0 — 디스크 표면 전역에서 다이아몬드-패드 상대속도 크기가 위치와 무관하게
동일해진다(process-integrator 노트 §2.1의 웨이퍼-패드 동속 결과와 동일 구조). 이는 디스크
자체의 국소 절삭 불균일(에지 vs 중심 aggressive 차이)을 이론상 완전히 없앨 수 있다는 뜻이며,
실무에서 동속 근접 세팅을 쓰는 이유의 운동학적 근거가 된다(단, Zheng et al. 실험은 Rs=0.73을
썼고 그 선택 이유는 논문에 명시되지 않음 — 미검증).
출처: [[../../knowledge/equipment/disk-rpm-load-radius-pcr]] §3, [[../../knowledge/physics/cmp-kinematics-rotary]] §2.1.

## Lv2-1 인시츄 vs 엑스시츄 컨디셔닝과 MRR 안정성

**Q4. Jeong et al.(2022) §2.2 표에서 연마압력이 2→5 psi로 오르면 패드를 완전 회복시키는 데
필요한 최소 컨디셔닝 시간은 어떻게 변하며, 5 psi/2 psi 배율은 얼마인가?**

A4. 10초→30초→60초→180초로 단조증가하며, 5 psi/2 psi 배율은 정확히 18배(180/10)다. "패드
변형이 클수록(고압) 회복에 더 긴 시간이 필요하다"는 원문 서술과 부합한다.
출처: [[../../knowledge/equipment/disk-insitu-exsitu-conditioning-mrr-stability]] §3, §6 python
verify 블록(문헌 표 원문 재현, DOI 10.3850/978-981-18-6021-8_or-12-0224.html).

**Q5. ex-situ 방식의 처리량(throughput) 손실이 in-situ와 구조적으로 다른 이유는 무엇이며, 5 psi·
10분 폴리싱 사이클에서 정량적으로 얼마의 손실이 계산되는가?**

A5. ex-situ는 연마와 컨디셔닝이 시간적으로 분리되어 컨디셔닝 시간만큼 웨이퍼가 연마되지 않는
직접 손실이 발생하지만, in-situ는 정의상(연마·컨디셔닝 동시 수행) 이 손실이 구조적으로 0이다.
5 psi(회복시간 180초)·10분(600초) 폴리싱 사이클이면 손실 = 180/(180+600) ≈ 23.1%로 계산된다.
단, 이 23.1%는 문헌 실측이 아니라 문헌의 회복시간표를 이 노트가 사이클 손실률 공식에 대입한
**파생 계산**이며, 실제 팹 레시피의 폴리싱:컨디셔닝 배치는 다를 수 있다(미검증, 방향성만 신뢰).
출처: [[../../knowledge/equipment/disk-insitu-exsitu-conditioning-mrr-stability]] §3, §6 python
verify 블록.

**Q6. Prasad et al.(2011)과 Son & Lee(2021)의 초록 인용은 왜 "2차 수준 인용"으로 표기되며, 그로
인해 어떤 결론을 직접 내릴 수 없는가?**

A6. 두 논문 모두 본문 PDF를 확보하지 못하고 초록만 확인했다(Prasad는 IOPscience 봇 차단, Son &
Lee는 MDPI 403 차단) — 세부 수치(스크래치 개수, in-situ/ex-situ의 정확한 구분)를 검증할 수 없다.
특히 Son & Lee의 "Case I"이 in-situ인지 ex-situ인지 초록에 명시되지 않아, 패드 수명 12h→20h+
(1.67배 개선)라는 수치를 "in-situ 대 ex-situ 비교"로 직접 쓸 수 없고 "컨디셔닝 접촉균일성이
패드 수명을 좌우한다는 정황 증거"로만 인용한다 — 확인 못 한 것을 확인 못 했다고 명시.
출처: [[../../knowledge/equipment/disk-insitu-exsitu-conditioning-mrr-stability]] §2, §4, §7.

**Q7. Baisie et al.(2010)의 "UNIFORM 프로파일이 최평탄"이라는 결론과 Wang et al.(2025)의 "정속
스윕이 오히려 중심을 과다컨디셔닝한다"는 결론은 서로 모순되는가?**

A7. 모순처럼 보이지만 아니다 — 두 논문은 서로 다른 변수를 "균일"하다고 부른다. Baisie et al.의
UNIFORM은 반경 세그먼트별 **체류시간(tᵢ)**이 균일한 것이고, Wang et al.의 정속 스윕은 **각속도
(dθ/dt)**가 균일한 것이다. 각속도가 균일하면 반환점 근방에서 dr/dθ→0이 되어 그 위치의 체류시간이
자동으로 커진다([[conditioner-sweep-algorithm-trajectory-density]] §3) — 즉 각속도 균일은 체류시간
불균일을 유발하므로, 체류시간을 균일하게 만들려면 오히려 반환점 근처에서 각속도를 가속해야 한다.
출처: [[../../knowledge/equipment/disk-sweep-recipe-flattening-baisie2010]] §6.

**Q8. Baisie et al.(2010) Table 3 데이터를 세그먼트 체류시간=국소마모 프록시로 재현했을 때, 어느
지표가 논문 서술과 정확히 일치했고 어느 지표가 어긋났는가?**

A8. TTV 순위(DESCENT가 최고, UNIFORM이 최소=0)는 정확히 일치했다. 반면 NU 순위는 어긋났다 — 논문은
"ASCENT and CONVEX show the highest values of NU"라고 서술했으나 재현 결과는 ASCENT=DESCENT가 NU
공동최고(54.92%)이고 CONVEX는 48.0%로 중간이었다. 원인은 본 재현이 논문의 실제 파이프라인(반경별
환형면적 가중 + 세그먼트 겹침 적산, Eq.5–7)을 생략하고 체류시간 자체를 직접 프록시로 썼기 때문으로
추정되나 확인하지 못했다(정직하게 미상으로 기록). 출처: [[../../knowledge/equipment/disk-sweep-recipe-flattening-baisie2010]] §5.


## Lv3-1 - 적응형 sweep, 폐루프 패드 프로파일 제어

**Q9. US9138860B2의 폐루프 제어(CLC)가 개루프 대비 그루브 깊이 변동을 얼마나 줄였다고 주장하며, Table I 수치로 재계산하면 그 주장은 확인되는가?**

A9. 명세서는 핀게이지 기준 40% 이상, 집적센서 기준 75% 이상 감소라고 주장한다. Table I 수치(conditioning-only: pin gauge 폐루프 2.7mil vs 개루프 4.5mil로 정확히 40.0%; integrated sensor 0.5mil vs 2.4mil로 79.2%)로 재계산하면 두 주장 모두 확인된다(polish 중 조건도 각각 40.7%/76.9%로 통과). 다만 두 측정 방식의 측정 반경범위가 달라(pin gauge 0-14.5in vs integrated sensor 1.7-14.7in) 완전히 동일한 물리량 비교인지는 원문 도면 없이 텍스트만으로는 확인 못 함. 출처: [[../../knowledge/equipment/disk-kinematics-closed-loop-adaptive-sweep]] 3장.

**Q10. Park, Hwang & Lee(2024)의 딥러닝 모델에서 학습 데이터 재현 오차와 미학습 조건 예측 오차는 각각 얼마이며, 이 차이가 disk-kinematics 향후 모델링에 주는 시사점은?**

A10. 재현(6개 학습조건 내부) 절대평균오차율 0.01%, 외삽(신규 Test 7 예측) 절대평균오차율 12.9%로 약 1290배 차이. 시사점: 신경망 기반 컨디셔닝 모델은 학습 범위 내에서는 사실상 완벽해 보이지만 학습에 없던 새 스윙 조건으로 일반화할 때 오차가 급격히 커진다. 따라서 신경망 예측기를 오픈루프로 그대로 신뢰하기보다, US9138860B2식 센서 피드백 폐루프와 결합해 예측 오차를 매 사이클 보정하는 구조가 더 안전하다(단, 이 결합 자체를 다룬 문헌은 본 조사에서 찾지 못함 - 저자 추론). 출처: [[../../knowledge/equipment/disk-kinematics-closed-loop-adaptive-sweep]] 4-5장.

**Q11. 폐루프(US9138860B2)와 표면요소법 순방향 모델(Baisie et al. 2010, Lv2-2)은 같은 물리를 어떻게 다른 방향으로 쓰는가?**

A11. 표면요소법은 주어진 스윕 레시피(체류시간 프로파일)를 대입해 누적 마모 프로파일을 계산하는 정방향(forward) 모델이다. 폐루프 제어는 반대로 측정된 마모 프로파일 대비 목표와의 편차를 계산해 다음 사이클 dwell time을 보정하는 역방향(inverse/feedback) 루프다. 둘 다 같은 관계식(누적 마모는 dwell시간과 PCR의 누적합에 비례)에 의존하지만, 전자는 오프라인 설계 도구, 후자는 온라인 보정 메커니즘이라는 역할 차이가 있다. 출처: [[../../knowledge/equipment/disk-kinematics-closed-loop-adaptive-sweep]] 2장.
