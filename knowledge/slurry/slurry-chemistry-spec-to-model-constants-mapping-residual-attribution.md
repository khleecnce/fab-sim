<!-- V2-SECTION: R2-slurry | Cal-1 2026-09-20 | 근거: 화학 스펙시트→χ 상수 매핑·POU pH·잔차 귀속·식별성 | 정본: ORG.md §7.3 -->
# Cal-1 — 슬러리 화학 스펙(pH·산화제·억제제·킬레이트) → χ 상수 매핑 + 실측 MRR 잔차 귀속 (slurry-chemistry)

> 에이전트: slurry-chemistry Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-20
> 선행(재서술 금지·인용만):
> [[cobalt-ruthenium-complexing-agent-oxidizer-free-chi-driver]] (내 Lv3-1 — 착화제가 산화제에 곱하는 게이트·φ 재료별),
> [[../cmp/psi-inhibitor-strength-k-primary-source-verification]] (내 Lv3-2 — ψ `inhibitor_strength_k` 3회차 종결·unverified 확정),
> [[../cmp/oxidizer-redox-potential-decomposition-metal-suitability]] (내 Lv1-1 — 산화제 E°·pH 의존),
> [[../cmp/inhibitor-chelator-adsorption-isotherm-passivation]] (내 Lv1-2 — 억제제=흡착 vs 킬레이트=착화),
> [[../cmp/ph-ionic-strength-zeta-dissolution-selectivity-pourbaix]] (내 Lv2-1 — pH의 두 그림: ζ vs Pourbaix),
> [[../cmp/stop-layer-chemistry-design-principles-oxide-nitride-cu-barrier-w-oxide]] (내 Lv2-2 — 레짐 게이트),
> [[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]] (cmp-calibrator Cal-1 — **내 산출은 이 레지스트리 §1 표에 추가되는 행**·귀속 순서 정본),
> [[../data/cmp-calibration-schema-integration-validation-rules]] (cmp-data-engineer Cal-1 — 통합 49필드·§5 제안은 이것과 충돌 없이 추가),
> [[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] (형제 Cal-1 — Kp_ref·배율 분해의 곱 구조),
> [[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]] (형제 Cal-1 — 스펙시트→입력 변환·식별성의 형식·깊이 기준),
> [[shelf-life-dilution-two-part-blending-qc]] (slurry-colloid — 2-part/희석/로트 QC 물리는 여기가 정본, **로트 QC 필드 중복 회피**),
> [[../cmp/preston-luo-dornfeld-mrr]] (Kp = Kp₀·χ·… 곱 구조)

## 0. 목적·범위·형제 경계

ORG.md §7.3은 slurry-chemistry에게 **"슬러리 화학 스펙(농도·pH·산화제 종류) → 화학 상수 매핑 +
실측 MRR과의 잔차 정의"**를 맡겼다. 이 노트가 그 산출물이다. 앞 단원(Lv1~Lv3-2)은 재서술하지 않고
**인용만** 한다 — Lv3-1이 세운 "착화제=산화제 곱 게이트", Lv3-2가 3회차에 종결한 "ψ `inhibitor_strength_k`
값 부재"를 캘리브레이션 맥락으로 옮기는 것이 이 단원의 몫이다.

이 단원이 푸는 실제 문제는 형제 slurry-abrasive Cal-1([[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]])이
푼 것과 같은 구조다 — **"스펙시트에 적힌 값을 그대로 모델 상수에 넣으면 틀린다."** 거기서는 입도의
측정 가중이 문제였고, 여기서는 **원액 pH ≠ 웨이퍼에 닿는 작동 pH**가 문제다: 산화제(H₂O₂)는 POU에서
별도 첨가되고 산성이라 알칼리 원액에 섞이면 pH를 끌어내린다(§2, Bae 2023 실측 원액 10 → 9.78).
`slurry_ph`(원액)로 χ_pH를 걸면 캘리브레이터가 "그 팹 편차"와 "혼합 pH 시프트"를 뒤섞어 오학습한다.

**형제 경계 (침범 금지, 인용만):**
- **입자 스펙(입도·형상·측정 가중)**은 slurry-abrasive 소관. 농도항 κ_conc·입경항 κ_size는 인용만
  하고 새 정량 안 만든다([[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]]).
- **로트 이력·2-part 혼합비·희석의 콜로이드 물리·PSD**는 slurry-colloid 소관([[shelf-life-dilution-two-part-blending-qc]]).
  이 노트는 혼합비/희석을 **"작동 화학상태(농도·pH)를 정하는 입력"**으로만 인용하고, 응집·쉘프라이프
  물리를 재유도하지 않는다 — 로트 QC 필드(제타·점도·나이)는 그 노트 소유이므로 §5에서 중복 제안하지 않는다.
- **막질별 Kp·선택비**는 film-* 소관. χ는 Kp의 **곱 인자**로만 들어가고 절대 Kp는 안 건드린다(§3).
- **피팅 알고리즘·잔차 GP·식별성 이론(Raue·Tuo&Wu·Le Gratiet)**은 cmp-calibrator 소관
  ([[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]]). 이 노트는 **화학 축의
  식별 조건·귀속 순서**만 세우고 그 레지스트리 §1 규칙(Kp_ref→스윕된 축만)에 정합하게 행을 추가한다.
- **스키마 파일**(`data/schema/*.json`)·`ingest.py`·`prior.py`·`sim/`은 읽기만. §5는 개정 **제안**이며
  구현은 PROFILE.md 구현 요청으로 넘긴다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 모든 수치는 공개 표준·문헌·특허·합성이다.

## 1. 화학 스펙시트/COA 실제 항목 → χ 상수 매핑 (Cal-1 (a))

### 1.1 상용 슬러리 COA/스펙시트·특허 실시예가 실제로 적는 화학 항목 — 1차 조사

| # | 소스(유형) | pH 표기 | 산화제 | 억제제/킬레이트 | 전도도/고형분 | 등급 |
|---|---|---|---|---|---|---|
| C1 | **Cabot 5001**(Miranda 2004 실사용, DOI:10.1109/WMED.2004.1297359) | "batch processed to pH ~8" (**원액**), 질산으로 pH 4·8 재조정 | H₂O₂ **1.5~3.5 vol% POU 별도 첨가** | 알루미나 베이스(억제제 조성 비공개) | 고형분 비공개 | E3 |
| C2 | **Bae 2023**(DOI:10.3390/app13063758, MDPI CC-BY) | 원액 pH 10 → **H₂O₂ 혼합 후 9.78** | H₂O₂ 1.0 wt% POU 별도 주입 | BTA + 글리신(농도 Table S1) | 실리카 ~60 nm | E3 |
| C3 | **Jani 2025**(DOI:10.1149/2162-8777/adc59e, CC-BY) | pH 3.0 고정 | H₂O₂ 3~7 wt% | 글리신 0~0.26 M·옥살산 0.02~0.08 M·DOSS·BTA | 실리카 1~6 wt% | E1(표) |
| C4 | **US20080090500A1**(PPG, cu_ph_acid_k 출처) | pH 3/4/5/6 완전교차 | H₂O₂ 3 wt% | 글리신 1 wt%·BTA 1 mM | 실리카 0~4 wt% | E3 |
| C5 | **Vazquez Bengochea 2018**(DOI:10.3390/mi9110542, via [[shelf-life-dilution-two-part-blending-qc]] §6) | 인라인 pH·굴절률 | H₂O₂(30%) POU 블렌딩 | — | **인라인 밀도·굴절률**, 블렌드비 UPW:PL-7106:H₂O₂=87:10.2:2.8 | E1(재인용) |

**조사 결과 4가지 사실:**
1. **pH는 두 개의 숫자다** — 원액 pH(COA·TDS에 적힘)와 POU 혼합 후 작동 pH(측정해야 앎). C1·C2가
   둘의 차이를 명시(Cabot 원액 8→재조정, Bae 원액 10→혼합 9.78). χ_pH가 필요한 것은 **후자**다(§2).
2. **산화제는 대개 POU 별도 첨가**다(C1·C2·C5). H₂O₂는 자기분해·산성이라 원액에 미리 못 넣는다 —
   그래서 "슬러리 pH"와 "산화제 농도"가 원액 스펙과 분리돼 있고, 혼합 시점·순서가 작동 pH를 바꾼다.
3. **억제제/킬레이트는 종(species)과 농도가 따로**다. 팩이 이미 `inhibitor_species`·`chelator_species`를
   조회 키로 갖고(§cu_h2o2_bta) 종이 다르면 값을 재사용하지 않는다 — COA가 종을 안 적으면 매핑 불가.
4. **전도도·고형분은 인라인 QC 표준 항목**(C5, 밀도·굴절률)이나 현행 화학 축 매핑엔 안 들어가 있다 —
   전도도는 이온강도 대리(제타·κ⁻¹ 경로, slurry-abrasive/colloid 소관)라 χ의 **간접 입력**이다.

### 1.2 매핑 표 — 스펙 항목이 어느 χ 상수의 어느 변수로 들어가나

χ는 Preston Kp의 **곱 인자**다: $K_p = K_{p0}\cdot\kappa_{size}\cdot\kappa_{conc}\cdot\chi_{pH}\cdot f_{ox}\cdot\psi\cdot(\text{킬레이트}\cdot\text{촉진})$
(sim `_f_kappa`·`sim/chemistry.py` 항 구조, [[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]] §5 인용).
각 스펙 항목이 어느 인자·팩 키·함수형에 들어가는지:

| 스펙시트/COA 항목 | 매핑 χ 상수(인자) | 팩 키 | 함수형(진입) | 1차 근거(등급) |
|---|---|---|---|---|
| **작동 pH**(POU 혼합 후) | χ_pH | `slurry_ph`,`ph_ref`,`cu_ph_acid_k`/`cu_ph_alkaline_k`/`w_ph_acid_k` | $\exp(-k(\mathrm{pH}-\mathrm{pH}_{ref}))$, V자 레짐 분기 | C4 US20080090500A1(E3)·US9200180B2(E3)·Stojadinović(E3) |
| 원액 pH | (χ 아님) 작동 pH 산출의 **입력**만 | — | 혼합·희석 후 재계산 필요 | C1·C2(E3) |
| **산화제 종·농도**(POU) | f_ox | `oxidizer`,`oxidizer_wt_pct`,`oxidizer_ref_wt_pct`,`oxidizer_passivation_K`/`_langmuir_K`/`_acid_chelator_K` | Langmuir 피복 $\phi+(1-\phi)\theta(C)/\theta(C_{ref})$, **레짐 게이트** | US20110165777A1(estimated)·US20110186542A1(literature)·Jani 2025(estimated) |
| **억제제 종·농도** | ψ | `inhibitor_species`,`inhibitor_mM`,`inhibitor_ref_mM`,`inhibitor_strength_k` | $\exp(-k\theta)$, θ=Langmuir | **값 부재**(Lv3-2 3회차 종결, unverified) |
| **킬레이트 종·농도** | 킬레이트 억제 a | `chelator_species`,`chelator_M`,`chelator_ref_M`,`chelator_suppression_a` | $\exp(-a(C-C_{ref}))$, 종 일치 시만 | Jani 2025(estimated, 판정#72) |
| (디카복실레이트) 촉진제 종·농도 | 촉진 지수 m | `promoter_species`,`promoter_M`,`promoter_anchor_M`,`promoter_exponent_m`,`promoter_floor_phi` | $\phi+(1-\phi)(C/C_{anchor})^m$, 종 일치 시만 | US6309560B1(estimated, 판정#75) |
| 고형분(wt%) | κ_conc (**slurry-abrasive 소관**) | `abrasive_wt_pct`,`abrasive_ref_wt_pct` | 포화형 (인용만) | US9499721B2(E1, 형제) |
| 전도도(µS/cm) | 제타/이온강도 (**형제 소관, χ 간접**) | (팩 IEP·이온강도) | κ⁻¹=0.304/√I·ζ 부호 | 내 Lv2-1(인용) |
| 2-part 혼합비·희석비 | (χ 아님) 작동 농도·pH 산출 입력 | — | slurry-colloid 물리 | C5·[[shelf-life-dilution-two-part-blending-qc]](인용) |

**핵심**: χ가 요구하는 것은 스펙시트의 **원액 값이 아니라 "웨이퍼에 닿는 순간의 작동 값"**이다. 산화제
농도·pH·희석은 POU에서 결정되므로(§2), 원액 스펙을 그대로 χ에 넣으면 매핑이 계통적으로 틀린다.

## 2. POU 혼합 후 pH ≠ 원액 pH — 측정 pH 없이는 χ_pH 귀속 불가 (Cal-1 (a) 핵심)

이 절이 이 단원의 고유 발견이다. cmp-calibrator 레지스트리는 P5(χ_pH)를 **"pH 스윕 + 측정 pH 명시
없으면 PriorExcluded"**로 이미 규정했다([[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]] §1 P5).
**왜** 측정 pH가 없으면 안 되는지를 1차 실측으로 못박는 것이 이 절이다.

**Bae, Kim, Kwak, Oh, Kim (2023)**, "Investigation of the Two-Way Injection Slurry-Supply Method for
the Cu CMP Process," *Appl. Sci.* 13(6) 3758, **DOI: 10.3390/app13063758** (MDPI CC-BY; MDPI가 PDF
직다운로드를 봇차단해 **HTML 전문 판독 = E3**, `papers/bae2023-two-way-injection-cu-cmp.txt`, INDEX 등록):

- 슬러리 원액 pH를 **10으로 조정**했으나, 산성인 H₂O₂ 1.0 wt%를 섞으면 **작동 pH가 ~9.78로 내려간다**
  (원문: *"Even if the pH of the slurry is adjusted to 10, H₂O₂ is acidic, so when mixed with 1.0 wt%
  H₂O₂, the pH slightly decreases to about 9.8."* Table 1: reference MRR 3105.4 Å/min @ pH **9.78**).
- H₂O₂ 용액 자체의 pH를 미리 10으로 맞춰 주입하면 혼합 후 pH가 ~10(≈0.2 높음)이 되고, 그 결과
  **MRR이 약 1000 Å/min 상승**(기준 ~3100 대비 ≈30%). 즉 **작동 pH 0.2 차이가 MRR 30%를 바꾼다.**
- 물리 연쇄(원문 Introduction): H₂O₂ 분해 → pH 변화 → 글리신 이온상태 변화 → 킬레이트 효과 변화.
  즉 pH는 **산화제 안정성 경로와 킬레이트 이온화 경로 둘 다**를 통해 MRR에 들어온다(내 Lv3-1 §3의
  "pH가 착화제 양성자화 분율로도 χ에 들어온다"의 독립 실측 확증).

**결론(어떤 필드가 해결하나)**: 스키마에 원액 `slurry_ph`만 있으면 캘리브레이터는 작동 pH를 모른다 —
Bae의 경우 10으로 기록됐지만 실제 χ_pH가 봐야 할 값은 9.78이다. **`measured_ph_pou`(POU 혼합·연마
직전 실측 pH) 필드가 이를 해결**한다(§5). 이 필드가 없으면 χ_pH는 레지스트리 P5 규칙대로
**PriorExcluded**로 두고 잔차를 Kp_ref에 흡수한다(§3, EVIDENCE-RULES 데이터 스누핑 금지).

## 3. 잔차 정의 + 화학 축별 식별 조건·귀속 순서 (Cal-1 (b))

### 3.1 잔차 정의와 귀속 순서 — 레지스트리 §1과 정합

잔차 $r=\mathrm{MRR}_{obs}/\mathrm{MRR}_{pred}$를 화학 축(pH·산화제·억제제·킬레이트)에 귀속하는 순서는
cmp-calibrator 레지스트리 귀속 순서([[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]] §1)에
**종속**된다 — 새 순서를 만들지 않는다:
1. **절대 Kp_ref(스칼라 배율)를 먼저** 고정한다(레지스트리 순서 1). χ 축은 그 다음이다.
2. **스윕된 화학 축만** 잔차를 귀속한다(레지스트리 순서 3). 그 축을 실제 흔든 데이터
   (validation/datasets의 pH·산화제 스윕)가 있을 때만. **없으면 Kp_ref에 흡수하고 쪼개지 않는다**
   (EVIDENCE-RULES §금지: 안 흔든 축의 임의 분할 = 데이터 스누핑).
3. **곱 구조라 축 간 상쇄**된다 — 한 조건만으로는 χ_pH·f_ox·ψ가 서로 상쇄돼 분리 안 된다(§4, film-oxide
   §4-A 곱 구조의 화학판). 각 축은 **자기 축만 흔들고 나머지를 고정**해야 식별된다.

### 3.2 화학 축별 식별 조건 표

| χ 축 | 팩 키 | 단일조건 식별 | 분리(귀속) 조건 | 식별 불가 시 처리 |
|---|---|---|---|---|
| **pH** χ_pH | `cu_ph_acid_k`·`cu_ph_alkaline_k` | **불가** (f_ox와 곱, V자 레짐) | pH 스윕 ≥2점 + **측정 작동 pH 명시** + 산화제·착화제 고정 + 레짐(산성/알칼리) 분리 | 측정 pH 없으면 **Kp_ref 흡수**(P5 PriorExcluded, §2) |
| **산화제** f_ox | `oxidizer_*_K` | **불가** (pH와 곱, 부호 레짐 의존) | 산화제만 스윕 ≥3점 + **레짐(pH·착화제) 명시** + 나머지 고정 | 레짐 미명시면 부호부터 불확실 → **Kp_ref 흡수** |
| **억제제** ψ | `inhibitor_strength_k` | **불가** (Kp_ref와 곱) | 억제제 농도 스윕 + **함수형 검증** + 종 일치 | **PriorExcluded**(값·함수형 모두 부재, §3.3) |
| **킬레이트** a | `chelator_suppression_a` | **불가** | 착화제만 스윕 ≥2점 + 종 일치(글리신) + 산화제 고정 | 종 불일치·미스윕 시 **Kp_ref 흡수** |
| (촉진) m | `promoter_exponent_m` | **불가** | 촉진제 스윕 + 종 일치(옥살산) | 종 불일치 시 폴백(항 비활성) |

### 3.3 ψ `inhibitor_strength_k` 값 부재의 캘리브레이션 처리 — EVIDENCE-RULES 판정

**판정 대상**: Lv3-2가 3회차에 종결한 ψ `inhibitor_strength_k`(cu 3.0·w 2.117, 둘 다 unverified,
[[../cmp/psi-inhibitor-strength-k-primary-source-verification]])를 캘리브레이션에서 **prior 제외로 둘 것인가,
넓은 prior로 둘 것인가.**

| 후보 | 논리 | 등급 |
|---|---|---|
| A: 넓은 prior | 값이 불확실하니 넓은 로그정규(estimated σ_log=0.811)를 주고 데이터가 정하게 | 운영 편의 |
| B: PriorExcluded | 값·함수형 모두 근거 부재 + Kp_ref와 곱으로 축퇴 → 넓은 prior는 잔차를 k에 임의 흡수(스누핑) | EVIDENCE-RULES §금지 + 레지스트리 P5 선례 |

**판정: B 채택(PriorExcluded).** 근거 셋:
1. **값이 unverified가 아니라 함수형 자체가 반증됐다** — w_fe_oxidizer에서 K를 자유롭게 풀어도(K→0
   극한까지) Langmuir+exp(−kθ)가 0.5wt% 앵커를 17.6% 못 맞춘다([[../cmp/psi-inhibitor-strength-k-primary-source-verification]]).
   함수형이 틀린 파라미터에 넓은 prior를 주면 데이터가 **틀린 축으로 잔차를 몰아넣는다**.
2. **Kp_ref와 곱으로 완전 축퇴**(§4). 넓은 prior의 k는 절대 스케일과 상쇄돼(film-oxide §4-A 구조)
   비식별 — Raue의 "flat valley"([[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]] §2.1).
3. **prior.py가 unverified를 이미 제외**한다(레지스트리 §4-B `assert "unverified" not in mult`).
   B는 새 규칙이 아니라 기존 규약의 적용이다.

**처리 방식**: ψ 항을 기준(inhibitor_mM=ref_mM)에서 항등 배수 1.0으로 고정하고 **캘리브레이션 타깃에서
제외**한다 — 억제제 농도 스윕 데이터가 와도 k를 피팅하지 않고(함수형 반증) 잔차를 Kp_ref에 흡수한다.
이는 EVIDENCE-RULES §절차 4(3회차 초과 → null/스코프 축소로 종결)의 캘리브레이션 판(스코프 축소:
"ψ K는 이 코퍼스에서 캘리브레이션 대상이 아니다")이다. **값도 함수형도 안 바꾼다**(코드 미변경).

## 4. Python 검증 — pH×산화제 교호작용 편향 + 2×2 분리 식별 (Cal-1 (c))

**재현 요약(한 줄)**: Miranda 2004 실측 2×2 4점(pH 4/8 × H₂O₂ 1.5/3.5 vol% → MRR 195.3·290.8·174.3·24.3
nm/min, DOI:10.1109/WMED.2004.1297359)을 대조·재구성해 — (A) pH 단독 스윕에서 피팅한 χ_pH 기울기가
산화제 농도에 따라 **부호가 바뀜**(ox 1.0 vol%에서 +0.120/pH, 3.5 vol%에서 −0.621/pH, 영교차 1.40 vol%)을
assert하고, (B) 2×2 동시 스윕(코드화 DOE)은 직교라 조건수 1.0·rank 4로 교호작용까지 식별되나 pH 단독은
rank 2/4로 교호작용 비식별임을 조건수·rank로 assert한다(numpy만). 실측 24.3~290.8 nm/min 4점과 대조.

```python verify
import numpy as np
# ═══ (A) pH 단독 스윕으로 χ_pH를 피팅하면 산화제 농도에 따라 부호가 바뀐다 ═══
# Miranda, Imonigie, Moll 2004 (WMED), DOI:10.1109/WMED.2004.1297359, Table 3 인쇄값(nm/min)
# (pH, H2O2 vol%, MRR): 팩 cu_h2o2_bta, 장비·억제제 전부 고정, 조성 2축만 변화
data = [(4.0,1.5,195.3),(4.0,3.5,290.8),(8.0,1.5,174.3),(8.0,3.5,24.3)]
pH = np.array([d[0] for d in data]); ox = np.array([d[1] for d in data])
y  = np.log(np.array([d[2] for d in data]))                 # 로그 MRR (곱 구조 → 로그선형)
# pH 단독 스윕(산화제를 한 수준에 고정)에서 잰 "겉보기 χ_pH 기울기"
slope_ox15 = (y[2]-y[0])/(pH[2]-pH[0])                      # ox 1.5%에 고정, pH 4→8
slope_ox35 = (y[3]-y[1])/(pH[3]-pH[1])                      # ox 3.5%에 고정, pH 4→8
# 쌍선형(교호작용) 모형 y = c + b_pH·pH + b_ox·ox + b_int·(pH·ox) 에서
#   겉보기 pH 기울기 = b_pH + b_int·ox  (산화제 수준의 함수 — 이게 편향의 정체)
b_int = (slope_ox35 - slope_ox15)/(3.5-1.5)
b_pH  = slope_ox15 - b_int*1.5                              # 교호작용을 걷어낸 pH '주효과'
apparent = lambda c: b_pH + b_int*c
cross = -b_pH/b_int                                          # 겉보기 기울기가 0을 지나는 산화제 농도
print(f"[A] 겉보기 χ_pH 기울기: ox1.5%={slope_ox15:+.3f}/pH  ox3.5%={slope_ox35:+.3f}/pH")
print(f"    분해: 주효과 b_pH={b_pH:+.3f}, 교호작용 b_int={b_int:+.3f}, 부호전환 산화제={cross:.2f} vol%")
print(f"    → 산화제 1.0%면 χ_pH={apparent(1.0):+.3f}(양), 3.5%면 {apparent(3.5):+.3f}(음)")
# 부호가 바뀐다: 같은 pH 단독 스윕이라도 어느 산화제 수준에서 쟀냐로 χ_pH 부호가 뒤집힌다
assert apparent(1.0) > 0 and apparent(3.5) < 0
assert 1.0 < cross < 3.5                                     # 실측 스윕 범위 안에서 부호 전환
assert b_pH > 0                                              # 교호작용을 걷으면 주효과는 양(+0.42), 겉보기는 음
# H2O2 효과 자체도 pH로 부호가 뒤집힘(Miranda ANOVA: 교호작용 p=0.0207, 원문 확증)
ox_slope_pH4 = (y[1]-y[0])/(3.5-1.5); ox_slope_pH8 = (y[3]-y[2])/(3.5-1.5)
assert ox_slope_pH4 > 0 and ox_slope_pH8 < 0
print(f"    (교차확증) H2O2 효과: pH4={ox_slope_pH4:+.3f}(증가) pH8={ox_slope_pH8:+.3f}(감소) — 부호 반전")
```

```python verify
import numpy as np
# ═══ (B) 2×2 동시 스윕이면 교호작용까지 분리 식별 / pH 단독은 비식별 ═══
data = [(4.0,1.5),(4.0,3.5),(8.0,1.5),(8.0,3.5)]
pH = np.array([d[0] for d in data]); ox = np.array([d[1] for d in data])
# 코드화(±1) 요인 — 표준 2^2 DOE(직교 설계)
pH_c = np.where(pH==4.0,-1.0,1.0); ox_c = np.where(ox==1.5,-1.0,1.0)
# 완전 2×2: [절편, pH, 산화제, 교호작용] 4열
X_full = np.column_stack([np.ones(4), pH_c, ox_c, pH_c*ox_c])
cond_full = np.linalg.cond(X_full); rank_full = np.linalg.matrix_rank(X_full)
assert cond_full < 1.01 and rank_full == 4                 # 직교 → 조건수 1.0, 4파라미터 전부 식별
# pH 단독 스윕(산화제를 1.5%에 고정): 산화제·교호작용 열이 상수/공선 → 비식별
m = ox == 1.5
X_ponly = np.column_stack([np.ones(m.sum()), pH_c[m], ox_c[m], (pH_c*ox_c)[m]])
rank_ponly = np.linalg.matrix_rank(X_ponly)
assert rank_ponly < 4                                       # 4열 중 rank 2 — 교호작용 분리 불가
# 비코드(원단위) 완전설계도 유한 조건수(식별 가능, 단 직교는 아님)
X_raw = np.column_stack([np.ones(4), pH, ox, pH*ox])
assert np.linalg.cond(X_raw) < 1e4 and np.linalg.matrix_rank(X_raw) == 4
print(f"[B] 2×2 동시 스윕(코드화): 조건수 {cond_full:.4f}·rank {rank_full}/4 → 교호작용 포함 전부 식별")
print(f"    pH 단독 스윕: rank {rank_ponly}/4 → 산화제·교호작용 비식별(겉보기 χ_pH가 (A)처럼 편향)")
print(f"    비코드 완전설계 조건수 {np.linalg.cond(X_raw):.1f} (유한 → 식별, 직교 아님)")
```

**결과 해석(정직하게)**
- (A)는 **Miranda 2004 실측 4점의 직접 계산 + 쌍선형 재구성**이다(정직 표지). 4점이라 교호작용 모형이
  자유도를 다 쓰므로(잔차 0) 이는 "재구성"이지 통계적 적합이 아니다 — 부호 전환은 실측 4점의 산술적
  귀결이고, 원문 ANOVA(교호작용 p=0.0207, H₂O₂ 단독 p=0.588 비유의)가 독립 확증한다.
- **주효과 b_pH=+0.42가 겉보기 기울기(둘 다 음)에 완전히 가려진다** — 이것이 "pH 단독 스윕으로 χ_pH를
  피팅하면 안 되는" 이유의 정량 형태다. 산화제 수준을 명시(레짐 고정)하지 않은 pH 잔차는 귀속 불가.
- (B)의 조건수 1.0은 코드화 2² 설계가 직교이기 때문이고, pH 단독의 rank 2/4는 산화제·교호작용 열이
  상수(공선)이기 때문이다 — 실측 노이즈와 무관한 **구조적** 결론(film-oxide §4-A 곱 구조의 화학판).
- 이 결과가 §3.2 표의 "각 축은 자기 축만 흔들고 나머지 고정 + 레짐 명시"를 강제한다.

## 5. 스키마 개정 제안 — 화학 필드 (Cal-1 (d), 파일 무수정)

통합 49필드([[../data/cmp-calibration-schema-integration-validation-rules]] §3)는 `slurry_ph`·제타 3필드만
갖고 **산화제·억제제·킬레이트 종/농도·작동 pH·전도도가 없다**. 아래는 **추가 제안**(전부 optional →
MINOR 버전업 1.1.0, 하위호환·구레코드 통과, cmp-data-engineer §6 규칙①과 정합). `slurry_spec` 객체에 응집.

| 필드(제안) | 타입/enum | 필수성 | 근거 | 효과 |
|---|---|---|---|---|
| `measured_ph_pou` | number | χ_pH 보정 시 **필수** | §2 Bae 2023 | 작동 pH — 없으면 χ_pH PriorExcluded |
| `oxidizer_species` | enum: H2O2/KIO3/Fe(NO3)3/KMnO4/none | 산화제 있으면 필수 | §1 C1·C3, 내 Lv1-1 | f_ox 종 키 |
| `oxidizer_conc_value`+`_unit`(wt%/vol%) | number/enum | 필수 | §1 C1·C2 | f_ox 응답 농도 |
| `oxidizer_added_at_pou` | bool | 권고 | §1 C1·C2·C5 | POU 별도 첨가 여부(작동 pH 재계산 트리거) |
| `inhibitor_species`+`inhibitor_conc_value`+`_unit`(mM/wt%/ppm) | string/number/enum | 억제제 있으면 필수 | §1 C4, 팩 조회 키 | ψ 종·농도(종 다르면 값 재사용 금지) |
| `chelator_species`+`chelator_conc_value`+`_unit`(M/wt%) | string/number/enum | 킬레이트 있으면 필수 | §1 C3·C4, 판정#72 | 킬레이트 억제 a 종·농도 |
| `promoter_species`+`promoter_conc_value` | string/number | 촉진제 있으면 | §1 C3, 판정#75 | 촉진 m(종 일치 시) |
| `conductivity_us_cm` | number | 권고 | §1 C5, 인라인 QC | 이온강도 대리(제타 축, 형제 소관) |
| `solids_wt_pct` | number | 권고 | §1 C2 | 고형분(→κ_conc, slurry-abrasive 소관) |
| `blend_ratio` | object `{component: ratio}` | 2-part면 권고 | §1 C5, [[shelf-life-dilution-two-part-blending-qc]] | 작동 농도·pH 산출 입력(colloid 소관 물리) |
| `dilution_ratio` | number | 희석 시 권고 | §1 C5 | 작동 농도·이온강도(colloid 소관) |

**주의(중복 회피)**: 로트 QC 상태량(제타·점도·나이·응집)은 **slurry-colloid 소유**
([[shelf-life-dilution-two-part-blending-qc]] §9)라 여기서 다시 제안하지 않는다. `blend_ratio`·
`dilution_ratio`는 그 노트가 이미 "팩에 없다"고 지적한 필드이나, 이 노트는 그 값을 **작동 화학상태(작동
pH·농도) 산출의 입력**으로만 쓴다 — 콜로이드 안정성 물리는 colloid, 화학 상수 매핑은 여기, 소유 분리.

## 6. 근거 충돌 판정 (EVIDENCE-RULES.md 서열)

| # | 충돌 | A (등급) | B (등급) | 판정 |
|---|---|---|---|---|
| 1 | ψ `inhibitor_strength_k` 캘리브레이션 처리 | 넓은 prior로 데이터가 정하게(운영 편의) | 함수형 반증+Kp_ref 축퇴 → PriorExcluded (E2 반증 + 레지스트리 P5) | **B 채택**(§3.3) — 함수형이 틀린 파라미터에 넓은 prior는 잔차 오흡수. 3회차 종결의 캘리브레이션 판=스코프 축소 |
| 2 | χ_pH 입력으로 원액 pH vs 작동 pH | 원액 pH(스펙시트에 있음, 편의) | 작동 pH(Bae 2023 실측: 원액10→9.78, 0.2pH가 MRR 30%) (E3) | **B 채택**(§2) — 원액 pH를 χ_pH에 넣으면 혼합 시프트를 팹 편차로 오학습. measured_ph_pou 필수 |

새 물리 충돌 없음(형제 기확정 값 재추정 안 함). 상반된 지수 평균낸 곳 없음.

## 7. 한계·미확보·미검증 (정직성 표기)

- **§4는 실측 4점의 산술 재구성**이지 다점 통계적 적합이 아니다(정직 표지). 교호작용 모형이 4점 자유도를
  다 써 잔차 0 — 부호 전환은 실측의 귀결이고 원문 ANOVA가 독립 확증하나, 함수형(쌍선형)의 외삽은 미검증.
- **Bae 2023은 MDPI HTML 판독(E3)**, 클린 PDF 미확보(PDF 봇차단). Table 1·본문 서술은 판독했으나
  Figure 4의 정확한 곡선·오차막대는 미판독 — "MRR ~1000 Å/min 상승"은 본문 서술 인용이다.
- **Eom 2007**(DOI:10.1149/1.2393015, JES 154 D38, Crossref 실존)은 pH 4에서 H₂O₂↑→RR 선형증가, pH 6에서
  7vol% 정점 후 감소를 보고해 §2·§4의 레짐 의존을 독립 지지하나 **IOP 유료·초록만(E5)** — 보강 인용으로만 썼다.
- **σ_log 등급 배수는 미검증 운영 규약**(prior.py docstring 자백, 레지스트리 §7 인용). §8 σ_log 열은 그
  규약을 계승했다.
- **f_ox·킬레이트 a·촉진 m 값은 전부 형제/내 앞 단원이 확정한 것**(estimated 등급)을 옮긴 것이고 이
  노트에서 재추정하지 않았다 — 각 값의 1차 근거·한계는 해당 팩 키 note·근거노트를 따른다.
- **전도도→이온강도→제타 경로는 slurry-abrasive/colloid 소관**이라 이 노트는 χ 간접 입력으로만 표기하고
  정량 매핑을 만들지 않았다. 전도도가 첨가제 동적평형과 조성 변화를 구분 못 한다는 맹점은
  [[shelf-life-dilution-two-part-blending-qc]] §6 인용.
- **작동 pH 재계산 폐형식은 미확보**다 — Bae는 "원액10→9.78"의 단일 관측만 준다. 혼합비·산화제 농도에서
  작동 pH를 예측하는 완충 모델은 이 코퍼스에 없어, 당장은 `measured_ph_pou`를 **입력으로 받는** 것이
  근거로 지지되는 최대치다(예측하지 않고 측정한다).

## 8. 레지스트리 추가 행 (cmp-calibrator §1 표에 추가 — 화학 축)

cmp-calibrator 레지스트리([[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]] §1)의
P5(χ_pH, "대부분 unverified·PriorExcluded")를 **화학 축별로 전개**한 행이다. σ_log는 prior.py
`confidence_to_log_sigma`(verified 0.101·measured 0.203·literature 0.405·estimated 0.811·unverified=제외,
레지스트리 §4-B 대조) 그대로 적용 — 새 규약 안 만든다. 잔차 귀속 순서는 레지스트리 순서(1=Kp_ref
먼저, 3=스윕된 축만)를 계승한다.

| # | 파라미터 (기호) | Kp 진입 | prior 중심 출처(등급) | 등급→σ_log | 식별에 필요한 스윕 | 잔차 귀속 순서 |
|---|---|---|---|---|---|---|
| C1 | **pH항 산성 $\chi_{pH}^{acid}$** (`cu_ph_acid_k`) | 곱 $\exp(-k\Delta\mathrm{pH})$ | US20080090500A1 pooled 12점 k=0.1428 (E3) | literature→0.405 | pH 스윕 ≥2 + **측정 작동 pH** + 산화제·착화제 고정, 산성 레짐 | 3 (측정 pH 없으면 **PriorExcluded**→Kp_ref 흡수) |
| C2 | **pH항 알칼리 $\chi_{pH}^{alk}$** (`cu_ph_alkaline_k`) | 곱 | US9200180B2 5점 k=0.3329 (E3) | literature→0.405 | 알칼리 레짐 pH 스윕 + 측정 pH + BTA無 | 3 (레짐·측정 pH 조건, 산성 k와 평균 금지) |
| C3 | **pH항 W $\chi_{pH}^{W}$** (`w_ph_acid_k`) | 곱 | Stojadinović 2016 k=0.1163 (E3, KIO3 대리계) | literature→0.405 | pH 2~5 산화제 존재 스윕 | 3 (외삽 금지, 대리계) |
| C4 | **산화제 $f_{ox}$ 알칼리·무착화제** (`oxidizer_passivation_K`) | 곱 Langmuir 억제형 | US20110165777A1 4점 K=0.8232 (estimated) | estimated→0.811 | 산화제만 스윕 + 알칼리·무착화제 레짐 명시 | 3 (레짐 미명시면 부호 불확실→흡수) |
| C5 | **산화제 $f_{ox}$ W** (`oxidizer_langmuir_K`) | 곱 Langmuir 촉진형 | US20110186542A1 3점 K=0.5496·φ=0.14 (literature) | literature→0.405 | 산화제 0/1/3wt% + φ 앵커 | 3 (정점 위 외삽 미확보) |
| C6 | **산화제 $f_{ox}$ 산성×착화제** (`oxidizer_acid_chelator_K`) | 곱 Langmuir 촉진형, **레짐 게이트** | Jani 2025 Expt30/31/32 K=0.7935 (estimated) | estimated→0.811 | 산성×착화제 레짐 + 산화제 스윕 + 착화제 종 | 3 (used_for_calibration=true, held-out 아님) |
| C7 | **억제제 $\psi$** (`inhibitor_strength_k`) | 곱 $\exp(-k\theta)$ | 값·함수형 부재(Lv3-2 3회차 종결) | **PriorExcluded** | 억제제 스윕 + **함수형 검증**(현재 반증됨) | **제외**(§3.3, Kp_ref 흡수·쪼개지 않음) |
| C8 | **킬레이트 억제 $a$** (`chelator_suppression_a`) | 곱 $\exp(-a\Delta C)$ | Jani 2025 통제쌍 2건 a=1.5119 (estimated, 판정#72) | estimated→0.811 | 착화제만 스윕 ≥2 + 종 일치(글리신) + 산화제 고정 | 3 (종 불일치·미스윕 시 흡수) |
| C9 | **촉진 지수 $m$** (`promoter_exponent_m`) | 곱 $(C/C_a)^m$ | US6309560B1 통제쌍 m=0.7238 (estimated, 판정#75) | estimated→0.811 | 촉진제 스윕 + 종 일치(옥살산) | 3 (종 불일치 시 항 비활성 폴백) |

**행 배정 원칙(정직)**: C1~C9는 전부 **화학 축이 Kp에 곱으로 들어가는 인자**라 절대 Kp_ref(레지스트리
P1) 뒤에 온다(귀속 순서 3). 어느 것도 단일조건 식별 불가(§4)이며 자기 축 스윕+나머지 고정+레짐 명시가
전제다. C7(ψ)만 값·함수형이 모두 부재해 **PriorExcluded**로 P5와 같은 지위다 — 나머지는 스윕이 있으면
귀속 가능한 estimated/literature다.

## 9. 구현 요청
→ [[../../agents/slurry-chemistry/PROFILE.md]] "## 구현 요청 (2026-09-20, Cal-1)" 참조
(measured_ph_pou 기반 χ_pH 라우팅·작동 pH 입력 게이트·ψ PriorExcluded 스위치·레짐 게이트 검사, §2·§3·§5).

## 10. 자기시험
→ [[../../agents/slurry-chemistry/EXAMS.md]] Cal-1 문항 참조.

## 상호링크
[[cobalt-ruthenium-complexing-agent-oxidizer-free-chi-driver]]
[[../cmp/psi-inhibitor-strength-k-primary-source-verification]]
[[../cmp/oxidizer-redox-potential-decomposition-metal-suitability]]
[[../cmp/inhibitor-chelator-adsorption-isotherm-passivation]]
[[../cmp/ph-ionic-strength-zeta-dissolution-selectivity-pourbaix]]
[[../cmp/stop-layer-chemistry-design-principles-oxide-nitride-cu-barrier-w-oxide]]
[[../calibration/calibration-parameter-registry-identifiability-sequential-fitting]]
[[../data/cmp-calibration-schema-integration-validation-rules]]
[[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]]
[[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]]
[[shelf-life-dilution-two-part-blending-qc]]
[[../cmp/preston-luo-dornfeld-mrr]]
