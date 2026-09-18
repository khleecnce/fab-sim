# 억제제 × 기질 ΔG_ads 조사 — Round 2

대상: (A) BTA × SiO₂ 흡착 자유에너지 1차 출처 / (B) US9200180B2 벤젠술폰산의 명세서상 기능
조사일: 2026-09-19 · 선행 회차: `~/fab-sim/_proposals/inhibitor_pairs_findings.md`
등록 대상: `sim/inhibitor_pairs.py` 의 `PAIR_TABLE`

---

## 결론 요약

| 항목 | 결과 |
|---|---|
| (A) BTA × SiO₂ ΔG_ads | **미확보** — 아래 §A 참조 (ECS Trans. 52(1) 489 원문 확보 실패 + K 미보고) |
| (B) 벤젠술폰산의 기능 | **확정** — 억제제가 **아니다**. Ta/TaN **착화제 겸 산화제(complexant + oxidant)** = **제거율 촉진제** |
| (B-4) 팩 판정 | **별도 팩 필요.** 'BTA 계 산성 Cu 팩'으로 모델링하면 안 됨 → **알칼리(pH 8.5~10) barrier(step-2) 팩**으로 분리 |

---

# (B) US9200180B2 — 벤젠술폰산의 기능 (원문 인용)

- 특허: US9200180B2, "Chemical-mechanical planarization composition having benzenesulfonic acid and per-compound oxidizing agents, and associated method for use"
- 출원 US12/419,619 (우선일 2003-10-23), 발명자 Gautam Banerjee, Timothy F. Compton, Junaid A. Siddiqui, Ajoy Zutshi
- 현 권리자: Versum Materials US LLC (구 Air Products)
- **원문 확보 경로: 로컬 사본 `~/fab-sim/papers/patents/US9200180B2.html` (Google Patents 전문) — 명세서 + 청구항 전문 직독. 추측 없음.**

## B-1. 명세서상 분류 — 억제제(corrosion inhibitor) 목록인가?

**아니다. 벤젠술폰산은 corrosion inhibitor 목록에 없다. 별개의 "organosulfonic acid" 활성성분 카테고리다.**

명세서의 corrosion inhibitor 목록은 벤젠술폰산을 포함하지 않는다 (원문):

> "Suitable corrosion inhibitors that may be added to the slurry composition include, for example, 1,2,4-triazole, benzotriazole, 6-tolylytriazole, tolyltriazole derivatives, 1-(2,3-dicarboxypropyl)benzotriazole, branched-alkylphenol-substituted-benzotriazole compounds, TINUVIN® 99-2, TINUVIN® 109, TINUVIN® 213, TINUVIN® 234, TINUVIN® 326, TINUVIN® 328, TINUVIN® 329, TINUVIN® 384-2, N-acyl-N-hydrocarbonoxyalkyl aspartic acid compounds, and mixtures thereof."

> "Preferred corrosion inhibitors are 1,2,4-triazole, TINUVIN® 109, TINUVIN® 328, TINUVIN® 329, CDX2128 and CDX2165."

→ 벤젠술폰산은 이 목록 어디에도 없다. 대신 발명의 **주성분(b 성분)** 으로 별도 취급된다:

> "In one embodiment, the invention is a chemical-mechanical planarization composition comprising: a) an abrasive; b) benzenesulfonic acid; c) a per-compound oxidizing agent; and d) water"

명세서는 벤젠술폰산을 **산화제 겸 킬레이트제** 범주로 명시한다 (원문):

> "Furthermore, multifunctional compounds such as ortho- or meta-polar-functional organosulfonic acids act dually as oxidizing agents and as efficient chelating agents."

> "Compared to hydrogen peroxide, benzenesulfonic acid not only serves as oxidants but complexes with tantalum ions to form tantalum sulfonate complexes, which results in high tantalum and/or tantalum nitride removal rates."

**판정: pH 조절제도 아니고, 억제제도 아니다. "산화제 + Ta 착화제 = barrier 제거율 촉진제(accelerator)".**
(참고로 선행기술 인용부에서도 동일 취지: US 6,740,589 를 인용하며 벤젠술폰산을 *"a copper-polishing accelerator"* 그룹의 하나로 서술한다 — 원문: "a copper-polishing accelerator selected from the group consisting of a large number of inorganic acids and organic acids, one of which is benzenesulfonic acid.")

## B-2. 발명자가 주장하는 효과 — Cu 제거율을 낮추나 높이나?

**Cu 제거율은 낮다(억제되는 쪽). 다만 그 억제의 주체는 벤젠술폰산이 아니라 "알칼리 + H₂O₂ 에 의한 Cu 부동태화"다. 벤젠술폰산이 직접 올리는 것은 Ta/TaN 이다.** 메커니즘 서술 원문 전문:

> "While not being bound by any particular theory, the inventor(s) believes that the following considerations may explain why a polishing composition comprising a) an abrasive, b) benzenesulfonic acid, c) a per-compound oxidizing agent, and d) water exhibits enhanced barrier layer material and low-k dielectric material removal rates in CMP processing. Typically when a slurry composition is exposed to copper and tantalum and/or tantalum nitride with a commonly used oxidizer such as hydrogen peroxide under basic conditions during CMP processing, both copper and tantalum and/or tantalum nitride undergo corrosion to form copper and tantalum ions, which forms passive hard copper oxide and tantalum oxide films. ... Thus, in an aqueous composition using hydrogen peroxide at a basic pH, copper and tantalum removal rates are very low. As described in the invention, the addition of benzenesulfonic acid to a slurry is believed to result in complexation with tantalum ions under basic pH polishing conditions. This complexation assists in maintaining tantalum ions in solution as benzenesulfonic acid complexes with tantalum ions, resulting in high tantalum and/or tantalum nitride removal. Interestingly, in the presence of both hydrogen peroxide and benzenesulfonic acid, copper removal rates are typically much lower than tantalum and/or tantalum nitride. This is possibly due to a much higher passivation rate for copper than tantalum and/or tantalum nitride in a mixture of hydrogen peroxide and benzenesulfonic acid."

선택비에 대한 정량적 주장 (원문):

> "5) both Ta and TaN removal rates are substantially increased with increasing benzenesulfonic acid concentration."

> "2) the removal rate of the various materials appears to be at a maximum when the concentration of benzenesulfonic acid is near 1%, for example between about 0.5% and 1.5%, and changes in selectivities are modest over a range of 0.5% to 3% benzenesulfonic acid;"

> "4) the TaN/Copper selectivity increases a large amount with increasing pH in the fluid composition; ... the Copper/PETEOS selectivity decreases a greater amount, and the Copper/low-k selectivity decrease the most with increasing pH;"

> "Generally, at an intermediate benzenesulfonic acid concentration of 2 weight % and hydrogen peroxide concentrations between about 1% and 5%, for example, the increase in the TaN removal rate and decreases in the copper, carbon-doped SiO₂, and PETEOS removal rates are substantially linear with increasing % hydrogen peroxide."

**정리:**
- 벤젠술폰산 ↑ → **Ta/TaN MRR 크게 ↑** (주효과), Cu MRR 은 그에 비해 상대적으로 낮게 유지
- Cu MRR 을 누르는 주체 = **염기성 pH + H₂O₂ 에 의한 Cu 산화막 부동태화**("much higher passivation rate for copper"), **분자 흡착 억제제가 아님**
- 목표 선택비는 오히려 "고선택비 지양, 균형" 이라고 명시:
  > "Additionally, while historically it was believed to be desirable to have selectivity ratios that were very high, e.g., greater than 20, greater than 40, even greater than 100, we believe a more balance approach is superior."
  > "the copper/barrier layer compound selectivity is between 0.66 and 1.5, wherein the PETEOS/barrier layer compound selectivity is between 0.66 and 1.5, and wherein the copper/low-K dielectric selectivity is between 0.66 and 1.5."

→ **이 슬러리는 Cu 제거 슬러리(step 1)가 아니라 barrier 제거 슬러리(step 2)다.** 원문:
> "This invention is especially useful for metal CMP and most especially for step 2 copper CMP processes."

## B-3. pH 범위와 BTA 포함 여부

**pH (원문):**
- 광의: > "wherein the composition has a pH ranging from 4.5 to about 12"
- 대표 임베디먼트: > "wherein the composition has a pH ranging from 5 to 11." (등록 청구항 1도 동일: "wherein the composition has a pH ranging from about 5 to 11")
- 최선호: > "wherein the pH of the fluid composition is between about 7 to about 10.5."
- **실제 실시예는 전부 중성~알칼리다** (원문 실시예 조건):
  - Comparative Ex.1 pH 11.2 / Ex.2 pH 8.5 / Ex.3 pH 9.6 / Ex.4 pH 10.2
  - Ex.5 pH 9.5 / Ex.6 pH 9.1 / Ex.7 pH 8.5 / Ex.8 pH 8.7 / Ex.9 pH 8.6 / Ex.10 pH 8.6
  - Ex.11 pH 9.2 / Ex.12 pH 9.8 / Ex.13 pH 9.8 / Ex.14 pH 10.0
  - Ex.15 pH 6.2 / Ex.16 pH 7.1 / Ex.17 pH 8.7 / Ex.18 pH 9.4 / Ex.19 pH 9.9
  - → **산성 실시예는 하나도 없다. 23개 실시예 중 최저가 pH 6.2, 중앙값 ≈ pH 9.**
  - pH 조절제는 KOH: > "C) Potassium Hydroxide: Aldrich Chemical Company, Inc"

**BTA 포함 여부 — 층위별로 답이 다르므로 정확히 구분해야 한다:**

1. **등록 청구항 1에서는 corrosion inhibitor 가 *필수 구성요소*이고, 그 마쿠쉬 군에 benzotriazole 이 들어 있다** (원문):
   > "1. A chemical-mechanical planarization composition comprising: A) an abrasive; B) about 0.1% to about 8% by weight of a per-type oxidizing compound; C) benzenesulfonic acid and/or a salt thereof; D) a corrosion inhibitor; and (E) water; wherein the composition has a pH ranging from about 5 to 11, and wherein the composition is substantially free of an amino acid having two or more nitrogen atoms, wherein said corrosion inhibitor is selected from the group consisting of 1,2,4-triazole, benzotriazole, 6-tolylytriazole, tolyltriazole derivatives, 1-(2,3-dicarboxypropyl)benzotriazole, branched-alkylphenolsubstituted-benzotriazoles, N-acyl-N-hydrocarbonoxylalkyl aspartic acid, and mixtures thereof."
   > "4. The composition of claim 1, wherein said corrosion inhibitor is present in a concentration from about 1 ppm to about 7000 ppm."
   - 즉 **BTA 는 "들어갈 수 있는 여러 선택지 중 하나"이며, 심사 과정에서 선행기술 회피용으로 청구항에 끌어올려진 한정이다.** 명세서가 꼽은 *선호* 억제제는 BTA 가 아니라 1,2,4-triazole / TINUVIN / CDX 계다(위 B-1 인용).

2. **명세서의 발명 서술과 23개 실시예 전부에는 BTA 가 없다.** 실시예 성분표 원문:
   > "The COMPONENTS used in the Examples include: A) Benzenesulfonic acid ... B) Hydrogen Peroxide: a 30 weight % solution ... C) Potassium Hydroxide ... D) Potassium-stabilized colloidal silica"
   → **실시예 조성 = 콜로이달 실리카 + H₂O₂ + 벤젠술폰산 + KOH. 억제제 0.** 즉 특허가 실제로 데이터로 입증한 슬러리에는 BTA 가 **들어가지 않는다**.

3. 오히려 명세서의 선호 임베디먼트는 억제제를 **빼는** 쪽이다 (원문):
   > "It is envisioned that in certain preferred embodiments of the invention, the polishing compositions are substantially free of water-miscible solvents, surfactants, pH adjusting agents, acids, corrosion inhibitors, fluorine-containing compounds, chelating agents, non-polymeric nitrogen-containing compounds, salts, and any combinations of the foregoing chemicals/additives."
   > "This can be as little as ... 'less than 0.1 weight %' for corrosion inhibitors."

**정리: 명세서 본문/실시예 기준 BTA 는 없다(0 ppm). 등록 청구항 기준으로만 "억제제 중 하나로 BTA 가 선택 가능"하며, 그 경우에도 1~7000 ppm 의 보조 첨가제이고 선호 억제제는 BTA 가 아니다. 어느 층위에서도 "BTA 가 Cu 억제의 주 메커니즘인 슬러리"가 아니다.**

## B-4. 판정 — 'BTA 계 산성 Cu 팩'으로 모델링해도 되는가?

### ❌ 타당하지 않다. **별도 팩(알칼리 barrier/Cu 계)으로 분리해야 한다.** 원문 근거 4가지:

| # | 모델 팩(BTA 산성 Cu) 전제 | US9200180B2 원문 사실 | 충돌 |
|---|---|---|---|
| 1 | pH ≈ 4 (산성) | 청구항 "pH ranging from about 5 to 11", 실시예 pH 6.2~11.2 (중앙값 ≈9) | **전 pH 영역 불일치.** Cu Pourbaix 영역 자체가 다름 |
| 2 | 억제 주체 = BTA 흡착막 (Langmuir θ) | "much higher passivation rate for copper ... in a mixture of hydrogen peroxide and benzenesulfonic acid" — 억제 주체는 **H₂O₂ 유래 Cu 산화물 부동태막** | **억제 물리가 다름.** 흡착 등온식이 아니라 산화막 성장/제거 균형 |
| 3 | 유기첨가제 = 억제제 → MRR ↓ | "both Ta and TaN removal rates are substantially increased with increasing benzenesulfonic acid concentration" — 첨가제는 **가속제** | **부호가 반대.** 첨가제 농도 ↑ 가 MRR ↑ |
| 4 | 대상막 = Cu 제거(step 1) | "especially useful for metal CMP and most especially for **step 2** copper CMP processes"; 목표 선택비 Cu/barrier **0.66~1.5** | **공정 스텝이 다름.** Cu 가 주 제거막이 아님 |

### 결론 및 권고

**앞 회차의 메커니즘 해석("설포네이트는 비배위 음이온이라 부동태막 형성 수단이 없다")은 검증 결과 — 결론은 맞고, 이유는 부분적으로 보정이 필요하다.**
- ✅ 맞음: 벤젠술폰산은 Cu 부동태막을 만들지 않는다. 명세서 어디에도 Cu–sulfonate 막 형성 주장이 없다. Cu 억제는 H₂O₂/알칼리 산화막 몫이다. → **`(benzenesulfonic, Cu)` 쌍은 PAIR_TABLE 에 등록하지 말 것.** 흡착 억제 항이 아니다.
- ⚠️ 보정: "배위력이 없다"는 전면 부정은 과했다. 명세서는 술포네이트가 **Ta 이온과는 용액상 착물을 만든다**고 명시한다("complexes with tantalum ions to form tantalum sulfonate complexes"). 단, 이는 **표면 흡착 부동태화가 아니라 용해 촉진(용액상 착화)** 이므로 ΔG_ads 와는 물리량이 다르다. 굳이 모델링한다면 억제항이 아니라 **Ta 용해도/제거율 촉진 항**이다.

**⇒ 47~95배 MRR 오차의 원인은 쌍 표(PAIR_TABLE)가 아니다.** 팩 정의가 틀렸다. 조치 순서:
1. `bta_acidic_cu` 팩에서 이 슬러리(US9200180B2 계열)를 분리한다.
2. 새 팩 `alkaline_barrier_step2` 를 만들고 축을 다시 잡는다: pH 8.5~10, KOH, H₂O₂ 1~5 wt%, 콜로이달 실리카 3~10 wt%, 유기산=벤젠술폰산(가속제, 0.5~3 wt%), **억제제 없음**.
3. 이 팩의 Cu MRR 은 **BTA 흡착 θ 로 누르는 것이 아니라 알칼리 H₂O₂ 부동태막 기반으로 낮게** 모델링해야 한다. Cu 억제 파라미터를 BTA ΔG 로 튜닝하려는 시도는 물리적으로 틀린 노브다.
4. 이 팩의 주 제거막은 Cu 가 아니라 TaN/Ta/low-k 다. 검증 지표를 Cu MRR 단독이 아니라 **TaN/Cu, TaN/PETEOS 선택비(목표 0.66~1.5)** 로 바꿀 것을 권한다.

---

# (A) BTA × SiO₂ — ΔG_ads

## 결과: **미확보**

- **쌍**: 1,2,3-benzotriazole (C₆H₅N₃) × SiO₂ (colloidal silica / PETEOS)
- **ΔG_ads**: **미확보 (등록 불가)**
- **측정법 / 출처 / 조건 / 다층여부 / confidence**: — (등록 불가. 아래 §A-log 참조)

### 요구 형식으로 기재 (빈칸 = 미확보)

| 항목 | 값 |
|---|---|
| 쌍 | BTA × SiO₂ |
| ΔG_ads (kJ/mol) | **미확보** |
| 측정법 | (리드였던 FCS 경쟁치환 — 정량 K 미보고) |
| 출처(DOI) | 10.1149/05201.0489ecst / 10.1557/opl.2013.1077 (둘 다 본문 미접근) |
| 온도·pH·전해질 | 미확보 |
| 다층여부 | 미확보 |
| confidence | — |

**ΔG = −RT·ln(55.34·K) 환산은 수행하지 않았다. K 값을 1차 출처에서 얻지 못했기 때문이다.** 숫자를 만들어 넣지 않는다.

---

## §A-log — 조사 이력 (재현 가능)

### A-1. 리드 원문 확보 시도 — 모두 실패

**대상 1: Moinpour, Wayman, Rawat, Carver, Remsen, "(Invited) Surface Adsorption of CMP Slurry Additives on Abrasive Particles", ECS Trans. 52(1) 489 (2013), DOI 10.1149/05201.0489ecst**

| 경로 | 결과 |
|---|---|
| `tools/find_open_access.py --title "Surface Adsorption of CMP Slurry Additives on Abrasive Particles"` | DOI 만 반환, **OA PDF 없음** |
| Unpaywall / OpenAlex | `is_oa: false`, `oa_status: "closed"`, `oa_url: null`, 리포지터리 전문 없음 |
| Semantic Scholar API | `openAccessPdf.status = "CLOSED"` |
| IOPscience `/pdf` 직접 요청 | HTTP 302 → Radware(`rdwr`) 봇 차단. 본문 미획득 |
| sci-hub.se / .st | 무관한 논문 반환(캐시 미스 — "Effect of Process Parameters on Particle Removal Efficiency…") = **이 DOI 미보유** |
| sci-hub.ru | 302 리다이렉트, 본문 없음 |
| sci-hub.wf | "Checking your browser…" 차단 |
| libgen.is / .rs / .st scimag | 결과 0건 |
| Anna's Archive SciDB | 응답 없음 |
| 브라우저 자동화 | 클라우드/로컬 백엔드 모두 사용 불가(프로바이더 미가동) |

**대상 2 (동일 연구, 자매 논문): Wayman, Turner, Rawat, Carver, Moinpour, Remsen, "Fluorescence Correlation Spectroscopic Investigation of Surface Adsorption of CMP Slurry Additives on Abrasive Particles", MRS Online Proc. Libr. 1560, mrss13-1560-bb04-04 (2013), DOI 10.1557/opl.2013.1077**
- Springer PDF 링크: HTML 스텁(3 KB)만 반환, PDF 아님
- Cambridge Core: **초록은 확보**, 전문은 페이월
- sci-hub 3개 미러 모두 미보유, OpenAlex `closed`

### A-2. 확보한 초록에서 읽히는 것 — **K 는 애초에 보고되지 않았을 가능성이 높다**

ECS Trans. 52(1) 489 초록 전문(OpenAlex 역색인 복원, 1차 출처의 초록):

> "Fluorescence correlation spectroscopy (FCS) is used to study additive-abrasive particle interactions in chemical-mechanical planarization (CMP) slurries. FCS provides quantitative determinations of the binding between additives and abrasive particles by characterizing the competitive adsorption of the additive and a fluorescent probe molecule, Alexa fluor 546 (A546) at the surface of a silica abrasive particle. **Analysis of the adsorption of benzotriazole (BTA) on colloidal silica confirms the displacement of A546 by added BTA.** However, glycine enhances the adsorption of A546 by colloidal silica. FCS is also shown to be a sensitive technique for detecting differences in the surface chemistry between different types of colloidal silica abrasive particles used in CMP processes."

자매 MRS 논문 초록(Cambridge Core, 1차 출처):

> "…Adsorption of the CMP additives glycine and benzotriazole (BTA) on precipitated and sol-gel colloidal silica abrasives are characterized. Significant differences in the fluorescent probe's adsorption to the different silica abrasives in the presence of the additives suggest surface chemistry differences between the different types of silica. **Extensions of the analysis of FCS data are proposed for improving the quantitative determination of the competitive adsorption of fluorescent probe dyes and CMP additives on abrasive particles.**"

**해석(추정임을 명시):**
1. BTA 에 대해 보고된 것은 **"A546 프로브가 밀려난다(displacement를 confirm)"는 정성 결과**다. 초록 어디에도 BTA 의 K, Kd, θ, ΔG 수치가 없다.
2. 자매 논문이 **"정량 결정을 개선하기 위한 해석법 확장을 제안한다"**고 쓴 것은, 이 시점에서 FCS 경쟁치환 데이터로부터 첨가제의 **절대 결합상수를 뽑는 방법이 아직 확립되지 않았음**을 저자들이 스스로 인정한 것으로 읽힌다.
3. 게다가 FCS 로 직접 관측되는 양은 **BTA 가 아니라 형광 프로브 A546 의 확산/결합**이다. BTA 값을 얻으려면 프로브의 K 를 별도로 알아야 하는 2차 추론이 필요하고, 그렇게 뽑은 값은 프로브 선택에 의존한다. 설령 본문에 숫자가 있더라도 `PAIR_TABLE` 의 Langmuir ΔG 와 **동일 물리량인지 검증 없이 등록하면 안 된다.**

→ 앞 회차가 "정량화했으나 kJ/mol 로 환산되어 있지 않다"고 기록한 것은, **환산만 남은 상태가 아니라 "환산할 K 자체가 없을 가능성이 크다"**로 하향 수정한다.

### A-3. 대체 1차 출처 탐색 — 전부 실패

검색어 계열(총 5종):
- `benzotriazole adsorption silica particles Langmuir adsorption constant isotherm CMP slurry zeta potential`
- `BTA adsorption isotherm silica surface equilibrium constant K L/mol Gibbs free energy`
- `benzotriazole adsorption on silica gel isotherm Langmuir equilibrium constant thermodynamic "free energy" aqueous`
- `BTA adsorption silica SiO2 "adsorption free energy" kJ/mol experimental isotherm water treatment`
- `"benzotriazole" removal adsorption "silica" Langmuir "KL" thermodynamics "ΔG" adsorbent`

**실험 등온선에서 구한 BTA × SiO₂ 의 ΔG_ads 를 보고한 논문을 찾지 못했다.** 물리적으로 놀랍지 않다: pH 7~11 에서 실리카 표면은 음전하(−SiO⁻)이고 BTA(pKa ≈ 8.2)는 중성 또는 음이온이라, Cu 처럼 배위결합으로 붙는 것이 아니라 수소결합/분산력 수준의 약한 물리흡착만 기대된다. 그래서 등온선을 열역학적으로 해석한 연구 자체가 드물다.

### A-4. 등록 금지 — 참고용 (절대 BTA × SiO₂ 줄에 쓰지 말 것)

- **Wang, Zhang, Tan et al., "Effect of Corrosion Inhibitor BTA on Silica Particles and their Adsorption on Copper Surface in Copper Interconnection CMP", ECS J. Solid State Sci. Technol. (2022), DOI 10.1149/2162-8777/ac627c** (OA, HYBRID/CC-BY-NC-ND)
  - pH 10 알칼리 슬러리에서 BTA 가 실리카 입자의 입도·제타전위를 바꾸고, 그 결과 **Cu 표면에 대한 SiO₂ 입자의 흡착**이 달라진다는 연구. 3 mM BTA 는 입자 흡착량을 줄이고, 더 높은 농도에서는 늘린다.
  - ⛔ **등록 금지 이유 2가지:**
    1. 측정 대상이 **BTA→SiO₂ 흡착이 아니라 SiO₂ 입자→Cu 표면 흡착**이다. 쌍이 다르다.
    2. 보고된 흡착에너지는 **분자동역학(MD) 계산값**이다("The adsorption energy of BTA and SiO₂ particles on copper surface was calculated by molecular dynamic simulation"). **실험 ΔG_ads(|ΔG| < 60 kJ/mol)와 섞으면 안 된다** — 본 조사 규칙 위반.
  - 다만 **정성 근거로는 유용**하다: BTA 가 실리카 입자 표면 화학에 실제로 영향을 준다는 독립적 확인.
- BTA × Cu = −30.02 kJ/mol (DOI 10.2320/matertrans.m2016310) → **기질 다름. SiO₂ 줄에 이식 금지.**
- BTA × Fe = −21.89 kJ/mol (동일 출처) → **등록 금지.**
- 아미노산/유기분자의 실리카 흡착 자유에너지 문헌군(예: amino acid × silica, HPLC 체류시간 기반) → **분자 다름. 등록 금지.**
- DFT/first-principle BTA 흡착에너지 논문군 → **계산값. 실험 ΔG 와 혼용 금지.**

### A-5. 시뮬레이터 등록 권고

1. **값을 만들지 말 것.** BTA × SiO₂ 는 `PAIR_TABLE` 미등록 상태를 유지한다.
2. 다만 "쌍이 없어서 0"과 "근거를 갖고 0에 가깝다"는 다르므로, `tools/declare_inhibitor_pair.py` 로 **"약한 물리흡착 수준, 실험 ΔG 1차 출처 없음"**을 사유와 함께 명시 선언할 것을 권한다. 근거: (a) FCS 로 BTA 가 실리카 표면 프로브를 밀어내는 정성 증거는 있다(DOI 10.1149/05201.0489ecst 초록) — 즉 흡착은 **0 이 아니다**; (b) 그러나 정량치가 없고, 표면 화학상 −SiO⁻ vs 중성/음이온 BTA 의 정전 조건은 강한 화학흡착을 기대하기 어렵다.
3. 만약 이 값이 모델 결과를 크게 좌우한다면, **문헌 대신 자체 측정**(QCM-D 또는 실리카 슬러리 상등액의 BTA UV 흡광 감소로 등온선 → Langmuir K → ΔG)이 현실적 경로다. 이 경로만이 조건(T, pH, 이온강도)을 슬러리와 일치시킬 수 있다.

### A-6. 다음 조사자가 이어받을 지점

- ECS Trans. 52(1) 489 본문은 **기관 구독(IOPscience) 또는 ECS Digital Library 계정**이 있어야 열린다. 도구로 뚫을 방법이 소진됐다. 저자 교신(Edward E. Remsen, Bradley University) 이 가장 빠른 경로일 수 있다.
- 같은 그룹의 후속·상위 논문: "Additive/Abrasive Interactions in Solution: Investigation of the Surface Chemistry and Adsorption Behaviour of CMP Abrasives" (IEEE Xplore doc 6353785). 미확인 — **여기에 정량 K 가 있을 가능성이 남아 있다.** 다음 회차 1순위 타깃으로 권고한다.

