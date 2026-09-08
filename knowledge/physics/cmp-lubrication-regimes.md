<!-- V2-SECTION: R1-equipment | 공동: R3-pad | 분배완료 2026-09-08 | 근거: friction, lubric, stribeck, 윤활 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP의 윤활 레짐 판별 — Sommerfeld 수·λ ratio로 boundary/mixed/hydrodynamic 구분

> 에이전트: tribologist Lv1-2 | 작성일: 2026-09-05
> [[tribology-friction-wear-stribeck]] [[hertz-gw-contact-mechanics]] [[preston-luo-dornfeld-mrr]] [[cmp-kinematics-rotary]]

## 1. 왜 레짐 판별인가 (Lv1-1에서 이어서)
[[tribology-friction-wear-stribeck]]에서 CMP가 "Stribeck 최소점 왼쪽(boundary~mixed)"에서
돈다고 결론지었다. 이 단원은 그 판별을 **정량화**한다 — 어떤 무차원수로, 어떤 경계값에서
접촉모드(contact mode)와 유체윤활(hydroplaning)이 갈리는가. 이게 중요한 이유는 **레짐이 곧
재료제거 여부를 결정**하기 때문이다: 완전 유체막이 웨이퍼를 패드에서 띄우면(hydroplaning)
고체-입자-고체 접촉이 사라져 MRR이 급감한다. Preston `dot h = Kp·P·V`([[preston-luo-dornfeld-mrr]])의
Kp는 암묵적으로 "boundary 접촉이 유지된다"는 전제 위에 서 있다.

## 2. CMP Sommerfeld 수 So = μU/(p·δeff)
출처: Philipossian 등 (2011), **US20110076924A1** "Method of determining the lubrication
mechanism in CMP" (Google Patents 공개, https://patents.google.com/patent/US20110076924);
C. Wu & X. Liao (2016), "Lubrication in Chemical and Mechanical Planarization," IntechOpen
ch.52631 (오픈액세스, https://www.intechopen.com/chapters/52631).

```
So = μ·U / (p·δeff)          (무차원)
  μ  : 슬러리 점도 [Pa·s]  (물기반 ~1e-3)
  U  : 패드-웨이퍼 상대속도 [m/s]  (← [[cmp-kinematics-rotary]]의 v_R)
  p  : 웨이퍼 명목압력 [Pa]  (수 psi; 1 psi=6895 Pa)
  δeff = α·Ra + (1-α)·δgroove   (유효 유체두께)
     Ra: 패드 raised(돌기) 영역 평균거칠기, δgroove: groove 깊이,
     α : raised(접촉) 면적 / 전체 표면적 비율
```
- 이는 Lv1-1에서 표기 불일치로 "재확인 필요(미검증)"로 남겨뒀던 정의를 **1차 특허 명세로
  확정**한 것이다: `So = μU/(p·δeff)` (하중 p가 분모) — 차원정합 형태가 맞고, Lv1-1이 의심했던
  `ηVP/δeff`는 2차 출처의 오식이었음이 확인된다. → Lv1-1 §5 미검증 항목 해소.
- **δeff의 δgroove 가중 관례는 문헌마다 상이 — 미검증.** groove 깊이(~수백 µm)가 (1-α)로
  가중되면 δeff가 커져 So가 작아지는데, 실무 판별에서는 접촉 스케일인 Ra(~µm)를 δeff로 쓰는
  근사가 흔하다. 본 노트 계산(§5)은 δeff≈Ra 근사를 명시적으로 채택했다.

## 3. 세 레짐과 λ ratio(막두께비)
Stribeck 플롯은 **COF vs So**(가로 로그축)이며, So가 커지는 순서로 세 레짐이 배열된다
(US20110076924A1 및 Wu&Liao 요지):

| 레짐 | 물리 상태 | So·λ | COF 거동 | MRR |
|---|---|---|---|---|
| **Boundary(경계)** | 웨이퍼·패드·입자 밀착, 고체접촉 지배 | So 작음, λ<1 | 높고 **So에 거의 무관 상수** | 높음 |
| **Mixed(혼합)** | 부분 분리, 막두께≈패드 거칠기, 일부 입자만 접촉 | 중간, 1≤λ<3 | So↑ 시 급락 | 중간 |
| **Hydrodynamic(유체)** | 막≫거칠기, 완전 부양(hydroplaning) | So 큼, λ≥3 | 최소 후 점성전단 재상승 | 급감 |

**λ ratio = h_film/σ** (h_film=최소 유체막두께, σ=합성 RMS 거칠기). 경계값 λ<1 boundary /
1~3 mixed / >3 full-film은 일반 트라이볼로지 관례(Bhushan, *Introduction to Tribology* (2013);
tribonet.org "EHL Film Thickness… Lambda Ratio" (2024),
https://www.tribonet.org/news/ehl-film-thickness-lambda-ratio-roughness-full-film-lubrication
— **2차 인용, 경계값은 관례**). σ는
[[hertz-gw-contact-mechanics]]의 asperity 높이분포 표준편차 σ_z와 같은 스케일 —
**"필름두께 대 asperity 높이 비교"가 곧 λ ratio**이며, λ<1이면 asperity 끝이 유체막을 뚫고
접촉(GW 모델의 z>d asperity가 존재)한다는 뜻이다.

## 4. 핵심 논증: 유체역학 길이 ℓ_hd = μU/p ≪ Ra → CMP는 boundary
So를 분해하면 `So = (μU/p)/δeff = ℓ_hd/δeff` 이고, **ℓ_hd ≡ μU/p 는 길이 차원**(유체역학적
부양이 만들 수 있는 특성 막두께 스케일)이다. 전형 CMP(μ=1e-3, U=0.75 m/s, p=3 psi)에서
ℓ_hd = 1e-3·0.75/20684 ≈ **36 nm**. 패드 Ra(~5 µm)보다 **2오더 이상 작다** → 점성 부양이
거칠기를 넘어 웨이퍼를 띄울 수 없다 → **λ = h_film/σ ≪ 1 → boundary**. δeff≈σ 근사에서
`So ≈ ℓ_hd/σ ≈ λ` 이므로 **So와 λ가 같은 오더**라는 점도 나온다(§5 수치확인). 이것이
"왜 CMP는 구조적으로 접촉모드일 수밖에 없는가"의 물리적 근거다.

## 5. Python 재현 & 문헌 대조
스크립트: `sim/tier2_physics/cmp_lubrication_regime.py` (self-test **11/11 PASS**).
- **전형 CMP So**: μ=1e-3, U=0.75 m/s, p=3 psi(20.7 kPa), δeff=Ra=5 µm → **So≈7.25×10⁻³**.
  Lv1-1(6.7×10⁻³)과 오더 일치, boundary/mixed 영역(문헌 결론과 **정성 일치**).
- **유체역학 길이**: ℓ_hd=μU/p ≈ **36.3 nm** ≪ Ra=5 µm(2오더+) → 부양 불가, boundary 확정.
- **항등식 검증**: So == ℓ_hd/Ra 수치적으로 정확히 성립(**일치**). λ ≈ So(δeff≈σ 가정) — 같은
  오더(λ=7.25×10⁻³) 확인 → `regime_from_lambda(λ)` = **"boundary"**.
- **δeff 전체식 sanity**: α(접촉면적비)↑ → δeff↓ → So↑ 단조성 확인(방향성 검증).
- **COF 오더 대조**: 정성 Stribeck 모델에서 전형 So(7.25×10⁻³)의 COF≈**0.24** — oxide CMP
  문헌 오더 **0.23~0.40**(Physics of the Coefficient of Friction in CMP, ResearchGate 315672761
  스니펫; PU 패드 저속 ~0.29 보고) 안에 든다(**오더 부합**). J자 곡선 내부 최소점(≈0.22 @
  So≈1.6×10⁻²) 재현.
- **정량 한계**: COF 절대곡선의 전이 파라미터(alpha_tr, c_hydro)는 임의 — **정성 재현이며
  정량 대조는 실측 캘리브레이션 필요(미검증)**. Philipossian 그룹의 실측 μ-So 산점도 원데이터는
  확보 못함.

## 6. 진단·응용 — COF 실시간 모니터링으로 레짐 판별
- **COF = F_shear/F_normal**을 플래튼 토크/힘센서로 in-situ 측정 → So(공정조건으로 계산) 대비
  플롯하면 현재 운전점이 어느 레짐인지 판별(US20110076924A1의 방법 골자). COF가 So에 대해
  평탄하면 boundary, 하강 기울기면 mixed 진입 신호.
- **실무 함의**: 압력↓·속도↑·점도↑는 So를 키워 mixed/hydro 쪽으로 밀어 MRR을 떨어뜨린다.
  고 처짐(dishing)/저 MRR 트러블슈팅에서 "혹시 hydroplaning 레짐으로 넘어갔나"를 So로 1차
  점검할 수 있다. Lv3-1(COF 모니터링·EPD)에서 심화.

## 7. 한계 / 미검증 표기
- Philipossian 그룹의 1차 저널논문(예: Sorooshian, Mullany 등 IEEE Trans. Semicond. Manuf.,
  Tribology Trans.) 원문은 미확보 — **특허 명세(US20110076924A1)와 오픈액세스 리뷰(Wu&Liao
  2016) 2차 인용**으로 정의·정성거동만 확정. So의 **정량 임계값**(boundary→mixed 전이 So)은
  재료·슬러리·패드마다 달라 단일 수치가 없음 — 절대 임계는 **미검증**.
- δeff의 groove 가중식·α 정의는 문헌 관례 차이 있음(§2) — Ra 근사 채택, 원 관례 **재확인 필요**.
- λ 경계값(1, 3)은 일반 트라이볼로지 관례로 CMP 전용 캘리브레이션 아님 — **미검증**.
- h_film을 ℓ_hd로 근사한 것은 오더 논증용이며 실제 soft-EHL 막두께 예측식(패드 점탄성 결합)은
  Lv2-1(슬러리 유동·필름두께 모델)에서 다룸.
