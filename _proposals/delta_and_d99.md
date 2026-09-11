# 구현 제안서 — Δ(손상 유발도) 3팩 활성화 + `abrasive_d99_nm` 문헌 근거

> 작성 2026-09-11 | 제안자: slurry-abrasive
> 근거 노트: [`knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md`](../knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md)
> **이 문서는 제안일 뿐이다. 작성자는 `sim/factors.py`와 `knowledge/params/*.yaml`을 수정하지 않았다**
> (동시 작업자 충돌 방지 지시). 아래 표/코드를 반영하는 것은 담당 작업자의 몫이다.

---

## 0. 한 줄 요약

3팩(`cu_h2o2_bta`, `oxide_silica`, `w_fe_oxidizer`)에 **파라미터 3키만 추가**하면
`_f_delta`가 `unmodeled` → `partial`로 전환된다. **`sim/factors.py` 코드 변경은 필수가 아니다**
(선택 개선 §4만 권고). Δ는 `MRR_COUPLED`에 없어 **MRR 예측값은 한 자리도 바뀌지 않는다.**

---

## 1. 현재 상태와 차단 원인

`sim/factors.py::_f_delta` (L876~916):

```python
if not pk.has("abrasive_d99_nm"):
    f.notes.append("⚠ Δ 미모델링: 대입자 tail(abrasive_d99_nm)이 팩에 없다. ...")
    return f          # ← status 기본값 유지 = unmodeled
d99     = float(pk.get("abrasive_d99_nm"))
d99_ref = float(pk.get_or("abrasive_ref_d99_nm", d99))
n       = float(pk.get_or("damage_exponent", 3.0))
val     = (d99 / d99_ref) ** n
```

- 차단 조건은 **`abrasive_d99_nm` 키 존재 여부 단 하나**다.
- `sti_ceria.yaml`은 이미 3키(700 / 700 / 1.44)를 갖고 있어 partial로 작동 중 → **같은 패턴을
  3팩으로 복제하면 된다.** (`sic_ceria_h2o2`는 별도 확인 대상, 이 제안 범위 밖)
- `damage_exponent` 코드 기본값 3.0은 **어떤 문헌 데이터점과도 일치하지 않는다**
  (근거 노트 §6-B verify가 이를 assert로 고정). 팩에서 반드시 덮어써야 한다.

## 2. Δ는 진단 전용이다 (설계 계약 확인)

```python
MRR_COUPLED = {"chi", "psi", "kappa", "tau"}      # sim/factors.py L62 — delta 없음
```

- Δ는 `mrr_multiplier()` 곱셈 루프에 들어가지 않는다 → **결함 위험도 예측 출력 전용**.
- 따라서 이 제안을 반영해도 **MRR 회귀·검증 수치는 변하지 않는다.** 이중 계상 위험 0.
- Egan & Kim 2019 §3.4가 "텅스텐 벌크 CMP에서 대입자는 MRR을 올리지 않는다"를 양산 데이터로
  실측한 것과 이 분리 설계가 정합적 — **대입자는 손상축 전용**이다.
- 제안 반영 시 팩 YAML 주석에 이 문장을 그대로 남길 것: *"Δ는 MRR에 곱해지지 않는 진단 팩터다.
  이 값을 올려도 MRR 예측은 변하지 않는다."*

## 3. 추가할 파라미터 (팩별 값)

### 3.1 `abrasive_d99_nm` — 대입자 꼬리 대표 직경

| 팩 | 값 (nm) | 단위 | confidence | 유도 경로 / 출처 |
|---|---|---|---|---|
| `oxide_silica` | **250.0** | nm | `literature` | `abrasive_size_nm`(50) × D99/D50 일반비 5.00. 비율 출처: Silco/Levitronix CMP Users Conference 2008 slide p.11(3세대 관측 4.29~5.00, 중앙값 5.00). 상한 대조: Fuso US2025/0059050A1이 LPC를 세는 bin이 0.20 µm — 오더 일치 |
| `cu_h2o2_bta` | **500.0** | nm | `literature` | `abrasive_size_nm`(100) × 5.00. 상한 대조: Showa Denko US6770218 B2 명세 *"maximum grain size of 1.0 µm or less, more preferably 0.5 µm"* — **선호 상한과 정확히 경계 일치** |
| `w_fe_oxidizer` | **750.0** | nm | `literature` | `abrasive_size_nm`(150) × 5.00. Showa Denko 절대 상한 1.0 µm 이내(선호 상한 0.5 µm는 초과 ⚠) |

> ⚠ **절대값을 읽지 마라.** 측정된 D99가 아니라 유도값이다. Δ가 쓰는 것은 `d99/d99_ref` **비율**
> 뿐이고, 근거 노트 §6-D verify가 *"일반비를 3.00/4.29/5.00 어느 것으로 바꿔도 what-if Δ 배수가
> 동일"* 함을 assert로 증명한다 — 유도값 불확실성이 출력을 오염시키지 않는 방어선.

### 3.2 `abrasive_ref_d99_nm` — 기준점 (Δ=1.0 보장)

| 팩 | 값 (nm) | confidence | 비고 |
|---|---|---|---|
| `oxide_silica` | **250.0** | `literature` | `abrasive_d99_nm`과 **반드시 동일값** |
| `cu_h2o2_bta` | **500.0** | `literature` | 〃 |
| `w_fe_oxidizer` | **750.0** | `literature` | 〃 |

**Δ=1.0 보장 방법**: `abrasive_ref_d99_nm := abrasive_d99_nm`로 두면
`(d99/d99_ref)**n = 1.0**n ≡ 1.0`으로 **부동소수 오차 없이 정확히 1.0**이다(동일 float 나눗셈).
sti_ceria가 이미 쓰는 방식이며 근거 노트 verify가 `assert base == 1.0`(부등호 허용치 없이)로
검증한다. Δ는 recipe `pack_overrides`로 `abrasive_d99_nm`만 흔들어 "D99가 이만큼 커지면" what-if를
묻는 축으로 쓴다.

### 3.3 `damage_exponent` — 손상 지수 n

| 팩 | 값 | confidence | 출처·근거 |
|---|---|---|---|
| `oxide_silica` | **1.44** | `literature` | Hitachi US8439995B2 4점 로그-로그 회귀(n=1.444, R²=0.997). 막질 일치(산화막 CMP), 연마입자 불일치(세리아 vs 실리카) ⚠. 교차확증: Remsen 2006(퓸드실리카·산화막) Table V 선형(n≈1) |
| `w_fe_oxidizer` | **2.54** | `literature` | Egan & Kim 2019(ECS JSS 8(5) P3206) 두 관측의 기하평균 √(3.73×1.73). 막질·공정 완전 일치(텅스텐 벌크 CMP, GLOBALFOUNDRIES 300 mm 양산) |
| `cu_h2o2_bta` | **2.54** | `estimated` | 동상 전이. 연마입자·촉매 계열 일치(알루미나+철촉매 금속 CMP — Showa Denko US6770218이 W(Ex.1)와 Cu(Ex.9)를 동일 슬러리로 다룸), **막질 불일치(Cu vs W)** → confidence 한 단계 강등 |

**기하평균을 쓰는 이유**: n은 로그축 기울기이므로 두 관측의 로그공간 중앙 = 기하평균(2.54)이
맞다(산술평균 2.73 아님). 두 관측이 2.16배 벌어져 있어 어느 쪽도 단독 사용 불가.

### 3.4 지어내지 않기 위해 **기각한** 후보 (기록 보존)

| 후보 | 값 | 기각 사유 |
|---|---|---|
| Showa Denko US6770218 Table 1 회귀 n | 13.07 (R²=0.93) | 스크래치가 5등급 **순서척도**(등급5 = "100개 이상", 상한 없음) / 입경 범위 0.19~0.25 µm로 **1.32배뿐** → 로그축 지렛대 부족으로 기울기 폭주 / α전환율·BET 동시 변동(Comp.1은 입경 최소인데 등급 5로 최악 — 결정상이 지배) |
| Fuso US2025/0059050A1 회귀 지수 | 0.425 (R²=0.987) | 종속변수가 스크래치 카운트가 아니라 **AFM Rq** / 독립변수가 D99가 아니라 **LPC 개수**(축 불일치) / 출원인 화이트리스트 미등재 |
| 코드 현 기본값 | 3.0 | 문헌 근거 없는 가정값. 어떤 문헌 데이터점(1.43/1.73/2.54/3.73)과도 일치하지 않음 |

## 4. `sim/factors.py` 변경 제안 (선택 — 필수 아님)

파라미터만 넣으면 코드 변경 없이 3칸이 해소된다. 아래는 **품질 개선 권고**이며 별건으로 다뤄도 된다.

### 4.1 (권고 A) docstring·경고 문구 갱신 — 안전한 최소 변경

현 경고는 `damage_exponent=3.0`이 "Hitachi n≈1.44보다 2배 가파르다"까지만 말한다.
텅스텐 n=2.54가 추가됐으므로 다음으로 보강 제안:

```python
f.notes.append(
    f"⚠ 손상 지수 n={n:g}는 화학종별 문헌 회귀값에서 온다. 순위(큰 입자가 더 긁는다)만 "
    "신뢰하고 절대값은 쓰지 마라. 문헌 데이터점: 세리아·산화막 n=1.44(US8439995B2, R²=0.997), "
    "텅스텐 벌크 n=2.54(Egan&Kim 2019 기하평균, 관측 1.73~3.73), 퓸드실리카 선형 n≈1"
    "(Remsen 2006). 코드 기본값 3.0은 이 중 어느 것과도 일치하지 않는 가정값이다 — "
    "팩에서 반드시 덮어써라. 근거: knowledge/cmp/"
    "delta-scratch-damage-d99-oversize-particle-model.md §4.3")
```

### 4.2 (권고 B) 유도 D99에 대한 출처 경고 — 사용자 오독 방지

D99가 실측이 아니라 유도값인 팩에서 절대값 오독을 막기 위한 선택적 게이트:

```python
# _f_delta 안, val 계산 직후
if abs(d99 - d99_ref) < 1e-12:
    f.notes.append(
        "ℹ Δ=1.0 (기준 조건). 이 팩의 D99는 평균 입경 × 업계 일반 꼬리비(D99/D50≈5.0, "
        "Levitronix/Silco 2008)로 유도한 값이며 실측 스펙이 아니다 — 절대값이 아니라 "
        "pack_overrides로 D99를 흔들었을 때의 **상대 배수**만 의미가 있다.")
```

### 4.3 (권고 C, 우선순위 낮음) 개수축 신설 검토 — 이번 제안 범위 밖

Fujifilm US10907074B2 Claim 1: *"less than **800,000** for large particle counts / weight percent
abrasive … particles **larger than 0.2 microns** per milliliter"*, Example 8: LPC/wt% solids 기준
**50,000**. 또 Example 5는 *"0.56 µm and/or 1.01 µm bin size are inadequate"* — Cu 슬러리의
스크래치 지배 bin이 0.2 µm임을 명시. 이는 D99(대표 직경)와 다른 **개수축**이며, Remsen 2006이
실제로 측정한 축이기도 하다. 향후 `abrasive_lpc_per_ml` + `lpc_bin_um` 파라미터 신설 시
`_f_delta`에 선형항(Remsen Table V가 선형을 지지)을 추가하는 경로를 검토할 수 있다.
**이번 제안에는 포함하지 않는다** — 3팩 어디에도 LPC 실측값이 없어 또 no-op이 된다.

## 5. 반영용 YAML 조각 (복사해 쓰라)

> ⚠ 아래는 제안 텍스트다. 작성자가 `knowledge/params/`를 건드리지 않았음을 다시 밝힌다.

<details>
<summary><code>knowledge/params/oxide_silica.yaml</code> — 기존 L130~132 "abrasive_d99_nm 없다" 주석 블록을 대체</summary>

```yaml
  # ── Δ 손상 유발도 (스크래치 위험) ─────────────────────────
  # ⚠ Δ는 MRR에 곱해지지 않는 **진단 전용** 팩터다(sim/factors.py MRR_COUPLED에 delta 없음).
  #   이 값을 바꿔도 MRR 예측은 변하지 않는다.
  # ⚠ 아래 D99는 **실측 스펙이 아니라 유도값**이다: abrasive_size_nm(50) × D99/D50 일반비 5.00.
  #   abrasive_d99_nm == abrasive_ref_d99_nm이므로 기준 조건에서 Δ=1.0이 정확히 성립한다.
  #   의미 있는 것은 절대값이 아니라 recipe pack_overrides로 D99를 흔들었을 때의 상대 배수다.
  abrasive_d99_nm:
    value: 250.0
    unit: nm
    note: >
      abrasive_size_nm(50 nm) × D99/D50 일반비 5.00 유도값. 일반비 출처는 Silco/Levitronix
      CMP Users Conference 2008 슬라이드 p.11(3세대 관측 4.29~5.00, 중앙값 5.00, 산업
      컨퍼런스 2차 자료). 오더 대조: Fuso US2025/0059050A1이 콜로이달 실리카 LPC를 세는
      bin이 0.20 µm로 이 값과 같은 대역. 실측 D99 아님.
    source: knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §4.2
    confidence: literature
  abrasive_ref_d99_nm:
    value: 250.0
    unit: nm
    note: 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지
    source: knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §4.2
    confidence: literature
  damage_exponent:
    value: 1.44
    unit: "-"
    note: >
      US8439995B2(Hitachi 세리아) 4점 로그-로그 회귀 n=1.444, R²=0.997. 막질 일치
      (산화막 CMP)이나 연마입자 불일치(세리아 vs 콜로이달 실리카) — 조건 외삽.
      교차확증: Remsen 2006(퓸드실리카·산화막) Table V가 선형(n≈1)을 지지해 방향 일치.
      sim/factors.py 기본값 3.0은 문헌 근거 없는 가정값이므로 반드시 덮어쓴다.
    source: knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §4.3
    confidence: literature
```
</details>

<details>
<summary><code>knowledge/params/cu_h2o2_bta.yaml</code> — <code>abrasive_size_nm</code> 블록 뒤에 추가</summary>

```yaml
  # ── Δ 손상 유발도 (스크래치 위험) — 진단 전용, MRR에 곱해지지 않음 ──
  abrasive_d99_nm:
    value: 500.0
    unit: nm
    note: >
      abrasive_size_nm(100 nm) × D99/D50 일반비 5.00 유도값(Silco/Levitronix 2008).
      독립 상한 대조: Showa Denko US6770218B2(알루미나 + 질산철 금속 CMP, W·Cu 동일 슬러리)
      명세 "maximum grain size of 1.0 µm or less, more preferably 0.5 µm" — 이 유도값이
      선호 상한 0.5 µm와 정확히 경계 일치한다. 알루미나 D99 실측값은 5회 탐색 모두 실패
      (abrasive-d99-alumina-fourth-attempt-guo-nanoalumina.md §3) — 유도값임을 명심.
    source: knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §4.2
    confidence: literature
  abrasive_ref_d99_nm:
    value: 500.0
    unit: nm
    note: 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지
    source: knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §4.2
    confidence: literature
  damage_exponent:
    value: 2.54
    unit: "-"
    note: >
      Egan & Kim 2019(ECS JSS 8(5) P3206, GLOBALFOUNDRIES 300mm 양산) 두 관측
      n_temp=3.73 / n_agit=1.73의 기하평균(로그축 중앙). ⚠ 원 관측은 **텅스텐** 벌크 CMP다 —
      Cu로의 전이는 연마입자·촉매 계열 유사성(Showa Denko US6770218이 W Ex.1과 Cu Ex.9를
      동일 알루미나+질산철 슬러리로 다룸)에만 기댄다. Cu 막질에서 직접 측정된
      D99-스크래치 대응쌍은 확인하지 못했다 → confidence를 estimated로 강등.
    source: knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §4.3
    confidence: estimated
```
</details>

<details>
<summary><code>knowledge/params/w_fe_oxidizer.yaml</code> — <code>abrasive_size_nm</code>(L74~78) 블록 뒤에 추가</summary>

```yaml
  # ── Δ 손상 유발도 (스크래치 위험) — 진단 전용, MRR에 곱해지지 않음 ──
  # ⚠ Egan & Kim 2019 §3.4: 텅스텐 벌크 CMP에서 대입자는 **MRR을 올리지 않고 스크래치만**
  #   늘린다("the rate does not increase … statistically comparable"). Δ와 κ의 분리 설계가
  #   이 팩에서 특히 물리적으로 옳다.
  abrasive_d99_nm:
    value: 750.0
    unit: nm
    note: >
      abrasive_size_nm(150 nm) × D99/D50 일반비 5.00 유도값(Silco/Levitronix 2008).
      Showa Denko US6770218B2(알루미나 + 질산철 3.5wt% 텅스텐 CMP) 절대 상한 1.0 µm 이내,
      단 선호 상한 0.5 µm는 초과 ⚠. 참고: Remsen 2006 스크래치 임계 직경 680 nm(실리카
      등가)를 넘는 유일한 팩 — 이 팩의 꼬리가 임계 이상 대역에 있다는 진단 신호.
      알루미나 D99 실측값은 미확보(5회 탐색 실패).
    source: knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §4.2
    confidence: literature
  abrasive_ref_d99_nm:
    value: 750.0
    unit: nm
    note: 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지
    source: knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §4.2
    confidence: literature
  damage_exponent:
    value: 2.54
    unit: "-"
    note: >
      Egan & Kim 2019(ECS JSS 8(5) P3206) 두 관측의 기하평균 √(3.73×1.73).
      막질·공정 완전 일치(텅스텐 벌크 CMP, 300mm 양산 라인 defect inspection 실측).
      ⚠ 각 관측이 n=1 단일 대응쌍이고 저자 서술이 반올림("sixty times", "85% reduction")이라
      정밀도는 낮다 — 순위만 신뢰.
    source: knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md §4.3
    confidence: literature
```
</details>

## 6. 기대 결과와 검증 방법

| 항목 | 반영 전 | 반영 후 |
|---|---|---|
| `cu_h2o2_bta` Δ | `unmodeled` | `partial` / `unverified` |
| `oxide_silica` Δ | `unmodeled` | `partial` / `unverified` |
| `w_fe_oxidizer` Δ | `unmodeled` | `partial` / `unverified` |
| 기준 조건 Δ값 | (미계산) | **정확히 1.0** (3팩 전부) |
| MRR 예측 | — | **변화 없음** (delta ∉ MRR_COUPLED) |

`confidence`가 `unverified`로 나오는 것은 `_f_delta`가 하드코딩으로 그렇게 설정하기 때문이며
(L906), 실제 근거 수준(literature/estimated)과 별개다. D99가 유도값·n이 화학종 전이값이므로
**unverified가 정직한 등급**이다 — 이를 올리려 코드를 고치지 마라.

검증 명령(반영 담당자용):
```bash
cd ~/fab-sim
python tools/accuracy_gaps.py            # delta UNMODELED 갭 3건 해소 확인
python -m pytest tests/ -q               # 기준 조건 1.0 계약·회귀 테스트
python tools/check_knowledge.py          # 지식노트 verify 블록 실행(본 노트 포함)
```

## 7. 정직한 미해결 (반영 담당자가 알아야 할 것)

1. **알루미나 D99 절대 실측값은 여전히 없다 (5회 연속 실패).** Cu/W 두 팩의 D99는 유도값이다.
   공개 1차 문헌 탐색 공간은 사실상 소진 — 제조사 QC 스펙은 NDA 하에만 존재한다는 것이
   Evonik·Baikowski·Fujimi 조사에서 반복 확인됐다.
2. **Cu 막질 D99-스크래치 대응쌍이 없다.** `cu_h2o2_bta`의 n=2.54는 텅스텐 관측의 전이값이다.
3. **Fuso 특허는 출원인 화이트리스트 미등재**(patent_sources.py)라 방향성 근거로만 썼다.
   화이트리스트에 Fuso Chemical을 추가할지는 별도 판단 사항으로 남긴다(일본 초고순도
   콜로이달실리카 CMP 메이저이며 Tokuyama·Admatechs와 동급으로 보인다 — 담당자 판단).
4. **개수축(LPC) 미구현.** Fujifilm US10907074B2의 "LPC/wt% < 800,000 @0.2 µm bin" 임계는
   Remsen 2006이 실제로 측정한 축과 같고 D99보다 물리적으로 직접적이지만, 3팩 어디에도
   LPC 실측값이 없어 이번엔 넣지 않았다(§4.3).
