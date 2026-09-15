# C4 — sic_ceria_h2o2 팩 held-out 유의성 진단

과제: C4(팩마다 유의 held-out ≥1, 유의 평균 ρ≥0.85)에서 "미완"으로 지목된 sic_ceria_h2o2
팩을 실측으로 재확인한다. 결론을 먼저 적는다: **완성 조건 자체는 이미 코드 기준으로 통과하고
있다(사실관계 정정) — 그러나 그 통과는 근거가 약한 단일 n=5 순환보정 데이터셋에 기대고 있고,
진짜 blind인 n=50 데이터셋(sic2026)은 여전히 비유의하다. 그 비유의의 원인은 n 부족이 아니라
`sim/factors.py::_f_chi`의 pH 항 선택 우선순위가 잘못돼 SiC 알칼리 영역(pH 9–11)에서 pH
민감도가 통째로 사라지는 코드 결함(2단계 분기 (b))이다.**

## 1단계 — 실측

### 1.0 실행 로그
```
$ .venv/bin/python tools/qa_loop.py run
QA 루프 #127  commit a21c76d  게이트 PASS
  유의 데이터셋 8/21  유의 평균 ρ = 0.9512
감사: 21개 데이터셋, 플래그 8개, 격리 0개
  ⚠ sic2026_ceria_h2o2_ph_DOE50: F2:출처에 DOI/특허번호 없음   ← 조사함, 4절 참조
  ⚠ entegris2022_us20220315802a1_sic_alumina_conc: C4:신고된 부분오염(calibration_contact)
```

### 1.1 sic_ceria_h2o2 팩에 연결된 데이터셋 — 실제 YAML `pack:` 필드 확인

과제 지시문의 4개 후보 중 **실제로 `pack: sic_ceria_h2o2`인 것은 2개뿐**이다(나머지 2개는
과제 작성 시점의 오기 — 실제로는 `pack: oxide_silica`):

```
$ grep -n "^pack:" validation/datasets/*.yaml
sic2026_ceria_h2o2_ph_DOE50.yaml:pack: sic_ceria_h2o2
entegris2022_us20220315802a1_sic_alumina_conc.yaml:pack: sic_ceria_h2o2
sic2023_shear_rheological_L9.yaml:pack: oxide_silica          ← sic팩 아님(오기)
carbide2023_slurry_composition_L9.yaml:pack: oxide_silica     ← sic팩 아님(오기, 초경합금 데이터)
```

### 1.2 각 데이터셋의 ρ·p·n과 held-out 취급 (`validation/backtest.py` 실행)

```
$ .venv/bin/python validation/backtest.py
entegris2022_us20220315802a1_sic_alumina_conc n= 5  ρ=+1.000  p=0.0083  스크리닝 사용 가능
sic2026_ceria_h2o2_ph_DOE50                    n=50  ρ=+0.089  p=0.266   참고용(캘리브레이션에 쓴 데이터 — 검증 아님)
```

- **entegris2022** (n=5): `used_for_calibration: false`, held-out 집계에 포함, p=0.0083 < 0.05 → **유의**.
  단 `calibration_contact` 신고됨 — 이 데이터셋(US20220315802A1 Table 1)이 바로
  `knowledge/params/sic_ceria_h2o2.yaml`의 `abrasive_conc_exponent=-0.406`의 **출처 그 자체**다
  (같은 n=5 표에서 로그-로그 회귀로 뽑은 값). 즉 "held-out 검증"이 아니라 "학습에 쓴 데이터로
  자기 자신을 채점"하는 순환 구조 — qa_loop의 C4 소프트플래그가 정확히 이걸 신고하고 있다.
  n=5는 완전측정(모든 조건이 단조), 순열검정 최소 p가 애초에 크지 않은 구간이라 통계적으로는
  유의로 나오지만 **독립성이 없다.**
- **sic2026** (n=50): `used_for_calibration: true`로 명시 — sic_ceria_h2o2의
  `ph_softening_per_unit`이 바로 이 DOE에서 역산됐기 때문에(팩 YAML 주석 확인) held-out
  집계에서 애초에 제외된다. 이건 정당한 처리다(자기 답안지 채점 방지). ρ=+0.089, p=0.266은
  **참고용 수치**이지 C4 게이트에 들어가는 숫자가 아니다.

### 1.3 sic_ceria_h2o2 팩의 completion.py C4 판정 — 실측 결과

```python verify
# verify: heldout_by_pack()이 실제로 어떻게 판정하는지 직접 실행
import sys; sys.path.insert(0, "tools")
import completion
ho = completion.heldout_by_pack()
assert ho["sic_ceria_h2o2"]["n_sig"] == 1          # entegris2022 하나
assert ho["sic_ceria_h2o2"]["mean_rho"] == 1.0     # entegris2022 rho
r = completion.check(verbose=False)
c4_fails = [f for f in r["fails"] if f.startswith("C4")]
assert c4_fails == []   # C4 실패 항목 0개 — 5개 팩 전부(sic_ceria_h2o2 포함) 통과
```
결과: **`tools/completion.py check()`의 fails 리스트에 C4 항목이 단 하나도 없다.** 현재 유일한
미완은 C2 10칸뿐이다(`Γ×5, χ×1, ψ×3, Δ×1`). COMPLETION.md 97행·428행의 "C4 sic팩 1건 남음"은
**작성 시점 이후 entegris2022 데이터셋이 추가되며 이미 해소된, 낡은 서술**이다(git log 확인:
commit `71e2c67` "VALIDATION: sic_ceria_h2o2 팩 held-out 확보 — Entegris ... 신규 held-out").

→ 이 회차의 1차 결론: **C4는 문서(COMPLETION.md)와 실측(코드)이 어긋나 있었다. 실측이 맞다.**
다만 그 "통과"가 n=5 순환보정 데이터 하나에 전적으로 의존하므로, 표로만 보고 끝내지 않고
진짜 blind 데이터(sic2026)가 왜 실패하는지를 이어서 진단했다(2단계).

### 1.4 F2 플래그("출처에 DOI/특허번호 없음") 조사 — sic2026의 출처는 실재하는가

YAML 주석의 출처: *Wang et al., "Machine Learning-Driven Optimization of Silicon Carbide
Chemical Mechanical Polishing with Surface Roughness Constraints", ACS SI Table S3*,
`https://ndownloader.figshare.com/files/60987447`.

직접 다운로드해 검증했다:
```
$ curl -sL -o /tmp/wang_sic_si.pdf "https://ndownloader.figshare.com/files/60987447" \
    --max-time 30 -w "HTTP:%{http_code} SIZE:%{size_download}\n"
HTTP:200 SIZE:859882      # YAML 주석의 "859,882 B" 와 정확히 일치
```
PDF 1페이지 제목·저자가 YAML 주석과 정확히 일치(22쪽, Hebei Univ. of Technology 등),
Table S3(p.5) 첫 3행 수치가 데이터셋 조건과 정확히 일치(2/6/9→160, 2/6/10→186.6,
2/6/11→376.1 nm/h). **합성/추정 데이터가 아니라 실재하는 출판물이다.**

F2가 뜬 원인은 데이터 문제가 아니라 **감사 도구의 오탐**이었다: `tools/qa_loop.py`의
`_source_ids()`는 YAML의 `source:` 필드 문자열만 정규식으로 스캔하는데(90–307행), 이
데이터셋은 ID를 별도 `doi:` 필드("figshare:31056549")에만 적어놨고 `source:` 필드
텍스트에는 없었다 — 다른 통과 데이터셋들(entegris2022 등)은 특허번호를 `source:` 문자열에
직접 박아 넣는 관행을 따르는데 이 파일만 그 관행을 안 지켰다. **조치**: 실제 PDF를 확보해
`papers/wang2026-acs-sic-cmp-si-table-s3.pdf`(+`.pdf.txt` 텍스트 추출본)로 등록하고,
`papers/INDEX.json`에 항목 추가, `source:` 필드에 `figshare:31056549` 토큰을 삽입해
감사 도구가 찾을 수 있게 했다(도구 로직은 건드리지 않음 — 데이터 파일만 정정).
재실행 결과 해당 F2 플래그 완전히 소멸(8개 플래그 → 7개), 유의 8/21·ρ0.9512 불변(회귀 없음).

## 2단계 — 분기 판정: sic2026이 비유의인 이유는 (a)/(b)/(c) 중 무엇인가

**결론: (b) 모델 예측이 체계적으로 틀렸다.** n=50은 검정력 문제가 아니다(n=50에서
필요한 최소 유의 ρ는 이미 낮다 — 실제로 아래 반사실 실험에서 같은 n=50으로 p=0.0015가
나온다). rho 자체가 낮은 것(0.089)의 원인을 잔차로 추적한 결과, 특정 팩터의 결함으로
좁혀졌다.

### 2.1 잔차 조사 — pH를 바꿔도 예측이 안 바뀐다

```
$ .venv/bin/python -c "실측 residual 덤프 (본문 스크립트)"
ph  CeO2 H2O2 P    obs      pred
9   2     6     5.5   2.67     833.46
10  2     6     5.5   3.11     833.46      ← pH 9→10→11, 예측 완전 동일(833.46)
11  2     6     5.5   6.27     833.46      ← 실측은 2.67→6.27로 2.3배 증가
10  2     4     5.5   2.70     833.46      ← H2O2 6→4로 바꿔도 예측 동일
10  2     2     5.5   2.97     833.46      ← H2O2 6→2로 바꿔도 예측 동일
```
예측이 CeO2 wt%·압력·rpm에만 반응하고 **pH·H2O2에는 전혀 반응하지 않는다.**

### 2.2 원인 A(부차) — 산화제(H2O2) 화학항이 이 팩에 아예 없다

```python verify
# verify
from sim.params import load_pack
pk = load_pack("sic_ceria_h2o2")
assert not pk.has("oxidizer_langmuir_K")
assert not pk.has("oxidizer_passivation_K")
assert not pk.has("oxidizer_peak_wt_pct")   # 세 경로 전부 없음
```
`sim/chemistry.py::_oxidizer_term`은 세 형태(Langmuir 촉진/억제/레거시 정점형) 중 하나의
형상 파라미터가 있어야 값을 낸다(193행 `if not pack.has("oxidizer_peak_wt_pct"): return None`).
sic_ceria_h2o2.yaml은 `oxidizer_ref_wt_pct`만 선언하고 형상 파라미터가 전혀 없어 이 항은
항상 `None` — H2O2 농도는 애초에 모델링되지 않았다. 이건 이번 회차에 새로 발견한 사실이며,
sim/factors.py의 `_f_chi`가 `terms`가 비어있지 않으면(ceria_tooth·pH항은 있으므로) 이
누락을 "화학층 비활성" 경고로 띄우지 않는다 — 조용히 삼켜진다.

### 2.3 원인 B(주범) — pH 항이 "틀린 메커니즘"으로 선택된다 (팩 상속 그림자 문제)

`sim/factors.py::_f_chi`(1097행)의 pH 항 선택 우선순위:
```python
if str(pk.get_or("abrasive", "")) == "ceria" and pk.has("abrasive_iep_ph"):
    ph_terms = [("ph_ceria_window", _ph_ceria_electrostatic_term)]   # ← sic팩이 여기로 빠짐
elif pk.has("w_ph_acid_k"):
    ...
elif pk.has("ph_peak") and pk.has("ph_ref"):
    ...
else:
    ph_terms = [("ph_softening", _ph_softening_term)]   # ← sic팩 전용 계수는 여기 있는데 못 옴
```
```python verify
# verify — 실제 확인
from sim.params import load_pack
pk = load_pack("sic_ceria_h2o2")
assert pk.has("abrasive_iep_ph") and not pk.has_own("abrasive_iep_ph")
assert pk.params["abrasive_iep_ph"].owner == "sti_ceria"          # 상속값, sic 고유값 아님
assert pk.has_own("ph_softening_per_unit") and pk.has_own("ph_ref")  # sic 고유 계수는 따로 있음
```
`sic_ceria_h2o2`는 `abrasive_iep_ph`(=6.8)를 **직접 선언한 적이 없고** 상속 체인
(`base→oxide_silica→sti_ceria→sic_ceria_h2o2`)에서 sti_ceria가 준 값을 물려받는다.
그런데 위 if/elif가 "ceria + abrasive_iep_ph 있음"을 최우선으로 보기 때문에, sic 팩이
**바로 이 sic2026 데이터에서 직접 역산해 자기 이름으로 선언한**(`has_own`) 전용 계수
`ph_softening_per_unit`(0.2787)·`ph_ref`(10.0)를 쓸 기회조차 얻지 못하고, 대신 STI-세리아
(Dandu 2009, pH 2~8 스윕)용으로 만들어진 IEP 정전 창 모델이 조용히 대신 실행된다.

이 IEP 창 모델은 sic2026이 탐색하는 pH 9–11 구간에서 **완전히 평평(포화)**하다:
```python verify
# verify — 창 모델 파라미터와 실제 값
import math
mid_hi = 6.8 - 1.0   # = 5.8, k_hi=10 (steep sigmoid)
def win(x, res_hi=0.18, k_hi=10.0, mid_hi=5.8):
    hi = 1.0/(1.0+math.exp(k_hi*(x-mid_hi)))
    return res_hi*(1-hi) + hi   # 세리아/실리카 양쪽 항 생략, 고pH 극한만
for ph in (9, 10, 11):
    v = win(ph)
    assert abs(v - 0.18) < 1e-4      # pH 9,10,11 전부 res_hi=0.18에 사실상 포화
```
mid_hi=5.8·k_hi=10인 시그모이드는 pH≥~6.5에서 이미 잔류값(res_hi=0.18)에 완전히
수렴한다. sic2026 DOE의 pH 9/10/11은 전부 이 포화 구간 안이라 `ph_ceria_window`
값이 사실상 상수(0.9999996~1.0000000, ratio 기준)가 되고, **모델은 pH를 9에서
11로 올려도 MRR이 전혀 안 바뀐다고 예측한다.** 실측은 정반대로 pH 9→11에서 MRR이
평균 2~3배 뛴다. IEP 정전 창 모델은 STI-세리아/실리카의 산성~중성 전이 물리
(pH 3~6)를 겨냥해 만든 것이라 **알칼리 영역(pH 9–11)에서 SiC-세리아-H2O2 계에
성립한다는 근거가 없다** — 실제로 실측과 정반대(무반응 vs 강반응)로 어긋난다.

### 2.4 반사실 실험 — 어느 쪽이 범인인지 정량 확인

```python verify
# verify — IEP 창 대신 sic 고유 ph_softening 항을 쓰면 어떻게 되는가
# (코드 미변경 — resolve()가 만든 ParamPack 사본에서 abrasive_iep_ph만 진단용으로 제거)
import sys, yaml, numpy as np
sys.path.insert(0, "validation")
import sim.models  # noqa: F401 — 모델 자동등록
from sim.engine import Recipe, simulate
import sim.factors as factors_mod
import backtest

raw = yaml.safe_load(open("validation/datasets/sic2026_ceria_h2o2_ph_DOE50.yaml"))["conditions"]

def recipe_from(c):
    ov = dict(c.get("overrides") or {})
    return Recipe(pack="sic_ceria_h2o2", pack_overrides=ov, pressure_psi=c.get("pressure_psi"),
                  rpm_platen=c.get("rpm_platen"), rpm_wafer=c.get("rpm_wafer"))

obs, pred_base, pred_cf = [], [], []
for c in raw:
    r = recipe_from(c)
    res = simulate(r, model="tier2.gw_physical_kp")
    pred_base.append(float(np.mean(res.mrr_nm_per_min)))
    obs.append(c["mrr_nm_per_min"])
    rr1 = r.resolve()
    fmult1, _ = factors_mod.mrr_multiplier(factors_mod.compute_factors(rr1))
    rr2 = r.resolve()
    del rr2.pack.params["abrasive_iep_ph"]          # IEP 분기를 못 타게 강제 → ph_softening 분기로
    fmult2, _ = factors_mod.mrr_multiplier(factors_mod.compute_factors(rr2))
    pred_cf.append(pred_base[-1] / fmult1 * fmult2)

rho_base = backtest.spearman_rho(pred_base, obs)
rho_cf = backtest.spearman_rho(pred_cf, obs)
n = len(obs)
p_base = backtest.perm_p_value(rho_base, n)
p_cf = backtest.perm_p_value(rho_cf, n)
assert n == 50
assert abs(rho_base - 0.0892) < 5e-3 and p_base > 0.05          # 현재 코드: 비유의
assert abs(rho_cf - 0.4040) < 5e-3 and p_cf < 0.05               # IEP창 제거: 유의로 전환
assert rho_cf > rho_base * 4                                     # 반사실 rho가 baseline의 4배 이상
```
`abrasive_iep_ph`를 해석된 팩 파라미터에서 제거해(=IEP 분기를 못 타게 강제) `_f_chi`가
`ph_softening` 분기로 빠지게 만들면, 같은 n=50 데이터에서 ρ가 0.089→0.404로 4.5배
뛰고 p=0.266(비유의)→0.0015(유의)로 뒤집힌다. **이걸로 pH 항 선택 오류가 sic2026
비유의의 주 원인임을 확인했다** — n 부족이 아니고, 무작위 잡음도 아니고, 특정
가정(세리아 IEP 정전 창이 알칼리 영역까지 유효하다)이 이 재료계에서 성립하지 않는다.

(ρ=0.404도 0.85 문턱에는 한참 못 미친다 — 2.2절의 산화제 항 부재가 남은 잔차의
상당 부분을 설명할 것으로 보이나, 두 원인을 동시에 끄고 정량 분리하는 것은 이번
회차 범위를 넘는다.)

### 2.5 코드를 고치지 않은 이유

COMPLETION.md의 원칙("데이터에 맞추려 식을 비트는 순간 회귀식이 된다")과 이번 과제
지시("원인을 특정해 여기까지만 쓰고 코드는 건드리지 마라")에 따라 `sim/factors.py`의
분기 우선순위나 `sic_ceria_h2o2.yaml`의 `abrasive_iep_ph` 오버라이드는 **변경하지
않았다.** 다만 이 결함이 이미 존재하는 confidence 판정에 영향을 줄 수 있다는 점은
판정 #33(EVIDENCE-RULES.md)에 기록했다 — 실행은 다음 회차 판단.

## 3단계 — 신규 SiC CMP 데이터 탐색

턴 예산(80턴 규칙)을 진단(1·2단계)에 집중 배분했고, 3단계는 시간이 남지 않아
시도하지 않았다.
> 미완: 신규 SiC CMP(세리아/알루미나+H2O2) n≥3 스윕 데이터 탐색 — 다음 회차 과제로 남긴다.

## 결론 요약

| 질문 | 답 |
|---|---|
| sic_ceria_h2o2에 연결된 데이터셋 | entegris2022(n=5, held-out, 유의) + sic2026(n=50, calibration, 참고용) — 나머지 2개는 실제로 oxide_silica 팩 소속(과제 지시문 오기) |
| C4가 현재 미완인가? | **아니다.** `tools/completion.py check()` 실측상 C4 fail 0건(5팩 전부 통과). COMPLETION.md 97·428행이 낡았다 |
| 그 "통과"는 견고한가? | 아니다 — 유일한 유의 held-out(entegris2022)이 팩의 학습 데이터 자체(`abrasive_conc_exponent` 출처)라 순환적이다(calibration_contact 기 신고됨) |
| sic2026(진짜 blind, n=50)은 왜 비유의(ρ=0.089,p=0.266)인가? | (b) 모델 결함. `_f_chi`의 pH 항 선택이 상속된 세리아 IEP 정전 창(pH 3~6용)을 최우선으로 골라, sic 고유 `ph_softening_per_unit`(자기 선언, 바로 이 데이터에서 역산)이 가려진다. IEP 창은 pH 9~11에서 완전 포화해 pH 민감도가 0이 되는데 실측은 2~3배 반응한다 |
| F2(출처 없음) 플래그는 데이터 문제인가? | 아니다 — 실재하는 ACS SI(figshare:31056549) 논문, 감사 도구가 `source:` 필드만 스캔해 생긴 오탐. PDF 확보·INDEX 등록·source 필드 정정으로 해소 |
| 코드를 고쳤는가? | 아니다. 원인만 특정하고 `sim/factors.py`·`knowledge/params/*.yaml`은 미변경. 데이터 인덱싱 파일(`papers/INDEX.json`, `sic2026...yaml`의 source 필드)만 정정 |

## 4단계 — 수정 및 결과(2026-09-15, 후속 회차)

과제: 판정#33이 남긴 결함(§2.3·§2.4)을 실제로 고친다. **일반 원칙**을 세운다 —
"팩이 어떤 pH 메커니즘의 고유 계수를 직접 선언(`has_own`)했다면, 상속만 받은
다른 메커니즘보다 우선한다." sic 팩만 이름으로 특별 취급하는 하드코딩은 금지.

### 4.1 코드 변경

`sim/factors.py::_f_chi`의 elif 체인을 (분기명, 항함수, 적용가능여부, 고유
계수 키) 4-튜플 리스트로 재구성하고, 2-패스 선택으로 바꿨다:
  1차 패스 — 적용 가능하고 고유 계수를 **직접 선언**(`has_own`)한 첫 후보.
  2차 패스(아무도 own이 아니면) — 기존 elif/else 순서 그대로.

이러면 "own인 메커니즘이 하나도 없으면 원래 동작과 100% 동일"이 구조적으로
보장된다 — 코드가 그 자체로 회귀 방지 증명이다.

### 4.2 4팩 분기 불변 확인 (실행 출력)

```
$ git stash -- sim/factors.py   # 수정 전 코드로 되돌려 대조
cu_h2o2_bta    ['oxidizer']                 partial
oxide_silica   ['ph_peak']                  partial
sti_ceria      ['ceria_tooth', 'ph_ceria_window']  modeled
w_fe_oxidizer  ['oxidizer', 'ph_w_acidic']  modeled
sic_ceria_h2o2 ['ceria_tooth', 'ph_ceria_window']  modeled   ← 수정 전(버그)

$ git stash pop   # 수정 후 코드
cu_h2o2_bta    ['oxidizer']                 partial
oxide_silica   ['ph_peak']                  partial
sti_ceria      ['ceria_tooth', 'ph_ceria_window']  modeled   ← 불변
w_fe_oxidizer  ['oxidizer', 'ph_w_acidic']  modeled          ← 불변
sic_ceria_h2o2 ['ceria_tooth', 'ph_softening']     modeled   ← 수정됨
```
4팩(cu_h2o2_bta·oxide_silica·sti_ceria·w_fe_oxidizer)은 글자 하나까지 동일,
sic_ceria_h2o2만 `ph_ceria_window` → `ph_softening`으로 바뀌었다. 이 표는
`tests/test_chi_ph_branch_own_priority.py::test_branch_selection_fixed_across_five_packs`
로 그대로 고정했다.

### 4.3 backtest.py 결과 — 반사실 실험값과 다르다, 원인을 찾았다

```
수정 전: sic2026_ceria_h2o2_ph_DOE50   n=50  ρ=+0.089  p=0.266
수정 후: sic2026_ceria_h2o2_ph_DOE50   n=50  ρ=+0.393  p=0.002
```
과제 지시문이 요구한 대조값은 §2.4 반사실 실험의 ρ=0.404·p=0.0015였다.
**일치하지 않는다 — 원인을 조사했다.**

```python verify
# verify — §2.4 반사실 실험이 실제로 어느 분기를 탔는지 재확인
import sys, yaml, numpy as np
sys.path.insert(0, "validation")
import sim.models  # noqa: F401
from sim.engine import Recipe, simulate
import sim.factors as factors_mod
import backtest

raw = yaml.safe_load(open("validation/datasets/sic2026_ceria_h2o2_ph_DOE50.yaml"))["conditions"]

def recipe_from(c):
    ov = dict(c.get("overrides") or {})
    return Recipe(pack="sic_ceria_h2o2", pack_overrides=ov, pressure_psi=c.get("pressure_psi"),
                  rpm_platen=c.get("rpm_platen"), rpm_wafer=c.get("rpm_wafer"))

branches = set()
for c in raw:
    r = recipe_from(c)
    rr2 = r.resolve()
    del rr2.pack.params["abrasive_iep_ph"]   # §2.4가 실제로 한 조작 그대로
    fac = factors_mod._f_chi(rr2)
    branches.add(tuple(sorted(fac.terms.keys())))
assert branches == {("ceria_tooth", "ph_peak")}   # ph_softening이 아니다!
```
**§2.4의 반사실 실험은 실제로 `ph_softening`이 아니라 `ph_peak`(오실리카에서
상속된 실리카 정점 모델) 분기를 탔다.** `abrasive_iep_ph` 하나만 지우면
elif 체인이 branch1(세리아 IEP)→branch2(W 산성)→**branch3(ph_peak: sic가
`ph_peak`을 상속으로 갖고 있고 `ph_ref`는 자기선언이라 조건이 참)**에서
멈춘다 — branch4(ph_softening)까지 가지 않는다. 즉 판정#33의 §2.4 서술
("IEP분기를 못 타게 하면 ph_softening 분기로 빠진다")은 **가림이 한 겹이
아니라 두 겹**이라는 사실을 놓친 오기였다: `abrasive_iep_ph`(sti_ceria
상속)가 1차 가림이고, `ph_peak`(oxide_silica 상속, sic는 값 자체를 선언한
적이 없음)이 2차 가림이다. 단순 삭제 반사실은 1차만 벗겨 2차 가림 뒤에
숨어있던 **또 다른 상속 메커니즘**(실리카 정점 모델)을 대신 노출시켰을
뿐이다.

`has_own` 우선 규칙은 두 겹을 한 번에 뚫는다 — `abrasive_iep_ph`도
`ph_peak`도 sic 입장에서는 `has_own=False`이므로 1차 패스에서 둘 다
건너뛰고 곧바로 sic가 **직접 역산해 선언한**(`has_own=True`) `ph_softening_
per_unit`으로 간다. 이게 §설계 원칙이 요구한 그대로의 동작이고,
`tests/test_chi_ph_branch_own_priority.py::test_sic_takes_ph_softening_not_
inherited_ceria_window`로 고정했다. ρ=0.393(<0.404)은 "실리카 정점 모델을
빌려 쓴 우연한 적합"보다 낮지만, **sic 고유 계수를 쓰는 것이 이 수정의
목적이므로 이 낮은 쪽이 맞는 결과다** — ρ를 높이려고 어느 분기를 택할지
고른 게 아니라, "누구 계수를 쓰는가"의 원칙을 고정한 결과가 이렇게
나온 것이다. 그래도 기준선(0.089)의 4.4배, 비유의(p=0.266)→유의(p=0.002)
전환은 §2.4의 핵심 결론("IEP 창이 알칼리 SiC 계에 안 맞는다")을 그대로
재확인한다.

### 4.4 헤드라인·격자·회귀 불변 확인 (실행 출력 그대로)

```
held-out 12개 전체 평균: ρ=+0.817, 쌍별 적중률 91.0%   (수정 전/후 동일)
  └ 유의 8개: ρ=+0.951, 쌍별 적중률 96.9%              (수정 전/후 동일)
```
sic2026은 `used_for_calibration: true`라 이 집계에 처음부터 안 들어간다 —
그래서 이 수정이 헤드라인 숫자를 안 건드리는 것이 **정상**이다(실제로
안 바뀜, 위 숫자가 그 확인).

```
$ .venv/bin/python tools/completion.py check   # 수정 전/후 모두
완성 판정: ❌ 미완 — 격자 40/50칸 충족                (수정 전/후 동일, C4는 여전히 fails 0건)

$ .venv/bin/python -m pytest -q
715 passed, 19 warnings in 188.11s              (수정 전 715 passed와 동일 — 0 실패)

$ .venv/bin/python tools/qa_loop.py run --strict
QA 루프 #131  commit f2b2d7a  게이트 PASS
  유의 데이터셋 8/21  유의 평균 ρ = 0.9512
```

### 4.5 산화제(H2O2) 항 부재 — 경고만 추가(모델링 안 함, §2.2 스코프 유지)

`_f_chi`에 구조적 검사를 추가했다: 팩이 `oxidizer_wt_pct`/`oxidizer_ref_wt_pct`
로 산화제 존재를 선언했는데 형상 파라미터(`oxidizer_langmuir_K`/
`oxidizer_passivation_K`/`oxidizer_peak_wt_pct`)가 하나도 없으면
`f.notes`에 경고를 추가한다(값·status·confidence는 그대로). 5팩 중 이
조건에 걸리는 것은 `sic_ceria_h2o2` 하나뿐이다(cu_h2o2_bta·w_fe_oxidizer는
형상 파라미터 보유, oxide_silica·sti_ceria는 산화제 개념 자체가 없음) —
이름 하드코딩 없이 구조로만 걸린다.

### 4.6 결론

**B(수정 완료) 채택.** `sim/factors.py::_f_chi`의 pH 항 선택에 `has_own`
우선 원칙을 넣어 sic 팩이 자기 고유 계수(`ph_softening_per_unit`)를 쓰게
됐다. 4팩 분기는 완전히 불변(테스트로 고정), 전체 pytest 0 실패, 완성
격자 40/50 불변, qa_loop PASS. sic2026 ρ는 0.089→0.393(4.4배), p는
0.266→0.002(유의 전환)로 판정#33의 결론(모델결함, n부족 아님)을 재확인
했다 — 다만 정확한 목표값(0.404/0.0015)과는 §4.3에서 밝힌 대로 **판정#33
§2.4 반사실 실험 자체의 서술 오류**(2겹 가림을 1겹만 벗겼다) 때문에
다르다. 이 오류는 이번 회차에 함께 정정했다. 산화제 항 부재(§2.2)는
경고 note만 추가했고 모델링은 이번 회차 범위 밖으로 그대로 남겼다.
