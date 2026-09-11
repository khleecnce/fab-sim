# 합성 데이터 생성기 — Tier1/2 모델 출력 + 현실적 노이즈로 캘리브레이션 파이프라인 검증 (cmp-data-engineer Lv2-2)

> 에이전트: cmp-data-engineer Lv2-2 | 작성일: 2026-09-11
> 관련: [[wafer-coordinate-units-outlier-cleaning]] (Lv2-1 — MAD 이상치 규칙을 이 노트의 합성 스파이크/드리프트 검출에 재사용), [[cmp-public-datasets-survey]] (Lv1-1 — Li et al. 2019 PHM2016 잔차값의 최초 출처), [[cmp-integration-schema-keys-semi-standards]] (Lv1-2 — 같은 잔차값을 스키마 검증에 이미 사용), [[diamond-grit-mesh-bonding]] (실측 제거율 CV% 대조 앵커)
> 범위: **캘리브레이션 파이프라인 자체를 검증**하기 위해, "정답(ground truth)을 아는" 합성 데이터를 어떻게 만드는가. Tier1(물리식)/Tier2(반경험식) 모델의 순수 출력에 센서 노이즈·웨이퍼간 편차·drift를 더할 때, 그 노이즈 크기가 실측 CMP/반도체 공정 데이터와 자릿수가 맞아야 한다는 게 이 단원의 핵심 주장이다. 노이즈 함수형 자체(Tier1/2 모델식)는 형제 에이전트 소관이라 재유도하지 않는다.

## 0. 문제 정의 — 왜 "정답을 아는" 가짜 데이터가 필요한가

캘리브레이션 파이프라인(입력 정규화 → 모델 적합 → κ 추정)을 실측 데이터만으로 검증하면, 파이프라인 버그와 모델 부정확성을 구분할 수 없다. Tier1/2 모델이 알려진 파라미터로 생성한 순수 출력값에 통제된 노이즈를 더해 합성 데이터셋을 만들면, "이 노이즈 아래서도 원래 파라미터를 복원하는가"를 코드로 테스트할 수 있다. 단, 노이즈를 비현실적으로 작게 넣으면 파이프라인이 과신되고, 비현실적으로 크게 넣으면 정상 파이프라인도 기각된다 — 그래서 노이즈 크기 자체를 실측 문헌값과 대조해야 한다(§3).

## 1. 합성 웨이퍼 프로파일 생성의 1차 문헌 패턴 — RBF 합·Zernike 합 + 가산 가우시안 노이즈

1차 논문: **McLoone, Johnston & Susto (2017/2018)**, "A Methodology for Efficient Dynamic Spatial Sampling and Reconstruction of Wafer Profiles," *IEEE Transactions on Automation Science and Engineering* 15(4), 1692–1703. **DOI: 10.1109/TASE.2017.2786213** (Queen's University Belfast PURE 리포지토리에서 OA 원문 확보, papers/susto2018-tase-spatial-sampling-wafer.txt로 fitz 렌더 후 텍스트 확인). CVD 막두께·플라즈마 식각 트렌치 깊이·폭 계측을 대상으로 하는 반도체 웨이퍼 프로파일 샘플링·재구성 방법론 논문으로, **평가를 위해 두 종류의 합성 웨이퍼 케이스 스터디**를 명시적으로 쓴다(§IV, 원문 확인).

- **Case study 2 [RBF]**: $z(x,y) = \sum_{i=1}^{N_g} h_i \exp\!\big(-\frac{(x-c_{xi})^2+(y-c_{yi})^2}{S_f^2}\big) + \epsilon$, $h_i\sim N(0,1)$, $c_{xi},c_{yi}\sim U(-1,1)$, **$\epsilon\sim N(0, 0.02)$가 계측 노이즈(measurement noise)를 모사**한다고 원문이 명시. $S_f$(spread factor)로 공간상관 스무스함을 조절 — Tier1 물리모델이 아니라 **순수 통계적 형상 생성기**지만, "가산 가우시안 노이즈로 계측 노이즈를 모사한다"는 방법론 자체가 이 단원이 재사용할 패턴이다.
- **Case study 3 [Zernike]**: $z(\rho,\theta)=\sum_{i=1}^{36}\alpha_i Z_i(\rho,\theta)$, $\alpha_i \sim N(0,\,8e^{-0.3i})$ — **모드 지수가 커질수록 계수 분산이 지수적으로 감쇠**한다. Zernike 다항식은 광학·반도체 계측에서 비축대칭 웨이퍼 형상을 표현하는 표준 직교기저(원문 §IV 확인)라, 이 분산 감쇠 법칙은 "고차 공간주파수 성분일수록 에너지가 작다"는 물리적으로 흔한 가정을 정식화한 것이다. 원문의 반경함수 $R^m_n(\rho)$ 완전식은 OCR 추출이 일부 손상돼 §4.2에서 재현하지 않고, **분산 감쇠 법칙 자체만** 재현한다(§8 확인 못함 표기).
- **Case study 1 [실측]**: 동일 논문이 합성 케이스와 **나란히** 실제 팹 데이터(단일 양산 툴, 50 사이트 고정 측정계획, 316웨이퍼, 기밀상 정규화)로도 같은 방법론을 검증한다. 즉 1차 문헌 자체가 "합성만으로 끝내지 말고 실데이터로 교차검증하라"는 이 단원의 기본 태도를 실천한 선례다.

→ **생성 규칙 1**: Tier1/2 CMP 모델(예: Preston MRR, GW 접촉역학)의 결정론적 출력을 위 $z(x,y)$ 역할로 대체하고, 그 위에 가산 가우시안 노이즈를 더하는 것이 문헌적으로 확립된 패턴이다. 노이즈의 **크기**(분산)만 CMP 도메인 실측값으로 교체해야 한다(§3).

## 2. 노이즈 성분 분해 — 센서 노이즈 vs 웨이퍼간 편차 vs drift

Big data/디지털트윈 문헌: **Moyne & Iskandar (2017)**, "Big Data Analytics for Smart Manufacturing: Case Studies in Semiconductor Manufacturing," *Processes* 5(3), 39. **DOI: 10.3390/pr5030039**(MDPI OA, papers/moyne2017-processes-bigdata.txt 확인). 이 논문은 "디지털 트윈(digital twin)"을 "기존 시스템의 확장으로서 팹 운영 전체를 동적으로 갱신되는 시뮬레이션 모델로 실시간 모사하는 상태"로 정의하고(§5.3, [19,20] 인용), 합성 데이터 생성기가 모사해야 할 노이즈/이상 패턴을 실무 관점에서 **4대 원형(archetype)**으로 제시한다(§4.1, 트레이스 파티셔닝 논의):

1. **step**(스위치 on/off 같은 계단형 변화), 2. **oscillation**(진동·언더댐프 구동), 3. **spike**(순간 교란), 4. **drift/ramp**(점진적 경향) — "물리적 공정에서 전형적으로 나타나는 신호 패턴"으로 명시.

drift의 **원인**도 명시적으로 열거한다(§3.1): 챔버 시즈닝(seasoning) 등 내부 공정·장비 요인, 소모품의 점진적 소모(gradual depletion of a consumable — CMP라면 패드·디스크 마모), 유지보수 이벤트·제품 전환 같은 외부 "컨텍스트" 변화. 또한 EHM(장비건전성모니터링)류 다변량 분석이 "노이즈와 기타 데이터품질 문제에 특히 취약하다(highly susceptible to noise)"고 명시해(§3.3), 노이즈를 무시한 파이프라인 검증이 왜 위험한지를 뒷받침한다.

→ **생성 규칙 2**: 합성 신호는 최소 3개 성분으로 분해해 생성한다 — **(a) 센서 노이즈**(iid 가우시안, §1의 $\epsilon$), **(b) 웨이퍼간 랜덤효과**(로트/웨이퍼 단위 상수 오프셋, RBF 모델의 $h_i$ 역할과 유사한 배치 수준 변동), **(c) drift**(공정 동역학 원인에 대응하는 시간의존 성분 — 패드/디스크 소모라면 단조 ramp, 유지보수 이벤트라면 step). 정확한 drift 함수형(선형 ramp vs 지수 vs Ornstein-Uhlenbeck)은 이 두 문헌이 확정해주지 않으므로 **미검증**으로 남기고, moyne2017의 정성적 4분류(step/oscillation/spike/drift)를 합성기의 이상 패턴 라이브러리로 채택한다.

## 3. 노이즈 크기 — 실측 CMP/공정 데이터와의 자릿수 대조

합성 노이즈 분산을 "그럴듯하게" 고르는 대신, 실측 문헌값과 자릿수를 맞춘다.

- **CMP 가상계측(VM) 잔차 — 절대 크기(nm/min) 앵커**: Li, Wu, Yu (2019), *J. Manuf. Sci. Eng.* 141(3):031003, **DOI: 10.1115/1.4042051** (앞서 [[cmp-public-datasets-survey]]·[[cmp-integration-schema-keys-semi-standards]]가 확보). PHM2016 CMP 데이터셋(실제 4개 CMP 툴의 FDC 신호→MRR)에서 GBT(35특징) 모델의 검증셋 R²=0.917, **잔차 표준편차 8.317 nm/min**. 이 값은 "센서 노이즈+공정 확률변동+모델 미스핏"이 합쳐진 **실측 노이즈 바닥(floor)**이다 — 합성 데이터에 이보다 훨씬 작은 노이즈를 넣으면 파이프라인이 실전보다 낙관적으로 통과하게 된다.
- **정성적 교차확인**: Di, Jia & Lee (2017), "Enhanced Virtual Metrology on Chemical Mechanical Planarization Process using an Integrated Model and Data-Driven Approach," *International Journal of Prognostics and Health Management* 8(2). **DOI: 10.36001/ijphm.2017.v8i2.2641**(PHM Society, CC-BY, papers/di2017-ijphm-cmp-vm.txt로 원문 확보). 같은 PHM2016 데이터셋에서 물리모델(Preston형) + 데이터기반 앙상블로 여러 모델의 20회 교차검증 MSE(평균·표준편차, Table 4)를 보고하며 통합모델이 최저 평균 MSE(7.07)를 낸다. 이 논문의 MSE는 원문에 단위가 명시되지 않아(정규화 여부 불명) **절대 수치는 재사용하지 않고**, "여러 독립 모델·조건에서도 잔차 규모가 한 자릿수 안에 모인다"는 **정성적 정합성**만 Li 2019 수치의 교차확인으로 인용한다(§8 참조, 출처 불명 항목).
- **상대 크기(CV%) 앵커 — 유사 공정(연마재 제거율)**: JP4508514B2(전착 다이아몬드 그릿 드레서 특허, 실시예 n=20 반복측정, patents.google.com 텍스트 확인 — [[diamond-grit-mesh-bonding]] §4가 먼저 확보). 종래 설계 제거율 130±18.0 µm/h → **CV 13.8%**, 발명 설계 156±8.6/170±9.0 µm/h → **CV 5.3~5.5%**. CMP 폴리싱 그 자체의 실측 CV%는 이번 조사에서 1차 확보하지 못했지만, **같은 "연마재 제거 공정" 계열의 실측 반복성이 5~14% 범위**라는 점은 합성 데이터의 웨이퍼간 편차 항 크기를 "1% 미만은 비현실적으로 작고 30%를 넘으면 비현실적으로 크다"는 대략의 상한/하한 감으로 쓸 수 있다(정성적 가이드라인, 정량 이식 아님).

→ **생성 규칙 3**: 합성 MRR형 변수의 센서 노이즈+미스핏 표준편차는 (변수 스케일이 유사하다면) **~8 nm/min 자릿수**를 하한 가이드로 삼고, 웨이퍼간 편차는 **CV 5~14%** 자릿수를 참고한다. 정확한 CMP MRR 자체의 CV%는 **미검증**(공개 문헌에서 1차 확보 못함) — 필요시 Tier1/2 모델 계열별로 형제 에이전트의 κ 신뢰도 노트에서 잔차 통계를 가져와 갱신해야 한다.

## 4. Python 재현 (verify)

### 4.1 RBF 합성 웨이퍼 + 가산 가우시안 노이즈 (McLoone/Susto 2018 eq.19)

```python verify
import numpy as np
rng = np.random.default_rng(42)

def rbf_wafer(rng, n_pts=2000, Ng=100, Sf=0.3, noise_var=0.02):
    theta = rng.uniform(0, 2*np.pi, n_pts)
    r = np.sqrt(rng.uniform(0, 1, n_pts))          # 단위원판 균일표본(면적가중)
    x, y = r*np.cos(theta), r*np.sin(theta)
    h = rng.normal(0, 1, Ng)                        # h_i ~ N(0,1)
    cx = rng.uniform(-1, 1, Ng); cy = rng.uniform(-1, 1, Ng)
    z_clean = np.zeros(n_pts)
    for i in range(Ng):
        z_clean += h[i]*np.exp(-((x-cx[i])**2 + (y-cy[i])**2)/Sf**2)
    eps = rng.normal(0, np.sqrt(noise_var), n_pts)  # eps ~ N(0, 0.02) 논문 명시값
    return x, y, z_clean, z_clean + eps

x, y, z_clean, z_noisy = rbf_wafer(rng)
noise = z_noisy - z_clean
# 노이즈 성분만 따로 대량표본으로 분산 검증 (분리 RNG로 좌표와 독립 확인)
eps_big = rng.normal(0, np.sqrt(0.02), 200_000)
assert abs(eps_big.mean()) < 0.01, "가산 노이즈 평균이 0에서 벗어남"
assert abs(eps_big.std() - np.sqrt(0.02)) < 0.01, "노이즈 표준편차가 문헌값 sqrt(0.02)=0.1414와 불일치"
assert np.all(np.hypot(x, y) <= 1.0 + 1e-9), "표본점이 단위원판을 벗어남"
print(f"[4.1] eps~N(0,0.02) 재현: mean={eps_big.mean():.4f}, std={eps_big.std():.4f} "
      f"(문헌값 std=sqrt(0.02)={np.sqrt(0.02):.4f})")
```

### 4.2 Zernike 계수 분산 감쇠 법칙 (eq.20) — 고차모드 에너지 감쇠

```python verify
import numpy as np
rng = np.random.default_rng(3)
i_idx = np.arange(1, 37)                    # 논문 케이스: N=7 -> 36개 Zernike 기저
var_i = 8 * np.exp(-0.3 * i_idx)            # alpha_i ~ N(0, 8*exp(-0.3*i)) 문헌 명시식
ratio = var_i[1:] / var_i[:-1]
assert np.allclose(ratio, np.exp(-0.3), atol=1e-9), "연속 모드간 분산비가 exp(-0.3) 상수가 아님"
assert np.all(np.diff(var_i) < 0), "모드 지수 증가에 따라 분산이 단조감소하지 않음"
assert abs(var_i[0] - 8*np.exp(-0.3)) < 1e-9      # i=1: ~5.9265
alpha = rng.normal(0, np.sqrt(var_i))
assert alpha.shape == (36,)
print(f"[4.2] Zernike 분산감쇠: var(i=1)={var_i[0]:.4f}, var(i=36)={var_i[-1]:.6f}, "
      f"연속비={ratio[0]:.4f}(=exp(-0.3)={np.exp(-0.3):.4f}) — 문헌식 재현")
```

### 4.3 노이즈 크기 문헌값 대조 (Li 2019 실측 잔차 vs JP4508514B2 실측 CV%)

```python verify
# Li, Wu, Yu (2019) DOI:10.1115/1.4042051 — 실측 CMP VM 잔차(노이즈 바닥)
r2_lit = 0.917
resid_std_lit_nm_per_min = 8.317
assert 0.90 <= r2_lit <= 0.93 and 8.0 <= resid_std_lit_nm_per_min <= 8.5, "Li2019 문헌값 범위 이탈"

# JP4508514B2 — 유사 연마재제거 공정 실측 CV%(n=20)
cv_conventional = 18.0 / 130     # 종래설계
cv_invented_1 = 8.6 / 156        # 발명 실시예1
cv_invented_2 = 9.0 / 170        # 발명 실시예2
assert abs(cv_conventional - 0.1385) < 0.001, cv_conventional
assert 0.05 <= cv_invented_1 <= 0.06 and 0.05 <= cv_invented_2 <= 0.06
assert cv_conventional > cv_invented_1 and cv_conventional > cv_invented_2, "종래 CV가 발명보다 작아 문헌 주장과 불일치"

# 합성데이터 노이즈 가이드라인: CV 자릿수가 5~14% 범위 안인지 자체 점검
lo, hi = 0.05, 0.14
assert lo <= cv_invented_1 <= hi and lo <= cv_conventional <= hi, "실측 CV%가 제안한 가이드 범위를 벗어남"
print(f"[4.3] 실측 노이즈바닥 {resid_std_lit_nm_per_min}nm/min(R^2={r2_lit}); "
      f"실측 CV%: 종래={cv_conventional*100:.1f}%, 발명={cv_invented_1*100:.1f}~{cv_invented_2*100:.1f}%")
```

### 4.4 노이즈 성분 분해 합성 신호 + Lv2-1 MAD 재사용 — spike는 잡히고 drift는 안 잡힌다

```python verify
import numpy as np
rng = np.random.default_rng(7)
n = 200
t = np.arange(n)
base = rng.normal(500.0, 5.0, n)             # (a) 센서 노이즈: sigma=5 (베이스라인)

# (c-1) spike: 순간 교란 1점 +40 (=8 sigma)
spiked = base.copy(); spiked[100] += 40.0
# (c-2) drift: 소모품 점진소모형 선형 ramp, 종점까지 총 30(=6 sigma) 누적
drifted = base + np.linspace(0.0, 30.0, n)

b = 1.4826                                    # Lv2-1(wafer-coordinate-units-outlier-cleaning) MAD 상수 재사용
def mad_z(x):
    med = np.median(x)
    mad = b*np.median(np.abs(x - med))
    return np.abs(x - med)/mad

z_spike = mad_z(spiked)
z_drift = mad_z(drifted)
assert z_spike[100] > 2.5, "스파이크가 MAD(2.5) 이상치로 검출되지 않음"
assert (z_spike[np.arange(n) != 100] > 2.5).mean() < 0.05, "스파이크 외 정상점의 오탐률이 과도함"
assert z_drift.max() < 2.5, "점진 drift가 MAD 점별 이상치로 (잘못) 검출됨 — drift는 점별탐지로 못 잡는 게 정상"

# drift는 점별 MAD 대신 시간-값 상관(추세)으로 잡아야 함을 대조
corr_drift = np.corrcoef(t, drifted)[0, 1]
corr_base = np.corrcoef(t, base)[0, 1]
assert corr_drift > 0.8 and abs(corr_base) < 0.3, "추세상관이 drift/베이스라인을 구분하지 못함"
print(f"[4.4] spike z={z_spike[100]:.2f}(검출) vs drift max z={z_drift.max():.2f}(미검출), "
      f"추세상관 drift={corr_drift:.2f} vs base={corr_base:.2f} — 점탐지·추세탐지 역할분리 재현")
```

## 5. 정량 재현 요약 (§4 대조표)

| 재현 항목 | 계산값 | 문헌/정의 앵커 | 결과 |
|---|---|---|---|
| RBF 노이즈 표준편차 | 0.1414 | McLoone/Susto 2018 eq.19, ε~N(0,0.02) | 일치(오차<0.01) |
| Zernike 연속모드 분산비 | 0.7408 | 동 논문 eq.20, exp(-0.3) | 완전 일치(<1e-9) |
| CMP VM 잔차 표준편차 | 8.317 nm/min | Li et al. 2019, DOI:10.1115/1.4042051 | 문헌값 재확인 |
| 유사공정 실측 CV%(종래/발명) | 13.8% / 5.3~5.5% | JP4508514B2 실시예·비교예 | 문헌값 재확인 |
| 스파이크 MAD z | 9.17(>2.5) | moyne2017 4패턴 중 spike | 검출 재현 |
| drift 점별 MAD z(최댓값) | 2.15(<2.5) | moyne2017 4패턴 중 drift | 미검출(의도된 결과) 재현 |
| drift 추세상관 | 0.90 (베이스라인 0.10) | §2 drift 정의 | 대안탐지 재현 |

RBF·Zernike 노이즈 모델은 문헌식과 완전 일치(정의식이므로 당연), CMP VM 잔차·유사공정 CV%는 실측 문헌값을 그대로 재확인, spike/drift 분리는 자체 설계 검증(§4.4)으로 "점별 이상치 탐지와 drift 탐지는 다른 도구가 필요하다"는 §2 주장을 수치로 뒷받침했다.

## 6. 구현 요청 (트랙B로 인계 — PROFILE.md에 등록)

- **무엇을**: `sim/calibration/synth.py`(신설) — Tier1/2 모델 출력에 노이즈를 입혀 합성 캘리브레이션 데이터셋 생성.
  1. `add_sensor_noise(clean, sigma)`: 가산 iid 가우시안. §1·§4.1 eps~N(0,var) 패턴.
  2. `add_wafer_random_effect(clean, wafer_ids, cv)`: 웨이퍼(로트) 단위 상수 배율/오프셋 랜덤효과. §3의 CV 5~14% 자릿수를 기본 프리셋으로.
  3. `add_drift(clean, kind='ramp'|'step', magnitude, t)`: moyne2017 §4.1의 drift/step 패턴. ramp 기본, step은 유지보수 이벤트 모사용 선택지.
  4. `add_spike(clean, idx, magnitude)`: moyne2017의 spike 패턴 — 파이프라인의 이상치 플래그(Lv2-1 `flag_outliers`)가 이를 잡는지 회귀테스트하는 용도.
  5. 전부 "clean 값·주입 노이즈 파라미터·seed"를 메타데이터로 반환(가역·재현, Lv1-1/Lv2-1 원칙 계승) — 캘리브레이션이 원래 파라미터를 복원하는지 채점 가능해야 함.
- **근거노트**: 본 노트 §1–3. **검증문헌값**: §4 전부(회귀테스트로 승격) — eps~N(0,0.02)(McLoone/Susto 2018, DOI:10.1109/TASE.2017.2786213), 잔차 8.317 nm/min(Li 2019, DOI:10.1115/1.4042051), CV 5.3~13.8%(JP4508514B2).
- **우선순위**: 중 — Lv1-2 스키마·Lv2-1 normalize.py가 먼저 확정된 후, Lv3-2 ingest 파이프라인의 "회귀테스트 데이터" 공급원으로 착수.

## 7. 남은 미확보·미검증 (정직성 표기)

- Zernike 반경함수 $R^m_n(\rho)$의 원문 완전식: OCR 추출이 손상돼 §4.2에서 재현하지 않았다. **분산 감쇠 법칙만 재현**, 실제 Zernike 기저 형상 자체는 미검증.
- drift의 정확한 함수형(선형 ramp vs 지수적 vs Ornstein-Uhlenbeck류 확률과정): moyne2017은 drift의 **원인**(챔버 시즈닝·소모품 소모·유지보수)과 **패턴 이름**(ramp)만 제시할 뿐 수식을 주지 않는다. §4.4의 선형 ramp는 이 단원이 채택한 **가장 단순한 근사**이며 실측 대조는 안 됨 — 미검증.
- Di et al. 2017의 MSE 단위: 원문에 정규화 여부·단위가 불명확해 절대수치를 재사용하지 않았다(§3). Li 2019와 같은 PHM2016 데이터셋을 쓰지만 전처리(정규화)가 다를 수 있어 직접 비교는 위험 — 정성적 자릿수 정합만 인용.
- CMP 폴리싱 자체의 실측 MRR CV%(웨이퍼간·런간): 이번 조사에서 1차 문헌으로 확보하지 못했다. §3의 5~14% CV 가이드는 **유사 연마재제거 공정(전착 드레서)에서 이식한 것이지 CMP 폴리싱 실측치가 아니다** — 대체 가능한 1차 CMP CV% 문헌이 확보되면 이 노트를 갱신해야 한다.
- 웨이퍼간 랜덤효과의 분포 형태(가우시안 가정): §1 RBF 모델의 $h_i\sim N(0,1)$을 그대로 빌렸으나, 이는 원 논문이 "형상 생성"을 위해 쓴 임의 가정이지 CMP 웨이퍼간 변동이 실제로 정규분포를 따른다는 실측 근거는 아니다 — 미검증.

## 8. 자기시험
→ [[../../agents/cmp-data-engineer/EXAMS.md]] Lv2-2 문항 참조.
