# 디스크-패드 절삭 모델: 재료제거와 표면조도 생성 (Lv2-1)

> disk-conditioner Lv2-1. [[conditioning-mechanism-asperity-regeneration]] [[conditioner-grit-design-space]]
> [[pad-wear-glazing-mrr-decay]] [[hertz-gw-contact-mechanics]] 상호링크.

## 1. 출처
1. A. Scott Lawing, "Pad Conditioning Effects in Chemical Mechanical Polishing", NCCAVS
   CMPUG 2004-05-05 (공개 PDF, AVS strategic-plan 아카이브:
   https://strategic-plan.avs.org/wp-content/uploads/CMPUG2004/CMPUG_05_2004_Lawing.pdf).
   Lv1-1에서 이미 정성 인용한 "Cut Rate = Wear Rate 균형" 개념의 1차 출처 — 본 단원에서는
   이 균형을 정량 모델로 구현하는 데 집중.
2. Rakesh K. Singh, Andrew Galpin, Christopher Vroman (Entegris, Inc.), "Development and
   Performance Data of a New CVD Diamond CMP Pad Conditioner", Entegris Application Note,
   2013(©2013, 자료번호 4435-7548ENT-1213). 공개 PDF:
   https://www.entegris.com/content/dam/web/resources/application-notes/appnote-planargem-cmp-7548.pdf
   — Pad Cut Rate(PCR)의 시간적 감쇠(exponential decay) 실측 데이터, Ra 수렴 실측 데이터를
   제공하는 산업 백서(피어리뷰 아님, 1차 실측 데이터 포함으로 취급).
3. Terry A. Ring, Abaneshwar Prasad, James A. Dirksen, "Dynamic CMP Pad Asperity Population
   Balance for Conditioning and Polishing" (저자 공개 PDF, [[conditioning-mechanism-asperity-regeneration]]
   §4에서 이미 도입한 Evans-Marshall 마모율 Eq.2) — 본 단원에서는 이 마모율식을 컨디셔너
   절삭(cut)에도 동일 구조로 재사용.
4. (참고, 본문 미확보·초록만 확인) Emmanuel A. Baisie, "Modeling, Simulation, And Optimization
   Of Diamond Disc Pad Conditioning In Chemical Mechanical Polishing", PhD Dissertation, North
   Carolina A&T State University, 2012. https://digital.library.ncat.edu/dissertations/37/
   — 초록: "surface element method"와 "conditioning density distribution" 두 운동학 모델로
   패드 표면 프로파일(TTV/Bow/NU)을 예측했고 실험으로 검증했다는 내용. **본 노트는 초록만
   읽었고 본문(PDF)은 접근 실패(대상 서버 403) — 수식·세부 검증치는 미확보, 개념 존재
   확인용으로만 인용**.

## 2. Cut Rate vs Wear Rate 균형의 정량화 (Lawing 개념 → 수식화)
- Lv1-1에서 정성적으로 도입한 개념: 정상상태 패드 표면은 (1) 웨이퍼-패드 접촉에 의한
  마모(Wear Rate, WR)와 (2) 컨디셔너의 절삭(Cut Rate, CR)의 균형점에서 결정된다.
- 두 과정 모두 동일한 물리(Evans-Marshall 소성변형 마모법칙, Eq.2)를 따른다고 가정하면:
  `Rate(P_n, Vel, Area) = (1/2)·P_n·Vel·cot(psi/2) / (H_pad^2·Area)` — 여기서 P_n·Vel는
  각각 웨이퍼-패드(WR 계산 시) 또는 컨디셔너-패드(CR 계산 시) 접촉조건으로 치환된다.
- **핵심 차이는 압입자 형상(psi, 곡률반경)**: 컨디셔너 다이아몬드는 각지고 날카로워
  cot(psi/2)가 크고 곡률반경(beta)이 작다 → 동일 하중·속도에서 CR ≫ WR이 성립하는 것이
  Ring et al.의 §4.3 "in-situ 동시접촉에서 컨디셔너 절삭이 지배적"이라는 서술의 정량적
  근거(psi가 작을수록 마모율 증가라는 관계식은 [[conditioning-mechanism-asperity-regeneration]]
  §4.1에서 이미 도입).

## 3. 컨디셔너 자체의 시간적 성능 감쇠 (PCR decay) — Entegris 실측 재현 대상
- Entegris Case Study 2 (IC1000 패드, DI water, 7 lbs downforce, 벤치탑 폴리셔): 기존
  다이아몬드 디스크는 10시간 내 PCR이 크게 감소(그래프, 정량 수치 본문 텍스트 미제공 —
  **부분 미검증**, 그림만 존재).
- **정량 앵커 포인트(본문 명시)**: 별도 상용공정 사례에서 "50시간 사용된 디스크의 평균
  PCR이 초기값 대비 지수적으로 감소해 **16%**로 떨어졌을 때(약 4 mils/hour) 교체됨" —
  이 지수감쇠 서술을 `PCR(t) = PCR_inf + (PCR_0 - PCR_inf)*exp(-t/tau)` 형태로 모델링하고,
  `PCR(50h)/PCR_0 = 0.16`(PCR_inf≈0 근사, 즉 완전 소진에 가깝다고 가정)을 앵커로 tau를
  역산 가능 (`tau = -50 / ln(0.16)` ≈ 27.4시간).
- **대조군(설계 개선 예시, Planargem)**: Case Study 2/4/5에서 PCR과 Ra가 각각 10~50시간
  동안 안정적으로 유지됨(그래프 서술 "stability of PCR data") — 이는
  `PCR(t)≈PCR_0`(tau→∞ 극한)으로 모델링 가능. [[conditioner-grit-design-space]] §5의
  "sharp-diamond 6시간 후 55~65% 유지 vs 경쟁사 ~15%"와 정성적으로 일치하는 별도 데이터
  포인트(다른 실험, 같은 현상군).

## 4. 표면조도(Ra) 수렴 — 브레이크인 시상수
- Entegris Case Study 3 (신품 폴리머 Pad-A, Planargem 컨디셔너, 7 lbs, DI water): Ra가
  신품 **4.6 µm → 0.5시간 만에 3.3 µm**로 급락한 뒤 **17시간 동안 실험오차 내에서 동일**하게
  유지(정량 실측치, 본문 명시).
- 이는 "패드 표면구조가 컨디셔너 하중에 크게 민감하지 않다 — 일단 고유구조가 복원되면
  추가 컨디셔닝은 더 바꾸지 않는다"는 [[conditioning-mechanism-asperity-regeneration]] §3의
  서술을 정량적으로 뒷받침 — brake-in 시상수가 매우 짧음(<0.5h)을 의미하며, 이후
  17시간 정체(steady-state)는 §2의 Cut Rate=Wear Rate 균형점 도달로 해석 가능.
- Ra(t)를 `Ra(t) = Ra_inf + (Ra_0 - Ra_inf)*exp(-t/tau_Ra)` 로 모델링하면, "0.5시간 만에
  거의 평형"이라는 서술은 `tau_Ra`가 분 단위(대략 5~10분 오더)로 매우 짧음을 시사 — 정확한
  tau_Ra 값은 본문에 그래프로만 제공되어 **미검증**, 정성적 상한(0.5h 내 90%+ 수렴)만
  앵커로 사용.

## 5. 종합: disk-conditioner Lv2-1 시뮬레이터 설계 방향
- **입력**: 컨디셔너 사용시간 t_cond(누적), 그릿 특성(sharp/blocky → tau 결정), 패드-웨이퍼
  접촉조건(WR 계산용, 기존 pad_wear_glazing.py 재사용).
- **컨디셔너 절삭 모델**: `PCR(t_cond) = PCR_inf + (PCR_0-PCR_inf)*exp(-t_cond/tau)` —
  실측 앵커(50h→16%)로 tau 캘리브레이션.
- **결합 개념(다음 Lv2-2 예고)**: 컨디셔너가 소진되어 PCR이 감소하면(CR↓), Cut Rate = Wear
  Rate 균형점이 이동해 정상상태 glazing 정도가 증가(패드가 더 매끈해짐, 곧 MRR 저하) —
  이는 기존 `pad_wear_glazing.py`의 "무컨디셔닝(B=D=0)" 극한과 "완전 컨디셔닝(정상상태 유지)"
  극한 사이의 중간 상태를 컨디셔너 노화(aging)로 잇는 다리가 된다.

## 6. 미검증 사항 (정직 표기)
- Entegris Case Study 2의 "10시간 내 PCR 크게 감소" 서술은 그래프 축만 제공, 정확한 %는
  **미검증**. 본 노트가 캘리브레이션에 사용한 "50h→16%" 수치는 Entegris 문서가 재인용한
  별도 상용공정 사례(출처 문서 내 4번 각주, Palmgren 2004 — 원문 미확보, 2차 인용)로
  **완전한 정량 검증은 아님**.
- Ra(t) 수렴 시상수(tau_Ra)는 그래프로만 제공, 정확한 지수형 여부 자체도 저자가 명시하지
  않음(단지 "0.5h 이후 오차범위 내 동일"이라 서술) — 지수형 가정은 fab-sim의 편의적 근사.
- Baisie(2012) dissertation의 surface element method/conditioning density distribution
  두 모델은 본문 미확보로 방정식 형태를 구현에 반영하지 못함 — Lv2-2 또는 후속 회차에서
  원문 확보 재시도 필요(NCAT 리포지토리 403, 대안: ProQuest, ILL 등 유료/기관 경로만
  확인됨 — 무료 재접근 방법 탐색 필요).
- Lawing(2004)의 "동일 마모법칙(Eq.2)이 웨이퍼-패드 접촉과 컨디셔너-패드 접촉 양쪽에
  형태를 유지한 채 적용된다"는 가정 자체는 Ring et al. 논문의 명시적 서술이 아니라 본
  노트 저자(disk-conditioner 에이전트)의 정합적 추론 — **미검증 가정**으로 명시.
