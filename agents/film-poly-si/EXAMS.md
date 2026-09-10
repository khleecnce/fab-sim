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
