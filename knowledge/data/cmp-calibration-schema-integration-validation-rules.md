<!-- V2-SECTION: R-data | Cal-1 2026-09-20 | 근거: 4형제 스키마개정 통합·JSON Schema 2020-12·SEMI·검증규칙·버전관리 | 정본: ORG.md §7.3 -->
# Cal-1 — 서브에이전트 스키마 개정 통합 + 검증 규칙 + 버전 관리 (cmp-data-engineer, 통합 소유자)

> 에이전트: cmp-data-engineer Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-20
> 선행(재서술 금지·인용만):
> [[cmp-integration-schema-keys-semi-standards]](Lv1-2 — SEMI 계보 키 체계·엔터티, 이 노트가 통합의 뼈대로 계승),
> [[cmp-measurement-ingest-schema-standardization]](Lv3-2 — 최소 스키마 4범주·GUM 불확도·물리불가능값 게이트),
> [[wafer-coordinate-units-outlier-cleaning]](Lv2-1 — 좌표·단위 정준화, notch/EE),
> [[cmp-data-quality-gate-and-anonymization]](Lv3-1 — 게이트 정책·k-익명성),
> [[synthetic-data-generation-tier1-tier2-noise-model]](Lv2-2 — 합성 레코드 생성),
> [[cmp-public-datasets-survey]](Lv1-1 — 시계열형/표형 분리·출처 강제),
> [[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]](형제 Cal-1 — 계측 지표 정의·WIWNU 5종, **정의는 여기가 정본**),
> [[../cmp/wafer-type-npw-ptw-metadata-schema-alignment-rules]](형제 Cal-1 — NPW/PTW 메타·정렬 규칙),
> [[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]](형제 Cal-1 — 옥사이드 Kp·선택비·디싱 필드),
> [[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]](형제 Cal-1 — 슬러리 스펙시트 변환·측정가중),
> [[../cmp/preston-luo-dornfeld-mrr]](K=Kp·P·V 정의)

## 0. 목적·범위·형제 경계

ORG.md §7.3은 cmp-data-engineer에게 **"통합 스키마(`data/schema/*.json`)를 소유하고, 각 서브에이전트가
정의한 스키마를 통합·검증한다"**를 맡겼다 — 이 에이전트 자체가 **캘리브레이션 층의 데이터 기반**이다.
2026-09-19에 네 형제(wafer-metrology·wafer-type·film-oxide·slurry-abrasive)가 각자 Cal-1을 마치며 **자기
축의 스키마 개정을 제안**했다. 이 노트는 그 네 제안을 **한 표로 수집(§2)하고, 같은 뜻 다른 이름·충돌을
판정(§2.3)해 통합 필드명·타입·필수성·enum을 확정(§3)**하고, **검증 규칙(§4)·버전 관리(§6)**를 정하는
통합 산출물이다.

이 단원이 푸는 실제 문제: 네 형제가 **독립적으로** 필드를 제안했으므로 (a) 같은 개념을 다른 이름으로
부른 것(`pattern_density_rho` vs `local_density`), (b) 단위 표기 규약이 갈린 것(`pressure_kPa` 접미형 vs
`abrasive_conc_value`+`_unit` 쌍), (c) 파생 가능한 중복(`n_sites` = `len(points)`)이 섞여 있다. 이를
판정 없이 스키마에 다 넣으면 **같은 밀도가 두 필드에 따로 들어와 조인이 깨지고**, 캘리브레이터가 규약
차이를 팹 고유 편차로 오학습한다(형제 4편이 공통으로 경고한 그 문제의 스키마 레벨 버전).

**형제 경계 (침범 금지, 인용만):**
- **지표 정의**(WIWNU 5종·SFQR·조도 스캔크기)는 wafer-metrology 소관 — 이 노트는 그 enum을 **입력으로만**
  받고 재정의하지 않는다([[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]]).
- **막질별 파라미터 의미**(Kp 배율·도핑 화학·선택비 물리)는 film-* 소관 — 필드의 **존재·타입**만 통합하고
  값의 물리는 인용만([[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]]).
- **NPW/PTW 정렬·전이 물리**는 wafer-type, **입자 측정가중 변환식**은 slurry-abrasive 소관 — 인용만.
- **잔차 GP 피팅·불확실성**은 cmp-calibrator 소관. 이 노트는 "검증 통과한 정준 레코드"까지만 책임진다.
- **`sim/`·`data/schema/` 파일 직접 수정 금지**(사용자 지시) — §5 통합 스키마와 §4 검증기는 **개정 제안**
  이며 구현은 PROFILE.md 구현 요청으로 소프트웨어 부문에 넘긴다. 파일은 읽기만 했다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 모든 레코드는 **합성**이다.

## 1. 통합 스키마 설계의 1차 근거 — 규격·표준·시간·로트

통합 스키마의 **형식**은 이미 정해진 규격을 따르는 것이지 발명이 아니다. 근거는 셋이다.

### 1.1 JSON Schema draft 2020-12 (규격 문서, json-schema.org 공식)

현행 `wafer_measurement.schema.json`이 선언한 dialect가 이것이다(`"$schema":
"https://json-schema.org/draft/2020-12/schema"`, 파일 2행 직접 확인). 통합 스키마가 쓸 키워드의 정확한
의미론을 이 규격에서 확정한다(원문 확인 = **E2급 규격 1차**):

- **조건부 검증**: `if`/`then`/`else`(Core, Appendix A — "apply subschemas … and combine their results"),
  `allOf`(현행 스키마가 coord_kind 분기에 이미 사용, 파일 52–81행), **`dependentRequired`(§6.5.4 —
  "properties that are required if a specific other property is present. Their requirement is dependent on
  the presence of the other property")**. → PTW·zeta·wt% 같은 상호의존을 이 두 방식으로 표현(§4).
- **범위**: `minimum`(§6.2.4 "inclusive lower limit … greater than or exactly equal"),
  `exclusiveMinimum`(§6.2.5 "strictly greater than (not equal to)"). → 밀도 [0,1]은 minimum/maximum,
  압력·시간 >0은 exclusiveMinimum(=물리불가능값 게이트, [[cmp-measurement-ingest-schema-standardization]] §2 계승).
- **열거·상수**: `enum`(§6.1.2 "value MUST be an array … equal to one of the elements"),
  `const`(§6.1.3 "functionally equivalent to an enum with a single value"). → 막종류·구조물·측정가중 enum,
  coord_kind 분기의 const.
- **버전 선언**: dialect meta-schema URI가 draft를 선언(§5). 우리 스키마의 **payload 버전**은 별도
  `version` 필드로 관리한다(§6, 현행 "1.0.0").

### 1.2 시간 표기 — RFC 3339 §5.6 (= ISO 8601 profile)

JSON Schema의 `format: "date-time"`(§7.3.1)은 **"a valid representation according to the 'date-time' ABNF
rule … derived from RFC 3339, section 5.6"**로 정의된다(규격 원문). RFC 3339는 ISO 8601의 인터넷 프로파일
이다. 따라서 `timestamp`(공정 이벤트 CEID_start/end, [[cmp-integration-schema-keys-semi-standards]] §1.1
E30 CEID)는 **RFC 3339 date-time 문자열**로 강제한다 — 예 `2026-09-20T04:30:00Z`, 오프셋 `+09:00`, 윤초
`:60` 허용. 절대시각은 익명화 단계에서 상대시각으로 일반화([[cmp-data-quality-gate-and-anonymization]] §4).

### 1.3 SEMI 표준 — 로트·기판·다이·이벤트 식별과 명명 (Lv1-2 계승)

로트·기판·다이 식별 키는 [[cmp-integration-schema-keys-semi-standards]]가 SEMI 계보로 이미 확정했다
(재서술 금지, 인용만): **LotID**(MES)→**CarrierID**(E87)→**SubstrateID**(E90, 조인 중심축)→**Die/Site
(X,Y)**(E142), 공정 이벤트 **RecipeID**(E40/E94)·**CEID**(E30), 소모품 **ConsumableID**(특허 US10593574).
형제가 제안한 `wafer_lot`·`recipe_id`·`mask_id`·`slurry_pack_id`는 이 계보에 사상된다(§3.4). 웨이퍼 직경
enum은 SEMI M1(현행 스키마 150/200/300), 측정점 배치는 SEMI MF1618/ASTM F1618-02가 근거
([[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]] §1.2, 인용).

## 2. 네 형제 스키마 개정 제안 수집 — 한 표

각 형제 노트 §5/§6이 제안한 record 레벨 필드를 원문 그대로 옮긴다(값·근거는 각 노트 소유, 여기선 통합만).

### 2.1 제안 필드 원본 (출처 노트 §절)

| 형제 | 제안 필드(요약) | 출처 |
|---|---|---|
| **wafer-metrology** | `metric_definition`(enum 7), `measured_quantity`(enum 6), `scalar_wiwnu`, `n_sites`, `outermost_radius_mm`, `site_plan_name`, `notch_reference_angle_deg`, `site_size_mm`, `scan_size_um`, `value_uncertainty`+`coverage_k`, `stat_ddof` | [[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]] §5 |
| **wafer-type** | `wafer_type`(enum NPW/PTW), `film_stack`, `wafer_lot`, `recipe_id`, `mask_id`, `structure_type`(enum 6), `pitch_um`/`line_width_um`/`line_space_um`, `local_density`/`die_density_mean`, `block_size_mm`, `die_size_mm`, `planarization_length_mm` | [[../cmp/wafer-type-npw-ptw-metadata-schema-alignment-rules]] §5.1 |
| **film-oxide** | `film_type`(enum 8), `dopant_B_wt_pct`/`dopant_P_wt_pct`, `anneal_reflow`, `initial_thickness_nm`, `pressure_kPa`/`velocity_m_per_s`, `slurry_pack_id`, `stop_layer`(enum 3), `selectivity_oxide_over_stop`, `feature_width_um`/`pattern_density_rho`, `dishing_nm`/`erosion_nm`/`overpolish_time_s`, `is_reference_film` | [[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] §5 |
| **slurry-abrasive** | `abrasive_size_value`+`_basis`(enum 8)+`_method`(enum 6), `psd_sigma_g`|(`d50`,`d99`), `abrasive_conc_value`+`_unit`(enum 3), `abrasive_density_kg_m3`, `zeta_mv`, `zeta_ph`, `zeta_ionic_strength_mM`, `slurry_ph` | [[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]] §6 |

제안 필드 단순 합 = 12+14+16+11 = **53개**(§4-A assert).

### 2.2 관찰: §5/§6 제안 집합끼리는 문자그대로 겹치는 필드가 없다

네 노트가 **서로 다른 접두어**(`abrasive_*`, `dopant_*`, `zeta_*`)와 축별 이름을 써서, §5/§6 제안
집합의 교집합은 공집합이다(§4-A assert). 충돌은 **같은 뜻 다른 이름**(개념중복)으로만 온다 — 이게 통합의
실제 판정 대상이다. (`site_plan_name`은 wafer-metrology §5 소유이자 wafer-type §1.1 근거표가 인용하는
공유 필드라 단일화 대상이지만 §5.1 제안표엔 없다.)

### 2.3 개념중복·충돌 판정 (EVIDENCE-RULES는 근거서열용 — 여기선 소유권·정본 규칙으로 판정)

| # | 충돌/중복 | 두 이름 | 판정 (정본) | 근거 |
|---|---|---|---|---|
| 1 | 패턴밀도 | film-oxide `pattern_density_rho` / wafer-type `local_density`·`die_density_mean` | **`local_density`(국소)·`die_density_mean`(다이평균)으로 통합**. `pattern_density_rho` 흡수 — 디싱식의 ρ는 국소밀도다 | wafer-type이 NPW/PTW 축 소유·`ptw_vm_schema.py`에 이미 존재(원문 확인). film-oxide 디싱 D_ss(ρ)의 ρ=local_density |
| 2 | 구조물 폭 | film-oxide `feature_width_um` / wafer-type `line_width_um`·`line_space_um`·`pitch_um` | **Park 정의(pitch=lw+ls) 3필드 정본**. `feature_width_um`은 디싱 대상이 트렌치면 `trench_width_um`으로 명확화, 라인이면 `line_width_um` | wafer-type §1.2 Park 1999 정의가 1차. 이름만 다른 파생 |
| 3 | 측정점 수 | wafer-metrology `n_sites` / `points` 배열 | **`len(points)`에서 파생**. `n_sites`는 원 점 없는 스칼라 폴백에서만 명시 | 현행 스키마 `points` minItems=1(파일 48행). 중복 저장 금지 |
| 4 | 증착 초기두께 | film-oxide `initial_thickness_nm` / wafer-type `film_stack[].thickness_nm` | **`film_stack[].deposited_thickness_nm`으로 흡수**. 측정 두께(point value)와 구분 | 다층 스택이 상위 표현. 초기두께=스택 최상층 두께 |
| 5 | 막종류 표현 | film-oxide `film_type`(enum 8) / wafer-type `film_stack[].material` | **`film_stack[].material` enum 도메인으로 흡수**. 어느 layer가 연마대상/정지층인지 `role`로 | film_stack이 다층, film_type은 단층 뷰. stop_layer도 role=stop |
| 6 | 단위 표기 규약 | film-oxide 접미형 `pressure_kPa`/`velocity_m_per_s` / slurry-abrasive·기존 point `value`+`unit` 쌍 | **정준단위 접미형을 record 공정조건 정본**(`pressure_kpa`,`velocity_m_per_s`), 원값은 point 패턴처럼 `*_raw`+`*_unit_raw`로 보존 | 이 프로젝트는 normalize.py가 정준단위로 통일(가역 원칙, [[wafer-coordinate-units-outlier-cleaning]]). 스칼라 공정조건은 정준 고정이 조인·비교에 유리 |

**판정 원칙**: 축의 **소유 에이전트**가 정한 이름을 정본으로 채택하고(밀도=wafer-type, 지표정의=wafer-metrology),
다른 노트의 동의어를 흡수한다. **평균·병기 금지**(EVIDENCE-RULES §금지) — 같은 개념은 하나의 필드로 수렴.

## 3. 통합 스키마 확정 — 필드명·타입·필수성·enum

§2.3 판정을 반영한 통합 record. **현행 6개 required는 불변**(하위호환, §6), 아래는 **추가** 필드다.
필수성은 조건부(§4 if/then·dependentRequired)로 표현한다.

### 3.1 웨이퍼·식별 (SEMI 계보, §1.3)

| 통합 필드 | 타입/enum | 필수성 | 소유 |
|---|---|---|---|
| `wafer_type` | enum `NPW`/`PTW` | **필수(구분 키)** | wafer-type |
| `wafer_lot` | string | 권고 | wafer-type (LotID) |
| `recipe_id` | string | 필수 | wafer-type (E40) |
| `slurry_pack_id` | string | 권고 | film-oxide (ConsumableID:slurry_lot) |
| `timestamp` | string(format date-time, RFC3339) | 권고 | 이 노트 §1.2 (E30 CEID) |
| `film_stack` | array of `{material(enum), method, deposited_thickness_nm, role∈{polish/stop/barrier}, dopant_B_wt_pct?, dopant_P_wt_pct?}` | 권고 | 통합(#4·#5 흡수) |
| `anneal_reflow` | bool | 권고 | film-oxide |
| `pressure_kpa`, `velocity_m_per_s` | number(exclusiveMinimum 0) | film_type/Kp 보정 시 필수 | film-oxide(#6 정준) |

### 3.2 계측 지표 (정의는 wafer-metrology 정본, 여기선 필드만)

| 통합 필드 | 타입/enum | 필수성 |
|---|---|---|
| `metric_definition` | enum `wiwnu_3sigma`/`wiwnu_1sigma`/`cv`/`halfrange`/`fullrange`/`range_over_sum`/`raw_points_only` | 사전계산 스칼라면 필수 |
| `measured_quantity` | enum `post_thickness`/`pre_thickness`/`amount_removed`/`removal_rate`/`dishing`/`roughness` | 필수 |
| `scalar_wiwnu` | number\|null | 원 점 없을 때만 |
| `outermost_radius_mm` | number | range형 스칼라면 필수 |
| `site_plan_name`, `notch_reference_angle_deg`, `site_size_mm`, `stat_ddof` | (wafer-metrology §5 그대로) | 권고 |
| `scan_size_um` | number | `measured_quantity=roughness`면 필수 |
| `value_uncertainty`+`coverage_k` | number(point 레벨) | 권고 (GUM, [[cmp-measurement-ingest-schema-standardization]] §1) |

`n_sites`는 흡수(§2.3 #3, `len(points)` 파생, 스칼라 폴백만).

### 3.3 패턴(PTW) — wafer-type 정본

| 통합 필드 | 타입/enum | 필수성 |
|---|---|---|
| `mask_id`, `structure_type`(enum `density`/`pitch`/`kelvin`/`serpentine`/`comb`/`blanket`) | string/enum | `wafer_type=PTW`면 필수 |
| `local_density`, `die_density_mean` | number [0,1] | PTW면 필수(유효 MRR용, #1 흡수) |
| `pitch_um`,`line_width_um`,`line_space_um`,`trench_width_um` | number | PTW·구조물면 권고(#2) |
| `block_size_mm`,`die_size_mm`,`planarization_length_mm` | array/number | PTW면 권고 |
| `selectivity_oxide_over_stop`,`dishing_nm`,`erosion_nm`,`overpolish_time_s` | number\|null | 디싱/선택비 보고 시(film-oxide) |
| `feature_width_um` | — | **흡수**(#2 → line_width_um/trench_width_um) |
| `is_reference_film` | bool | 권고 (절대 Kp 식별 게이트) |

### 3.4 슬러리 스펙 (slurry-abrasive 정본, 별도 `slurry_spec` 객체 권장)

| 통합 필드 | 타입/enum | 필수성 |
|---|---|---|
| `abrasive_size_value`+`abrasive_size_basis`(enum 8)+`abrasive_size_method`(enum 6) | number/enum | value 필수, basis 필수 |
| `psd_sigma_g` 또는 (`d50`,`d99`) | number | 권고 |
| `abrasive_conc_value`+`abrasive_conc_unit`(enum `wt_pct`/`vol_pct`/`g_per_L`) | number/enum | 필수 |
| `abrasive_density_kg_m3` | number | `abrasive_conc_unit=wt_pct`면 필수 |
| `zeta_mv`,`zeta_ph`,`zeta_ionic_strength_mM`,`slurry_ph` | number | zeta면 zeta_ph 필수 |

## 4. Python 검증 — 통합 판정·검증기·JSON Schema 의미론·버전관리

**재현 요약(한 줄)**: (A) 4형제 제안필드 53개→통합 49개(§5/§6 문자중복 0·개념중복 5쌍 중 4개 record 흡수)
·단위규약 2종 공존을 집합으로 판정; (B) 표준 라이브러리만의 검증기로 합성 6레코드(정상3·위반3)가 의도대로
갈림; (C) JSON Schema 2020-12 키워드(dependentRequired§6.5.4·minimum§6.2.4·exclusiveMinimum§6.2.5·
const§6.1.3·if/then·date-time§7.3.1=RFC3339) 순수파이썬 재현이 spec 정의와 일치; (D) semver 하위호환
(optional추가=minor·구레코드 통과 / required추가=major·구레코드 반려→마이그레이션). 4블록 assert PASS.

**문헌값 대조**: [B] 검증기의 정상 레코드는 형제 노트가 이미 확정한 1차 문헌값을 그대로 입력으로
**대조·재현**한다 — 압력 20.7 kPa·속도 0.8 m/s(oxide_silica 팩 캘리브레이션점, film-oxide §4),
최외곽반경 147 mm(NIST Griesmann 2007 EE 3 mm → 유효반경, DOI:10.1063/1.2799352),
입자밀도 2200 kg/m³(비정질 실리카, slurry-abrasive §2 R2 DOI:10.1016/s0016-0032(29)91451-4 환산계),
제타 −63 mV @pH 8.1(Seo 2021, slurry-abrasive §1 S5). 이 문헌값들이 통합 스키마 필드에 담겨 정상
판정을 받고, 물리불가능값(압력 −5.0 kPa)·범위이탈(밀도 1.7)은 반려됨을 assert로 확인한다.

```python verify
import numpy as np
# ═══ (A) 4형제 §5/§6 제안 record 필드를 집합으로 놓고 중복·충돌 판정 ═══
metrology = {"metric_definition","measured_quantity","scalar_wiwnu","n_sites",
    "outermost_radius_mm","site_plan_name","notch_reference_angle_deg",
    "site_size_mm","scan_size_um","value_uncertainty","coverage_k","stat_ddof"}
wtype = {"wafer_type","film_stack","wafer_lot","recipe_id","mask_id","structure_type",
    "pitch_um","line_width_um","line_space_um","local_density","die_density_mean",
    "block_size_mm","die_size_mm","planarization_length_mm"}
oxide = {"film_type","dopant_B_wt_pct","dopant_P_wt_pct","anneal_reflow","initial_thickness_nm",
    "pressure_kPa","velocity_m_per_s","slurry_pack_id","stop_layer",
    "selectivity_oxide_over_stop","feature_width_um","pattern_density_rho",
    "dishing_nm","erosion_nm","overpolish_time_s","is_reference_film"}
abrasive = {"abrasive_size_value","abrasive_size_basis","abrasive_size_method","psd_sigma_g",
    "abrasive_conc_value","abrasive_conc_unit","abrasive_density_kg_m3",
    "zeta_mv","zeta_ph","zeta_ionic_strength_mM","slurry_ph"}
# §5/§6 제안집합끼리 문자그대로 겹치는 필드 없음 → 충돌은 '같은뜻 다른이름'으로만
assert (metrology & wtype)==set() and (metrology & oxide)==set() and (wtype & oxide)==set()
assert "site_plan_name" in metrology              # metrology §5 소유(공유 단일화 대상)
concept_dupes = {("pattern_density_rho","local_density"),
                 ("feature_width_um","line_width_um|trench_width_um"),
                 ("n_sites","len(points)"),
                 ("initial_thickness_nm","film_stack[].deposited_thickness_nm"),
                 ("film_type","film_stack[].material(enum)")}
assert len(concept_dupes)==5
suffix_unit = {"pressure_kPa","velocity_m_per_s","initial_thickness_nm","scan_size_um"}
assert suffix_unit & oxide == {"pressure_kPa","velocity_m_per_s","initial_thickness_nm"}
assert ("abrasive_conc_value" in abrasive) and ("abrasive_conc_unit" in abrasive)
raw_sum = len(metrology)+len(wtype)+len(oxide)+len(abrasive)
unified = raw_sum - 4                              # record서 흡수: pattern_density_rho·feature_width_um·n_sites·initial_thickness_nm
assert raw_sum==12+14+16+11==53 and unified==49
print(f"[A] 제안필드합 {raw_sum} → 통합 {unified}개 (문자중복 0·개념중복 5쌍 중 4개 흡수·단위규약 2종 공존)")
```

```python verify
import re
# ═══ (B) 통합 스키마 검증기 — 표준 라이브러리만(jsonschema 미사용) ═══
WAFER_TYPE={"NPW","PTW"}
METRIC_DEF={"wiwnu_3sigma","wiwnu_1sigma","cv","halfrange","fullrange","range_over_sum","raw_points_only"}
RANGE_DEFS={"halfrange","fullrange","range_over_sum"}
MEASURED_Q={"post_thickness","pre_thickness","amount_removed","removal_rate","dishing","roughness"}
_DT=re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")
def is_rfc3339(s):
    if not isinstance(s,str) or not _DT.match(s): return False
    mo,d=int(s[5:7]),int(s[8:10]); h,mi,se=int(s[11:13]),int(s[14:16]),int(s[17:19])
    return 1<=mo<=12 and 1<=d<=31 and h<=23 and mi<=59 and se<=60      # se=60 윤초 허용
def validate(r):
    e=[]
    if r.get("wafer_type") not in WAFER_TYPE: e.append("wafer_type enum")
    if "metric_definition" in r and r["metric_definition"] not in METRIC_DEF: e.append("metric_definition enum")
    if "measured_quantity" in r and r["measured_quantity"] not in MEASURED_Q: e.append("measured_quantity enum")
    if "timestamp" in r and not is_rfc3339(r["timestamp"]): e.append("timestamp not RFC3339/ISO8601")
    for k in ("pressure_kpa","velocity_m_per_s","time_s"):
        if r.get(k) is not None and r[k]<=0: e.append(f"{k}<=0 invalid")   # exclusiveMinimum
    for k in ("local_density","die_density_mean"):
        if r.get(k) is not None and not (0.0<=r[k]<=1.0): e.append(f"{k} out of [0,1]")
    if r.get("wafer_type")=="PTW":
        for k in ("mask_id","structure_type","local_density"):
            if r.get(k) is None: e.append(f"PTW requires {k}")
    if r.get("metric_definition") in RANGE_DEFS and not r.get("points"):
        if r.get("outermost_radius_mm") is None: e.append("range-scalar requires outermost_radius_mm")
    if r.get("measured_quantity")=="roughness" and r.get("scan_size_um") is None:
        e.append("roughness requires scan_size_um")
    if r.get("zeta_mv") is not None and r.get("zeta_ph") is None: e.append("zeta_mv requires zeta_ph")
    if r.get("abrasive_conc_unit")=="wt_pct" and r.get("abrasive_density_kg_m3") is None:
        e.append("wt_pct requires abrasive_density_kg_m3")
    if r.get("film_type") is not None and (r.get("pressure_kpa") is None or r.get("velocity_m_per_s") is None):
        e.append("Kp unidentifiable: film_type without pressure/velocity")
    return e
ok1={"wafer_type":"NPW","timestamp":"2026-09-20T04:30:00Z","metric_definition":"wiwnu_3sigma",
     "measured_quantity":"post_thickness","film_type":"PECVD_TEOS","pressure_kpa":20.7,
     "velocity_m_per_s":0.8,"points":[{"value":480.0,"unit":"nm"}]}
ok2={"wafer_type":"PTW","timestamp":"2026-09-20T04:31:00.5+09:00","mask_id":"MIT854",
     "structure_type":"density","local_density":0.5,"measured_quantity":"dishing",
     "recipe_id":"R1","points":[{"value":40.0,"unit":"nm"}]}
ok3={"wafer_type":"NPW","timestamp":"2026-01-01T00:00:60Z","metric_definition":"fullrange",
     "measured_quantity":"removal_rate","scalar_wiwnu":3.4,"outermost_radius_mm":147.0,
     "abrasive_conc_unit":"wt_pct","abrasive_density_kg_m3":2200.0,"zeta_mv":-63.0,"zeta_ph":8.1}
bad1={"wafer_type":"PTW","timestamp":"2026-09-20T04:30:00Z","measured_quantity":"dishing",
      "local_density":1.7,"points":[{"value":40.0,"unit":"nm"}]}
bad2={"wafer_type":"NPW","timestamp":"2026-13-40T99:99:99Z","metric_definition":"halfrange",
      "measured_quantity":"post_thickness","scalar_wiwnu":2.1}
bad3={"wafer_type":"NPW","timestamp":"2026-09-20T04:30:00Z","film_type":"HDP",
      "pressure_kpa":-5.0,"measured_quantity":"roughness"}
assert validate(ok1)==[] and validate(ok2)==[] and validate(ok3)==[]
e1,e2,e3=validate(bad1),validate(bad2),validate(bad3)
assert any("PTW requires mask_id" in x for x in e1) and any("[0,1]" in x for x in e1)
assert any("RFC3339" in x for x in e2) and any("outermost_radius" in x for x in e2)
assert any("pressure_kpa<=0" in x for x in e3) and any("unidentifiable" in x for x in e3) and any("scan_size_um" in x for x in e3)
assert is_rfc3339("2026-01-01T00:00:60Z") and not is_rfc3339("2026-13-40T99:99:99Z")
print(f"[B] 정상 3건 통과·위반 3건 반려 (위반사유수 {list(map(len,(e1,e2,e3)))})")
```

```python verify
import re
# ═══ (C) JSON Schema 2020-12 키워드 의미론을 순수파이썬으로 재현 → spec 정의와 일치 ═══
def dependent_required(inst, dep):                # §6.5.4
    return [(t,req) for t,reqs in dep.items() if t in inst for req in reqs if req not in inst]
dep={"zeta_mv":["zeta_ph"]}
assert dependent_required({"foo":1},dep)==[]                       # trigger 없으면 요구 안 함
assert dependent_required({"zeta_mv":-63.0},dep)==[("zeta_mv","zeta_ph")]
assert dependent_required({"zeta_mv":-63.0,"zeta_ph":8.1},dep)==[]
assert (0.0>=0.0) and not (-1e-9>=0.0)            # minimum §6.2.4 inclusive
assert not (0.0>0.0) and (1e-9>0.0)               # exclusiveMinimum §6.2.5 exclusive
assert ("PTW"=="PTW")==("PTW" in ["PTW"])         # const §6.1.3 ≡ 단일원소 enum
def if_then(inst):                                # if/then (Core, Appendix A)
    return [k for k in ("mask_id","structure_type","local_density")
            if inst.get("wafer_type")=="PTW" and k not in inst]
assert if_then({"wafer_type":"NPW"})==[]
assert set(if_then({"wafer_type":"PTW"}))=={"mask_id","structure_type","local_density"}
_DT=re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")
assert _DT.match("2026-09-20T04:30:00Z") and not _DT.match("2026-09-20 04:30:00")   # §7.3.1=RFC3339
print("[C] dependentRequired§6.5.4·minimum§6.2.4·exclusiveMinimum§6.2.5·const§6.1.3·if/then·date-time§7.3.1 모두 일치")
```

```python verify
import re
# ═══ (D) 스키마 버전관리·마이그레이션 하위호환 (semver, 현행 version="1.0.0") ═══
def parse(s):
    m=re.match(r"^(\d+)\.(\d+)\.(\d+)$",s); assert m,s
    return tuple(int(x) for x in m.groups())
def bump(old,kind):
    M,m,p=parse(old)
    return {"major":f"{M+1}.0.0","minor":f"{M}.{m+1}.0","patch":f"{M}.{m}.{p+1}"}[kind]
CUR="1.0.0"; assert parse(CUR)==(1,0,0)
def validate_minimal(rec, required): return [k for k in required if k not in rec]
req_v1={"wafer_id","wafer_diameter_mm","notch_direction","edge_exclusion_mm","coord_kind","points"}
old={"wafer_id":"W1","wafer_diameter_mm":300,"notch_direction":"Bottom",
     "edge_exclusion_mm":3.0,"coord_kind":"polar","points":[{"value":480,"unit":"nm"}]}
# 규칙①: optional 필드 추가=하위호환=MINOR. 구레코드가 그대로 통과
assert validate_minimal(old, req_v1)==[] and bump(CUR,"minor")=="1.1.0"
# 규칙②: required 추가=하위호환 깨짐=MAJOR. 구레코드 반려
req_v2=req_v1|{"wafer_type"}
assert validate_minimal(old, req_v2)==["wafer_type"] and bump(CUR,"major")=="2.0.0"
# 규칙③: 마이그레이션 — wafer_type 미기재 구레코드에 안전기본값(NPW) 주입 + 버전스탬프
def migrate(rec, from_v, to_v):
    r=dict(rec)
    if parse(to_v)[0]>=2 and "wafer_type" not in r:
        r["wafer_type"]="NPW"; r["_migrated_from"]=from_v
    r["_schema_version"]=to_v; return r
mig=migrate(old,CUR,"2.0.0")
assert mig["wafer_type"]=="NPW" and mig["_migrated_from"]=="1.0.0" and validate_minimal(mig,req_v2)==[]
print(f"[D] semver {CUR}: optional추가→1.1.0(구레코드 통과)·required추가→2.0.0(구레코드 반려→마이그레이션 후 통과)")
```

**결과 해석(정직하게)**
- [A]는 **네 형제 노트 §5/§6 제안필드에 대한 집합 연산**이다 — 문헌 재현이 아니라 통합 판정의 산술
  근거(정직 표지). 필드 목록은 각 노트 원문에서 그대로 옮겼다.
- [B]의 검증기는 **표준 라이브러리만으로 직접 구현**했다(`jsonschema` 4.25.1이 `.venv`에 설치돼 있으나
  이식성과 자립 검증을 위해 미사용). RFC3339 파서는 **구조·범위만 검사하는 부분구현**이고 완전한 ABNF가
  아니다(§7 정직표지) — 윤초·오프셋만 대표적으로 확인했다.
- [C]는 JSON Schema 2020-12 **규격 정의를 파이썬 진리값으로 재현**한 것이다. spec 자체를 재실행한 게
  아니라 정의(§6.5.4·§6.2.4·§6.2.5·§6.1.3·§7.3.1)를 코드로 옮겨 의미가 일치함을 보인 것이다.
- [D]의 semver 규칙(optional=minor·required=major)은 **SemVer 2.0.0 관례**를 스키마 payload에 적용한
  것이다 — 이 관례 자체는 이 노트의 운영 규약이지 CMP 문헌값이 아니다(§7 정직표지). 현행 `version`
  "1.0.0"과 `ingest.py`의 `schema.get("version")` provenance 기록(원문 확인, 173·208행)이 이 규칙의 실장 지점.

## 5. `data/schema/wafer_measurement.schema.json` 통합 개정 제안 (소프트웨어 부문 인계 — 파일 직접수정 금지)

§3 통합 필드를 현행 스키마에 얹는 방식. **현행 6 required·point 구조·allOf coord_kind 분기는 불변**(하위호환).

1. **record 최상위 추가**: §3.1~3.3 필드를 `properties`에 추가하되 전부 optional(하위호환, §6 규칙①).
   `wafer_type`만 다음 major(2.0.0)에서 required 승격 후보(§6 규칙②·마이그레이션).
2. **조건부 필수성은 `allOf`의 if/then + `dependentRequired`로**(§1.1, §4-C 재현):
   - `if wafer_type=PTW then required:[mask_id,structure_type,local_density]`
   - `dependentRequired:{zeta_mv:[zeta_ph], abrasive_conc(wt_pct 분기): if/then으로 abrasive_density_kg_m3}`
   - `if measured_quantity=roughness then required:[scan_size_um]`
   - `if metric_definition∈range형 and not points then required:[outermost_radius_mm]`
3. **범위 제약**: `local_density`·`die_density_mean` `minimum:0,maximum:1`; `pressure_kpa`·`velocity_m_per_s`
   `exclusiveMinimum:0`([[cmp-measurement-ingest-schema-standardization]] §2 물리불가능값과 정합).
4. **시간**: `timestamp` `type:string, format:"date-time"`(§1.2). format-assertion vocabulary 채택 시
   실검증, 아니면 annotation — [B]식 파서로 ingest 단계 보강.
5. **slurry_spec**: §3.4를 별도 객체(`slurry_spec`)로 중첩 — record가 계측/공정/슬러리 3영역으로 커지므로
   슬러리 스펙은 서브객체로 응집(slurry-abrasive §6 "별도 slurry_spec 객체" 제안 채택).
6. **버전**: `version`을 "1.0.0"→"1.1.0"(optional 추가, §6). `$defs`에 `film_stack_layer`·`slurry_spec` 정의.

## 6. 스키마 버전 관리·마이그레이션 규칙 (제안)

현행 스키마는 `version:"1.0.0"` 필드를 가지고 `ingest.py`가 이를 provenance에 기록한다(원문 확인). 규칙:

- **SemVer 2.0.0을 payload 스키마에 적용**(§4-D):
  - **PATCH**(1.0.x): 설명·주석·비제약 메타 변경. 검증 동작 불변.
  - **MINOR**(1.x.0): **optional 필드 추가, enum 값 추가**(기존 값 유지). **하위호환** — 구 버전 레코드가
    새 스키마로 그대로 통과. §5의 통합 추가는 전부 여기(1.0.0→1.1.0).
  - **MAJOR**(x.0.0): **required 추가, enum 값 삭제, 타입 변경, 필드 rename**. 하위호환 깨짐 — 구 레코드는
    **마이그레이션 필요**. `wafer_type` required 승격이 대표 사례(→2.0.0).
- **마이그레이션 함수**(§4-D `migrate`): 구 레코드에 (a) 안전 기본값 주입(`wafer_type` 미기재 → `NPW`=
  블랭킷 가정, 문서화된 규칙), (b) `_migrated_from`·`_schema_version` 스탬프. **원본 파기 전 마이그레이션
  로그 보존**([[cmp-data-quality-gate-and-anonymization]] 원칙과 정합).
- **검증 시점 버전 기록**: `ingest.py`가 이미 `schema_version`을 IngestResult·parquet 메타에 남긴다 —
  어떤 레코드가 어느 스키마 버전으로 검증됐는지 추적 가능(회귀·재검증의 근거). 이건 이미 구현돼 있어
  **추가 요청 아님**(원문 확인, ingest.py 173·208행).

## 7. 남은 미확보·미검증 (정직성 표기)

- **JSON Schema 2020-12 Core 문서**(if/$id/$ref 상세)는 Validation 문서만 원문 확인했고 Core는 Validation의
  Appendix A 참조로만 확인했다(E2 vs E3). §4-C의 if/then 재현은 의미론 수준이지 Core ABNF 완전 대조가 아니다.
- **RFC3339 date-time ABNF 완전 구현 아님**(§4-B/C): 정규식+범위검사로 구조·윤초·오프셋만 검사한다.
  일수 상한(30/31/윤년)·타임존 실범위 등 완전 검증은 미구현 — ingest 단계에서 `datetime.fromisoformat`류로
  보강 필요(단 Python 3.9 `fromisoformat`은 `Z`·윤초 미지원이라 별도 파서 필요, 미해결 한계).
- **SemVer·MINOR/MAJOR 경계 규칙은 운영 관례**(§4-D 정직표지)이지 CMP 문헌값이 아니다. `prior.py`의
  σ_log 규약이 "미검증 운영 규약"인 것과 같은 지위.
- **통합 필드값의 실제 캘리브레이션 성능은 미시연**이다. 이 노트는 **스키마 통합·검증·버전**까지만
  책임진다 — 잔차 GP 학습·불확실성은 cmp-calibrator 소관(ORG.md §7.3).
- **§2.3 판정은 소유권·정본 규칙**(축 소유 에이전트 이름 채택)이지 EVIDENCE-RULES 근거서열 판정이 아니다 —
  네 형제 필드는 값 충돌이 아니라 명명 중복이라 서열이 아니라 정본화로 해소된다(새 판정표 항목 없음).
- **SEMI 표준 원문 미열람**(Lv1-2에서 이미 밝힘): E5/E30/E90/E142/E40/E87/E10 식별자 의미는 벤더
  기술문서 교차확인한 표준 통설(E5급 일부 포함). MF1618·M1은 스코프·초록만(형제 노트 §1 인용).

## 8. 결론 (Cal-1 답)

1. **네 형제 §5/§6 제안필드 53개는 §5/§6 집합끼리 문자중복이 없고, 충돌은 전부 '같은 뜻 다른 이름'**이다
   (§2.2). 개념중복 5쌍을 축 소유 에이전트의 이름으로 정본화(밀도=`local_density`, 폭=Park 정의,
   `n_sites`=`len(points)` 파생, 초기두께·막종류=`film_stack` 흡수) → 통합 record 49개(§2.3·§4-A).
2. **단위 표기 규약 2종**(접미형 vs value+unit 쌍)은 공정조건은 정준단위 접미형, 원값은 `*_raw` 보존으로
   통일(§2.3 #6, normalize.py 가역 원칙 계승).
3. **검증 규칙은 JSON Schema 2020-12로 표현 가능**: 상호의존은 `if/then`·`dependentRequired`(§6.5.4),
   범위는 `minimum`/`exclusiveMinimum`, 시간은 `format:date-time`(§7.3.1=RFC3339=ISO8601). 표준
   라이브러리만의 검증기가 합성 6레코드를 정상3·위반3으로 갈랐다(§4-B).
4. **버전 관리는 SemVer**: optional 추가=MINOR(하위호환·구레코드 통과), required 추가=MAJOR(마이그레이션
   필요). `ingest.py`가 `schema_version`을 이미 provenance에 기록한다(§6·§4-D).
5. 통합 스키마·검증기·마이그레이션 구현은 **소프트웨어 부문 인계**(§5, PROFILE 구현 요청) — 파일 무수정.

## 9. 구현 요청
→ agents/cmp-data-engineer/PROFILE.md "## 구현 요청 (2026-09-20, Cal-1)" 참조.

## 10. 자기시험
→ agents/cmp-data-engineer/EXAMS.md Cal-1 문항 참조.

## 상호링크
[[cmp-integration-schema-keys-semi-standards]] [[cmp-measurement-ingest-schema-standardization]]
[[wafer-coordinate-units-outlier-cleaning]] [[cmp-data-quality-gate-and-anonymization]]
[[synthetic-data-generation-tier1-tier2-noise-model]] [[cmp-public-datasets-survey]]
[[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]]
[[../cmp/wafer-type-npw-ptw-metadata-schema-alignment-rules]]
[[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]]
[[../cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules]]
[[../cmp/preston-luo-dornfeld-mrr]]
