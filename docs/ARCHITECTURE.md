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

> **2026-09-07 갱신 (S1 문서 동기화)**: 최초 작성(9/5) 이후 S3가 그날 저녁 이미 처리돼
> `models.py`(커밋 1145ca7)로 4개 모델이 등록됐다. 아래는 `sim.models.register_all()` /
> `available_models()` 실측(4개) 기준.

### 3a. 이미 이관됨 (engine.available_models() 실측 4개)
| Model 이름 | 소스 모듈 | 형태 |
|---|---|---|
| `tier1.preston_radial` | wiwnu.py | 얇은 어댑터, tier1 전용 |
| `tier2.gw_physical_kp` | gw_preston_link.py (+gw_pressure_solve, gw_contact) | Kp를 alpha_removal×n_contacts(P) GW 접촉역학에서 유도 |
| `tier2.wear_aware` | (GWPhysicalKpModel 위임, 시간보정 미적용) | S13 모순 미해결 상태를 notes로만 보고 — 마모 시계열 자체는 구현 안 됨(§3c) |
| `tier1.pattern_density` | pattern_density.py | PTW MRR_up = blanket/ρ_eff 후처리형 Model. dishing/erosion 산출은 아직 없음(S6 스키마 확장 대기) |

### 3b. 이관 대상 (근거·문헌값 있음, 다음 항목) — 현재 비어 있음
S3(gw_preston_link)·S6 1차분(pattern_density 등록)이 이미 3a로 옮겨졌다. 다음 이관
후보는 S12(패드/컨디셔너/윤활 계열 20개) — 대부분 §3c 보류 사유(시계열 스키마 부재,
정량 연결식 부재)가 걸려 있어 "바로 이관 가능"은 현재 없음. S17(frictional_heating_arrhenius,
tier2_physics/에 신규 추가)도 순수 함수 라이브러리 지위라 Model 등록 대상 아님(STATUS.md 9/6 15:30 판단 유지).

### 3c. 이관 보류 — 지식/필드 부족 또는 스코프 밖 (지금 손대지 않는다)
| 모듈 | 보류 사유 |
|---|---|
| conditioner_*.py (3개), pad_wear_glazing.py, wear_aware_*.py | 시계열(패드 컨디셔닝 이력)이 Recipe에 없다. Recipe는 "한 번의 런"만 표현 — 다회차 상태(패드 나이, PCR)를 넣으려면 스키마 확장 필요. **게다가 pad_wear_glazing 계열은 S13 모순(ad-hoc↓ vs GW↑, corr=-0.998) 미해결** — 어느 쪽이든 지금 이관하면 틀린 물리를 제품에 넣는 것 |
| dlvo_colloid.py, slurry_components.py, pourbaix_nernst_slope.py | 화학 축. slurry-* 도메인 에이전트가 "이 값을 Kp에 어떻게 반영하는지" 정량 관계를 아직 안 냄 — 구현 요청 대기(수신함에 3건 등록됨, 우선순위 중) |
| cmp_lubrication_regime.py, tribology_basics.py, viscoelastic_maxwell.py, slurry_film_lubrication.py | 마찰계수/윤활영역 축. Kp와의 정량 연결식이 지식노트에 없음. frictional_heating_arrhenius(S17)는 열-화학 커플링만 다루고 여전히 Kp 연결식 없음 — tribologist 커리큘럼 진행 후 재검토 |
| gw_contact.py, gw_pressure_solve.py | gw_preston_link.py가 이미 감싸서 쓰므로 직접 Model화 불필요 |
| integration/spatiotemporal_removal*.py | wiwnu_pattern_combined 기반 2D 맵 — S6(dishing/erosion 산출) 스키마 확장 시 재검토 |

## 4. 스키마 부채 (sim-architect가 볼 것)

- `Recipe`는 순간(single-run) 스냅샷만 표현. 패드 나이·컨디셔닝 이력 같은 "상태"를 담을
  필드가 없다 — §3c 대다수 모듈이 이관 못 하는 근본 이유.
- `kp_m_per_pa`는 화학+기계 뭉뚱그림. gw_preston_link 이관(S3) 후에도 alpha_removal은
  화학 lump 상수로 남는다 — slurry 조성이 Kp에 어떻게 매핑되는지는 여전히 미해결.
- PTW 경로(pattern_density) 연결 시 Recipe에 die 레이아웃/유효밀도맵 입력이 필요 —
  현재는 스칼라 필드뿐이라 배열/맵 타입 필드 추가가 불가피 (SCHEMA-CHANGELOG.md 기록 대상).

## 5. 결론 — 다음 실행에 뭘 볼 것

S3·S6(1차, pattern_density 등록)은 완료됐다. 남은 실행 가능 후보는 (a) S13 판정
전 §3-A 스냅샷 처리는 9/6에 끝남(TEST-AUDIT S18) — 남은 §3-B 스냅샷 3건
(`test_pad_wear_glazing::p_r_changes_significantly`, `test_slurry_film_lubrication::z0_order_of_magnitude`,
`test_conditioner_sweep_kinematics::pca_profile_has_nonzero_coverage`)은 전부 "임의 임계값"이며
독립 문헌 정량값이 없어 폐형식 유도가 불가능 — 스냅샷 유지가 정직한 선택(TEST-AUDIT.md 참고),
강제 교체는 하지 않는다. (b) S13(패드 마모 모순)은 pad-lifecycle 에이전트가 아직 Lv1-2까지만
이수(G3/실측 필요)해 판정 근거가 부족 — 지식이 코드보다 앞선다는 원칙상 지금 코드로
추측 해결 금지, 도메인 학습 진행을 기다린다. (c) 실제 가용한 다음 항목은 **S12**(남은 20개
모듈 중 지식·필드 요건이 갖춰진 서브셋부터 개별 판단) 또는 도메인 구현요청 수신함
(slurry-chemist 3건 중 지식 상태 좋은 것 우선).
