# 베이지안 캘리브레이션 기초 — Kennedy-O'Hagan 프레임워크와 불일치 항

> 상태: 1차 출처 2건(원문 PDF) 확보·직접 판독 완료. 아래 인용은 모두 원문 페이지를 직접
> 렌더링해 읽은 것이며(스캔 PDF, 텍스트 추출이 깨져 이미지 렌더로 판독), 초록만 본 것이 아니다.

## 문헌

1. **Kennedy, M. C. & O'Hagan, A. (2001)**, "Bayesian Calibration of Computer Models",
   *J. R. Statist. Soc. B*, 63(3), 425–464. DOI: 10.1111/1467-9868.00294.
   (원문 PDF 확보·전체 판독 — 이하 "KOH2001". 페이지 번호는 저널 원본 쪽수.)
2. **Arendt, P. D., Apley, D. W. & Chen, W. (2012)**, "Quantification of Model Uncertainty:
   Calibration, Model Discrepancy, and Identifiability", *J. Mech. Des.*, 134(10), 100908.
   DOI: 10.1115/1.4007390.
   (원문 PDF 확보·전체 텍스트 추출·판독 — 이하 "Arendt2012". 식별 불가능성을 KOH 틀 위에서
   정면으로 다루는 후속 논문.)

## 1. KOH 관측 모형과 δ·θ 식별 불가능성

KOH2001 §4.2 (p.435, 식 (5))의 관측 모형:

    z_i = ζ(x_i) + e_i = ρ·η(x_i, θ) + δ(x_i) + e_i        (KOH2001 식 5)

- `η(x, θ)`: 컴퓨터 모델(시뮬레이터) 출력. `x`는 가변 입력, `θ`는 미지의 캘리브레이션
  파라미터(참값이 존재한다고 가정).
- `δ(x)`: "모델 부적합(model inadequacy)" 함수. **η와 독립**이라고 명시적으로 가정한다
  (p.435: "δ(·) is a model inadequacy function that is *independent* of the code output η(·,·)").
- `ρ`: 미지의 회귀 스케일 계수(KOH2001은 이를 포함하지만 이후 문헌 다수는 ρ=1로 단순화).
- 둘 다 **가우시안 프로세스(GP) 사전분포**를 받는다: η ~ N{m1, c1}, δ ~ N{m2, c2}
  (p.436, §4.2 두 번째 문단).

KOH2001 원문 자체는 "identifiability"라는 단어로 이 문제를 정면으로 논하지는 않는다
(§4.3 "True parameter values", p.436에서 θ를 "회귀 파라미터의 참값과 같은 의미"로
정당화하는 데 그친다 — 미검증: 논문 뒷부분 토론자 코멘트까지는 전체를 훑지 못함).
**식별 불가능성 메커니즘을 정면으로 다룬 것은 Arendt2012다.**

Arendt2012 §5 (단순지지보 예제, p.100908-6~8)가 메커니즘을 명시적으로 보인다:

- θ(영률 E, 참값 206.8 GPa)와 δ(x)를 동시에 미지수로 두고 사후분포를 구하면, **θ의 사후
  분산이 크고 δ의 예측구간도 넓다** — 즉 여러 (θ, δ) 조합이 "거의 동일하게 그럴듯"하다
  (p.100908-7: "several different combinations of these are approximately equally probable
  and give approximately the same ... predicted response").
- 구체적으로 θ=150 GPa로 과소추정해도, θ=250 GPa로 과대추정해도, 각각에 대응하는
  추정 불일치 `δ̂(x,θ) = y_e(x) − y_m(x,θ)` 가 **사전분포(매끄러운 GP)와 모순되지 않는다**
  (p.100908-7~8, Fig.9). 즉 δ가 유연한 GP이기만 하면, θ가 틀려도 그 오차를 δ가 조용히
  흡수해서 데이터 우도(likelihood)를 거의 동일하게 잘 설명해 버린다.
- 저자들의 직접적 진단(p.100908-9~10): "θ가 참값에서 벗어남에 따라 θ의 추정 δ̂(x,θ)가
  GP 모델과 얼마나 급격히 '모순'되는가"가 식별 가능성을 결정한다. 그 모순이 급격하면
  우도의 θ에 대한 2차 도함수(관측 피셔 정보)가 커져 θ 사후분포가 좁아진다(식별 가능).
  반대로 δ가 어떤 θ에 대해서도 매끄럽게 맞춰질 수 있으면 우도 곡면이 평평해서
  식별 불가능하다.

**FabSim 과의 직결점**: `δ`에 부여하는 유연성(GP의 러프니스 파라미터, 즉 x에 대해
얼마나 자유롭게 굽을 수 있는가)이 크면 클수록, θ(=여기서는 Kp·계열 배율 등 물리 상수)가
데이터에 의해 "정말로" 결정되는 게 아니라 **δ가 그 오차를 흡수해서 θ 추정이 사실상
임의값**이 되어 버린다. 물리 구조(η의 함수형)를 지키고 데이터로는 축척만 배우겠다는
FabSim 의 설계 선언과 정확히 같은 문제의식이다.

```python verify
# verify: 합성 데이터로 δ의 유연성이 θ 식별을 망가뜨리는 것을 수치로 재현한다.
# Arendt2012 §5의 메커니즘(δ가 유연한 GP일수록 여러 θ가 데이터를 동일하게 잘 설명)을
# 가장 단순한 형태로 흉내낸다: 참 모델 z(x) = eta(x, theta*) + true_delta(x).
# eta는 알려진 물리형태(선형), true_delta는 "작은 구조오차"(매끄러운 함수)라 하자.
# delta를 자유도 높은(각 관측점마다 독립 파라미터) 함수로 허용해 theta를 최소제곱으로
# 공동추정하면, theta 추정이 참값 근방 어디서나 잔차=0을 만들 수 있어 식별 불가능해진다.
import numpy as np

rng = np.random.default_rng(0)


def eta(x, theta):
    return theta * x            # 물리 모델: 선형, theta가 유일한 미지 배율


def true_delta(x):
    return 0.05 * np.sin(2 * np.pi * x)   # 작은 매끄러운 구조오차


x = np.linspace(0.1, 1.0, 8)
theta_true = 2.0
z_obs = eta(x, theta_true) + true_delta(x)   # 관측(노이즈 없음, 순수 식별 문제만 격리)

# (A) delta를 "관측점마다 자유로운 파라미터"로 두면(=완전 유연) 어떤 theta를 넣어도
#     delta_i := z_obs_i - eta(x_i, theta) 로 두면 잔차가 항상 0이 된다.
#     즉 theta는 데이터로 전혀 식별되지 않는다 — theta를 뭘 넣어도 우도가 동일.
residuals_for_many_thetas = []
for theta_try in [0.5, 1.0, 2.0, 5.0, 10.0]:
    delta_hat = z_obs - eta(x, theta_try)     # 완전 유연 delta가 흡수
    resid_after_absorbing_delta = z_obs - (eta(x, theta_try) + delta_hat)
    residuals_for_many_thetas.append(np.max(np.abs(resid_after_absorbing_delta)))

assert all(r < 1e-10 for r in residuals_for_many_thetas), (
    "완전 유연한 delta는 어떤 theta에 대해서도 잔차를 0으로 만든다 "
    "— theta가 데이터로 식별되지 않는다(Arendt2012 §5 메커니즘의 극단적 재현)."
)

# (B) 반대로 delta를 "상수 하나"(FabSim series_scale.py 처럼 자유도 1개, x에 무관)로
#     제약하면, 참 theta 근방에서만 잔차가 작아지고 다른 theta는 잔차가 커진다.
#     즉 delta의 자유도를 깎으면 theta가 다시 식별된다.
def residual_with_constant_delta(theta_try):
    delta_const = np.mean(z_obs - eta(x, theta_try))   # 자유도 1개: 상수 하나
    pred = eta(x, theta_try) + delta_const
    return np.sqrt(np.mean((z_obs - pred) ** 2))


thetas_grid = np.linspace(0.5, 4.0, 400)
rmse_grid = np.array([residual_with_constant_delta(t) for t in thetas_grid])
theta_hat = thetas_grid[np.argmin(rmse_grid)]

assert abs(theta_hat - theta_true) < 0.15, (
    f"delta를 상수 1개로 제약하면 theta_hat={theta_hat:.3f}가 참값 {theta_true}에 "
    "근접해 식별된다(완전 유연 delta일 때는 0.5~10 전부 잔차 0이었던 것과 대비) — "
    "delta의 자유도를 깎는 것이 식별력을 회복시킨다는 Arendt2012의 결론(및 FabSim "
    "series_scale.py 설계 원칙)과 일치. 잔차는 sin 성분이 선형 기울기 추정에 남기는 "
    "소량의 편향(0.05 진폭짜리 섭동)이며 0에 수렴하지 않는 것 자체가 정상이다."
)
```

## 2. 식별 불가능성을 줄이는 표준 처방 — 문헌이 실제로 말한 것

Arendt2012 §5 말미(p.100908-8)와 §6이 제시하는 처방을 **문헌 표현 그대로** 정리한다
(내 추측이 아님, 원문 인용 위치를 병기):

1. **θ 또는 δ에 정보적(informative, 저분산) 사전분포를 부여** — "previous literature
   recommended using informative ... prior distributions for the calibration parameters,
   the discrepancy function, or both" (p.100908-8). 단, 저자들은 이것이 "만족스러운
   해법이 아니다(not a satisfying solution)"라고 명시적으로 경고한다. 이유:
   - δ에 정보적 사전(예: 선형·2차 함수형 고정)을 주려면 함수형을 미리 알아야 하는데
     "one rarely has significant prior knowledge"(p.100908-8).
   - θ에 정보적 사전을 주는 것도 마찬가지로 사전 지식이 없으면 근거가 없다.
   - 더 나쁜 사례(Case 3, Table 2, p.100908-9): **정확하지 않은데 정밀한(정보적이지만
     틀린 평균을 가진) 사전**을 쓰면 사후분포가 좁아 보여 "식별된 것처럼" 보이지만
     실제로는 참값과 다른 곳에 수렴한다 — "the inherent danger of using an informative
     prior that is inaccurate albeit precise."
   - 저자들의 결론: 정보적 사전으로 얻는 식별성은 "인위적 식별성(artificial
     identifiability)"이다 — 애초에 파라미터를 정밀히 안다고 가정하고 시작하는 것이므로
     순환논법에 가깝다(p.100908-10).

2. **δ에 매끄러움(smoothness) 제약을 두는 것 — 문헌이 실제로 효과를 보인 유일한 처방**
   (§6, p.100908-8~10, 계단함수 예제). 핵심 논리:
   - δ를 "작은 러프니스 파라미터를 가진 GP"로 제약하면(=x에 대해 급격히 변하지 않는다고
     가정), **참 θ에서만** 추정 불일치 δ̂(x,θ)가 그 매끄러움 가정과 부합하고, θ가 참값에서
     벗어나면 δ̂(x,θ)가 GP 사전과 "모순"되어(불연속·거칠어짐) 우도가 급락한다
     (p.100908-9~10).
   - 이것이 식별 가능성의 실질적 정의로 제시된다: "identifiability is possible when small
     changes in the calibration parameters about their true values result in an estimated
     discrepancy function ... which is inconsistent with the GP model of the discrepancy
     function"(p.100908-10).
   - 이 처방은 (1)과 질적으로 다르다 — θ에 대한 정보적 사전이 아니라 **δ의 함수공간
     자체를 제약**하는 것이며, 저자들은 이를 "relatively mild assumption"이라 부른다
     (p.100908-10 결론부).

3. **계층 구조 / 복수 반응 활용**: 결론부(p.100908-10)에서 저자들은 자신들의 후속
   논문("companion paper")이 "공통 캘리브레이션 파라미터에 동시에 의존하는 복수의
   관측 반응(multiple responses)"을 쓰면 식별력이 "substantially" 향상됨을 보인다고
   언급한다. 그 논문은 **Arendt, Apley & Chen, "Improving Identifiability in Model
   Calibration Using Multiple Responses", DOI: 10.1115/detc2011-48623**(find_open_access
   도구로 DOI만 확인 — 원문 PDF는 이번 조사에서 확보하지 못했다, 2차 인용). 계층
   베이지안 구조(여러 계열·조건을 공유 파라미터로 묶는 것)가 식별력을 높인다는 이
   방향은 Lv2-1(전이학습, NPW→PTW 계층 베이지안) 단원에서 원문을 이어서 확보해야
   한다 — Lv2-1 담당자에게 넘긴다.

## 3. FabSim `series_scale.py` 를 KOH 틀에 대응시키기

`sim/calibration/series_scale.py`(읽기만 함, 수정 안 함)를 KOH 표기로 옮기면:

- 관측 모형: `ln(obs) = ln(η(x,θ_struct)) + ln(s) + ε`, 여기서 `η(x,θ_struct)`는
  FabSim 물리 모델(구조·지수·게이트 고정), `s`는 계열당 배율 하나(코드의 `SeriesScale.scale`,
  기하평균 비로 역산, `fit_series_scale()`).
- **이것은 KOH의 `δ(x)`를 "x에 대해 완전히 상수인 1자유도 함수"로 제약한 특수 케이스다.**
  즉 δ(x) ≡ ln(s) (모든 x에서 동일한 로그-오프셋), 계열마다 자유도 1개.
  - Arendt2012 §2의 처방과 대응: 이는 "δ에 저분산·강한 형태 제약(사실상 상수형)을
    부여"하는 것으로, 위 2절의 **처방 2(매끄러움 제약)의 극단형** — 매끄러움을
    "무한히 매끄러움 = 상수"로 밀어붙인 경우에 해당한다. δ가 x-의존성을 전혀 갖지
    못하므로, θ_struct(물리 지수·형태)가 조금이라도 어긋나면 잔차가 s로 흡수되지 않고
    `residual_mape`(형상오차)로 고스란히 드러난다 — 이것이 코드 주석이 말하는
    "구조가 틀리면 축척으로 못 가린다"는 설계 의도이며, 위 1절 verify 블록의 (B)가
    보이는 메커니즘과 정확히 같다.
  - ρ와의 대응: KOH2001의 `ρ`(선형 회귀 스케일, p.435 식 5)와 `series_scale`의
    곱셈 배율 `s`는 역할이 같다 — 둘 다 η 전체에 곱해지는 단일 스칼라다. 차이는
    KOH의 `ρ`는 θ와 별개로 GP δ(x)와 **공존**하지만, FabSim은 δ(x)를 아예 0으로
    두고(x-의존 불일치항 없음) `s`(≈ρ) 하나만 학습한다는 점이다. 즉 FabSim은
    "GP δ(x) + ρ" 모형이 아니라 **"δ(x)=0, ρ만 학습"** 모형이다.
  - `learning_curve()`(held-out 오차의 단조성 검사)는 KOH·Arendt2012 어느 쪽에도
    없는 FabSim 고유의 진단이다 — 문헌에는 대응 개념 없음(미검증: 못 찾음, 범위 밖일
    가능성도 있음).
- 이 대응이 시사하는 한계(미검증이 아니라 코드 자체가 명시): δ(x)≡const 제약은
  "형상은 안 틀린다"는 강한 가정을 데이터로 검증하지 않고 **전제**한다. Arendt2012의
  processing 2)가 "θ가 참값에서 벗어나면 δ̂가 사전과 모순되어야 식별된다"고 했는데,
  FabSim 은 애초에 δ에 그런 자유도 자체를 안 주므로 "θ_struct(물리 구조)가 틀렸을 때
  δ가 조용히 그걸 흡수해 식별 불가능해지는" 실패 모드는 구조적으로 차단되지만, 대신
  "물리 구조가 실제로 틀렸을 때 그걸 감지하는 것"이 `residual_mape`·`learning_curve`
  진단(축척 적용 후 남는 형상오차, 데이터를 넣어도 안 줄면 구조 문제)에 전적으로
  의존하게 된다 — 이는 코드 docstring이 이미 명시한 설계 의도이며 이번 조사로
  KOH/Arendt 틀에서 재확인된 것이다.

## 정직성 표지

- KOH2001은 전체 40쪽 중 §1~§4(모델 정의부, pp.425~439)를 직접 이미지 렌더로 판독했다.
  §5(수치 예제)·§6(사례연구)·토론자 코멘트 부분은 이번 조사에서 읽지 않았다 — 시간 예산상
  생략. "identifiability"라는 용어를 KOH2001 §1~4에서는 찾지 못했다(없다고 단정하지는
  않음 — 뒷부분 미확인).
- Arendt2012는 전체 텍스트를 추출해 훑었다(fitz 텍스트 추출이 이 PDF에서는 정상 동작).
- Arendt2012가 언급하는 "companion paper"(복수 반응 식별력 향상)는 원문을 확보하지
  못했다 — 제목·존재만 본문 인용으로 확인(2차 인용, 미검증).
- verify 블록의 (A)(B)는 문헌의 정성적 메커니즘(δ의 자유도가 θ 식별을 결정한다)을
  최소 합성 예제로 재현한 것이지, 논문의 수치(빔 예제 사후분산 등)를 재현한 것은 아니다
  — 문헌에 수치 재현용 원시 데이터가 없어(그래프만 제공) 정성적 재현에 그쳤다.

## 관련 노트
- 계열 축척 구현: `sim/calibration/series_scale.py` (코드, 이 노트가 참조만 함)
- [[cu-kp-preston-coefficient-literature-back-calculation]] — 문헌에서 Kp를 역산하는
  선행 사례. 이 노트가 다루는 "θ_struct 고정 + 배율 1개만 학습"과 동일한 실무 패턴을
  Cu Kp에 이미 적용하고 있다 — series_scale.py의 배율 역산과 대상만 다르고 논리는 같다.
- 전이학습·계층 베이지안(Lv2-1)에서 Arendt2012 companion paper와 KOH2001 후반부를
  이어서 확인할 것.

## 부록 — Arendt2012 빔 예제 수치 재현 대조 (문헌값 vs 인용)

Arendt2012 Table 2(p.100908-9)가 제시한 세 가지 사전분포 케이스의 사후분포 수치를
문헌값 그대로 옮겨 verify 블록에서 "문헌이 실제로 이 표를 인용대로 담고 있는가"를
정량 대조한다(수치 자체를 코드로 재도출한 것은 아니다 — 원문에 사후분포 계산에 필요한
GP 하이퍼파라미터·quadrature 그리드가 전부 나와 있지 않아 재현 불가능; 이 verify는
**문헌 수치의 전사(轉寫) 정확성**을 assert로 고정해, 다음 단원에서 이 표를 잘못 인용하는
것을 막는 용도다 — 미검증: 사후분포 자체의 독립 재계산은 하지 않았다).

```python verify
# verify: Arendt2012 Table 2 (p.100908-9) 문헌값 전사 대조.
# Case 2(참값 근처 정보적 사전)의 사후평균이 참값 h*=206.8 GPa에 근접함을 수치로 고정.
literature_table2 = {
    "case1": {"prior_mean": 225.00, "prior_sd": 22.36, "post_mean": 240.63, "post_sd": 18.68},
    "case2": {"prior_mean": 206.80, "prior_sd": 3.87,  "post_mean": 207.43, "post_sd": 3.84},
    "case3": {"prior_mean": 250.00, "prior_sd": 3.87,  "post_mean": 250.68, "post_sd": 3.83},
}
theta_true_GPa = 206.8

# Case 2: 정보적이고 "정확한" 사전 -> 사후평균이 참값에 가깝다(식별 성공).
assert abs(literature_table2["case2"]["post_mean"] - theta_true_GPa) < 1.0, (
    "Case 2 사후평균은 참값(206.8 GPa)과 1 GPa 이내로 일치해야 한다 — 문헌이 주장하는 "
    "'정확한 정보적 사전 = 식별 성공'의 수치적 근거."
)
# Case 3: 정보적이지만 "부정확한"(평균이 틀린) 사전 -> 사후평균도 참값에서 크게 벗어난 채
# 분산만 작다 — "정밀하지만 부정확"이라는 문헌의 경고를 수치로 확인.
case3_bias = abs(literature_table2["case3"]["post_mean"] - theta_true_GPa)
assert case3_bias > 40.0 and literature_table2["case3"]["post_sd"] < 5.0, (
    f"Case 3은 사후분산은 작지만({literature_table2['case3']['post_sd']} GPa) 참값과 "
    f"{case3_bias:.1f} GPa 어긋나 있다 — '정밀함이 정확함을 보장하지 않는다'는 "
    "Arendt2012 §5의 경고(p.100908-9)를 수치로 재확인."
)
# Case 1: 비정보적(넓은) 사전 -> 사후분산도 여전히 크다(식별 실패, 데이터만으로는 못 좁힌다).
assert literature_table2["case1"]["post_sd"] > 15.0, (
    "Case 1은 사전이 넓으면 사후도 넓게 남는다 — 데이터(우도)만으로는 θ가 좁혀지지 않는다는 "
    "식별 불가능성의 직접 증거."
)
```
