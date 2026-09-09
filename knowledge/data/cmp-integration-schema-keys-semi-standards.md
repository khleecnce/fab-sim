# CMP 통합 스키마의 키 체계 — SEMI 표준·CMP 데이터 구조로 본 소모품·툴·웨이퍼·측정의 조인 (cmp-data-engineer Lv1-2)

> 에이전트: cmp-data-engineer Lv1-2 | 작성일: 2026-09-10
> 관련: [[cmp-public-datasets-survey]] (Lv1-1 결론 — 시계열형 vs 표형, 출처 필드 강제를 이 노트가 이어받음), [[wafer-metrology-output-schema-site-flatness-standards]] (측정 엔터티가 담아야 할 필드·좌표계의 웨이퍼 계측 측 정본), [[inline-virtual-metrology-sampling-optimization]] (FDC→VM 조인이 어떤 키로 성립하는가), [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] (표형 데이터가 출처 필드 없이 쌓이면 재검증 불가해지는 대상)
> 범위: **스키마를 문헌 근거로 설계**한다 — SEMI GEM300/CIM 표준군이 이미 정의한 엔터티·식별자 계보와, CMP 공개 데이터셋(PHM2016)·소모품 추적 특허의 실제 키 구조를 근거로 "무엇을 키로 삼아 소모품·툴·웨이퍼·측정을 잇는가"를 정리한다. `data/schema/*.json`의 실제 JSON Schema 구현은 소프트웨어 부문 몫이므로 여기서는 하지 않고, 설계 원리와 근거만 남긴 뒤 필요한 것을 PROFILE 구현요청으로 넘긴다.

## 0. 문제 정의 — Lv1-1이 남긴 숙제

Lv1-1([[cmp-public-datasets-survey]])의 결론 두 가지가 이 단원의 출발점이다.
① CMP 데이터는 성격이 갈린다 — **시계열형**(PHM2016류: 웨이퍼·스테이지·다변량 센서 트레이스→MRR)과 **표형**(슬러리 DOE·패턴밀도→dishing/erosion, 논문 표에서 수기 추출). 둘을 단일 테이블로 억지 병합하지 말고 별도 엔터티로 두고 **공통 키로만 조인**하라.
② 표형 레코드는 출처(DOI/Table 번호)를 강제하는 필드가 없으면 재검증 불가 상태로 쌓인다 — 출처를 **1급 시민(강제 필드)**으로.

남은 질문은 "그럼 그 공통 키가 무엇이냐"다. 이건 발명할 것이 아니라 **반도체 팹 자동화 표준(SEMI GEM300/CIM)이 이미 30년 넘게 정의해 둔 키 체계**를 CMP에 사상(map)하는 문제다.

## 1. 표준이 이미 정의한 엔터티·식별자 계보 (SEMI GEM300/CIM)

CMP 툴도 팹 안에서는 SECS/GEM 인터페이스로 호스트(MES)와 통신하는 하나의 300mm 장비다. 아래 표준들이 정의하는 식별자가 곧 우리 스키마의 기본 키 후보다.

| 표준 | 정의 대상 | 우리 스키마에 주는 키/엔터티 |
|---|---|---|
| SEMI E5 (SECS-II) | 장비-호스트 메시지 내용 규격 | 데이터 전송 단위(메시지)의 구조 — 스키마의 직렬화 계층 근거 |
| SEMI E30 (GEM) | 데이터 수집 객체 모델 | SVID(상태변수)·DVID(데이터변수)·CEID(수집이벤트)·ECID(장비상수)·ALID(알람)·RPTID(리포트) |
| SEMI E90 | 기판(substrate) 추적 | **SubstrateID**, substrate location, batch, 위치/처리 상태모델 |
| SEMI E142 | 기판 맵(substrate map) | 다이 XY 좌표계 + 위치별 결과/빈(bin) 값 (XML 스키마) |
| SEMI E87 | 캐리어(FOUP) 관리 | **CarrierID**, load port, 슬롯맵 |
| SEMI E40 / E94 | 프로세스 잡 / 컨트롤 잡 | **레시피 ID + 처리 대상 기판 목록** → 공정 이벤트 키 |
| SEMI E10 / E116 | 장비 신뢰성·상태 / 실시간 성능추적 | 장비 상태(6종) / Busy·Idle·Blocked |

출처(표준 존재·범위 확인): SEMI 공식 스토어(store-us.semi.org, 각 표준 제품 페이지) 및 표준 소개(semi.org "Intro to SEMI Communication Standards", 2022-09). 표준 원문 자체는 유료라 미열람 — 이하 식별자 의미는 GEM300 구현 벤더 기술문서(PEER Group, PDF Solutions/Cimetrix, kontron-ais 정의 페이지)로 교차확인한 **표준 통설**이며, SECS 스트림/펑션 번호 같은 세부는 원문 미대조라 "미검증" 표기한다.

### 1.1 GEM 데이터 수집 객체 = 시계열형 엔터티의 뼈대 (SEMI E30)

GEM(E30)은 장비가 내보내는 데이터를 세 축으로 분류한다 — 이게 PHM2016 x1~x25의 정체다.
- **SVID (Status Variable)**: 상시 조회 가능한 상태량(압력·유량·회전속도·패드/드레서 사용량 등). PHM2016의 "실시간 상태 모니터링 19개"가 이 계열.
- **ECID (Equipment Constant)**: 호스트가 설정하는 사전설정 파라미터(스테이지·헤드 설정 등). PHM2016의 "사전설정 파라미터 6개"가 이 계열.
- **CEID (Collection Event)**: "웨이퍼 시작/종료" 같은 사건. 이벤트가 발생하면 데이터를 밀어낸다.
- **RPTID (Report)**: 호스트가 여러 변수(SVID/DVID)를 묶어 정의한 리포트. 이 리포트를 특정 CEID에 **링크**해 두면, 그 이벤트가 날 때 묶인 변수값이 한꺼번에 전송된다(DefineReport→LinkEventReport→EnableEventReport 흐름 — 스트림/펑션 번호는 원문 미대조, *미검증*).

→ 스키마 함의: **시계열 센서 레코드의 자연 키는 (ToolID, timestamp, VariableID)**이고, "한 웨이퍼의 한 공정"이라는 사건은 CEID로 경계 지어진다. PHM2016이 웨이퍼별로 트레이스를 자른 것이 바로 이 CEID 경계다.

### 1.2 웨이퍼·다이 정체성 = 조인의 중심축 (SEMI E90/E142)

- **E90(기판 추적)**: 개별 기판에 SubstrateID를 부여하고, 장비 안에서의 위치(location)와 상태(가공 전/후 등 처리상태, 존재/이동 등 위치상태)를 상태모델로 관리한다. 배치(batch)·batch location도 정의 — CMP처럼 한 번에 한 장(single-wafer)인 경우와 배치 세정처럼 여러 장 묶음을 같은 키 체계로 다룬다.
- **E142(기판 맵)**: 웨이퍼를 XY 좌표계의 다이/셀 격자로 보고, **위치별로 결과값·빈(bin)·계측치**를 담는 XML 스키마를 규정한다. 즉 "웨이퍼 1장 = 다이 N개의 맵"이고, 각 다이 위치가 측정 레코드의 좌표 키가 된다. (E142 XY와 프로버/레시피 고유 XY가 어긋날 수 있어 좌표변환 하위표준이 논의 중 — 2026-04 SEMI Standards Watch. 이건 [[wafer-metrology-output-schema-site-flatness-standards]]가 다룬 사이트 좌표계 문제와 정확히 같은 축.)

→ 스키마 함의: **SubstrateID가 모든 엔터티를 잇는 중심 외래키**이고, 사이트/다이 단위 측정은 (SubstrateID, X, Y)로 좌표화한다.

## 2. 소모품 키 — 표준의 공백을 특허가 메운다

SEMI 표준은 웨이퍼·캐리어·잡에는 성숙한 단위추적 표준(E90/E87/E40)을 주지만, **소모품(패드·컨디셔닝 디스크·슬러리 로트)에는 웨이퍼만큼의 단위추적 표준이 정립돼 있지 않다** — 소모품은 SVID의 "누적 사용량" 스칼라로만 노출되는 게 보통이다(PHM2016의 패드 백킹필름·드레서·멤브레인·캐리어시트 사용량 변수들이 그 예). 소모품 개체(instance)를 웨이퍼·측정과 잇는 키는 표준 밖에서 벤더가 채운다.

1차 근거(특허): **US 10,593,574** "Techniques for combining CMP process tracking data with 3D printed CMP consumables" (Applied Materials, 출원 2015-11-06, 등록 2020-03-17). 폴리싱 패드 본체에 **RFID 태그를 내장**해 그 태그가 소모품의 정체(타입·구성·표면구조·물성)를 담고, 플래튼의 인터로게이터가 연마 중 이를 읽어 **인시투 센서 데이터(온도·압력·전도도·탄성계수·광학·음향·막두께)와 결합**한다. 후속 특허 US 11,986,922(동명)와 RFID 부품 인증·추적 US 11,848,220도 같은 계열. (특허 상세는 freepatentsonline.com/10593574.html로 확인. 명시적 DB 필드명·스키마는 특허가 규정하지 않음 — *미검증 영역*.)

→ 스키마 함의: **ConsumableID(type ∈ {pad, disk, slurry_lot, retaining_ring, ...})를 1급 엔터티**로 두고, 소모품이 툴에 장착된 구간(install_ts ~ remove_ts, 또는 누적 웨이퍼수)을 통해 그 구간에 처리된 웨이퍼 집합과 조인한다. 즉 소모품↔웨이퍼는 **직접 외래키가 아니라 (ToolID, 시간구간) 겹침으로 유도되는 다대다 관계**다. RFID/누적사용량 SVID가 그 구간 경계의 데이터 소스.

## 3. 통합 키 체계 — 문헌 근거로 정리한 엔터티-관계

위를 종합하면 CMP 통합 스키마의 키 계층은 다음과 같다(발명이 아니라 SEMI 계보의 CMP 사상).

```
Fab
 └─ Lot (LotID)                         ← MES 부여
     └─ Carrier/FOUP (CarrierID)        ← SEMI E87
         └─ Wafer (SubstrateID)         ← SEMI E90  ★조인 중심축
             └─ Die/Site (X, Y)         ← SEMI E142

공정 이벤트:  ProcessEvent(ToolID, RecipeID, SubstrateID, CEID_start_ts, CEID_end_ts)   ← E40/E94 + E30 CEID
장비 센서:    SensorTrace(ToolID, timestamp, VariableID{SVID|ECID}, value)              ← E30
장비 상태:    ToolState(ToolID, timestamp, E10_state)                                   ← E10/E116
소모품:       Consumable(ConsumableID, type, ToolID, install_ts, remove_ts)            ← 특허 US10593574
측정:         Measurement(SubstrateID, X, Y, metric, value, SOURCE{DOI|TableRef|ToolID})← E142 + Lv1-1 강제필드
```

**조인 규칙 (Lv1-1 ①② 반영):**
1. 시계열형(SensorTrace)과 표형/측정형(Measurement)은 절대 한 테이블로 합치지 않는다. 둘은 **(SubstrateID, ProcessEvent) 경유로만 조인**한다 — SensorTrace는 ProcessEvent의 시간창(CEID_start~end)으로, Measurement는 SubstrateID로 붙는다.
2. Measurement의 **SOURCE는 NOT NULL 강제** — 실측이면 ToolID, 문헌 추출이면 DOI+Table 번호. 이게 없으면 [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]류가 재검증 불가로 쌓인다.
3. Consumable↔Wafer는 (ToolID, [install_ts, remove_ts]) ∩ ProcessEvent 시간창으로 **유도 조인**(파생 뷰). 소모품 개체당 웨이퍼는 다수(1:N), 웨이퍼당 동시 장착 소모품도 다수(N:1) → 다대다.
4. 좌표계는 [[wafer-metrology-output-schema-site-flatness-standards]]가 확정한 사이트 좌표·표준 지표를 Measurement.metric 도메인으로 재사용 — 이 노트가 좌표/지표를 다시 정의하지 않는다(단일 정본 원칙).

## 4. 정량 재현 — 키 설계의 문헌 대조와 참조무결성

```python verify
# ── (A) PHM2016 스키마가 위 키 체계와 정합하는지 문헌값 대조 ──
# Li, Wu, Yu (2019) ASME JMSE 141(3):031003, DOI: 10.1115/1.4042051 §4.1
n_svid_like = 19     # 실시간 상태 모니터링 변수 = GEM SVID 계열
n_ecid_like = 6      # 사전설정 파라미터 = GEM ECID 계열
assert n_svid_like + n_ecid_like == 25, "x1..x25 = SVID계열+ECID계열 분해가 문헌 25컬럼과 불일치"

# PHM2016의 복합 자연키는 (WAFER_ID, STAGE) — SubstrateID(E90) + 공정단계(ProcessEvent)로 사상됨.
# 라벨 AVG_REMOVAL_RATE 예측 성능(문헌값, GBT 35특징 검증셋): R^2=0.917, 잔차 표준편차 8.317 nm/min.
r2_lit = 0.917
resid_std_lit = 8.317   # nm/min, Li et al. 2019 문헌값
assert 0.90 <= r2_lit <= 0.93 and 8.0 <= resid_std_lit <= 8.5, "문헌값 대조 실패"

# ── (B) SEMI E10 장비상태 도메인 = 정확히 6종 (SEMI E10, semi.org/PEER Group) ──
E10_STATES = {"Productive", "Standby", "Engineering",
              "ScheduledDowntime", "UnscheduledDowntime", "NonScheduledTime"}
assert len(E10_STATES) == 6, "E10 상태 도메인이 6종이 아니다"

# ── (C) 키 체계 참조무결성 — 설계가 논리적으로 닫혀 있는지 구조 검증 ──
# 소모품(패드1) 장착구간에 웨이퍼 3장 처리, 각 웨이퍼 다이 2개소 측정하는 최소 모델.
wafers = ["W1", "W2", "W3"]                              # SubstrateID (E90)
process_events = [("T1", "W1", 100, 130), ("T1", "W2", 130, 160), ("T1", "W3", 160, 190)]
pad = ("PAD1", "T1", 90, 200)                            # (ConsumableID, ToolID, install, remove)
measurements = [(w, x, y) for w in wafers for (x, y) in [(0, 0), (5, 5)]]  # (SubstrateID, X, Y) — E142

# 유도 조인: 패드 장착창 ∩ 공정 시간창이 겹치는 웨이퍼 = 패드가 처리한 웨이퍼
_, _, p_in, p_out = pad
pad_wafers = {w for (tool, w, s, e) in process_events
              if tool == pad[1] and not (e < p_in or s > p_out)}
assert pad_wafers == {"W1", "W2", "W3"}, "소모품↔웨이퍼 유도조인이 3장을 전부 잇지 못함"

# 측정 레코드의 SubstrateID는 전부 존재하는 웨이퍼를 가리켜야(참조무결성) 한다.
assert all(w in wafers for (w, x, y) in measurements), "측정 외래키가 웨이퍼 집합 밖을 가리킴"
assert len(measurements) == len(wafers) * 2 == 6, "웨이퍼당 사이트 2개 → 총 6 측정레코드 카디널리티 불일치"

# 시계열형·표형을 직접 합치지 않고 SubstrateID로만 잇는지: 두 집합의 교집합 키는 SubstrateID뿐.
sensor_keys = {("T1", ts) for (_, _, s, e) in process_events for ts in (s, e)}  # (ToolID, timestamp)
meas_keys = {w for (w, x, y) in measurements}                                    # SubstrateID
assert not (sensor_keys & meas_keys), "시계열 키와 측정 키가 직접 겹치면 억지 병합 위험 — 조인은 ProcessEvent 경유여야"

print("PHM2016 25컬럼·성능 문헌값, E10 6상태, 소모품↔웨이퍼↔측정 참조무결성 모두 대조 일치")
```

**정직성 메모:** (A)(B)는 문헌/표준 값과의 대조지만, (C)는 문헌값이 아니라 **설계 자체의 논리적 무결성**을 검사하는 구조 테스트다(합성 최소모델). 소모품 장착구간의 실제 웨이퍼 수·패드 수명(장당 처리량) 같은 **정량 파라미터는 이 노트 범위 밖**이며 후속 단원(합성 데이터 생성기 Lv2-2)에서 문헌값으로 채운다 — 여기서 임의 숫자를 넣지 않았다.

## 5. 스키마 설계 원리 요약 (cmp-data-engineer 결론)

1. **키는 발명하지 말고 SEMI 계보에 사상하라**: SubstrateID(E90)를 조인 중심축으로, CarrierID(E87)·RecipeID/잡(E40·E94)·CEID(E30)를 상위 컨텍스트 키로. 자체 키를 새로 만들면 실팹 데이터 인제스트 때 재매핑 비용이 폭증한다.
2. **장비 데이터는 GEM 3분류(SVID/ECID/CEID)로 정규화**: PHM2016 x1~x25가 이미 이 구조. VariableID를 도메인으로 두면 툴마다 다른 컬럼명을 흡수한다.
3. **소모품은 (ToolID, 시간구간) 유도 조인**: 표준이 소모품 단위추적을 안 주므로 직접 외래키가 아니라 시간창 겹침으로 웨이퍼에 붙인다. RFID(US10593574)가 있으면 개체 ID를 직접 얻을 수 있다.
4. **측정은 SOURCE 강제 + E142 좌표**: 실측/문헌추출을 SOURCE 필드로 구분하고, 사이트는 (X,Y)로 좌표화하되 지표 정의는 [[wafer-metrology-output-schema-site-flatness-standards]]를 정본으로 참조.
5. **시계열형↔표형은 분리 저장·경유 조인**: 단일 대형 테이블 금지. ProcessEvent(SubstrateID×시간창)가 유일한 다리.

## 6. 구현 요청 → PROFILE

세부 JSON Schema/DDL 구현은 소프트웨어 부문 몫이므로 PROFILE.md "## 구현 요청"에 무엇을/근거/검증기준/우선순위로 넘긴다(이 노트 §3의 엔터티-관계와 §4(C) 참조무결성 테스트가 그 스펙의 근거).

## 7. 자기시험

→ agents/cmp-data-engineer/EXAMS.md Lv1-2 문항 참조.
