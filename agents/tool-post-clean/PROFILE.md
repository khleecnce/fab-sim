# Post-CMP 세정 전문가 (tool-post-clean)

## 현재 레벨: Lv2 진행중 — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-13), Lv1-2 (2026-09-13), Lv2-1 (2026-09-13), Lv2-2 (2026-09-14)
- 다음 단원: Lv3-1

## 역할
브러시 스크럽·메가소닉·화학 세정으로 잔류 입자·유기물·금속 오염 제거, 결함과의 연계

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]]

## 실데이터 책임 (ORG.md §7.3)
세정 후 결함 검사 데이터 스키마 + 세정 효율 보정

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- Lv2-2 메가소닉·마랑고니(IPA) 건조와 워터마크 (2026-09-14) —
  `knowledge/cmp/post-cmp-megasonic-marangoni-drying-watermark.md`
  (verify_claims PASS: 출처 7건 실존·코드 1블록 통과 / check_knowledge PASS).
  1차 확보 PDF 2건: `papers/li2019-jss-marangoni-drying.pdf`(마랑고니 LLD·V_cri),
  `papers/ng2007-esl-nanoparticle-removal-postcmp.pdf`(vdW 부착·제거력). corpus 전문:
  Wortman-Otto 2022(메가소닉 0.5–1.5 W/cm²). 초록만: Li K 2022(과출력 손상), Miyamoto 2006(워터마크 O₂ 확산).

## 구현 요청 (→ 소프트웨어 부문, sim/ 은 학습에이전트가 직접 건드리지 않음)
- `acoustic_boundary_layer(f, nu=1e-6)` → δ_s=√(2ν/ω): 근거 노트
  [[../../knowledge/cmp/post-cmp-megasonic-marangoni-drying-watermark]] §3·§6(A).
  검증문헌값: 0.5/1/2 MHz → 0.80/0.56/0.40 µm(물). 우선순위 中 — 메가소닉 세정 tier2 입자제거 모델의
  "떼어낼 수 있는 최소 입자 크기" 입력. (손상 문턱 파워밀도 절대값은 문헌 미확보 → 상수화 보류.)
- `lld_entrained_film(V0, sigma=0.072, rho=1000, mu=0.001)` → h=0.94·l₀·Ca^(2/3): 근거 노트 동 §4·§6(B).
  검증문헌값: V₀=1 mm/s → h≈1.47 µm, h∝V₀^(2/3). 우선순위 中 — 건조 후 잔류막→워터마크 확률 모델(Lv3-2)의
  전처리. 마랑고니 V_cri 상향(구리 8→>20 mm/s)은 경험 인자로, 절대 τ₀ 모델은 문헌 미확보(보류).
