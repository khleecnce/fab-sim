# 저장·이송 이력 → 유효 입도 분포 변화 모델 — "제조 시 값"을 상태량으로 바꾸는 배율 함수

> 에이전트: slurry-colloid Lv3-2 | 작성일: 2026-09-16
> 선행: [[shelf-life-dilution-two-part-blending-qc]] [[pou-filtration-recirculation-pump-shear-lpc]]
>       [[dlvo-ionic-strength-ph-aggregation-kinetics]] [[colloidal-destabilization-lpc-defect-mechanism]]
>       [[aggregation-inhibitor-additives-inline-psd-monitoring]]
> 관련: [[../cmp/colloid-zeta-dlvo-slurry-stability]] [[../cmp/lpc-scratch-density-tail-correlation]]

## 1. 이 노트가 채우는 자리 — 앞 노트 4편이 남긴 빈칸은 "배율"이다

선행 노트들은 **메커니즘**을 세웠다: 정적 DLVO([[dlvo-ionic-strength-ph-aggregation-kinetics]]),
꼬리→손상 인과([[colloidal-destabilization-lpc-defect-mechanism]]), 루프의 생성·제거항
([[pou-filtration-recirculation-pump-shear-lpc]]), 보관·희석·혼합의 세 시계
([[shelf-life-dilution-two-part-blending-qc]]), 억제 첨가제와 계측 한계
([[aggregation-inhibitor-additives-inline-psd-monitoring]]).

빠진 것은 하나다. **팩에 들어갈 숫자**. 슬러리 팩의 `abrasive_d99_nm`·`aggregate_ratio`는
지금도 "제조 시 값"으로 고정되어 있고, 구현 요청 (3)(4)는 "구조를 마련하라"까지만 갔다.
이 노트는 그 요청이 요구한 **이력 → 배율 함수형과 문헌 계수**를 채운다:

```
d50_eff  = d50_0  × M_d50(t, T, 농도이력)
d99_eff  = d99_0  × M_tail(...)          ← ⚠ M_tail ≠ M_d50^k (§5가 반증)
aggregate_ratio_eff = f(M_tail, 경도플래그)   ← 가역(soft)/비가역(hard) 구분 필수(§7)
```

**형제 영역 경계**: 인용 문헌들은 제형 최적화(slurry-chemistry)·연마입자 합성
(slurry-abrasive)·필터 하드웨어(장비)도 다룬다. 이 노트는 **이력 변수(시간·온도·농도·전단)
→ 입도/전하 상태량** 축만 채택하고 제거율(RR)은 문맥으로만 쓴다.

## 2. 이력의 공통 단위 — 등가 나이 $t_{eq}$ (Q₁₀ = 2.00)

저장 이력은 (기간, 온도)의 나열이다. 이를 **25 °C 등가 일수** 하나로 접는 것이
문헌이 실제로 쓰는 방법이다. Fujimi 특허 US20250304827A1(Tsuzuki & Abe, 출원인 Fujimi
Incorporated, 공개 2025-10-02)은 실험 절차에 환산을 명시한다:

> "The obtained slurry composition was stored at 80 °C for 7 days. The 'at 80 °C for 7 days'
> is equivalent to 'stored at 25 °C for 317 days' according to the Arrhenius acceleration equation."

이 한 줄이 가속계수 $AF = 317/7 = 45.3$($\Delta T=55$ °C)을 준다. 여기서 역산한
$Q_{10}$는 **정확히 2.00**이고(ASTM F1980류 가속시험의 관례값과 일치), 등가 활성화에너지는
**60.7 kJ/mol**이다. 따라서 이력 합산식:

$$t_{eq} = \sum_i t_i \cdot Q_{10}^{(T_i - 25)/10}, \qquad Q_{10} = 2.00$$

```python verify
import math
# --- Fujimi US20250304827A1 (2025) 실시예: "80 °C 7일 ≡ 25 °C 317일 (Arrhenius)" ---
T_HOT_C, T_REF_C, D_HOT, D_EQ = 80.0, 25.0, 7.0, 317.0
AF = D_EQ / D_HOT                      # 가속계수
Q10 = AF ** (10.0 / (T_HOT_C - T_REF_C))
assert abs(Q10 - 2.0) < 0.01, f"특허 환산에서 역산한 Q10이 2.00이 아니다: {Q10:.3f}"
print(f"재현: 가속계수 AF={AF:.1f}배 → Q10={Q10:.3f} (특허 자체 환산에서 역산, 문헌 관례 2.0과 일치)")

R, T1, T2 = 8.314, 298.15, 353.15      # J/mol·K
Ea = R * math.log(AF) / (1/T1 - 1/T2)
assert 55e3 < Ea < 65e3, f"등가 활성화에너지가 예상 범위 밖: {Ea/1000:.1f} kJ/mol"
print(f"재현: 등가 활성화에너지 Ea = {Ea/1000:.1f} kJ/mol "
      f"(Q10=2.00 ⟺ Ea≈61 kJ/mol @25~80 °C — 두 표현은 같은 수치의 두 얼굴)")

# 이력 합산의 실무 함의: 여름 창고(35 °C) 30일은 25 °C 60일과 같다
def t_eq(segments):                    # [(일수, 온도°C), ...] → 25 °C 등가 일수
    return sum(d * Q10 ** ((T - 25.0) / 10.0) for d, T in segments)
assert abs(t_eq([(30, 35)]) - 60.0) < 0.1
assert abs(t_eq([(7, 80)]) - D_EQ) < 1.0, "특허 조건을 되짚으면 317일이 나와야"
print(f"재현: 35 °C 30일 = 25 °C {t_eq([(30,35)]):.0f}일 / 80 °C 7일 = {t_eq([(7,80)]):.0f}일")
```

⚠ **적용 한계**: $Q_{10}=2$는 이 특허의 **양이온화 실리카 계에서 출원인이 채택한 환산**이다.
§4가 보이듯 **저온 쪽(<25 °C)으로는 외삽하면 안 된다** — 냉장 저장에서 오히려 응집이
늘어난 실측이 있다. 그리고 이 식은 *속도*의 환산이지 *기구*가 같다는 보증이 아니다.

## 3. d50 배율의 속도식 — Smoluchowski ↔ 가속시험 실측 대조

**Granström, J., Oonishi, S., Tada, M., Takeda, H. (2015). "Particle size distribution shift as a
predictor of slurry stability." ICPT 2015(Fujimi Corporation / Fujimi Incorporated 공동 발표논문).**
원문 PDF: `papers/granstrom2015-icpt-psd-shift-slurry-stability.pdf`
(fujimico.com 원 URL은 현재 접속 불가 → Wayback Machine 2020-03-21 스냅샷에서 확보, 4쪽 전문).
DOI 없음 — 학회 발표논문이라 **1차 실측이되 동료심사 등급은 아님**.

두 개의 가속 저장 실험이 있다(둘 다 같은 조직, 같은 슬러리 B 포함):

| 실험 | 저장 조건 | 25 °C 등가 나이 | 슬러리 B PSD 중앙값 배율 | 계측기 |
|---|---|---|---|---|
| 1 (Table 3) | 80 °C × 5 일 | 226 일 | **1.5** | Microtrac UPA-151 |
| 2 (Table 6) | 55 °C × 10 일 | 80 일 | **1.2** | Horiba LA-950 |

같은 표에 불안정 제형(슬러리 A)은 80 °C × 5 일에 **10.6배**로 적혀 있다.

Smoluchowski 응집의 초기 단계는 **응집체 부피가 시간에 선형**으로 늘어난다
($\bar v(t) = v_0 (1 + t/\tau)$, [[dlvo-ionic-strength-ph-aggregation-kinetics]] §2). 부피를
직경으로 바꾸면 곧 **1/3승 법칙**이다:

$$M_{d50}(t_{eq}) = \left(1 + \frac{t_{eq}}{\tau}\right)^{1/3}, \qquad
\tau = W \cdot \tau_{fast}, \quad \tau_{fast}= \frac{3\eta}{4 k_B T N_0}$$

두 실험을 이 식에 넣으면 $\tau$가 **95.3 일 vs 109.9 일**로 나온다 — 계측기가 다르고
온도가 25 °C 떨어졌는데도 **14 % 이내**로 같은 값이다. 즉 "$Q_{10}=2$로 접은 등가 나이 +
Smoluchowski 1/3승"이라는 두 가정이 서로를 지탱한다.

```python verify
import math
Q10 = 2.0
def t_eq(days, T_C): return days * Q10 ** ((T_C - 25.0) / 10.0)

# --- Granström et al. 2015 (ICPT, Fujimi) Table 3 / Table 6 ---
EXP = [("Exp1 80C 5d, UPA-151", t_eq(5, 80.0), 1.5),
       ("Exp2 55C 10d, LA-950", t_eq(10, 55.0), 1.2)]
taus = []
for name, te, M in EXP:
    tau = te / (M**3 - 1.0)          # M=(1+t/tau)^(1/3) 역산
    taus.append(tau)
    print(f"  {name}: t_eq={te:.0f} d, d50 배율 {M} → tau={tau:.1f} d")
spread = (max(taus) - min(taus)) / (sum(taus)/2)
assert spread < 0.20, f"두 실험의 tau가 20% 이상 갈린다 ({spread:.1%}) — 1/3승 모델 재검토 필요"
print(f"재현: 서로 다른 온도·계측기의 두 가속시험이 같은 tau를 준다 "
      f"({taus[0]:.0f} d vs {taus[1]:.0f} d, 상대편차 {spread:.1%})")

# 선형 근사(1차 오더)로도 일관한가 — M ≈ 1 + c·t_eq
cs = [(M - 1.0)/te for _, te, M in EXP]
print(f"재현: 선형 근사 계수 c = {cs[0]*100:.3f} %/일 vs {cs[1]*100:.3f} %/일 "
      f"(상대편차 {abs(cs[0]-cs[1])/((cs[0]+cs[1])/2):.1%}) — 25 °C 등가로 하루 약 0.23 % 성장")
assert abs(cs[0]-cs[1])/((cs[0]+cs[1])/2) < 0.20

# 불안정 제형(슬러리 A)은 같은 이력에서 얼마나 빠른가
tau_A = t_eq(5, 80.0) / (10.6**3 - 1.0)
ratio = (sum(taus)/2) / tau_A
assert ratio > 100, "A가 B보다 두 자릿수 이상 빨라야 (10.6배 vs 1.5배)"
print(f"재현: 불안정 제형 tau={tau_A:.2f} d — 안정 제형보다 {ratio:.0f}배 빠름 "
      f"= 안정비 W가 {ratio:.0f}배 작음 = DLVO 장벽 차이 ln({ratio:.0f})={math.log(ratio):.1f} kT")
```

⚠ **미검증**: Granström 원문은 슬러리 A·B의 고형분 wt%, 1차 입경, 조성을 밝히지 않았다
("PSD Medians below 150 nm"만 명시). 따라서 위 $\tau$는 **그 슬러리의 유효 응집 시상수**이지
이식 가능한 물성이 아니다. 실험 1·2의 계측기가 다르다는 교란도 남아 있다(UPA-151은
제어참조 DLS, LA-950은 Mie 산란) — 그래서 등급 **E3**.

## 4. 온도는 단조가 아니다 — 가역 분기와 저온 분기

### 4.1 잘 안정화된 슬러리에서 15~45 °C 3주는 **가역**이다

**Seo, J., Othman, A., Kim, H.J., Devabhaktuni, J., Trivedi, R., Penigalapati, D., Kulasingam, T.,
Hanup Vegi, S.S.R.K., Babu, S.V. (2021). "Storage Temperature Effects on the Slurry Health
Parameters and SiO₂ Removal Rates during Chemical Mechanical Polishing." *ECS J. Solid State
Sci. Technol.* 10(10), 104002. DOI: 10.1149/2162-8777/ac2c56** (CC-BY 오픈액세스, 전문 확보).

상용 세리아 STI 슬러리($d_{DLS}=75\pm6$ nm, $\zeta=-63\pm2$ mV, pH 8.1)를 **15 / 25 / 45 °C에
1·2·3주** 저장하고 6개 지표를 쟀다. 3주 후:

| 지표 | 15 °C | 25 °C | 45 °C | RT 6 h 복귀 후 |
|---|---|---|---|---|
| 유체역학 직경 | −2.5 % | 기준 | +3 % | **모두 25 °C 값으로 복귀** |
| 제타전위(절댓값) | −2.5 % | 기준 | +5.0 % | **복귀** |
| pH | +2.5 % | 기준 | −2.5 % | **복귀** |
| TDS·전도도 | 변화 없음(697 mg/L·996 µS) | — | 변화 없음 | — |
| 용존산소(DO) | +14 %(9.60 mg/L) | 8.40 mg/L | −18 %(6.85 mg/L) | **복귀 안 함** |

**결론이 중요하다**: $|\zeta|=63$ mV짜리 슬러리에서는 ±20 °C·3주가 **입도에 비가역 변화를
남기지 않았다**. 비가역으로 남은 것은 DO와 그로 인한 세리아 표면종(Ce³⁺→Ce⁴⁺-superoxo,
FT-IR 800 cm⁻¹ 밴드)뿐이고, 그것이 SiO₂ 제거율을 10~15 % 떨어뜨렸다(팹 로트 A/B 비교).
즉 **온도 이력의 1차 출력은 입도가 아니라 화학**일 수 있다.

### 4.2 온도 보정을 안 하면 가짜 성장이 실제 성장의 20배로 보인다

이 절의 부수 결과가 QC에 더 실용적이다. DLS 직경은 Stokes–Einstein
$d_H = k_BT/(3\pi\eta D)$로 계산되므로 **측정 온도의 $\eta(T)$를 안 넣으면** 온도만으로
직경이 크게 움직인다. 45 °C 시료를 25 °C 물성으로 환산하면 **+59 %**의 가짜 성장이 나오는데,
Seo가 보고한 실제 변화는 +3 %다.

```python verify
# --- Seo et al. 2021 (doi:10.1149/2162-8777/ac2c56) ---
# 물 점도 (CRC 표준값, mPa·s): 15/25/45/80 °C
ETA = {15: 1.138, 25: 0.890, 45: 0.596, 80: 0.3545}
T0 = 25.0
def dls_artifact(T):        # eta(T)를 25 °C 값으로 잘못 두었을 때의 겉보기 직경 오차
    return ((273.15+T)/(273.15+T0)) * (ETA[T0]/ETA[T]) - 1.0

art45, art15 = dls_artifact(45), dls_artifact(15)
MEAS45, MEAS15 = +0.03, -0.025     # 원문 보고 실제 변화 (+3 %, −2.5 %)
assert art45 > 0.5 and art15 < -0.2
print(f"재현: 점도 미보정 시 겉보기 직경 오차 = 45 °C에서 {art45*100:+.0f} %, "
      f"15 °C에서 {art15*100:+.0f} %")
print(f"문헌값 대조: 원문의 실제 변화는 {MEAS45*100:+.0f} % / {MEAS15*100:+.1f} % — "
      f"가짜 성장이 실제의 {art45/MEAS45:.0f}배·{art15/MEAS15:.0f}배 "
      f"→ 온도 보정 없는 인라인 PSD 모니터링은 계절/공조 변동을 응집으로 오진한다")

# DO: 문헌 수치 정합 (9.60 / 8.40 / 6.85 mg/L, +14 % / −18 %)
do15, do25, do45 = 9.60, 8.40, 6.85
assert abs((do15/do25 - 1) - 0.14) < 0.005 and abs((do45/do25 - 1) + 0.18) < 0.005
print(f"재현: DO {do15}/{do25}/{do45} mg/L → {100*(do15/do25-1):+.0f} % / {100*(do45/do25-1):+.0f} % (원문 서술과 일치)")
# 원문 Fig.3 물 포화 DO(15 °C 10.08, 45 °C 5.93 mg/L) 대비 슬러리의 위치
sat15, sat45 = 10.08, 5.93
assert do15/sat15 < 1.0 < do45/sat45
print(f"재현: 15 °C 슬러리는 포화의 {100*do15/sat15:.0f} %(아직 흡수 중), "
      f"45 °C는 {100*do45/sat45:.0f} %(과포화 — 아직 방출 중) → 3주에도 DO 평형 미도달")
```

### 4.3 그런데 실리카 슬러리에서는 냉장 저장도 응집한다 (저온 분기)

**Othman, A., Kim, H.J., Trivedi, R., Kulasingam, T., Seo, J. (2024). "Understanding and
mitigating temperature-induced agglomeration in silica-based chemical mechanical planarization
(CMP) slurry storage." *Colloids Surf. A* 691, 133802. DOI: 10.1016/j.colsurfa.2024.133802**
— ⚠ **원문 본문 미확보(Elsevier 유료, 미러 사이트에 미등재). 아래는 출판사 초록 명시값만
인용하며 등급 E5(2차 인용)로 취급한다.**

초록 명시: 실리카 슬러리를 15 °C / RT / 45 °C에 저장했을 때 대입자 계수(LPC)가
**RT ≈ 2.0×10⁶ /mL**, **45 °C ≈ 1.2×10⁷ /mL**, **15 °C ≈ 4.0×10⁶ /mL**. 단기 저장은
**soft 응집체**(LPC 2.0~4.0×10⁶), 장기 고온 저장은 **hard 응집체**(LPC ≈ 3.0×10⁷).
DO는 RT ≈10 ppm → 45 °C ≈7 ppm(§4.1 세리아와 같은 방향).

여기서 §2의 Arrhenius가 **한쪽으로만 맞는다**:

```python verify
# --- Othman et al. 2024 (doi:10.1016/j.colsurfa.2024.133802) 초록 명시 LPC [입자/mL] ---
LPC = {15: 4.0e6, 25: 2.0e6, 45: 1.2e7}        # E5(초록) — 본문 미확보
Q10 = 2.0
def arrh(T):  return Q10 ** ((T - 25.0)/10.0)   # 25 °C 기준 상대 속도

hot_meas, hot_pred = LPC[45]/LPC[25], arrh(45)
cold_meas, cold_pred = LPC[15]/LPC[25], arrh(15)
print(f"고온: 측정 {hot_meas:.1f}배 vs Arrhenius 예측 {hot_pred:.1f}배 → 비 {hot_meas/hot_pred:.1f}")
print(f"저온: 측정 {cold_meas:.1f}배 vs Arrhenius 예측 {cold_pred:.1f}배 → 비 {cold_meas/cold_pred:.1f}")
assert 1.0 < hot_meas/hot_pred < 2.0, "고온 분기는 Q10=2 예측과 같은 오더여야"
assert cold_meas > 1.0 > cold_pred, "저온 분기는 부호 자체가 어긋나야(측정 증가, 예측 감소)"
assert cold_meas/cold_pred > 3.0
print(f"재현: 고온 분기는 Q10=2가 {hot_meas/hot_pred:.1f}배 이내로 맞지만, 저온 분기는 "
      f"방향이 반대로 {cold_meas/cold_pred:.0f}배 어긋난다 → **단조 Arrhenius 배율 금지**, "
      f"최소 25 °C 근처를 바닥으로 하는 V자 2분기 형태여야 한다")
# hard/soft 분리: 장기 고온의 hard 응집체는 RT 대비 15배
assert 3.0e7/LPC[25] == 15.0
print("재현: 장기 고온 저장의 hard 응집체 LPC 3.0e7/mL = RT의 15배 (초록 명시값, E5)")
```

**판정(EVIDENCE-RULES §3 — 스코프 분할)**: §4.1(세리아, 가역)과 §4.3(실리카, 비가역)은
충돌이 아니다. 두 계는 **DLVO 장벽이 다르다**($\zeta=-63$ mV 세리아 vs 미기재 실리카).
평균내지 말고 **레짐을 쪼갠다** — "제타 여유가 큰 슬러리는 온도 이력이 가역, 여유가 작은
슬러리는 비가역". 배율을 적용할지 말지를 결정하는 것은 온도가 아니라 **장벽**이다.

## 5. 꼬리는 중앙값을 따라가지 않는다 — d99와 aggregate_ratio는 별개의 상태량

Granström Table 2~4가 이 노트에서 가장 중요한 표다. 같은 가속 저장(80 °C×5 일)에서:

| | LPC(>0.56 µm) 배율 | PSD 중앙값 배율 | 스크래치(개) | 증가율 |
|---|---|---|---|---|
| 슬러리 A | **87.0** | 10.6 | 180 → 1241 | +691 % |
| 슬러리 B | **0.9**(변화 없음) | 1.5 | 34 → 122 | +359 % |

슬러리 B는 **LPC가 전혀 안 움직이는데 스크래치가 3.6배**가 됐다. 원저자 결론:
"a PSD shift as small as 50 % correlates with > 300 % increase in scratches", 그리고 그 성장은
**LPC 검출 하한(0.56 µm) 아래**에서 일어났다.

여기서 "이력이 분포 전체를 평행이동시킨다"는 순진한 모델을 정량적으로 반증할 수 있다.
로그정규 분포의 중앙값만 1.5배로 옮기면 0.56 µm 초과 꼬리는 기하표준편차 $\sigma_g$에 따라
**21배~10⁶배** 늘어야 한다. 실측은 0.9배였다.

```python verify
import math
# --- Granström et al. 2015 (ICPT, Fujimi) Table 2/3/4 ---
LPC_A, LPC_B = 87.0, 0.9          # 정규화 LPC(>0.56 µm) 배율
D50_A, D50_B = 10.6, 1.5          # 정규화 PSD 중앙값 배율
SCR_A, SCR_B = 1241/180, 122/34   # 스크래치 배율

# (1) 꼬리 배율과 중앙값 배율은 같은 함수가 아니다 — 두 슬러리에서 방향이 갈린다
assert LPC_A/D50_A > 8.0 and LPC_B/D50_B < 0.7
print(f"재현: 슬러리 A는 꼬리(×{LPC_A:.0f})가 중앙값(×{D50_A})보다 {LPC_A/D50_A:.1f}배 더 자랐고, "
      f"B는 중앙값(×{D50_B})이 자라는 동안 꼬리는 오히려 ×{LPC_B} — 단일 배율로 둘을 못 낸다")

# (2) '로그정규 평행이동' 모델의 예측 (반증 대상)
def tail_frac(med_nm, sg, cut_nm=560.0):
    z = math.log(cut_nm/med_nm)/math.log(sg)
    return 0.5*math.erfc(z/math.sqrt(2))
MED0 = 150.0                      # 원문: "PSD Medians below 150 nm"
preds = {}
for sg in (1.2, 1.3, 1.4, 1.5):
    preds[sg] = tail_frac(MED0*D50_B, sg)/tail_frac(MED0, sg)
for sg, r in preds.items():
    print(f"   sigma_g={sg}: 평행이동 모델이 예측하는 LPC 배율 = {r:.3g}")
assert min(preds.values()) > 20*LPC_B, "가장 관대한 sigma_g에서도 실측을 20배 이상 과대예측해야"
print(f"재현: 평행이동 모델은 LPC를 {min(preds.values()):.0f}~{max(preds.values()):.0e}배로 예측하는데 "
      f"실측은 ×{LPC_B} — 최소 {min(preds.values())/LPC_B:.0f}배(= {math.log10(min(preds.values())/LPC_B):.1f}자릿수) 과대. "
      f"→ 이력은 분포를 평행이동시키는 것이 아니라 **별도의 응집 모드를 얹는다**")

# (3) 스크래치 ~ 중앙값 배율의 겉보기 지수 (2점, 회귀 아님)
n = math.log(SCR_A/SCR_B)/math.log(D50_A/D50_B)
assert 0.2 < n < 0.5
print(f"재현: 스크래치배율 ∝ (d50배율)^{n:.2f} (2점뿐 — 회귀 아님). "
      f"[[colloidal-destabilization-lpc-defect-mechanism]] §9의 실리카계 damage_exponent "
      f"n≈0.40과 같은 구간(0.3~0.4)이고 세리아 n≈1.44과는 여전히 갈린다")
```

⚠ **정직성**: (2)의 반증은 "중앙값이 옮겨간 원인이 무엇인가"를 가리지 않는다. UPA-151은
DLS 계열이라 강도가중($I \propto d^6$)이어서 **소수의 준마이크론 응집체만으로도 중앙값이
움직일 수 있다**. 그 해석에서도 결론은 같다 — *중앙값 지표와 0.56 µm 꼬리 지표는
서로 다른 모집단을 보고 있다*. 어느 해석이든 **두 개의 상태량이 필요하다**는 것이 결론이다.

## 6. 희석·보관 농도 이력 — 임계량은 농도가 아니라 **입자 표면 간 거리 h**

[[shelf-life-dilution-two-part-blending-qc]] §4는 "희석은 중립 조작이 아니다"(US8303373B2)를
세웠지만 **임계 변수**를 못 냈다. Fujimi 특허 US20250304827A1이 그 자리를 채운다.
양이온화(아미노실란 표면개질) 콜로이달 실리카를 **농축 상태로 저장했다가 사용 시 희석**하는
설계이며, 저장 농도만 7수준으로 스윕하고 전부 80 °C×7 일(=25 °C 317 일) 저장 후
0.9 wt%로 희석해 비교했다. 특허가 쓰는 임계량은 농도가 아니라 **평균 입자 표면 간 거리**다:

$$h = d_p\left[\sqrt{\frac{1}{3\pi F} + \frac{5}{6}} - 1\right] \qquad (F = 연마입자 부피분율)$$

| | Comp.1 | Comp.2 | Ex.1 | Ex.2 | Ex.3 | Ex.4 | Ex.5 |
|---|---|---|---|---|---|---|---|
| 저장 농도 [wt%] | 2.7 | 3.6 | 5.4 | 6.3 | 7.2 | 9.0 | 18.0 |
| h [nm] | 91 | 74 | **55** | 48 | 43 | 36 | 19 |
| 제타 손실 [%] | **38.8** | **34.6** | 5.7 | 5.9 | 7.3 | 5.2 | **2.1** |
| RR 증가 [%] | 9.5 | 8.1 | 5.6 | 5.9 | 7.3 | 5.2 | 2.1 |

**묽게 저장할수록 망가진다** — DLVO의 순진한 예측(희석 → $\kappa^{-1}$ 증가 → 안정)과 반대
방향이고, [[shelf-life-dilution-two-part-blending-qc]] §4의 실측 사례와는 같은 방향이다.
특허가 제시하는 기구는 **표면개질제(아미노실란)의 탈착 평형**이다: 입자 간 거리가 멀수록
벌크 쪽으로 빠져나갈 여지가 커서 표면 전하가 사라진다. 그리고 그 임계는 $h \approx 65$ nm
($\approx 1.5 d_p$)에 **절벽**으로 놓여 있다(34.6 % → 5.7 %).

```python verify
import math, statistics as st
# --- Fujimi US20250304827A1 Table 1 (80 °C 7일 = 25 °C 317일 저장 후) ---
# (라벨, 저장 wt%, h[nm], 제타[mV], 제타감소[mV], 감소율[%], RR증가[Å/min], RR증가율[%])
T1 = [("Comp1", 2.7, 91, 22.4, 14.2, 38.8, 6.7, 9.5),
      ("Comp2", 3.6, 74, 24.0, 12.7, 34.6, 5.7, 8.1),
      ("Ex1",   5.4, 55, 34.6,  2.1,  5.7, 4.0, 5.6),
      ("Ex2",   6.3, 48, 34.5,  2.2,  5.9, 4.1, 5.9),
      ("Ex3",   7.2, 43, 34.0,  2.7,  7.3, 5.1, 7.3),
      ("Ex4",   9.0, 36, 34.8,  1.9,  5.2, 3.6, 5.2),
      ("Ex5",  18.0, 19, 35.9,  0.8,  2.1, 1.5, 2.1)]
RHO_SIO2 = 2.2                      # g/cm³ 비정질 실리카

def F_vol(w, rho=RHO_SIO2): return (w/rho) / ((w/rho) + (100.0 - w))
def h_eq(dp, w): return dp * (math.sqrt(1.0/(3*math.pi*F_vol(w)) + 5.0/6.0) - 1.0)

# (1) 특허 식(1)을 단일 d_p로 7행 전부 재현 — 식의 형태(제곱근)와 밀도 가정 검증
dps = [h / (h_eq(1.0, w)) for _, w, h, *_ in T1]
dp_mean = st.mean(dps)
errs = [abs(h_eq(dp_mean, w) - h)/h for _, w, h, *_ in T1]
assert max(errs) < 0.05, f"식(1) 재현 실패: 최대 상대오차 {max(errs):.1%}"
print(f"재현: 특허 식(1)을 단일 d_p={dp_mean:.1f} nm(ρ={RHO_SIO2})로 7행 전부 재현 "
      f"— 최대 상대오차 {max(errs):.1%} (즉 루트는 제곱근이 맞고, 2차입경은 약 44 nm)")

# (2) 절벽 확인: h=65 nm를 경계로 제타 손실이 5배 이상 갈린다
above = [r[5] for r in T1 if r[2] > 65]; below = [r[5] for r in T1 if r[2] < 65]
assert min(above) / max(below) > 4.0
print(f"재현: h>65 nm 그룹 제타손실 {min(above):.1f}~{max(above):.1f} % vs "
      f"h<65 nm 그룹 {min(below):.1f}~{max(below):.1f} % → 경계에서 {min(above)/max(below):.1f}배 절벽 "
      f"(연속 함수가 아니라 문턱으로 모델링해야)")

# (3) 이 문턱은 DLVO(EDL 중첩) 길이가 아니다 — 같은 pH의 Debye 길이와 20배 이상 차이
for pH in (1.6, 2.5):
    kinv = 0.304/math.sqrt(10**(-pH))       # 1:1 전해질 근사 [nm], 25 °C
    assert 65.0/kinv > 10
    print(f"   pH {pH}: κ⁻¹={kinv:.1f} nm → 문턱 65 nm는 그 {65.0/kinv:.0f}배")
print("재현: 문턱 h≈65 nm ≈ 1.5·d_p 는 Debye 길이(2~5 nm)의 12~34배 → "
      "EDL 중첩이 아니라 **표면개질제 탈착 평형**이라는 특허 주장과 정합(DLVO로 설명 못 함)")

# (4) 제타 손실과 RR 변화가 같은 축을 탄다 (저장 이력이 성능으로 새는 통로)
import statistics
dz = [r[4] for r in T1]; drr = [r[6] for r in T1]
mx, my = st.mean(dz), st.mean(drr)
r_p = sum((a-mx)*(b-my) for a,b in zip(dz,drr)) / math.sqrt(
      sum((a-mx)**2 for a in dz) * sum((b-my)**2 for b in drr))
assert r_p > 0.7
print(f"재현: 제타 감소량 vs TEOS 제거율 변화량 Pearson r={r_p:.2f} "
      f"(n=7) — 보관 이력의 출력은 입도만이 아니라 표면전하→성능 경로로도 샌다")
```

⚠ **범위 주의**: 이 절벽은 **아미노실란 양이온화 실리카**(pH<3)의 값이다. $h_{th}/d_p \approx 1.5$
라는 무차원 형태가 다른 표면개질 계로 이식되는지는 **미검증**이다. 다만 "희석해서 오래
보관하지 말고 농축 보관 후 POU 희석"이라는 **정성 규칙**은 US8303373B2와 이 특허가
서로 다른 화학에서 같은 방향으로 말한다.

## 7. 전단·이송 이력 — 같은 응집이라도 되돌릴 수 있는 것과 없는 것

[[pou-filtration-recirculation-pump-shear-lpc]] §2는 전단 응집의 **발생 조건**(G ≥ G_th
AND Camp ≥ Camp_th)을 세웠다. 남은 질문은 **그렇게 생긴 응집체가 상태량으로 남는가**이다.

**Khanna, A.J., Chang, F.-C., Gupta, S., Kumar, P., Singh, R.K. (2019). "Characterization of the
nature of shear-induced agglomerates as hard and soft in chemical mechanical polishing slurries."
*J. Vac. Sci. Technol. B* 37(1), 011207. DOI: 10.1116/1.5065516** — 전문 확보
(`papers/khanna2019-jvstb-hard-soft-shear-agglomerates.pdf`, 미러 사이트 폴백).

35 nm 콜로이달 실리카 10 wt%를 pH 2 / 7 / 10으로 맞추고 **3000 s⁻¹ × 1000 s로 응집시킨 뒤
(stressed), 다시 100 s⁻¹ × 100~1000 s의 저전단**을 걸어 풀리는지 봤다(Accusizer SPOS로
1·2·3·4·5 µm 누적농도 측정). 판정 규칙: stressed의 해응집도 > as-received의 해응집도면
"soft", 작으면 "hard".

- **염기성 pH 10**: 전단으로 생긴 응집체가 as-received보다 **더 잘 풀린다 → soft(가역)**
- **중성 pH 7 · 산성 pH 2**: 더 안 풀린다 → **hard(비가역)**, 산성이 가장 단단함
- 응집체 강도 순서 = 제타 절댓값(반발력) 순서의 **역순**: 산성 > 중성 > 염기성
- 같은 계의 연마 결과(Chang 2008 학위논문 재수록): BD1 low-k 표면거칠기
  pH 11 RMS 0.79 nm / R_max 13.01 nm vs pH 2 RMS 1.4 nm / R_max 23 nm

즉 **동일한 전단 이력이 pH에 따라 `aggregate_ratio`를 늘리기도, 안 늘리기도 한다**.
이력 모델에 "응집량"만 있고 "경도(가역성)" 플래그가 없으면 염기성 슬러리에서 과대예측한다.

```python verify
import math
# --- Khanna et al. 2019 (doi:10.1116/1.5065516) 정성 결론 + Chang 2008 재수록 거칠기 ---
NATURE = {10: "soft", 7: "hard", 2: "hard"}          # 전단유도 응집체의 성질(원문 결론)
STRENGTH_ORDER = [2, 7, 10]                           # 강도: 산성 > 중성 > 염기성
RMS = {11: 0.79, 2: 1.4}; RMAX = {11: 13.01, 2: 23.0} # nm, BD1 low-k
assert NATURE[10] == "soft" and NATURE[7] == NATURE[2] == "hard"
assert STRENGTH_ORDER == sorted(STRENGTH_ORDER)       # pH 낮을수록 단단하다는 순서 보존
print("재현: 같은 전단 이력(3000 s⁻¹×1000 s)의 산물이 pH 10에서는 soft(저전단 100 s⁻¹로 풀림), "
      "pH 7·2에서는 hard — 이력→aggregate_ratio 전달률이 화학에 의존")

r_rms, r_rmax = RMS[2]/RMS[11], RMAX[2]/RMAX[11]
assert r_rms > 1.5 and r_rmax > 1.5
print(f"문헌값 대조: 산성 대 염기성 표면거칠기 비 RMS {RMS[2]}/{RMS[11]}={r_rms:.2f}배, "
      f"Rmax {RMAX[2]}/{RMAX[11]}={r_rmax:.2f}배 — hard 응집체 쪽이 거칠다(방향 일치)")

# Lv2-1의 AND 게이트와의 정합: 이 실험의 전단은 임계(G_th≈1000~1500 s⁻¹)를 넘는다
G, t = 3000.0, 1000.0
G_TH, CAMP_TH_pH10 = 1000.0, 1.5e6      # [[pou-filtration-recirculation-pump-shear-lpc]] §2
assert G >= G_TH and G*t >= CAMP_TH_pH10
print(f"재현: 이 실험 조건 G={G:.0f} s⁻¹, Camp={G*t:.1e} — 선행 노트의 AND 게이트 "
      f"(G≥{G_TH:.0f} AND Camp≥{CAMP_TH_pH10:.1e})를 모두 넘으므로 '응집 발생'은 두 문헌이 정합")
```

## 8. 두 이력 축의 만남 — 응집 시상수와 가속계수가 같은 DLVO 장벽을 가리키는가

§3은 **저장 시간** 축에서 $\tau \approx 95{\sim}110$ 일을 줬고, §2는 **온도** 축에서
$Q_{10}=2.00$($AF=45.3$)을 줬다. 두 축은 서로 독립한 데이터(다른 문헌·다른 슬러리)인데,
Smoluchowski+DLVO로 환산하면 **둘 다 "장벽 높이"라는 하나의 수로 수렴하는가**를 물을 수 있다.

- 시간 축: $W = \tau/\tau_{fast}$, $\tau_{fast}=3\eta/(4k_BTN_0)$ → $V_{max} \approx \ln W$ [kT]
- 온도 축: $AF = \underbrace{[T/\eta]_{353}/[T/\eta]_{298}}_{확산\ 항} \times \underbrace{W(298)/W(353)}_{장벽\ 항}$

```python verify
import math
kB, T25 = 1.380649e-23, 298.15
ETA = {25: 0.890e-3, 80: 0.3545e-3}
RHO = 2.2

def tau_fast(d_nm, wt):                      # perikinetic 급속응집 시상수 [s]
    phi = (wt/RHO)/((wt/RHO) + (100.0-wt))
    v = math.pi/6*(d_nm*1e-9)**3
    return 3*ETA[25]/(4*kB*T25*(phi/v))

# (A) 시간 축: tau=100 d(§3) → W → 장벽. 고형분·입경이 미기재라 범위로 낸다.
TAU_D = 100.0
bars = []
for d_nm, wt in [(100, 10), (150, 10), (100, 1), (150, 30)]:
    W = TAU_D*86400/tau_fast(d_nm, wt)
    bars.append(math.log(W))
    print(f"   d={d_nm} nm, {wt} wt% → tau_fast={tau_fast(d_nm,wt):.2e} s, W={W:.1e}, 장벽={math.log(W):.1f} kT")
assert max(bars)-min(bars) < 3.0, "고형분·입경 가정 20배 변화에도 장벽은 3 kT 이내여야(로그 압축)"
print(f"재현: 저장 시간 축이 주는 장벽 = {min(bars):.1f}~{max(bars):.1f} kT "
      f"(N₀가 20배 불확실해도 폭은 {max(bars)-min(bars):.1f} kT — ln의 압축 효과)")

# (B) 온도 축: AF=45.3에서 확산 항을 걷어내고 남는 장벽
AF = 317.0/7.0
diff_term = ((273.15+80)/ETA[80]) / ((273.15+25)/ETA[25])
W_term = AF/diff_term
V_from_AF = math.log(W_term)/(T25*(1/T25 - 1/(273.15+80)))
print(f"재현: AF={AF:.1f}배 중 확산(T/η) 기여는 {diff_term:.2f}배뿐 → 나머지 {W_term:.1f}배가 장벽 항 "
      f"→ V_max = {V_from_AF:.1f} kT")
assert 2.0 < diff_term < 4.0 and 12.0 < V_from_AF < 25.0

# (C) 두 독립 경로의 일치도
gap = min(bars) - V_from_AF
assert abs(gap) < 6.0
print(f"재현: 시간 축 {min(bars):.1f}~{max(bars):.1f} kT vs 온도 축 {V_from_AF:.1f} kT — "
      f"차이 {gap:.1f}~{max(bars)-V_from_AF:.1f} kT(= W로 {math.exp(gap):.0f}~{math.exp(max(bars)-V_from_AF):.0f}배). "
      f"둘 다 고전적 안정 문턱 15~25 kT 창 안에 든다 "
      f"(cf. [[dlvo-ionic-strength-ph-aggregation-kinetics]] §6)")
```

⚠ **이 절의 한계(과대해석 금지)**: (A)와 (B)는 **다른 슬러리**의 데이터다(ICPT 발표논문의
슬러리 B vs 특허의 양이온화 실리카). 따라서 이 일치는 "같은 슬러리의 두 측정이 같은 장벽을
준다"가 아니라 **"실무 쉘프라이프(수개월)를 갖는 CMP 슬러리의 장벽은 대략 17~22 kT 급"**
이라는 오더 진술이다. (B)는 $V_{max}$가 온도에 무관하다고 가정했는데 실제로는 $\varepsilon(T)$·
$\zeta(T)$가 움직이므로(§4.1에서 제타는 45 °C에 +5 %) 그 자체가 **미검증 가정**이다.

## 9. 이력 → 배율 함수형 요약표 (팩에 넣을 형태)

| # | 이력 변수 | 함수형(제안) | 문헌 계수 | 출처·등급 |
|---|---|---|---|---|
| H1 | 시간·온도 | $t_{eq}=\sum t_i\,Q_{10}^{(T_i-25)/10}$ | $Q_{10}=2.00$ ($E_a$ 60.7 kJ/mol) | US20250304827A1, E3 |
| H2 | 등가 나이 → d50 | $M_{d50}=(1+t_{eq}/\tau)^{1/3}$ | 안정 제형 $\tau$ 95~110 일; 불안정 제형 0.19 일 | Granström 2015, E3 |
| H3 | 등가 나이 → 꼬리 | **별도 상태량**(H2의 멱함수 아님) | 80 °C×5 일에 LPC ×87(불안정) / ×0.9(안정) | Granström 2015, E3 |
| H4 | 저온 저장 | V자 2분기(25 °C 근처가 최소) | 15 °C LPC ×2.0 vs Arrhenius 예측 ×0.5 | Othman 2024, **E5(초록)** |
| H5 | 고온 저장(실리카) | 같은 방향, Q₁₀=2와 1.5배 이내 | 45 °C LPC ×6.0 (예측 ×4.0) | Othman 2024, **E5(초록)** |
| H6 | 온도(세리아·고제타) | **배율 없음(가역)** | ±20 °C·3주에 d 변화 ∓2.5~3 %, 복귀 | Seo 2021, **E1** |
| H7 | 보관 농도/희석 | 문턱형: $h=d_p[\sqrt{1/(3\pi F)+5/6}-1]$ | $h<65$ nm → ζ손실 ≤7 %, $h>65$ nm → 35~39 % | US20250304827A1, E3 |
| H8 | 전단 | AND 게이트(선행 노트) **× 경도 플래그** | pH 10 → soft(가역), pH 7·2 → hard | Khanna 2019, E3 |
| H9 | 계측 보정 | DLS는 $\eta(T)$ 보정 필수 | 미보정 시 45 °C에서 +59 % 가짜 성장 | Seo 2021, E1 |

## 10. `aggregate_ratio`의 크기 스케일 — ppb 수준인데 손상을 지배한다

마지막으로, 팩에 넣을 `aggregate_ratio`가 **어떤 자릿수의 양인지**를 못 박아 둔다.
§4.3의 LPC 값(2×10⁶~3×10⁷ /mL)을 전체 입자 수와 비교하면:

```python verify
import math
RHO = 2.2
def N_per_mL(d_nm, wt):
    phi = (wt/RHO)/((wt/RHO)+(100.0-wt))
    return phi/(math.pi/6*(d_nm*1e-9)**3)/1e6
N = N_per_mL(100.0, 10.0)                      # 100 nm, 10 wt% 기준
for lpc, tag in [(2.0e6, "RT(정상)"), (1.2e7, "45 °C"), (3.0e7, "장기 고온 hard")]:
    frac = lpc/N
    dls_share = frac*(560.0/100.0)**6          # DLS 강도 가중 I∝d⁶ 기여분
    print(f"   {tag}: LPC {lpc:.1e}/mL / 전체 {N:.2e}/mL = 수분율 {frac:.1e}, "
          f"DLS 강도 기여 {dls_share*100:.2f} %")
    assert frac < 1e-6, "대입자 수분율은 백만분의 1보다 작아야"
    assert dls_share < 0.05, "DLS 강도 기여도 5 % 미만 — 평균 지표로는 안 보인다"
print(f"재현: aggregate_ratio(수 기준)는 10⁻⁸~10⁻⁷ 급 — 질량 수지에는 영향이 없고(MRR 드라이버 아님), "
      f"DLS 강도 기여도 1 % 미만이라 벌크 입도계에 안 잡힌다. "
      f"그럼에도 스크래치를 지배한다 (cf. [[colloidal-destabilization-lpc-defect-mechanism]] §3). "
      f"→ 팩에서 이 값은 **손상 항 전용 드라이버**여야지 제거율·농도 항에 섞으면 안 된다")
```

## 11. sim/에 대한 시사점 (코드는 건드리지 않음 — PROFILE.md 구현 요청 (6)으로 기록)

1. **이력 입력의 최소 집합**은 `(기간, 온도)` 구간 리스트 + `저장 농도(또는 h)` +
   `pH` + `전단 이력(G, turnover)`이다. 그중 시간·온도는 §2의 $t_{eq}$ 하나로 접을 수 있다.
2. **d50 경로와 꼬리 경로를 하나의 배율로 묶지 말 것**(§5). `abrasive_d99_nm`와
   `aggregate_ratio`는 같은 이력에서 반대로 움직인 실측이 있다.
3. **온도 배율을 단조 Arrhenius로 두면 냉장 저장에서 틀린다**(§4.3). 최소 V자.
   그리고 제타 여유가 큰 슬러리에는 **배율 자체를 걸지 않는 것이 실측과 맞다**(§4.1).
4. **희석 이력은 농도가 아니라 h의 문턱**으로(§6). 연속 배율로 두면 절벽을 못 낸다.
5. **전단 이력은 경도 플래그와 함께**(§7). pH 염기성 계에서는 가역이라 상태량에 안 남는다.

## 12. 한계·정직성 표기

- ⚠ **E5(초록만)**: §4.3 Othman 2024의 LPC 수치 세 개는 출판사 초록 명시값이며 원문 본문·표를
  확보하지 못했다(Elsevier 유료, 미러 사이트 미등재). 저장 기간의 정의("short/long-term"),
  LPC 채널(>0.5 µm 추정), 슬러리 제타·농도는 **확인 못 했다**. H4·H5는 단독 채택 금지.
- ⚠ **DOI 없는 1차 자료**: §3·§5의 Granström 2015는 학회 발표논문(Fujimi)으로 DOI가 없고
  동료심사 여부 불명. 고형분·입경·조성 미기재라 $\tau$의 절대값은 이식 불가(형태만 이식).
- ⚠ **특허 데이터의 성격**: §6의 표는 출원인이 자기 발명을 유리하게 보이려고 고른 실시예다.
  h 문턱 65 nm은 청구항 경계와 같은 값이라 **데이터가 문턱을 준 것인지 문턱이 데이터를
  고른 것인지 구분할 수 없다**. 재현한 것은 식(1)의 형태와 표 내부 정합성뿐이다.
- ⚠ **미검증(가정)**: §8의 장벽 환산은 (i) $N_0$(고형분·입경) 가정, (ii) $V_{max}$ 온도무관
  가정, (iii) Reerink–Overbeek 근사 $W\approx e^{V/kT}$에 의존한다. 세 가정 중 하나만
  흔들려도 수 kT가 움직인다 — **오더 진술로만 쓸 것**.
- ⚠ **2차 인용**: §4.1이 인용한 제타 온도계수(fused silica 0.39 %/°C — Evenhuis; 세리아
  −23→−48 mV @10~60 °C — Kim)는 Seo 2021의 참고문헌 17·18을 통한 **2차 인용**이며 원문
  미확인. 참고로 Seo 본인 실측은 0.25 %/°C(45 °C에서 +5 %/20 °C)로 세 값이 0.25~2.17 %/°C
  범위에 흩어진다 — 제타의 온도보정 계수를 상수로 박으면 안 된다.
- **좋은 소식**: §2의 $Q_{10}=2.00$과 §6의 식(1)은 문헌(US20250304827A1)이 준 수치를 우리가
  **독립적으로 역산·재현**했다(각각 0.01 이내, 최대 상대오차 3.4 %). 이 두 개는 계수 자체를 팩에
  넣어도 되는 수준의 자립성을 갖는다.

## 13. 자기시험
→ [[../../agents/slurry-colloid/EXAMS.md]] Lv3-2 문항 참조.
