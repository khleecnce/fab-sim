# Lv3-2 설계 확정 — prior/fit_npw/fit_ptw/predict/drift의 수학 형태

> 상태: 조사 중 — 뼈대 생성. cmp-calibrator Lv1~Lv3-1(전부 이수)의 결론을 종합해
> `sim/calibration/{prior,fit_npw,fit_ptw,predict,drift}.py`의 **설계 명세**를 확정한다.
> 이 노트는 코드를 넣지 않는다(`sim/`은 다른 크론이 동시에 쓴다) — 산출물은 이 노트 +
> `agents/cmp-calibrator/PROFILE.md`의 `## 구현 요청`이다.

## 0. 이 노트가 종합하는 선행 결론

- [[bayesian-calibration-koh-discrepancy]] — `series_scale.py`는 KOH δ(x)를 상수 1자유도로
  제약한 특수 케이스.
- [[hierarchical-bayesian-npw-ptw-transfer]] — QW2008 식(7)의 계층 링크 모형과 정밀도가중
  사후분포(수축 형태)를 이미 유도·verify.
- [[uq-prediction-interval-coverage-extrapolation-warning]] — 예측구간은 KOH 분해상
  θ불확실성+δ(x)+e 세 항의 합, series_scale의 배율 CI만으로는 과소커버리지.
- [[calibration-drift-detection-recalibration-triggers]] — EWMA 통계량 분산
  `σ²_EWMA=(λ/(2-λ))σ²`(NIST 핸드북), PST2014 ARL–오경보 트레이드오프.

이번 단원은 위 넷을 **모듈 경계**로 잘라 함수 시그니처를 확정하는 것이 목적이다.

## 문헌 (이 노트에서 새로 추가)

1. **Lai, B. & Bernstein, D. S. (2024)**, "Adaptive Kalman Filtering Developed from
   Recursive Least Squares Forgetting Algorithms", *2024 American Control Conference (ACC)*,
   pp. 2088–2093. https://doi.org/10.23919/acc60939.2024.10644929 (find_open_access.py가
   Crossref로 DOI 확인·제목 일치 검증 완료, 프리프린트 arXiv:2404.10914v1 전문 6쪽을
   fitz+텍스트로 전체 판독 완료 — 이하 "LB2024". IEEE ACC는 동료심사 학회지 논문).
2. **Qian, P. Z. G. & Wu, C. F. J. (2008)** — 재인용, [[hierarchical-bayesian-npw-ptw-transfer]]에서
   원문 판독 완료(이하 "QW2008").
3. **Kennedy, M. C. & O'Hagan, A. (2001)** — 재인용, [[bayesian-calibration-koh-discrepancy]]에서
   원문 판독 완료.
4. **Polunchenko, A. S., Sokolov, G. & Tartakovsky, A. G. (2014)** — 재인용,
   [[calibration-drift-detection-recalibration-triggers]]에서 원문 판독 완료(이하 "PST2014").
5. **NIST/SEMATECH e-Handbook of Statistical Methods**, §6.3.2.4 — 재인용, 위 노트에서 이미
   인용(정부 공개문서, EWMA 정의·분산식 출처).

이 단원에서 **새로 확보한 1차 출처는 LB2024 1건**이고, 나머지 넷은 선행 단원에서 이미
원문 판독을 마친 것을 그대로 재사용한다(정직성 표지).

## 1. n에 따른 수축(shrinkage) 닫힌해 — n=0/1/5 가중치

[[hierarchical-bayesian-npw-ptw-transfer]] §2가 이미 판독한 QW2008 p.198의 `ρ0` 완전조건부
사후분포(정밀도가중평균)를 **n개의 등정밀 i.i.d. PTW 관측**(설계벡터 `yl1 = (1,...,1)`,
관측공분산 `M = σ²_obs·I`)의 특수 경우로 좁히면:

    yl1ᵀM⁻¹yl1 = n/σ²_obs,   yl1ᵀM⁻¹(yh-δ0) = (n·ȳ)/σ²_obs

이므로 사후평균은

    μ_post(n) = (u/v + n·ȳ/σ²_obs) / (1/v + n/σ²_obs)
              = w(n)·ȳ + (1-w(n))·u,   w(n) = n / (n + k),   k ≜ σ²_obs/v

`u`=NPW 기반 사전평균(=fit_npw.py 산출), `v`=그 사전분산, `k`=**"사전이 PTW 관측 몇 개어치
정보량인가"**를 나타내는 등가표본수(equivalent prior sample size)다. 이 식은 QW2008이 유도한
정밀도가중평균 형태를 `yl1=1`(순수 절편·척도 오프셋 추정, series_scale.py의 배율 `ln(s)`가
바로 이 절편이다)로 특수화한 것으로, **이 노트가 직접 유도**했다(QW2008 원문이 이 특수 케이스
수치를 표로 준 것은 아니다 — 정직성 표지).

```python verify
# verify(1): 위에서 유도한 w(n)=n/(n+k) 닫힌해를, 실제 정밀도가중 사후평균 계산(1절 원식)과
# n=0,1,5에서 직접 대조한다. k(=sigma_obs^2/v, 사전의 등가표본수)를 3가지로 바꿔가며 확인.
import numpy as np

u_prior = 1.0   # NPW 기반 사전평균 (예: fit_npw가 준 ln(scale) 사전)
rng = np.random.default_rng(0)


def posterior_mean_full(u, v, sigma_obs2, ybar, n):
    """QW2008 p.198 정밀도가중평균, yl1=1(n개), M=sigma_obs^2 I 특수화."""
    if n == 0:
        return u
    data_prec = n / sigma_obs2
    return (u / v + n * ybar / sigma_obs2) / (1.0 / v + data_prec)


def w_closed_form(n, k):
    return n / (n + k) if (n + k) > 0 else 0.0


for sigma_obs2, v in [(1.0, 1.0), (1.0, 0.1), (4.0, 2.0)]:
    k = sigma_obs2 / v
    for n in [0, 1, 5]:
        ybar = rng.normal(2.5, np.sqrt(sigma_obs2 / max(n, 1)))  # 참 평균 2.5짜리 PTW 데이터
        mu_full = posterior_mean_full(u_prior, v, sigma_obs2, ybar, n)
        w = w_closed_form(n, k)
        mu_closed = w * ybar + (1 - w) * u_prior
        assert abs(mu_full - mu_closed) < 1e-9, (
            f"n={n}, k={k}: 닫힌해({mu_closed:.6f})가 정밀도가중 원식({mu_full:.6f})과 "
            f"불일치 — 유도 오류.")
        if n == 0:
            assert abs(mu_full - u_prior) < 1e-12, "n=0이면 사후평균은 사전평균과 정확히 같아야 한다."

# k=1(사전이 PTW 관측 1개와 동등한 정보량)일 때 n=0/1/5 가중치를 명시적으로 보고
k = 1.0
weights = {n: w_closed_form(n, k) for n in [0, 1, 5]}
assert weights[0] == 0.0
assert abs(weights[1] - 0.5) < 1e-12          # n=1, k=1: 정확히 반반
assert abs(weights[5] - 5 / 6) < 1e-12        # n=5, k=1: 데이터 쪽으로 5/6
print("k=1일 때 n=0/1/5의 데이터 가중치 w(n):", weights)
```

**핵심**: `k`(사전 강도, 등가표본수)를 얼마로 잡느냐가 전체 설계의 유일한 손잡이라는 점이
[[hierarchical-bayesian-npw-ptw-transfer]]의 결론과 정확히 같다 — 이 노트는 그 결론을
n=0/1/5라는 **구체적 소량 데이터 지점**에서 수치로 못박은 것이다. `k`를 어떻게 고정하는지는
아래 §4(구현 요청)에 실무적 제안(디폴트 k=1 근처, 데이터가 쌓이며 재추정)으로 남긴다 — 일반
원칙은 QW2008도 제시하지 않는다(기존 노트가 이미 미검증으로 표시).

## 2. NPW→PTW 방향을 담당하는 항 — 어느 게 "prior"이고 어느 게 "우도"인가

[[hierarchical-bayesian-npw-ptw-transfer]] §1이 정리한 QW2008 §2.1~2.3의 절 구성 자체가
방향을 강제한다:

- **1단계(§2.2, QW2008 식 5)**: `yl(x)`(NPW=LE) 데이터**만**으로 GP를 적합한다. 이 적합은
  PTW 데이터를 전혀 보지 않는다.
- **2단계(§2.3, QW2008 식 7)**: 1단계에서 나온 `yl`의 **사후예측 평균**이 링크식
  `yh(x)=ρ(x)yl(x)+δ(x)+ε(x)`에 **고정 입력(fixed regressor)**으로 대입된다. `ρ,δ`의
  사전평균(`u_ρ, u_δ`)도 이 시점에 NPW 이력·물리모델에서 고정한다. 오직 `ρ,δ`만 PTW
  데이터로 갱신된다(§1의 `ptw_posterior` 함수가 갱신하는 것도 `ρ0`뿐, `yl` 쪽은 상수
  취급).

즉 **"어느 항이 방향을 담당하는가"**의 답은 단일 파라미터가 아니라 **모형 그래프의 위상
(topology)**이다 — `yl(x)`(NPW GP)에서 `yh(x)`(PTW GP)로 화살표가 나가고, 역방향 화살표는
없다(NPW 적합은 PTW 우도 항을 전혀 포함하지 않는다). Perdikaris2015 식 2.5(`Z2=ρ1·Z1+δ2`,
[[hierarchical-bayesian-npw-ptw-transfer]] §3)의 마르코프 가정("Z_{t-1}(x)가 주어지면
다른 x'의 Z_{t-1}(x')에서 더 배울 게 없다")이 이 단방향성의 수학적 근거다 — **레벨 s의
사후분포를 조건화하는 데 레벨 s+1 데이터가 전혀 등장하지 않는다**(Perdikaris2015 식 2.6).

FabSim 설계로 옮기면: `prior.py`가 물리모델 η(x,θ)를 내고, `fit_npw.py`가 그 위에
NPW 데이터로 1단계 GP(=`yl`)를 적합해 **(u_ρ, v_ρ)**(§1의 `u, v`)를 산출하고,
`fit_ptw.py`는 그 `(u_ρ,v_ρ)`를 **입력으로만** 받아 PTW 데이터로 §1의 정밀도가중
갱신을 수행한다 — `fit_ptw.py`가 `fit_npw.py`의 출력을 다시 바꾸는 경로는 설계상 없다.
이것이 "역방향이 아님"을 코드 의존성 그래프 수준에서 강제하는 방법이다.

## 3. drift: 지수망각 vs 상태공간(칼만) — 소량 데이터 판정

LB2024(§I, §IV, Table I)의 핵심 결과: **지수망각은 칼만 필터의 특수 케이스다**, 그것도
아주 좁은 특수 케이스다. LB2024 Table I 행 1~2:

    RLS(무망각):        Sigma_k = 0                     (물리적 프로세스 노이즈 없음 가정)
    지수망각(스칼라 λ): Sigma_k = (1/λ - 1)·P_k          (LB2024 Table I, 행 2)

즉 지수망각이 실제로 하는 일은 "매 스텝 공분산을 `1/λ`배로 부풀린다"는 것 뿐이며, 이는
칼만 필터의 프로세스 노이즈 `Σ_k`를 **현재 공분산에 비례하는 등방적(isotropic) 값**으로
고정한 것과 정확히 같다(LB2024 Corollary 2, 식 24). 따라서 "지수망각 vs 칼만"은 이분법이
아니라 **"구조 없는 디폴트 vs 물리 구조가 들어간 일반형"**의 문제다:

- 지수망각(및 그 스칼라 확장, Table I 행 3~4)은 **어느 축이 얼마나 빨리 변하는지에 대한
  물리적 사전지식을 전혀 쓰지 않는다** — λ 하나로 "전체적으로 최근 데이터를 얼마나
  중시할지"만 정한다.
  - λ→0(빠른 망각)에서 σ²_EWMA=λ/(2-λ)·σ²(NIST 핸드북 §6.3.2.4,
    [[calibration-drift-detection-recalibration-triggers]] §2.1) 공식을 그대로 뒤집으면
    **등가표본수** `n_eff(λ) = (2-λ)/λ`를 얻는다(아래 verify에서 [[calibration-drift-detection-recalibration-triggers]]
    verify(1)이 이미 재현한 PST2014 Table 4.1의 λ값 0.275/0.096/0.049에 대해 계산).
- 칼만/상태공간은 `A_k`(상태전이)에 **물리적으로 알려진 시상수를 직접 넣을 수 있다** —
  FabSim은 이미 `conditioner_pcr_decay`(τ=27.4h, [[calibration-drift-detection-recalibration-triggers]]
  §1②)라는 **알려진 지수감쇠 시상수**를 Γ/S 축에 갖고 있다. 이 지식을 가진 축에서
  구조없는 스칼라 λ 하나로 재추정하는 것은 이미 아는 정보를 버리는 것이다 — LB2024
  §IV가 말하듯 "구조 없는 지수망각은 Σ_k=(1/λ-1)P_k라는 **가장 단순한** 프로세스 노이즈
  선택에 불과하고, 실제 물리적 교란 형태를 알면 그 형태를 Σ_k에 직접 넣는 것이
  일반적으로 더 낫다"(LB2024는 이를 마찰-충돌 disturbance 사례로 예시, 결과는 Fig.2-4
  — KF*가 λ_k를 순간적으로 낮춰 프로세스 노이즈를 키운 시점에 정확히 상태추정
  오차가 줄어드는 것을 확인).

아래 verify(2)가 재현하는 구체 수치: PST2014 Table 4.1의 λ=0.275(오경보 ARL γ=100)는
n_eff≈6.27배, λ=0.096(γ=1000)는 n_eff≈19.8배, λ=0.049(γ=10000)는 n_eff≈39.8배 — 몬테카를로
시뮬레이션(40만 스텝)으로 5% 이내 재현했다(문헌값 λ 자체는 PST2014 폐형식에서 온 것이고,
n_eff는 그 λ를 NIST 분산식으로 환산한 이 노트의 산출물이다).

**판정**: 소량 데이터(n=0~5)일수록 판정은 오히려 명확해진다 — 데이터가 적을수록 사후분포는
prior(=구조)에 크게 의존하는데(§1의 w(n) 작음), 구조 없는 지수망각은 이 상황에서 "얼마나
빨리 잊을지"를 알려줄 데이터 자체가 부족하다(λ를 데이터로 튜닝하기 힘들다). **물리적
시상수가 알려진 축(Γ, S)은 상태공간(칼만, A_k에 τ=27.4h를 직접 인코딩)을, 물리적 시상수가
없는 축(Kp — 슬러리 로트 변동에 알려진 감쇠 모형이 없음, [[calibration-drift-detection-recalibration-triggers]]
§1③)은 지수망각(NIST EWMA, λ를 PST2014류 ARL–오경보 트레이드오프로 설계)을 쓴다.** 이는
"자유도를 늘리지 않는다"는 §4의 설계 제약과도 맞다 — 지수망각(스칼라 λ 1개)이 이미 아는
구조(τ)를 다시 데이터로 추정하려 들면 오히려 자유도 낭비다.

```python verify
# verify(2): NIST EWMA 분산식 sigma_EWMA^2=(lam/(2-lam))*sigma^2 을 뒤집은 등가표본수
# n_eff(lam)=(2-lam)/lam 을, [[calibration-drift-detection-recalibration-triggers]]가 이미
# PST2014 Table 4.1에서 재현한 (lam, A, gamma) 세 쌍에 적용해 계산하고, 몬테카를로
# EWMA 정상상태 분산으로 독립 재현(동일 시드 실험 재사용 대신 새로 시뮬레이션).
import numpy as np


def n_eff(lam):
    return (2 - lam) / lam


cases = [0.275, 0.096, 0.049]  # PST2014 Table 4.1의 (lam,A,gamma)=(100,1000,10000) 설계값
neffs = [n_eff(l) for l in cases]
assert neffs[0] < neffs[1] < neffs[2], (
    "lam이 작을수록(느리게 망각) 등가표본수는 커져야 한다: " + str(neffs))

# 몬테카를로로 EWMA 정상상태 분산을 재현하고 n_eff = sigma^2 / var(EWMA) 로 역산해 대조.
# lam이 작을수록(0.049) 자기상관 시간이 길어 수렴이 느리므로 스텝 수를 넉넉히 준다.
rng = np.random.default_rng(2)
sigma2 = 1.0
for lam, neff_formula in zip(cases, neffs):
    z = 0.0
    hist = []
    nsteps, burn = 400000, 20000
    for t in range(nsteps):
        y = rng.normal(0.0, np.sqrt(sigma2))
        z = lam * y + (1 - lam) * z
        if t > burn:  # 정상상태만 사용(초기 과도상태 제외)
            hist.append(z)
    var_mc = np.var(hist)
    neff_mc = sigma2 / var_mc
    rel_err = abs(neff_mc - neff_formula) / neff_formula
    assert rel_err < 0.05, (
        f"lam={lam}: 몬테카를로 n_eff={neff_mc:.2f}가 닫힌해 n_eff={neff_formula:.2f}와 "
        f"{rel_err:.1%} 차이 — 과도함.")
    print(f"lam={lam}: n_eff(닫힌해)={neff_formula:.2f}, n_eff(MC)={neff_mc:.2f}")

# LB2024 Table I 행2(Sigma_k=(1/lam_RLS-1)P_k, RLS 관례: lam_RLS=1이면 무망각)와
# NIST EWMA(lam=1이면 직전값만 사용=n_eff=1)는 lam의 "방향"이 정반대 관례임을 명시.
# 이 노트는 NIST/PST2014 관례(lam=신규관측 가중치)만 쓰고, LB2024의 lam_RLS는
# Sigma_k 형태(구조 없는 프로세스 노이즈)를 인용하는 데만 쓴다 — 두 lam을 같은 축에 섞지 않는다.
assert (1 / 1.0 - 1) == 0.0  # LB2024: lam_RLS=1(무망각) => 추가 프로세스 노이즈 0, RLS와 동일
```

## 4. `series_scale.py`와의 접합 — 자유도 1개 제약을 지키는 방법

`series_scale.py`(`sim/calibration/series_scale.py`)는 계열당 배율 `s`(=exp(ln s), 자유도
1개) 하나만 역산하고 형상은 절대 바꾸지 않는다는 설계 제약을 갖는다(파일 최상단 docstring).
이번 단원이 제안하는 계층 구조는 **이 자유도 수를 늘리지 않는다** — `ln(s)`라는 스칼라
하나를 "직접 데이터에서 역산"하던 것을, "NPW 사전(u) + PTW 데이터(n개)의 정밀도가중 평균"
(§1)으로 **재료만 바꿔 같은 스칼라 하나**를 내는 것으로 바꾼다:

- `fit_npw.py`: NPW 데이터에 `fit_series_scale`(기존 함수, 그대로 재사용)을 적용해 얻은
  `(scale, mape, ci)`를 **§1의 (u, v)로 변환**해서 넘긴다(u=ln(scale), v=부트스트랩 CI
  폭에서 역산한 분산). 즉 `fit_npw.py`는 새 통계량을 만드는 게 아니라 기존
  `fit_series_scale`의 출력을 계층모델의 사전으로 **재포장**한다.
- `fit_ptw.py`: PTW 데이터(n장)에 대해 §1의 `posterior_mean_full`을 적용해 **같은 스칼라
  `ln(s)`**의 사후값을 내되, 입력 사전이 물리모델(η, 기존 `series_scale` 방식대로 n=0이면
  물리모델 그대로)이 아니라 **NPW 사후**라는 점만 다르다. n_PTW=0이면 §1 verify가 보였듯
  사후=NPW 사전 그대로이고, `series_scale.py`가 이미 처리하는 "1점 배율은 신뢰구간을
  낼 수 없다"는 경고(코드의 `notes` 필드)는 그대로 유지한다.
- `predict.py`: [[uq-prediction-interval-coverage-extrapolation-warning]]이 이미 설계한
  `predict_interval`(배율 분산 + 잔차 분산 합산)을 그대로 쓰되, "배율 분산"의 출처가
  `fit_series_scale`의 부트스트랩이 아니라 §1의 사후분산 `σ²_ρ/(1/v+n/σ²_obs)`로 바뀐다 —
  **API 시그니처는 바뀌지 않는다**, 분산의 계산 출처만 바뀐다.
- `drift.py`: §3의 판정에 따라 두 갈래로 구현한다. (a) Γ,S처럼 물리 시상수가 있는 축은
  상태공간형(`A_k`에 τ=27.4h 인코딩), (b) Kp처럼 물리 시상수가 없는 축은 §3 verify(2)의
  `n_eff(λ)`를 갖는 EWMA — 단, [[calibration-drift-detection-recalibration-triggers]]
  §3 규칙 C(소모품 교체 이벤트)가 트리거되면 `fit_ptw.py`의 **n을 0으로 리셋**해 §1의
  사후가 NPW 사전으로 완전히 되돌아가게 한다(사후분산도 §1 n=0 케이스로 복귀) — "잔차
  이력 초기화"라는 기존 노트의 표현을 이 노트의 언어로 정확히 옮기면 **"n_PTW←0"** 이다.
  이 재설정도 자유도를 늘리지 않는다(같은 스칼라의 값이 리셋될 뿐, 새 파라미터가
  생기지 않는다).

이 절 전체의 요지: 계층 베이지안화는 **"무엇을 추정하는가"(자유도 개수)를 바꾸지 않고
"그 추정치가 어디서 오는가"(사전의 출처와 갱신 규칙)만 바꾼다** — `series_scale.py`의
설계 제약(구조는 물리, 축척만 데이터)과 정확히 같은 정신이다.

## 정직성 표지

- §1의 `w(n)=n/(n+k)` 닫힌해는 **이 노트가 QW2008 식을 i.i.d. 등정밀 특수 케이스로 직접
  유도**한 것이다 — QW2008 원문이 이 특수형을 명시적으로 표로 준 것은 아니다.
- §3의 "물리 시상수 있으면 칼만, 없으면 지수망각" 판정은 LB2024의 **일반 이론적 결과**
  (지수망각=칼만의 프로세스노이즈 특수형)에서 이 노트가 내린 **설계 판단**이다 — LB2024
  자체가 CMP 재보정 사례를 다루지는 않는다(질량-스프링-댐퍼 충돌 사례). 따라서 이 판정은
  "문헌이 직접 CMP에 적용해 검증한 것"이 아니라 "일반 이론을 FabSim 맥락에 적용한 추론"
  이라는 점을 명시한다 — **미검증(적용 판단)**.
- `k`(사전 강도, 등가표본수)의 기본값 선택은 이번 조사에서 일반 원칙을 확보하지 못했다
  ([[hierarchical-bayesian-npw-ptw-transfer]] 구현 요청이 이미 남긴 미해결과 동일 사안) —
  §4 구현 요청에 실무적 제안만 남긴다.
- 조사 범위 지침("대규모 데이터 전제 논문 제외")에 따라 딥러닝 기반 캘리브레이션·전이학습
  논문은 검색하지 않았다 — **범위 밖이라 뺐다**(못 찾은 것과 다름).

## 관련 노트

- [[bayesian-calibration-koh-discrepancy]] — KOH δ(x)와 series_scale.py의 대응.
- [[hierarchical-bayesian-npw-ptw-transfer]] — 이 노트가 특수화한 QW2008 정밀도가중 사후식의
  원 유도, Perdikaris2015 AR(1) 마르코프 가정.
- [[gp-regression-small-data-kernel-prior-mean]] — `fit_npw.py`가 산출하는 `yl(x)` 자체
  모형(물리 기반 평균함수 GP)의 커널 설계 근거.
- [[uq-prediction-interval-coverage-extrapolation-warning]] — `predict.py`가 재사용하는
  `predict_interval`/`extrapolation_warning` API.
- [[calibration-drift-detection-recalibration-triggers]] — `drift.py`가 재사용하는
  EWMA/CUSUM 관리도, 소모품 리셋 규칙 C, τ=27.4h 시상수.

## 구현 요청 초안

(PROFILE.md `## 구현 요청`에 모듈별 함수 시그니처로 확정해 옮긴다.)
