# Post-CMP 세정 전문가 (tool-post-clean)

## 현재 레벨: Lv3 진행중 — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1 (2026-09-13), Lv1-2 (2026-09-13), Lv2-1 (2026-09-13), Lv2-2 (2026-09-14), Lv3-1 (2026-09-15), Lv3-2 (2026-09-19)
- 다음 단원: Cal-1 (세정 후 결함 검사 데이터 스키마 + 세정 효율 보정, G2 이후)

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

## 이수 기록 (Lv3-2)
- Lv3-2 세정 조건 → 잔류 결함 확률 모델 (2026-09-19) —
  `knowledge/cmp/post-cmp-cleaning-conditions-residual-defect-probability-model-spec.md`
  (verify_claims PASS: 출처 5건 실존·코드 1블록 통과 / check_knowledge PASS).
  1차 확보 PDF(신규 1): `papers/an2012-jjap-pva-brush-pre-process-params.pdf`(An·Lee·Kim·Jeong 2012 JJAP,
  DOI 10.1143/jjap.51.026501, PVA 브러시 PRE vs rpm(50–300, peak≈150)·overlap·젖음성, PSL 300nm 60s PRE~99%,
  sci.bban.top 미러). 기확보 재사용: gowda2020(E1 OA, pH 8/10/12→PRE 35/71/>99%·질화막 29/60/>99%·재부착 제타
  −53~−60mV), Wortman-Otto 2022(corpus 전문, 메가소닉 0.5–1.5 W/cm² 2차속도론·고파워 저해·300s 포화),
  Seo2019(부식 Igc), Sato2011(제타부호). 초록만(E5): Handa et al. 2021 ECS JSST(DOI 10.1149/2162-8777/abf16a,
  재부착 DLVO-가우시안 모델 — IOP 봇차단·sci-hub 미등재), Miyamoto2006(워터마크 O₂). 핵심 재현: PRE=1−e^{−kt}로
  An2012 99%→k=0.077/s·반감 9.0s; Gowda pH 로지스틱은 pH8·10 재현하나 pH12는 7.7pp 계단(IEP 통과 재부착 차단);
  D~Poisson(λ), λ=N₀(1−PRE)+λ_redep(제타 같은부호→0), 워터마크·부식 독립 Poisson 가산. 형제 침범 없음(결함
  분류/RCA=defect-scientist [[../../knowledge/cmp/defect-probability-model-process-conditions-rca]] §2.2 빈칸만 채움,
  금속이온 흡착=surface-contamination — 인용만).

## 구현 요청 (→ 소프트웨어 부문, sim/ 은 학습에이전트가 직접 건드리지 않음)
- `pre_removal_kinetics(N0, k, t, order=1)` → 1차: N=N0·exp(−kt), PRE=1−exp(−kt); 2차: N=N0/(1+k2·N0·t).
  근거 노트 [[../../knowledge/cmp/post-cmp-cleaning-conditions-residual-defect-probability-model-spec]] §2·§7(A)(C).
  검증문헌값: An2012 저친수 PRE=0.99@t=60s → k=0.0768/s, 반감 9.03s, 남은분율 0.01. **우선순위 高** — Lv3-2 λ
  모델의 λ_stuck=N0·(1−PRE) 드라이버. 메가소닉은 2차(Wortman-Otto 2022) — order 스위치 필수. k(조건)의 절대
  스케일·2차 계수는 계·조건 의존(미확보) → 캘리브레이션 파라미터로.
- `pre_ph_logistic(pH, b, pH50, zeta_gate=True)` → 로지스틱 1/(1+exp(−b(pH−pH50)))에 재부착 게이트를 곱함.
  근거 노트 동 §2B·§7(B). 검증문헌값: Gowda2020 산화막 pH8→0.35, pH10→0.71 재현(b=0.757, pH50=8.82);
  pH12는 로지스틱 단독으로 ~0.92이나 실측 >0.99 → **zeta_gate(IEP 통과 부호반전)로 계단 보정 필수**. 우선순위 中.
- `lambda_residual(N0, PRE, zeta_p, zeta_s, redep_frac)` → λ=N0·(1−PRE)+λ_redep; λ_redep=0 if ζ_p·ζ_s≥0
  else redep_frac·N_detached (Gowda2020/Sato2011 부호규칙; Handa2021 DLVO-가우시안은 방향만 E5). 근거 노트 동
  §3·§7(D). 검증: 같은부호 재부착 0, 반대부호 양수, Poisson 평균=분산. **우선순위 高** — defect-scientist §2.2가
  미해결로 남긴 η_removal·ΔG_barrier(ζ) 폐형식의 세정에이전트측 입력. redep_frac 절대값은 미확보(구조만).
- `lambda_total_add(lam_particle, lam_watermark, lam_corrosion)` → 독립 Poisson 가산(평균=분산=합). 근거 노트
  동 §4·§7(E). 워터마크 λ_watermark(V₀, 용존O₂; Miyamoto2006 E5)·부식 λ_corrosion∝∫Igc dt(Seo2019 E1). 개수/wafer
  환산계수 미확보 → 가산 구조만, 계수는 Cal-1 캘리브레이션. 우선순위 中.
- (결합) `acoustic_boundary_layer`·`lld_entrained_film`·`particle_removal_scaling`(기존 3건)는 PRE·λ의 **물리
  입력**(최소 제거입경·워터마크 전처리막·입경 스케일링)으로 곱해짐 — 중복 없음(결정론 물리량 × 확률 λ). 결합식
  PRE(R,조건)=PRE_max(조건)·g(F_D/F_a;R). 근거 노트 동 §6.
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
