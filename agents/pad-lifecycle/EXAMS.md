# 자기시험 — 패드 수명 전문가 (pad-lifecycle)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1 브레이크인 물리: 초기 asperity 형성과 MRR 상승 곡선

**출처**: Jeong, Jeong, Shin, Choi, Haedo Jeong, "Identification of the Break-In Mechanism
by Asperity Deformation of CMP Pad", *J. Korean Soc. Precis. Eng.* 38(2), 87-95 (2021),
doi.org/10.7736/JKSPE.020.082 (원문 PDF 미확보, 저널 웹페이지 요약 확인).

**Q1. Jeong et al.(2021) 실험에서 웨이퍼 압력 210/280/350 g/cm² 조건 각각에서 패드가
FWU(fully warmed-up) 상태에 도달하는 데 걸린 시간은 얼마였으며, 압력과 어떤 방향의
관계를 보였는가?**

A1. 210 g/cm²에서 133 min, 280 g/cm²에서 118.6 min, 350 g/cm²에서 52.8 min — 압력이
높을수록 FWU 도달 시간이 짧아지는 반비례 경향을 보였다. (출처: Jeong et al. 2021 결과
요약, 본 노트 §2)

**Q2. FWU 상태 도달 전후로 실접촉면적과 접촉 둘레(perimeter)는 각각 어떻게 변했으며,
이것이 "실접촉면적이 줄면 MRR도 준다"는 단순 GW 직관과 왜 겉보기에 어긋나는가?**

A2. FWU 상태에서 실접촉면적은 감소했지만 접촉 둘레는 오히려 증가했다. 단순 GW 직관은
동일 asperity 분포 φ(z) 내에서 하중만 바꿀 때의 관계([[hertz-gw-contact-mechanics]] §4,
지수분포 GW의 A_r∝W)인 반면, 브레이크인은 φ(z) 자체가 시간에 따라 변하는 과정이라 이
정적 관계가 그대로 적용되지 않는다 — 접촉 둘레·개수 증가가 슬러리 입자 관여 계면을
늘려 MRR 상승에 기여했을 수 있다는 것이 본 노트 §3의 미검증 가설이다. (출처: Jeong et
al. 2021 결과 요약; 본 노트 §3)

**Q3. 본 노트 §4에서 FWU 도달 시간을 압력의 거듭제곱(t_FWU ∝ P^n)으로 회귀했을 때
지수 n과 문헌값 대비 상대오차는 얼마였으며, 이 결과를 어느 수준의 신뢰도로 받아들여야
하는가?**

A3. n≈-1.74, 문헌값 대비 상대오차 12~24%. 3개 데이터점으로 2개 파라미터(n, A)를
적합한 것이라 통계적 유의성이 낮고, 온도 의존 점탄성 연화 등 압력 외 변수가 섞였을
가능성도 있어 **오더 수준의 정성적 일치**로만 받아들여야 한다(미검증 가설). (출처: 본
노트 §4 python verify 블록 실행 결과)

## Lv1-2 정상 마모율과 컨디셔닝 강도의 균형 (마모 = 재생)

**출처**: Hong Shi, Terry A. Ring, "CMP pad wear and polish-rate decay modeled by
asperity population balance with fluid effect", *Microelectronic Engineering* 87,
2368-2375 (2010), DOI: 10.1016/j.mee.2010.04.010 (원문 전체 확보·직접 읽음);
A. Scott Lawing, NCCAVS CMPUG 2004 발표자료(공개 PDF).

**Q1. Lawing(2004)이 말하는 "정상상태(steady state)"란 어떤 두 프로세스의 균형인가,
그 균형이 Cut Rate < Wear Rate 쪽으로 무너지면 무슨 현상이 일어나는가?**

A1. 패드 마모(Pad Wear, 웨이퍼-패드 접촉에 의한 asperity 평탄화)와 컨디셔너 절삭
(Conditioner Cut Rate, 다이아몬드 디스크가 patrol 표면을 깎아 intrinsic 구조를
복원)의 균형이다. Cut Rate < Wear Rate이면 "Severe glazing"(과대마모=심한 유리화)이
진행된다. (출처: 본 노트 §1, [[conditioning-mechanism-asperity-regeneration]] §1)

**Q2. Shi & Ring(2010)이 컨디셔너를 끈 극한(B=D=0)에서 유체(슬러리) 효과를 포함한
모델과 포함하지 않은 모델은 각각 pad-wafer 분리거리 d(t)의 장기 거동에서 어떤
차이를 보이는가?**

A2. 유체를 무시하면 d가 시간에 따라 0까지 계속 감소(패드가 무한정 마모)하는 반면,
유체를 포함하면 d가 유한한 정상상태 d*로 수렴하고 그 지점에서 하중을 유체가 전담해
asperity 마모가 정지한다(P_f(d*)=P_app, P_a(d*)=0). (출처: 본 노트 §2.3, Shi&Ring
2010 p.9-10 직접 확인)

**Q3. 본 노트 §4의 자체 검증 스크립트에서 계산된 정상상태 분리거리 d*는 얼마이며,
이 수치를 실제 CMP 공정값으로 얼마나 신뢰할 수 있는가?**

A3. Stein et al.(1996) 조건(D=0.15m, μ=0.0016 Pa·s, U=0.153 m/s, Papp=50kPa)에서
d* ≈ 13550 nm(13.55 µm)이며, Pf(d*)=50.000 kPa로 Papp와 정확히 일치(항등식 자기
무모순 확인). 그러나 이는 대수적 항등식 검증이지 독립 실측치 비교가 아니며, 절대값이
문헌상 알려진 asperity 스케일(수십 nm~수 µm)보다 커서 물리적 타당성은 확인하지
못했다 — 미검증. (출처: 본 노트 §4 python verify 블록 실행 결과)

## Lv2-1 glazing 메커니즘: asperity 소성변형·슬러리 잔류물·MRR 감소

**출처**: Seonho Jeong, Yeongil Shin, Jongmin Jeong, Seunghun Jeong, Haedo Jeong, "Novel
Probability Density Function of Pad Asperity by Wear Effect over Time in Chemical Mechanical
Planarization", *Materials* 17, 1817 (2024), doi.org/10.3390/ma17081817, PMC11051262 (OA 전문
확보·직접 읽음); A. Scott Lawing, NCCAVS CMPUG 2004 발표자료(공개 PDF, 그래프 판독);
Yongsik Moon, Ph.D. dissertation, UC Berkeley 1999 (공개 PDF). 노트:
knowledge/materials/pad-glazing-mechanism-mrr-decay.md

**Q1. glazing을 구성하는 세 가지 물리 요소는 무엇이며, 각각 어느 출처가 어떤 수준으로
뒷받침하는가? 이 중 본 노트에서 정량화된 것은 무엇인가?**

A1. (a) asperity 끝의 마모·소성 평탄화 — 높이편차 σz 감소와 등가반경 μR 증가(Jeong et al.
2024, 1차 전문), Lawing 2004의 높이분포 2차 피크(truncation); (b) 슬러리 연마입자에 의한
기공 막힘 → 슬러리 수송 차단(Moon 1999 박사논문, 1차); (c) 슬러리 잔류물·웨이퍼 입자
응착층(McGrath & Davis 2004, 초록 스니펫 수준 2차 인용). 정량화된 것은 (a)뿐이며 (b)(c)의
기공 폐색률·잔류물 두께와 마찰계수 변화는 1차 출처 미확보(미검증). (출처: 본 노트 §1, §6)

**Q2. Jeong et al.(2024) Table 1에서 컨디셔닝 없이 2 psi로 10분 연마했을 때 접촉점 수는
어떻게 변했고, 같은 조건의 Fig.9 정규화 MRR은 얼마나 줄었는가? 두 감소율이 크게 다른
이유를 GW 접촉역학으로 설명하라.**

A2. 접촉점 수는 109→56(−48.6%)인데 MRR은 1.00→0.835(−17%)만 줄었다. 하중이 일정하므로
남은 asperity에 하중이 재분배되고(지수분포 GW에서 A_r/W는 η·d와 무관한 상수 → 접촉당
면적이 2배), 마모로 반경이 커져(Eq.4: 7.8→19.6 µm, 2.5배) asperity당 접촉력 감소를
보상하기 때문이다(Jeong 2024 §4.2, Fig.10). 이 보상은 접촉수·압입깊이가 함께 급감하는
후기에 사라져 MRR이 급락한다. 1분 컨디셔닝으로 접촉점은 114(초기의 105%)로 복원된다.
(출처: 본 노트 §2.1–2.3, §4 verify (A)(B)(D))

**Q3. Lawing(2004) ex situ 감쇠 데이터에서 fumed 실리카와 colloidal 실리카 슬러리의 31분
MRR 감쇠율은 각각 얼마였고, 저자가 말한 "logarithmic decay"는 판독 데이터로 어느 정도
재현되었는가? 이 결과의 신뢰 한계는?**

A3. Fumed(중간 공격성 컨디셔너) 2280→1480 Å/min(−35%), colloidal 2950→2730 Å/min(−7%) —
fumed가 약 4.7배 큰 감쇠. rate = a − b·ln t 적합은 R² > 0.95이고 같은 데이터의 선형 적합보다
R²가 높아 "로그형" 서술이 재현된다. 한계: 발표자료 그래프의 눈금 판독값(±30 Å/min)이며
피어리뷰 논문이 아니고, fumed/colloidal 차이가 기계적 마모인지 기공 막힘·잔류물(구성요소
b/c)인지는 이 자료로 분리 불가(미검증). (출처: 본 노트 §3, §4 verify (E))
