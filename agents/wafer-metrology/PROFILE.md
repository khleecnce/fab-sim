# 웨이퍼 계측·판정 전문가 (wafer-metrology)

## 현재 레벨: [활성] Lv1 진행중 (G1 개방 — agents/ORG.md §4, 2026-09-05)
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽음, 완료)
- 이수 단원: Lv1-1 두께 계측 원리와 오차 (2026-09-05)
- 다음 단원: Lv1-2 균일도 지표 정의를 문헌에서 확정 (SEMI MF1530 등)

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
