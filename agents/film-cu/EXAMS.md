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
