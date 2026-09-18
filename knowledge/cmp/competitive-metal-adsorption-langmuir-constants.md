<!-- V2-SECTION: R2-slurry | 정본: ARCHITECTURE-V2.md §3 -->
# 경쟁 Langmuir 흡착 K_i 문헌표 — Cu·Fe·Co·W·Ru 산화물/실리카 표면 흡착 평형상수 (1단계: 문헌만)

> 에이전트: surface-contamination | 작성일: 2026-09-18
> 선행: [[post-cmp-residual-metal-prediction-langmuir-scm]] [[post-cmp-metallic-contamination-sources]]

## 1. 왜 필요한가

`sim/tier2_physics/competitive_metal_langmuir.py`의 경쟁 Langmuir 함수는 금속마다 K_i를 받는
자리(`metals: {이름: (K_i, C_i_free)}`)가 있지만, 현재 모듈 안에 실제 박혀 있는 문헌값은
**Cr 하나**(K_CR=1e6 L/mol, Loewenstein·Charpin·Mertens 1999 오더값)뿐이다
([[post-cmp-residual-metal-prediction-langmuir-scm]] §2·§7). 이 노트는 Cu·Fe·Co·W(+Co 관련
James&Healy)의 표면 금속흡착 평형상수를 1차 문헌에서 추가 확보한다. **Ru는 확보 실패**
(§8). 이 과제는 문헌 정리만이며, `sim/`는 0줄도 건드리지 않았다.

## 2. 확보 결과 요약

| 금속 | 1차 문헌 | scope --check | 표면 | 상태 |
|---|---|---|---|---|
| Fe | Schindler et al. 1976 | ✓ 허용 | 실리카(Silikagel H) | 확보(조건부 SCM 상수) |
| Cu | Schindler et al. 1976 **+** Sun 2007(기존 노트) | ✓ 허용 (둘 다) | 실리카(Aerosil 200 / TEOS 산화막) | 확보(두 독립 1차, 값이 갈림 — §5) |
| Co | James & Healy 1972 Part I | ✓ 허용 | 실리카(SiO₂) | **부분 확보** — Langmuir/SCM형 K_i가 아니라 다른 정의(§3.3) |
| W | Gustafsson 2003 | ✓ 허용 | 페리하이드라이트(수산화철, **실리카·알루미나 아님**) | 확보하되 표면 불일치 명시(§3.4) |
| Ru | — | — | — | **1차 미확보**(§8) |
| Mn, Al | — | — | — | **미착수**(턴 예산상 조사 안 함, "못 찾음"과 구분해 명시) |

Cr(기존 Loewenstein 1999)까지 포함하면 K_i 문헌표에 **6개 금속 종**(Cr·Fe·Cu·Co·W, Cu는 중복
2건)이 기록된다 — 기존 1개(Cr)에서 실질적으로 **4개 증가**(Fe·Cu·Co·W), Ru는 실패.

## 3. K_i 표 — 정의별로 분리 (섞지 않음, §4 참고)

### 3.1 표 A — Langmuir 사이트경쟁 K_i (기존 노트, 대조용 그대로 인용)
| 금속종 | 흡착체 | pH | 이온세기 | K_i (L/mol) | 정의 | 온도 | 출처 |
|---|---|---|---|---|---|---|---|
| Cr³⁺ | 친수성 화학산화막 Si(100) | 3 (단독실험) | 미기재(희석 HNO₃, 배경전해질 농도 불명) | ≈10⁶ (오더값, 저자 "about") | σ=σ0·K[M]/(1+K_H[H+]+K[M]) (Langmuir 사이트경쟁, Eq.22) | 20 °C | Loewenstein·Charpin·Mertens 1999 |
| H⁺ | 〃 | — | 〃 | K_H≈10³ (오더값, 저자 "probably") | 〃 | 20 °C | 〃 |

이 값은 이미 `sim/tier2_physics/competitive_metal_langmuir.py`의 `K_CR`/`K_H_DEFAULT`와 동일 —
재인용만, 이 노트에서 새로 만든 수치 없음.

### 3.2 표 B — Schindler 1976 조건부 표면착화 상수 *K₁′, *β₂′ (실리카, 25 °C)
반응: `≡SiOH + Mᶻ⁺ ⇌ (≡SiO)M^(z-1)+ + H⁺` (*K₁′), `2≡SiOH + Mᶻ⁺ ⇌ (≡SiO)₂M^(z-2)+ + 2H⁺` (*β₂′).
전위차 ψ=0 근사(Eq.10)를 적용한 **조건부**(intrinsic, 특정 이온세기에서) 상수 — 정의상
무차원(몰분율 비, 미검증 재확인은 §6).

| 금속이온 | 흡착체 | 이온세기(배경전해질) | pH | log*K₁′ | log*β₂′ | 온도 | 출처 |
|---|---|---|---|---|---|---|---|
| Fe³⁺ | Silikagel H (실리카젤, BET 3.72×10⁹ cm²/kg) | 3 M NaClO₄ | 적정범위 −log[H⁺]≈1–8 (단일 pH 아님, 전 구간 적합) | −1.77 (±0.04) | −4.22 (±0.06) | 25 °C | Schindler, Fürst, Dick, Wolf 1976 |
| Cu²⁺ | Aerosil 200 (실리카, BET 1.60×10⁹ cm²/kg) | 1 M NaClO₄ | 〃 | −5.52 (±0.13) | −11.19 (±0.02) | 25 °C | 〃 |

(논문은 Cd²⁺·Pb²⁺도 같은 표에 보유하나 이번 과제 목표 금속(Cu·Fe·Co·W·Ru)에 없어 표에서 뺐다.)

### 3.3 Co — James & Healy (1972) Part I: **Langmuir/SCM형 K_i 미기재** (정의 불일치, 정직 표기)
- 출처: R. O. James, T. W. Healy, "Adsorption of Hydrolyzable Metal Ions at the Oxide–Water
  Interface. I. Co(II) Adsorption on SiO₂ and TiO₂ as Model Systems", *J. Colloid Interface
  Sci.* 40(1), 42–52 (1972), doi:10.1016/0021-9797(72)90172-5 (원문 PDF
  `papers/james1972-jcis-co-adsorption-sio2-tio2-model-systems.pdf`, sci-hub.kr에서 제목·저자·
  DOI 대조 후 확보).
- 이 논문은 등온선(흡착밀도 vs pH·농도)을 Stern–Grahame 이중층 모델로 해석해 **특이흡착
  자유에너지 φ**(Eq.5, Grahame식)만 보고한다 — Loewenstein의 몰농도 기반 질량작용 K_i(L/mol)나
  Schindler의 조건부 표면착화 *K₁′와 **정의가 다르다**(전기이중층 특이흡착 포텐셜이지, 표면
  자리 경쟁이나 배위결합 반응의 평형상수가 아니다). 따라서 **같은 표에 넣지 않는다.**
  - TiO₂ 위 Co²⁺: φ ≈ −5.5, −5.0, −4.1 kcal/mol (각각 10⁻⁵, 10⁻⁴, 10⁻³ M, pH 5.6=PZC 근방).
  - SiO₂ 위 Co²⁺: φ ≈ −2.2 kcal/mol (10⁻²~10⁻⁴ M) — **저자 스스로 "pH 2.0까지의 외삽이라
    불확실하다(unreliable)"고 명시**. 이온세기·배경전해질 농도는 본문에 구체 수치 없음
    (미기재).
  - K_i로 변환 안 함: φ→K 변환은 표면전위 ψ(≠0)와 흡착자리 밀도를 알아야 하는데 이 논문은
    SiO₂ 쪽에서 그 값을 안 준다(TiO₂만 EDL 특성이 잘 맞다고 서술). 환산 근거가 없으므로
    **환산하지 않는다**(작업지시 "환산 근거가 없으면 환산하지 마라").
  - Part III(같은 저자, doi:10.1016/0021-9797(72)90174-9, "열역학 모델")가 ΔG°ads 같은 수치를
    더 줄 가능성이 있지만, sci-hub 접근이 반복 캡차("로봇 확인")로 막혀 **이번 회차에는
    원문을 못 봤다** — 미확보로 남긴다(§8).

### 3.4 W — Gustafsson 2003 DLM 상수 (표면 불일치 명시: 페리하이드라이트, 실리카·알루미나 아님)
- 출처: J. P. Gustafsson, "Modelling molybdate and tungstate adsorption to ferrihydrite",
  *Chem. Geol.* 200(1–2), 105–115 (2003), doi:10.1016/S0009-2541(03)00161-X (원문 PDF
  `papers/gustafsson2003-chemgeo-molybdate-tungstate-ferrihydrite.pdf`, KTH DiVA 리포지토리
  OA).
- ⚠ **이 논문의 흡착체는 신선 페리하이드라이트(수산화철, HFO)다 — 과제가 요구한 "실리카·
  알루미나 표면"이 아니다.** CMP 관련 텅스텐 이온(WO₄²⁻, 음이온!) 흡착 SCM 문헌 중 이번
  탐색에서 primary로 확보 가능했던 것이 이것뿐이었다(§8, OpenAlex/Crossref로 알루미나·실리카
  대상 텅스텐산 흡착 논문을 찾지 못함). **타계(iron oxide) 전이값 — 실리카 표면 예측에
  직접 쓰면 안 된다.**
- 조건: 0.01 M NaNO₃, pH 3–10, 25 °C, 총 Fe 3×10⁻⁴~3×10⁻³ M, WO₄²⁻ 초기농도 50 µM, DLM
  (Dzombak & Morel 1990 diffuse-layer model), FITEQL 4.0 비선형 회귀.
- 반응(Table 2): D4. `≡FeOH + WO₄²⁻ + 2H⁺ ⇌ ≡FeOW(OH)₅ + H₂O` (완전 양성자화 단좌표);
  D6. `≡FeOH + WO₄²⁻ + H⁺ ⇌ ≡FeOHWO₄²⁻ + H₂O` (부분 양성자화).
- log K_D4,INT(가중평균) = **19.31**(총Fe 2개 런에서 수렴 위해 고정, 1개 런만 σ=0.064로 자유적합);
  log K_D6,INT(가중평균) = **6.40**(σ 0.037/0.046/0.13, 3개 런 모두 자유적합) — 단위는 D4가
  [H⁺]⁻² 항을 포함해 D6과 정의(반응식의 H⁺ 차수)가 달라 **두 상수를 서로 비교하면 안 된다**
  (같은 표 안에서도 반응식이 다르면 값을 섞어 해석 금지).
- 정의: DLM intrinsic 상수는 전기이중층 보정(o-plane 전위)을 포함한 질량작용 상수로,
  Schindler의 ψ=0 근사 *K₁′나 Loewenstein의 순수 몰농도 K_i와도 정의가 다르다(§4).

## 4. 정의 통일 검사 (섞으면 안 되는 이유)

| 정의체계 | 반응/식 | 단위 | 전기이중층 처리 | 출처 |
|---|---|---|---|---|
| A. Langmuir 사이트경쟁 K_i | σ=σ0·K[M]/(1+ΣK_j[M_j]) | L/mol | 없음(암묵적으로 무시) | Loewenstein 1999 (Cr) |
| B. Schindler 조건부 *K₁′/*β₂′ | ≡SiOH+M⇌(≡SiO)M+H⁺ | 무차원(몰분율비) | ψ=0 근사(무시, 명시적 근사) | Schindler 1976 (Fe·Cu) |
| B′. Sun 2007 FITEQL pK1/pK2 | 위와 동일 반응식 | 무차원 | 전체 확산이중층(DDL) 적용 | Sun 2007 (Cu, 기존 노트) |
| C. James&Healy 특이흡착 φ | Grahame 식 Γ=2rC exp(−zeφ/kT) | kcal/mol (자유에너지) | Stern-Grahame 이중층 명시 | James&Healy 1972 (Co) |
| D. Gustafsched(Gustafsson) DLM log K_INT | ≡FeOH+WO₄²⁻+nH⁺⇌착물 | (mol/L)⁻ⁿ 질량작용, o-면 전위 보정 포함 | DLM(확산층+정전보정) | Gustafsson 2003 (W) |

**B와 B′는 반응식이 동일**(같은 두 자리 유형)하므로 원칙적으로 같은 표에 넣을 수 있다 —
실제로 §5에서 그렇게 비교한다. **A/B/C/D는 서로 다른 정의라 절대 같은 열에 넣지 않았다**
(표 A·B·3.3·3.4를 분리한 이유).

## 5. Cu K₁ 값이 갈리는 경우 — 평균내지 않고 스코프를 쪼갠다

같은 반응식(≡SiOH+Cu²⁺⇌≡SiOCu⁺+H⁺)에 대해 두 독립 1차 문헌이 다른 log K₁ 값을 준다:

| 문헌 | 흡착체 | 이온세기 | 방법 | log K₁ |
|---|---|---|---|---|
| Schindler 1976 | Aerosil 200 (건식 실리카) | 1 M NaClO₄ | 전위차적정, 선형(y=x) 회귀, ψ=0 근사 | −5.52 |
| Sun 2007 (기존 노트 §4) | TEOS 산화막 | 0.01 M | FITEQL, 확산이중층모델(DDL) 비선형 회귀 | −4.35 |

차이는 1.17 log 단위(≈14.8배) — **작지 않다**. EVIDENCE-RULES에 따라 평균내지 않는다.
근거 서열로는 둘 다 **E2(동일계 폐형식, 대상계이지만 표면제법·전해질이 다름)**로 같은
등급이라 "더 나은 값"을 고를 근거가 없다 — 대신 **원인이 되는 조건 차이를 스코프로
명시**한다:
1. 흡착체 제법이 다르다 — 건식 실리카젤(Aerosil, 열처리 발열 실리카) vs 습식 TEOS 산화막
   (CMP 슬러리 맥락에 더 가까움).
2. 이온세기가 100배 다르다(1 M vs 0.01 M) — Schindler의 ψ=0 근사는 고이온세기에서 더
   타당하지만 Sun은 저이온세기에서 DDL을 정식으로 풀어 전위항을 명시적으로 넣었다.
3. **두 값 다 "표에 넣되 스코프를 분리해서" 기록한다** — CMP 슬러리(저이온세기, 습식 산화막)
   맥락엔 Sun 2007이 더 가깝고, 고염 세정액(예: SC-1, I~수백 mM) 맥락엔 Schindler가 더
   가깝다는 것이 스코프 분리 기준이다.

## 6. 정량 재현 절 (python verify)

```python verify
import math

# ===== (1) Schindler 1976 Table II Fe3+: Eq.16 Z(pH)가 물리적으로 1~2 범위를 벗어나지 않아야 한다 =====
# Z = "흡착된 M당 방출된 H+ 수" — 반응[1](n=1)만 있으면 Z=1, 반응[2](n=2)만 있으면 Z=2.
logK1_Fe, logB2_Fe = -1.77, -4.22   # Table II, Silikagel H, I=3M NaClO4, 25C
K1_Fe, B2_Fe = 10**logK1_Fe, 10**logB2_Fe
Co_silikagel = 3.6  # mol/kg, Silikagel H 총 실라놀 자리 (본문 "Co = 3.6 mole·kg-1")

def Z_fe(pH):
    H = 10**-pH
    return (K1_Fe + 2*B2_Fe*Co_silikagel/H) / (K1_Fe + B2_Fe*Co_silikagel/H)

z_vals = {pH: Z_fe(pH) for pH in (1, 2, 3, 4, 5)}
for pH, z in z_vals.items():
    assert 1.0 <= z <= 2.0, f"pH{pH}: Z={z} 물리적 범위 밖"
assert z_vals[1] < z_vals[2] < z_vals[3] < z_vals[4]   # Fig.2 추세(저pH→고pH, Z 단조증가)와 방향 일치
assert z_vals[1] < 1.2 and z_vals[4] > 1.9              # 저pH에서 반응[1] 지배, 고pH에서 반응[2] 지배
print(f"(1) Schindler Fe Z(pH): {{{', '.join(f'{p}:{v:.3f}' for p,v in z_vals.items())}}} — 1<=Z<=2 만족, 단조증가")

# ===== (2) Cu K1 두 문헌 정량 대조 (평균내지 않음, 차이만 계산) =====
logK1_Cu_schindler = -5.52   # Aerosil 200, I=1M NaClO4
logK1_Cu_sun = -4.35         # TEOS 산화막, I=0.01M, FITEQL (Sun 2007, 기존 노트 §4 pK1=4.35)
diff_log = logK1_Cu_schindler - logK1_Cu_sun
factor = 10**abs(diff_log)
assert 1.0 < abs(diff_log) < 1.5      # "작지 않은 차이" 정량 확인 (평균 금지 판단의 근거)
assert 14 < factor < 16
print(f"(2) Cu log K1: Schindler {logK1_Cu_schindler} vs Sun {logK1_Cu_sun} → 차이 {diff_log:.2f} log단위 ({factor:.1f}배, 원인: 흡착체·이온세기 다름, §5)")

# ===== (3) Gustafsson 2003 Table 4 텅스텐 D6 가중평균 재현 (Dzombak-Morel 오차전파식) =====
vals = [6.60, 6.21, 6.24]     # log K_D6,INT, 3개 총Fe 농도 런
sigmas = [0.037, 0.046, 0.13]
w = [1/s**2 for s in sigmas]
wavg = sum(v*wi for v, wi in zip(vals, w)) / sum(w)
reported = 6.40
diff_pct = abs(wavg - reported) / reported * 100
assert diff_pct < 1.0   # 논문이 명시한 절차(역분산 가중평균)를 0.58% 이내로 재현
print(f"(3) Gustafsson W D6 가중평균 재계산 {wavg:.3f} vs 논문 {reported} → 차이 {diff_pct:.2f}%")

# ===== (4) 정의 단위 확인: A(L/mol, 유한값)과 B(무차원, <1)는 절대 같은 열에 못 들어간다 =====
K_Cr_A = 1e6   # 표 A, Loewenstein, 정의상 L/mol
K1_Cu_B = 10**logK1_Cu_schindler   # 표 B, Schindler, 정의상 무차원 몰분율비
assert K_Cr_A > 1        # A는 몰농도 역수 크기의 값 (L/mol)
assert K1_Cu_B < 1e-4     # B는 조건부 몰분율비이며 ψ=0 근사에서 항상 <<1
print(f"(4) 정의 확인: K_Cr(A)={K_Cr_A:.0e} L/mol (몰농도 스케일) vs *K1'_Cu(B)={K1_Cu_B:.2e} (무차원, 자릿수부터 다름) — 병합 금지 근거")
```

**결과 해석(정직하게)**: (1) Schindler 1976의 Fe³⁺ Table II 상수를 논문 자신의 Eq.16에 넣으면
Z가 저pH 1.11→고pH 1.999로 물리적으로 요구되는 [1,2] 범위 안에서 단조증가한다 — 원문 Fig.2의
정성적 추세(2−Z가 pH 1~3에서 감소)와 방향이 맞는다. Fig.1의 실제 %ads 곡선은 실험별 A/V
스케일 인자(A′)가 본문에 없어 재현하지 못한다(§3.2 한계). (2) Cu의 두 1차 문헌값은 14.8배
차이가 나며 이는 §5에서 결정한 "평균 금지, 스코프 분리"를 정량으로 뒷받침한다. (3) Gustafsson
2003의 텅스텐 D6 가중평균은 저자가 명시한 Dzombak–Morel 역분산 가중평균 절차로 0.58% 이내
재현된다 — 표 3.4의 log K=6.40 값이 창작이 아니라 원문 절차의 산출물임을 확인. (4) 표 A와
표 B의 K는 자릿수 스케일 자체가 다르므로(L/mol 유한값 vs 무차원 몰분율비<<1) 같은 열에 넣는
것 자체가 정의 오류라는 것을 수치로 보인다.

## 7. 2단계에서 아직 없는 것 — 엔진 등록이 안 되는 이유

이 노트는 K_i를 **문헌에서 확보**했을 뿐이다. `competitive_langmuir_surface()`에 넣으려면
`metals: {이름: (K_i, C_i_free)}`의 **C_i_free(금속이온 유리농도, mol/L)**가 필요한데:
- FabSim의 Recipe/팩 스키마에는 슬러리·세정액의 금속이온 농도 필드가 없다
  ([[post-cmp-residual-metal-prediction-langmuir-scm]] §7과 동일한 결론).
- 이번에 확보한 K_i들도 **정의가 서로 다르다**(§4) — 하나의 `competitive_langmuir_surface`
  호출에 표 A(Cr)와 표 B(Fe·Cu)를 그냥 섞어 넣으면 안 된다. 섞으려면 먼저 Schindler류
  조건부 *K₁′를 Loewenstein류 몰농도 K_i로 변환하는 절차가 필요한데, 그 변환에는 흡착자리
  밀도(σ0)와 전위보정(ψ)이 필요하고 지금은 그 변환식 자체가 검증되지 않았다(§3.3에서 φ→K
  변환을 거부한 것과 같은 이유).
- 따라서 2단계는 "C_i_free 스키마 추가"뿐 아니라 "**K_i 정의 변환 절차의 검증**"까지 포함해야
  한다 — 다음 회차가 표만 보고 바로 엔진에 박으면 정의 불일치로 틀린 값이 나온다.

## 8. 정직한 실패·미착수 기록

- **Ru**: OpenAlex·Semantic Scholar(레이트리밋)·Crossref 질의 모두 무관한 논문만 반환
  (예: "Ru(III) 암민착물 메조다공성 실리카 그래프팅" 2003 — 흡착이 아니라 화학적 그래프팅이라
  다른 현상). CMP 맥락의 Ru 표면흡착 SCM 1차 문헌은 **이번 탐색에서 찾지 못했다**
  (Ru CMP 자체가 최근 노드에서야 중요해진 재료라 고전 SCM 문헌 시대(1970~2000년대)와 겹치지
  않을 가능성이 있음 — 이건 추정이며 확인 안 됨).
- **Mn, Al**: 턴 예산상 검색을 시작하지 않았다 ("못 찾음"이 아니라 "미착수"). 다음 회차가
  0에서 다시 찾아야 한다.
- **Co**: 1차 문헌은 확보(James & Healy 1972 Part I)했으나 K_i 정의의 수치가 아니라 다른
  물리량(특이흡착 자유에너지, SiO₂ 값은 저자가 "unreliable"이라 명시)만 있어 **표 B/A와
  나란히 놓을 수 있는 K_i는 미기재**로 남긴다. Part III(열역학 모델, 같은 저자 1972)가
  ΔG°ads류 수치를 더 줄 가능성이 있으나 sci-hub 캡차("로봇 확인")에 반복 차단되어 이번
  회차에는 못 봤다 — **1차 미확보**로 표기(§3.3).
- **W**: 실리카·알루미나 대상 텅스텐산 흡착 SCM 1차 문헌은 찾지 못했다. 확보한 Gustafsson
  2003은 페리하이드라이트(철산화물) 대상이라 **타계 전이값**이며 그대로 실리카 CMP 예측에
  쓰면 안 된다(§3.4에 경고 명시).
- **sci-hub 접근 이력**: `sci-hub.se`/`sci-hub.st`는 이번 세션에서 DNS/연결 실패(HTTP 000),
  `sci-hub.ru`→`sci-hub.kr` 리다이렉트만 응답했고 그마저 연속 요청 시 "로봇 확인"(캡차)에
  걸려 James & Healy Part III·Ru 관련 추가 시도를 포기했다. Schindler 1976과 James 1972
  Part I은 **다운로드 즉시 제목·저자·DOI를 원문 첫 페이지와 대조해 오염 없음을 확인**했다
  (메모리 기록의 sci-hub.kr 오염 사례 경고에 따른 조치).

## 9. 확보 파일

- `papers/schindler1976-jcis-ligand-properties-surface-silanol-fe-cu-cd-pb.pdf` (Fe·Cu SCM)
- `papers/james1972-jcis-co-adsorption-sio2-tio2-model-systems.pdf` (Co, K_i 아닌 φ만)
- `papers/gustafsson2003-chemgeo-molybdate-tungstate-ferrihydrite.pdf` (W, 타계 페리하이드라이트)
- 세 파일 모두 `papers/INDEX.json`에 등록.
