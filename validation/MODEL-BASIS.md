# FabSim 모델 근거 보고서 (MODEL-BASIS)

생성: 2026-09-14 00:59 · 커밋 기준 자동 생성 — 손으로 고치지 말고 코드/팩/노트를 고쳐라.

완성 판정: **미완** (25/50칸). 미충족 25건은 끝에.

## 0. 결합식

```
MRR(r) = Kp · P(r) · V(r) · κ · χ · ψ · τ        (기준 조건에서 κ=χ=ψ=τ=1)
Λ, Π 는 P·V 자체의 분해(장비축), Θ·Γ·Δ·S 는 출력·진단 축 — MRR에 곱하지 않는다.
```

Kp는 팩마다 문헌 한 점에서 역산한 값이라 절대값은 그 조성·조건에 묶인다. 팩터는 전부 **기준 대비 배수**이므로 Kp와 이중 계상되지 않는다(`tests/test_factors.py`가 기준 1.0 계약을 강제).


## Λ 기계 부하 강도 (`lambda`) — 축: equipment · 파트: tool · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Λ 기계 부하 강도 = P·V (Preston 곱, 단위면적 마찰일률).

Preston MRR = Kp·P·V 에서 Kp를 뺀 나머지 전부. 장비가 웨이퍼에 가하는
기계적 부하를 단일 숫자로 압축한 것이다.

기준: 팩의 pressure_psi × (그 조건의 상대속도). 기준 조건에서 1.0.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |
| oxide_silica | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |
| sic_ceria_h2o2 | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |
| sti_ceria | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |
| w_fe_oxidizer | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |

엔진이 스스로 보고하는 한계:

- P·V = 3.456 psi·m/s (기준 대비 1.000배)

근거 노트(verify 블록 보유): `knowledge/cmp/preston-luo-dornfeld-mrr.md`, `knowledge/physics/cmp-kinematics-rotary.md`


## Π 반경 하중 분포 (`pi`) — 축: equipment · 파트: tool · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Π 반경 하중 분포 — 존압력·리테이너링이 만드는 P(r) 형상.

Λ이 '얼마나 세게'라면 Π는 '어디를 세게'다. TTV/WIWNU를 지배하는 축이고,
Λ과 직교해야 한다(전체를 키우면 Λ, 기울기를 바꾸면 Π).

정의: 정규화 P(r)/P̄ 의 엣지/센터 비. 균일하면 1.0.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |
| oxide_silica | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |
| sic_ceria_h2o2 | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |
| sti_ceria | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |
| w_fe_oxidizer | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |

엔진이 스스로 보고하는 한계:

- 균일 압력 — Π=1.0 (존압력·엣지집중 없음)

근거 노트(verify 블록 보유): `knowledge/equipment/cmp-multizone-carrier-radial-response.md`


## Θ 열·유동 부하 (`theta`) — 축: equipment · 파트: tool · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Θ 열·유동 부하 — 마찰 발열과 슬러리 냉각/공급의 균형.

발열은 두 독립 채널의 곱이다: Λ(웨이퍼-패드 마찰, 기존)과 리테이닝 링 압력(링-패드 마찰,
Lee/Guo/Jeong 2012, doi:10.1007/s12541-012-0004-8, knowledge/physics/cmp-theta-retaining-
ring-pressure-heat-channel.md — Table 1 총마찰력 선형회귀 R²>0.99). 냉각은 세 독립 채널로
이루어진다: ①슬러리 유량(SFR, 대류 물질교환) ②플래튼 냉각수 온도(열전달 구동력 ΔT)
③플래튼 회전속도(회전 대류냉각, von Karman 회전원판 Nu∝Re^0.5 — Harmand et al. 2013,
doi:10.1016/j.ijthermalsci.2012.11.009, knowledge/physics/cmp-theta-rotation-convective-
cooling-driver.md). rpm_platen은 Λ의 발열(V=ω·r_cc, 선형)에도 쓰이지만 냉각 쪽에서는
제곱근으로 스케일링돼 순net 효과는 완화될 뿐 상쇄되지 않는다(같은 노트 §2).
Yuh 2015(doi:10.1007/s40684-015-0041-8)가 SFR·온도를 독립 실험축으로 스윕했다
(knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md §1).
온도는 Arrhenius로 화학속도를, 유량은 신선 슬러리 공급을 지배한다.

⚠ 회전 냉각 채널은 전체 냉각의 일부만 차지한다(2026-09-13 정정): White 2003 원문 열저항
네트워크(정상상태 검증판은 sim/tier2_physics/cmp_theta_steady_state_heat_balance.py,
frictional-heating-temperature-arrhenius-coupling.md §8.2/§8.4)에 따르면 냉각은
G_slurry(엔탈피 수송, 회전무관)+G_pad(전도, 회전무관)+G_air(회전 대류, √Ω)의 병렬합이고
Shin 2025 중앙 케이스 분해가 슬러리 74%/패드 19%/공기 7%임을 준다. 과거에는 cool_rotation
전체를 √Ω로 스케일해 이 7% 채널의 효과를 냉각 전체(100%)에 적용했다 — 회전 냉각 효과를
심하게 과대평가한 것이다(§8.4 "정정 후보"로 기록되어 있었음). 지금은 가중평균
(1-W_AIR_FRACTION)·1.0 + W_AIR_FRACTION·√Ω로 그 7%만 반영한다. W_AIR_FRACTION=0.07은
단일 케이스(Shin 2025 중앙값)에서 나온 근사치이고 범위는 6~8%다(§8.4 최소/최대 케이스) —
구조적 결측(§8.5: 웨이퍼/헤드 경로 미모델링, L_pad 유효길이, h_air CMP 실측, 완전 열교환
가정)이 전혀 닫히지 않았으므로 confidence는 여전히 estimated다.

⚠ 절대 온도가 아니라 **기준 대비 부하비**다. 실제 ΔT 예측은
knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md 의
모델이 담당하고, 여기서는 팩터로 압축만 한다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |
| oxide_silica | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |
| sic_ceria_h2o2 | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |
| sti_ceria | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |
| w_fe_oxidizer | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |

엔진이 스스로 보고하는 한계:

- ⚠ 발열/냉각을 1차 비례로 압축했다 — 실제 열저항·체류시간은 미반영. 절대 ΔT는 별도 열모델이 담당한다.

근거 노트(verify 블록 보유): `knowledge/equipment/cmp-rpm-ratio-flowrate-temperature-mrr-stability.md`, `knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md`, `knowledge/physics/cmp-theta-retaining-ring-pressure-heat-channel.md`, `knowledge/physics/cmp-theta-rotation-convective-cooling-driver.md`, `knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md`


## Γ 컨디셔닝 부하 (`gamma`) — 축: equipment · 파트: tool · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Γ 컨디셔닝 부하 — 디스크가 패드에 가하는 단위시간 절삭일 (Preston형).

Zheng et al.(2023) Eq.11: PCR = Kp·P·v_rel. v_rel(디스크-패드 상대속도)의
지배항은 disk-rpm-load-radius-pcr.md §4가 유도·검증한 **디스크 중심 속도
ω_p·r_cc**다 — 이 항은 디스크 자전비(Rs=ω_disk/ω_pad)와 무관하게 정확하고,
같은 문헌조건(Rs=0.73)에서 디스크 전체 평균 v/(ω_p·r_cc)는 1.0004(0.04%
편차)로 사실상 완전히 지배적이다(§7 verify). r_cc는 레시피가 아니라 스윕
기구 형상(같은 장비)이므로 F·v 비율에서 상쇄돼, v 항을 rpm_platen(같은
플래튼) 비율만으로 근사할 수 있다 — Λ이 이미 쓰는 것과 동일 근사(§7 참조).

**cond_sweep_cpm(스윕 왕복수 n_a)은 v_rel 식에 나타나지 않는다** — 반경별
궤적밀도·체류시간 분포(어디를 깎는가)를 결정하는 별개 축이다
(conditioner-sweep-algorithm-trajectory-density.md,
conditioner-sweep-kinematics-pcr-profile.md). Γ는 반경 무관 스칼라(총
절삭 부하)이므로 sweep_cpm을 곱하지 않는다 — 곱하면 서로 다른 물리량
(회전 상대속도 vs 왕복수)을 이중 계상하는 것이었다(2026-09-11 정정, 이전
버전은 force×sweep×duty로 sweep을 속도 대리항처럼 썼다).

confidence는 여전히 `estimated`로 하한한다 — 이유(문헌 근거 포함):
(1) 디스크 내 상대속도의 Rs 보정항은 무시할 수 없다(에지 peak-to-peak
14.4%, §7) — disk RPM 드라이버가 팩에 없어 정량 반영이 불가능하다.
(2) 컨디셔너 자체의 PCR 시간적 소진(50h에 초기값의 16%로 감쇠,
conditioner-disk-pad-cutting-model.md §3) — `cond_disk_usage_hours`가
팩에 있으면 sim/tier2_physics/conditioner_pcr_decay.py의
`pcr_decay()`(TAU_AGING_HOURS≈27.4h, Entegris 2차인용 앵커 50h→16% 역산)로
반영된다. 없으면 여전히 디스크가 신품(aging 배수=1.0)이라고 암묵 가정한다.
이 앵커 자체가 2차 인용(Palmgren 2004 원문 미확보)이므로 confidence 하한은
유지한다. (3) 임계하중(critical downforce) 아래에서는 절삭이 안 일어난다는
비선형이 F 선형항에 미반영이다. (1)과 (3)은 완화 가능한 근사가 아니라
구조적 결측이므로, 개별 드라이버가 literature 등급이어도 모델 자체의
신뢰도는 그보다 낮게 유지한다.

⚠ 여기는 **장비 설정**(하중·회전속도·duty)만 담는다. 디스크의 형상(그릿
밀도·돌출)은 소모품이므로 κ/τ 쪽으로 간다. 이 분리를 지켜야 "디스크를
바꿀까 컨디셔너 세팅을 바꿀까"에 답할 수 있다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |
| oxide_silica | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |
| sic_ceria_h2o2 | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |
| sti_ceria | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |
| w_fe_oxidizer | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |

엔진이 스스로 보고하는 한계:

- ⚠ cond_sweep_cpm은 Γ 크기에 곱하지 않는다 — 문헌(disk-rpm-load-radius-pcr.md, conditioner-sweep-algorithm-trajectory-density.md)에 따르면 스윕 왕복수는 v_rel 식에 없고 반경별 궤적밀도(공간분포)만 결정한다. 총 절삭 부하가 아니다.
- ⚠ force×velocity(rpm_platen)×duty 곱 형태는 절삭일률의 1차 근사다 — 임계하중(critical downforce) 아래에서는 절삭이 안 일어난다는 비선형이 미반영. disk-conditioner 노트 참조.
- ⚠ velocity 항은 rpm_platen(패드 RPM)만 쓴다 — 디스크 자전비(Rs) 보정은 disk-rpm-load-radius-pcr.md §7 기준 디스크 평균으로는 <0.1%지만 디스크 에지에서는 peak-to-peak 14.4%까지 벌어진다(cond_disk_rpm 드라이버 부재로 정량 반영 불가 — 반경별 분포는 별도 모듈의 몫).

근거 노트(verify 블록 보유): `knowledge/equipment/conditioner-disk-pad-cutting-model.md`, `knowledge/equipment/disk-rpm-load-radius-pcr.md`


## κ 접촉 강도 (`kappa`) — 축: consumable · 파트: slurry, pad, disk · MRR 결합: 예

### 모델 정의 근거 (코드 docstring 그대로)

```
κ 접촉 강도 = 활성 입자 수 × 입자당 압입 깊이.

**세 파트가 함께 결정하는 대표 팩터다.**
  - 슬러리: 입경 R, 함량 → 접촉 입자 수
  - 패드:   경도 H, 탄성률 → 입자당 하중과 압입
  - 디스크: asperity 밀도 → 실접촉 면적

물리: δ_p = F/(2πR·H) 이고 제거 단면 A_f ∝ δ_p^1.5 ⟹ **MRR ∝ H^-1.5**
(knowledge/cmp/particle-wafer-interaction-... §4, verify PASS).

⚠ 화학적 연화(χ)도 같은 H를 통해 들어간다. **두 번 세지 않도록** κ는
'기계적 경도'만, χ는 '화학이 만든 경도 변화분'만 담당한다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | partial | literature | size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-size-null-result-force-partitio; pad-hardness-porosity-measurement-method; gw-contact.md |
| oxide_silica | modeled | literature | conc×1.000, size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-concentration-mrr-saturation-co; abrasive-size-concentration-ph-K-additiv; abrasive-size-concentration-ph-K-additiv; pad-hardness-porosity-measurement-method; gw-contact.md |
| sic_ceria_h2o2 | modeled | literature | conc×1.000, size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-concentration-mrr-saturation-co; abrasive-size-concentration-ph-K-additiv; abrasive-size-concentration-ph-K-additiv; pad-hardness-porosity-measurement-method; gw-contact.md |
| sti_ceria | modeled | literature | conc×1.000, size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-concentration-mrr-saturation-co; abrasive-size-concentration-ph-K-additiv; abrasive-size-concentration-ph-K-additiv; pad-hardness-porosity-measurement-method; gw-contact.md |
| w_fe_oxidizer | modeled | literature | conc×1.000, size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-concentration-mrr-saturation-co; abrasive-size-concentration-ph-K-additiv; abrasive-size-null-result-force-partitio; pad-hardness-porosity-measurement-method; gw-contact.md |

엔진이 스스로 보고하는 한계:

- ⚠ Shore D는 경도의 대리지표다. H^-1.5의 H는 압입경도(GPa)인데 Shore D↔GPa 환산이 비선형이라 순위는 맞아도 절대값은 캘리브레이션이 필요하다. Qi/Joyce/Boyce 2003(DOI:10.5254/1.3547752, 위 노트 §8)이 범용 탄성체용 Shore D→탄성률 해석해(eq.11)를 주지만 confidence는 못 올린다 — ①62D 앵커점에서 FEA 대비 49% 편향만 확인됐고 60D에서의 편향 크기는 모름, ②범용 가황고무 대상(폴리우레탄 미검증), ③애초에 그 논문의 E는 압입경도가 아니라 단축인장 탄성률이라 물리량 자체가 다르다.
- ⚠ asperity 밀도 지수 0.5는 GW 접촉에서 실접촉면적이 밀도의 제곱근에 가깝게 증가한다는 근사다 — 미검증.
- ⚠ 농도 지수 n=-0.406 — 표면적 극한(1/3)은 US9499721B2 E1 실측 전역회귀(n≈0.30)로 압입 극한(4/3)보다 우세하다고 판정됐다(같은 데이터가 국소 지수는 0.56→0.11로 붕괴 — 순수 거듭제곱은 고농도 포화를 못 담는다는 별개의 구조적 한계는 남아있음).
- ⚠ 농도 지수 n=0.333 — 표면적 극한(1/3)은 US9499721B2 E1 실측 전역회귀(n≈0.30)로 압입 극한(4/3)보다 우세하다고 판정됐다(같은 데이터가 국소 지수는 0.56→0.11로 붕괴 — 순수 거듭제곱은 고농도 포화를 못 담는다는 별개의 구조적 한계는 남아있음).
- ⚠ 부분 모델링 — 반영된 항 3/4: size, pad_hardness, asperity
- ⚠ 입자 함량 20 wt%가 포화농도 7 wt%를 넘었다 — 실제로는 더 넣어도 MRR이 안 오른다(Luo-Dornfeld 포화영역). 현재 항은 계속 증가시키므로 이 구간 예측은 과대평가다.
- 농도 지수 n=+0.333 를 **이론에서 유도**했다 (등급 estimated). n_C = p(1−αχ) = 1·(1−0.667·1) = +0.333 · n_d = −q(1−αχ)+β = -0.000
- 농도 지수 n=-0.406 를 **이론에서 유도**했다 (등급 estimated). n_C = p(1−αχ) = 1·(1−0.667·1) = +0.333 · n_d = −q(1−αχ)+β = -0.000

근거 노트(verify 블록 보유): `knowledge/cmp/abrasive-concentration-mrr-saturation-contact-probability.md`, `knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md`, `knowledge/cmp/abrasive-size-null-result-force-partition-theory.md`, `knowledge/materials/pad-hardness-porosity-measurement-methods.md`


## χ 화학 반응성 (`chi`) — 축: consumable · 파트: slurry · MRR 결합: 예

### 모델 정의 근거 (코드 docstring 그대로)

```
χ 화학 반응성 — 표면 연화·산화가 만드는 MRR 배수.

기존 sim/chemistry.py를 승계하되, pH는 **정점형 항으로 교체**한다
(단조 연화항은 pH 11 위를 과대평가한다 — `_ph_peak_term` docstring 참조).
억제 항은 여기가 아니라 ψ가 가져간다 — 방향이 반대이고, 사용자가
"함량 변화에 따른 성능 변화"를 볼 때 촉진과 억제를 분리해 봐야 한다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | partial | unverified | oxidizer×1.000 | oxidizer_wt_pct, slurry_ph | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| oxide_silica | partial | literature | ph_peak×1.000 | slurry_ph | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| sic_ceria_h2o2 | modeled | unverified | ceria_tooth×1.000, ph_ceria_window×1.000 | slurry_ph, ce3_fraction | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| sti_ceria | modeled | unverified | ceria_tooth×1.000, ph_ceria_window×1.000 | slurry_ph, ce3_fraction | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| w_fe_oxidizer | partial | estimated | oxidizer×1.000 | oxidizer_wt_pct, slurry_ph | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |

엔진이 스스로 보고하는 한계:

- pH 10.5 (정점 11, 기준 10.5) → 상대 1.000. 실측 3점(Li 2021 Fig.1) 기반 정점형(pH≳9.0), 산성(pH≤6)은 골 형태 로그이차(cn109609035b n=7, 반등 포함 피팅). ⚠ 염기 정점식은 3점을 지나는 최소 가정, 산성 골 로그이차는 n=7 피팅 — 둘 다 문헌 폐형식은 아니다. ⚠ 6~9 전환구간은 데이터 없어 로그-선형 보간(미검증 외삽).
- ⚠ R/R booster(glycine 등)가 팩에 없다 — 막질별 선택비를 만드는 주요 축인데 통로가 없다. 담당 R2-slurry.
- ⚠ pH 10는 세리아 IEP(6.8) 근접 — 제타≈0, 응집·스크래치 위험(Δ↑). 분산제 없이는 실무 부적합.
- ⚠ 화학 항들을 독립으로 보고 곱했다 — pH-흡착, 산화제-세리아 산화환원 커플링은 미모델링.
- 산화제 기계 하한 φ=0.15 (기본값) — 이 팩에 관측이 없어 금속막 CMP 의 관측 대역(0.12~0.27, 4계 독립 수렴) 중앙값을 쓴다. φ 는 재료보다 기계 조건(연마재 경도·압력·속도)이 정하는 양이다. ⚠ 이 계의 직접 관측이 아니므로 절대값은 신뢰하지 말 것.
- 세리아 chemical tooth: Ce³⁺ 분율 0.150 (기준 0.150). 화학 경로 82% + 기계 경로 18% 로 분해 — 활성점이 0 이어도 입자는 단단한 산화물이라 기계적 제거가 남는다. ⚠ Ce³⁺–MRR 함수형은 문헌에 폐형식이 없어 활성점 수에 선형으로 가정했고, 분해 비율은 Netzband & Dunn 2020 의 5.5배 관측에서 역산했다 — 미검증.
- 세리아 정전 창: pH 10 (창 4.9~6.8, 기준 10) → 상대 1.000. 창 안에서 세리아(+)·실리카(−) 인력, 밖에서 반발. ⚠ 창 위치는 IEP 물리, 기울기·잔류율은 Dandu 2009 실측 역산 — 미검증.
- 세리아 정전 창: pH 5.5 (창 2.5~6.8, 기준 5.5) → 상대 1.000. 창 안에서 세리아(+)·실리카(−) 인력, 밖에서 반발. ⚠ 창 위치는 IEP 물리, 기울기·잔류율은 Dandu 2009 실측 역산 — 미검증.

근거 노트(verify 블록 보유): `knowledge/cmp/ceria-slurry-ce-redox-selectivity.md`, `knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md`


## ψ 표면 보호도 (`psi`) — 축: consumable · 파트: slurry · MRR 결합: 예

### 모델 정의 근거 (코드 docstring 그대로)

```
ψ 표면 보호도 — 표면 흡착 보호(억제제 피복 또는 분산제 흡착)가 만드는
제거 억제 배수 (≤1).

χ와 분리한 이유: 사용자가 배합을 조정할 때 "촉진을 올릴까 억제를 낮출까"는
서로 다른 결정이다. 하나의 화학 배수로 뭉치면 그 판단이 사라진다.
디싱/에로전은 이 항이 지배한다.

ψ 정의 확장(COMPLETION.md): 원래는 Cu/W용 금속 부동태 억제제(BTA 등)만
모델링했다. 하지만 oxide_silica/sic_ceria_h2o2/sti_ceria 세 팩은 금속이
아니라 실리카/세리아 슬러리라 inhibitor_mM이 없다 — 그렇다고 표면 흡착
보호가 없는 게 아니라, 통로가 폴리머 분산제 흡착(PVA/PVP)으로 바뀐 것뿐이다.
그래서 억제제 항이 없을 때 분산제 흡착 항으로 폴백한다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | modeled | unverified | inhibitor×1.000 | inhibitor_mM | cu-electrochemistry-pourbaix-bta-oxidize; inhibitor-chelator-adsorption-isotherm-p |
| oxide_silica | modeled | literature | dispersant×1.000 | dispersant_type | abrasive-size-concentration-ph-K-additiv |
| sic_ceria_h2o2 | modeled | estimated | dispersant×1.000 | dispersant_type | abrasive-size-concentration-ph-K-additiv |
| sti_ceria | modeled | estimated | dispersant×1.000 | dispersant_type | abrasive-size-concentration-ph-K-additiv |
| w_fe_oxidizer | modeled | unverified | inhibitor×1.000 | inhibitor_mM | cu-electrochemistry-pourbaix-bta-oxidize; inhibitor-chelator-adsorption-isotherm-p |

엔진이 스스로 보고하는 한계:

- ψ 정의 확장: 표면 흡착 보호(passivation/adsorption shield) — 이 팩은 금속 부동태가 아니라 폴리머 분산제 흡착 경로
- ⚠ surfactant가 미연결 — 계면활성제도 피복을 통해 억제에 기여하는데 통로가 없다.
- 분산제 흡착 보호: NONE = 기준 조성이라 배수 1.000 (Kp가 이 조성에서 역산됐다 — 절대 저해율을 다시 곱하면 이중 계상). 다른 분산제로 바꾸면 그 상대비가 반영된다(knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md §6, Li et al. 2021 실측).
- 억제제 1 mM (기준 1 mM), θ=0.966. ⚠ 고농도 감쇠 형상(inhibitor_strength_k)은 문헌값 없음 — 캘리브레이션 대상.
- 억제제 121.8 mM (기준 121.8 mM), θ=0.993. ⚠ 고농도 감쇠 형상(inhibitor_strength_k)은 문헌값 없음 — 캘리브레이션 대상.

근거 노트(verify 블록 보유): `knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md`, `knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md`, `knowledge/cmp/inhibitor-chelator-adsorption-isotherm-passivation.md`


## τ 슬러리 전달 (`tau`) — 축: consumable · 파트: slurry, pad, disk · MRR 결합: 예

### 모델 정의 근거 (코드 docstring 그대로)

```
τ 슬러리 전달 — 접촉부에 도달하는 신선 슬러리 유효분율.

⚠⚠ 이 팩터의 가장 중요한 사실: **"슬러리를 더 많이 나르면 MRR이 비례해서
오른다"는 직관은 실측으로 기각됐다.**

근거 ①  Prasad 2013 (doi:10.1557/jmr.2013.173, III.D.3, Mirra 툴 TEOS):
  동일 수지경도·유사 기공크기에서 기공률 %P만 15%→45%로 30%p 올렸는데
  평균 RR 증가는 **단 8%**("nominal increase", 원문 표현). 저자 스스로
  "기공=슬러리 저장소이므로 비례 증가"를 기대했다가 빗나갔다고 적었다.

근거 ②  Mu et al. 2016 (doi:10.1016/j.mee.2016.02.035, Table 3):
  그루브 폭 → 슬러리 이용효율 η (3 PSI 기준)
      300 µm → η 9.9%
      600 µm → η 13.4%   (+35% 상대)
      900 µm → η 12.8%   (정체·미세 감소)
  **단조가 아니다.** 600 µm 부근에서 꺾인다. 넓힐수록 좋다는 가정은
  틀렸다 — V_groove와 V_total이 함께 커져 q_actual 비율이 안 변하기 때문이다
  (저류 부피가 과하면 정체 슬러리가 늘어난다).

그래서 이 구현은 두 가지를 지킨다:
  1. η는 **실측 3점 보간**으로 낸다(단조 멱함수 금지 — 정체 구간을 놓친다).
  2. η→MRR 결합은 **매우 약하게** 들어간다. 지수는 Prasad 데이터에서 역산:
     보유용량 3배(15→45%)에 RR 1.08배 ⟹ n = ln(1.08)/ln(3) ≈ 0.07.
     ⚠ 이건 기공률 실험에서 뽑아 그루브 축에 적용한 **교차 대입**이라
     미검증이다. 순위(전달이 나아지면 조금 낫다)만 신뢰하고 크기는
     캘리브레이션 대상이다.

τ가 진짜로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다.
Prasad III.D.2: 기공 2 µm 패드는 중심이 슬러리 기아로 처지고 엣지가 올라
엣지-중심 RR 차이가 200 nm/min을 넘었다. 그 프로파일 결합은 아직 미구현이며
이 사실을 notes에 싣는다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | modeled | unverified | groove_eta×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |
| oxide_silica | modeled | unverified | groove_eta×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |
| sic_ceria_h2o2 | modeled | unverified | groove_eta×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |
| sti_ceria | modeled | unverified | groove_eta×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |
| w_fe_oxidizer | modeled | unverified | groove_eta×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |

엔진이 스스로 보고하는 한계:

- ⚠ τ 등급=unverified: 드라이버(기공률·그루브폭)는 literature 등급이지만 τ의 **결합 지수**(tau_mrr_exponent=0.07)가 기공률 실험에서 역산해 그루브 축에 교차 대입한 값이라 크기를 문헌이 보증하지 않는다 — 가장 약한 고리가 등급을 정한다. 순위만 신뢰하라.
- ⚠ τ가 실제로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다. 기공 2 µm 패드에서 중심이 슬러리 기아로 처지고 엣지-중심 RR 차이가 200 nm/min을 넘었다(Prasad 2013 III.D.2). 이 프로파일 결합은 미구현 — 담당 R3-pad × R2-slurry.
- 그루브 폭 600 µm → 슬러리 이용효율 η=13.4% (기준 600 µm, η=13.4%). ⚠ η는 600 µm 부근에서 정체·반전한다 — 넓힐수록 좋지 않다(Mu 2016 Table 3 실측).
- 기공률 30% (기준 30%). ⚠ 실측상 기공률 15→45%(3배)에도 RR은 8%만 올랐다 — 비례 가정은 기각됐다(Prasad 2013). 기공 외 이송(그루브·간극)을 기공률 등가 360% 로 두어 두 실측점을 정확히 재현한다. 기공 경로 기여는 7.7% 뿐이다.

근거 노트(verify 블록 보유): `knowledge/materials/pad-groove-geometry-contact-area-flow-resistance.md`, `knowledge/materials/pad-porosity-slurry-transport-mrr.md`


## Δ 손상 유발도 (`delta`) — 축: consumable · 파트: slurry, pad, disk · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Δ 손상 유발도 — 스크래치·결함 발생 경향.

대입자 tail(D99)이 지배한다. 평균 입경이 아니라 **꼬리**가 스크래치를 만든다.

⚠ 2026-09-13 추가: `aggregate_ratio`(콜로이드 불안정화 정도, 0~1) 항을 곱셈으로
추가했다. 근거: Basim & Moudgil 2002 (J. Colloid Interface Sci. 256(1) 137-142,
doi:10.1006/jcis.2002.8352) — NaCl 0.2M(이 계의 CCC=0.25M 미달, 벌크 광산란
입도계로는 **평균 입경이 전혀 안 바뀜**)인데도 AFM 최대표면변형(Rmax)이
25nm→50nm로 **2배** 증가했다(원문 Table 1). 즉 d99가 포착 못 하는 "일시적
(transient) 응집체"에 의한 손상 경로가 d99 경로와 독립적으로 존재한다는 것이
실측으로 확인됐다(knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism.md
§3, §6). `aggregate_ratio=1.0`을 "이 논문의 NaCl 0.2M 불안정화 정도"로 정의하고
그 조건에서 관측된 배수(2.0)로 계수를 고정했다: `1 + aggregate_ratio`.
⚠⚠ 이 계수는 **n=1(단일 데이터점)**에서 나온 값이다 — 화학종(실리카 학술
모델계)·조건(7.0 psi, IC1000/Suba IV) 특유의 값이며 다른 화학종·조건으로의
일반화는 미검증이다. 순위(불안정화가 클수록 손상↑)만 신뢰하라. 팩 기본값은
`aggregate_ratio=0.0`(무영향, 항×1.0)이라 기존 팩·기준 조건의 Δ 계약은 안 깨진다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | modeled | estimated | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec |
| oxide_silica | modeled | literature | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec |
| sic_ceria_h2o2 | modeled | estimated | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec |
| sti_ceria | modeled | estimated | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec |
| w_fe_oxidizer | modeled | literature | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec |

엔진이 스스로 보고하는 한계:

- 손상 지수 n=1.44(등급=literature) — 2026-09-14 판정(EVIDENCE-RULES #12): 이전 코드 기본값 n=3.0은 출처 없는 가정값(E6, 채택 금지)이었다. US8439995B2(Hitachi, 세리아 D99-스크래치 4점 실측) 로그-로그 회귀 n≈1.44(R²=0.997, E3)로 교체했다 — knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §3. 교차확증: lpc-scratch-density-tail-correlation.md(Remsen 2006, fumed silica)도 선형(n≈1 근방)을 지지해 같은 방향(n=3.0보다 훨씬 완만)으로 수렴한다. 순위(큰 입자가 더 긁는다)는 물론 절대 배수도 이제 문헌 근거가 있으나, 표본이 작아(세리아 1개 화학종, 실질 독립 3점) confidence 상한은 literature — verified로는 올리지 않는다.
- 손상 지수 n=2.54(등급=estimated) — 2026-09-14 판정(EVIDENCE-RULES #12): 이전 코드 기본값 n=3.0은 출처 없는 가정값(E6, 채택 금지)이었다. US8439995B2(Hitachi, 세리아 D99-스크래치 4점 실측) 로그-로그 회귀 n≈1.44(R²=0.997, E3)로 교체했다 — knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §3. 교차확증: lpc-scratch-density-tail-correlation.md(Remsen 2006, fumed silica)도 선형(n≈1 근방)을 지지해 같은 방향(n=3.0보다 훨씬 완만)으로 수렴한다. 순위(큰 입자가 더 긁는다)는 물론 절대 배수도 이제 문헌 근거가 있으나, 표본이 작아(세리아 1개 화학종, 실질 독립 3점) confidence 상한은 literature — verified로는 올리지 않는다.
- 손상 지수 n=2.54(등급=literature) — 2026-09-14 판정(EVIDENCE-RULES #12): 이전 코드 기본값 n=3.0은 출처 없는 가정값(E6, 채택 금지)이었다. US8439995B2(Hitachi, 세리아 D99-스크래치 4점 실측) 로그-로그 회귀 n≈1.44(R²=0.997, E3)로 교체했다 — knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §3. 교차확증: lpc-scratch-density-tail-correlation.md(Remsen 2006, fumed silica)도 선형(n≈1 근방)을 지지해 같은 방향(n=3.0보다 훨씬 완만)으로 수렴한다. 순위(큰 입자가 더 긁는다)는 물론 절대 배수도 이제 문헌 근거가 있으나, 표본이 작아(세리아 1개 화학종, 실질 독립 3점) confidence 상한은 literature — verified로는 올리지 않는다.

근거 노트(verify 블록 보유): `knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md`, `knowledge/cmp/lpc-scratch-density-tail-correlation.md`, `knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism.md`


## S 시간 안정성 (`stab`) — 축: consumable · 파트: slurry, pad, disk · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
S 시간 안정성 — 컨디셔닝 없는 연속 연마 중 MRR 드리프트(로그감쇠).

출처: Jeong, Shin, Jeong, Jeong, Jeong (2024), "Novel Probability Density
Function of Pad Asperity by Wear Effect over Time in CMP", Materials 17(8),
1817, doi:10.3390/ma17081817 (PMC11051262, 전문 확보). Fig.9 정규화 MRR
(IC1000 패드·콜로이달 실리카·SiO2 블랭킷·컨디셔닝 없이 1~10분 연속연마,
2/5 psi 두 조건 pooled)를 rate=a+b·ln(t[min]) 로그감쇠 회귀(R²=0.74,
지식노트 knowledge/materials/pad-glazing-mechanism-mrr-decay.md §4(D)가
로그형이 선형보다 우수함을 별도로 확인)로 피팅해 시간축 인자로 편입.
기준 조건(Recipe 기본 time_s=60s=1 min)에서 정확히 1.0 — ln(1)=0.

⚠ 도메인 한계: (1) 원 데이터는 실리카/IC1000 단일계이며 세리아·알루미나
슬러리·다른 패드로의 외삽은 미검증(confidence=estimated로 강등).
(2) 1~10분 범위 밖은 clamp(외삽 금지, 값 고정). (3) 이 회귀는 무-컨디셔닝
단발 연마의 초기 드리프트만 담는다 — 컨디셔닝 사이클·패드 수명(수십 시간)
누적 마모는 여전히 미모델링(담당 R3-pad×R4-disk, 실데이터 없음).

⚠ 2026-09-13 EVIDENCE-RULES 판정#8 — pad_usage_hours·pad_wafer_count·
disk_usage_hours를 드라이버 수집 대상에서 제외한다(스코프 축소, τ의
groove_depth_mm 축소와 같은 패턴). 근거: Son & Lee 2021(doi:10.3390/app11083521)
이 확보한 수십시간 축 MRR 드리프트(Case I 44.9%/16h vs Case II 7.4%/20h,
6.1배 차이)는 **컨디셔너 구조(swing-arm 단일 vs 분할형 5구역)** 가 지배
인자임을 논문이 직접 명시하는데, FabSim 팩은 컨디셔너 구조를 파라미터로
갖지 않는다 — 어느 감쇠율(2.81%/h vs 0.37%/h)을 쓸지 근거가 없다.
Song & Kim 2018류 디스크 그릿 구조 비교 문헌(doi:10.1007/s00170-018-1956-3)도
같은 구조: PWR·MRR이 그릿 배열/타입에 갈리고 시간/웨이퍼수만으로는 안 갈린다.
즉 이 시간축은 physically real 하지만, "장비 구성 변수"가 팩에 없어 이식할
수 없다 — knowledge/materials/pad-usage-hours-conditioning-mrr-decay-son-lee2021.md
§7(구현 요청)이 이미 이 선행조건을 명시했었다. 컨디셔너 구조가 팩 파라미터로
추가되기 전까지는 이 세 드라이버를 걷어내는 것이 "빠진 항을 숨기는 것"이
아니라 "반응 안 하는 죽은 드라이버를 정직하게 걷어내는 것"이다(PARTIAL이
아니라 modeled로 승격 가능해짐 — time_s만 남은 드라이버와 완전히 일치).
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | modeled | estimated | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |
| oxide_silica | modeled | literature | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |
| sic_ceria_h2o2 | modeled | estimated | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |
| sti_ceria | modeled | estimated | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |
| w_fe_oxidizer | modeled | estimated | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |

엔진이 스스로 보고하는 한계:

- ⚠ 원 데이터는 콜로이달 실리카/IC1000 단일계다 — 이 팩의 연마입자(alumina)로의 외삽은 미검증(confidence=estimated). fumed vs colloidal 실리카만도 감쇠율이 5배 차이 난다(knowledge/materials/pad-glazing-mechanism-mrr-decay.md §3, Lawing 2004) — 다른 화학종은 그 이상 벗어날 수 있다.
- ⚠ 원 데이터는 콜로이달 실리카/IC1000 단일계다 — 이 팩의 연마입자(ceria)로의 외삽은 미검증(confidence=estimated). fumed vs colloidal 실리카만도 감쇠율이 5배 차이 난다(knowledge/materials/pad-glazing-mechanism-mrr-decay.md §3, Lawing 2004) — 다른 화학종은 그 이상 벗어날 수 있다.
- ⚠ 컨디셔닝 사이클·수십 시간 규모 패드 수명 누적 마모는 여전히 미모델링 (무-컨디셔닝 단발 1~10분 데이터만 반영). 담당 R3-pad × R4-disk.

근거 노트(verify 블록 보유): `knowledge/materials/pad-glazing-mechanism-mrr-decay.md`


## 파라미터 도출 근거 (팩 YAML의 source/note/confidence 그대로)


### 팩 `cu_h2o2_bta`

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| film | cu |  | verified |  |  |
| abrasive | alumina |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| kp_m_per_pa | 3.5e-13 | m^2/N | estimated | knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md | ⚠ Cu는 산화막보다 MRR이 크다(연질 금속 + 화학적 산화층 제거). 이 값은 문헌 MRR 범위(400~800 nm/min @ 2~3psi)에서 역산한 대표값이며 우리가 재현 검증하지 않았다. 실데이터 캘리브레이션(M3) 전까지 절대값을 신뢰하지 마라. |
| slurry_ph | 4.0 | pH | literature | knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md | 산성 — Pourbaix상 Cu 용해/부동태 경계 제어 |
| oxidizer | H2O2 |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| oxidizer_wt_pct | 3.0 | wt% | verified | knowledge/cmp/slurry-components-overview.md | 이번 런의 H2O2 농도. 이 값을 바꾸면 화학층이 MRR을 바꾼다 |
| oxidizer_ref_wt_pct | 3.0 | wt% | verified | knowledge/cmp/slurry-components-overview.md | 기준 농도 — 화학 배수가 1.0이 되는 지점. Kp가 이 조성의 문헌 MRR에서 역산됐으므로 반드시 명시해야 한다. 없으면 로더가 '현재 농도'로 폴백해 항상 자기 자신과 비교하게 되고 배수가 영원히 1.0이 된다(2026-09-06 실제 발생: 산화제 민감도가 '미모델링'으로 오진됐 |
| oxidizer_peak_wt_pct | 3.0 | wt% | verified | knowledge/cmp/slurry-components-overview.md | Kaufman 경쟁모델의 MRR 정점 농도. 착화제 유무로 1%→3% 이동이 확인됨. 화학층은 이 정점 대비 손실을 계산한다(정점에서 배수 1.0). |
| oxidizer_curve_n | 2.0 | - | unverified | knowledge/cmp/slurry-components-overview.md | 단봉 곡선의 정점 이후 감소 완만도. ⚠현상론 형상 파라미터, 미검증 |
| inhibitor | BTA |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| inhibitor_mM | 1.0 | mM | verified | knowledge/cmp/slurry-components-overview.md | BTA 농도. Langmuir θ=0.97 → 표면 97% 피복 = 제거 억제 |
| inhibitor_dG_ads_kJ | -35.4 | kJ/mol | verified | knowledge/cmp/slurry-components-overview.md | BTA 흡착 자유에너지. K=2.9e4 L/mol로 환산되며 노트 verify 블록 PASS. 물리흡착(-20~-40 kJ/mol) 영역 — 세리아 화학흡착(-111~-258)과 대비된다. |
| inhibitor_ref_mM | 1.0 | mM | verified | knowledge/cmp/slurry-components-overview.md | 기준 농도. 여기서 화학 배수가 정확히 1.0이 되어 Kp가 그대로 쓰인다. Kp가 이 조성의 문헌 MRR에서 역산됐기 때문에 반드시 일치시켜야 이중계상이 없다. |
| inhibitor_strength_k | 3.0 | - | unverified | knowledge/cmp/slurry-components-overview.md | ⚠ 억제 강도 형상 파라미터. 잔여율 = exp(-k·θ). (1-θ)를 쓰면 θ가 0.97에서 포화돼 2mM과 5mM이 구분되지 않는다(실제 발생). 실제 억제는 피복률뿐 아니라 막 치밀도·재생속도에도 달려 고농도에서도 계속 세진다. **문헌 폐형식 없음 — 캘리브레이션 1순위.**  |
| abrasive_size_nm | 100.0 | nm | literature | knowledge/cmp/abrasive-size-d50-ekc-alumina-cu-h2o2-bta-gopa | Cu+알루미나+H2O2+BTA를 정확히 동시에 다루는 1차 문헌(Gopal & Talbot 2007, JES 154(6) H507, doi:10.1149/1.2718474 — 원문 PDF 직접 확보·판독)에서 EKC Technology 알루미나 공칭 입경 100 nm(Ihnfeldt & |
| abrasive_size_exponent | 0.0 | - | literature | knowledge/cmp/abrasive-size-null-result-force-partition-theo | **검증된 영(null) 결과 — "모름"이 아니라 "효과 없음"이다.** EVIDENCE-RULES.md 판정 #1 (2026-09-11)로 확정. 5회차 순환하던 RESPONSE_DEAD를 종결한다. 충돌: Bai 2007(Appl.Surf.Sci. 253, 8489) 폐형식 유도는 |
| abrasive_d99_nm | 500.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | abrasive_size_nm(100 nm) × D99/D50 일반비 5.00 유도값(Silco/Levitronix 2008). 독립 상한 대조: Showa Denko US6770218B2(알루미나 + 질산철 금속 CMP, W·Cu 동일 슬러리) 명세 "maximum grain size |
| abrasive_ref_d99_nm | 500.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지 |
| damage_exponent | 2.54 | - | estimated | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | Egan & Kim 2019(ECS JSS 8(5) P3206, GLOBALFOUNDRIES 300mm 양산) 두 관측 n_temp=3.73 / n_agit=1.73의 기하평균(로그축 중앙). ⚠ 원 관측은 **텅스텐** 벌크 CMP다 — Cu로의 전이는 연마입자·촉매 계열 유사성(Sh |
| dishing_sensitivity | 1.0 | - | unverified | knowledge/cmp/pattern-dependent-dishing-erosion.md | ⚠ 미연결. dishing 정량에는 금속:산화막 MRR 비가 필요한데 아직 두 팩을 동시에 로드하는 다막질 모델이 없다(film-cu 에이전트 대기). |
| film_bulk_hardness_pa | 1200000000.0 | Pa | literature | Nanoindentation of electroplated Cu films — 결정립 크기에 따라 1.0~1 | 전해도금 구리막의 나노압입 경도. 산화막보다 한 자릿수 무르다 — 같은 접촉응력에서도 소성 쪽으로 더 가깝다는 뜻이다. ⚠ 이것은 **벌크** 경도이지 CMP 가 실제로 깎는 화학 변질층의 경도가 아니다. 변질층 경도의 절대값은 공개 문헌에 없다(_knowledge_audit/mecha |

### 팩 `oxide_silica`

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| film | oxide |  | verified |  |  |
| abrasive | silica |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| kp_m_per_pa | 1e-13 | m^2/N | verified | knowledge/cmp/preston-luo-dornfeld-mrr.md | STI 문헌 캘리브레이션점: P=20.7kPa, V=0.8m/s → MRR≈254.05 nm/min. sim/tier1_empirical/preston.py 가 이 값으로 5/5 PASS. |
| slurry_ph | 10.5 | pH | literature | knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md | 실리카 슬러리 염기성 — 표면 실라놀 이온화로 제거 촉진 |
| abrasive_size_nm | 50.0 | nm | literature | knowledge/cmp/particle-wafer-interaction-mechanical-chemical |  |
| abrasive_iep_ph | 2.5 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 실리카 등전점 — pH 10.5에서 강한 음전하 → 정전 안정 |
| hamaker_j | 8.5e-21 | J | literature | knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md §5 | 실리카-물-실리카 Hamaker 상수. 노트 §5: "실리카-물-실리카는 통상 ~0.85×10^-20 J 오더로 채택(본 재현값)" — sim/tier2_physics/dlvo_colloid.py self-test가 이 값으로 DLVO V_T(h) 정성 형태(장벽 존재/소멸)를 재현한다 |
| abrasive_wt_pct | 20.0 | wt% | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | Li et al. 2021 pH 실험 조건(20 wt% 콜로이달 실리카, K+ 0.25 mol/L). 통상 범위는 1~10 wt%(총론)이나 이 논문 계는 20~30 wt%로 높다. |
| abrasive_ref_wt_pct | 20.0 | wt% | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | κ 농도항 기준점 — 위와 같은 조건 |
| abrasive_conc_exponent | 0.3333 | - | literature | knowledge/cmp/abrasive-concentration-mrr-saturation-contact- | R ∝ C0^(1/3) 표면적 지배 극한. Li 2021 자체는 1/3(표면적)과 4/3(압입) 두 극한을 제시만 하고 어느 쪽인지 확정하지 않았으나(E5), 같은 화학계(TEOS/콜로이달실리카)의 US9499721B2 E1 직접 실측(TABLE 18, 0.5~3.0wt% 4압력)을 3 |
| abrasive_saturation_wt_pct | 7.0 | wt% | literature | knowledge/materials/pad-3dprinted-nonporous-lowdefect-review | Luo-Dornfeld 포화영역 — 퓸드 실리카 12 wt% 계에서 7 wt% 이상 RR 불변 확인. 이 위로는 농도항이 과대평가된다(factors.py가 경고를 띄운다). |
| abrasive_ref_size_nm | 50.0 | nm | literature | knowledge/cmp/particle-wafer-interaction-mechanical-chemical | κ 입경항 기준점 — abrasive_size_nm과 같은 값 |
| abrasive_size_peak_nm | 80.0 | nm | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | Li et al. 2021 Fig.4 실측 MRR 정점 위치(40/80/130nm 스윕 중 80nm 최대) |
| abrasive_size_exp_below_peak | 1.3333333333 | dimensionless | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | 정점 이하(40→80nm) 구간 지수 = Eq.4(압입 지배) φ 지수 4/3. 2026-09-13 pdfplumber 벡터좌표 재추출로 확정(이전 버전은 지수·부호 OCR 혼선으로 미배선 상태였음). |
| abrasive_size_exp_above_peak | -0.3333333333 | dimensionless | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | 정점 이상(80→130nm) 구간 지수 = Eq.3(표면적 지배) φ 지수 -1/3. 2026-09-13 pdfplumber 벡터좌표 재추출로 확정. |
| ph_peak | 11.0 | pH | verified | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | MRR 최대 pH (20 wt% 실리카, K+ 0.25 M, SiO2 막). 정점형 거동 |
| ph_ref | 10.5 | pH | literature | knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md | χ pH항 기준점 — 이 팩의 slurry_ph와 같은 값 |
| ph_mrr_at_peak_rel | 1.113 | - | verified | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | pH 10.0 대비 pH 11.0의 MRR 비 (1727/1551 = 1.113, +11.3%). 노트 verify 블록이 이 값을 assert한다. |
| abrasive_d99_nm | 250.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | abrasive_size_nm(50 nm) × D99/D50 일반비 5.00 유도값. 일반비 출처는 Silco/Levitronix CMP Users Conference 2008 슬라이드 p.11(3세대 관측 4.29~5.00, 중앙값 5.00, 산업 컨퍼런스 2차 자료). 오더 대조:  |
| abrasive_ref_d99_nm | 250.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지 |
| damage_exponent | 1.44 | - | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | US8439995B2(Hitachi 세리아) 4점 로그-로그 회귀 n=1.444, R²=0.997. 막질 일치 (산화막 CMP)이나 연마입자 불일치(세리아 vs 콜로이달 실리카) — 조건 외삽. 교차확증: Remsen 2006(퓸드실리카·산화막) Table V가 선형(n≈1)을 지지해  |
| slurry_viscosity_pa_s | 0.001 | Pa·s | literature | knowledge/materials/slurry-viscosity-rheology-literature-val | 콜로이달 실리카 CMP 슬러리 **실측** 점도. Lee et al. 2025 (Nanomaterials 15(16) 1248, DOI 10.3390/nano15161248, OA) Brookfield DV-II+Pro: 첨가제 무관 기본 슬러리 ~0.98 cP (§3.2 Fig.3a) |
| pad_ra_m | 5e-06 | m | estimated | knowledge/physics/cmp-lubrication-regimes.md §5 | 패드 raised 영역 평균거칠기 — 노트는 "~5µm 전형"으로만 명시 |
| dispersant_type | NONE | - | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | Li et al. 2021 §6의 기준 MRR(2700 Å/min, 무첨가)과 이 팩의 기준 조성을 일치시킨다 — 팩 기본값에서 ψ=1.0이 되어 이중 계상을 피한다. PVA(-3.6%), PVP(-7.9%)는 같은 논문 실측값이며 레시피 오버라이드로 스캔한다. |
| film_bulk_hardness_pa | 9e+09 | Pa | literature | Nanoindentation of thermal/TEOS SiO2 films — 표준 보고 범위 8~10 G | 열산화막·TEOS 산화막의 나노압입 경도. 3 psi 조건의 실접촉 압력(약 36 MPa)보다 두 자릿수 크므로 탄성 접촉 레짐을 가리킨다. ⚠ 이것은 **벌크** 경도이지 CMP 가 실제로 깎는 화학 변질층의 경도가 아니다. 변질층 경도의 절대값은 공개 문헌에 없다(_knowledge |

### 팩 `sic_ceria_h2o2`

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| film | sic_4h |  | measured | Wang et al. ACS SI Table S3 — 4H-SiC 웨이퍼 |  |
| abrasive | ceria |  | measured | Wang et al. ACS SI Table S3 — CeO2 연마입자 |  |
| slurry_ph | 10.0 |  | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (pH 9/10/11) |  |
| ph_softening_ref | 10.0 |  | measured | Wang et al. ACS SI Table S3 — DOE 중심값을 기준으로 잡는다 |  |
| ph_softening_per_unit | 0.2787 |  | measured | Wang et al. ACS SI Table S3 50조건 역산 (pH만 다른 9조/12쌍, 배수 1.633 |  |
| abrasive_ref_wt_pct | 4.0 | wt% | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (CeO2 2/4/6 wt%) |  |
| abrasive_conc_exponent | -0.406 | - | literature | knowledge/cmp/sic-alumina-concentration-negative-exponent-en | base(oxide_silica)의 +1/3(표면적지배, Li2021 콜로이달실리카 1~30wt%)을 오버라이드. SiC+알루미나 직접 실측(US20220315802A1 Table 1, n=5, 0.1~5wt%)에서 로그-로그 회귀로 지수 -0.406(음수, 압입지배 레짐) 확인 — E |
| oxidizer_ref_wt_pct | 4.0 | vol% | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (H2O2 2/4/6 vol%) | ⚠ 키 이름은 wt_pct 인데 원문 단위는 **vol%** 다(Wang DOE: H2O2 2/4/6 vol%). H2O2 30% 수용액 기준 vol%↔wt% 는 밀도차로 약 1.1배 어긋나므로 엄밀히 같지 않다. χ 항이 **기준 대비 비(c/c_ref)** 로만 쓰므로 같은 단위끼리 |
| abrasive_size_nm | 120.0 | nm | literature | knowledge/cmp/sic-ceria-abrasive-particle-size-chen2017-rsc. | SiC+세리아 1차 문헌 실측값으로 승격(기존 base sti_ceria 상속값 80nm는 세리아가 아니라 같은 원문의 실리카 dmean을 잘못 전용한 값으로 보임 — 노트 §3). Chen et al. 2017 (RSC Adv. 7, 16938–16952, DOI 10.1039/C6R |
| dispersant_type | NONE | - | estimated | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | oxide_silica 팩에서 상속된 경로이다. Li et al. 2021은 실리카 슬러리 실통이라 세리아(STI/SiC) 화학계로의 전이는 교차계 외삽이다(EVIDENCE-RULES E4) — 세리아 슬러리는 실제로 EAA 공중합제 분산제를 사용한다는 정직 기록이 slurry-comp |
| slurry_viscosity_pa_s | 0.0014 | Pa·s | literature | knowledge/materials/slurry-viscosity-rheology-literature-val | 세리아 슬러리 실제 점도(sti_ceria와 동일 근거: Kim 2024 DOI 10.3390/polym16243593 §3.3 Fig.17d 상용 세리아 1.41 cP, 25°C). ⚠ H2O2 추가 세리아 슬러리의 점도를 **직접 재는 문헌은 미확보**다. H2O2는 저농도 수용액이 |
| abrasive_ref_size_nm | 120.0 | nm | literature | 이 팩의 abrasive_size_nm 과 같은 출처 — 기준점은 독립 측정값이 아니라 '어느 조건에서 Kp | κ 입경항 기준점 — 이 팩의 abrasive_size_nm(120 nm)과 일치시킨다. 키가 없어 실리카 부모의 50 nm 를 상속하고 있었다 (2026-09-13 model_hygiene 극한검사가 검출). |
| abrasive_wt_pct | 4.0 | wt% | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (CeO2 2/4/6 wt%) | 이 팩의 근거 DOE(Wang et al. ACS SI Table S3) 중심 수준. 이전에는 키가 없어 실리카 부모의 20 wt% 를 상속했는데, 그 값은 DOE 범위(2/4/6 wt%) 밖이고 이 재료계의 근거가 아니다 — 기준점 4.0 과 5배 어긋나 기준조건에서 κ 농도항이 0. |
| wafer_iep_ph | 4.9 | pH | literature | knowledge/cmp/sic-isoelectric-point-singh2006-jnr.md | SiC 표면 등전점(1차 문헌 실측, 분산제 무첨가 조건, PCD·입도·점도 3중 정합). base(sti_ceria)에서 상속되던 실리카 산화막 IEP(2.5)는 SiC 표면이 아니라 다른 막질(oxide_silica) 것이므로 이 팩 전용값을 명시적으로 선언한다(sim/factors |
| film_bulk_hardness_pa | 26000000000.0 | Pa | literature | Nanoindentation of 4H-SiC single crystal — 보고 범위 24~28 GPa | 4H-SiC 단결정의 나노압입 경도. 이 저장소에서 가장 단단한 막질이고, 그래서 같은 압력에서도 탄성 쪽에 깊이 머문다. ⚠ 이것은 **벌크** 경도이지 CMP 가 실제로 깎는 화학 변질층의 경도가 아니다. 변질층 경도의 절대값은 공개 문헌에 없다(_knowledge_audit/mec |
| abrasive_size_peak_nm | 163.0 | nm | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 세리아 입경-MRR 정점. 근거·한계·등급은 sti_ceria.yaml 의 동일 키와 같다 (Oh et al. 2010 MEE DOI 10.1016/j.mee.2010.07.040, 62/116/163/232 nm 중 163 nm 최대 — 1차 전문 미확보, Wang et al. 202 |
| abrasive_size_exp_below_peak | 1.3333333333 | dimensionless | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 압입 지배 d^(4/3). Bellahsene et al. 2025 (DOI 10.3390/nano15171366, MDPI OA, 전문 확보) §2.1 Eq.(1) 메커니즘 폐형식. 상속을 끊고 명시 재선언 (값은 부모와 동일하나 판단 주체를 이 팩으로 옮긴다). ⚠ 세리아·SiC 계 |
| abrasive_size_exp_above_peak | -0.3333333333 | dimensionless | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 표면적 지배 d^(-1/3). 근거·한계는 abrasive_size_exp_below_peak 와 동일. ⚠ 이 팩의 본값 120 nm 는 정점 163 nm 아래이므로 이 지수는 현재 기준조건에서 발동하지 않는다(120 nm < 163 nm → below 가지). 입경 슬라이더를 163 |
| ph_ref | 10.0 | pH | literature | 이 팩의 slurry_ph 와 같은 출처 — 기준점은 독립 측정값이 아니라 "어느 조건에서 Kp 를 역산했는 |  |

### 팩 `sti_ceria`

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| abrasive | ceria |  | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md |  |
| kp_m_per_pa | 2.2e-13 | m^2/N | estimated | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | ⚠ 세리아는 화학결합(Si-O-Ce) 기반이라 실리카보다 산화막 MRR이 높다. Netzband 2020에서 H2O2 첨가 시 Ce3+ 증가로 MRR 5.5배 변화가 보고됐는데, 그건 조성 의존이라 단일 상수로 뭉뚱그린 이 값은 대표값일 뿐이다. 미재현. |
| slurry_ph | 5.5 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 세리아 IEP 6.8 부근 아래 — 약양전하로 실리카 표면(음전하) 정전인력 |
| abrasive_iep_ph | 6.8 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md |  |
| ph_ref | 5.5 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §4 | 세리아 정전 창(2.5~6.8) 안의 기준점 — slurry_ph와 같은 값 |
| wafer_iep_ph | 2.5 | pH | literature | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §4 | 실리카 산화막 표면 IEP. 정전 창의 하단. 2차 인용 범위(2~3) |
| abrasive_size_nm | 60.0 | nm | literature | knowledge/cmp/sti-cmp-ceria-high-selectivity-nitride-stop-di | Dandu Veera, Peddeti, Babu 2009 (J. Electrochem. Soc. 156(12) H936-H943, doi:10.1149/1.3230624) — Rhodia Inc. 세리아 슬러리, 원문 명시 "mean diameter d_mean = 60 nm" (무첨가 |
| abrasive_d99_nm | 700.0 | nm | estimated | knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §2.2 | Hitachi US8439995B2 Example 1 D99(문헌 실측) — 화학종(세리아, STI/ILD 산화막 CMP) 일치를 근거로 기준점(baseline)에 이식. 팩의 실제 조성값 아님, what-if 스캔용 기준. |
| abrasive_ref_d99_nm | 700.0 | nm | estimated | knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §2.2 | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중계상 방지 |
| damage_exponent | 1.44 | - | literature | knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §3 | US8439995B2 4점 실측 로그-로그 회귀값(n=1.44, R²=0.997) — sim/factors.py 기본값(3.0, 문헌 근거 없는 가정값)보다 약 2배 완만. 세리아 화학종 한정(텅스텐/알루미나는 별도 검토 필요, egan-kim2019 n_temp=3.73· n_agit |
| oxide_nitride_selectivity | 60.0 | - | literature | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | Hwang 2024 실측 선택비 59~80 범위의 하단. 아미노산/계면활성제 첨가로 제어된다. ⚠ 엔진은 아직 이 값을 쓰지 않는다 — nitride 정지층 모델(film-nitride) 미구현. |
| ce3_fraction | 0.15 | - | literature | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 표면 Ce3+ 분율. 산소공공 x에 대해 전하균형 f=2x (노트 verify PASS). H2O2 0.5wt% 첨가 시 최대가 되며, 이때 oxide MRR이 상용 대비 5.5배로 보고됐다(Netzband & Dunn 2020). 이 값을 올리면 화학층이 MRR을 올린다. |
| ce3_fraction_ref | 0.15 | - | estimated | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 기준 조건(배수 1.0이 되는 지점). 여기서 Kp가 캘리브레이션돼 있다고 본다 |
| ceria_tooth_gain | 1.0 | - | unverified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | ⚠ Ce3+ 분율 → MRR 배수의 기울기. Netzband의 5.5배는 Ce3+ 외 다른 변수도 함께 움직인 결과라 그대로 쓸 수 없어 보수적으로 1.0(선형)을 놓았다. **문헌에 폐형식 함수가 없다 — 이 값이 캘리브레이션 1순위 대상이다.** |
| dispersant_type | NONE | - | estimated | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | oxide_silica 팩에서 상속된 경로이다. Li et al. 2021은 실리카 슬러리 실통이라 세리아(STI/SiC) 화학계로의 전이는 교차계 외삽이다(EVIDENCE-RULES E4) — 세리아 슬러리는 실제로 EAA 공중합제 분산제를 사용한다는 정직 기록이 slurry-comp |
| slurry_viscosity_pa_s | 0.0014 | Pa·s | literature | knowledge/materials/slurry-viscosity-rheology-literature-val | 세리아 CMP 슬러리 **실제** 점도. Kim et al. 2024 (Polymers 16(24) 3593, DOI 10.3390/polym16243593) §3.3 Fig.17d: 상용 세리아 슬러리 초기 실제 **1.41 cP** (25°C, Brookfield cone/plate |
| abrasive_ref_size_nm | 60.0 | nm | literature | 이 팩의 abrasive_size_nm 과 같은 출처 — 기준점은 독립 측정값이 아니라 '어느 조건에서 Kp | κ 입경항 기준점 — 이 팩의 abrasive_size_nm(60 nm)과 일치시킨다. 키가 없어 실리카 부모의 50 nm 를 상속해 기준조건 κ=1.275 였다 (2026-09-13 model_hygiene 극한검사가 검출). 값이 아니라 기준점만 옮기므로 예측 형상은 불변이고 배수만 |
| abrasive_size_peak_nm | 163.0 | nm | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 세리아 산화막 CMP 입경-MRR 정점. Oh, Singh, Gupta, Cho 2010 (Microelectronic Engineering, DOI 10.1016/j.mee.2010.07.040) — 수열합성 단결정 세리아 62/116/163/232 nm 4점 1축 스윕에서 163 n |
| abrasive_size_exp_below_peak | 1.3333333333 | dimensionless | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 정점 이하 구간 지수 = 압입 지배 d^(4/3). 값 자체는 부모(oxide_silica)와 같지만 **상속이 아니라 이 계에 대한 판단으로 재선언**한다 — 재료 특이 키를 상속시키면 부모가 바뀔 때 세리아 팩이 조용히 끌려간다(같은 결함이 wafer_iep_ph 에서도 발생했다). |
| abrasive_size_exp_above_peak | -0.3333333333 | dimensionless | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 정점 이상 구간 지수. 근거·한계는 abrasive_size_exp_below_peak 와 동일 (Bellahsene 2025 §2.1 표면적 지배 가지). 세리아 재추정 없음 — 미검증. |

### 팩 `w_fe_oxidizer`

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| film | w |  | verified |  |  |
| abrasive | alumina |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| kp_m_per_pa | 2.8e-13 | m^2/N | estimated | knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md | ⚠ 문헌 W MRR 범위(300~600 nm/min @ 3psi)에서 역산한 대표값. 미재현. W는 Fe(III)/H2O2 산화 후 기계적 제거라 산화막과 메커니즘이 다르다. |
| slurry_ph | 2.5 | pH | literature | knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md | 강산성 — Pourbaix상 W 산화물 용해 억제하며 부동태막 유지 |
| oxidizer | Fe(NO3)3 |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| oxidizer_wt_pct | 3.0 | wt% | literature | papers/US20110186542A1.txt | 이번 런의 H2O2 농도. Fe(III) 활성제와 공존하는 W 슬러리의 통상 상한 구간. |
| oxidizer_ref_wt_pct | 3.0 | wt% | literature | papers/US20110186542A1.txt | 기준 농도 — 화학 배수 1.0. 실시예 표의 최고 농도(3 wt%)를 기준으로 상대화했다. |
| oxidizer_peak_wt_pct | 6.0 | wt% | estimated | papers/US20110186542A1.txt | ⚠ 실측 3점(0/1/3 wt%)이 단조 증가라 정점을 직접 못 봤다. Kaufman 단봉을 0→1→3의 상대비(0.14/0.63/1.0)에 격자 적합해 얻은 값(n=3, log-err 0.012). 3 wt% 위는 외삽. |
| oxidizer_curve_n | 3.0 | - | estimated | papers/US20110186542A1.txt | 위와 같은 적합에서. 현상론 형상 파라미터. |
| oxidizer_mech_floor | 0.14 | - | literature | papers/US20110186542A1.txt | H2O2 0 wt%에서 남는 순수 기계 연마 분율(3 wt% 대비). 15조건 전부에서 0.117~0.189, 평균 0.142. Kaufman 단봉은 C=0에서 0이라 이 바닥이 없으면 산화제 0 예측이 0이 된다. |
| abrasive_size_nm | 50.0 | nm | literature | knowledge/cmp/w-cmp-abrasive-d50-bielmann1999-osti-cabot-con | Bielmann et al. 1999(ECS Solid-State Lett. 2(3) 148, DOI:10.1149/1.1390765) 실측 W CMP 폴리싱 슬러리의 γ-알루미나 1차입자경("primary size ~50 nm diam"). 원래 후보였던 OSTI 0.7μm(질산철 문 |
| abrasive_ref_size_nm | 50.0 | nm | literature | knowledge/cmp/w-cmp-abrasive-d50-bielmann1999-osti-cabot-con | κ 입경항 기준점 — abrasive_size_nm과 같은 값(cu_h2o2_bta의 abrasive_ref_size_nm 패턴과 동일). |
| abrasive_size_exponent | 0.0 | - | literature | knowledge/cmp/w-cmp-abrasive-size-null-result-egan-kim-2019. | **검증된 영(null) 결과** — cu_h2o2_bta와 독립적인 두 번째 계에서 확정. Egan & Kim 2019(ECS JSSTechnol. 8(5) P3206, DOI:10.1149/2.0311905jss, GLOBALFOUNDRIES W contact CMP 실제 양산 데이 |
| abrasive_wt_pct | 10.0 | wt% | literature | knowledge/cmp/kappa-abrasive-concentration-cu-w-cooper-bielm | Bielmann et al. 1999(같은 논문·같은 문장, 위 abrasive_size_nm과 동일 출처) — "The polishing slurries contained 10 wt % γ-alumina particles". 입경과 농도를 같은 실험·같은 문장에서 동시 확보해 내적 정 |
| abrasive_ref_wt_pct | 10.0 | wt% | literature | knowledge/cmp/kappa-abrasive-concentration-cu-w-cooper-bielm | κ 농도항 기준점 — 이 실험 조건 자체(Bielmann 1999)를 기준으로 잡아 κ=1.0 계약 유지 |
| abrasive_conc_exponent | 0.3333 | - | literature | knowledge/cmp/kappa-abrasive-concentration-cu-w-cooper-bielm | Wang et al. 2012(ECS Trans. 41(43) 103-111, DOI:10.1149/1.4717508, Applied Materials Reflexion GT 실제 W CMP 실험)이 W 계에서 **직접** "the removal rate was observed to s |
| abrasive_d99_nm | 750.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | abrasive_size_nm(150 nm) × D99/D50 일반비 5.00 유도값(Silco/Levitronix 2008). Showa Denko US6770218B2(알루미나 + 질산철 3.5wt% 텅스텐 CMP) 절대 상한 1.0 µm 이내, 단 선호 상한 0.5 µm는 초과 ⚠ |
| abrasive_ref_d99_nm | 750.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지 |
| damage_exponent | 2.54 | - | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | Egan & Kim 2019(ECS JSS 8(5) P3206) 두 관측의 기하평균 √(3.73×1.73). 막질·공정 완전 일치(텅스텐 벌크 CMP, 300mm 양산 라인 defect inspection 실측). ⚠ 각 관측이 n=1 단일 대응쌍이고 저자 서술이 반올림("sixty t |
| inhibitor | picolinic_acid |  | literature | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol |  |
| inhibitor_mM | 121.8 | mM | estimated | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 1.5 wt% 피콜린산(포화 농도, 밀도 1 g/mL 근사)에 해당하는 몰농도. 원문 Lee & Seo(2022) 3.3절에서 정지식각 90->11 A/min(8.2배 감소), CMP 제거율 120->85 A/min(1.41배 감소)의 실측 포인트. wt%->mol/L 환산은 밀도 근사 |
| inhibitor_K_L_per_mol | 1108.0 | L/mol | literature | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 원문 Table 1 Langmuir 상수 b=0.009 L/mg를 MW=123.11 g/mol로 몰단위 환산. 노트 verify 블록 PASS(K=1108 L/mol). |
| inhibitor_ref_mM | 121.8 | mM | estimated | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 기준 농도 = inhibitor_mM과 동일(1.5 wt% 포화점). 여기서 화학 배수 1.0, 이 팩의 kp_m_per_pa는 이 농도 근처(원 특허 실시예)에서 역산된 값이라 이중계상 방지를 위해 일치시켰다. |
| inhibitor_strength_k | 2.117 | - | unverified | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 정지식각 90->11 A/min(8.2배 감소) 역산값. Cu/BTA의 k=3.0(cu_h2o2_bta.yaml)과 다른 화학종 전용 값 — 물질계별로 별도 파라미터가 필요함을 보여준다. 노트 verify PASS. 0.5wt%에서 모델은 이미 강한 억제를 예측하나 원문은 "억제 실패" |
| film_bulk_hardness_pa | 12000000000.0 | Pa | literature | Nanoindentation of CVD W films — 보고 범위 10~14 GPa | CVD 텅스텐막의 나노압입 경도. ⚠ 이것은 **벌크** 경도이지 CMP 가 실제로 깎는 화학 변질층의 경도가 아니다. 변질층 경도의 절대값은 공개 문헌에 없다(_knowledge_audit/mechanics.md 의 최대 병목). 다만 변질층은 벌크보다 무르므로 H_surface ≤  |

## 검증 (특허·논문 held-out)

| 팩 | 데이터셋 | 유의 | 유의 평균 ρ |
|---|---|---|---|
| cu_h2o2_bta | 5 | 2 | 0.8587 |
| oxide_silica | 6 | 2 | 0.996 |
| sic_ceria_h2o2 | 2 | 1 | 1.0 |
| sti_ceria | 5 | 2 | 0.95 |
| w_fe_oxidizer | 2 | 1 | 1.0 |

## 미충족 항목

- C2 Γ gamma/cu_h2o2_bta: confidence=estimated
- C2 Γ gamma/oxide_silica: confidence=estimated
- C2 Γ gamma/sic_ceria_h2o2: confidence=estimated
- C2 Γ gamma/sti_ceria: confidence=estimated
- C2 Γ gamma/w_fe_oxidizer: confidence=estimated
- C2 χ chi/cu_h2o2_bta: confidence=unverified
- C2 χ chi/sic_ceria_h2o2: confidence=unverified
- C2 χ chi/sti_ceria: confidence=unverified
- C2 χ chi/w_fe_oxidizer: confidence=estimated
- C2 ψ psi/cu_h2o2_bta: confidence=unverified
- C2 ψ psi/sic_ceria_h2o2: confidence=estimated
- C2 ψ psi/sti_ceria: confidence=estimated
- C2 ψ psi/w_fe_oxidizer: confidence=unverified
- C2 τ tau/cu_h2o2_bta: confidence=unverified
- C2 τ tau/oxide_silica: confidence=unverified
- C2 τ tau/sic_ceria_h2o2: confidence=unverified
- C2 τ tau/sti_ceria: confidence=unverified
- C2 τ tau/w_fe_oxidizer: confidence=unverified
- C2 Δ delta/cu_h2o2_bta: confidence=estimated
- C2 Δ delta/sic_ceria_h2o2: confidence=estimated
- C2 Δ delta/sti_ceria: confidence=estimated
- C2 S stab/cu_h2o2_bta: confidence=estimated
- C2 S stab/sic_ceria_h2o2: confidence=estimated
- C2 S stab/sti_ceria: confidence=estimated
- C2 S stab/w_fe_oxidizer: confidence=estimated