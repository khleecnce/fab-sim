# 자기시험 — 슬러리 화학 전문가 (slurry-chemistry)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1 산화제 화학 (H₂O₂·KIO₃·Fe(NO₃)₃) — 2026-09-10
> 근거노트: [[../../knowledge/cmp/oxidizer-redox-potential-decomposition-metal-suitability]]

**Q1.** 텅스텐(W)과 구리(Cu)에 대해 H₂O₂·IO₃⁻·Fe³⁺ 세 산화제의 산화 자발성을 표준환원전위로 판정하라. 왜 "열역학적으로 가능"이 곧 "실무 선택"은 아닌가?

**A1.** 셀전위 `E_cell = E°(산화제) − E°(금속)`가 양수면 산화 자발(ΔG=−nFE_cell<0). E°(Vanýsek CRC): H₂O₂/H₂O +1.776 V, IO₃⁻/I⁻ +1.085 V, Fe³⁺/Fe²⁺ +0.771 V. 금속: WO₃/W −0.090 V, Cu²⁺/Cu +0.342 V.
- W: 셋 다 E_cell>0 (H₂O₂ +1.866, IO₃⁻ +1.175, Fe³⁺ +0.861 V) → 모두 자발.
- Cu: H₂O₂ +1.434, IO₃⁻ +0.743, Fe³⁺ +0.429 V → 역시 모두 양수지만 Fe³⁺ 구동력은 W 대비 절반으로 급감.
열역학은 "가능/불가능"만 정하고, 실제 선택은 **속도론(분해·산화 kinetics)·금속오염·선택비**가 결정한다(예: H₂O₂는 가장 강하지만 자기분해로 불안정, Fe³⁺는 안정하지만 Fe 오염). 출처: 근거노트 §2·§5.1(Vanýsek, CRC Handbook Electrochemical Series).

**Q2.** H₂O₂가 열역학적으로 반드시 분해된다는 것을 두 독립 방법으로 보이고, 이것이 W/Cu 슬러리 운용(현장혼합·pot-life)과 어떻게 연결되는지 설명하라.

**A2.** 불균등화 `2H₂O₂→2H₂O+O₂`. ① 전기화학: E_cell = E°(H₂O₂/H₂O) − E°(O₂/H₂O₂) = 1.776 − 0.695 = +1.081 V > 0 → ΔG=−2F·E<0 (≈−208.6 kJ/2mol). ② 표준생성깁스: 2(−237.14)−2(−134.03) = −206.2 kJ/2mol. 두 값 1.15% 이내 일치 → 자발 확정. 상온에서 느린 건 활성화 장벽 때문이며 **전이금속(Fe·Cu)이 Fenton 촉매로 장벽을 낮춰** 분해를 가속(Fe²⁺+H₂O₂ k≈63 M⁻¹s⁻¹, Fe³⁺ 개시는 ~10⁴배 느림 — De Laat & Gallard 1999, doi.org/10.1021/es981171v). 따라서 H₂O₂ 슬러리는 소모·기포·라디컬 생성으로 수명이 짧아 **연마 직전 현장혼합(point-of-use)** 이 표준. 반면 KIO₃·Fe(NO₃)₃는 자기분해가 없어 저장안정성이 좋다. 출처: 근거노트 §3·§5.2.

**Q3.** 세 산화제의 pH 의존성(Nernst 기울기)을 비교하고, Fe(NO₃)₃가 강산성(pH≈2.5) W plug 슬러리에 쓰이는 이유와 그 한계를 말하라.

**A3.** dE/dpH = −0.0591·(m/n) (m=H⁺ 계수, n=전자수). H₂O₂(m=2,n=2)와 IO₃⁻/I⁻(m=6,n=6)은 둘 다 −59.1 mV/pH → pH가 오르면 산화력이 약해진다. Fe³⁺/Fe²⁺(m=0,n=1)은 H⁺ 미관여라 **0 mV/pH, pH 무관**. 따라서 Fe³⁺는 강산성에서도 산화력이 유지되어 pH≈2.5 W 슬러리에 적합(WO₃ 부동태 유지에도 강산성이 유리). **한계**: Fe는 Si 밴드갭 중앙 근처 deep-level trap(소수캐리어 수명 킬러)이라 극미량도 소자에 해로워([[../../knowledge/cmp/metal-contamination-device-impact-irds-limits]]) back-end W에 국한되고 Fe-free로 대체되는 추세. 출처: 근거노트 §4·§5.3([[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]] §2 Nernst 기울기).
