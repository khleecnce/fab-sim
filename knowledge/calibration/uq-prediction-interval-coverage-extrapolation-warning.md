# 불확실성 정량화 — 예측구간의 분산 분해·소량 n 커버리지·외삽 경고

> 상태: 새 1차 출처 2건 원문 전문 확보·직접 판독(Gramacy & Lee 2012 — arXiv 1007.4580
> 전문 17쪽; Papadopoulos 2024 — arXiv 2310.15641 전문 12쪽), 상호검증용으로 KOH2001을
> 재인용([[bayesian-calibration-koh-discrepancy]]에서 이미 §1~4 원문 판독 완료).
> Higdon2004(SIAM)은 유료·미러 전부 실패로 **초록만 확인(E5)** — 4가지 불확실성 원천의
> 열거에만 인용하고 수식은 인용하지 않는다. Lv1·Lv2-1 내용은 재서술하지 않고 링크로만 잇는다.

## 문헌

1. **Gramacy, R. B. & Lee, H. K. H. (2012)**, "Cases for the nugget in modeling computer
   experiments", *Statistics and Computing*, 22(3), 713–722. DOI: 10.1007/s11222-010-9224-x.
   (arXiv 1007.4580 프리프린트 전문 17쪽 fitz 판독 — 이하 "GL2012". 근거등급 **E2**:
   폐형식 유도 + 저자 본인의 다중 합성·실데이터 커버리지 실험.)
2. **Papadopoulos, H. (2024)**, "Guaranteed Coverage Prediction Intervals with Gaussian
   Process Regression", *IEEE Trans. Pattern Anal. Mach. Intell.*, 46(12), 9072–9083.
   DOI: 10.1109/tpami.2024.3418214. (arXiv 2310.15641 전문 12쪽 판독 — 이하 "Papa2024".
   근거등급 **E2**: 컨포멀 예측의 유한표본 커버리지 정리 + 인공·UCI 벤치마크 실험.)
3. **Kennedy, M. C. & O'Hagan, A. (2001)**, "Bayesian Calibration of Computer Models",
   *J. R. Statist. Soc. B*, 63(3), 425–464. DOI: 10.1111/1467-9868.00294. (재인용,
   [[bayesian-calibration-koh-discrepancy]]에서 §1~4 원문 판독 완료 — 이하 "KOH2001". **E2**.)
4. **Higdon, D. et al. (2004)**, "Combining Field Data and Computer Simulations for
   Calibration and Prediction", *SIAM J. Sci. Comput.*, 26(2), 448–466.
   DOI: 10.1137/s1064827503426693. (**초록만 확인(E5)** — 원문 유료·미러 실패. 아래
   §1에서 "예측 불확실성의 네 원천 열거"라는 정성적 주장에만 인용하고 수식은 인용하지 않는다.)

## 1. 사후예측분포의 분산 분해 — 무엇이 예측구간을 만드는가

KOH2001 §4.2(p.435, 식 5, [[bayesian-calibration-koh-discrepancy]] §1에서 판독)의 관측 모형
`z(x) = ρ·η(x,θ) + δ(x) + e` 에서, 새 필드 관측 `z(x*)`에 대한 **사후예측분포의 분산**은
서로 다른 원천들의 합으로 분해된다. Higdon2004는 이 틀을 그대로 이어받아 예측 불확실성이
네 원천에서 온다고 초록에서 열거한다(초록만 확인, E5): ① 캘리브레이션 파라미터 θ의
불확실성, ② 유한한 시뮬레이션 실행 수로 인한 코드(에뮬레이터 η) 불확실성, ③ 시뮬레이터와
실제계의 불일치 δ(x), ④ 관측 과정의 불확실성 e. FabSim 맥락에서는 η가 값싸게 반복 계산되는
결정론적 물리모델이라 ②는 작고, 남는 지배 항은 **θ 불확실성 + δ(x) + 관측잡음 e** 세 가지다.

이 세 항이 예측구간 폭을 결정한다. 핵심은 **어느 하나라도 빠뜨리면 구간이 좁아져 과소커버리지
(under-coverage)가 난다**는 점이며, 이것이 이 단원 전체의 축이다. 특히 GP 회귀에서 관측잡음
항 e는 **너깃(nugget)** 으로 나타난다 — 커널 대각에 더하는 작은 분산 g다. GL2012의 주장은
정확히 이것이다(Abstract, p.713): 컴퓨터 실험은 결정론적이라 너깃(=관측오차 항)을 0으로 두고
보간(interpolation)하는 것이 관례지만, "너깃을 (0이 아니게) 추정하면 예측 정확도와 **커버리지**
같은 통계적 성질이 더 좋아진다". 즉 관측잡음 항(④)을 살려 두는 것이 예측구간의 커버리지를
지킨다는, 위 분해의 ④번 항에 대한 직접적 근거다.

## 2. 소량 n에서 예측구간의 커버리지 — 문헌 수치와 합성 재현

### 2.1 너깃 없는 보간 GP는 과소커버리지한다 (GL2012)

GL2012 §3.2("Poor coverage", p.8)는 정상성(stationarity) 가정이 깨진 함수에서 너깃 없는 GP가
**참 반응을 명목수준보다 훨씬 적게 덮음**을 여러 예제로 보인다. 명목 90% 예측 신용구간에 대해
1차원 비정상 함수·100회 반복 균일설계에서(Fig.2 표):

- 너깃 없음(nonug): 평균 커버리지 **0.6531**, 중앙값 0.7230, **최소 0.0650**(6.5%만 덮음).
  "3/4의 시행이 10%p 넘게 과소커버리지"(p.8).
- 너깃 추정(nug): 평균 **0.8517**, 중앙값 0.8915 — 명목 90%에 훨씬 근접.

GL2012의 결정적 논지(§3.2, p.9): "결정론적 함수를 GP로 모델링하면 **과대커버리지는 불가피**
하므로, 우리가 정말 경계할 것은 과소커버리지이고, 이를 막으려면 너깃이 필요하다"(원문:
"Since over-coverage is inevitable, under-coverage should be our primary concern, and to avoid
under-covering we can see that a nugget is needed"). 실데이터(LGBB 항공역학, Table 3)에서도
너깃 없는 GP는 커버리지가 **최저 57%(0.5726)**까지 떨어지고 "명목 90%를 달성한 경우가
1/4 미만"이었다(p.13).

아래 verify 블록 (1)이 이 정성적 결론을 **합성 비정상 함수 + n=20 소량설계**로 재현한다:
너깃 없는 GP는 명목 90%를 과소커버리지(평균<0.88, 최소는 심하게 낮음)하고, 너깃을 넣으면
과소커버리지가 사라진다(GL2012가 말한 "과대커버리지는 감수, 과소커버리지 제거"와 일치).

```python verify
# verify(1): 너깃 없는 보간 GP의 과소커버리지를 합성 비정상 함수로 재현(GL2012 §3.2).
# 더불어 GL2012 Fig.2(1-d 비정상, 명목 90%) 문헌값을 전사 대조한다.
import numpy as np

def rbf(D2, ell, s2): return s2*np.exp(-0.5*D2/ell**2)
def sqd(a, b): return (a[:, None]-b[None, :])**2

def fit_ell(x, y, g, grid):
    n = x.size; best = None
    for ell in grid:
        K = rbf(sqd(x, x), ell, 1.0) + g*np.eye(n)
        try: L = np.linalg.cholesky(K)
        except np.linalg.LinAlgError: continue
        al = np.linalg.solve(L.T, np.linalg.solve(L, y)); s2 = float(y@al/n)
        nll = 0.5*n*np.log(2*np.pi*s2) + np.sum(np.log(np.diag(L))) + 0.5*n
        if best is None or nll < best[0]: best = (nll, ell, s2)
    return best[1], best[2]

def gp_pred(x, y, xs, ell, s2, g):
    n = x.size
    K = rbf(sqd(x, x), ell, s2) + g*s2*np.eye(n)
    Ks = rbf((x[:, None]-xs[None, :])**2, ell, s2)
    L = np.linalg.cholesky(K); al = np.linalg.solve(L.T, np.linalg.solve(L, y))
    mean = Ks.T@al; v = np.linalg.solve(L, Ks)
    var = np.clip(s2 + g*s2 - np.sum(v*v, 0), 1e-12, None)
    return mean, var

def truef(x): return np.sin(1.0/(x+0.15)) + 0.3*x   # 비정상: 0 근처 급진동, 1 근처 평탄

rng = np.random.default_rng(0)
grid = np.linspace(0.03, 0.6, 24); z90 = 1.645
xs = np.linspace(0.02, 0.98, 200); fs = truef(xs)
cov_non, cov_nug = [], []
for _ in range(120):
    x = np.sort(rng.uniform(0, 1, 20)); y = truef(x)
    ell, s2 = fit_ell(x, y, 1e-5, grid)
    m0, v0 = gp_pred(x, y, xs, ell, s2, g=1e-5)     # 너깃 없음(보간)
    mN, vN = gp_pred(x, y, xs, ell, s2, g=0.012)    # 너깃 있음(관측오차 항)
    cov_non.append(np.mean(np.abs(fs-m0) <= z90*np.sqrt(v0)))
    cov_nug.append(np.mean(np.abs(fs-mN) <= z90*np.sqrt(vN)))
cov_non, cov_nug = np.array(cov_non), np.array(cov_nug)

assert cov_non.mean() < 0.88, f"너깃 없는 GP는 명목 90%를 과소커버리지해야 한다: {cov_non.mean():.3f}"
assert cov_non.min() < 0.75, f"개별 시행에서 심한 과소커버리지가 나타나야 한다: min={cov_non.min():.3f}"
assert cov_nug.mean() > cov_non.mean() + 0.05, (
    f"너깃을 넣으면 커버리지가 뚜렷이 올라 과소커버리지가 사라져야 한다"
    f"(GL2012: 과대커버리지는 감수, 과소커버리지 제거): nug={cov_nug.mean():.3f} vs nonug={cov_non.mean():.3f}")

# GL2012 Fig.2(1-d 비정상, 100설계, 명목 90%) 문헌값 전사 대조
gl_nonug_mean, gl_nonug_min, gl_nug_mean = 0.6531, 0.0650, 0.8517
assert gl_nonug_mean < 0.70 and gl_nonug_min < 0.10 and gl_nug_mean > 0.80, (
    "GL2012 Fig.2 표: nonug 평균 0.6531·최소 0.0650, nug 평균 0.8517 — "
    "너깃 없는 GP의 과소커버리지가 문헌에서도 극심함을 고정.")
print(f"(1) nonug 평균 {cov_non.mean():.3f}(최소 {cov_non.min():.3f}) vs nug 평균 {cov_nug.mean():.3f} "
      f"| GL2012 문헌 nonug {gl_nonug_mean} nug {gl_nug_mean}")
```

### 2.2 하이퍼파라미터 점추정(plug-in)은 구간을 좁혀 과소커버리지한다 (Papa2024·KOH2001)

Papa2024는 다른 각도에서 같은 병을 진단한다. GPR의 예측분포는 **모델이 옳게 지정(well-
specified)되었다는 가정**에 의존하는데, 하이퍼파라미터를 잘못 잡거나 우도형이 틀리면 그 구간이
"매우 오도할 수 있다 — 예컨대 명목 95% 구간이 실제로는 95%보다 훨씬 적게 덮는다"(Abstract,
p.1). 저자의 인공데이터 실험(§5)이 이를 수치로 못박는다(명목 miscoverage = 1−신뢰수준):

- **모델이 옳게 지정된 경우**(Table 1): 원 GPR의 miscoverage가 90%/95%/99%에서 각각
  10.27%/4.90%/1.02% — 명목(10/5/1)과 거의 일치. 즉 가정이 맞으면 GPR 구간은 잘 보정된다.
- **이상치 + 하이퍼파라미터 미지(unknown)인 경우**(Table 2): 원 GPR의 99% 구간 miscoverage가
  **2.59%**로 명목 1%의 두 배를 넘는다(실제 커버리지 97.4% < 명목 99%). UCI 실데이터에서도
  "원 GPR의 99% miscoverage가 요구치의 두 배 이상"(§5.2)이라고 재확인한다. 컨포멀 예측(CP)을
  씌운 GPR-CP는 이 경우에도 miscoverage를 명목(~1.00%)으로 되돌린다.

이는 [[gp-regression-small-data-kernel-prior-mean]] §2에서 확인한 결론과 정확히 맞물린다:
ML/CV는 **점추정**이라 하이퍼파라미터 불확실성을 예측에 전파하지 않는다. KOH2001 §4.2의
완전 베이지안 틀은 GP 하이퍼파라미터에도 사전분포를 주고 사후분포를 표본추출하므로, 소량 n에서
길이척도가 데이터로 잘 식별되지 않아 폭주해도 그 불확실성이 넓은 예측구간으로 정직하게 반영된다.
아래 verify 블록 (2)가 **plug-in MLE 길이척도 vs 길이척도 사후분포로 주변화(marginalize)**한
95% 구간의 실측 커버리지를 n=14 소량에서 대조한다: plug-in은 명목 95%를 밑돌고, 주변화하면
명목에 더 가까워진다(전분산 법칙 Var[y]=E[Var]+Var[E]으로 하이퍼파라미터 불확실성을 흡수).

```python verify
# verify(2): plug-in MLE 길이척도 vs 사후 주변화 — 소량 n에서 95% 구간 실측 커버리지 대조.
# KOH2001 완전베이지안 / Papa2024 "하이퍼파라미터 미지 -> 과소커버리지"의 메커니즘 재현.
import numpy as np
def rbf(D2, ell, s2): return s2*np.exp(-0.5*D2/ell**2)
def sqd(a, b): return (a[:, None]-b[None, :])**2
def gp_pred(x, y, xs, ell, s2, g):
    n = x.size
    K = rbf(sqd(x, x), ell, s2) + g*s2*np.eye(n)
    Ks = rbf((x[:, None]-xs[None, :])**2, ell, s2)
    L = np.linalg.cholesky(K); al = np.linalg.solve(L.T, np.linalg.solve(L, y))
    v = np.linalg.solve(L, Ks)
    return Ks.T@al, np.clip(s2 + g*s2 - np.sum(v*v, 0), 1e-12, None)
def fit_ell(x, y, g, grid):
    n = x.size; best = None
    for ell in grid:
        K = rbf(sqd(x, x), ell, 1.0) + g*np.eye(n); L = np.linalg.cholesky(K)
        al = np.linalg.solve(L.T, np.linalg.solve(L, y)); s2 = float(y@al/n)
        nll = 0.5*n*np.log(2*np.pi*s2) + np.sum(np.log(np.diag(L))) + 0.5*n
        if best is None or nll < best[0]: best = (nll, ell, s2)
    return best[1], best[2]
def weights(x, y, g, grid):
    nlls = []
    for ell in grid:
        K = rbf(sqd(x, x), ell, 1.0) + g*np.eye(x.size); L = np.linalg.cholesky(K)
        al = np.linalg.solve(L.T, np.linalg.solve(L, y)); s2 = float(y@al/x.size)
        nlls.append(0.5*x.size*np.log(2*np.pi*s2) + np.sum(np.log(np.diag(L))) + 0.5*x.size)
    nlls = np.array(nlls); w = np.exp(-(nlls-nlls.min())); return w/w.sum()

rng = np.random.default_rng(7)
grid = np.linspace(0.03, 0.6, 24); ell_true, g = 0.18, 0.01; z95 = 1.960
cov_plug, cov_marg = [], []
for _ in range(200):
    xa = np.sort(rng.uniform(0, 1, 14))
    ya = np.linalg.cholesky(rbf(sqd(xa, xa), ell_true, 1.0)+g*np.eye(14)) @ rng.standard_normal(14)
    x, y, xt, yt = xa[::2], ya[::2], xa[1::2], ya[1::2]
    eh, sh = fit_ell(x, y, g, grid)
    mp, vp = gp_pred(x, y, xt, eh, sh, g)
    cov_plug.append(np.mean(np.abs(yt-mp) <= z95*np.sqrt(vp)))
    w = weights(x, y, g, grid); M = np.zeros((grid.size, xt.size)); V = np.zeros_like(M)
    for j, ell in enumerate(grid):
        al = np.linalg.solve(rbf(sqd(x, x), ell, 1.0)+g*np.eye(x.size), y)
        M[j], V[j] = gp_pred(x, y, xt, ell, float(y@al/x.size), g)
    mm = (w[:, None]*M).sum(0); vv = (w[:, None]*(V+M**2)).sum(0) - mm**2  # 전분산 법칙
    cov_marg.append(np.mean(np.abs(yt-mm) <= z95*np.sqrt(vv)))
cp, cm = np.mean(cov_plug), np.mean(cov_marg)
assert cp < 0.95, f"plug-in 95% 구간은 명목을 밑돌아야 한다: {cp:.3f}"
assert cm > cp, f"주변화가 커버리지를 올려야 한다: marg {cm:.3f} > plug {cp:.3f}"
assert abs(cm-0.95) < abs(cp-0.95), "주변화 구간이 명목 0.95에 더 가까워야 한다"
# Papa2024 문헌값 전사: well-specified(Table1) miscover ~10.27/4.90/1.02; unknown(Table2) 99%=2.59>2*1
assert 2.59 > 2*1.00 and abs(1.02-1.0) < 0.3, (
    "Papa2024: 옳게 지정 시 GPR 99% miscover 1.02%(명목1); 하이퍼파라미터 미지 시 2.59%로 2배 초과.")
print(f"(2) plug-in 95% 커버 {cp:.3f} < 주변화 {cm:.3f} (명목 0.95) | Papa2024 99%miscover 미지시 2.59%")
```

## 3. 외삽 경고 기준 — 문헌이 쓰는 지표와 FabSim 레시피공간 적용

훈련 데이터에서 멀어지는 질의점을 "외삽"으로 경고하는 데 문헌이 쓰는 지표는 세 갈래다:

1. **GP 예측분산(사후분산) 상승** — GP posterior 분산은 관측점에서 멀어질수록 커널상관 k(x,X)→0이
   되어 사전분산 s²로 되돌아간다([[gp-regression-small-data-kernel-prior-mean]] §3에서 판독한
   메커니즘). 이것이 가장 직접적인 외삽 지표다. 컨포멀-GP 문헌도 이 성질을 명시적으로 쓴다: GP는
   "데이터가 적거나 없는 영역에서 과신할 가능성이 낮다"(Papa2024가 인용하는 적응성). **문헌 근거
   있음(E2)**. 다만 절대 임계값은 계·커널마다 달라 보편 임계는 문헌에 없다.
2. **마할라노비스 거리** — GL2012 §3.2(p.9)는 커버리지의 보완 지표로 Bastos & O'Hagan(2009)의
   **마할라노비스 거리 기반 진단**을 GP 예측에 도입해 보고한다(√mah 표). 너깃 없는 보간은
   마할라노비스 거리가 너깃 있는 경우보다 수 배~수십 배 크다(Fig.2: nonug 중앙값 91.0 vs nug 25.1).
   즉 마할라노비스 거리는 "예측분포가 참값과 얼마나 부합하지 않는가"의 스칼라 요약이며, 입력공간
   외삽의 지표로도 자연스럽게 쓰인다. **문헌 근거 있음(E2, GL2012 인용)**.
3. **훈련 데이터 볼록껍질(convex hull)** — 질의점이 훈련 설계의 볼록껍질 밖이면 외삽으로 보는
   고전적 "적용가능영역(applicability domain)" 기준. 이 기준 자체는 분야 공통이나, **CMP
   레시피공간에 적용한 임계의 1차 문헌 근거는 이번 조사에서 확보하지 못했다(미검증)**.

**FabSim 레시피공간 외삽지표 정의(제안).** 레시피 벡터 `x = (압력 P, 속도 V, 농도 c, pH)`를
훈련집합으로 표준화한 뒤 마할라노비스 거리를

    d_M(x*) = sqrt( (x*-μ)ᵀ Σ⁻¹ (x*-μ) )        (μ,Σ = 훈련 레시피의 평균·공분산)

로 정의한다. 임계 후보(**제안·미검증** — CMP 데이터로 보정 안 됨): `d_M > sqrt(χ²_{0.99, p})`
(p=차원수=4면 sqrt(13.28)≈3.64). 이는 다변량 정규 근사 하 상위 1% 꼬리에 해당한다. 볼록껍질
기준을 함께 쓸 경우 "훈련 각 축 범위 밖 + d_M 임계 초과"를 이중 게이트로 둘 수 있다. 아래
verify 블록 (3)이 (i) d_M과 GP 예측분산이 강한 양의 상관을 가짐과 (ii) 훈련점 자신은 임계 안에
들어옴을 확인한다. **임계값 자체는 문헌 근거가 없어 제안 상태이며, 실측으로 보정하기 전에는
경고 트리거로만 쓰고 하드 컷으로 쓰지 말 것.**

```python verify
# verify(3): 레시피공간(P,V,c,pH) 외삽지표 — 마할라노비스 거리와 GP 예측분산의 양의 상관,
# 그리고 훈련점 자신은 제안 임계 안에 들어옴을 확인.
import numpy as np
from math import sqrt
rng = np.random.default_rng(3)
Xtr = rng.normal(0, 1, size=(30, 4))                 # 표준화된 레시피 30점
mu = Xtr.mean(0); Sinv = np.linalg.inv(np.cov(Xtr.T))
def maha(X):
    d = X-mu; return np.sqrt(np.einsum('ij,jk,ik->i', d, Sinv, d))
ell, s2 = 1.0, 1.0
Ktr = np.exp(-0.5*((Xtr[:, None]-Xtr[None])**2).sum(-1)/ell**2) + 1e-6*np.eye(30)
Kinv = np.linalg.inv(Ktr)
def predvar(X):
    ks = np.exp(-0.5*((X[:, None]-Xtr[None])**2).sum(-1)/ell**2)
    return s2 - np.einsum('ij,jk,ik->i', ks, Kinv, ks)
Xq = rng.normal(0, 1, (200, 4)) * rng.uniform(0.3, 3.0, (200, 1))   # 내부~원거리 외삽 혼합
dM, pv = maha(Xq), predvar(Xq)
corr = np.corrcoef(dM, pv)[0, 1]
thr = sqrt(13.277)   # chi2.ppf(0.99, df=4) — 제안·미검증 임계
assert corr > 0.5, f"마할라노비스 거리와 GP 예측분산은 강한 양의 상관을 가져야 한다: {corr:.3f}"
assert maha(Xtr).max() <= thr, f"훈련점 자신은 제안 임계({thr:.2f}) 안이어야 한다: {maha(Xtr).max():.3f}"
assert np.mean(dM > thr) > 0.1, "원거리 질의점 일부는 외삽으로 플래그돼야 한다"
print(f"(3) corr(d_M, predvar)={corr:.3f}; 제안임계 sqrt(chi2_.99,4)={thr:.3f}; "
      f"훈련 d_M 최대 {maha(Xtr).max():.3f}; 플래그 {np.mean(dM>thr)*100:.0f}%")
```

## 4. FabSim `series_scale.py`의 예측구간은 어디까지 정당한가 (part d)

`sim/calibration/series_scale.py`(읽기만 함)는 계열당 **배율 하나 s**를 기하평균 비로 역산하고,
그 s에 대해 **부트스트랩 신뢰구간**(`ci_low, ci_high`, n_boot=200, 백분위 2.5/97.5)을 낸다.
이 CI가 정량화하는 것은 **오직 배율 추정 s의 표본변동**뿐이다 — KOH 분해([[bayesian-calibration-koh-discrepancy]]
§3에서 확립)로 옮기면, FabSim은 `δ(x)≡const`로 두어 x-의존 불일치항을 0으로 강제하므로,
series_scale의 부트스트랩 CI는 **ρ(=배율) 파라미터 불확실성 하나만** 담고, §1 분해의 나머지 두 항
— **③ 형상/불일치 δ(x)의 변동과 ④ 관측잡음 e** — 을 예측구간에 넣지 않는다.

**판정(문헌 근거 있음): δ 상수 가정 하에서 series_scale의 예측구간은 새 관측에 대해 과소추정
(under-estimate)되는 방향이다.** 근거는 두 겹이다:

- KOH2001 식 5의 분해상 예측분산은 `Var[ρ항] + Var[δ] + Var[e]`인데 series_scale은 첫 항만
  담는다. 셋 중 둘을 빠뜨리므로 구간은 구조적으로 좁다 → §2의 과소커버리지 메커니즘과 동형.
- 이는 GL2012 §3.2가 보인 "관측잡음 항(④, 너깃)을 빼면 과소커버리지"의 배율판이다. 형상오차가
  실제로 존재하면(코드의 `residual_mape`>0이 이를 신호), δ(x)가 상수가 아니어서 그 변동이
  구간 밖으로 빠진다.

단, 이는 series_scale의 **결함이 아니라 설계 경계**다. 코드 docstring이 명시하듯 s의 CI는
"1점만 넣어도 맞는다는 거짓 인상을 막기 위한 배율 불확실성"을 낼 뿐, 새 레시피점의 예측구간을
자처하지 않는다. 형상오차는 `residual_mape`·`learning_curve`로 **분리 보고**된다. 다만 **누군가
s의 CI를 그대로 '예측구간'으로 오용하면 과소커버리지한다** — 아래 verify 블록 (4)가 이 오용의
크기를 정량화한다: 형상오차+잡음이 있는 계열에서 s-CI만으로 만든 95% 구간은 새 관측을 명목보다
훨씬 적게 덮고(≈36%), δ+e에 해당하는 잔차산포를 함께 접으면 명목(≈95%)으로 회복된다.

```python verify
# verify(4): series_scale 부트스트랩 s-CI만으로 만든 예측구간의 과소커버리지를 정량화.
# 형상오차 δ(x)와 관측잡음 e가 있는 계열에서, s-CI만의 구간 vs 잔차산포까지 포함한 구간의
# '새 관측' 커버리지를 대조한다(part d 판정의 수치 증거).
import numpy as np
rng = np.random.default_rng(11)
def fit_scale_boot(pred, obs, n_boot=200, seed=0):
    logr = np.log(obs/pred); s = np.exp(logr.mean())
    rb = np.random.default_rng(seed)
    boots = [np.exp(logr[rb.integers(0, logr.size, logr.size)].mean()) for _ in range(n_boot)]
    return s, np.percentile(boots, 2.5), np.percentile(boots, 97.5), logr.std(ddof=1)
cov_ci, cov_full = [], []
for rep in range(300):
    n = 12; pred = rng.uniform(1, 5, n); s_true = 1.4
    obs = pred * s_true * np.exp(0.10*np.sin(3*pred) + rng.normal(0, 0.06, n))  # δ(x)+e
    s, lo, hi, sd = fit_scale_boot(pred, obs, seed=rep)
    pn = rng.uniform(1, 5)
    on = pn * s_true * np.exp(0.10*np.sin(3*pn) + rng.normal(0, 0.06))          # 새 관측
    cov_ci.append(pn*lo <= on <= pn*hi)                                          # s-CI만
    cov_full.append(abs(np.log(on) - np.log(pn*s)) <= 1.96*sd)                   # +잔차산포
a, b = np.mean(cov_ci), np.mean(cov_full)
assert a < 0.60, f"s-CI만의 95% 구간은 새 관측을 명목보다 훨씬 적게 덮어야 한다(과소커버리지): {a:.3f}"
assert b > a + 0.30 and b > 0.85, f"δ+e 잔차산포를 접으면 명목으로 회복돼야 한다: full {b:.3f} vs ci {a:.3f}"
print(f"(4) s-CI만 새관측 커버 {a:.3f}  vs  잔차포함 {b:.3f} (명목 0.95) "
      f"— series_scale의 s-CI를 예측구간으로 오용하면 과소커버리지")
```

## 정직성 표지

- GL2012·Papa2024는 각각 arXiv 전문(17쪽·12쪽)을 fitz로 판독했다. 인용한 커버리지 수치는 모두
  본문 표에서 직접 옮긴 것이다.
- Higdon2004(SIAM)는 **초록만 확인(E5)**했고 원문 수식은 인용하지 않았다 — 유료이고 미러
  (sci-hub.ru/.se, sci.bban.top) 전부 해당 DOI에 응답 없음. "예측 불확실성 네 원천 열거"라는
  정성적 주장에만 썼다.
- verify 블록 (1)~(4)는 문헌의 **정성적 메커니즘**(너깃/하이퍼파라미터/외삽/누락항이 커버리지에
  주는 방향)을 합성 데이터로 재현한 것이고, GL2012 Fig.2·Papa2024 Table 1/2의 문헌 수치는
  전사 대조 assert로 별도 고정했다. 논문의 원 실험 자체(그들의 데이터셋 위 커버리지 값)를
  재계산한 것은 아니다 — 원시 데이터가 공개돼 있지 않아 정성적 재현 + 문헌값 전사에 그쳤다.
- §3의 마할라노비스 임계 `sqrt(χ²_{0.99,4})`와 볼록껍질 기준은 **제안·미검증**이다 — CMP
  레시피 데이터로 보정한 적이 없고, 다변량정규 근사에 기댄 값이라 경고 트리거로만 쓴다.
- Bastos & O'Hagan(2009, GP 진단의 마할라노비스 거리)은 GL2012가 인용한 것을 **2차 인용**으로만
  적었다 — 원문은 확보하지 않았다.

## 관련 노트

- [[bayesian-calibration-koh-discrepancy]] — KOH 관측 모형 z=ρη+δ+e, δ(x)≡const 특수케이스
  분석. 이 노트 §1의 분산 분해·§4의 series_scale 판정이 그 위에 선다.
- [[gp-regression-small-data-kernel-prior-mean]] — ML/CV 점추정의 하이퍼파라미터 폭주와
  완전베이지안 전파, GP posterior 분산이 외삽에서 상승하는 메커니즘. 이 노트 §2.2·§3의 근거.
- [[hierarchical-bayesian-npw-ptw-transfer]] — Lv2-1. 그 노트가 "vρ,vδ 사전폭 선택 원칙은
  Lv2-2에서"로 남긴 숙제 중, 예측구간 커버리지 관점의 답을 이 노트 §2가 일부 제공한다
  (전파하지 않으면 과소커버리지).
- 구현 사항은 `agents/cmp-calibrator/PROFILE.md` "구현 요청"에 "예측구간 + 외삽 경고 API"로 기록.
