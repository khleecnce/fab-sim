<!-- V2-SECTION: R1-equipment | 분배완료 2026-09-08 | 근거: endpoint, epd, friction, 마찰, 토크 | 정본: ARCHITECTURE-V2.md §3 -->
# 마찰계수(COF) 실시간 모니터링과 마찰기반 종점검출(friction-based EPD)

> 에이전트: tribologist Lv3-1 | 작성일: 2026-09-06
> [[tribology-friction-wear-stribeck]] [[cmp-lubrication-regimes]] [[frictional-heating-temperature-arrhenius-coupling]] [[preston-luo-dornfeld-mrr]] [[hertz-gw-contact-mechanics]] [[../cmp/wafer-metrology-thickness-methods]]

## 1. 왜 마찰신호가 종점을 아는가 — 문제 정의
CMP의 종점(endpoint, EP)은 "제거해야 할 막(Cu·W·barrier)이 웨이퍼 전면에서 막 벗겨져 아래 막이
드러나는 순간"이다. Cu 다마신은 Cu → barrier(Ta/TiN/Ti) → 유전체(oxide/ILD) 스택을 순차로 뚫는데,
과연마(over-polish)는 dishing·erosion([[preston-luo-dornfeld-mrr]] 계열의 패턴의존 결함)을 키우고
under-polish는 잔막(residue)을 남긴다. 종점을 실시간으로 잡아야 한다.

**핵심 관찰:** 서로 다른 재료는 패드·슬러리에 대한 **마찰계수(COF)가 다르다.** 막이 벗겨져 다른 재료가
노출되면 계면 마찰이 계단·기울기로 변하고, 이 변화가 플래튼/캐리어의 **토크·모터전류·전단력**에
그대로 실린다. 즉 마찰신호는 "지금 무엇을 갈고 있는가"의 대리변수다. [[cmp-lubrication-regimes]] §6에서
"COF 실시간 모니터링으로 레짐을 판별한다"고 예고한 것을 이 단원에서 종점검출로 심화한다.

## 2. COF 정의와 마찰신호 사슬: 전단력 → 토크 → 모터전류
CMP에서 마찰계수는 계면의 **전단력(마찰/drag force) / 수직력(down force)** 로 정의·측정한다:
```
COF = F_shear / F_normal          F_normal = P · A_wafer  (P=명목압력, A=웨이퍼면적)
F_shear = μ · F_normal = μ · P · A         (Amontons, [[tribology-friction-wear-stribeck]] §2)
```
이 전단력이 회전 플래튼에 거는 **저항 토크**는 (웨이퍼 중심이 플래튼축에서 반경 r_c)
```
τ_wafer ≈ F_shear · r_c
모터전류  I = τ / K_t          (DC/BLDC 모터, K_t=토크상수 — 장비상수, 절대값 미검증)
모터 마찰동력  P_motor,fric = τ_wafer · ω = F_shear · V = μ·P·V·A = q·A = Q_f
```
마지막 항등이 중요하다: **플래튼 모터가 웨이퍼 마찰을 이기며 쓰는 기계동력은 곧 계면에서 소산되는
마찰발열 Q_f 와 같다**(둘 다 μPVA) — [[frictional-heating-temperature-arrhenius-coupling]] §2의 q=μPV와
같은 물리량의 두 얼굴이다. 그래서 모터전류(∝토크∝전단력)는 μ의 변화를 실시간으로 반영한다.
단, 실제 모터전류에는 베어링·리테이너링·패드 컨디셔너 등 **큰 baseline**이 겹쳐 있어, 종점신호는
그 위에 얹힌 **작은 계단**으로 나타난다(§4의 소신호 문제).

## 3. 마찰기반 EPD의 원리 — 재료전이에서 μ가 바뀐다
- **모터전류/토크법(motor-current EPD):** 플래튼(또는 스핀들) 모터전류가 갈고 있는 표면의 COF를 추종한다.
  저COF 금속을 갈다가 금속이 다 벗겨지고 고COF(또는 저COF) 하지막이 드러나면 전류가 계단으로 변한다 —
  이 전이시점이 종점. 광학창(window)이 필요 없고 웨이퍼 전면 평균신호라 저가·범용이다.
- **전단력/힘센서법(shear-force EPD):** 캐리어에 3축 스트레인게이지 힘센서를 달아 F_shear·F_normal을
  직접 재고 COF=F_s/F_n을 산출, Cu→Ta, Ta→SiO₂ 전이의 마찰변화를 검출(300/450 mm 적용 가능,
  scientific.net AMR.53-54.125 요지). 모터전류법보다 잡음 대비가 낫지만 센서 통합비용이 든다.
- **신호처리:** 원신호는 유동·거칠기 요동으로 잡음이 크다. 이동평균·wavelet 분해(db4)·SPRT(순차확률비검정)
  등으로 계단/기울기를 추출한다(Li 2017; SPRT-on-wavelet-COF 보고). 잡음억제와 검출지연은 트레이드오프(§4).

**정량 근거 — Li, Lu, Luo (2017, OA):** Cu(~4200 nm)/Ti barrier(~350 nm)/TEOS(~2000 nm) 스택에서
barrier→유전체 전이 시 플래튼 **모터전력이 약 30,300 W → 28,670 W (Δ≈1630 W, ~30 s에 걸쳐)** 감소하는
계단을 관측해 종점검출 타당성을 입증(Li, Lu, Luo, *Micromachines* 8(6) 177, 2017,
doi.org/10.3390/mi8060177, PMC6190379, MDPI CC BY, PMC 전문 확인). 샘플링 12.15 Hz, 121점 이동평균 사용.

## 4. 소신호·검출지연 트레이드오프 (정량)
종점신호(Δ≈1630 W)는 baseline(≈30,300 W)의 **약 5%**에 불과한 소신호다. 잡음 속에서 이를 잡으려면
이동평균 창을 넓혀야 하는데, 창이 넓을수록 **검출이 지연**되어 과연마가 는다. Li 2017은
121점 이동평균(half-span N=60), 12.15 Hz에서 지연 T=N/R을 **약 5초 미만**으로, 이때 TEOS 제거율
229 nm/min 기준 **과연마 20 nm 미만**으로 산정했다 — §6에서 재현한다. 샘플링을 40 Hz로 올리면
같은 창에서 지연이 준다(Li 2017). 이것이 마찰기반 EPD 설계의 핵심 저울: **잡음억제 ↔ 검출지연 ↔ 과연마.**

## 5. COF·전단력·모터전류 상관과 레짐 의존성
**Headley et al. (2019, OA):** 12개 Stribeck⁺ 곡선(블랭킷 CVD-W 8 + SiO₂ 4)에서 1000 Hz로
전단력·수직력·플래튼모터전류(PMC)를 수집해 상관을 구했다: **PMC vs 전단력 r=0.955 (R²=0.916)**,
**PMC vs COF r=0.758 (R²=0.608)**. COF 상관이 낮은 것은 boundary 윤활이 지배한 **5개 케이스에서
COF가 pseudo-Sommerfeld 수에 대해 거의 안 변했기 때문**(Headley, Frank, Sampurno, Philipossian,
*ECS J. Solid State Sci. Technol.* 8(10) P634, 2019, doi.org/10.1149/2.0251910jss, OA). 후속 정상상태 논문은
1초 간격에선 PMC-전단력 일치율 ~64%, PMC-COF ~62%로 낮고 10초 이상 평균에서 개선됨을 보였다
(Headley et al., *ECS JSST* 9(4) 044003, 2020, doi.org/10.1149/2162-8777/ab8392, OA).
- **물리 해석(재현 포인트):** PMC는 토크=F_shear·r_c 로 **전단력의 직접 대리**라 상관이 매우 높지만(0.955),
  COF=F_shear/F_normal 은 수직력 정규화가 추가돼 산포가 늘어 상관이 낮아진다(0.758). 즉 모터전류는
  엄밀히는 "COF계"가 아니라 "전단력계"다.
- **레짐 연결:** COF가 Sommerfeld 수에 평탄한 5개 케이스는 [[tribology-friction-wear-stribeck]]의
  **boundary plateau**(μ가 높고 So에 무관한 구간)에 해당한다. boundary/mixed에서는 COF가 재료별로
  뚜렷이 다르므로 **마찰 EPD가 잘 먹지만**, 완전 hydrodynamic(hydroplaning)에서는 μ가 점성전단 지배로
  재료무관·저값이 되어 **마찰 대비가 사라져 EPD가 실패**한다. 마찰 EPD는 CMP가 boundary~mixed
  ([[cmp-lubrication-regimes]] §4의 ℓ_hd≪Ra 논증)에서 돌기에 의존한다.

## 6. Python 재현 & 문헌 대조
```python verify
import math
# (1) COF 정의: F_s = mu*F_n, F_n = P*A
psi = 6894.76
P = 3*psi                      # W CMP 전형 3 psi
A = math.pi*0.15**2            # 300mm 웨이퍼 [m^2]
V = 0.70                       # 상대 미끄럼속도 [m/s] (Lai 2001 thesis)
mu = 0.4                       # W CMP boundary COF (0.1~0.7 범위)
F_n = P*A; F_s = mu*F_n; COF = F_s/F_n
print(f"F_n={F_n:.0f} N, F_s={F_s:.0f} N, COF=F_s/F_n={COF:.2f}")
assert abs(COF-mu)<1e-9
assert 0.1 <= mu <= 0.7
assert 500 < F_n < 2000

# (2) 마찰전단력 -> 플래튼토크 -> 모터전류, 모터마찰동력 = F_s*V = mu*P*V*A = q*A = Q_f
r_c = 0.20; omega = V/r_c
tau_wafer = F_s*r_c
P_motor_fric = tau_wafer*omega
q = mu*P*V; Q_f = q*A
print(f"tau={tau_wafer:.1f} Nm, P_motor_fric={P_motor_fric:.0f} W, Q_f=q*A={Q_f:.0f} W")
assert abs(P_motor_fric - F_s*V) < 1e-6          # tau*omega == F_s*V (기하 항등)
assert abs(P_motor_fric - Q_f) < 1e-6            # 모터마찰동력 == 마찰발열 (Lv2-2 q=uPV와 동일)
assert 100 < Q_f < 1000                          # 수백 W (White 2003 200~300W와 동오더)
Kt = 0.5; I = tau_wafer/Kt                       # I=tau/K_t, K_t 장비상수(절대값 미검증)
assert I > 0

# (3) Li et al. 2017 (PMC6190379): 종점 모터전력 계단 + 소신호대비
P_base, P_after = 30300.0, 28670.0
dP = P_base - P_after; contrast = dP/P_base
print(f"Li2017: dP={dP:.0f} W, contrast={contrast*100:.1f}%")
assert abs(dP-1630)<1                            # 산술 재현
assert 0.03 < contrast < 0.08                    # ~5% 소신호(대신호 위 작은 계단)

# (4) Li 2017: 121점 이동평균(half-span 60), 12.15Hz -> 지연<5s; RR229nm/min -> 과연마<20nm
N_half, R_s = 60, 12.15
delay = N_half/R_s; RR = 229.0/60.0; over = delay*RR
print(f"delay={delay:.2f} s, over-removal={over:.1f} nm (RR=229 nm/min)")
assert delay < 5.0 and over < 20.0               # Li: 지연<5s, 과연마<20nm TEOS

# (5) Headley 2019 (DOI 10.1149/2.0251910jss): PMC vs SF r=0.955,R2=0.916 > PMC vs COF r=0.758,R2=0.608
r_SF, R2_SF = 0.955, 0.916
r_COF, R2_COF = 0.758, 0.608
print(f"Headley2019: r(PMC,SF)={r_SF} > r(PMC,COF)={r_COF}")
assert r_SF > r_COF and R2_SF > R2_COF           # PMC는 COF보다 전단력에 더 직결
assert abs(R2_SF - r_SF**2) < 0.02               # SF: R2~r^2 (0.912 vs 0.916)
# COF: avg(R2)=0.608 != avg(r)^2=0.575 -- 케이스별 평균이라 항등 아님(정직 기록)
assert R2_COF > r_COF**2 - 0.01
print("ALL PASS")
```
- **COF 정의·전단력:** 3 psi·300mm·V=0.70 m/s·μ=0.4에서 F_n≈1462 N, F_s≈585 N, COF=0.40으로 정의 항등 확인(COF 0.1~0.7 범위).
- **모터동력 항등:** 모터 마찰동력 P_motor,fric=τ·ω=F_s·V=μPVA=q·A=**409 W**로 Q_f와 정확히 일치, White 2003 마찰열 200~300 W와 동오더 재현.
- **Li 2017 종점계단(PMC6190379):** 모터전력 30,300→28,670 W, Δ=**1630 W(=baseline의 5.4%)** 산술 재현 — 대신호 위 소신호임을 확인.
- **Li 2017 지연/과연마(PMC6190379):** 121점 이동평균(N=60)·12.15 Hz → 지연 **4.94 s(<5 s)**, 229 nm/min에서 과연마 **18.8 nm(<20 nm)** 재현.
- **Headley 2019 상관:** PMC vs 전단력 r=**0.955**(R²=0.916) > PMC vs COF r=**0.758**(R²=0.608) — 모터전류가 COF보다 전단력의 직접대리임을 재현.

## 7. EPD 방법 비교 (마찰 vs 광학 vs 와전류 vs 음향)
출처: Lai (2001) MIT PhD thesis ch.6(공개, web.mit.edu/cmp) 및 위 리뷰·특허류 종합.

| 방법 | 감지량 | 강점 | 약점 |
|---|---|---|---|
| **마찰(모터전류/전단력)** | COF·전단력 변화 | 광학창 불필요, 저가, 범용, 금속 clear-up에 강함 | 웨이퍼전면 **평균값만**(공간분해 불가), 소신호·고잡음, 인접막 COF 유사 시 무력 |
| **광학(간섭/반사)** | 막두께·표면반사 | **국소(die-level)** 분해, 투명 유전체 두께 직접 | 광학창·정렬 필요, 불투명금속엔 반사법만, 패턴의존 |
| **와전류(eddy current)** | 도전막 두께 | 비접촉·무오염, 반복성 우수, 금속두께 직접 | 도전막 한정, 유전체 EP 불가 |
| **음향방출(AE)** | 접촉음향 | 재료 **경도차**만 있으면 마찰 유사해도 검출 | 정성적, 잡음 민감 |

- **마찰법의 근본한계(Lai 2001):** 마찰신호는 "웨이퍼 전면 평균"이라 within-wafer·die-level 불균일을
  못 본다 — 광학·와전류의 국소검출을 보완재로 함께 쓰는 **멀티센서**가 실무 추세. 또한 barrier(Ta/TaN)와
  하지 유전체의 COF가 비슷하면 Ta→oxide 전이신호가 약해, 모터전류법은 **Cu→barrier 전이를 잡고 정해진
  overpolish 시간을 더하는** 방식으로 운용한다.
- [[../cmp/wafer-metrology-thickness-methods]]의 오프라인 두께계측(ex-situ)과 대비되는 **in-situ** 축이 EPD다.

## 8. 한계 / 미검증 표기
- **모터전류-COF 절대변환 미검증:** I=τ/K_t의 토크상수 K_t, 웨이퍼중심 반경 r_c, 플래튼/캐리어 모터
  간 토크분배, baseline(베어링·링·컨디셔너) 크기는 모두 **장비 종속**이다 — 본 노트는 비례성·항등
  (P_motor,fric=μPVA=Q_f)만 재현했고 절대전류 예측은 하지 않았다.
- **재료별 COF 절대값 미확보:** Cu/Ta/oxide-패드 COF의 정량 실측표(슬러리·산화제 종속)를 1차로 확보하지
  못했다. 본 노트는 μ=0.4를 W CMP boundary 대표값(0.1~0.7 범위)으로 **가정**해 정의·오더만 검증했다 —
  전이방향(상승/하강)의 정량 대소는 **미검증**(슬러리 화학에 따라 뒤집힐 수 있음).
- **상관계수는 특정 툴/슬러리 값:** Headley 2019의 r=0.955/0.758은 APD-800 폴리셔·특정 W/ILD 조건의
  케이스평균이며, avg(R²)=0.608≠avg(r)²=0.575처럼 케이스평균이라 r²=R² 항등이 정확히 성립하지 않는다
  (정직 기록). 일반화는 미검증, 대소관계(전단력>COF 상관)만 신뢰.
- **Li 2017 조건 종속:** 1630 W·30 s·229 nm/min은 해당 툴/스택(Cu/Ti/TEOS)의 실측이며 다른 스택에선
  다르다 — 소신호(~5%)·지연-과연마 트레이드오프의 **오더·구조**만 일반화 가능.
- **1차 미확보 항목:** 3축 힘센서 EPD(scientific.net AMR.53-54.125)는 요지·초록만 확인(전문 미독).
