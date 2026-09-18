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

## Lv2-2 패드 두께·그루브 깊이 모니터링과 교체 기준(경제성 포함)

**출처**: Jungyu Son, Hyunseop Lee, "Contact-Area-Changeable CMP Conditioning for Enhancing
Pad Lifetime", *Applied Sciences* 11(8), 3521 (2021), doi.org/10.3390/app11083521 (OA 전문
확보·직접 읽음); US7198546B2 LSI Logic·US6951503B1 Lam Research·US20130217306A1 TSMC·
US20120225612A1 Micron·US5595527A Texas Instruments (모두 등록/공개 특허, Google Patents
전문 확인). 노트: knowledge/materials/pad-thickness-groove-depth-monitoring-replacement-economics.md

**Q1. Son & Lee(2021)의 마라톤 실험에서 Case I(기존 풀컨택트 컨디셔너)과 Case II(분할
컨디셔너)의 평균 패드 컷레이트, MRR 감소율, 그루브 상태(SEM 관찰)는 각각 어땠는가? 이
결과가 "그루브 마모는 glazing과 독립된 실패 모드"라는 이 노트의 주장을 어떻게 뒷받침하는가?**

A1. Case I은 컷레이트 43.4 μm/h로 16시간 만에 그루브가 SEM 단면에서 완전히 소멸하고
웨이퍼가 파손돼 실험이 중단됐으며, MRR은 401.3→221.0 nm/min(−44.9%)까지 급락했다. Case
II는 컷레이트 22.2 μm/h(약 절반)로 20시간 후에도 그루브가 남아 있었고, MRR은
387.7→359.0 nm/min(−7.4%)만 줄었다. 두 실패 지표(그루브 소멸 시점과 MRR 급락 시점)가
Case I에서 같은 12~16시간 구간에 동시에 나타난 것은, 국소 과다마모라는 공통 원인이
asperity 스케일(glazing/MRR)과 그루브 스케일(mm)의 실패를 함께 유발할 수 있음을 보여준다
— 다만 완전한 인과분리는 이 논문만으로는 불가능하다(미검증). (출처: 본 노트 §2, §6)

**Q2. 패드 두께·그루브 깊이를 실측하는 특허 3건(US7198546B2, US6951503B1,
US20130217306A1)이 각각 사용하는 센싱 원리는 무엇이며, 이 중 구체적인 교체 임계값
수치를 공개한 것이 있는가?**

A2. US7198546B2(LSI Logic)는 접촉식 스타일러스(그루브를 지날 때 드래그 변화)와 비접촉식
(전자기 임피던스·레이저 반사·초음파 두께계)을 함께 청구하며, "패드가 완전히 소진되면
평평해진다"(그루브 깊이→0)를 종료 기준으로 삼되 구체 임계값은 없다. US6951503B1(Lam
Research)은 와전류센서 한 쌍의 차동측정(Δd=(d1−d1′)+(d2−d2′))으로 100 μm 수준의 국소
마모를 검출할 수 있다고 명시하지만, 교체 기준은 두께 수치가 아니라 "CMP 결과가 미리 정한
성능 수준 아래로 떨어지면"이라는 성능 프록시다. US20130217306A1(TSMC, 포기된 출원)은
음향 트랜스듀서의 도달시간·위상차로 그루브 깊이를 재지만 "미리 정한 값보다 작으면 소진"
이라고만 하고 구체 수치를 공개하지 않는다. 즉 **세 특허 모두 구체적인 교체 임계값 수치는
비공개**다(미검증). (출처: 본 노트 §3)

**Q3. 이 노트 §5 verify (D)에서 계산한 "패드 수명 연장에 따른 웨이퍼당 소모품비 절감률"의
보수적 추정치와 낙관적 추정치는 각각 얼마이며, 이 계산이 어떤 점에서 "문헌이 보고한
수치"가 아니라 "이 노트의 추정"인지 설명하라.**

A3. 보수적으로 Son & Lee(2021) 실험이 실제로 관찰한 수명비(Case II 20h/Case I 16h=1.25배)를
쓰면 절감률 약 20%, 낙관적으로 컷레이트의 역수비(43.4/22.2≈1.95배, 그루브가 완전히
닳을 때까지 실제로 견딘다고 가정한 상한)를 쓰면 약 49%가 나온다. 이 숫자는 Son &
Lee(2021)의 마모율·수명 데이터와 US5595527A(Texas Instruments, 1997)의 "패드비용은
CMP 스텝 수에 비례한다"는 구조적 관계를 이 노트가 산술적으로 조합해 만든 것이지, 두
문헌 중 어느 쪽도 이 절감률 자체를 실측·보고하지 않았다 — 처리량·가동률 등 다른 변수를
무시한 1차 근사이며, 노트 본문에도 "문헌 수치 아님"으로 명시했다. (출처: 본 노트 §4, §5
verify (D))

## Lv3-1 최신 리뷰: 패드 수명 예측, 인시츄 패드 상태 센싱

출처: Kim, Choi, "In Situ Metrology for Pad Surface Monitoring in CMP Using a
Common-Path Phase-Shifting Interferometry", Appl. Sci. 11(15), 6839 (2021),
doi.org/10.3390/app11156839; Je, Kang, Kim, "Challenges and Innovations in CMP in the
More-than-Moore Era", IJPEM-GT (2026), doi.org/10.1007/s40684-025-00819-9 (초록만).

Q1. Kim, Choi(2021)의 공통경로(common-path) 위상천이 간섭계가 기존 이중빔(double-arm)
간섭계보다 진동 환경에 강한 이유는 무엇이며, 정량적으로 얼마나 개선됐는가?

A1. 기준빔과 시료빔이 하나의 광경로를 공유해(공통경로) 외부진동이 두 빔에 동일하게
걸리므로 위상차가 상쇄된다. 정량적으로 진동+태핑 조건에서 신호 표준편차가 이중빔
방식 대비 제안 방식이 9~13배 작았다(Fig. 2b). (출처: 본 노트 1.3, 4절 verify 블록)

Q2. 이 논문이 실제 사용 후(worn-out) CMP 패드에서 측정한 표면거칠기(Ra)는 얼마이며,
이 값과 저자가 명시한 시스템의 횡분해능(lateral resolution)을 비교했을 때 어떤 관계가
성립하는가?

A2. Ra=303 nm(습식 침지 조건), 횡분해능은 약 3 µm(=3000 nm)로 Ra보다 약 10배 크다.
이 시스템은 수직(높이) 방향으로는 nm급 정밀도를 갖지만 수평 방향으로는 그보다
훨씬 거친 분해능을 갖는 비대칭 성능 구조다. (출처: 본 노트 1.3~1.4, 4절 verify 2블록)

Q3. 2026년 최신 리뷰(Je et al.)가 인시츄 센싱을 어떤 맥락에 위치시켰으며, 이 노트가
패드 수명 예측에 대해 확보하지 못한 것은 무엇인가?

A3. Je et al.(2026) 초록은 AI 기반 공정예측과 인시츄 센싱을 CMP를 data-informed,
sustainable manufacturing platform으로 전환시키는 핵심 축으로 언급한다(초록만 확인,
본문 미확보). 그러나 이 회차에서 패드 잔여수명(RUL) 정량 예측 모델 자체의 1차 출처는
확보하지 못했다. 원류로 추정되는 Muthukrishnan/Boning(1997, SPIE)은 DOI 실존만
확인했고 본문, 미러 사이트 3개 미러 모두 봇 차단으로 미확보. (출처: 본 노트 2.1, 2.3, 5절)

## Lv3-2 사용시간·컨디셔닝 이력 → 시간 의존 Kp·asperity 모델

출처: Sampurno, Rice, Zhuang, Philipossian, "Correlation of Pad Topography, Friction Force and
Removal Rate during Tungsten CMP", ECS Trans. 34(1), 621 (2011), doi.org/10.1149/1.3567648;
Zhou et al., "Study on Pad Performance Deterioration in CMP of Fused Silica", ECS JSS 7(6), P295
(2018), doi.org/10.1149/2.0011806jss; Wu et al., "Aggressive Diamond Characterization and Wear
Analysis during CMP", ECS JSS 2(1), P36 (2013), doi.org/10.1149/2.036301jss.
노트: knowledge/materials/pad-usage-conditioning-history-time-dependent-kp-asperity.md

Q1. Sampurno et al.(2011)의 abruptness λ는 Greenwood-Williamson 모델의 어떤 파라미터와 같은
양이며, 패드 나이 0→8.5 h 동안 λ가 어떻게 변하는가? 그 변화를 단일 지수감쇠로 기술하면 안 되는
이유를 정량적으로 답하라.

A1. λ는 "표면높이 PDF의 오른쪽 꼬리가 1/e로 떨어지는 거리"로 정의되므로, 지수분포 GW 모델
φ(z)=β·exp(−βz)의 1/β(=σ_z 스케일)와 같은 양이다. 판독값은 45.6 → 45.9 → 45.0 → 39.8 →
34.6 µm(0/0.5/2.5/5.5/8.5 h)로, 첫 2.5 h는 사실상 변하지 않다가 그 뒤 선형에 가깝게 떨어진다.
정체-후-선형감소 적합(λ0=45.75 µm, 무릎 2.07 h, 기울기 1.73 µm/h)은 R²=0.9995인 반면 t=0부터의
단일 지수(τ=31.2 h)는 R²=0.937에 그친다 — 지수형은 존재하지 않는 초기 감쇠를 만들어내고 무릎
이후의 급락을 과소평가한다. 다만 λ의 상대표준편차가 30%이므로 무릎 시각의 불확도는 크다(미검증).
(출처: 본 노트 §2.3~2.4 verify 블록)

Q2. 패드가 늙어 λ가 24% 줄어드는 동안 MRR은 3.5%밖에 줄지 않았다. 지수분포 GW 폐형식으로
이 둔감함을 설명하고, 같은 논문의 COF는 왜 같은 논리로 설명되지 않는지 답하라.

A2. 하중 W와 asperity 반경 R이 고정이면 GW 폐형식에서 A_r ∝ λ^(−1/2), p_local = W/A_r ∝
λ^(+1/2)이다. MRR을 "실접촉면적 × 국소압력"으로 보면 둘의 λ 의존성이 정확히 상쇄되어 총하중
W만 남으므로 예측 지수는 0이다. 실측 탄성은 MRR ∝ λ^0.159로 세 후보(−0.5 면적지배 / 0 총하중보존
/ +0.5 국소압력지배) 중 0에 가장 가깝다 — 패드가 늙어도 하중이 보존되는 한 Kp(t)는 둔감하다.
반면 COF 실측 탄성은 +0.582인데, 전단강도 일정의 경계윤활 모델은 COF ∝ A_r/W ∝ λ^(−1/2)를
예측하므로 부호부터 반대다. 즉 COF 감소는 접촉면적으로 설명되지 않고 평탄해진 패드 위 슬러리막
두께 증가(윤활영역 전이)가 필요한데, 이 노트의 데이터로는 Sommerfeld 수를 계산할 수 없어
후보 설명에 머문다(미검증). (출처: 본 노트 §3 verify 블록)

Q3. 현행 `sim/tier2_physics/conditioner_pcr_decay.py`는 컨디셔너 공격성을 A(t)=exp(−t/27.4 h)로
쓴다. Wu et al.(2013)의 30시간 실측은 이 모델의 어느 부분을 지지하고 어느 부분을 반증하는가?
그럼에도 이 노트가 τ를 교체하지 않은 이유는?

A3. 지지: 연마 전에 식별된 "원래 top-20 공격 다이아"의 furrow 면적은 15 h에 45%/48%(평균 47%)
감소해 잔존비 0.535가 되는데, 지수모델의 15 h 예측 0.578은 실험 재현성(표준편차 ≤ 평균의 15%)
이내로 일치한다. 반증: 원래 다이아가 닳으면 신생 공격 다이아가 방향당 7개씩 "태어나" 보충하므로
활성 다이아 **전체**의 furrow 면적은 15 h에 −10~−22%에 그치고 15→30 h는 거의 불변이다. 30 h에서
실측 0.84 대 지수예측 0.335로 2.5배 차이가 난다. 즉 지수형은 개별 다이아 마모를 기술할 뿐
디스크 전체 절삭능을 기술하지 못하며, 하한 A_inf(≈0.84, 30 h 기준)를 둔 형태가 필요하다.
교체하지 않은 이유: Wu의 실험은 30 h까지이고 지표가 furrow 단면적인 반면 τ=27.4 h의 근거인
Entegris 사례는 50 h 시점의 패드 절삭율(PCR)이다 — 시간 구간도 측정량도 달라 직접 비교가
불가능하다. 상반된 두 지수를 평균내지 않고, 0~30 h 구간의 반증만 기록했다(50 h 스케일 1차
실측은 미확보). (출처: 본 노트 §5 verify 블록)

## Cal-1 — 패드 이력 로그 → 시간축 보정 파라미터 (2026-09-19)

Q1. `pad_wear_half_life_h`(base.yaml, 48.0 h, confidence=estimated)의 source 필드는
`pad-wear-glazing-mrr-decay.md`를 가리킨다. 이 인용은 왜 검증 가능한 근거로 쓸 수 없는가?

A1. 그 노트 본문을 검색하면 "48"이라는 수치도 "반감기/half-life"라는 용어도 등장하지 않는다
(Cal-1 노트 §1 verify가 이 사실 자체를 문자열 검색으로 확인). 즉 source 필드는 "이 개념을
다루는 노트"를 가리킬 뿐 "48h 값의 출처"가 아니다. 게다가 `grep -rn pad_wear_half_life_h sim/`가
공집합이라 이 키는 엔진 어디에도 연결되지 않은 orphan 파라미터이고(`knowledge/components/process.yaml`
528행 `status: not_wired`), 무엇의 반감기인지(asperity 높이? MRR? Kp?)조차 정의돼 있지 않다.
(출처: Cal-1 노트 §1)

Q2. Sampurno(2011) λ(t), Zhou(2018) MRR(t), Wu(2013) furrow A(t) — 세 1차 출처 모두 "정체-후-감소"
함수형인데도 Cal-1 노트는 이들로부터 "의사 반감기" 3개를 계산했다. 그 값은 각각 얼마이며,
48 h와 비교해 무엇을 말해주는가? 이 숫자를 그대로 새 pack 값으로 채택하면 안 되는 이유는?

A2. Sampurno λ(t) 정체-후-선형감소 적합(y0=45.75µm, 무릎 2.07h, 기울기 1.73µm/h)에서 y0/2에
도달하는 시각은 15.26 h. Zhou MRR(t)은 0.9 psi에서 4.47 h, 1.26 psi에서 4.23 h. Wu의 furrow
감쇠성분(τ_wear≈15h 오더)만 떼어 ln2를 곱하면 10.4 h. 세 값(4.2~15.3h)은 fab-sim 현재값 48h의
1/3 미만에 몰려 있어, 48h이 최소한 이 세 1차 데이터가 시사하는 시정수 오더보다는 크다는 정황
증거가 된다. 그러나 세 값은 전부 **컨디셔닝이 계속 도는 조건**의 측정이고, "정체-후-감소" 곡선을
억지로 지수 반감기 프레임에 투영한 것이라 애초에 정의상 반감기가 아니다 — 그대로 대입하면
"정체 구간 없는 순수 지수감쇠"라는 다른 모델을 문헌이 지지하지 않는 형태로 pack에 박게 된다.
(출처: Cal-1 노트 §2~§3 verify 블록)

Q3. `knowledge/pad/pad-material-gw-effective-modulus-asperity-distribution.md` §5는 이미
2026-09-15에 같은 파라미터의 1차 출처 확보 실패를 판정했고 EVIDENCE-RULES #40이 그 판정을
승인했다. Cal-1 노트가 그 판정에 동의하면서도 새로 만든 것은 무엇인가?

A3. 판정 자체(estimated 유지)는 뒤집지 않았다 — 동의한다. 새로 만든 것은 두 가지. (i) 대조
브래킷의 품질: pad-material §5의 브래킷은 원문 미확보 2차 재인용(Son&Lee, MDPI 봇차단)에서 선형
감소율을 억지로 지수 재해석한 것(4.9~187h, 폭 38배)인 반면, Cal-1의 브래킷은 pad-lifecycle이
이미 원문 PDF로 직접 읽은 1차 출처 3건에서 나온 것(4.2~15.3h, 폭 3.6배)이라 훨씬 좁고 신뢰도가
높다. (ii) Cal-1 과제가 요구하는 "시간축 보정 파라미터"에 대한 구체적 제안: 단일 반감기 스칼라
대신 정체-후-감소 구조(y0, t_k, s)를 쓰고, PHM 2016 실장비 477웨이퍼 교차검증(Lv3-2 §6, ρ=0.030
패드축 vs ρ=−0.696 드레서축)에 따라 1순위 입력을 `pad_usage_hours`가 아니라
`disk_usage_hours`로 삼으라는 제안. (출처: Cal-1 노트 §4)
