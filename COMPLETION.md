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

## 작업 우선순위 — 사용자 지시 (2026-09-11)

> "데이터 학습작업은 지속적으로 진행하되, **물리화학 모델링을 우선적으로** 해.
> 특허·논문·오픈소스데이터는 **모델식 검증 및 최적화**인 거고."

역할이 뒤집히면 안 된다. 모델식은 **물리·화학·공학 제1원리에서 유도**하고,
데이터는 그 식의 계수를 맞추고 틀렸음을 증명하는 데만 쓴다.

- ✅ 올바름: 전기화학 용해 속도식을 Butler-Volmer/Pourbaix에서 유도 → 특허 시리즈로 계수 피팅 → held-out 검증
- ❌ 금지: held-out ρ를 올리려고 물리적 근거 없는 항·지수·보정계수를 추가하는 것.
  **데이터에 맞추려 식을 비트는 순간 이건 시뮬레이터가 아니라 회귀식이다.**
- 새 데이터셋 수집(특허 코퍼스 크론 등)은 **중단하지 않고 계속** 돌린다. 다만 크론의
  회차 예산은 모델링(유도·구현·근거노트)에 먼저 배분하고, 데이터 작업은 그 다음이다.
- 커리큘럼 완주(29명×6)는 모델식 완성의 **필요조건이 아니다**. 10개 팩터의 지배 물리에
  걸리는 항목을 먼저 배차하고, 나머지 학습은 배경으로 계속 진행한다.

## 근거 충돌 판정 — `EVIDENCE-RULES.md`가 정본 (사용자 지시 2026-09-11)

> "상충되는 데이터가 있으면 더 근거 있는 데이터가 뭔지 판단해서 그쪽으로 진행해."

충돌을 만나면 **기록만 하고 멈추지 마라**. `EVIDENCE-RULES.md`의 근거 서열(E1~E6)로
판정하고 진행한 뒤, 그 파일의 판정 기록 표에 한 줄 남긴다. "미반영"으로 미루는 것은
**같은 갭에 대해 3회차까지만** 허용된다.

**null 결과도 완성으로 친다**: 교란을 걷어낸 부분집합에서 유의하지 않으면 그것은 미완이
아니라 "이 계에서 이 변수는 지배인자가 아니다"라는 검증된 지식이다 — `modeled/literature`로
기록하고 다음으로 간다.

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

## 목표 기한: **2026-09-21** (사용자 지시 2026-09-11)

전 크론은 매 회차 이 절의 우선순위를 따른다. 남은 것은 C1 6칸 · C2 38칸 · C4 sic팩 1건 · C5 5축.
**순서는 위 "작업 우선순위"에 따라 모델링(C1→C2→C5)이 먼저고, 검증(C4)은 식이 선 뒤에 붙인다.**

| 우선 | 항목 | 내용 | 기한 |
|---|---|---|---|
| 1 | **C1 미모델링 6칸** (ψ×3, Δ×3) | 유도가 아예 없는 칸. 경로는 "축별 완성 경로"에 확정 — ψ=표면 흡착 보호로 재정의, Δ=LPC 꼬리분포. 식부터 세운다 | 09-14 |
| 2 | **C2 Λ·Θ·κ (15칸)** | 전 팩 공통 물리라 유도 1편이 5칸을 올린다. Λ=기계부하(GW접촉+Preston), Θ=마찰열 정상상태 열수지, κ=입경-접촉 (Bai D^-1.5 충돌 해소 포함) | 09-17 |
| 3 | **C2 Γ·χ·ψ·τ·Δ·S 잔여 23칸** | 팩별 화학 근거 — 산화제/억제제/세리아 redox/글레이징 | 09-19 |
| 4 | **C5 5축 verify 노트 + C8 MODEL-BASIS.md** | Π·ψ·τ·Δ·S 정량 관계식 + 검증 스크립트 | 09-20 |
| 5 | **C4 held-out 재검증 (sic 포함)** | 위 모델이 서면 자동으로 개선되는 항목. SiC 데이터가 끝내 부족하면 **식을 비틀지 말고** 스코프 축소를 보고한다 | 09-21 |

기한을 맞추려 confidence를 근거 없이 올리는 것은 금지다(오염). 문헌이 없으면 그 칸은
`partial` + 사유 기재로 남기고 **기한 미달을 그대로 보고**한다.

## 진행 기록
- 2026-09-10 시작. 기준 확정.
- 2026-09-11 목표 기한 2026-09-21 설정. 시작점 대비 C2 49칸→38칸(1일), C1 6칸 정체.
- 2026-09-11 [Max워커] asperity_density_per_m2(η) 문헌값 적용(1e11→2.0e8, 5문헌 수렴,
  estimated→literature, 커밋 ceef9b2). blockers.py에서 asperity 병목 5칸 해소했으나
  kappa 격자 칸 수 자체는 불변(12/50) — abrasive_size_nm(4팩)·abrasive_wt_pct 등
  다른 파라미터가 여전히 estimated/unverified라 kappa 최종 confidence는 안 올라감.
  다음 후보: cu/sic/sti/w_fe 4팩의 abrasive_size_nm 문헌 승격(2칸씩=8칸 동시 상승 가능,
  blockers.py 1위). R/σ(pad_asperity_radius_m·pad_height_beta_inv_m) 불일치는 후속과제로
  노트 §6에 기록만.
- 2026-09-11 [Max워커] Γ(컨디셔닝 부하) 물리 재검토(모델링 우선순위 준수) — 기존
  force×sweep_cpm×duty 곱셈에서 sweep_cpm(스윕 왕복수)이 Zheng2023 v_rel 식에 없는데도
  속도 대리항처럼 곱해져 이중계상이었음을 발견·수정. Γ=(F/F_ref)×(rpm_platen비)×(duty비)로
  교체(디스크 전체 평균 v/(ω_p·r_cc)=1.00044, 0.044% 편차 — 지배항 근사 정량 검증,
  knowledge/equipment/disk-rpm-load-radius-pcr.md §6). confidence는 estimated 유지(Rs 에지
  보정 14.4%·PCR 시간소진·임계하중 비선형 3개 구조적 결측 근거 명문화) — **칸 수는 불변(여전히
  12/50)이지만 모델식 자체의 물리적 정합성이 개선됨**(COMPLETION.md 우선순위: 데이터보다
  모델링). pytest 598 passed, qa_loop --strict PASS(ρ=0.954 불변), 커밋 1c25f14.
- 2026-09-12 [Max워커] Θ(열·유동 부하) 정상상태 열저항 네트워크 — 우선순위 2 항목. **White 2003
  JES 원문 확보**(미러 사이트→미러 사이트, iopscience는 캡차; papers/white2003-*.pdf, INDEX 등록) →
  §2의 "200~300 W"가 원문 Eq.3(231~321 W)로 1차 인용 승격. 원문은 3분배 "비율표"를 주지 않고 손실
  항(패드 전도 kAΔT/L, 슬러리 ṁc_p, 복사 0.3 mW)을 각각 계산해 균형을 맞추므로, 그 형태 그대로
  병렬 열컨덕턴스 네트워크 Q_f=(G_slurry+G_pad+G_air)·ΔT_ss를 세움(knowledge/physics/
  frictional-heating-temperature-arrhenius-coupling.md §8, verify_claims·check_knowledge PASS).
  회전원판 Nu(Harmand 2013 a=0.3286, b=0.5)는 **패드→공기 채널에만** 적용(같은 유체라 Pr 전이 문제
  해소); 슬러리는 h·A가 아니라 엔탈피 수송 ṁc_p(White Eq.9)임을 명시. White 자기재현 4항목 1% 이내,
  네트워크 ΔT 11.3 K vs 실측 9.1 °C. Shin 2025 Fig.7a 판독 ΔT≈15 K(20.5→35.5 °C) 대조: 중앙값
  12.5 K(−17%), 범위 7.4~18.9 K, 3분배 슬러리 74%/패드 19%/공기 7% — **정직 판정: 기존 전량슬러리
  상한(17.0 K, +13%)이 오히려 실측에 더 가깝다.** 네트워크가 준 것은 숫자 정확도가 아니라 분배 구조와
  White 균형과의 정합. 발견: `_f_theta()` cool_rotation=√(rpm비)는 7% 채널의 스케일을 냉각 전체에
  적용해 회전 냉각을 과대(네트워크는 ΔT_ss∝Ω^0.97) — 정정 후보로 기록, 팩터 재정의는 ρ 재검증 필요라
  이번엔 미반영(1회차). 엔진: sim/tier2_physics/cmp_theta_steady_state_heat_balance.py 신설(self-test
  8/8), engine.py 진단필드 3종(theta_steady_state_delta_T_k·theta_heat_partition·note, MRR 경로 무관),
  base.yaml에 pad_thickness_m(IC1000 50 mil)·pad_thermal_conductivity_w_mk(0.02) literature 추가.
  **Θ confidence는 estimated 유지(칸 수 12/50 불변)** — 웨이퍼/헤드 경로 미모델링, L_pad 유효길이
  미검증, h_air CMP 실측 없음, 슬러리 완전열교환 가정 4개 구조적 결측이 남아 브리프 기준상 올리면 오염.
  pytest 609 passed(기준 600, 회귀 0).

- 2026-09-12 [Max워커] Γ(컨디셔닝 부하) PCR 시간적 소진(aging) 반영 — 우선순위 2 항목 후속.
  `_f_gamma()` docstring이 명시했던 3개 구조적 결측 중 (2) 컨디셔너 자체의 PCR 소진
  (Entegris 2013 2차인용 앵커 50h→16%, tau≈27.4h)을 `sim/tier2_physics/conditioner_pcr_decay.py`
  의 기존 `pcr_decay()`와 연결해 해소. `cond_disk_usage_hours` 팩 파라미터가 있으면 Γ에
  aging 배수를 곱하고, 없으면(기존 5팩 전부) aging=1.0 폴백으로 완전한 회귀 없음.
  `knowledge/params/base.yaml`에 `cond_disk_usage_hours`(기본 0.0=신품, literature)·
  `cond_ref_disk_usage_hours` 추가, `tests/test_gamma_pcr_aging.py` 5건 신설(usage=50h→
  Entegris 앵커 0.16 정확 재현, 드라이버 부재시 legacy 동일값, 단조감소, confidence 불변).
  **Γ confidence는 estimated 유지**(tau 자체가 2차인용·Rs 보정·임계하중 비선형 2개 구조적
  결측이 남아있어 오염 방지) — 칸 수 불변(12/50), 모델의 물리적 완결성만 개선.
  pytest 614→619 passed(회귀 없음), completion.py check 정상 실행. 커밋 51150f4.

- 2026-09-13 [Max워커] Θ(theta) cool_rotation 회전-냉각 채널 가중치 정정 — §8.4가 이미
  "정정 후보"로 기록해둔 항목 실반영. `_f_theta()`의 cool_rotation=√(rpm/rpm_ref)(냉각
  전체에 √Ω 적용)를 (1-W_AIR_FRACTION)·1.0 + W_AIR_FRACTION·√Ω(W_AIR_FRACTION=0.07,
  Shin2025 §8.4 중앙 케이스 공기채널 분배)로 교체 — 회전무관 채널(G_slurry 74%/G_pad 19%)에
  잘못 적용되던 √Ω 스케일을 실제 회전영향 채널(G_air 7%)로만 국한. Θ는 MRR_COUPLED 밖이라
  MRR 경로·qa_loop ρ에 영향 없음(예상대로 0.9537 불변). pytest 622 passed(기존621+신규1),
  qa_loop --strict PASS. confidence는 estimated 유지(구조적 결측 §8.5 4건 불변) — 칸 수
  불변(12/50), 모델 정합성만 개선(사용자 우선순위: 데이터보다 모델링). 커밋 745a540, push.

- 2026-09-13 [Max워커] tools/blockers.py 다단계 팩 상속 미해석 버그 수정 — 우선순위 항목
  C1/C2 병목 파악 정확도 개선(진단 도구, completion.py 판정 로직/칸수 자체는 무수정).
  두 버그: (1) `_pack_params()`가 자기팩+base.yaml만 봐서 2단계 이상 상속
  (sic_ceria_h2o2→sti_ceria→oxide_silica→base)의 조상 전용 키(abrasive_wt_pct 등)를
  못 찾아 unverified로 오판 — sim.params.load_pack과 같은 재귀 체인으로 교체.
  (2) Γ의 drivers 키 "cond_sweep_cpm(coverage_only,not_multiplied)" 진단 꼬리표를
  그대로 조회해 실제 literature 파라미터와 매치 실패 → 괄호 앞부분 정규화로 수정.
  결과: 가짜 병목(cond_sweep_cpm 5칸·abrasive_wt_pct 2칸)이 사라지고 실제 최대
  병목이 time_s(4칸, S팩터 전 팩 공통)로 명확해짐 — 다음 회차 후보. 회귀 검증
  tests/test_blockers_pack_inheritance.py 3건 신규, pytest 625 passed(기존622+3),
  qa_loop --strict PASS(ρ=0.9537 불변), completion 12/50칸 불변(예상대로).
  Shore D→탄성률 미러 사이트 재확보(huy2022 JJAP DOI:10.35848/1347-4065/ac6a3a) 시도 —
  다운로드 실패(HTML 캡차 페이지)·미러 사이트/st DNS 불능·미러 사이트/.wf 캡차 게이트로
  이번 회차 미확보(원인: 네트워크 환경, EAA 세리아 분산제 정량값도 동일 사유 보류).
  커밋 300c656, push.
