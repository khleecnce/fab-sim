<!-- V2-SECTION: R2-slurry | 공동: R1-equipment | 분배완료 2026-09-08 | 근거: chemistry, passivation, pourbaix, slurry, 화학 | 정본: ARCHITECTURE-V2.md §3 -->
# 마찰열·계면 온도장 → Arrhenius 화학반응속도 결합 (CMP 열-화학 커플링)

> 에이전트: tribologist Lv2-2 | 작성일: 2026-09-06
> [[tribology-friction-wear-stribeck]] [[cmp-lubrication-regimes]] [[cmp-slurry-flow-lubrication-film-thickness]] [[surface-chemistry-cu-w-pourbaix-passivation]] [[preston-luo-dornfeld-mrr]]

## 1. 왜 필요한가 — 마찰과 화학을 잇는 잃어버린 고리
[[tribology-friction-wear-stribeck]]에서 CMP를 마찰(COF)·마모(Archard)로, [[surface-chemistry-cu-w-pourbaix-passivation]]에서
표면반응(산화막 형성)으로 각각 다뤘다. 그런데 이 둘은 **온도**로 물리적으로 결합한다: 마찰이 하는 일이
계면을 데우고(마찰열), 그 온도가 Arrhenius 법칙을 통해 화학반응속도(→화학 MRR)를 배수로 증폭한다.
[[preston-luo-dornfeld-mrr]]의 K_p가 "슬러리 화학에 민감한 이유"의 상당 부분이 이 열-화학 커플링이다.
이 단원은 (1) 마찰동력 q=μPV, (2) 계면 온도장(평균·플래시·열확산), (3) Arrhenius 결합, (4) 공정 함의를
문헌 공정조건으로 정량 대조한다.

## 2. 마찰열 발생 — 단위면적당 발열 q = μ·P·V
미끄럼 마찰이 소산하는 동력은 마찰응력(τ=μ·P)×미끄럼속도(V)이므로 **단위면적당 발열유속**은
```
q = μ · P · V        [W/m²]   (μ=COF, P=명목압력[Pa], V=상대속도[m/s])
전체 마찰동력  Q_f = q · A_wafer = μ · P · V · A_wafer   [W]
```
이는 [[tribology-friction-wear-stribeck]]의 마찰력 F=μN에 속도를 곱한 마찰동력의 면적밀도이며,
CMP는 boundary~mixed 레짐([[cmp-lubrication-regimes]])이라 μ가 커서(oxide CMP COF 0.23~0.40) 발열이 크다.
Ma et al.(2023)은 selective-layer CMP를 P=0.05 MPa, V=0.75 m/s, 슬러리 150 mL/min 조건에서 마찰력
F_f=18.5~57 N을 실측하고, 마찰에너지 E_f=v_r∫F_f dt가 온도·MRR과 상관함을 보였다
(Ma, Belkhir et al., *Materials* 16(7) 2550, 2023, DOI 10.3390/ma16072550, PMC10095230, CC BY, EuropePMC 전문 확인).
White et al.(2003)은 CMP 마찰열을 **약 200~300 W**로, 화학열은 ~1 W로 산정해 **발열은 마찰이 지배**함을
보였다(White, Melvin, Boning, *J. Electrochem. Soc.* 150 G271, 2003, DOI 10.1149/1.1560642 — Shin 2025 §2.2 재인용,
원문 초록만 확인). §6 verify 블록에서 q=μPV(전형값)로 이 200~300 W 오더를 재현한다.

## 3. 계면 온도장 — 평균 상승, 플래시 온도, 패드 저열전도
발생한 q는 세 곳으로 분배된다: 슬러리(대류 냉각), 웨이퍼, 패드. **핵심 비대칭**은 다공성 폴리우레탄
패드의 열전도도가 극히 낮다는 점이다 — **k_pad ≈ 0.02 W/m·K**(Shin et al. 2025) — 그래서 마찰열의
상당량이 패드 심부로 빠지지 못하고 **계면 근처에 축적**되어 웨이퍼·슬러리 쪽으로 흐른다.
- **평균 온도상승 ΔT (수~수십 ℃):** Shin et al.(2025)은 미제어 CMP에서 90초 후 패드온도가 약 36 ℃까지
  상승, 보텍스튜브 냉각 시 약 30 ℃로 유지(무냉각 대비 3 ℃+ 높음)를 실측했다
  (Shin et al., *Materials* 18(19) 4461, 2025, DOI 10.3390/ma18194461, PMC12525981, CC BY, EuropePMC 전문 확인).
  §6에서 "모든 마찰열이 슬러리 유량으로 제거된다"는 에너지균형 상한을 계산해 이 수~수십 ℃ 오더를 대조한다.
- **플래시 온도(flash temperature):** asperity 접촉 순간의 국소 순간고온([[hertz-gw-contact-mechanics]]의
  실접촉점에서만 발생). 실접촉면적 A_r ≪ A_nominal이라 국소 열유속 q_local=q·(A_n/A_r)이 평균의 수십 배가
  되어, 접촉점 순간온도는 평균 웨이퍼온도보다 훨씬 높을 수 있다(Shin 2025는 "화학반응온도는 transient
  flash heating이 결정"이라 서술). **플래시 온도의 정량 절대값은 본 노트에서 미검증**(Blok/Archard flash
  모델 결합은 Lv3 후보).
- **열확산 스케일:** 특성 열확산 길이 ℓ_th≈√(α·t)로, 접촉 통과시간 t가 짧을수록 열이 얕게 갇힌다 —
  패드 저열전도(낮은 α)가 표면 열집중을 강화하는 물리적 근거(§6 sanity check).

## 4. Arrhenius 결합 — 온도가 화학 MRR을 배수로 증폭
화학반응 속도상수는 Arrhenius 법칙을 따른다. Shin et al.(2025)은 **제거율(RR)을 반응속도의 대리변수**로 두고
CMP에 직접 적용했다(원문 Eq.1-2):
```
RR = A · exp(−Ea/RT)     ⟺     ln RR = −(Ea/R)·(1/T) + ln A
  Ea: 겉보기 활성화에너지[J/mol], R=8.314 J/(K·mol), T: 평균 공정온도[K], A: 빈도인자(Å/min)
```
ln RR vs 1/T 기울기(=−Ea/R)에서 겉보기 Ea를 얻는다. Shin et al.(2025) 실측 겉보기 활성화에너지(blanket wafer):

| 재료 | Ea [kJ/mol] | ln A | 온도민감도 |
|---|---|---|---|
| SiO₂ | 8.75 | 9.7 | 낮음(거의 온도무관) |
| Ta | 29.9 | 18.1 | 중간 |
| Cu | 151.7 | 66.3 | 매우 높음(온도로 급증) |

**두 온도 T1→T2 사이 반응속도 배율** = exp[(Ea/R)·(1/T1 − 1/T2)]. §6에서 ΔT=20 ℃(30→50 ℃)일 때 Cu는
약 41배, Ta 2.1배, SiO₂ 1.2배로 계산된다 — 즉 **같은 온도상승이 Cu MRR은 수십 배 키우고 oxide는 거의
안 바꾼다.** 이것이 "공정온도로 Cu/barrier/oxide **선택비**를 조절"하는 Shin 논문의 핵심이자, [[preston-luo-dornfeld-mrr]]의
K_p가 온도(=마찰조건)에 민감한 이유의 화학적 근거다. DeNardis et al.이 Cu 산화율의 Arrhenius 거동을 보인 것과
정합(Shin 2025 §서론 재인용, 원문 미확인).

## 5. EPD·공정 함의 — 온도 모니터링과 정상상태
- **온도 실시간 모니터링:** 계면온도(IR 센서·플래튼 열화상)는 마찰상태와 화학속도를 동시에 반영하는
  in-situ 지표 → [[cmp-lubrication-regimes]]의 COF 모니터링과 함께 EPD·공정드리프트 진단에 쓴다(Lv3-1 심화).
- **정상상태 온도:** 발열 Q_f=μPV·A와 냉각(슬러리 대류+패드 확산)이 평형을 이루는 T_ss가 존재. 냉각을
  키우면(보텍스튜브) T_ss를 낮춰 Cu MRR을 억제, dishing을 줄인다(Shin 2025: 30 ℃ 유지가 선택비·dishing 최적).
- **되먹임 주의:** 온도↑ → 화학연화(H↓, [[surface-chemistry-cu-w-pourbaix-passivation]]) → MRR↑ → 마찰일↑ →
  온도↑의 양의 되먹임 가능성. 냉각제어가 이 폭주를 끊는다.

## 6. Python 재현 & 문헌 대조
```python verify
import math
R = 8.314  # J/(K mol)

# --- (1) 마찰열 q=uPV : Ma et al. 2023 공정조건, oxide CMP COF 오더 ---
mu, P, V = 0.3, 0.05e6, 0.75            # COF~0.3, 0.05 MPa, 0.75 m/s (Ma 2023 조건)
q = mu * P * V                          # W/m^2
A = math.pi * 0.1**2                    # 200mm 웨이퍼 면적 [m^2]
Qf = q * A                              # 전체 마찰동력 [W]
print(f"q=uPV = {q:.0f} W/m^2, Q_f = q*A = {Qf:.0f} W")
assert abs(q - 11250) < 1, q
# White et al. 2003 문헌값: 마찰열 200~300 W. 우리 Q_f=353W는 같은 오더(수백 W).
assert 100 < Qf < 700, "White 200-300W 오더 밖"
# 역산: 200-300W를 200mm 웨이퍼 면적으로 나눈 열유속도 q=uPV 오더(1e4 W/m^2)와 부합
for Wt in (200, 300):
    flux = Wt / A
    assert 5e3 < flux < 1e4, flux
print(f"  White 200-300W -> {200/A:.0f}~{300/A:.0f} W/m^2 (q=uPV 오더와 부합)")

# --- (2) 평균 온도상승: 마찰열 전량이 슬러리로 제거된다는 에너지균형 상한 ---
rho, cp, flow = 1000.0, 4180.0, 150e-6/60   # 물기반 슬러리, 150 mL/min
mdot = rho * flow
for Qh in (200, 300):
    dT = Qh / (mdot * cp)
    print(f"  Q={Qh}W -> dT_상한 = {dT:.1f} C")
    assert 5 < dT < 40, dT          # 수~수십 C 오더 (실측 ~36C, 문헌과 오더 일치)
# Shin 2025 실측: 미제어 ~36C, 제어 ~30C. 상한 추정(19~29C)이 이 수~수십C 오더를 포괄.

# --- (3) Arrhenius 반응속도 배율: Shin et al. 2025 문헌 Ea로 dT=20C(30->50C) ---
Ea_lit = {"SiO2": 8.75e3, "Ta": 29.9e3, "Cu": 151.7e3}   # J/mol (Shin 2025 실측)
T1, T2 = 303.15, 323.15   # 30C, 50C
ratio = {m: math.exp(Ea/R*(1/T1 - 1/T2)) for m, Ea in Ea_lit.items()}
for m in ("SiO2", "Ta", "Cu"):
    print(f"  {m}: Ea={Ea_lit[m]/1e3:.2f} kJ/mol -> 30->50C 배율 = {ratio[m]:.2f}x")
# Cu는 수십 배(선택비 급변), oxide는 거의 불변 — Shin 논문 핵심 주장 정량 재현
assert 35 < ratio["Cu"] < 50, ratio["Cu"]      # ~41.5x
assert 1.1 < ratio["SiO2"] < 1.4, ratio["SiO2"] # ~1.24x
assert ratio["Cu"] > 20 * ratio["SiO2"], "Cu/oxide 선택비 온도민감도 대비"

# --- (4) ln A 재구성 sanity: Cu Ea=151.7kJ/mol, lnA=66.3에서 RR@303K 산출 ---
lnA_Cu = 66.3
RR_Cu = math.exp(lnA_Cu) * math.exp(-Ea_lit["Cu"]/(R*303.15))  # A/min
print(f"  Cu RR@30C = {RR_Cu:.0f} A/min  (Shin: 30C 부근 400~500 A/min 수렴)")
assert 100 < RR_Cu < 2000, RR_Cu   # 문헌 수백 A/min 오더

# --- (5) 열확산 길이 sanity: 패드 저열전도가 표면 열집중 강화 ---
# alpha = k/(rho*cp). 패드 k=0.02 W/mK(Shin) << 물 k=0.6 -> 패드 alpha 훨씬 작음
alpha_pad = 0.02/(1200*1500)   # PU 대략 밀도/비열
alpha_water = 0.6/(1000*4180)
assert alpha_pad < alpha_water, (alpha_pad, alpha_water)
print(f"  alpha_pad={alpha_pad:.2e} < alpha_water={alpha_water:.2e} -> 패드가 열 덜 흡수(표면 축적)")
print("ALL PASS")
```
- **q=μPV 재현:** 전형 CMP 조건에서 q≈1.1×10⁴ W/m², 전체 마찰동력 Q_f≈353 W → White et al.(2003)
  문헌값 **200~300 W와 같은 오더**(수백 W). 역산 열유속 6.4~9.5×10³ W/m²도 q=μPV 오더와 부합.
- **온도상승 오더:** 슬러리 전량냉각 상한 ΔT≈19~29 ℃ → Shin et al.(2025) 실측 수~수십 ℃(미제어 ~36 ℃)와
  **오더 일치**(상한 추정이라 실측을 포괄).
- **Arrhenius 배율:** 문헌 Ea로 30→50 ℃ 시 **Cu 41.5배·Ta 2.08배·SiO₂ 1.24배** → "온도가 Cu MRR을 수십 배
  키우고 oxide는 거의 안 바꾼다"는 Shin 논문 핵심을 정량 재현. Cu RR@30 ℃ 재구성도 수백 Å/min 오더로 문헌 부합.

## 7. 한계 / 미검증 표기
- **플래시 온도 절대값 미검증:** asperity 국소 순간온도의 정량 예측(Blok flash temperature)은 본 노트 범위 밖 —
  평균온도만 정량, 플래시는 정성(A_r/A_n 배율 논증)에 그침. Lv3 후보.
- **온도상승은 "상한 추정"만 재현:** §6 (2)는 마찰열 전량이 슬러리로 간다는 가정의 상한이며, 실제 삼분배
  (슬러리/웨이퍼/패드) 비율은 White 2003의 열모델을 이식해야 정량화된다 — **오더 대조에 한정, 절대값 미검증**.
- **White et al.(2003) 원문 미확보:** 마찰열 200~300 W는 Shin 2025 §2.2의 재인용 + 초록 수준 — 1차 열모델
  본문은 미독(DOI는 crossref 실존 확인).
- **Ea는 특정 슬러리·툴 조건값:** Shin 2025의 Cu 151.7/Ta 29.9/SiO₂ 8.75 kJ/mol은 특정 barrier 슬러리·POLI-500
  툴의 겉보기 Ea로, 슬러리 화학·산화제가 바뀌면 달라진다 — 절대값 일반화는 **미검증**(오더·재료간 대소관계만 신뢰).
- ceria/oxide CMP의 겉보기 Ea "≈0.43 eV"(≈41 kJ/mol) 언급을 검색에서 봤으나 1차출처 미확정 — **채택 보류**.
