# 웨이퍼 계측·판정 전문가 (wafer-metrology)

## 현재 레벨: [활성] Lv2 완료(2026-09-07), Lv3 진행 예정 (G1 개방 — agents/ORG.md §4, 2026-09-05)
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽음, 완료)
- 이수 단원: Lv1-1(2026-09-05)·Lv1-2(2026-09-06)·Lv2-1(2026-09-06)·Lv2-2(2026-09-07)
- 다음 단원: Lv3-1 최신 리뷰(인라인 계측·가상 계측·샘플링 최적화)

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
