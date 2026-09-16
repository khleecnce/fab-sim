# S12 잔여 미등록 모듈 전수 재판정

확정 방법: `sim/tier2_physics/*.py` 전체 목록(39개, `__init__` 제외)과 `sim/engine.py`
안의 `import <module>` 패턴을 grep으로 기계적으로 대조. 백로그 서술이나 기억에 의존하지
않았다.

```
comm -23 <(ls sim/tier2_physics/*.py | xargs -n1 basename | sed 's/\.py$//' | sort) \
         <(for m in ...; do grep -qE "^\s*import ${m}( |$)" sim/engine.py && echo $m; done | sort)
```

미등록 모듈 9개 (2026-09-16 확정):
1. competitive_metal_langmuir
2. conditioner_asperity_distribution
3. disk_active_grit_fraction
4. disk_cutrate_coupling
5. friction_cof_epd
6. metal_contamination_surface
7. pad_wear_glazing
8. wear_aware_endpoint
9. wear_aware_kp_physical

전부 코드를 직접 열어 (a)~(d) 4항목을 확인했다. **9개 전부 영구 스킵**으로 판정했다
(등록 0건). 과거 3회차처럼 "docstring 사유가 일부만 참"인 사례가 이번에도 2건
발견됐으나(아래 ①③), 진짜 블로커는 다른 곳에 있어 최종 판정은 바뀌지 않았다.

## 모듈별 판정

| 모듈 | public 함수 / 필수입력 | 부재 입력 & 근거 | 판정 |
|---|---|---|---|
| ① **competitive_metal_langmuir** | `competitive_langmuir_surface(metals, pH, sigma0, K_H)` — metals: `{name:(K_i, C_i_free)}`, pH | docstring(L11)은 "Recipe에 pH 필드가 없어"라고 하지만 **부분만 참** — `slurry_ph`는 **6팩 전부**(cu_h2o2_bta/oxide_silica/sic_alumina_kmno4/sic_ceria_h2o2/sti_ceria/w_fe_oxidizer, `grep -l slurry_ph: knowledge/params/*.yaml`)에 `has_own`으로 존재하고 이미 다른 진단(`galvanic_hydroxide_ph` 등, engine.py:750,944)이 `rr.p("slurry_ph")`로 쓴다. 진짜 블로커는 **금속 이온 유리농도 `C_i_free [mol/L]`** — `grep -niE "conc|molar|mol_l"` 로 6팩 전체를 훑어도 금속 이온 몰농도 필드는 전무(`chelator_M`은 착화제 농도로 별개). K_i 표도 Cr 하나뿐(모듈 L15-17, "K_i 표 부재"). | **영구 스킵**(스키마 부재: 금속이온농도. pH 자체는 이미 존재) |
| ② **conditioner_asperity_distribution** | `sigma_series(sigma0, A0, tau_hours, ...)`, `calibrate_A0_from_halving_time` | `A0`(similarity 상수)가 결정적 블로커: 모듈 L29-32, L78-80이 "문헌에서 fit parameter로만 제공되어 공개 정량값이 없다 ... 정량 예측치 아님, 정성 시연용 값"이라고 **스스로** 명시. `sigma0`(초기 표준편차)는 실은 `pad_height_beta_inv_m`(base.yaml, 지수분포 1/beta = std)로 대입 가능할 수도 있었으나(스케일링 성질이 분포족에 무관, 모듈 L26-27), A0가 비정량이라 무의미. | **영구 스킵**(A0가 문헌 fit-only·비정량, 모듈 자체 인정, conditioner_asperity_distribution.py:29-32) |
| ③ **disk_active_grit_fraction** | `active_fraction_uniform(h_lo,h_hi,engage_depth)`, `active_fraction_single_height()`, `disk_active_grit_fraction(protrusion_pdf, engage_depth, n_total, ...)` | `h_lo/h_hi`는 문헌실측 기본값 있음(Kim&Kang 2011, L84-86, has_own 아니지만 리터럴 문헌값). 그러나 `engage_depth`는 **기본값 금지가 모듈 자체 설계**(L23-24, "PROFILE.md 구현요청 §4 명시": 인자로만 받고 기본값 없음) — 하중·패드경도의 함수인데 그 함수 자체가 노트에 없어 계산 불가. `protrusion_pdf`(디스크 종류: 전착/CVD패턴)와 `n_total`(그릿 총수)도 6팩 어디에도 없음(`grep -niE "grit" knowledge/params/*.yaml`→ base.yaml 주석에만 등장, 값 없음). | **영구 스킵**(engage_depth 기본값 자체가 모듈 설계상 금지 + protrusion_pdf/n_total 스키마 부재) |
| ④ **disk_cutrate_coupling** | `cutrate_density_scaling(N,N_ref,CR_ref)`, `cutrate_rpk_scaling(Rpk,...)`, `disk_cutrate_coupled(..., Neff_ratio=None, g=None)` | `N`(그릿 밀도)·`Rpk`(표면조도) 둘 다 6팩에 없음(③과 동일 grep). `g`(활성비율 지수)는 모듈이 **스스로 engine 미등록을 선언**(L19-22: "노트 §5·§6이 명시적으로 미확정, 캘리브레이션 파라미터로 남긴다고 못박았으므로 ... engine에는 미등록"). | **영구 스킵**(N/Rpk 스키마 부재 + g는 모듈 자체가 이미 미등록 선언, disk_cutrate_coupling.py:19-22) |
| ⑤ **friction_cof_epd** | 마찰사슬: `shear_force/normal_force/cof_from_forces/platen_torque/motor_power_friction/motor_current`. EPD: `moving_average/detect_step_transition/detection_delay_s/over_polish_nm/detect_endpoint` | EPD 함수군은 시계열 신호(모터전력 샘플열)가 필수 입력인데 `Recipe`(sim/engine.py:51-94)는 압력·rpm·시간 등 **스칼라 단발값만** 갖고 시계열 필드가 전혀 없음 — docstring 주장(L9-13)이 구조적으로 100% 참임을 Recipe 필드 목록으로 직접 확인. 마찰사슬 함수는 이론상 `mu`만 있으면 순방향 계산 가능하고 `cof_stribeck_estimate`(이미 등록된 필드, engine.py:195)가 후보이지만, 이 값은 이미 `cmp_theta_steady_state_heat_balance`(engine.py:654-678)가 **다른 mu(cof_boundary, 문헌 가정)로 동일 물리량 Q_f=μPAV를 이미 계산**하고 있어, `cof_stribeck_estimate`(그 자체도 "λ≈So 근사, 정량 항등식 아님"이라 노트에 명시)로 같은 형태의 값을 또 등록하면 서로 다른 mu로 같은 물리량을 중복 산출해 어느 쪽이 맞는지 판단 기준 없이 혼란만 늘림. `motor_current`는 `K_t`가 "장비상수, 절대값 미검증"(L18-19)이라 별도로도 스킵. | **영구 스킵**(EPD군: 시계열 스키마 구조적 부재, Recipe 필드 확인. 마찰사슬군: 순방향 계산 자체는 가능하나 이미 다른 mu로 등록된 Q_f와 중복이라 등록 보류) |
| ⑥ **metal_contamination_surface** | `monolayer_density_si100(a_cm=상수)`, `fraction_of_monolayer(tol, ml)`, `boltzmann_surface_enrichment(zeta_mV, valence, T_K)`, `goi_early_failure_ratio(n_fail,n_total)`, `precmp_to_spec_ratio(precmp, spec)` | 앞의 2개는 격자상수·ITRS스펙 등 **레시피와 무관한 상수만** 써서 항상 같은 값을 반환 — 함수는 호출 가능하지만 레시피별로 구분되지 않아 "진단"이 아니라 상수 재현(등록해도 정보량 0). `boltzmann_surface_enrichment`는 `zeta_mV`가 필수인데 이 값은 실측 mV가 아니라 pH구간별 **정성 카테고리 표**(모듈 L57, "IEP/약산성/중성/약알칼리")로만 존재 — `slurry_ph`(연속값)를 이 4구간에 매핑하려면 모듈에 없는 새 임계값을 발명해야 함(금지 항목: 근거 없는 새 값). `goi_early_failure_ratio`는 Wang2024 특정 실험의 고정 숫자(8/71) 재현일 뿐 레시피와 무관. `precmp_to_spec_ratio`는 `precmp_atoms_cm2`(세정전 실측 오염량)가 필수인데, 모듈 자신이 그 유일한 후보값(`FE_ORDER_OF_MAGNITUDE_UNVERIFIED`)을 "**출처 불명·미검증(2차 요약 오귀속)**"이라고 2026-09-09에 스스로 정정함(L22-28) — 문헌 근거 없는 자체가정이라 기본값으로 못 씀. | **영구 스킵**(5개 함수 모두 개별 사유: 레시피무관 상수 2개, 카테고리표뿐이라 연속매핑 불가 1개, 고정문헌재현 1개, 기본값이 출처불명이라 명시적으로 정정된 1개) |
| ⑦ **pad_wear_glazing** | `simulate_pad_wear(..., c_w=1e-8, C1=2e-6, ...)` | 시간축 MRR 드리프트를 내는 핵심 계수 `c_w`(MRR 스케일)·`C1`(마모속도)이 **모듈 자신이 "임의 오더, self-test용 — 물리적 캘리브레이션 아님" / "임의 오더, 안정적 오일러 적분 위해 튜닝"이라고 명시**(pad_wear_glazing.py:87-88). 문헌 근거 있는 값이 아니라 자체 가정임을 코드가 직접 자백. | **영구 스킵**(c_w/C1이 비문헌 임의값임을 모듈 스스로 명시, pad_wear_glazing.py:87-88) |
| ⑧ **wear_aware_endpoint** | `compare_naive_vs_drift(target, pad_wear_kwargs)` | `simulate_pad_wear`(⑦)의 시계열을 그대로 소비 — MRR(t) 자체가 ⑦의 비문헌 `c_w`/`C1`에 의존하므로 `optimism_pct`(정상상태 예측 대비 낙관도)가 정성적 방향(양수)만 의미 있고 절대 수치는 ⑦과 동일한 이유로 미검증. 독립적으로 시계열을 공급할 다른 경로 없음(Recipe엔 시계열 필드 없음, ⑤와 동일 확인). | **영구 스킵**(⑦의 비문헌 상수를 그대로 상속, wear_aware_endpoint.py:26 `from pad_wear_glazing import simulate_pad_wear`) |
| ⑨ **wear_aware_kp_physical** | `compare_adhoc_vs_physical(pad_wear_kwargs)` | ⑦의 이산 마모 루프를 재사용하는 동시에, 모듈 자신의 self-test가 **의도한 결과와 반대(corr≈-0.998, 기대 corr>0.9)로 실패하도록 그대로 남겨둔 문서화된 반증 모듈**(L37-63, "⚠️ 불일치 발견... assert 기준은 낮추지 않았고, 실패는 실패로 둔다"). 물리 그림 자체가 "압력 고정·집단 마모" 시나리오에서 검증되지 않았음을 코드가 스스로 증명. | **영구 스킵**(자체 self-test가 의도적으로 FAIL 상태를 문서화, wear_aware_kp_physical.py:37-63 + ⑦ 상속) |

## 스키마 확장(Recipe 시계열·이온농도·제타전위)이 실제로 가치 있는가

결론부터: **지금은 가치가 없다.** 4갈래로 나눠 확인했다.

1. **금속 이온농도(①)**: 값이 존재하면 `competitive_langmuir_surface`가 즉시 순방향
   등록 가능하다(pH는 이미 6팩 전부에 있음). 다만 K_i 표가 Cr 하나뿐이라(①의 확인)
   이온농도를 넣어도 결과는 "오더 검증"에 머문다 — 스키마보다 **K_i 문헌표 확보가
   먼저**다. 스키마만 추가하면 미검증 오더 상수(K_H=1e3 등)와 결합해 거짓 정밀도를
   만들 위험이 있다.
2. **디스크(컨디셔너) grit 밀도·Rpk·engage_depth(③④)**: base.yaml:75가 이미
   "R은 소재 물성이 아니라 컨디셔닝(디스크 grit·하중)이 만드는 기하량"이라고 명시했다
   — 즉 이 값들은 **화학 팩(oxide_silica 등) 6개가 각자 선언할 값이 아니라 장비
   단위(컨디셔너 디스크 모델)로 공유되는 값**이다. 지금 스키마(`knowledge/params/*.yaml`
   = 필름·슬러리 화학 팩)에 넣으면 "Cu 화학 팩을 바꿨는데 디스크 사양이 같이
   바뀐다"는 잘못된 결합이 생긴다. 가치 있으려면 `knowledge/params/base.yaml`과
   별도로 **장비 팩(예: `equipment/conditioner_disk.yaml`)**을 신설하고 Recipe에
   `conditioner_disk: Optional[str]` 같은 선택 필드를 추가하는 구조가 맞다 — 지금
   과제 범위를 넘는 설계변경이라 이번엔 손대지 않았다.
3. **제타전위(⑥)**: 현재 문헌이 연속 함수가 아니라 4구간 정성 표만 제공해서, 스키마에
   `zeta_mV` 필드를 추가해도 채울 정량 출처가 없다. pH→zeta 연속식을 문헌에서 먼저
   확보해야 스키마 추가가 의미 있다.
4. **시계열(⑤⑦⑧⑨)**: Recipe를 "단발 런 스냅샷"에서 궤적으로 바꾸는 것은
   `docs/ARCHITECTURE.md`가 이미 인지한 스키마 부채이자 전체 엔진(`resolve()`,
   `WaferResult`, 모든 진단 함수)에 영향을 주는 구조 변경이다. 이번 9개 모듈 중
   실제로 시계열을 "레시피 입력"으로 요구하는 것은 없다(⑦⑧⑨는 시계열을 **내부에서
   생성**하지, Recipe에서 읽지 않는다 — 블로커는 시계열 스키마가 아니라 c_w/C1의
   문헌값 부재다). 유일하게 시계열이 진짜 필요한 것은 ⑤의 EPD 검출부인데, 그건
   실시간 신호처리 알고리즘 검증 도구지 배치 시뮬레이션 진단이 아니라서 애초에
   Recipe 스키마로 흡수할 대상이 아니다. **결론: 시계열 스키마 확장은 이 9개 모듈
   기준으로는 정당화되지 않는다.**

## S12 종결 결론

9개 미등록 모듈 전부를 코드 근거와 함께 재확인했고, 전부 **영구 스킵이 재확정**됐다.
과거 3회차와 달리 이번엔 "docstring 사유가 부분적으로 틀림"을 2건(①의 pH 존재, ②의
sigma0 대입 가능성) 찾았지만 두 경우 모두 진짜 블로커(①이온농도, ②A0)가 별도로
확실히 존재해 최종 판정(스킵)은 바뀌지 않았다. 새로 등록한 모듈은 0개이며, 숫자를
늘리기 위한 None-스텁도 추가하지 않았다(금지 사항 준수).

**S12 항목은 이번 판정으로 종결 가능하다.** 남은 9개는 각각:
- 문헌 미확보(K_i 표, engage_depth 모델, pH→zeta 연속식) — 지식노트 보강이 먼저다.
- 장비-화학 팩 분리라는 설계 변경(디스크 grit 밀도·Rpk) — 별도 백로그 항목으로
  분리해야 한다(이번 과제 범위 아님).
- 모듈 자신이 이미 "비정량/미검증/실패"라고 문서화한 것(A0, c_w/C1, wear_aware_kp_physical
  self-test) — 새 문헌이 나오기 전엔 재론할 필요가 없다.
- 이미 다른 경로로 등록된 물리량과의 중복(friction_cof_epd 마찰사슬) — 두 mu 추정치 중
  어느 쪽이 맞는지 판단할 근거가 생기기 전엔 등록할 이유가 없다.

추가 조치가 필요하면 "지식노트 보강"(K_i, engage_depth, ζ-pH) 또는 "장비 팩 스키마
신설"(디스크 grit) 쪽 백로그로 새로 열어야 하며, 지금의 S12(엔진 등록 전수 재판정)
작업 자체는 여기서 닫는다.
