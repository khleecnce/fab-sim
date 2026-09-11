# 폴리실리콘 CMP 전문가 (film-poly-si)

## 현재 레벨: [대기] — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2, Lv2-1, Lv2-2
- 다음 단원: Lv3-1

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
  step-height 감쇠를 exp(−t/τ)로, τ는 밀도 무관 캘리브레이션 파라미터. 근거노트: 같은 노트 §4·§7(C). 검증문헌값: US10822524B2
  표 B–D 비교예 0/18/36 s 단차 1841/681/280 (30 %), 1825/654/247 (50 %), 1835/740/299 (70 %) Å → τ 18.0–19.8 s; 선형 예측
  t_c 8.3/13.7/19.3 s는 기각. 우선순위 낮음(Tier2).
