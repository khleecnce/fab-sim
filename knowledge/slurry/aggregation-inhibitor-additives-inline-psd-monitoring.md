# 응집 억제 첨가제와 실시간 입도 모니터링 — 꼬리를 막는 손과 꼬리를 보는 눈

> 에이전트: slurry-colloid Lv3-1 | 작성일: 2026-09-14
> 선행: [[colloidal-destabilization-lpc-defect-mechanism]] [[dlvo-ionic-strength-ph-aggregation-kinetics]]
>       [[pou-filtration-recirculation-pump-shear-lpc]] [[shelf-life-dilution-two-part-blending-qc]]
> 관련: [[../cmp/colloid-zeta-dlvo-slurry-stability]] [[../cmp/lpc-scratch-density-tail-correlation]]

## 1. 이 노트가 채우는 자리 — 그리고 형제 영역과의 경계

선행 노트 4편은 **왜/어떻게 슬러리가 불안정화되어 LPC 꼬리가 생기는가**를 세웠다:
정적 화학(이온강도·pH, [[dlvo-ionic-strength-ph-aggregation-kinetics]]), 그것이 손상으로
연결되는 인과([[colloidal-destabilization-lpc-defect-mechanism]]), 팹 루프의 전단 생성·필터
제거([[pou-filtration-recirculation-pump-shear-lpc]]), 제조·보관·희석·혼합 이력
([[shelf-life-dilution-two-part-blending-qc]]). 이 Lv3-1 노트는 그 위에 **대응(counter-measure)
두 축**을 올린다:

- **(a) 응집을 억제하는 손** — 고분자 분산제·전해질형 분산제(첨가제)의 정량 효과: 첨가량
  (wt%)에 대한 제타전위·평균입경·현탁 안정성의 변화.
- **(b) 응집을 보는 눈** — 실시간/인라인 입도 모니터링(단일입자 광학계수 SPOS, DLS,
  Nano-LPM)의 검출한계·농도범위·상관계수, 그리고 그 계측을 근본적으로 제약하는 통계 바닥.

**⚠ 형제 영역 침범 금지 선언**: 이 노트가 인용하는 세리아·란타넘-세리아 슬러리 논문들은
연마입자 자체의 합성(slurry-abrasive 영역)이나 제거율·선택비 제형 최적화(slurry-chemistry
영역)도 다룬다. 이 노트는 그 부분을 **의도적으로 배제**하고 오직 **안정화(분산제 흡착·전하)와
모니터링(계측) 관점만** 채택한다. 제거율(RR) 수치는 문맥으로만 스치고 드라이버로 쓰지 않는다.

## 2. 첨가제 (1) — 고분자 분산제: 첨가량↑ → 제타↑·입경↓·보관드리프트↓ (단조)

**Hwang, S., Park, J., Kim, W. (2024). "The Stability Evaluation of Ceria Slurry Using Polymer
Dispersants with Varying Contents for Chemical Mechanical Polishing Process." *Polymers* 16(24),
3593. DOI: 10.3390/polym16243593 (PMC11679047)** — MDPI OA 전문(JATS XML) 확보.

세리아 슬러리에 **에틸렌-아크릴산(EAA) 공중합체의 아연염**을 고분자 분산제로 **5 / 6 / 7 wt%**
(D5/D6/D7) 넣고 상용 세리아와 비교했다. 이 분산제의 핵심은 폴리아크릴산 사슬의 카복실기
(-COOH)가 세리아 표면에 흡착해 **정전기 반발을 키우는 전기-입체(electrosteric) 안정화**다.
분산 관련 정량 결과(원문 본문·표):

| 항목 | 상용 | D5 (5 wt%) | D6 (6 wt%) | D7 (7 wt%) | 방향 |
|---|---|---|---|---|---|
| 제타전위 (mV, 절댓값) | 49.2 | 42.9 | 45.3 | 52.1 | 첨가량↑ → 증가 |
| DLS 평균입경 (nm) | — | 281.6 | 251.8 | 227.2 | 첨가량↑ → 감소 |
| 점도 변화율 (cP, 60 °C·3개월) | — | 0.39 | 0.23 | 0.03 | 첨가량↑ → 감소(안정) |

세 지표가 **모두 같은 방향**을 가리킨다: 분산제를 더 넣을수록 표면 흡착이 조밀해져 제타가
커지고(반발↑), 응집이 줄어 DLS 입경이 작아지며, 고온 장기보관 시 점도 드리프트(응집 지표)가
거의 0에 수렴한다. D7(7 wt%)이 상용보다도 제타가 높고(52.1 > 49.2 mV) 입경이 작았다.
이는 [[shelf-life-dilution-two-part-blending-qc]] §2의 "보관 시계"를 첨가제로 늦추는 직접
사례다 — 60 °C 3개월에도 점도 드리프트 0.03 cP.

```python verify
import numpy as np
# --- Hwang et al. 2024 (doi:10.3390/polym16243593) 분산 지표 3종 ---
wt      = np.array([5.0, 6.0, 7.0])        # 분산제 함량 D5/D6/D7 [wt%]
zeta    = np.array([42.9, 45.3, 52.1])     # 제타전위 절댓값 [mV] (상용 49.2)
size    = np.array([281.6, 251.8, 227.2])  # DLS 평균입경 [nm]
visc    = np.array([0.39, 0.23, 0.03])     # 60°C·3개월 점도 변화율 [cP]
Z_COMM, STAB_TH = 49.2, 30.0               # 상용 제타, 안정성 경험 문턱 |ζ|>30mV

# (1) 세 지표가 모두 첨가량에 단조 — 제타 증가, 입경 감소, 드리프트 감소
assert all(zeta[i] < zeta[i+1] for i in range(2)), "제타는 첨가량↑에 단조증가여야"
assert all(size[i] > size[i+1] for i in range(2)), "입경은 첨가량↑에 단조감소여야"
assert all(visc[i] > visc[i+1] for i in range(2)), "점도 드리프트는 첨가량↑에 단조감소여야"
print(f"재현: 5→7wt% 에서 제타 {zeta[0]}→{zeta[-1]}mV, 입경 {size[0]}→{size[-1]}nm, "
      f"드리프트 {visc[0]}→{visc[-1]}cP — 세 지표 방향 일치")

# (2) 제타-입경 상관: 완전 음의 순위상관(반발 클수록 응집 작다)
r = float(np.corrcoef(zeta, size)[0,1])
assert r < -0.9, f"제타-입경 상관이 강한 음이어야 하는데 r={r:.3f}"
print(f"재현: 제타 vs 입경 Pearson r={r:.3f} (강한 음 — 전기-입체 반발이 응집 억제; "
      f"완전선형(−1)은 아님: 3점, 상용 대비 D5가 약간 낮은 제타)")

# (3) D7만 상용을 넘어선다 (문헌 주장: 7wt%가 상용보다 우수)
assert zeta[-1] > Z_COMM and all(z > STAB_TH for z in zeta), \
    "D7 제타가 상용(49.2)을 넘고, 세 시료 모두 |ζ|>30mV 안정영역이어야"
print(f"문헌값 대조: D7 {zeta[-1]}mV > 상용 {Z_COMM}mV, 전 시료 |ζ|>{STAB_TH:.0f}mV 안정영역")
```

## 3. 첨가제 (2) — 전해질형 분산제(SHMP): 최적 투여량이 존재한다(단조 아님)

**Mei, Y., Chen, W., Chen, X. (2024). "The Effect of Sodium Hexametaphosphate on the Dispersion
and Polishing Performance of Lanthanum–Cerium-Based Slurry." *Materials* 17(19), 4901.
DOI: 10.3390/ma17194901 (PMC11477672)** — MDPI OA 전문 확보.

란타넘-세리아 연마재(1차 입경 **600–800 nm**, 응집 경향 강함)에 **헥사메타인산나트륨
(SHMP, (NaPO₃)₆, 중합도 6)**을 분산제로 **0.3 / 0.4 / 0.5 / 0.6 / 0.8 / 1.5 / 3.0 wt%** 스윕했다.
SHMP는 다가 음이온 폴리인산으로, §2의 고분자와 달리 **작은 전해질형 분산제**다. 원심분리 후
상등액 **탁도(NTU, 높을수록 입자가 현탁에 오래 남음=잘 분산)**로 안정성을 판정:

- SHMP **무첨가**: 탁도 매우 낮음(현탁 성능 나쁨).
- 0.3 → 0.5 wt%로 탁도 급상승, **0.5 wt%에서 최대 2715 NTU**(최적, 접촉각도 최소 45°).
- 0.5 wt% **초과에서는 감소**(원문: "최적 투여량은 약 0.5 wt%") — 과투여 시 재-불안정화.

제타전위(SHMP 처리 시): pH 6에서 **−48.49 mV**, pH 11에서 **−51.99 mV**(두 국소 최대), pH 12에서
−28.55 mV. 무첨가 슬러리는 pH 3에서 **+34.65 mV**(표면 수산기 양성자화). 즉 SHMP는 제타를
강한 음으로 끌어내려 반발을 만든다.

**§2와 대비되는 이 절의 핵심**: 고분자 분산제(§2)는 조사 구간에서 **단조**였지만, 전해질형
소분자 분산제(SHMP)는 **최적점을 가진 산(∩)형**이다. 과투여하면 이온강도 증가
([[dlvo-ionic-strength-ph-aggregation-kinetics]] §3의 Debye 압축)와 가교/전하 과포화로 오히려
불안정해진다. 따라서 "분산제는 많을수록 좋다"는 일반화는 **틀린다** — 첨가제 종류에 따라
단조냐 최적형이냐가 갈린다(§7에서 sim 함의로).

```python verify
# --- Mei et al. 2024 (doi:10.3390/ma17194901) SHMP 분산 ---
dose = [0.3, 0.4, 0.5, 0.6, 0.8, 1.5, 3.0]   # SHMP 투여량 [wt%] (원문 스윕)
TURB_MAX_NTU, DOSE_OPT = 2715.0, 0.5          # 최대 탁도와 그 위치(원문 명시)
# 제타(원문): SHMP 처리 pH6/pH11, 무첨가 pH3
z_pH6, z_pH11, z_noSHMP_pH3 = -48.49, -51.99, 34.65   # mV
STAB_TH = 30.0

# (1) 최적점 존재: 최대 탁도 위치가 스윕 구간의 '내부'(양 끝이 아님) → ∩형
assert DOSE_OPT in dose and DOSE_OPT != min(dose) and DOSE_OPT != max(dose), \
    "최적 투여량이 스윕 내부에 있어야 ∩형(최적점 존재)이라 말할 수 있다"
below = [d for d in dose if d < DOSE_OPT]; above = [d for d in dose if d > DOSE_OPT]
assert below and above, "최적점 양쪽에 데이터가 있어야(0.3~0.5 상승, 0.5 초과 감소)"
print(f"재현: SHMP 탁도 최대 {TURB_MAX_NTU:.0f} NTU @ {DOSE_OPT}wt% — "
      f"최적점이 스윕 내부(0.3~3.0) → 고분자(§2)의 단조와 달리 ∩형(과투여 재-불안정화)")

# (2) SHMP는 제타를 강한 음으로: |ζ|가 안정 문턱을 크게 넘는다
assert abs(z_pH6) > STAB_TH and abs(z_pH11) > STAB_TH, "SHMP 처리 |ζ|>30mV 안정영역이어야"
# (3) 부호 전환: 무첨가 저pH(+34.65)에서 SHMP·중성~염기에서 강한 음으로
assert z_noSHMP_pH3 > 0 > z_pH6, "무첨가 저pH는 양(+), SHMP 처리는 음(−)이어야"
print(f"문헌값 대조: 무첨가 pH3 {z_noSHMP_pH3:+.2f}mV → SHMP pH6 {z_pH6:.2f}mV / "
      f"pH11 {z_pH11:.2f}mV (|ζ| 최대 {abs(z_pH11):.1f}mV, 안정 문턱 {STAB_TH:.0f}의 "
      f"{abs(z_pH11)/STAB_TH:.1f}배)")
```
⚠ **미검증**: 0.5 wt% 초과 구간의 개별 탁도 수치는 원문 Figure 2(그래프)에만 있어 이 노트가
수치화하지 못했다 — "0.5 초과 감소"는 원문 서술("optimal ≈ 0.5%")과 침강 사진에 근거한
**정성 판정**이다. 절대 탁도 곡선의 하강 기울기는 인용하지 않는다.

## 4. 폐형식 재현 — 첨가제로 바뀐 제타가 DLVO 장벽·Smoluchowski 안정비 W를 얼마나 올리나

§2의 측정 제타·입경을 [[dlvo-ionic-strength-ph-aggregation-kinetics]] §7과 같은 DLVO 폐형식
($V_T=V_{vdW}+V_{edl}$, 상수전위 근사)에 넣으면, **첨가제가 제타를 올린 효과가 응집 장벽·
안정비로 얼마나 증폭되는지**를 정량화할 수 있다. 안정비는 Reerink–Overbeek 근사
$W\sim e^{V_{max}/k_BT}$([[dlvo-ionic-strength-ph-aggregation-kinetics]] §3의 Fuchs 적분을
장벽높이로 축약한 형태)로 쓴다.

핵심 긴장: 분산제를 더 넣으면 **제타는 오르지만(장벽↑)** DLS 입경은 **작아진다(a↓, 장벽↓)**.
EDL 장벽은 $\propto a\zeta^2$, vdW는 $\propto a$이므로 둘이 상충한다. 실제 측정값으로 계산하면
$\zeta^2$ 증가(42.9²→52.1², 1.47배)가 반경 감소(140.8→113.6 nm, 0.81배)를 이겨 **순 장벽은
D5<D6<D7로 단조 증가**한다.

```python verify
import math, numpy as np
KB, T = 1.380649e-23, 298.15
EPS0, EPSR = 8.8541878128e-12, 78.5

def kinv_nm(I): return 0.304/math.sqrt(I)                       # Debye 길이 [nm], 1:1 전해질 25°C
def V_vdW(h,A,a): return -A*a/(12.0*h)                          # 구-구 근접 근사
def V_edl(h,a,zeta,I):
    kappa = 1.0/(kinv_nm(I)*1e-9)
    return 2*math.pi*EPS0*EPSR*a*zeta**2*math.log(1.0+math.exp(-kappa*h))
def barrier_kT(a,zeta,A,I):
    hs = np.linspace(0.1e-9, 30e-9, 4000)
    V  = np.array([V_vdW(h,A,a)+V_edl(h,a,zeta,I) for h in hs])
    return V.max()/(KB*T)

# 세리아 문헌 오더: Hamaker A=8.5e-20 J (2차 인용, [[../cmp/colloid-zeta-dlvo-slurry-stability]] §5)
# 이온강도 I는 원문 미기재 → 1 mM 가정(아래 결론은 '같은 I에서의 시료 간 비교'라 가정값에 견고)
A_ceria, I_assume = 8.5e-20, 1.0e-3
samples = {'D5':(281.6,42.9), 'D6':(251.8,45.3), 'D7':(227.2,52.1)}   # (DLS nm, |ζ| mV)

bars, Ws = {}, {}
for name,(d_nm,z_mV) in samples.items():
    a = d_nm*1e-9/2; z = z_mV*1e-3
    b = barrier_kT(a, z, A_ceria, I_assume)
    bars[name] = b; Ws[name] = math.exp(min(b,700.0))
    print(f"  {name}: a={a*1e9:.1f}nm, |ζ|={z_mV}mV → 장벽 {b:.0f} kT, W≈exp({b:.0f})={Ws[name]:.2e}")

# (1) 첨가량↑ → 순 장벽 단조 증가 (ζ² 증가가 반경 감소를 이긴다)
assert bars['D5'] < bars['D6'] < bars['D7'], "순 DLVO 장벽이 D5<D6<D7로 단조증가여야"
# (2) ζ²·a 상충의 정량 확인: ζ²는 1.47배 커지고 a는 0.81배로 준다
ratio_z2 = (52.1/42.9)**2; ratio_a = 227.2/281.6
assert ratio_z2 > 1.4 and ratio_a < 0.85, "ζ²↑와 a↓가 실제로 상충해야"
assert ratio_z2*ratio_a > 1.0, "ζ²·a 곱이 1보다 커야 EDL 장벽 순증가(장벽 지배항)"
print(f"재현: D5→D7 에서 ζ²×{ratio_z2:.2f}, a×{ratio_a:.2f} → EDL 항 ×{ratio_z2*ratio_a:.2f} (순증가)")
# (3) 안정비 W는 장벽을 지수증폭 — 첨가제 3wt%p 차이가 W를 여러 자릿수 벌린다
assert Ws['D7']/Ws['D5'] > 1e10, "장벽 지수증폭으로 W 비가 10자릿수 이상 벌어져야"
print(f"재현: W(D7)/W(D5) ≈ {Ws['D7']/Ws['D5']:.1e} — 제타 {42.9}→{52.1}mV(첨가량 5→7wt%)가 "
      f"안정비를 {math.log10(Ws['D7']/Ws['D5']):.0f}자릿수 증폭")
```
⚠ **미검증(절대값)**: 위 장벽·W의 **절대값**은 이온강도 1 mM 가정과 Hamaker 오더 인용에
의존하므로 인용하지 않는다(원문은 이온강도·Hamaker를 안 줬다). **검증한 것은 시료 간
방향·순서**(D5<D6<D7)와 상충항의 부호($\zeta^2 a$ 순증가)뿐이다 — 이는 가정값이 세 시료에
공통이라 가정에 견고하다. EVIDENCE-RULES 등급 **E3**(대상계 실측이나 이온강도·Hamaker 교란).

## 5. 모니터링 (1) — LPC 계수의 지울 수 없는 바닥: Poisson 통계

**Lee, M., Kim, D., Heo, T.-Y., Park, T., Kim, W., Choi, D. (2020). "Universal inherent fluctuations
in statistical counting of large particles in slurry used for semiconductor manufacturing."
*Scientific Reports* 10, 71768. DOI: 10.1038/s41598-020-71768-3 (PMC7477581)** — Nature OA 전문 확보.

CMP 슬러리의 대입자(**≥0.5 µm**, 주 연마입자 ≈0.1 µm)를 세는 파티클 카운터(광산란·광소멸·
홀로그래피)의 측정값에 **기기 종류와 무관한 보편적(universal) 요동**이 존재함을 해석적으로
유도하고 실험·몬테카를로로 검증한 1차 논문이다. 측정 절차는 이 단원의 앞 노트들과 직결된다:
슬러리를 **수십 배 희석**(원문 희석계수 δ=60)해 카운터에 수 mL/min으로 흘리고 수 분간 센 뒤
1 mL당 개수로 환산한다 — **희석 자체가 [[shelf-life-dilution-two-part-blending-qc]] §6.3의
교란**이자, 아래 통계 바닥의 원인이다.

핵심 폐형식: 희석이 대입자를 시료 부피에 무작위로 뿌리므로 계수는 **Poisson 통계**를 따른다.
평균 λ인 Poisson의 표준편차는 √λ이므로 **상대오차 $E\propto 1/\sqrt{\lambda}$**다. n회 반복측정의
95 % 신뢰구간 반폭을 평균으로 나눈 상대오차는 $E \approx z\,\sqrt{\lambda}/(\sqrt{n}\,\lambda)
= z/\sqrt{n\lambda}$ ($z=1.96$). **덜 셀수록(λ 작을수록) 요동이 커진다** — 그리고 카운터에
필요한 희석은 λ를 δ배 줄이므로 통계 정확도와 상충한다.

```python verify
import math
# --- Lee et al. 2020 (doi:10.1038/s41598-020-71768-3) Poisson 계수 바닥 ---
Z95, N_REP, DELTA = 1.96, 3, 60          # 95%CI z, 반복 n=3, 희석계수 δ=60 (원문 파라미터)

def rel_err(lam, n=N_REP, z=Z95):        # 상대오차 E = z/sqrt(n·λ)
    return z/math.sqrt(n*lam)

# (1) √λ 스케일: 셈 수 100배면 상대오차 1/10 (요동은 개수의 제곱근에 반비례)
E_lo, E_hi = rel_err(100), rel_err(10000)
assert abs((E_lo/E_hi) - 10.0) < 1e-6, "100배 계수 증가는 상대오차를 정확히 10배 낮춰야(1/√λ)"
print(f"재현: λ=100 → E={E_lo*100:.1f}%, λ=10⁴ → E={E_hi*100:.1f}% (100배 계수 → 요동 1/{E_lo/E_hi:.0f})")

# (2) 요동을 절반으로 줄이려면 셈 수를 4배로 (√ 법칙의 실무적 대가)
lam0 = 400.0
assert abs(rel_err(4*lam0) - 0.5*rel_err(lam0)) < 1e-9, "E 절반엔 λ 4배 필요"
print(f"재현: E를 절반으로 → λ {lam0:.0f}→{4*lam0:.0f} (4배 계수 필요) = 측정시간/부피 4배 대가")

# (3) 희석의 대가: δ=60 희석은 유효 λ를 60배 줄여 상대오차를 √60배 키운다
worsen = math.sqrt(DELTA)
assert abs(rel_err(1000/DELTA)/rel_err(1000) - worsen) < 1e-9
print(f"재현: 희석계수 δ={DELTA}는 같은 측정부피에서 상대오차를 √{DELTA}={worsen:.1f}배 악화 "
      f"→ 카운터가 요구하는 희석(농도범위 맞추기)이 곧 계수통계의 적 (Lee 2020)")
```

이 절이 앞 노트에 주는 못: [[colloidal-destabilization-lpc-defect-mechanism]] §3은 "벌크
광산란 입도계는 LPC 꼬리에 둔감하다(부피가중 주 모드가 지배)"고 했다. 여기에 더해 **개별입자
계수(SPOS)조차 그 꼬리를 셀 때 Poisson 바닥에 걸린다** — 꼬리는 희소해서(λ 작음) 본질적으로
요동이 크다. 즉 LPC 관리는 "더 좋은 센서"만으로 안 되고 **충분한 계수(부피·시간)**를 확보해야
한다는 통계적 제약이 있다.

## 6. 모니터링 (2) — SPOS 단일입자 광학계수·Nano-LPM/DLS: 검출한계·농도범위·상관

대입자 꼬리를 실제로 세는 계측기 두 부류의 최신 사양. **아래 두 논문은 초록만 확보(원문
본문은 출판사 봇차단으로 미확보) — 초록에 명시된 수치만 인용하며 E5(2차 인용)로 취급한다.**

**(i) 단일입자 광학 계수·측정(SPOS 계열)** — Hussels, M., Lichtenfeld, H., Woehlecke, H.,
Wollik, E., Lerche, D. (2024). "Instrument with an ultra-wide dynamic detection range for the
optical counting and sizing of individual particles in suspensions." *Rev. Sci. Instrum.* 95(2),
023704. DOI: 10.1063/5.0165811. 초록 명시: 수용액 현탁 속 나노·마이크로 개별 입자를 **두 방향
광산란**으로 검출, **동적 검출범위 ≥ 6 자릿수(decade)**, 유체역학적 집속(hydrodynamic focusing)
으로 입자를 분리해 안정된 산란 조건 확보. → 서브마이크론 주 모드와 희소한 대입자 꼬리를
**같은 기기에서** 넓은 농도범위로 커버한다는 것이 SPOS류의 강점(→ §5 Poisson 바닥을
넓은 λ에서 회피).

**(ii) 인라인 Nano-LPM vs DLS vs SEM** — Cho, S., Cho, Y., Roux, A., Gwak, S., Troolin, D.,
Han, H. (2026). "Nano liquid particle monitoring system for colloidal nanoparticle measurement:
reducing non-volatile residue via virtual impactor with large-droplet removal."
*Meas. Sci. Technol.* 37(23). DOI: 10.1088/1361-6501/ae6ba6. 초록 명시: 에어로졸 기반 입도분포
측정계(Nano-LPM)를 DLS·SEM과 대조, 표준 폴리스티렌라텍스(**PSL 50–200 nm**)로 교정 시
**농도 응답이 거의 완벽 선형(R² > 0.995)**, 반복 측정의 결합표준불확도 작음.

```python verify
import math
# --- 모니터링 사양 (초록 기반, E5 2차 인용 — 아래는 초록 명시값의 정합성/함의 체크) ---
DECADES = 6                     # Hussels 2024 (doi:10.1063/5.0165811): 동적범위 ≥6 decade
DYN_RANGE = 10.0**DECADES
R2_LIN = 0.995                  # Cho 2026 (doi:10.1088/1361-6501/ae6ba6): PSL 농도응답 선형
PSL_LO, PSL_HI = 50.0, 200.0    # nm, Cho 2026 교정 범위

assert DYN_RANGE >= 1e6, "≥6 decade면 동적범위 ≥10⁶"
assert R2_LIN > 0.99, "농도응답 R²>0.99 (초록 명시값 기록)"
assert PSL_HI/PSL_LO == 4.0, "PSL 교정 범위 50~200nm는 4배 구간"
print(f"문헌값 기록(초록): 동적범위 ≥{DYN_RANGE:.0e}({DECADES} decade), "
      f"PSL {PSL_LO:.0f}~{PSL_HI:.0f}nm 선형응답 R²>{R2_LIN}")

# (i) 검출한계 대비: LPC 관심 임계(≥0.5µm=500nm, Lee 2020)는 DLS 주모드(~100nm)의 5배 —
#     DLS(강도가중 평균)로는 이 희소 꼬리가 주모드에 묻힌다(선행노트 반복 주제).
LPC_TH_NM, DLS_MODE_NM = 500.0, 100.0
assert LPC_TH_NM/DLS_MODE_NM == 5.0
print(f"함의: LPC 임계 {LPC_TH_NM:.0f}nm는 주모드 {DLS_MODE_NM:.0f}nm의 {LPC_TH_NM/DLS_MODE_NM:.0f}배 "
      f"→ DLS(강도·부피가중 평균)는 꼬리에 둔감, 단일입자계수(SPOS)가 필요 "
      f"(cf. [[colloidal-destabilization-lpc-defect-mechanism]] §3)")

# (ii) 선형응답 R²>0.995는 '필요조건'일 뿐 — §5 Poisson 바닥은 R²와 무관하게 남는다
#      (교정이 완벽해도 희소 꼬리는 셈 수 부족으로 요동)
lam_tail = 50.0                 # 희소 대입자 꼬리의 전형적 낮은 계수(예시)
E_tail = 1.96/math.sqrt(3*lam_tail)
assert E_tail > 0.15, "λ~50 꼬리는 R²와 무관하게 상대오차>15% (Poisson 바닥)"
print(f"함의: 농도응답 R²>{R2_LIN}(교정)이어도 λ≈{lam_tail:.0f} 꼬리는 상대오차 {E_tail*100:.0f}% "
      f"— 선형성(계통)과 계수통계(우연)는 다른 축, 둘 다 잡아야 한다")
```
⚠ **미검증**: (i)(ii)의 수치(6 decade, R²>0.995, PSL 50–200 nm)는 **초록 문장 그대로**이며
원문 본문·표를 확보하지 못했다(AIP·IOP 봇차단). 검출한계의 절대 µm값, 농도범위(개수/mL),
방법 간 상관계수(R)의 구체값은 **확인 못함** — 위 verify는 초록 명시값의 자릿수 정합성과
§5 통계와의 논리적 함의만 검사한 것이지, 원문 재현이 아니다.

## 7. sim/에 대한 시사점 (코드는 건드리지 않음 — PROFILE.md 구현 요청으로 기록)

1. **첨가제 효과는 종류에 따라 단조 vs 최적형으로 갈린다**(§2 고분자 단조, §3 SHMP ∩형).
   `aggregate_ratio` 같은 상태량을 "분산제량의 선형 감소함수"로 두면 전해질형에서 틀린다 —
   과투여 재-불안정화(∩형)를 표현하려면 최적점 파라미터가 필요하다. 절대 계수 근거는 아직 없음.
2. **첨가제 → 안정성의 물리 통로는 제타(전하)다**(§4). 첨가제량을 직접 드라이버로 넣기보다
   **제타전위**를 매개변수로 두고 DLVO 장벽·W로 연결하는 것이 이식성이 높다(§4 폐형식은
   [[dlvo-ionic-strength-ph-aggregation-kinetics]] §7 코드와 동일 골격).
3. **LPC는 계측 자체에 Poisson 바닥이 있다**(§5). 만약 sim이 LPC를 '측정된 관측량'으로 낸다면,
   그 관측에는 $E=z/\sqrt{n\lambda}$의 우연오차가 붙어야 정직하다 — 단일 결정값으로 내면
   실측 재현성(로트 간 산포)을 과신하게 된다.

## 8. 한계·정직성 표기

- ⚠ **E3(교란)**: §2·§3의 첨가제 실험은 세리아/란타넘-세리아 연마재 계다. 제타·입경 변화의
  **방향**은 이식 가능하나(전기-입체 안정화의 일반 물리), 특정 wt% 최적값(SHMP 0.5 wt%)이나
  절대 제타값을 실리카·W 슬러리에 그대로 쓰면 안 된다 — 표면화학·IEP가 다르다.
- ⚠ **미검증(절대값)**: §4의 DLVO 장벽·W 절대값은 이온강도(원문 미기재, 1 mM 가정)·Hamaker
  오더 인용에 의존 — 시료 간 **순서/방향만** 검증됐다.
- ⚠ **초록 기반(E5)**: §6의 두 모니터링 논문은 원문 본문 미확보. 6 decade·R²>0.995·PSL
  50–200 nm는 초록 명시값이며, 검출한계 µm·농도범위·방법 간 상관 R의 구체값은 확인 못함.
- ⚠ **그래프 판독 부재**: §3의 SHMP 0.5 wt% 초과 탁도 하강은 원문 그래프·서술에 근거한 정성
  판정이고 개별 수치는 인용하지 않았다.
- **좋은 소식**: §2의 세 지표(제타·입경·점도드리프트)가 **동시에** 같은 방향으로 움직였다 —
  분산제 최적화의 성패는 값싼 지표(제타·보관 점도) 두 개만으로도 방향을 잡을 수 있다.

## 9. 자기시험
→ [[../../agents/slurry-colloid/EXAMS.md]] Lv3-1 문항 참조.
