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
