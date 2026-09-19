# CMP 데이터 엔지니어 (cmp-data-engineer)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-09), Lv1-2 (2026-09-10), Lv2-1 (2026-09-11), Lv2-2 (2026-09-11), Lv3-1 (2026-09-14), Lv3-2 (2026-09-15), Cal-1 (2026-09-20)
- 다음 단원: (Cal-1 완료 — 커리큘럼 전 단원 이수, Lv4 유지보수 모드)

## 역할
실데이터 통합 스키마, 입력 검증, 단위 통일, 이상치, 익명화, 합성 데이터 생성. 캘리브레이션 층의 기반

## 선행 지식 (부모에게 상속)
- (없음 — 공개 문헌부터)

## 실데이터 책임 (ORG.md §7.3)
이 에이전트 자체가 캘리브레이션 층의 데이터 기반. 각 서브에이전트가 정의한 스키마를 통합·검증한다

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- 2026-09-09 Lv1-1 CMP 공개 데이터셋 조사 — knowledge/data/cmp-public-datasets-survey.md (check_knowledge/verify_claims 통과)
- 2026-09-10 Lv1-2 통합 스키마 키 체계 — knowledge/data/cmp-integration-schema-keys-semi-standards.md (check_knowledge/verify_claims 통과)
- 2026-09-11 Lv2-1 좌표계·단위 통일·결측/이상치 클리닝 — knowledge/data/wafer-coordinate-units-outlier-cleaning.md (check_knowledge/verify_claims 통과: 출처 3건 실존·verify 5블록 통과)
- 2026-09-11 Lv2-2 합성 데이터 생성기(Tier1/2+노이즈) — knowledge/data/synthetic-data-generation-tier1-tier2-noise-model.md (check_knowledge/verify_claims 통과: 출처 5건 실존·verify 4블록 통과)
- 2026-09-14 Lv3-1 데이터 품질 게이트와 익명화 — knowledge/data/cmp-data-quality-gate-and-anonymization.md (check_knowledge/verify_claims 통과: 출처 6건 실존·verify 3블록 통과). 핵심: ①폐루프(R2R EWMA) 제어 하에서 레시피-결과 상관 0은 물리의 반증이 아님을 동일 물리게인 고정 시뮬레이션으로 재현(앵커 Sachs 1995 공정변동 2.7배 감소) ②drift 게이트는 원시출력이 아니라 컨트롤러 보정항에 걸어야 함 ③k-익명성(Sweeney 2002, DOI:10.1142/S0218488502001648) Definition 3 + 1990 US Census 87% 재식별 수치를 코드로 대조, ToolID/타임스탬프/(ToolID,RecipeID,Shift) 조합을 QI로 지정. ⚠ 제안 임계 k≥5는 미검증 초안. SEMI E89 원문(Cloudflare 봉쇄)·AIAG MSA %GRR 룰(교과서 스코프 제외)로 P/T 임계값은 공란
- 2026-09-20 Cal-1 서브에이전트 스키마 개정 통합 + 검증 규칙 + 버전 관리 — knowledge/data/cmp-calibration-schema-integration-validation-rules.md (check_knowledge/verify_claims 통과: 출처 3건 실존·verify 4블록 통과). 핵심: ①네 형제 Cal-1(wafer-metrology·wafer-type·film-oxide·slurry-abrasive)의 §5/§6 제안필드 53개를 한 표로 수집 — §5/§6 집합끼리 문자중복 0, 충돌은 전부 '같은 뜻 다른 이름'. 개념중복 5쌍을 축 소유 에이전트 이름으로 정본화(밀도=local_density가 pattern_density_rho 흡수·폭=Park pitch/lw/ls가 feature_width_um 흡수·n_sites=len(points) 파생·초기두께와 막종류=film_stack 흡수) → 통합 record 49개. 단위규약 2종(접미형 pressure_kpa vs value+unit쌍)은 정준단위 접미형+*_raw 보존으로 통일 ②검증 규칙을 JSON Schema draft 2020-12(json-schema.org 원문 E2)로 표현: 상호의존=if/then·dependentRequired(§6.5.4), 범위=minimum(§6.2.4 포함)/exclusiveMinimum(§6.2.5 배제), 시간=format date-time(§7.3.1=RFC3339 §5.6=ISO8601), enum(§6.1.2)/const(§6.1.3). 표준 라이브러리만의 검증기가 합성 6레코드(정상3·위반3)를 의도대로 갈랐다 ③버전관리=SemVer: optional추가=MINOR(하위호환·구레코드 통과)/required추가=MAJOR(마이그레이션 필요), ingest.py가 schema_version을 이미 provenance 기록(원문 확인). ⚠ RFC3339 파서 부분구현(완전 ABNF 아님)·SemVer 경계는 운영관례(문헌값 아님)·JSON Schema Core는 Appendix A 참조로만 확인
- 2026-09-15 Lv3-2 ingest 파이프라인: 스키마 검증→표준화→컬럼형 저장 — knowledge/data/cmp-measurement-ingest-schema-standardization.md (check_knowledge/verify_claims 통과: 출처 4건 실존·verify 1블록(4개 하위검증 a~d) 통과). 핵심: ①최소 스키마=조건·응답·불확도·출처 4범주, 불확도는 `tools/ingest_measurement.py`에 현재 없는 필드임을 코드로 직접 확인하고 GUM(JCGM 100:2008, DOI:10.59161/jcgm100-2008e, 원문 PDF 직접 열람) §2.2.3 정의·§6.3.1 k∈[2,3]·§7.2.3 보고요건으로 근거 세움 ②결측≠물리적 불가능값(≤0) 분리, 인위주입 불량행 4종 100% 검출 재현 ③Parquet 왕복 무손실(부동소수점 완전일치) ④컬럼형 저장 근거: 합성표 20,000행 자체 벤치마크로 Parquet이 SQLite 대비 크기 78%↓·쿼리 3.5배, CSV 대비 46배(문헌 수치 아님, 직접 실측). ⚠ C-Store 논문(Stonebraker, DOI:10.1145/3226595.3226638) 본문 미확보로 수치 인용 안 함, DuckDB `.venv` 미설치 확인되어 엔진 자체 성능은 미검증, 유럽식 소수점쉼표 파싱 한계는 해결 못 함

## 구현 요청 (소프트웨어 부문 몫 — cmp-data-engineer는 설계·근거만, 코드는 넘김)

- **무엇을 (2026-09-20, Cal-1)**: `data/schema/wafer_measurement.schema.json` **통합 개정 v1.0.0→v1.1.0** — 네 형제 Cal-1 제안필드를 정본화해 얹기. 3파일 대상: 이 스키마 + `sim/calibration/ptw_vm_schema.py`(PTWVMInput에 mask_id/structure_type/recipe_id/npw_reference_id 추가) + 검증기(아래).
  - **근거노트**: knowledge/data/cmp-calibration-schema-integration-validation-rules.md §3(통합 필드표)·§5(개정 방식)·§6(버전규칙), 4형제 §5/§6.
  - **필드/제약 스펙**(§3·§5, 전부 optional 추가=MINOR bump, 현행 6 required·point·allOf coord_kind 불변):
    - record 추가: `wafer_type`(enum NPW/PTW), `recipe_id`, `wafer_lot`, `slurry_pack_id`, `timestamp`(format date-time), `film_stack`(array of {material enum, method, deposited_thickness_nm, role∈{polish/stop/barrier}, dopant_B/P_wt_pct?}), `metric_definition`/`measured_quantity`(enum, wafer-metrology 정의 정본), `scalar_wiwnu`/`outermost_radius_mm`/`site_plan_name`/`n_sites`(스칼라 폴백), `mask_id`/`structure_type`(enum)/`local_density`/`die_density_mean`/`pitch_um`/`line_width_um`/`line_space_um`/`trench_width_um`/`block_size_mm`/`die_size_mm`/`planarization_length_mm`(PTW), `pressure_kpa`/`velocity_m_per_s`(정준단위 접미형+원값은 *_raw), `is_reference_film`, `selectivity_oxide_over_stop`/`dishing_nm`/`erosion_nm`/`overpolish_time_s`. point 추가: `scan_size_um`/`value_uncertainty`/`coverage_k`. 별도 `slurry_spec` 객체: `abrasive_size_value`+`_basis`(enum 8)+`_method`(enum 6), `psd_sigma_g`|(d50,d99), `abrasive_conc_value`+`_unit`(enum 3), `abrasive_density_kg_m3`, `zeta_mv`/`zeta_ph`/`zeta_ionic_strength_mM`/`slurry_ph`.
    - **개념중복 흡수(§2.3)**: `pattern_density_rho`→`local_density`, `feature_width_um`→`line_width_um`/`trench_width_um`, `n_sites`→`len(points)` 파생, `initial_thickness_nm`→`film_stack[].deposited_thickness_nm`, `film_type`→`film_stack[].material` enum. **두 개를 따로 두지 말 것**.
    - **조건부 필수(§5-2, JSON Schema 2020-12)**: `if wafer_type=PTW then required:[mask_id,structure_type,local_density]`; `dependentRequired:{zeta_mv:[zeta_ph]}`; `if abrasive_conc_unit=wt_pct then required:[abrasive_density_kg_m3]`; `if measured_quantity=roughness then required:[scan_size_um]`; `if metric_definition∈{halfrange,fullrange,range_over_sum} and not points then required:[outermost_radius_mm]`.
    - **범위**: `local_density`/`die_density_mean` minimum:0/maximum:1; `pressure_kpa`/`velocity_m_per_s` exclusiveMinimum:0.
  - **검증기**: `sim/calibration/ingest.py`의 `validate_record`는 이미 jsonschema Draft202012Validator를 쓰므로(원문 확인) 위 스키마 개정만으로 대부분 자동 적용됨. format date-time은 format-assertion vocabulary 켜거나 노트 §4-B 파서로 보강(Python 3.9 `fromisoformat`이 Z·윤초 미지원이라 별도 파서 필요).
  - **마이그레이션(§6)**: `migrate(record, from_v, to_v)` — v2.0.0(wafer_type required 승격)에서 구 레코드에 wafer_type=NPW 기본값 주입 + `_migrated_from`/`_schema_version` 스탬프. 원본 파기 전 로그 보존.
  - **검증문헌값**: 노트 §4 4블록(제안필드 53→49·정상3/위반3·JSON Schema 의미론·semver)을 회귀테스트로 승격. JSON Schema 2020-12 §6.5.4/§6.2.4/§6.2.5/§6.1.3/§7.3.1, RFC3339 §5.6.
  - **우선순위**: 상 — 캘리브레이션 층의 데이터 입구. cmp-calibrator의 fit_npw/fit_ptw가 이 통합 스키마의 wafer_type·local_density·metric_definition을 전제로 잔차를 귀속한다.

- **무엇을**: `data/schema/*.json` — CMP 통합 스키마의 JSON Schema/DDL. 엔터티: Lot, Carrier, Wafer(=Substrate), Die/Site, ProcessEvent, SensorTrace, ToolState, Consumable, Measurement.
  - **근거노트**: knowledge/data/cmp-integration-schema-keys-semi-standards.md §3(엔터티-관계 다이어그램)·§4(C)(참조무결성 최소모델).
  - **키/제약 스펙**:
    - Wafer.SubstrateID = 조인 중심 외래키(모든 하위 엔터티가 참조). 계층 Lot→Carrier(E87)→Wafer(E90)→Die/Site(X,Y, E142).
    - SensorTrace 자연키 (ToolID, timestamp, VariableID{SVID|ECID}) — GEM E30 3분류를 VariableID 도메인으로.
    - ProcessEvent(ToolID, RecipeID, SubstrateID, CEID_start_ts, CEID_end_ts) — E40/E94+CEID.
    - Consumable(ConsumableID, type∈{pad,disk,slurry_lot,retaining_ring,...}, ToolID, install_ts, remove_ts). 소모품↔웨이퍼는 **직접 FK 금지**, (ToolID, 시간구간)∩ProcessEvent 시간창 유도 뷰(다대다).
    - Measurement(SubstrateID, X, Y, metric, value, **SOURCE NOT NULL**) — SOURCE는 실측=ToolID / 문헌추출=DOI+TableRef. metric 도메인·좌표계는 wafer-metrology-output-schema-site-flatness-standards를 정본 참조(재정의 금지).
    - 시계열형(SensorTrace)·표형(Measurement) **단일 테이블 병합 금지** — ProcessEvent 경유 조인만.
  - **검증문헌값**: PHM2016 컬럼 19(SVID)+6(ECID)=25, 복합키(WAFER_ID,STAGE)↔(SubstrateID,ProcessEvent) 사상(Li et al. 2019, DOI 10.1115/1.4042051). E10 상태 도메인 6종. §4(C) 참조무결성 테스트가 스키마 수용시험(acceptance test)의 시드.
  - **우선순위**: 중(Lv2-1 단위·좌표계 통일, Lv3-2 ingest 파이프라인의 선행 골격이므로 그 단원 착수 전 확정 필요).

- **무엇을**: `sim/calibration/normalize.py`(신설) — raw 측정 정규화 유틸 4종.
  - **근거노트**: knowledge/data/wafer-coordinate-units-outlier-cleaning.md §1–3, 검증은 §5 verify 블록 5개를 회귀테스트로 승격.
  - **함수 스펙**:
    - `to_canonical_coords(coords, notch_dir, kind∈{polar,cartesian,die})` → SEMI M20 정준계(원점=중심, +x=오른쪽, +y=위, 노치=−y). notch_dir는 US7539552B2식 4값 열거형(Bottom/Right/Top/Left). 극좌표 $x=r\cosθ$, 다이 인덱스 아핀 $x=x_0+(c-c_0)p_x,\;y=y_0+(r_0-r)p_y$(**행축 부호반전 필수**). 원 좌표계·노치배향은 메타로 보존(가역).
    - `to_canonical_units(value, unit)` → Å→nm(×0.1), Å/s→nm/min(×6), psi→kPa(×6.894757), rpm+radius→m/s($2πrN/60$). 원 단위 문자열 메타 보존.
    - `flag_outliers(values, method='mad', k=2.5)` → MAD(1.4826·median|dev|, 임계 2.5, Leys 2013)/IQR(1.5). σ기반은 옵션이되 default 금지. **삭제 아닌 플래그**(원값+사유 보존).
    - `apply_edge_exclusion(r, ee_mm, D_mm)` → EE 밖은 "측정범위밖" 마스크, 결측 NaN과 **구분**. 300mm EE 3mm→제외 3.96%.
  - **검증문헌값**: psi=6.894757 kPa(NIST SP811), 1 Å/s=6 nm/min, MAD상수 1.4826(=1/Φ⁻¹0.75), EE3mm(300mm)=3.96%, 노치회전 시 TTV·WIWNU 불변·단위10× 시 CV 불변(uniformity.py 호출 대조). 전부 §5 assert.
  - **우선순위**: 중 — Lv3-2 ingest 파이프라인의 "표준화" 단계 핵심. Lv1-2 스키마 골격 확정 후 착수.

- **무엇을**: `sim/calibration/synth.py`(신설) — Tier1/2 모델 출력에 노이즈를 입혀 합성 캘리브레이션 데이터셋 생성.
  - **근거노트**: knowledge/data/synthetic-data-generation-tier1-tier2-noise-model.md §1–3, 검증은 §4 verify 블록 4개를 회귀테스트로 승격.
  - **함수 스펙**:
    - `add_sensor_noise(clean, sigma)` → 가산 iid 가우시안(McLoone/Susto 2018 eq.19 eps~N(0,0.02) 패턴).
    - `add_wafer_random_effect(clean, wafer_ids, cv)` → 웨이퍼(로트) 단위 상수 배율/오프셋 랜덤효과. cv 기본 프리셋 5~14%(§3 실측 앵커).
    - `add_drift(clean, kind='ramp'|'step', magnitude, t)` → moyne2017 §4.1의 drift/step 패턴(챔버 시즈닝·소모품 소모·유지보수 이벤트 모사).
    - `add_spike(clean, idx, magnitude)` → moyne2017의 spike 패턴. `flag_outliers`(위 normalize.py)가 이를 잡는지 회귀테스트하는 용도.
    - 전부 "clean 값·주입 노이즈 파라미터·seed"를 메타데이터로 반환(가역·재현) — 캘리브레이션이 원래 파라미터를 복원하는지 채점 가능해야 함.
  - **검증문헌값**: eps~N(0,0.02)(McLoone/Susto 2018, DOI:10.1109/TASE.2017.2786213), 잔차 8.317 nm/min·R²=0.917(Li et al. 2019, DOI:10.1115/1.4042051), 실측 CV 5.3~13.8%(JP4508514B2). MAD 점탐지는 spike는 잡되 gradual drift는 못 잡음(§4.4 assert) — drift 검증에는 추세상관 등 별도 탐지기 필요.
  - **우선순위**: 중 — Lv1-2 스키마·Lv2-1 normalize.py 확정 후, Lv3-2 ingest 파이프라인의 회귀테스트 데이터 공급원으로 착수.

- **무엇을**: `tools/ingest_measurement.py` 확장(불확도·출처 필드) + `sim/calibration/ingest.py`(신설, CURRICULUM.md 지정 경로) — 검증된 행을 Parquet으로 내보내는 단계.
  - **근거노트**: knowledge/data/cmp-measurement-ingest-schema-standardization.md §1(최소 스키마 4범주)·§2(검증 규칙)·§4(컬럼형 저장 근거)·§5(verify 블록 전체를 회귀테스트로 승격).
  - **함수/필드 스펙**:
    - `points` 각 항목에 `uncertainty`(값과 같은 단위의 결합표준불확도 u_c) + `coverage_k`(기본 2, GUM §6.3.1 범위 2~3) 필드 추가. 둘 다 없으면 `warnings`(강제 아님 — 기존 데이터 호환)로만 신고, 문헌 추출 레코드는 `source`(DOI+표 번호) **필수(NOT NULL)** — [[cmp-integration-schema-keys-semi-standards]] Measurement.SOURCE 제약과 동일.
    - `validate_row()`류 물리적 불가능값 검사(`removed_nm<0`, `pressure_psi<=0`, `time_s<=0`)를 `blockers`에 추가 — 현재 코드는 결측만 보고 부호를 안 본다. 단위 의심(`thickness_post_nm>3000` 류 자릿수 이탈)은 `warnings`.
    - `to_parquet(records, path)` — pyarrow(이미 `.venv`에 21.0.0 설치 확인)로 검증 통과 레코드를 컬럼형 저장. DuckDB는 `.venv` 미설치이므로 1단계는 pyarrow만, DuckDB 도입은 별도 의존성 추가 결정 필요.
  - **검증문헌값**: GUM(JCGM 100:2008, DOI:10.59161/jcgm100-2008e) §2.2.3·§6.3.1·§7.2.3, psi→kPa 6.894757(NIST SP811, [[wafer-coordinate-units-outlier-cleaning]] 재사용), Parquet 왕복 무손실·집계쿼리 SQLite 대비 3.5배·CSV 대비 46배(자체 벤치마크, §5(d)). 전부 노트 §5 assert.
  - **우선순위**: 중 — Lv3-2가 이 단원의 마지막이므로 Cal-1(캘리브레이션 층 통합) 착수 전에 확정 필요.
