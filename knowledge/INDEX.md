# 지식베이스 인덱스

> llm-wiki 방식: 모든 노트는 [[상호링크]] + 출처 필수.
> 상태 표기: **검증**(코드/수치 재현 완료) / 출처확인 / **미검증**(출처 불충분)

## cmp/
- [[preston-luo-dornfeld-mrr]] — Preston(1927) 선형식, Brown/Tseng-Wang/Bulsara/Luo-Dornfeld(2001)/Fu/Shi-Zhao/Bastawros 모델 계보 정리. **검증**(sim/tier1_empirical/preston.py 5/5 PASS) (2026-09-04, process-integrator Lv2-1)
- [[colloid-zeta-dlvo-slurry-stability]] — 제타전위/Henry식(Smol·Hückel), Debye 길이 κ⁻¹≈0.304/√I, DLVO V_T=V_vdW+V_edl(장벽·2차최소), 세리아/실리카/알루미나 IEP·pH·이온세기 안정성. **검증**(sim/tier2_physics/dlvo_colloid.py 12/12 PASS) (2026-09-05, slurry-chemist Lv1-1)
- [[wiwnu-pressure-velocity-wafer-scale]] — WIWNU 지표(half-range·σ·3σ, 산업표준 부재), MRR(r)=Kp·P(r)·V(r) 결합, 멤브레인 존압·리테이너링 엣지효과(플랫펀치 특이점·Fu-Chandra·Boning). **검증**(sim/tier1_empirical/wiwnu.py 5/5 PASS: 속도만 0.195% vs 압력만 14.1%로 압력지배 정량) (2026-09-05, process-integrator Lv2-2)
- [[slurry-components-overview]] — 슬러리 6요소(연마입자 실리카/세리아/알루미나·산화제 H2O2/Fe/SPC·억제제 BTA·착화제 citrate/glycine·분산제·pH완충) 역할·상호작용, Kaufman 경쟁모델(산화제-MRR 정점), BTA Langmuir passivation. **검증**(sim/tier2_physics/slurry_components.py 12/12 PASS: BTA ΔG=-35.4kJ/mol→K=2.9e4, 1mM θ=0.97 / 산화제 정점 1%→3% 이동) (2026-09-05, slurry-chemist Lv1-2)
- [[particle-wafer-interaction-mechanical-chemical-balance]] — 단일 연마입자 Hertz 접촉(실리카 R=50nm, F=50nN→접촉응력 1.22 GPa·압입 0.271 nm), 탄성/소성 전이(p_max vs 경도 H), 화학-기계 시너지 δ_p=F/(2πRH)∝1/H·plowing V∝H⁻¹·⁵(연화 4배→체적 8배), Luo-Dornfeld 활성입자 MRR∝P^½V·정지식각 vs CMP 레짐, Kaufman passivation-abrasion. **검증**(노트 verify 1블록 PASS: GPa 접촉응력·sub-nm 압입·8배 시너지·V₁∝F^1.5) (2026-09-06, slurry-chemist Lv2-2)
- [[ceria-slurry-ce-redox-selectivity]] — 세리아(CeO₂) CMP: Ce³⁺/Ce⁴⁺ 산화환원(산소공공 x→Ce³⁺ 분율 f=2x 전하균형), Si-O-Ce "chemical tooth" 화학결합(DFT 규산 흡착E −111/−258 kJ/mol=화학흡착, (100)/(111) 2.32배·Brugnoli 2023 PMC10116594), 세리아-실리카 IEP(6.8/2.5) 정전인력, oxide:nitride 선택비 제어(아미노산·계면활성제, Hwang 2024 선택비 59–80·Netzband 2020 H₂O₂→Ce³⁺↑ MRR 5.5배). **검증**(노트 verify 1블록 PASS: 전하균형·화학흡착·정전인력·선택비 재현) (2026-09-06, slurry-chemist Lv3-1)
- [[pattern-dependent-dishing-erosion]] — MIT effective-density 모델(RR=K/ρ_eff, planarization length 3–5mm), step-height 두 레짐(비압축성 선형/압축성 지수감쇠)+통합모델(h1=a1+a2exp(-ρ/a3)), Cu dishing/oxide erosion 정의·overpolish·removal-rate diagram(정상상태 d_ss), Cu interaction distance 50–100µm. **검증**(sim/tier1_empirical/pattern_density.py 9/9 PASS: 제거량∝1/ρ_eff, τ회수, d_ss 교차) (2026-09-05, process-integrator Lv3-1)
- [[post-cmp-metallic-contamination-sources]] — post-CMP 오염 발생원 분류: 슬러리유래(Fe/Fenton·K/NH₄완충·세리아 Ce-O-Si결합·BTA유기)·배선 Cu²⁺ 재흡착(제타/pH 정전흡착)·패드/디스크·세정수. atoms/cm² 축, 허용치 ~1e10=단분자층 1.5e-5(15ppm ML), Fe 세정전 ~1.5e12(허용치 150배). **검증**(노트 §6 verify PASS: Si(100) 6.78e14/cm², Cu²⁺ Boltzmann 농축 IEP 1배→−40mV 22배 단조증가) (2026-09-06, surface-contamination Lv1-1)
- [[pattern-metrics-dishing-erosion-stepheight]] — 패턴 지표 문헌 정의: dishing/erosion 기준면 3종 병기(Park 1998·Pan 1999·Noh e1/e2, 총손실=field loss+erosion+dishing), step height=ISO 5436-1형 LS(Z=aX+b+hδ), residual 2개념·edge roll-off 2개념(SEMI M77 ROA/M68 ZDD/M67 ESFQR vs CMP 엣지 프로파일) 분리, 측정 구조물 8종 치수표(MIT/AMAT/IBM US5723874/PDF Solutions US7197726/ITRS), ITRS 2007 스펙(erosion=10%×높이, 100 µm dishing 24→5 nm). **검증**(노트 §6 verify PASS: ITRS erosion 행 9/9 재현 ±0.5 nm, IBM 밀도정의 11/11, LS 스텝 0.01 nm, 곡률오차 8.9% vs ~10%, ROA 규약 4배차) (2026-09-07, wafer-metrology Lv2-2)

## materials/
- [[pad-viscoelasticity-dma]] — 패드 폴리우레탄 저장/손실탄성률, Maxwell 모델, DMA. **검증**(sim/tier2_physics/viscoelastic_maxwell.py 5/5 PASS) (2026-09-04, pad-mechanic Lv1-1)
- [[pad-structure-groove-subpad]] — IC1000류 발포체·K-groove·subpad 구조, 역할분리(국소 vs 글로벌). *출처확인* (2026-09-04, pad-mechanic Lv1-2)
- [[hertz-gw-contact-mechanics]] — Hertz 단일접촉(F~delta^1.5) + Greenwood-Williamson 통계 asperity모델(지수분포, A_r∝W 선형성). **검증**(sim/tier2_physics/gw_contact.py 5/5 PASS) (2026-09-04, pad-mechanic Lv2-1)
- [[pad-viscoelasticity-temp-frequency-dma]] — 패드 PU E'·tanδ의 온도·주파수 의존: WLF/TTS(1955 보편상수 17.44/51.6 K ↔ 8.86/101.6 K 재매개화 재현), Cabot US20170087688A1 Table 1B(D100 E' 25/50/80 °C=1000/141/19 MPa, Tg(DSC) 43~46 °C·tanδ 피크 56~67 °C @1 Hz → 25→50 °C E' 3~10배 감소), Khanna 2019(E'25/E'90 비 188/21/4 ↔ MRR 드리프트 2/1.45/1 순서 일치), GW A_r∝1/E* 연결. Kim 2006(35→10 MPa)과 15배 불일치 원인 미상·IC1000 자체 E'(T) 표 미확보로 정직 기록. **검증**(노트 §6 verify 1블록 PASS, 출처 12건 실존) (2026-09-07, pad-material Lv2-1)
- [[pad-glazing-mechanism-mrr-decay]] — glazing 3요소(asperity 소성평탄화·기공 막힘·잔류물 응착) 정의, Jeong 2024(OA, doi 10.3390/ma17081817) 무컨디셔닝 10 min: 접촉점 109→56(−49%)·반경 7.8→19.6 µm·MRR −17%(초기 상승 후 급감), 1 min 컨디셔닝 복원; Lawing 2004 ex situ 감쇠 fumed −35% vs colloidal −7%(로그형 R²>0.95). **검증**(노트 verify 1블록 PASS, 출처 6건 실존) (2026-09-07, pad-lifecycle Lv2-1)

## equipment/
- [[conditioning-mechanism-asperity-regeneration]] — Lawing 2004 실측(경쟁효과·공격성·접촉면적%) + Ring/Prasad/Dirksen population balance 유사변수해(정성 재현, 폐형식해 수치검증은 미검증). *출처확인/부분미검증* (2026-09-04, disk-conditioner Lv1-1)
- [[cmp-tool-architecture]] — 헤드/플래튼/리테이너링/컨디셔너 구조, 플렉시블 멤브레인·존별 압력제어(AMAT 특허), 문헌 표준 공정조건. *출처확인* (2026-09-03, process-integrator Lv1-1)

## physics/
- [[cmp-kinematics-rotary]] — 회전식 폴리셔 상대속도장 유도, ω_w=ω_p 균일성, 운동학 수 µ와 NU=2|µ|. **검증**(sim/tier1_empirical/kinematics.py 7/7 PASS) (2026-09-03, process-integrator Lv1-2)
- [[tribology-friction-wear-stribeck]] — Amontons-Coulomb 마찰(실접촉면적), Archard 마모식 V=k·W·L/H(Kp≈k/H 대응), 윤활 3레짐·Stribeck 곡선(µ 최소점), Hersey/Sommerfeld 수로 CMP=mixed/boundary 판별. **검증**(sim/tier2_physics/tribology_basics.py 10/10 PASS) (2026-09-05, tribologist Lv1-1)
- [[cmp-lubrication-regimes]] — CMP Sommerfeld So=μU/(p·δeff)·δeff=αRa+(1-α)δgroove(Philipossian 특허), λ ratio 레짐경계, 유체역학 길이 ℓ_hd=μU/p≈36nm≪Ra로 CMP=boundary 정량논증(So≈λ), COF 0.23~0.40 진단. **검증**(sim/tier2_physics/cmp_lubrication_regime.py 11/11 PASS) (2026-09-05, tribologist Lv1-2)
- [[cmp-slurry-flow-lubrication-film-thickness]] — 3-D Reynolds 윤활방정식(패드 다공성·처짐 포함, Thakurta 2001), Re*로 윤활이론 정당화, z₀ 무차원 길이스케일, h_min 파라미터 의존성(압력↓·속도↑·점도↑→h_min↑, 웨이퍼자전↑→감소). *출처확인/정성재현*(sim/tier2_physics/slurry_film_lubrication.py 10/10 PASS, 절대 h_min 미검증) (2026-09-05, tribologist Lv2-1)
- [[frictional-heating-temperature-arrhenius-coupling]] — 마찰발열 q=μPV(≈1.1e4 W/m², Q_f≈353W→White 2003 200-300W 오더), 계면 온도장(평균 수~수십℃·플래시·패드 저열전도 k=0.02W/mK), Arrhenius RR=A·exp(-Ea/RT)로 열-화학 결합(Shin 2025 Ea Cu 151.7/Ta 29.9/SiO₂ 8.75 kJ/mol, ΔT20℃→Cu 41.5배·oxide 1.24배로 선택비 급변). **검증**(노트 §6 verify 블록 PASS) (2026-09-06, tribologist Lv2-2)
