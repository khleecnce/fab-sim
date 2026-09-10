# Post-CMP 표면 오염 전문가 (surface-contamination)

## 현재 레벨: Lv3 (진행) — 활성화 게이트는 agents/ORG.md §4
- 부모: cmp-integrator (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv1-1, Lv1-2 (Lv1 완료), Lv2-1, Lv2-2 (Lv2 완료), Lv3-1, Lv3-2 (Lv3 완료 — 6/6 완주)
- 다음 단원: Cal-1 (G2 이후 활성, 고객 TXRF/ICPMS 스키마 + 로트별 보정 파라미터) · Lv4 확장

## 역할
CMP 후 웨이퍼 표면에 남는 금속 이온(Cu·Fe·K·Ca·Al)·이온성 잔류·유기 잔류의 발생원·측정·허용치·제거. 세정 화학과 슬러리 화학의 연결고리

## 선행 지식 (부모에게 상속)
- [[../../knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation]]
- [[../../knowledge/cmp/colloid-zeta-dlvo-slurry-stability]]

## 실데이터 책임 (ORG.md §7.3)
고객 TXRF/ICPMS 데이터 스키마 + 슬러리 로트별 오염 기여 보정 파라미터

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
| 단원 | 노트 | 검증 | 이수일 |
|---|---|---|---|
| Lv1-1 표면 오염 종류와 발생원 | [[../../knowledge/cmp/post-cmp-metallic-contamination-sources]] | verify_claims PASS(출처6건 실존) · check_knowledge PASS · §6 verify PASS | 2026-09-06 |
| Lv1-2 측정 기법 TXRF·VPD-ICPMS·SIMS·XPS | [[../../knowledge/cmp/wafer-surface-metal-detection-txrf-vpdicpms-sims-xps]] | verify_claims PASS(출처2건 실존·코드1블록 통과) · check_knowledge PASS | 2026-09-06 |
| Lv2-1 금속 오염이 소자에 미치는 영향(ITRS/IRDS 허용치) | [[../../knowledge/cmp/metal-contamination-device-impact-irds-limits]] | verify_claims PASS(출처4건 실존·코드1블록 통과) · check_knowledge PASS | 2026-09-07 |
| Lv2-2 흡착 메커니즘과 제거 화학(IEP·킬레이트 logK·DHF·오존수·RCA·막질별 레시피) | [[../../knowledge/cmp/post-cmp-adsorption-cleaning-chemistry]] | verify_claims PASS(출처22건 실존·코드1블록 통과) · check_knowledge PASS · §6 verify (A)Davies (B)K′(pH) (C)IEP 부호 PASS | 2026-09-07 |
| Lv3-1 최신 리뷰(저농도 잔류 제어·Co/Ru 갈바닉·PVA 브러시 cross-contamination·IRDS 2024) | [[../../knowledge/cmp/low-level-metal-cobalt-ruthenium-cross-contamination]] | verify_claims PASS(출처24건 실존·코드1블록 통과) · check_knowledge PASS · §6 verify (A)갈바닉 방향/크기 불일치 명시 (B)Co/Cu 수산화물 전이 pH (C)IRDS 배수 PASS | 2026-09-08 |
| Lv3-2 잔류 금속 예측 모델 골격(경쟁 Langmuir·SCM·킬레이트 분기·세정 η) + 문헌값 대조 | [[../../knowledge/cmp/post-cmp-residual-metal-prediction-langmuir-scm]] | verify_claims PASS(출처5건 실존·코드1블록 통과, 1차 원문 PDF 5건 확보: Loewenstein 1998/1999·Seo 2001·Martin 1999·Sun 2007 학위논문) · check_knowledge PASS · §6 verify (A)Cr [M]지수 0.74 vs 0.73 일치·pH지수 불일치 명시 (B)비정전 SCM 8 %/15 % vs 실측 50/100 % 불일치→Boltzmann |ψ|≈31 mV 정합 (C)CA f_free·Seo K/IRDS 50·1500배·DHF η 0.98 PASS | 2026-09-09 |

## 구현 요청 (소프트웨어 부문)
- 현재 없음. Lv1-1은 발생원 분류·정성 모델 중심이라 sim/ 편입 대상 수식 없음. (Cu²⁺ Boltzmann 정전흡착 정량 모델은 Lv2-2 세정화학에서 흡착등온선으로 확장 시 재검토.)
- Lv1-2도 측정기법 비교·검출한계 계산이 중심이라 sim/ 편입 대상 수식 없음. TXRF/VPD-ICPMS/SIMS/XPS 검출한계 오더 비교표는 향후 cmp-data-engineer가 §7.3 고객 데이터 스키마 설계 시 "어떤 기법으로 측정된 값인지" 태그가 필요하다는 근거로 참조할 것.
- Lv2-1도 GOI 파괴전압 데이터·ITRS/IRDS 허용치 표가 중심이라 sim/ 편입 대상 수식은 없음. 다만
  §5의 "1×10¹⁰ atoms/cm² = ITRS FEP 스펙"은 향후 defect-scientist가 결함/수율 진단 모델을 만들
  때 판정 임계값 상수로 참조할 근거가 된다 — 구현 시점에 이 노트를 인용할 것.
- ~~**[Lv2-2 요청 1 · 우선순위 중] `chelation_conditional_logK(ligand, metal, pH, I)`** — 순수함수. 입력: 리간드(EDTA/시트르산)·금속(Fe³⁺/Cu²⁺/Ca²⁺)·pH·이온세기. 내부: (1) MINTEQ `minteq.v4.dat`(NIST46.2 태그) I=0 logK와 양성자화 logβₙ 테이블, (2) Davies 식(A=0.509)으로 I 보정, (3) Ringbom α_H로 조건부 K′(pH). 근거노트: knowledge/cmp/post-cmp-adsorption-cleaning-chemistry.md §4·§6(A)(B). 검증문헌값: Fe–EDTA logK(I=0.1)=25.1, Cu–EDTA 18.7~18.8 (Kontoghiorghes 2020 PMC7349684, Palden 2020 PMC9057912) — Davies 예측 25.13/18.79로 0.05 이내. K′(pH) 단조증가·Fe>Cu>Ca 순서·pH3 시트르산–Ca logK′<0 을 테스트로. 용도: Lv3-2 잔류금속 예측 모델의 "유리 이온 분율" 입력.~~ ✅ 2026-09-07 완료 — `sim/tier2_physics/chelation_surface_charge.py` (커밋해시는 나중에 채움, S23)
- ~~**[Lv2-2 요청 2 · 우선순위 중] `oxide_surface_charge_sign(oxide, pH)` + IEP 테이블** — SiO₂ 2.0(Brugnoli 2023 PMC10116594), CeO₂ 6.8(동, 실측범위 5.21–9.40 Ederer 2025 PMC12519946), α-Al₂O₃ 9.5(Zhang 2024 PMC11462379). 반환: 부호(+/0/−)와 pH−IEP. Lv1-1 Boltzmann 정전흡착(§6(C))의 ζ 부호 입력으로 연결하고, 슬러리(colloid-zeta 노트)와 세정 pH에서 입자–웨이퍼 정전 인력/반발 판정에 공용. 근거노트 §3·§6(C). 검증: DHF 0.5 wt% pH≈1.90(HF pKa 3.17)에서 세 산화물 +, pH 11에서 모두 −, pH 5에서 CeO₂+/SiO₂−.~~ ✅ 2026-09-07 완료 — `sim/tier2_physics/chelation_surface_charge.py` (커밋해시는 나중에 채움, S23)
- **[Lv3-1 요청 1 · 우선순위 중] `galvanic_pair_direction(metalA, metalB, E0_table=None)` + `hydroxide_transition_pH(metal, C_mol_L)`** — 순수함수 2개.
  (1) 표준환원전위 표(CRC Vanýsek: Co −0.28, Cu 0.3419, Ru 0.455, Ti −1.630, Ta₂O₅/Ta −0.750, WO₃/W −0.090 V)로 어느 금속이 양극(용해)인지와 ΔE°를 반환.
  (2) minteq.v4.dat PHASES의 M(OH)₂ + 2H⁺ = M²⁺ + 2H₂O log K(Cu 8.674, Co 13.094)로 농도 C에서 수산화물 석출 시작 pH* = (logK − log C)/2 반환.
  근거노트: knowledge/cmp/low-level-metal-cobalt-ruthenium-cross-contamination.md §3.1·§3.3·§6(A)(B). 검증문헌값: Cu/Co ΔE°=0.62 V(Co 양극), Ru/Cu 0.113 V(Cu 양극);
  100 ppm Cu pH*=5.74(Bisht 2022 관찰 ≈6, ±0.5), Co 7.93(Cu보다 2.0~2.5 높음). docstring에 "ΔE_corr 크기는 표준전위로 예측 불가(Lee 2021 4배, Seo 2019 1/15)"를 명기.
  용도: Lv3-2 잔류 예측 모델에서 "이온 상태(정전흡착·브러시 흡수) vs 입자 상태(brush loading)" 분기와 갈바닉 용해 방향 입력.
- (주의) 두 함수 모두 금속 가수분해·수산화물 침전·박막 실제 IEP는 미반영 — 노트 §7 한계 그대로 docstring에 명기할 것.
- ~~**[Lv3-2 요청 1 · 우선순위 상] `competitive_langmuir_surface(metals, pH, sigma0=3e12, K_H=1e3)`**~~ ✅ 2026-09-10 완료
  (software/BACKLOG.md S41, `sim/tier2_physics/competitive_metal_langmuir.py`, 커밋 986d8cb) — Loewenstein 1999
  Eq.22 재현, 테스트 5건(Cr [M]지수 0.73±0.05·자리분율 0.4%·pH3·10nM Cu 오더·단일금속 항등성·다중금속 Θ 일관성).
  engine 미등록(Recipe 스키마 부재, 기존 tier2_physics 순수함수들과 동일 지위). 순수함수. 입력: {금속: (K_i [L/mol], C_i,free [mol/L])}, pH.
  식: σ_i = σ0·K_i·C_i/(1 + K_H·10^-pH + Σ_j K_j·C_j) (Loewenstein·Charpin·Mertens 1999 Eq.22, doi:10.1149/1.1391670). 반환: {금속: atoms/cm²}와 총 점유율 Θ.
  근거노트: knowledge/cmp/post-cmp-residual-metal-prediction-langmuir-scm.md §2·§6(A). 검증문헌값: σ0 = 1/(3.00e-13 cm²/atom) = 3e12(자리분율 0.4 %),
  K_Cr≈1e6·K_H≈1e3에서 pH 3·pM 8→5의 [M] 지수 0.74(문헌 Table VI 0.73±0.07), pH 3·10 nM → ≈1.5e10 atoms/cm²(Table I Cu 0.9~1.7e10 오더).
  docstring에 "pH 지수는 −0.12로 문헌 −0.39와 불일치(타금속 경쟁항·K 오더값), Cu·Fe·K·Ca의 K_i는 미확보 — Cal-1 회귀 대상"을 명기.
- **[Lv3-2 요청 2 · 우선순위 중] `residual_after_clean(sigma_ads, step)`** — η 테이블: DIW 린스 η≈0(K·Ca, Seo 2001; Cu pH 6 흡착분 부분 비가역 Sun 2007),
  CA 100 ppm 린스 η = 1 − 7.53e10/4.32e13 (Sun 2007 Fig.4.7), DHF 3 nm η = 1 − 2e10/1e12 = 0.98 (Seo 2001 doi:10.1023/A:1011242900843 Fig.2, PE-TEOS K).
  근거노트 §5·§6(C). 브러시·메가소닉·유량 의존은 미포함(노트 §7)임을 docstring에.
- **[Lv3-2 요청 3 · 우선순위 중] 체인 조립 `predict_residual_metal(recipe_like)`** — 순서: free_metal_fraction(Lv2-2) → hydroxide_transition_pH(Lv3-1 요청, 이온/입자 분기)
  → competitive_langmuir_surface 또는 SCM(Sun 2007 Table 4.1: 2 OH/nm², pKa1 5.9, pK1 4.35, pK2 8.22) × boltzmann_surface_enrichment(Lv1-1, S15) → residual_after_clean.
  검증: 노트 §6(B) — 비정전 SCM은 pH 6 흡착 8.4 %로 실측 50 %에 미달, Boltzmann 11배(|ψ|≈31 mV, ζ −17 mV와 방향 정합)를 곱해야 함을 테스트로 고정.
  Recipe에 pH·킬레이트·금속농도 필드가 없으므로(ARCHITECTURE §4 스키마 부채) engine 등록은 하지 말고 순수함수 라이브러리로.
- **[Lv3-2 정정 요청 · 우선순위 상] `metal_contamination_surface.py` SEO2001 상수 출처 정정** ✅ 2026-09-09 완료
  (software/BACKLOG.md S38, `SEO2001`→`FE_ORDER_OF_MAGNITUDE_UNVERIFIED` 개명 + "출처 불명" 정직 표기,
  하위호환 별칭 유지, 커밋 ee4aff5) — Seo 2001(doi:10.1023/A:1011242900843) 원문 확인 결과 W-CMP Fe 1.5e12/1e11 수치가 본문에 없음(논문은 KOH 슬러리 산화막 CMP의 K·Ca: PE-TEOS K≈1e12, O3-BPSG K≈3e13, dHF 3 nm 후 ≈2e10). 코드 주석·docstring의 출처를 '출처 불명·미검증(2차 요약 오귀속)'으로 바꾸고, 필요하면 K 값(1e12, Seo 2001 Fig.1b·2 판독)으로 교체할 것. 근거: knowledge/cmp/post-cmp-residual-metal-prediction-langmuir-scm.md §5.1, Lv1-1 노트 §2 추기.
