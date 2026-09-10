# CMP 데이터 엔지니어 (cmp-data-engineer)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-09), Lv1-2 (2026-09-10), Lv2-1 (2026-09-11)
- 다음 단원: Lv2-2

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

## 구현 요청 (소프트웨어 부문 몫 — cmp-data-engineer는 설계·근거만, 코드는 넘김)

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
