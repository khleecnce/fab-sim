<!-- V2-SECTION: R1-equipment | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: friction, stribeck, 마찰, 윤활 | 물리 총론 — 여러 섹션 공유 | 정본: ARCHITECTURE-V2.md §3 -->
# 트라이볼로지 기초 — 마찰(Amontons-Coulomb)·마모(Archard)·윤활 3레짐·Stribeck 곡선

> 에이전트: tribologist Lv1-1 | 작성일: 2026-09-05
> [[hertz-gw-contact-mechanics]] [[preston-luo-dornfeld-mrr]] [[cmp-kinematics-rotary]] [[pad-wear-glazing-mrr-decay]]

## 1. 왜 트라이볼로지인가 (CMP 관점)
CMP는 본질적으로 **윤활된 3체 마모(three-body wear)** 공정이다: 웨이퍼(피가공면)–슬러리 입자(3체)–패드(대향면).
Preston 식 `dot h = Kp·P·V`([[preston-luo-dornfeld-mrr]])의 Kp 안에는 (a) 어떤 윤활 레짐인가(고체접촉 비율),
(b) 마모계수(입자가 재료를 얼마나 파내는가)가 숨어 있다. 이 단원은 그 세 축 —
**마찰(Amontons-Coulomb)·마모(Archard)·윤활(Stribeck)** — 의 고전 법칙을 정리하고 CMP가
어느 레짐에서 도는지 판별하는 무차원수(Hersey/Sommerfeld)를 세운다.

## 2. Amontons-Coulomb 마찰법칙 + 실접촉면적 관점
고전 3법칙(Amontons 1699, Coulomb 1785 — 2차 인용, DoITPoMS Tribology TLP / Bhushan
*Introduction to Tribology* 2013 표준 요약):
1. 마찰력은 수직하중에 비례: **F = µ·N** (µ=마찰계수).
2. 마찰력은 겉보기(명목) 접촉면적과 무관.
3. (Coulomb) 운동마찰은 미끄럼 속도와 대체로 무관.

**왜 명목면적과 무관한가 — 실접촉면적 이론(Bowden & Tabor 1950, 2차 인용):**
거친 표면은 asperity 끝에서만 닿으므로 실접촉면적 A_r ≪ A_nominal. 소성접촉이면 A_r = N/H
(H=경도), 마찰력은 접합부 전단강도 τ로 F = τ·A_r = τ·N/H. 따라서 **µ = τ/H = 상수**가 되어
하중·명목면적과 무관한 Amontons 법칙이 미시적으로 설명된다. 탄성접촉(GW 지수분포)에서도
A_r ∝ N이 성립함을 [[hertz-gw-contact-mechanics]] §4에서 이미 해석적으로 확인했다 —
**두 노트의 핵심 연결고리**(A_r ∝ N → µ 일정).

## 3. Archard 마모식 — V = k·W·L/H
원 논문: J.F. Archard, "Contact and Rubbing of Flat Surfaces," *J. Appl. Phys.* 24, 981–988 (1953).
**DOI: 10.1063/1.1721448** (`find_open_access.py --title` + Crossref API로 2026-09-08 실존·서지 확인:
title="Contact and Rubbing of Flat Surfaces", published 1953-08-01 — 단 원문 유료, OA 미확보이므로
본문 수식·k값은 여전히 2차 교차검증: DoITPoMS 'Wear' TLP(Cambridge, doitpoms.ac.uk); Encyclopedia MDPI
"Archard's Law: Foundations, Extensions, and Critiques" (encyclopedia.pub/entry/58780, 2024)).
k의 1차원리 예측 미해결 문제 참고문헌 **arXiv:2110.03647** "A criterion for critical junctions in
elastic-plastic adhesive wear" (2021-10-07, arXiv API로 2026-09-08 실존 확인 — 제목 일치, 초록만 확인·
본문 미독).

```
마모부피   V = k · W · L / H
   V: 마모 debris 부피[m^3], W: 수직하중[N], L: 미끄럼거리[m],
   H: 연질재 경도[Pa], k: 무차원 마모계수(wear coefficient)
면적당(마모깊이)  V/A = k · P · L / H   (P = W/A = 명목압력)
```
**유도 골자(2차 인용):** 각 asperity 접합부(면적 πa²)가 소성이면 하중 δW = H·πa²를 지지.
접합부 하나가 미끄럼거리 2a 동안 반구형 조각(부피 (2/3)πa³)을 확률 k로 떼어냄 →
단위거리당 마모율 dV/dL = k·W/(3H). k를 재정의(3 흡수)하면 V = k·W·L/H.

- **k의 의미:** 마모 심각도. 금속-금속 비윤활 k~10⁻²~10⁻⁴, 윤활 시 10⁻⁶~10⁻⁸ 오더
  (Archard 1953 및 교과서 표, **2차 인용·오더만 채택, 절대값 미검증**). k의 1차원리 예측은
  아직 미해결 문제로 남아 있음(arXiv:2110.03647 "critical junctions in adhesive wear" 등 활발).
- **CMP 연결:** 마모깊이식 `V/A = k·P·L/H`는 Preston `dot h = Kp·P·V`와 **구조가 동일**하다
  (L = V_slide·t). 즉 **Kp ≈ k/H** 라는 1차 대응이 성립 — 재현 스크립트에서 수치로 확인함(§7).
  단 CMP는 순수 기계마모가 아니라 화학적 연화(passivation layer)가 H를 낮추므로 k에 화학효과가
  뭉뚱그려짐 → 이것이 Kp가 슬러리 화학에 민감한 이유. [[pad-wear-glazing-mrr-decay]]의 패드 마모도
  같은 Archard 틀로 볼 수 있음.

## 4. 윤활 3레짐과 Stribeck 곡선
출처: STLE "Lubrication Fundamentals — The Stribeck curve" (*TLT* 2022, stle.org); tribonet.org
"How to Read a Stribeck Curve" (2차 정리). Stribeck(1902)/Hersey(1914) 실험이 기원.

가로축 **Hersey 수 = η·N/P** (η=점도, N=속도, P=단위길이당 하중), 세로축 마찰계수 µ:

| 레짐 | 막두께 vs 거칠기 | µ 거동 | 전형 µ (2차 인용) |
|---|---|---|---|
| Boundary(경계) | 막 ≪ 거칠기, 고체-고체 접촉 지배 | 높고 거의 일정 | 0.05–0.20 |
| Mixed(혼합) | 막 ≈ 거칠기, 부분 분리 | Hersey↑ 시 **급락** | 0.004–0.10 |
| Hydrodynamic(유체) | 막 ≫ 거칠기, 완전 분리 | 최소 후 완만 **재상승**(점성전단) | 0.002–0.01 |

**핵심: µ는 Hersey 수의 단조함수가 아니라 최소점을 갖는 U자(정확히는 J자) 곡선**이다.
최소점이 mixed→hydrodynamic 전이 부근이며, 여기가 마찰 최소·발열 최소 운전점. µ 우측 재상승은
막이 두꺼워지며 점성 전단저항 ∝ η·V/h 가 커지기 때문(고체접촉은 거의 사라짐).

## 5. CMP는 어느 레짐? — Sommerfeld 수 판별
출처: C. Wu & X. Liao, "Lubrication in Chemical and Mechanical Planarization," IntechOpen
ch.52631 (2016, 오픈액세스); A. Philipossian 등의 CMP Stribeck⁺ 연구(2차 인용).

CMP에서는 Hersey 수 대신 **무차원 Sommerfeld 수**를 쓴다:
```
So = η · V / (P · δ_eff)
   η: 슬러리점도[Pa·s], V: 패드-웨이퍼 상대속도[m/s]([[cmp-kinematics-rotary]]의 v_R),
   P: 웨이퍼 압력[Pa], δ_eff: 유효 슬러리막 두께 ≈ 패드 Ra
```
- log(µ) vs log(So) 플롯으로 boundary/mixed/(elasto)hydrodynamic을 구분(Wu&Liao Fig.7–8).
- **결론: 실용 CMP는 대부분 boundary~mixed 레짐**에서 운전된다 — 막이 패드 거칠기 수준(수 µm)이라
  웨이퍼·패드·입자가 여전히 직접 접촉해야 재료제거가 일어나기 때문. 완전 hydrodynamic이면
  접촉이 사라져 MRR이 급감(연마가 아니라 부양). 그래서 CMP는 "Stribeck 최소점 왼쪽"을 의도적으로
  유지한다.
- **막두께 관례 주의(미검증):** Wu&Liao 본문 수식이 `So = ηVp/δeff`로 표기되나 차원상
  하중은 분모여야 무차원이 됨(η[Pa·s]·V[m/s]/(P[Pa]·δ[m]) = 무차원). 본 노트는 차원정합
  형태 `η·V/(P·δeff)`를 채택했고 표기 불일치는 원문 오식(誤植) 가능성 — **1차 재확인 필요**.

## 6. 무차원수 요약 (혼동 주의)
- **Hersey 수** η·N/P: 관례상 차원이 남을 수 있음(N을 rpm/rps, P를 하중/길이로 씀). 오더 판별용.
- **Sommerfeld 수** (베어링) = (η·N/P)·(r/c)² 또는 CMP형 η·V/(P·δeff): 무차원.
- **무차원 막두께 λ = h_min/σ** (σ=합성 RMS 거칠기): λ<1 boundary, 1≤λ≤3 mixed, λ>3 full-film
  (Bhushan 2차 인용, 경계값은 관례). Stribeck 가로축을 λ로 쓰기도 함.

## 7. Python 재현 & 문헌 대조
스크립트: `sim/tier2_physics/tribology_basics.py` (self-test **10/10 PASS**).
- **Archard 스케일링 재현:** V ∝ W, V ∝ L, V ∝ 1/H 세 비례관계가 수치적으로 정확히 성립(문헌
  법칙과 **일치**).
- **Archard 오더 대조:** 연강 pin-on-disk 예시(k=1e-3, W=10N, H=1.8GPa, L=1000m) →
  V=5.56×10⁻⁹ m³ = **5.56 mm³/km**. 금속 비윤활 마모의 문헌 오더(mm³ 스케일)와 **부합**.
  (주: 최초 손계산에서 지수 오기 5.6e-6로 잘못 적었으나 실제 5.6e-9로 재확인 — 정직 기록.)
- **Preston 대응 검증:** `k/H`를 Kp로 두면 Archard 마모깊이 = Kp·P·L 이 Preston형과 수치 일치 →
  **Kp ≈ k/H 대응 확인**(오더 연결, 화학효과 제외).
- **Sommerfeld 오더:** CMP 전형(η=1e-3 Pa·s, V=1 m/s, P=3e4 Pa≈4.3psi, δeff=5µm) →
  So≈6.7×10⁻³ — mixed/boundary 영역에 해당(문헌 결론과 **정성 일치**).
- **Stribeck 곡선 정성 재현:** 접촉분율 f=exp(-αSo) 단순모델로 µ(So)를 그리면 **내부에 최소점**
  존재(min µ≈0.004 @ So≈0.12), 좌측 boundary µ≈0.15, 우측 hydrodynamic 재상승 — Stribeck의
  J자 형상과 최소점 위치를 **정성적으로 재현**. (정량 곡선은 실측 캘리브레이션 필요 — 미검증.)

```python verify
import sys, math
sys.path.insert(0, "sim/tier2_physics")
from tribology_basics import archard_wear_volume, cmp_sommerfeld, stribeck_cof

# Archard 스케일링 (V ∝ W, V ∝ L, V ∝ 1/H) — §3
k, W, L, H = 1e-3, 10.0, 100.0, 1e9
V0 = archard_wear_volume(k, W, L, H)
assert math.isclose(archard_wear_volume(k, 2*W, L, H), 2*V0)
assert math.isclose(archard_wear_volume(k, W, 3*L, H), 3*V0)
assert math.isclose(archard_wear_volume(k, W, L, 2*H), 0.5*V0)

# Archard 오더 대조: 연강 pin-on-disk 예시 (k=1e-3, W=10N, H=1.8GPa, L=1000m)
# 문헌 오더(금속 비윤활 마모, mm^3 스케일) 대조 — §7
V_ex = archard_wear_volume(1e-3, 10.0, 1000.0, 1.8e9)
assert math.isclose(V_ex, 5.5556e-9, rel_tol=1e-3), f"V_ex={V_ex:.4e}"
assert 1e-9 < V_ex < 1e-7  # 문헌 오더 범위 안

# CMP Sommerfeld 오더 (η=1e-3 Pa·s, V=1 m/s, P=3e4 Pa, δeff=5µm) — §5
So = cmp_sommerfeld(1e-3, 1.0, 3e4, 5e-6)
assert math.isclose(So, 6.667e-3, rel_tol=1e-2), f"So={So:.4e}"
assert 1e-3 < So < 1e-1  # mixed/boundary 영역 오더

# Stribeck 곡선: 내부에 최소점 존재 (정성 재현) — §4,§7
Hs = [10**x for x in range(-4, 1)]
cofs = [stribeck_cof(h) for h in Hs]
min_idx = cofs.index(min(cofs))
assert 0 < min_idx < len(cofs) - 1, "최소점이 양 끝이 아니라 내부에 있어야 함(J자 곡선)"

print("PASS: Archard 스케일링 3종 + 오더 대조 + Sommerfeld 오더 + Stribeck 최소점 내부 존재 — 전부 확인")
```

## 8. 한계 / 미검증 표기
- Archard 1953 원문·k 표 절대값은 유료로 미확보 — **2차 인용, 오더만 채택**.
- Amontons/Coulomb/Bowden-Tabor 원전 미확보 — 표준 교과서(Bhushan 2013) **2차 인용**.
- CMP Sommerfeld 수 정의의 δ_eff·표기 관례가 문헌마다 상이 — 차원정합 형태 채택, 원문 오식
  가능성 **재확인 필요(미검증)**.
- Stribeck 재현은 **정성 모델**(전이 파라미터 α, µ_bl 등은 임의)로 최소점 존재만 보인 것 —
  실제 CMP µ-So 곡선의 정량 대조는 다음 단원 Lv1-2(윤활레짐 판별)에서 실측/문헌 데이터로 진행.
