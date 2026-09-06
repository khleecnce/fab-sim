# 자기시험 — 시험 웨이퍼 전문가 (wafer-type)

> 단원 이수 시 3문항 + 모범답안을 여기에 추가한다. 답안에는 출처를 단다.

## Lv1-1/Lv1-2: NPW/PTW 기초 (2026-09-06)

**Q1. NPW의 표준 측정점 체계는 몇 점이며 어떤 구조인가?**
A1. 49점 polar 배열 — center 1점 + 3개 동심원 링에 각각 8/16/24점(1+8+16+24=49).
출처: US6922603B1 특허 명세("a typical 49-point array... a center point, and three
concentric rings"), [[uniformity-metrics-definitions-standards]] §5에서 1차 확인.

**Q2. Effective density 모델(MRS99 eq.1)에서 국소 제거율은 유효밀도와 어떤 관계인가?
ρ_eff가 0.2→0.8로 4배 증가하면 제거율은 어떻게 변하는가?**
A2. RR_up(x,y) = K/ρ_eff(x,y), 즉 반비례. ρ_eff가 4배 커지면 RR은 1/4로 준다
(K=200 nm/min 예시에서 1000→250 nm/min, 본 노트 §4 python verify 블록에서 assert로
확인). 출처: Boning et al., "Pattern Dependent Modeling for CMP Optimization and
Control," MRS 1999, eq.1(1차, PDF 원문 확인).

**Q3. Kim & Seo(2002)가 보고한 STI-CMP 패턴/비패턴 웨이퍼 간 상관계수는 얼마이며,
이 수치를 얼마나 신뢰할 수 있는가?**
A3. r약 0.7109로 보고됨(검색엔진 스니펫 발췌). 그러나 원문을 확보하지 못해(미러 사이트
미러 5종 전부 무응답, OA 경로도 전부 실패) 정의(피어슨 r인지 R2인지)조차 불확실 —
미검증, 2차 인용으로만 사용 가능. NPW to PTW 예측이 완전하지 않다(1.0이 아니다)는
정성적 사실의 근거로만 쓰고, 정량 결론(예: "71% 설명력")은 도출하지 않는다.

## Lv2-1: NPW→PTW 예측 실패의 물리 (확장 GW 모델, 2026-09-06)

**Q1. 확장 GW 모델(Vasilev et al. 2011)에서 up-region과 down-region의 유효곡률
κ_U, κ_D는 각각 무엇의 함수이며, NPW(h=0)에서는 왜 이 항이 사라지는가?**
A1. κ_U = κ_asperity + 4αh/line², κ_D = κ_asperity − 4αh/space² (eq.5). h(step height)와
구조 크기(line/space)의 함수다. NPW는 패턴이 없어 h=0이므로 두 식 모두 κ_asperity로
수렴 — 즉 패턴 크기·피치 의존성을 담는 항 자체가 원리적으로 관측되지 않는다.
출처: doi.org/10.1109/TSM.2011.2107756 §II eq.2,5 (1차, 원문 확인).

**Q2. 밀도만 반영한 basic GW 모델 대비 피치까지 반영한 extended GW 모델이 실측 데이터에서
얼마나 오차를 줄였는가(density field, step-height RMS 기준)?**
A2. Basic GW 19nm → Extended GW 13nm (약 32% 개선). Pitch field에서는 20.5nm → 13.5nm
(약 34% 개선). 출처: (Vasilev et al. 2011) Table I, §III 서술 — 1차 원문 수치 그대로 인용,
재계산 아님(digitize 안 함).

**Q3. h→0 극한에서 RR_U와 RR_D가 RR0로 수렴한다는 것을 코드로 어떻게 검증했으며, 이게
"NPW가 언제 PTW를 잘 예측하는가"에 대해 시사하는 바는?**
A3. eq.27을 그대로 구현해 h=1e-6(사실상 0)일 때 RR_U, RR_D 둘 다 RR0(=185 nm/min, 1%
이내)로 수렴함을 assert로 확인(본 노트 §3 python verify). 시사점: NPW가 PTW를 잘
예측하는 구간은 오직 **국소평탄(local planarity, h≈0)이 이미 달성된 이후**뿐이며,
평탄화 초기 단계(step height가 큰 구간)에서는 원리적으로 NPW만으로 예측 불가.

## Lv2-2: 측정 기법의 NPW/PTW 적합성 (SE·스타일러스·AFM·XRF, 2026-09-07)

**Q1. 블랭킷(NPW)에서 잘 쓰던 분광 엘립소미터를 패턴 웨이퍼(PTW)에 그대로 쓰면 왜 두께가 안 나오는가?
정량 근거를 들어 설명하라.**
A1. 세 가지 물리적 제약. (1) 스팟 vs 패드: 제품/패턴 웨이퍼는 0.1–10 µm 피처로 덮여 있고 측정 패드는 통상
100 µm×100 µm(US7095511). SE는 70° 경사 입사라 빔이 1/cos70° = 2.92배 늘어나 50 µm 빔이 146 µm 타원이 되어
패드를 벗어난다(25 µm 마이크로스팟이면 73 µm로 들어감). (2) 혼입광·회절: 패드 밖 패턴에서 반사·회절된 빛이
검출기에 섞여 Δ를 오염 — KLA US9574992는 40 µm 타깃에서 pupil/field stop으로 이를 차단해야 0.02 Å 매칭이
된다고 서술. (3) 모델: 스팟 안에 격자가 들어오면 단일막 Fresnel이 아니라 RCWA/Mueller 스캐터로메트리로
피팅해야 한다(Garcia-Caurel et al. 2013, arxiv.org/abs/1210.1076). 따라서 PTW의 SE 두께는 "밀도가 명시된
특정 패드에서의 값"이지 NPW의 "막 두께"와 같은 물리량이 아니다.
출처: 본 노트 §1–§2, verify (B).

**Q2. Cu·W 같은 금속막에 SE로 두께를 못 재는 이유를 침투깊이로 정량화하고, 그렇다면 NPW와 PTW에서
금속막 두께/높이는 각각 무엇으로 재는가?**
A2. Cu의 소광계수 k=3.408(632.8 nm, Johnson & Christy 1972, doi.org/10.1103/PhysRevB.6.4370)에서 강도 침투깊이
d_p = λ/(4πk) ≈ 14.8 nm. 50 nm 막을 왕복하면 기판 정보가 e^{−100/14.8} ≈ 0.1%만 남아 Horiba·Woollam의 "약 50 nm
이상은 광학상수만, 두께 불가" 문턱과 정합(verify (A)). CMP 후 Cu(수백 nm)·W는 불투명. NPW에서는 XRF(스팟
40 mm, Cu 1 µm까지 비선형 2.3%로 선형 영역 — NIST XCOM μ/ρ=52.55 cm²/g) 또는 EC/4PP로 "두께"를 재고,
PTW에서는 스타일러스(넓은 구조의 dishing/erosion 단차)·AFM(sub-µm 참조)으로 "높이차"를 잰다. XRF를 PTW에
쓰면 다이 여러 개가 평균된 패턴밀도 가중 평균 두께만 나온다.
출처: 본 노트 §2.2, §5, verify (A)(E).

**Q3. 스타일러스와 AFM으로 PTW 단차를 잴 때 각각의 지배적 오차원인과 정량 규칙을 말하라.**
A3. 스타일러스: NIST 기준 팁 반경 1.52 ± 0.15 µm → 폭 w < 2R = 3.04 µm 트렌치는 바닥에 못 닿아 깊이 과소평가;
팁 크기 효과의 부호는 라인/스페이스 비에 의존(peak 폭 > valley 폭이면 Ra 과소, 반대면 과대 — Renegar et al.
2012, 초록만). 단차 측정계 표준불확도는 NIST Table 3 계수로 30 nm 단차 0.023X ≈ 0.69 nm, 1 µm 단차 0.0025X = 2.5 nm.
AFM: 픽셀 피치가 지배 — 스텝 폭에 최소 4픽셀 필요(Ahn et al. 2019, arxiv.org/abs/1909.09508). 116 nm 폭이면
피치 ≤ 29 nm, 즉 40 µm 스캔은 1024 px여도 39 nm 피치라 실패(폭 최대 11배 과대). 높이는 강건(184 vs SEM
187.3 nm, 2% 이내). 팁 반경 30 nm는 30 nm까지만 설명. 따라서 PTW에서 sub-µm dishing 프로파일은 스캔 크기를
줄이거나 픽셀 수를 늘려 피치를 맞춘 AFM으로, 큰 피치 어레이·패드는 스타일러스로 잰다.
출처: 본 노트 §3–§4, verify (C)(D).
