# 억제제 × 기질 흡착 자유에너지 (ΔG_ads) 문헌 조사

대상: CMP 슬러리 억제제(corrosion inhibitor / additive) × 금속·산화막 기질
목적: `sim/inhibitor_pairs.py` 의 `PAIR_TABLE` 에 (억제제, 기질) 쌍 키로 등록
조사일: 2026-09-19 / 도구: 내장 web_search + PDF 원문 확보

## 결과 요약

| # | 쌍 | 상태 | ΔG_ads |
|---|---|---|---|
| 1 | benzenesulfonic acid × Cu | **미확보** (메커니즘상 부재 가능성 높음) | — |
| 2 | BTA × Ta/TaN | **미확보** (메커니즘상 부재 — 아래 해석 참조) | — |
| 3 | malonic acid × Cu | ✅ **확보** | −47.7 kJ/mol (산화 Cu) / −38.3 kJ/mol (환원 Cu) |
| 4 | malonic acid × W | **미확보** (작용 메커니즘이 표면흡착이 아님) | — |
| 5 | benzenesulfonic acid × SiO₂ | **미확보** (정전 반발 — 흡착 자체가 불리) | — |
| 6 | benzenesulfonic acid × Ta | **미확보** | — |
| 7 | BTA × SiO₂ | **미확보** (정성 흡착 증거는 있으나 ΔG 정량치 없음) | — |

**확보 쌍: 1 / 7**

## 규칙 준수 확인
- 다른 기질 값 이식 **없음**
- 인접 분자(succinate, ethylmalonate, TTA, SDBS/DBSA, BTC 등) 값 이식 **없음** — 참고 기재 시 `등록 금지 — 참고용` 표시함
- 미확보 항목은 검색 이력 + 미확보 사유(메커니즘상 부재 vs 미측정)를 각각 기재함

---

## 1) benzenesulfonic acid (벤젠설폰산 / 그 염) × Cu  ❌ 미확보

- **쌍**: benzenesulfonic acid (C₆H₅SO₃H) / sodium benzenesulfonate (C₆H₅SO₃Na, CAS 515-42-4) × Cu
- **ΔG_ads**: **미확보**
- **confidence**: —

### 미확보 사유 (해석)

검색어 계열(총 6가지 조합): `"benzenesulfonic acid" copper adsorption free energy Langmuir corrosion inhibitor kJ/mol`,
`"sodium benzenesulfonate" adsorption metal surface Gibbs free energy inhibitor QCM XPS`,
`"benzenesulfonate" adsorption copper surface Gibbs free energy kJ/mol inhibitor sulfonic acid aromatic`,
`"sulfonic acid" OR "sulfonate" copper corrosion inhibitor "delta G" adsorption Langmuir "kJ mol" benzene ring aryl`,
`"benzenesulfonic acid" copper corrosion inhibitor electrochemical study adsorption`,
`CMP slurry patent "benzenesulfonic acid" additive copper polishing composition`.

**결론: 아무도 안 잰 것이 아니라, 이 분자가 Cu 표면에 이 메커니즘으로 작용하지 않기 때문일 가능성이 높다.** 근거 3가지:

1. **설포네이트는 배위력이 거의 없는 음이온이다.** 술폰산은 pKa ≈ −2.8 로 전 pH 영역에서 완전 해리되어 −SO₃⁻ 로 존재하고, 음전하가 3개 산소에 완전 비편재화되어 Cu(I)/Cu(II) 에 대한 유효 donor 능력이 매우 낮다. 무기화학에서 triflate/tosylate 계열이 "non-coordinating anion" 으로 분류되는 것과 같은 이유다. BTA(triazole N 고립전자쌍)나 malonate(인접 2개 카르복실의 킬레이트)와 달리 **표면 착물/부동태막을 만들 구조적 수단이 없다.**
2. **문헌에서 설포네이트가 Cu 억제제로 나올 때는 예외 없이 긴 알킬 사슬이 붙은 계면활성제다.** SDBS(sodium dodecylbenzenesulfonate), DBSA(dodecylbenzene sulfonic acid), SDS 등. 이들의 억제 성능은 **C12 소수성 꼬리의 소수성 상호작용/미셀 형성**에서 나오며, 벤젠고리+설포네이트 머리 자체가 아니다. 즉 이 문헌들의 값은 benzenesulfonic acid 줄에 **쓸 수 없다.**
3. **CMP 슬러리 특허에서 벤젠설폰산은 억제제 목록이 아니라 pH 조절제/전해질/계면활성제 대이온(counterion) 항목에 등장한다.** 억제제 기능이 청구항에 기재된 예를 찾지 못했다.

### 등록 금지 — 참고용 (절대 이 줄에 쓰지 말 것)
- SDS(sodium dodecyl sulphate) × Cu: ΔG_ads ≈ **−75.06 kJ/mol** (Langmuir, 30 °C, HNO₃ 산성, gasometric). 출처: Scirp *Engineering* 2018, paperid=89525. → **분자 골격 자체가 다름(황산에스터 + C12 사슬). 등록 금지.**
- SDBS × Cu (H₂SO₄ 중, 2-MBI 와의 시너지 연구): DOI 10.1007/s10800-008-9606-3. ΔG 값 미확인. → **등록 금지 — 참고용.**

### 다음 단계 제안 (총괄 판단용)
- 만약 `sim/` 에서 benzenesulfonic acid 가 **억제제**로 등록되어야 하는 게 아니라 **pH/이온강도 항**으로 다뤄져야 하는 것이라면, PAIR_TABLE 등록이 아니라 모델 구조 자체를 재검토해야 한다. 3개 검증계열이 이 쌍에서 막혀 있다면, 그 슬러리의 실제 억제 주체가 다른 성분(예: 함께 든 아졸계, 또는 설포네이트 계면활성제의 알킬 사슬)이 아닌지 조성표를 먼저 확인할 것을 권한다.
- 대안 1차 출처 경로: sci-hub 로 *J. Electroanal. Chem.* / *Corros. Sci.* 의 "specific adsorption of anions on Cu electrode" 계열(설페이트/설포네이트 특이흡착, 전기모세관/차분용량 측정)을 뒤지면 ΔG 대신 **특이흡착 Gibbs 에너지**가 나올 수 있으나, 이는 억제 메커니즘과 다른 물리량이므로 그대로 이식하면 안 된다.

---

## 2) BTA (benzotriazole) × Ta / TaN  ❌ 미확보

- **쌍**: 1,2,3-benzotriazole (C₆H₅N₃) × Ta / TaN (실제 표면은 Ta₂O₅)
- **ΔG_ads**: **미확보**
- **confidence**: —

### 미확보 사유 (해석)

검색어 계열: `benzotriazole tantalum TaN adsorption free energy inhibitor CMP`,
`benzotriazole BTA tantalum nitride TaN barrier CMP adsorption free energy electrochemical`,
`benzotriazole TaN tantalum adsorption XPS inhibition barrier CMP does BTA adsorb on tantalum`,
`tantalum Ta corrosion inhibitor adsorption free energy Langmuir isotherm kJ/mol electrochemical`,
`Controllable adjustment Ta Cu material removal rate TSV CMP inhibitor BTA adsorption energy tantalum`.

**결론: 미측정이 아니라, BTA 가 Ta 에는 그 메커니즘으로 작용하지 않기 때문이다.** 이것이 값보다 중요한 정보다.

1. **BTA 억제의 물리적 실체는 Cu(I)–BTA 중합 착물막**이다. 표면 금속 양이온이 triazole N 과 배위해 [Cu(I)BTA]ₙ 사슬을 만드는 것이 부동태의 본질이다. Ta 표면은 **Ta₂O₅(valve metal oxide)** 로 덮여 있고 Ta⁵⁺ 는 d⁰ 로 lone-pair donor 와 π-back donation 을 할 수 없으며 수용액에서 가용성 양이온을 거의 내지 않는다. **착물막을 만들 상대가 없다.**
2. **barrier CMP 문헌이 이를 간접 확증한다.** BTA 가 배리어 CMP 슬러리에 들어가는 이유는 **Ta 를 억제하기 위해서가 아니라, 노출된 Cu 를 선택적으로 억제해 Ta/Cu 선택비를 올리기 위해서**다. 즉 BTA 가 Ta 에 거의 붙지 않는다는 사실 자체가 공정 설계의 전제다. (예: Ta/Cu 선택비 1.02:1 → 1.79:1 조절 연구, DOI 10.1007/s10853-024-10133-5 — 여기서도 Ta 측 MRR 조절은 GH/TT-LYK 및 연마입자 표면전하로 하지 BTA 로 하지 않는다.)
3. 같은 이유로 BTA 는 Cu 에 대해 −30.02 kJ/mol 인 반면 d-오비탈 구조가 다른 Fe(steel) 에 대해서는 −21.89 kJ/mol 로 급감한다(기존 등록 출처 DOI 10.2320/matertrans.m2016310 의 관찰). **금속의 d-오비탈 구조가 BTA 흡착 안정성을 지배한다**는 이 논문의 결론은 d⁰ 인 Ta₂O₅ 에서 BTA 흡착이 더욱 약할 것을 강하게 시사한다.

### 시뮬레이터 등록 권고
- 값을 지어내지 말고, 이 쌍은 **"억제 무시 가능(ΔG_ads → 0, 물리흡착 수준)"** 으로 **명시적으로 선언**할 것을 권한다. PAIR_TABLE 에 쌍이 **없어서** 0 이 되는 것과, **근거를 갖고** 0 으로 선언하는 것은 다르다. 후자는 `tools/declare_inhibitor_pair.py` 로 사유와 함께 등록하면 "억제 0" 이 모델 결함이 아니라 물리적 사실임을 기록에 남길 수 있다.
- 다만 Ta₂O₅ 표면 하이드록실(Ta–OH)과 BTA 의 수소결합에 의한 **약한 물리흡착(−5 ~ −20 kJ/mol 범위)** 가능성은 배제 못 한다. 이 범위는 **estimated 이며 1차 출처 없음** — 등록 시 반드시 그렇게 표시할 것.

### 등록 금지 — 참고용
- BTA × Fe(steel): −21.89 kJ/mol (DOI 10.2320/matertrans.m2016310). → **Ta 줄에 쓰지 말 것.** 과거 5,700배 오차의 원인 유형.
- BTA × Co: DFT/MC 흡착에너지 다수 존재(DOI 10.1016/j.colsurfa.2020.124486 계열). → **기질 다름, 등록 금지.**
- TTA(메틸벤조트리아졸) 값 일체. → **인접 분자, 등록 금지.**

---

## 3) malonic acid (말론산 / 말론산나트륨) × Cu  ✅ 확보

- **쌍**: sodium malonate (말론산나트륨, malonate anion ⁻OOC–CH₂–COO⁻) × Cu
- **ΔG_ads**:
  - **산화된 Cu 표면 (oxidized, E = 0.0 V vs SHE — 즉 Cu₂O/CuO 로 덮인 표면): ΔG⁰_a,max = −47.7 kJ/mol**  ← CMP 슬러리(산화제 존재, 산화막 위) 조건에 가장 가까움. **1순위 등록 권장값.**
    - 같은 표면 하한값 ΔG⁰_a,min = −43.6 kJ/mol, Temkin 불균일 인자 f = 1.65
    - B_max = 0.43×10⁷ L/mol, B_min = 0.08×10⁷ L/mol
  - **환원된(산화막 없는) Cu 표면 (E = −0.60 V vs SHE): ΔG⁰_a,max = −38.3 kJ/mol**
    - ΔG⁰_a,min = −31.8 kJ/mol, f = 2.62, B_max = 9.49×10⁴ L/mol, B_min = 6.85×10³ L/mol
- **측정법**: *in situ* 엘립소메트리 (ellipsometry, Rudolph Research 2000, 위상차각 Δ 측정, 정확도 ±0.05°) + 정전위 제어 전극(potentiostatic, SHE 기준) → Drude 식으로 피복률 θ 환산 → **full Temkin 등온흡착식** 적합. 보조 검증: 양극 분극곡선(anodic polarization, 0.2 mV/s), 7일 침지 중량감소 부식시험, 탈착(desorption) 실험.
- **출처**: M.O. Agafonkina, I.A. Kuznetsov, N.P. Andreeva, Yu.I. Kuznetsov, "Copper protection with sodium salts of lower dicarboxylic acids in neutral aqueous solution", *International Journal of Corrosion and Scale Inhibition*, **2020**, vol. 9, no. 3, pp. 1000–1013.
  **DOI: 10.17675/2305-6894-2020-9-3-13** (open access, PDF 원문 확보·검증 완료)
- **온도/전해질/pH**: 실온 **22 ± 2 °C**. **붕산염 완충액(borate buffer), pH 7.40**. 엘립소메트리 등온선은 10⁻⁸–10⁻¹⁰ M 초희석 영역에서 취득. 분극·부식시험은 여기에 **0.01 M NaCl** 추가. malonic acid 는 NaOH 로 중화해 나트륨염으로 사용(CAS 141-82-2).
- **다층 흡착 여부**: **Langmuir 절편 유래가 아님 — full Temkin 등온식 유래.**
  Temkin 식은 표면 에너지 불균일성(인자 f)을 포함하므로 결과가 단일값이 아니라 ΔG_a,max(최고에너지 사이트) ~ ΔG_a,min(최저에너지 사이트) **범위**로 나온다. 저자는 특정 농도 이상에서 등온선이 plateau 에 도달하는 것을 **단분자층(monolayer) 피복 완료**로 해석했고, 엘립소메트리로 환산한 층 두께(산화표면 0.23 nm, 환원표면 0.11 nm)가 malonate 분자 길이보다 **작아** **평면 배향(planar orientation)의 단층**임을 독립 확인했다.
  → **따라서 이 값은 명백히 첫층(ΔG1) 값이며, 다층 기여를 포함하지 않는다.**
- **흡착 성격**: 용액을 순수 완충액으로 교체해도 탈착이 일어나지 않고 오히려 (−δΔ)가 120분간 계속 증가 → **화학흡착(chemisorption)** 으로 확정. |ΔG| > 40 kJ/mol 기준과도 일치(산화표면 기준).
- **confidence**: **literature**

### 등록 시 주의사항
1. **산화막 유무로 9.4 kJ/mol 차이**(−47.7 vs −38.3). CMP 슬러리는 산화제(H₂O₂ 등)를 포함해 Cu 표면이 산화 상태이므로 **−47.7 kJ/mol 이 물리적으로 맞다.** 환원 표면 값은 무산화제 조건(예: 순수 기계연마 구간)에서만 의미가 있다.
2. **조건 외삽 불확실도**: pH 7.40 붕산염 완충 + 0.01 M NaCl 이며, 실제 Cu CMP 슬러리(pH 4–10, 글리신/시트르산 등 착화제 + H₂O₂ 공존)와 다르다. 착화제는 malonate 와 표면 사이트를 경쟁하므로 유효 억제는 이 값보다 **약할** 수 있다. 등록 시 불확실도 항에 반영할 것.
3. **Temkin 값을 Langmuir 기반 모델에 그대로 넣을 때 주의.** 기존 등록된 bta×cu (−30.02 kJ/mol) 는 Langmuir 절편 유래이고, 이 값은 Temkin 유래다. PAIR_TABLE 이 등온식 종류를 구분하지 않는다면 **isotherm 종류 필드를 추가**하는 것이 맞다. Temkin ΔG_a,max 는 "가장 강한 사이트" 값이므로 Langmuir 단일 ΔG 보다 체계적으로 더 음수로 나오는 경향이 있다.
4. **1차 출처 계보**: 산화 Cu 위 malonate 흡착의 최초 보고는 같은 저자군의 Andreeva et al., *Korroz.: mater., zashch.* 2020, no. 10 (러시아어, 미입수)이다. 위 IJCSI 2020 논문이 그 값을 수치·표와 함께 자기 데이터로 재수록하고 있으므로 1차 출처로 사용 가능하다.

### 등록 금지 — 참고용 (같은 논문, 같은 기질, 다른 분자)
같은 표 1(산화 Cu, E = 0.0 V) 의 인접 분자 값:
- **sodium succinate × Cu: −77.4 kJ/mol** → **등록 금지 — 참고용.** CH₂ 하나 차이인데 malonate 와 **30 kJ/mol** 차이가 난다. 이식하면 큰 오차.
- **sodium ethylmalonate × Cu: −69.4 kJ/mol** → **등록 금지 — 참고용.** 에틸 치환기 하나 차이로 malonate 대비 21.7 kJ/mol 차이.
- 참고로 같은 저자군의 다른 논문(DOI 10.17675/2305-6894-2021-10-4-14)에서 succinate × MNZh5-1 합금 = −89.3 kJ/mol → **기질도 분자도 다름, 등록 금지.**

> 이 세 값의 편차 폭(−47.7 / −69.4 / −77.4) 자체가 **"인접 분자 값 이식 금지" 규칙의 정량적 근거**다. 작용기 하나 차이가 ΔG 를 30 kJ/mol 움직이고, 이는 K_ads 로 환산하면 상온에서 약 **10⁵ 배** 차이다.

---

## 4) malonic acid (말론산) × W (텅스텐)  ❌ 미확보

- **쌍**: malonic acid / malonate × W (실제 표면은 WO₃ / WO₄²⁻)
- **ΔG_ads**: **미확보**
- **confidence**: —

### 미확보 사유 (해석)

검색어 계열: `malonic acid tungsten W CMP adsorption Gibbs free energy inhibitor EIS Langmuir`,
`malonic acid tungsten corrosion inhibition adsorption free energy Langmuir "kJ/mol" W surface`,
`malonic acid tungsten CMP inhibitor adsorption isotherm potentiodynamic polarization Gibbs free energy`.

**결론: 아무도 안 잰 쪽에 가깝지만, 더 정확히는 W CMP 에서 말론산의 역할이 애초에 "W 표면 흡착 억제제"가 아니기 때문이다.** 확인된 1차 문헌 2편이 모두 다른 메커니즘을 보고한다:

1. **Zhang & Raghavan, "Use of Malonic Acid in Chemical-Mechanical Polishing (CMP) of Tungsten", *MRS Proc.* 477, 115 (1997), DOI 10.1557/PROC-477-115.**
   말론산의 역할은 **알루미나 연마입자와 W 표면의 제타전위를 동시에 음으로 만들어 정전 반발로 입자 오염(particulate contamination)을 줄이는 것**이다. 즉 말론산은 **연마입자 표면**에 작용(alumina surface 가 malonate 음이온을 uptake)하며, **W 금속 표면에 부동태막을 만드는 억제제로 기술되지 않는다.** 논문은 electrokinetic(제타전위) + 흡착량 측정을 했을 뿐 ΔG_ads 를 산출하지 않았다.
2. **"The effect of dicarboxylic acid stabilizers on tungsten CMP", *Colloids Surf. A* (2024), DOI 10.1016/j.colsurfa.2024.135... (S0927775724012974).**
   옥살산/말론산/숙신산의 역할을 **H₂O₂ 안정화제(용액상 라디칼 분해 억제)** 로 규정한다. 다시 **용액상 화학**이지 W 표면 흡착이 아니다.

→ 따라서 **PAIR_TABLE 에 malonic×W 를 억제제 쌍으로 등록하는 것 자체가 물리적으로 부적절할 수 있다.** 말론산이 W MRR 에 주는 영향은 (a) H₂O₂ 안정화를 통한 산화제 유효농도 변화, (b) 연마입자–W 정전 상호작용 변화로 들어가야 하며, 흡착 억제항이 아니다. 이 구조적 판단을 총괄에 올린다.

### 등록 금지 — 참고용
- BTC(benzotriazole-5-carboxylic acid) × W: "moderate value of Gibbs free energy change of adsorption" 존재가 보고됨. 출처: Park, Ryu, Kim, Yerriboina et al., "The Adsorption and Removal of Corrosion Inhibitors During Metal CMP", *2020 CSTIC*, **DOI 10.1109/CSTIC49141.2020.9282467**. → **분자가 다름(BTA 유도체), 말론산 줄에 절대 쓰지 말 것.** 수치도 초록에서 확인 불가(본문 유료, 미입수).
- benzethonium chloride × W: DOI 10.1016/j.jcis.2023.04.012 (중성·알칼리 매질 W 억제제). → **분자 다름, 등록 금지.** 단 W 억제제 쌍이 별도로 필요하면 이 논문이 유력한 1차 후보다.
- picolinic acid × WO₃ 배위착물: DOI 10.3390/app12031227. → **분자 다름, 등록 금지.** W 표면에 실제로 작용하는 배위형 첨가제의 사례로는 참고 가치 있음.

---

## 5) benzenesulfonic acid × SiO₂ (oxide)  ❌ 미확보

- **ΔG_ads**: **미확보**
- **confidence**: —

### 미확보 사유 (해석)

검색어: `benzenesulfonic acid SiO2 silica adsorption free energy silanol aromatic sulfonate isotherm kJ/mol`,
`benzene sulfonic acid silica surface adsorption enthalpy DFT silanol hydrogen bond kJ/mol amorphous SiO2`.

**결론: 메커니즘상 흡착이 불리해서 아무도 억제제로 재지 않았다.**
1. **정전 반발.** 실리카의 등전점은 pH ≈ 2–3 이므로 CMP 실사용 전 pH 영역(4–11)에서 SiO₂ 표면은 **음전하(≡Si–O⁻)** 다. 벤젠설포네이트도 전 pH 에서 **음이온(−SO₃⁻)** 이다. 동부호 전하끼리는 반발하며, 이는 실제로 말론산이 W CMP 에서 "알루미나·W 를 동시에 음전하로 만들어 입자 오염을 줄인다"고 쓰이는 것과 같은 원리다 — 즉 **설포네이트의 실리카에 대한 기능은 흡착이 아니라 분산 안정화(반발)** 쪽이다.
2. 실리카 표면 유기물 흡착 문헌은 **실라놀(Si–OH) 과의 수소결합**을 지배 기구로 본다. 설포네이트는 H-bond **받개(acceptor)** 는 될 수 있으나 강한 donor 가 없고, 음전하 반발이 이를 상쇄한다.
3. 검색 결과 실리카 위 방향족 흡착 에너지는 대부분 **기상/비수계(DFT·IGC·마이크로칼로리미터)** 값이며 수용액 CMP 조건과 직접 비교 불가.

### 등록 금지 — 참고용 (수치 이식 절대 금지 — 기상/비수계 값임)
- benzene × 하이드록실화 실리카 클러스터: **−30.6 kJ/mol**, 무(無)실라놀 실록산 클러스터: −1.8 kJ/mol (DFT B3LYP/6-31G(d), 기상). 출처: Frontiers in Chemistry 2023, DOI 10.3389/fchem.2023.1084046.
  → **벤젠 ≠ 벤젠설폰산이며, 기상 DFT ≠ 수용액 ΔG_ads. 등록 금지 — 참고용.** 다만 "실라놀 있으면 방향족 고리 π–HO 상호작용으로 −30 kJ/mol 수준까지 간다"는 **상한 감각(order of magnitude)** 은 제공한다.
- toluene × 하이드록실화 실리카: −23.0 kJ/mol (동일 출처). → **등록 금지 — 참고용.**

---

## 6) benzenesulfonic acid × Ta  ❌ 미확보

- **ΔG_ads**: **미확보**
- **confidence**: —

### 미확보 사유 (해석)

전용 1차 문헌 0건. 위 1)항의 "설포네이트는 배위 불가 음이온" 논거와 5)항의 "정전 반발" 논거가 **동시에** 적용되는 조합이다.

- Ta 표면 = Ta₂O₅, 등전점 pH ≈ 2.7–3.0 → CMP 영역에서 **음전하**. 설포네이트도 음이온 → **정전 반발**.
- Ta⁵⁺ 는 d⁰ → 설포네이트 산소의 약한 lone pair 와도 안정한 표면 착물을 못 만든다.
- 문헌 부재의 원인은 **"아무도 안 쟀다"가 아니라 "억제제 후보로 고려된 적이 없다"** 로 판단한다. 배리어 CMP 문헌에서 Ta MRR 조절은 연마입자 표면전하(양전하 실리카), 착화제(GH, DTPA-5Na), 또는 산화제로 이루어지며 설포네이트계는 등장하지 않는다.

**권고**: 2)항과 동일하게 **"억제 무시 가능"을 근거와 함께 명시 선언**. 값을 만들어 넣지 말 것.

---

## 7) BTA (benzotriazole) × SiO₂ (oxide)  ❌ 미확보 (정성 증거는 있음)

- **ΔG_ads**: **미확보 (정량치 없음)**
- **confidence**: —

### 미확보 사유 (해석)

검색어: `benzotriazole silica SiO2 adsorption free energy isotherm CMP slurry abrasive`.

**여기는 앞의 경우들과 성격이 다르다. 흡착은 실제로 일어나며 측정도 되었지만, 아무도 그것을 ΔG_ads (kJ/mol) 로 환산해 보고하지 않았다.** 확인된 1차 문헌 2편:

1. **"(Invited) Surface Adsorption of CMP Slurry Additives on Abrasive Particles", *ECS Transactions* **52**(1), 489 (2013), DOI 10.1149/05201.0489ecst.**
   형광상관분광법(FCS)으로 콜로이드 실리카 입자 표면에서 BTA 가 형광 프로브(Alexa Fluor 546)를 **경쟁적으로 치환(displacement)** 함을 확인 → **BTA 는 실리카에 실제로 흡착한다.** 그러나 결합의 정량 지표를 경쟁 치환 곡선으로만 제시하고 **ΔG_ads 로 환산하지 않았다.** (원문 유료, 초록 수준까지만 확인)
2. **"Effect of Corrosion Inhibitor BTA on Silica Particles and their Adsorption on Copper Surface", *ECS J. Solid State Sci. Technol.* (2022), DOI 10.1149/2162-8777/ac627c.**
   pH 10 에서 BTA 가 실리카 입자의 제타전위·입도를 바꿔 응집/분산을 좌우함을 SEM·XPS 로 보고. MD 시뮬레이션 흡착에너지는 계산했으나 **모두 Cu(111) 표면 기준**이다(SiO₂ 분자 × Cu = −8.37 kcal/mol, BTA × Cu = −87.9 kcal/mol). **BTA × SiO₂ 표면 자체의 흡착에너지는 계산하지 않았다.**

### ⛔ 오독 주의 (중요)
위 2번 논문의 **"SiO₂ × Cu(111) = −8.37 kcal/mol (≈ −35.0 kJ/mol)"** 는 **실리카 분자가 구리 표면에 흡착하는 값**이다. 이것을 **BTA × SiO₂ 줄에 쓰면 기질도 흡착종도 뒤바뀐 이중 오류**가 된다. 반드시 피할 것. 마찬가지로 같은 표의 **BTA × Cu(111) = −87.9 kcal/mol (≈ −368 kJ/mol, MD 기준)** 은 기존 등록된 실험값 −30.02 kJ/mol 과 한 자릿수 이상 다르다 — **MD/DFT 흡착에너지(E_ads)와 실험 흡착 자유에너지(ΔG_ads)는 서로 다른 물리량이며 혼용하면 안 된다.** 이것이 향후 유사 사고의 주요 위험원으로 보인다.

### 다음 단계 제안
- ECS Trans. 52(1) 489 원문을 sci-hub 또는 `tools/find_open_access.py --title "Surface Adsorption of CMP Slurry Additives on Abrasive Particles"` 로 입수하면 FCS 경쟁 결합상수 K 에서 ΔG = −RT ln(55.5·K) 로 환산 가능할 수 있다. **이번 턴 예산 내에서는 미시도.** 가장 회수 가능성이 높은 잔여 쌍이다.

---

## 총괄 보고용 메모

1. **확보 1건**: malonate × Cu (산화표면 −47.7 kJ/mol, Temkin, ΔG1 단층, literature, DOI 10.17675/2305-6894-2020-9-3-13).
2. **최우선 쌍(benzenesulfonic × Cu)은 값이 없는 것이 아니라, 그 분자가 Cu 억제제가 아닐 가능성이 높다.** 3개 검증계열이 이 쌍에서 막혀 있다면 **PAIR_TABLE 보강이 아니라 해당 슬러리의 억제 주체 재식별**이 먼저다. 이것이 이번 조사의 가장 중요한 산출물이다.
3. **BTA × Ta, benzenesulfonic × Ta 는 "미등록으로 방치"가 아니라 "억제 무시 가능"을 근거와 함께 명시 선언**할 것을 권한다. 그래야 MRR 과대예측이 모델 결함인지 물리적 사실인지 구분된다.
4. **malonic × W 는 쌍 등록 자체가 구조적으로 부적절**하다 — 말론산의 W CMP 내 역할은 H₂O₂ 안정화 + 연마입자 제타전위 조절이며 W 표면 흡착이 아니다. 모델에서 다른 항으로 옮겨야 한다.
5. **회수 가능성이 가장 높은 잔여 쌍은 BTA × SiO₂** (ECS Trans. 52(1) 489 의 FCS 결합상수 → ΔG 환산). 다음 턴 우선순위로 권장.
6. **신규 위험 발견**: MD/DFT 흡착에너지 E_ads 와 실험 ΔG_ads 혼용. 같은 BTA×Cu 가 문헌에 따라 −30 kJ/mol(실험 Langmuir) 과 −368 kJ/mol(MD) 로 공존한다. PAIR_TABLE 에 **측정법 구분 필드**가 없다면 다음 5,700배 사고의 유력 후보다.
