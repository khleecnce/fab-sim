# BTA 억제항 — 평형 흡착상수(K_eq)를 CMP 정상상태 θ에 직접 대입하는 것은 [A] 실측에 의해 정량 반증된다

> 대상: `sim/chemistry.py::_inhibitor_term`, `sim/factors.py::_f_psi`,
> `knowledge/params/cu_h2o2_bta.yaml`의 `inhibitor_dG_ads_kJ`·`inhibitor_strength_k`.
> [[../EVIDENCE-RULES]] §판정 기록 #17
> [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Cu-BTA 막의 XPS·QCM 정량 — 이 노트가 다루는
> "기계적 벗김"의 막 실체가 그쪽에 있다)
> [[inhibitor-chelator-adsorption-isotherm-passivation]] (Langmuir vs Frumkin 등온식·ΔG_ads=−35.4 kJ/mol의
> 원 출처 — 이 노트는 그 값을 CMP 정상상태에 그대로 쓰는 것이 반증됨을 보인다)

## 1. 질문

`_inhibitor_term`(sim/chemistry.py:167)은 BTA 흡착 자유에너지 ΔG_ads(평형값, −35.4 kJ/mol)로부터
Langmuir 흡착상수 K를 구하고, 그 K로 표면 피복률 θ를 계산해 잔여 제거율 = exp(−k·θ)를 만든다.
θ=K·C/(1+K·C)는 **평형** 흡착등온식이다. CMP는 패드·연마입자가 계속 막을 기계적으로 벗겨내는
**정상상태(steady-state)** 공정인데, 평형 K를 그 정상상태 θ에 그대로 대입해도 되는가?
BTA 농도-제거율 실측 문헌 [A]로 이 가정을 직접 시험한다.

## 2. 1차 출처

- **[A]** Len, V.S.C., McNeill, D.W., Gamble, H.S. (2000). "An Evaluation of the Effects of Benzotriazole
  in NH₄OH Slurry for Copper CMP." *MRS Proceedings* 613, E7.4.1.
  DOI: 10.1557/proc-613-e7.4.1. 전문 확보: `papers/kim-mrs613-bta-nh4oh-cu-cmp.pdf`(로컬, 6쪽).
  `tools/scope.py --agent slurry-chemist --check` 결과 ✓ 허용.
- **[B]** PubChem CID 7220 (1H-benzotriazole): C₆H₅N₃, MW 119.12 g/mol. API 직접 조회.
- **[C]** PubChem CID 1018 (picolinic acid): C₆H₅NO₂, MW 123.11 g/mol. API 직접 조회.

## 3. [A]의 실측

조건: 5 vol.% NH₄OH + 2 wt.% α-알루미나(300 nm) + BTA 0.1~0.75 wt.%, 1.75 psi, 플래튼/캐리어
60 rpm, 슬러리 130 mL/min, 4점 프로브 시트저항으로 Cu 제거율 측정. 원문 그대로:

> "Copper polish rate plunges from 400 nm/min to 65 nm/min with the addition of 0.1 wt.% BTA.
>  The change in polish rate as BTA concentration in the slurry is increased above 0.1 wt.% is
>  less significant. At 0.25 wt.% BTA the polish rate has fallen to 42 nm/min, but further
>  increase in BTA concentration has little effect."

| BTA (wt.%) | BTA (mM, MW 119.12, ρ≈1 g/mL) | Cu 제거율 (nm/min) |
|---|---|---|
| 0    | 0      | 400 |
| 0.1  | 8.395  | 65  |
| 0.25 | 20.987 | 42  |
| 0.5  | 41.974 | ~42 ("little effect") |
| 0.75 | 62.962 | ~42 ("little effect") |

이 계는 **알칼리(NH₄OH) + 알루미나** — 산성 H₂O₂+BTA인 `cu_h2o2_bta` 팩과 계가 다르다(§7에서 다룬다).
그러나 "BTA 농도를 올리면 Cu 제거율이 얼마나 떨어지는가"라는 **함수 형태**를 직접 시험할 수 있는 유일한
정량 스윕(n=5, 40배 농도 범위)이라 이 절의 목적(모델 형태 검증)에는 쓸 수 있다.

## 4. 현행 모델 반증(정량)

현행 팩 값: `inhibitor_dG_ads_kJ = -35.4`, `inhibitor_strength_k = 3.0`.
K = `K_from_dG_ads(-35400)` = exp(35400/(8.314462618·298.15))/55.5 = **28676 L/mol**.

이 K에서는 0.1 wt%(8.395 mM)와 0.25 wt%(20.987 mM) 모두 K·C가 235와 587로 커서 θ가 이미 포화한다:
θ(0.1wt%) = 0.99586, θ(0.25wt%) = 0.99834. 모델이 예측하는 두 농도 사이의 제거율 비는

    R(0.25)/R(0.1) = exp(−k·(θ2−θ1)) = exp(−3.0·0.00248) ≈ **0.9926** (0.7% 하락)

실측 비는 42/65 = **0.6462**(35.4% 하락)다. 즉 **모델은 사실상 무변화를 예측하는데 실측은 35%
하락한다** — 두 비 사이의 차이는 34.6퍼센트포인트다. 팩 기준(inhibitor_ref_mM=1.0 mM) 대비 ψ
배수를 0.5~20 mM로 스캔해도 1.0991 → 1.0000 → 0.9515 → 0.9228 → 0.9133 → 0.9086로, **40배
농도 범위에서 배수가 1.2배밖에 움직이지 않는다.**

이것이 정확히 `_inhibitor_term` docstring(sim/chemistry.py:172-186)이 (1−θ) 형태에서 피하려던
실패 모드다 — "2mM과 5mM의 구분이 사라진다." exp(−k·θ)로 (1−θ)의 하한 포화는 피했지만, **θ 자체가
K가 너무 커서 포화**해 있어 같은 고장이 K 쪽에서 재발한 것이다. 약한 고리는 k가 아니라 K였다.

## 5. 물리 해석 — K_eq vs K_eff

ΔG_ads = −35.4 kJ/mol은 **정적 평형** 흡착 자유에너지다([[inhibitor-chelator-adsorption-isotherm-passivation]]
경로로 도입된 값). CMP 중에는 패드·연마입자가 Cu-BTA 막의 형성 속도와 경쟁하며 기계적으로 벗겨낸다
— [A] 원문: "the polish pad and the abrasives in the slurry try to mechanically abrade away this
monolayer as soon as it forms." 정상상태 피복률은 형성/제거 경쟁으로 정해지므로, 유효 흡착상수는
평형값보다 작아야 한다:

    θ_ss = K_eff·C/(1+K_eff·C),   K_eff ≈ K_eq / (1 + k_abrade/k_desorb)

K_eff < K_eq는 "없는 항을 만든 것"이 아니라, 지금까지 `_inhibitor_term`에 없던 **기계적 제거항을
명시적으로 인정**한 결과다. 아래 §6에서 [A]의 두 점으로 이 K_eff를 역산한다.

이 형성/제거 경쟁 프레임은 Cu-BTA 막의 QCM 형성 속도론을 직접 실측한 Tamilmani (2005)의 관찰
([[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §1에서 이미 확보·인용)과도 정합적이다 —
그 학위논문은 Cu-BTA 막이 유한한 형성 속도를 가진다는 것을 QCM으로 직접 보여, "막이 형성되는
족족 기계적으로 벗겨진다"는 [A]의 정성 서술이 임의의 가정이 아니라 독립적으로 관측된 속도론과
부합함을 뒷받침한다.

## 6. 역산값과 플래토 미재현(모델 한계)

**k=3.0 고정, 0.1 wt% 점(65/400=0.1625)으로 K_eff 역산** (Langmuir 역산은 닫힌 형이다):
θ_target = −ln(0.1625)/3.0 = 0.60569, K_eff = θ/(C·(1−θ)) = **182.98 L/mol**.
0.25 wt%에서 예측 제거율 = 400·exp(−3.0·θ(20.987mM, K=183)) = **37.01 nm/min**, 실측 42 대비
**−11.87%** 편차. K_eq/K_eff = 28676/183 = 156.7 → 함의: k_abrade/k_desorb ≈ 156.

**(K, k) 2점 동시 피팅**(0.1wt%·0.25wt% 두 점을 정확히 재현하는 해, 수치해): K_eff = **249.73 L/mol**,
k = **2.684**. 두 점(0.1625, 0.105)을 소수점 이하까지 정확히 재현한다. 이 K로 역환산한
dG_ads = −R·T·ln(55.5·K) = **−23.64 kJ/mol**(팩 값 −35.4보다 약함 — 물리흡착 영역 안쪽이지만 더 약한
쪽). K_eq/K_eff = 28676/249.73 = 114.8 → k_abrade/k_desorb ≈ 115.

**⚠ 두 해 모두 0.5·0.75 wt% 플래토를 재현하지 못한다(Len 2000 §10 역산).** k=3.0 고정 해는
0.5 wt%에서 28.14 nm/min, 0.75 wt%에서 25.31 nm/min을 예측한다. 2점 피팅 해는 각각
34.51 / 32.08 nm/min을 예측한다. 실측(Len 2000)은 둘 다 ~42 nm/min으로 **평평**하다 — 두 해
모두 계속 감소를 예측하는데 실측은 멈춘다. Langmuir
θ와 exp(−k·θ)의 조합 자체가 **하한(floor)이 없는 함수형**이라 이 플래토를 구조적으로 못 만든다.
[A]는 이 플래토를 "제거가 거의 전적으로 기계적이 됨"으로 설명한다 — 화학 기여가 0으로 수렴하는
**기계적 하한(mechanical floor)**이 있다는 뜻이고, 현행 곱셈형 ψ(하한 없이 0으로 계속 갈 수 있는
구조)에는 이 하한 항이 없다. **이것은 이번 회차에 고치지 않는다** — 모델 한계로 기록만 한다.

## 7. 계 불일치 — 왜 이식하지 않는가

[A]는 **알칼리(NH₄OH) + 알루미나** 계다. `cu_h2o2_bta` 팩은 **산성 H₂O₂ + BTA** 계다. pH는
Cu-BTA 막 형성(Cu(I)-BTA 착물의 안정 pH 영역)과 BTA 자체의 프로톤화(약염기성 질소, pKa~1·8 부근
헤테로고리)에 직접 영향을 준다. 따라서 [A]에서 역산한 K_eff(183 또는 249.7 L/mol)의 **절대값을
산성계로 이식하는 것은 정당화되지 않는다.**

EVIDENCE-RULES.md 서열로 매기면: [A]는 대상 계(Cu+BTA)의 직접 실측이지만 pH·연마입자가 팩과
달라 **E3**(대상계 실측이지만 교란/불일치 있음)다. 반면 팩의 현재 ΔG=−35.4 kJ/mol 경로는 애초에
문헌 폐형식 없이 도입된 값(평형 흡착값을 정상상태에 대입)이라 이번 반증 이전부터 **검증되지 않은
경로**였다. E3인 [A]가 "이 경로(K_eq를 그대로 씀)가 깨졌다"는 것을 보여주는 데는 충분하지만,
"올바른 K_eff 값이 183(또는 250)이다"라고 결론짓는 데는 부족하다 — 그러려면 산성 H₂O₂+BTA 계의
직접 실측(E1/E2)이 필요하다. 그러므로 이번 판정은 **"K_eq 경로가 반증됐다"까지**이며, K_eff 값
자체는 채택하지 않는다.

## 8. 과제 B: 피콜린산 wt%→몰농도

`w_fe_oxidizer.yaml`의 `inhibitor_mM=121.8`(1.5 wt% 피콜린산 포화 농도)의 근거를 MW로 재검산한다.
피콜린산(picolinic acid, PubChem CID 1018) MW = 123.11 g/mol([C]).

    wt%→mM 환산: C[mM] = (wt%/100)·ρ[g/mL]·1000 / MW · 1000

| ρ (g/mL) | 계산 몰농도 (mM) |
|---|---|
| 0.995 | 121.23 |
| 1.000 | **121.84** |
| 1.005 | 122.45 |
| 1.010 | 123.06 |

팩 값 121.8 mM은 ρ=1.000 계산값 121.84와 **−0.03% 차이**로 사실상 일치한다
([[w-cmp-picolinic-acid-inhibitor-langmuir-dissolution-suppression]] 원 팩 값 대조). 1.5 wt%는
희박수용액 영역이라 밀도를 0.995~1.010으로 흔들어도(1.5% 밀도 불확실성) 몰농도는 121.23~123.06 mM
(ρ=1.000 기준 −0.5%~+1.0%)로만 움직인다 — ψ 계산에서 무시할 수 있는 크기다.

⚠ 단 `w_fe_oxidizer.yaml`은 `inhibitor_ref_mM == inhibitor_mM == 121.8`이라 **이 팩의 ψ 배수는
항상 정확히 1.0이다** — 지금 이 문서화가 바꾸는 것은 "121.8이라는 숫자가 MW 환산으로 재현되는가"
뿐이고, 실제 시뮬레이션 결과(다른 농도를 넣지 않는 한)에는 아무 영향이 없다. 이 환산 정확도는
**다른 피콜린산 농도를 시뮬레이션할 때만** 의미를 갖는다.

## 9. 결론과 다음 단계

- **cu_h2o2_bta.yaml**: `inhibitor_dG_ads_kJ`(=−35.4)는 값 자체는 유지하되(평형 ΔG로는 여전히
  유효할 수 있음 — 이 값을 반증한 것이 아니라 "이 값을 CMP 정상상태 θ에 그대로 대입하는 경로"를
  반증했다), confidence를 **verified → estimated로 강등**한다. `inhibitor_strength_k`(=3.0,
  unverified)는 값을 바꾸지 않는다 — §4~6에서 약한 고리로 판명된 것은 k가 아니라 K이기 때문에
  k를 건드릴 근거가 없다.
- **w_fe_oxidizer.yaml**: `inhibitor_mM`(=121.8)은 confidence를 **estimated → literature로 승격**한다
  — MW(PubChem CID 1018, 123.11 g/mol) 환산이 −0.03% 오차로 팩 값을 재현하고([[w-cmp-picolinic-acid-inhibitor-langmuir-dissolution-suppression]]),
  밀도 불확실성의 영향도 ψ 계산에서 무시 가능한 크기임을 확인했다.
- **미확보/다음 과제**: 산성 H₂O₂+BTA 계에서 BTA 농도-제거율 직접 스윕(K_eff 실측)은 이번 회차에
  확보하지 못했다. 확보되면 `inhibitor_K_eff_L_per_mol`이라는 새 파라미터로 ΔG 경로와 분리해
  도입하고, §6의 플래토(기계적 하한) 항 도입도 함께 검토해야 한다(§구현 요청, agents/slurry-chemist/PROFILE.md).

## 10. 검증 (코드)

```python verify
import sys, math
sys.path.insert(0, ".")
sys.path.insert(0, "sim/tier2_physics")
import slurry_components as SC
from scipy.optimize import fsolve

MW_BTA = 119.12  # g/mol, PubChem CID 7220
MW_PICOLINIC = 123.11  # g/mol, PubChem CID 1018

def wt_to_mM(wt_pct, MW, rho=1.0):
    return wt_pct / 100.0 * rho * 1000.0 / MW * 1000.0

# (a) MW 119.12로 0.1/0.25 wt% -> mM 환산
c01 = wt_to_mM(0.1, MW_BTA)
c025 = wt_to_mM(0.25, MW_BTA)
assert abs(c01 - 8.395) < 0.01, f"0.1wt%->{c01:.3f}mM"
assert abs(c025 - 20.987) < 0.01, f"0.25wt%->{c025:.3f}mM"

# (b) 팩 현재값 dG=-35.4 kJ/mol -> K_eq
dG_pack = -35.4e3
K_eq = SC.K_from_dG_ads(dG_pack)
assert abs(K_eq - 28676) < 5, f"K_eq={K_eq:.1f}, 예상 ~28676 L/mol"

# (c) 현행 파라미터(K_eq, k=3.0)의 예측비 vs 실측비 — 불일치를 assert한다
k_pack = 3.0
C1, C2 = c01 * 1e-3, c025 * 1e-3
theta1 = SC.langmuir_coverage(C1, K_eq)
theta2 = SC.langmuir_coverage(C2, K_eq)
pred_ratio = math.exp(-k_pack * (theta2 - theta1))
obs_ratio = 42.0 / 65.0
assert abs(pred_ratio - 0.9926) < 0.001, f"pred_ratio={pred_ratio:.4f}"
assert abs(obs_ratio - 0.6462) < 0.001, f"obs_ratio={obs_ratio:.4f}"
gap_pp = (pred_ratio - obs_ratio) * 100
assert gap_pp >= 30, (
    f"현행 K_eq 예측비({pred_ratio:.4f})와 실측비({obs_ratio:.4f})의 차이가 "
    f"{gap_pp:.1f}pp로 30pp 미만 — 반증이 성립하지 않는다")

# (d) k=3.0 고정, 0.1wt%(65/400) 점으로 K_eff 역산 (Langmuir 역산은 닫힌 형)
r1 = 65.0 / 400.0
theta1_target = -math.log(r1) / k_pack
K_eff_fixed_k = theta1_target / (C1 * (1 - theta1_target))
assert abs(K_eff_fixed_k - 182.98) < 0.5, f"K_eff={K_eff_fixed_k:.2f}"

def residual(C, K, k):
    return math.exp(-k * SC.langmuir_coverage(C, K))

pred_025 = 400.0 * residual(C2, K_eff_fixed_k, k_pack)
assert abs(pred_025 - 37.01) < 0.05, f"0.25wt% 예측={pred_025:.2f}"
dev_pct = (pred_025 - 42.0) / 42.0 * 100
assert abs(dev_pct - (-11.87)) < 0.1, f"편차={dev_pct:.2f}%"

# (e) (K,k) 2점 동시 피팅 — 0.1wt%·0.25wt% 두 점을 정확히 재현
r2 = 42.0 / 400.0

def eqs(x):
    K, k = x
    return [residual(C1, K, k) - r1, residual(C2, K, k) - r2]

(K_fit, k_fit), info, ier, msg = fsolve(eqs, [200.0, 3.0], full_output=True)
assert ier == 1, f"2점 피팅 미수렴: {msg}"
assert abs(K_fit - 249.73) < 0.5, f"K_fit={K_fit:.2f}"
assert abs(k_fit - 2.684) < 0.005, f"k_fit={k_fit:.4f}"
assert abs(residual(C1, K_fit, k_fit) - r1) < 1e-6
assert abs(residual(C2, K_fit, k_fit) - r2) < 1e-6

dG_fit = SC.dG_ads_from_K(K_fit)
assert abs(dG_fit / 1000.0 - (-23.64)) < 0.05, f"dG_fit={dG_fit/1000:.2f} kJ/mol"

# (f) 플래토 미재현: 두 해 모두 0.5wt% 예측이 실측(~42)보다 낮다
c05 = wt_to_mM(0.5, MW_BTA) * 1e-3
pred_k3_05 = 400.0 * residual(c05, K_eff_fixed_k, k_pack)
pred_2pt_05 = 400.0 * residual(c05, K_fit, k_fit)
assert pred_k3_05 < 42.0, f"k=3.0 고정 해가 플래토를 재현하면 안 된다: {pred_k3_05:.2f}"
assert pred_2pt_05 < 42.0, f"2점 피팅 해가 플래토를 재현하면 안 된다: {pred_2pt_05:.2f}"

# (g) 피콜린산 MW 123.11로 1.5wt% -> mM, 밀도 밴드
c_picolinic = wt_to_mM(1.5, MW_PICOLINIC, rho=1.000)
assert abs(c_picolinic - 121.84) < 0.01, f"picolinic 1.5wt%->{c_picolinic:.2f}mM"
pack_dev_pct = (121.8 - c_picolinic) / c_picolinic * 100
assert abs(pack_dev_pct) < 0.1, f"팩값 121.8 vs 계산값 {c_picolinic:.2f} 괴리 {pack_dev_pct:.3f}%"

band = [wt_to_mM(1.5, MW_PICOLINIC, rho=r) for r in (0.995, 1.000, 1.005, 1.010)]
max_dev_pct = max(abs((b - c_picolinic) / c_picolinic * 100) for b in band)
assert max_dev_pct < 1.5, f"밀도밴드 최대편차 {max_dev_pct:.2f}% — ψ 계산에 무시 못할 크기"

print(f"OK: K_eq={K_eq:.0f} L/mol 예측비({pred_ratio:.4f}) vs 실측비({obs_ratio:.4f}) "
      f"gap={gap_pp:.1f}pp — 현행 K_eq 경로 반증.")
print(f"k=3.0 고정 역산 K_eff={K_eff_fixed_k:.1f} (dev {dev_pct:.1f}%), "
      f"2점 피팅 K={K_fit:.1f}/k={k_fit:.3f}(dG={dG_fit/1000:.1f}kJ/mol) — "
      f"둘 다 0.5wt% 플래토(관측 ~42) 미재현: {pred_k3_05:.1f}/{pred_2pt_05:.1f} nm/min.")
print(f"피콜린산: {c_picolinic:.2f} mM (팩값 121.8, {pack_dev_pct:.2f}% 괴리), "
      f"밀도밴드 최대편차 {max_dev_pct:.2f}%.")
```

## 11. 미확보·한계 (정직 표기)

- 산성 H₂O₂+BTA 계의 BTA 농도-제거율 직접 스윕 실측은 **미확보**다 — [A]는 알칼리+알루미나 계라
  K_eff 절대값의 근거로 쓸 수 없다(§7).
- §6의 두 K_eff 역산(183·249.7)은 [A]의 데이터로부터 나온 값이며, cu_h2o2_bta 팩에는 **채택하지
  않는다**(계 불일치). 참고용으로만 남긴다.
- Langmuir θ + exp(−k·θ) 함수형은 §6에서 확인한 대로 0.5·0.75 wt%의 관측 플래토를 구조적으로
  재현하지 못한다 — 기계적 하한(mechanical floor) 항이 모델에 없다는 뜻이며, 이번 회차에는 이
  항을 도입하지 않는다(코드 변경 없음, 문서화만).
- [A]의 4점 프로브 시트저항 기반 제거율 측정은 저자가 정밀 오차막대를 보고하지 않아, "little
  effect"·"~42 nm/min"의 정밀도는 원문 서술 수준(추정)이다.
- `inhibitor_mM`(w_fe_oxidizer)의 승격은 "121.8이라는 값이 맞다"에 대한 것이지, Lee & Seo(2022)
  원 실험의 wt%→mol/L 환산에 쓰인 실제 밀도가 정확히 1.000 g/mL이었는지는 원문에 명시되지 않아
  여전히 **근사**다(밴드가 작다는 것만 이번에 확인했다).

## 12. 자기시험

1. 현행 팩(ΔG=−35.4 kJ/mol, k=3.0)이 예측하는 0.1→0.25 wt% 제거율 비와 [A]의 실측 비는 각각
   얼마이고, 몇 퍼센트포인트 차이나는가?
   → 예측 0.9926, 실측 0.6462, 약 34.6pp 차이.
2. 이 반증에서 "약한 고리"로 지목된 것은 k인가 K인가? 왜 k를 건드리지 않는가?
   → K(흡착상수)다. k=3.0 고정만으로도 K를 183으로 낮추면(Len 2000 §6 역산) 0.1/0.25 wt% 두 점
   중 한쪽을 정확히, 다른 쪽을 −11.9% 오차로 재현한다 — k를 바꿀 필요가 없었다.
3. K_eff(183 또는 249.7)를 `cu_h2o2_bta.yaml`에 즉시 채택하지 않는 이유는?
   → [A]가 알칼리(NH₄OH)+알루미나 계이고 팩은 산성 H₂O₂+BTA 계라 pH·화학이 다르다(E3, 계 불일치) —
   "K_eq 경로가 틀렸다"까지는 보여주지만 "올바른 값이 이것이다"는 보여주지 못한다.
4. Langmuir+exp(−k·θ) 모델의 구조적 한계는 무엇이며, [A]는 그 물리적 원인을 뭐라고 설명하는가?
   → 하한(floor)이 없어 고농도에서도 계속 감소를 예측하지만 실측은 평평(plateau)하다. [A]는
   고농도에서 "제거가 거의 전적으로 기계적이 됨"으로 설명한다 — 화학 기여가 0으로 수렴하는
   기계적 하한이 있다는 뜻.
5. w_fe_oxidizer의 `inhibitor_mM` 승격이 실제 시뮬레이션 결과를 바꾸는가?
   → 아니다. `inhibitor_ref_mM == inhibitor_mM`이라 ψ 배수는 항상 1.0이다 — 승격은 "이 팩이
   다른 피콜린산 농도로 재계산될 때 쓸 환산식의 신뢰도"에 대한 것이다.
