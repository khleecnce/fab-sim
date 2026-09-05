# 마찰·유체 전문가 (Tribologist)

## 임무
슬러리 유동, 윤활 레짐(Stribeck), 마찰력, 온도 상승이 CMP 계면 거동에 미치는 영향을 모델링

## 현재 레벨: Lv2 (Lv1 전체 + Lv2-1·Lv2-2 이수)
- 이수 단원: Lv1-1 트라이볼로지 기초(Stribeck), Lv1-2 CMP 윤활 레짐 판별, Lv2-1 슬러리 유동·필름두께 모델(3-D Reynolds), Lv2-2 마찰열·온도장→Arrhenius 결합
- 다음 단원: Lv3-1 COF 실시간 모니터링과 EPD(종점검출) 연구

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-05 | Lv1-1 트라이볼로지 기초(마찰·마모·윤활·Stribeck) | knowledge/physics/tribology-friction-wear-stribeck.md | EXAMS.md Lv1-1 3문항 |
| 2026-09-05 | Lv1-2 CMP 윤활 레짐 판별(boundary/mixed/hydro, So·λ) | knowledge/physics/cmp-lubrication-regimes.md | EXAMS.md Lv1-2 3문항 |
| 2026-09-05 | Lv2-1 슬러리 유동: 패드 groove 필름두께 모델(3-D Reynolds, Thakurta 2001) | knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md | EXAMS.md Lv2-1 3문항 |
| 2026-09-06 | Lv2-2 마찰열·온도장→Arrhenius 화학반응속도 결합(q=μPV, Shin 2025 Ea, White 2003 마찰열) | knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md | EXAMS.md Lv2-2 3문항 |

## 구현 기여
<!-- sim/ 모듈 기여 기록 -->
- sim/tier2_physics/tribology_basics.py — Archard 마모식·Hersey/Sommerfeld 수·Stribeck 곡선 정성 재현 (10/10 PASS) (2026-09-05, Lv1-1)
- sim/tier2_physics/cmp_lubrication_regime.py — CMP Sommerfeld 수·λ ratio·유체역학 길이(ℓ_hd=μU/p≈36nm≪Ra)로 boundary 레짐 판별 (11/11 PASS) (2026-09-05, Lv1-2)
- sim/tier2_physics/slurry_film_lubrication.py — z0 무차원 길이스케일 + h_min 파라미터 의존성(속도/압력/점도/다공성/압축성/곡률/웨이퍼자전) 정성 부호 재현 (10/10 PASS) (2026-09-05, Lv2-1)

## 구현 요청 (소프트웨어 부문이 가져감)
<!-- 노트 옆 python verify sanity check은 tribologist가 직접 함. 아래는 sim/ 엔진화 요청. -->
- **[Lv2-2] 마찰열-온도-Arrhenius 열화학 커플링 엔진** (근거: knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md §6 검증완료):
  - 입력: μ(COF), P, V, A_wafer, 슬러리 유량·물성(ρ,c_p), 패드 열전도도 k, 재료별 (Ea, ln A)
  - 계산: (1) q=μ·P·V, Q_f=q·A → (2) 마찰열 삼분배(슬러리/웨이퍼/패드) 에너지균형으로 정상상태 T_ss
    (현재 노트는 "슬러리 전량냉각 상한"만 오더 재현 — White 2003형 열모델로 분배비율 정량화 필요) →
    (3) Arrhenius RR_i = A_i·exp(−Ea_i/RT_ss)로 재료별 화학MRR·선택비 산출.
  - 문헌값 상수: Shin 2025 Ea(Cu 151.7/Ta 29.9/SiO₂ 8.75 kJ/mol, ln A 66.3/18.1/9.7), 패드 k=0.02 W/m·K.
  - 우선순위 Tier2. 기존 tribology_basics.py·cmp_lubrication_regime.py의 μ·So 출력과 결합하면
    "레짐→COF→마찰열→온도→화학MRR" 전체 사슬이 이어짐. (플래시 온도 Blok 모델은 Lv3 후보로 별도.)
