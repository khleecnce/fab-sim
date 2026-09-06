# 테스트 감사: 재현 vs 스냅샷 분류 (S2)

> 작성 2026-09-06 ([Max워커] S2). 대상: `tests/*.py` 22개 파일(conftest 제외 21개), 119개 테스트(`pytest --co` 기준, parametrize 전개 포함).
> 코드 수정 없음 — 감사 문서만 작성. 이 문서는 "어떤 테스트가 실제로 문헌·물리와 대조하는가"를 답하기 위한 것이다.

## 0. 분류 기준

| 분류 | 정의 | 세부 유형(근거 유형 열) |
|---|---|---|
| **재현** | 계산 결과를 외부 근거와 **정량** 비교한다 | **문헌**: 출처가 있는 문헌 상수·정의 / **해석해**: 폐형식·극한·해석적 비율 / **항등식**: 선형성·라운드트립·두 경로 동일성 등 수학적 항등식(배선 검증 성격, 물리 오류는 못 잡음) |
| **혼합** | 물리와 비교하되 **정성(부호·단조·순서)** 또는 **오더(문헌 범위 수십~수백 배 폭)** 만 확인. 또는 문헌값과 임의 임계가 섞임 | 정성 / 오더 |
| **스냅샷** | 외부 근거 없는 임의 숫자와 비교하거나, 코드가 "지금 내는 값"을 그대로 고정 | 임의 임계 / 관측값 고정 |
| **스모크** | 실행 성공·shape·예외 발생·노트 문자열 등 계약만 확인 | 계약 |

판정 규칙: assert가 비교하는 **숫자의 출처**를 본다. 모듈 docstring에 문헌이 있어도 assert가 그 문헌값을 안 쓰면 재현으로 치지 않는다.
"항등식"은 정의상 재현에 포함하지만(과제 정의), 물리 검증력이 낮으므로 통계에서 따로 센다.

## 1. 파일별 분류표

"분류(개수)" 열은 재현/혼합/스냅샷/스모크 순. 대표 함수는 각 분류의 예시.

| 파일명 | 테스트 수 | 주분류 | 분류(재현/혼합/스냅/스모크) | 근거 유무 | 비고 |
|---|---|---|---|---|---|
| test_conditioner_asperity_distribution.py | 5 | 혼합 | 3/2/0/0 | 해석해 ✓ (`similarity_scaling` → σ비 = exp(2At)). 앵커 `T_HALF_HOURS=48h`는 소스 주석에 "임의 기준, 미검증" | `halves_sigma_at_calibrated_time`은 48h로 A0를 보정한 뒤 48h에 절반인지 보는 라운드트립(자명 항등식). `aging_slower`·`monotonic`은 정성 |
| test_conditioner_pcr_decay.py | 6 | 혼합 | 2/3/0/1 | Entegris 앵커(50h→16%, 2차 문서). 단 τ를 그 앵커로 보정하므로 `anchor_calibration_exact`는 자기순환 항등식 | `tau_inf` 극한 항등식 ✓. 나머지 3개는 순서·단조 정성. `rejects_bad_ratio` 예외 계약 |
| test_conditioner_sweep_kinematics.py | 5 | 재현(항등식) | 4/0/1/0 | Zheng·Zhao·Lu 2023 Eq.1-9·Table 1 조건 사용. assert는 기하 항등식(정지 불변, 반경 상한 R_p+R_a+R_i, 위상 스케일링) | `pca_zero_outside_reach`는 `(not any(mask)) or …` 구조라 범위 밖 bin이 없으면 **공허하게 통과**. `pca_profile_has_nonzero_coverage`(>5%)는 임의 임계 → 스냅샷 |
| test_demo_app_smoke.py | 1 | 스모크 | 0/0/0/1 | 없음(의도된 스모크) | 예외 0건·탭 2개 |
| test_engine.py | 9 | 혼합 | 3/2/1/3 | 문헌 정의 ✓ (`metric_definitions`: US6922603B1 3σ=3×1σ, CV≡1σ WIWNU). Preston 선형성 항등식 ✓ | `uniform_pressure_gives_low_nonuniformity`(cv<0.5%)는 "process-integrator 판단 edge/center≈1.004"에서 온 내부 파생값 → 스냅샷. `edge_pressure_increases_ttv`의 "3배"는 임의. 노트 문자열 계약 3건 |
| test_gw_contact.py | 5 | 재현 | 4/0/1/0 | Hertz F∝δ^1.5, a²=Rδ, GW 1966 지수분포 A_r/W 폐형식 ✓ | `plasticity_index_order_of_magnitude`(0.01<ψ<100)는 4자릿수 폭 + H=50MPa "미검증 오더값" → 스냅샷 |
| test_gw_pressure_solve.py | 4 | 재현 | 3/1/0/0 | GW 폐형식 1/ratio ✓, 라운드트립 항등식 ✓, p_r 압력 불변(지수분포 해석 성질) ✓ | `contact_area_fraction_monotonic` 정성 |
| test_gw_preston_link.py | 4 | 재현/혼합 | 3/1/0/0 | n∝P(지수분포 GW 정확해) ✓. 보정점 항등식은 자명. 문헌 MRR 범위 50~1000 nm/min(jeez-semicon 가이드, preston.py 주석) | `calibration_mrr_in_literature_range`는 20배 폭 오더 → 혼합. STI 대표값 254 nm/min(ACS Langmuir 2026)이 주석에 있으나 미사용 |
| test_kinematics.py | 8 | 재현 | 7/1/0/0 | Lai 2001 Eq.2.11/2.12, Hasni 2026 JJMIE Eq.3 ✓. ν=2\|μ\| 해석해(4 파라미터) ✓ | 가장 모범적. `rs_neq1_edge_faster_than_center`만 정성 |
| test_models.py | 19 | 스모크/혼합(계약) | 1/9/2/7 | 외부 근거 없음 — 파일 docstring대로 "엔진에 제대로 붙었나" 계약 테스트 | `pressure_monotonic`×4·`zone_pressure_applied`×4 정성. `gw_and_preston_converge`: assert는 10%인데 실패 메시지는 "5% 이내여야" → **불일치**. `wear_model_reports_unresolved_contradiction`은 노트 문자열 `corr=-0.998`을 고정(의도된 정직 스냅샷, S13 미해결). `ptw_pattern_raises_mrr`는 1/ρ 해석해(3.33배)가 있는데 ">2배"만 확인 |
| test_pad_wear_glazing.py | 5 | 혼합 | 1/3/1/0 | Shi & Ring 2010(Wear, 저자 공개 PDF) — 정성 거동(단조감소·수확체감)만. `C1=2e-6` 소스 주석 "임의 오더" | `discrete_t0_matches_continuum_gw`(10% 허용) 이산↔연속 항등식. `p_r_changes_significantly`(>1%) 임의 → 스냅샷 |
| test_pourbaix_nernst_slope.py | 6 | 재현 | 3/0/0/3 | Nernst −59.16 mV/pH(RT·ln10/F, 물리상수) ✓. W 반응 기울기(Krishnan 2010 Chem.Rev. 2차) ✓ | `is_self_limiting_type`·문자열 반환은 데이터표 계약 → 스모크 |
| test_preston.py | 5 | 혼합/재현 | 3/1/1/0 | P·V 선형 항등식 ✓(단 `velocity_doubling`은 테스트 안에서 Kp·P·V를 직접 계산해 자명). Rs=1 평탄(Lai) ✓. 문헌 범위 20~2000 nm/min 오더 | `rs_neq1_edge_center_ratio_matches_kinematics`의 **1.00391은 kinematics.py 출력값**(문헌 아님) → 스냅샷. 시간평균 \|v\|의 폐형식(완전타원적분)으로 교체 가능 |
| test_process_time.py | 4 | 재현(항등식) | 3/1/0/0 | 시간 선형·역수 항등식 ✓, Rs=1 → WIWNU=0 ✓ | `rs_neq1_wiwnu_small_positive_order`(0<w<5%)는 정합값 0.39%를 알면서 느슨 → 혼합 |
| test_slurry_film_lubrication.py | 7 | 혼합(정성) | 0/6/0/1 | Thakurta 2001(papers/ PDF 확보) — 소스 주석 스스로 "부호가 문헌과 일치하는가만" | `z0_order_of_magnitude`(1e-6<z0<1e-3, 3자릿수 폭)는 논문 h_min=36 µm·Eq.19가 있어 정량화 가능. `curvature_has_interior_maximum` 정성(Fig.6c) |
| test_spatiotemporal_removal.py | 4 | 재현(항등식) | 4/0/0/0 | 시간 선형, ρ=1 → K·t, 배선, CV 시간불변(대수) | 전부 배선 항등식. 물리 오류 감지력 없음(의도된 통합 검증) |
| test_spatiotemporal_removal_physical_kp.py | 5 | 재현(항등식) | 4/0/1/0 | 균일압에서 상수 Kp와 일치(1e-6), α 배선, kp_eff(P_ref)=Kp_lit 자명 | `wide_pressure_range_deviation`(<1e-2)은 GW n∝P 정확해 상 편차가 ~1e-4여야 하므로 1%는 임의 여유 → 스냅샷 |
| test_viscoelastic_maxwell.py | 5 | 재현(해석해) | 5/0/0/0 | Maxwell 모델 극한(E'→0/E, E''→0), E''_max=E/2 at ω=1/τ0, tanδ 극한 ✓ (Ferry 1980 표준식) | 모범적 |
| test_wear_aware_endpoint.py | 4 | 재현(항등식) | 2/1/0/1 | 누적 vs trapz(1e-9), 무드리프트 극한 = process_time v0(1%) | `naive_is_optimistic`(>0) 정성. `unreachable_target_raises` try/except 수동 구현(pytest.raises 미사용, 동작엔 문제 없음) |
| test_wear_aware_kp_physical.py | 5 | 혼합(항등식+정직 스냅샷) | 3/0/2/0 | 원본 루프 재현 1e-12 ✓, C1=0 극한 상수 ✓ | `n_contacts_actually_increases`·`normalized_curves_are_strongly_anticorrelated`(corr<−0.9)는 **관측된 모순을 고정**한 스냅샷. docstring이 이를 명시(가설 반증, 거짓 PASS 방지) — S13 판정 전까지 최선 |
| test_wiwnu_pattern_combined.py | 3 | 재현(항등식) | 3/0/0/0 | 극한 a)/b) 배선 항등식, CV² 곱구조 대수 하한 ✓ | docstring이 half_range는 하한 미보장이라 assert 안 함을 명시(정직) |
| conftest.py | 0 | — | — | sys.path 설정만 | — |
| **합계** | **119** | | **61/31/10/17** | | |

## 2. 요약 통계

| 분류 | 개수 | 비율 |
|---|---|---|
| 재현 (문헌 + 해석해 + 항등식) | 61 | 51.3% |
| ─ 그중 **문헌 상수·정의** 정량 대조 | 3 | 2.5% |
| ─ 그중 **해석해·극한** 정량 대조 | 22 | 18.5% |
| ─ 그중 **항등식·배선**(자명 라운드트립 포함) | 36 | 30.3% |
| 혼합 (정성 방향 / 문헌 오더 범위) | 31 | 26.1% |
| 스냅샷 (임의 임계 / 관측값 고정) | 10 | 8.4% |
| 스모크 (계약·shape·예외·문자열) | 17 | 14.3% |
| **합계** | **119** | 100% |

**실제 문헌/물리 정량 검증 비율: 25/119 = 21.0%** (문헌 3 + 해석해 22).
항등식까지 넓게 잡으면 51.3%. 정성 방향 검증(혼합)까지 포함하면 77.3%.

문헌 숫자를 assert에 직접 쓰는 테스트는 단 3개(`test_engine::metric_definitions`, `test_pourbaix::standard_59mV`, `test_pourbaix::w_passivation`)뿐이다.
나머지 "문헌 근거"는 모듈 docstring에만 있고 assert는 해석해·항등식·정성 방향을 본다. 해석해 22개 중 20개가 세 파일(kinematics 6, viscoelastic 5, gw_contact 4, gw_pressure_solve 2, 기타 5)에 몰려 있어, tier2 물리 모듈 중 컨디셔너·패드마모·슬러리막 계열은 정량 재현이 0건이다.

## 3. 스냅샷 교체가 필요한 목록

### 3-A. 교체 후보 — 해석해·문헌값이 이미 있는데 안 쓰는 경우 (7건)

| # | 테스트 | 현재 assert | 대조 가능한 근거 | 교체안 |
|---|---|---|---|---|
| 1 | test_preston.py::`rs_neq1_edge_center_ratio_matches_kinematics` | `abs(ratio − 1.00391) < 1e-4` (kinematics.py 출력값 고정) | 시간평균 상대속력 ⟨\|v\|⟩_θ = (1/2π)∮√(a²+b²+2ab cosθ)dθ 는 완전타원적분 E(k)의 폐형식. Lai 2001 Eq.2.11에서 직접 유도 | `scipy.special.ellipe`로 edge/center 비를 계산해 1e-9 수준으로 비교. kinematics.py 교차값 의존 제거 |
| 2 | test_engine.py::`uniform_pressure_gives_low_nonuniformity` | `cv_pct < 0.5` (process-integrator 판단값) | 같은 폐형식(#1)으로 Rs=50/60 반경 프로파일의 CV를 해석적으로 계산 가능. 또는 `km.speed_stats()["nu_ref"]=2\|μ\|`로 상한 도출 | 해석 CV(≈0.39% 근방)에 상대오차 1e-3으로 비교 |
| 3 | test_models.py::`gw_and_preston_converge` | `rel < 0.10` (메시지는 "5% 이내") | GW 지수분포에서 n∝P가 **정확**하므로(gw_preston_link 테스트 1e-6, 4는 1e-4로 이미 확인) 두 모델은 보정점 밖에서도 일치해야 함 | 허용오차를 1e-3으로 조이고 메시지·assert 숫자 일치시킬 것. 10%면 실제 회귀(예: 존압력 배선 오류)를 놓침 |
| 4 | test_spatiotemporal_removal_physical_kp.py::`wide_pressure_range_deviation_is_small_and_finite` | `max(rel_dev) < 1e-2` | #3과 동일 근거(n∝P 정확해). 14~96 kPa에서도 편차는 ~1e-4 | 1e-3으로 조임 |
| 5 | test_conditioner_sweep_kinematics.py::`pca_profile_has_nonzero_coverage` | `nonzero/len > 0.05` | Zheng·Zhao·Lu 2023 Table 1 조건의 PCR 반경 프로파일(논문 Fig.) — 모듈이 Eq.1-9·Table 1을 "그대로 구현"했으므로 논문 프로파일 형상(피크 위치·가장자리 감쇠)과 대조 가능 | 논문 Fig. 디지타이즈값 또는 최소한 "피크 반경이 R_p±(R_a−R_i) 범위"라는 기하 조건으로 교체. 동시에 `pca_zero_outside_reach`의 공허 통과(`or`) 제거 |
| 6 | test_gw_contact.py::`plasticity_index_order_of_magnitude` | `0.01 < ψ < 100` | GW 1966 판정 임계(ψ<0.6 탄성, >1 소성)가 gw_contact.py:87에 이미 적혀 있음. H는 knowledge/materials/pad-hardness-porosity-measurement-methods.md(Shore D60, Pureon 데이터시트)에서 경도값 확보 가능 | 문헌 H로 ψ를 계산해 "탄성/소성 판정이 문헌 서술과 일치"를 assert. H 미확보 시 최소한 범위를 1자릿수로 |
| 7 | test_models.py::`ptw_pattern_raises_mrr` (분류상 혼합이지만 동일 성격) | `sparse > dense * 2` (주석은 "약 3.3배") | RR_up = K/ρ_eff (Boning MRS 1999 / Stine 1998)이므로 ρ=1.0 vs 0.3 → 정확히 1/0.3 = 3.333배 (PL 컨볼루션이 균일맵에선 항등) | `pytest.approx(1/0.3, rel=1e-6)` |

### 3-B. 스냅샷이 최선 — 외부 근거가 아직 없음 (3건)

| # | 테스트 | 이유 | 해제 조건 |
|---|---|---|---|
| 8 | test_wear_aware_kp_physical.py::`n_contacts_actually_increases_under_fixed_pressure_wear` | ad-hoc(MRR↓) vs GW(n↑) 모순의 **관측 방향을 정직하게 고정**. 어느 쪽이 옳은지 문헌·실험 판정 전(BACKLOG S13) | S13 판정 후 옳은 방향을 문헌값으로 assert |
| 9 | test_wear_aware_kp_physical.py::`normalized_curves_are_strongly_anticorrelated_not_matched` (corr<−0.9) + test_models.py::`wear_model_reports_unresolved_contradiction`(노트 문자열 `corr=-0.998` 고정) | 동일. 단 **문자열 안의 숫자를 고정**한 후자는 corr이 −0.997로만 바뀌어도 깨지는 취약 스냅샷 — `"정반대" in n` 조건만으로도 계약은 성립하므로 숫자 문자열은 빼는 게 안전 | S13 |
| 10 | test_pad_wear_glazing.py::`p_r_changes_significantly_over_wear_time` (>1%) | C1=2e-6이 "임의 오더"라 절대 변화량에 문헌 대응 없음. Shi & Ring 2010에는 polish-rate 감쇠 곡선이 있으나 마모계수 보정 전엔 비교 불가 | pad-lifecycle 브레이크인/글레이징 노트에서 MRR 감쇠 시상수 확보 후, C1 보정 → 감쇠율 정량 비교 |

### 3-C. 혼합(오더·정성) 중 정량화 여지 — 우선순위 낮음

- test_gw_preston_link.py::`calibration_mrr_in_literature_range`, test_preston.py::`order_of_magnitude_matches_literature`: 50~1000 / 20~2000 nm/min 폭. preston.py 주석의 STI 대표값 254.05 nm/min(ACS Langmuir 2026)과 Kp=1e-13의 관계를 명시하면 "같은 자릿수"(0.3~3배) 정도로 조일 수 있다. 단 Kp 자체가 재료조합 보정값이라 tight 대조는 부적절 — 오더 유지가 정직.
- test_slurry_film_lubrication.py::`z0_order_of_magnitude_matches_paper`: Thakurta 2001 Eq.19가 그대로 구현돼 있으므로 논문 샘플 조건에서 z0 수치를 계산해 논문 h_min=36 µm과 h_min/z0 무차원비(Fig.6c)로 대조 가능. papers/ 에 PDF 확보돼 있음.
- test_process_time.py::`rs_neq1_wiwnu_small_positive_order`(0<w<5%): #1·#2의 폐형식으로 0.39%를 해석적으로 도출하면 정량화.
- test_engine.py::`edge_pressure_increases_ttv`("3배"): p_edge_concentration P0[1+A(r/Rw)^n]에서 amp=0.3이면 엣지 MRR 증가분이 해석적으로 계산됨 → 배율을 유도값으로.

## 4. 감사 중 발견한 사소한 문제(코드 미수정, 기록만)

1. test_models.py:52 — assert 10% vs 메시지 "5% 이내" 불일치.
2. test_conditioner_sweep_kinematics.py:45 — `(not np.any(mask)) or …` 로 범위 밖 bin이 없으면 공허 통과. **실측 확인**: 현재 r_bins=25 설정에서 bin 중심 최대 354.8 mm < 도달반경 357+5 mm 이라 mask가 비어 있고, 이 테스트는 지금 **아무것도 검증하지 않는다**(항상 통과). §3-A #5에서 함께 교체.
3. test_conditioner_pcr_decay.py:37-38 — `import pytest` 후 `__import__("pytest")` 중복(동작 무해).
4. test_wear_aware_endpoint.py:38-43 — try/except 수동 플래그 대신 `pytest.raises(RuntimeError)`가 관례.
5. 문헌 근거가 모듈 docstring에만 있고 테스트 docstring엔 없는 파일이 다수(conditioner·slurry_film·pad_wear). 교체 작업 시 테스트 쪽에 출처를 옮겨 적으면 이 감사가 자동 갱신 가능해진다.

## 5. 부록 — 비(非)재현 테스트 전체 명단

재현 61개는 §1 표의 근거 열로 갈음. 아래는 조치 판단에 필요한 혼합·스냅샷·스모크 58개.

**스냅샷 (10)**: sweep_kinematics::pca_profile_has_nonzero_coverage · engine::uniform_pressure_gives_low_nonuniformity · gw_contact::plasticity_index_order_of_magnitude · models::gw_and_preston_converge · models::wear_model_reports_unresolved_contradiction · pad_wear_glazing::p_r_changes_significantly_over_wear_time · preston::rs_neq1_edge_center_ratio_matches_kinematics · spatiotemporal_physical_kp::wide_pressure_range_deviation_is_small_and_finite · wear_aware_kp_physical::n_contacts_actually_increases_under_fixed_pressure_wear · wear_aware_kp_physical::normalized_curves_are_strongly_anticorrelated_not_matched

**혼합 (31)**: conditioner_asperity::{aging_conditioner_sigma_shrinks_slower_than_ideal, sigma_monotonic_nonincreasing} · pcr_decay::{pcr_monotonic_nonincreasing, aging_conditioner_wears_more_than_ideal, three_tier_ranking} · engine::{simulate_shapes_and_units(단위 항등식+계약), edge_pressure_increases_ttv} · gw_pressure_solve::contact_area_fraction_monotonic · gw_preston_link::calibration_mrr_in_literature_range · kinematics::rs_neq1_edge_faster_than_center · models::{pressure_monotonic×4, ptw_pattern_raises_mrr, zone_pressure_applied×4} · pad_wear_glazing::{mean_height_monotonic, mrr_monotonic, decay_diminishing_returns} · preston::order_of_magnitude_matches_literature · process_time::rs_neq1_wiwnu_small_positive_order · slurry_film::{z0_order_of_magnitude, z0_decreases_with_pressure, h_min_scaling_increases_with_velocity, h_min_scaling_decreases_with_porosity_and_compressibility, wafer_rotation_offsets_pad_inflow, curvature_has_interior_maximum} · wear_aware_endpoint::naive_is_optimistic_when_mrr_decays

**스모크 (17)**: pcr_decay::calibrate_tau_from_anchor_rejects_bad_ratio · demo_app::loads_without_exception · engine::{models_registered, remaining_and_overpolish_note, ptw_and_film_notes_are_honest} · models::{all_models_registered, model_runs_and_shapes×4, pattern_density_clamps_and_warns, ptw_without_pattern_model_warns} · pourbaix::{zero_electron_raises, cu_reactions_are_self_limiting_type, complexing_agent_shifts_peak_direction} · slurry_film::p_app_zero_raises · wear_aware_endpoint::unreachable_target_raises_runtime_error
