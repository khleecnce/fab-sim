# 웨이퍼 계측·판정 전문가 (wafer-metrology)

## 현재 레벨: [활성·유지보수] 커리큘럼 6/6 완주 (2026-09-08)
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽음, 완료)
- 이수 단원: Lv1-1(2026-09-05)·Lv1-2(2026-09-06)·Lv2-1(2026-09-06)·Lv2-2(2026-09-07)·Lv3-1(2026-09-08)·Lv3-2(2026-09-08)
- 다음: Cal-1(캘리브레이션 단원, G2 이후 활성)까지 대기. 유지보수 모드 — 신규 논문 발견 시 Lv4 확장 노트 작성

## 역할
CMP 결과를 무엇으로 측정하고 합격 판정하는가. WIWNU·TTV·radial TTV·CV·Ra/Rq·step height·잔막·엣지 롤오프. 측정 포인트 체계와 지표 정의를 표준화한다. 이 정의가 곧 시뮬 엔진의 출력 스키마다

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/wiwnu-pressure-velocity-wafer-scale]]
- [[../../knowledge/cmp/pattern-dependent-dishing-erosion]]

## 실데이터 책임 (ORG.md §7.3)
고객 계측 데이터(포인트 좌표·두께·조도) 스키마 소유. 지표 정의 불일치(고객마다 다른 WIWNU 정의)를 매핑하는 규칙

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- 2026-09-05 Lv1-1 두께 계측 원리(엘립소미터·리플렉토미터·와전류·4점탐침·XRF)
  — knowledge/cmp/wafer-metrology-thickness-methods.md
  (check_knowledge.py·verify_claims.py 통과, EXAMS.md 3문항 작성)
- 2026-09-06 Lv1-2 균일도 지표 정의 문헌 확정(TTV·WIWNU σ/3σ/half-range·CV·radial·49점체계)
  — knowledge/cmp/uniformity-metrics-definitions-standards.md
  (check_knowledge.py·verify_claims.py 통과, DOI 4건 실존확인, EXAMS.md 3문항 작성.
   1차 출처: US6922603B1 특허 + Lee&Boning 1999/Kumar 2019/robust-metric 1995 DOI)
- 2026-09-07 Lv2-2 패턴 지표 정의 문헌 확정(dishing·erosion·step height·residual·edge roll-off, 측정 구조물·판정 스펙)
  — knowledge/cmp/pattern-metrics-dishing-erosion-stepheight.md
  (check_knowledge.py·verify_claims.py 통과, DOI 7건 Crossref/OpenAlex 실존확인, 특허 4건(US5723874·US7197726B2·
   US10600634·US9829310) 텍스트 확인, EXAMS.md 3문항 작성. 1차 원문 확보: Park VMIC98·Boning MRS99·Pan CMP-MIC99·
   Park ECS99·Tugbawa CMP-MIC2001(boning.mit.edu/mtlsites PDF)·ITRS 2007 Interconnect·NIST 스텝하이트 문서·
   Taylor Hobson ISO 5436-1 튜토리얼. 미확보: ISO 5436-1·SEMI M67/M68/M77 원문, Steigerwald 1994 본문)

## 구현 요청 (소프트웨어 부문 인계 — 직접 sim/ 수정 금지)

### [High] sim/metrics/uniformity.py PROVISIONAL 정의를 문헌 정의로 교체
- **무엇을**: 현재 `UniformityMetrics.definition` 문자열이 "PROVISIONAL — Lv1-2 학습 후 확정"이며
  docstring도 잠정 상태다. 이를 아래 문헌 확정 정의로 교체하고, docstring 상단에 근거 노트
  `knowledge/cmp/uniformity-metrics-definitions-standards.md`를 링크할 것.
- **근거노트**: knowledge/cmp/uniformity-metrics-definitions-standards.md (게이트 2종 통과)
- **확정 정의(문헌 default)**:
  - TTV = t_max − t_min (SEMI MF1530; Kao&Chung 2021 Eq.1.5). "무엇의 max−min인가"(기판/잔막/제거량) 필드에 명시.
  - WIWNU **default = 3σ**: 100·3σ/mean (US6922603B1 특허). 1σ(=CV)·half-range=(max−min)/(2·mean)도 병기 출력.
  - CV = 100·σ/mean — 1σ WIWNU와 **동일 수**임을 코드 주석에 명시. ddof=0 default, 소표본 시 ddof 메타 기록.
  - radial: **문헌 default = 방위각 평균 반경프로파일 t̄(r)의 σ(또는 range)/mean**. 현재 코드의
    "링별 max−min의 최대"(회사 관행)는 **별도 필드명**(예: `radial_maxring_range_nm`)으로 강등 병기,
    default 아님으로 표기. 단일 표준식 부재를 docstring에 명시.
- **검증 문헌값(회귀테스트로 넣을 것)**:
  - 3σ WIWNU = 3 × 1σ WIWNU (항등, <1e-12)
  - CV ≡ 1σ WIWNU (항등, <1e-12)
  - 면적가중 선형 반경프로파일(Pc=1,Pe=1.5) half-range = 18.75%([[../../knowledge/cmp/wiwnu-pressure-velocity-wafer-scale]] §5 해석해, 상대오차<0.2%)
  - 49점 체계 = 중심1 + 3링(8/16/24) (US6922603B1)
- **주의**: edge exclusion 폭을 입력·출력 메타로 노출(지표와 함께 보고 필수). 회사 관행식을 삭제하지
  말고 병기(Cal-1 고객 정의 mapping에서 필요).
- **우선순위**: High — 이 정의가 곧 엔진 출력 스키마이고 현재 잠정 상태라 다운스트림(보고/판정)이 잠정에 묶여 있음.

**→ 처리 완료 (2026-09-06, software-lead)**: `sim/metrics/uniformity.py` PROVISIONAL 제거, 요청대로
radial 지표를 문헌 default(방위각평균 반경프로파일 σ/range = `radial_sigma_pct`/`radial_range_pct`)로
교체하고 회사 관행은 `radial_maxring_range_nm`/`_ring`으로 강등 병기. 항등식 회귀(3σ=3×CV) 추가.
119 tests passed. `docs/SCHEMA-CHANGELOG.md` 신설 기록. 커밋 f3ecfc6.


### [High] sim/metrics/pattern_metrics.py 신설 — 패턴 지표(dishing·erosion·step height·residual·ROA) 계산 라이브러리
- **무엇을**: 프로파일러 1D 스캔(x, z)·광학 두께맵·반경 두께 프로파일을 입력으로 아래 지표를 산출하는 순수함수 모듈.
  (a) `step_height_iso5436(x, z, regions)` — ISO 5436-1형 최소제곱 `Z=aX+b+hδ`, step=2h, 전이부 인접영역 제외 옵션,
      기판 곡률(2차) 제거 옵션. (b) `dishing_erosion_from_profile(x, z, field_mask, line_mask, array_mask)` —
      **default 기준면 = 필드 oxide면(Pan 1999식)**, field_loss(별도 입력: 광학 두께)·erosion·dishing·총손실을
      모두 출력하고 Park 1998식(증착두께 기준)으로의 환산값 병기. 출력에 `stage`(pre-clear step / post-clear dishing)
      메타 필수. (c) `roa(r, t, convention)` — SEMI M77형 ROA. convention 파라미터로 기준점(P1,P2,P3)·기준선 차수를
      명시 강제(default 없음 — 규약 미지정 시 예외). 사전 정의 규약 2종: `sunedison_300mm`(120/140→148 mm),
      `edge_3_6mm`(엣지에서 3/6 mm). (d) `itrs_allowance(height_nm, frac=0.10)` — "10%×height" 규칙 판정기.
      (e) residual: `residual_metal_fraction(map)`은 결함량(0 허용 판정), `remaining_thickness = as_dep − removed`는
      연속량으로 **필드명 분리**.
- **근거노트**: knowledge/cmp/pattern-metrics-dishing-erosion-stepheight.md (게이트 2종 통과) §1·§6.
- **검증 문헌값(회귀테스트)**: ITRS 2007 Table INTC2a erosion 행 9개 연도 = round(0.1×(pitch/2)×A/R) (±0.5 nm);
  IBM US5723874 표 11행 space ratio=oxide/pitch, 밀도=1−space ratio(<0.06%p); 합성 50 nm 스텝 LS 회수 <1 nm;
  곡률 2 µm/9 µm 스텝 단순피팅 오차 3–30%(Taylor Hobson "약 10%"); 동일 프로파일 두 ROA 규약 차이 >30%;
  Pan 1999 100 µm dishing 50 nm vs ITRS-2007 24 nm 비율 1.5–3.
- **주의**: 회사 관행 정의(있다면)는 default로 두지 말고 별도 필드로 병기(Cal-1 매핑 소관). erosion은 프로파일이
  아니라 광학 두께차로도 들어올 수 있으므로 입력 경로 2개 모두 지원.
- **우선순위**: High — Lv3-2(출력 스키마 확정·지표 라이브러리)의 전제이며, 현재 sim/metrics에는 blanket 지표(uniformity.py)만 있음.

## Lv2-1 이수 (2026-09-06)
표면 조도(Ra·Rq·Rz)와 AFM 스캔 크기 의존성 학습. 지식노트:
knowledge/cmp/wafer-surface-roughness-afm-scan-scale-dependence.md.
핵심: Rq는 재질 고유 상수가 아니라 스캔 크기의 함수(self-affine fractal, w(L)∝L^H) —
스캔 크기 명시 없는 조도 비교는 무의미함을 확인. Rq/Ra=√(π/2)≈1.2533 항등식 재현(가우시안
합성, <1% 오차), self-affine 스케일링 지수 자기재현(<50% 오차, 합성검증). 정량 문헌값:
SiC CMP Ra≤0.13nm(Wang et al. 2026, DOI 10.1021/acs.langmuir.5c05695). 미확보: SiO2/Cu/W
개별 대표값(검색 오매칭), 리소 공정 영향 정량화, Sayles&Thomas(1978)/Palasantzas(1993)
원문(미러 사이트 접속 차단) — 다음 재시도 대상으로 남김. check_knowledge.py/verify_claims.py
둘 다 통과(정규식 버그 수정 후 재확인, tools/verify_claims.py DOI 정규식이 "(NN)" 포함
Elsevier DOI를 절단하던 문제를 학습총괄이 수정).

## Lv2-2 이수 (2026-09-07)
패턴 지표(dishing·erosion·step height·잔막·엣지 롤오프)의 정의·측정 구조물·판정 기준 학습. 지식노트:
knowledge/cmp/pattern-metrics-dishing-erosion-stepheight.md.
핵심: dishing/erosion 정의는 기준면(최종 oxide면 vs 증착두께 vs 필드 oxide면+field loss 분리)에 따라 셋으로
갈리며 총손실=field loss+erosion+dishing 항등식으로 상호 환산 — default는 Pan 1999식(필드면 기준, field loss
별도). 스텝하이트는 ISO 5436-1 교정표준 측정법의 LS 직선피팅(Z=aX+b+hδ, step=2h)을 차용. ITRS 2007 erosion
허용치 행이 "10%×배선높이" 비율 규칙임을 9개 연도 전부 재현(±0.5 nm). ROA는 기준점 규약(SunEdison 120/140/148 mm
vs Corning 엣지 3/6 mm)에 따라 같은 프로파일에서 4배 차이 — 규약 병기 필수. "엣지 롤오프"(웨이퍼 기하 vs CMP
제거율 프로파일)와 "residual"(잔류 금속 결함 vs 잔여 막두께)은 각각 두 개념이라 스키마 필드 분리.
측정 구조물 8종(MIT area/pitch/density 마스크, AMAT 100 µm 트렌치·5 µm 루프, IBM 정사각/서펜타인 모니터,
PDF Solutions MT-Kelvin, ITRS 기준 구조)의 치수를 1차 문서에서 표로 정리. 미확보: ISO 5436-1·SEMI 원문,
Steigerwald 1994 본문, STI 필드폭-dishing 수치 출처. check_knowledge.py/verify_claims.py 둘 다 통과.

## Lv3-1 이수 (2026-09-08)
최신 리뷰 — 인라인(통합) 계측 vs 오프라인 계측, 가상 계측(VM), 계측 샘플링 최적화. 지식노트:
knowledge/cmp/inline-virtual-metrology-sampling-optimization.md.
핵심: (1) 계측 3층위(in-situ EPD / 통합·인라인 / 오프라인)는 시간축·출력·제어 대상이 달라 대체 불가 — AMD US6645780이
통합 계측=W2W(dynamic-time) 루프, 오프라인=L2L(constant-time) 루프로 분리하고 오프라인의 문제를 "too late"(지연)로 명시.
(2) VM 공개 벤치마크 PHM 2016 CMP(Di, Jia & Lee 2017, CC-BY 원문): FDC 125특징 → 가중 앙상블 테스트 MSE 7.07(1위),
DBN 7.29 < tree bagging 7.22, persistent 8.23 < KNN 9.60 — 특징공학·시계열성이 딥러닝을 이김; Table 4/5/6 재현.
IBM US9240360은 VM 예측오차와 실측오차에 신뢰도 가중을 두어 "실측 간격 최대화"를 청구. (3) 샘플링: 로트 수준
static→adaptive→dynamic(Nduhura-Munga 2013 원문, material-at-risk 개념), 웨이퍼 내 사이트는 FSCA로 50→7점(NMSE 0.96 %)
+ 동적 공간 샘플링(MSSI/WOI, 정적 검출률 43.8 %→100 %)(McLoone, Johnston & Susto 2018 저자원고; Table I~IV 재현, CDS WOI
8행 닫힌형 ±0.1 %p). 합성 검증 2건: 49→9점 SE 2.33배·range WIWNU 과소추정·엣지 롤오프 무감; VM 보강 EWMA R2R에서
VM 오차가 드리프트보다 작을 때만 이득. 미확보: Rao 2000 ISSM·Jebri 2017·Kang 2009·Dreyfus 2021·Breidung 2025(초록만),
Zhang 2021 Wide&Deep MSE 6.33(스니펫, 미검증), 통합 계측기 정밀도/포인트/처리량의 1차 비교, CMP 실데이터 FSCA 성분수.
check_knowledge.py/verify_claims.py 둘 다 통과(출처 17건 실존, verify 4블록). EXAMS.md 3문항 작성.

### [Medium] sim/metrics/sampling_plan.py 신설 — 계측 샘플링 플랜 객체와 샘플링 손실 정량화 (구현 요청)
- **무엇을**: (a) `SitePlan`(사이트 좌표 목록 + 이름: `p49_us6922603`, `p9_center_4_4`, `fsca_custom`) 과
  `LotPlan`(static 1/n, adaptive, dynamic 자리표시자)을 정의하고, 엔진의 전 반경 프로파일/다이 맵에서 플랜대로
  샘플링해 [[uniformity.py]] 지표를 계산하는 `sample_and_score(profile_map, site_plan) -> metrics + meta`.
  (b) `material_at_risk(lot_plan)` = 두 계측 사이 처리 로트 수(Nduhura-Munga 2013). (c) `fsca_select(X, tau=0.99)`
  — 이력 두께 행렬 X(N×V)에서 전진선택 성분분석으로 사이트 우선순위·k*·CVE 벡터 반환, `pca_lower_bound(X, tau)`
  병기; `wmr_fit/predict`(측정 사이트→미측정 사이트 선형회귀). (d) 동적 공간 샘플링 `sds_plan(clusters, t)`와
  지표 `mssi`, `woi = (ceil(V/Vm)-1)/MSSI*100`.
- **근거노트**: knowledge/cmp/inline-virtual-metrology-sampling-optimization.md §3.2·§3.3·§4 블록 2·3 (게이트 2종 통과).
- **검증 문헌값(회귀테스트)**: McLoone 2018 Table I 누적분산 → φ_PCA=5, k*=7 (τ=99 %); Table III CDS WOI 8행 =
  (ceil(50/Vm)−1)/(50−Vm)×100 (±0.1 %p); RDS WOI=100; 합성 RBF 프로파일에서 FSCA NMSE < 무작위 NMSE(모든 Vm);
  49점→9점 잡음 SE 비 √(49/9)=2.33(±10 %); range형 WIWNU는 부분집합에서 항상 ≤ 전체(항등).
- **주의**: 사이트 플랜 이름·엣지 제외 폭을 지표와 함께 메타로 출력(Lv1-2 요청과 동일 원칙). FSCA 산업 사례는 CMP가
  아니므로 CMP 성분수는 시뮬레이터 합성 데이터로만 보고하고 "문헌값 아님" 표기.
- **우선순위**: Medium — Lv3-2 출력 스키마에 `measurement_mode`/`site_plan` 메타가 들어가야 하므로 그 전에 인터페이스만이라도 확정 필요.

**→ 부분 처리 완료 (2026-09-08, software-lead, S36)**: `sim/metrics/sampling_plan.py` 신설 —
로트 샘플링 5함수(`material_at_risk`/`mssi_min_balanced`/`mssi_cds`/`woi`/`static_sampling_plan`).
§3.1(Nduhura-Munga material_at_risk 정의) + §4 블록2 Table III(V=50) CDS WOI% 그대로 재현 테스트 5건.
**미착수 잔여**: FSCA/PCA 사이트선택(fsca_select/pca_lower_bound), wmr_fit/predict, sds_plan —
전부 데이터 기반(이력 두께 행렬 X 필요) 알고리즘이라 이번 회차 범위 밖으로 명시 제외. 필요시 재요청.

### [Low] sim/metrics/vm_baseline.py — Di 2017형 VM 베이스라인(persistent + LR + tree bagging 가중 앙상블)
- **무엇을**: 시뮬레이터 런 로그(P 존별·V·패드/디스크 사용량·폴리싱 시간·선행 MRR 시차)를 특징으로 웨이퍼별 평균 MRR을
  예측하는 베이스라인. 가중치 w=(1/e³)/Σ(1/e³), e=mean(ε)+3·std(ε)(Monte-Carlo CV). 의존성은 numpy(+선택적 sklearn).
- **근거노트**: 같은 노트 §2.2·§4 블록 1·4.
- **검증**: 합성 데이터에서 persistent MSE < KNN MSE, 앙상블 MSE ≤ 최고 단일 모델(Di 2017의 상대 순위 재현 — 절대 MSE
  7.07은 툴·레시피 종속이라 비교 대상 아님); VM 보강 EWMA R2R에서 σ_VM < 드리프트일 때만 출력 σ 감소(블록 4).
- **우선순위**: Low — APC 연계(G3 이후) 전까지는 데모 성격.


## Lv3-2 이수 (2026-09-08) — 커리큘럼 6/6 완주
출력 스키마 확정: ASTM/SEMI 두께·평탄도 표준 약어 체계(GBIR/GF3R/GF3D/GFLR/GFLD/SBIR/SBID/SF3R/SF3D/SFQR/SFQD 11종)와
Bow/Warp를 문헌(3차 편집본 경유, ASTM F534/F657/F1241/F1390/F1530 발췌)에서 확정. 지식노트:
knowledge/cmp/wafer-metrology-output-schema-site-flatness-standards.md.
핵심: GBIR(이상 평탄 후면 기준 range)이 SEMI MF1530 TTV와 수식·가정이 동일함을 원문 인용으로 교차검증(assert 재현).
uniformity.py에 없는 SFQR류(사이트별 국소 최소자승 평면) 필드를 새로 확인 — 리소그래피 depth-of-focus 판정에 필요하나
현재 코드는 전역 range/시그마만 가짐. Bow(중심 1점)와 Warp(전체 range)가 서로 독립적 정보임을 원문 Figure 4 예시로 확인
(Bow=0이어도 Warp>0 가능). "49점 웨이퍼 맵=산업표준" 통념의 1차 근거는 Bibby & Harwood(1997, DOI 10.1016/S0040-6090(97)00435-5)
초록만 확인(원문 Cloudflare 차단으로 미확보) — Lv1-1·Lv3-1과 합쳐 노트 3편 연속으로 SEMI 표준문서 직접 인용을 못 찾음(미검증으로 명시).
check_knowledge.py/verify_claims.py 둘 다 통과(출처 1건 실존, verify 1블록 통과). EXAMS.md 3문항 작성. CURRICULUM 6/6 완주.

### [Low] sim/metrics/flatness.py 신설 — ASTM/SEMI 평탄도 지표 11종 + Bow/Warp (구현 요청)
- **무엇을**: GBIR/GF3R/GF3D/GFLR/GFLD/SBIR/SBID/SF3R/SF3D/SFQR/SFQD 계산 함수(입력: 기존 compute_metrics_points와 동일
  (x,y,value) 사이트 배열) + bow(3점 기준평면, 중심값)·warp(3점 또는 최소자승 평면, range). 기준평면 계산은
  numpy.linalg.lstsq로 충분(신규 외부 의존성 없음).
- **근거노트**: knowledge/cmp/wafer-metrology-output-schema-site-flatness-standards.md §1.2·§1.3.
- **검증 문헌값(회귀테스트로 승격)**: 노트 §3 assert 그대로 — SBIR(1.0,-0.5)=1.5, SBID(1.0,-0.5)=1.0,
  Fig.8a/8b 둘 다 SBIR=SBID=1.0, GBIR(725.3,724.1)=TTV(725.3,724.1)=1.2(항등식).
- **우선순위**: Low — 엔진 WaferResult에 형상(bow/warp) 필드 자체가 없어 스키마 확장이 선행되어야 함. G1 유지보수 모드 중 후순위.
