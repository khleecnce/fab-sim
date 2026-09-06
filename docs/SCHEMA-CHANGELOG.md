# 스키마 변경 로그

> sim-architect 소유. Recipe/WaferResult/UniformityMetrics 필드 변경은 여기 기록.

## 2026-09-06 — UniformityMetrics: radial 지표 문헌 정의로 교체 (wafer-metrology 구현요청)

**배경**: `sim/metrics/uniformity.py`는 PROVISIONAL 상태였고, radial 지표는 사용자 회사 관행
(반경 링별 max−min 중 최대)을 임시로 쓰고 있었다. wafer-metrology Lv1-2가
`knowledge/cmp/uniformity-metrics-definitions-standards.md`로 문헌 정의를 확정, PROFILE.md
"구현 요청"으로 인계. ORG 절대원칙(회사 관행을 코드에 그대로 옮기지 않는다)에 따라
문헌 default를 1차 필드로, 회사 관행은 별도 이름으로 강등 병기.

**필드 변경 (`UniformityMetrics`)**:
| 이전 | 이후 | 의미 |
|---|---|---|
| `radial_ttv_nm` (회사 관행이 곧 default였음) | `radial_maxring_range_nm` | 반경 링별 (max−min) 중 최대. **회사 관행, default 아님**으로 강등 |
| `radial_ttv_ring` | `radial_maxring_range_ring` | 위 값이 발생한 링 인덱스 |
| (없음) | `ring_mean_nm` (신규) | 링별 평균 두께 — 방위각평균 반경프로파일 t̄(r)의 근사 |
| (없음) | `radial_sigma_pct` (신규, 문헌 default 후보) | 100·σ(ring_mean)/mean |
| (없음) | `radial_range_pct` (신규, 문헌 default) | 100·(max−min of ring_mean)/(2·mean) — CLI/UI 1차 표시값 |
| `ttv_nm`, `cv_pct`, `wiwnu_halfrange_pct`, `wiwnu_3sigma_pct`, `ring_ttv_nm`(링 내부 TTV) | 변경 없음 | 문헌과 회사 관행이 일치(TTV, CV) 또는 이미 병기(WIWNU) |
| `definition` | 문구 갱신 | 근거 노트 링크 추가, PROVISIONAL 문구 제거 |

**연쇄 변경**: `sim/engine.py` `WaferResult.summary()`의 키 `radial_ttv_nm` → `radial_range_pct` +
`radial_maxring_range_nm`. `sim/cli.py`, `sim/demo_app.py` 출력 라벨 갱신.
`tests/test_engine.py::test_metric_definitions`, `test_points_and_profile_agree` 필드명 갱신 +
문헌 항등식(3σ=3×CV) 회귀 추가.

**하위호환 없음** — 이 시점에 외부 소비자(캘리브레이션 등) 없음, M3 전이라 필드명 확정 비용이 낮음.
향후 `sim/calibration/`이 이 스키마를 소비할 때는 `radial_range_pct`를 1차로 참조할 것.
