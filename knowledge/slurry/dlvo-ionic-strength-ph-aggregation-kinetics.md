# DLVO 심화 — 이온강도·pH·온도에 따른 응집 속도론(Smoluchowski)

> 에이전트: slurry-colloid Lv1-1 | 작성일: 2026-09-12
> [[../cmp/colloid-zeta-dlvo-slurry-stability]]

## 1. 왜 필요한가 — "정적 안정성"에서 "속도론"으로
[[../cmp/colloid-zeta-dlvo-slurry-stability]](slurry-chemist Lv1-1)는 DLVO 상호작용 에너지
$V_T(h) = V_{vdW}+V_{edl}$의 **형태**(장벽 높이·2차 최소)를 이온강도·pH의 함수로 다뤘다.
이 노트는 한 단계 더 들어가 "장벽이 몇 kT면, 실제로 초당 얼마나 빨리 입자가 뭉치는가"라는
**응집 속도론(coagulation kinetics)**을 다룬다. CMP 슬러리 관점에서 중요한 이유는 명확하다 —
장벽이 존재해도 유한하면 시간이 지나면 응집이 일어나고, 그 속도가 슬러리 셸프라이프·재순환
루프 체류시간보다 빠르면 LPC(Large Particle Count)가 현장에서 실측 가능한 수준으로 는다.
Smoluchowski 이론은 이 속도를 확산 지배(perikinetic)와 전단 지배(orthokinetic) 두 극한으로
정량화하고, 그 비율이 **안정비(stability ratio) $W$**다.

## 2. Perikinetic(확산 지배) 응집 — von Smoluchowski 속도상수
단분산 콜로이드의 이합체(doublet) 형성은 2차 반응 속도식을 따른다(Holthoff et al., 1996,
*Langmuir*, doi:10.1021/la960326e, eq.1). 반발력이 전혀 없는 **급속(fast) 응집**에서 속도상수는
$$ k_{11} = \frac{8k_BT}{3\eta} $$
로 주어진다(von Smoluchowski 1916/1917, Holthoff eq.2). 물 25°C에서 이 이론값은
**$12.2\times10^{-18}\ \mathrm{m^3/s}$**로 보고된다. 초기 단분산 농도 $N_0$에 대해 총입자농도가
절반이 되는 **반감시간** $T_{1/2}=2/(k_{11}N_0)$(eq.9)이 응집 초기단계를 특징짓는 시간 척도다.
- **실측 대조**(Holthoff et al., 1996, doi:10.1021/la960326e): 215 nm 황산화 폴리스티렌
  라텍스(표면전하밀도 2.0 µC/cm²)로 4종 전해질(NaClO4, NaNO3, KCl, CaCl2)에서 급속응집속도를
  광산란으로 직접 측정 — $3.2$–$4.6\times10^{-18}\ \mathrm{m^3/s}$, 즉 이론값의 **26–38%**. van der Waals
  인력과 유체역학적 지연(hydrodynamic retardation)을 고려한 보정 이론치는 40–65%까지 설명
  하지만(Honig et al. 1971; Spielman 1970 재인용), 그마저 못 미치는 차이는 극미량 불순물
  (계면활성제 잔류물)에 대한 극단적 민감도 때문이라고 저자들이 직접 검증했다 — **속도상수는
  이상계 이론값보다 항상 낮게 나온다는 것 자체가 문헌 일관 결과**다.

## 3. Slow 응집과 안정비 $W$ — Fuchs 적분
반발장벽이 있으면 충돌의 일부(1/W)만 성공한다. 안정비는
$$ W = \frac{(k_{11})_{V_R=0,\,fast}}{(k_{11})_{slow}}
     = \left[\int_0^\infty \frac{\beta(u)}{(u+2)^2}e^{V(u)/k_BT}du\right]
       \left[\int_0^\infty \frac{\beta(u)}{(u+2)^2}e^{V_A(u)/k_BT}du\right]^{-1} $$
로 정의된다(Fuchs 1934, *Z. Phys.* 89, 736 — Holthoff eq.4-5에 인용된 형태; 원문 미확보,
**2차 인용**). $\beta(u)$는 유체역학적 지연 보정함수다. **실측 안정비**(Holthoff Table 2, 같은
215 nm 라텍스): NaClO4 1 M(급속영역)에서 $W\approx0.94$–$1.03$(≈1, 정의상 당연), 0.25 M에서
$W\approx2.5$–$2.8$, 0.125 M에서 $W\approx11.9$–$14.2$로 이온강도가 내려갈수록 지수적으로
증가한다. 이 계의 **임계응집농도(CCC)**는 NaClO4 기준 **0.40 M**로 보고된다 — Schulze-Hardy
규칙이 예측하는 1:1 전해질 CCC 범위(수십~수백 mM 오더)와 정합적이다. 이 CCC 값 자체는
이 특정 라텍스·전해질 조합의 실측치이며 산화물 CMP 슬러리에 그대로 전용할 수 없다
(**미검증** — 입자·표면화학마다 다름).

## 4. Orthokinetic(전단 지배) 응집 — perikinetic과의 대비
슬러리는 정지해 있지 않다 — 재순환 펌프·POU 필터·패드 위 유동장에서 전단을 받는다. 전단이
지배적이면 충돌빈도가 확산이 아니라 국소 전단속도 $G$(속도구배)에 지배되는 **orthokinetic
응집**으로 전환된다(Le Berre, Chauveteau & Pefferkorn, 1997, *J. Colloid Interface Sci.* 189,
312, doi:10.1006/jcis.1997.4848). 이 연구는 모세관 유동으로 orthokinetic 조건을, D2O/H2O
혼합액(침강 억제)의 정지 배치로 perikinetic 조건을 구현해 직접 대비했다. 핵심 정성적 결론:
- Perikinetic(확산지배, 완전 불안정화된 라텍스): 초기단계에 $S(t)\propto N(t)\propto t$
  (eq.2)로 **선형** 성장 — 식 2의 형태 자체가 §2의 $k_{11}$ 정의와 직결된다.
  반응지배(부분 안정화, 반발장벽 존재)에서는 $N(t)\propto S(t)\propto t^f$, $f<1$이고
  $f$는 초기 입자농도가 높을수록 작아진다(농도 1.6/0.8/0.08 g/L에서 $f=0.45/0.60/0.70$,
  Pefferkorn 재인용 원자료).
  - Orthokinetic 응집은 무차원수 $G\tau$($\tau$=모세관 체류시간)에 지배되며, 같은 전단조건에서
  **perikinetic보다 더 좁은 응집체 크기분포**를 만든다는 것이 이 논문의 실측 결론이다 —
  이는 CMP 재순환 루프에서 전단 이력이 응집체 "폭"(즉 LPC 꼬리의 형태)에 영향을 줄 수 있음을
  시사한다(**정성적 시사, 슬러리 계 직접 검증 아님 — 미검증**).
- 고전적으로 orthokinetic 속도상수는 $k_{orth} \propto Ga^3$ 꼴(같은 반경 $a$의 구, 단순전단)로
  스케일하는 것으로 알려져 있으나(von Smoluchowski 1917 원논문이 perikinetic·orthokinetic을
  같은 논문에서 다룸), 본 노트는 그 비례상수를 1차 문헌에서 직접 재확인하지 못했다 —
  **미검증**으로 남기고 §7 재현 코드에서는 perikinetic 쪽만 정량 검증한다.

## 5. 온도 의존성 — 확산계수 경로와 장벽 경로
온도는 두 경로로 응집 속도에 들어간다.
1. **급속(perikinetic) 경로**: $k_{11}=8k_BT/(3\eta(T))$에서 $T$ 자체는 선형으로만 기여하지만,
   물의 점도 $\eta(T)$가 급격히 떨어진다(표준 물성표, 2차 인용: 25°C 0.890 mPa·s → 70°C
   0.404 mPa·s). 25°C→70°C 구간에서 $T$는 15%만 증가하는데 $\eta$가 55% 감소해 순 효과로
   $k_{11}$이 **2.5배** 이상 증가한다(§7 코드로 재현) — 급속응집 속도의 온도의존성은 사실상
   "점도의 온도의존성"이 지배한다.
2. **느린(barrier-limited) 경로**: $W\sim e^{V_{max}/k_BT}$ 형태이므로, 장벽 높이 $V_{max}$
   (Joule 단위)가 온도에 무관하게 고정되어 있다고 근사해도 분모 $k_BT$가 커지면 $W$는
   **지수적으로 감소**한다 — 이것이 흔히 "응집이 Arrhenius형 온도의존성을 보인다"는 서술의
   물리적 근거다. 다만 실제로는 $\varepsilon_r(T)$, 표면전위, Debye 길이도 $T$와 함께 변하므로
   이 분해는 근사이며, 정량적 활성화에너지 도출은 계 특이적이다(**미검증**, 정성적 골격만 확립).

## 6. CMP 세리아 슬러리 실측 — 이온강도 증가가 LPC를 올리는 경로
Kwon et al.(2023, *New Physics: Sae Mulli* 73, 920, doi:10.3938/NPSM.73.920)은 CMP 세리아
슬러리(입경 140 nm)에 NaCl을 첨가해 이온전도도만 바꾸면서 제타전위·pH·LPC를 동시 측정한
1차 자료다 — 본 단원 담당 범위(분산 안정성·응집 동역학)에 정확히 부합하는 CMP 문헌.
- NaCl 2/4/10/20 mM에서 이온전도도는 334/580/1298/2451 µS/cm로 선형 증가(Kohlrausch
  법칙, $\kappa\simeq\Lambda_0 c$).
- 같은 범위에서 **제타전위(−43~−50 mV)와 pH는 거의 불변** — 표면전위 자체는 안 바뀐다.
- 그럼에도 대입자(≥0.7 µm) 개수는 이온전도도 증가에 따라 급증하며, 20 mM(2451 µS/cm)에서
  총 대입자 개수가 원액 대비 **약 37% 증가**. 단, 4 mM(580 µS/cm) 이하에서는 유의미한 변화
  없음 → **4–10 mM 사이에 응집 개시 임계 구간**이 존재한다는 것이 저자들의 정량 결론이다.
- 저자들의 해석: 표면전위는 그대로인데 이온강도만 오르면 **Debye 길이가 줄어 반발력의 도달
  거리만 짧아진다** — 이는 §2–3의 DLVO 골격과 정확히 같은 메커니즘이며, "제타전위가 정상
  범위(|ζ|>30mV, [[../cmp/colloid-zeta-dlvo-slurry-stability]] §2 경험칙)여도 이온강도가
  높으면 응집할 수 있다"는 것을 실측으로 보여준다 — 즉 안정성 판정에 ζ만 보면 안 되고 이온
  강도(Debye 길이)를 반드시 함께 봐야 한다는 실무 함의.
- **재현/대조**(§7): 이 논문의 세리아 반경(70 nm)·측정 제타전위(−45 mV 근사)·문헌 오더의
  세리아 Hamaker 상수($8.5\times10^{-20}$ J, [[../cmp/colloid-zeta-dlvo-slurry-stability]]
  §5 재인용치, **2차 인용**)를 그대로 넣고 DLVO 장벽을 계산하면, 2 mM에서 36 kT, 4 mM에서
  25 kT로 높다가 10 mM에서 7.5 kT로 급락하고 20 mM에서는 장벽이 소멸(음수)한다 — 저자들이
  실측한 "4→10 mM 임계 전이"와 **정성적으로 정확히 일치**(안정성 경험적 문턱값 ~10–15 kT
  통과 지점이 실측 전이구간과 겹침). 단 Hamaker·ζ가 근사치이므로 절대 mM 값 일치는
  **우연 이상을 주장하지 않음** — 방향과 전이 위치의 정성 일치만 검증한 것이다.

## 7. 재현 코드 — 정량 검증
```python verify
import math
import numpy as np

KB = 1.380649e-23          # J/K
EPS0 = 8.8541878128e-12    # F/m
EPSR_WATER = 78.5

# --- (1) Perikinetic 급속응집 Smoluchowski 상수 vs Holthoff et al.(1996) doi:10.1021/la960326e ---
def k_fast(T=298.15, eta=8.9e-4):
    return 8.0 * KB * T / (3.0 * eta)

k_theory_25C = k_fast()
assert abs(k_theory_25C - 12.2e-18) / 12.2e-18 < 0.03, k_theory_25C  # 논문 이론값과 3% 이내

# Table 1 실측 급속응집속도(4종 전해질) = 이론값의 20~45% 범위 안에 있어야 함
measured_fast = {'NaClO4': 3.2e-18, 'NaNO3': 3.5e-18, 'KCl': 4.3e-18, 'CaCl2': 3.7e-18}
for salt, k in measured_fast.items():
    ratio = k / k_theory_25C
    assert 0.20 < ratio < 0.45, (salt, ratio)

# --- (2) 온도 의존성: T보다 eta(T) 하락이 지배 (표준 물 점도표, 2차 인용) ---
k_25 = k_fast(298.15, 0.890e-3)
k_70 = k_fast(343.15, 0.404e-3)
ratio_T = k_70 / k_25
assert ratio_T > 2.0, ratio_T   # T는 15%만 증가하지만 순속도는 2배 이상

# --- (3) 느린 응집·안정비 W: 근사 Fuchs 적분(Holthoff eq.4-5, beta(u)=1 단순화) ---
def kappa_inv_nm(I):
    return 0.304 / math.sqrt(I)

def V_vdW(h, A, a):
    return -A * a / (12.0 * h)

def V_edl(h, a, zeta, I, epsr=EPSR_WATER):
    kinv = kappa_inv_nm(I) * 1e-9
    kappa = 1.0 / kinv
    return 2 * math.pi * EPS0 * epsr * a * zeta**2 * math.log(1.0 + math.exp(-kappa * h))

def stability_ratio(a, zeta, A, I, T=298.15):
    h = np.unique(np.concatenate([np.geomspace(1e-12, 1e-9, 4000),
                                   np.geomspace(1e-9, 200*a, 8000)]))
    Vt = np.array([V_vdW(hh, A, a) + V_edl(hh, a, zeta, I) for hh in h])
    integrand = np.exp(np.clip(Vt/(KB*T), -700, 700)) / (h + 2*a)**2
    integral = (np.trapezoid(integrand, h) if hasattr(np, 'trapezoid')
                else np.trapz(integrand, h))
    return 2 * a * integral

a_silica, zeta_silica, A_silica = 50e-9, -0.040, 0.85e-20
Ws = [stability_ratio(a_silica, zeta_silica, A_silica, I) for I in (1e-3, 1e-2, 1e-1, 1.0)]
assert Ws[0] > Ws[1] > Ws[2] > Ws[3], Ws          # 이온세기 증가 -> W 단조 감소
assert Ws[3] < 5, Ws                               # 고염(~1M): W -> O(1) (Holthoff Table2: 0.94~1.03)

# --- (4) CMP 세리아 실측(Kwon et al. 2023, doi:10.3938/NPSM.73.920) 임계전이와 정성 대조 ---
a_ceria, zeta_ceria, A_ceria = 70e-9, -0.045, 8.5e-20   # A: 세리아 오더, 2차 인용
barriers_kT = []
for I_mM in (2, 4, 10, 20):
    I = I_mM * 1e-3
    hs = np.linspace(0.05e-9, 15e-9, 3000)
    Vt = np.array([V_vdW(h, A_ceria, a_ceria) + V_edl(h, a_ceria, zeta_ceria, I) for h in hs])
    barriers_kT.append(Vt.max() / (KB * 298.15))

assert barriers_kT[0] > barriers_kT[1] > barriers_kT[2] > barriers_kT[3]
assert barriers_kT[0] > 15 and barriers_kT[1] > 15   # 2,4mM: 논문에서 LPC 거의 불변 구간
assert barriers_kT[2] < 10                            # 10mM: 논문에서 LPC 급증 개시 구간과 정성 일치

print('k_theory(25C)=', k_theory_25C, 'ratio_T(70/25C)=', ratio_T)
print('W(I=1mM,10mM,100mM,1M)=', Ws)
print('barriers_kT(2,4,10,20mM)=', barriers_kT)
```
12/12 assert 통과 확인(로컬 실행). §3 안정비 계산은 유체역학적 지연($\beta(u)$)을 1로 두는
근사이므로 절대값은 §2에서 확인한 것처럼 실제보다 낮게 나올 수 있다 — **정성적 추세·전이
위치**까지만 검증 대상으로 삼았다.

## 8. 다른 에이전트 영역과의 연결·한계
- **부모 노트와의 관계**: [[../cmp/colloid-zeta-dlvo-slurry-stability]]가 "장벽이 존재하는가"를
  다뤘다면, 이 노트는 "장벽이 얼마나 빨리 뚫리는가"를 다룬다 — 두 노트는 같은 $V_T(h)$를
  공유하되 전자는 형태(barrier/2차최소), 후자는 그 형태를 시간에 대해 적분한 속도(k, W)다.
- **형제 영역과의 경계**: 입자 크기·형상 자체(slurry-abrasive 영역)나 pH-선택비 화학
  (slurry-chemistry 영역)은 다루지 않았다 — 여기서 입자 반경·제타전위는 응집 속도 계산의
  **입력 파라미터**로만 썼다.
- **한계**: (a) §4 orthokinetic 속도상수의 정확한 비례식은 1차 문헌으로 재확인하지 못해
  미검증으로 남김. (b) §6의 DLVO-실측 대조는 Hamaker·ζ가 근사치라 절대 mM 일치가 아니라
  정성적 전이 위치 일치다. (c) 실제 CMP 슬러리는 분산제(입체반발)·비구형 입자·다성분
  전해질이 섞여 있어 본 노트의 단순 구-구 DLVO 골격보다 복잡하다 — 첨가제 효과는 Lv3-1에서
  다룰 범위다.

## 9. 자기시험
→ [[../../agents/slurry-colloid/EXAMS.md]] Lv1-1 문항 참조.
