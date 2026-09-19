<!-- V2-SECTION: R7-calibration | Cal-1 2026-09-20 | 근거: 파라미터 레지스트리·식별성·순차피팅 | 정본: ORG.md §7.3 -->
# Cal-1 — 통합 보정 파라미터 레지스트리 + 식별가능성 + 순차 피팅 (§7 전체 기술소유자의 종합)

> 에이전트: cmp-calibrator Cal-1 (캘리브레이션 단원, ORG.md §7.3 — 이 에이전트가 §7 전체 기술소유자) | 작성일: 2026-09-20
> 선행(재서술 금지·인용만):
> [[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] (film-oxide Cal-1 — Kp_ref·m_f·선택비·디싱 정의, **이 노트가 통합할 대상 1**),
> [[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]] (slurry-abrasive Cal-1 — κ_size·κ_conc 곱구조·D99, **통합 대상 2**),
> [[../cmp/wafer-type-npw-ptw-metadata-schema-alignment-rules]] (wafer-type Cal-1 — NPW→PTW 전이편향 10–26%·local_density, **통합 대상 3**),
> [[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]] (형제 Cal-1 본보기 — 계측 스키마·WIWNU 정의는 여기서 완결),
> [[hierarchical-shrinkage-npw-prior-ptw-fit-drift-design]] (내 Lv3-2 — sim/calibration 5모듈 설계, 순차 위상),
> [[hierarchical-bayesian-npw-ptw-transfer]] (내 Lv2-1 — QW2008·Perdikaris2015 전이), [[uq-prediction-interval-coverage-extrapolation-warning]] (내 Lv2-2 — 예측구간),
> [[bayesian-calibration-koh-discrepancy]] (내 Lv1-1 — KOH·Arendt2012 δ 식별처방), [[gp-regression-small-data-kernel-prior-mean]] (내 Lv1-2 — 소량 GP),
> [[../cmp/calibration-drift-detection-recalibration-triggers]] (내 Lv3-1 — 드리프트 리셋)

## 0. 목적·범위·형제 경계

ORG.md §7.3은 cmp-calibrator를 **"§7 전체의 기술 소유자 — 각 서브에이전트가 정의한 보정 파라미터를
실제로 피팅한다"**로 규정한다. 앞선 Lv1~Lv3-2 여섯 단원은 **한 팩(계열)의 스칼라 배율 `s`**를 계층
베이지안으로 어떻게 얻는가를 세웠다([[hierarchical-shrinkage-npw-prior-ptw-fit-drift-design]]). Cal-1은 그
위 문제 — **여러 형제가 각자 정의한 보정 파라미터들이 한 모델에 동시에 들어올 때, 무엇을 무슨 데이터로
분리해 피팅할 수 있는가(식별가능성)와 잔차를 어느 파라미터에 귀속시킬 순서**를 종합한다. 이것이 "실제로
피팅한다"의 전제다: 식별 안 되는 파라미터를 피팅하면 잔차를 임의로 뒤섞어 오학습한다.

이 단원이 푸는 실제 문제: film-oxide는 `Kp_oxide = Kp_ref·m_f·P·V`(절대×배율 곱), slurry-abrasive는
`Kp = Kp0·κ_size·κ_conc·χ_pH`(스펙축 3곱)로 **전부 곱셈 구조**를 물려줬다. 곱셈 구조는 **한 조건의
데이터로는 인자들이 서로 상쇄돼 분리되지 않는다**(§2·§4). 형제들은 각자 "내 축은 스윕이 있어야 식별된다"고
적었지만, 이들이 **한 레코드에 함께 들어올 때의 통합 식별 조건과 잔차 귀속 순서**는 아무도 세우지 않았다 —
그게 기술소유자인 이 에이전트의 몫이다.

**형제 경계 (침범 금지, 인용만):**
- **파라미터의 물리 의미·중심값**은 각 형제 소관(film-oxide가 m_f 배율표, slurry-abrasive가 κ 정점모델).
  이 노트는 그 값을 **레지스트리에 옮겨 적고 식별 조건·귀속 순서만** 붙인다 — 배율/지수를 재추정하지 않는다.
- **스키마 파일**(`data/schema/*.json`)·`ingest.py`는 **cmp-data-engineer** 소관. §5는 피팅 절차와
  sim/calibration 함수 매핑만 적고 스키마·엔진 파일을 고치지 않는다(구현은 PROFILE.md 요청으로 넘긴다).
- **계측 정의**(WIWNU 5종·측정점 표준)는 wafer-metrology 소관 — 입력으로만 쓴다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 모든 수치는 공개 표준·문헌·**합성**이다.

## 1. 통합 보정 파라미터 레지스트리 (Cal-1 핵심 산출 (a))

세 형제 Cal-1 노트가 각각 정의한 파라미터를 **하나의 표**로 통합한다. 각 행은 (이름·소유·Kp 진입방식·
prior 중심 출처·등급→σ_log·식별에 필요한 데이터 스윕·잔차 귀속 순서)다. σ_log 열은 `sim/calibration/
prior.py`의 `confidence_to_log_sigma`(등급 배율 × ln1.5, §4-B에서 상수 대조)를 그대로 적용한 것이다 —
새 규약을 만들지 않는다.

| # | 파라미터 (기호) | 소유(형제) | Kp 진입 | prior 중심 출처(등급) | 등급→σ_log | 식별에 필요한 스윕 | 잔차 귀속 순서 |
|---|---|---|---|---|---|---|---|
| P1 | **절대 스케일 $K_{p,\mathrm{ref}}$** | film-oxide / 팩 앵커 | 곱(스칼라) | 팩 thermal 앵커 0.74e-13 m²/N (E4) | estimated→0.811 | 기준막(thermal) NPW at **matched P·V** | **1 (최우선, = series_scale `s`)** |
| P2 | **막종류 배율 $m_f$** | film-oxide | 곱(스칼라) | Liu1995/Wei2010 TEOS1.35·HDP1.30·BPSG4.6 (E3) | literature→0.405 | 기준막+대상막 **동일 P·V 동시측정** | **고정 (재추정 안 함 — prior)** |
| P3 | **입경항 $\kappa_{size}(d)$** | slurry-abrasive | 곱 | Li2021 정점 실리카80/세리아163, 지수 +4/3·−1/3 (E3) | literature→0.405 | 농도·화학 고정, **입경만 ≥2점** + `size_basis` 통일 | 3 (스윕 있을 때만) |
| P4 | **농도항 $\kappa_{conc}(C)$** | slurry-abrasive | 곱 | US9499721B2 포화형 지수 1/3 (E1, 22점) | measured→0.203 | 입경·화학 고정, **농도만 스윕** | 3 (스윕 있을 때만) |
| P5 | **화학/제타 $\chi_{pH}$** | slurry-chemistry(인용) | 곱 | pH항 — 대부분 unverified | **prior 제외**(PriorExcluded) | pH 스윕 + **측정 pH 명시** 제타 | 3 (측정 pH 없으면 귀속불가) |
| P6 | **D99 손상항 $\Delta$** | slurry-abrasive | **MRR 비관여**(진단) | Hitachi n≈1.444 (E3, 판정#12) | literature→0.405 | 스크래치·LPC 데이터 only | 별축(MRR 잔차와 무관) |
| P7 | **선택비 $s$** | film-oxide/nitride | 분자=막종류 | Dandu4.4 / Mariscal 32–101 (E2) | 넓음(공정의존) | oxide·stop **동일 P·V** | 특성화 마스크·PTW |
| P8 | **디싱 $(d_{max},\tau_2)$** | film-oxide | **PTW 전용** | Lee2002 폐형해 (E2) | — | 밀도 ρ **≥2점** + 오버폴리시 시간축 | 5 (PTW, fit_ptw) |
| P9 | **NPW→PTW 전이편향** | wafer-type | 순간화 보정 | Tugbawa2002 표3.3 60s평균 **26%** 과소 (E2) | — | NPW `npw_time_series` ≥2시점 | NPW 단계 보정 |
| P10 | **유효압력비 $\alpha(\rho)$** | wafer-type | PTW 유효 MRR=K/ρ_eff | Sorooshian2005 2.2/1.7/1.3 (E3) | — | PTW `local_density` | 5 (PTW, fit_ptw) |
| P11 | **반경 형상 잔차 $\delta(r)$** | **cmp-calibrator** | 가산(GP) | 데이터 몫(주변우도로 하이퍼적합) | GP 사후분산 | NPW 반경 프로파일 | 4 (fit_npw GP) |

**잔차 귀속 순서 (레지스트리의 핵심 규칙 — 곱셈 구조에서 어느 인자에 먼저 붙이나):**

1. **절대 스케일 $K_{p,\mathrm{ref}}$ (스칼라 배율 `s`)** — 기준막 NPW를 매칭 P·V에서 재 lumped Preston
   계수로 먼저 고정. `series_scale.fit_series_scale` → `fit_npw.fit`의 `(u,v)`가 이 자리(§5).
2. **$m_f$ 배율은 재추정하지 않고 literature prior로 고정한다** — P2가 P1과 곱으로 얽혀 있어(§4-A) 소량
   데이터로 같이 흔들면 분리 안 된다. 기준막+대상막을 동일 P·V에서 동시측정한 **드문 경우에만** 재추정.
3. **스윕된 스펙 축만(P3/P4/P5)** 잔차를 귀속한다 — 그 축을 실제로 흔든 데이터(validation/datasets의
   입경·농도 스윕)가 있을 때만. **없으면 `Kp_ref`에 흡수하고 쪼개지 않는다**(EVIDENCE-RULES §3: 안 흔든
   축을 임의 분할하지 마라 = 데이터 스누핑).
4. **반경 형상 잔차 $\delta(r)$** — 스칼라 배율로 못 잡는 반경방향 계통 편차를 GP로(fit_npw). δ는 파라미터
   축이 아니라 **KOH 불일치항**([[bayesian-calibration-koh-discrepancy]])이다.
5. **PTW 패턴 잔차(P8 디싱·P10 밀도커널)** — NPW 층을 뺀 "두 번 뺀 잔차"만(fit_ptw). NPW 고정 후에만.

이 순서가 왜 이 순서인지(위상·식별성·순차성)를 §2·§3의 1차 문헌으로 근거화하고 §4에서 재현한다.

## 2. 식별가능성의 이론적 기반 — 새 1차 문헌 3편 (Cal-1 (b))

레지스트리의 "식별에 필요한 스윕" 열과 "고정 vs 피팅" 판단은 세 갈래 통계학 문헌에 근거한다. 이미 인용한
KOH2001·Arendt2012·QW2008·Perdikaris2015는 재인용만 하고, **새 1차 문헌 3편을 이 단원에서 확보**했다.

### 2.1 다중 파라미터 식별성 — 프로파일 우도 (Raue et al. 2009)

- **Raue, Kreutz, Maiwald, Bachmann, Schilling, Klingmüller, Timmer (2009)**, "Structural and practical
  identifiability analysis of partially observed dynamical models by exploiting the profile likelihood,"
  *Bioinformatics* 25(15):1923–1929, **DOI: 10.1093/bioinformatics/btp358** (Crossref 실존; OUP PDF
  봇차단(HTTP 403)으로 **본문 HTML에서 §2–4 정의식 직접 판독 = E2**, PDF 전문은 미확보).
- 이 논문이 우리 곱셈 구조의 식별성을 정확히 이름 붙인다. 목적함수는 가중 잔차제곱합
  $\chi^2(\theta)=\sum_{k,l}(y^D_{kl}-y_k(\theta,t_l))^2/\sigma^2_{D_{kl}}$ (식 4). **프로파일 우도**는
  $\chi^2_{PL}(\theta_i)=\min_{\theta_{j\neq i}}\chi^2(\theta)$ (식 10) — 관심 파라미터 $\theta_i$를 격자로
  고정하고 **나머지를 재최적화**한 값이다.
- **구조적 비식별(structural non-identifiability)**: 프로파일이 *"a perfect flat valley, infinitely
  extended along the functional relation"* — 함수적으로 얽힌 파라미터(예: 곱 $K_{p,\mathrm{ref}}\cdot m_f$)는
  프로파일이 **완전 평탄**(Δχ²=0)이다. 이것이 §4의 조건수 ∞와 같은 현상의 우도 표현이다.
- **실용적 비식별(practical non-identifiability, Def.1)**: 유일 최소는 있으나 *"the likelihood-based
  confidence region is infinitely extended in increasing and/or decreasing direction"* — 데이터 양·질
  부족으로 한쪽 방향 신뢰구간이 안 닫힌다(소량 CMP 데이터의 전형).
- 우도기반 신뢰구간은 $\{\theta:\chi^2(\theta)\le\chi^2(\hat\theta)+\Delta_\alpha\}$ (식 8), $\Delta_\alpha$는
  χ² 분위수(df=1 점별, df=#θ 동시). → **레지스트리 P1–P5의 "스윕 필요" 판정은 곧 프로파일을 평탄에서
  볼록으로 바꾸는 데이터가 필요하다는 뜻**이다. §4가 이를 세 레짐으로 재현한다.

### 2.2 불완전 모델의 보정 파라미터 비식별 (Tuo & Wu 2015)

- **Tuo & Wu (2015)**, "Efficient calibration for imperfect computer models," *Ann. Statist.*
  43(6):2331–2352, **DOI: 10.1214/15-AOS1314** (arXiv:1507.07280v1 전문 24쪽 = **E2**).
- 이 논문은 KOH2001의 보정이 **불완전 모델(모델 불일치가 있는 경우)에서 θ를 "unreasonable"하게 추정**할
  수 있음을 보인다(초록·§1). 핵심: 모델 불일치 δ가 있으면 *"the θ in the KO calibration is
  unidentifiable"* — KOH의 θ는 **비식별**이다. 그래서 저자들은 "참값"을 **L2 사영**으로 재정의한다:
  $\theta^*:=\arg\min_{\theta\in\Theta}\lVert\zeta(\cdot)-y_s(\cdot,\theta)\rVert_{L_2(\Omega)}$ (식 2.2).
- FabSim 함의: 우리 잔차 δ(r)(P11)가 존재하는 한, 물리 파라미터(P1 절대 Kp)를 δ와 **동시에** 자유
  추정하면 θ가 비식별로 흐른다 — 이것이 **P2 배율을 prior로 고정하고 δ는 GP로 분리**하는 설계의
  정당화다. Tuo&Wu의 L2 사영은 series_scale.py가 하는 "물리모델을 진실로 놓고 스칼라 배율만 최소자승으로
  맞추는" 동작(OLS 계열)에 대응한다 — 저자들은 OLS를 *"consistent but not efficient"*로 판정하므로, 우리
  스칼라 배율은 **편향은 없되 효율은 최적 아님**(더 정보적인 GP 처방이 원칙적으로 존재)임을 정직하게
  받아들인다(미검증 — L2 최적을 구현하지 않음).
- 보강(E5): **Brynjarsdóttir & O'Hagan (2014)**, "Learning about physical parameters: the importance of
  model discrepancy," *Inverse Problems* 30(11):114007, **DOI: 10.1088/0266-5611/30/11/114007** (IOP
  유료·봇차단, **초록만 E5**). 초록 원문: 모델 불일치가 *"being confounded with calibration parameters,
  which will only be resolved with meaningful priors"* — δ와 θ의 교락은 **의미 있는 prior로만** 풀린다.
  이는 Arendt2012의 두 식별 처방([[bayesian-calibration-koh-discrepancy]] §의 "δ 함수공간 제약 + 정보적
  사전")과 정확히 같은 결론이고, **P2 m_f를 literature prior로 고정한다**는 레지스트리 규칙의 문헌 근거다.

### 2.3 순차 피팅의 근거 — 재귀 co-kriging (Le Gratiet & Garnier 2014)

- **Le Gratiet & Garnier (2014)**, "Recursive co-kriging model for design of computer experiments with
  multiple levels of fidelity," *Int. J. Uncertainty Quantification* 4(5):365–386, **DOI:
  10.1615/int.j.uncertaintyquantification.2014006914** (arXiv:1210.0686v3 전문 24쪽 = **E2**).
- NPW 먼저·PTW 잔차 후라는 순차 위상을 **엄밀히 정당화**한다. 재귀 모형은
  $Z_t(x)=\rho_{t-1}(x)\,Z_{t-1}(x)+\delta_t(x),\quad Z_{t-1}(x)\perp\delta_t(x)$ (식 1) — 하위 레벨
  $Z_{t-1}$과 잔차 $\delta_t$가 **독립**이다. **Proposition 1**: 이 재귀 모형의 예측 평균·분산이 KOH(2000,
  Biometrika 87:1–13)의 원 co-kriging과 **동일**하다(*"identical to the ones of the original co-kriging
  model"*). 즉 **하위 레벨을 먼저 적합하고 상위 잔차를 따로 적합해도 결합 적합과 같은 사후분포를 준다** —
  순차 분해가 근사가 아니라 정확하다.
- FabSim 함의: 이것이 [[hierarchical-shrinkage-npw-prior-ptw-fit-drift-design]] §2의 "NPW 적합이 PTW
  우도를 전혀 보지 않는 1→2단계 위상"(Perdikaris2015 마르코프 가정)에 대한 **독립적 두 번째 근거**다.
  독립성 $Z_{t-1}\perp\delta_t$이 곧 `fit_ptw.fit`이 `npw_correction`을 **읽기전용 필수 인자**로 받고
  자기가 새로 학습하는 것은 "관측−물리−NPW보정" 두 번 뺀 잔차뿐이라는 코드 계약(fit_ptw.py docstring)의
  통계적 정본이다. 반대로 PTW가 NPW를 되먹이면 독립성이 깨져 Prop.1의 동일성이 성립하지 않는다.

## 3. 왜 이 순차 순서인가 — 세 근거의 합류

레지스트리 §1의 귀속 순서 1→5는 세 문헌이 서로 다른 각도에서 같은 결론에 이른다:
- **위상(Le Gratiet Prop.1 + Perdikaris2015)**: 하위(NPW)⊥잔차(PTW)라야 순차=결합. → 순서 4·5(NPW δ
  먼저, PTW 잔차 나중).
- **비식별(Raue 식10 + Tuo&Wu)**: 곱으로 얽힌 P1·P2·P3–P5는 프로파일이 평탄 → **안 흔든 축은 고정하고
  스칼라 lumped로 흡수**. → 순서 1·2·3.
- **교락 해소(Brynjarsdóttir + Arendt2012)**: δ와 θ의 교락은 정보적 prior로만. → P2를 literature prior로
  못박고 δ를 GP로 분리.

즉 순차 피팅은 편의가 아니라 **식별성이 강제하는 유일한 안전한 순서**다: 곱 인자를 다 풀 데이터가 없는
소량 레짐에서, 가장 넓은 prior(P1 estimated)를 데이터로 눌러 lumped 스케일로 흡수하고, 그보다 좁은
prior로 고정 가능한 것(P2 literature)은 고정하며, 반경/패턴 잔차는 비모수(δ)로 분리한다.

## 4. Python 검증 — 곱셈 구조의 3-레짐 식별성 + prior σ_log 대조 (Cal-1 (c))

**재현 요약(한 줄)**: Preston 곱모형 `MRR=Kp_ref·m_f·κ_size·P·V` 합성데이터(진값 TEOS 배율 1.35·입경
지수 4/3)로 최소자승 Jacobian 조건수와 **프로파일 우도 평탄도(Raue 식10)**를 계산해 — (1) 단일조건=cond ∞·
프로파일 완전평탄(Δχ²=0, 구조적 비식별), (2) P·V 스윕만=Kp_ref만 복원(오차<0.05)·배율/입경은 여전히
평탄, (3) 막종류+입경 스윕 추가=조건수 유한·전 파라미터 복원(오차<0.06)·프로파일 볼록(Δχ²>1) 을 assert
하고, 별 블록에서 prior.py σ_log 상수(literature 0.405·estimated 0.811·95%폭 ×2.21배)를 대조한다.

```python verify
import numpy as np
# ═══ 곱셈 구조 3-레짐 식별성 — 표준라이브러리+numpy만 (과제 (c) 지시) ═══
# 모형: MRR = Kp_ref·m_f(막)·κ_size(입경)·P^a·V^b. log공간: y = β0 + a·logP + b·logV + β1·[막=target] + β2·log(d/dref)
#   β0=logKp_ref(P1 절대), β1=log m_f(P2 배율, 진값=log1.35), β2=κ_size 기울기(P3, 진값=4/3), a=b=1(Preston)
rng = np.random.default_rng(0)
b0, b1, b2, a, b = np.log(0.74e-13), np.log(1.35), 4.0/3.0, 1.0, 1.0   # film-oxide m_TEOS=1.35, slurry κ정점하 4/3
dref = 50.0                                                            # oxide_silica 팩 입경 기준
def gen(rows, noise=0.02):
    X, y = [], []
    for (P, V, ft, d) in rows:
        xf = 1.0 if ft == "target" else 0.0; xd = np.log(d/dref)
        mu = b0 + b1*xf + b2*xd + a*np.log(P) + b*np.log(V)
        X.append([1.0, np.log(P), np.log(V), xf, xd]); y.append(mu + rng.normal(0, noise))
    return np.array(X), np.array(y)
P0, V0 = 20.7e3, 0.8
R1 = [(P0, V0, "ref", dref)]*25                                        # 레짐1: 단일조건 반복 25
Pg, Vg = [10e3, 20.7e3, 35e3], [0.5, 0.8, 1.2]
R2 = R1 + [(P, V, "ref", dref) for P in Pg for V in Vg for _ in range(3)]           # 레짐2: P·V 스윕만
R3 = R2 + [(P0, V0, ft, d) for ft in ("ref","target") for d in (dref,65.0,120.0) for _ in range(4)]  # 레짐3: +막+입경

def profile_dchi(X, y, idx):                # Raue 식10: β_idx 격자고정+나머지 재최적화 → χ² 프로파일의 진폭
    center = {3: b1, 4: b2}.get(idx, 0.0)
    grid = np.linspace(-1.0, 1.0, 41) + center
    cols = [c for c in range(X.shape[1]) if c != idx]; chis = []
    for g in grid:
        yr = y - g*X[:, idx]; beta, *_ = np.linalg.lstsq(X[:, cols], yr, rcond=None)
        r = yr - X[:, cols] @ beta; chis.append(r @ r)
    return float(np.max(chis) - np.min(chis))                         # 0 = 완전평탄(구조적 비식별)

out = {}
for name, rows in [("R1", R1), ("R2", R2), ("R3", R3)]:
    X, y = gen(rows); cond = np.linalg.cond(X.T @ X)
    beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    out[name] = dict(cond=cond, rank=int(rank), kp=abs(beta[0]-b0), mf=abs(beta[3]-b1),
                     sz=abs(beta[4]-b2), pf_sz=profile_dchi(X,y,4), pf_mf=profile_dchi(X,y,3))
    print(f"{name}: cond={cond:.2e} rank={rank}/5 | Kp_err={out[name]['kp']:.3f} "
          f"m_f_err={out[name]['mf']:.3f} κ_err={out[name]['sz']:.3f} | Δχ²(입경)={out[name]['pf_sz']:.2e}")

# (1) 단일조건 = 구조적 비식별: 조건수 ∞, 프로파일 완전평탄(Raue "flat valley")
assert out["R1"]["cond"] > 1e12 and out["R1"]["rank"] < 5
assert out["R1"]["pf_sz"] < 1e-9 and out["R1"]["pf_mf"] < 1e-9        # Δχ²=0 = 어느 값이든 동일 우도
# (2) P·V 스윕만 = Kp_ref(lumped Preston 계수)만 식별, 배율·입경은 여전히 평탄
assert out["R2"]["cond"] > 1e12 and out["R2"]["rank"] == 3
assert out["R2"]["kp"] < 0.05                                         # 절대 스케일 복원 (오차<0.05)
assert out["R2"]["pf_sz"] < 1e-9 and out["R2"]["pf_mf"] < 1e-9        # m_f·κ_size는 아직 분리 불가
# (3) 막종류+입경 스윕 추가 = 전부 식별: 조건수 유한, 전 파라미터 복원, 프로파일 볼록
assert out["R3"]["cond"] < 1e7 and out["R3"]["rank"] == 5
assert out["R3"]["kp"] < 0.06 and out["R3"]["mf"] < 0.06 and out["R3"]["sz"] < 0.06
assert out["R3"]["pf_sz"] > 1.0 and out["R3"]["pf_mf"] > 1.0          # 유일 최소 = 식별
print("[식별성] 단일조건 cond=∞·평탄 → P·V스윕 Kp_ref만 → +막+입경 전부식별(cond<1e7, Δχ²>1)")
```

```python verify
import numpy as np
# ═══ 레지스트리 σ_log 열 대조 — sim/calibration/prior.py confidence_to_log_sigma 상수 ═══
LN15 = np.log(1.5)                                     # prior.py _LOG_SIGMA_LITERATURE (판정#55, 문헌간 1.5배 산포)
mult = {"verified": 0.25, "measured": 0.5, "literature": 1.0, "estimated": 2.0}   # prior.py _CONFIDENCE_MULTIPLIER
sig = {g: LN15*m for g, m in mult.items()}
# prior.py 상수와 문헌값 대조: literature σ_log=0.405, estimated 0.811, measured 0.203, verified 0.101
assert abs(sig["literature"] - 0.405) < 0.003 and abs(sig["estimated"] - 0.811) < 0.003
assert abs(sig["measured"] - 0.203) < 0.003 and abs(sig["verified"] - 0.101) < 0.003
# 레지스트리 배정 정합: P1 절대 Kp_ref=estimated(넓게), P2 배율 m_f=literature, P4 농도=measured(E1 22점)
assert sig["estimated"] > sig["literature"] > sig["measured"] > sig["verified"]   # 절대스케일이 배율보다 넓다
# 95% prior 폭 배율 = exp(±1.96σ): m_f는 ×2.21배, Kp_ref는 ×4.90배로 대조
w_mf, w_kp = np.exp(1.96*sig["literature"]), np.exp(1.96*sig["estimated"])
assert abs(w_mf - 2.21) < 0.03 and abs(w_kp - 4.90) < 0.06
# P5 χ_pH(unverified 다수)는 prior 생성 제외 — 근거없는 값에 폭 부여 금지(PriorExcluded)
assert "unverified" not in mult
print(f"[σ_log] verified {sig['verified']:.3f}·measured {sig['measured']:.3f}·"
      f"literature {sig['literature']:.3f}·estimated {sig['estimated']:.3f}; "
      f"95%폭 m_f ×{w_mf:.2f}배·Kp_ref ×{w_kp:.2f}배; unverified 제외")
```

**결과 해석(정직하게)**
- 두 블록 모두 **합성데이터/코드상수에 대한 이 노트의 직접 계산**이지 실측 재현이 아니다(정직성 표지).
  진값 배율(1.35)·지수(4/3)만 형제 노트 문헌 판독값을 썼다. 조건수 ∞와 프로파일 평탄은 곱셈 구조의
  수학적 귀결이라 실측 노이즈가 있어도 회복되지 않는다 — **스윕(구조적 정보)만이 식별을 준다**.
- R2에서 β0(logKp_ref) 자체가 복원되는 이유는 P·V 스윕이 절편+Preston 지수(a,b)를 full-rank로 만들기
  때문이고, m_f·κ_size는 여전히 상수열이라 rank 3/5에 머문다 — Raue의 구조적 비식별이 정확히 그 두 축에만
  남는다. 이는 film-oxide §4-A(기준막 없으면 배율과 절대가 얽힘)의 통합판이다.
- σ_log 블록은 prior.py 운영 규약(등급 배율)을 그대로 계승한 것이고 문헌값이 아니다 — prior.py docstring이
  "verified/measured/estimated 배수는 미검증 운영 규약"이라 자백한 그대로다(§7).

## 5. 피팅 절차 명세 + sim/calibration 함수 매핑 (Cal-1 (d))

통합 레코드가 들어와 UQ 예측이 나가기까지의 5단계를, 각 단계가 `sim/calibration`의 어느 함수에 대응하는지·
**없는 것(미구현)**은 무엇인지로 정리한다. 함수 시그니처는 [[hierarchical-shrinkage-npw-prior-ptw-fit-drift-design]]가
확정한 것을 인용하며, 여기서 새 설계를 만들지 않는다.

| 단계 | 입력→출력 | 대응 sim/calibration 함수 | 상태 | 이 레지스트리와의 연결 |
|---|---|---|---|---|
| **1. Ingest** | 통합 스키마 레코드 → 표준단위 관측(nm/nm_per_min) | `ingest.py`(스키마검증·단위정준) | 구현됨 | P1–P11의 `pressure`·`velocity`·`film_type`·`local_density` 필드 통과(§5 스키마제안은 형제 소관) |
| **2. Prior** | 팩 YAML+등급 → 로그정규 사전 | `prior.py: build_param_priors`/`confidence_to_log_sigma` | 구현됨 | 레지스트리 σ_log 열이 곧 이 함수 출력. P5 unverified는 `PriorExcluded`로 제외(§4-B) |
| **3-N. NPW 적합** | NPW(pred,obs)+prior → 스칼라 배율 `s`(=P1) + 반경 δ(r)(=P11) | `series_scale.fit_series_scale`→`fit_npw.fit`; `fit_npw.NPWCorrection` | 구현됨 | 귀속 순서 1·4. **P2 배율 재추정 경로는 없음**(설계상 고정) |
| **3-P. PTW 적합** | PTW(pred,obs)+`NPWCorrection`(읽기전용 필수) → 두 번 뺀 잔차(P8·P10) | `fit_ptw.fit`(npw_correction 필수) | 구현됨 | 귀속 순서 5. Le Gratiet 독립성(§2.3)이 이 필수인자 계약의 정본 |
| **4. 잔차 진단** | 잔차 시계열 → EWMA 관리도·소모품 리셋 | `drift.py: residual_ewma_signal`·`consumable_reset_event` | 구현됨 | 로트/패드 변경 시 유효 n을 0으로(내 Lv3-1) |
| **5. UQ 출력** | 보정예측 + 90% CI + 이론대비 편차 | `predict.py: predict_radial`→`PredictionResult` | 구현됨 | δ+e 산포 포함해야 커버리지 회복(내 Lv2-2, ≈36%→≈95%) |

**미구현(레지스트리가 드러낸 공백 — PROFILE.md 구현요청 §8):**
- **스펙축 잔차 귀속(P3/P4/P5)**: 현재 `fit_npw`는 반경 δ(r)만 학습하고 **입경·농도·pH 축에 잔차를
  귀속하는 경로가 없다**. §1 순서 3(스윕 있을 때만 귀속)을 실제로 하려면 validation/datasets의 스윕 축을
  design matrix로 받아 κ_size/κ_conc 계수를 별도 최소자승으로 뽑는 함수가 필요하다(§4 블록1이 그 원형).
- **막종류 배율 재추정 게이트(P2)**: `is_reference_film` 플래그(film-oxide §5 제안)를 읽어 "기준막+대상막
  동일 P·V 동시측정"일 때만 m_f를 열어주는 조건부 경로 — 지금은 항상 고정. 없으면 안전(고정이 보수적).
- **P7 선택비·P8 디싱의 조건 매칭 검사**: oxide·stop이 동일 P·V인지, 밀도 ρ가 ≥2점인지(§1 식별조건)를
  ingest 게이트에서 검사하는 로직 — 현재 없음.

## 6. 근거 충돌 판정 (EVIDENCE-RULES.md 서열)

| # | 충돌 | A (등급) | B (등급) | 판정 |
|---|---|---|---|---|
| 1 | m_f 배율을 데이터로 재추정 vs prior 고정 | 소량 고객데이터로 m_f 자유추정(자유도↑) | Brynjarsdóttir/Arendt2012: 교락은 정보적 prior로만 해소 (E5/E2) | **B 채택(고정)** — δ·θ 교락이 소량 레짐에서 m_f를 비식별로 흐르게 함(§2.2·§4-A). 재추정은 기준막+대상막 동시 스윕에서만 |
| 2 | 스윕 없는 축의 잔차 귀속 | 백테스트 ρ가 좋아지는 축에 귀속 | EVIDENCE-RULES §3·§금지: 데이터 스누핑 금지 | **B 채택** — 안 흔든 축을 임의 분할하지 않고 lumped Kp_ref에 흡수(순서 규칙 3) |

새 물리 충돌 없음 — 두 판정 모두 방법론(식별성) 규칙이다. 상반된 지수를 평균낸 곳 없음.

## 7. 한계·미확보·미검증 (정직성 표기)

- **Raue 2009는 PDF 전문 미확보**(OUP 봇차단 403). §2.1의 식 4/8/10·Def.1은 OUP 기사 HTML에서 직접
  판독했으나 그림·응용예(§5)는 못 읽었다 — 정의식만 E2, 나머지 미확인.
- **Brynjarsdóttir & O'Hagan 2014는 초록만(E5)**. IOP 유료·봇차단으로 전문 미확보. 교락 결론은 초록
  원문 인용이나 이론 논증(§theoretical arguments)은 미판독 — 보강 인용으로만 썼다.
- **σ_log 등급 배수(0.25/0.5/2.0)는 미검증 운영 규약**이다(prior.py docstring 자백). literature=ln1.5만
  판정#55 근거가 있고 나머지는 상대 배수다 — 레지스트리 σ_log 열은 이 규약을 그대로 계승했다.
- **§4는 합성데이터·코드상수 계산**이지 실측 재현이 아니다(정직 표지). 진값 배율/지수만 형제 노트
  문헌값이다. 조건수·프로파일 평탄은 곱 구조의 수학적 귀결.
- **Tuo&Wu의 L2 최적 처방은 미구현**이다 — series_scale의 스칼라 최소자승은 OLS 계열(consistent but not
  efficient)이라 원칙적으로 더 효율적인 처방이 있으나 이 프로젝트는 구현하지 않았다(우선순위 낮음).
- **레지스트리 중심값은 전부 형제 노트에서 옮긴 것**이고 이 노트에서 새로 측정하지 않았다 — 각 값의 1차
  근거·미확보는 해당 형제 노트(§0 링크)를 따른다. P5 χ_pH·P9 전이편향의 절대수치는 형제 소관이라 재검증
  안 함.

## 8. 구현 요청
→ [[../../agents/cmp-calibrator/PROFILE.md]] "## 구현 요청" 참조 (스펙축 잔차 귀속 함수·m_f 재추정 게이트·
조건매칭 검사 3건, §5 미구현 목록).

## 9. 자기시험
→ [[../../agents/cmp-calibrator/EXAMS.md]] Cal-1 문항 참조.

## 상호링크
[[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]]
[[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]]
[[../cmp/wafer-type-npw-ptw-metadata-schema-alignment-rules]]
[[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]]
[[hierarchical-shrinkage-npw-prior-ptw-fit-drift-design]] [[hierarchical-bayesian-npw-ptw-transfer]]
[[uq-prediction-interval-coverage-extrapolation-warning]] [[bayesian-calibration-koh-discrepancy]]
[[gp-regression-small-data-kernel-prior-mean]] [[../cmp/calibration-drift-detection-recalibration-triggers]]
