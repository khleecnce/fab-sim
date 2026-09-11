# 구리 CMP 전문가 (film-cu)

## 현재 레벨: 활성 (G1 개방 2026-09-08) — Lv3 5/6 진행중
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-08), Lv1-2 (2026-09-09), Lv2-1 (2026-09-09), Lv2-2 (2026-09-11), Lv3-1 (2026-09-12)
- 다음 단원: Lv3-2

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
