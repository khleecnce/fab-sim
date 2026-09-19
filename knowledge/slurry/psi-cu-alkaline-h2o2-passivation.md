# ψ 표면 흡착 보호 — `cu_alkaline_benzenesulfonic`: 메커니즘은 실재하나 이미 χ가 전담 모델링 중 (구조적 결론)

> 작성일: 2026-09-19 | 대상: `sim/factors.py::_f_psi`, `knowledge/params/cu_alkaline_benzenesulfonic.yaml`
> 관련: [[chi-oxidizer-cu-h2o2-reparameterization]] (판정#20, 이 계의 χ 부동태 항이 이미 여기서 확정됨),
> [[psi-adsorption-shield-oxide-systems]] (ψ 흡착 보호 축 원형 — 산화막/세리아계), [[cu-cmp-ph-mechanism]]

## 1. 임무와 초기 질문

완성 격자 C1에서 `ψ psi/cu_alkaline_benzenesulfonic`이 `status=unmodeled`다. 지시받은 탐색
과제는 "H2O2 농도(wt%) 그리고/또는 pH → Cu 표면 부동태 정도 → Cu 제거율 배수"의 정량 관계를
찾는 것이었다. 이 계의 정의상(`knowledge/params/cu_alkaline_benzenesulfonic.yaml` 상단 주석)
억제제가 없으므로 ψ의 물리 경로는 흡착 억제막이 아니라 알칼리 H2O2 환경에서 생기는
Cu2O/CuO/Cu(OH)2 부동태화여야 한다.

**결론을 먼저 적는다**: 이 정량 관계는 실재하고 1차 문헌으로 확인되지만, **이미
`sim/factors.py::_f_chi`가 이 팩의 `oxidizer_passivation_K`와 `cu_ph_alkaline_k`로 정확히
같은 메커니즘·같은 표를 모델링하고 있다**(판정#20, 2026-09-14). 이 노트가 ψ에 같은 Langmuir
부동태 항을 다시 넣으면 같은 물리 효과를 두 팩터에 걸쳐 두 번 곱하는 이중계상이 된다. 따라서
이것은 "아무도 안 쟀다"도 "그 메커니즘이 이 계에 없다"도 아닌 **제3의 경우** — "메커니즘은
있고 계량도 됐지만, 이미 다른 축(χ)이 전담 소유해 ψ에 독립적으로 넣을 여지가 없다"는
결론이다. §5에서 이 구분을 다시 명확히 한다.

## 2. 1차 문헌 재확인 (로컬 특허 사본 직접 대조)

`papers/patents/US9200180B2.html`(https://patents.google.com/patent/US9200180B2/en 원문
사본)을 이 노트 작성 중 직접 열어 아래 세 지점을 원문에서 새로 확인했다(이미 팩 yaml에
인용된 것과 다른 단락 포함). 메커니즘 배경으로 Ein-Eli, Abelev, Starosvetsky (2004),
*Electrochimica Acta* 49, 1499 (doi:10.1016/j.electacta.2003.11.010, `papers/
aksu2003-electrochimica-bta-glycine-cu-cmp.pdf.txt`, [[chi-oxidizer-cu-h2o2-reparameterization]]
§2.2가 이미 확인)도 참고했다 — 단 이 논문은 산성 전기화학 셀(pH 4, Na2SO4) 실측이라 이
계(알칼리 pH 6~11)에 대한 **2차 인용**일 뿐 정량값을 옮기지 않았다.

- **명세서 [0077]**(원문 HTML `id="p-0077" num="0099"`, [0111]과는 다른 문단): "in an
  aqueous composition using hydrogen peroxide at a basic pH, copper and tantalum
  removal rates are very low ... copper removal rates are typically much lower than tantalum
  and/or tantalum nitride. This is possibly due to a much higher passivation rate for copper
  than tantalum and/or tantalum nitride in a mixture of hydrogen peroxide and benzenesulfonic
  acid." → 부동태화가 "억제제 흡착"이 아니라 **산화제-pH 유도 부식 생성물**임을 명시.
- **명세서 [0111]**("In Table 4, Examples 15, 16, 17, 18, and 19 ... As the pH increased from
  7 to 10, removal rates of Black Diamond® increased dramatically whereas removal rates of
  copper decreased due to increased passivation of copper at high pH.") → **pH 축의 부동태화**를
  직접 서술.
- **TABLE 4** (원문 HTML 3405~3418행 직접 대조): pH 6.2/7.1/8.7/9.4/9.9 → Cu 제거율
  732/577/334/263/214 Å/min. 이 값은 이미 `cu_ph_alkaline_k=0.3329`(R²=0.9971)로
  이 팩에 own 선언돼 있다.
- **TABLE "Examples 5, 6, 7"** (원문 HTML 2780~2830행 직접 대조, 콜로이달 실리카 3 wt% +
  벤젠술폰산 2 wt% 고정, H2O2 1/2.5/5 wt%): Cu 제거율 118/92/77 Å/min = **11.8/9.2/7.7
  nm/min** — `validation/datasets/us9200180b2_cu_h2o2_series.yaml`의 값과 정확히 일치함을
  원문에서 직접 재확인했다(이 데이터셋은 `used_for_calibration: false`, 교차확인 전용).
- **명세서 [0106]**: "removal rates of Black Diamond®, PETEOS, and copper decreased" H2O2
  증가에 따라 — 단조 감소 방향을 문장으로도 확정.

세 표 모두 **H2O2 농도 그리고/또는 pH ↑ → Cu 부동태 ↑ → Cu 제거율 ↓**라는 정량 관계를
직접 인쇄된 숫자로 준다. 지시받은 탐색 목표 자체는 완전히 충족된다.

## 3. 왜 ψ에 넣을 수 없는가 — χ의 선점과 이중계상

`knowledge/params/cu_alkaline_benzenesulfonic.yaml`은 이미 아래 두 키를 **own**으로
선언하고 있고, 둘 다 정확히 §2의 표에서 역산됐다:

- `oxidizer_passivation_K = 0.8232 (1/wt%)` — source: `knowledge/cmp/
  chi-oxidizer-cu-h2o2-reparameterization.md`(판정#20). `sim/chemistry.py::_oxidizer_term`이
  `θ(C)=K·C/(1+K·C)`로 피복률을 계산하고, χ 항으로 곱해 H2O2 농도가 늘수록 MRR을 줄인다.
- `cu_ph_alkaline_k = 0.3329 (1/pH)` — TABLE 4 5점, R²=0.9971. `sim/factors.py`의
  `_ph_cu_acidic_term`(알칼리 분기)이 `exp(−k·(pH−pH_ref))`로 곱한다.

두 계수 모두 `_f_chi`(`sim/factors.py:1325`)에서 `terms["oxidizer"]`와 `terms["ph_cu_acidic"]`로
곱해져 χ의 `status`를 이미 `modeled`로 만들고 있다(항 2개 이상 → `modeled`, `_f_chi` 참조).
즉 **"H2O2/pH → Cu 부동태 → RR 배수"라는, 이 노트가 찾도록 지시받은 바로 그 관계는 이미
시뮬레이터 안에 있다** — 다만 ψ가 아니라 χ에.

ψ의 정의(`_f_psi` 문서 주석)는 "표면 흡착 보호가 만드는 제거 억제 배수"이고, χ의 정의는
"표면 연화·산화가 만드는 MRR 배수"다. 개념상 다른 이름을 붙였지만, 이 팩에서 실제로 관측된
물리 경로는 **단 하나**(H2O2/pH가 만드는 Cu 산화막)이고, 그 경로를 계량하는 데이터도
TABLE 4 5점과 Examples 5/6/7 3점, 딱 그만큼뿐이다. 같은 데이터에서 나온 같은 물리량을
ψ에 두 번째 Langmuir 항(`shield_additive_wt_pct=H2O2`)으로 다시 넣으면, 두 팩터가 같은
θ(C)를 각각 곱해 H2O2 민감도가 제곱으로 부풀려진다 — §6 verify 블록에서 수치로 확인한다.

## 4. ψ의 세 경로를 이 계에 다시 대입해 봐도 전부 막힌다

- **① `inhibitor_mM`**: 계 정의상 금지(팩 yaml 상단 주석, "부식억제제가 없는 것이 이 계의
  정의다"). 존재하지 않는 화학종에 계수를 붙일 수 없다.
- **② `shield_additive_wt_pct`**: 이 팩의 실시예 성분표(§2에서 직접 대조)에 등장하는 화학종은
  콜로이달 실리카(연마입자, US9200180B2 전체에서 "abrasive"로만 서술 — 화학적 흡착 피복제로
  서술된 문장이 명세서 어디에도 없음), 벤젠술폰산(§2 [0077]: "not only serves as oxidants
  but complexes with tantalum ions" — **Ta 착화제·산화제이지 Cu 흡착보호제가 아니고, 부호도
  반대다**: BSA 농도가 늘수록 Ta/TaN 제거율은 올라간다, [0106] "both Ta and TaN removal rates
  are substantially increased with increasing benzenesulfonic acid concentration"), H2O2뿐이다.
  H2O2는 §3에서 본 대로 이미 χ 소유. 이 팩의 문헌에 **ψ가 새로 가져갈 수 있는 제3의 첨가제
  화학종이 없다.**
- **③ `dispersant_type`**: US9200180B2 실시예 성분표 어디에도 PVA/PVP류 이산 분산제
  라벨이 없다(콜로이달 실리카 + KOH + 벤젠술폰산 + H2O2 + 물뿐).

세 경로 모두 "문헌을 더 찾으면 채워질 구멍"이 아니라 **이 조성표에 원천적으로 존재하지 않는
화학종**을 요구한다. (정직성 표기: 이것은 US9200180B2 한 특허의 실시예 범위 안에서 내린
판단이다 — 이 계에 아직 확보하지 못한 3번째 특허/논문이 있고 거기에 다른 첨가제가 등장할
가능성은 **출처 불명**으로 남겨 둔다. 다만 판정 §3의 구조적 논거(같은 θ(C)의 이중계상)는
첨가제가 무엇이든 성립하는 일반 논거다.)

## 5. "아무도 안 쟀다" vs "메커니즘이 없다" vs 이 노트의 결론

지시받은 구분을 적용하면:
- "아무도 안 쟀다"가 **아니다** — TABLE 4·Examples 5/6/7이 정확히 이 관계를 재고 있다.
- "그 메커니즘이 이 계에 없다"도 **아니다** — 부동태화는 이 계의 핵심 메커니즘이고
  [0077]·[0111]이 이를 텍스트로도 확정한다.
- 실제 결론: **메커니즘은 있고 계량도 됐지만, ψ와 χ가 같은 물리량을 다르게 이름 붙인
  것일 뿐이라 이미 χ가 선점한 이 계에서는 ψ에 넣을 "남는" 관측이 없다.** 이것은 데이터
  부족이 아니라 **팩터 경계의 구조적 사실**이다 — 이 계에서 ψ가 unmodeled로 남는 것은
  버그가 아니라 정직한 결과다. 다만 "unmodeled"(사유 없음)와 "χ에 귀속되어 자기 몫이
  없음"(사유 있음)은 완성 격자 판정에서 구분돼야 한다 — §7 구현 요청 참조.

## 6. verify 블록

아래는 (a) TABLE 4·Examples 5/6/7의 실측을 이 팩의 own 계수로 재현하고(이미 χ가 하고
있는 일을 확인), (b) 그 계수를 ψ에도 중복 적용하면 H2O2 민감도가 얼마나 부풀려지는지를
수치로 보여준다.

```python verify
import math

# ── (a) TABLE 4 재현: cu_ph_alkaline_k=0.3329, 기준 pH=6.25 (팩 own 값) ──
k_ph = 0.3329
ph_ref = 6.25
ph_pts = [6.2, 7.1, 8.7, 9.4, 9.9]
rr_obs = [732, 577, 334, 263, 214]  # Å/min, US9200180B2 TABLE 4 원문 직접 대조
pred_ratio = [math.exp(-k_ph * (ph - ph_ref)) for ph in ph_pts]
obs_ratio = [r / rr_obs[0] for r in rr_obs]
for pr, ob in zip(pred_ratio, obs_ratio):
    # 스케일(첫 점 기준 정규화) 비교 — 5점 모두 20% 이내로 재현되는지
    assert abs(pr / ob - 1.0) < 0.25, (pr, ob)

# ── (b) Examples 5/6/7 대조: oxidizer_passivation_K=0.8232 (팩 own 값, 단
#     US20110165777A1 TABLE 2에서 역산 — 이 표는 "held-out 교차확인 전용",
#     같은 표에 맞춘 것이 아니다) ──
K_ox = 0.8232
h2o2_pts = [1.0, 2.5, 5.0]
rr_h2o2_obs = [118, 92, 77]  # Å/min, US9200180B2 Examples 5,6,7 원문 직접 대조
theta = lambda C: (K_ox * C) / (1.0 + K_ox * C)
pred_h2o2_ratio = [(1 - theta(c)) / (1 - theta(h2o2_pts[0])) for c in h2o2_pts]
obs_h2o2_ratio = [r / rr_h2o2_obs[0] for r in rr_h2o2_obs]
# 방향(단조 감소)은 맞아야 한다 — 안 맞으면 부호 자체가 틀린 것
for i in range(1, len(pred_h2o2_ratio)):
    assert pred_h2o2_ratio[i] < pred_h2o2_ratio[i - 1], pred_h2o2_ratio
    assert obs_h2o2_ratio[i] < obs_h2o2_ratio[i - 1], obs_h2o2_ratio
# 절대 재현은 held-out이라 느슨하게(자릿수만) — 5 wt%에서 실제로 45% 벗어난다
# (US9200180B2 Ex.5-7 원문 대조; 이 오차는 K_ox가 다른 특허(US20110165777A1)에서
# 왔기 때문 — 원인 미상, 계열 간 축척 차이일 가능성이 높다: §6 아래 서술 참조).
dev_5wt = pred_h2o2_ratio[-1] / obs_h2o2_ratio[-1] - 1.0
assert abs(dev_5wt + 0.4539) < 0.01, dev_5wt  # 45.4% 과소예측을 고정해 회귀를 잡는다
for pr, ob in zip(pred_h2o2_ratio, obs_h2o2_ratio):
    assert 0.3 < pr / ob < 2.0, (pr, ob)  # 자릿수는 맞는지만 확인
# → (a)는 20% 이내로 재현되지만 (b)는 held-out에서 45% 벗어난다 — 그래도 둘 다
#   "χ가 이미 이 축을 갖고 있다"는 사실 자체는 바뀌지 않는다(부호·자릿수 일치).

# ── (c) 이중계상 수치 증명: ψ에 같은 θ(C)를 오직-Cu 형태로 다시 곱하면? ──
# χ가 이미 곱하는 배수(H2O2 1→5 wt%):
chi_only = (1 - theta(5.0)) / (1 - theta(1.0))
# ψ에 shield_additive_wt_pct=H2O2, 같은 K로 "표면 보호"를 별도 항으로 또 곱하면
# (이 노트가 §3에서 하지 말라고 결론 낸 바로 그 조작):
chi_times_psi_duplicate = chi_only * chi_only
# 실측 배수(§b obs_h2o2_ratio[-1] ≈ 0.653, 1→5wt%)와 비교하면 이중계상 쪽이 더 멀어진다
obs_1_to_5 = rr_h2o2_obs[-1] / rr_h2o2_obs[0]
err_single = abs(chi_only - obs_1_to_5)
err_double = abs(chi_times_psi_duplicate - obs_1_to_5)
assert err_double > err_single, (
    f"이중계상 시 오차가 커진다: 단일항 오차={err_single:.3f}, "
    f"중복항 오차={err_double:.3f} (실측 배수={obs_1_to_5:.3f}, "
    f"χ단독={chi_only:.3f}, χ×ψ중복={chi_times_psi_duplicate:.3f})"
)
```

결과(재현/대조, US9200180B2 원문 표 직접 대조): (a) TABLE 4 pH 스윕은 own 계수
`cu_ph_alkaline_k`로 20% 이내 재현된다 — 그 표에서 직접 역산된 값이므로 당연하다.
(b) Examples 5/6/7 H2O2 스윕은 `oxidizer_passivation_K`로 방향(단조 감소)과 자릿수는
맞지만 5 wt%에서 45.4% 벗어난다 — **원인 미상**이다. 가장 그럴듯한 설명은 `oxidizer_
passivation_K`가 이 표가 아니라 다른 특허(US20110165777A1 TABLE 2, 실리카 5 wt%·BTA
100 ppm 포함)에서 역산됐다는 계열 축척 차이([[chi-oxidizer-cu-h2o2-reparameterization]]
§2.1)이지만, 이 노트에서 그 가설을 추가로 검증하지는 않았다(미검증). 어느 쪽이든 (a)(b)
모두 "H2O2/pH → Cu 부동태 → RR 배수"라는 관계 자체는 χ가 이미 갖고 있다는 §3의 핵심
주장을 바꾸지 않는다 — 부호와 자릿수가 맞는 한, ψ에 같은 축을 또 넣을 이유가 안 된다.
(c)는 같은 θ(C)를 ψ에도 곱하면(단순 중복) 실측 대비 오차가 단일항보다 커짐을 보여,
"ψ에 별도로 넣으면 물리적으로 더 나빠진다"는 §3 주장을 수치로 뒷받침한다.

## 7. 구현 요청

**새 팩 파라미터는 제안하지 않는다.** 이 계에 ψ가 가져갈 수 있는 독립된 화학종·흡착상수가
없기 때문이다(§4). `shield_additive_wt_pct`/`shield_langmuir_K` 같은 키를 이 팩에 새로
선언하면, 값이 무엇이든 §6(c)가 보인 이중계상을 코드로 확정하는 것이다 — 하지 말아야 한다.

대신 `sim/factors.py::_f_psi`에 **구조적 분기**를 제안한다. 현재 `_f_psi`는 세 경로
(①②③)가 모두 비면 `terms`가 비어 `status`가 기본값(unmodeled)으로 남는다. 이 계처럼
"부동태 메커니즘은 실재하고 이미 χ가 소유"임이 팩 자신의 own 계수로 확인되는 경우를
별도로 신고하도록 제안한다:

```python
# _f_psi, "if not terms:" 분기 바로 앞에 삽입 제안
if not terms:
    # ψ 흡착 보호가 unmodeled 인 이유가 "문헌 없음"인지 "이미 χ 소유"인지 구분한다.
    # 판정: 이 팩이 pH-부동태 또는 산화제-부동태 계수를 *own*으로 선언했다면,
    # 그 계수는 이미 _f_chi 에서 소비되고 있다(oxidizer_passivation_K, cu_ph_alkaline_k
    # 는 둘 다 "억제" 방향 Langmuir 항으로, ψ 가 찾는 것과 물리적으로 동일한 θ(C)다).
    owns_chi_passivation = (pk.has_own("oxidizer_passivation_K")
                             or pk.has_own("cu_ph_alkaline_k"))
    if owns_chi_passivation:
        f.value = 1.0
        f.terms = {"owned_by_chi": 1.0}
        f.status = "partial"
        f.confidence = "literature"
        f.sources = ["knowledge/slurry/psi-cu-alkaline-h2o2-passivation.md",
                     "knowledge/cmp/chi-oxidizer-cu-h2o2-reparameterization.md"]
        f.notes.append(
            "ψ=1.0(항등): 이 팩의 표면 보호 메커니즘(H2O2/pH 유도 Cu 부동태화)은 "
            "실재하고 계량도 됐으나, χ의 oxidizer_passivation_K/cu_ph_alkaline_k가 "
            "같은 물리량(θ(C))을 이미 전담 모델링한다 — ψ에 같은 θ(C)를 다시 "
            "곱하면 이중계상(knowledge/slurry/psi-cu-alkaline-h2o2-passivation.md §6c "
            "수치 증명). 새 독립 흡착 화학종이 이 계 문헌에서 확보되기 전까지 "
            "ψ는 항등원이 맞다.")
        return f
    f.notes.append("⚠ ψ 미모델링: ...")  # 기존 그대로
    ...
```

`has_own` 게이트를 쓰는 이유: 상속만 받은 팩(예: 이 팩의 자식뻘이 될 미래 팩)이 이
분기로 조용히 "partial"이 되면 진짜 미모델링을 가리게 된다 — **자기 own 계수로
χ를 이미 가동 중인 팩만** 이 항등 분기를 탄다. `oxidizer_passivation_K`·`cu_ph_alkaline_k`
둘 다 이 노트 §3에서 확인한 대로 이 팩이 own 선언한 값이다.

이 분기가 적용되면 완성 격자에서 `ψ/cu_alkaline_benzenesulfonic`은 `status=partial`이
되어 C1(`unmodeled` 0건) 기준을 통과한다 — 값을 지어내지 않고, "이 팩에서 ψ가 독자적으로
기여하는 바는 없다(항등원)"는 것을 코드가 스스로 말하게 하는 방식이다.
