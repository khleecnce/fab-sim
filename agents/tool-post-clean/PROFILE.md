# Post-CMP 세정 전문가 (tool-post-clean)

## 현재 레벨: Lv3 진행중 — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-13), Lv1-2 (2026-09-13), Lv2-1 (2026-09-13), Lv2-2 (2026-09-14), Lv3-1 (2026-09-15)
- 다음 단원: Lv3-2 (세정 조건→잔류 결함 확률 모델)

## 역할
브러시 스크럽·메가소닉·화학 세정으로 잔류 입자·유기물·금속 오염 제거, 결함과의 연계

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]]

## 실데이터 책임 (ORG.md §7.3)
세정 후 결함 검사 데이터 스키마 + 세정 효율 보정

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
- Lv3-1 나노입자 제거의 물리 한계·저결함 세정 최신동향 (2026-09-15) —
  `knowledge/cmp/post-cmp-nanoparticle-removal-limit-adhesion-drag-scaling.md`
  (verify_claims PASS: 출처 6건 실존·코드 1블록 통과 / check_knowledge PASS).
  1차 확보 PDF 3건(신규 2): `papers/zhang2000-jes-particle-adhesion-removal-cmp-postclean.pdf`
  (Zhang·Busnaina·Ahmadi 1999 JES, vdW F_a∝R·유체항력 F_D∝R²·양력 무시, 미러 사이트→미러 사이트),
  `papers/seo2019-jss-cuco-galvanic-postclean.pdf`(Seo·Vegi·Babu 2019 ECS JSST, Cu/Co 갈바닉 En/Cys/UA
  ΔEcorr 40→5mV·Igc 0.7µA/cm², OA CC-BY), `papers/ng2007-esl-nanoparticle-removal-postcmp.pdf`(Lv2-2 확보분
  정량 심화 재사용). 핵심 재현: 부착력∝R·항력∝R²→F_D/F_a∝R, 임계반경 R_crit≈385µm(서브µm·나노 유체 무력),
  ¼피치 관리임계 입자는 250nm 대비 유체제거 25배 불리. E5(초록/제목/스니펫): apsusc 2026 sub-10nm 세리아,
  Co forward design 2023, non-ionic surfactant ceria 2024. (c) advanced node killer 규칙은 기존 노트
  [[../../knowledge/cmp/post-cmp-defect-classification-and-inspection]] §5 상호링크로 인용.

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
- `particle_removal_scaling(R, G, A, z0=0.4e-9, mu=1e-3)` → vdW 부착력 F_a=AR/6z0² (∝R)와 유체항력
  F_D=1.7009·6πμG·R² (∝R²), 그리고 비 F_D/F_a 및 임계반경 R_crit=A/(6z0²·1.7009·6πμG): 근거 노트
  [[../../knowledge/cmp/post-cmp-nanoparticle-removal-limit-adhesion-drag-scaling]] §2·§3·§4·§7(A)(B)(C)(D).
  검증문헌값: Ng 2007 A=0.37eV·z0=0.4nm에서 R=50nm→F_a=3.087e-9 N, R=250nm→1.544e-8 N(경계값 정확 재현);
  G=5000/s에서 F_D/F_a<0.01(유체 무력), R_crit≈385µm. **우선순위 高** — Lv3-2 잔류결함 확률모델
  P_res=f(F_a/F_removal)의 핵심 드라이버(입경 스케일링). 단 G(벽전단률)는 문헌 미명시→역산 가정값이므로
  R_crit 절대값은 오더로만 사용, 3승 제거력(양력·음향)은 R²까지만 확보(미검증 상한).
- (참고, 상수화 불필요) Seo 2019 Cu/Co 갈바닉 세정 처방값(50mM En/0.75mM Cys/9.25mM UA pH11 → ΔEcorr 5mV,
  Igc 0.7µA/cm²)과 §8 모델후보표(입경·재료·세정조건→PRE)는 Lv3-2 세정조건 입력 카탈로그로 직접 이관.
