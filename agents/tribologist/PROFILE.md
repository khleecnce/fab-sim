# 마찰·유체 전문가 (Tribologist)

## 임무
슬러리 유동, 윤활 레짐(Stribeck), 마찰력, 온도 상승이 CMP 계면 거동에 미치는 영향을 모델링

## 현재 레벨: Lv2 (Lv1 전체 + Lv2-1 이수)
- 이수 단원: Lv1-1 트라이볼로지 기초(Stribeck), Lv1-2 CMP 윤활 레짐 판별, Lv2-1 슬러리 유동·필름두께 모델(3-D Reynolds)
- 다음 단원: Lv2-2 마찰열과 온도 분포 → 화학반응 속도 결합

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-05 | Lv1-1 트라이볼로지 기초(마찰·마모·윤활·Stribeck) | knowledge/physics/tribology-friction-wear-stribeck.md | EXAMS.md Lv1-1 3문항 |
| 2026-09-05 | Lv1-2 CMP 윤활 레짐 판별(boundary/mixed/hydro, So·λ) | knowledge/physics/cmp-lubrication-regimes.md | EXAMS.md Lv1-2 3문항 |
| 2026-09-05 | Lv2-1 슬러리 유동: 패드 groove 필름두께 모델(3-D Reynolds, Thakurta 2001) | knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md | EXAMS.md Lv2-1 3문항 |

## 구현 기여
<!-- sim/ 모듈 기여 기록 -->
- sim/tier2_physics/tribology_basics.py — Archard 마모식·Hersey/Sommerfeld 수·Stribeck 곡선 정성 재현 (10/10 PASS) (2026-09-05, Lv1-1)
- sim/tier2_physics/cmp_lubrication_regime.py — CMP Sommerfeld 수·λ ratio·유체역학 길이(ℓ_hd=μU/p≈36nm≪Ra)로 boundary 레짐 판별 (11/11 PASS) (2026-09-05, Lv1-2)
- sim/tier2_physics/slurry_film_lubrication.py — z0 무차원 길이스케일 + h_min 파라미터 의존성(속도/압력/점도/다공성/압축성/곡률/웨이퍼자전) 정성 부호 재현 (10/10 PASS) (2026-09-05, Lv2-1)
