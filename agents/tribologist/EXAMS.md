# 자기시험 기록 — 마찰·유체 전문가 (Tribologist)

<!-- 단원별 3문항+모범답안, 출처 포함 -->

## Lv1-1 트라이볼로지 기초: 마찰·마모·윤활·Stribeck (2026-09-05)
근거: [[../../knowledge/physics/tribology-friction-wear-stribeck]], [[../../knowledge/materials/hertz-gw-contact-mechanics]], [[../../knowledge/cmp/preston-luo-dornfeld-mrr]]

**Q1. Amontons 마찰법칙에서 마찰력이 "명목 접촉면적과 무관"한 이유를 실접촉면적 개념으로 설명하라. 이것이 GW 노트와 어떻게 연결되는가?**
A1. 거친 표면은 asperity 끝에서만 닿아 실접촉면적 A_r ≪ A_nominal이다. 소성접촉이면
A_r = N/H(H=경도), 마찰력 F = τ·A_r = τ·N/H이므로 µ = τ/H = 상수가 되어 하중·명목면적과
무관해진다(Bowden & Tabor 1950, 2차 인용). 핵심은 **F ∝ A_r ∝ N**이라는 점. [[hertz-gw-contact-mechanics]]
§4에서 탄성접촉(GW 지수분포)에서도 A_r ∝ W가 해석적으로 성립함을 보였으므로, 소성이든 탄성이든
A_r가 하중에 선형 → µ 일정이 Amontons 법칙의 미시적 근거다.

**Q2. Archard 마모식 V = k·W·L/H를 쓰고, 이것이 Preston 식 dot h = Kp·P·V와 어떤 대응을 갖는지 보여라. 재현 결과는?**
A2. V=k·W·L/H(Archard 1953). 면적으로 나누면 마모깊이 V/A = k·P·L/H (P=W/A, L=V_slide·t).
이는 Preston `dot h = Kp·P·V`와 구조가 동일하며 **Kp ≈ k/H** 대응이 성립한다. 재현
(`sim/tier2_physics/tribology_basics.py`, 10/10 PASS): k/H를 Kp로 두면 Archard 깊이=Kp·P·L이
수치적으로 Preston형과 일치 확인. 단 CMP는 화학적 연화가 H를 낮추고 k에 화학효과가 뭉뚱그려져
Kp가 슬러리 화학에 민감(순수 기계마모와 차이). [[preston-luo-dornfeld-mrr]] 참조.

**Q3. Stribeck 곡선의 3레짐과 µ의 U자 거동을 설명하고, CMP가 어느 레짐에서 운전되는지 Sommerfeld 수로 답하라.**
A3. 가로축 Hersey수 η·N/P(CMP는 Sommerfeld So=η·V/(P·δeff)), 세로축 µ. Boundary(막≪거칠기,
µ 높고 일정 0.05–0.20) → Mixed(막≈거칠기, µ 급락) → Hydrodynamic(막≫거칠기, µ 최소 후 점성전단으로
완만 재상승 0.002–0.01). µ는 최소점을 갖는 J자 곡선. **CMP는 boundary~mixed 레짐**에서 운전 —
완전 유체막이면 접촉이 사라져 MRR 급감하므로 "Stribeck 최소점 왼쪽"을 의도적으로 유지한다
(Wu&Liao 2016, IntechOpen ch.52631). 재현: 전형 CMP 값에서 So≈6.7×10⁻³ (mixed 영역)로 확인.

## Lv1-2 CMP의 윤활 레짐 판별(boundary/mixed/hydrodynamic) (2026-09-05)
근거: [[../../knowledge/physics/cmp-lubrication-regimes]], [[../../knowledge/physics/tribology-friction-wear-stribeck]], [[../../knowledge/materials/hertz-gw-contact-mechanics]]

**Q1. CMP Sommerfeld 수 So = μU/(p·δeff)를 쓰고, 유체역학 길이 ℓ_hd=μU/p 개념을 이용해 "왜 CMP는 구조적으로 boundary 레짐인가"를 정량 논증하라.**
A1. So=μU/(p·δeff)=ℓ_hd/δeff이며 ℓ_hd≡μU/p는 점성 부양이 만들 수 있는 특성 막두께 스케일이다.
전형 CMP(μ=1e-3 Pa·s, U=0.75 m/s, p=3 psi=20.7 kPa)에서 ℓ_hd=1e-3·0.75/20684≈**36 nm**로,
패드 Ra(~5 µm)보다 2오더 이상 작다. 즉 점성막이 거칠기를 넘어 웨이퍼를 띄울 수 없으므로
λ=h_film/σ≪1 → boundary. δeff≈σ 근사에서 So≈ℓ_hd/σ≈λ라 So와 λ가 같은 오더(≈7.25×10⁻³)다.
재현(`sim/tier2_physics/cmp_lubrication_regime.py` 11/11 PASS): So=7.25×10⁻³, ℓ_hd=36.3 nm,
λ<1 → regime="boundary" 확인. (출처: Philipossian US20110076924A1; Wu&Liao 2016.)

**Q2. λ ratio(막두께비)의 세 레짐 경계값을 쓰고, λ가 [[hertz-gw-contact-mechanics]]의 어떤 물리량과 연결되는지 설명하라.**
A2. λ=h_film/σ, λ<1 boundary / 1≤λ<3 mixed / λ≥3 hydrodynamic(관례, 미검증). σ는 GW 모델의
asperity 높이분포 표준편차 σ_z와 같은 스케일이다. λ<1이면 유체막두께가 거칠기보다 작아
asperity 끝(GW의 z>d 돌기)이 막을 뚫고 접촉 → 실접촉면적 A_r>0 → 재료제거 가능. 즉
"필름두께 대 asperity 높이 비교"가 곧 λ이며, boundary 판별은 GW 접촉이 살아있음을 보장한다.
완전 유체막(λ>3, hydroplaning)이면 z>d asperity가 사라져 A_r→0, MRR 급감.

**Q3. COF 실시간 측정으로 레짐을 진단하는 원리와, 압력·속도·점도 변화가 레짐을 어느 쪽으로 미는지 답하라.**
A3. COF=F_shear/F_normal을 in-situ 측정해 So(공정조건 계산) 대비 플롯한다(US20110076924A1).
boundary에서는 COF가 So에 대해 평탄한 고값(oxide CMP 문헌 0.23~0.40, 재현 모델 0.24), mixed로
들어가면 하강 기울기가 나타난다 — 이 기울기 출현이 전이 신호. So=μU/(p·δeff)이므로 **압력↓,
속도↑, 점도↑는 So를 키워** mixed/hydrodynamic 쪽으로 밀어 접촉을 줄이고 MRR을 떨어뜨린다.
반대로 boundary 유지(고 MRR)를 위해선 So를 작게 — 즉 충분한 압력과 적정 속도가 필요하다.
저 MRR·hydroplaning 의심 시 So로 1차 점검(Lv3-1 COF·EPD에서 심화).

## Lv2-1 슬러리 유동: 패드 groove 필름두께 모델 (2026-09-05)
근거: [[../../knowledge/physics/cmp-slurry-flow-lubrication-film-thickness]], [[../../knowledge/physics/cmp-lubrication-regimes]], [[../../knowledge/physics/cmp-kinematics-rotary]]

**Q1. Thakurta et al.(2001)이 3-D Navier-Stokes 대신 Reynolds 윤활방정식을 쓸 수 있다고 정당화한 근거는 무엇이며, 그 결과 몇 변수 문제가 몇 변수로 줄어드는가?**
A1. 환산 레이놀즈수 Re* = (ρUR₁/μ)·(h̄/R₁)²를 계산하면 전형 CMP 조건(h̄~수십µm, R₁~수cm)에서
Re*~1e-2~1e-3으로 작다 — 관성항이 점성항에 비해 무시 가능하다는 뜻이며, 이는 슬라이더 베어링
윤활이론의 정당화 조건과 동일하다(Thakurta 2001 Eq.1). 그 결과 (u,v,w,P_f) 4변수 3-D 문제가
**압력 P_f 하나만 푸는 2-D 문제**(일반화 Reynolds 방정식, Eq.13)로 축약된다.

**Q2. h_min이 CMP 레짐 판별에 쓰이는 이유를, 이전 단원(Lv1-2)의 λ ratio와 연결해 설명하라.**
A2. h_min(최소 슬러리 필름두께)이 패드 평균거칠기(~20µm)보다 크면 웨이퍼가 패드에서 완전히
떠 있는 윤활레짐, 작으면 asperity가 막을 뚫는 접촉레짐이다. 이는 [[cmp-lubrication-regimes]]의
λ=h_film/σ<1(boundary)/≥3(hydrodynamic) 판별과 **동일한 물리**를 다른 방식(3-D 압력장 직접
계산 vs 오더 추정)으로 표현한 것 — h_min은 λ 계산에 쓰는 h_film의 정량 계산치에 해당한다.

**Q3. 웨이퍼 자전 속도(ω₁)를 증가시키면 h_min이 증가하는가 감소하는가? 왜 이것이 "직관에 반하는" 결과인가?**
A3. **감소한다.** 직관적으로는 회전이 빨라지면 유입 유량이 늘어 필름이 두꺼워질 것 같지만,
패드 회전(ω₂)에 의한 슬러리 유입은 패드 표면속도가 만드는 압력구배(수렴유로)에 의존하는데,
웨이퍼가 자전하면 웨이퍼 표면에서의 상대속도 분포가 바뀌어 이 패드 유입 효과를 상쇄한다
(Thakurta 2001 Fig.7a, §5 표 "웨이퍼 회전속도만↑(패드 고정)" 항목 — 유일하게 회전 증가가
반대 방향 효과를 갖는 파라미터). 재현: `sim/tier2_physics/slurry_film_lubrication.py`
`h_min_wafer_rotation_effect()` — ω₁ 증가 시 대리량 감소 확인(PASS).

## Lv2-2 마찰열·온도장 → Arrhenius 화학반응속도 결합 (2026-09-06)
근거: [[../../knowledge/physics/frictional-heating-temperature-arrhenius-coupling]], [[../../knowledge/physics/tribology-friction-wear-stribeck]], [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]

**Q1. 단위면적당 마찰발열 q=μ·P·V를 쓰고, 전형 CMP 조건으로 전체 마찰동력을 산출해 White et al.(2003)의 문헌값과 오더를 대조하라.**
A1. 마찰응력 τ=μP에 미끄럼속도 V를 곱한 소산동력의 면적밀도가 q=μPV [W/m²]이고, 전체 마찰동력은
Q_f=q·A_wafer. 전형값 μ=0.3(oxide CMP COF 0.23~0.40, boundary~mixed 레짐), P=0.05 MPa, V=0.75 m/s
(Ma et al. 2023 조건)에서 q=0.3·50000·0.75=**1.13×10⁴ W/m²**, 200 mm 웨이퍼(A=0.0314 m²)에서
Q_f=q·A≈**353 W**. White, Melvin, Boning(*J. Electrochem. Soc.* 150 G271, 2003, DOI 10.1149/1.1560642)의
마찰열 **200~300 W**(화학열 ~1 W로 발열은 마찰 지배)와 **같은 오더**다. 역산하면 200~300 W는
6.4~9.5×10³ W/m²로 q=μPV 오더와 부합. 재현: 노트 §6 verify 블록 PASS.

**Q2. "공정온도가 Cu/oxide 선택비를 조절한다"는 Shin et al.(2025)의 주장을 Arrhenius 배율 계산으로 정량 설명하라.**
A2. RR=A·exp(−Ea/RT)이므로 T1→T2 반응속도 배율=exp[(Ea/R)(1/T1−1/T2)]. Shin et al.(*Materials* 18(19)
4461, 2025, DOI 10.3390/ma18194461, PMC12525981) 실측 겉보기 Ea는 SiO₂ 8.75, Ta 29.9, Cu 151.7 kJ/mol.
ΔT=20 ℃(30→50 ℃)에서 배율은 **Cu ≈41.5배, Ta ≈2.08배, SiO₂ ≈1.24배**다. 즉 같은 온도상승이 Cu MRR을
수십 배 키우지만 oxide는 거의 안 바꾼다 → 온도가 곧 선택비 손잡이. Ea가 큰 Cu일수록 지수항 민감도가
커서 그렇다. 냉각으로 T_ss를 30 ℃로 낮추면 Cu 과다제거·dishing이 억제된다(Shin 2025). 재현: 노트 §6 PASS.

**Q3. CMP 계면에서 마찰열이 "표면에 집중"되는 물리적 이유와, 평균온도 vs 플래시온도의 차이를 설명하라.**
A3. 다공성 폴리우레탄 패드의 열전도도가 k≈0.02 W/m·K로 극히 낮아(Shin 2025) 열확산계수 α=k/ρc_p가
물보다 훨씬 작다 → 마찰열이 패드 심부로 빠지지 못하고 계면 근처에 축적되어 웨이퍼·슬러리로 흐른다.
**평균 온도상승**은 웨이퍼 전면 평균(수~수십 ℃, 실측 미제어 ~36 ℃; 슬러리 전량냉각 상한 에너지균형으로
19~29 ℃ 오더 재현)인 반면, **플래시 온도**는 asperity 실접촉점(A_r≪A_n, [[hertz-gw-contact-mechanics]])에서만
순간적으로 오르는 국소 고온으로, 국소 열유속 q_local=q·(A_n/A_r)이 평균의 수십 배라 평균보다 훨씬 높다
— 화학반응온도는 이 transient flash heating이 결정한다(Shin 2025 서술). 플래시 절대값은 **미검증**(Lv3 후보).

## Lv3-1 COF 실시간 모니터링과 EPD(종점검출) (2026-09-06)
근거: [[../../knowledge/physics/friction-cof-monitoring-endpoint-detection]], [[../../knowledge/physics/cmp-lubrication-regimes]], [[../../knowledge/physics/frictional-heating-temperature-arrhenius-coupling]]

**Q1. 마찰전단력에서 플래튼 모터전류까지의 신호 사슬을 쓰고, "플래튼 모터가 마찰을 이기며 쓰는 동력이 곧 마찰발열"임을 항등식으로 보여라.**
A1. 계면 전단력 F_shear=μ·F_normal=μ·P·A(Amontons). 이 힘이 회전 플래튼에 거는 저항토크는
τ_wafer≈F_shear·r_c(r_c=웨이퍼중심의 플래튼축 반경). DC/BLDC 모터는 τ=K_t·I이므로 모터전류
I=τ/K_t ∝ F_shear ∝ μ. 모터가 마찰을 이기며 쓰는 기계동력은 P_motor,fric=τ_wafer·ω=F_shear·(r_c·ω)=
F_shear·V=μ·P·V·A. 한편 [[frictional-heating-temperature-arrhenius-coupling]]의 단위면적 마찰발열
q=μPV, 전체발열 Q_f=q·A=μPVA. 따라서 **P_motor,fric=Q_f** — 모터가 마찰에 쓴 전기동력과 계면에서
소산된 마찰열은 같은 μPVA다. 재현(노트 §6): 3psi·300mm·0.70m/s·μ=0.4에서 둘 다 409 W(White 2003
마찰열 200~300W와 동오더). 단 실제 모터전류엔 베어링·링·컨디셔너 baseline이 겹쳐 종점신호는 소신호.

**Q2. Headley et al.(2019)에서 플래튼 모터전류(PMC)가 COF(r=0.758)보다 전단력(r=0.955)과 더 강하게 상관하는 이유를 물리로 설명하라. 그리고 COF 상관을 끌어내린 5개 케이스가 어느 윤활레짐인지 답하라.**
A2. PMC는 토크=F_shear·r_c 이므로 **전단력의 직접 대리**다 → 거의 선형(r=0.955, R²=0.916).
반면 COF=F_shear/F_normal 은 수직력으로 정규화가 한 번 더 들어가 F_normal의 요동이 산포로 더해져
상관이 낮아진다(r=0.758, R²=0.608). 즉 모터전류는 엄밀히 "COF계"가 아니라 "전단력계"다
(Headley, Sampurno, Philipossian, *ECS JSST* 8(10) P634, 2019, doi.org/10.1149/2.0251910jss). COF를
끌어내린 5개 케이스는 COF가 pseudo-Sommerfeld 수에 거의 안 변한 **boundary 윤활**(Stribeck의
boundary plateau, [[tribology-friction-wear-stribeck]])이다. 역으로 완전 hydrodynamic이면 μ가
점성전단 지배로 재료무관·저값이 되어 마찰 EPD 대비가 사라진다 → 마찰 EPD는 boundary~mixed에서 성립.

**Q3. 마찰기반 EPD의 "소신호-검출지연-과연마" 트레이드오프를 Li et al.(2017) 수치로 설명하고, 마찰법이 광학·와전류법 대비 갖는 근본한계 하나를 말하라.**
A3. 종점신호(모터전력 계단 Δ≈1630 W)는 baseline(≈30,300 W)의 **약 5%**에 불과한 소신호라 잡음에
묻힌다(Li, Lu, Luo, *Micromachines* 8(6) 177, 2017, PMC6190379). 이를 잡으려 이동평균 창을 넓히면
검출이 지연된다: 121점(half-span 60)·12.15 Hz → 지연 T=N/R≈**4.94 s(<5 s)**, TEOS 229 nm/min에서
**과연마≈18.8 nm(<20 nm)**. 창↑→잡음↓·지연↑·과연마↑의 저울이다(샘플링을 40Hz로 올리면 완화).
근본한계: 마찰신호는 **웨이퍼 전면 평균값**이라 within-wafer·die-level 공간불균일을 못 본다(Lai 2001
MIT thesis ch6) — 광학(간섭/반사)의 국소검출이나 와전류의 도전막 두께 직접측정과 달리 공간분해가 없어,
실무에선 멀티센서로 보완한다. 또 barrier(Ta/TaN)와 하지 유전체의 COF가 유사하면 전이신호가 약해
Cu→barrier 전이를 잡고 정해진 overpolish 시간을 더하는 방식으로 운용한다.
