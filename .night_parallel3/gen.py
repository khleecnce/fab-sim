tasks = {
"wafertype": """담당 에이전트: **wafer-type**
학습 단원: **Lv2-2 측정 기법 — 엘립소미터·프로파일러(스타일러스)·AFM·XRF의 막질별 적합성과 측정 오차**
- agents/wafer-type/CURRICULUM.md Lv2-2 항목만 학습하라. 여러 단원을 얕게 훑지 마라.
- **먼저 읽어라(선행)**: knowledge/cmp/npw-ptw-test-wafer-fundamentals.md, knowledge/cmp/npw-ptw-pattern-effect-gw-physics.md, knowledge/cmp/wafer-metrology-thickness-methods.md, knowledge/cmp/uniformity-metrics-definitions-standards.md
- 조사 범위: `.venv/bin/python tools/scope.py --agent wafer-type --queries` 로 검색어 확인. `--check "<제목>"`으로 허용 여부 확인. 형제 에이전트(wafer-metrology의 지표 정의) 영역 침범 금지 — 너의 focus는 **NPW vs PTW 웨이퍼 유형에 따라 어떤 측정 기법이 적합/부적합한가**이다.
- 목표: 분광엘립소메트리(투명 유전체막 두께·굴절률, 금속막 불가), 스타일러스 프로파일러(step height·접촉식), AFM(nm 조도·국소), XRF(금속막 두께·조성)의 원리·적용 막질(SiO2/SiN/poly/Cu/W)·검출한계·오차원인. NPW(블랭킷)에서 유효한 기법이 PTW(패턴)에서 왜 제약되는가(스팟 크기 vs 다이 피치, 회절 등). 막질별 적합성 표.
- python verify: 최소 1개 정량 관계를 문헌값 상수로 박고 재현. 예) 엘립소미터 두께-위상 관계, 또는 XRF 형광강도-두께 선형/지수 관계, 또는 스타일러스 수직분해능 스펙. 문헌 수치와 대조하고 안 맞으면 정직히 기록.
- 상호링크 최소 3개: [[wafer-metrology-thickness-methods]], [[npw-ptw-test-wafer-fundamentals]], [[wafer-surface-roughness-afm-scan-scale-dependence]] 등 실존 파일.
- 노트: knowledge/cmp/wafer-type-metrology-techniques-suitability.md
""",
"surfcontam": """담당 에이전트: **surface-contamination**
학습 단원: **Lv2-2 흡착 메커니즘과 제거 화학 — 제타전위·pH·킬레이트(시트르산·EDTA)·희석 HF·오존수, 막질별 세정 레시피**
- agents/surface-contamination/CURRICULUM.md Lv2-2 항목만 학습하라. 여러 단원을 얕게 훑지 마라.
- **먼저 읽어라(선행)**: knowledge/cmp/post-cmp-metallic-contamination-sources.md, knowledge/cmp/metal-contamination-device-impact-irds-limits.md, knowledge/cmp/wafer-surface-metal-detection-txrf-vpdicpms-sims-xps.md, knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md, knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md
- 조사 범위: `.venv/bin/python tools/scope.py --agent surface-contamination --queries`. `--check`로 허용 확인.
- 목표: 금속 이온/입자가 웨이퍼 표면에 흡착하는 메커니즘(정전기적 인력·제타전위 부호, pH 의존), 킬레이트제(시트르산·EDTA)의 안정도상수(logK)와 금속(Fe·Cu·Ca) 착물 형성, 희석 HF(산화막 식각·재흡착 억제)·오존수(유기물 산화)의 역할, SC-1/SC-2(RCA) 세정 화학, 막질별(Cu는 부식 주의, oxide는 HF) 세정 레시피 차이. 제타전위 pH 의존 곡선·IEP(등전점) 값.
- python verify: 최소 1개 정량. 예) EDTA/시트르산-금속 안정도상수(logK) 문헌값 대조, 또는 특정 산화물(SiO2·Al2O3·CeO2) IEP pH 문헌값, 또는 pH에 따른 제타전위 부호 전환. 문헌 상수 박고 재현, 안 맞으면 정직 기록.
- 상호링크 최소 3개: [[post-cmp-metallic-contamination-sources]], [[colloid-zeta-dlvo-slurry-stability]], [[surface-chemistry-cu-w-pourbaix-passivation]] 등 실존 파일.
- 노트: knowledge/cmp/post-cmp-adsorption-cleaning-chemistry.md
""",
"diskdesign": """담당 에이전트: **disk-design**
학습 단원: **Lv2-2 디스크 설계 → 패드 표면 조도·asperity 분포 정량 관계**
- agents/disk-design/CURRICULUM.md Lv2-2 항목만 학습하라. 여러 단원을 얕게 훑지 마라.
- **먼저 읽어라(선행)**: knowledge/materials/pad-conditioning-wear-regeneration-balance.md, knowledge/materials/pad-hardness-porosity-measurement-methods.md, knowledge/materials/hertz-gw-contact-mechanics.md, knowledge/materials/gw-nominal-vs-local-pressure.md, knowledge/materials/pad-glazing-mechanism-mrr-decay.md
- 조사 범위: `.venv/bin/python tools/scope.py --agent disk-design --queries`. `--check`로 확인. focus는 **다이아몬드 디스크 설계 파라미터(그릿 크기·밀도·돌출)가 컨디셔닝된 패드 표면 조도·asperity 높이 분포·밀도에 미치는 정량 관계**. 형제(disk-kinematics의 sweep/하중) 영역 침범 금지.
- 목표: 컨디셔닝이 패드 표면에 만드는 asperity 통계(Ra·Rq·정점밀도·정점반경·높이분포 σ), 그릿 크기↔조도 스케일링, GW 모델 파라미터(β 반경, η 밀도, σ 표준편차)와 디스크 스펙 연결, 컨디셔닝 후 패드 조도 실측값(μm 단위). Preston 계수/MRR와 asperity 접촉면적 연계.
- python verify: 최소 1개 정량. 예) GW 모델에서 실접촉면적 A_r ∝ 하중 관계, 또는 그릿크기-패드조도 문헌 데이터 회귀, 또는 asperity 높이 σ↔MRR 경향. 문헌 상수 박고 대조, 안 맞으면 정직 기록.
- 상호링크 최소 3개: [[pad-conditioning-wear-regeneration-balance]], [[hertz-gw-contact-mechanics]], [[pad-hardness-porosity-measurement-methods]] 등 실존 파일.
- 노트: knowledge/materials/disk-design-pad-roughness-asperity-relation.md
""",
}
common = open("_common.txt").read()
for k,v in tasks.items():
    open(f"{k}.txt","w").write(common + "\n===== 아래는 너의 담당 =====\n" + v)
    print("wrote", k, len(v))
