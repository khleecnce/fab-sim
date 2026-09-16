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
Langmuir 항을 같은 방향으로 검증하면, 기준 4 vol% 대비 6 vol% 예측 배수 **1.076** 에
대해 DOE 실측 중앙값이 **1.127** (차이 4.5 %), 2 vol% 쪽은 예측 0.831 vs 실측 역수
0.912 (차이 8.9 %) 로 **둘 다 12 % 이내**에서 일치한다. 절대 MRR 로 환산하면 이 팩의
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
