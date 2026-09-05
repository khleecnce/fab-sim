#!/usr/bin/env python3
"""agents/ORG.md의 [대기] 에이전트 전원에 PROFILE/CURRICULUM/EXAMS 골격을 생성한다.
각 커리큘럼은 도메인 단원 + §7.3 캘리브레이션 단원을 포함한다. 이미 있으면 건드리지 않는다."""
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent / "agents"
TODAY = date.today().isoformat()

# id: (한글명, 부모, 한줄 역할, 선행 knowledge, [도메인 단원 Lv1-1..Lv3-2], 캘리브레이션 단원)
AGENTS = {
    # ── 슬러리 분화
    "slurry-abrasive": ("슬러리 입자 전문가", "slurry-chemist",
        "실리카(콜로이달/퓸드)·세리아·알루미나 입자의 크기·형상·농도·경도가 MRR·결함에 미치는 영향",
        ["cmp/slurry-components-overview", "cmp/colloid-zeta-dlvo-slurry-stability"],
        ["입자 종류별 제조법과 물성(콜로이달/퓸드 실리카, 세리아 소성/습식)",
         "입도 분포(D50·D90·LPC)와 측정법(DLS·레이저회절·SPOS)",
         "입자 경도·형상과 기계적 제거: Hertz 압입, 입자당 제거 체적",
         "입자 농도-MRR 포화 곡선과 접촉 확률 모델",
         "세리아 화학적 톱니(chemical tooth) 메커니즘과 옥사이드 선택비",
         "입자 파라미터 → Kp 기여 정량모델 구현 (sim/tier2)"],
        "스펙시트(입도·농도·제타) → 모델 입력 변환 규칙 정의 + 공개 데이터로 검증"),
    "slurry-chemistry": ("슬러리 화학 전문가", "slurry-chemist",
        "산화제·억제제·킬레이트·pH 완충·계면활성제가 막질별 용해·패시베이션·선택비를 어떻게 정하는가",
        ["cmp/surface-chemistry-cu-w-pourbaix-passivation", "cmp/slurry-components-overview"],
        ["산화제 화학: H2O2·KIO3·Fe(NO3)3 — 산화 전위, 분해 속도, 금속별 적합성",
         "억제제(BTA·TAZ)·킬레이트(글리신·시트르산) 흡착과 패시베이션 막",
         "pH·이온강도가 제타전위·용해율·선택비에 미치는 영향 (Pourbaix 재해석)",
         "선택비 설계: oxide:nitride, Cu:barrier, W:oxide — 정지층 화학",
         "최신 리뷰: 코발트·루테늄 배선용 신규 화학, 무산화제 슬러리",
         "화학 조성 → 용해율·패시베이션 상수 정량모델 (sim/tier2)"],
        "화학 스펙(농도·pH·산화제 종류) → 화학 상수 매핑 + 실측 MRR과의 잔차 정의"),
    "slurry-colloid": ("슬러리 안정성 전문가", "slurry-chemist",
        "분산 안정성·응집·POU 필터·쉘프라이프·희석/혼합이 대입자(LPC)와 스크래치에 미치는 영향",
        ["cmp/colloid-zeta-dlvo-slurry-stability"],
        ["DLVO 심화: 이온강도·pH·온도에 따른 응집 속도(Smoluchowski)",
         "LPC(Large Particle Count) 측정과 스크래치 상관관계",
         "POU 필터(깊이/막)·재순환·펌프 전단이 입자에 미치는 영향",
         "쉘프라이프·희석·혼합(2액형) 안정성과 현장 QC 항목",
         "최신 리뷰: 응집 억제 첨가제, 실시간 입도 모니터링",
         "저장·이송 이력 → 유효 입도 분포 변화 모델 (sim/tier2)"],
        "슬러리 로트·보관 이력 데이터 → LPC·결함 예측 잔차 정의"),
    # ── 패드 분화
    "pad-material": ("패드 소재 전문가", "pad-mechanic",
        "폴리우레탄 조성·경도(Shore D)·기공률·점탄성(DMA)이 접촉역학·MRR·결함에 미치는 영향",
        ["materials/pad-viscoelasticity-dma", "materials/hertz-gw-contact-mechanics"],
        ["PU 화학: 프리폴리머·경화제·발포 — 조성이 경도·기공을 정하는 방식",
         "경도·탄성률·기공률 측정법과 문헌값 범위 (IC1000/IC1010/하드·소프트)",
         "점탄성 심화: 온도·주파수 의존 저장/손실 탄성률과 CMP 조건 매핑",
         "기공 구조와 슬러리 보유·이송: 기공률-MRR 관계",
         "최신 리뷰: 3D 프린팅 패드, 무발포 패드, 저결함 패드 소재",
         "소재 파라미터 → GW 유효 강성·asperity 분포 정량모델 (sim/tier2)"],
        "패드 스펙시트(경도·밀도·기공) → 접촉모델 입력 변환 + 실측 프로파일 잔차"),
    "pad-structure": ("패드 구조 전문가", "pad-mechanic",
        "그루브(동심원·XY·나선) 형상·피치·깊이와 서브패드 적층이 슬러리 유동·압력 분포·엣지 효과에 미치는 영향",
        ["materials/pad-structure-groove-subpad"],
        ["그루브 종류와 기능: 슬러리 분배·배출·유체압 완화",
         "그루브 기하(폭·깊이·피치) → 유효 접촉면적·유동 저항",
         "서브패드 강성 적층과 웨이퍼 스케일 압력 분포(엣지 롤오프)",
         "그루브 마모에 따른 유동 특성 변화와 수명 판정",
         "최신 리뷰: 최적 그루브 설계, CFD 기반 유동 해석",
         "그루브·적층 파라미터 → 압력 분포·유동 모델 (sim/tier2)"],
        "패드 구조 스펙 → 엣지 효과 보정 파라미터 정의"),
    "pad-lifecycle": ("패드 수명 전문가", "pad-mechanic",
        "브레이크인·정상 마모·glazing·교체 기준 — 패드 사용 이력이 시간 의존 MRR·결함에 미치는 영향",
        ["materials/pad-wear-glazing-mrr-decay", "equipment/conditioning-mechanism-asperity-regeneration"],
        ["브레이크인 물리: 초기 asperity 형성과 MRR 상승 곡선",
         "정상 마모율과 컨디셔닝 강도의 균형 (마모 = 재생)",
         "glazing 메커니즘: asperity 소성변형·슬러리 잔류물·MRR 감소",
         "패드 두께·그루브 깊이 모니터링과 교체 기준(경제성 포함)",
         "최신 리뷰: 패드 수명 예측, 인시츄 패드 상태 센싱",
         "사용시간·컨디셔닝 이력 → 시간 의존 Kp·asperity 모델 (sim/tier2)"],
        "패드 이력 로그(사용시간·컨디셔닝 횟수) → 시간축 보정 파라미터"),
    # ── 디스크 분화
    "disk-design": ("컨디셔너 디스크 설계 전문가", "disk-conditioner",
        "다이아몬드 그릿 크기·밀도·돌출 높이·본딩(전착/브레이징/CVD)이 패드 절삭율·asperity 재생·수명에 미치는 영향",
        ["equipment/conditioner-grit-design-space", "equipment/conditioner-disk-pad-cutting-model"],
        ["다이아몬드 그릿 규격(메시·형상·품질)과 본딩 기술 비교",
         "그릿 밀도·돌출 높이 → 패드 절삭율(cut rate) 모델",
         "그릿 탈락·마모와 디스크 수명, 스크래치 결함 연계",
         "디스크 설계 → 패드 표면 조도·asperity 분포 정량 관계",
         "최신 리뷰: CVD 다이아 디스크, 패턴화 그릿 배열",
         "디스크 파라미터 → 절삭율·asperity 재생 모델 (sim/tier2)"],
        "디스크 스펙시트 → 절삭 모델 입력 변환 + 실측 패드 마모율 잔차"),
    "disk-kinematics": ("컨디셔닝 운동학 전문가", "disk-conditioner",
        "sweep 프로파일·하중·RPM·체류시간이 패드 반경별 컨디셔닝 밀도(PCR)와 프로파일에 미치는 영향",
        ["equipment/conditioner-sweep-kinematics-pcr-profile"],
        ["컨디셔너 sweep 운동학: 아암 각속도·체류시간 → 반경별 궤적 밀도",
         "하중·RPM·디스크 반경이 PCR 프로파일에 미치는 영향",
         "인시츄 vs 엑스시츄 컨디셔닝과 MRR 안정성",
         "sweep 레시피 최적화: 패드 프로파일 평탄화 목표",
         "최신 리뷰: 적응형 sweep, 폐루프 패드 프로파일 제어",
         "sweep 레시피 → PCR·패드 프로파일 예측 모델 (sim/tier2, 기존 conditioner_sweep 확장)"],
        "sweep 레시피 + 실측 패드 두께 프로파일 → 절삭 모델 보정"),
    # ── 웨이퍼 축
    "wafer-type": ("시험 웨이퍼 전문가", "cmp-integrator",
        "NPW(블랭킷)와 PTW(패턴) 웨이퍼의 목적·구조·측정 체계·데이터 해석 차이. 두 유형 데이터를 잇는 전이 규칙의 소유자",
        ["cmp/wiwnu-pressure-velocity-wafer-scale", "cmp/pattern-dependent-dishing-erosion"],
        ["NPW: 블랭킷 막 종류·두께·측정 포인트 체계(49/81pt·엣지 제외)·WIWNU 정의",
         "PTW: 표준 테스트 패턴(MIT/SEMATECH 마스크)·패턴밀도·피치·다이 맵",
         "NPW 결과가 PTW를 예측하지 못하는 이유: 패턴 효과의 물리",
         "측정 기법: 엘립소미터·프로파일러·AFM·XRF — 막질별 적합성과 오차",
         "최신 리뷰: 제품 웨이퍼(product wafer) 대리 지표, 가상 계측",
         "NPW→PTW 전이 규칙 정량화: 어떤 파라미터가 이전되고 어떤 것이 새로 필요한가 (sim/calibration)"],
        "NPW/PTW 메타데이터 스키마 소유. 두 유형 실데이터 정렬·비교 규칙 정의 (§7.2 전이 규칙의 구현)"),
    "film-oxide": ("옥사이드 CMP 전문가", "cmp-integrator",
        "TEOS·HDP·SOD 등 SiO2 막의 CMP — ILD 평탄화·STI. 기계 제거 지배, 실리카/세리아 슬러리",
        ["cmp/preston-luo-dornfeld-mrr", "cmp/slurry-components-overview"],
        ["옥사이드 막 종류(TEOS/HDP/BPSG/SOD)와 밀도·경도·수화층 차이",
         "옥사이드 CMP 메커니즘: 수화층 형성과 기계 제거 (Cook 모델)",
         "ILD CMP: 다층 배선 평탄화, 글로벌/로컬 평탄도",
         "STI CMP: 세리아 슬러리 고선택비, 나이트라이드 정지, 디싱",
         "최신 리뷰: 세리아 첨가제 선택비 제어, 저결함 옥사이드 CMP",
         "옥사이드 막질별 Kp·선택비 파라미터 세트 정의 + 문헌값 재현 (sim/tier2)"],
        "옥사이드 실데이터(막종류·MRR·WIWNU·디싱) 스키마 + 보정 파라미터(Kp_oxide, 선택비) 정의"),
    "film-nitride": ("나이트라이드 CMP 전문가", "cmp-integrator",
        "SiN 막의 CMP 및 정지층 역할 — STI 선택비, 하드마스크 제거",
        ["cmp/slurry-components-overview"],
        ["SiN 막 종류(LPCVD/PECVD)와 물성, CMP 제거 난이도",
         "나이트라이드 정지층 메커니즘: 세리아 슬러리 선택비 화학",
         "STI 나이트라이드 손실·디싱과 공정 윈도우",
         "나이트라이드 직접 CMP: 하드마스크·게이트 응용",
         "최신 리뷰: 나이트라이드 선택비 첨가제, 3D NAND 응용",
         "나이트라이드 Kp·선택비 파라미터 + 문헌값 재현 (sim/tier2)"],
        "나이트라이드 실데이터 스키마 + 정지층 손실 보정 파라미터"),
    "film-poly-si": ("폴리실리콘 CMP 전문가", "cmp-integrator",
        "Poly-Si 막의 CMP — 게이트·3D NAND 채널홀·캐패시터. 알칼리 화학 용해+기계 제거",
        ["cmp/surface-chemistry-cu-w-pourbaix-passivation"],
        ["Poly-Si 물성(도핑·결정립)과 CMP 거동",
         "알칼리(KOH/TMAH/아민) 화학 용해 메커니즘과 pH 의존성",
         "Poly:oxide 선택비 설계와 게이트 CMP 공정 윈도우",
         "3D NAND 응용: 고종횡비 구조 위 Poly CMP, 디싱",
         "최신 리뷰: 고선택비 Poly 슬러리, 무결함 Poly CMP",
         "Poly-Si Kp·화학 용해율 파라미터 + 문헌값 재현 (sim/tier2)"],
        "Poly-Si 실데이터 스키마 + 도핑 의존 보정 파라미터"),
    "film-cu": ("구리 CMP 전문가", "cmp-integrator",
        "Cu 배선 CMP — 전기화학 부식·패시베이션 제어, 배리어 CMP, dishing/erosion. 화학 지배",
        ["cmp/surface-chemistry-cu-w-pourbaix-passivation", "cmp/pattern-dependent-dishing-erosion"],
        ["Cu CMP 3단계(벌크·소프트랜딩·배리어)와 각 단계 슬러리 요구",
         "Cu 전기화학: Pourbaix, BTA 패시베이션, 산화제-억제제 균형",
         "Cu dishing·erosion 물리와 패턴밀도·선폭 의존성",
         "배리어(Ta/TaN/Co) CMP와 Cu:배리어:옥사이드 선택비",
         "최신 리뷰: 저압 Cu CMP, 갈바닉 부식, 고종횡비 배선",
         "Cu 막질 Kp·화학 상수·dishing 커널 파라미터 + 문헌값 재현 (sim/tier2)"],
        "Cu 실데이터(NPW MRR·PTW dishing/erosion 맵) 스키마 + 패턴 의존 보정 파라미터 — PTW 보정의 대표 사례"),
    "film-w": ("텅스텐 CMP 전문가", "cmp-integrator",
        "W 플러그·contact CMP — 산화제(H2O2/Fe) 화학, 리세스·코어링, 배리어(Ti/TiN)",
        ["cmp/surface-chemistry-cu-w-pourbaix-passivation"],
        ["W CMP 메커니즘: 산화막(WO3) 형성-제거 순환, 산화제 종류별 차이",
         "Fe 촉매 H2O2 슬러리 화학과 알루미나/실리카 입자 선택",
         "W 플러그 리세스·코어링·키홀 결함과 공정 윈도우",
         "Ti/TiN 배리어 CMP와 W:배리어:옥사이드 선택비",
         "최신 리뷰: 3D NAND 워드라인 W CMP, 저결함 W 슬러리",
         "W Kp·산화 속도 파라미터 + 문헌값 재현 (sim/tier2)"],
        "W 실데이터 스키마 + 산화제 농도 의존 보정 파라미터"),
    "film-emerging": ("신소재 CMP 전문가", "cmp-integrator",
        "Co·Ru·Mo 배선, GST(PCM), 고유전체 등 차세대 막질의 CMP — Phase 2",
        ["cmp/surface-chemistry-cu-w-pourbaix-passivation"],
        ["Co 배선 CMP: 부식 민감성, 갈바닉, 억제제 화학",
         "Ru·Mo CMP: 난용해 금속의 산화제 화학(RuO4 독성 포함)",
         "GST·칼코게나이드 CMP: 연질막 결함 제어",
         "고유전체·2D 소재 CMP 동향",
         "최신 리뷰: 3nm 이하 배선 소재 로드맵과 CMP 요구",
         "신소재 파라미터 세트 골격 정의 (sim/tier2)"],
        "신소재 실데이터 스키마 초안"),
    # ── 장비
    "tool-platen-head": ("CMP 툴 플래튼·헤드 전문가", "cmp-integrator",
        "플래튼·헤드 구조, 멀티존 압력 제어, 리테이너링, RPM·유량이 웨이퍼 스케일 압력·속도 분포에 미치는 영향",
        ["equipment/cmp-tool-architecture", "physics/cmp-kinematics-rotary"],
        ["툴 아키텍처: 플래튼·헤드·리테이너링·슬러리 아암 — 주요 벤더(AMAT/Ebara) 비교",
         "멀티존 헤드 압력 제어와 존-반경 응답 행렬",
         "리테이너링 압력·마모와 엣지 프로파일",
         "RPM 비·유량·온도 제어와 MRR 안정성",
         "최신 리뷰: 폐루프 프로파일 제어, 헤드 신기술",
         "툴 설정 → 압력·속도 분포 모델 (sim/tier2, 기존 kinematics·wiwnu 확장)"],
        "툴 로그(존압력·RPM·유량·온도 시계열) 파싱·정렬 규칙 + 존 응답 행렬 보정"),
    "tool-endpoint": ("종말점 검출 전문가", "cmp-integrator",
        "광학·모터전류·와전류 EPD 원리와 신호 해석, 종말점 → 제거량 역산",
        ["equipment/cmp-tool-architecture"],
        ["EPD 원리별 비교: 광학(반사율/간섭)·모터전류(마찰)·와전류(금속 두께)",
         "신호 처리: 노이즈·필터·알고리즘·오버폴리시 제어",
         "막질별 EPD 적합성과 한계(투명막·다층)",
         "EPD 트레이스 → 제거량·잔막 역산 방법",
         "최신 리뷰: ML 기반 EPD, 인시츄 계측 통합",
         "EPD 신호 → 제거량 모델 (sim/tier2, 기존 wear_aware_endpoint 확장)"],
        "EPD 트레이스 실데이터 스키마 + 역산 보정"),
    "tool-post-clean": ("Post-CMP 세정 전문가", "cmp-integrator",
        "브러시 스크럽·메가소닉·화학 세정으로 잔류 입자·유기물·금속 오염 제거, 결함과의 연계",
        ["cmp/colloid-zeta-dlvo-slurry-stability"],
        ["Post-CMP 오염 종류(입자·유기 잔류·금속 이온)와 발생 원인",
         "PVA 브러시 스크럽 물리: 접촉·전단·제타전위 제어",
         "세정 화학: 암모니아·시트르산·계면활성제·부식 방지",
         "메가소닉·건조(IPA/마랑고니)와 워터마크",
         "최신 리뷰: 저결함 세정, 나노입자 제거 한계",
         "세정 조건 → 잔류 결함 확률 모델 (sim/tier2)"],
        "세정 후 결함 검사 데이터 스키마 + 세정 효율 보정"),
    # ── 물리·데이터
    "defect-scientist": ("CMP 결함 과학자", "cmp-integrator",
        "스크래치·잔류입자·부식·디싱·딜라미네이션의 발생 물리, 분류 체계, 원인 추적. 진단 에이전트의 핵심",
        ["cmp/pattern-dependent-dishing-erosion", "physics/tribology-friction-wear-stribeck"],
        ["결함 분류 체계(스크래치·마이크로스크래치·잔류입자·부식·피트·딜라미·워터마크)와 검사 장비",
         "스크래치 물리: 대입자·패드 파편·디스크 그릿 탈락 — 발생원별 형상 특징",
         "부식·피트: 갈바닉·국부 용해, 슬러리 화학 연계",
         "결함 밀도 통계와 수율 영향 모델",
         "최신 리뷰: 결함 자동 분류(ML), 근본원인 분석 방법론",
         "공정 조건 → 결함 발생 확률 모델 + 원인 역추적 규칙 (sim/tier2)"],
        "결함 맵·분류 라벨 스키마 소유 + 결함 확률 모델 보정. '왜 결함이 났나' 진단 근거 제공"),
    "cmp-data-engineer": ("CMP 데이터 엔지니어", "cmp-integrator",
        "실데이터 통합 스키마, 입력 검증, 단위 통일, 이상치, 익명화, 합성 데이터 생성. 캘리브레이션 층의 기반",
        [],
        ["CMP 공개 데이터셋 조사: 논문 부록·SEMATECH·대학 공개 데이터 — 무엇이 있고 무엇이 없는가",
         "통합 스키마 설계: 소모품·툴·웨이퍼·측정을 잇는 키 체계 (data/schema/*.json)",
         "단위·좌표계 통일(반경/다이 맵), 결측·이상치 처리 규칙",
         "합성 데이터 생성기: Tier1/2 모델 + 노이즈로 파이프라인 검증용 데이터 생성",
         "데이터 품질 게이트와 익명화(고객 식별 정보 제거) 규칙",
         "ingest 파이프라인 구현: 스키마 검증 → 표준화 → 파케이/DuckDB (sim/calibration/ingest.py)"],
        "이 에이전트 자체가 캘리브레이션 층의 데이터 기반. 각 서브에이전트가 정의한 스키마를 통합·검증한다"),
    "cmp-calibrator": ("CMP 캘리브레이션 과학자", "cmp-integrator",
        "물리 prior + 고객 실데이터 → 잔차 보정 모델. 소량 데이터 GP/BNN, NPW→PTW 전이, 불확실성, 드리프트. 제품의 핵심 기술",
        [],
        ["베이지안 캘리브레이션 기초: Kennedy-O'Hagan 프레임워크, 물리모델 + 불일치 항",
         "소량 데이터 GP 회귀: 커널 설계, 하이퍼파라미터, 물리 기반 평균함수",
         "전이학습: NPW 보정치를 prior로 PTW 잔차 학습 — 계층 베이지안",
         "불확실성 정량화와 예측 구간, 외삽 경고",
         "드리프트 감지: 소모품 로트·패드 교체·툴 PM 후 재보정 트리거",
         "sim/calibration/{prior,fit_npw,fit_ptw,predict,drift}.py 구현 + 합성 데이터 검증"],
        "이 에이전트가 §7 전체의 기술 소유자. 각 서브에이전트가 정의한 보정 파라미터를 실제로 피팅한다"),
    # ── 출력/판정 축 (사용자 지시 9/5: uniformity·roughness·TTV·post-CMP 금속 관리)
    "wafer-metrology": ("웨이퍼 계측·판정 전문가", "cmp-integrator",
        "CMP 결과를 무엇으로 측정하고 합격 판정하는가. WIWNU·TTV·radial TTV·CV·Ra/Rq·step height·잔막·엣지 롤오프. 측정 포인트 체계와 지표 정의를 표준화한다. 이 정의가 곧 시뮬 엔진의 출력 스키마다",
        ["cmp/wiwnu-pressure-velocity-wafer-scale", "cmp/pattern-dependent-dishing-erosion"],
        ["두께 계측 원리와 오차: 엘립소미터(투명막)·4점탐침/와전류(금속)·XRF·프로파일러·AFM — 막질별 적합성",
         "균일도 지표 정의 표준화: WIWNU(half-range/σ/3σ)·TTV(81pt max-min)·radial TTV(반경별 링 max-min 중 최대)·CV(σ/μ) — 정의마다 값이 다르므로 병기 원칙. 측정 포인트 체계(49/81pt·엣지 제외 폭·다이 맵)",
         "표면 조도(Ra·Rq·Rz)와 AFM 스캔 크기 의존성, 막질·슬러리별 문헌값 범위, 조도가 후속 공정(리소·증착)에 미치는 영향",
         "패턴 지표: step height·dishing·erosion·잔막(residual)·엣지 롤오프 — 측정 구조물과 판정 기준(스펙 예시)",
         "최신 리뷰: 인라인 계측·가상 계측(virtual metrology)·계측 샘플링 최적화",
         "출력 스키마 확정 + 지표 계산 라이브러리 구현 (sim/metrics/) — 반경 프로파일·다이 맵 입력 → 전 지표 동시 산출, 테스트 포함"],
        "고객 계측 데이터(포인트 좌표·두께·조도) 스키마 소유. 지표 정의 불일치(고객마다 다른 WIWNU 정의)를 매핑하는 규칙"),
    "surface-contamination": ("Post-CMP 표면 오염 전문가", "cmp-integrator",
        "CMP 후 웨이퍼 표면에 남는 금속 이온(Cu·Fe·K·Ca·Al)·이온성 잔류·유기 잔류의 발생원·측정·허용치·제거. 세정 화학과 슬러리 화학의 연결고리",
        ["cmp/surface-chemistry-cu-w-pourbaix-passivation", "cmp/colloid-zeta-dlvo-slurry-stability"],
        ["표면 오염 종류와 발생원: 슬러리 유래(Fe 촉매·K 완충제·Ce)·패드/디스크 유래·배선 금속(Cu) 재흡착·세정수 유래",
         "측정 기법: TXRF·VPD-ICPMS·SIMS·XPS — 검출 한계(atoms/cm²)·막질별 적합성·샘플링 위치",
         "금속 오염이 소자에 미치는 영향: Cu 확산·게이트 산화막 열화·수명 저하 — 허용치 근거(ITRS/IRDS)",
         "흡착 메커니즘과 제거 화학: 제타전위·pH·킬레이트(시트르산·EDTA)·희석 HF·오존수 — 막질별 세정 레시피",
         "최신 리뷰: 저농도 금속 잔류 제어, Co/Ru 신소재 오염, 세정 후 재오염(cross-contamination)",
         "슬러리 조성·세정 조건 → 잔류 금속 농도 예측 모델 골격 (sim/tier2) + 문헌값 대조"],
        "고객 TXRF/ICPMS 데이터 스키마 + 슬러리 로트별 오염 기여 보정 파라미터"),
}


def profile(aid, name, parent, role, prereq):
    pre = "\n".join(f"- [[../../knowledge/{p}]]" for p in prereq) or "- (없음 — 공개 문헌부터)"
    return f"""# {name} ({aid})

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: {parent} (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: 없음
- 다음 단원: Lv1-1

## 역할
{role}

## 선행 지식 (부모에게 상속)
{pre}

## 실데이터 책임 (ORG.md §7.3)
{AGENTS[aid][5]}

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
(크론이 갱신)
"""


def curriculum(aid, name, units, calib):
    lv = ["Lv1-1", "Lv1-2", "Lv2-1", "Lv2-2", "Lv3-1", "Lv3-2"]
    lines = [f"# 커리큘럼 — {name} ({aid})", "",
             "> 규칙: 순서대로 학습. 단원마다 ①출처 있는 지식노트(knowledge/) ②자기시험 3문항+답(EXAMS.md) ③가능하면 수식의 코드 재현.",
             "> 유료 논문은 미러 사이트 활용(사용자 지시 9/5). 출처 없는 수치는 '미검증' 표기.", ""]
    for l, u in zip(lv, units):
        lines.append(f"- [ ] {l} {u}")
    lines += ["", "## 캘리브레이션 단원 (ORG.md §7.3 — Lv2 완료 후, G2 이후 활성)",
              f"- [ ] Cal-1 {calib}", "",
              "## 확장 (Lv4 — 교수급)",
              "- 최신 논문 상시 추적, 기존 모델의 한계 지적 및 개선 제안",
              "- 부모·형제 에이전트와의 결합 모델 설계 리뷰", ""]
    return "\n".join(lines)


def exams(aid, name):
    return f"""# 자기시험 — {name} ({aid})

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

(아직 없음)
"""


created = []
for aid, (name, parent, role, prereq, units, calib) in AGENTS.items():
    d = ROOT / aid
    if d.exists():
        continue
    d.mkdir()
    (d / "PROFILE.md").write_text(profile(aid, name, parent, role, prereq))
    (d / "CURRICULUM.md").write_text(curriculum(aid, name, units, calib))
    (d / "EXAMS.md").write_text(exams(aid, name))
    created.append(aid)

print(f"생성 {len(created)}명: {', '.join(created)}")
print(f"전체 에이전트 디렉토리: {len([p for p in ROOT.iterdir() if p.is_dir()])}개")
