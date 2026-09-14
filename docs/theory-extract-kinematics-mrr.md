# FabSim 운동학·제거율·시간적분 계열 — 지배방정식 및 출처 추출

> 코드 독스트링/구현에서 **실제 확인된 식만** 옮김. 추정·보완 없음.
> 검증: `kinematics.py`, `preston.py` self-test 실행 결과 전부 PASS (본 문서 하단 수치 인용).

---

## 1. `sim/tier1_empirical/kinematics.py` — 회전식(rotary) 폴리셔 운동학

**목적:** 웨이퍼-패드 상대속도 분포 V(r,θ)를 계산 — Preston 식의 V 공급원.

**지배방정식** (웨이퍼 중심 좌표계, y축은 O_w→O_p 반대방향):

```
v_x = -(ω_w - ω_p) * y
v_y =  (ω_w - ω_p) * x - ω_p * r_cc
|v| = sqrt(v_x^2 + v_y^2)
```

동등한 극좌표 표현:

```
|v| = ω_p * r_cc * sqrt( (r*μ)^2 + 2*r*μ*cos(θ) + 1 )
μ   = (R_w / r_cc) * (1 - Rs),   Rs = ω_w / ω_p,   r = β/R_w (무차원 반경)
```

비균일도 해석해:
```
(max - min)/v_ref = 2*|μ|,   v_ref = ω_p * r_cc     (|μ| <= 1)
```

핵심 귀결: ω_w = ω_p → v_x=0, v_y = -ω_p·r_cc → **|v| = ω_p·r_cc (웨이퍼 전면 균일)**.

**기호/단위**

| 기호 | 의미 | 단위 |
|---|---|---|
| ω_w | 헤드(웨이퍼) 각속도 | rad/s |
| ω_p | 플래튼(패드) 각속도 | rad/s |
| r_cc | 두 회전축 간 거리 | m |
| R_w | 웨이퍼 반경 | m |
| x, y | 웨이퍼 중심 기준 좌표 | m |
| θ | 웨이퍼 좌표계 방위각 | rad |
| Rs | 속도비 ω_w/ω_p | - |
| μ | 운동학 수 (속도 비균일도 척도) | - |
| \|v\| | 국소 상대속도 크기 | m/s |

단위 변환: `RPM = 2π/60`, `rpm_to_rads(rpm) = rpm * 2π/60`.

**유도 경로:** (rpm_w, rpm_p) → rpm_to_rads → (ω_w, ω_p) → relative_velocity(x,y,ω_w,ω_p,r_cc) → |v|(r,θ) → speed_stats(mean/std/nu_ref/nu_range/cv/μ) 및 preston_mrr_profile.

**출처**
- Lai, MIT PhD thesis, 2001 — Eq. 2.10/2.11 (Cartesian 상대속도), Eq. 2.12 (ω_w=ω_p 균일성), Eq. 2.5 (θ평균=시간평균 등방성 논거)
- Hasni et al., 2026, JJMIE — Eq. 3 (극좌표 표현)
- 지식노트: `knowledge/physics/cmp-kinematics-rotary.md`, `knowledge/equipment/cmp-tool-architecture.md`

**가정·한계 (독스트링 명시)**
- ω_w, ω_p는 같은 부호(동일 방향 회전) 가정.
- 웨이퍼 자전으로 반경 r의 점이 θ 전체를 균일히 훑는다고 보아 θ평균 = 시간평균.
- ⚠️ 문헌 모순 정직 보고: JJMIE(2026)가 보고한 ±2.4% 속도 범위는 같은 논문 Eq.(3)에 조건을 대입하면 ±9.2%가 나와 약 4배 불일치. **본 모듈은 Lai(MIT) 유도식을 정본으로 채택하고 JJMIE 보고수치는 채택하지 않음.**

---

## 2. `sim/tier1_empirical/preston.py` — Preston MRR

**목적:** CMP 공정변수(P, V) → 재료제거율 MRR.

**지배방정식**
```
MRR = Kp * P * V                              (Preston, 1927)
MRR(r) = Kp * P(r) * <|v(r,θ)|>_θ             (반경별 시간평균)
MRR_wafer = 면적가중(r dr dθ) 평균 of Kp*P*|v|
mrr_to_nm_per_min: MRR[nm/min] = MRR[m/s] * 1e9 * 60
```

**기호/단위**

| 기호 | 의미 | 단위 |
|---|---|---|
| Kp | Preston 계수 (재료·슬러리·화학 lump 상수) | m²/N |
| P | 국소 압력 | Pa |
| V = \|v\| | 국소 상대속도 | m/s |
| MRR | 국소 재료제거율 | m/s (→ nm/min 변환) |

Kp 오더: ~1e-13 ~ 1e-12 (SiO2/콜로이달실리카), 독스트링에 **\*미검증, 오더만 채택\*** 명시.

**유도 경로:** (rpm_w, rpm_p, r_cc, R_w) →[kinematics] V(r,θ) → θ평균 → ×P(r) ×Kp → MRR(r) → 면적가중 평균 → wafer_avg_mrr → nm/min.
`pressure_fn(r)`을 주면 압력의 반경의존성 반영(기본은 균일 스칼라).

**출처**
- Preston, 1927 (MRR = Kp·P·V)
- Lai 2001 Eq. 2.5 (θ평균 = 시간평균 논거)
- Luo & Dornfeld (2001) 형 확장 `dh/dt = C(P)·P^(1/2)·V` — **Tier2로 유보**(GW 접촉모델 성숙 후 구현)
- 지식노트: `knowledge/cmp/preston-luo-dornfeld-mrr.md`
- 오더체크 대조군: 일반 산화막 CMP 50~1000+ nm/min (jeez-semicon.com 슬러리 가이드), STI 대표 254.05 nm/min = 2540.5 Å/min (ACS Langmuir 2026 pre-irradiation 연구 baseline), Kp 오더 출처 novasolver.jp 공학계산기 FAQ (\*미검증\*)

**가정·한계**
- v0는 균일압력 가정(존별 압력분포는 Lv2-2 wiwnu.py에서 결합).
- Kp는 재료조합별 **캘리브레이션 대상이지 이 모듈이 예측하는 항이 아님**을 명시.
- 압력균일 v0에서는 WIWNU=0 — 즉 모델 구조 자체가 "WIWNU의 원인은 압력분포"라는 결론을 내포.

**검증 수치(실행 확인):** P 2배→MRR 2배(오차<1e-9), V 2배→MRR 2배, Rs=1에서 반경 프로파일 편차 0.00e+00, Rs=50/60에서 edge/center = 1.00391, P=20.7 kPa·Rs=1·Kp=1e-13에서 156.1 nm/min.

---

## 3. ⭐ RPM → 상대속도 V → MRR 경로 추적 (면접 핵심)

1. **입력:** platen RPM(rpm_p), head RPM(rpm_w), 축간거리 r_cc[m], 웨이퍼 반경 R_w[m].
2. **각속도 변환:** ω = rpm × 2π/60 [rad/s].
3. **국소 상대속도(Lai Eq.2.11):** 웨이퍼 위 점 (x,y)=(r cosθ, r sinθ)에서
   `v_x = -(ω_w-ω_p)·y`, `v_y = (ω_w-ω_p)·x - ω_p·r_cc`, `V = sqrt(v_x²+v_y²)`.
   → 즉 V는 **두 RPM의 차(ω_w-ω_p)가 반경 r에 곱해지는 항**과, **플래튼 RPM × 축간거리(ω_p·r_cc)라는 반경 무관 기저항**의 벡터합이다.
4. **시간평균:** 웨이퍼 자전으로 θ가 균일 주사되므로 `<V(r)>_θ = (1/2π)∮V dθ`.
5. **Preston 대입:** `MRR(r) = Kp·P(r)·<V(r)>_θ`.
6. **웨이퍼 평균:** 면적가중(w ∝ r) 평균 → wafer_avg_mrr → ×6e10 → nm/min.
7. **시간적분:** 두께 = MRR × t (process_time.py).

**정량적 함의 (코드로 검증됨)**
- Rs = ω_w/ω_p = 1이면 (ω_w-ω_p)=0 → V = ω_p·r_cc, 전면 완전균일. 예: 60/60 rpm, r_cc=200 mm → V = 1.256637 m/s, std = 0.
- Rs ≠ 1이면 속도 비균일도 = 2|μ|, μ=(R_w/r_cc)(1-Rs). 50/60 rpm·R_w=150 mm·r_cc=200 mm → μ=0.125 → 순간 범위 25.0%.
- 하지만 **θ(시간)평균을 취하면 이 25%가 대부분 상쇄**되어, 반경별 시간평균 MRR의 edge/center 비는 1.00391 (≈0.4%)에 불과.
  → "운동학적 RPM 불일치는 edge-fast 경향을 만들지만 자전평균으로 거의 상쇄되며, WIWNU의 지배 인자는 압력분포"가 FabSim의 구조적 결론(wiwnu.py 검증 3번: 속도만 <0.3% vs 압력만 수 %급).

---

## 4. `sim/tier1_empirical/process_time.py` — 시간 적분

**목적:** 정상상태 Preston MRR 프로파일 → 제거두께 / 엔드포인트 시간.

**지배방정식**
```
removed_thickness(r, t) = MRR(r) * t
endpoint_time = target_thickness / MRR_ref
WIWNU[%] = (max - min)/mean * 100
```

| 기호 | 의미 | 단위 |
|---|---|---|
| t | 폴리싱 시간 | s |
| MRR(r) | 반경별 제거율 | m/s |
| target_thickness | 목표 제거두께 | m |

**유도 경로:** preston.mrr_profile → (rs, mrr) → ×t → 제거두께(r) → wiwnu_percent; 또는 목표두께 ÷ 평균 MRR → 엔드포인트 시간.

**출처:** `knowledge/cmp/preston-luo-dornfeld-mrr.md` (새 물리 없음, preston.py의 정상상태 MRR을 시간에 대해 선형적분).

**가정·한계 (명시)**
- **새 물리 가정 없음** — MRR 정상상태 가정하 단순 선형 시간적분.
- **유량(flow rate)은 명시적으로 제외** — 슬러리 물질전달/화학 근거 노트가 아직 없어서. 향후 별도 구현.
- 어떤 MRR을 엔드포인트 기준으로 쓸지는 호출부 책임(함수는 나눗셈만 수행).

---

## 5. `sim/tier1_empirical/wiwnu.py` — 압력×속도 결합 WIWNU

**목적:** 반경별 압력·속도 분포의 웨이퍼 스케일 결합 → 불균일도 지표.

**지배방정식**
```
MRR(r) = Kp * P(r) * <|v(r,θ)|>_θ

압력 프로파일:
  uniform:            P(r) = p0
  edge_concentration: P(r) = p0 * [1 + A*(r/R_w)^n]
  zoned:              P(r) = piecewise-constant (동심존별 압력)

WIWNU 지표 (면적가중 mean/std, 가중치 w ∝ r):
  half_range[%] = 100*(max-min)/(2*mean)
  sigma[%]      = 100*std/mean,  three_sigma = 3×
  edge_center   = MRR(R_w)/MRR(0)
```

| 기호 | 의미 | 단위 |
|---|---|---|
| p0 | 기준 멤브레인 압력 | Pa |
| A (amp) | 엣지 압력집중 진폭 (엣지가 (1+A)배) | - |
| n | 집중 지수(클수록 최외곽 국소화) | - |
| zone_edges / zone_press | 정규화 존 경계 / 존별 압력 | - / Pa |

**유도 경로:** (존압 세팅, 엣지집중 파라미터) → P(r/R_w) → preston.mrr_profile(pressure_fn) → MRR(r) → 면적가중 통계 → WIWNU 지표.

**출처**
- Boning 그룹, "A study of within-wafer non-uniformity metrics", IEEE ICMTS 1999 (WIWNU 지표에 **문헌상 표준 정의가 없다**는 지적 → 3가지 정의 모두 제공)
- Luo (eScholarship) / Boning, MRS 2004 — gap + 패드 굽힘으로 엣지 압력 급증 → edge-fast
- 지식노트: `knowledge/cmp/wiwnu-pressure-velocity-wafer-scale.md`, `preston-luo-dornfeld-mrr.md`, `physics/cmp-kinematics-rotary.md`

**가정·한계**
- 압력 프로파일은 **합성/문헌예시이며 FEM 1차계산이 아님** — 정성적 형상만 문헌 근거.
- 면적가중 시 r=0 특이점은 w[0]=0.25·w[1]로 회피(이산화 잔차 ~6e-5).
- 검증 결론: 속도 단독 <0.3% vs 압력 단독(엣지 +30%) 수 %급 → **압력 지배**. MRR이 곱 구조라 압력·속도 기여는 선형중첩이 아님.

---

## 6. `sim/tier1_empirical/pattern_density.py` — 패턴밀도 의존(dishing/erosion)

**목적:** 다이 스케일 패턴밀도 → 국소 제거율·step height·dishing.

**지배방정식**
```
1) 유효밀도:      rho_eff(x) = (w * rho_local)(x)     (w의 특성길이 = PL)
   가우시안 근사:  w(dx) = exp(-0.5*(dx/PL)^2) / Σw
2) 밀도기반 제거율 (MRS99 eq.1):  RR_up(x) = K / rho_eff(x)
3a) 비압축성 패드: h(t) = max(h0 - (K/rho)*t, 0),   소멸시각 t_c = rho*h0/K
    up 제거량: t<t_c → (K/rho)*t;  t>t_c → h0 + K*(t - t_c)
3b) 압축성 패드:   h(t) = h_c * exp(-(t - t_c)/tau)
    통합모델 접촉높이 (MRS99 eq.4): h1 = a1 + a2*exp(-rho/a3)
4) Overpolish (MRS99 Fig.13 removal-rate diagram):
    r_cu(d)  = RR_m * (1 - d/dmax)
    r_ox(d)  = RR_ox/(1 - rho_m) * (1 + b*d)
    정상상태: d_ss = (RR_m - A) / (RR_m/dmax + A*b),  A = RR_ox/(1-rho_m)
```

| 기호 | 의미 | 단위 |
|---|---|---|
| rho_local / rho_eff | 국소 / 유효 패턴밀도 | - (0~1) |
| PL | planarization length | 길이 (예제는 mm) |
| K | blanket 제거율 (= Kp·P·V) | Å/min (예제) |
| h0 / h_c | 초기 / 접촉시점 step height | Å |
| t_c | 국소 평탄화(접촉) 시각 | min |
| tau | 압축성 패드 step 감쇠 시상수 | min |
| a1,a2,a3 | 접촉높이 모델 계수 | Å, Å, - |
| d, dmax | dishing, 최대 dishing | Å |
| RR_m / RR_ox | 금속(Cu) / 산화막 제거율 | Å/min |
| rho_m | 금속 패턴밀도 | - |
| b | oxide rate의 dishing 민감계수 | 1/Å |

**유도 경로:** (rho_local(x), PL) → effective_density → rho_eff(x) → K/rho_eff → RR_up(x); (K, h0) → t_c → step height 시계열; (RR_m, RR_ox, rho_m, dmax, b) → d_ss.

**출처**
- Boning et al., MRS Spring 1999, "Pattern Dependent Modeling for CMP Optimization and Control" — eq.1, eq.2, eq.4, Fig.13
- Stine et al., IEEE TSM 1998
- Ouma, PhD thesis 1999 (물리적 elliptic 커널)
- Grillaert (비압축성 패드), Burke/Tseng (압축성 패드), Smith (통합모델)
- 지식노트: `knowledge/cmp/pattern-dependent-dishing-erosion.md`

**가정·한계**
- Ouma의 물리적 커널은 탄성패드 굽힘에서 유도한 **타원형(elliptic)**인데 여기서는 **정규화 가우시안 근사**를 씀 — 정확한 elliptic 적분형(MRS99 eq.2)은 재현하지 않음, 노트에 **미검증 표기**.
- 경계는 edge 패딩(유한 die 근사).

---

## 7. `sim/tier1_empirical/wiwnu_pattern_combined.py` — 웨이퍼×다이 스케일 브리지

**목적:** pattern_density의 상수 K 자리에 반경 의존 blanket rate K(r)을 대입해 2D 결합 제거율 맵 생성.

**지배방정식**
```
K(r) = MRR_radial(r) = Kp * P(r) * <|v(r,θ)|>_θ     (wiwnu.mrr_radial → np.interp 보간)
RR(r, x) = K(r) / rho_eff(x)

결합 지표(반경축은 r 면적가중, 다이축은 균일가중):
  sigma_pct = 100*std/mean
  대수적 항등: CV_comb^2 = CV_r^2 + CV_x^2 + CV_r^2*CV_x^2 >= max(CV_r^2, CV_x^2)
```

| 기호 | 의미 | 단위 |
|---|---|---|
| r | 절대 웨이퍼 반경 | m |
| x | 다이 내부 위치 | mm |
| K(r) | 반경별 blanket MRR | m/s |
| RR(r,x) | 결합 제거율 | m/s |

**유도 경로:** (RPM, r_cc, R_w, Kp, P(r)) → K(r); (rho_local(x), PL) → rho_eff(x); 둘의 외적 나눗셈 → RR(r,x).

**출처:** 상위 모듈 상속 — wiwnu.py(Preston+운동학), pattern_density.py(Boning MRS99 eq.1). 새 문헌 도입 없음.

**가정·한계 (독스트링 명시, 미검증 표기)**
- 웨이퍼 위 **어느 반경의 다이든 내부 rho_eff(x)가 동일**하다고 가정(엣지 다이 절단·회전 효과 없음).
- K(r)과 rho_eff(x)는 **분리가능(separable)** — 반경-패턴 교차항(엣지에서만 패턴 영향 증폭 같은 비선형 결합) 없음.
- 반경축(m)과 다이축(mm)은 물리적으로 다른 스케일이므로 섞지 않고 각자 축 유지.
- half_range_pct는 max/min 두 점에만 의존해 **대수적 하한 보장이 없음** → assert 대상 아님, 참고용만.

---

## 8. `sim/integration/spatiotemporal_removal.py` — 시공간 조립 레이어

**목적:** RR(r,x) × t → thickness(r,x,t).

**지배방정식**
```
thickness(r, x, t) = RR(r, x) * t = [K(r) / rho_eff(x)] * t
endpoint_time(r,x) = target_thickness / RR(r,x)
CV[%] = 100*std/mean   (RR과 thickness는 스칼라 t배 차이 → CV는 시간 불변)
```

**유도 경로:** combined_removal_map → RR(r,x) →(process_time.removed_thickness)→ thickness 필드; 셀별 RR → endpoint_time.

**출처:** `knowledge/cmp/luo-dornfeld-integrated-cmp-framework.md` — **Luo & Dornfeld 2003 리뷰**("Preston식이 3-스케일을 잇는 인터페이스", §4-5, Fig.6 통합 프레임워크).

**가정·한계 (설계 원칙 그대로)**
1. 기존 5개 tier1/tier2 모듈 **1바이트도 수정 안 함**(순수 import).
2. **새 물리 가정 추가 없음** — 조립(assembly)만.
3. GW/Preston-Kp 물리적 분해 연결은 이번 스코프 밖(Kp가 함수형이 되면 kp=상수 시그니처 self-test 회귀 위험 → Lv4 유보). 이 모듈의 kp는 preston.py와 동일한 상수.

---

## 9. `sim/integration/spatiotemporal_removal_physical_kp.py` — GW 기반 물리적 Kp 확장

**목적:** lump 상수 Kp를 GW 접촉모델의 기하량으로 분해해 반경별 Kp_eff(r)로 대체(선택적 확장).

**지배방정식**
```
GW-link 미시모델:   MRR = alpha_removal * n_contacts(P) * V
유효 Preston 계수:  Kp_eff(r) := alpha_removal * n_contacts(P(r)) / P(r)
  → Kp_eff(r)*P(r)*V(r) = alpha_removal*n_contacts(P(r))*V(r)   (항등식 재배열, 새 가정 아님)

캘리브레이션:  alpha_removal = Kp_lit * P_ref / n_contacts(P_ref)
               (= MRR_ref / (n_ref * V_ref))
MRR(r) = <Kp_eff(r) * P(r) * |v(r,θ)|>_θ
RR(r,x) = K_eff(r) / rho_eff(x),   thickness = RR * t
```

또한 gw_preston_link.py의 물리적 해석:
```
Kp_physical := alpha_removal * (dn/dP)      (n(P)가 P에 선형이면 Preston과 정합)
```

| 기호 | 의미 | 단위 |
|---|---|---|
| alpha_removal | 접촉점 1개가 단위 상대속도당 깎는 부피율 | m³/s per contact per (m/s) |
| n_contacts(P) | GW 접촉점 수 (순수 기하/역학량, 화학 무관) | 개 |
| Kp_eff(r) | 반경별 유효 Preston 계수 | m²/N |
| P_ref, V_ref, kp_lit | 캘리브레이션 지점 | 20.7 kPa, 0.8 m/s, 1e-13 m²/N |

**유도 경로:** (P_ref, V_ref, kp_lit) → calibrate_alpha_removal → alpha_removal; P(r) → n_contacts_at(P) → Kp_eff(r) → preston.local_mrr → MRR(r) → K_eff(r) → /rho_eff(x) → ×t.

**출처**
- Greenwood-Williamson(GW) 접촉모델 — `knowledge/materials/gw-nominal-vs-local-pressure.md`, `knowledge/materials/hertz-gw-contact-mechanics.md`
- 캘리브레이션 기준값: STI 254.05 nm/min @ P=20.7 kPa (ACS Langmuir 2026 baseline, preston.py §2 인용), Kp=1e-13 m²/N
- V_ref=0.8 m/s는 preston.py 독스트링의 STI 표준조건 V≈0.6~1.0 m/s의 **중간값 채택(명시)**

**가정·한계 (정직 보고 포함)**
- alpha_removal은 **화학 종속 lump 상수라 모델이 예측하는 항이 아님** — 검증 대상은 "GW 기하모델만으로 Preston의 P-선형성이 설명되는가"이지 Kp 절대값 예측이 아님.
- 기존 파일 무수정 원칙 때문에 반경 루프를 로컬 재구현(코드 중복 감수), 단 Preston 대수는 preston.local_mrr 재사용.
- **정량적 실익 제한 정직 보고:** 14~96 kPa 구간에서 n_contacts(P)가 거의 완벽히 선형(잔차<1e-6)이라 Kp_eff(r)이 상수 kp_lit에서 거의 안 벗어남 → 물리기반 vs 상수-Kp 두께필드 편차가 실무적으로 무시 가능(<0.01%). 의의는 **정성적/구조적**(Kp가 화학 lump가 아니라 GW 기하량으로 분해된다는 것).
- 기존 thickness_field(kp=상수)를 **대체하지 않고 나란히 제공**하는 선택적 확장.

---

## 10. `sim/tier2_physics/blanket_rate_transfer.py` — 블랭킷 순간/평균 rate 전이

**목적:** 60 s 평균 rate와 모델이 요구하는 순간 포화 rate a1의 괴리를 해소.

**지배방정식**
```
eq.3.51  AR(t)      = a1*t + a2*(exp(-t/tau) - 1)         [누적 제거량]
eq.3.52  r_avg(t)   = AR(t)/t                              [평균 rate]
eq.3.53  r_inst(t)  = a1 - (a2/tau)*exp(-t/tau)            [순간 rate]
```

| 기호 | 의미 | 단위 |
|---|---|---|
| AR(t) | 누적 제거량 | Å |
| a1 | 포화 순간속도 | Å/s |
| a2 | 초기 지연 크기 계수 | Å |
| tau | 시상수 | s |
| t | 폴리싱 시간 | s |

**유도 경로:** 관측 (times, removed) 쌍 → `fit_blanket_rate` 최소제곱(scipy curve_fit, 없으면 tau grid search + (a1,a2) 선형 lstsq) → (a1, a2, tau) → r_inst(t)/r_avg(t).

**출처:** **Tugbawa, 2002, MIT EECS PhD thesis** (dspace.mit.edu/handle/1721.1/8083), 표 3.3, eq.3.51-3.53. 지식노트 `knowledge/cmp/npw-ptw-transfer-rules-quantitative.md` §3, §6 verify (B).

**가정·한계**
- 순수 함수 라이브러리로 engine.py/models.py에 **미등록** — Recipe에 시간축(시계열 폴리시 진행) 스키마가 없어 조립 입력이 없기 때문.
- fit 초기값/그리드는 전달 데이터 스케일에서 산출 — **문헌값을 지어내 초기값으로 쓰지 않는다**.
- 최소 3개 (t, removed) 쌍 필요.

---

## 11. `sim/tier2_physics/recipe_conversion_factor.py` — 레시피 간 RR 변환계수

**목적:** 레시피 A→B 전환 시 제거율 변환계수 산출.

**지배방정식** (US20060116785A1 식(1))
```
F(X,Y,Z) = (1.223 - 0.605*exp(-(X-3.4)/2.117))
         * (1.085 - 0.302*exp(-(Y-80)/98.39))
         * (1.187 - 0.719*exp(-(Z-40)/66.304))

conversion_factor = F(recipe_to) / F(recipe_from)
```

| 기호 | 의미 | 단위 |
|---|---|---|
| X | 다운포스 | psi |
| Y | 슬러리 유량 | ml/min |
| Z | 패드(플래튼) 회전 | rpm |
| F | work function | - |

레시피 표(표 1): ILD (4.0 psi, 150 ml/min, 63 rpm), STI (4.2, 200, 63), IMD (4.6, 100, 108).

**유도 경로:** (다운포스, 유량, 플래튼 rpm) → work_function F → 두 레시피 F 비 → 변환계수. 특허 실시예: ILD 기준 STI 1.12, IMD 1.41.

**출처:** **US20060116785A1**, "Method of predicting CMP removal rate for CMP process in a CMP process tool" (공개 2006-06-01, 출원 2004-11-29, 등록판 **US7333875B2**, Taiwan Semiconductor Manufacturing Co.), 식(1)·표 1·표 2·청구항 6. 지식노트 `knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md` §2.2, §6 verify (A).

**가정·한계**
- 특허 원문 표기 `e^{-(Y-80/98.39)}`는 **괄호 누락 오기로 판단** — `(Y-80)/98.39`로 읽어야 표 2의 변환계수(STI 1.12, IMD 1.41)가 재현됨(코드 주석 명시).
- 청구항 6은 변환계수가 "substantially 0.5~2" 범위라고 명시하나, 다른 조합에서는 벗어날 수 있어 **예외를 던지지 않음**(범위 확인은 호출측 책임).
- engine 미등록 — Recipe 스키마에 "레시피 간 전이" 개념 자체가 없음(docs/ARCHITECTURE.md §4 스키마 부채).

---

## 12. `sim/tier2_physics/npw_ptw_effective_pressure.py` — 패턴밀도별 유효압력비

**목적:** 실측 표 기반 유효압력/인가압력 비 조회 + Boning 1/ρ 모델과의 정면 비교.

**지배방정식 / 관계식**
```
table_ratio(density, P_applied, T) = P_effective / P_applied     (Sorooshian 실측표 조회)
inverse_density_ratio(rho) = 1/rho                                (RR_up = K/rho_eff가 함의하는 증폭비)
mean_ratio_at_density(rho) = 8개 표값(4온도 × 2압력) 평균
```

| 기호 | 의미 | 단위 |
|---|---|---|
| density (ρ) | 패턴밀도 (0.10 / 0.50 / 0.90) | - |
| P_applied | 인가압력 (3, 7) | psi |
| P_effective | 유효압력 | psi |
| temp_C | 온도 (10/23/35/45) | °C |

**유도 경로:** (밀도, 인가압력, 온도) → 표 정확조회 → 유효압력비; 별도로 1/ρ 모델값과 **나란히 비교**(합치지 않음).

**출처:** **Sorooshian (2005) PhD dissertation** §3.3, 표 3.3(10°C)/3.4(23°C)/3.5(35°C)/3.6(45°C), 요약 문장 §3.3.3. 지식노트 `knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md` §4, §6 verify (B)(B').

**핵심 결론(노트 §4, 코드 self-test로 검증)**
- 밀도 10/50/90%에서 유효압력/인가압력 비는 각각 **약 2.2 / 1.7 / 1.3배**(논문 요약값), 표 8조건 평균으로는 2.67 / 1.79 / 1.27.
- 1/ρ 모델이 함의하는 값은 10 / 2 / 1.11배 → **저밀도(10%)에서 1/ρ 모델이 실측을 4배 이상 과대예측**.
- 온도 단조성: 45°C 비율 > 10°C 비율이 전 조합에서 성립.

**가정·한계**
- 표에 없는 (density, pressure, temp) 조합은 **조용한 보간·외삽 금지 → ValueError**(다른 tier2_physics 모듈 공통 관례).
- 새로운 문헌 숫자 도입 없음 — 지식노트 §6 verify 블록의 표·로직을 순수함수로 옮긴 것.

---

## 부록: 출처 문헌 일람

| 문헌 | 사용 모듈 | 제공 내용 |
|---|---|---|
| Preston (1927) | preston.py | MRR = Kp·P·V |
| Lai, MIT PhD thesis (2001) | kinematics.py, preston.py | Eq.2.5/2.10/2.11/2.12 상대속도장 |
| Hasni et al., JJMIE (2026) | kinematics.py | Eq.3 극좌표 상대속도 (수치는 미채택) |
| Luo & Dornfeld (2001) | preston.py (유보) | dh/dt = C(P)·P^(1/2)·V |
| Luo & Dornfeld (2003) 리뷰 | spatiotemporal_removal.py | 3-스케일 통합 프레임워크(§4-5, Fig.6) |
| Boning et al., MRS Spring 1999 | pattern_density.py | RR_up=K/ρ_eff (eq.1), h1 (eq.4), Fig.13 |
| Stine et al., IEEE TSM (1998) | pattern_density.py | 밀도모델 |
| Ouma PhD (1999) | pattern_density.py | elliptic 가중커널(가우시안으로 근사) |
| Boning 그룹, IEEE ICMTS 1999 | wiwnu.py | WIWNU 지표 표준 부재 지적 |
| Luo(eScholarship)/Boning MRS 2004 | wiwnu.py | 엣지 압력집중 → edge-fast |
| Greenwood-Williamson 접촉모델 | gw_preston_link, physical_kp | n_contacts(P), Kp 분해 |
| Tugbawa, MIT EECS PhD (2002) | blanket_rate_transfer.py | eq.3.51-3.53, 표 3.3 |
| US20060116785A1 / US7333875B2 (TSMC) | recipe_conversion_factor.py | work function 식(1), 표1·2, 청구항6 |
| Sorooshian PhD (2005) | npw_ptw_effective_pressure.py | 표 3.3-3.6 유효압력 실측 |
| ACS Langmuir (2026) | preston.py, gw_preston_link.py | STI baseline 254.05 nm/min |
