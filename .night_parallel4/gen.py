tasks = {
"wafmet": """담당 에이전트: **wafer-metrology**
학습 단원: **Lv3-1 최신 리뷰 — 인라인 계측·가상 계측(virtual metrology)·계측 샘플링 최적화**
- agents/wafer-metrology/CURRICULUM.md Lv3-1 항목만 학습하라. 여러 단원을 얕게 훑지 마라.
- **먼저 읽어라(선행)**: knowledge/cmp/wafer-metrology-thickness-methods.md, knowledge/cmp/uniformity-metrics-definitions-standards.md, knowledge/cmp/wafer-surface-roughness-afm-scan-scale-dependence.md, knowledge/cmp/pattern-metrics-dishing-erosion-stepheight.md
- 조사 범위: `.venv/bin/python tools/scope.py --agent wafer-metrology --queries` 로 검색어 확인. `--check "<제목>"`으로 허용 여부 확인. focus는 **CMP 공정의 계측 전략** — 인라인/인시추 계측, 가상 계측(VM: 공정·장비 센서 데이터로 계측치 예측), 계측 샘플링 최적화(어느 웨이퍼/어느 포인트를 측정할까). 형제(wafer-type의 NPW/PTW 해석 차이)나 지표 정의(Lv1-2에서 이미 확정) 재탕 금지.
- 목표: (1) 인라인 계측 vs 오프라인 계측의 트레이드오프, in-situ EPD와의 구분. (2) 가상 계측(VM) — 입력 특징(FDC 센서: 압력·모터전류·마찰·시간), 모델(회귀/PLS/신경망), R²·RMSE 등 성능 지표 문헌값, APC(피드백/피드포워드 제어) 연계. (3) 계측 샘플링 최적화 — dynamic sampling, 웨이퍼당 측정 포인트 축소가 검출력에 미치는 영향. 반도체 CMP VM 리뷰 논문(예: Susto, Chien, Moyne 등)에서 정량값 확보.
- python verify: 최소 1개 정량. 예) VM 모델의 보고된 R²/RMSE 값을 상수로 박고 재현 조건 확인, 또는 샘플링 포인트 수 축소 시 평균 추정 표준오차 스케일링(SE ∝ 1/√n) 재현, 또는 PLS 성분수-설명분산 관계. 문헌 상수 박고 대조, 안 맞으면 정직 기록.
- 상호링크 최소 3개: [[wafer-metrology-thickness-methods]], [[uniformity-metrics-definitions-standards]], [[cmp-tool-endpoint-thermal-slurry-delivery]] 등 실존 파일(knowledge/ 목록 확인 후 실제 파일명).
- 노트: knowledge/cmp/inline-virtual-metrology-sampling-optimization.md
""",
"wafertype": """담당 에이전트: **wafer-type**
학습 단원: **Lv3-1 최신 리뷰 — 제품 웨이퍼(product wafer) 대리 지표·가상 계측**
- agents/wafer-type/CURRICULUM.md Lv3-1 항목만 학습하라. 여러 단원을 얕게 훑지 마라.
- **먼저 읽어라(선행)**: knowledge/cmp/npw-ptw-test-wafer-fundamentals.md, knowledge/cmp/npw-ptw-pattern-effect-gw-physics.md, knowledge/cmp/wafer-type-metrology-techniques-suitability.md, knowledge/cmp/pattern-metrics-dishing-erosion-stepheight.md
- 조사 범위: `.venv/bin/python tools/scope.py --agent wafer-type --queries`. `--check`로 허용 확인. focus는 **제품 웨이퍼를 직접 파괴계측하지 않고 대리 지표(모니터 웨이퍼·인접 다이·전기적 파라미터)로 추정하는 방법**과 그 한계. 형제(wafer-metrology의 VM 일반론)와 겹치지 않게 — 너는 **NPW(모니터)가 PTW(제품)의 대리로 얼마나 유효한가**에 집중.
- 목표: (1) monitor wafer(send-ahead)로 제품 웨이퍼 상태를 추정하는 관행과 오차원. (2) 제품 웨이퍼 대리 지표 — 전기 테스트(Rs·via resistance)·인라인 광학과 실제 다이 성능의 상관. (3) NPW→PTW 예측이 실패하는 지점(패턴밀도 의존)을 대리 지표가 어떻게 보완/못 하는가. (4) 가상 계측이 PTW에 적용될 때 NPW와 다른 특징이 필요한 이유.
- python verify: 최소 1개 정량. 예) send-ahead 모니터-제품 편차의 보고된 상관계수, 또는 패턴밀도 vs 잔막의 대리 추정 오차, 또는 사각(blanket) 제거율 대비 패턴 유효 제거율 비(density factor) 문헌값 재현. 상수 박고 대조, 안 맞으면 정직 기록.
- 상호링크 최소 3개: [[npw-ptw-test-wafer-fundamentals]], [[npw-ptw-pattern-effect-gw-physics]], [[wafer-type-metrology-techniques-suitability]] 등 실존 파일.
- 노트: knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md
""",
"surfcontam": """담당 에이전트: **surface-contamination**
학습 단원: **Lv3-1 최신 리뷰 — 저농도 금속 잔류 제어, Co/Ru 신소재 오염, 세정 후 재오염(cross-contamination)**
- agents/surface-contamination/CURRICULUM.md Lv3-1 항목만 학습하라. 여러 단원을 얕게 훑지 마라.
- **먼저 읽어라(선행)**: knowledge/cmp/post-cmp-metallic-contamination-sources.md, knowledge/cmp/metal-contamination-device-impact-irds-limits.md, knowledge/cmp/post-cmp-adsorption-cleaning-chemistry.md, knowledge/cmp/wafer-surface-metal-detection-txrf-vpdicpms-sims-xps.md, knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md
- 조사 범위: `.venv/bin/python tools/scope.py --agent surface-contamination --queries`. `--check`로 허용 확인. focus는 **최신(2015~) 세정/오염 제어 리뷰** — 저농도(1E9~1E10 atoms/cm² 이하) 금속 잔류를 어떻게 더 낮추나, Co·Ru 등 신소재 배선의 오염/부식 특이성, 세정 장비/브러시/린스에서의 재오염(cross-contamination) 메커니즘.
- 목표: (1) 저농도 금속 잔류 제어 최신 기법(기능성 세정액·전해 이온수·나노버블 등)과 달성 수준(atoms/cm²). (2) Co/Ru CMP 후 오염·갈바닉 부식 — 기존 Cu/W와 화학적 차이(용해거동·pH창). (3) cross-contamination — PVA 브러시 흡착·재방출, 세정조 carry-over, 재흡착 억제 화학. IRDS 최신 로드맵의 표면 금속 허용치와 비교.
- python verify: 최소 1개 정량. 예) 갈바닉 부식 전위차(Co vs Cu vs Ru 표준환원전위 문헌값)로 부식 방향 판정, 또는 IRDS 허용치 대비 달성 잔류값 배수, 또는 재흡착 억제에 필요한 pH(제타전위 부호 전환) 재현. 상수 박고 대조, 안 맞으면 정직 기록.
- 상호링크 최소 3개: [[post-cmp-adsorption-cleaning-chemistry]], [[metal-contamination-device-impact-irds-limits]], [[surface-chemistry-cu-w-pourbaix-passivation]] 등 실존 파일.
- 노트: knowledge/cmp/low-level-metal-cobalt-ruthenium-cross-contamination.md
""",
}
common = open("_common.txt").read()
for k,v in tasks.items():
    open(f"{k}.txt","w").write(common + "\n===== 아래는 너의 담당 =====\n" + v)
    print("wrote", k, len(v))
