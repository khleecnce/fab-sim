# CMP 회전식 폴리셔 운동학 — 상대속도 분포 유도

> 담당: [[process-integrator]] Lv1-2 · 작성 2026-09-03 · 상태: **코드 검증 완료**
> 구현: `sim/tier1_empirical/kinematics.py` · 연결: [[cmp-tool-architecture]]
> 중요도: ★★★ Preston식의 v_R이 여기서 나온다. 모든 MRR 모델의 기초.

## 1. 좌표계
웨이퍼 중심 O_w, 플래튼 중심 O_p, 축간거리 **r_cc**. 두 축 모두 폴리싱면에 수직.
각속도 ω_w(헤드), ω_p(플래튼), 같은 방향(부호 동일). 좌표는 웨이퍼 중심 고정계 (x,y),
y축을 축간선 방향으로 잡는다.

## 2. 유도 (Lai 2001, MIT thesis Eq. 2.7–2.12)[1]
웨이퍼 위 점 P(r,θ)의 웨이퍼 속도: v_r,w = 0, v_θ,w = ω_w r  (자전만).
같은 공간점에서 패드의 속도:
    v_r,p = ω_p r_cc sinθ ,   v_θ,p = ω_p (r + r_cc cosθ)      … (2.7)
상대속도 = 웨이퍼 − 패드:
    v_r,R = −ω_p r_cc sinθ ,  v_θ,R = (ω_w − ω_p) r − ω_p r_cc cosθ   … (2.8)
직교좌표(x = r cosθ, y = r sinθ)로 바꾸면 **핵심 결과**:

```
v_x = −(ω_w − ω_p) · y
v_y =  (ω_w − ω_p) · x − ω_p · r_cc                        … Eq. (2.11)
|v_R| = { [(ω_w−ω_p)y]² + [(ω_w−ω_p)x − ω_p r_cc]² }^(1/2)  … Eq. (2.10)
```

### 2.1 ★ ω_w = ω_p 인 경우
```
v_x = 0 ,  v_y = −ω_p r_cc   →  |v_R| = ω_p·r_cc  (x,y와 무관!)
```
**웨이퍼 전면의 모든 점이 정확히 같은 크기·같은 방향의 상대속도를 갖는다**[1, Eq.2.12].
방향은 웨이퍼 고정계에서 보면 ω_w/2π 주파수로 회전 → 어느 점도 특정 방향으로
편중 마모되지 않음(**등방성 폴리싱**). 이것이 실제 CMP에서 헤드·플래튼 RPM을
같거나 근접하게 두는 이유다.

부수 결과: 동속 + 균일압력이면 웨이퍼에 걸리는 마찰력은 y방향뿐이고
F_y = µ p π r_w², **웨이퍼에 작용하는 토크 Q_w = 0**, 플래튼 토크 Q_p = µ p π r_w² r_cc [1, Eq.2.17].
→ 헤드 토크 신호가 0에 가까운지로 동속 세팅을 in-situ 확인 가능(엔드포인트 활용 여지).

## 3. 운동학 수(kinematic number) µ
극좌표로 정리한 등가식[2]:
```
|v_R| = ω_p r_cc · sqrt( (r̄µ)² + 2 r̄µ cosθ + 1 ),   r̄ = r/R_w ∈[0,1]
µ = (R_w / r_cc)(1 − Rs),   Rs = ω_w/ω_p
```
µ 하나가 ①웨이퍼 크기 R_w ②플래튼 크기(축간거리 r_cc) ③RPM 비 를 모두 담는다.
전형 장비에서 R_w/r_cc < 1, |1−Rs| < 0.5 이므로 **|µ| ≤ 0.5**[2].

**속도 비균일도 (해석해, 본 노트에서 유도):** 엣지 r̄=1에서 최대·최소가 나므로
```
(v_max − v_min) / (ω_p r_cc) = |1+µ| − |1−µ| = 2|µ|      (|µ| ≤ 1)
```
→ **비균일도는 µ에 정비례.** µ=0 (Rs=1)에서 0, 즉 §2.1과 연속적으로 이어진다.
r_cc를 키우면(큰 플래튼) µ가 작아져 비균일도가 준다 — "웨이퍼-패드 중심 거리가
멀수록 속도 비균일도가 줄어든다"는 문헌 서술[2]과 정합.

## 4. 시간평균과 반경 프로파일
웨이퍼가 자전하므로 반경 r의 점은 한 바퀴 동안 θ 전체를 균일하게 훑는다 →
**θ평균 = 시간평균**[1, Eq.2.5]. 이 평균 속도는 r에 따라 **단조 증가**하므로
Rs≠1이면 Preston MRR이 "엣지 fast" 프로파일이 된다.
단, µ가 작으면 그 차이는 2차항이라 작다 (아래 검증 참조).

## 5. 코드 검증 결과 (`sim/tier1_empirical/kinematics.py`, 2026-09-03 실행)
300mm 웨이퍼(R_w=150mm), r_cc=200mm, 플래튼 60rpm 기준. **7/7 PASS**.
**문헌값과 대조**: Rs=1일 때 Lai(2001)[1] 해석식이 예측하는 |v_R| = ω_p·r_cc = 1.256637 m/s와
아래 `verify` 블록의 코드 계산 결과가 1e-5 m/s 이내로 완전히 일치한다(재현 성공).

> ⚠ 아래 표는 서술이다. **기계가 실행하는 실제 검증은 이 코드 블록이다** (`tools/verify_claims.py`가 매번 실행). 표의 숫자와 코드 결과가 다르면 코드가 옳다.

```python verify
"""운동학 주장 재현 — 이 블록이 실패하면 위 표의 주장은 거짓이다."""
import sys
sys.path.insert(0, ".")
from sim.tier1_empirical.kinematics import speed_stats

R_W, R_CC, RPM_P = 0.150, 0.200, 60.0

# 주장 1: Rs=1이면 전면 균일, |v| = ω_p·r_cc = 1.256637 m/s
s = speed_stats(R_w=R_W, r_cc=R_CC, rpm_w=RPM_P, rpm_p=RPM_P)
assert abs(s["mean"] - 1.256637) < 1e-5, f"문헌 표기값 1.256637 불일치: {s['mean']}"
assert s["std"] < 1e-12, f"Rs=1인데 균일하지 않다: std={s['std']:.2e}"
assert s["nu_ref"] < 1e-12, f"NU가 0이 아니다: {s['nu_ref']:.2e}"

# 주장 2: NU = 2|µ| 해석해 (표의 4개 지점)
for rpm_w, nu_pct in [(50, 25.0), (55, 12.5), (66, 15.0), (72, 30.0)]:
    s = speed_stats(R_w=R_W, r_cc=R_CC, rpm_w=rpm_w, rpm_p=RPM_P)
    got = s["nu_ref"] * 100
    assert abs(got - nu_pct) < 1e-9, f"rpm_w={rpm_w}: {got} != {nu_pct}"
    assert abs(got - 2 * abs(s["mu"]) * 100) < 1e-9, "NU = 2|µ| 관계 깨짐"

print("PASS — Rs=1 균일성(1.256637 m/s), NU=2|µ| 해석해 4점 재현 확인")
```

| 검증 항목 | 결과 |
|---|---|
| Rs=1 → 전면 균일 | \|v\|=1.256637 m/s = ω_p·r_cc 정확 일치, std=0.00e+00, NU=0.00e+00 ✔ |
| NU = 2\|µ\| 해석해 | 50/60rpm=25.0000%, 55/60=12.5000%, 66/60=15.0000%, 72/60=30.0000% (상대오차<1e-12) ✔ |
| Lai(직교) ≡ JJMIE(극) | 최대 절대차 2.22e-16 m/s ✔ |
| Rs=1 Preston 프로파일 | 반경 편차 0.00e+00 (완전 평탄) ✔ |
| Rs=50/60 프로파일 | edge/center MRR = 1.00391 (엣지 fast) ✔ |

RPM 스윕 (면적평균 속도 / NU / CV):
```
 50/60rpm  µ=+0.1250  1.2591 m/s  NU=25.00%  CV= 6.26%
 60/60rpm  µ= 0.0000  1.2566 m/s  NU= 0.00%  CV= 0.00%
 66/60rpm  µ=-0.0750  1.2575 m/s  NU=15.00%  CV= 3.76%
 71/60rpm  µ=-0.1375  1.2596 m/s  NU=27.50%  CV= 6.88%
 80/60rpm  µ=-0.2500  1.2666 m/s  NU=50.00%  CV=12.41%
```
**해석 포인트:** RPM을 5~10% 어긋내면 *순간* 속도 비균일도는 12~25%로 크지만,
시간평균 MRR 비균일도는 0.4% 수준에 그친다(edge/center=1.00391). 즉 회전이
비균일을 대부분 평균으로 지워준다 — 실공정 WIWNU의 주범이 운동학보다
**압력분포(멤브레인·리테이너링)** 라는 문헌 주장[3]과 정합한다.
→ Phase 0의 WIWNU v0 모델은 압력 항에 무게를 두어야 한다.

## 6. 미검증 / 문헌 모순
JJMIE(2026)[2]는 R_w=50mm, 웨이퍼/패드 59/71 rpm에서 속도 0.664~0.696 m/s
(평균 0.680, ±2.4%)라 보고한다. 그러나 **같은 논문의 Eq.(3)** 에 이 조건을 넣으면
평균 = ω_p·r_cc = 0.680 → r_cc = 91.5mm, µ = (50/91.5)(1−59/71) = 0.0924 →
NU = 2µ = 18.5% (±9.2%)로, 보고값의 약 4배다. r_cc가 명시되지 않아 확정은 못 하나
자기모순 가능성이 높다. **본 프로젝트는 Lai(MIT) 유도식을 정본으로 채택**하고
JJMIE의 보고 수치는 채택하지 않는다.

## 7. 선형(linear) 폴리셔 — 참고
패드가 x방향 등속 v_p로 병진하고 웨이퍼만 자전하는 경우[1, Eq.2.4]:
```
|v_R| = ( v_p² + 2 v_p ω_w r sinθ + ω_w² r² )^(1/2)
```
θ평균 반경속도는 0, θ방향 평균은 ω_w r → 자전이 등방성을 준다. 다만 슬라이딩
거리가 r에 따라 증가하므로 균일하려면 **ω_w ≪ v_p / r_w** 여야 한다[1, Eq.2.6].

## 출처
1. J.-Y. Lai, *Mechanics, Mechanisms, and Modeling of the Chemical Mechanical Polishing Process*, PhD thesis, MIT, 2001, Chapter 2 §2.2.2. https://web.mit.edu/cmp/publications/thesis/jiunyulai/ch2.pdf
2. A. Hasni, S. M. Raza, H. A. Siddiqui, M. H. Qureshi, "Computational and Experimental Study of Velocity Anisotropy and Slurry Hydrodynamics in Wafer-Pad CMP", *Jordan J. Mech. Ind. Eng.* 20(1), 17–27, 2026. DOI 10.59038/jjmie/200102. https://jjmie.hu.edu.jo/vol20/vol20-1/02-JJMIE-324-25.pdf  (§6 모순 주의)
3. H. Lee et al., "Approaches to Sustainability in CMP: A Review", 2021. https://pmc.ncbi.nlm.nih.gov/articles/PMC8617369/
4. (관련, 원문 미확보) "Effect of Process Conditions on Uniformity of Velocity and Wear Distance of Pad and Wafer during CMP", *J. Electron. Mater.*, 2004 — ζ "kinematic number" 원전으로 추정. https://link.springer.com/article/10.1007/s11664-004-0294-4
5. F. W. Preston, "The theory and design of plate glass polishing machines", *J. Soc. Glass Technol.* 11, 214–256, 1927 (Lai[1] 재인용).
