# 커리큘럼 — 슬러리 입자 전문가 (slurry-abrasive)

> 규칙: 순서대로 학습. 단원마다 ①출처 있는 지식노트(knowledge/) ②자기시험 3문항+답(EXAMS.md) ③가능하면 수식의 코드 재현.
> 유료 논문은 미러 사이트 활용(사용자 지시 9/5). 출처 없는 수치는 '미검증' 표기.

- [x] Lv1-1 입자 종류별 제조법과 물성(콜로이달/퓸드 실리카, 세리아 소성/습식)
- [x] Lv1-2 입도 분포(D50·D90·LPC)와 측정법(DLS·레이저회절·SPOS)
- [x] Lv2-1 입자 경도·형상과 기계적 제거: Hertz 압입, 입자당 제거 체적 (완료 2026-09-11)
- [x] Lv2-2 입자 농도-MRR 포화 곡선과 접촉 확률 모델 (2026-09-12, knowledge/cmp/abrasive-concentration-mrr-saturation-contact-probability.md — 총괄 게이트 PASS 확인)
- [x] Lv3-1 세리아 화학적 톱니(chemical tooth) 메커니즘과 옥사이드 선택비 (2026-09-13, knowledge/cmp/ceria-chemical-tooth-particle-site-density-facet.md — verify_claims·check_knowledge 둘 다 통과)
- [x] Lv3-2 입자 파라미터 → Kp 기여 정량모델 (2026-09-16, knowledge/cmp/abrasive-parameters-to-kp-contribution-quantitative-model.md — verify_claims·check_knowledge 둘 다 통과. 산출물은 항별 1차 회귀 감사·함수형 AIC 비교·3입자 배율표·D99→Δ 귀속 + 팩 갱신 제안표 + sim/tier2 구현 요청서. sim/·YAML 미수정)

## 캘리브레이션 단원 (ORG.md §7.3 — Lv2 완료 후, G2 이후 활성)
- [x] Cal-1 스펙시트(입도·농도·제타) → 모델 입력 변환 규칙 정의 + 공개 데이터로 검증 (2026-09-19, knowledge/cmp/slurry-abrasive-specsheet-to-model-input-conversion-rules.md — verify_claims·check_knowledge 둘 다 통과. Evonik TDS=Z-avg(강도가중) vs Versum 특허=disc centrifuge(질량가중 D99="99wt.%") 스펙 가중 불일치, Hatch-Choate median 변환(disc centrifuge D99/D50→σg=1.31, D75 3.6% 교차검증)·wt%→vol%(입자밀도 필수)·1차입경 vs 응집체 3규칙, 팩 50nm=Evonik 50 우연일치이나 size_basis 부재로 최대 35% 잠재편차, Kp 곱셈구조 단일조건 식별불가→스윕 필요, data/schema 슬러리 스펙 필드 개정 제안)

## 확장 (Lv4 — 교수급)
- 최신 논문 상시 추적, 기존 모델의 한계 지적 및 개선 제안
- 부모·형제 에이전트와의 결합 모델 설계 리뷰
