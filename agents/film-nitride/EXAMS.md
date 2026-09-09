# 자기시험 — 나이트라이드 CMP 전문가 (film-nitride)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1 SiN 막 종류(LPCVD/PECVD)와 물성, CMP 제거 난이도 (2026-09-10)
> 노트: [[../../knowledge/materials/film-nitride-lpcvd-pecvd-properties-cmp]]

**Q1.** 같은 "실리콘 나이트라이드"인데 LPCVD Si₃N₄가 PECVD SiNₓ:H보다 CMP에서 더 안 깎이는(=더 좋은 정지층) 이유를 조성·수소·경도 관점에서 설명하라.
**A1.** LPCVD는 700–800 ℃ 고온에서 DCS+NH₃로 증착돼 Si–N 망목이 완전 가교되고 수소가 배출돼 **거의 화학량론(Si/N≈0.75)·무수소·고밀도** 막이 된다. PECVD는 200–400 ℃ 저온 플라즈마로 SiH₄+NH₃를 분해해 **Si 과잉·수소 10–19 at%(Si–H·N–H)·저밀도**의 덜 가교된 막이 된다(Yang & Pham 2018, *Silicon*, DOI 10.1007/s12633-018-9791-6, 초록 2차 인용; Gan 2018 *Surfaces* Fig.1a "all SiNₓ films were Si-rich", DOI 10.3390/surfaces1010006). 결과적으로 나노압입 경도가 **LPCVD SiN ≈22.5 GPa > PECVD SiNₓ ≈13.6 GPa**(Gan 2018 Table 2; Zheng 2013 *Adv.Mater.Sci.Eng.* 2차)이고, 수소·Si과잉은 가수분해(제거의 속도결정단계)를 촉진하므로 PECVD가 상대적으로 잘 깎인다. 두 축(기계 경도↑, 화학 가수분해↓)이 모두 LPCVD를 더 단단·불활성으로 만든다.

**Q2.** 나이트라이드는 세리아로도 왜 "직접" 깎이지 않는가? 제거 메커니즘과 첨가제가 선택비를 만드는 원리를 쓰라.
**A2.** 나이트라이드는 옥사이드·세리아보다 단단해(Srinivasan 2015 리뷰 p.P5031 "Silicon nitride is harder than silicon dioxide or ceria", DOI 10.1149/2.0071511jss) 세리아 입자(더 무름)로 직접 긁어낼 수 없다. 대신 표면이 물/산소로 **가수분해**되어 얇은 서브옥사이드(SiO₂/Si(OH)₄)로 바뀌고 그 무른 층만 제거된다: Si₃N₄+6H₂O→3SiO₂+4NH₃, ≡Si–O–Si≡+H₂O→Si(OH)₄. 가수분해가 속도결정단계이므로, 고리형 아민·아미노산 같은 첨가제가 SiN 표면에 흡착해 사이트블로킹하면 가수분해가 억제돼 나이트라이드 RR이 급락한다(Dandu 2009: 세리아+0.05% 아민 → 나이트라이드 2–3 nm/min, 옥사이드 350 nm/min = 선택비 ≈117:1, DOI 10.1149/1.3230624).

**Q3.** Mariscal 2020은 Si₃N₄를 "highly chemically-limited", SiO₂를 "mechanically-limited"라 했고 두 막의 활성화에너지는 1.47 vs 1.40 eV로 거의 같다. 그렇다면 100:1급 선택비는 무엇이 만드는가?
**A3.** 활성화에너지 차이(0.07 eV)는 미미하므로 선택비의 주범이 아니다. 선택비를 세우는 것은 **전지수인자 A**(표면 반응사이트 밀도/반응성)다: SiO₂ A=9.77×10⁻⁴ vs Si₃N₄ A=8.47×10⁻⁶ mol·m⁻²·s⁻¹로 **~115배** 차이가 나고, 이 A비가 관측 블랭킷 선택비(Mariscal 최대 101:1, Dandu 2009 ≈117:1)의 자릿수와 일치한다(Mariscal 2020 Table I, DOI 10.1149/2162-8777/ab89bc). 즉 SiN은 화학(가수분해 사이트가 적음)이 발목을 잡는 chemically-limited 막이라, SiO₂와 온도민감도(Eₐ)는 비슷해도 절대 반응속도가 두 자릿수 낮다.

