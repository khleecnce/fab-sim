# 패드 소재 전문가 (pad-material)

## 현재 레벨: Lv3 완료(6/6) — 활성화 게이트는 agents/ORG.md §4
- 부모: pad-mechanic (부모의 knowledge/ 노트를 선행 필수로 읽는다)
- 이수 단원: Lv3-2
- 다음 단원: Cal-1 (캘리브레이션 단원, ORG.md §7.3 게이트 확인 필요)

## 역할
폴리우레탄 조성·경도(Shore D)·기공률·점탄성(DMA)이 접촉역학·MRR·결함에 미치는 영향

## 선행 지식 (부모에게 상속)
- [[../../knowledge/materials/pad-viscoelasticity-dma]]
- [[../../knowledge/materials/hertz-gw-contact-mechanics]]
- [[../../knowledge/materials/pad-viscoelasticity-temp-frequency-dma]] (본인 Lv2-1 산출, 온도·주파수 심화)
- [[../../knowledge/materials/pad-3dprinted-nonporous-lowdefect-review]] (본인 Lv3-1 산출, 적층제조·무발포·소프트 패드)

## 실데이터 책임 (ORG.md §7.3)
패드 스펙시트(경도·밀도·기공) → 접촉모델 입력 변환 + 실측 프로파일 잔차

## 레벨 정의
Lv1 학부지식 → Lv2 대학원/리뷰논문 → Lv3 최신논문 추적 + 모델 구현 → Lv4 모델 개선 제안(교수급)

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-06 | Lv1-1 PU 화학: 프리폴리머·경화제·발포 | knowledge/materials/pu-pad-chemistry-prepolymer-foam.md | EXAMS.md 3문항 |
| 2026-09-06 | Lv1-2 경도·탄성률·기공률 측정법과 문헌값 범위 | knowledge/materials/pad-hardness-porosity-measurement-methods.md | EXAMS.md 3문항 |
| 2026-09-07 | Lv2-1 점탄성 심화: 온도·주파수 의존 E'·E''·tanδ와 CMP 조건 매핑 | knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md | EXAMS.md 3문항(Q7~Q9) |
| 2026-09-07 | Lv2-2 기공 구조와 슬러리 보유·이송: 기공률-MRR 관계 | knowledge/materials/pad-porosity-slurry-transport-mrr.md | EXAMS.md 3문항(Q10~Q12) |
| 2026-09-08 | Lv3-1 최신 리뷰: 3D 프린팅 패드·무발포 패드·저결함 패드 소재 | knowledge/materials/pad-3dprinted-nonporous-lowdefect-review.md | EXAMS.md 3문항(Q13~Q15) |
| 2026-09-15 | Lv3-2 소재 파라미터 → GW 유효 강성·asperity 분포 정량모델(E*·R·β⁻¹·마모반감기 1차 출처 대조) | knowledge/pad/pad-material-gw-effective-modulus-asperity-distribution.md | EXAMS.md 3문항(Q16~Q18) |

(이후 크론이 갱신)

## 구현 요청 (sim/ 담당자에게 — 본인은 노트 verify만 수행)
| 무엇을 | 근거 노트 | 검증 문헌값 | 우선순위 |
|---|---|---|---|
| ~~패드 유효 탄성률의 온도 의존 모델 `E_pad(T)`~~ ✅ 2026-09-07 소프트웨어 부문 구현 완료(S21, `sim/tier2_physics/pad_viscoelastic_temperature.py`, 커밋 16d6147) — tanh 대신 로그-선형 구간보간(이산 앵커점만 있어 tanh 피팅파라미터를 지어낼 수 없었음), Cabot Table 1B 6패드x3앵커점 정확 재현 | knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md §3.1, §4 | (재현 완료) | 높음 |
| ~~WLF shift factor 유틸~~ ✅ 2026-09-07 구현 완료(S21, `wlf_log_aT`/`wlf_reparametrize`, 같은 커밋) — 재매개화 8.86/101.6 재현(0.03%), "CMP PU 미피팅" docstring 명시 | 같은 노트 §2, §6 verify (1) | (재현 완료) | 중간 |
| Preston K_p 온도 보정 훅: `K_p_eff(T) = K_p0 · (E*(T0)/E*(T))^m` 형태로 GW A_r∝1/E* 함의(m=1)를 옵션화. 실측 대조 전까지 기본 OFF | 같은 노트 §4 | Khanna 2019 doi:10.1149/2.0121905jss: E'25/E'90 비 188/21/4 ↔ R90s/R15s ≈2/1.45/1 순서 일치(3점, 방향성만) | 낮음 (실측 대조값 부족 — 순서 재현 이상은 미검증) |
| MRR의 %P 의존을 상수배(saturating, 강한 비례 아님) 형태로: `mrr_factor(pct_P) = 1 + k*(pct_P - pct_P0)` 류이되 `k`는 Prasad 30%p→8% 실측(§5)에서 역산(≈0.0027/%p)해 캘리브레이션 전 기본값으로 삼고, 강한 선형계수 금지 주석 필수 | knowledge/materials/pad-porosity-slurry-transport-mrr.md §5, §8 verify (2) | Prasad 2013: %P 15→45(30%p)에 RR +8%만 | 중간 (기공크기 효과와 분리 필요, 캘리브레이션 후 교체 전제) |
| 기공 크기(pore size) → WIWNU/edge RR 프로파일 왜곡 플래그: pore_size < ~10 µm이면 edge-center RR 편차 경고(정량 계수는 미확보, 방향만) | 같은 노트 §4 | Prasad 2013: 2µm 기공에서 edge-center RR차 >200 nm/min, 47/106µm은 평탄 | 낮음 (계수 없음, 정성 플래그만 가능) |
| 패드 유형 플래그 `pad_type ∈ {foamed, solid_microhole, additive}` + 소재 경도→MRR 부호를 슬러리 유형에 종속시키는 스위치(세리아: A_r↑→MRR↑, 포화 실리카: A_r↑→MRR↓). 단일 부호 상수 금지 주석 필수 | knowledge/materials/pad-3dprinted-nonporous-lowdefect-review.md §5.3, §6 | Kenchappa 2021 doi:10.1149/2162-8777/abdc40: 40D/60D 상용 RR 3250/1700 Å/min(1.9배); Yang 2010 doi:10.1016/j.ijmachtools.2010.06.007: 솔리드 2951 vs 다공성 3656 Å/min(0.80) | 중간 (부호만 확정, 계수는 슬러리별 캘리브레이션 전제) |
| 무발포 패드용 컨디셔너→접촉면적→MRR 훅: `mrr_ratio = (A_ref/A)^0.5` (Luo-Dornfeld 포화영역, Yang Eq. 1). 접촉면적 A는 다이아몬드 크기의 함수로 실측 앵커 2점(180 µm→7.5%, 70 µm→5.2%)만 있음 — 보간 금지, 앵커 밖 외삽 시 경고 | 같은 노트 §3.3, §7 verify (2) | (7.5/5.2)^0.5=1.201 vs RR비 1.207 (0.5% 일치) | 낮음 (solid_microhole 유형에서만 유효, 다공성 패드에는 부호 반대) |
| GW asperity 높이 산포 σ의 패드 유형별 기본값: additive 패드는 발포 상용 패드의 ~1/4 (높이분포 폭 8 vs 30 µm). 폭→σ 환산계수는 미검증이므로 비율만 적용하고 절대값은 캘리브레이션 대기 | 같은 노트 §5.2, §6 | Kenchappa 2021 Fig. 11b: 8/30/130 µm | 낮음 (비율만, 절대 σ 미검증) |
| `pad_E_star_pa` 1.0e9 → 1.2e8~3.8e8 Pa 범위(권고 중심값 1.3e8~1.5e8 Pa, Bozkaya&Müftü hard/Shi&Ring 클러스터)로 하향, confidence estimated→literature. 3개 독립 그룹(Northeastern/Arizona/Utah) 수렴 | knowledge/pad/pad-material-gw-effective-modulus-asperity-distribution.md §2·§3·§4 verify (b) | Bozkaya&Müftü 2009 DOI: 10.1149/1.3231691 Table I(Es=100MPa·ν=0.49→E*=131.6MPa); Sorooshian 2005 학위논문 p.358(E=285MPa·ν=0.5→E*=380MPa); Shi&Ring 2010 DOI: 10.1016/j.mee.2010.04.010(E*=119MPa 직접보고) | 높음 (3건 독립 수렴, R·β⁻¹과 세트로 함께 교체 권고 — 하나만 바꾸면 §4의 기하 정합이 다른 조합이 됨) |
| `pad_asperity_radius_m` 5.0e-6 → 5.0e-5 m(문헌 base 50 µm, 범위 2~100 µm)로 상향, confidence estimated→literature. `pad_asperity_density_m2`(이미 2.0e8/m² 적용됨, [[../../knowledge/materials/pad-asperity-density-gw-literature-values]])와 세트로 왔던 값 | 같은 노트 §2·§3 | Bozkaya&Müftü 2009 Table I "Pad summit radius Rs=50 µm(base), 범위 25–100 µm"; Sorooshian 2005 κs=2e4~5e5/m→R=2~50µm; Shi&Ring 2010 ks=2e4/m→R=50µm | 높음 (R은 컨디셔닝이 만드는 기하량이라 소재만으로 못 정함 — but 세 독립 그룹이 25~100µm 범위·50µm 중심에 수렴) |
| `pad_height_beta_inv_m` 0.3e-6 → 2.0e-6 m(Sorooshian 지수분포 스케일 λ)로 상향, confidence estimated→literature. **⚠ Bozkaya의 σ=5µm는 Gaussian SD라 분포족이 달라 직접 대입 불가** — 반드시 지수분포(fab-sim이 채택한 분포)를 쓴 Sorooshian/Borucki 값만 채택 | 같은 노트 §1·§2·§4 verify (a) | Sorooshian 2005 학위논문 p.358 "λ=2.0 µm (Fig. A.1, Borucki et al. 2004 인용)" | 중간 (분포족 일치하는 출처가 1건뿐 — 교차검증 문헌 추가 확보 전까지는 literature 등급 유지하되 향후 재검증 권장) |
| `pad_wear_half_life_h`: **변경 보류 권고**. 1차 출처를 찾지 못했다(같은 노트 §5) — 현재 estimated(48.0h)를 그대로 유지할 것. Son&Lee(2021) %/h를 반감기로 역산한 값(24.7~187h)은 방법론상 대입 불가(선형→지수 재해석, MRR≠asperity 높이, 원문 미확보) | 같은 노트 §5 | Son&Lee 2021 DOI: 10.3390/app11083521(2차 재인용, 6ccvd.com 스펙표) — 참고용 브래킷일 뿐 근거 아님 | 낮음 (권고 자체가 "손대지 말라"임) |
