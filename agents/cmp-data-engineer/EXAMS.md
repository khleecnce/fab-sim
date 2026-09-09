# 자기시험 — CMP 데이터 엔지니어 (cmp-data-engineer)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1 CMP 공개 데이터셋 조사 (2026-09-09, knowledge/data/cmp-public-datasets-survey.md)

**Q1. 현재까지 확인된, 실제 CMP 툴에서 수집된 다운로드 가능한 구조화 공개 데이터셋은 무엇이며 어떤 형태의 문제(회귀/분류)를 겨냥하는가?**

A1. 2016 PHM Data Challenge CMP 데이터셋(PHM Society 주관). 4개 CMP 툴에서 지정 웨이퍼들의 시계열 신호(x1~x25, 총 25컬럼 = 실시간 상태 모니터링 19개 + 사전설정 파라미터 6개)를 모아, 목표변수 `AVG_REMOVAL_RATE`(CMP 전후 두께차로 산출한 평균 제거율)를 예측하는 **회귀(가상계측, VM) 문제**다. 학습셋은 웨이퍼 1981개·트레이스 672,744개(185개 CSV), 검증 144,148·테스트 156,262 트레이스. 조성-MRR 화학모델이 아니라 장비 FDC 신호→MRR 문제라는 점이 핵심. (출처: Li, Wu, Yu 2019, *J. Manuf. Sci. Eng.* 141(3):031003, DOI: 10.1115/1.4042051 §4.1)

**Q2. UCI SECOM 데이터셋을 CMP 공정 데이터로 바로 재사용할 수 없는 이유는?**

A2. SECOM(1,567 인스턴스 × 591 컬럼, CC BY 4.0, McCann & Johnston 2008)은 반도체 제조 공정의 센서 신호이지만 **공정 단계가 명시되지 않고 특징이 익명화**되어 있어 CMP 여부·어떤 파라미터인지 되짚을 수 없다. 라벨도 압력·pH 같은 연속 MRR이 아니라 불량 104건 vs 정상 1463건(약 14:1)의 이진 pass/fail 분류다. 즉 데이터 형태(다변량 FDC + 불균형 라벨)는 참고할 수 있어도 CMP 스키마의 직접 소스로 쓸 수 없다. (출처: archive.ics.uci.edu/dataset/179/secom)

**Q3. 슬러리 조성(입자크기·농도·pH 등)과 MRR의 관계를 다루는 문헌 데이터는 어떤 형태로 존재하며, 이것이 스키마 설계에 왜 문제가 되는가?**

A3. 별도의 다운로드 가능한 부록 데이터파일이 아니라 **논문 본문의 표·그래프**로만 존재한다 (예: knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md는 여러 논문 표에서 수치를 수기로 옮겨 재구성한 것). MIT Boning 그룹(Tugbawa 학위논문 등)도 논문 PDF는 공개하지만 별도 데이터 저장소는 이번 조사에서 찾지 못했다. 문제는 이런 "수기 추출" 레코드에 출처(DOI/Table 번호)를 강제하는 스키마 필드가 없으면 재검증이 불가능해진다는 점 — 그래서 Lv1-2 스키마는 시계열형(PHM2016류)과 표형(슬러리 DOE류) 데이터를 별도 엔터티로 두고 출처 필드를 1급 시민으로 넣어야 한다.

## Lv1-2 통합 스키마 키 체계 (2026-09-10, knowledge/data/cmp-integration-schema-keys-semi-standards.md)

**Q1. CMP 통합 스키마에서 소모품·툴·웨이퍼·측정을 잇는 "조인 중심축" 키는 무엇이며, 왜 이 키를 새로 발명하지 말아야 하는가?**

A1. 조인 중심축은 **SubstrateID**로, SEMI E90(기판 추적) 표준이 개별 웨이퍼에 부여하는 식별자다. 웨이퍼 계층은 Lot(LotID) → Carrier/FOUP(CarrierID, SEMI E87) → Wafer(SubstrateID, E90) → Die/Site(X,Y, SEMI E142)로 내려가고, 측정·공정이벤트·(유도)소모품 관계가 전부 이 SubstrateID를 외래키로 붙는다. 새 키를 발명하면 안 되는 이유는 실팹 데이터는 이미 SECS/GEM 인터페이스로 이 표준 식별자들을 달고 나오므로, 자체 키를 만들면 인제스트 때 전 레코드를 재매핑해야 해 비용이 폭증하기 때문이다. (출처: SEMI E90/E87/E142, store-us.semi.org·PEER Group 정의 페이지; 좌표계 논의 semi.org Standards Watch 2026-04)

**Q2. PHM2016 데이터셋의 x1~x25 컬럼은 GEM(SEMI E30) 데이터 수집 객체 관점에서 어떻게 분해되며, 이것이 스키마 정규화에 주는 함의는?**

A2. 실시간 상태 모니터링 변수 19개는 GEM의 **SVID(Status Variable)** 계열(압력·유량·회전속도·패드/드레서/멤브레인 사용량 등 상시 조회 상태량), 사전설정 파라미터 6개는 **ECID(Equipment Constant)** 계열(호스트가 설정하는 스테이지·헤드 값)로 분해된다(19+6=25). 웨이퍼별로 트레이스가 잘린 경계는 GEM의 **CEID(Collection Event, 웨이퍼 시작/종료 사건)**에 해당한다. 함의: 장비 센서 데이터를 (ToolID, timestamp, VariableID{SVID|ECID}, value)로 정규화하고 VariableID를 도메인으로 두면, 툴마다 다른 컬럼명을 흡수하면서 표준 3분류로 일관되게 저장할 수 있다. (출처: Li, Wu, Yu 2019, ASME JMSE 141(3):031003, DOI: 10.1115/1.4042051 §4.1; SEMI E30 GEM)

**Q3. SEMI 표준은 웨이퍼에는 성숙한 단위추적(E90)을 주지만 소모품(패드·디스크·슬러리 로트)에는 그렇지 않다. 그러면 소모품을 처리한 웨이퍼 집합과 어떻게 조인하며, 그 근거는?**

A3. 소모품은 보통 SVID의 "누적 사용량" 스칼라로만 노출되고 개체(instance) 단위추적 표준이 없으므로, ConsumableID를 1급 엔터티로 두되 **직접 외래키가 아니라 (ToolID, [install_ts, remove_ts]) 시간구간과 ProcessEvent 시간창(CEID_start~end)의 겹침으로 유도 조인**한다. 소모품 개체당 웨이퍼는 다수(1:N), 웨이퍼당 동시 장착 소모품도 다수 → 다대다이며 파생 뷰로 만든다. 근거는 Applied Materials 특허 US 10,593,574 — 폴리싱 패드에 RFID 태그를 내장해 소모품 정체를 인시투 센서 데이터(온도·압력·막두께 등)와 결합하는 방식으로, RFID가 있으면 시간구간 유도 대신 개체 ID를 직접 얻는다. (출처: US10593574, Applied Materials, 등록 2020-03-17)
