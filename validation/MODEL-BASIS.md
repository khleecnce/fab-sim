# FabSim 모델 근거 보고서 (MODEL-BASIS)

생성: 2026-09-11 13:31 · 커밋 기준 자동 생성 — 손으로 고치지 말고 코드/팩/노트를 고쳐라.

완성 판정: **미완** (12/50칸). 미충족 39건은 끝에.

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

발열은 Λ에 비례하고(마찰일률), 냉각·공급은 SFR에 비례한다.
온도는 Arrhenius로 화학속도를, 유량은 신선 슬러리 공급을 지배한다.

⚠ 절대 온도가 아니라 **기준 대비 부하비**다. 실제 ΔT 예측은
knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md 의
모델이 담당하고, 여기서는 팩터로 압축만 한다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | partial | estimated | heat(Λ)×1.000, cool(SFR)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s |
| oxide_silica | partial | estimated | heat(Λ)×1.000, cool(SFR)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s |
| sic_ceria_h2o2 | partial | estimated | heat(Λ)×1.000, cool(SFR)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s |
| sti_ceria | partial | estimated | heat(Λ)×1.000, cool(SFR)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s |
| w_fe_oxidizer | partial | estimated | heat(Λ)×1.000, cool(SFR)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s |

엔진이 스스로 보고하는 한계:

- ⚠ 발열/냉각을 1차 비례로 압축했다 — 실제 열저항·체류시간은 미반영. 절대 ΔT는 별도 열모델이 담당한다.

근거 노트(verify 블록 보유): `knowledge/equipment/cmp-rpm-ratio-flowrate-temperature-mrr-stability.md`, `knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md`


## Γ 컨디셔닝 부하 (`gamma`) — 축: equipment · 파트: tool · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Γ 컨디셔닝 부하 — 디스크가 패드에 가하는 단위시간 절삭일.

⚠ 여기는 **장비 설정**(하중·스윕·duty)만 담는다. 디스크의 형상(그릿 밀도·
돌출)은 소모품이므로 κ/τ 쪽으로 간다. 이 분리를 지켜야 "디스크를 바꿀까
컨디셔너 세팅을 바꿀까"에 답할 수 있다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | modeled | estimated | force×1.000, sweep×1.000, duty×1.000 | cond_downforce_lbf, cond_sweep_cpm, cond_duty_pct | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |
| oxide_silica | modeled | estimated | force×1.000, sweep×1.000, duty×1.000 | cond_downforce_lbf, cond_sweep_cpm, cond_duty_pct | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |
| sic_ceria_h2o2 | modeled | estimated | force×1.000, sweep×1.000, duty×1.000 | cond_downforce_lbf, cond_sweep_cpm, cond_duty_pct | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |
| sti_ceria | modeled | estimated | force×1.000, sweep×1.000, duty×1.000 | cond_downforce_lbf, cond_sweep_cpm, cond_duty_pct | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |
| w_fe_oxidizer | modeled | estimated | force×1.000, sweep×1.000, duty×1.000 | cond_downforce_lbf, cond_sweep_cpm, cond_duty_pct | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md |

엔진이 스스로 보고하는 한계:

- ⚠ force×sweep×duty 곱 형태는 절삭일률의 1차 근사다 — 임계하중(critical downforce) 아래에서는 절삭이 안 일어난다는 비선형이 미반영. disk-conditioner 노트 참조.

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
| cu_h2o2_bta | partial | estimated | size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-size-null-result-force-partitio; pad-hardness-porosity-measurement-method; gw-contact.md |
| oxide_silica | partial | estimated | conc×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-size-concentration-ph-K-additiv; pad-hardness-porosity-measurement-method; gw-contact.md |
| sic_ceria_h2o2 | partial | estimated | conc×1.710, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-size-concentration-ph-K-additiv; pad-hardness-porosity-measurement-method; gw-contact.md |
| sti_ceria | partial | estimated | conc×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-size-concentration-ph-K-additiv; pad-hardness-porosity-measurement-method; gw-contact.md |
| w_fe_oxidizer | partial | estimated | pad_hardness×1.000, asperity×1.000 | abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | pad-hardness-porosity-measurement-method; gw-contact.md |

엔진이 스스로 보고하는 한계:

- ⚠ Shore D는 경도의 대리지표다. H^-1.5의 H는 압입경도(GPa)인데 Shore D↔GPa 환산이 비선형이라 순위는 맞아도 절대값은 캘리브레이션이 필요하다.
- ⚠ asperity 밀도 지수 0.5는 GW 접촉에서 실접촉면적이 밀도의 제곱근에 가깝게 증가한다는 근사다 — 미검증.
- ⚠ 농도 지수 n=0.333 — 문헌은 1/3(표면적)~4/3(압입) 두 극한만 제시하고 어느 쪽인지 정하지 않았다. 순위는 신뢰, 크기는 캘리브레이션 대상.
- ⚠ 부분 모델링 — 반영된 항 2/4: pad_hardness, asperity
- ⚠ 부분 모델링 — 반영된 항 3/4: conc, pad_hardness, asperity
- ⚠ 부분 모델링 — 반영된 항 3/4: size, pad_hardness, asperity
- ⚠ 입경 항 미적용: 지수(abrasive_size_exponent)가 팩에 없다. 문헌은 정점형(~80nm 최대)이라고만 서술하고 지수를 확정하지 못했으므로 임의값을 쓰지 않는다 — 입경을 바꿔도 κ가 변하지 않는다는 뜻이다. 단조 지수를 넣으면 정점 거동을 놓친다.
- ⚠ 입자 함량 20 wt%가 포화농도 7 wt%를 넘었다 — 실제로는 더 넣어도 MRR이 안 오른다(Luo-Dornfeld 포화영역). 현재 항은 계속 증가시키므로 이 구간 예측은 과대평가다.

근거 노트(verify 블록 보유): `knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md`, `knowledge/cmp/abrasive-size-null-result-force-partition-theory.md`, `knowledge/materials/pad-hardness-porosity-measurement-methods.md`


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
| cu_h2o2_bta | partial | estimated | oxidizer×1.000 | oxidizer_wt_pct, slurry_ph | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| oxide_silica | partial | estimated | ph_peak×1.000 | slurry_ph | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| sic_ceria_h2o2 | modeled | estimated | ceria_tooth×1.000, ph_ceria_window×0.187 | slurry_ph, ce3_fraction | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| sti_ceria | modeled | estimated | ceria_tooth×1.000, ph_ceria_window×1.000 | slurry_ph, ce3_fraction | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| w_fe_oxidizer | partial | estimated | oxidizer×1.000 | oxidizer_wt_pct, slurry_ph | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |

엔진이 스스로 보고하는 한계:

- pH 10.5 (정점 11, 기준 10.5) → 상대 1.000. 실측 3점(Li 2021 Fig.1) 기반 정점형(pH≳9.0), 산성(pH≤6)은 골 형태 로그이차(cn109609035b n=7, 반등 포함 피팅). ⚠ 염기 정점식은 3점을 지나는 최소 가정, 산성 골 로그이차는 n=7 피팅 — 둘 다 문헌 폐형식은 아니다. ⚠ 6~9 전환구간은 데이터 없어 로그-선형 보간(미검증 외삽).
- ⚠ R/R booster(glycine 등)가 팩에 없다 — 막질별 선택비를 만드는 주요 축인데 통로가 없다. 담당 R2-slurry.
- ⚠ pH 10는 세리아 IEP(6.8) 근접 — 제타≈0, 응집·스크래치 위험(Δ↑). 분산제 없이는 실무 부적합.
- ⚠ 화학 항들을 독립으로 보고 곱했다 — pH-흡착, 산화제-세리아 산화환원 커플링은 미모델링.
- 세리아 chemical tooth: Ce³⁺ 분율 0.150 (기준 0.150). ⚠ Ce³⁺–MRR 함수형은 문헌에 폐형식이 없어 선형 비례로 가정했다 — 미검증.
- 세리아 정전 창: pH 10 (창 2.5~6.8, 기준 5.5) → 상대 0.187. 창 안에서 세리아(+)·실리카(−) 인력, 밖에서 반발. ⚠ 창 위치는 IEP 물리, 기울기·잔류율은 Dandu 2009 실측 역산 — 미검증.
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
| cu_h2o2_bta | partial | unverified | groove_eta×1.000, porosity×1.000 | groove_depth_mm, groove_pitch_mm, groove_width_um, pad_porosity_pct | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |
| oxide_silica | partial | unverified | groove_eta×1.000, porosity×1.000 | groove_depth_mm, groove_pitch_mm, groove_width_um, pad_porosity_pct, slurry_viscosity_pa_s | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |
| sic_ceria_h2o2 | partial | unverified | groove_eta×1.000, porosity×1.000 | groove_depth_mm, groove_pitch_mm, groove_width_um, pad_porosity_pct, slurry_viscosity_pa_s | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |
| sti_ceria | partial | unverified | groove_eta×1.000, porosity×1.000 | groove_depth_mm, groove_pitch_mm, groove_width_um, pad_porosity_pct, slurry_viscosity_pa_s | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |
| w_fe_oxidizer | partial | unverified | groove_eta×1.000, porosity×1.000 | groove_depth_mm, groove_pitch_mm, groove_width_um, pad_porosity_pct | pad-groove-geometry-contact-area-flow-re; pad-porosity-slurry-transport-mrr.md §5 |

엔진이 스스로 보고하는 한계:

- ⚠ τ 등급=unverified: 드라이버(기공률·그루브폭·점도)는 literature 등급이지만 τ의 **결합 지수**(tau_mrr_exponent=0.07)가 기공률 실험에서 역산해 그루브 축에 교차 대입한 값이라 크기를 문헌이 보증하지 않는다 — 가장 약한 고리가 등급을 정한다. 순위만 신뢰하라.
- ⚠ τ가 실제로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다. 기공 2 µm 패드에서 중심이 슬러리 기아로 처지고 엣지-중심 RR 차이가 200 nm/min을 넘었다(Prasad 2013 III.D.2). 이 프로파일 결합은 미구현 — 담당 R3-pad × R2-slurry.
- 그루브 폭 600 µm → 슬러리 이용효율 η=13.4% (기준 600 µm, η=13.4%). ⚠ η는 600 µm 부근에서 정체·반전한다 — 넓힐수록 좋지 않다(Mu 2016 Table 3 실측).
- 기공률 30% (기준 30%). ⚠ 실측상 기공률 15→45%(3배)에도 RR은 8%만 올랐다 — 비례 가정은 기각됐다(Prasad 2013). 지수 0.07은 그 8%에서 역산한 값이다.

근거 노트(verify 블록 보유): `knowledge/materials/pad-groove-geometry-contact-area-flow-resistance.md`, `knowledge/materials/pad-porosity-slurry-transport-mrr.md`


## Δ 손상 유발도 (`delta`) — 축: consumable · 파트: slurry, pad, disk · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Δ 손상 유발도 — 스크래치·결함 발생 경향.

대입자 tail(D99)이 지배한다. 평균 입경이 아니라 **꼬리**가 스크래치를 만든다.
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | partial | unverified | d99×1.000 | abrasive_d99_nm, abrasive_size_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md |
| oxide_silica | partial | unverified | d99×1.000 | abrasive_d99_nm, abrasive_size_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md |
| sic_ceria_h2o2 | partial | unverified | d99×1.000 | abrasive_d99_nm, abrasive_size_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md |
| sti_ceria | partial | unverified | d99×1.000 | abrasive_d99_nm, abrasive_size_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md |
| w_fe_oxidizer | partial | unverified | d99×1.000 | abrasive_d99_nm, abrasive_size_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md |

엔진이 스스로 보고하는 한계:

- ⚠ 손상 지수 n=1.44는 문헌 폐형식이 없어 팩에서 받는 가정값이다. 순위(큰 입자가 더 긁는다)만 신뢰하고 절대값은 쓰지 마라. ⚠ n=3.0 기본값은 US8439995B2(Hitachi, 세리아 D99-스크래치 4점 실측) 회귀값 n≈1.44(R²=0.997)보다 약 2배 가파르다 — knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §3. 교차확증: lpc-scratch-density-tail-correlation.md(Remsen 2006, fumed silica)도 선형(n≈1 근방)을 지지 — n=3.0이 과대추정일 가능성. 표본이 작아(세리아 1개 화학종, 실질 독립 3점) 기본값을 즉시 교체하지 않았다(구현 요청으로 PROFILE.md에 기록).
- ⚠ 손상 지수 n=2.54는 문헌 폐형식이 없어 팩에서 받는 가정값이다. 순위(큰 입자가 더 긁는다)만 신뢰하고 절대값은 쓰지 마라. ⚠ n=3.0 기본값은 US8439995B2(Hitachi, 세리아 D99-스크래치 4점 실측) 회귀값 n≈1.44(R²=0.997)보다 약 2배 가파르다 — knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §3. 교차확증: lpc-scratch-density-tail-correlation.md(Remsen 2006, fumed silica)도 선형(n≈1 근방)을 지지 — n=3.0이 과대추정일 가능성. 표본이 작아(세리아 1개 화학종, 실질 독립 3점) 기본값을 즉시 교체하지 않았다(구현 요청으로 PROFILE.md에 기록).

근거 노트(verify 블록 보유): `knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md`, `knowledge/cmp/lpc-scratch-density-tail-correlation.md`


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
```

### 팩별 상태

| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta | partial | estimated | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |
| oxide_silica | partial | literature | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |
| sic_ceria_h2o2 | partial | estimated | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |
| sti_ceria | partial | estimated | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |
| w_fe_oxidizer | partial | estimated | time_min_log_decay×1.000 | time_s | ma17081817 (PMC11051262) Fig.9; pad-glazing-mechanism-mrr-decay.md |

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
| abrasive_size_nm | 100.0 | nm | estimated | knowledge/cmp/particle-wafer-interaction-mechanical-chemical |  |
| abrasive_size_exponent | 0.0 | - | literature | knowledge/cmp/abrasive-size-null-result-force-partition-theo | **검증된 영(null) 결과 — "모름"이 아니라 "효과 없음"이다.** EVIDENCE-RULES.md 판정 #1 (2026-09-11)로 확정. 5회차 순환하던 RESPONSE_DEAD를 종결한다. 충돌: Bai 2007(Appl.Surf.Sci. 253, 8489) 폐형식 유도는 |
| abrasive_d99_nm | 500.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | abrasive_size_nm(100 nm) × D99/D50 일반비 5.00 유도값(Silco/Levitronix 2008). 독립 상한 대조: Showa Denko US6770218B2(알루미나 + 질산철 금속 CMP, W·Cu 동일 슬러리) 명세 "maximum grain size |
| abrasive_ref_d99_nm | 500.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지 |
| damage_exponent | 2.54 | - | estimated | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | Egan & Kim 2019(ECS JSS 8(5) P3206, GLOBALFOUNDRIES 300mm 양산) 두 관측 n_temp=3.73 / n_agit=1.73의 기하평균(로그축 중앙). ⚠ 원 관측은 **텅스텐** 벌크 CMP다 — Cu로의 전이는 연마입자·촉매 계열 유사성(Sh |
| dishing_sensitivity | 1.0 | - | unverified | knowledge/cmp/pattern-dependent-dishing-erosion.md | ⚠ 미연결. dishing 정량에는 금속:산화막 MRR 비가 필요한데 아직 두 팩을 동시에 로드하는 다막질 모델이 없다(film-cu 에이전트 대기). |

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
| abrasive_conc_exponent | 0.3333 | - | unverified | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | R ∝ C0^(1/3) 표면적 지배 극한. 논문은 1/3(표면적)과 4/3(압입) 두 극한을 제시하고 어느 쪽인지 확정하지 않았다 — 보수적으로 낮은 쪽을 기본값으로 둔다. ⚠ 순위(농도↑→MRR↑)만 문헌이 직접 서술·검증했다. 크기는 캘리브레이션 대상. |
| abrasive_saturation_wt_pct | 7.0 | wt% | literature | knowledge/materials/pad-3dprinted-nonporous-lowdefect-review | Luo-Dornfeld 포화영역 — 퓸드 실리카 12 wt% 계에서 7 wt% 이상 RR 불변 확인. 이 위로는 농도항이 과대평가된다(factors.py가 경고를 띄운다). |
| abrasive_ref_size_nm | 50.0 | nm | literature | knowledge/cmp/particle-wafer-interaction-mechanical-chemical | κ 입경항 기준점 — abrasive_size_nm과 같은 값 |
| ph_peak | 11.0 | pH | verified | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | MRR 최대 pH (20 wt% 실리카, K+ 0.25 M, SiO2 막). 정점형 거동 |
| ph_ref | 10.5 | pH | literature | knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md | χ pH항 기준점 — 이 팩의 slurry_ph와 같은 값 |
| ph_mrr_at_peak_rel | 1.113 | - | verified | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | pH 10.0 대비 pH 11.0의 MRR 비 (1727/1551 = 1.113, +11.3%). 노트 verify 블록이 이 값을 assert한다. |
| abrasive_d99_nm | 250.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | abrasive_size_nm(50 nm) × D99/D50 일반비 5.00 유도값. 일반비 출처는 Silco/Levitronix CMP Users Conference 2008 슬라이드 p.11(3세대 관측 4.29~5.00, 중앙값 5.00, 산업 컨퍼런스 2차 자료). 오더 대조:  |
| abrasive_ref_d99_nm | 250.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지 |
| damage_exponent | 1.44 | - | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | US8439995B2(Hitachi 세리아) 4점 로그-로그 회귀 n=1.444, R²=0.997. 막질 일치 (산화막 CMP)이나 연마입자 불일치(세리아 vs 콜로이달 실리카) — 조건 외삽. 교차확증: Remsen 2006(퓸드실리카·산화막) Table V가 선형(n≈1)을 지지해  |
| slurry_viscosity_pa_s | 0.001 | Pa·s | literature | knowledge/materials/slurry-viscosity-rheology-literature-val | 콜로이달 실리카 CMP 슬러리 **실측** 점도. Lee et al. 2025 (Nanomaterials 15(16) 1248, DOI 10.3390/nano15161248, OA) Brookfield DV-II+Pro: 첨가제 무관 기본 슬러리 ~0.98 cP (§3.2 Fig.3a) |
| pad_ra_m | 5e-06 | m | estimated | knowledge/physics/cmp-lubrication-regimes.md §5 | 패드 raised 영역 평균거칠기 — 노트는 "~5µm 전형"으로만 명시 |
| dispersant_type | NONE | - | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | Li et al. 2021 §6의 기준 MRR(2700 Å/min, 무첨가)과 이 팩의 기준 조성을 일치시킨다 — 팩 기본값에서 ψ=1.0이 되어 이중 계상을 피한다. PVA(-3.6%), PVP(-7.9%)는 같은 논문 실측값이며 레시피 오버라이드로 스캔한다. |

### 팩 `sic_ceria_h2o2`

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| film | sic_4h |  | measured | Wang et al. ACS SI Table S3 — 4H-SiC 웨이퍼 |  |
| abrasive | ceria |  | measured | Wang et al. ACS SI Table S3 — CeO2 연마입자 |  |
| slurry_ph | 10.0 |  | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (pH 9/10/11) |  |
| ph_softening_ref | 10.0 |  | measured | Wang et al. ACS SI Table S3 — DOE 중심값을 기준으로 잡는다 |  |
| ph_softening_per_unit | 0.2787 |  | measured | Wang et al. ACS SI Table S3 50조건 역산 (pH만 다른 9조/12쌍, 배수 1.633 |  |
| abrasive_ref_wt_pct | 4.0 |  | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (CeO2 2/4/6 wt%) |  |
| oxidizer_ref_wt_pct | 4.0 |  | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (H2O2 2/4/6 vol%) |  |
| dispersant_type | NONE | - | estimated | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | oxide_silica 팩에서 상속된 경로이다. Li et al. 2021은 실리카 슬러리 실통이라 세리아(STI/SiC) 화학계로의 전이는 교차계 외삽이다(EVIDENCE-RULES E4) — 세리아 슬러리는 실제로 EAA 공중합제 분산제를 사용한다는 정직 기록이 slurry-comp |
| slurry_viscosity_pa_s | 0.0014 | Pa·s | literature | knowledge/materials/slurry-viscosity-rheology-literature-val | 세리아 슬러리 실제 점도(sti_ceria와 동일 근거: Kim 2024 DOI 10.3390/polym16243593 §3.3 Fig.17d 상용 세리아 1.41 cP, 25°C). ⚠ H2O2 추가 세리아 슬러리의 점도를 **직접 재는 문헌은 미확보**다. H2O2는 저농도 수용액이 |

### 팩 `sti_ceria`

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| abrasive | ceria |  | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md |  |
| kp_m_per_pa | 2.2e-13 | m^2/N | estimated | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | ⚠ 세리아는 화학결합(Si-O-Ce) 기반이라 실리카보다 산화막 MRR이 높다. Netzband 2020에서 H2O2 첨가 시 Ce3+ 증가로 MRR 5.5배 변화가 보고됐는데, 그건 조성 의존이라 단일 상수로 뭉뚱그린 이 값은 대표값일 뿐이다. 미재현. |
| slurry_ph | 5.5 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 세리아 IEP 6.8 부근 아래 — 약양전하로 실리카 표면(음전하) 정전인력 |
| abrasive_iep_ph | 6.8 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md |  |
| ph_ref | 5.5 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §4 | 세리아 정전 창(2.5~6.8) 안의 기준점 — slurry_ph와 같은 값 |
| wafer_iep_ph | 2.5 | pH | literature | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §4 | 실리카 산화막 표면 IEP. 정전 창의 하단. 2차 인용 범위(2~3) |
| abrasive_size_nm | 80.0 | nm | estimated | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md |  |
| abrasive_d99_nm | 700.0 | nm | estimated | knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §2.2 | Hitachi US8439995B2 Example 1 D99(문헌 실측) — 화학종(세리아, STI/ILD 산화막 CMP) 일치를 근거로 기준점(baseline)에 이식. 팩의 실제 조성값 아님, what-if 스캔용 기준. |
| abrasive_ref_d99_nm | 700.0 | nm | estimated | knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §2.2 | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중계상 방지 |
| damage_exponent | 1.44 | - | literature | knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §3 | US8439995B2 4점 실측 로그-로그 회귀값(n=1.44, R²=0.997) — sim/factors.py 기본값(3.0, 문헌 근거 없는 가정값)보다 약 2배 완만. 세리아 화학종 한정(텅스텐/알루미나는 별도 검토 필요, egan-kim2019 n_temp=3.73· n_agit |
| oxide_nitride_selectivity | 60.0 | - | literature | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | Hwang 2024 실측 선택비 59~80 범위의 하단. 아미노산/계면활성제 첨가로 제어된다. ⚠ 엔진은 아직 이 값을 쓰지 않는다 — nitride 정지층 모델(film-nitride) 미구현. |
| ce3_fraction | 0.15 | - | literature | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 표면 Ce3+ 분율. 산소공공 x에 대해 전하균형 f=2x (노트 verify PASS). H2O2 0.5wt% 첨가 시 최대가 되며, 이때 oxide MRR이 상용 대비 5.5배로 보고됐다(Netzband & Dunn 2020). 이 값을 올리면 화학층이 MRR을 올린다. |
| ce3_fraction_ref | 0.15 | - | estimated | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 기준 조건(배수 1.0이 되는 지점). 여기서 Kp가 캘리브레이션돼 있다고 본다 |
| ceria_tooth_gain | 1.0 | - | unverified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | ⚠ Ce3+ 분율 → MRR 배수의 기울기. Netzband의 5.5배는 Ce3+ 외 다른 변수도 함께 움직인 결과라 그대로 쓸 수 없어 보수적으로 1.0(선형)을 놓았다. **문헌에 폐형식 함수가 없다 — 이 값이 캘리브레이션 1순위 대상이다.** |
| dispersant_type | NONE | - | estimated | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | oxide_silica 팩에서 상속된 경로이다. Li et al. 2021은 실리카 슬러리 실통이라 세리아(STI/SiC) 화학계로의 전이는 교차계 외삽이다(EVIDENCE-RULES E4) — 세리아 슬러리는 실제로 EAA 공중합제 분산제를 사용한다는 정직 기록이 slurry-comp |
| slurry_viscosity_pa_s | 0.0014 | Pa·s | literature | knowledge/materials/slurry-viscosity-rheology-literature-val | 세리아 CMP 슬러리 **실제** 점도. Kim et al. 2024 (Polymers 16(24) 3593, DOI 10.3390/polym16243593) §3.3 Fig.17d: 상용 세리아 슬러리 초기 실제 **1.41 cP** (25°C, Brookfield cone/plate |

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
| abrasive_size_nm | 150.0 | nm | estimated | knowledge/cmp/particle-wafer-interaction-mechanical-chemical |  |
| abrasive_d99_nm | 750.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | abrasive_size_nm(150 nm) × D99/D50 일반비 5.00 유도값(Silco/Levitronix 2008). Showa Denko US6770218B2(알루미나 + 질산철 3.5wt% 텅스텐 CMP) 절대 상한 1.0 µm 이내, 단 선호 상한 0.5 µm는 초과 ⚠ |
| abrasive_ref_d99_nm | 750.0 | nm | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지 |
| damage_exponent | 2.54 | - | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | Egan & Kim 2019(ECS JSS 8(5) P3206) 두 관측의 기하평균 √(3.73×1.73). 막질·공정 완전 일치(텅스텐 벌크 CMP, 300mm 양산 라인 defect inspection 실측). ⚠ 각 관측이 n=1 단일 대응쌍이고 저자 서술이 반올림("sixty t |
| inhibitor | picolinic_acid |  | literature | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol |  |
| inhibitor_mM | 121.8 | mM | estimated | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 1.5 wt% 피콜린산(포화 농도, 밀도 1 g/mL 근사)에 해당하는 몰농도. 원문 Lee & Seo(2022) 3.3절에서 정지식각 90->11 A/min(8.2배 감소), CMP 제거율 120->85 A/min(1.41배 감소)의 실측 포인트. wt%->mol/L 환산은 밀도 근사 |
| inhibitor_K_L_per_mol | 1108.0 | L/mol | literature | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 원문 Table 1 Langmuir 상수 b=0.009 L/mg를 MW=123.11 g/mol로 몰단위 환산. 노트 verify 블록 PASS(K=1108 L/mol). |
| inhibitor_ref_mM | 121.8 | mM | estimated | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 기준 농도 = inhibitor_mM과 동일(1.5 wt% 포화점). 여기서 화학 배수 1.0, 이 팩의 kp_m_per_pa는 이 농도 근처(원 특허 실시예)에서 역산된 값이라 이중계상 방지를 위해 일치시켰다. |
| inhibitor_strength_k | 2.117 | - | unverified | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 정지식각 90->11 A/min(8.2배 감소) 역산값. Cu/BTA의 k=3.0(cu_h2o2_bta.yaml)과 다른 화학종 전용 값 — 물질계별로 별도 파라미터가 필요함을 보여준다. 노트 verify PASS. 0.5wt%에서 모델은 이미 강한 억제를 예측하나 원문은 "억제 실패" |

## 검증 (특허·논문 held-out)

| 팩 | 데이터셋 | 유의 | 유의 평균 ρ |
|---|---|---|---|
| cu_h2o2_bta | 5 | 2 | 0.8587 |
| oxide_silica | 6 | 2 | 0.996 |
| sic_ceria_h2o2 | 2 | 0 | None |
| sti_ceria | 5 | 2 | 0.95 |
| w_fe_oxidizer | 2 | 1 | 1.0 |

## 미충족 항목

- C2 Θ theta/cu_h2o2_bta: confidence=estimated
- C2 Θ theta/oxide_silica: confidence=estimated
- C2 Θ theta/sic_ceria_h2o2: confidence=estimated
- C2 Θ theta/sti_ceria: confidence=estimated
- C2 Θ theta/w_fe_oxidizer: confidence=estimated
- C2 Γ gamma/cu_h2o2_bta: confidence=estimated
- C2 Γ gamma/oxide_silica: confidence=estimated
- C2 Γ gamma/sic_ceria_h2o2: confidence=estimated
- C2 Γ gamma/sti_ceria: confidence=estimated
- C2 Γ gamma/w_fe_oxidizer: confidence=estimated
- C2 κ kappa/cu_h2o2_bta: confidence=estimated
- C2 κ kappa/oxide_silica: confidence=estimated
- C2 κ kappa/sic_ceria_h2o2: confidence=estimated
- C2 κ kappa/sti_ceria: confidence=estimated
- C2 κ kappa/w_fe_oxidizer: confidence=estimated
- C2 χ chi/cu_h2o2_bta: confidence=estimated
- C2 χ chi/oxide_silica: confidence=estimated
- C2 χ chi/sic_ceria_h2o2: confidence=estimated
- C2 χ chi/sti_ceria: confidence=estimated
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
- C2 Δ delta/cu_h2o2_bta: confidence=unverified
- C2 Δ delta/oxide_silica: confidence=unverified
- C2 Δ delta/sic_ceria_h2o2: confidence=unverified
- C2 Δ delta/sti_ceria: confidence=unverified
- C2 Δ delta/w_fe_oxidizer: confidence=unverified
- C2 S stab/cu_h2o2_bta: confidence=estimated
- C2 S stab/sic_ceria_h2o2: confidence=estimated
- C2 S stab/sti_ceria: confidence=estimated
- C2 S stab/w_fe_oxidizer: confidence=estimated
- C4 sic_ceria_h2o2: 유의 held-out 0건