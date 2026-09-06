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
