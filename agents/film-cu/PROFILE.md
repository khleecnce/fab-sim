# 구리 CMP 전문가 (film-cu)

## 현재 레벨: 활성 (G1 개방 2026-09-08) — Lv2 3/6 진행중
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-08), Lv1-2 (2026-09-09), Lv2-1 (2026-09-09)
- 다음 단원: Lv2-2

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

- **Lv2-1 (2026-09-09)**: Cu dishing·erosion 물리 — Hooke 압력분배·removal-rate diagram·닫힌 시간해(D_ss, τ₃, Y₁)·d_max(w, s) 경험식·
  엣지 라운딩 ψ(s)·모델 한계(ear·과도 오버폴리시·블랭킷 속도 시간의존).
  노트: [[../../knowledge/cmp/cu-dishing-erosion-density-step-height-model-tugbawa]]
  (1차출처: Tugbawa 2002 MIT 학위논문 hdl 1721.1/8083 전문(수식·Table 3.9/3.10 판독) + Tugbawa 2001 CMP-MIC + Park 1998 VMIC + Ruan 2009
  J. Semicond.(Wayback 원문, 시뮬레이터 출력) + Vasilev 2011; Steigerwald 1994 JES는 초록만(미러 사이트 전 미러 캡차).
  verify 3블록 통과, verify_claims 출처 3건 실존·check_knowledge 통과. 미해결: 50 % 어레이 Y₁ 41 % 과대, Fig 3.12 지수 0.51 vs α₂ 0.17–0.30)

## 구현 요청
- **[P1] Cu-H₂O Pourbaix 경계 함수** `sim/tier2_physics/cu_pourbaix.py` (제안): 입력(pH, E, log a_Cu) → 안정상(Cu / Cu²⁺ / Cu₂O /
  Cu(OH)₂[CuO 대용]) 반환. 상수는 CRC E° 6개(0.3419, 0.521, 0.153, −0.360, −0.222, −0.080)만 사용, 경계식은 노트 §2 1–5번.
  근거노트: [[../../knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §2·§7 verify 1.
  검증문헌값: Tamilmani 2005 그림 4.1 — Cu²⁺/Cu 0.22 V(a=1e-4)·0.16 V(1e-6), 삼중점 pH 4.2, Cu/Cu₂O pH 8에서 0.00 V·pH 13에서
  −0.30 V (±0.03 V/±0.15 pH). CuO 경계(pH 5.65, 절편 0.64 V)는 CuO ΔG_f° 1차값 확보 전까지 "미검증" 플래그로 남길 것.
- **[P2] 산화제 혼합전위 모델**: 슬러리 H₂O₂ wt%·pH → Cu가 보는 전위 E_mix. 열역학 상한(1.776 − k·pH + k/2·log c)이 아니라
  O₂/H₂O₂~H₂O₂/H₂O 사이 실측 보간(Tamilmani 2005 4 % H₂O₂: pH 2/4/6/8 → 0.68/0.48/0.50/0.41 V ±0.05)을 기본값으로.
  근거: 노트 §3·verify 2. 우선순위 P2 — P1 위에서 "Cu²⁺ 영역인가 산화물 영역인가" 판정에 쓰임.
- **[P2] 정적식각/MRR 비 파라미터** (dishing 커널 입력): Cu 슬러리 프로파일에 `static_etch_rate_nm_min`·`mrr_over_ser` 필드.
  기본값 Lee H. 2023(H₂O₂ 3 wt%/구연산 0.2/BTA 0.05, pH 3.7): SER 26.4 nm/min, MRR 302.5 nm/min(비 11.5). 패드 비접촉
  저지대는 SER로만 깎이도록 timeline에 연결 — Lv2-1 dishing 노트 작성 후 구현(선행 의존).
- **[P3] BTA 막 두께 상수**: Cu(I)-BTA 2–4 분자층(0.12 µg/cm², Tamilmani 2005 QCM) — Kaufman 경쟁모델의 "막 두께" 초기값.
  단 하이드록실아민계 실측이므로 H₂O₂계 적용 시 "미검증" 플래그.

- **[P1] Tugbawa 밀도-스텝하이트 오버폴리시 커널** `sim/tier2_physics/cu_dishing_erosion_tugbawa.py` (제안): 입력(r_cu, r_ox, Φ_cu, d_max, d₂, t−t₃)
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
