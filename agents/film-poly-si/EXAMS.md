# 자기시험 — 폴리실리콘 CMP 전문가 (film-poly-si)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1 Poly-Si 물성(도핑·결정립)과 CMP 거동

**Q1. 고농도 보론도핑 poly-Si가 무도핑 poly-Si보다 CMP 제거율(MRR)이 낮은 이유를 전자적
관점에서 설명하라.**

A1. 보론은 억셉터(p-type)로 poly-Si 표면 근처에 음전하 공핍층을 형성하고, 알칼리 슬러리의
핵심 식각종인 수산화이온(OH⁻)을 정전기적으로 반발시켜 표면 전달(transportation)을
억제한다. 이 때문에 화학적 식각 속도가 느려져 MRR이 낮아진다. 실측으로 무도핑(웨이퍼 C)
MRR이 고농도 보론도핑(웨이퍼 A, 저항 2.2 mΩ·cm) 대비 약 5배 높고, 저항이 2.2→3.5 mΩ·cm로
증가(도핑 감소)하면 MRR이 약 3배 증가한다. 출처: Pirayesh, H. (2014), PhD thesis, Univ. of
Alberta, 6장 ("Boron doping effects on polysilicon CMP") — [[../../knowledge/materials/film-poly-si-doping-grain-cmp]] §2.

**Q2. Park et al.(2016)의 poly-Si LPCVD 증착온도(545/585/625°C) 실험에서, 증착온도가
높을수록 MRR이 증가한 이유를 결정립 크기가 아니라 무엇으로 설명했는가?**

A2. 결정립 "크기" 자체는 LPCVD 온도에 따라 변하지 않았다(결정립계 밀도만 증가). MRR의
경향을 실제로 좌우한 것은 **영률(Young's modulus)**이었다 — 증착온도가 높을수록 영률이
낮아지고(169→151 GPa, 어닐링 전), 재료가 무를수록 CMP로 더 빨리 깎여 MRR이 높아진다(어닐링
전 7032→7200 Å/min). 즉 결정립계 밀도/영률이 매개 변수이고, 결정립 크기는 이 실험 범위에서
직접적 인과관계가 없었다. 출처: Park, S., Jeong, H., Yoon, S.-H. (2016), DOI:
10.7763/IJMMM.2016.V4.236 — [[../../knowledge/materials/film-poly-si-doping-grain-cmp]] §3.

**Q3. 로직 게이트 CMP와 3D NAND 채널 CMP에서 poly-Si가 수행하는 역할의 근본적 차이는
무엇인가?**

A3. 로직 게이트(HKMG replacement-gate 흐름, 통념상 서술 — 1차 문헌 미확보·미검증)에서
poly-Si는 **희생(더미) 게이트**로, CMP 후 습식/건식 식각으로 완전히 제거되고 금속 게이트로
치환된다 — 최종 소자에 남지 않는다. 반면 3D NAND에서는 워드라인이 텅스텐 리플레이스먼트
게이트이고, poly-Si는 수직 채널홀을 채우는 **채널 재료로 최종 소자에 영구히 남는다**(Lee et
al. 2021이 보인 macaroni oxide/poly-Si channel/tunnel oxide/charge-trap nitride/blocking
oxide 스택). 따라서 3D NAND CMP는 "남기는" 재료의 평탄도·디싱 균일성(채널-간 저항 산포
억제)이 목표인 반면, 게이트 CMP는 "제거 준비"를 위한 평탄화·종료점 확보가 목표다. 출처:
Lee, J. et al. (2021), DOI: 10.3390/electronics10212632 —
[[../../knowledge/materials/film-poly-si-doping-grain-cmp]] §4.

## Lv1-2 알칼리(KOH/TMAH/아민) 화학 용해 메커니즘과 pH 의존성

**Q1. poly-Si의 알칼리 습식 식각률은 KOH(=OH⁻) 농도를 계속 올린다고 단조 증가하지 않고 특정
농도에서 최대를 찍은 뒤 감소한다. Seidel의 속도식으로 그 이유를 설명하라.**

A1. Seidel et al.(1990)은 전 농도범위 최적 피팅으로 식각률 R ∝ [H₂O]⁴·[KOH]^(1/4)를 얻었다.
OH⁻(≈KOH) 농도 의존은 **4제곱근**이라 매우 약하게만 증가하는 반면, 물 농도 의존은 **4제곱**으로
강하다. 알칼리 농도를 올리면 [OH⁻]^(1/4)는 완만히 오르지만 용액에서 물이 밀려나 [H₂O]⁴가
급락하므로, 둘의 곱인 식각률은 어떤 농도에서 **최대(peak)를 찍고 감소**한다. 밀도 근사
ρ=1+0.9w로 rate-law를 최대화하면 peak≈16.8 wt% KOH로, 문헌 관측 ~20 wt%((100)-Si)와 동일
오더로 대조된다. 출처: Seidel, H. et al. (1990), DOI: 10.1149/1.2086277 —
[[../../knowledge/materials/film-poly-si-alkaline-dissolution-ph-kinetics]] §3·§7.

**Q2. Bae et al.(2022)에서 에틸렌디아민(EDA)은 같은 pH(~10.9)의 NaOH/KOH보다 Si 폴리싱률이 약
3배 높았다(EDA 552.8 vs NaOH 177.1 nm/min). "OH⁻ 농도는 pH에 단순 비례한다"는 사실과 함께,
이 3배 차이가 왜 순수 화학(pH/OH⁻)만으로 설명되지 않는지, 그리고 무엇으로 설명되는지 답하라.**

A2. EDA·NaOH·KOH의 OH⁻ 농도는 슬러리 pH에 단순 비례하므로 **같은 pH면 OH⁻ 농도가 같다**. 따라서
OH⁻ 공급(=화학적 용해 구동력)만으로는 세 물질이 같아야 하고, 3배 차이는 설명되지 않는다. Bae는
초과분을 세 요소의 시너지로 분해했다: (i) 화학 — EDA로 XPS Si-O-H 비율이 18.5%→42.2%로 늘어
수화(무른 층)가 심화, (ii) 흡착 — 접촉각이 50.5°→14.55°로 급감해 슬러리·입자의 표면 전달 증가,
(iii) 정전기 — 실리카 zeta(−44.9→−36.8 mV)·웨이퍼 표면전위가 덜 음전하가 되어 입자-막 반발력
감소(1503→1043 상대단위)로 기계적 접촉 효율 상승. 즉 화학(용해)×기계(마모)의 시너지에서 아민이
세 축을 동시에 밀어올린 결과다. 출처: Bae, J.-Y. et al. (2022), DOI: 10.3390/nano12213893 —
[[../../knowledge/materials/film-poly-si-alkaline-dissolution-ph-kinetics]] §4·§5.

**Q3. Seidel(1990)의 알칼리 용해 전기화학 모델을 한 반응식으로 쓰고, 그 모델이 왜 고농도 보론
도핑 poly-Si의 MRR 저하(Lv1-1)를 설명하는지 연결하라.**

A3. 모델의 산화 단계는 "OH⁻ 4개가 표면 Si 1개와 반응해 전도대로 전자 4개를 주입"하는 것으로,
정미 반응식은 **Si + 4OH⁻ → Si(OH)₄ + 4e⁻**이다(Bae의 2단계 식 (2)+(3) 합과 계량적으로 일치).
이 주입된 전자는 표면 공간전하층 때문에 표면 근처에 국소화된다. 핵심이 "전자 주입 + 표면
공간전하층"이므로, p형(보론) 도핑이 만든 표면 공핍층은 이 전자 주입과 OH⁻ 접근을 정전기적으로
방해해 용해(따라서 화학적 MRR)를 억제한다 — 이것이 Lv1-1에서 본 "고농도 보론 poly-Si의 MRR이
무도핑 대비 ~5배 낮다"는 실측의 전기화학적 근거다. 출처: Seidel, H. et al. (1990), DOI:
10.1149/1.2086277 — [[../../knowledge/materials/film-poly-si-alkaline-dissolution-ph-kinetics]]
§2; Lv1-1 [[../../knowledge/materials/film-poly-si-doping-grain-cmp]] §2.

## Lv2-1 Poly:oxide 선택비 설계와 게이트 CMP 공정 윈도우 (2026-09-11)

**Q1. Park et al.(2007, DOI 10.3938/jkps.51.214)에서 TMAH 농도를 올렸을 때 poly:oxide 선택비는
왜 비단조(피크형)로 움직이는데 oxide 제거율은 40–60 Å/min 구간에 거의 고정되는가?**

A1. 선택비 변화는 거의 전부 poly 제거율의 비단조 변화에서 온다 — oxide는 TMAH 화학에 거의
반응하지 않고 순수 기계적 마모율에 가깝게 유지되기 때문이다(원문: "the oxide removal rate was
maintained at 40 to 60 Å/min"). poly 쪽은 OH⁻가 실라놀기를 만들어 Si–Si 백본드를 약화시키는
화학 용해(Seidel 반응식과 정합)와, poly-oxide 제타전위 비대칭(poly는 pH10+에서도 약한 음전하,
oxide/실리카는 강한 음전하)이 만드는 abrasive–poly 정전 인력/abrasive–oxide 정전 반발이 겹쳐
농도에 따라 피크-후-하락하는 접촉각(친수성) 곡선을 그대로 따라간다. 출처: [[../../knowledge/materials/film-poly-si-oxide-selectivity-gate-cmp-window]] §2.

**Q2. 같은 poly-Si/SiO₂ 재료쌍인데 US10119048B1(2018)의 아민 알콕실레이트 첨가 슬러리에서는
선택비 방향이 §2와 왜 반대로 뒤집히는가? 무첨가 대비 수치로 답하라.**

A2. 목표 공정 자체가 반대다 — §2(Park 2007)는 NAND 플로팅게이트/STI형으로 poly를 빨리 깎아야
하지만, US10119048B1은 replacement metal gate 공정으로 더미 poly-Si 게이트를 etch stop으로
보존하며 위의 TEOS(ILD) 산화막만 깎아야 한다. 그 결과 명세서는 oxide:poly 선택비를 최소 3:1,
바람직하게는 8:1–20:1로 설계 목표를 못박는다. 무첨가(Ex.16)는 TEOS 3867 / poly 1721 =
2.25:1에 그치지만, 아민 알콕실레이트 0.0050 pbw 첨가(Ex.19)는 TEOS 2065 / poly 115 = 17.96:1로
명세서 우선범위 안에 들어온다 — 같은 재료쌍이라도 첨가제 설계로 선택비의 부호와 크기가 모두
뒤집힌다. 출처: [[../../knowledge/materials/film-poly-si-oxide-selectivity-gate-cmp-window]] §4.

**Q3. Seidel(1990) 활성화에너지 차이(Ea_SiO2=0.85 eV, Ea_Si=0.59 eV)로 예측한 상온 습식식각
Si:SiO2 선택비는 얼마이며, 이것이 §2·§4의 CMP 실측 선택비(25–114:1)와 왜 자릿수가 다른가?**

A3. Arrhenius 비 exp((0.85−0.59)/(kB·295K))로 계산하면 상온 습식식각 선택비는 오더
~2.8×10⁴:1로 예측되는데, 이는 CMP 실측 최대치(114:1)보다 200배 이상 크다. 이 괴리는 Seidel
모델이 정적 습식식각만 기술하는 반면 CMP는 여기에 기계적 마모가 곱해지는 동적 과정이기
때문이다 — oxide는 화학적으로는 거의 안 깎이지만 연마입자의 기계적 마모가 화학적 식각보다
훨씬 빠르게 벗겨내므로, 화학이 부여하는 거대한 잠재 선택비가 CMP 실측에서 크게 압축된다.
단 이 압축의 정량 메커니즘(마모 모델 계수)은 확인하지 못했다 — 정성적 방향만 확인
(미검증). 출처: [[../../knowledge/materials/film-poly-si-oxide-selectivity-gate-cmp-window]] §6.
