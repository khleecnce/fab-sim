# 자기시험 — Post-CMP 세정 전문가 (tool-post-clean)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1 Post-CMP 오염 종류와 발생 원인 — "세정 공정 관점"
→ 지식노트: [[../../knowledge/cmp/post-cmp-tool-cleaning-contamination-types-sources]]

**Q1. 접촉식 PVA 브러시 세정이 "제거 도구"이면서 동시에 "오염 발생원"이 되는 기구를 설명하라.**
A1. 브러시는 다공성·친수성 PVA 매트릭스라서 웨이퍼에서 떼어낸 슬러리·패드 파편·유기잔류물을 흡수했다가
그 다음 세정(다음 웨이퍼 또는 같은 웨이퍼의 다른 지점)에서 재부착시킨다 — "uptake of polish waste …
into the brush matrix"가 접촉 모드에서 "waste redeposition and scratching"으로 이어진다
(Wortman-Otto et al., *ACS Omega* 7, 26029, 2022, DOI: 10.1021/acsomega.2c00683, PMC9352252). 이를
줄이려는 비접촉식 메가소닉도 정적 탱크·과출력 조건에서는 재부착 신호(P-103 계면활성제 사례)를 보여,
"비접촉=무오염"은 아니다.

**Q2. Post-Cu CMP 세정에서 부식 억제제(BTA류)가 유기 잔류의 발생원이 되는 이유와, 그 대안(아민)이 갖는
트레이드오프를 설명하라.**
A2. BTA 같은 억제제는 Cu 표면에 임시 보호층을 만들도록 설계되지만, 그 층 자체가 소수성 유기 필름으로
남아 이후 공정(CVD 등)을 방해한다. 대안으로 2-아미노에탄올 같은 통상 아민을 쓰면 유기 잔류는 줄지만
Cu 표면을 에칭해 부식 결함을 만드는 것으로 관찰됐다 — 즉 "유기잔류 제거"와 "부식 방지"가 서로 당기는
축이다(KR102113995B1, EKC Technology, 명세서 배경 설명).

**Q3. PVA 브러시에 흡수된 Cu가 pH에 따라 "헹궈서 제거되는 오염"과 "브러시에 고정되는 오염"으로 갈리는
이유를 pH~6 문턱값과 함께 설명하고, 이 문턱값을 Cu(OH)₂ 열역학으로 어떻게 독립 재현했는지 말하라.**
A3. pH 3에서는 Cu가 이온 상태로 남아 DIW 헹굼으로 크게 제거되지만, pH 7·11에서는 Cu(OH)₂→CuO로
바뀌어 브러시 결절 내부에 Cu(II)–PVA 착물로 고정되며 헹궈도 잘 빠지지 않는다(Bisht et al., 2022,
ICPT proceedings). 지식노트 §6에서는 [[../../knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]가
CRC 표준전위로부터 이미 도출한 Cu(OH)₂ 용해도곱(logKsp=-19.06)을 그대로 이용해, 100 ppm Cu²⁺ 조건의
침전 개시 pH를 계산하면 ≈5.87로 나와 문헌이 인용한 "전이 pH 6"과 상대차 2.2%로 독립 일치함을 코드로
검증했다(서로 다른 문헌·다른 방법의 교차검증).
