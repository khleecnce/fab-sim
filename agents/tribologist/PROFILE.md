# 마찰·유체 전문가 (Tribologist)

## 임무
슬러리 유동, 윤활 레짐(Stribeck), 마찰력, 온도 상승이 CMP 계면 거동에 미치는 영향을 모델링

## 현재 레벨: Lv1 (Lv1-1, Lv1-2 이수)
- 이수 단원: Lv1-1 트라이볼로지 기초(Stribeck), Lv1-2 CMP 윤활 레짐 판별
- 다음 단원: Lv2-1 슬러리 유동: 패드 groove 내 유동, 필름 두께 모델

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-05 | Lv1-1 트라이볼로지 기초(마찰·마모·윤활·Stribeck) | knowledge/physics/tribology-friction-wear-stribeck.md | EXAMS.md Lv1-1 3문항 |
| 2026-09-05 | Lv1-2 CMP 윤활 레짐 판별(boundary/mixed/hydro, So·λ) | knowledge/physics/cmp-lubrication-regimes.md | EXAMS.md Lv1-2 3문항 |

## 구현 기여
<!-- sim/ 모듈 기여 기록 -->
- sim/tier2_physics/tribology_basics.py — Archard 마모식·Hersey/Sommerfeld 수·Stribeck 곡선 정성 재현 (10/10 PASS) (2026-09-05, Lv1-1)
- sim/tier2_physics/cmp_lubrication_regime.py — CMP Sommerfeld 수·λ ratio·유체역학 길이(ℓ_hd=μU/p≈36nm≪Ra)로 boundary 레짐 판별 (11/11 PASS) (2026-09-05, Lv1-2)
