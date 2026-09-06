# FabSim 아키텍처 — sim/ 모듈 지도

> 작성: software-lead (S1, 2026-09-05). engine.py v0(커밋 0549548) 인수 시점 스냅샷.
> 목적: 25개 물리 모듈이 지금 어떻게 서로 의존하고, 어느 것이 `engine.Model`로
> 이미 이관됐고, 어느 것이 이관 대상인지 한 곳에서 본다. 코드가 바뀌면 이 문서도 갱신한다
> (문서가 코드와 어긋나면 이 문서가 틀린 것 — S1 완료 기준).

## 1. 계층 구조 (실제 sys.path 배선 기준)

```
sim/engine.py                 ← 유일한 공개 API (Recipe → simulate → WaferResult)
  ├─ sim/metrics/uniformity.py   (compute_metrics — wafer-metrology 소유, 문헌 확정 2026-09-06)
  └─ Model 등록부
        └─ PrestonRadialModel  → tier1_empirical/wiwnu.py 만 호출

sim/tier1_empirical/   경험식. 서로 거의 독립, engine이 아직 wiwnu.py만 사용
sim/tier2_physics/     물리 기반(GW 접촉, DLVO, 점탄성 등). engine 미연결
sim/integration/       tier1+tier2 조합 스크립트. engine 미연결
sim/demo_app.py        Streamlit. tier1_empirical을 **직접 import** (engine 우회 — S5 대상)
```

engine.py는 물리 모듈을 import할 때 `sys.path.insert`로 `tier1_empirical/`,
`tier2_physics/`, `integration/`을 평평하게(flat) 넣는다 — 패키지 상대 import가 아니라
"bare import"다. 이는 각 모듈이 `python3 module.py`로 단독 self-test 실행되는 걸
전제로 한 설계라, sim-architect가 향후 스키마를 바꿀 때도 이 배선 방식은 유지해야
기존 25개 모듈의 self-test(`if __name__ == "__main__"`)가 안 깨진다.

## 2. 모듈별 의존 그래프 (import 관계, 실측)

| 모듈 | 이 모듈이 import하는 것 | 이 모듈을 import하는 것 |
|---|---|---|
| tier1_empirical/kinematics.py | numpy만 | preston.py, wiwnu.py, demo_app.py, gw_preston_link.py |
| tier1_empirical/preston.py | kinematics.py | demo_app.py |
| tier1_empirical/wiwnu.py | kinematics.py | **engine.py(PrestonRadialModel)**, demo_app.py |
| tier1_empirical/process_time.py | 없음 | demo_app.py |
| tier1_empirical/pattern_density.py | 없음 | demo_app.py, wiwnu_pattern_combined.py |
| tier1_empirical/wiwnu_pattern_combined.py | wiwnu.py, pattern_density.py | integration/spatiotemporal_removal.py |
| tier2_physics/gw_contact.py | 없음 | gw_pressure_solve.py |
| tier2_physics/gw_pressure_solve.py | gw_contact.py | gw_preston_link.py, pad_wear_glazing.py(구조 유사, 독립 구현) |
| tier2_physics/gw_preston_link.py | gw_pressure_solve.py, kinematics.py | (미사용 — S3 대상) |
| tier2_physics/wear_aware_kp_physical.py | pad_wear_glazing.py 계열 | (독립) |
| tier2_physics/wear_aware_endpoint.py | 없음(자체 완결) | (독립) |
| tier2_physics/conditioner_*.py (3개) | 서로 참조 없음, 각자 완결 | (독립) |
| tier2_physics/dlvo_colloid.py, pourbaix_nernst_slope.py, slurry_components.py | 없음 | (독립, 화학 축) |
| tier2_physics/cmp_lubrication_regime.py, tribology_basics.py, viscoelastic_maxwell.py, slurry_film_lubrication.py | 없음 | (독립, 트라이볼로지 축) |
| tier2_physics/pad_wear_glazing.py | 없음(자체 GW 재구현) | wear_aware_endpoint.py, wear_aware_kp_physical.py |
| integration/spatiotemporal_removal.py | wiwnu_pattern_combined.py | (독립, PTW 경로) |
| integration/spatiotemporal_removal_physical_kp.py | 없음(자체 완결) | (독립) |

**관찰**: tier2_physics의 절반 이상(GW 접촉 계열 제외)은 서로 완전히 독립된 "물리 개념
증명" 스크립트다. 이관 우선순위를 정할 근거가 된다(§3).

## 3. engine.Model 이관 분류

### 3a. 이미 이관됨
- `PrestonRadialModel`(engine.py) — wiwnu.py의 `mrr_radial`을 감싼 얇은 어댑터. tier1 전용.

### 3b. 이관 대상 — 근거·문헌값 이미 있음, 다음 항목
| 모듈 | 이관 형태 | 담당 | 비고 |
|---|---|---|---|
| gw_preston_link.py | `Model` (tier2.gw_preston) — Kp를 alpha_removal×n_contacts(P)로 분해 | sim-developer (S3) | Recipe에 새 필드 불필요, kp_m_per_pa 대신 alpha_removal 옵션 추가만 |
| pattern_density.py | `Model` 아님, WaferResult 후처리 확장(dishing_nm/erosion_nm 채움) | sim-developer (S6) | wafer=PTW 게이트, Recipe에 die 밀도맵 필드 필요 → sim-architect 스키마 검토 |

### 3c. 이관 보류 — 지식/필드 부족 또는 스코프 밖 (지금 손대지 않는다)
| 모듈 | 보류 사유 |
|---|---|
| conditioner_*.py (3개), pad_wear_glazing.py, wear_aware_*.py | 시계열(패드 컨디셔닝 이력)이 Recipe에 없다. Recipe는 "한 번의 런"만 표현 — 다회차 상태(패드 나이, PCR)를 넣으려면 스키마 확장 필요. M3 결합모델 논의 시 sim-architect가 판단 |
| dlvo_colloid.py, slurry_components.py, pourbaix_nernst_slope.py | 화학 축. slurry-* 도메인 에이전트가 "이 값을 Kp에 어떻게 반영하는지" 정량 관계를 아직 안 냄 — 구현 요청 대기 |
| cmp_lubrication_regime.py, tribology_basics.py, viscoelastic_maxwell.py, slurry_film_lubrication.py | 마찰계수/윤활영역 축. Kp와의 정량 연결식이 지식노트에 없음 — tribologist 커리큘럼 진행 후(현재 2/6) |
| gw_contact.py, gw_pressure_solve.py | gw_preston_link.py가 이미 감싸서 쓰므로 직접 Model화 불필요 |
| integration/spatiotemporal_removal*.py | wiwnu_pattern_combined 기반 2D 맵 — S6(pattern_density)와 통합 시 재검토 |

## 4. 스키마 부채 (sim-architect가 볼 것)

- `Recipe`는 순간(single-run) 스냅샷만 표현. 패드 나이·컨디셔닝 이력 같은 "상태"를 담을
  필드가 없다 — §3c 대다수 모듈이 이관 못 하는 근본 이유.
- `kp_m_per_pa`는 화학+기계 뭉뚱그림. gw_preston_link 이관(S3) 후에도 alpha_removal은
  화학 lump 상수로 남는다 — slurry 조성이 Kp에 어떻게 매핑되는지는 여전히 미해결.
- PTW 경로(pattern_density) 연결 시 Recipe에 die 레이아웃/유효밀도맵 입력이 필요 —
  현재는 스칼라 필드뿐이라 배열/맵 타입 필드 추가가 불가피 (SCHEMA-CHANGELOG.md 기록 대상).

## 5. 결론 — 다음 실행에 뭘 볼 것

BACKLOG S3(gw_preston_link 이관)이 유일하게 "지식+문헌값+스키마 변경 불필요"를
동시에 만족하는 다음 항목이다. S6/S7은 스키마 확장이 선행돼야 하므로 게이트 유지.
