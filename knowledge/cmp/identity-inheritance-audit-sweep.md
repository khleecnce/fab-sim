<!-- V2-SECTION: R2-slurry | 정체성 상속 전수감사 2026-09-18 -->
# 정체성 상속 전수감사 — 같은 결함이 네 번 반복된 뒤 기계에 넘긴 것

> 판정#60 (2026-09-18, Max워커). 판정#59 의 직접 후속.
> 산출물: `tools/audit_identity_inheritance.py`(신고 도구),
> `tests/test_identity_inheritance_audit.py`(계약 6건).
> **결론: 신고 18건 중 2건이 MRR 을 실제로 움직이는 살아 있는 결함**이고,
> 그 2건은 **판정#59 와 같은 팩의 같은 유형**이다(입경축).

## 1. 왜 도구를 만들었나

같은 유형의 결함이 네 번 나왔다. 전부 사람이 **우연히** 발견했다.

| 판정 | 내용 |
|---|---|
| #34 | sic 팩이 `sti_ceria` 의 IEP 정전창(산성용)을 상속해 자기 pH 계수를 가림 |
| #48 | sic 팩이 실리카 부모의 연마입자 농도를 상속 |
| #52 | 근거 문헌과 파라미터가 서로 다른 팩에 흩어짐 |
| #59 | `sic_alumina_kmno4` 가 `abrasive` 키 자체를 `'ceria'` 로 상속 — 알루미나 슬러리에 세리아 화학항이 켜져 있었다 |

네 번이면 개별 대응이 아니라 상시 감사의 문제다.

## 2. 설계 — 축(axis)이 핵심이고, 보수성이 의도다

상속받은 파라미터 K 에 대해 (1) K 가 어느 **재료축**에 속하는지 이름으로 분류하고
(2) 그 축의 재료가 **나**와 **K 를 실제로 선언한 조상**에서 다르면 신고한다.

축 없이 그냥 대조하면 무슨 일이 일어나는지 먼저 측정했다: **64건**이 나오고
그 안에 `pad_ra_m`(패드 표면거칠기)이 "연마입자가 다르다"는 이유로 섞인다.
패드 물성은 연마입자와 무관하다 — 그런 신고가 섞이면 도구를 아무도 안 본다.
축 분류를 넣으면 **18건**으로 줄고 전부 실제 재료축에 걸린 것만 남는다.

**축을 분류하지 못하는 키는 신고하지 않는다.** 이건 누락이 아니라 설계다 —
추측해서 신고하면 오탐이 나고, 오탐이 나면 도구가 죽는다. 대신 사각지대를
숨기지 않고 `--unclassified` 로 따로 낸다(테스트로 고정: 사각지대가 신고
목록에 섞이면 실패).

`AXIS_NONE`(재료가 달라도 상속이 정당하다고 **선언한** 키)에는 근거를 적었다:
`hamaker_j`(입자-매질-기판 3자 상수라 한 축에 귀속 불가)·`damage_exponent`
(재료 고유인지 공정 고유인지 미확정)·`dispersant_type`·`slurry_viscosity_pa_s`.
이 네 건은 **미검증**이다 — "괜찮다"가 아니라 "축을 정할 근거가 없다"는 뜻이다.

## 3. 결과 — 18건, 그중 살아 있는 것 2건

`PYTHONPATH=. .venv/bin/python tools/audit_identity_inheritance.py` 실측:

- `sic_alumina_kmno4` 16건 (연마입자 14 · 산화제 2)
- `sic_ceria_h2o2` 1건 · `sti_ceria` 1건 (둘 다 `abrasive_saturation_wt_pct` ← `oxide_silica`)

각 항목의 값을 1.5배 흔들어 MRR 변화를 측정해 **살아 있는 것과 죽은 것을 갈랐다**:

| 상태 | 건수 | 내용 |
|---|---|---|
| ★ MRR 영향 | **2** | `abrasive_size_nm`(Δ=0.455) · `abrasive_ref_size_nm`(Δ=0.313) |
| 무영향 | 15 | 세리아 계수(ce3_*·ceria_tooth_*)는 판정#59 가 이미 분기를 껐고, 산화제 계수는 판정#50 종 게이트가 껐고, 나머지는 소비처가 없다 |
| 비수치 | 1 | `oxidizer_langmuir_species`(문자열 — 게이트가 소비) |

즉 **판정#59 와 판정#50 이 이미 막아둔 것이 대부분이고, 뚫려 있는 축은 입경 하나**다.

## 4. 살아 있는 결함 — 입경축 (신규 발견)

```
sic_alumina_kmno4:
  abrasive_size_nm      = 120.0 nm  (owner=sic_ceria_h2o2, confidence=literature)
  abrasive_ref_size_nm  = 120.0 nm  (owner=sic_ceria_h2o2)
  abrasive_size_peak_nm = 163.0 nm  (owner=sic_ceria_h2o2)
  abrasive_size_exp_below_peak = 1.3333  (owner=sic_ceria_h2o2)
  abrasive_size_exp_above_peak = -0.3333 (owner=sic_ceria_h2o2)
```

이 다섯 값은 전부 **세리아 슬러리**(sic_ceria_h2o2)에서 온 것이고, 이 팩의
연마입자는 알루미나다. 그리고 이 팩의 근거 문헌 두 건은 **다른 입경**을 적는다:

- Gong 2024 (doi:10.3390/ma17030679) Table 1 — 알루미나 **500 nm**
- 데이터셋 YAML 의 `scope_note` 가 이미 이 사실을 적어뒀다: "입경도 원문 500 nm
  인데 팩은 이를 자기선언하지 않는다(절대값에만 영향, 이 DOE 는 입경을 고정하므로
  순위에는 무영향)"

즉 **이미 알려져 있었으나 상속 경로가 보이지 않아 방치돼 있던 것**이다. 이번 감사가
그 경로를 명시했다.

**문헌값 대조**: 팩이 쓰는 값 **120 nm**(세리아 상속) vs Gong 2024 Table 1 인쇄값
**500 nm**(알루미나) — **4.17배 불일치**이고, 두 값은 이 팩의 입경 정점
163 nm 를 사이에 두고 **서로 반대편**에 있다(120 nm 는 below-peak 가지, 500 nm 는
above-peak 가지). 즉 값만 다른 게 아니라 **적용되는 곡선 가지 자체가 다르다**.
아래 verify 블록이 κ size 항 1.00000(120 nm) vs 1.03534(500 nm) 와 MRR 비
1.0353배를 매번 재계산해 이 대조를 고정한다.

실측 κ(입경축) 값:

| abrasive_size_nm | κ size 항 | κ 전체 |
|---|---|---|
| 120 (현재, 세리아 상속) | 1.00000 | 0.483137 |
| 163 (정점) | 1.50433 | 0.726796 |
| 500 (Gong 실측 알루미나) | 1.03534 | 0.500209 |

MRR 비(120 nm → 500 nm) = **1.0353배**. 영향이 3.5% 로 작은 이유는 정점(163 nm)을
사이에 두고 양쪽 지수가 반대 부호(below +1.333 / above -0.333)라 120 과 500 이
우연히 비슷한 배수로 떨어지기 때문이다 — **작은 것이 맞아서가 아니라 우연이다.**

## 5. 왜 이번에 고치지 않는가

값을 500 nm 로 바꾸는 것은 한 줄이지만, **그러면 안 되는 이유가 있다**:

`abrasive_size_peak_nm`(163)·`_exp_below_peak`(1.333)·`_exp_above_peak`(-0.333)이
전부 **세리아 계에서 나온 형상**이다. 입경 값만 알루미나 것으로 바꾸면 **알루미나
입경을 세리아 입경-MRR 곡선에 대입**하게 된다 — 판정#59 §2 에서 실측으로 확인한
"실리카 곡선을 알루미나에 씌우는" 것과 **정확히 같은 함정**이다. 정점 위치와 두
지수가 알루미나 계에서도 같다는 근거는 없다(미검증).

정직한 상태 기술은 이것이다: **이 팩의 입경축은 값도 곡선도 남의 재료 것이다.**
값 하나만 고치면 "부분적으로 맞는 것처럼 보이는" 더 나쁜 상태가 된다.

따라서 이번 회차의 산출은 **값 변경이 아니라 신고의 상시화**다. 코드·YAML 0줄 변경,
격자 불변, MRR 비트 불변.

## 6. 미검증·확인 못 한 것

- **`AXIS_PREFIX` 분류표가 완전한지 검증하지 못했다.** 132개 키 중 축을 배정한 것은
  접두사 9종 + 개별 지정 11종이고, 나머지는 `--unclassified` 로 빠진다. 빠진 키에
  같은 유형의 결함이 있을 수 있다(사각지대).
- **`AXIS_NONE` 4건의 "축 없음" 판단은 근거가 없다** — 문헌으로 확인한 것이 아니라
  "한 축에 귀속시킬 근거를 못 찾았다"는 뜻이다(미검증).
- **`abrasive_saturation_wt_pct` ← `oxide_silica` 2건**(sic_ceria_h2o2·sti_ceria)은
  MRR 무영향이라 이번에 파고들지 않았다. 소비처가 생기면 판정 대상이다.
- **입경축 결함의 정확한 크기는 미확정**: 1.0353배는 **세리아 곡선을 그대로 쓴다는
  가정 하의** 값이다. 알루미나 곡선이 다르면 이 수치 자체가 무의미하다.

## 출처
- Gong J., Wang W., Liu W., Song Z., Materials 17(3) 679 (2024),
  doi:10.3390/ma17030679, Table 1 — 알루미나 500 nm.
- US20220315802A1 (Entegris / University of Florida), Table 1.
- 선행 판정: EVIDENCE-RULES.md 판정#34·#48·#50·#52·#59.
- 선행 노트: [[sic-alumina-pack-abrasive-identity-inheritance-defect]]
  (knowledge/cmp/sic-alumina-pack-abrasive-identity-inheritance-defect.md)

```python verify
# 판정#60 — 감사 도구가 실제로 돌고, 축 분류가 오탐을 막고,
# 입경축 수치가 노트에 적힌 그대로인지 매번 재확인한다.
import numpy as np
import sim.engine as E
from sim import factors
from sim.params import load_pack
from tools.audit_identity_inheritance import audit, _axis_of, AXIS_NONE

res = audit()
ms = {(m["pack"], m["key"]): m for m in res["mismatches"]}

# 1) 판정#59 유형(세리아 계수를 알루미나 팩이 상속)이 실제로 신고된다
for k in ("ce3_fraction", "ceria_tooth_gain", "ceria_tooth_exponent"):
    m = ms[("sic_alumina_kmno4", k)]
    assert m["axis"] == "abrasive" and m["mine"] == "alumina" and m["theirs"] == "ceria", m

# 2) 살아 있는 입경축 결함 2건이 신고된다
for k in ("abrasive_size_nm", "abrasive_ref_size_nm"):
    assert ("sic_alumina_kmno4", k) in ms, k

# 3) 오탐 없음 — 패드/장비 키는 신고되지 않는다
for (_p, k) in ms:
    assert k.split("_")[0] not in {"pad", "cond", "platen", "rpm", "sfr",
                                   "groove", "retaining", "cof"}, k

# 4) 축을 모르는 키는 추측하지 않는다
assert _axis_of("pad_ra_m") is None
assert _axis_of("kp_m_per_pa") is None
for k in AXIS_NONE:
    assert _axis_of(k) is None, k

# 5) §4 표의 입경축 수치 재현
pk = load_pack("sic_alumina_kmno4")
assert not pk.has_own("abrasive_size_nm"), "이미 자기선언됐다면 이 노트는 낡았다"
assert pk.param("abrasive_size_nm").owner == "sic_ceria_h2o2"
assert abs(float(pk.get("abrasive_size_nm")) - 120.0) < 1e-9
assert abs(float(pk.get("abrasive_size_peak_nm")) - 163.0) < 1e-9

def kappa(size):
    rr = E.Recipe(pack="sic_alumina_kmno4",
                  pack_overrides={"slurry_ph": 5, "oxidizer_wt_pct": 2,
                                  "abrasive_wt_pct": 3,
                                  "abrasive_size_nm": size}).resolve()
    return factors._f_kappa(rr).value

for size, want in ((120, 0.483137), (163, 0.726796), (500, 0.500209)):
    got = kappa(size)
    assert abs(got - want) < 1e-5, (size, got, want)

def mrr(size):
    return float(np.mean(E.simulate(E.Recipe(
        pack="sic_alumina_kmno4",
        pack_overrides={"slurry_ph": 5, "oxidizer_wt_pct": 2,
                        "abrasive_wt_pct": 3,
                        "abrasive_size_nm": size})).mrr_nm_per_min))

ratio = mrr(500) / mrr(120)
assert abs(ratio - 1.0353) < 1e-3, ratio

# 6) 감사는 읽기 전용 — MRR 을 건드리지 않는다
before = mrr(120)
audit()
assert mrr(120) == before

print("판정#60 verify: 6/6 PASS (신고 %d건, 사각지대 %d건)"
      % (len(res["mismatches"]), len(res["unclassified"])))
```
