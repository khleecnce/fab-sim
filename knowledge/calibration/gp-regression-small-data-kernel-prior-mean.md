# 소량 데이터 GP 회귀 — 커널 설계·하이퍼파라미터·물리 기반 평균함수

> 상태: 1차 출처 3건 확보(2건 원문 PDF 전체 판독, 1건 arXiv 프리프린트 전체 판독).
> "MAP 추정이 소량 n에서 길이척도를 어떻게 다루는가"를 정면으로 다루는 1차 문헌은
> 이번 조사 범위 안에서 찾지 못했다 — 아래 §2에 미검증으로 명시한다.

## 문헌

1. **Bachoc, F. (2013)**, "Cross Validation and Maximum Likelihood estimations of
   hyper-parameters of Gaussian processes with model misspecification",
   *Computational Statistics & Data Analysis*, 66, 55–69. DOI: 10.1016/j.csda.2013.03.016.
   (arXiv 프리프린트 1301.4320v3로 원문 전체 확보·판독 — 이하 "Bachoc2013". 페이지
   번호는 프리프린트 자체 쪽번호.)
2. **Hoffer, J. G., Geiger, B. C. & Kern, R. (2022)**, "Gaussian Process Surrogates for
   Modeling Uncertainties in a Use Case of Forging Superalloys", *Applied Sciences*,
   12(3), 1089. DOI: 10.3390/app12031089. (오픈 액세스, TU Graz 리포지토리 PDF로
   전문 확보·판독 — 이하 "Hoffer2022".)
3. **Kennedy, M. C. & O'Hagan, A. (2001)**, "Bayesian Calibration of Computer Models",
   *J. R. Statist. Soc. B*, 63(3), 425–464. DOI: 10.1111/1467-9868.00294. (원문 PDF
   전체 판독 — [[bayesian-calibration-koh-discrepancy]] 노트에서 이미 전문 확보한 것과
   동일 문헌. 이하 "KOH2001".)

## 1. 커널 선택과 매끄러움 가정 — 소량 n에서 RBF/Matérn의 차이

Hoffer2022 §2.1 (p.6, 식 9–10)이 두 표준 커널을 정의한다:

    k_RBF(x,x') = exp(-||x-x'||² / l²)                                  (Hoffer2022 식 9)
    k_Matérn(x,x') = [1/(Γ(ν)2^(ν-1))]·(√(2ν)|x-x'|/l)^ν·K_ν(√(2ν)|x-x'|/l)   (Hoffer2022 식 10)

RBF(=Gaussian/squared-exponential)는 무한 번 미분 가능한 함수만 표현할 수 있다는
매끄러움 가정을 내포한다. Matérn은 규칙성 파라미터 ν로 이 가정을 완화한다(ν→∞에서
RBF로 수렴). Bachoc2013 §5.1(p.13)은 이를 "covariance function이 참 함수와 다르면
misspecification"이라 부르고, 정확히 이 매끄러움 가정 오류가 소량 n에서 얼마나
치명적인지를 §5.5(p.17)에서 수치로 보인다.

Bachoc2013 §5.5(p.17)의 핵심 관찰: Ishigami 함수(매끄러운 해석함수)에 대해 n=100개
관측점에서는 Gaussian 커널(무한matically 매끄러움)이 exponential 커널(ν=1/2, 거친
경로)보다 작은 MSE를 낸다(Table 2, p.18). 그러나 **같은 함수에 n=70으로 관측점을
줄이면 Gaussian 커널의 MSE가 오히려 exponential보다 커진다**(Table 3, p.18: Gaussian
MSE 3.15~4.13 vs exponential 2.91~3.23). 저자의 해석(p.17): "충분한 관측점이 없으면
매끄러운 함수에 대해서도 exponential이 주는 선형보간으로 충분할 수 있다" — 즉
매끄러움 가정이 이론적으로 옳아도, 그 가정에 맞는 길이척도·형태를 데이터로부터
정확히 추정하기에 n이 부족하면 더 유연/거친 커널이 실전에서 낫다는, 반직관적이지만
1차 수치실험으로 확인된 결과다.

**FabSim 관련성**: CMP 계열별 실측 데이터는 전형적으로 n<30이다. Bachoc2013의
n=70→100 경계 관찰(둘 다 FabSim 기준으로는 "많은" 축에 속함)은, n이 이보다 훨씬
작은 우리 상황에서는 매끄러움 가정이 강한 RBF보다 Matérn 3/2(ν=3/2, 1회 미분가능)가
더 안전한 기본값이라는 정성적 근거가 된다 — 다만 이 경계값 자체가 CMP 데이터에
그대로 적용된다는 문헌적 근거는 없다(**미검증**: n<30 레짐에서의 정량적 비교는
1차 출처가 이번 조사에서 확보되지 않았다).

## 2. 하이퍼파라미터 추정 — MLE vs CV vs 완전 베이지안, 길이척도 문제

Bachoc2013 §5.1(p.13, 식 20)의 ML 목적함수:

    f_ML(θ) = (1/n)·log det(Γ_θ) + log(y^T Γ_θ^{-1} y)          (Bachoc2013 식 20)

와 CV(leave-one-out) 목적함수(식 21, p.13):

    f_CV(θ) = y^T Γ_θ^{-1} diag(Γ_θ^{-1})^{-2} Γ_θ^{-1} y         (Bachoc2013 식 21)

둘 다 θ(길이척도 등)에 대해 국소최솟값을 여러 개 가질 수 있어 BFGS를 여러 초기점에서
재시작한다고 명시한다(p.14). 저자가 실측으로 경고하는 길이척도 폭주 현상은 p.14–15에
구체적으로 나온다: **Gaussian 계열이나 규칙성 파라미터가 큰 Matérn에서, CV로 θ를
추정하면 "큰 상관길이가 추정되는" 경향이 있고**, 이것이 예측분산 항 (1-γᵀΓ⁻¹γ)을
수치적으로 0에 가깝게(때로는 반올림오차로 음수까지) 만들어 예측분산 계산 자체가
깨진다(p.14). 저자는 이를 막기 위해 σ²_CV가 경험분산의 1000배를 넘으면 벌점을 주는
임시방편을 쓴다(p.15). Martin and Simpson (2004, p.7)을 인용하며 "CV가 상관길이를
과대추정하는 경향이 있다"고 재확인한다(Bachoc2013 p.15, **2차 인용** — Martin &
Simpson 원문은 이번 조사에서 확보하지 않았다).

ML과 CV는 둘 다 **점추정(point estimate)** 이라는 공통점이 있다 — 하이퍼파라미터의
불확실성을 전파하지 않는다. 이와 대조적으로 KOH2001 §4.2(p.436, [[bayesian-calibration-koh-discrepancy]]
노트에서 이미 확인)의 틀은 GP 하이퍼파라미터(η, δ의 상관길이·분산)에도 사전분포를
주고 사후분포를 MCMC로 표본추출하는 **완전 베이지안** 접근이다. 이 경우 소량 n에서
하이퍼파라미터가 폭주해도(예: 길이척도의 사후분포가 넓게 퍼짐) 그 불확실성이 예측
구간에 그대로 반영되어 과신을 막는다 — 반면 ML/CV 점추정은 폭주한 하이퍼파라미터
값 하나를 "확정값"으로 쓰기 때문에 과신 위험이 남는다.

**MAP(사후최빈값) 추정**에 대해서는 이번 조사에서 이를 정면으로 다루는 1차 문헌을
확보하지 못했다. 일반적으로 MAP는 ML 목적함수(식 20)에 하이퍼파라미터 사전분포의
로그를 더한 정규화 추정으로 알려져 있으나(교과서적 정의이므로 여기서는 서술만 하고
문헌 인용은 하지 않는다), **소량 n에서 MAP가 길이척도 폭주를 얼마나 억제하는지에
대한 정량적 문헌값은 미검증**이다. `> ⚠ 이 항목은 1차 출처 확보 실패 — 시도한 검색어:
"MAP estimation length-scale Gaussian process small sample"`.

## 3. 물리 기반 평균함수와 KOH δ(x)의 관계

표준 GP 회귀는 평균함수를 0으로 두는 것이 관례다(Hoffer2022 §2.1 p.5, 식 4: "we
define that they are jointly Gaussian and have **zero mean**"). Hoffer2022는 실제로
FEM 시뮬레이션 전체를 두 개의 영-평균 GP로 대체하는 접근이라, 물리 모델이 GP의
평균함수 자리에 들어가지 않는다 — 즉 우리가 찾는 "물리 기반 평균함수" 설계와는
다른 선택지다.

Bachoc2013 §5.6(p.19, Table 4)은 "universal Kriging"이라는 이름으로 상수·아핀
평균함수를 시험한다: Ishigami 함수에서 상수 대신 아핀(affine) 평균함수를 쓰면
exponential 상관함수에서만 미미하게 개선되고(MSE 1.96→1.98은 오히려 근소 악화,
PVA는 소폭 개선), Gaussian 상관함수에서는 "평균함수가 모델을 과매개변수화해
성능을 약간 해친다"(p.19)고 보고한다. 저자는 Stein(1999, p.138)을 인용해 "Kriging
모델에서 평균함수 선택 문제는 공분산함수 선택 문제보다 훨씬 덜 중요하다"고
결론짓는다(Bachoc2013 p.19, **2차 인용** — Stein 1999 원문 미확보).

이 결과는 언뜻 "평균함수는 중요하지 않다"로 읽히지만, 요점은 **아핀/상수 평균함수는
물리 정보를 담지 않는다**는 것이다. Bachoc2013이 시험한 평균함수는 데이터 자체로부터
추정되는 회귀계수(β)일 뿐, 외부 물리 지식이 아니다. 반면 KOH2001 §4.2(p.435, 식 5,
[[bayesian-calibration-koh-discrepancy]] 노트 §1)의 관측 모형

    z(x) = ρ·η(x,θ) + δ(x) + e                                    (KOH2001 식 5)

은 GP의 평균 자리에 **물리 시뮬레이터 η(x,θ)** 를 놓고, 그 위의 잔차만 GP(δ)로
학습한다. 이것이 Bachoc2013의 "아핀 평균함수"와 본질적으로 다른 점은, η가 데이터
범위 밖에서도 물리 법칙에 따라 계산 가능하다는 것이다 — 아핀 평균은 외삽 구간에서도
직선을 그릴 뿐이지만, η는 외삽 구간에서 물리적으로 의미 있는 값을 준다. 즉 Bachoc의
"평균함수는 덜 중요하다"는 결론은 **관측 구간 내부(보간)** 에서는 맞지만, FabSim이
평균함수에 물리모델을 쓰는 이유는 보간 성능이 아니라 **외삽 시 안전망**이다 — 이
구분은 Bachoc2013 자체에는 없고, 여기서 KOH2001과 대조해 도출한 것이다.

핵심 메커니즘: GP posterior mean은 `m(x) + k(x,X)K⁻¹(y - m(X))` 형태다. 관측점에서
멀어질수록(외삽) `k(x,X)→0`이므로 posterior mean은 `m(x)`로 수렴한다. `m(x)=0`이면
외삽 구간에서 예측이 0으로 붕괴하지만, `m(x)=η(x,θ)`(물리 모델)이면 외삽 구간에서
예측이 물리 예측값으로 되돌아간다 — 이것이 아래 verify 블록에서 재현하는 것이다.

```python verify
# verify1: Bachoc2013 §3 (p.6) "var1(sigma_ML^2) = 2/n, the Cramer-Rao bound"을
# Monte Carlo로 재현한다. R1=R2(모델이 정확히 맞는 경우)일 때 sigma_ML^2 = (1/n) y^T Gamma^-1 y
# 의 이론분산이 2/n임을 수치로 확인한다.
import numpy as np

rng = np.random.default_rng(0)
n = 30  # FabSim 전형적 소량 데이터 규모
x = np.sort(rng.uniform(0, 1, n))
ell = 0.2  # correlation length


def matern32(d, ell):
    r = np.sqrt(3) * np.abs(d) / ell
    return (1 + r) * np.exp(-r)


D = np.abs(x[:, None] - x[None, :])
Gamma = matern32(D, ell) + 1e-10 * np.eye(n)  # nugget for conditioning
L = np.linalg.cholesky(Gamma)

n_mc = 20000
sigma2_ml = np.empty(n_mc)
Gamma_inv = np.linalg.inv(Gamma)
for i in range(n_mc):
    z = rng.standard_normal(n)
    y = L @ z  # y ~ N(0, Gamma), i.e. R1 = R2 = Gamma exactly
    sigma2_ml[i] = (y @ Gamma_inv @ y) / n

mean_hat = sigma2_ml.mean()
var_hat = sigma2_ml.var()
var_lit = 2.0 / n  # Bachoc2013 p.6: "var1(sigma_ML^2) = 2/n, the Cramer-Rao bound"

# 몬테카를로 표준오차 감안, 문헌값 2/n 과 상대오차 10% 이내
rel_err_var = abs(var_hat - var_lit) / var_lit
assert abs(mean_hat - 1.0) < 0.05, f"E[sigma2_ML] should be ~1, got {mean_hat}"
assert rel_err_var < 0.10, f"var(sigma2_ML) vs Bachoc2013 2/n: {rel_err_var*100:.1f}% 차이"
print(f"E[sigma2_ML]={mean_hat:.4f} (기대 1.0), "
      f"var(sigma2_ML)={var_hat:.5f} vs 문헌값 2/n={var_lit:.5f}, "
      f"상대오차 {rel_err_var*100:.1f}%")
```

```python verify
# verify2: 물리 기반 평균함수 m(x)=eta(x)가 있는 GP의 posterior mean이
# (a) 관측점을 통과하고 (b) 외삽 구간에서 m(x)로 회귀함을 확인한다.
# 대조군으로 m(x)=0(표준 GP)은 외삽 구간에서 0으로 붕괴함을 같이 보인다.
# eta(x)는 FabSim 스타일 Preston형 물리모델을 흉내낸 임의 함수(가상, 실데이터 아님).
import numpy as np


def eta(x):
    return 2.0 + 0.5 * x  # 가상의 "물리 예측" (선형, 예시일 뿐 실제 Preston식 아님)


def rbf(d, ell=0.3, sigma2=1.0):
    return sigma2 * np.exp(-(d ** 2) / (2 * ell ** 2))


rng = np.random.default_rng(1)
x_obs = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
noise_std = 0.05
y_obs = eta(x_obs) + rng.normal(0, noise_std, size=x_obs.size)  # 물리모델 근처의 관측치

D_oo = np.abs(x_obs[:, None] - x_obs[None, :])
K_oo = rbf(D_oo) + noise_std ** 2 * np.eye(x_obs.size)
K_oo_inv = np.linalg.inv(K_oo)

x_test = np.array([0.5, 6.0, 10.0])  # 0.5=보간, 6.0/10.0=관측범위 밖 외삽
D_to = np.abs(x_test[:, None] - x_obs[None, :])
K_to = rbf(D_to)

# 물리 기반 평균함수 GP
mean_test_phys = eta(x_test) + K_to @ K_oo_inv @ (y_obs - eta(x_obs))
# 영-평균 GP (대조군)
mean_test_zero = K_to @ K_oo_inv @ y_obs

# (a) 보간 지점(x=0.5, 관측점과 정확히 겹침)에서는 두 모델 모두 관측 근방을 통과해야 함
assert abs(mean_test_phys[0] - y_obs[2]) < 0.05, "물리기반 GP가 관측점을 통과하지 못함"

# (b) 외삽 지점(x=10, 가장 가까운 관측점에서 9.1 떨어짐, RBF 길이척도 0.3의 30배)에서
#     물리기반 GP는 물리모델 예측값 eta(10)=7.0으로 회귀해야 함
phys_pred_at_10 = eta(np.array([10.0]))[0]
rel_gap_phys = abs(mean_test_phys[2] - phys_pred_at_10) / phys_pred_at_10
assert rel_gap_phys < 0.01, f"물리기반 GP가 외삽에서 물리모델로 회귀하지 않음: {rel_gap_phys*100:.2f}%"

# 영-평균 GP는 같은 외삽 지점에서 0 근방으로 붕괴 — 물리적으로 틀린 값
assert abs(mean_test_zero[2]) < 0.01, "영-평균 GP가 외삽에서 0으로 붕괴하지 않음(대조군 실패)"

print(f"보간(x=0.5): 물리기반 GP={mean_test_phys[0]:.3f}, 관측값={y_obs[2]:.3f}")
print(f"외삽(x=10): 물리기반 GP={mean_test_phys[2]:.3f} (물리모델 eta(10)={phys_pred_at_10:.3f}, "
      f"차이 {rel_gap_phys*100:.2f}%), 영-평균 GP={mean_test_zero[2]:.4f}(0으로 붕괴)")
```

## 4. FabSim 캘리브레이션 층과의 연결

`sim/calibration/series_scale.py`([[bayesian-calibration-koh-discrepancy]] 노트 §1에서
이미 다룸)는 δ(x)를 상수 1자유도로 제약한 KOH의 특수 케이스다. 이번 단원에서 확인한
내용을 더하면: 그 설계가 옳다는 것을 뒷받침하는 근거가 하나 더 늘었다 — Bachoc2013
Table 4(p.19)가 보여주듯 **평균함수 자유도를 늘리는 것(상수→아핀)조차 소량 n에서
과매개변수화 위험**이 있는데, series_scale.py처럼 평균함수(물리모델 η) 자체는
고정하고 배율 하나만 학습하는 쪽이 오히려 Bachoc2013이 관찰한 과매개변수화 위험을
회피하는 방향과 일치한다.

## 5. 구현 관련 메모 (코드 변경 없음)

이번 단원에서는 `sim/`을 읽지도 수정하지도 않았다. §2에서 확인한 "CV 점추정은 소량
n에서 하이퍼파라미터를 과대추정할 수 있다"(Bachoc2013 p.14–15)는 관찰은, 만약 향후
GP 기반 캘리브레이션(Lv2 이후 커리큘럼의 "sim/calibration/fit_ptw.py" 등)을 구현할
때 하이퍼파라미터를 순수 CV로 고르지 말고 물리 사전지식으로 상관길이를 제약하거나
완전 베이지안으로 불확실성을 전파해야 한다는 근거가 된다. 코드 변경은 PROFILE.md
`## 구현 요청` 절에 남긴다.

[[bayesian-calibration-koh-discrepancy]]
