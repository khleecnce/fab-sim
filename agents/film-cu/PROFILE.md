# 구리 CMP 전문가 (film-cu)

## 현재 레벨: 활성 (G1 개방 2026-09-08) — Lv3 6/6 진행중
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-08), Lv1-2 (2026-09-09), Lv2-1 (2026-09-09), Lv2-2 (2026-09-11), Lv3-1 (2026-09-12), Lv3-2 (2026-09-15)
- 다음 단원: (Lv3 완료 — Lv4 대기)

## 역할
Cu 배선 CMP — 전기화학 부식·패시베이션 제어, 배리어 CMP, dishing/erosion. 화학 지배

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]
- [[../../knowledge/cmp/pattern-dependent-dishing-erosion]]

## 실데이터 책임 (ORG.md §7.3)
Cu 실데이터(NPW MRR·PTW dishing/erosion 맵) 스키마 + 패턴 의존 보정 파라미터 — PTW 보정의 대표 사례

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- **Lv1-1 (2026-09-08)**: Cu CMP 3단계(벌크·소프트랜딩·배리어)와 슬러리 요구.
  노트: [[../../knowledge/cmp/cu-cmp-three-step-process-slurry-requirements]]
  (1차출처: US2009/0057264A1 특허, verify 2블록 통과, check_knowledge/verify_claims 통과)
- **Lv1-2 (2026-09-09)**: Cu 전기화학 — Pourbaix 정량 경계, BTA 패시베이션 막, 산화제-억제제 균형.
  노트: [[../../knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]
  (1차출처: Tamilmani 2005 UA 학위논문 hdl 10150/280774 전문 + CRC Vanýsek E° 표 + Lee H. 2023 PMC9966509;
  verify 3블록 통과, verify_claims 출처 6건 실존·check_knowledge 통과. CuO ΔG_f° 미확보로 CuO 경계는 방향만 확인)
- **Lv2-2 (2026-09-11)**: 배리어(Ta/TaN/Co) CMP와 Cu:배리어:옥사이드 선택비.
  노트: [[../../knowledge/cmp/film-cu-barrier-ta-tan-co-selectivity]]
  (check_knowledge/verify_claims 통과, 출처 4건 실존·검증코드 1블록 통과)

- **Lv2-1 (2026-09-09)**: Cu dishing·erosion 물리 — Hooke 압력분배·removal-rate diagram·닫힌 시간해(D_ss, τ₃, Y₁)·d_max(w, s) 경험식·
  엣지 라운딩 ψ(s)·모델 한계(ear·과도 오버폴리시·블랭킷 속도 시간의존).
  노트: [[../../knowledge/cmp/cu-dishing-erosion-density-step-height-model-tugbawa]]
  (1차출처: Tugbawa 2002 MIT 학위논문 hdl 1721.1/8083 전문(수식·Table 3.9/3.10 판독) + Tugbawa 2001 CMP-MIC + Park 1998 VMIC + Ruan 2009
  J. Semicond.(Wayback 원문, 시뮬레이터 출력) + Vasilev 2011; Steigerwald 1994 JES는 초록만(미러 사이트 전 미러 캡차).
  verify 3블록 통과, verify_claims 출처 3건 실존·check_knowledge 통과. 미해결: 50 % 어레이 Y₁ 41 % 과대, Fig 3.12 지수 0.51 vs α₂ 0.17–0.30)
- **Lv3-1 (2026-09-12)**: 최신 리뷰 — 저압 Cu CMP, 갈바닉 부식(ΔE_corr·면적비·마찰 재부동태), 고종횡비 배선(초박 Ru/Mo 배리어 → 선택비 1:1).
  노트: [[../../knowledge/cmp/cu-cmp-low-pressure-galvanic-corrosion-advanced-interconnect-review]]
  (1차출처 전문 6건: Lee et al. 2021 Sci Rep PMC8551296(Cu/Ru ΔE 0.49→0.09 V, 선택비 3.86→1.05 @1.5 psi) + Gamagedara & Roy 2024 Materials
  (0.014 MPa Cu/Mo 46/41 nm/min, 창 1±0.5) + Moon 2023 Adv Sci 리뷰 + Han 2012 NRL(저압 정의) + Cabot KR101557514B1(Ru OCP −100 mV) + Tamilmani 2005
  갈바닉 직접 실측(마찰 중 500 vs 정지 <2 µA/cm², rpm 비례). verify 4블록 **수계산 통과** — ⚠ 이 세션은 네트워크·python 실행이 모두 미승인이라
  verify_claims/check_knowledge를 기계로 못 돌렸고 신규 원문 다운로드도 못 했다(로컬 코퍼스로 구성). 총괄이 두 도구를 실행해 확정할 것.
  미해결: Cu/Ru 마찰 중 갈바닉 실측 부재, ≤1 psi Cu MRR 실측 부재(Pandija 2009·Liu 2011 원문 미확보), Lee 2021 I_corr↑ vs R_p↑ 상반 이유 불명)
- **Lv3-2 (2026-09-15)**: Cu Kp(Preston 계수) 문헌 역산 — `kp_m_per_pa=3.5e-13`을 1차 (P,V,MRR) 실측표로 재현. 다중 문헌 Kp 분포
  (산성/중성 H2O2·기계 계 1.1~5.8e-13 m²/N, 중앙 ≈1.9e-13)에 팩값이 상단부로 포함되고, **Tugbawa 2002 블랭킷 Cu r_cu=159 Å/s@4psi
  역산치 3.67e-13이 팩값과 5 % 이내 일치** → "미재현" 종결. Guo 2004 순수 기계 baseline 1.75e-13(팩의 0.5배, 화학강화 방향 정합).
  Preston 선형성: Guo 실측으로 threshold~6 psi·V≲0.7 m/s 레짐에서만 a=b=1(고압 P^1/6·고속 포화). H2O2 정점 3.6 wt%(Seal/Gopal 산성)로
  `oxidizer_peak_wt_pct=3.0` 확증(판정#20 알칼리 단조감소와는 레짐 분리).
  노트: [[../../knowledge/cmp/cu-kp-preston-coefficient-literature-back-calculation]]
  (신규 1차출처: Guo & Subramanian 2004 JES DOI 10.1149/1.1640632 전문(Preston 계수 직접 적합) + Wei et al. 2013 Surf Coat Technol
  DOI 10.1016/j.surfcoat.2012.04.004 전문(H2O2+BTA+glycine) + Gopal & Talbot 2007 JES DOI 10.1149/1.2718474 전문; Li&Babu 2001·Tugbawa
  2002·Lee 2021 형제노트 재인용. verify 5블록 통과, verify_claims 출처 7건 실존·check_knowledge 통과. 팩 갱신 제안: kp_m_per_pa
  값 유지·근거를 일반범위→Tugbawa r_cu 역산으로 교체, confidence estimated 유지(r_cc 환산 ±30~44 % 불확실). 미해결: 팩 화학 정확일치
  단일 (P,V,MRR) 문헌 부재(wei2013은 실리카 연마재), rpm 문헌의 r_cc 미보고)
- **Δ damage_exponent 1차 문헌 재탐색 (2026-09-15)**: `cu_h2o2_bta.yaml::damage_exponent=2.54`
  (텅스텐 전이, E4)를 Cu 직접 실측으로 승격 가능한지 판정 — **estimated 유지, 승격 안 함**.
  Cu 직접 문헌 3편 확보(Teo 2003 정성적 로컬 기확보, Li et al. 2018 ECS JSS 신규 fetch —
  Cu 배리어 CMP EDA 분산제 스윕에서 그래프 판독으로 LPC-스크래치 5점 재구성해 `scratch~LPC^3.22`
  R²=0.974 회귀, Saka et al. 2009 신규 fetch — Cu 단일입자 스크래치 폭=지름/2 선형모델). 셋 다
  damage_exponent가 정의하는 "D99→스크래치 **개수**" 축과 다른 물리량(LPC=임계초과 **개수**축은
  D99로 환산 불가·폭 모델은 **크기**축)이라 대입 불가 — 방향성 확신은 커졌으나(m=3.22가 기존
  W 관측 범위 1.73~3.73 안) 등급은 그대로. `find_open_access.py --title`은 두 신규 논문 모두
  IOP 링크만 반환(직접 fetch 403 Radware) → `미러 사이트()` 함수 직접 호출로 미러 사이트→미러 사이트
  미러 URL 확보 후 `curl -e referer`로 우회 다운로드.
  노트: [[../../knowledge/cmp/delta-damage-exponent-cu-primary-source]]
  (신규 1차출처: Li et al. 2018 ECS JSS DOI 10.1149/2.0101806jss 전문(그래프 판독 verify 포함)
  + Saka et al. 2009 DOI 10.1149/1.3121964 전문; Teo et al. 2003 SPIE 5041 로컬 코퍼스 재검토.
  YAML 미수정 — 판정 규칙상 승격 근거 미달을 정직하게 기록.)

## 구현 요청
- **[P1] Cu-H₂O Pourbaix 경계 함수** ✅ 9/10 완료 — `sim/tier2_physics/cu_pourbaix.py`(S40, 커밋 495ed90).
  경계식 6종 + `stable_phase()` 종합 판정, Tamilmani 2005 그림4.1 재현 테스트 12건. CuO는 ΔG_f° 미확보로
  미구현, Cu(OH)₂ 대체값으로 명시적 미검증 표기. engine 미등록(Recipe 스키마 부재).
- **[P2] 산화제 혼합전위 모델**: 슬러리 H₂O₂ wt%·pH → Cu가 보는 전위 E_mix. 열역학 상한(1.776 − k·pH + k/2·log c)이 아니라
  O₂/H₂O₂~H₂O₂/H₂O 사이 실측 보간(Tamilmani 2005 4 % H₂O₂: pH 2/4/6/8 → 0.68/0.48/0.50/0.41 V ±0.05)을 기본값으로.
  근거: 노트 §3·verify 2. 우선순위 P2 — P1 위에서 "Cu²⁺ 영역인가 산화물 영역인가" 판정에 쓰임.
- **[P2] 정적식각/MRR 비 파라미터** (dishing 커널 입력): Cu 슬러리 프로파일에 `static_etch_rate_nm_min`·`mrr_over_ser` 필드.
  기본값 Lee H. 2023(H₂O₂ 3 wt%/구연산 0.2/BTA 0.05, pH 3.7): SER 26.4 nm/min, MRR 302.5 nm/min(비 11.5). 패드 비접촉
  저지대는 SER로만 깎이도록 timeline에 연결 — Lv2-1 dishing 노트 작성 후 구현(선행 의존).
- **[P3] BTA 막 두께 상수**: Cu(I)-BTA 2–4 분자층(0.12 µg/cm², Tamilmani 2005 QCM) — Kaufman 경쟁모델의 "막 두께" 초기값.
  단 하이드록실아민계 실측이므로 H₂O₂계 적용 시 "미검증" 플래그.

- **[P1] Tugbawa 밀도-스텝하이트 오버폴리시 커널** ✅ 9/10 완료 — `sim/tier2_physics/cu_dishing_erosion_tugbawa.py`(S42, 커밋 31bd312). 입력(r_cu, r_ox, Φ_cu, d_max, d₂, t−t₃)
  → D_cu(t), E_ox(t) 닫힌 해(eq 3.37–3.42). 유전체 기울기는 Φ/((1−Φ)·d_max)로 고정 — 현행 `pattern_density.steady_state_dishing`의 자유
  파라미터 b 제거. d_max(w, s) = B·w^α₂·min(s, s_l)^β₂ (eq 3.46) 기본값 Table 3.9 ψ 포함 행(B 333 Å, α₂ 0.303, β₂ 0.259, s_l 100 µm);
  엣지 라운딩 r'_ox = (C·e^{−s/s_c} + 1)·r_ox (C 3.04, s_c 22.5 µm). 근거노트: [[../../knowledge/cmp/cu-dishing-erosion-density-step-height-model-tugbawa]] §1–3·verify 1–3.
  검증문헌값: Tugbawa 2002 Fig 3.14 — Φ 0.9·s 1 µm 어레이 erosion 기울기 61 Å/s(±4), 모델 58.2 Å/s; Tugbawa 2001 Fig 3 — 80 %/33 % 정상상태
  dishing 265/320 Å(r_cu 135, r_ox,eff 7.8–10.3 Å/s, d_max ≈ 350 Å); τ₃ 1–3 s. 플래그: Φ_eff > 0.95 또는 과도 오버폴리시(E_ox 기울기 꺾임) 영역은
  "과대예측" 경고(§4.2), Φ_eff 계산엔 L₃ ≈ 1.3–1.5 mm 가우시안 창.
- **[P2] 블랭킷 Cu 속도 시간의존** `r(t) = a₁ − (a₂/τ_r)·e^{−t/τ_r}` (eq 3.53) — 장비 옵션 파라미터(Mirra Table 3.3: a₁ 120–250 Å/s, τ_r 6–16 s;
  "일부 장비 미관측"). [[../../knowledge/physics/frictional-heating-temperature-arrhenius-coupling]]의 온도 포화와 결합 후보. 근거노트 §4.3.
- **[P2 갱신] 정적식각/MRR 비** (위 항목의 선행 의존 해소): 커널에서 D_cu ≥ d_max(패드 비접촉)일 때 RR_cu = 0 대신 SER 26.4 nm/min(Lee H. 2023) 하한 적용.
  근거노트 §6.
- **[P2] 갈바닉 커플 모듈** (Lv3-1, 2026-09-12): 입력(배리어 종류 Ta/Ru/Co/Mo, 슬러리 pH·산화제, 억제제 농도, 회전속도, 노출 면적비 A_Cu/A_barrier)
  → 출력(ΔE_corr, 갈바닉 전류밀도 i_gal, Faraday 환산 등가 제거율). 구조: i_gal = i_gal,abr(rpm) · [마찰 중] / 감쇠 후 포화값 [정지], 마찰 중 값은
  회전속도에 비례(Tamilmani 2005 Cu/Ta: 222 rpm 500 → 90 rpm 180 µA/cm², 정지 <2 µA/cm², H₂O₂ pH 6/8 정지 포화 ~10 µA/cm²). 억제제는 ΔE_corr을
  줄이는 항으로: 니코틴산 0/0.03/0.05 M → Cu/Ru ΔE 0.49/0.15/0.09 V(Lee 2021 Table 1), Cabot 암모늄 아세테이트 → Ru OCP −0.10 V. 검증문헌값:
  10 µA/cm² ≡ Ta 1.3 Å/min; 노트 verify 2·3. 근거노트 §2–§4. 플래그: Cu/Ru 마찰 중 실측 부재 → Cu/Ta 비례성 전이는 "미검증" 표시.
- **[P2] 배리어 선택비 1:1 프로파일** (Lv3-1): 슬러리 프로파일에 `barrier_type`·`barrier_to_cu_selectivity`·`selectivity_window` 필드. 기본값 Ru:
  Cu/Ru 1.05(니코틴산 0.05 M, Lee 2021, 1.5 psi), Mo: Mo/Cu 0.89 또는 1.12(정의 불명, Gamagedara 2024, 0.014 MPa)·창 1 ± 0.5. Tugbawa 커널의 배리어
  클리어 단계 r_b = 선택비 × r_cu로 연결(선택비 1이면 pre-dishing 0). 근거노트 §1·§5, verify 3·4. Ta/TaN 값(≥3–4:1)은 Lv2-2 노트가 정본.
- **[P3] 저압 MRR 하한**: ≤1 psi에서 Preston 선형 외삽 대신 화학 하한(무연마 Cu 10 nm/min, 구연산 pH 8, Gamagedara 2024 역산)을 바닥값으로 두는
  옵션. ≤1 psi 실측이 없어 "미검증" 플래그 — Pandija 2009·Liu 2011 원문 확보 후 갱신. 근거노트 §6.
- **[P2] Kp Preston 선형 유효창 플래그** (Lv3-2, 2026-09-15): `sim/tier1_empirical/preston.py`(구현은 소프트웨어 부문)에서 팩 Kp가
  **저압(threshold~1.5 psi ~ 6 psi)·저속(V≲0.7 m/s) 레짐 밖에서 선형 외삽 시 과대예측**함을 경고 플래그로. 근거: Guo & Subramanian 2004
  (DOI 10.1149/1.1640632) — P>6 psi에서 MRR∝P^(1/6), V>0.7 m/s에서 포화. 검증문헌값: 6→12 psi 순수 Preston(P¹) 대비 P^1/6이면 1.78배
  과대(노트 §9 블록3). 근거노트 §4. Kp 절대값은 Tugbawa r_cu=159 Å/s@4psi 역산 3.67e-13(팩 3.5e-13과 5 % 이내, 노트 §6·verify 블록1).
- **[P3] 산화제 항 pH 레짐 분기** (Lv3-2): 현재 팩은 산성 `oxidizer_peak_wt_pct=3.0`(정점형)과 알칼리 유래 `oxidizer_passivation_K`
  (판정#20, 단조감소)를 동시 보유. Seal/Gopal 2007(산성 pH4 정점 3.6 wt%)과 US20110165777A1(알칼리 pH10.3 단조감소)은 pH 레짐이
  달라 **평균 금지·레짐 분리**(노트 §5.1). 구현 시 두 경로를 pH로 분기하거나 우선순위를 명시할 것 — 현재 상호배타 우선순위(판정#20)가
  산성 정점을 덮지 않는지 확인 필요. 근거노트 §5.1, [[../../knowledge/cmp/chi-oxidizer-cu-h2o2-reparameterization]].
