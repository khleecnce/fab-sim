# POU 필터·재순환 루프·펌프 전단 — LPC 꼬리의 생성항과 제거항

> 에이전트: slurry-colloid Lv2-1 | 작성일: 2026-09-13
> 선행: [[colloidal-destabilization-lpc-defect-mechanism]] [[dlvo-ionic-strength-ph-aggregation-kinetics]]
> 관련: [[../cmp/lpc-scratch-density-tail-correlation]] [[../cmp/colloid-zeta-dlvo-slurry-stability]]

## 1. 이 노트가 채우는 자리

선행 노트 [[colloidal-destabilization-lpc-defect-mechanism]]는 "콜로이드가 불안정화되면
LPC 꼬리가 생기고 그것이 스크래치가 된다"는 **인과 체인**을 세웠지만, 그 불안정화를
일으키는 것이 무엇인지는 정적 화학(이온강도·pH)까지만 다뤘다. 실제 팹에서 슬러리는
제조 후 웨이퍼에 닿기까지 **펌프로 수십~수백 번 순환**하고 **여러 단의 필터를 통과**한다.
그래서 웨이퍼에 도달하는 LPC는 다음 수지(收支)의 결과다:

```
LPC(웨이퍼 도달) = LPC(제조 시) + [펌프 전단 생성항] − [필터 제거항]
```

이 노트는 두 항을 각각 정량화한다: **생성항**은 전단률 G(1/s)와 노출시간의 함수
(§2~3, Khanna et al. 2018·2019), **제거항**은 필터 리텐션·beta ratio와 통과 횟수의 함수
(§4~6, Rastegar 2017 / Entegris 2014 / Wood 2019 / Seo 2003). §7에서 두 항을 합쳐
"재순환 루프에서 실측 제거율이 이상 모델보다 훨씬 낮다"는 정량 불일치를 보이고,
그것이 생성항의 존재를 요구한다는 결론에 이른다.

## 2. 생성항 (1) — 전단 유도 응집의 두 조건: 임계 전단률 AND Camp 수

**Khanna, A.J., Gupta, S., Kumar, P., Chang, F.-C., Singh, R.K. (2018). "Study of Agglomeration
Behavior of Chemical Mechanical Polishing Slurry under Controlled Shear Environments."
*ECS J. Solid State Sci. Technol.* 7(5), P238–P242. DOI: 10.1149/2.0091805jss**
및 같은 팀의 후속 **Khanna et al. (2019). "Quantification of shear induced agglomeration in
chemical mechanical polishing slurries under different chemical environments."
*Microelectronic Engineering* 210, 1–7. DOI: 10.1016/j.mee.2019.03.012**
— 둘 다 미러 사이트 폴백으로 전문 확보(`papers/khanna2018-...pdf`, `papers/khanna2019-...pdf`).

### 2.1 실험 설계 (E1급: 한 변수만 스윕, 교란 통제)
Silco EM3530K 콜로이드 실리카(1차 입경 **35 nm**), DIW로 **10 wt%** 희석, pH는 질산으로
2 / 7 / 10 세 조건. 3 mL 시료를 Paar Physica UDS 200 **레오미터**(동심원통)로
**G = 100 / 1000 / 1500 / 2000 / 3000 s⁻¹**, **t = 100 / 1000 / 2500 s** 격자 스윕.
전단 전후의 대입자 분포를 **Accusizer 780 SPOS**(0.51–200 µm 단일입자 계수)로 측정하고
`정규화 누적농도 = C(전단 후)/C(as-received)`로 정의 — 1.0보다 크면 응집, 작으면 해응집.
슬러리 전달 시스템을 실험실에서 **전단률 하나로 환원**해 재현한 설계라는 점이 핵심이다.

### 2.2 결과 — 세 영역(해응집 / 전이 / 응집)
pH 10(2018 논문)에서:
| 전단률 G | t=100 s | t=1000 s | t=2500 s |
|---|---|---|---|
| 100 s⁻¹ | 해응집 | 해응집(더 강함) | 해응집(가장 강함) |
| 1000 s⁻¹ | 해응집 | 해응집 | 해응집 |
| 1500 s⁻¹ | 해응집 | **응집** | **응집** |
| 2000 s⁻¹ | ≈1.0(전이) | **응집** | **응집** |
| 3000 s⁻¹ | ≈1.0(전이) | **응집(최대)** | **응집(최대)** |

→ 저자들의 결론: pH 10 실리카의 **임계 전단률은 1000–1500 s⁻¹ 사이**.
그 아래에서는 시간을 아무리 늘려도 응집이 안 일어나고, 오히려 기존의 약하게 뭉친
응집체가 깨져 **LPC가 줄어든다**(해응집). 이건 실무적으로 중요하다 — 저전단 순환은
LPC를 늘리는 게 아니라 줄인다.

### 2.3 Camp 수와 pH 의존성 (2019 논문)
Camp(1953)의 응집조 설계수 **Camp number = G·t**(무차원). 2019 논문이 측정한
**임계 Camp 수**:
| pH | 제타전위 부호·크기 | 임계 Camp 수 | 임계를 만든 (G, t) |
|---|---|---|---|
| 2 (≈IEP) | ≈0 (반발력 최소) | **1×10⁵** | 1000 s⁻¹ × 100 s |
| 7 | 음(중간) | **1.5×10⁵** | 1500 s⁻¹ × 100 s |
| 10 | 강한 음 | **1.5×10⁶** | 1500 s⁻¹ × 1000 s |

실리카 IEP≈pH 2에서 반발장벽이 사라지므로 임계 Camp 수가 가장 낮고, pH 10에서 가장
높다 — 즉 **DLVO 반발장벽이 전단 응집의 문턱을 그대로 설정**한다. 선행 노트
[[dlvo-ionic-strength-ph-aggregation-kinetics]]의 정적 응집속도론이 동적(전단) 조건으로
확장되는 지점이 여기다.

### 2.4 ⚠ 중요 — Camp 수 하나로는 부족하다
2019 논문 §3.3에 명시된 반례: pH 10에서 **G=1000 s⁻¹ × t=2500 s → Camp = 2.5×10⁶**은
임계 Camp(1.5×10⁶)를 **1.67배 넘는데도 응집이 관측되지 않았다**. G가 임계 전단률
(1000–1500 s⁻¹) 미만이면 입자가 반발장벽을 넘지 못하므로 시간을 곱해도 소용없다.
따라서 응집 판정은 **AND 조건**이다:

```
응집 발생 ⟺ (G ≥ G_th)  AND  (G·t ≥ Camp_th)
```

이것이 sim/ 모델링에 그대로 넘어가야 할 형태다(§9 구현 요청). 두 조건을 하나로
합치거나 Camp 수만 쓰면 위 반례에서 틀린다.

```python verify
import math

# --- Khanna et al. 2018 (doi:10.1149/2.0091805jss), pH10 실리카 35nm/10wt% ---
# (G[1/s], t[s]) -> 원문이 보고한 거동. True=응집, False=해응집/무변화
pH10 = {(100,100):False,(100,1000):False,(100,2500):False,
        (1000,100):False,(1000,1000):False,(1000,2500):False,
        (1500,100):False,(1500,1000):True,(1500,2500):True,
        (2000,100):False,(2000,1000):True,(2000,2500):True,
        (3000,100):False,(3000,1000):True,(3000,2500):True}

# 문헌값: 임계 Camp 수 (Khanna et al. 2019, doi:10.1016/j.mee.2019.03.012, 결론절)
CAMP_TH = {2: 1.0e5, 7: 1.5e5, 10: 1.5e6}
G_TH_PH10_LO, G_TH_PH10_HI = 1000.0, 1500.0   # 2018 논문: "1000~1500 s^-1 사이"

# (1) pH10 임계 Camp 수 재현: 응집이 일어난 (G,t) 중 최소 Camp가 1.5e6이어야 한다
camps_agg = [G*t for (G,t),agg in pH10.items() if agg]
assert min(camps_agg) == CAMP_TH[10], f"재현 실패: {min(camps_agg):.3g} vs 문헌값 1.5e6"
print(f"pH10 임계 Camp 수 재현 = {min(camps_agg):.2e} (문헌값 1.5e6, 일치)")

# (2) 임계 전단률: G<=1000 에서는 t를 아무리 늘려도 응집이 없어야 한다
assert all(not agg for (G,t),agg in pH10.items() if G <= G_TH_PH10_LO)
assert any(agg for (G,t),agg in pH10.items() if G >= G_TH_PH10_HI)
print(f"임계 전단률 재현: G<={G_TH_PH10_LO:.0f}/s 전량 비응집, G>={G_TH_PH10_HI:.0f}/s 응집 발생")

# (3) 핵심 반례 — Camp 수만으로 판정하면 틀린다 (2019 §3.3)
G_c, t_c = 1000.0, 2500.0
camp_c = G_c*t_c
assert camp_c > CAMP_TH[10], "반례 전제: Camp가 임계를 넘어야 함"
assert pH10[(G_c,t_c)] is False, "원문: 이 조건에서 응집이 관측되지 않았다"
print(f"반례: G={G_c:.0f}/s x t={t_c:.0f}s -> Camp={camp_c:.2e} "
      f"(임계 {CAMP_TH[10]:.1e}의 {camp_c/CAMP_TH[10]:.2f}배)인데 응집 없음 "
      f"-> AND 조건(G>=G_th AND Gt>=Camp_th) 필요")

# (4) pH -> 임계 Camp 단조증가 (DLVO 반발장벽 순서와 일치)
phs = sorted(CAMP_TH)
vals = [CAMP_TH[p] for p in phs]
assert all(vals[i] < vals[i+1] for i in range(len(vals)-1)), "pH 증가 시 임계 Camp 단조증가여야"
ratio_10_over_2 = CAMP_TH[10]/CAMP_TH[2]
assert abs(ratio_10_over_2 - 15.0) < 1e-9
print(f"pH2 -> pH10 임계 Camp 비 = {ratio_10_over_2:.0f}배 (IEP 근처가 15배 취약)")
```

## 3. 생성항 (2) — 실제 팹 루프의 전단 노출량은 임계를 얼마나 넘는가

**Entegris "Filtration Characteristics of CMP Slurries" (Rakesh K. Singh, Application Note
4435-7590ENT-0214, 2014, entegris.com)** — 업체 기술문서(스코프 가중치 0.5)지만 **팹 루프의
회전수(turnover)를 명시한 유일하게 확보된 수치 출처**다:
- 벤치 루프에서 12 wt% 실리카를 5.0 µm 등급 루프 필터로 **4.3 L/min, 5시간 재순환 →
  34 turnovers/hour, 총 ~170 turnovers**.
- 본문 명시: "In a real life fab operation, the slurry typically goes through
  **one hundred turnovers** before it is consumed."

이 100 turnovers를 §2의 임계값과 대조하면, **팹 루프에서 Camp 수는 사실상 항상 초과**되고
**임계 전단률만이 실질적 설계 레버**라는 결론이 나온다(아래 verify).

```python verify
# --- Entegris AN 4435-7590 (2014): 루프 회전수 ---
TURNOVERS_PER_H = 34.0          # 문헌값 (4.3 L/min, 5h에 ~170 turnovers)
TOTAL_5H = 170.0                # 문헌값
FAB_TURNOVERS = 100.0           # 문헌값: 팹에서 소진 전 통상 회전수

sec_per_turn = 3600.0/TURNOVERS_PER_H
assert abs(TURNOVERS_PER_H*5 - TOTAL_5H) < 1e-9, "34/h x 5h = 170 내부 정합 실패"
print(f"1 turnover = {sec_per_turn:.1f} s (문헌값 34 turnovers/h와 정합)")

t_loop = FAB_TURNOVERS*sec_per_turn            # 팹 루프 총 체류시간 [s]
CAMP_TH_PH10 = 1.5e6                           # Khanna 2019
# 가정(명시): 루프 체류시간 전체가 전단률 G에 노출된다는 상한 가정.
for G in (100.0, 1500.0, 3000.0):
    camp = G*t_loop
    print(f"  G={G:6.0f}/s -> 100턴오버 누적 Camp={camp:.2e} "
          f"({camp/CAMP_TH_PH10:.1f}x pH10 임계)")
camp_at_Gth = 1500.0*t_loop
assert camp_at_Gth/CAMP_TH_PH10 > 10.0, "임계 전단률에서 Camp가 임계의 10배를 넘어야 함"
print(f"결론: G가 임계(1500/s)에 이르는 순간 Camp는 이미 임계의 "
      f"{camp_at_Gth/CAMP_TH_PH10:.1f}배 -> 팹 루프에서 구속조건은 '노출시간'이 아니라 '전단률'")
# 반대 방향 확인: 저전단(100/s)이면 100턴오버로도 Camp 임계 미달
assert 100.0*t_loop < CAMP_TH_PH10, "저전단 100/s는 100턴오버로도 Camp 임계 미만이어야"
print(f"  (저전단 100/s: Camp={100.0*t_loop:.2e} < {CAMP_TH_PH10:.1e} — 임계 미달)")

# --- Wood et al. 2019 (doi:10.1109/ASMC.2019.8791775) 벤치 루프 내부 정합 ---
FLOW_LPM = 5.0        # 문헌값: 5 L/min
MIN_PER_TURN = 4.0    # 문헌값: 1 tank turn ~ 4분
TURNS_FOR_1000L = 50.0  # 문헌값: 50 tank turns ~ 1,000 L
tank_L = FLOW_LPM*MIN_PER_TURN
vol = TURNS_FOR_1000L*tank_L
assert abs(vol - 1000.0) < 1.0, f"내부 정합 실패: {vol} L != 1000 L"
print(f"Wood2019 내부 정합: 탱크 {tank_L:.0f} L x 50턴 = {vol:.0f} L (원문 '약 1,000 L'와 일치)")
```

## 4. 제거항 (1) — 리텐션·beta ratio의 정의와 실측 스프레드

필터 성능은 두 등가 표기가 쓰인다. **단일통과 리텐션** E와 **beta ratio** β:

```
β_x = N_상류(≥x) / N_하류(≥x)        E = 1 − 1/β        β = 1/(1 − E)
```
(β는 유압/공정 필터 업계 표기, E는 CMP 문헌 표기. 같은 양의 다른 좌표다.)

Entegris AN 4435-7590 Table 1의 **단일통과 실측**(AccuSizer 780, 오차 ±5%):

| 슬러리 | CS05(0.5 µm 등급) ≥0.56 µm 리텐션 | Δp (psi) | 유량 (mL/min) |
|---|---|---|---|
| Silica-1 (~25 wt%) | **78 %** | 40 | 127 |
| Silica-2 (~25 wt%) | **90 %** | 28 | 275 |
| Ceria-1 (<1 wt%) | **56 %** | 12.7 | 469 |
| Alumina-1 (<1 wt%) | **88 %** | 19 | 450 |
| Alumina-2 (<1 wt%) | **83 %** | 14 | 458 |
| PSL 비드 챌린지 | **62 %** | 11.8 | 500 |

**PSL 비드가 보수적 대리시험이 아니다**는 점이 핵심 관찰이다: PSL(62 %)은 실리카·알루미나
슬러리보다 리텐션을 **과소평가**하고 세리아(56 %)보다는 **과대평가**한다. 즉 필터 등급
스펙만으로 실제 슬러리의 제거항을 예측할 수 없고, 화학종별 실측이 필요하다.

"리텐션을 조이면 Δp가 커져 수명이 짧아진다"는 통념은 이 6점에서 **Pearson r=0.46으로
약하게만** 성립한다. 원인은 교란이다 — Δp는 리텐션뿐 아니라 **고형분 농도**에도 강하게
의존하는데 표의 silica-1/-2는 ~25 wt%, 나머지는 <1 wt%다. 고형분을 통제해 <1 wt% 3건만
보면 **r=0.76으로 올라간다**(아래 verify). EVIDENCE-RULES §2③(교란 통제)의 전형적 사례이며,
**교란을 걷어내기 전의 r=0.46을 그대로 인용하면 안 된다**. 단 n=3이라 방향만 채택한다.

```python verify
# --- Entegris AN 4435-7590 (2014) Table 1: CS05(0.5um 등급), >=0.56um 누적 리텐션[%] ---
CS05 = {"silica-1":78.0, "silica-2":90.0, "ceria-1":56.0,
        "alumina-1":88.0, "alumina-2":83.0, "PSL":62.0}
# CMP1(1.0um 등급), >=1.01um 누적 리텐션[%]
CMP1 = {"silica-1":63.0, "ceria-1":53.0, "alumina-1":71.0, "alumina-2":69.0, "PSL":36.0}

beta = lambda E_pct: 1.0/(1.0 - E_pct/100.0)
for k,v in CS05.items():
    print(f"  CS05 {k:10s}: E={v:.0f}%  -> beta={beta(v):.2f}")
# 항등식 왕복 검증 (E -> beta -> E)
for v in CS05.values():
    assert abs((1.0 - 1.0/beta(v))*100.0 - v) < 1e-9
print("beta<->리텐션 항등식 왕복 재현 OK (E = 1 - 1/beta)")

# 문헌값 대조: 78% -> beta 4.55, 88% -> beta 8.33, 56% -> beta 2.27
assert abs(beta(78.0) - 4.545) < 0.01 and abs(beta(88.0) - 8.333) < 0.01
assert abs(beta(56.0) - 2.273) < 0.01
print(f"문헌값 대조: 78% -> beta {beta(78.0):.2f}, 56% -> beta {beta(56.0):.2f} "
      f"(세리아는 실리카 대비 beta가 {beta(78.0)/beta(56.0):.1f}배 낮다)")

# PSL은 보수적 대리시험이 아니다 — 양방향으로 빗나간다
assert CS05["PSL"] < CS05["silica-1"], "PSL이 실리카를 과소평가해야(관측)"
assert CS05["PSL"] > CS05["ceria-1"],  "PSL이 세리아를 과대평가해야(관측)"
print(f"PSL {CS05['PSL']:.0f}% 는 silica-1 {CS05['silica-1']:.0f}% 를 과소, "
      f"ceria-1 {CS05['ceria-1']:.0f}% 를 과대평가 -> 단방향 안전여유로 쓸 수 없음")

# 등급이 조이면 리텐션이 오른다(같은 슬러리, CS05 0.5um vs CMP1 1.0um)
for k in ("silica-1","ceria-1","alumina-1","alumina-2","PSL"):
    assert CS05[k] > CMP1[k], f"{k}: 조인 등급이 더 높은 리텐션을 줘야"
print("등급 0.5um(CS05) > 1.0um(CMP1) 리텐션 — 5개 슬러리 전부에서 성립")

# 리텐션과 Δp의 트레이드오프 — 교란(wt% 고형분)을 걷어내야 보인다
import numpy as np
E_all  = np.array([78, 90, 56, 88, 83, 62], float)          # silica-1,-2, ceria-1, alu-1,-2, PSL
dp_all = np.array([40, 28, 12.7, 19, 14, 11.8], float)
r_all = float(np.corrcoef(E_all, dp_all)[0, 1])
print(f"전체 6건 리텐션 vs Δp Pearson r={r_all:.2f}  <- 기대만큼 높지 않다")
assert 0.3 < r_all < 0.6, f"전체 상관은 약한 수준(0.3~0.6)으로 나와야 하는데 r={r_all:.2f}"

# 원인: Δp는 고형분 농도에도 강하게 의존한다(silica-1/-2는 ~25 wt%, 나머지는 <1 wt%).
# 교란을 걷어내고 저고형분(<1 wt%) 슬러리 3건만 보면 상관이 회복된다.
E_low  = np.array([56, 88, 83], float)      # ceria-1, alumina-1, alumina-2 (모두 <1 wt%)
dp_low = np.array([12.7, 19, 14], float)
r_low = float(np.corrcoef(E_low, dp_low)[0, 1])
assert r_low > r_all, "교란(고형분)을 통제하면 상관이 올라가야 한다"
print(f"저고형분(<1 wt%) 3건만: r={r_low:.2f} (전체 {r_all:.2f} 대비 "
      f"{(r_low-r_all)/abs(r_all)*100:.0f}% 상승) -> 조일수록 Δp 증가 = 수명 단축 트레이드오프는 "
      f"고형분을 통제했을 때만 드러난다 (n=3이라 유의성은 주장 불가, 방향만)")
```

## 5. 제거항 (2) — 왜 깊이필터가 "체"처럼 작동하지 않는가 (DLVO가 지배)

**Rastegar, V., Ahmadi, G., Babu, S.V. (2017). "Filtration of aqueous colloidal ceria slurries
using fibrous filters – An experimental and simulation study." *Separation and Purification
Technology* 176, 231–242. DOI: 10.1016/j.seppur.2016.12.017** (미러 사이트 폴백으로 전문 확보)

폴리프로필렌 부직 섬유 필터(**섬유경 d_f = 2 µm, 섬유 부피분율 α ≈ 20 %**)에 콜로이드
세리아(35–600 nm)를 통과시키고, UV-vis로 상·하류 농도를 재어 `E = 1 − C_out/C_in`을
측정. 동시에 ANSYS-FLUENT로 단일섬유 주위 유동에 **항력·양력·Brownian·EDL·vdW**를 모두
넣은 Lagrangian 입자추적으로 단일섬유 포집효율 η를 계산했다(면속도 **0.38 mm/s**).

### 5.1 핵심 결과 — 포집은 기하가 아니라 정전기가 정한다
필터 섬유의 제타전위는 −15 mV(음)이다. 입자 제타전위를 pH로 바꿔가며 측정한
**실험 단일섬유 효율 η**(원문 Fig. 17·18, 그래프 판독값 ±0.01):

| pH | 입자 제타 | η(실험) |
|---|---|---|
| 3 | 강한 양 | **0.20** |
| 4 | 양 | 0.18 |
| 5.5 | 약한 양 | 0.142 |
| 7.5 | 음(IEP 초과) | **0.025** |
| 11 | 강한 음 | **0.005** |

세리아 IEP ≈ **pH 6.5**를 넘는 순간 효율이 절벽처럼 떨어진다(5.5 → 7.5에서 **5.7배 감소**).
입자와 섬유가 같은 부호로 대전되면 EDL 반발이 포집을 막기 때문이다.

**이것이 이 단원에서 가장 중요한 인과 연결이다**: 선행 노트
[[colloidal-destabilization-lpc-defect-mechanism]]와 [[../cmp/colloid-zeta-dlvo-slurry-stability]]가
말하는 "슬러리를 안정하게 만드는 강한 음전하"는, **같은 이유로 필터가 대입자를
못 잡게 만든다**. 안정성과 여과성은 같은 DLVO 파라미터의 상충하는 두 요구다.
실무 함의: pH 10–11에서 돌리는 실리카 슬러리(Khanna의 EM3530K, Seo의 퓸드실리카 pH 10–11)는
전단 응집에는 가장 강하지만(§2.3), 그 대입자를 필터로 걷어내기는 가장 어려운 조건이다.

### 5.2 표준 섬유필터 모델과의 정합 — 왜 리텐션이 100 %가 아닌가
섬유 여과의 표준 폐형식(단일섬유 효율 η → 필터 전체 효율 E):

```
E = 1 − exp( −4 α η L / (π d_f (1−α)) )
```
(α=섬유 부피분율, L=매질 두께. 원문은 Eq. (S4)로 인용하나 **보충자료에 있어 원 식을
확보하지 못했다 — 여기 쓴 것은 표준 문헌형이며, 원문 식과의 문자 대조는 ⚠ 미검증**.)

이 식에 Rastegar가 **우호 조건**에서 잰 η=0.1~0.2를 넣으면, 실제 깊이필터 두께(mm 단위)
에서 E는 사실상 **100 %**가 되어야 한다. 그런데 Entegris 실측 단일통과 리텐션은 56–90 %다.
모순을 해소하려면 실제 팹 슬러리에서 η가 **10⁻³~10⁻² 수준**이어야 하고 — 그 값이 바로
Rastegar가 **반발(음-음) 조건**에서 측정한 η(0.005~0.025)다. 두 독립 출처가 여기서 만난다.

```python verify
import math

# --- Rastegar et al. 2017 (doi:10.1016/j.seppur.2016.12.017) 실험 단일섬유 효율 ---
eta_exp = {3.0:0.200, 4.0:0.180, 5.5:0.142, 7.5:0.025, 11.0:0.005}  # Fig.18 판독값
IEP_CERIA = 6.5   # 원문 본문 명시

phs = sorted(eta_exp)
assert all(eta_exp[phs[i]] > eta_exp[phs[i+1]] for i in range(len(phs)-1)), "pH 증가 -> η 단조감소"
drop = eta_exp[5.5]/eta_exp[7.5]
assert drop > 5.0, f"IEP({IEP_CERIA}) 전후 급락이 5배를 넘어야 하는데 {drop:.2f}배"
print(f"IEP(pH {IEP_CERIA}) 횡단: η {eta_exp[5.5]:.3f} -> {eta_exp[7.5]:.3f} = {drop:.1f}배 감소")
print(f"pH3 vs pH11 극단 비: {eta_exp[3.0]/eta_exp[11.0]:.0f}배")

# --- 표준 섬유필터 모델 (원문 Eq.(S4)는 보충자료 미확보 -> 표준형 사용, 미검증 표기) ---
ALPHA, D_F = 0.20, 2.0e-6      # Rastegar 문헌값: 섬유 부피분율 20%, 섬유경 2 um
def E_filter(eta, L):
    return 1.0 - math.exp(-4.0*ALPHA*eta*L/(math.pi*D_F*(1.0-ALPHA)))
def eta_required(E, L):
    return math.log(1.0/(1.0-E))*math.pi*D_F*(1.0-ALPHA)/(4.0*ALPHA*L)

# (1) 우호 조건 η=0.1을 두께 5mm에 넣으면 사실상 100% -> 실측 78%와 모순
E_pred = E_filter(0.10, 5.0e-3)
assert E_pred > 0.999, "우호 조건에서는 모델이 사실상 완전포집을 예측해야"
print(f"모델 예측 E(η=0.10, L=5mm) = {E_pred*100:.4f}% vs Entegris 실측 78% -> 모순")

# (2) 실측 78%를 만들려면 η가 얼마여야 하는가 (두께는 원문 미기재 -> 1~5mm 범위 가정)
lo, hi = eta_required(0.78, 5.0e-3), eta_required(0.78, 1.0e-3)
print(f"역산: E=78%를 주는 η = {lo:.2e}(L=5mm) ~ {hi:.2e}(L=1mm)")
# 이 구간이 Rastegar의 '반발 조건' 실측 η(0.005, pH11)를 품는가?
assert lo <= eta_exp[11.0] <= hi, (
    f"역산 구간 [{lo:.2e},{hi:.2e}]이 반발조건 실측 η={eta_exp[11.0]} 를 포함해야")
print(f"-> 역산 구간이 Rastegar 반발조건 실측 η={eta_exp[11.0]} (pH11)를 포함. "
      f"즉 팹 슬러리의 저리텐션은 '얇은 필터'가 아니라 'EDL 반발로 η가 1~2자릿수 낮아진 것'으로 설명된다")
# 반대로 우호조건 η(pH3)는 역산 구간 밖(너무 큼)이어야 한다
assert eta_exp[3.0] > hi
print(f"   (우호조건 η={eta_exp[3.0]}는 역산 상한 {hi:.2e}보다 {eta_exp[3.0]/hi:.0f}배 커서 구간 밖)")
```

## 6. 제거항 (3) — POU 필터의 실측 효과와 유량 의존성

**Seo, Y.-J., Kim, S.-Y., Lee, W.-S. (2003). "Advantages of point of use (POU) slurry filter and
high spray method for reduction of CMP process defects." *Microelectronic Engineering* 70, 1–6.
DOI: 10.1016/S0167-9317(03)00278-8** (미러 사이트 폴백으로 전문 확보). IPEC Avanti 472,
IC-1000/Suba-IV, 퓸드실리카 KOH계 pH 10–11, 11 wt%. **0.5 µm 깊이형 POU 필터**
(제조사 스펙: 1.0 µm 입자에 대해 **80 % 이상 여과효율**).

정량 결과(원문 본문·Fig. 4):
- 무필터 시 1–2 µm 입자수 **5,000 ~ 17,000** → POU 필터 통과 시 **3,500 ~ 500**,
  **2 µm 초과는 전량 제거**.
- POU 필터 수명(스크래치 억제 관점) ≈ **3주**: 설치 21일째부터 마이크로스크래치 결함이
  나타나고 31일째부터 1 µm 초과 스크래치가 나타남(0.5 µm 필터가 0.7 µm 필터보다 항상 낮은
  결함밀도).
- **유량 의존성**(원문 Fig. 5, 판독값): 슬러리 유량 200/400/700/1000 mL/min에서 ~1.1 µm
  피크 카운트가 각각 **≈2,000 / 2,300 / 3,300 / 7,000**로 증가 — 저자 결론
  "유량이 오를수록 POU 필터의 대입자 여과효율이 떨어진다."

유량 의존성은 §5의 물리와 정합한다: 면속도가 오르면 (a) 섬유 근방 체류시간이 줄어
Brownian·차단 포집 기회가 줄고 (b) 이미 잡힌 입자에 걸리는 항력이 커져 재비산이 늘어난다.

```python verify
import numpy as np

# --- Seo et al. 2003 (doi:10.1016/S0167-9317(03)00278-8) ---
# Fig.5 판독값(그래프 판독 -> 정확도 한계 있음, 아래에서 미검증으로 다룸)
Q = np.array([200.0, 400.0, 700.0, 1000.0])          # mL/min
N = np.array([2000.0, 2300.0, 3300.0, 7000.0])       # ~1.1um 피크 카운트

assert all(N[i] < N[i+1] for i in range(len(N)-1)), "유량 증가 -> 대입자 통과 단조증가여야(원문 결론)"
slope, intercept = np.polyfit(np.log(Q), np.log(N), 1)
pred = np.exp(intercept)*Q**slope
r2 = 1.0 - ((N-pred)**2).sum()/((N-N.mean())**2).sum()
print(f"거듭제곱 적합: N ∝ Q^{slope:.2f}, R²={r2:.3f}")
assert slope > 0.5, f"지수가 0.5를 넘어야 '유량이 지배적'이라 말할 수 있는데 {slope:.2f}"
# 정직성: R²가 0.8 미만이면 거듭제곱 형태 자체가 최적이 아니다
assert r2 < 0.9, "R²가 0.9 미만임을 기록(판독 4점, 거듭제곱 가정은 잠정)"
print(f"5배 유량(200->1000 mL/min)에서 대입자 통과 {N[-1]/N[0]:.1f}배 증가")

# 본문 수치: 무필터 1-2um 5000~17000 -> POU 필터 후 3500~500
no_filter = (5000.0, 17000.0); with_filter = (3500.0, 500.0)
# 상한끼리 비교하면 리텐션 하한을 얻는다
ret_hi = 1.0 - with_filter[0]/no_filter[1]
assert ret_hi > 0.7, "상한 기준 리텐션이 70%를 넘어야 (제조사 스펙 80%와 정합)"
print(f"1-2um 구간 리텐션(상한 기준) = {ret_hi*100:.0f}% "
      f"(제조사 스펙 '1.0um 입자 80% 이상'과 같은 자릿수)")
```

## 7. 두 항의 합 — 재순환 실측이 이상 제거모델을 크게 밑돈다

**Wood, B.H., Hsu, A., Shie, B. (2019). "The Benefits of Multi-Stage Filtration for Improved CMP
Slurry Large Particle Retention." *2019 30th Annual SEMI ASMC*, 194–197.
DOI: 10.1109/ASMC.2019.8791775** (Entegris 소속 저자, 학회 발표논문 — 스코프 가중치 0.5;
미러 사이트 폴백으로 전문 확보).

벤치 루프에서 실리카 슬러리를 **5 L/min**(탱크 20 L, 1 tank turn ≈ 4분)으로 순환시키며
**T0(단일통과)** 와 **T25(25 tank turns)** 시료를 각각 **최초 feed 대비**로 비교했다.
CDS 필터 등급 5 / 0.5 / 0.3 µm × POU 70 nm 유무의 조합. 원문 Fig. 4–6 판독값:

| 채널 | CDS 5 µm T0 | CDS 5 µm T25 | CDS 0.3 µm T0 | CDS 0.3 µm T25 |
|---|---|---|---|---|
| ≥0.3 µm | 0.10 | 0.405 | 0.91 | 1.00 |
| ≥0.5 µm | 0.62 | 0.66 | 0.95 | 0.95 |
| ≥1 µm | 0.62 | 0.835 | 0.955 | 0.99 |

### 7.1 이상 모델 — 완전혼합 재순환 탱크(CSTR)
잘 섞인 탱크에서 유량 Q, 단일통과 효율 E로 순환하면 생성항이 없을 때
```
C(n)/C₀ = exp(−E·n),   누적제거율 R(n) = 1 − exp(−E·n)   (n = tank turns)
```
가장 열린 CDS 5 µm, ≥0.3 µm 채널에서 E=0.10이므로 n=25에서 R=**91.8 %**가 예측된다.
**실측은 40.5 %**다. 역산한 실효 효율은 E_eff=0.021로, 단일통과 실측치의 **1/4.8**이다.
세 채널 전부에서 같은 방향의 갭이 나오며 그 크기는 **1/4.8 ~ 1/14.4**다
(≥0.5 µm에서 가장 크고 ≥0.3 µm에서 가장 작다 — 아래 verify 출력).

### 7.2 해석 — 이 갭이 §2의 생성항을 요구한다
제거만 있는 모델이 실측을 **과대예측**한다는 것은, 순환 중 **LPC가 계속 만들어지고 있다**는
뜻이다. 가장 자연스러운 후보가 §2의 펌프 전단 응집이다(Wood 루프의 펌프 사양·전단률은
원문 미기재 — ⚠ **미검증**, 인과를 단정하지 않는다). 대안 가설 둘도 배제하지 못했다:
(b) "tank turn" 회계가 각 유체 요소의 필터 통과 횟수와 1:1이 아닐 가능성,
(c) 깊이필터가 시간에 따라 로딩되며 리텐션이 변하는 효과. **어느 하나를 고르기에는
근거가 부족하다**(EVIDENCE-RULES §절차 3: 스코프를 쪼개어 셋을 병렬 가설로 남긴다).
다만 **"제거만으로는 설명이 안 된다"**는 부등호 자체는 세 가설 어느 쪽에서도 성립한다 —
이것이 이 절의 검증된 결론이다.

### 7.3 다단(multi-stage) 구성의 실측 이득
- 원문 초록: SDS 필터 개선만으로 **LPC(>0.5 µm) 60 % 감소**, POU 필터를 추가하면 **80–90 %**.
- 촘촘한 CDS(0.3 µm)에서는 T0≈T25로 **포화** — 순환을 더 돌려도 이득이 없다. 반면 열린
  CDS(5 µm)에서만 순환 횟수 의존성이 크게 나타난다.
- 작동입자(mean PSD)는 가장 촘촘한 조합(CDS 0.3 µm + POU 70 nm)에서도 **유의하게 이동하지
  않았다**(원문 Fig. 7) — "필터를 조이면 연마입자까지 걸러 MRR이 떨어진다"는 우려에 대한
  직접 반증.
- 수명: POU 단독이면 50 tank turns(≈1,000 L)에 Δp **+15 %**, CDS 가드필터를 앞에 두면
  같은 체적에서 **증가폭이 절반**.

```python verify
import math

# --- Wood et al. 2019 (doi:10.1109/ASMC.2019.8791775) Fig.4-6 판독값 ---
# 채널: (CDS 5um T0, CDS 5um T25, CDS 0.3um T0, CDS 0.3um T25)
data = {">=0.3um": (0.100, 0.405, 0.910, 1.000),
        ">=0.5um": (0.620, 0.660, 0.950, 0.950),
        ">=1um"  : (0.620, 0.835, 0.955, 0.990)}
N_TURNS = 25.0

print("완전혼합(CSTR) 이상 모델  R(n)=1-exp(-E*n) 과 실측 대조 (CDS 5um, n=25):")
ratios = []
for ch,(E0,E25,_,_) in data.items():
    pred = 1.0 - math.exp(-E0*N_TURNS)
    E_eff = -math.log(1.0-E25)/N_TURNS
    ratios.append(E0/E_eff)
    print(f"  {ch:8s}: 예측 {pred*100:6.2f}% vs 실측 {E25*100:5.1f}% "
          f"-> 실효효율 {E_eff:.4f} (단일통과의 1/{E0/E_eff:.1f})")
    assert pred > E25, f"{ch}: 제거만 있는 모델은 실측을 과대예측해야(생성항 존재의 증거)"
assert min(ratios) > 3.0, f"갭이 3배 이상이어야 유의미한데 최소 {min(ratios):.1f}배"
print(f"모든 채널에서 과대예측, 실효효율 저하 {min(ratios):.1f}~{max(ratios):.1f}배 "
      f"-> 순환 중 LPC 생성항이 존재해야 수지가 맞는다")

# 촘촘한 CDS(0.3um)에서는 순환 이득이 포화 (T25-T0 가 열린 필터보다 작아야)
for ch,(E0,E25,T0t,T25t) in data.items():
    gain_open, gain_tight = E25-E0, T25t-T0t
    assert gain_tight <= gain_open + 1e-9, f"{ch}: 촘촘한 필터에서 순환 이득이 더 작아야"
    print(f"  {ch:8s}: 순환이득 CDS5um {gain_open:+.3f} vs CDS0.3um {gain_tight:+.3f}")

# 초록 명시 수치: SDS 개선 60%, +POU 80-90%
LPC_SDS, LPC_SDS_POU = 0.60, (0.80, 0.90)
assert LPC_SDS_POU[0] > LPC_SDS
resid = (1-LPC_SDS_POU[0])/(1-LPC_SDS)
print(f"초록 문헌값: SDS만 {LPC_SDS*100:.0f}% 저감 -> +POU {LPC_SDS_POU[0]*100:.0f}~"
      f"{LPC_SDS_POU[1]*100:.0f}% 저감 (잔존 LPC가 {resid:.2f}배로 추가 감소)")

# 수명: POU 단독 50턴에 Δp +15%, CDS 가드 추가 시 증가폭 절반
DP_POU_ONLY, DP_WITH_GUARD = 0.15, 0.15/2
assert abs(DP_WITH_GUARD - 0.075) < 1e-9
print(f"수명: 50 tank turns(약 1,000 L)에서 Δp 증가 {DP_POU_ONLY*100:.0f}% -> "
      f"CDS 가드 추가 시 {DP_WITH_GUARD*100:.1f}% (절반)")
```

## 8. 한계·정직성 표기

- ⚠ **미검증**: §5.2의 섬유필터 폐형식은 Rastegar 원문이 Eq. (S4)로 보충자료에 둔 식이며,
  **보충자료를 확보하지 못해** 표준 문헌형을 대신 썼다. 문자 일치는 확인하지 못했고,
  역산한 η 구간(1.9×10⁻³~9.5×10⁻³)은 매질 두께 L=1~5 mm라는
  **저자가 명시하지 않은 가정** 위에 있다. 결론(반발 조건 η와 자릿수가 맞는다)은
  자릿수 수준의 주장이며 계수 수준의 주장이 아니다.
- ⚠ **미검증**: §6 Seo 2003의 유량-카운트 4점과 §7의 Wood 2019 막대값은 모두
  **그래프 판독값**이다(원문에 수치표 없음). 판독오차를 ±5 % 정도로 보면 §6의
  거듭제곱 지수(≈0.71, R²≈0.77)는 형태 가정 자체가 잠정이다 — 지수를 sim/ 상수로
  옮기면 안 된다.
- ⚠ **미검증**: §7.2의 세 가설(펌프 전단 생성 / turnover 회계 / 필터 로딩) 중 어느 것이
  지배적인지 확정할 근거가 없다. Wood 2019는 루프 펌프의 종류·전단률을 기재하지 않았다.
- ⚠ **확인 못함**: Khanna의 임계 전단률·Camp 수는 **35 nm 실리카 10 wt% 한 계**에서만
  측정됐다. 세리아·알루미나, 다른 고형분, 계면활성제 첨가계로의 이식 가능성은 저자들도
  "future work"로 남겼다. 화학종이 바뀌면 임계값을 그대로 쓰면 안 된다(§2.3의 pH 의존성
  15배 스프레드가 그 경고다).
- **레오미터 ≠ 펌프**: Khanna의 G는 동심원통 레오미터의 **균일 전단**이다. 실제 펌프(벨로즈·
  다이어프램·원심)는 국소적으로 훨씬 높은 전단이 좁은 영역에 걸린다. 원문도 Litchy &
  Schoeb(Levitronix 기술자료)를 인용해 원심펌프가 100–1000 Pa 응력을 준다고만 적었다 —
  **그 자료는 확보하지 못해 2차 인용**이며, 응력(Pa)과 전단률(1/s) 사이 환산에 필요한
  점도 조건도 명시되지 않아 이 노트는 환산을 시도하지 않았다.
- **좋은 소식 하나**: §7.3의 "작동입자 PSD는 안 움직인다"는 결과는 원문 Fig. 7의 직접
  비교이며, 필터를 조이는 것의 부작용 우려를 낮춘다. 다만 단일 실리카 슬러리 1건이다.

## 9. sim/에 대한 시사점 (코드는 건드리지 않음 — PROFILE.md 구현 요청으로 기록)

1. **전단 응집 판정은 AND 조건**(§2.4). Camp 수 단일 스칼라로 게이트를 만들면 문헌
   반례(G=1000 s⁻¹×2500 s)에서 틀린다.
2. **LPC는 상태량이지 입력 상수가 아니다**(§7). 슬러리 팩의 `abrasive_d99_nm` /
   `aggregate_ratio`는 "제조 시 값"이 아니라 "루프 이력을 통과한 값"이어야 한다.
   생성항−제거항 수지가 필요하다.
3. **필터 리텐션은 화학종·pH 의존**(§4, §5). 등급(µm)만으로 β를 정하면 세리아에서 2.3배,
   실리카에서 4.5배로 2배 어긋난다.

## 10. 자기시험
→ [[../../agents/slurry-colloid/EXAMS.md]] Lv2-1 문항 참조.
