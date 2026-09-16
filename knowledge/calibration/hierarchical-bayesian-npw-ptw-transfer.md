# 전이학습: NPW 보정치를 prior로 PTW 잔차 학습 — 계층 베이지안

> 상태: 1차 출처 2건(원문 PDF/전문 확보·직접 판독), 상호검증용 3건째(Kennedy & O'Hagan
> 2001, [[bayesian-calibration-koh-discrepancy]] 노트에서 이미 원문 판독 완료된 것을
> 재인용)를 더해 3건. Kennedy & O'Hagan (2000, Biometrika)의 원문 자체(AR(1) 다중신뢰도
> 모형의 최초 출처)는 이번 조사에서 **확보 실패**했다 — 아래 "정직성 표지" 참조.

## 문헌

1. **Qian, P. Z. G. & Wu, C. F. J. (2008)**, "Bayesian Hierarchical Modeling for
   Integrating Low-Accuracy and High-Accuracy Experiments", *Technometrics*, 50(2),
   192–204. DOI: 10.1198/004017008000000082 (find_open_access.py로 DOI 확인, 저자
   개인 페이지 `www2.isye.gatech.edu/~jeffwu/publications/bayesian_hiermodel.pdf`에서
   전문 PDF 직접 확보·전체 36쪽 fitz 판독 완료 — 이하 "QW2008").
2. **Perdikaris, P., Venturi, D., Royset, J. O. & Karniadakis, G. E. (2015)**,
   "Multi-fidelity modelling via recursive co-kriging and Gaussian–Markov random
   fields", *Proc. R. Soc. A*, 471, 20150018. DOI: 10.1098/rspa.2015.0018
   (find_open_access.py로 Unpaywall 경로 OA 확인, PMC(PMC4528652) 전문 HTML 확보·
   판독 — 이하 "Perdikaris2015". Kennedy & O'Hagan(2000)의 1계 자기회귀(AR(1))
   다중신뢰도 모형을 §2c에서 원 논문 표기 그대로 재도출한다.)
3. **Kennedy, M. C. & O'Hagan, A. (2001)**, "Bayesian Calibration of Computer
   Models", *J. R. Statist. Soc. B*, 63(3), 425–464. DOI: 10.1111/1467-9868.00294.
   ([[bayesian-calibration-koh-discrepancy]] 노트에서 이미 원문 §1~4 직접 판독 완료 —
   이 노트에서는 δ(x)·ρ 표기의 선행 정의로만 재인용한다.)

## 1. NPW→PTW를 "저정밀·다량 실험 vs 고정밀·소량 실험"의 계층 베이지안 틀로 대응시키기

QW2008 §1의 문제 설정은 "낮은 정확도지만 값싸고 풍부한 실험(LE)"과 "높은 정확도지만
비싸고 희소한 실험(HE)"을 통합하는 것이다(QW2008 p.192, Abstract 및 §1). 이 틀은
FabSim의 NPW→PTW 관계와 구조적으로 대응한다:

- **LE ↔ NPW**: 블랭킷 웨이퍼는 패턴이 없어 측정·실험이 빠르고 저렴하며 다량 확보
  가능하다(QW2008의 "빠른 근사 코드"에 대응).
- **HE ↔ PTW**: 패턴 웨이퍼는 실제 고객 레시피 조건에서만 얻어지고 수량이
  "레시피당 수십 장 규모"(SCOPE.yaml cmp-calibrator절)로 제한된다(QW2008의 "느리고
  비싼 상세 실험"에 대응).

QW2008 §2.3, 식 (7)이 제시하는 연결(link) 모형:

    yh(xi) = ρ(xi)·yl(xi) + δ(xi) + ε(xi),  i = 1,...,n1      (QW2008 식 7)

여기서 `yl`은 LE(=NPW) 출력, `yh`는 HE(=PTW) 출력, `ρ(·)`는 GP(ρ0, σ²_ρ, φ_ρ)를 따르는
**척도 조정**, `δ(·)`는 GP(δ0, σ²_δ, φ_δ)를 따르는 **위치 조정**, `ε(·)`는 측정오차다
(QW2008 p.196). 저자들은 이 식이 Kennedy & O'Hagan(2000/2001)의 자기회귀 모형을
"상수 하나였던 척도조정을 GP로 확장"한 것이라고 명시한다(QW2008 §2.8, p.202: "Kennedy
and O'Hagan uses an autoregressive model as an adjustment model with a constant chosen
for scale adjustment, which cannot handle complex scale change from LE to HE"). 즉
FabSim 맥락으로 옮기면:

- `yl(x)` = NPW에서 얻은 물리 prior 기반 예측(순수 물리모델 또는 NPW 데이터로 이미
  적합된 GP).
- `ρ(x), δ(x)` = **NPW→PTW 전이 시 필요한 척도·위치 보정** — 패턴밀도·단차·컨택트
  면적비 등으로 인한 체계적 차이를 흡수하는 항.
- `ε(x)` = PTW 측정 자체의 노이즈.
- 이 전체가 "계층"인 이유는 `yl`을 먼저 자체 GP(QW2008 §2.2, 식 5)로 적합하고, 그
  적합 결과 위에 `ρ, δ`라는 **두 번째 층의 GP**를 올려 HE 데이터로 갱신하기 때문이다
  (QW2008 §2.1의 표준 베이지안 GP가 §2.2의 LE 모형에 쓰이고, §2.3의 링크 모형이 그
  위에 얹힌다 — 계층 구조 자체가 논문 §2의 절 구성이 보여주는 바다).

## 2. 사후분포 형태 — NPW prior 정밀도가 PTW 사후평균의 수축(shrinkage)을 결정한다

QW2008 §2.4(p.198, 식 없음 명명이지만 원문 유도의 핵심)가 조건부 사후분포로 제시하는
`ρ0`의 완전조건부 분포(θ3 조건부, MCMC의 한 스텝, p.198~199):

    p(ρ0 | yl, yh, ...) ~ N( (uρ/vρ + yl1ᵀM⁻¹(yh − δ0·1)) / (1/vρ + yl1ᵀM⁻¹yl1),
                              σ²_ρ / (1/vρ + yl1ᵀM⁻¹yl1) )              (QW2008 유도, p.198)

- `uρ`는 ρ0의 사전평균(=NPW 단독 분석 또는 과거 이력에서 얻은 "척도 보정 사전 기대값"),
  `vρ`는 사전분산 스케일(작을수록 사전이 강함), `yl1ᵀM⁻¹yl1`은 PTW 데이터가 제공하는
  정보량(설계행렬의 관측정밀도, PTW 표본 수·산포에 비례해 커진다).
- 형태 자체가 **정밀도 가중평균**(precision-weighted average)이다: 사전 정밀도
  `1/vρ`와 데이터 정밀도 `yl1ᵀM⁻¹yl1`의 합으로 나눈 가중합이 사후평균이다. 사전
  정밀도가 커지면(=NPW로부터 얻은 사전이 확신에 차 있으면, `vρ→0`) 사후평균은
  `uρ`(NPW 기반 사전값)로 수축하고, PTW 데이터가 늘어나면(정밀도 `yl1ᵀM⁻¹yl1` 증가)
  사후평균은 PTW 데이터만의 추정치로 이동하며 사후분산은 단조 감소한다 — 아래 verify
  블록 (A)(B)가 이 두 성질을 QW2008의 식 형태 그대로 구현해 확인한다.

## 3. AR(1) 다중신뢰도 모형과 불확실성 전파 — Perdikaris2015의 재도출

Perdikaris2015 §2c(식 2.5~2.7)는 Kennedy & O'Hagan(2000)의 자기회귀 co-kriging을
s-레벨로 일반화해 재도출한다. NPW를 레벨 1, PTW를 레벨 2로 두면:

    Z2(x) = ρ1(x)·Z1(x) + δ2(x)                                   (Perdikaris2015 식 2.5, s=2)

이고, 마르코프 성질(식 2.6, "given Z_{t-1}(x), Z_t(x)를 다른 지점의 Z_{t-1}(x')로부터
더 배울 것이 없다")을 가정하면 PTW 레벨의 사후분산은(식 2.7, s=2로 축약):

    Var[Z2 | y2,y1] = Σ_Z2 + ρ1² · Σ_Z1                            (Perdikaris2015 식 2.7, s=2)

즉 **PTW 예측의 총 불확실성 = PTW 자체 잔차 분산 + (NPW→PTW 결합계수)² × NPW 자체
잔차 분산**이다. 이것이 시사하는 바는: NPW의 (자체) 불확실성이 얼마나 PTW 예측
불확실성으로 "새어 들어오는지"는 오직 결합계수 ρ1의 크기에 달려 있다 — ρ1이 작으면
(NPW와 PTW의 척도 연결이 약하면) NPW 쪽 불확실성은 PTW 예측에 거의 영향을 주지
않고, ρ1이 크면(강하게 결합되면) NPW의 불확실성이 그대로 더해진다. 아래 verify
블록 (C)가 이 단조성을 확인한다.

## 4. FabSim에의 시사점 (`sim/`은 읽기 전용, 코드 없음)

- QW2008·Perdikaris2015 둘 다 "링크 함수(ρ,δ 또는 ρ1)의 사전분포 폭"이 전이 강도를
  결정하는 유일한 손잡이임을 보여준다. NPW 데이터가 많다고 해서 PTW 사후평균이
  자동으로 NPW값에 수렴하는 게 아니라, **NPW→PTW 링크 파라미터(ρ,δ)의 사전 확신도를
  얼마나 강하게 주느냐**가 수축 정도를 결정한다 — 이는 `agents/cmp-calibrator/
  PROFILE.md`의 "구현 요청" 절에 남길 만한 설계 변수다(아래 참고).
- QW2008 §2.8(p.202)이 명시하듯 Kennedy-O'Hagan의 "척도 조정 = 상수"보다 QW2008의
  "척도 조정 = GP(x에 따라 변함)"이 더 유연하다. FabSim에서 패턴밀도·단차 등 x에
  따라 NPW→PTW 괴리가 달라진다면(예: 저밀도 영역과 고밀도 영역에서 다른 보정이
  필요하다면) 상수 배율(`series_scale.py` 방식, [[bayesian-calibration-koh-discrepancy]]
  노트가 이미 KOH 틀로 분석함)보다 QW2008 식 링크가 원칙적으로 더 적합할 수 있다 —
  단, 그만큼 PTW 데이터가 더 필요하다는 트레이드오프가 있다(QW2008은 학습에 HE
  24~36점을 썼다 — FabSim의 "레시피당 수십 장" 규모와 같은 자릿수이나, QW2008
  사례는 반복측정 없는 순수 계산실험이라 노이즈 구조가 다르다는 차이는 있다).

## 구현 요청 (실제 코드는 `agents/cmp-calibrator/PROFILE.md`에 별도 기록)

이 노트가 제시하는 손잡이(사전 정밀도 `vρ, vδ`)를 실제로 어떻게 정하는지는 QW2008이
데이터 기반 경험적 베이즈(§2.4, p.198)로 처리한다 — 이 부분은 다음 단원(Lv2-2
불확실성 정량화)에서 더 깊게 다뤄야 한다(미검증: QW2008이 vρ,vδ 자체를 어떻게
고정했는지는 "사전 하이퍼파라미터"로 논문이 명시한 값만 확인했고, 그 값을 어떤
기준으로 골랐는지의 일반 원칙은 이번 조사에서 확인하지 못함).

## 정직성 표지

- **Kennedy & O'Hagan (2000, Biometrika 87(1), 1–13)의 원문 확보 실패.** 저자
  개인 페이지(tonyohagan.co.uk)는 초록만 제공하고 PDF/포스트스크립트 링크가 없다.
  academia.edu 사본은 403으로 접근 차단. sci-hub 계열 미러(sci-hub.se, sci.bban.top)는
  모두 이 DOI에 대해 404 또는 "논문을 찾을 수 없습니다"를 반환했다 — sci-hub
  전멸([[fabsim-literature-access-fallbacks]] 메모와 일치). 이 논문의 AR(1) 모형
  자체는 **Perdikaris2015가 원 표기 그대로 재도출한 것을 2차 경유로 확인**했다(식
  2.5~2.7, 위 §3). 원논문의 수치 예제나 토론 부분은 이번 조사에서 전혀 보지 못했다.
- QW2008은 36쪽 전문을 fitz로 완전 판독했다(스캔본이 아니라 텍스트 추출이 정상
  동작하는 PDF였다).
- Perdikaris2015는 PMC HTML 전문을 curl로 확보해 판독했다(§1~2 도입부와 co-kriging
  절 §2c를 집중 판독, 이후 GMRF/SPDE 절(§3 이후)은 이번 조사 범위 밖이라 읽지 않았다
  — Hilbert 공간 근사·SPDE는 이 단원(계층 베이지안 전이) 주제와 직결되지 않는다고
  판단해 의도적으로 생략).
- verify 블록 (A)(B)는 QW2008이 실제로 유도한 조건부 사후분포 식을 M=I(독립 관측)로
  단순화해 그대로 구현한 것이다 — 논문이 준 수치를 재현한 것이 아니라 **논문이 유도한
  수식의 정성적 성질**(수축·분산감소)을 코드로 확인한 것이다.
- verify 블록 (C)는 Perdikaris2015 식 2.7을 s=2로 축약해 그대로 구현·성질 확인한
  것이다 — 마찬가지로 수식 형태의 정성적 확인이다.
- verify 블록 (D)는 (Qian & Wu, 2008) Table 3(p.31)이 보고한 4가지 방법의 SRMSE(BHGP 8%,
  분리분석(SEP) 15%, QIAN 9%, KO 7% — 논문 표기로는 0.08/0.15/0.09/0.07)를 논문이 실은
  표의 개별 예측값(byh)에서 **직접 재계산**해 대조한 것이다 — 단순 전사 대조가 아니라
  독립 재현이며, (Qian & Wu, 2008) 재계산값이 문헌값과 1.5%p 이내로 일치함을 확인했다.

## 관련 노트

- [[bayesian-calibration-koh-discrepancy]] — KOH2001의 `δ(x)`·`ρ` 표기, 그리고
  `series_scale.py`를 "δ(x)≡상수"의 극단적 특수 케이스로 분석한 선행 노트. 이 노트의
  QW2008 링크 모형(식 7)은 그 특수 케이스를 "x에 따라 변하는 GP"로 일반화한 것이다.
- [[gp-regression-small-data-kernel-prior-mean]] — 소량 데이터 GP 커널·평균함수 설계.
  이 노트의 `yl(x)` 자체 모형(QW2008 §2.2, 식 5)이 그 노트가 다룬 물리 기반 평균함수
  GP와 같은 대상이다.
- Lv2-2(불확실성 정량화·외삽 경고) 단원에서 QW2008 §2.4의 경험적 베이즈 하이퍼파라미터
  추정(vρ, vδ 결정법)을 이어서 확인할 것 — 이번 단원에서는 "형태"만 확인했고 "값을
  어떻게 고르는가"는 미해결로 남겼다.

```python verify
# verify (A)(B): QW2008 p.198의 rho0 완전조건부 사후분포를 M=I로 단순화해 구현하고,
# (A) NPW 사전 정밀도(1/v_rho)가 커질수록 사후평균이 NPW 사전값(u_rho)으로 수축하는지,
# (B) PTW 데이터 n이 늘수록 사후분산이 단조 감소하는지 확인한다.
import numpy as np

rng = np.random.default_rng(1)
rho_true = 0.9
sigma_rho2 = 1.0
u_rho = 0.5  # NPW 기반 사전평균(참값 0.9와 의도적으로 다르게 설정 — 수축을 뚜렷이 보기 위함)


def ptw_posterior(u_rho, v_rho, sigma_rho2, yl1, yh, delta0=0.0):
    # QW2008 p.198: mean = (u/v + yl1^T M^-1 (yh-delta0)) / (1/v + yl1^T M^-1 yl1), M=I
    data_precision = yl1 @ yl1
    data_term = yl1 @ (yh - delta0)
    post_mean = (u_rho / v_rho + data_term) / (1.0 / v_rho + data_precision)
    post_var = sigma_rho2 / (1.0 / v_rho + data_precision)
    return post_mean, post_var


n_ptw = 5
x_ptw = rng.uniform(0.5, 2.0, n_ptw)
y_ptw = rho_true * x_ptw + rng.normal(0, 0.02, n_ptw)

m_tight_prior, _ = ptw_posterior(u_rho, 1e-6, sigma_rho2, x_ptw, y_ptw)
m_loose_prior, _ = ptw_posterior(u_rho, 1e6, sigma_rho2, x_ptw, y_ptw)
ols_estimate = (x_ptw @ y_ptw) / (x_ptw @ x_ptw)

assert abs(m_tight_prior - u_rho) < 1e-3, (
    f"NPW 사전이 매우 정밀하면(v_rho->0) 사후평균({m_tight_prior:.4f})이 NPW 사전값"
    f"({u_rho})으로 완전히 수축해야 한다 — QW2008 정밀도가중평균 형태의 직접 귀결."
)
assert abs(m_loose_prior - ols_estimate) < 1e-3, (
    f"NPW 사전이 매우 무정보적이면(v_rho->inf) 사후평균({m_loose_prior:.4f})이 PTW 데이터만의 "
    f"최소제곱 추정치({ols_estimate:.4f})로 수렴해야 한다."
)

v_rho = 1.0
variances = []
for n in [2, 5, 10, 20, 40]:
    xs = rng.uniform(0.5, 2.0, n)
    ys = rho_true * xs + rng.normal(0, 0.02, n)
    _, v = ptw_posterior(u_rho, v_rho, sigma_rho2, xs, ys)
    variances.append(v)

assert all(variances[i] > variances[i + 1] for i in range(len(variances) - 1)), (
    f"PTW 표본 수 n이 늘수록({[2,5,10,20,40]}) 사후분산은 단조 감소해야 한다: {variances}"
)
```

```python verify
# verify (C): Perdikaris2015 식 2.7(s=2로 축약)을 구현 — PTW 예측 총분산에 NPW 잔차
# 불확실성이 결합계수 rho1의 제곱에 비례해 새어 들어오는지 확인한다.
def cokriging_level2_variance(var_z2, var_z1, rho1):
    return var_z2 + rho1 ** 2 * var_z1


var_z1 = 0.05  # NPW 레벨 자체 잔차 분산(다량 데이터라 작다)
var_z2 = 0.20  # PTW 레벨 자체 잔차 분산(소량 데이터라 크다)

v_weak_link = cokriging_level2_variance(var_z2, var_z1, rho1=1e-6)
assert abs(v_weak_link - var_z2) < 1e-3, (
    "rho1->0(NPW-PTW 결합이 없다시피 하면) PTW 총분산은 PTW 자체 분산으로 수렴해야 한다 "
    "— NPW 쪽 불확실성이 전파되지 않는다."
)

v_strong_link = cokriging_level2_variance(var_z2, var_z1, rho1=1.0)
assert abs(v_strong_link - (var_z2 + var_z1)) < 1e-9, (
    "rho1=1(완전결합)이면 NPW 잔차분산이 그대로 더해져야 한다 — 식 2.7의 정의 자체."
)

rhos = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
vs = [cokriging_level2_variance(var_z2, var_z1, r) for r in rhos]
assert all(vs[i] <= vs[i + 1] for i in range(len(vs) - 1)), (
    f"|rho1| 증가에 따라 PTW 총분산은 단조 비감소해야 한다: {vs}"
)
```

```python verify
# verify (D): QW2008 Table 3(p.31, Linear Cellular Alloy 11개 held-out 지점)의
# 개별 예측값(byh)에서 SRMSE를 직접 재계산해, 논문이 보고한 값(0.08/0.15/0.09/0.07,
# p.31 본문)과 대조한다. 표를 그대로 옮긴 것이 아니라 표 안의 원시 예측값으로부터
# SRMSE 공식(본문 p.31)을 독립적으로 재적용한 것이다.
import numpy as np

yh = [25.82, 19.77, 20.52, 18.78, 24.68, 22.30, 23.33, 32.85, 34.80, 36.11, 27.36]
byh_bhgp = [23.57, 23.61, 20.20, 16.81, 26.01, 22.76, 23.18, 37.07, 34.33, 35.90, 26.04]
byh_sep = [23.22, 26.67, 22.26, 16.32, 23.76, 20.32, 21.65, 34.38, 31.75, 31.10, 21.36]
byh_qian = [24.20, 25.00, 20.46, 17.29, 24.82, 21.90, 22.67, 35.80, 33.28, 35.86, 26.15]
byh_ko = [28.66, 22.97, 20.24, 17.34, 25.86, 21.76, 22.94, 33.85, 31.89, 34.87, 25.49]


def srmse(pred, obs):
    pred = np.array(pred)
    obs = np.array(obs)
    return float(np.sqrt(np.mean(((pred - obs) / obs) ** 2)))


literature_srmse = {"BHGP": 0.08, "SEP": 0.15, "QIAN": 0.09, "KO": 0.07}
recomputed = {
    "BHGP": srmse(byh_bhgp, yh),
    "SEP": srmse(byh_sep, yh),
    "QIAN": srmse(byh_qian, yh),
    "KO": srmse(byh_ko, yh),
}

for k in literature_srmse:
    diff = abs(recomputed[k] - literature_srmse[k])
    assert diff < 0.015, (
        f"{k}: 표 원시값으로 재계산한 SRMSE {recomputed[k]:.3f}가 논문 보고값 "
        f"{literature_srmse[k]} (p.31 본문)과 0.015 이내로 일치해야 한다. 차이={diff:.4f}"
    )
```
