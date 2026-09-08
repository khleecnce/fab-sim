<!-- V2-SECTION: R1-equipment | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: kinematic, rpm, tool-architecture | 정본: ARCHITECTURE-V2.md §3 -->
# WIWNU 모델 — 압력·속도·슬러리 반경분포의 웨이퍼 스케일 결합

> 에이전트: process-integrator Lv2-2 | 작성일: 2026-09-05
> [[preston-luo-dornfeld-mrr]] [[cmp-kinematics-rotary]] [[cmp-tool-architecture]] [[hertz-gw-contact-mechanics]]

## 1. WIWNU 정의와 지표 — "표준이 없다"는 것이 핵심

WIWNU(within-wafer non-uniformity)는 한 장의 웨이퍼 안에서 두께제거(또는 MRR)가
반경/위치에 따라 얼마나 균일한지를 하나의 수로 요약한 값이다. 웨이퍼 위 다점 측정
$\{\Delta_i\}$(제거두께 또는 잔막)에 대해 문헌에서 쓰이는 지표는 **여러 종류가 공존**한다:

- **표준편차형**: $\text{WIWNU}\% = 100\cdot \sigma(\Delta_i)/\overline{\Delta_i}$, 흔히 **$3\sigma/\text{mean}$** 을 "3σ WIWNU"로 표기.
- **범위형(k값·반범위)**: $k = (\Delta_{max}-\Delta_{min})/(2\,\overline{\Delta})$ — 이 단원이 명시한 정의식(반범위/half-range).
- $k$값은 max/min만 쓰므로 이상점(outlier)에 민감하고 **일반적으로 σ형보다 크다**.

출처: W. Lee, D. Boning et al., "A study of within-wafer non-uniformity metrics," *IEEE Int. Conf. Microelectronic Test Structures (ICMTS)* (1999) — "there is no standard guideline for reporting WIWNU ... calculation varies in the industry"를 명시(검색스니펫·IEEE Xplore 초록으로 확인, 본문 유료 **미검증**). 실무 리뷰에서도 σ/mean(%)과 range 지표가 혼용됨(A. Kumar, *IMAPS 2019 Boston*, "Optimizing the WIWNU at the CMP step ... for 3D IC stacking", imapsource.org 오픈액세스 — 제목·소속만 확인, PDF 바이너리 **본문 미검증**).

→ **함의**: WIWNU 수치를 인용할 때는 반드시 정의식을 병기해야 한다. 본 코드베이스는
half-range·σ·3σ를 **모두** 출력한다(`sim/tier1_empirical/wiwnu.py`).

## 2. MRR(r) = Kp·P(r)·V(r) 결합 — 무엇이 주범인가

Preston식([[preston-luo-dornfeld-mrr]])을 반경 프로파일로 쓰면
$$ \text{MRR}(r) = K_p \cdot P(r) \cdot \langle |v(r,\theta)|\rangle_\theta $$
곱 구조이므로 WIWNU는 **압력 반경분포 $P(r)$** 와 **시간평균 속도 반경분포 $\langle|v|\rangle_\theta$** 의
곱이 만드는 비균일이다. 두 항의 상대적 기여를 분리하면:

- **속도항**: [[cmp-kinematics-rotary]] Lv1-2 결론 계승 — 웨이퍼 자전으로 반경 $r$의 점은
  $\theta$ 전구간을 균일하게 훑어 순간 비균일( $2|\mu|$, 예: 50/60rpm에서 25%)이 **자전평균으로
  거의 상쇄**된다. 시간평균 edge/center MRR비는 50/60rpm에서 겨우 1.00391(0.39%).
- **압력항**: 멤브레인 존압 분포 + **리테이너링/엣지효과**가 수 %급 비균일을 만든다 →
  **실측 WIWNU의 주범은 압력분포**. 재현(§5)에서 속도단독 0.195% vs 엣지압+30% 14.1%로
  약 70배 차이를 정량 확인(대조).

이 판단은 Preston이 $P\cdot V$ **곱**이라는 점에서 구조적으로 강화된다: 속도가 균일해지는
$\omega_w=\omega_p$ 조건에서 MRR 반경 프로파일은 순수하게 $P(r)$을 따른다(preston.py §3 검증과 정합).

## 3. 압력 반경분포 — 멤브레인 존압과 엣지효과

**(a) 멤브레인 다중존(zoned) 능동제어.** 현대 캐리어 헤드는 웨이퍼 뒷면을 동심
다중존으로 나눠 반경별 down-force를 독립 제어한다([[cmp-tool-architecture]], AMAT
멀티존 특허 US6558232/US6966822 "multi-pressure zone loading for improved edge and
annular zone material removal control", uspto 공개). 이것이 반경 MRR 프로파일을 직접
튜닝하는 1차 손잡이다.

**(b) 엣지효과 — 리테이너링과 패드 굽힘.** 웨이퍼 엣지에서 패드가 웨이퍼-링 사이
gap을 따라 굽으면서 **국소 압력집중**이 생긴다. 고전 **플랫펀치(flat punch)** 접촉해는
강체펀치 가장자리에서 압력이 $p(r)\propto 1/\sqrt{1-(r/R_w)^2}$ 로 **발산(특이점)**하는데,
CMP에서는 이 특이성을 리테이너링이 웨이퍼 바깥 패드를 선(先)가압해 완화한다
(escholarship.org, J. Luo & D. Dornfeld, "Wafer-Scale CMP Modeling of With-in Wafer
Non-Uniformity" — UC 공개 챕터. PDF 바이너리라 본문 **미검증**, 검색스니펫으로
"flat punch model ... pressure increases sharply at the wafer edge, so a retaining ring
can be put around the wafer to adjust the pressure distribution" 확인).

**(c) 굽힘/탄성 기반 wafer-scale 압력해.** 강체펀치 대신 웨이퍼·패드의 탄성변형을
넣으면 엣지 압력이 유한해지고 gap 크기·패드 영률·링압에 따라 엣지가 **더 빠르거나 더
느리게** 폴리싱됨:
- Fu & Chandra (2001), "A model for wafer scale variation of removal rate in CMP based on
  **elastic** pad deformation," *J. Electron. Mater.* **30**, 400–408 (Springer, 초록만 확인,
  본문 유료 **미검증**): 웨이퍼 곡률·연마조건에 따라 계면압력이 크게 변함 → 해석적 압력
  프로파일을 Preston식에 넣어 MRR 예측·실측 대조.
- Fu & Chandra (2002), viscoelastic 확장, *J. Electron. Mater.* (Springer, 초록만 확인).
- Boning 그룹, "CMP at the Wafer Edge — Modeling the Interaction between Wafer Edge
  Geometry and Polish Performance," *MRS Proc.* **867**, W5.1 (2004): gap·패드강성·웨이퍼/링
  압력이 엣지 수 mm의 fast/slow를 결정, edge roll-off(웨이퍼 초기형상 편차)와 결합.
  "uniformity improves when the gap is maximized or eliminated, ring pressure ≈ carrier
  pressure, and pad/wafer relative velocity is high"(검색스니펫 확인, 본문 **미검증**).
- Winkler 탄성기초 근사 $q(x)=K\,u(x)$(국소압력 = 국소 패드압축) — 반경별 $P(r)$을
  패드압축 $u(r)$의 선형함수로 잡는 가장 단순한 모델(검색스니펫으로 형태 확인).

→ **엣지 보정 손잡이**: (1) 링압을 캐리어압에 맞춤, (2) 웨이퍼-링 gap 최소화, (3) 엣지존
멤브레인 압력 하향. 세 가지가 edge roll-off/edge-fast를 상쇄하는 실무 레버다.

## 4. 슬러리 분포 — 왜 v0에서 2차 항인가

슬러리 유동/체류시간의 반경 비균일(중앙 결핍, 엣지 과잉)도 반경별 화학·입자공급을 통해
WIWNU에 기여하나, Preston v0에서는 이 효과가 $K_p$ 안에 lump되어 있고([[preston-luo-dornfeld-mrr]] §1)
반경별로 $K_p(r)$을 분해하려면 슬러리 막두께·유동해석(slurry-chemist 영역)과
입도분포 활성화(Luo-Dornfeld형 $P^{1/2}$)가 선행돼야 한다. 따라서 **v0는 슬러리 항을
$K_p$ 상수로 두고 압력·속도 결합에 집중**하며, 슬러리 반경분포는 Tier2로 유보한다
(Lv2-1에서 확정한 판단 계승).

## 5. Python 재현 — `sim/tier1_empirical/wiwnu.py` (preston.py/kinematics.py 재사용)

`preston.mrr_profile(..., pressure_fn=P(r))`에 반경 압력 콜러블을 넘겨 MRR(r)을 얻고,
half-range·σ·3σ WIWNU를 산출. self-test **5/5 PASS**(2026-09-05 실행):

1. **지표 산술 재현/대조**: 선형 $P(r)=P_c+(P_e-P_c)(r/R_w)$, $R_s{=}1$(V균일)에서 면적가중
   평균의 해석해 $\overline P = P_c+\tfrac23(P_e-P_c)$, half-range $=(P_e-P_c)/(2\overline P)$.
   → 수치 18.7488% vs **문헌값(해석해)** 18.7500%, 상대오차 $6.2\times10^{-5}$(이산화·r=0
   처리 잔차). 지표 코드 정확성 **검증**.
2. **구조적 WIWNU=0**: 균일압력 + $R_s{=}1$ → half-range $<10^{-9}$% (preston.py §3과 정합).
3. **압력 지배 대조(검증)**: 속도만(균일P, 50/60rpm) half-range **0.195%** vs 압력만(엣지압
   +30% 집중, $R_s{=}1$) **14.11%** → 약 70배. §2 "압력이 주범" 정량 재확인.
4. **멤브레인 존압 민감도**: 3존 헤드에서 엣지존 압력 $-10/0/+10$%p → half-range
   $5.15/0.00/4.86$% (균일세팅에서 최소, 물리와 일치). **엣지존 +1%p당 ΔWIWNU ≈ 0.49%p**
   — 존압 제어의 민감도 오더 제시(합성예시, 절대값은 압력 프로파일 형상 가정에 종속 **미검증**).
5. **곱 구조 확인**: 엣지압 집중에 $R_s{\ne}1$을 얹어도 WIWNU 이동 0.210%p(≈속도단독 규모)
   → $P\cdot V$ 곱에서 속도 기여가 압력 기여(14%)에 미세 중첩됨을 정성 확인.

**한계/미검증**: §3의 압력 프로파일(플랫펀치형 $P{=}P_0[1+A(r/R_w)^n]$, zoned)은 형상만
문헌 근거이고 계수 $A,n$은 예시값이다. 실제 엣지 압력집중의 정량형은 웨이퍼/패드 영률·
두께·gap의 탄성/굽힘 FEM(Fu-Chandra, Boning 계열)을 풀어야 하며 본 v0는 그 결과를
반경 프로파일로 **주입**받는 프레임만 제공한다(1차 FEM 계산 아님).

## 6. 공정통합 관점 종합

- WIWNU v0는 "MRR(r)=Kp·P(r)·V(r) + WIWNU 지표"로 완성. 남은 자유도는 **$P(r)$의
  물리적 결정**뿐 → pad-mechanic(엣지 굽힘/접촉, [[hertz-gw-contact-mechanics]]),
  equipment(멤브레인 존압/링압 [[cmp-tool-architecture]])와의 결합 지점이 명확해졌다.
- 지표는 정의 의존적이므로 시뮬레이터 출력은 half-range·σ·3σ 병기가 원칙.
- 다음(Lv3-1 dishing/erosion)은 이 웨이퍼 스케일 위에 **패턴/밀도 스케일** WIWNU를 얹는다.

## 7. 자기시험
→ [[../../agents/process-integrator/EXAMS.md]] Lv2-2 문항 참조.
