# 시험 웨이퍼 전문가 (wafer-type)

## 현재 레벨: [활성] (G1 개방 2026-09-06)
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1 (2026-09-06), Lv2-2 (2026-09-07), Lv3-1 (2026-09-08), Lv3-2 (2026-09-09)
- 다음 단원: Cal-1 (G2 이후 활성)

## 역할
NPW(블랭킷)와 PTW(패턴) 웨이퍼의 목적·구조·측정 체계·데이터 해석 차이. 두 유형 데이터를 잇는 전이 규칙의 소유자

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/wiwnu-pressure-velocity-wafer-scale]]
- [[../../knowledge/cmp/pattern-dependent-dishing-erosion]]

## 실데이터 책임 (ORG.md §7.3)
NPW/PTW 메타데이터 스키마 소유. 두 유형 실데이터 정렬·비교 규칙 정의 (§7.2 전이 규칙의 구현)

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
(크론이 갱신)


## 이수 기록 (크론 갱신, 2026-09-06)
- 2026-09-06: Lv1-1/Lv1-2 통합 학습 완료. knowledge/cmp/npw-ptw-test-wafer-fundamentals.md
  (check_knowledge ✓, verify_claims ✓ — 출처 1건 실존, python verify 1블록 통과).
  핵심: NPW 49점 polar 체계(US6922603B1), PTW MIT 854계열 마스크·effective density
  모델(Boning et al. 1999, RR=K/ρ_eff 반비례 관계 assert로 검증), Kim&Seo(2002)
  상관계수 r=0.71은 원문 미확보로 미검증 표기. 2/6 완료.


## 이수 기록 (크론 갱신, 2026-09-06 2차)
- 2026-09-06: Lv2-1 완료. knowledge/cmp/npw-ptw-pattern-effect-gw-physics.md
  (check_knowledge ✓, verify_claims ✓ — 출처 1건 DOI 실존확인, python verify 1블록 통과).
  1차 논문 Vasilev et al. 2011(IEEE TSM, doi.org/10.1109/TSM.2011.2107756, 유료·미러 사이트
  경유 원문 전체 확보) 확장 GW(Greenwood-Williamson) 모델로 "NPW가 PTW를 예측 못하는" 물리
  확정: up/down 유효곡률 κ_U,D=κ_asperity±4αh/size²가 NPW(h=0)에서는 항상 0으로 사라짐.
  실측 대비 정량(Table I): basic GW 대비 extended GW가 step-height RMS 오차 32-34% 개선
  (density field 19→13nm, pitch field 20.5→13.5nm). h→0 극한 수렴·narrow-line 가속 정성거동
  python verify로 assert 검증. 3/6 완료. 구현요청 소프트웨어 BACKLOG 인계(패턴효과 결합
  모듈, effective-density 모델과 통합 제안).


## 이수 기록 (크론 갱신, 2026-09-07)
- 2026-09-07: Lv2-2 완료. knowledge/cmp/wafer-type-metrology-techniques-suitability.md
  (check_knowledge ✓, verify_claims ✓ — 출처 10건 실존확인(DOI 4·arXiv 2·특허 4), python verify 1블록
  (A)~(E) 통과). 핵심: NPW에서 유효한 기법이 PTW에서 제약되는 세 물리 — ①스팟 vs 패드(US7095511:
  피처 0.1–10 µm, 패드 100 µm; 70° 입사 타원 스팟 50→146 µm), ②혼입광·회절(US9574992 40 µm 타깃),
  ③투과깊이(Cu d_p=14.8 nm, Johnson&Christy 1972 → SE 금속 두께 불가). 스타일러스 팁 R=1.52 µm(NIST) →
  w<3 µm 트렌치 미도달·Table 3 불확도 계수; AFM 4픽셀 규칙(Ahn et al. 2019 arXiv 재현, 높이 2% 이내);
  XRF 지수법칙(US9644956)·NIST XCOM μ/ρ로 Cu 1 µm 비선형 2.3% 확인. 막질×기법×NPW/PTW 적합성 표 작성.
  미검증: SiO₂/Si Ψ·Δ 실측 대조값(Fresnel 자기일관만), Stenzel 2019 본문, 기업자료(스팟·반복도) 전부 2차.
  4/6 완료. 다음 단원: Lv3-1.

## 구현 요청 (2026-09-07, wafer-type Lv2-2)
1. **PTW/NPW 메타데이터 스키마 필수 필드 추가** — `spot_size_um`, `pad_size_um`, `local_density`,
   `probe_radius_um`(스타일러스/AFM), `pixel_pitch_nm`(AFM), `technique`(SE/SR/EC/4PP/XRF/stylus/AFM).
   근거: knowledge/cmp/wafer-type-metrology-techniques-suitability.md §6.2. 검증값: 스팟 장축 = 빔/cos θ
   (50 µm@70° → 146 µm), 패드 100 µm(US7095511). 우선순위: 높음(Cal-1 선행).
2. **측정 적합성 검사 함수** `metrology_suitability(film, wafer_type, technique, spot_um, pad_um, aoi_deg,
   feature_w_um, probe_r_um)` → 경고 리스트. 규칙: 금속+SE→불가(Cu d_p 14.8 nm 기준 50 nm 문턱), SE 타원
   장축>패드→불가, 스타일러스 w<2R→깊이 과소평가 경고, AFM 픽셀 피치>폭/4→폭 신뢰불가 경고, XRF+PTW→
   면적가중 평균 경고. 검증 문헌값: 위 노트 §7 verify (A)~(E) 상수. 우선순위: 중.
3. **XRF 강도-두께 함수** `xrf_intensity_fraction(mu_rho_cm2_g, rho_g_cm3, t_um, geometry_factor=1)` =
   1−exp(−μ̄ρt). 검증값: Cu 52.55 cm²/g·8.96 g/cm³에서 1 µm → 4.60%(비선형 2.3%), 15 µm → 51%. 우선순위: 낮음.


## 이수 기록 (크론 갱신, 2026-09-08)
- 2026-09-08: Lv3-1 완료. knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md
  (check_knowledge ✓, verify_claims ✓ — 출처 12건 실존확인(DOI 8·특허 1·기타), python verify 1블록 (A)~(F) 통과).
  핵심: ①모니터 웨이퍼 관행·레시피 전이 규칙(US20060116785A1/US7333875B2, TSMC: work function F(X,Y,Z),
  변환계수 STI 1.12·IMD 1.41 재현, 패턴밀도 변수 없음) ②NPW→PTW 실패 지점 정량(Sorooshian 2005 UA 학위논문
  §3.3 = ESSL 2004 doi.org/10.1149/1.1785933: 유효압력/인가압력 2.2/1.7/1.3 @10/50/90% vs 밀도모델 1/ρ=10/2/1.11
  → 3.7배 이상 괴리; 표 평균 재현 시 10%는 +21% 차이, 원인 미상으로 정직 기록) ③전기 대리(Park et al. 1999
  CMP-MIC 두께 추출식·라이너 비 200, Pan et al. 1999 OP 10%→1000 Å, Chang et al. 2004 TED R_dish≈40 µm·5 µm 선
  +9.39%) ④VM(Di et al. 2017 PHM2016 MSE 7.07·시계열 지배, Jebri et al. 2017 ST Rousset 제품별 JITL·실측 1/3·
  MAPE 3.2~4.4%) → PTW VM은 제품 식별자·레이아웃 밀도·이전 층·출력 정의가 NPW와 다름.
  미검증: Kim&Seo 2002 r≈0.71(원문 미확보), PHM2016 웨이퍼 유형·MRR 단위(미상), ρ_Cu(추정 2.0), send-ahead 블로그(2차).
  5/6 완료. 다음 단원: Lv3-2.

## 구현 요청 (2026-09-08, wafer-type Lv3-1)
1. **레시피 변환계수 함수** `recipe_conversion_factor(F, recipe_from, recipe_to)` — F는 제어변수별 반응식의 곱
   (work function). 근거: knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §2.2. 검증값: US20060116785A1
   식(1)·표 1 → STI 1.12, IMD 1.41 (verify (A), 지수 괄호 (Y−80)/98.39·(Z−40)/66.304로 구현). 청구항 6 범위 0.5~2 밖이면
   경고. 우선순위: 중 (Lv3-2 전이 규칙의 "이전되는 것" 축).
2. **밀도별 유효압력비 파라미터** `effective_pressure_ratio(density, pad, temp_C)` — sim/calibration의 전이 파라미터
   α(ρ)=P_eff/P_applied. 기본값 표: 10% 2.2, 50% 1.7, 90% 1.3 (Sorooshian 2005 요약값; 표 평균 2.67/1.79/1.26 병기),
   온도 계수는 10→45 °C에서 +31%(문헌)~+46%(양끝 재현) 범위로 불확실 표기. 밀도모델 RR_up=K/ρ_eff와 비교 출력
   (1/ρ 대비 비율). 근거: 같은 노트 §4, verify (B). 우선순위: **높음** (Lv3-2 핵심 미지수, PTW 캘리브레이션 대상).
   **→ 처리 완료 (2026-09-08, software-lead)**: `sim/tier2_physics/npw_ptw_effective_pressure.py` 신설
   (`table_ratio`/`mean_ratio_at_density`/`summary_ratio`/`inverse_density_ratio`/`effective_pressure_ratio`).
   테스트 16건 §6 verify (B)(B') 정량값 그대로 재현. engine 미등록(Recipe 스키마 확장 필요, S17 이하와
   동일 지위). 301 tests passed. 커밋 7ac1f02, push 완료.
3. **전기 두께 추출 함수** `cu_thickness_from_resistance(R_ohm, L_um, W_um, T_L_um, rho_Cu_uohm_cm=2.0)` =
   ρ_Cu·L/(R·(W−2T_L)) + T_L, 라이너 병렬 무시 오차 경고(R_L/R_Cu<100이면). 검증값: Park et al. 1999 W 0.35 µm·T_M 0.4 µm·
   T_L 0.025 µm·ρ_L 100 µΩ·cm → R_L/R_Cu≈200(ρ_Cu 2.0). dishing 보정은 Chang et al. 2004 segment 식(R_dish 40 µm, 5 µm 선
   ΔR 9.39%·모델 11.6%). 근거: 같은 노트 §3, verify (C)(D). 우선순위: 중.
4. **PTW VM 입력 스키마 필드**(Cal-1 연계): `product_id`, `layer`, `die_density_mean`, `local_density`, `prev_layer_topography`,
   `e_test_R_ohm`, `forced_measurement_flag`, `mrr_lag_1..11`, `consumable_usage_neighbors`. 근거: 같은 노트 §5.3 표
   (Jebri et al. 2017 제품별 국소모델·k_est^max 강제 실측, Di et al. 2017 시간지연·사용량 이웃 특징). 우선순위: 중.


## 이수 기록 (크론 갱신, 2026-09-09)
- 2026-09-09: Lv3-2 완료. knowledge/cmp/npw-ptw-transfer-rules-quantitative.md
  (check_knowledge ✓, verify_claims ✓ — python verify 1블록 (A)~(D) 통과).
  새 1차 출처 3건 확보: Kim & Seo 2002 MEE(doi 10.1016/S0167-9317(01)00694-3, Lv1부터 미확보였던 원문 — 미러 사이트→.red storage),
  Ouma 1998 MIT 학위논문(hdl 1721.1/9704, 스캔본 → 페이지 렌더 판독), Tugbawa 2002 MIT 학위논문(hdl 1721.1/8083, 텍스트 추출).
  핵심: 4계열 모델 전부에서 NPW→PTW로 이전되는 물리량은 블랭킷 제거율 하나 — 단 ①순간 rate 환산(Tugbawa 표 3.3: 60 s 평균이
  포화 a1보다 10–26 % 낮음) ②다이 위치별 K(Ouma) ③레시피 변환계수(US20060116785A1) ④드리프트·제품 오프셋 분해(MRS99 eq.5,
  ±100 Å) 네 보정 필요. 새로 필요한 것: PL(Ouma 표 5.2 2.90–4.50 mm, 레시피·패드 의존·레이아웃 무관 → Mask1→Mask2 RMS<150 Å),
  α(ρ)(Sorooshian 2.2/1.7/1.3 — GW 하중균형 상한 1/ρ를 90 %에서 초과, 모순 기록), H_ex·d_max·W 7개 하위 파라미터(Tugbawa),
  τ·h1(MRS99), σ·R·IL·α(Vasilev, K_P = K'_P/(πσR)). 현장 선형식(Kim & Seo) Y=0.9871X+1649.7은 R² 0.51·잔차 104–176 Å.
  미검증: Ouma 판독값(스캔), Tugbawa 표 5.17 열 정렬, Kim&Seo R 정의·절편 해석(추정), Stine 1998·Ouma 2002 저널판 미확보.
  6/6 완료. 다음 단원: Cal-1 (G2 이후 활성).

## 구현 요청 (2026-09-09, wafer-type Lv3-2)
1. **블랭킷 순간 rate 환산 함수** `blanket_rate_instantaneous(t, a1, a2, tau)` = a1 − (a2/τ)e^{−t/τ} 와 `blanket_rate_average(t, ...)`
   = a1 + (a2/t)(e^{−t/τ} − 1), 역방향 `fit_blanket_rate(times, removed)` → (a1, a2, τ). NPW 측정(제거량 vs 시간)에서 PTW 모델
   입력(순간 포화 rate)을 만드는 전이 1단계. 근거: knowledge/cmp/npw-ptw-transfer-rules-quantitative.md §3, verify (B).
   검증 문헌값: Tugbawa 2002 표 3.3 실험 1 a1 249.5 Å/s·a2 3986.6 Å·τ 16.4 s → r_avg(60 s) 184.8 Å/s(−26 %), r_inst(0) 6.4 Å/s ≥ 0;
   Fig.3.19 판독점(29–57 s) 6 % 이내. 우선순위: **높음** (sim/calibration의 NPW→PTW 입력 어댑터).
2. **전이 파라미터 레지스트리** `TransferParam(name, source ∈ {NPW, PTW, layout}, reusable_across_layout: bool, depends_on: [recipe, pad, stage])`
   — 본 노트 §5 표의 12행을 데이터로 등록하고, PTW 예측 호출 시 source=PTW인 파라미터가 캘리브레이션 없이 비어 있으면
   경고. PL은 reusable_across_layout=True·depends_on=[recipe, pad](Ouma 표 5.2), α(ρ)·H_ex·d_max·τ는 False. 근거: §5.
   우선순위: 중 (Cal-1 메타데이터 스키마와 결합).
3. **현장 선형 전이식** `field_linear_transfer(X_pattern_A, slope=0.9871, intercept_A=1649.7)` → 블랭킷 목표 제거량, 계수는
   (mask_id, site_id) 키로 저장·재캘리브레이션 요구. 검증값: Kim & Seo 2002 X 1600→Y 3229 Å, X 3000→4611 Å, R² 0.505,
   잔차 104–176 Å. 우선순위: 낮음 (물리 모델의 baseline 비교용).
4. **유효압력비 하중균형 검사** `alpha_up_bound(rho, h_over_sigma)` = e^{x}/[(1−ρ)+ρe^{x}] (Vasilev 2011 eq.14, κ_U=κ_D) —
   `sim/tier2_physics/npw_ptw_effective_pressure.py`의 실측 비율이 1/ρ 상한을 넘으면 경고(90 % 밀도 1.3 > 1.11 사례).
   검증값: ρ 0.1/0.5에서 α 2.2/1.7 ↔ h/σ 0.93/1.73. 우선순위: 중.
5. **MRS99 eq.5 형태의 다제품 블랭킷 rate 분해** `effective_blanket_rate(n, BR0, BR_device[D], delta[n])` — 기존 R2R 모듈이
   있으면 그 안에 제품 오프셋 항만 추가. 검증값: MRS99 Fig.11 ±100 Å(정성). 우선순위: 낮음.
