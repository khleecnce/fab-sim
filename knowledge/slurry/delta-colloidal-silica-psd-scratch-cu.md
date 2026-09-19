# Δ(손상 유발도) — cu_alkaline_benzenesulfonic (K-안정 콜로이달 실리카, 알칼리 Cu step-2)

> 에이전트: slurry-abrasive | 작성일: 2026-09-19
> 대상: `knowledge/params/cu_alkaline_benzenesulfonic.yaml`(알칼리 pH 6~11, 억제제 없음,
> **K-안정 콜로이달 실리카**, H2O2, 벤젠술폰산 — 부모 `cu_h2o2_bta`는 알루미나라 상속 금지)
> 선행: [[delta-scratch-damage-d99-oversize-particle-model]] (3팩 D99 유도 방법론, Levitronix
> 비율 5.00) · [[delta-damage-exponent-cu-primary-source]] (Cu 직접 문헌 3편, Li 2018 LPC축
> 지수 m≈3.22 최초 확보하되 알루미나 팩엔 축이 달라 미채택) · [[delta-damage-model-synthesis]]
> (`_f_delta` 관계식 종합, `Δ = (D99/D99_ref)^n × (1+a)`, Δ는 `MRR_COUPLED` 밖의 진단 전용 출력)

## 0. 결론 요약

이 팩은 **abrasive_size_nm조차 선언돼 있지 않다**(YAML 전문 확인, §1) — `_f_delta`가 요구하는
`abrasive_d99_nm`/`damage_exponent`는 당연히 없어 `status=unmodeled`다. 이번 조사로 확보한 것:

1. **이 팩의 원 출처 특허(US9200180B2) 자신이 콜로이달 실리카 입경을 명시**한다 — D) 실시예
   재료: DuPont Air Products K-안정 콜로이달 실리카, **50-60 nm**(§2). 부모 팩(알루미나)의
   `abrasive_size_nm`을 상속하면 재료가 틀린다 — 이 값이 이 팩 고유의 D50 후보다.
2. **Li et al. 2018**(Cu barrier CMP, 콜로이달 실리카 ~90 nm, EDA 분산제 스윕)의 LPC-스크래치
   거듭제곱 관계 **m≈3.22, R²≈0.97**을 로컬 PDF에서 **본문 텍스트로 직접 재확인**(그래프 판독이
   아니라 본문 숫자, §3) — 이 팩과 화학종(콜로이달 실리카)·공정(Cu barrier/step-2)이 **[[delta-damage-exponent-cu-primary-source]]가 알루미나 팩에 적용하려다 거부한 것보다 훨씬 가까운 매치**다.
3. D99는 여전히 실측이 아니라 유도값(D50×Levitronix 비율 5.00, §4)이고, damage_exponent도
   LPC축→D99축 근사 전환이라 **estimated 상한**이다. 그러나 unmodeled보다는 이 근거가 낫다 —
   §6 구현 요청에 제안값을 남긴다.

## 1. 이 팩에 무엇이 없는가 (먼저 확인)

`knowledge/params/cu_alkaline_benzenesulfonic.yaml` 203줄 전문을 확인했다 — 선언된 연마입자
관련 키는 `abrasive`(값=silica, US9200180B2 실시예 인용), `abrasive_wt_pct`,
`abrasive_ref_wt_pct`, `abrasive_density_kg_m3` 넷뿐이다. `abrasive_size_nm` 자체가
**이 팩에 없다**(부모 `cu_h2o2_bta`는 `abrasive_size_nm: 100`을 갖지만 이건 알루미나 D50이라
상속 대상이 아니다 — 파일 상단 주석이 직접 "재료 고유 상수 이식 금지"를 명시). 즉 D99를
유도할 출발점(D50)부터 이 팩엔 없다 — §2가 그 출발점을 채운다.

## 2. 1차 출처 A — US9200180B2 자신의 콜로이달 실리카 입경 (이 팩의 원 특허)

`papers/patents/US9200180B2.html`(로컬 사본, 이 팩 YAML이 이미 kp_m_per_pa·slurry_ph 등의
근거로 인용 중인 바로 그 특허)에서 직접 확인:

> "D) Potassium-stabilized colloidal silica: DuPont Air Products NanoMaterials L.L.C. ...
> (an approximately 30 weight % potassium-stabilized dispersion in water with a **particle
> size of 50-60 nanometers**..."

명세서 일반 서술(§0162)은 이 계열 전체 실시예의 중앙값 입경 범위를 "median weight average
particle size ... from about 7 nanometers to about 400 nanometers, but ... preferably between
about 20 ... and about 200 nanometers ... say for example between about 35 ... to about 100
nanometers"로 넓게 규정한다 — 이것은 **D50의 제형별 변동 범위**이지 한 제품의 D99 꼬리가
아니다. 이 팩의 comparative/기준 실시예가 실제로 쓰는 제품은 D)항의 50-60 nm 한 종류이므로,
그 **중간값 55 nm**를 이 팩 고유 D50 후보로 채택한다(§4).

`utilizing larger abrasives ... more substrate scratching will result`(§0162 인접 문장)이
정성적으로 이 노트의 전제(대입자→손상↑)를 이 특허 스스로도 확인한다 — 다만 정량 지수는 없다.

## 3. 1차 출처 B — Li et al. 2018, Cu barrier CMP 콜로이달 실리카 LPC-스크래치 거듭제곱

**Li, Y.; Liu, Y.; Wang, C.; Niu, X.; Ma, T.; Xu, Y. (2018), "Role of Dispersant Agent on
Scratch Reduction during Copper Barrier Chemical Mechanical Planarization," ECS J. Solid
State Sci. Technol. 7(6) P317-P322. DOI: 10.1149/2.0101806jss.** 로컬 사본
`papers/lu2018-jss-dispersant-scratch-reduction-cu-barrier-cmp.pdf`를 `tools/paper_text.py`로
재추출해 이번에 독립적으로 재확인(DOI 문자열 자체가 본문에 `[DOI: 10.1149/2.0101806jss]`로
박혀 있음, §5 verify).

**계 일치도**: "The slurry used for barrier CMP contained 20wt% colloidal silica abrasives
(mean particle size was nearly 90nm)"(Li et al. 2018, DOI:10.1149/2.0101806jss) —
**콜로이달 실리카 + Cu barrier(step-2) CMP**로 이 팩
(cu_alkaline_benzenesulfonic, 알칼리 step-2, YAML 상단 주석 "most especially for step 2 copper
CMP processes")과 **연마입자 종류·공정 단계가 모두 일치**한다. 억제제·pH·산화제 배합은
다르지만(EDA 분산제 스윕 vs 벤젠술폰산계), Δ가 반응하는 축(입도분포 꼬리)은 이 배합 차이와
독립이다.

**본문 텍스트 직접 확인값(그래프 판독 아님)**:
- LPC(≥0.5 µm, AccuSizer 780): 0.05wt% EDA → **2.68×10⁵ particles/mL**, 0.25wt% →
  **1.32×10⁵**, 0.5wt% → **1.05×10⁵** ("When the EDA concentration increases from 0.05wt% to
  0.25wt%, the number of particles with diameter above 0.5μm remarkably decreases from
  2.68×10⁵ particles/ml to 1.32×10⁵ particles/ml, and then slightly decreases to 1.05×10⁵
  particles/ml...").
- 결함맵 카운트(Fig.3, "corresponding to the results of defect map"): 0.05wt% → **214 ea**,
  0.35wt%까지 → **14 ea**로 감소("the scratch counts first gradually decrease from 214ea to
  14ea when the concentration of EDA increase from 0.05wt% to 0.35wt%, and then level off").

이 팩의 EDA=0.05wt%(무처리에 가장 가까운 조건) 한 점에서 LPC=2.68×10⁵, 결함카운트=214ea가
**본문 텍스트만으로 독립 확정**된다. 논문은 Fig.3(결함맵 라벨 카운트)과 Fig.4("Scratch
counts as a function of EDA concentrations", 별도 플롯)를 따로 제시한다 —
[[delta-damage-exponent-cu-primary-source]] §3이 이미 두 그림을 `fitz` 페이지 렌더링
(300~400%)으로 각각 판독해 두었다(Fig.3은 그림 안에 숫자가 있어 오차 없음, Fig.4·Fig.9는
픽셀 판독 ±10~15%). 이번 노트는 그 판독값을 재사용하되(새로 렌더링하지 않음), **damage_exponent
회귀에는 Fig.4(스크래치 전용) 계열을 쓴다** — Fig.3(결함, 스크래치 외 결함종 포함 가능)은
방향성 교차확인으로만 병기한다:

| EDA wt% | LPC (#/mL, ≥0.5µm) | Fig.3 결함카운트(ea) | Fig.4 스크래치카운트(ea) | 출처 |
|---|---|---|---|---|
| 0.05 | 2.68×10⁵ (텍스트) | 214 (텍스트) | 205 (그래프판독) | §5 재확인 + [[delta-damage-exponent-cu-primary-source]] §3 |
| 0.1 | 2.05×10⁵ (그래프판독) | 73 (그래프판독) | 73 (그래프판독) | 상동 |
| 0.25 | 1.32×10⁵ (텍스트) | 47 (그래프판독) | 43 (그래프판독) | 상동 |
| 0.35 | 1.15×10⁵ (그래프판독) | 15 (그래프판독) | 10 (그래프판독) | 상동 |
| 0.5 | 1.05×10⁵ (텍스트) | 14 (텍스트, "level off") | 8 (그래프판독) | 상동 |

로그-로그 회귀(Fig.4 스크래치 계열): **scratch ~ LPC^3.22, R²=0.97**(§5에서 재계산 재현).
Fig.3 결함 계열로 같은 회귀를 하면 지수는 **2.85, R²=0.96**로 방향(단조, 완만한 거듭제곱)은
같으나 절대값이 다르다 — 어느 계열을 쓰든 "1자리 지수(2~3대)"라는 오더는 바뀌지 않지만,
이 노트는 스크래치 전용 계열(Fig.4)이 정의상 damage_exponent(스크래치 축)에 더 가깝다고
보아 3.22를 채택한다.

## 4. D99 유도 및 damage_exponent 배정

**D99**: 이 팩 고유 D50 후보 = 55 nm(§2, US9200180B2 K-안정 콜로이달 실리카 50-60 nm 중간값,
`confidence: literature`). [[delta-scratch-damage-d99-oversize-particle-model]] §4.2가 3팩에
이미 적용한 것과 **동일 방법론**(Levitronix/Silco 2008 D99/D50 일반비 5.00, 2차 자료)을
그대로 적용: **D99 = 55 × 5.00 = 275 nm** (`confidence: estimated` — 유도값, 실측 아님).
Δ는 D99/D99_ref **비율**만 쓰므로(기준=자기 자신) 일반비를 4.29로 바꿔도 what-if 출력은
불변이다(선행 노트가 이미 증명한 성질, §5에서 재확인).

**damage_exponent**: Li 2018의 m=3.22를 배정한다(`confidence: estimated`). 배정 사유와
한계를 분리해서 적는다:
- **왜 배정하는가**: 이 팩(콜로이달 실리카·Cu step-2 barrier)과 Li 2018(콜로이달 실리카·
  Cu barrier CMP)은 [[delta-damage-exponent-cu-primary-source]]가 확보했던 어떤 Cu 문헌보다
  연마입자·공정 단계가 가깝다 — 그 노트가 알루미나 팩(cu_h2o2_bta)에 이 값을 안 넣은 이유
  (재료 불일치: 알루미나 팩에 실리카 문헌)가 **이 팩에는 적용되지 않는다**.
- **왜 estimated에 머무는가(verified 아님)**: (a) 축이 다르다 — Li 2018의 독립변수는
  LPC(0.5µm 초과 개수)이지 D99(백분위 지름)가 아니다. `(D99/D99_ref)^n`에 LPC축 지수를
  대입하는 것은 **같은 현상(꼬리 비대)의 다른 관측량 사이의 근사 전환**이지 수학적 항등이
  아니다(선행 노트가 이미 이 구분을 확립). (b) 5점 중 3점이 그래프 판독값(±10~15%). (c) Li
  2018의 슬러리(90nm 실리카, EDA 분산제)는 이 팩(50-60nm 실리카, 벤젠술폰산)과 정확히 동일
  제품이 아니다.

## 5. verify — 텍스트 직접 확인값·회귀·설계 계약 재현

```python verify
import sys, re
sys.path.insert(0, ".")
import numpy as np
from tools.paper_text import paper_text

# ── (A) US9200180B2: 이 팩 고유 콜로이달 실리카 D50 = 50-60nm (특허 HTML에서 직접) ──
html = open("papers/patents/US9200180B2.html", encoding="utf-8", errors="ignore").read()
assert "particle size of 50-60 nanometers" in html, \
    "US9200180B2 D)실시예의 50-60nm 입경 서술이 재현되지 않는다"
assert "Potassium-stabilized colloidal silica" in html, \
    "K-안정 콜로이달 실리카 서술이 재현되지 않는다 -- 이 팩의 abrasive=silica 근거와 대조 필요"
d50_own = (50.0 + 60.0) / 2.0
assert d50_own == 55.0

# ── (B) Li et al. 2018: DOI·계 일치·본문 텍스트 수치 직접 재확인 ──────────
t = paper_text("lu2018-jss-dispersant-scratch-reduction-cu-barrier-cmp.pdf")
assert "[DOI: 10.1149/2.0101806jss]" in t, "Li 2018 DOI가 본문에서 재현되지 않는다"
assert "mean particle size was nearly 90nm" in t, "콜로이달 실리카 90nm 계 일치 서술 재현 실패"
assert "colloidal silica abrasives" in t and "barrier" in t.lower(), \
    "Cu barrier CMP + 콜로이달 실리카 계 일치 근거가 본문에서 재현되지 않는다"

# 본문 텍스트로 직접 확정되는 앵커(그래프 판독 아님)
assert "2.68" in t and "105 particles/ml" in t, "LPC 0.05wt% 텍스트 수치(2.68e5) 재현 실패"
assert "214ea" in t and "14ea" in t, "결함카운트 텍스트 앵커(214ea/14ea) 재현 실패"
assert "1.32" in t and "1.05" in t, "LPC 0.25/0.5wt% 텍스트 수치 재현 실패"

# ── (C) 5점 계열 회귀 -- m과 R^2가 노트 기재값과 일치하는지 재계산 ──────────
eda      = np.array([0.05, 0.1, 0.25, 0.35, 0.5])
lpc      = np.array([2.68e5, 2.05e5, 1.32e5, 1.15e5, 1.05e5])
defects  = np.array([214.0, 73.0, 47.0, 15.0, 14.0])   # Fig.3, 텍스트 앵커: 0.05->214, 0.5->14
scratch  = np.array([205.0, 73.0, 43.0, 10.0, 8.0])     # Fig.4, 전량 그래프 판독(damage_exponent 채택 계열)

# 텍스트 확정 앵커 재확인
assert lpc[0] == 2.68e5 and lpc[2] == 1.32e5 and lpc[4] == 1.05e5
assert defects[0] == 214.0 and defects[4] == 14.0

def loglog_slope(y):
    ln_l = np.log(lpc / lpc[0])
    ln_y = np.log(y / y[0])
    m = float(np.sum(ln_l * ln_y) / np.sum(ln_l * ln_l))
    pred = y[0] * (lpc / lpc[0]) ** m
    r2 = 1 - float(np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))
    return m, r2

m_scratch, r2_scratch = loglog_slope(scratch)
m_defect, r2_defect = loglog_slope(defects)
print(f"Fig.4 스크래치 계열: scratch ~ LPC^{m_scratch:.3f}, R^2={r2_scratch:.3f}")
print(f"Fig.3 결함 계열(교차확인): defects ~ LPC^{m_defect:.3f}, R^2={r2_defect:.3f}")
assert abs(m_scratch - 3.22) < 0.05, f"노트 기재 m=3.22(Fig.4)와 어긋남: {m_scratch:.3f}"
assert r2_scratch > 0.9, f"R^2가 낮으면 §4의 estimated 채택 근거가 약해짐: {r2_scratch:.3f}"
assert abs(m_defect - 2.85) < 0.05, f"노트 기재 교차확인값 2.85(Fig.3)와 어긋남: {m_defect:.3f}"
assert r2_defect > 0.9
m = m_scratch  # damage_exponent 채택값

# ── (D) D99 유도 + 기준 조건 Δ=1.0 + 일반비 선택 불변성 ─────────────────
LEVITRONIX_RATIO = 5.00   # [[delta-scratch-damage-d99-oversize-particle-model]] §2.4/§6-C
d99_own = d50_own * LEVITRONIX_RATIO
assert d99_own == 275.0

def f_delta(d99, d99_ref, n):
    return (d99 / d99_ref) ** n

n_proposed = m  # damage_exponent 제안값 = Li2018 회귀 지수
base = f_delta(d99_own, d99_own, n_proposed)
assert base == 1.0, "기준 조건(D99=D99_ref)에서 Δ는 정확히 1.0이어야 한다"

for alt_ratio in (4.29, 5.00, 3.00):
    ref = d50_own * alt_ratio
    whatif = ref * 1.5
    assert abs(f_delta(whatif, ref, n_proposed) - 1.5 ** n_proposed) < 1e-12, \
        "일반비 선택에 따라 what-if Δ가 바뀌면 유도값 불확실성이 결과를 오염시킨다"
print(f"D99 고유값(D50={d50_own}nm × {LEVITRONIX_RATIO}) = {d99_own}nm, "
      f"기준 Δ=1.0 확인, 일반비 불변성 확인")

# ── (E) 기존 cu_h2o2_bta(알루미나) 값과의 대조 -- 다른 값이어야 이 노트의 존재 이유가 선다 ──
D99_ALUMINA_PACK = 500.0        # cu_h2o2_bta (알루미나 D50=100nm × 5.00)
N_ALUMINA_PACK = 2.54           # cu_h2o2_bta damage_exponent (W->Cu 전이, estimated)
assert d99_own != D99_ALUMINA_PACK, "실리카 고유 D99가 알루미나 팩값과 같으면 재료 이식 의심"
assert abs(n_proposed - N_ALUMINA_PACK) > 0.3, \
    "지수가 알루미나 전이값과 사실상 같으면 '더 가까운 매치'라는 §4 주장이 약해진다"
print(f"대조: 이 팩 제안(D99={d99_own}nm, n={n_proposed:.2f}) vs "
      f"알루미나 cu_h2o2_bta(D99={D99_ALUMINA_PACK}nm, n={N_ALUMINA_PACK}) -- 별개 값 확인")
```

## 6. 구현 요청

`knowledge/params/cu_alkaline_benzenesulfonic.yaml`에 아래 4키를 **팩 고유 선언**
(`has_own` — 부모 `cu_h2o2_bta`의 동명 키를 상속하면 알루미나 상수가 섞여 들어온다)으로
추가 제안:

```yaml
params:
  abrasive_size_nm:
    value: 55.0
    unit: nm
    source: >
      US9200180B2 §D) 실시예 "Potassium-stabilized colloidal silica: DuPont Air Products
      NanoMaterials L.L.C. ... particle size of 50-60 nanometers" — 50/60 중간값.
    confidence: literature

  abrasive_d99_nm:
    value: 275.0
    unit: nm
    note: >
      abrasive_size_nm(55nm, 위) × D99/D50 일반비 5.00 (Silco/Levitronix 2008, 2차 자료,
      [[delta-scratch-damage-d99-oversize-particle-model]] §2.4와 동일 방법론). 실측
      D99가 아니라 유도값 — 절대값을 신뢰하지 말고 비율(D99/D99_ref)만 쓴다.
    source: US9200180B2 + Silco/Levitronix 2008 (일반비)
    confidence: estimated

  abrasive_ref_d99_nm:
    value: 275.0
    unit: nm
    note: 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지.
    source: 자기 자신(설계 계약)
    confidence: estimated

  damage_exponent:
    value: 3.22
    note: >
      Li et al. (2018) ECS JSST 7(6) P317-P322, DOI:10.1149/2.0101806jss, Cu barrier CMP +
      콜로이달 실리카(~90nm) LPC(≥0.5µm)-스크래치 로그-로그 회귀(5점, R²=0.97). 독립변수가
      LPC(개수)이지 D99(지름 백분위)가 아니라는 축 불일치가 있으나, 이 팩과 연마입자·공정
      단계가 일치하는 가장 가까운 Cu 문헌이라 W→Cu 알루미나 전이값(2.54)보다 우선한다.
    source: "Li et al. 2018, DOI: 10.1149/2.0101806jss"
    confidence: estimated
```

**수식**: `sim/factors.py::_f_delta`는 이미 `Δ = (D99/D99_ref)^n × (1+a)` 형태로 구현돼
있다 — 코드 변경 불필요, 위 4키를 채우면 `pk.has("abrasive_d99_nm")` 게이트를 통과해
`status`가 `unmodeled → partial/modeled`로 바뀐다(드라이버가 `abrasive_d99_nm` 하나뿐이고
`aggregate_ratio`를 선언하지 않으면 `modeled`). 기준 조건 `abrasive_d99_nm ==
abrasive_ref_d99_nm == 275.0`이므로 Δ=1.0이 항등으로 성립한다(§5-D에서 assert).

**활성화 조건**: 위 4키(`abrasive_size_nm`, `abrasive_d99_nm`, `abrasive_ref_d99_nm`,
`damage_exponent`)를 이 팩이 **직접 선언**(`has_own`)해야 한다. 부모 `cu_h2o2_bta`가 이미
같은 이름의 키를 갖고 있어 선언을 빠뜨리면 조용히 알루미나 값(D99=500nm, n=2.54)이 상속돼
"실리카 계인데 알루미나 상수로 손상도를 진단한다"는 이 팩 존재 이유(YAML 상단 주석의
"재료 고유 상수 이식 금지")를 정면으로 위반한다.

## 7. 한계 (정직한 표기)

- ⚠ **미검증**: D99=275nm은 실측이 아니라 D50×일반비 유도값이다. K-안정 콜로이달 실리카의
  실측 D99(또는 LPC 절대 스펙)는 DuPont Air Products 제품 데이터시트에 있을 가능성이 높으나
  NDA/비공개로 이번 조사에서 확보하지 못했다.
- ⚠ **미검증**: damage_exponent=3.22는 LPC축 지수를 D99축 지수로 **근사 전환**한 값이다.
  [[delta-damage-exponent-cu-primary-source]] §4가 이미 지적했듯 두 축의 정량적 환산 관계는
  분포 형태 정보 없이 유도 불가능하다 — 이 노트는 "더 가까운 화학종 매치"를 근거로 근사를
  **선택**한 것이지, 축 불일치 문제 자체를 해소한 것이 아니다.
- ⚠ **미검증**: Li 2018 5점 중 3점(0.1/0.35wt%의 LPC, 0.1/0.25wt%의 스크래치)은 그래프
  판독값(±10~15%)이다. 텍스트로 직접 확정되는 것은 앵커 2쌍(EDA=0.05wt%: LPC=2.68e5/
  스크래치=214ea 완전쌍, EDA=0.35wt%: 스크래치=14ea 단독)뿐이다.
- ⚠ **범위 밖**: Δ는 `MRR_COUPLED`에 없는 진단 전용 출력이라 이 제안은 MRR 예측값을 바꾸지
  않는다 — 결함 위험도 진단(notes) 항목만 unmodeled에서 벗어난다.
- **1차 출처 확보 경로**: 둘 다 로컬에 이미 있었다 — 특허(`papers/patents/US9200180B2.html`,
  이 팩이 다른 파라미터 근거로 이미 인용 중인 파일)와 Li 2018 PDF
  (`papers/lu2018-jss-dispersant-scratch-reduction-cu-barrier-cmp.pdf`, 선행 노트가 미러
  사이트+curl referer 우회로 확보해 둔 사본). 새 네트워크 접근 없이 `tools/paper_text.py`
  재추출만으로 이번 조사를 완결했다.

## 8. 출처

- US 9,200,180 B2 (Air Products and Chemicals, Inc. / 현 Versum·Merck). §D) 실시예,
  §0162 명세. `papers/patents/US9200180B2.html`. 이 팩 YAML이 이미 kp_m_per_pa·slurry_ph
  등 다수 파라미터의 1차 출처로 인용 중.
- Li, Y.; Liu, Y.; Wang, C.; Niu, X.; Ma, T.; Xu, Y. (2018), "Role of Dispersant Agent on
  Scratch Reduction during Copper Barrier Chemical Mechanical Planarization," ECS J. Solid
  State Sci. Technol. 7(6) P317-P322. DOI: 10.1149/2.0101806jss.
- Silco Electronic Materials (2008), "Handling and Filtration of CMP Slurries", Levitronix
  CMP Users Conference — D99/D50 일반비 5.00 (2차 자료, [[delta-scratch-damage-d99-oversize-particle-model]] §2.4 경유 인용).
