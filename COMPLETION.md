# 물리·화학 모델링 완성 기준 (COMPLETION.md) — 2026-09-10

사용자 지시 원문:
> "물리, 화학 및 공학을 학습해서 CMP 공정을 시뮬레이션할수 있는 모델을 만들어. 모델을 만들기 위해서
> 지식을 활용해서 학습을 하고 그 학습 내용을 통해서 새로운 지식을 도출해. 그래서 CMP 공정을 모사할 수
> 있는 모델을 만들어. 실제 데이터 적용은 그다음이야. 모델검증은 당분간은 특허/논문에 있는 데이터로 해.
> 모델링 완성을 목표로해" / "10개 기준으로 진행해. 다만 새로운 파라미터가 도출되거나 의미없는
> 파라미터가 있으면 늘리거나 줄여도 돼."

## 완성의 정의 (기계 판정 — `tools/completion.py`)

팩터 10개 × 팩 5개(cu_h2o2_bta·oxide_silica·sic_ceria_h2o2·sti_ceria·w_fe_oxidizer) 격자에서:

| 조건 | 기준 | 판정 도구 |
|---|---|---|
| C1 모델링 | 모든 칸 `status ∈ {modeled, partial}`, `unmodeled` 0 | `completion.py` |
| C2 근거 | 모든 칸 `confidence ≥ literature` (estimated·unverified 0) | 〃 |
| C3 반응 | MRR 결합 팩터(κ·χ·ψ·τ)는 `--sensitivity` 탄성도 ≠ 0 | `sim.cli --sensitivity` |
| C4 검증 | 팩마다 유의(p<0.05) held-out ≥ 1, 유의 평균 ρ ≥ 0.85 | `qa_loop.py` |
| C5 형상 | 각 팩터에 문헌 정량 관계(폐형식 또는 실측 회귀)와 verify 블록 있는 노트 ≥ 1 | `completion.py` |
| C6 무퇴보 | 매 변경 `qa_loop run --strict` PASS | 크론 게이트 |
| C7 완성 후 상시검증 | 완성 판정 이후에도 매 회차 `completion.py check` + `qa_loop run --strict` — 한 칸이라도 되돌아가면 즉시 텔레그램 보고 + 원인 커밋 revert | 성장엔진·심야병렬 |
| C8 근거 보고 | `completion.py report` 가 팩터별 **모델 정의 근거**(어느 문헌의 어느 관계식)와 **파라미터 도출 근거**(어느 표/그림에서 어떻게 역산, confidence)를 한 문서(`validation/MODEL-BASIS.md`)로 생성. 완성 시 사용자에게 제출 | `completion.py` |

사용자 지시(2026-09-10): "완성된 후에는 오류가 없도록 루프를 돌려서 검증해. 그리고 각 모델이
정의 된 근거, 파라미터가 도출된 근거를 나중에 나에게 보고해."

`partial`은 완성으로 친다 — 단, 빠진 드라이버가 **왜** 빠졌는지(문헌 없음)가 노트에 있어야 한다.
문헌이 없는 것을 지어내 채우는 것은 완성이 아니라 오염이다.

## 팩터 재정의 허용 규칙
- **늘리기**: 문헌이 기존 팩터로 환원되지 않는 독립 물리를 보이면 추가. 예: 패드 점탄성(tanδ)이
  κ(접촉)와 S(시간)로 환원되지 않으면 새 팩터. 추가 시 `FACTOR_SPEC`에 축·파트·근거 노트 명시.
- **줄이기/합치기**: 두 팩터가 held-out에서 항상 같은 방향으로만 움직이고(|ρ|>0.95) 분리해도 사용자
  결정이 달라지지 않으면 합친다. 판정은 데이터로, 취향으로 하지 않는다.
- 웨이퍼는 팩터가 아니다(사용자 확정). 장비축·소모품축 분리 유지(사용자 확정).

## 현재 상태 (2026-09-10 시작점)
```
factor     cu_h2o2_bta  oxide_silica  sic_ceria_h2     sti_ceria  w_fe_oxidize
Λ lambda  modeled/esti  modeled/esti  modeled/esti  modeled/esti  modeled/esti
Π pi      modeled/veri  modeled/veri  modeled/veri  modeled/veri  modeled/veri
Θ theta   partial/esti  partial/esti  partial/esti  partial/esti  partial/esti
Γ gamma   modeled/unve  modeled/unve  modeled/unve  modeled/unve  modeled/unve
κ kappa   partial/esti  partial/esti  partial/esti  partial/esti  partial/esti
χ chi     partial/esti  partial/esti  modeled/esti  modeled/esti  partial/esti
ψ psi     modeled/unve   UNMODELED     UNMODELED     UNMODELED   modeled/unve
τ tau     partial/unve  partial/unve  partial/unve  partial/unve  partial/unve
Δ delta    UNMODELED     UNMODELED    partial/unve  partial/unve   UNMODELED
S stab    partial/esti  partial/lite  partial/esti  partial/esti  partial/esti
```
unmodeled 6칸, confidence<literature 49/50칸. 유의 held-out 6개(67조건) ρ +0.935.

## 축별 완성 경로 (문헌이 있는 것만 — 조사 결과에 따라 갱신)
- **ψ 산화막 계**: 산화막 CMP엔 금속 부식억제제가 없다. 대신 STI 선택비의 본질인 **SiN 억제제
  (PAA·아미노산 흡착)**와 실리카 계의 **계면활성제/폴리머 흡착에 의한 MRR 억제**가 ψ다.
  → 팩터 정의를 "금속 부동태"에서 "표면 흡착 보호(passivation/adsorption shield)"로 넓힌다.
- **Δ**: LPC(대입자 수)–스크래치 밀도 상관(lpc-scratch-density-tail-correlation.md),
  응집 배수(Egan-Kim 2019), Hitachi US8439995 D99 스펙. D99가 없는 팩은 D99/D50 일반비
  (Levitronix 2008)로 대체하되 confidence=literature 표기.
- **S**: 글레이징 로그감쇠(Jeong 2024)는 있음. 컨디셔닝 재생과 결합해 정상상태 모델로 확장
  (Γ와 S의 결합: 드레서 절삭율 vs 글레이징률 균형). PHM2016 드레서-MRR ρ=-0.70이 검증 데이터.
- **Θ**: 패드 열전도·슬러리 비열·대류 계수 문헌 확보 → 정상상태 열수지 완성.
- **κ 입경 지수**: Bai 2007 D^-1.5는 QA FAIL(TW202115224A와 방향 충돌). 입자 형상·응집을 분리한
  뒤 재시도. 충돌 자체가 "지수 하나로 안 된다"는 새 지식이다.

## 진행 기록
- 2026-09-10 시작. 기준 확정.
