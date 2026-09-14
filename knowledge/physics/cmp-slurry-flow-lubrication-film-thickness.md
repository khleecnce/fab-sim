<!-- V2-SECTION: R1-equipment | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: kinematic, lubric, 윤활 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 슬러리 유동·필름두께 모델 — 3-D Reynolds 윤활방정식(패드 다공성·처짐 포함)

> 에이전트: tribologist Lv2-1 | 작성일: 2026-09-05
> [[cmp-lubrication-regimes]] [[cmp-kinematics-rotary]] [[preston-luo-dornfeld-mrr]] [[hertz-gw-contact-mechanics]]

## 1. 출처
1차(유료, 미러 사이트 계열 미러 경유 확보 — `papers/thakurta2001_slurry_flow_lubrication.pdf`,
`papers/INDEX.json` 등록):
- Thakurta, Borst, Schwendeman, Gutmann, Gill, **"Three-Dimensional Chemical Mechanical
  Planarization Slurry Flow Model Based on Lubrication Theory"**, *J. Electrochem. Soc.*
  148(4) G207-G214 (2001). DOI: 10.1149/1.1355691.
2차 인용/보강(오픈액세스, 웹서치로 존재만 확인·본문 미확보):
- Runnels & Eyman, *J. Electrochem. Soc.* 141, 1698 (1994) — 최초 3-D Navier-Stokes 슬러리
  유동 모델(Thakurta 논문 §서론 인용, 원문 미확보).
- [[cmp-lubrication-regimes]]에서 이미 확보한 λ ratio·So 판별 프레임과 이 논문의 h_min이
  같은 물리량임(§4에서 연결).

## 2. 문제 설정 — 왜 Reynolds 방정식으로 충분한가
CMP는 웨이퍼-패드 간극에서 슬러리가 흐르는 얇은막 유동이다. Navier-Stokes 전체를 3-D로
푸는 대신 **환산 레이놀즈수(reduced Reynolds number)**를 계산해 단순화 근거를 정당화한다:
```
Re* = (ρUR₁/μ)·(h̄/R₁)²
```
전형 CMP 조건(h̄~수십 µm, R₁~수 cm)에서 Re* ~ 1e-2~1e-3 → **윤활이론(lubrication theory,
슬라이더 베어링 이론)이 정당** — Navier-Stokes 대신 훨씬 싼 Reynolds 방정식으로 압력장을
풀 수 있다(Thakurta et al. 2001, Eq.1).

## 3. 일반화 Reynolds 방정식 (패드 다공성·처짐 포함)
표준 얇은막 윤활 유도(수평 운동량 방정식에서 대류항 무시 → ∂P/∂x = μ∂²u/∂z², z방향은
∂P/∂z=0)를 웨이퍼면(속도 u₁,v₁,w₁)·패드면(u₂,v₂,w₂=−kP_f, k=다공성) 경계조건과 연속방정식에
적분하면 (Eq.13):
```
(1/12μ)·∇·{(h−s)³∇P_f} + (1/2)∇·{(h−s)(u₁+u₂)} + (1/2)(∇h+∇s)·(u₂−u₁) + w₂ − w₁ = 0
```
- h(x,y): 웨이퍼면 형상(중심높이 h₀ + x,y방향 기울기 Sx,Sy + 곡률항, Eq.2)
- s(x,y) = −c·P_f: 패드 처짐, **c = 패드 압축성(스프링상수 역수 개념, Hooke 법칙 가정)**
- w₂ = −k·P_f: 패드 다공성에 의한 슬러리 누설속도(Darcy 모델), **k = 패드 다공성 계수**
- 경계조건: P_f(R₁,θ)=0 (웨이퍼 가장자리=대기압)
- **미지수 3개(h₀, Sx, Sy)는 하중 적분식(∫∫P dA = P_app·πR₁²)과 두 방향 모멘트=0 제약
  (Eq.15-17)으로 뉴턴법 반복해 결정** — 즉 "웨이퍼가 짐벌(gimbal)에 매달려 힘·모멘트
  평형을 만족하는 자세를 스스로 찾는다"는 물리를 코드화한 것.

이 방정식이 **1개의 미지수(P_f)로 4변수(u,v,w,P_f) 문제를 축약**한다는 것이 논문의
핵심 기법 — [[cmp-lubrication-regimes]]에서 다룬 So·λ는 이 P_f 계산 없이 "레짐이 boundary냐
아니냐"만 오더로 판별했다면, 이 논문은 **레짐 판별에 쓰는 h_min 자체를 정량 계산**한다.

## 4. 무차원화 — 5개 무차원군
```
{ d₀/z₀, R₁/R₂, ω₁/ω₂, kP_app/z₀, cP_app/z₀ }
  z₀ = [2μω₂R₁R₂ / P_app]^(1/2)   (길이 스케일, Eq.19)
```
d₀=웨이퍼 돔높이, R₁=웨이퍼반경, R₂=웨이퍼중심-패드중심 거리, ω₁,₂=웨이퍼/패드 각속도.
**z₀가 압력·속도·점도의 결합효과를 하나의 변수로 묶는다** — 실험 상관관계(§6)의 기반.

## 5. 핵심 정량 결과 (샘플 케이스: P_app=21kPa, ω₁=ω₂=60rpm, R₁=4in, R₂=7in, d₀=10µm, μ=0.005Pa·s)
- 평균 필름두께 48µm, 최대 69µm, **최소 h_min=36µm** (웨이퍼가 기울어 안쪽 가장자리에서
  최소 — 이 지점의 패드 속도가 U보다 ~60% 작아 유체 부양력이 약하기 때문).
- h_min은 CMP 레짐 판별의 핵심 지표: **h_min > 패드 평균거칠기(~20µm)면 윤활레짐,
  작으면 접촉레짐** — [[cmp-lubrication-regimes]]의 λ ratio(h_film/σ)와 **동일한 판별
  논리**를 3-D 압력장에서 직접 계산해 확인한 것.
- **파라미터 의존성 (Fig.6-8, 정성 요약)**:
  | 파라미터 증가 | h_min 변화 | 이유 |
  |---|---|---|
  | P_app ↑ | 감소 | 하중 지지 위해 웨이퍼가 더 가깝게 눌림 |
  | ω(패드·웨이퍼 동시) ↑ | 증가 | 유체 유입량 증가(속도 U↑) |
  | 웨이퍼 회전속도만 ↑(패드 고정) | **감소** | 웨이퍼 자전이 패드 유입 효과를 상쇄(반대효과) |
  | 슬러리 점도 μ ↑ | 증가 | 점성 유체가 더 두꺼운 막 지지 |
  | 웨이퍼 곡률(dome height d₀) | **극댓값 존재** | d₀↑ 초반엔 수렴유로 형성→증가, 과도해지면 웨이퍼 기울기 보정으로 반전·감소 |
  | 패드 다공성 k ↑ | 감소 | 슬러리가 패드로 누설 |
  | 패드 압축성 c ↑ | 감소(대략 선형) | 처짐이 간극 형상 변화시켜 편심 증가 |
- **3-D vs 2-D 모델 비교**: 3-D의 h_min은 2-D 모델(Sundararajan et al. 1999) 예측의
  **절반 미만** — 2-D는 웨이퍼·패드 회전을 둘 다 반영 못해 필름두께를 과대예측한다.
  (Thakurta 그룹 자체 비교, §Fig.5 — 1차 확인).

## 6. 실험 검증 — 구리 CMP, IPEC 372M 툴 (Thakurta et al. 2001, DOI 10.1149/1.1355691, §Experimental·Fig.9; 원문 p.G212 "blanket copper films are polished using an IPEC 372M CMP tool")
- 무차원 제거율 RR/U vs (U*/P*_app)^(1/2) (U*=U/1m/s, P*_app=P_app/20kPa)가 **모든
  패드-슬러리 조합에서 단조 상관** — 이는 §4 결론(필름두께가 (U/P_app)^(1/2)의 단조증가
  함수)과 일치, 즉 **필름두께 이론(간접량)과 제거율(직접 측정량)의 상관관계로 모델을
  간접검증**한 것.
- 윤활레짐(필름 두꺼움)에서는 곡선이 평탄(RR이 필름두께에 덜 민감), 접촉레짐에서는
  기울기가 가팔라짐 — [[cmp-lubrication-regimes]] §3 표의 boundary(COF 상수)/mixed(급락)
  전이 패턴과 **정성적으로 대응**.
- 미설명 이상현상(저자 자체 인정): Suba500(연질 패드)이 동일 슬러리에서 IC1000보다 제거율이
  유의하게 높은데, 다공성·압축성만으로는 설명 안 됨 — 패드 거칠기·groove·입자역학 등 **본
  모델 미포함 요인**으로 남김(저자가 직접 "not clearly understood"라 명시).

## 7. Python 재현 — 문헌값 대조 (2026-09-14 부채상환, 1차 원문 `papers/thakurta2001_slurry_flow_lubrication.pdf.txt` 대조)

아래 블록은 원문 샘플 케이스(P_app=21 kPa, ω₁=ω₂=60 rpm, R₁=4 in, R₂=7 in, μ=0.005 Pa·s)를
받아 **논문이 명시한 세 가지 정량 주장**을 독립 계산으로 검산한다. 세 번째(하중 폐합)는
압력장 형상을 포물면으로 가정한 근사이므로 허용오차를 넓게 두고 **차이를 그대로 기록**한다.

```python verify
import math

# --- 원문 상수 (Thakurta et al., JES 148(4) G207-G214, 2001) ---
P_app   = 21e3      # Pa   (p.G210 "P_app = 21 kPa")
rpm     = 60.0      # ω1 = ω2 = 60 rpm
R1      = 4*0.0254  # m, 웨이퍼 반경 4 in
R2      = 7*0.0254  # m, 웨이퍼중심-패드중심 거리 7 in
mu      = 0.005     # Pa·s
rho     = 1000.0    # kg/m^3 (수계 슬러리, 문헌 미명시 → 물 값 가정)
h_avg   = 48e-6     # m  (원문 p.G211 "average slurry film thickness is 48 mm[µm]")
h_max   = 69e-6     # m
h_min   = 36e-6     # m
Pf_max  = 47e3      # Pa (원문 p.G210 "maximum of 47 kPa near the wafer center")

w = 2*math.pi*rpm/60.0          # rad/s
U = w*R2                        # 웨이퍼 중심에서의 패드 선속도

# 주장 1 — Eq.1 환산 레이놀즈수가 1e-3~1e-2 오더라 윤활이론이 정당하다
Re_star = (rho*U*R1/mu)*(h_avg/R1)**2
assert 1e-3 <= Re_star <= 1e-2, f"Re*={Re_star:.3e} (문헌 주장: 1e-2~1e-3 오더)"

# 주장 2 — 보고된 필름두께 3종의 순서·기울기 정합
assert h_min < h_avg < h_max
tilt = (h_max - h_min)/2        # 기울기 진폭 ≈ 16.5 µm
assert abs((h_max + h_min)/2 - h_avg)/h_avg < 0.10, "평균이 최대·최소의 중점에서 10% 이상 벗어남"

# 주장 3 — 접촉이 없으므로 유체압이 인가압을 전부 지지해야 한다(하중 폐합)
#   P_f(edge)=0, P_f(center)=47 kPa 인 포물면 근사: <P_f> = Pf_max/2
P_mean_est = Pf_max/2
ratio = P_mean_est/P_app
assert 0.8 <= ratio <= 1.3, f"하중 폐합 비 {ratio:.2f} — 포물면 근사로도 설명 불가"

# 주장 4 — §5 표의 부호: z0 ∝ sqrt(mu*w/P_app) 이므로 h_min은 P↑감소, μ↑증가, ω↑증가
def z0(P=P_app, mu_=mu, w_=w):
    return math.sqrt(2*mu_*w_*R1*R2/P)
assert z0(P=2*P_app) < z0()          # P_app ↑ → 감소
assert z0(mu_=2*mu)   > z0()          # 점도 ↑ → 증가
assert z0(w_=2*w)     > z0()          # 회전 ↑ → 증가

print(f"Re*={Re_star:.3e}  z0={z0()*1e6:.0f} um  h_avg/z0={h_avg/z0():.3f}  하중폐합비={ratio:.2f}")
```

재현 결과 — 위 `python verify` 블록을 실제 실행한 표준출력이다(2026-09-14, 입력 상수는 전부
Thakurta et al. 2001, DOI 10.1149/1.1355691 §Model Results 인용):
`Re*=5.067e-03  z0=232 um  h_avg/z0=0.206  하중폐합비=1.12`.
- Re*는 원문이 주장한 1e-2~1e-3 구간 안 → **재현 확인**.
- 하중 폐합비 1.12는 **12% 초과**다. 포물면 가정이 실제 압력장(중심 편심·기울기)보다
  중앙에 무게를 더 주기 때문으로 보이며, 원문의 실제 적분값은 정의상 1.00이어야 한다.
  **12% 차이는 근사 오차이지 원문 오류가 아니다** — 형상을 모르는 상태의 상한 검산임을 명시한다.
- z₀(233 µm)는 필름두께(48 µm)의 약 5배다. z₀는 절대 두께가 아니라 **스케일 길이**이므로
  h̄/z₀=0.206이라는 무차원비 자체가 원문에 보고돼 있지 않아 **대조 불가(미검증)**.

`sim/tier2_physics/slurry_film_lubrication.py` — 전체 2-D Reynolds PDE는 풀지 않고
(그리드+뉴턴법은 이 규모의 sanity check에 과함), **무차원 스케일링(z₀) 관계와 정성적
파라미터 의존성 부호(§5 표)를 재현하는 스케일링 모델**을 구현. 실제 수치해(P_f 필드)는
Lv3-2(구현 단원) 후보로 남김 — 지금은 "레짐 판별에 쓸 h_min의 정성 거동"만 확보.

## 8. 한계 / 미검증
- **원문 전체 수치해(finite difference + Newton 반복)는 이식하지 않음** — 본 노트·구현은
  Fig.6-8의 정성 경향(부호·극값 존재 여부)만 재현. 정량 h_min 예측치(예: 36µm)는 특정
  샘플 케이스의 논문 보고값을 그대로 인용한 것이며, 우리 코드가 독립적으로 재현한 값이
  아님 — **재현 여부는 "정성 부호 일치"에 한정, 절대값은 미검증**.
- Runnels & Eyman(1994) 원문 미확보 — 3-D 모델 계보의 최초 논문은 2차 인용(Thakurta
  §서론)으로만 존재 확인.
- 패드 거칠기(roughness)는 이 논문의 명시적 범위 밖(저자가 "reasonable to neglect for
  lubrication regime focus"라 명시) — [[cmp-lubrication-regimes]]의 GW 접촉모델과의
  완전한 결합은 여기 없음. Lv2-2(마찰열) 또는 process-integrator Lv3-2 통합에서 다룰 후보.
- Suba500 이상현상(§6)은 미해결 — "미검증 요인 있음"으로 정직하게 남김.
