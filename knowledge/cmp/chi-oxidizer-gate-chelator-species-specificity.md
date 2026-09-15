<!-- V2-SECTION: R2-slurry | 근거: oxidizer, chi, chelator, glycine, oxalic_acid, regime, gate | 정본: ARCHITECTURE-V2.md §3 -->
# χ/cu_h2o2_bta 산성×착화제 게이트 — 착화제 종 특이성 (EVIDENCE-RULES 판정#47)

> 작성일: 2026-09-16
> 대상: `sim/chemistry.py::_oxidizer_term` (레짐 게이트 블록), `knowledge/params/cu_h2o2_bta.yaml`
> 선행:
>   [[chi-cu-h2o2-regime-reversal-jani2025]] (판정#38·#41 — 게이트 신설, K=0.7935를
>   **옥살산** 데이터(Jani 2025 Expt 30/31/32)로 적합. 저자 스스로 "글리신 proxy"라고
>   명시)
>   [[chi-cu-h2o2-glycine-acidic-sweep]] (판정#43 — **글리신** 1차 데이터(US5,575,885)
>   확보. 촉진 가지에 대면 구조적 반증(부호 반대, K→∞ 발산). 억제 가지는 시도 안 함 —
>   이번 판정이 그 후속)
>   [[chi-chelator-species-oxidizer-sign-divergence]] (판정#45 — "옥살산과 글리신을
>   하나의 산성×착화제 레짐으로 묶은 것 자체가 과도한 일반화"라고 이미 판정했으나
>   코드는 미반영이었다 — 이번 판정이 그 반영. 번복이 아니다)
>
> 1차 출처(전부 선행 노트에서 이미 원문 대조 완료, 이번 판정은 재사용):
>   - Hirabayashi et al., US Patent 5,575,885 (Toshiba, 등록 1996), FIG.2 —
>     `papers/hirabayashi1996-us5575885-cu-polishing-aminoacetic-acid.pdf`
>   - Jani et al. 2025, doi:10.1149/2162-8777/adc59e, Table I×II Expt 30/31/32
>   - US Patent Application 20110165777A1 (2011), TABLE 2 — 판정#20·#38이 이미
>     사용한 `oxidizer_passivation_K=0.8232` 원 데이터

## 0. 이번 판정이 다루는 두 가지 (독립)

- **A. 게이트 결함 수정** — 현재 코드는 "산성+착화제 아무거나"면 옥살산으로 적합된
  `oxidizer_acid_chelator_K`를 쓴다. 판정#43이 글리신으로 이를 반증했다. 종 일치를
  요구하도록 게이트를 좁힌다. (모델링 결함 수정 — 판정#45의 문서상 결론과 코드의
  불일치 해소이지, 새로운 판단이 아니다)
- **B. 억제 가지 K 재판정** — cu_h2o2_bta가 A 이후 돌아갈 `oxidizer_passivation_K=0.8232`가
  실은 알칼리×무착화제 계(판정#38, US20110165777A1)에서 역산됐다. 이제 손에 있는
  산성×글리신 1차 데이터(US5,575,885, 판정#43이 확보)로 재판정한다.

A는 B의 결론과 무관하게 수행했다(A는 값 문제가 아니라 코드가 잘못된 계수를
잘못된 계에 적용하는 결함이다).

## 1. 게이트 결함의 성격

판정#41의 게이트는 `slurry_ph < 6.0 AND chelator_M > 0.0`만 보고 촉진-포화형
(`oxidizer_acid_chelator_K = 0.7935`)을 켰다. 그런데 이 K는 **옥살산 0.08M** 데이터
(Jani 2025 Expt 30/31/32)로만 적합됐고, 판정#41 스스로 노트에 "글리신 존재 조건에서
H2O2만 바뀐 실험쌍은 하나도 없다... 옥살산 데이터를 글리신 레짐의 **방향 대리(proxy)**로만
쓴다"고 명시했다. 판정#43이 실제 글리신 데이터(US5,575,885)를 이 가지에 대입하자
부호가 반대(옥살산: 증가, 글리신: 감소)로 나왔고 최소자승 해가 K→∞로 발산했다 —
"K값이 틀렸다"가 아니라 **이 계수를 다른 착화제 종에 전이한 것 자체가 틀렸다**는
구조적 반증이다. 판정#45가 "옥살산·글리신을 하나의 레짐으로 묶은 것이 과도한
일반화"라고 이미 결론 냈지만 `sim/chemistry.py`는 여전히 착화제 종을 구분하지 않고
있었다 — **문서와 코드의 불일치**였다.

### 수정 내용

`oxidizer_acid_chelator_K` 옆에 `oxidizer_acid_chelator_species`(값: `oxalic_acid`,
판정#41이 실제로 쓴 착화제 — 지어낸 값이 아니다)를 선언하고, 게이트가 이 값과 팩의
`chelator_species`가 일치할 때만 발동하도록 좁혔다(`sim/chemistry.py` 171~230행경).
- **일치**(가상의 옥살산 팩): 촉진-포화형 발동, 기존과 동일한 계산.
- **불일치**(cu_h2o2_bta, 글리신): note에 "K는 {옥살산}으로 적합됐는데 팩 착화제는
  {글리신} — 판정#43이 부호 반전을 실측했으므로 전이하지 않는다"를 남기고, 기존 산화제
  경로(`oxidizer_passivation_K`)로 폴백.
- **`oxidizer_acid_chelator_species` 자체가 없는 구버전 팩**: 종 일치를 검증할 수
  없으므로 지어내지 않고 판정#41 이전 동작(항상 발동)을 유지하되 경고 note를 남긴다.
- 팩 이름 하드코딩 없음 — `chelator_species`/`oxidizer_acid_chelator_species` 필드로만
  분기한다(판정#34 원칙 유지).
- 다른 4팩(oxide_silica, sic_ceria_h2o2, sti_ceria, w_fe_oxidizer)은애초에
  `oxidizer_acid_chelator_K`를 선언하지 않아 이 블록에 진입조차 하지 않는다 —
  비트 단위 불변을 계약 테스트로 고정(`tests/test_oxidizer_acid_chelator_gate.py`
  테스트 ①).

### 결과

`cu_h2o2_bta`(글리신)는 이제 자기 레짐인 `oxidizer_passivation_K`(억제형)로 돌아간다.
`tests/test_sensitivity.py::test_oxidizer_sensitivity_sign_follows_passivation`이 이
방향 전환(양수→음수)을 계약으로 고정한다 — 부호가 다시 뒤집힌 것은 회귀가 아니라
판정#41이 도입한 BIAS를 판정#47이 되돌린 것이다.

## 2. 네 가지 함수형-데이터 조합의 SSE 표 (US5,575,885 FIG.2, 0.5/5.0/12.0 wt% → 76.0/37.4/10.5 nm/min)

스케일 A를 자유(최소자승 정규방정식으로 각 K마다 해석적 최적화)로 두고, φ(기계 하한)만
고정한 뒤 K 하나를 grid+scipy `minimize_scalar`로 전역 탐색했다(직접 재현, 아래
python verify 블록에 코드 포함).

| 함수형 | φ | K* | SSE | 예측(0.5/5.0/12.0 wt%) |
|---|---|---|---|---|
| 촉진-포화형(현행 게이트, `oxidizer_acid_chelator_K`) | 0.15(팩 기본 floor) | →∞(발산) | **2167.94** | [41.3, 41.3, 41.3] (평탄) |
| 억제형(`oxidizer_passivation_K`) | 0.00 | 0.3521 | **68.51** | [76.53, 32.61, 17.23] |
| 억제형(`oxidizer_passivation_K`) | **0.15**(팩 기본 floor, 미선언 시 적용값) | 0.6956 | **183.00** | [74.35, 32.37, 22.95] |
| 억제형(`oxidizer_passivation_K`) | 0.30 | 0.7393 | **486.69** | [66.97, 37.08, 30.63] |

**촉진-포화형이 K→∞(평탄 예측)로 발산하는 것과 SSE=2167.94는 정확히 재현됐다**
(Max워커 사전 실측치와 일치). **φ=0.00 억제형(K*=0.3521, SSE=68.51)도 정확히
일치했다.** 그러나 **φ=0.15 억제형은 재현하며 다른 값을 얻었다** — Max워커
사전 실측은 K*=0.492/SSE=105/예측[76.4,31.5,18.9]로 보고됐으나, grid(0.0005 간격,
0.0005~5.0)와 `scipy.optimize.minimize_scalar`(bounds 1e-6~50, xatol=1e-12) 양쪽
모두 K*=0.6956에서 전역최소 SSE=183.00을 확인했다(K=0.492에서는 SSE=197.35로 더
나쁘다 — 사전 실측치가 전역최적이 아니었다). 이 노트는 **직접 재계산한 값**
(SSE=183.00)을 이후 판단의 근거로 쓴다. 어느 쪽 수치를 쓰든 결론(아래 §4)에는
영향이 없다 — 촉진형 대비 억제형(φ 무관)이 4.5~32배 낮다.

## 3. 식별성 검사

φ는 이 팩이 `oxidizer_mech_floor`를 선언하지 않아 코드 기본값 **0.15**가 실제로
적용된다(`sim/chemistry.py::_oxidizer_term` 150행, `pack.get_or("oxidizer_mech_floor",
0.15)`) — 그러므로 φ=0.15가 이 팩의 운전상 유효값이고, 이 항의 식별성 판단도 φ=0.15
기준으로 해야 한다(φ=0.00은 가상 시나리오일 뿐 이 팩에 적용되지 않는다).

K*=0.6956(φ=0.15)에서 0.3배·3배 교란:

| K | SSE | SSE/SSE_min |
|---|---|---|
| 0.3×K* = 0.2087 | 422.56 | 2.31× |
| K* = 0.6956 | 183.00 | 1.00× |
| 3×K* = 2.0865 | 247.48 | **1.35×** |

기존 `oxidizer_passivation_K=0.8232`(판정#20 원 적합값, 0.3K*~3K*에서 5배 이상
악화 확인됨)의 식별성 기준을 그대로 적용하면 **이 데이터는 K를 식별하지 못한다** —
3배 교란에도 SSE가 1.35배밖에 악화하지 않는다(참고: φ=0.00에서는 0.3×/3×가 각각
8.13×/4.96×로 훨씬 뚜렷하지만, φ=0.00은 이 팩에 적용되는 값이 아니므로 채택 근거가
될 수 없다 — φ를 데이터에 맞춰 고르는 것은 과제 지시로 금지되어 있다).

식별성 검사의 실행 코드와 assert는 §7 python verify 블록((4)항)에 통합했다.

## 4. 판단과 사유 — **(c) 값·등급 전부 유지**

기존 `oxidizer_passivation_K=0.8232`를 이 데이터(φ=0.15)에 그대로 적용하면
SSE=185.50, 예측=[74.8, 31.4, 22.7]이다. 이번에 전역 재탐색으로 찾은 "최적" K*=0.6956의
SSE=183.00과 비교하면 **차이가 1.4%**에 불과하다 — 재적합이 실질적 개선을
주지 않는다. 이는 §3의 식별성 실패(3배 교란에도 1.35배 악화)와 정확히 같은 현상의
다른 표현이다: SSE(K) 곡면이 φ=0.15에서 매우 평평해서, 기존 K와 "최적" K가
통계적으로 구별되지 않는다.

판단 기준(과제 지시 4.(a)/(b)/(c))에 대입하면:
- **(a) 재적합값 채택+literature 승격 — 기각.** 식별성이 실패했다(§3). 격자를
  채우려고 퇴화한 최적해를 문헌 등급으로 올리면 "데이터가 K를 지지한다"는
  거짓 인상을 준다.
- **(b) 값은 바꾸되 estimated 유지 — 기각.** 바꿀 값(0.6956)이 기존 값(0.8232)과
  성능상 구별되지 않는데(SSE 1.4% 차이), 식별 안 되는 방향으로 숫자만 바꾸는 것은
  "재판정"이 아니라 잡음을 코드에 새겨 넣는 것이다.
- **(c) 값·등급 전부 유지 — 채택.** 기존 K=0.8232는 (i) 방향(단조 감소)을 정확히
  재현하고, (ii) 이번 회차에 확보한 산성×글리신 1차 데이터에서의 SSE가 "최적" 재적합과
  1.4%밖에 차이 나지 않으며, (iii) 애초에 이 데이터로는 K가 식별되지 않는다. 바꿀
  근거가 없다.

**잔차의 정직한 평가(과제 지시 3항)**: 12wt%에서 기존 K로도 +116.1%, "최적" K로도
+118.5% 과대예측이 남는다(예측 22.7~22.9 vs 실측 10.5) — 과제가 예고한 "+64~80%"보다
크다(그 수치는 Max워커의 미검증 사전 실측 φ=0.15 예측 18.9nm/min에서 나온 것으로, §2의
재계산으로 반증됐다. φ=0.00일 때만 +64%가 나온다). φ를 낮출수록(0.30→0.15→0.00) SSE와
잔차가 개선되는 뚜렷한 경향(486.69→183.00→68.51)을 보이는데, 이는 과제가 경고한 대로
"φ(기계 하한)가 고농도 꼬리를 떠받치는 구조라 φ가 클수록 악화한다"는 정확한 징후다.
그러나 φ는 이 데이터의 자유 파라미터가 아니라 기계 상수로 코드에 고정되어 있고, 이
팩은 그 상수를 오버라이드하지 않았다 — φ를 낮춰서 잔차를 줄이는 것은 적합이지 관측이
아니므로 하지 않는다. 이 잔차는 **K값 문제가 아니라 함수형(Langmuir 피복-억제)의
한계**일 가능성이 높다 — 12wt%라는 고농도에서 실측 제거율(10.5)이 φ·(1-φ) 가중 평균의
바닥(φ=0.15×A≈14.3)에 근접해 있어, 이 폐형식이 표현할 수 있는 점근 하한 자체가 실측보다
높다. 이 한계는 이번 판정 범위 밖(함수형 재설계는 별도 BIAS급 판정 필요)이므로 기록만
한다.

## 5. 한계

- **US5,575,885 데이터의 한계는 판정#43 §6을 그대로 승계한다**: 특허 도면 그래프
  판독(±5% 내외 추정), pH 비직접측정(자연 pH, KOH 무첨가로부터 <7 추정), 글리신
  농도가 팩(1wt%)과 다름(도면 데이터는 0.1wt%), n=3 단일 실시예.
- **스케일 자유도**: §2의 SSE 비교는 A(절대 크기)를 자유 파라미터로 두고 K만
  비교했다 — 실제 팩은 `oxidizer_ref_wt_pct=3.0`(이 데이터에 없는 농도)에서 배수
  1.0이 되도록 정규화하므로, 이 SSE 비교는 "형태(shape) 적합도" 비교이지 팩의
  절대 MRR 예측을 검증한 것이 아니다.
- **φ 고정**: §3~4에서 반복 확인했듯 φ=0.15는 이 데이터에서 온 값이 아니라 코드
  기본값이다. φ를 이 데이터로 추정하려는 시도는 하지 않았다(과제 지시로 금지).
- **Max워커 사전 실측치와의 불일치(φ=0.15)**: §2에서 밝혔듯 사전 실측
  K*=0.492/SSE=105는 전역최적이 아니었다(직접 재계산 SSE=183.00이 더 낮다). 결론에
  영향은 없으나(어느 쪽이든 촉진형보다 1자릿수 이상 낮음), 사전 실측치를 그대로
  믿지 않고 재현해 확인한 결과다.
- **오차 발생 가능 지점**: 최소자승 전역탐색은 grid(0.0005~5.0, step 0.0005) +
  `scipy.optimize.minimize_scalar`(bounds 조정) 두 방법을 교차검증했으나, 이 함수형
  자체가 K에 대해 매끄러운 단일봉이라는 가정에 의존한다(관측된 곡선 형태상 타당해
  보이나 수학적으로 증명하지 않았다).
- **함수형 한계 가능성(§4 마지막 문단)**: 12wt%에서 남는 큰 잔차가 K 문제가 아니라
  Langmuir 피복-억제 폐형식 자체가 이 농도-반응 곡률을 표현 못 하는 것일 수 있다 —
  다음 BIAS급 판정에서 비단조/다른 포화 함수형을 검토할 근거로 남긴다.

## 6. C 게이트 — held-out 회귀 확인

`tools/qa_loop.py run --strict` 결과(2026-09-16 실행): 유의 데이터셋 7/25, **유의
평균 ρ = 0.9442** — 과제가 지정한 하한(0.9442)에서 내려가지 않았다(동일값 유지,
격리 2건은 판정#47과 무관한 기존 US9200180B2 used_for_calibration 누락 항목).

## 7. python verify

```python verify
import sys
sys.path.insert(0, ".")
import numpy as np
from scipy.optimize import minimize_scalar
from sim.tier2_physics.slurry_components import oxidizer_coverage_langmuir as theta

# US5,575,885 FIG.2 (판정#43이 판독) — 글리신 0.1wt% 고정, H2O2 스윕
C = np.array([0.5, 5.0, 12.0])
RR = np.array([76.0, 37.4, 10.5])

def sse_free_A(K, phi, kind):
    t = theta(C, K)
    if kind == "promo":
        g = phi + (1 - phi) * t
    else:
        g = phi + (1 - phi) * (1.0 - t)
    A = np.sum(g * RR) / np.sum(g * g)
    pred = A * g
    return float(np.sum((pred - RR) ** 2)), pred, A

# ── (1) 촉진 가지(현행 게이트, phi=0.15 팩 기본값) — 발산/평탄 ──
res_promo = minimize_scalar(lambda K: sse_free_A(K, 0.15, "promo")[0],
                             bounds=(1e-6, 1e8), method="bounded",
                             options={"xatol": 1e-10})
sse_promo, pred_promo, _ = sse_free_A(res_promo.x, 0.15, "promo")
print(f"촉진 K*={res_promo.x:.3e} SSE={sse_promo:.2f} pred={np.round(pred_promo,1)}")
assert res_promo.x > 1e5, "촉진 가지 최적 K가 발산(K→∞)해야 한다"
assert np.ptp(pred_promo) < 0.1, "촉진 가지 최적해는 평탄 예측이어야 한다(K→∞ 극한)"
assert sse_promo > 2000, "촉진 가지 SSE가 크게 남아 있어야 한다(평탄해도 데이터를 못 담음)"

# ── (2) 억제 가지 — phi 세 수준 ──
results = {}
for phi in (0.0, 0.15, 0.30):
    res = minimize_scalar(lambda K: sse_free_A(K, phi, "passiv")[0],
                           bounds=(1e-6, 50), method="bounded",
                           options={"xatol": 1e-12})
    sse, pred, A = sse_free_A(res.x, phi, "passiv")
    results[phi] = (res.x, sse, pred)
    print(f"억제 phi={phi} K*={res.x:.4f} SSE={sse:.2f} pred={np.round(pred,2)}")

# Max워커 사전 실측(phi=0.0)과 정확히 일치해야 한다
K0, sse0, pred0 = results[0.0]
assert abs(K0 - 0.3521) < 0.001, f"phi=0.0 K* 재현 실패: {K0}"
assert abs(sse0 - 68.51) < 0.1, f"phi=0.0 SSE 재현 실패: {sse0}"

# phi=0.15(팩의 실제 유효 floor)가 이 팩에 적용되는 값이다
K15, sse15, pred15 = results[0.15]
assert abs(K15 - 0.6956) < 0.001, f"phi=0.15 K* 계산 불일치: {K15}"
assert 180.0 < sse15 < 186.0, f"phi=0.15 SSE 계산 불일치: {sse15}"

# ── (3) 핵심 주장 — 억제 가지가 촉진 가지보다 최소 1자릿수(10배) 낮다 ──
# 이 팩에 실제 적용되는 phi=0.15(기본값)와, 참고용 phi=0.00(기계 하한 없음 극단)에서
# 확인한다. phi=0.30(경질 연마재·고하중 극단, 이 팩에는 해당 없음)은 참고로만 출력한다.
for phi in (0.0, 0.15):
    K, sse, pred = results[phi]
    ratio = sse_promo / sse
    assert ratio >= 10.0, f"phi={phi}: 촉진/억제 SSE비 {ratio:.1f}가 1자릿수 미만"
    print(f"phi={phi}: 촉진 SSE / 억제 SSE = {ratio:.1f}배")
K30, sse30, _ = results[0.30]
print(f"(참고, 이 팩에 비적용) phi=0.30: 촉진 SSE / 억제 SSE = {sse_promo/sse30:.1f}배")

# ── (4) 식별성 — phi=0.15(실제 적용값)에서 3배 교란 시 SSE 배율 ──
Kstar = K15
sse_03, _, _ = sse_free_A(0.3 * Kstar, 0.15, "passiv")
sse_3x, _, _ = sse_free_A(3.0 * Kstar, 0.15, "passiv")
ratio_03 = sse_03 / sse15
ratio_3x = sse_3x / sse15
print(f"phi=0.15 식별성: 0.3K*→{ratio_03:.2f}배, 3K*→{ratio_3x:.2f}배 (판정#20 기준 5배)")
assert ratio_3x < 5.0, "phi=0.15에서는 3배 교란으로도 5배 악화에 못 미쳐야 한다(식별 실패 확인)"

# ── (5) 판단(c) — 기존 K=0.8232가 "최적" 재적합과 사실상 구별 안 됨 ──
sse_old, pred_old, _ = sse_free_A(0.8232, 0.15, "passiv")
improvement = sse_old / sse15
print(f"기존 K=0.8232: SSE={sse_old:.2f} vs 재적합 K={Kstar:.4f}: SSE={sse15:.2f}"
      f" (개선비 {improvement:.3f})")
assert improvement < 1.05, "기존 K와 재적합 K의 SSE 차이가 5% 이상이면 (c) 판단 근거가 깨진다"

# 두 K 모두 방향(단조 감소)은 정확히 재현한다
assert pred_old[0] > pred_old[1] > pred_old[2], "기존 K도 단조 감소를 재현해야 한다"

# ── (6) 실제 팩 정규화 공식(C_ref=3.0)으로도 방향이 유지되는지 재확인 ──
def f_actual(Cv, K, phi, Cref=3.0):
    t, tref = theta(Cv, K), theta(Cref, K)
    return phi + (1 - phi) * (1.0 - t) / (1.0 - tref)

ratios = [f_actual(c, 0.8232, 0.15) for c in (0.5, 5.0, 12.0)]
assert ratios[0] > ratios[1] > ratios[2], f"팩 정규화 공식에서도 단조 감소여야 한다: {ratios}"

# 잔차 크기 보고(12wt%) — 두 K 모두 실측보다 과대예측
over_old = (pred_old[2] - RR[2]) / RR[2]
over_new = (pred15[2] - RR[2]) / RR[2]
print(f"12wt% 과대예측: 기존 K {over_old:.1%}, 재적합 K {over_new:.1%}")
assert over_old > 1.0 and over_new > 1.0, "12wt%에서 100% 이상 과대예측이 남아있음을 확인"

print("=> 판정: (c) 값·등급 전부 유지. A(게이트 종특이성)만 코드에 반영한다.")
```

## 8. 실행 로그 (게이트 확인, 2026-09-16)

- `tools/verify_claims.py`: 1/1 통과 (출처 2건 실존, 검증코드 1블록 통과)
- `tools/check_knowledge.py`: 1/1 통과
- `tests/test_oxidizer_acid_chelator_gate.py`: 15 passed (기존 10 + 신규 5)
- `tests/test_sensitivity.py`: 12 passed (판정#47로 방향 전환된 부호 포함)
- `pytest -q` 전체: **847 passed**, 0 failed (판정 전 842 passed 기준 대비 +5, 회귀 0)
- `tools/completion.py check`: 격자 49/50 (C2 `χ chi/cu_h2o2_bta`=estimated 그대로,
  §4의 (c) 판단과 일치 — 격자를 채우지 않은 것이 이번 판정의 정직한 결과다)
- `tools/qa_loop.py run --strict`: 유의 평균 ρ = **0.9442**(하한 유지, §6)

> 완료. A(게이트 종특이성 수정, `sim/chemistry.py` + `knowledge/params/cu_h2o2_bta.yaml`
> 에 `oxidizer_acid_chelator_species` 신설)와 B(K 재판정, 결론=(c) 값·등급 전부 유지)
> 모두 수행했다. 미완 항목 없음.
