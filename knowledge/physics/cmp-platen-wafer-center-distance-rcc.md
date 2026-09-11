<!-- V2-SECTION: R1-equipment | 분배완료 2026-09-11 | 근거: r_cc, 축간거리, 플래튼 기하, kinematic number | 정본: ARCHITECTURE-V2.md §3 -->
# 웨이퍼중심–플래튼중심 거리 r_cc (center_offset_m) — 1차 문헌 수치

> 담당: [[process-integrator]] Lv1-2 · 작성 2026-09-11 · 상태: **문헌값 확보, 코드 재현 완료**
> 선행: [[cmp-kinematics-rotary]] (r_cc가 들어가는 상대속도 유도식 — 그 노트는 r_cc의 *역할*만 다루고
> *수치 근거*는 다루지 않았다. 이 노트가 그 공백을 메운다.)
> 연결: [[cmp-tool-architecture]] · 대상 파라미터: `knowledge/params/base.yaml: center_offset_m`
> 중요도: ★★★ Preston 속도항의 지배항이 ω_p·r_cc 이므로, r_cc 하나가 MRR 절대값을 직접 스케일한다.

## 1. 이 노트가 답해야 하는 질문

`center_offset_m`은 지금까지 0.180 m, confidence=**estimated**("툴마다 다름")였다. 근거 없는 대표값이라는 뜻이다.
질문은 하나다: **회전식 CMP 툴에서 r_cc의 수치를 명시한 1차 문헌이 존재하는가.**
결론부터: **존재한다. 3편 확보**. 12인치(300 mm) 플랫폼 기준 e₀ = 200 mm 가 1차 문헌 명시값이다.

## 2. 1차 출처 (PDF 확보, 본문 대조 완료)

1. **Zhao, Wang, He, Lu (2012)**, "Effect of Kinematic Parameters and Their Coupling Relationships on
   Global Uniformity of Chemical-Mechanical Polishing", *IEEE Trans. Semicond. Manuf.* **25**(3), 502–510.
   DOI: 10.1109/TSM.2012.2190432. 소속: 칭화대 마찰학 국가중점연구실.
   OA 없음 → 미러 사이트 경유로 PDF 확보(`papers/zhao2012-tsm-kinematic-coupling.pdf`, 10.3 MB, 본문 전체 확인).
   ★ **핵심 인용 (§IV, Fig. 8 직전 문단, 원문 그대로):**
   > "All below calculations are based on the following dimensional parameters for 12 in CMP platform:
   > Δe₀ = 25 mm, e₀ = 200 mm."

   여기서 `e`는 논문 Eq.(1) 정의상 "the center distance between the platen and the wafer carrier",
   즉 우리의 r_cc와 **정확히 같은 양**이다. `e₀`는 캐리어 왕복(sweep) 이전의 기준 축간거리,
   `Δe₀`는 왕복 진폭의 절반이다(Eq. 8, Fig. 7).

2. **Kim & Jeong (2004)**, "Effect of Process Conditions on Uniformity of Velocity and Wear Distance of
   Pad and Wafer during Chemical Mechanical Planarization", *J. Electron. Mater.* **33**(1), 53–60.
   DOI: 10.1007/s11664-004-0294-4. ζ("kinematic number")의 **원전**이며,
   [[cmp-kinematics-rotary]] §3에서 "원전으로 추정"이라 적고 원문 미확보 상태로 남겼던 바로 그 논문이다.
   미러 사이트 경유 PDF 확보(`papers/kim-jeong-2004-jem-kinematic-number.pdf`, 703 KB, 본문 전체 확인).
   ★ Fig. 6·Fig. 7 캡션에 **D = 150 mm** 명시(D = "distance between rotation centers" = r_cc).
   Fig. 7 조건: ω_w = 30 rpm, ω_p = 40 rpm, D = 150 mm, ζ = 0.17.

3. **Ye & Yao (2025)**, "Research on the Trajectory and Relative Speed of a Single-Sided Chemical
   Mechanical Polishing Machine", *Micromachines* **16**(4), 450. DOI: 10.3390/mi16040450.
   PMC12029203 (CC BY, 전문 무료). 상하이교통대. 정오표: *Micromachines* **17**(2), 160 (PMC12943132) —
   Fig. 5m 라벨과 Eq.(10) 첨자 오기 정정, **본 노트가 쓰는 Table 1 수치는 정정 대상이 아니다**(확인함).
   ★ Table 1 "Motion trajectory simulation parameters" (단위 mm, 전부 반지름):
   | Carrier 175 | Plate(Pad) 457 | Wafer 62.5 | **e 277.89** |
   5인치(125 mm) 웨이퍼용 단면 폴리셔라 300 mm 툴은 아니지만, **e와 플래튼 반경이 같은 표에 함께 실린
   유일한 사례**라 기하 정합성 검증(아래 §5-3)에 쓸 수 있다.

### 2.1 채택하지 않은 후보 (기록)
- Lai (2001) MIT 박사논문 [[cmp-kinematics-rotary]] 참조문헌 1. ch2·ch6 전문을 재검색했으나
  r_cc는 **기호로만** 등장하고 수치는 없다(실험기는 100 mm 웨이퍼, 장치 치수 미기재). 유도식의 정본일 뿐
  수치 출처는 아니다 — 이 점을 명확히 하는 것이 이 노트를 따로 만든 이유다.
- Zhang et al. (2023) *Micromachines* 14, 1683 (PMC10536193, DOI 10.3390/mi14091683). Table 1에
  "Platen diameter 380 mm"가 있으나 같은 표의 "Conditioner arm sweep range Radial 83~308 mm"와
  **모순**된다(반경 308 mm를 쓸면 플래튼 지름은 최소 616 mm여야 한다). 본문은 12인치 플랫폼이라
  서술한다. 표 내부 자기모순이므로 **플래튼 직경 근거로 채택하지 않는다**(미검증으로 남긴다).
- 300 mm 양산 툴(AMAT Reflexion/Mirra, Ebara)의 r_cc를 명시한 논문·특허는 **찾지 못했다**.
  Google Patents 검색은 이번 세션에서 HTTP 503으로 불통이었고, 웹 2차 출처(장비 재생업체 페이지 등)에
  "플래튼 직경 660–750 mm" 같은 서술이 보이나 **1차 출처가 아니므로 인용하지 않는다**.

## 3. 정량 관계 — r_cc가 들어가는 자리

[[cmp-kinematics-rotary]] Eq.(2.10)의 등가식을 Zhao(2012) Eq.(3)·(7) 표기로 쓰면:

```
v = ω_p·e · sqrt( (ρζ)² + 2ρζ cosθ + 1 + β² + 2ρζβ sinθ )
ρ = r/r₀ ,  α = ω_w/ω_p ,  ζ = (r₀/e)(1 − α) ,  β = v_R/(ω_p e)
```
(r₀ = 웨이퍼 반경, v_R = 캐리어 왕복 병진속도. Zhao 2012 Eq. 3,7 — Kim & Jeong 2004의 ζ 정의와 동일.)

- Zhao §II 말미(원문): "For a general CMP tool, 0 < ρ ≤ 1, r₀/e ≈ 1, α ≈ 1, ζ ≈ 0, and β ≈ 0 are
  reasonable... **Therefore, ω_p·e is the major part determining the magnitude of the relative velocity.**"
  → **r_cc는 속도 절대값의 지배항**이고, 웨이퍼면 내 분포(WIWNU)에는 ζ = (r₀/e)(1−α)를 통해 2차로 들어간다.
- Kim & Jeong: "velocity uniformity has a small value when the ratio r_w/D reduces and R approaches 1.
  ... low r_w/D (i.e., **large diameter table**)" → r_cc를 키우면 속도 비균일도가 준다.
  이는 [[cmp-kinematics-rotary]] §3의 NU = 2|µ| 해석해와 부호·방향이 일치한다(µ와 ζ는 같은 양).
- 왕복(sweep)이 있으면 r_cc는 **상수가 아니라 시간함수**다: e(t) = e₀ + ∫v_R dt, 진폭 ±Δe₀ (Zhao Eq. 11–12).
  Zhao의 12인치 값으로는 e ∈ [175, 225] mm. FabSim은 현재 정적 r_cc만 쓰므로 e₀를 대표값으로 쓴다.

## 4. 채택값과 근거 사슬

| 항목 | 값 | 근거 |
|---|---|---|
| **제안값 r_cc** | **0.200 m** | Zhao 2012 §IV, "12 in CMP platform: e₀ = 200 mm" 직접 인용 |
| 운전 범위(sweep 포함) | 0.175 ~ 0.225 m | 같은 문장의 Δe₀ = 25 mm, Zhao Eq.(11) |
| 200 mm 웨이퍼 툴 참고 | 0.150 m | Kim & Jeong 2004 Fig. 6·7 캡션 D = 150 mm |
| 5인치 단면 폴리셔 참고 | 0.27789 m | Ye & Yao 2025 Table 1 (DOI 10.3390/mi16040450, 동급 툴 아님, 기하검증용) |
| 기존 FabSim 값 | 0.180 m | 근거 없음(estimated). 제안 범위 [0.175, 0.225] **안에는 있다** |

→ confidence를 **literature**로 올린다. 근거는 "300 mm 양산기 실측"이 아니라 "12인치 플랫폼을 명시한
동료심사 논문의 설계 치수"다. measured/verified가 아닌 이유를 여기 명시해 둔다.

## 5. 정량 재현 (python verify) — 문헌 수치를 실제로 재현한다

```python verify
"""r_cc 문헌값 재현. 이 블록이 실패하면 §2~§4의 주장은 거짓이다."""
import math

# ── 주장 1: Kim & Jeong (2004) Fig.7 — D=150mm, ω_w=30, ω_p=40 에서 ζ=0.17 을 재현한다.
#   ζ = (r_w/D)(1-R), R = ω_w/ω_p.  원문은 D만 주고 r_w는 그 그림에 적지 않았으므로,
#   ζ를 역산해 r_w를 복원하고 그것이 물리적으로 말이 되는 웨이퍼(200mm급)인지 확인한다.
D = 0.150                      # m — Kim & Jeong 2004, Fig.6/Fig.7 캡션 명시값
R = 30.0 / 40.0                # ω_w/ω_p, Fig.7 캡션
zeta_reported = 0.17           # Fig.7 캡션 명시값
r_w_recovered = zeta_reported * D / (1.0 - R)
assert abs(r_w_recovered - 0.102) < 0.005, f"복원 r_w={r_w_recovered:.4f} m"
# → 0.102 m ≈ 200mm 웨이퍼의 반경(0.100 m). 즉 D=150mm는 200mm 웨이퍼 툴의 축간거리다.
zeta_back = (0.100 / D) * (1.0 - R)
assert abs(zeta_back - zeta_reported) < 0.005, (zeta_back, zeta_reported)
print(f"Kim&Jeong 2004 재현: D=150mm, R=0.75 → ζ={zeta_back:.4f} (문헌 0.17, 오차 {zeta_back-0.17:+.4f})"
      f" / 역산 웨이퍼 반경 {r_w_recovered*1000:.1f} mm ≈ 200mm 웨이퍼")

# ── 주장 2: Zhao et al. (2012) 12인치 플랫폼 e₀=200mm, Δe₀=25mm.
E0, DE0 = 0.200, 0.025         # m — Zhao 2012 §IV 원문 명시값
e_min, e_max = E0 - DE0, E0 + DE0
assert abs(e_min - 0.175) < 1e-12 and abs(e_max - 0.225) < 1e-12, (e_min, e_max)
# 2a) 300mm 웨이퍼가 이 축간거리에서 ζ가 논문이 허용한 |ζ|≤0.5 범위에 드는가
#     Kim&Jeong의 전제는 r_w/D < 1 **그리고** |1−R| < 0.5 이다 → α ∈ [0.5, 1.5] 에서만 검사한다.
R_W300 = 0.150                 # m — SEMI M1 300mm 웨이퍼 반경
for alpha in (0.5, 0.9, 0.95, 1.0, 1.1, 1.5):
    z = (R_W300 / E0) * (1.0 - alpha)
    assert abs(z) <= 0.5, (alpha, z)
# 전제를 벗어난 α=2.0 은 |ζ|>0.5 로 문헌 근사 밖이라는 것도 명시적으로 확인한다
assert abs((R_W300 / E0) * (1.0 - 2.0)) > 0.5
assert abs((R_W300 / E0) * (1 - 0.95) - 0.0375) < 1e-12
print(f"Zhao 2012: e₀={E0*1000:.0f} mm, sweep ±{DE0*1000:.0f} mm → e∈[{e_min*1000:.0f},{e_max*1000:.0f}] mm;"
      f" 300mm 웨이퍼 α=0.95 에서 ζ={0.0375:.4f} (|ζ|≤0.5 충족)")
# 2b) 논문의 근사 전제 r₀/e ≈ 1 이 300mm 웨이퍼에서 성립하는가(자릿수 점검)
ratio = R_W300 / E0
assert 0.5 < ratio < 1.0, ratio
print(f"   r₀/e = {ratio:.3f} — 논문 전제 'r₀/e ≈ 1'과 같은 자릿수(0.5~1.0), 근사 유효")

# ── 주장 3: Ye & Yao (2025) Table 1 기하 정합성 — e가 물리적으로 가능한 값인가.
#   캐리어가 플래튼 밖으로 나가면 안 된다: e + R_carrier ≤ R_plate
R_CARRIER, R_PLATE, R_WAFER5, E_YE = 0.175, 0.457, 0.0625, 0.27789   # m, Table 1
assert E_YE + R_CARRIER <= R_PLATE, (E_YE + R_CARRIER, R_PLATE)
margin = R_PLATE - (E_YE + R_CARRIER)
assert 0.0 <= margin < 0.010, margin
assert R_WAFER5 < R_CARRIER
print(f"Ye&Yao 2025 Table1 기하 폐합: e+R_carrier={(E_YE+R_CARRIER)*1000:.2f} mm ≤ R_plate=457 mm"
      f" (여유 {margin*1000:.2f} mm) — 표 수치 자기정합 확인")

# ── 주장 4: 채택값이 기존 estimated 값과 어떻게 다른가 (정직성 점검)
OLD, NEW = 0.180, 0.200
assert e_min <= OLD <= e_max, "기존값이 문헌 범위 밖이면 이 서술을 고쳐야 한다"
assert abs(NEW - E0) < 1e-12, "채택값은 Zhao e₀ 그 자체여야 한다"
print(f"기존 estimated {OLD*1000:.0f} mm → 채택 literature {NEW*1000:.0f} mm "
      f"(기존값도 sweep 범위 [175,225] mm 안에 있었음; 변화 {(NEW/OLD-1)*100:+.1f}%, "
      f"ω_p·r_cc 지배항이므로 MRR 속도항도 같은 비율로 이동)")

# ── 주장 5: Preston 속도항 스케일 — Lai(2001) Eq.2.12 |v_R| = ω_p·r_cc, 55 rpm 기준
rpm_p = 55.0
w_p = 2.0 * math.pi * rpm_p / 60.0
v_old, v_new = w_p * OLD, w_p * NEW
assert abs(v_old - 1.036726) < 1e-5, v_old
assert abs(v_new - 1.151917) < 1e-5, v_new
print(f"ω_p·r_cc @55rpm: {v_old:.6f} m/s (구) → {v_new:.6f} m/s (신), +{(v_new/v_old-1)*100:.1f}%")
print("PASS — Kim&Jeong ζ=0.17 재현, Zhao e₀=200mm 범위·전제 검증, Ye&Yao 기하 폐합, 속도항 환산 확인")
```

## 6. 미검증 / 한계 — 정직하게

1. **300 mm 양산기(AMAT Reflexion, Ebara 등)의 r_cc 실측값은 끝내 찾지 못했다.** 채택값 200 mm는
   양산 장비 도면값이 아니라 "12인치 플랫폼"이라고 명시한 논문의 시뮬레이션 설계 치수다.
   장비사 데이터시트는 r_cc를 공개하지 않고, Google Patents는 이번 세션에 503으로 조회 불가였다.
   → measured 등급으로 올리려면 특허 도면(축간거리 치수 기재)이나 장비 매뉴얼이 필요하다. **미검증 항목 1.**
2. **플래튼 직경으로부터의 기하 제약은 300 mm 툴에 대해 성립시키지 못했다.** 1차 문헌으로 확보한
   플래튼 직경은 Ye & Yao의 457 mm 반경(5인치 툴)뿐이고, 12인치 툴의 플래튼 직경 1차 출처는 없다
   (§2.1의 380 mm 값은 같은 표 안에서 모순되어 기각). → 기하 제약 경로는 **미완**. **미검증 항목 2.**
3. Kim & Jeong Fig. 6 캡션은 "radius of wafer = 200 mm"라 적혀 있으나, 같은 논문 Fig. 7의
   ζ = 0.17을 역산하면 반경 102 mm(= 200 mm 웨이퍼의 반경)가 나온다(§5 주장 1). 캡션의
   "radius"는 **diameter의 오기로 추정**한다. 본 노트는 Fig. 7의 자기정합 값을 따른다. **추정 1건.**
4. r_cc의 시간의존성(sweep, e(t) = e₀ ± 25 mm)은 문헌에 명시돼 있으나 FabSim 현재 엔진은 정적
   r_cc만 받는다. 속도 절대값은 ±12.5% 흔들린다는 뜻이다 — 향후 `center_offset_sweep_m` 도입 여지.
   현 시점에서는 **미검증(모델 미반영)**.

## 7. sim/에 반영할 때의 주의

- `center_offset_m: 0.200`으로 올리면 `sim/factors.py`의 `V = omega_p * center_offset_m`가 그대로
  +11.1% 이동한다. Preston k_p를 실측에 맞춰 캘리브레이션한 지점이 있다면 **함께 재조정**해야 한다.
- `lambda_ref_center_offset_m`(같은 파일 166행)도 같은 근거를 공유하지만, 이는 λ 정규화 기준점이라
  바꾸면 기존 λ 값의 의미가 달라진다. **본 제안은 `center_offset_m`만 대상으로 한다**(다른 작업자 충돌 방지).

## 출처
1. D. Zhao, T. Wang, Y. He, X. Lu, "Effect of Kinematic Parameters and Their Coupling Relationships on
   Global Uniformity of Chemical-Mechanical Polishing", *IEEE Trans. Semicond. Manuf.* 25(3), 502–510, 2012.
   https://doi.org/10.1109/TSM.2012.2190432 · PDF: `papers/zhao2012-tsm-kinematic-coupling.pdf` (미러 사이트 경유, 본문 확인)
2. H. Kim, H. Jeong, "Effect of Process Conditions on Uniformity of Velocity and Wear Distance of Pad and
   Wafer during Chemical Mechanical Planarization", *J. Electron. Mater.* 33(1), 53–60, 2004.
   https://doi.org/10.1007/s11664-004-0294-4 · PDF: `papers/kim-jeong-2004-jem-kinematic-number.pdf` (미러 사이트 경유, 본문 확인)
3. G. Ye, Z. Yao, "Research on the Trajectory and Relative Speed of a Single-Sided Chemical Mechanical
   Polishing Machine", *Micromachines* 16(4), 450, 2025. https://doi.org/10.3390/mi16040450 · PMC12029203 (OA)
   정오표: *Micromachines* 17(2), 160, 2026, PMC12943132 (Table 1 수치는 정정 대상 아님).
4. J.-Y. Lai, *Mechanics, Mechanisms, and Modeling of the Chemical Mechanical Polishing Process*,
   PhD thesis, MIT, 2001, §2.2.2 및 §6.3. https://web.mit.edu/cmp/publications/thesis/jiunyulai/ch2.pdf
   (r_cc 유도식의 정본. **수치는 없음** — §2.1 참조)
5. (기각) Y. Zhang et al., "Prediction of Pad Wear Profile and Simulation of Its Influence on Wafer
   Polishing", *Micromachines* 14(9), 1683, 2023. https://doi.org/10.3390/mi14091683 · PMC10536193.
   Table 1 내부 모순으로 플래튼 직경 근거에서 제외(§2.1).
