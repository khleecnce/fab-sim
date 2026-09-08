# 자기시험 — 구리 CMP 전문가 (film-cu)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1 Cu CMP 3단계(벌크·소프트랜딩·배리어)와 슬러리 요구 (2026-09-08)

**Q1.** Cu damascene CMP가 왜 한 가지 압력·슬러리로 한 번에 밀지 않고 여러 단계(벌크→소프트랜딩→
배리어)로 나뉘는가?
**A1.** 벌크 제거는 처리량을 위해 고압·고MRR이 필요하지만, 배리어 근접부에서는 얇아진 Cu가
과도한 압력·화학적 용해에 노출되면 dishing이 급격히 커진다 — 두 요구가 상충한다. 특허
US2009/0057264A1(Applied Materials)은 벌크(~1.8 psi, ~9000 Å/min) → rate quench 전이
(~0.5 psi) → 소프트랜딩(~1.3 psi, ~1800 Å/min) → 잔류제거(≤0.3 psi)로 다운포스·제거속도를
계단식으로 낮춘다. 소프트랜딩/벌크 제거속도 비는 약 20%(0.15~0.25 범위, verify 재현).

**Q2.** "Rate quench" 전이 스텝의 목적은 무엇이며, 왜 순수 기계적 변수(압력)만의 문제가 아닌가?
**A2.** 벌크 단계에서 패드 위에 누적된 Cu²⁺ 부산물이 BTA 등 억제제의 부동태(passivation) 효과를
떨어뜨린다([[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]] 참조). Rate
quench는 슬러리·린스 유량을 늘려 이 Cu 이온 농도를 씻어내 억제제 효과를 회복시키는 스텝 —
특허 원문 "reduce the copper ion concentration on the polishing pad... preserving passivation
agent effectiveness". 즉 국소 전기화학 평형을 재설정하는 것이지 다운포스 조절만이 아니다.

**Q3.** Pan(1999)의 실측에서, 광폭(100µm) 트렌치의 "최적 오버폴리시" 조건과 5µm pitch 90%
밀도 라인/스페이스 어레이(40% 오버폴리시)의 Cu 두께손실 비율은 각각 얼마이며 어느 쪽이 더 큰가?
**A3.** 광폭 트렌치 최적OP: 500Å 디싱 / 5000Å 목표두께 = 약 10%. 고밀도 어레이 40%OP: 목표두께의
약 70%(erosion이 주 원인). 후자가 훨씬 크다 — erosion 지배(고밀도)가 dishing 지배(광폭
트렌치·최적OP)보다 두께손실 비율이 크다는 것이 이 논문의 핵심 관찰
([[../../knowledge/cmp/cu-cmp-three-step-process-slurry-requirements]] §6 verify 블록 재현,
[[../../knowledge/cmp/pattern-dependent-dishing-erosion]]과 연결).

출처: [[../../knowledge/cmp/cu-cmp-three-step-process-slurry-requirements]] (US2009/0057264A1,
Pan et al. 1999 CMP-MIC, Park et al. 1998 VMIC)

## Lv1-2 Cu 전기화학: Pourbaix, BTA 패시베이션, 산화제-억제제 균형 (2026-09-09)

**Q1.** CRC 표준전위표에 Cu₂O의 반쪽반응이 알칼리형(Cu₂O + H₂O + 2e⁻ = 2Cu + 2OH⁻, E° = −0.360 V)으로만 있다. 이것으로
Pourbaix 도표의 Cu/Cu₂O 경사선을 어떻게 얻고, 용존 Cu 활동도 10⁻⁴에서 Cu/Cu²⁺/Cu₂O 삼중점 pH는 얼마인가?
**A1.** 물의 자동해리(pK_w = 14)를 더해 산성형으로 바꾼다: E° = −0.360 + 0.05916×14 = 0.468 V, 선은 E = 0.468 − 0.05916·pH
(기울기 −59 mV/pH, m = n). Cu²⁺/Cu₂O 선은 E° = 2×0.3419 − 0.468 = 0.216 V에 기울기 +59 mV/pH. 이 선과 Cu²⁺/Cu 수평선
(0.3419 + 0.0296·log a = 0.224 V)이 만나는 삼중점 pH = (0.3419 − 0.216 + 0.118)/0.05916 = 4.14 — Tamilmani 2005 그림 4.1
판독 4.2와 ±0.15 pH 내 일치. 활동도가 100배 낮아지면 삼중점은 정확히 +1.0 pH 이동한다(verify 1).

**Q2.** 4 % H₂O₂ 용액의 백금전극 실측 산화환원전위가 pH 2에서 약 0.68 V vs SHE인데, H₂O₂/H₂O의 E°는 1.776 V다. 이 1 V의
차이는 무엇이며 Cu CMP 설계에 어떤 뜻인가?
**A2.** H₂O₂는 산화제이자 환원제(O₂/H₂O₂, E° 0.695 V)라서 전극이 읽는 것은 H₂O₂ 분해의 두 반쪽반응이 만드는 혼합전위이지
H₂O₂/H₂O Nernst값이 아니다. 실측 0.41–0.68 V는 O₂/H₂O₂ 선(pH 2: 0.58 V)과 H₂O₂/H₂O 선(1.66 V) 사이에 있다(verify 2).
따라서 Cu 표면이 실제로 보는 전위는 0.4–0.7 V대이고, pH 2–4에서는 Cu²⁺ 영역(막 없이 용해 = 정적식각 허용), pH 6–8에서는
CuO 영역 하단(부동태막)에 걸린다 — 산성 H₂O₂ 슬러리에 BTA가 반드시 필요한 열역학적 이유.

**Q3.** BTA 패시베이션 막의 화학조성·두께·형성속도를 실측 근거로 말하고, 패드 위 Cu²⁺ 농도가 높으면 왜 막 품질이 나빠지는가?
**A3.** XPS: Cu 2p shake-up 위성 없음(Cu²⁺ 부재), Auger Cu⁺ 571.0 eV 강피크, C/N = 2.8(BTA의 3) → 막은 고분자 [Cu(I)BTA]ₙ.
QCM: 0.12 µg/cm² = 6.06×10¹⁴ 분자/cm² = 단분자층(수직 3.3×10¹⁴, 수평 1.6×10¹⁴)의 2–4층, 침지 즉시 형성되며 용해속도를
≈560 Å/min(50 µg/cm²/min 환산)에서 <0.8 Å/min으로 떨어뜨림(verify 3). Cu를 2분 먼저 용해시킨 뒤 BTA를 넣으면 질량이
0.5 µg/cm²까지 늘어나는데, 이는 흡착이 아니라 계면 Cu 이온과 BTA의 착체 침전이다 — 두껍고 느슨한 침전물이 슬러리 BTA를
소모하고 막 품질을 떨어뜨리므로, 3단계 공정의 rate quench가 소프트랜딩 전에 패드 위 Cu 이온을 씻어내는 것이다.

출처: [[../../knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Tamilmani 2005 UA 학위논문 hdl 10150/280774,
CRC Vanýsek 전기화학 시리즈, Lee H. 2023 Micromachines PMC9966509)

## Lv2-1 Cu dishing·erosion 물리와 패턴밀도·선폭 의존성 (2026-09-09)

**Q1.** 오버폴리시 단계에서 "dishing이 깊어지면 Cu 제거율은 줄고 유전체 제거율은 는다"는 removal-rate diagram의 두 직선 기울기는
자유 파라미터인가? 기울기가 어디서 오는지 수식으로 말하고, 정상상태 dishing D_ss와 정상상태 erosion 속도 Y₁을 써라.
**A1.** 자유 파라미터가 아니다. 패드를 Hooke 스프링으로 보면 Cu 위 압력은 P_cu = P₁(1 − D/d_max)로 선형 감소하고, 면적가중 평균압이
P₁로 보존되어야 하므로 유전체 위 압력은 P_ox = P₁[1 + Φ/(1−Φ)·D/d_max]가 된다 — 유전체 쪽 기울기는 Φ_cu/((1−Φ_cu)·d_max)로 **고정**된다
(Tugbawa 2002 eq 3.31–3.34). Preston형을 대입하면 RR_cu = r_cu(1 − D/d_max), RR_ox = r_ox[1 + Φ/(1−Φ)·D/d_max], 교점이
D_ss = d_max(r_cu − r_ox)(1−Φ)/[r_cu(1−Φ) + r_oxΦ], 그때 erosion 속도 Y₁ = r_cu·r_ox/[r_cu(1−Φ) + r_oxΦ] (eq 3.39, 3.41).
Y₁은 Φ에 단조증가(밀도↑ → erosion↑)이고, d_max·w·s는 Y₁에 직접 안 들어간다 — 선폭 효과는 d_max(τ₃)를 통해서만 dishing에 들어간다.
현행 sim의 steady_state_dishing이 쓰는 자유 기울기 b는 이 유도로 제거해야 한다(노트 §6).

**Q2.** 캘리브레이션에서 유효 유전체 제거율 r_ox를 자유 추출하면 측정 블랭킷 속도(< 1 Å/s)의 6–10배가 나온다. 왜 그런가, 그리고 Tugbawa 2001
데이터로 어떻게 확인했는가?
**A2.** 밀도 모델은 스페이스 효과를 d_max 안에 2차로만 담는데, 실측 erosion은 스페이스가 좁을수록 훨씬 크다(w = 20 µm 어레이에서 s = 1 µm
2050 Å vs 100 µm 60 Å, Fig 3.16). 원인은 up-area 가장자리의 국소 압력 피크에 의한 엣지/코너 라운딩이며, 밀도 접근은 L₃ 창으로 평균하면서
이 피크를 지운다. 그래서 피팅이 r_ox를 부풀려 흡수한다. 처방은 ψ(s) = C·e^{−s/s_c} + 1 승수(C ≈ 3–7, s_c ≈ 15–23 µm) — 넣으면 r_ox가
4.34 → 2.22/0.9 Å/s로 내려가고 RMS도 107→70, 74→46 Å로 준다(Table 3.9/3.10). 확인: Tugbawa 2001 Fig 4의 erosion 기울기(80 %: 32 Å/s,
33 %: 15 Å/s)에 eq 3.41을 역으로 풀면 유효 r_ox = 7.8/10.3 Å/s로, 캡션의 측정 블랭킷 1.5 Å/s의 5–7배가 나오고 두 밀도에서 30 % 안에 일치한다
(노트 verify 2).

**Q3.** d_max의 선폭·스페이스 의존을 경험식으로 쓰고, 추출 지수의 크기가 뜻하는 바와 밀도-스텝하이트 모델이 설명 못 하는 세 가지 현상을 들어라.
**A3.** d_max = B·(w/w₀)^α₂·(min(s, s_l)/s₀)^β₂ (eq 3.46; s_l ≈ 100 µm에서 스페이스 포화) 또는 B·w^α₂·ln(s/s_m) (eq 3.47). 추출값 α₂ = 0.17–0.30,
β₂ = 0.19–0.29(Mirra, EPC-5001, 4 psi·75 rpm) — 둘 다 1보다 훨씬 작아 선폭 10배에 dishing 1.5–2배의 **체감 멱법칙**이다. 고립선 판독
(Fig 3.12)에서 10 µm/1 µm 비 2.12는 10^0.303 = 2.01과 6 % 일치하지만 0.25–10 µm 전 구간 지수는 0.51로 표와 어긋난다(원인 미상).
설명 못 하는 것: ① ear/어레이 가장자리 효과(고립선이 같은 폭 어레이선보다 더 파임, 0.25 µm 고립선도 파이는데 H_ex는 0 → d_max ≠ H_ex,
슬러리·입자 효과 포함), ② 과도 오버폴리시(Φ≈99 % 어레이의 erosion 기울기가 꺾이는데 모델은 선형 → 과대예측; 어레이-필드 장거리 높이차가
유효압을 낮추는 항 부재), ③ 순수 선폭 효과(Vasilev 2011: 좁은 nitride up-area가 더 빨리 깎여 dishing이 오히려 줄어드는 현상 — 확장 GW의
곡률항 κ_D = κ_asp − 4αh/s²이 필요).

출처: [[../../knowledge/cmp/cu-dishing-erosion-density-step-height-model-tugbawa]] (Tugbawa 2002 MIT 학위논문 hdl 1721.1/8083,
Tugbawa et al. 2001 CMP-MIC, Park et al. 1998 VMIC, Ruan et al. 2009 J. Semicond., Steigerwald 1994 JES 초록, Vasilev 2011 IEEE TSM)
