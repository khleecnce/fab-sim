<!-- V2-SECTION: R2-slurry | 분배완료 2026-09-08 | 근거: ceria, chemistry, particle-wafer, redox, selectivity | 정본: ARCHITECTURE-V2.md §3 -->
# 세리아(CeO₂) 슬러리 — Ce³⁺/Ce⁴⁺ 산화환원 메커니즘과 oxide:nitride 선택비 제어

> 에이전트: slurry-chemist Lv3-1 | 작성일: 2026-09-06
> [[slurry-components-overview]] [[particle-wafer-interaction-mechanical-chemical-balance]] [[surface-chemistry-cu-w-pourbaix-passivation]] [[colloid-zeta-dlvo-slurry-stability]] [[post-cmp-metallic-contamination-sources]]

## 1. 왜 필요한가 — 세리아는 "화학적 이빨(chemical tooth)"을 가진 특수 연마입자
[[slurry-components-overview]] §2에서 세리아를 "단순 마모가 아니라 Si–O–Ce 결합을 만들어 SiO₂를
뜯어내는 화학기계적 입자"로 개요만 잡았다. 이 노트는 그 메커니즘을 심화한다. 실리카·알루미나는
경도·접촉역학([[particle-wafer-interaction-mechanical-chemical-balance]])이 지배하는 **거의 순수 기계**
연마재지만, 세리아는 SiO₂와 **실제 화학결합**을 형성해 같은 압력·같은 입경에서도 산화막 제거율이
현저히 높다(Cook, "Chemical processes in glass polishing," *J. Non-Cryst. Solids* 120, 152–171, 1990
— 유리연마 화학모델의 원류; 원문 유료·**1차 미확보**·초록/2차 인용, Crossref 실존확인). 이 화학친화가
STI(shallow trench isolation)에서 **SiO₂는 빠르게, Si₃N₄(정지층)는 느리게** 깎는 높은 선택비의 물리적
근거다. 핵심 명제:
- 세리아 표면의 **Ce³⁺ 자리가 활성점**이다 — Ce³⁺가 SiO₂ 표면과 Si–O–Ce(=Ce–O–Si) 다리결합을 만든다.
- 이 결합은 **물리흡착이 아니라 화학흡착**(§3에서 DFT 흡착에너지로 정량)이라, 슬라이딩 시 세리아가
  실리카 표면에서 Si(OH)₄ 단위를 **뜯어낸다**("chemical tooth").
- Ce³⁺는 산소공공(oxygen vacancy)과 짝을 이루며(§2), H₂O₂·계면활성제·도핑으로 Ce³⁺/Ce⁴⁺ 비율을
  조절하면 제거율이 바뀐다.
- **선택비 제어**(§5)는 아미노산·계면활성제가 nitride 표면 또는 세리아 활성점을 선택적으로 막아서 이룬다.

## 2. Ce³⁺/Ce⁴⁺ 산화환원 — 산소공공과 전하균형
세리아는 형석(fluorite) 구조 CeO₂지만 표면·나노입자에서 산소를 쉽게 내놓아 **CeO₂₋ₓ**로 비화학량론이
된다. 산소(O²⁻) 하나가 빠지면 남은 2개 전자가 이웃한 **Ce⁴⁺ 둘을 Ce³⁺로 환원**한다. 즉 산소공공 1개당
Ce³⁺ 2개 — 전하중립으로부터 **Ce당 Ce³⁺ 분율 f = 2x**(§7 verify (A)에서 자기일관 검증). 나노입자일수록
비표면적↑ → 표면 산소공공↑ → Ce³⁺ 분율↑이라, 세리아 CMP에서 **작은/환원된 입자가 화학적으로 더
활성**이다.
- **활성점 = Ce³⁺**: Ce³⁺가 SiO₂와 Si–O–Ce를 형성해 제거를 개시한다(Netzband & Dunn 2020, ECS
  J. Solid State Sci. Technol. 9, 044002, doi:10.1149/2162-8777/ab8393, **오픈액세스 CC-BY**; 후속
  "The Role of Ce³⁺ vs Ce⁴⁺ during Polishing of SiO₂/Si₃N₄" 계열과 정합).
- **촉매 사이클(catalase-mimetic)**: 세리아는 H₂O₂를 카탈라아제처럼 분해한다 — Ce⁴⁺→Ce³⁺(H₂O₂가 환원),
  이어 Ce³⁺→Ce⁴⁺(재산화)로 입자가 원상복귀. 이 **재생 가능한 산화환원 짝** 덕에 세리아는 소모되지 않고
  화학작용을 지속한다. Netzband & Dunn은 H₂O₂ 0.5 wt%에서 표면 Ce³⁺% 최대 → 산화막 MRR을 상용
  대비 **5.5배**로 끌어올리고 oxide:nitride 선택비를 1:1→**3:1**로 개선했다(§7 verify (E)).
- **첨가제로 Ce³⁺/Ce⁴⁺ 제어**: 양이온 계면활성제는 흡착-산화 시너지로 Ce³⁺→Ce⁴⁺ 전환을 촉진하고,
  H₂ 환원 전처리는 Ce³⁺/Ce⁴⁺ 비를 높여 oxide MRR을 개선한다("Improvement of oxide CMP by increasing
  Ce³⁺/Ce⁴⁺ ratio via hydrogen reduction," *Mater. Sci. Semicond. Process.*, 2023, ScienceDirect —
  원문 유료·초록/2차 인용). **어느 방향이 제거에 유리한가는 계·목적에 따라 상충하는 보고가 있어
  미검증** — Ce³⁺ 활성점설(제거 개시)과 Ce⁴⁺ 산화력설이 공존한다.

## 3. Si–O–Ce 화학결합 — "chemical tooth"의 정량 (DFT/반응성 MD)
순수 기계설(세리아도 그냥 딱딱한 입자일 뿐) vs 화학결합설(Si–O–Ce 다리)의 논쟁은 원자수준 계산으로
화학결합설 쪽으로 기울었다. Brugnoli et al., "New Atomistic Insights on the CMP of Silica Glass with
Ceria Nanoparticles," *Langmuir* 39(16), 2023, doi:10.1021/acs.langmuir.3c00304 (**오픈액세스, PMC10116594**):
- **규산(H₄SiO₄) 흡착에너지(DFT)**: 세리아 (111) 면 **−1.15 eV**, (100) 면 **−2.67 eV**. 환산하면
  **−111 ~ −258 kJ/mol**(§7 verify (B)) — 물리흡착(−20 ~ −40 kJ/mol, cf. [[slurry-components-overview]]
  §4 BTA 흡착 경계)보다 훨씬 강한 **화학흡착**. 이것이 Cook "chemical tooth"의 정량 근거다.
- (100) 면이 (111)보다 **2.32배** 강한 결합 — 저배위 Ce(6배위 vs 7배위)가 bidentate로 결합하기 때문.
  즉 입자 형상·노출면(morphology)이 화학활성을 좌우한다(형상제어 연구의 근거).
- **제거 3경로**(반응성 MD): ① Si가 Si–O–Ce로 결합→5배위→슬라이딩이 Si–O–Si를 ~4 ps에 끊음(기계
  개입), ② Ce–OH가 실록산 다리를 직접 양성자화해 즉시 절단(순수 화학), ③ (100)면 vicinal Ce–OH가
  5배위 유도(~20 ps)→절단. 제거단위는 2.5 ns에 약 6개 SiO₄ — **화학이 결합을 약화시키고 기계가
  마무리**하는 [[particle-wafer-interaction-mechanical-chemical-balance]] §4 시너지 원리의 원자판.
- Hoshino et al., "Mechanism of polishing of SiO₂ films by CeO₂ particles," *J. Non-Cryst. Solids* 283,
  129–136, 2001 (원문 유료·**1차 미확보**·2차 인용, Crossref 실존확인)이 이 "Si–O–Ce 직접결합 후
  Si–O 결합 절단" 모델을 실험적으로 처음 제시.

## 4. 세리아-실리카 정전 상호작용 — 등전점(IEP) 차이
화학결합에 더해 **정전인력**이 접촉을 돕는다. [[colloid-zeta-dlvo-slurry-stability]]의 IEP·제타전위를
세리아-실리카 쌍에 적용:
- **세리아 IEP ≈ 6.7–7.8**, **실리카 IEP ≈ 2–3**(2차 인용, 시료·수화상태 의존 **미검증** 범위;
  Cerium Oxide Slurries in CMP 전기영동 연구 및 Cambridge JMR "Effect of pH on ceria–silica
  interactions" doi:10.1557/JMR.2005.0176 계열). 표면전하 부호 = sign(IEP − pH).
- **두 IEP 사이 작동 pH(대략 pH 4–6)**에서 세리아는 (+), 실리카는 (−) → **반대부호 정전인력**이
  입자를 웨이퍼로 끌어당겨 화학결합 형성을 촉진(§7 verify (C)). 실리케이트 용출이 세리아 IEP를
  낮추면 인력이 약해진다(post-CMP 세정에서 EDTA로 Ce–O–Si를 끊어 입자를 떼는 것과 연결 —
  [[post-cmp-metallic-contamination-sources]]의 세리아 잔류오염).
- **주의**: IEP 근처는 제타≈0으로 응집 위험(스크래치↑) → 분산제·계면활성제 입체장벽 필요
  ([[slurry-components-overview]] §6, [[colloid-zeta-dlvo-slurry-stability]] DLVO 장벽).

## 5. oxide : nitride 선택비 제어 — STI CMP의 핵심
STI에서 SiO₂(채움)는 빨리, Si₃N₄(연마정지층)는 느리게 깎아야 한다. 세리아 자체의 SiO₂ 화학친화로
기본 선택비가 높지만, 첨가제로 더 끌어올린다.
- **화학친화 기반 기본 선택비**: Hwang & Kim 2024, *Polymers* 16, 844, doi:10.3390/polym16060844
  (**오픈액세스, PMC10974854**)에서 소포폴리머별 oxide(PETEOS)/nitride MRR로 선택비 **59–80** 재현
  (§7 verify (D)): 예) BYK 5558/83 = 67, G-336 5417/68 = 80. nitride가 oxide의 수십분의 일로 억제됨.
- **nitride 억제 메커니즘**: Si₃N₄는 마찰-트라이볼로지 마모로 표면이 산화막으로 전환되며 깎이는데,
  이 전환을 억제하는 첨가제를 넣으면 nitride MRR이 급감한다(Netzband & Dunn 2020).
- **아미노산 첨가제**: L-프롤린·L-글루탐산 등이 nitride 제거를 억제해 선택비를 높인다. glutamic acid는
  pH 5에서 높은 oxide/nitride 선택비를 준다 — 아미노산이 세리아 활성점(Ce³⁺) 또는 nitride 표면에
  선택 흡착해 특정 표면 반응을 막는다는 모델(IOP ECS "Further Investigation of Slurry Additives for
  Selective Polishing of SiO₂ over Si₃N₄ Using Ceria," doi:10.1149/2.0061511jss; Elsevier "Abrasive and
  additive interactions in high selectivity STI CMP slurries" 계열 — 유료·2차 인용). 아미노산의
  **이온형태(zwitterion/음이온)**가 흡착·선택비를 좌우.
- **계면활성제**: 아크릴산계 첨가제가 nitride 표면에 선택 흡착해 선택비를 **~70**까지 올림. 최적
  조합 예: pH 5 + 라이신 0.02 M + 글루탐산 0.02 M + TEAH 0.003 M → 선택비 35.49(2차 인용, 조건의존
  **미검증**).
- **정리 표(정성)**:

| 손잡이 | 무엇을 바꾸나 | oxide MRR | nitride MRR | 선택비 | 근거 |
|---|---|---|---|---|---|
| H₂O₂/Ce³⁺비 | 활성 Ce³⁺점 농도 | ↑ | (조건) | 1:1→3:1 | Netzband 2020 (OA) |
| 입자 형상/노출면 | (100) 저배위 Ce 비율 | ↑(강결합) | — | (간접) | Brugnoli 2023 (OA) |
| pH (4–6) | 정전인력·아미노산 형태 | ↑ | 조절 | ↑ | JMR 2005 등 |
| 아미노산(Pro·Glu·Lys) | nitride 억제/활성점 차단 | ~유지 | ↓↓ | ↑↑ | ECS/Elsevier (2차) |
| 계면활성제(아크릴산계) | nitride 선택흡착 | ~유지 | ↓ | ~70 | 2차 인용 |
| 소포폴리머 | 분산·거품 | ↑ | ↓ | 59–80 | Hwang 2024 (OA) |

## 6. 순수 기계설 vs 화학결합설 — 현재 결론과 한계
- **결론**: "화학기계 결합설"이 우세. §3 DFT 흡착에너지(−111~−258 kJ/mol, 화학흡착 영역)와 반응성 MD
  절단경로가 Si–O–Ce **화학결합**의 실재를 정량 지지. 순수 기계설로는 세리아가 더 경한 실리카·알루미나
  대비 같은 입경에서 SiO₂ 제거율이 높은 점, nitride 대비 큰 선택성을 설명 못 한다.
- **한계·불명확한 점**:
  - (a) Ce³⁺가 유리한가 Ce⁴⁺가 유리한가는 계·목적별 상충 보고 존재 — 제거 개시(Ce³⁺ 활성점)와
    산화력(Ce⁴⁺)이 공존, **정량적 최적비는 미검증**.
  - (b) IEP(세리아 6.7–7.8, 실리카 2–3)는 **2차 인용 범위**, 시료·수화·실리케이트 오염에 민감.
  - (c) 아미노산·계면활성제 선택비 절대값(35–70)은 슬러리·패드·압력 의존이라 **미검증**, 재현은
    Hwang 2024의 MRR 원자료 기반 선택비(59–80)만 수행.
  - (d) §7 verify는 문헌 수치의 **재현·자기일관·단위환산·부호논리**를 검사할 뿐, DFT 값 자체나 실험
    MRR 절대값을 독립 계산하지는 못한다(원문 값을 상수로 채택).
  - (e) Cook 1990·Hoshino 2001 원문은 **유료·1차 미확보**, 초록/2차 인용. 1차 출처는 OA인 Netzband
    2020·Brugnoli 2023·Hwang 2024(DOI/PMC 실존확인)로 충당.

## 7. 정량 재현 (코드)
**재현 요약**: 산소공공 x=0.1→Ce³⁺ 20% 전하균형 자기일관, 규산 흡착E −111/−258 kJ/mol을 화학흡착
영역으로 대조, (100)/(111) 결합강도 2.32배, 세리아(+)-실리카(−) 정전인력, oxide:nitride 선택비
59–80(BYK 67·G-336 80) 재현 — 아래 verify 1블록 PASS.

문헌 상수(DFT 흡착에너지·MRR·IEP)를 박고 관계식/재현/단위환산을 assert. 못 맞으면 정직히 기록.

```python verify
# 세리아 CMP: 산소공공-Ce3+ 전하균형 · Si-O-Ce 화학흡착 · IEP 정전인력 · 선택비
# 문헌값을 상수로 박고 재현/자기일관/단위환산/부호논리를 검증.

# ── (A) 산소공공 x ↔ Ce3+ 분율 전하균형 (CeO_{2-x}) ──
# O2- 하나 이탈 → 2e-가 Ce4+ 둘을 Ce3+로 환원. 전하중립: 4(1-f)+3f = 2(2-x) → f = 2x.
def ce3_fraction(x):
    return 2*x                       # Ce당 Ce3+ 분율
assert abs(ce3_fraction(0.10) - 0.20) < 1e-12   # CeO1.90 → Ce3+ 20%
assert abs(ce3_fraction(0.05) - 0.10) < 1e-12   # CeO1.95 → Ce3+ 10%
for x in (0.02, 0.10, 0.25):                     # 전하중립 자기일관성
    f = ce3_fraction(x)
    assert abs(4*(1-f) + 3*f - 2*(2-x)) < 1e-12
print(f"(A) 산소공공 x=0.10 → Ce3+ {ce3_fraction(0.10)*100:.0f}% (전하균형 자기일관 OK)")

# ── (B) Si-O-Ce는 화학흡착 (Brugnoli 2023 Langmuir doi:10.1021/acs.langmuir.3c00304, PMC10116594) ──
eV = 96.485                          # 1 eV = 96.485 kJ/mol
E111 = -1.15 * eV                    # 규산 흡착E, 세리아(111)
E100 = -2.67 * eV                    # 세리아(100)
assert abs(E111 - (-110.96)) < 0.5
assert abs(E100 - (-257.61)) < 0.5
assert E111 < -50 and E100 < -50     # 물리흡착(-20~-40)보다 강함 → 화학흡착
assert abs((-2.67)/(-1.15) - 2.32) < 0.02   # (100)/(111) 결합강도비
print(f"(B) 규산 흡착E (111)={E111:.0f}·(100)={E100:.0f} kJ/mol → 화학흡착, (100)/(111)={2.67/1.15:.2f}배")

# ── (C) IEP 차이 → 작동 pH에서 세리아(+)·실리카(-) 정전인력 ──
IEP_ceria, IEP_silica = 6.8, 2.5     # 2차 인용(시료의존, 미검증 범위)
def charge_sign(IEP, pH):
    return 1 if pH < IEP else (-1 if pH > IEP else 0)   # pH<IEP → 표면 양전하
for pH in (4, 5, 6):
    assert charge_sign(IEP_ceria, pH) * charge_sign(IEP_silica, pH) < 0   # 반대부호 = 인력
assert charge_sign(IEP_ceria, 8.0) * charge_sign(IEP_silica, 8.0) > 0     # pH>세리아IEP → 둘 다 음(-)
print("(C) pH 4-6: 세리아(+)·실리카(-) 반대부호 → 정전인력(접촉 촉진)")

# ── (D) oxide:nitride 선택비 재현 (Hwang & Kim 2024 Polymers doi:10.3390/polym16060844, PMC10974854) ──
data = {  # 시료: (oxide_MRR Å/min, nitride_MRR Å/min, 보고 선택비)
    "Base": (3493, 60, 59), "Depol": (4650, 75, 62),
    "BYK": (5558, 83, 67),  "G-336": (5417, 68, 80),
}
for name, (ox, ni, rep) in data.items():
    calc = ox / ni
    assert abs(round(calc) - rep) <= 1, f"{name}: 계산 {calc:.1f} vs 보고 {rep}"
    assert calc > 40                     # nitride가 oxide의 수십분의 일로 억제
print(f"(D) 선택비 재현: BYK {5558}/{83}={5558/83:.0f}, G-336 {5417}/{68}={5417/68:.0f} (보고 67·80과 일치)")

# ── (E) Netzband & Dunn 2020 (ECS JSS doi:10.1149/2162-8777/ab8393, OA) 비율 ──
MRR_boost, sel_before, sel_after = 5.5, 1.0, 3.0   # H2O2 0.5wt%로 Ce3+↑
assert MRR_boost > 1 and abs(sel_after/sel_before - 3.0) < 1e-9
print(f"(E) H2O2 0.5wt%(Ce3+↑): oxide MRR {MRR_boost}배·선택비 {sel_before:.0f}→{sel_after:.0f}")

print("PASS: 전하균형 f=2x · Si-O-Ce 화학흡착(-111~-258 kJ/mol) · IEP 정전인력 · 선택비 59-80 재현")
```

## 8. 다른 에이전트·단원과의 연결
- **[[slurry-components-overview]]**: §2 세리아 "화학적 이빨" 개요를 Ce³⁺ 활성점·Si–O–Ce 결합으로 심화.
- **[[particle-wafer-interaction-mechanical-chemical-balance]]**: §4 화학연화×기계제거 시너지의 원자판이
  §3 반응성 MD 절단경로(화학이 결합 약화 → 기계가 마무리).
- **[[colloid-zeta-dlvo-slurry-stability]]**: IEP·제타전위·DLVO를 세리아-실리카 쌍에 적용(§4).
- **[[surface-chemistry-cu-w-pourbaix-passivation]]**: 금속 CMP의 "무른 막 형성→기계박리"와 대비 —
  세리아 oxide CMP는 산화막 대신 **입자-기판 직접 화학결합**이 화학 손잡이라는 점이 다르다.
- **[[post-cmp-metallic-contamination-sources]]**: Ce–O–Si 결합이 끊기지 않으면 세리아 입자가 웨이퍼에
  잔류 → 후속 세정(EDTA로 Ce³⁺ 착화·결합 절단) 문제로 이어짐.
- **구현 요청**: Ce³⁺/Ce⁴⁺ 비 → oxide MRR, 아미노산 농도 → 선택비 정량모델은 담당 PROFILE.md
  "구현 요청"에 등록(직접 sim/ 미투입).

## 9. 자기시험
→ [[../../agents/slurry-chemist/EXAMS.md]] Lv3-1 문항 참조.
