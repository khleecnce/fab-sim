<!-- V2-SECTION: R2-slurry | 정확도루프 C1(죽은 축) sic_ceria_h2o2 χ 산화제항 2026-09-16 -->
# 알칼리 SiC CMP에서 H2O2 농도 → MRR — 촉진-포화형(Langmuir) 배선과 그 상한

> slurry-chemist Lv3-2 확장 | 작성일: 2026-09-16
> 선행: [[sic-alumina-concentration-negative-exponent-entegris]] (같은 팩 κ 농도항)
> [[w-cmp-wo3-passivation-oxidizer-kaufman]] (산화제 단봉형의 원형)
> 스코프: slurry-chemist(화학 첨가제 축). 팩 `sic_ceria_h2o2` / `sic_alumina_kmno4`.

## 1. 왜 이 단원인가 — 축이 죽어 있었다

`sim/factors.py`(L1303~1311)가 매 실행 경고를 내고 있었다:

> ⚠ 산화제 농도(oxidizer_wt_pct/oxidizer_ref_wt_pct)가 팩에 선언돼 있으나
> 형상 파라미터(oxidizer_langmuir_K/oxidizer_passivation_K/oxidizer_peak_wt_pct)가
> 하나도 없어 χ가 산화제 변화에 조용히 무반응

즉 `sic_ceria_h2o2` 팩에서 **H2O2 농도를 2 → 6 으로 바꿔도 예측 MRR이 한 자리도
움직이지 않았다.** 이 팩의 근거 DOE(50조건)에서 H2O2는 실측 인자 순위 5위
(ρ=+0.221)로 살아 있는 축인데 모델에는 없었다 — 미모델링이 아니라 **배선 누락**이다.

## 2. 1차 출처

1. **Wei M. et al., "Influences of Polishing Slurry Components on Material Removal and
   Surface Morphology of 4H-SiC C-Face Based on Fenton Reaction CMP", Crystals 16 (2026) 179,
   DOI 10.3390/cryst16030179** (오픈액세스, `papers/wei2026-cryst16030179-4hsic-fenton-cmp.pdf`).
   4H-SiC C면, 콜로이달 실리카 110 nm 8 wt% + Fe3O4 0.03 wt%, pH 9, 34.5 kPa, 50/50 rpm.
   H2O2 0/2.5/5/7.5/10 wt% 스윕에서 **5 wt%에서 MRR 최대 701 nm/h**, 그 위는 ·OH 소광
   (2·OH → H2O2, ·OH + H2O2 → H2O + ·OOH)으로 감소. §3.3 본문 인쇄값.
2. **Wang et al., figshare:31056549 (ACS SI Table S3)** — 이 팩의 근거 50조건 완전 DOE
   (CeO2 2/4/6 wt% × H2O2 2/4/6 vol% × pH 9/10/11 × 압력·rpm).
   이미 `validation/datasets/sic2026_ceria_h2o2_ph_DOE50.yaml` 로 등록돼 있고
   `used_for_calibration: true` 다.

## 3. 형상 선택 — 왜 단봉(Kaufman)이 아니라 촉진-포화(Langmuir)인가

Wei 2026은 정점(5 wt%)과 그 위의 감소를 명확히 보여준다. 그러나 **이 팩의 운전 구간은
2~6 vol% 이고 기준은 4 vol%** 다. 두 문헌의 농도 단위가 다르다(wt% vs vol%) —
H2O2 30 % 수용액 기준 vol%↔wt% 는 밀도차로 약 1.1배 어긋난다(이 팩의
`oxidizer_ref_wt_pct` note 에 이미 기록된 사실). **정점 위치는 절대 농도량이므로
단위를 건너 옮기면 안 된다** → Wei 의 5 wt% 를 `oxidizer_peak_wt_pct` 로 그대로
넣는 것은 단위 전이 오류가 된다. 그래서 정점형을 채택하지 않는다.

대신 **같은 계·같은 단위**의 DOE 쌍(H2O2 만 다르고 CeO2·pH·압력·rpm 이 모두 같은
18쌍)에서 촉진-포화형 Langmuir 의 K 하나만 적합한다. 폐형식은 코드와 동일하다:

    f(C) = φ + (1-φ)·θ(C)/θ(C_ref),  θ(C)=K·C/(1+K·C),  φ=0.15(기계 하한 기본값)

```python verify
import itertools, math, statistics as st
import numpy as np, yaml
from scipy.optimize import least_squares

d = yaml.safe_load(open('validation/datasets/sic2026_ceria_h2o2_ph_DOE50.yaml', encoding='utf-8'))
rows = [(c['overrides']['abrasive_wt_pct'], c['overrides']['oxidizer_wt_pct'],
         c['overrides']['slurry_ph'], c['pressure_psi'], c['rpm_platen'],
         c['rpm_wafer'], c['mrr_nm_per_min']) for c in d['conditions']]

# H2O2 만 다른 쌍 (나머지 5개 조건 완전 일치)
pairs = []
for a, b in itertools.combinations(rows, 2):
    if a[0] == b[0] and a[2] == b[2] and a[3] == b[3] and a[4] == b[4] and a[5] == b[5] and a[1] != b[1]:
        lo, hi = (a, b) if a[1] < b[1] else (b, a)
        pairs.append((lo[1], hi[1], hi[6] / lo[6]))
assert len(pairs) == 18, f"쌍 수가 18이 아니다: {len(pairs)}"

phi, Cref = 0.15, 4.0
def f(C, K):
    th = lambda c: K * c / (1 + K * c)
    return phi + (1 - phi) * th(C) / th(Cref)

def resid(k):
    K = k[0]
    return [math.log(f(hi, K) / f(lo, K)) - math.log(r) for lo, hi, r in pairs]

K = float(least_squares(resid, [1.0], bounds=([1e-3], [1e4])).x[0])
print(f"적합 K = {K:.4f} L/vol%")
assert abs(K - 0.7600) < 0.01, f"팩에 넣은 K=0.76 과 재적합값이 다르다: {K:.4f}"

# ① 기준 조건 1.0 계약 (Kp 이중 계상 방지)
assert abs(f(Cref, K) - 1.0) < 1e-12

# ② 관측 방향: 2 -> 4 -> 6 단조 증가 (중앙값 기준)
for lohi in [(2, 4), (4, 6), (2, 6)]:
    obs = st.median([r for lo, hi, r in pairs if (lo, hi) == lohi])
    pred = f(lohi[1], K) / f(lohi[0], K)
    print(f"{lohi}: 실측 중앙값 {obs:.3f} vs 예측 {pred:.3f}")
    assert obs > 1.0 and pred > 1.0, f"{lohi} 에서 방향이 어긋난다"
    assert abs(pred / obs - 1) < 0.12, f"{lohi} 예측/실측 편차 12% 초과"

# ③ 산포는 크다 — 숨기지 않고 assert 로 박아 둔다
r = np.array(resid([K]))
rms = float(np.sqrt((r ** 2).mean()))
print(f"로그 잔차 rms = {rms:.4f} (= {100*(math.exp(rms)-1):.1f} %)")
assert 0.25 < rms < 0.30, "잔차 크기가 기록(0.2724)과 다르다"

# ④ Wei 2026 의 정점(5 wt%)은 이 구간(2~6 vol%)의 위쪽 경계 근처다 —
#    6 vol% 이상으로 외삽하면 소광으로 실제는 꺾인다. 모델은 계속 오르므로 상한 선언.
print("범위 상한 6 vol%: 그 위는 Wei 2026 §3.3 의 ·OH 소광 구간 — 이 항으로 외삽 금지")
```

실행값(2026-09-16): K=0.7600, 기준 1.0 계약 성립, (2,4) 실측 1.096 vs 예측 1.203,
(4,6) 1.127 vs 1.076, (2,6) 1.209 vs 1.295, 로그 잔차 rms 0.2724(=31.3 %).

## 4. 불확실성 — 정직하게

- **K 는 약하게만 결정된다.** 18쌍 부트스트랩(400회) 2.5/50/97.5 백분위 =
  **0.320 / 0.797 / 2.697**. 즉 한 자릿수 안에서만 고정된다. `confidence: estimated`.
- 잔차 31 %는 크다. 같은 (2→4) 쌍에서도 실측 비가 0.911 ~ 2.431 로 흩어진다 —
  DOE 에 펌프유량·연마시간(논문 PCA에서 H2O2 보다 강한 인자)이 섞여 있고 엔진이
  그 둘을 모델링하지 않기 때문이다(팩 헤더에 이미 기록된 한계).
- **Wei 2026 은 형상의 방향과 상한만 지지한다.** 연마입자가 실리카(세리아 아님)이고
  Fe3O4 촉매가 있어 K 값 자체를 옮겨올 수 없다 — 값은 이 팩 자신의 DOE 에서 왔다.
- 이 항은 **캘리브레이션 데이터에서 나왔다.** 같은 DOE 로 다시 채점하면 자기 답안지
  채점이다. held-out 개선 주장에 쓰지 않는다.

## 5. 새로 도출한 지식 — 팩 반영

- `knowledge/params/sic_ceria_h2o2.yaml` 에 `oxidizer_langmuir_K: 0.76`
  (unit `1/vol%`, confidence `estimated`, 근거=이 노트) 신설.
  → `sim/chemistry.py::_oxidizer_term` 의 촉진-포화 경로가 켜지고, χ 의 산화제 축이
  살아난다(기준 4 vol% 에서 배수 1.0 유지 — κ·Kp 이중 계상 없음).
- `sic_alumina_kmno4` 는 **상속시키지 않는다.** 산화제가 KMnO4 (E°(MnO4⁻/MnO2)=+1.68 V)
  로 H2O2 와 다른 종이고 단위도 wt% 다. 그 팩의 경고는 남겨 둔다 — 지어내지 않는 쪽이
  맞다(같은 파일 note 에 이미 "H2O2 형상을 전용하지 마라" 라고 적혀 있다).

## 6. 적용 범위

| 항목 | 범위 |
|---|---|
| 막질 | 4H-SiC (C면 기준; Si면은 MRR 이 자리수로 낮다 — Wei 2026 §1) |
| 산화제 | H2O2 **2~6 vol%** (기준 4) |
| pH | 9~11 (알칼리) |
| 금지 | 6 vol% 초과 외삽(소광 구간), 다른 산화제 종으로 K 전이, wt%↔vol% 무환산 이식 |

## 7. 문헌값 대조 · 미검증 항목 정리

**정량 재현(문헌값 대조).** Wei 2026(https://doi.org/10.3390/cryst16030179) §3.3 은
H2O2 를 0 → 5 wt% 로 올릴 때 MRR 이 최대 **701 nm/h** 까지 오른다고 인쇄한다. 이 노트의
Langmuir 항을 같은 방향으로 검증한 결과는 아래 두 줄이며, 실측값의 출처는 전부
[[validation/datasets/sic2026_ceria_h2o2_ph_DOE50]](figshare:31056549, ACS SI Table S3)의
18쌍이고 §3 verify 블록 ②의 assert 가 매번 재실행해 확인한다:

- 기준 4 vol% 대비 **6 vol%**: 예측 배수 1.076 vs 실측 중앙값 1.127 — 차이 4.5 %
  (figshare:31056549 SI Table S3)
- 기준 4 vol% 대비 **2 vol%**: 예측 0.831 vs 실측 역수 0.912 — 차이 8.9 %
  (figshare:31056549 SI Table S3)

둘 다 §3 verify 블록 ②가 박아 둔 상한 12 % 안에 든다. 절대 MRR 로 환산하면 이 팩의
기준 조건 예측 3.31 nm/min(=198.5 nm/h)이고, Wei 의 701 nm/h 와는 계가 다르므로
(연마입자 실리카·Fe3O4 촉매·34.5 kPa) **절대값 대조는 하지 않는다**.

**미검증으로 남기는 것.**
- K=0.76 의 신뢰구간이 0.32~2.70(부트스트랩 400회)으로 넓다 — 값은 **추정**이며 한
  자릿수 수준에서만 의미가 있다. confidence 는 `estimated` 로 둔다.
- Langmuir 함수형 자체가 이 계에서 옳다는 1차 근거는 **확인 못 했다**. 18쌍이 지지하는
  것은 "2→6 vol% 구간에서 단조 증가하고 기울기가 완만해진다"까지다.
- Wei 2026 의 5 wt% 정점을 이 팩의 vol% 축으로 옮긴 값은 **미검증**이라 쓰지 않았다.
- 펌프유량·연마시간(DOE 에서 H2O2 보다 강한 인자)은 엔진에 없다 — 잔차 31 % 의 상당
  부분이 여기서 온다는 것은 **추정**이고 분해해 확인하지 못했다.

## 8. 독립 held-out 대조 (2026-09-16 추가) — 승격 시도와 그 결과

§3 의 K=0.7600 은 **이 팩의 캘리브레이션 데이터**(figshare:31056549, `used_for_calibration: true`)
에서 나왔다. 그래서 판정#50 은 confidence 를 `estimated` 로 고정했다. 이번 회차의 과제는
완성 격자에 마지막으로 남은 C2 칸(χ/sic_ceria_h2o2)을 **캘리브레이션 밖 1차 출처**로
승격시킬 수 있는가였다.

### 8.1 확보한 독립 관측 — Liang et al. 2026 의 H2O2 매칭쌍

Liang, Juan; Zhang, Yan; et al., "Chemical mechanical polishing on silicon carbide using
developed ceria composite abrasives and their synergistic polishing mechanism",
Nano Research (2026), **doi:10.26599/NR.2026.94909100** (Tsinghua Univ. Press, CC-BY,
출판사 PDF 확보: `papers/nr2026-ceria-composite-abrasive-sic-cmp.pdf`, 49 p).

§2.3 **본문 인쇄값**에 H2O2 만 다르고 나머지(연마입자 5 wt%, pH 7, 30 kPa, 90 rpm,
60 min)가 전부 같은 쌍이 하나 있다 — 그래프 판독이 아니다:

| H2O2 | MRR(인쇄값) | 비 |
|---|---|---|
| 8 wt% | 538.45 nm/h | — |
| 10 wt% | 570.76 nm/h | **1.0600** |

이 논문은 이 팩의 **어떤 파라미터에도 쓰이지 않았다**(팩 출처는 Wang figshare / Chen2017 /
Singh2007 / Oh2010 / Kim2024 뿐). 데이터셋 `liang2026_4hsic_ceria_composite_h2o2_conc.yaml`
로 이미 등록돼 있고 `used_for_calibration: false` 다.

### 8.2 대조 결과

```python verify
# Liang 2026 §2.3 인쇄값 vs 판정#50 의 Langmuir 항 (K=0.76, phi=0.15, C_ref=4)
phi, Cref = 0.15, 4.0
def f(C, K):
    th = lambda c: K * c / (1.0 + K * c)
    return phi + (1.0 - phi) * th(C) / th(Cref)

K = 0.7600
MRR_8, MRR_10 = 538.45, 570.76          # nm/h, doi:10.26599/NR.2026.94909100 §2.3
obs = MRR_10 / MRR_8
assert abs(obs - 1.0600) < 1e-3, obs

pred = f(10.0, K) / f(8.0, K)
assert abs(pred - 1.0252) < 1e-3, pred
# 방향은 맞다(둘 다 >1)
assert pred > 1.0 and obs > 1.0
# 크기는 3.3% 과소예측 — 숨기지 않고 박아 둔다
dev = pred / obs - 1.0
assert -0.05 < dev < 0.0, dev

# 이 한 쌍만으로 K 를 역산하면?
import math
lo, hi = 1e-4, 1e4
for _ in range(200):
    m = math.sqrt(lo * hi)
    if f(10.0, m) / f(8.0, m) > obs: lo = m
    else: hi = m
K_req = math.sqrt(lo * hi)
assert abs(K_req - 0.2675) < 1e-3, K_req
# 판정#50 의 부트스트랩 95% 구간은 0.320~2.697 — 역산값은 그 **아래**에 있다
assert K_req < 0.320
```

**읽는 법.** 배수 자체는 −3.3 % 로 잘 맞는다. 그러나 이 구간(8→10 wt%)은 Langmuir 가
거의 포화한 평탄 구간이라 **배수가 K 에 둔감**하다: K 를 부트스트랩 구간 양 끝으로
흔들어도 예측비는 1.0523(K=0.32) ~ 1.0076(K=2.70)에서만 움직인다. 즉 이 한 쌍은
"방향과 자릿수가 맞다"는 확인은 되지만 **K 값을 식별하지 못한다**. 게다가 이 쌍이
요구하는 K=0.2675 는 부트스트랩 구간 밖(아래)이다 — 지지라기보다 "더 급한 포화"를
가리킨다.

### 8.3 계 불일치 — 이식하지 않는 이유

- 연마입자가 순수 세리아가 아니라 **CuxO-CeO2/Al2O3 복합**(질량 대부분이 알루미나,
  Table S2: Cu 1.09 wt%·Ce 1.03 wt%)이다.
- **pH 7 중성**이다(이 팩 기준은 pH 10 알칼리).
- **CuxO Fenton-유사 촉매**가 H2O2 를 ·OH 로 분해한다 — 이 팩에 없는 기전이고,
  판정#50 이 Wei 2026(Fe3O4 촉매)의 단봉형을 이 팩에 안 가져온 것과 같은 이유다.
- 농도축이 8~10 wt% 로, §6 이 선언한 **외삽 금지 구간(6 vol% 초과)** 안에 있다.

EVIDENCE-RULES 서열로 **E4(타계 전이 유도)** 다. §3 의 적합 데이터가 E2(대상계·교란
5축 통제)이므로 E4 가 E2 를 밀어낼 수 없다.

### 8.4 판정

**승격 기각 — `confidence: estimated` 유지, 값 0.7600 불변, 코드·팩 미변경.**

C2 는 "1차 출처로 값을 대조해 승격"을 요구하는데, 이번에 확보한 유일한 캘리브레이션 밖
1차 출처는 (a) 계가 다르고(E4) (b) 그 구간에서 K 를 식별하지 못한다. 근거 없이 등급만
올리는 것은 이 저장소가 판정#24A·#28·#32 에서 반복해 거부해 온 행위다.

**null 도 결론이다**(EVIDENCE-RULES §4): 이 회차가 확인한 것은 "K 를 못 올린다"가 아니라
**"K 를 올리려면 알칼리·무촉매·순수 세리아 계의 H2O2 1축 스윕이 필요하고, 그 문헌은
현재 코퍼스(전문 1,527건)와 웹 접근 범위에 없다"** 이다. 코퍼스 전수 스캔(SiC+세리아
+H2O2+MRR 교집합) 결과 후보 0건, SiC+H2O2 5건은 전부 몰리브덴·GaN·Fe 촉매계였다.

**재개 조건**: (i) 알칼리 pH 9~11 · 무촉매 · 세리아 연마입자로 H2O2 농도만 3점 이상
스윕한 문헌, 또는 (ii) Liang Fig.3(i) 의 4/6/12 wt% 세 점을 **인쇄 수치로** 제공하는
ESM 표(현재는 그래프만 있어 판독값을 만들지 않았다). 3회차 규칙의 **1회차**다.
