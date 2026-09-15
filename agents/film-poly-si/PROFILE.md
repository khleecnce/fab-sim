# 폴리실리콘 CMP 전문가 (film-poly-si)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1, Lv2-2, Lv3-1, Lv3-2
- 다음 단원: (Lv3-2 완료 — 캘리브레이션 단원 대기)

## 역할
Poly-Si 막의 CMP — 게이트·3D NAND 채널홀·캐패시터. 알칼리 화학 용해+기계 제거

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]

## 실데이터 책임 (ORG.md §7.3)
Poly-Si 실데이터 스키마 + 도핑 의존 보정 파라미터

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
(크론이 갱신)
- 2026-09-10 Lv1-1 Poly-Si 물성(도핑·결정립)과 CMP 거동 — knowledge/materials/film-poly-si-doping-grain-cmp.md
- 2026-09-11 Lv1-2 알칼리(KOH/TMAH/아민) 화학 용해 메커니즘과 pH 의존성 — knowledge/materials/film-poly-si-alkaline-dissolution-ph-kinetics.md
- 2026-09-11 Lv2-1 Poly:oxide 선택비 설계와 게이트 CMP 공정 윈도우 — knowledge/materials/film-poly-si-oxide-selectivity-gate-cmp-window.md
- 2026-09-12 Lv2-2 3D NAND 응용: 고종횡비 구조 위 Poly CMP, 디싱 — knowledge/materials/film-poly-si-3dnand-har-poly-cmp-dishing.md
  (⚠ 이 회차는 서브에이전트 세션에서 python·웹 실행 권한이 승인되지 않아 verify_claims.py / check_knowledge.py를 **실행하지 못함**.
  verify 블록 4개는 손으로 수치 검산했고 게이트 정규식은 수동 대조함 — 총괄이 커밋 전 두 도구를 반드시 실행할 것)
- 2026-09-13 Lv3-1 최신 리뷰: 고선택비 Poly 슬러리, 무결함 Poly CMP — knowledge/materials/film-poly-si-high-selectivity-lowdefect-slurry.md
  (verify_claims PASS: 출처 9건 실존·코드 6블록 통과·출처없는 수치주장 0 / check_knowledge PASS. 확보 원문 4건 전문 +
  학회 발표논문 1건 + 초록 1건. 기존 Lv1-2·Lv2-1·Lv2-2 노트에 후속 역링크 추가함)
- 2026-09-16 Lv3-2 Poly-Si Kp·화학 용해율 파라미터 + 문헌값 재현 — knowledge/materials/film-poly-si-kp-preston-dissolution-rate-literature-reproduction.md
  (verify_claims PASS: 출처 6건 실존·코드 6블록 통과·출처없는 수치주장 0 / check_knowledge PASS. Park2007(V직접)·Penta2011·
  Pirayesh2014·Bae2022·Lagudu2019·Jeon2021 재인용 합성. 결론: 표준 알칼리 실리카 poly-Si Kp≈2.3e-13 m²/N(oxide 팩의 2.3배,
  estimated), 도핑배율 undoped 1.0→p⁺ 0.20, 정적식각≪MRR(1/5000). poly_si_silica.yaml 신설 제안표는 §7 — 아래 [P7] 참조)

## 구현 요청 (sim/ 은 소프트웨어 부문 담당 — 여기 적기만 한다)
- **[P1] poly-on-oxide 패턴 디싱: Lee 2002 2물질 폐형해의 poly 기호 재사용 + d_max ∝ 1/ρ 변형** — 무엇: STI용 D_ss/K_ss/τ 식
  (식 2.32·2.33·2.38·2.46–2.49)을 K = 블랭킷 poly RR, s = poly:oxide 선택비, ρ = 정지층(up) 분율로 파라미터화한 poly 팩 분기.
  d_max = Kτ₂/(sρ)(1/ρ 변형)를 기본으로. 근거노트: knowledge/materials/film-poly-si-3dnand-har-poly-cmp-dishing.md §3·§7(B),
  EVIDENCE-RULES 판정 #5. 검증문헌값: US10822524B2 표 B–D 비교예(s = 97) 디싱 재성장 727/631/313 Å @ PD 30/50/70 %,
  30/70 % 비율 2.32(모델 2.29). 우선순위 중(Tier2 패턴 모델 — 3D NAND 팩 전제).
- **[P2] 트렌치(down) poly 제거율 화학 억제 인자 χ_down ∈ [0,1]** — 무엇: 정지층 노출 후 down 영역 RR에 곱하는 첨가제 의존
  인자. 선택비(Kp 비율)만으로는 1-2(69:1, 최종 단차 594 Å)와 1-1*(97:1, 878 Å)·1-5(1832:1, 1871 Å)를 동시에 표현 못 함
  (§7(D): 모델 차 <1 % vs 실측 32 %). 근거노트: 같은 노트 §3·§7(D). 검증문헌값: 표 F 디아민 3.75/7.5/15 ppm → 최종 단차
  478/385/250 Å(50 % PD, 75 s), 선택비 72/71/69. 우선순위 중.
- **[P3] 단차 소멸 시정수: Phase 1A 선형 대신 Phase 1B 지수형(τ ≈ 18–20 s, PD 무관)** — 무엇: poly 팩 오버버든 평탄화 단계의
  step-height 감쇠를 exp(−t/τ)로, τ는 밀도 무관 캘리브레이션 파라미터. 근거노트: film-poly-si-3dnand-har-poly-cmp-dishing.md §4·§7(C). 검증문헌값: US10822524B2
  표 B–D 비교예 0/18/36 s 단차 1841/681/280 (30 %), 1825/654/247 (50 %), 1835/740/299 (70 %) Å → τ 18.0–19.8 s; 선형 예측
  t_c 8.3/13.7/19.3 s는 기각. 우선순위 낮음(Tier2).
- **[P4] 비-Preston 문턱압력 모델 MRR = k·(P − P_th)⁺·V (poly 팩, 첨가제 의존)** — 무엇: Preston 항을 문턱형으로 바꾸는
  분기. 파라미터 2개(k, P_th)뿐이며 P_th는 첨가제로 이동한다. Lv2-2 [P2]가 요청한 χ_down의 물리적 실체이므로 **[P2]보다
  먼저 시도할 것**(χ_down은 무차원 곱셈인자라 정상상태에서만 의미가 있으나, 문턱형은 압력장에서 직접 0을 만든다).
  근거노트: knowledge/materials/film-poly-si-high-selectivity-lowdefect-slurry.md §5·§9(C).
  검증문헌값(Lagudu 2019, DOI 10.1149/2.0081905jss): 250 ppm 아민 + 25 ppm CPB, pH 10 — P_th = 1.5(PDADMAC) /
  2.5(DADMAC) / 1.0(GC) psi, 4 psi에서 RR 300–350 nm/min → 역산 k = 130 / 217 / 108 nm/min/psi. CPB ≥ 50 ppm이면
  1–4 psi 전 구간 0(과억제). 무 CPB Prestonian 대조: 1·2 psi에서 80–270 nm/min. 우선순위 **높음**(Tier1 Preston 분기,
  패턴 디싱 예측에 직결).
- **[P5] 팩 스키마에 `abrasive_free` 분기** — 무엇: 무연마재/저고형분 슬러리에서는
  knowledge/cmp/delta-scratch-damage-d99-oversize-particle-model.md의 Δ = (d99/d99_ref)^n 손상 팩터가 **정의되지 않는다**
  (연마입자 분포 자체가 없음). 현재 `_f_delta`는 `abrasive_d99_nm` 유무로만 판정하므로 무연마재 팩이 조용히 unmodeled로
  빠진다. 근거노트: 같은 노트 §4·§11-2. 검증문헌값(Jeon 2021, DOI 10.1016/j.mssp.2021.105755): AFM Ra 연마전 3.58 →
  1 wt% 실리카 0.94 → 250 ppm PDADMAC 무연마재 0.52 → +750 ppm PEG 0.42 nm (무연마재가 연마재보다 조도 45 % 낮음).
  우선순위 낮음(스키마 정합성).
- **[P6] 선택비를 스칼라가 아니라 "oxide RR 억제인자"로 분리** — 무엇: `poly_oxide_selectivity` 한 숫자 대신 poly RR과
  oxide 억제인자를 따로 두기. 문헌의 선택비 계단(25–45 → 69–1832 → ≥280)은 poly 가속이 아니라 **산화막 억제**에서
  나오며(§9(F): 산화막 억제 2–3배 × poly 가속 2.1–3.5배 = 선택비 6.2배), 무첨가 세리아처럼 선택비가 1 미만으로
  뒤집히는 계도 있어 스칼라 배율로는 부호를 못 담는다. 근거노트: 같은 노트 §8·§9(F). 검증문헌값: Park 2007 oxide
  4–6 nm/min·선택비 45 vs Penta 2011 oxide ≤ 2 nm/min·poly 559–636. 우선순위 중.
- **[P7] poly_si_silica.yaml 팩 신설 (oxide_silica base 상속) + kp_m_per_pa=2.3e-13·도핑배율·정적식각 무시** — 무엇:
  현재 없는 poly-Si 팩을 신설. `film: poly_si`, `abrasive: silica`, `slurry_ph: 10.5`, **`kp_m_per_pa: 2.3e-13 m²/N`
  (estimated, oxide 팩 1.0e-13의 2.3배)**, 도핑배율 키 `kp_doping_ratio_{undoped:1.0, p_plus:0.20, p_minus:0.60}`
  (n_plus는 미선언 — 값 없음), Preston 지수 `a=b=1`(V≲0.7 m/s·rpm≲90 유효), `static_etch_negligible: true`.
  근거노트: knowledge/materials/film-poly-si-kp-preston-dissolution-rate-literature-reproduction.md §3·§6·§7.
  검증문헌값: Park 2007(DOI 10.3938/jkps.51.214, V=0.539 m/s 직접 → Kp 2.5e-13 앵커), Penta 2011(DOI 10.1021/la104257k,
  4psi 90rpm poly RR 230–245 nm/min), Pirayesh 2014(undoped 5× 고B → 도핑배율), Bae 2022(DOI 10.3390/nano12213893,
  typical Preston). ⚠ kp 절대값은 rpm→V의 r_cc 미확인으로 estimated 유지(literature 승격 불가). 우선순위 **높음**
  (poly Tier2의 최기본 상수 — 이게 없어 지금까지 poly 시뮬레이션 자체가 불가능).
