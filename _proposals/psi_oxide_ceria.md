# 구현 제안 — ψ 표면 흡착 보호에 **농도 축** 추가 (oxide / ceria 계)

> 작성 2026-09-11 | 근거노트: `knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md`
> 대상: `sim/chemistry.py` (새 함수), `sim/factors.py::_f_psi` (분기 1개 추가),
> `knowledge/params/{sti_ceria,oxide_silica}.yaml` (키 추가)
> ⚠ **이 제안서는 코드를 수정하지 않았다.** `sim/factors.py`는 다른 작업자가 동시에
> 만지고 있어 손대지 않았다. 아래는 적용 대상자가 그대로 옮길 수 있는 형태로만 적었다.

---

## 0. 먼저 — 전제 하나를 정정한다

작업 지시는 세 팩의 ψ가 `status=unmodeled`이라고 했다. **실측하니 아니다:**

```
$ .venv/bin/python -c "from sim.engine import Recipe; from sim.factors import compute_factors; ..."
oxide_silica       status=modeled    value=1.0  conf=literature
sti_ceria          status=modeled    value=1.0  conf=estimated
sic_ceria_h2o2     status=modeled    value=1.0  conf=estimated
```

세 팩 모두 `_dispersant_protection_term`(PVA/PVP/PAA/PAM 이산 룩업)으로 이미 `modeled`다.
따라서 **완성 격자 C1 3칸은 이미 unmodeled가 아니다.** 격자를 이 기준으로 판정하고 있었다면
그 판정은 이미 참이다.

**진짜 결손은 다른 데 있다: 농도 축이 없다.** 현재 ψ는 분산제 *종류*만 받고 *얼마나
넣느냐*는 못 받는다. 그래서 첨가제 농도를 바꿔도 ψ가 상수다 — 사용자가 실제로 돌리는
노브가 죽어 있다. 이 제안은 그 축을 연다. (이건 파라미터 승격이 아니라 §2의 새 모델식이
필요한 작업이 맞다.)

---

## 1. 파라미터 키 목록

### 1.1 신규 키

| 키 | 단위 | 의미 |
|---|---|---|
| `surfactant_wt_pct` | wt% | 현재 계면활성제 농도 (사용자 노브) |
| `surfactant_ref_wt_pct` | wt% | 기준 농도 — Kp가 역산된 조성. **ψ=1.0의 정의점** |
| `surfactant_ads_K_per_wt_pct` | 1/wt% | 협동 흡착상수. C₅₀ = 1/K |
| `surfactant_ads_n` | – | Hill 협동성 지수. n=1이면 단일자리 Langmuir로 환원 |
| `surfactant_shield_k` | – | 피복→억제 감쇠 강도 |

### 1.2 팩별 값

#### `sti_ceria` — ✅ 직접 적용 (Park 2003과 같은 계: 세리아 + 계면활성제 + SiO₂/Si₃N₄)

```yaml
  surfactant_wt_pct:
    value: 0.10
    unit: wt%
    note: >
      Park 2003 Fig.3 고선택비 창(0.08~0.4 wt%)의 하단.
      질화막 임계농도 0.08 wt% 바로 위 — 질화막은 이미 억제됐고(60 Å/min)
      산화막은 아직 온전한(3650 Å/min) 지점. STI 정지막 공정의 표준 작동점.
    source: knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md §5.4
    confidence: estimated
  surfactant_ref_wt_pct:
    value: 0.10
    unit: wt%
    note: ψ=1.0 기준점 — surfactant_wt_pct와 동일값으로 이중계상 방지(설계계약 ①)
    source: knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md §5.3
    confidence: estimated
  surfactant_ads_K_per_wt_pct:
    value: 1.2949
    unit: "1/wt%"
    note: >
      Park 2003 (doi:10.1143/jjap.42.5420) Fig.3a 산화막 9점 회귀. C50=0.772 wt%.
      ⚠ 질화막 값은 K=14.02(C50=0.0713)로 10.8배 다르다 — 이 차이가 STI 선택비의
      기원이다. ψ는 피연마막(산화막) 값을 쓴다.
    source: knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md §5.4
    confidence: estimated
  surfactant_ads_n:
    value: 4.620
    unit: "-"
    note: >
      협동(hemimicelle) 흡착 지수. n=1(단일자리 Langmuir)은 Park 데이터를 재현하지
      못한다 — 실측 S자 문턱을 원리적으로 못 만든다(노트 §4에서 기각).
    source: knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md §4, §5.4
    confidence: estimated
  surfactant_shield_k:
    value: 3.000
    unit: "-"
    note: >
      ⚠ 이 9점만으로 k는 식별되지 않는다(노트 §5.5: k=1.63~50에서 SSE 0.0143→0.0125로
      거의 평평). k=3.0을 고른 근거는 θ_max=0.54로 포화에서 멀다는 것 — 설계계약 ③
      (θ→1에서 고농도 구분 소실)을 구조적으로 회피한다. k=1.63이면 θ_max=0.995로
      정확히 그 함정에 빠진다. **(K, n, k)는 한 묶음으로만 쓸 것.**
    source: knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md §5.5
    confidence: estimated
```

#### `oxide_silica` — ⚠ 부분 적용 (함수형만 전이, K는 캘리브레이션 대상)

값은 `sti_ceria`와 **동일하게** 넣되 note에 전이 사실을 명시한다. 연마입자가 실리카로
다르지만 **피복 대상 막이 SiO₂로 같다** — 흡착은 막 표면에서 일어나므로 이쪽이 지배축이다.
다만 Park에 실리카 슬러리 데이터가 없어 K의 정량 전이는 미검증이다.

```yaml
  surfactant_ads_K_per_wt_pct:
    value: 1.2949
    unit: "1/wt%"
    note: >
      ⚠ 교차계 전이: Park 2003은 **세리아** 슬러리 실측이다. 이 팩은 실리카 연마입자다.
      흡착이 일어나는 면은 SiO2 막으로 같으므로 함수형과 자릿수는 전이한다고 보되,
      K의 정량값은 미검증 — 캘리브레이션 1순위. 순위(더 넣으면 더 깎인다)만 신뢰하라.
    source: knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md §7
    confidence: estimated
```
(`_ads_n`, `_shield_k`, `_wt_pct`, `_ref_wt_pct`는 `sti_ceria`와 동일값·동일 전이 경고)

#### `sic_ceria_h2o2` — ❌ **넣지 않는다**

**근거를 못 찾았고, 그래서 안 넣는다.** 이유:
- 피연마재가 **SiC**다. Si–C 공유결합 세라믹이라 SiO₂의 실란올 표면화학과 흡착 기구가
  다르다. Park 2003에 SiC 데이터가 없고, 검색한 어느 문헌에도 SiC CMP의 계면활성제
  농도–MRR 스윕이 없었다.
- 이 팩의 원 출처(Wang et al. ACS SI Table S3) DOE 축은 CeO₂ wt% / H₂O₂ / pH이고
  **계면활성제 농도 축 자체가 없다.**

→ 현행 이산 분산제 경로(`dispersant_type: PVA`)를 그대로 두고, 농도축 부재를 notes로
신고한다. 여기서 숫자를 지어내면 시뮬레이터가 오염된다 — 이 제안서가 지키는 유일한
절대 규칙이다.

---

## 2. 계산 로직

### 2.1 `sim/chemistry.py` — 새 함수 (기존 함수 수정 없음)

```python
def _surfactant_shield_term(pack, notes: List[str]) -> Optional[float]:
    """계면활성제 협동 흡착 → 연마입자 접근 차단 → MRR 억제 배수.

    ψ의 '표면 흡착 보호' 경로 중 **농도 연속** 갈래.
    (이산 갈래 = _dispersant_protection_term, 분산제 종류 룩업)

    근거: Park et al. 2003, Jpn. J. Appl. Phys. 42(9A), 5420
          doi:10.1143/jjap.42.5420, Fig.3 9점 농도 스윕.
          knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md

    ⚠ 왜 단일자리 Langmuir가 아닌가:
      계면활성제는 hemimicelle로 **협동 흡착**한다. 실측 질화막 RR은 0→0.04 wt%에서
      거의 안 변하다가(800→660) 0.04→0.08에서 절벽처럼 떨어진다(660→80). 이 S자
      문턱을 단일자리 θ=KC/(1+KC)는 원리적으로 못 만든다 — 실제로 맞춰보면 가중
      SSE가 산화막 0.357 / 질화막 1.357로 기각된다(노트 §4).
      Hill 형 θ = (KC)^n/(1+(KC)^n)로 간다. n=1이면 Langmuir로 정확히 환원되므로
      기존 형식의 상위호환이다.

    ⚠ 왜 (1-θ)가 아니라 exp(-k·θ)인가:
      _inhibitor_term(chemistry.py:144-158)이 기록한 2026-09-06 사고와 같은 이유.
      θ가 포화하면 그 위 농도가 전부 같은 값으로 뭉개져 고농도 구분이 죽는다.
      같은 형식을 재사용한다 — 새 함수형을 발명하지 않는다.
    """
    if not pack.has("surfactant_wt_pct"):
        return None
    need = ("surfactant_ads_K_per_wt_pct", "surfactant_ads_n", "surfactant_shield_k")
    missing = [k for k in need if not pack.has(k)]
    if missing:
        notes.append(
            f"⚠ surfactant_wt_pct는 있으나 흡착 파라미터가 없어 차단 항 건너뜀: "
            f"{', '.join(missing)}")
        return None

    C = float(pack.get("surfactant_wt_pct"))
    K = float(pack.get("surfactant_ads_K_per_wt_pct"))
    n = float(pack.get("surfactant_ads_n"))
    k = float(pack.get("surfactant_shield_k"))

    def _theta(c: float) -> float:
        """협동(Hill/Sips) 피복률. n=1이면 단일자리 Langmuir."""
        if c <= 0.0:
            return 0.0
        x = (K * c) ** n
        return x / (1.0 + x)

    # 기준 농도 대비 상대값 — 절대 잔여율을 곱하면 Kp에 이미 반영된 억제를
    # 두 번 센다(설계계약 ①). exp 차분 형태라 C==C_ref에서 exp(0)=1.0 정확.
    if pack.has("surfactant_ref_wt_pct"):
        C_ref = float(pack.get("surfactant_ref_wt_pct"))
    else:
        C_ref = C
        notes.append("⚠ surfactant_ref_wt_pct가 팩에 없어 기준=현재 농도로 폴백했다 "
                     "— 계면활성제 변화가 MRR에 반영되지 않는다.")

    val = math.exp(-k * (_theta(C) - _theta(C_ref)))
    notes.append(
        f"계면활성제 흡착 차단: {C:g} wt% (기준 {C_ref:g}), θ={_theta(C):.3f}, "
        f"배수 {val:.3f} (C50={1.0/K:.3f} wt%). "
        "Park 2003 doi:10.1143/jjap.42.5420 Fig.3 회귀. "
        "⚠ k는 이 데이터로 식별되지 않는다 — (K,n,k) 묶음으로만 유효.")
    return val
```

### 2.2 `sim/factors.py::_f_psi` — 분기 1개 추가

현재 구조는 `억제제 → (없으면) 분산제 → (없으면) unmodeled`다. 여기에 계면활성제 항을
**분산제와 곱해지는 항**으로 넣는다. 둘은 서로 다른 물리(종류 vs 농도)라 배타가 아니다.

기존 `dv is None` 분기(factors.py:735) 직전에 삽입하고, 마지막 조립부를 이렇게 바꾼다:

```python
    # ── 기존: dv = _dispersant_protection_term(pk, dnotes) 직후 ──
    snotes: List[str] = []
    sv = _surfactant_shield_term(pk, snotes)
    if pk.has("surfactant_wt_pct"):
        try:
            f.drivers["surfactant_wt_pct"] = float(pk.get("surfactant_wt_pct"))
        except (TypeError, ValueError):
            pass

    if dv is None and sv is None:
        f.notes.append("⚠ ψ 미모델링: 억제제 파라미터도, 분산제 종류도, "
                       "계면활성제 농도도 팩에 없다. 표면 흡착 보호를 "
                       "시뮬레이션할 수 없다.")
        f.notes.extend(notes); f.notes.extend(dnotes); f.notes.extend(snotes)
        return f

    terms: Dict[str, float] = {}
    value = 1.0
    confs = []
    srcs = []
    if dv is not None:
        terms["dispersant"] = dv
        value *= dv
        confs.append(_pack_conf(pk, "dispersant_type"))
        srcs.append("knowledge/cmp/"
                    "abrasive-size-concentration-ph-K-additive-mrr-quantitative.md §6")
    if sv is not None:
        terms["surfactant_shield"] = sv
        value *= sv
        confs.append(_pack_conf(pk, "surfactant_ads_K_per_wt_pct"))
        srcs.append("knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md")

    f.value = value
    f.terms = terms
    f.status = "modeled"
    f.confidence = _worst_conf(*confs, "unverified") if confs else "unverified"
    f.sources = srcs
    f.notes.append("ψ 정의 확장: 표면 흡착 보호(passivation/adsorption shield) — "
                   "이 팩은 금속 부동태가 아니라 폴리머/계면활성제 흡착 경로")
    if sv is None and dv is not None:
        f.notes.append("⚠ 분산제 종류만 모델링됐다 — 첨가제 **농도** 축이 이 팩에 없어 "
                       "농도를 바꿔도 ψ가 변하지 않는다.")
    f.notes.extend(dnotes); f.notes.extend(snotes)
    return f
```

> ✅ `_worst_conf` 시그니처 확인함: `(*confs: str) -> str` — 가변인자다.
> 위 `_worst_conf(*confs, "unverified")` 호출은 그대로 동작한다.

---

## 3. 기준조건 1.0 보장 방법 (설계계약 ①)

세 겹으로 막는다:

1. **대수적 항등.** ψ = exp(−k·[θ(C) − θ(C_ref)])이므로 C = C_ref이면 지수가 정확히 0,
   `exp(0.0) == 1.0`은 IEEE-754에서 정확하다. 부동소수점 오차조차 없다.
   (비율 형태 `exp(-kθ)/exp(-kθ_ref)`로 쓰면 나눗셈 오차가 생긴다 — **차분 형태로 쓸 것.**)
2. **팩 값으로 강제.** 세 팩 모두 `surfactant_wt_pct == surfactant_ref_wt_pct`로 넣는다.
   기본 레시피에서 항등적으로 1.0.
3. **회귀 테스트.** `tests/test_factors.py`의
   `test_all_factors_are_unity_at_reference_condition`이 이미 이걸 잡는다. 추가로:

```python
def test_psi_surfactant_concentration_axis_is_live():
    """계면활성제 농도를 올리면 ψ가 실제로 내려가야 한다 (죽은 축 회귀 방지)."""
    base = _factors(pack="sti_ceria")["psi"]
    assert base.value == 1.0
    hi = _factors(pack="sti_ceria", surfactant_wt_pct=0.80)["psi"]
    assert hi.value < 0.5, f"농도를 8배 올렸는데 ψ={hi.value} — 축이 죽었다"

def test_psi_no_saturation_collapse_at_high_surfactant():
    """θ 포화 뒤에도 고농도 구분이 살아 있어야 한다 (설계계약 ③)."""
    vals = [_factors(pack="sti_ceria", surfactant_wt_pct=c)["psi"].value
            for c in (0.8, 1.6, 3.2)]
    assert vals[0] > vals[1] > vals[2], f"고농도 구분 소실: {vals}"
```

검산(제안 파라미터로 실제 계산한 값):

| C (wt%) | θ | ψ |
|---|---|---|
| 0.00 | 0.0000 | 1.0002 |
| 0.08 | 0.0000 | 1.0002 |
| **0.10 = C_ref** | 0.0001 | **1.0000** |
| 0.20 | 0.0019 | 0.9944 |
| 0.40 | 0.0457 | 0.8721 |
| 0.80 | 0.5407 | 0.1975 |
| 1.60 | 0.9666 | 0.0550 |
| 3.20 | 0.9986 | 0.0500 |

**실제 팩 로더로 검증했다**(`sim/engine.Recipe(...).resolve()` + 위 §2.1 함수 그대로,
`sti_ceria`/`oxide_silica` 양쪽). 확인된 것:
- `C == C_ref`에서 `psi == 1.0` **정확히**(비트 단위, `assert v == 1.0` 통과).
- θ가 0.9986으로 포화한 뒤에도 ψ가 0.0550 → 0.0500으로 **계속 감소**한다 = 설계계약 ③
  충족. 단 감쇠가 느리다 — k=3.0의 하한이 exp(−3)=0.0498이라 3.2 wt% 이상은 사실상
  바닥이다. 실용 농도 범위(≤1 wt%)에서는 문제없다.
- 파라미터가 없는 팩(`sic_ceria_h2o2`)은 `None`을 반환해 **조용한 1.0을 쓰지 않는다**
  (설계계약 ②). 농도만 있고 흡착상수가 없는 부분 지정도 `None` + 사유 note.

> ψ가 C < C_ref에서 1.0002로 **1을 아주 살짝 넘는다.** 의도된 것이다 — 계면활성제를
> 기준보다 덜 넣으면 보호막이 얇아 MRR이 오른다. 기존 `_inhibitor_term`도 같은 상대
> 구조라 1을 넘을 수 있다. 다만 `_f_psi` docstring은 ψ를 "≤1"이라 적어 놨으므로
> **그 문구를 "기준 대비 배수(1을 넘을 수 있음)"로 고쳐야 한다.** 안 고치면 다음
> 사람이 클램프를 넣고, 클램프가 들어가면 저농도 축이 죽는다.

---

## 4. 이 제안이 3칸에 대해 실제로 하는 일

| 팩 | 현재 | 제안 후 | 근거 |
|---|---|---|---|
| `sti_ceria` | modeled(종류만, 농도축 없음) | **modeled + 농도축 live** | Park 2003 직접 적용 — 같은 계 |
| `oxide_silica` | modeled(종류만) | **modeled + 농도축 live**(전이, 캘리브레이션 대상) | 함수형 전이, K 미검증 |
| `sic_ceria_h2o2` | modeled(종류만) | **변경 없음** | SiC 문헌 없음 — 지어내지 않는다 |

정직한 요약: **3칸 중 2칸에 농도 축이 열린다. 1칸(SiC)은 근거를 못 찾았다.**
그리고 세 칸 모두 원래부터 `unmodeled`이 아니었다(§0).

---

## 5. 같이 해야 할 일

1. **`_f_psi` docstring 수정** — "≤1" → "기준 대비 배수". §3 마지막 경고 참조.
2. **`INDEX.json` 등록** — 새로 확보한 PDF 4건:
   - `papers/kim2003-jjap-surfactant-oxide-nitride-selectivity-ceria.pdf` (Park 2003, 주 출처)
   - `papers/america2004-ecs-slurry-additive-nitride-suppression.pdf` (첨가제 10종 Table I)
   - `papers/prasad2006-jes-aminoacid-adsorption-silica-nitride-sti.pdf` (반증 출처)
   - `papers/dandu2015-jss-further-slurry-additives-sio2-si3n4-ceria.pdf` (교차검증)
3. **아미노산 축은 별건으로** — America 2004 Table I(선택비 6.1~228, 10종)은 농도 스윕이
   아니라 이산 룩업이다. ψ의 농도축이 아니라 **선택비(막질별 배수) 축**에 넣어야 맞다.
   Prasad 2006이 아미노산의 흡착량–억제 상관을 명시적으로 반증했으므로
   **아미노산에 Langmuir/Hill θ를 쓰면 안 된다.**
4. **캘리브레이션 1순위**: `oxide_silica`의 `surfactant_ads_K_per_wt_pct`(교차계 전이),
   그다음 두 팩의 `surfactant_shield_k`(비식별).
