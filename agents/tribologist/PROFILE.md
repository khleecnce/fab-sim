# 마찰·유체 전문가 (Tribologist)

## 임무
슬러리 유동, 윤활 레짐(Stribeck), 마찰력, 온도 상승이 CMP 계면 거동에 미치는 영향을 모델링

## 현재 레벨: Lv3 완주 (커리큘럼 6/6 이수) — CURRICULUM.md 확장(Lv4) 대기
- 이수 단원: Lv1-1 트라이볼로지 기초(Stribeck), Lv1-2 CMP 윤활 레짐 판별, Lv2-1 슬러리 유동·필름두께 모델(3-D Reynolds), Lv2-2 마찰열·온도장→Arrhenius 결합, Lv3-1 COF 실시간 모니터링·마찰기반 EPD, Lv3-2 CMP 마찰계수 실측(Lai 2001 MIT thesis)·hydroplaning 미도달·Preston 상수 붕괴
- **M1(MILESTONES.md 지식병목) 게이트: slurry-chemist 6/6(2026-09-08) + tribologist 6/6(2026-09-08) → M1 완결 조건 충족.**
- 다음: Lv4(교수급) 확장 단원 — 최신 논문 상시 추적·기존 모델 한계 지적. G1 이후 Cal-1(캘리브레이션) 단원도 대기.

## 이수 기록
| 날짜 | 단원 | 산출 노트 | 자기시험 |
|---|---|---|---|
| 2026-09-05 | Lv1-1 트라이볼로지 기초(마찰·마모·윤활·Stribeck) | knowledge/physics/tribology-friction-wear-stribeck.md | EXAMS.md Lv1-1 3문항 |
| 2026-09-05 | Lv1-2 CMP 윤활 레짐 판별(boundary/mixed/hydro, So·λ) | knowledge/physics/cmp-lubrication-regimes.md | EXAMS.md Lv1-2 3문항 |
| 2026-09-05 | Lv2-1 슬러리 유동: 패드 groove 필름두께 모델(3-D Reynolds, Thakurta 2001) | knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md | EXAMS.md Lv2-1 3문항 |
| 2026-09-06 | Lv2-2 마찰열·온도장→Arrhenius 화학반응속도 결합(q=μPV, Shin 2025 Ea, White 2003 마찰열) | knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md | EXAMS.md Lv2-2 3문항 |
| 2026-09-06 | Lv3-1 COF 실시간 모니터링·마찰기반 EPD(전단력→토크→모터전류, Li 2017 PMC6190379, Headley 2019 r=0.955/0.758) | knowledge/physics/friction-cof-monitoring-endpoint-detection.md | EXAMS.md Lv3-1 3문항 |
| 2026-09-08 | Lv3-2 CMP 마찰계수 실측(MIT Lai 2001 학위논문, Cu CMP 접촉모드 COF 0.40-0.49, hydroplaning 미도달 근거3가지, Preston kp 지수 압력별 비보편(-1 vs -0.5)) | knowledge/physics/cmp-friction-regime-experimental-mit-lai.md | EXAMS.md Lv3-2 3문항 |

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
- **[Lv3-1] 마찰기반 EPD 신호모델 엔진** (근거: knowledge/physics/friction-cof-monitoring-endpoint-detection.md §2·§4·§6 검증완료):
  - 입력: 층별 스택(재료·두께)과 재료별 COF(μ_Cu/μ_barrier/μ_oxide), P, V, A_wafer, r_c(웨이퍼중심 반경),
    baseline 모터동력 P_base, 잡음레벨, 샘플링레이트 R, 이동평균 창 N, 각 층 제거율 RR.
  - 계산: (1) 시간에 따라 노출재료가 바뀌며 μ(t) 계단 발생 → (2) 신호 = P_base + μ(t)·P·V·A (모터마찰동력,
    노트 §2 항등 P_motor,fric=μPVA=Q_f 사용) + 백색잡음 → (3) N점 이동평균 → (4) 계단검출(임계기울기 or SPRT)로
    종점시각 추정 → (5) 검출지연 T=N_half/R(N_half=창 반폭)과 과연마 = T·RR 산출.
  - 검증 문헌값(노트 §6에서 재현): Li 2017(PMC6190379) 종점계단 baseline 대비 ~5%(Δ1630W/30300W),
    121점·12.15Hz → 지연<5s·과연마<20nm@229nm/min; Headley 2019(doi.org/10.1149/2.0251910jss)
    PMC↔전단력 r=0.955 > PMC↔COF r=0.758 (모터전류=전단력 대리).
  - 우선순위 Tier2. cmp_lubrication_regime.py의 레짐판별과 결합: hydrodynamic이면 μ 재료대비 소멸→EPD 실패
    플래그. 마찰열-온도 엔진(위 Lv2-2 요청)의 Q_f와 동일 μPVA를 공유하므로 두 엔진은 같은 마찰동력 코어를 쓴다.

- **[Lv3-2] 재료별 boundary COF 분리 요청** (근거: knowledge/physics/cmp-friction-regime-experimental-mit-lai.md §3,§6 검증완료):
  현재 `sim/tier2_physics/cmp_lubrication_regime.py`의 `cof_stribeck(mu_bl=0.30)`은 oxide CMP 문헌값
  (0.23~0.40, 2차 인용) 기준 단일 상수다. 그런데 Cu CMP 1차 실측(Lai 2001, 중성 Al₂O₃ 슬러리)의
  접촉모드 COF는 0.40~0.49로 그 상한을 초과한다 — mu_bl을 재료(oxide/Cu/추후 W·barrier)별 딕셔너리로
  분리하고, 현재 값은 "oxide 전용"으로 이름을 바꿔 명시할 것을 요청. 우선순위 낮음(정성 방향성만 확인,
  Cu 슬러리 화학이 다양해 단일 Cu 상수도 과단순화 — film-cu 에이전트 활성화 후 재검토가 더 적절할 수 있음).

## 산출물 기록 (소프트웨어 부문이 기록)
- 2026-09-06 (S17, software-lead): Lv2-2 마찰열-Arrhenius 엔진 **부분 구현**.
  `sim/tier2_physics/frictional_heating_arrhenius.py` 신설 — q=μPV, Q_f, ΔT(슬러리 전량냉각 상한),
  Arrhenius 반응속도·배율, Shin2025 재료 상수(Cu/Ta/SiO₂ Ea·lnA) 재현. `tests/test_frictional_heating_arrhenius.py`
  8건 전부 노트 §6 문헌·해석해 대조값 재현(q=11250 W/m², Q_f 200-700W White오더, ΔT 5-40K Shin오더,
  Cu/oxide 30→50℃ 배율 41.5x/1.24x). **미완료**: engine.available_models() 미등록(MRR Model이 아니라
  순수 열-화학 함수 라이브러리 — tribology_basics.py와 같은 지위), `sim/chemistry.py`에 온도항으로
  연결하려면 팩에 슬러리 유량·ρ·cp·재료별 Ea가 필요한데 현재 팩(oxide_silica/cu_h2o2_bta)에 없음.
  다음 요청 시 화학 부문(tribologist/pad-mechanic)이 팩 파라미터를 채워주면 chemistry.py 통합 가능.
  커밋 (다음 참조).
