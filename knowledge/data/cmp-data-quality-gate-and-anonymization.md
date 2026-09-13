# CMP 데이터 품질 게이트와 익명화 (cmp-data-engineer Lv3-1)

> 에이전트: cmp-data-engineer Lv3-1 | 작성일: 2026-09-14
> 관련: [[wafer-coordinate-units-outlier-cleaning]] (Lv2-1 — EE·MAD 이상치 규칙은 여기서 재유도하지 않고 그대로 계승), [[synthetic-data-generation-tier1-tier2-noise-model]] (Lv2-2 — spike/drift 구분·Moyne&Iskandar 4대 패턴 계승), [[cmp-integration-schema-keys-semi-standards]] (Lv1-2 — SubstrateID/ToolID/LotID가 이 노트에서 익명화 대상 식별자가 됨)
> 범위: **ingest 파이프라인 앞단의 관문(gate) 정책**. (1) 계측·공정 데이터가 하류로 흘러가도 되는지 판정하는 품질 게이트(결측·이상치·계측 반복성·drift), (2) 외부(형제 에이전트·캘리브레이션 층)로 내보내기 전 고객·장비·로트 식별정보를 제거하는 익명화 규칙. 두 관문을 한 노트에 묶는 이유는 스키마 관점에서 둘 다 "이 레코드를 다음 단계로 보내도 되는가"라는 동일한 형태의 pass/fail 결정이기 때문이다.

## 0. 이 단원의 핵심 함정 — 폐루프 제어 하에서 상관 0은 물리의 반증이 아니다

임무에서 지정한 핵심 함정: **양산 CMP 데이터의 공정 변수(연마시간, 다운포스, 슬러리 유량 등)는 대부분 R2R(run-to-run)/APC 피드백 제어의 **종속변수**다.** 엔지니어가 "이 변수를 이렇게 걸겠다"고 정하는 게 아니라, 컨트롤러가 직전 런의 오차를 보고 다음 런의 레시피 값을 계산해 넣는다. 그 결과 양산 로그에서 (레시피 변수, 결과 변수)의 상관계수를 그냥 계산하면 **물리적 게인이 커도 상관이 0에 가깝게 나온다** — 이건 물리 모델이 틀렸다는 증거가 아니라, 좋은 제어가 출력의 분산을 깎아버린 통계적 인공물(regulator paradox)이다. 데이터 엔지니어가 이 함정을 게이트 설계에 반영하지 않으면, 하류의 물리 모델 검증(Tier1/2 캘리브레이션)이 "데이터가 물리를 반증한다"는 잘못된 결론에 도달한다.

이 현상을 다루는 통계적 배경 문헌은 Box, G. and Kramer, T., "Statistical Process Monitoring and Feedback Adjustment: A Discussion," *Technometrics* 34(3), 1992 (DOI: 10.2307/1270028, Crossref로 존재·서지 확인 — **원문은 JSTOR 유료, 미러 사이트 미러(미러 사이트 등) 전부 403으로 미확보**). 이 논문의 구체적 결론을 원문에서 직접 확인하지 못했으므로 이 노트는 그 내용을 인용하지 않고, 제목이 다루는 주제("피드백 조정 하의 통계적 공정 모니터링")만 배경으로 밝힌다 — **2차 인용조차 하지 않음**을 명시.

대신 반도체 R2R 제어의 1차 문헌인 Sachs, E., Hu, A., Ingolfsson, A., "Run by run process control: combining SPC and feedback control," *IEEE Trans. Semiconductor Manufacturing* 8(1), 1995 (DOI: 10.1109/66.350755, OpenAlex 초록으로 확인, 본문은 IEEE 유료·미확보)를 정량 앵커로 쓴다. 초록에 명시된 실측 수치: 실리콘 에피택시 공정(barrel reactor)에 R2R 제어를 적용했을 때 **급변 모드(rapid mode)는 교란 후 3런 안에 공정을 복귀**시켰고, **점진 모드(gradual mode)는 이력 데이터 대비 공정 변동을 2.7배 감소**시켰다. 즉 R2R 제어가 실제로 출력 분산을 큰 폭으로 줄인다는 것 자체가 문헌으로 확인된 사실이며, §1의 시뮬레이션은 "분산이 줄면 상관도 같이 무너진다"는 다음 단계를 코드로 보여준다.

```python verify
import numpy as np
rng = np.random.default_rng(7)

# 폐루프 제어 함정: 물리 게인 g는 동일하게 유지한 채,
# (A) 개루프(랜덤 입력)와 (B) R2R EWMA 피드백 제어(Sachs et al. 1995의
#     "gradual mode" 적분형 보정과 같은 형태)에서 corr(입력,출력)이
#     어떻게 달라지는지 자체 시뮬레이션으로 보인다. 문헌 수치의 재현이 아니라
#     메커니즘 재현이며, 정량 앵커(공정변동 감소폭 2.7배)는 위 Sachs 1995
#     실측치로 별도 제시했다.
n = 300
g = 5.0          # 물리 게인 (연마시간 1min당 제거량 5nm) — 두 시나리오 동일하게 고정
target = 100.0   # 목표 제거량 (nm)
drift = np.cumsum(rng.normal(0, 0.15, n))   # 챔버 시즈닝형 서서히 흐르는 외란
meas_noise = rng.normal(0, 0.3, n)          # 계측 노이즈

# (A) 개루프: 연마시간 X를 랜덤하게 흩뿌려 공정에 인가 (제어 없음)
X_open = rng.normal(target / g, 3.0, n)
Y_open = g * X_open + drift + meas_noise

# (B) 폐루프 R2R: EWMA 적분 제어로 목표를 유지하도록 X를 런마다 보정
lam = 0.3
X_cl = np.zeros(n)
Y_cl = np.zeros(n)
X_cl[0] = target / g
Y_cl[0] = g * X_cl[0] + drift[0] + meas_noise[0]
for t in range(1, n):
    X_cl[t] = X_cl[t - 1] - (lam / g) * (Y_cl[t - 1] - target)
    Y_cl[t] = g * X_cl[t] + drift[t] + meas_noise[t]

r_open = np.corrcoef(X_open, Y_open)[0, 1]
r_cl = np.corrcoef(X_cl, Y_cl)[0, 1]
print(f"open-loop  corr={r_open:.3f} var(Y)={np.var(Y_open):.2f}")
print(f"closed-loop corr={r_cl:.3f} var(Y)={np.var(Y_cl):.2f}")

assert abs(r_open) > 0.8, "개루프에서는 물리 게인이 상관으로 뚜렷이 드러나야 한다"
assert abs(r_cl) < 0.3, "폐루프 R2R 제어 하에서는 같은 게인이 상관에 거의 안 보여야 한다"
# g는 두 시나리오에서 한 번도 바뀌지 않았다 — 상관 붕괴는 통계적 인공물이지 반증이 아니다
```

**게이트 함의**: 데이터 품질 게이트는 "레시피 변수-결과 변수 상관이 낮다"를 자동으로 이상 신호나 물리모델 기각 사유로 채점해선 안 된다. 대신 (1) 해당 변수가 R2R/APC 폐루프 안에 있는지 메타데이터(제어 루프 ID·활성 여부)로 먼저 확인하고, (2) 폐루프 변수는 원시 레시피 값이 아니라 **컨트롤러의 보정항(예: EWMA 상태, 오차 적분)** 을 drift·이상 탐지 대상으로 삼아야 한다 — Sachs 1995의 "gradual mode"가 바로 이 보정항이며, [[synthetic-data-generation-tier1-tier2-noise-model]] §4.4의 drift 패턴(챔버 시즈닝·소모품 소모)이 폐루프 하에서는 원시 출력이 아니라 이 보정항에 나타난다.

## 1. 결측 데이터 게이트 — 완전성(completeness)

레코드가 하류로 흘러가려면 최소한 "무엇이 왜 없는지"가 구분되어야 한다. [[wafer-coordinate-units-outlier-cleaning]] §3.1이 이미 확립한 원칙(EE 밖은 결측이 아니라 정의상 측정 범위 밖)을 웨이퍼 내부 구조뿐 아니라 시계열(SensorTrace)에도 그대로 적용한다.

- **구조적 결측(structural missing)**: 센서가 그 레시피 스텝에서 원래 비활성(예: 슬러리 유량계가 버프 스텝에서는 로그를 안 남김), EE 밖 사이트. → NaN이 아니라 "해당없음(N/A)" 플래그.
- **누락(true missing)**: 통신 장애·타임아웃으로 있어야 할 값이 빠짐. → NaN + 사유 코드(timeout/parse-error/sensor-fault).
- 데이터 결측의 메커니즘 분류(완전무작위결측 MCAR/무작위결측 MAR/비무작위결측 MNAR)는 통계학에서 표준 개념이나, 원 논문(Rubin 1976)은 1990년 이전이라 이 에이전트 스코프에서 제외 대상이다(`tools/scope.py` 확인: 1976 < 1990, 고전 예외 목록에 없음). 대신 후속 리뷰 문헌인 Schafer, J.L., "Multiple imputation: a primer," *Statistical Methods in Medical Research* 8(1), 1999 (DOI: 10.1177/096228029900800102, OpenAlex 초록만 확인 — "최근 수년간 다중대체가 결측값 데이터 분석의 유연한 패러다임으로 자리잡았다"는 요지, 본문 유료 미확보)을 개념 출처로만 남긴다. **이 노트가 제시하는 구체적 완전성 임계값(아래)은 문헌 수치가 아니라 자체 정의이며 미검증이다.**

| 게이트 | 기준(자체 정의, 미검증) | 판정 |
|---|---|---|
| 웨이퍼 단위 완전성 | 필수 사이트의 90% 미만 유효 | reject |
| 트레이스 단위 완전성 | 기대 샘플 수 대비 80% 미만 | reject, 재수집 요청 |
| 구조적 결측 오분류 | N/A를 NaN으로 저장 | reject (Lv1-2 SOURCE 필드 요구사항 위반) |

## 2. 계측 반복성 게이트 — Gauge R&R (SEMI E89)

측정값이 게이트를 통과하려면 **계측 시스템 자체가 그 변별력을 낼 능력이 있는지**부터 확인해야 한다. 1차 표준 근거: **SEMI E89-1104E** "Guide for Measurement System Analysis (MSA)"(북미 지역표준위원회 2004-08-16 승인; store-us.semi.org 원문은 Cloudflare 봉쇄로 완전본 미확보이나, avadocuments.com에 공개된 8쪽 미리보기(섹션 1–8.7 앞부분, "SUPERSEDED" 표기된 구판)에서 용어·정의·핵심 수식을 직접 확인함 — **부분 확보, 최신판 아님을 명시**).

E89가 정의하는 핵심 개념(5.3절):
- **반복성(repeatability, σr)**: 동일 조건(같은 오�레이터·같은 장비·같은 시험 웨이퍼·짧은 시간)에서 반복 측정한 변동.
- **재현성(reproducibility, σR)**: 오퍼레이터·셋업·시간·장비 등 "다른(but 전형적인) 조건"에서 측정한 변동. 서로 독립인 q개 요인이 있으면 분산이 직접 합산된다(E89 Eq.3): $\sigma_R^2=\sigma_1^2+\sigma_2^2+\cdots+\sigma_q^2$.
- **총분산(5.3.40)**: $\sigma_{Total}^2 = \sigma_{Product}^2+\sigma_R^2$ (제품 자체의 변동 + 재현성 제곱).
- **신호대잡음비 SNR(5.3.36, Eq.5)**: $SNR=\sqrt{(\sigma_{Total}^2-\sigma_R^2)/\sigma_R^2}$ — 위 총분산 정의를 대입하면 $SNR=\sigma_{Product}/\sigma_R$과 대수적으로 같다.
- **P/T ratio(정밀도/공차비, 5.3.24)**: 계측 변동을 제품 규격폭과 비교하는 2차 지표. E89 미리보기 구간에는 구체적 합격선(예: AIAG MSA 매뉴얼의 "P/T<0.1 우수/0.1–0.3 조건부/>0.3 불합격" 같은 룰)이 나오지 않았고, 이 수치 자체는 텍스트북(AIAG 매뉴얼) 출처라 이 에이전트 스코프(교과서 금지)에서 애초에 인용 대상이 아니다. **따라서 이 노트는 P/T 정성적 정의만 채택하고 구체적 합격 임계값은 "미검증"으로 비워둔다** — 임계값이 필요하면 게이트 정책은 사내 공정능력(Cp/Cpk) 요구사항에서 별도로 역산해야 한다.

```python verify
import numpy as np
rng = np.random.default_rng(42)

# SEMI E89-1104E 정의식 재현: Eq(3) 재현성 분산분해, 5.3.40 총분산, Eq(5) SNR
sigma_r = 0.50    # repeatability (nm), 가정값 — 문헌은 임계값을 주지 않으므로 예시 수치
sigma_lu = 0.30   # load-unload 재현성 성분 (nm), 가정값
sigma_day = 0.20  # day-to-day 재현성 성분 (nm), 가정값
sigma_R_theory = np.sqrt(sigma_r**2 + sigma_lu**2 + sigma_day**2)  # Eq(3)

# 몬테카를로: 중첩 랜덤효과(day > load-unload > repeat)로 재현성 성분을 실제로
# 합성해, 표본표준편차가 Eq(3) 이론값에 수렴하는지 확인
n_days, n_loads, n_reps = 40, 20, 30
day_eff = rng.normal(0, sigma_day, n_days)
total = []
for d in range(n_days):
    lu_eff = rng.normal(0, sigma_lu, n_loads)
    for l in range(n_loads):
        rep = rng.normal(0, sigma_r, n_reps)
        total.append(day_eff[d] + lu_eff[l] + rep)
total = np.concatenate(total)
sigma_R_mc = np.std(total, ddof=1)

rel_err = abs(sigma_R_mc - sigma_R_theory) / sigma_R_theory
assert rel_err < 0.05, f"MC 재현성 {sigma_R_mc:.4f} vs 문헌식(Eq.3) 이론 {sigma_R_theory:.4f}"
print(f"reproducibility MC={sigma_R_mc:.4f} Eq(3) theory={sigma_R_theory:.4f} rel_err={rel_err:.2%}")

# 5.3.40 총분산·Eq(5) SNR 대수적 항등식 대조
sigma_product = 2.0  # nm, 가정 제품 변동
sigma_Total = np.sqrt(sigma_product**2 + sigma_R_theory**2)          # 5.3.40
SNR = np.sqrt((sigma_Total**2 - sigma_R_theory**2) / sigma_R_theory**2)  # Eq(5)
assert abs(SNR - sigma_product / sigma_R_theory) < 1e-9, "SNR=sigma_Product/sigma_R 항등식 불일치"
print(f"sigma_Total={sigma_Total:.4f} SNR={SNR:.4f} (=sigma_product/sigma_R, 5.3.36+5.3.40 대수적 재현)")
```

**게이트 규칙**: 신규 계측 채널을 ingest 파이프라인에 편입하기 전, E89식 반복성·재현성 추정(위 분산분해)이 없는 채널은 **잠정(provisional)** 등급으로만 통과시키고, Measurement.SOURCE 메타데이터에 `msa_status=provisional`을 강제한다(Lv1-2 §4 SOURCE NOT NULL 원칙의 연장). SNR이 낮다는 것은 "공정이 안정적"이 아니라 "계측기가 제품 변동과 계측 잡음을 구분 못 한다"는 뜻임을 게이트 로직에 명시해야 한다 — 오독하면 §0의 함정과 뒤섞여 "상관이 낮으니 계측을 의심해야 하는데 공정을 의심"하는 반대 오류가 생긴다.

## 3. Drift·이상치 게이트 — Lv2-1/Lv2-2 계승 + 폐루프 보정항 포인트

이상치(spike) 탐지 규칙(MAD, k=2.5, Leys 2013)과 drift(점진적 경향) 탐지가 점별 이상치 탐지로는 안 잡힌다는 사실은 [[wafer-coordinate-units-outlier-cleaning]] §3, [[synthetic-data-generation-tier1-tier2-noise-model]] §4.4에서 이미 문헌 근거(SEMI M1 FQA, Leys et al. 2013 DOI:10.1016/j.jesp.2013.03.013, Moyne & Iskandar 2017 DOI:10.3390/pr5030039)와 함께 확정했으므로 재유도하지 않는다. 이 단원이 추가하는 것은 **§0의 폐루프 함정과 결합했을 때 drift 게이트를 어디에 걸어야 하는가**뿐이다:

- 폐루프 제어가 없는 변수(예: 소모품 누적 사용량 SVID) → drift 탐지는 원시 값에 직접 건다(기존 규칙 그대로).
- 폐루프 제어가 있는 변수(레시피 파라미터·목표추종 출력) → drift 탐지는 원시 출력이 아니라 **컨트롤러 보정항**(EWMA 상태, 목표와의 누적 오차)에 걸어야 한다. 원시 출력에 drift 게이트를 걸면 컨트롤러가 이미 지워버린 신호를 찾는 것이라 항상 "정상"으로 오판정된다 — 이것이 §0 함정의 시계열 버전이다.

## 4. 익명화 규칙 — 고객·장비·로트 식별자 제거

FabSim의 Lv1-2 통합 스키마([[cmp-integration-schema-keys-semi-standards]])는 SubstrateID·LotID·ToolID·ConsumableID를 1급 식별자로 두는데, 이 식별자들을 그대로 외부(형제 에이전트·공개 벤치마크·논문 부록)로 내보내면 특정 고객·특정 장비를 재식별할 수 있다. 익명화는 "이름 지우기"가 아니라 **식별자 조합(quasi-identifier)이 얼마나 좁게 개체를 좁히는가**를 정량으로 관리하는 문제라는 것이 이 절의 핵심이며, 1차 근거는 Sweeney, L., "k-Anonymity: A Model for Protecting Privacy," *International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems* 10(5), 2002, pp.557–570 (DOI: 10.1142/S0218488502001648, dataprivacylab.org에서 저자 자신이 공개한 전문 PDF로 직접 확인).

핵심 정의(논문 Definition 2, 3 원문 확인):
- **준식별자(quasi-identifier, QI)**: 이름·주소처럼 그 자체로 직접식별자는 아니지만, 조합하면 개체를 유일하게 좁히는 속성 집합(Dalenius의 용어를 채택). 논문 예시: {name, address, ZIP, birth date, gender}.
- **k-익명성(Definition 3)**: 테이블 RT가 QI에 대해 k-익명성을 만족한다 ⟺ RT[QI]의 모든 값 조합이 RT 안에서 최소 k번 이상 나타난다.
- **재식별 위험의 실증**: 논문 서론은 1990년 미국 인구총조사 자료로 "{5자리 ZIP, 성별, 생년월일}만으로도 미국 인구의 **87%(2억4800만 명 중 2억1600만 명)**가 사실상 유일하게 식별된다"는 실측 결과를 인용한다(논문 각주 [1]).
- **집행 수단**: 같은 저자의 선행연구 제목이 논문 각주에 그대로 나온다 — "Protecting privacy when disclosing information: k-anonymity and its enforcement through generalization and suppression"(Samarati & Sweeney, 1998) — 즉 k-익명성을 만족시키는 표준 수단은 **일반화(generalization, 예: ZIP 5자리→4자리+`*`)**와 **억제(suppression, 해당 레코드/필드 삭제)** 둘이다.

```python verify
# Sweeney(2002) Figure 2 예시(k=2, QI={Race,Birth,Gender,ZIP})를 그대로 재현해
# 논문이 주장하는 k=2, 그리고 87%(216/248백만) 재식별 위험 수치를 코드로 대조한다.
from collections import Counter

table = [
    ("Black", 1965, "m", "0214*"),  # t1
    ("Black", 1965, "m", "0214*"),  # t2
    ("Black", 1965, "f", "0213*"),  # t3
    ("Black", 1965, "f", "0213*"),  # t4
    ("Black", 1964, "f", "0213*"),  # t5
    ("Black", 1964, "f", "0213*"),  # t6
    ("White", 1964, "m", "0213*"),  # t7
    ("White", 1964, "m", "0213*"),  # t8
    ("White", 1964, "m", "0213*"),  # t9
    ("White", 1967, "m", "0213*"),  # t10
    ("White", 1967, "m", "0213*"),  # t11
]
counts = Counter(table)
k_observed = min(counts.values())
assert k_observed == 2, f"Sweeney Fig.2 예시는 k=2여야 하는데 관측값 {k_observed}"
assert counts[("White", 1964, "m", "0213*")] == 3  # t7=t8=t9, k=2 조건은 '최소'이므로 3중복도 허용
print(f"k-anonymity(observed) = {k_observed}, group sizes = {sorted(counts.values())}")

pct = 216 / 248 * 100  # 1990 US Census, {ZIP5,gender,DOB} 조합 고유식별 비율
assert abs(pct - 87) < 1.0, f"논문 수치 87%와 불일치: {pct:.2f}%"
print(f"{{ZIP5,gender,DOB}} 유일식별 비율 = {pct:.2f}% (논문 값: 87%)")
```

### 4.1 FabSim 스키마에 적용 — 설계 제안(미검증, 도메인 특화 검증 데이터 없음)

Sweeney의 일반 모델을 Lv1-2 스키마에 그대로 적용하면:

| Lv1-2 필드 | 위험 유형 | 처리 |
|---|---|---|
| SubstrateID, LotID | 직접식별자(고객이 자기 로트번호로 역추적 가능) | 억제 + 세션별 해시 대체(원본은 사내에만 보존) |
| ToolID | 준식별자(특정 고객이 특정 장비군만 쓰는 경우 장비ID가 곧 고객 식별) | 일반화: 장비 모델 클래스로 대체(예: `ToolID=FAB3-CMP-07` → `ToolClass=RotaryA`) |
| ProcessEvent 타임스탬프 | 준식별자(외부에 공개된 생산 일정과 결합 시 재식별) | 일반화: 절대시각 → 상대시각(공정 시작 기준) 또는 날짜→주 단위 |
| (ToolID, RecipeID, Shift) 조합 | 준식별자 조합(§4 정의 그대로 적용) | 배포 전 위 3.1의 verify 코드와 동일한 방식으로 그룹 크기 최소값 k를 계산해, k < 임계값(자체 정의, 예: k≥5)이면 해당 조합을 억제 또는 상위 카테고리로 일반화 |

**이 표의 임계값(k≥5)은 문헌에서 온 것이 아니라 이 노트가 제안하는 초안이며 미검증이다** — 실제 운용 시 형제 에이전트가 필요로 하는 통계적 검정력과 재식별 위험을 저울질해 총괄(ORG.md)이 확정해야 한다.

## 5. 스코프 밖에서 제외한 문헌 (명시)

- SEMI E89 표준 원문 전체(최신판) — store-us.semi.org Cloudflare 봉쇄로 미확보. 이 노트는 구판(2004) 미리보기 8쪽만 확보했음을 §2에서 이미 명시.
- AIAG MSA 매뉴얼의 %GRR/P/T 합격 임계값(10%/30% 룰 등) — 교과서·업계 매뉴얼 출처로 이 에이전트 스코프(교과서 금지)에서 원천 제외. 대체 임계값을 문헌으로 못 박지 못했으므로 §2 P/T 임계값은 공란.
- Rubin(1976) MCAR/MAR/MNAR 원 논문 — 1990년 이전, 고전 예외 목록에 없어 `tools/scope.py`가 거부.
- Box & Kramer(1992) 원문 — DOI만 확인, JSTOR 유료·미러 사이트 미러 전부 403으로 본문 미확보. §0에서 내용을 인용하지 않고 존재만 명시.

## 6. 요약 — ingest 게이트 체크리스트

1. **완전성**: N/A(구조적) vs NaN(누락) 구분 저장 여부.
2. **계측 반복성**: 채널에 E89식 반복성·재현성 추정이 있는가(없으면 provisional).
3. **이상치**: MAD(k=2.5) 플래그가 원값 보존 방식으로 붙어 있는가([[wafer-coordinate-units-outlier-cleaning]] 계승).
4. **drift**: 폐루프 변수는 원시값이 아니라 컨트롤러 보정항에 걸려 있는가(§3).
5. **폐루프 함정 점검**: 레시피-결과 상관이 낮다는 사실 하나만으로 물리모델을 기각하지 않는가(§0) — 제어 루프 메타데이터 확인이 선행되어야 한다.
6. **익명화**: 외부 반출 전 (ToolID,RecipeID,Shift) 등 준식별자 조합의 k값이 임계 이상인가(§4).
