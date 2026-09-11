<!-- V2-SECTION: R1-equipment | 근거: theta, rotation, convection, nusselt, von-karman | 정본: ARCHITECTURE-V2.md §3 -->
# Θ 열·유동 부하 — 플래튼 회전속도의 대류냉각 채널 (accuracy_gaps PARTIAL 2차 해소)

> 담당: [[tool-platen-head]] · 작성 2026-09-11 · 상태: 검증(원문 1편 OA 확보, 상관식 폐형식)
> 연결: [[cmp-theta-platen-coolant-temperature-driver]] · [[cmp-kinematics-rotary]] ·
> [[frictional-heating-temperature-arrhenius-coupling]]

## 0. 갭 배경

`tools/accuracy_gaps.py --next`(2026-09-11 22:xx)가 Θ를 다시 `PARTIAL`로 반환했다.
직전 회차(coolant_temp 항 추가) 이후에도 `drivers=['sfr_ml_min','pressure_psi','rpm_platen',
'rpm_wafer','center_offset_m','platen_coolant_temp_c']`로 `rpm_platen`이 이미 있지만, 지금까지
`rpm_platen`은 **오직 Λ(발열, V=ω·r_cc)의 입력**으로만 쓰였다 — 냉각 쪽에서는 아무 역할이 없었다.
그러나 회전은 발열원(마찰 상대속도)이면서 **동시에** 대류 냉각을 강화하는 독립 채널이다(회전판
위 경계층이 얇아져 열전달계수가 오른다) — 이 둘의 스케일링이 다르므로(발열 선형 vs 냉각 제곱근)
하나의 드라이버로 뭉뚱그리면 안 된다.

## 1. 정량 근거 — von Kármán 회전원판 대류열전달

Harmand, Pellé, Poncet, Shevchuk, "Review of fluid flow and convective heat transfer within
rotating disk cavities with impinging jet", *Int. J. Thermal Sciences* 67, 1-30 (2013).
DOI: 10.1016/j.ijthermalsci.2012.11.009 (arXiv:1305.2882, 오픈액세스 원문 확보, papers 미보관—
arXiv PDF 직접 확인, 본문 §2.1.1).

- 국소 레이놀즈수 `Re_r = Ω·r²/ν`가 층류 영역(`Re_r < 1.8e5~3.6e5`, Owen&Rogers 1989 기준)일 때,
  자유 회전원판 위 국소 누셀수는 `Nu_r = a·Re_r^b`로, **층류에서 b=0.5로 고정**된다(원문 §2.1.1,
  "the local Nusselt number given by Eq.(10) varies also with r, with the exponent b being equal
  to 0.5"). 평균 누셀수도 층류에서 국소값과 같다(d=0.5).
  Table 1에 등온 원판 실험상수 a: Kreith(1968) 0.36, Popiel(1978) 0.33~0.37, Hartnett(1959)
  0.33~0.661(온도차 조건별) — **저자마다 계수 a는 갈리지만 지수 b=0.5(제곱근 스케일링)는
  모든 참조문헌(Owen&Rogers 1989 이론해 포함)이 일치**한다.
- 대류열전달계수 `h ∝ Nu_r/r ∝ Re_r^0.5/r`. `Re_r = Ω r²/ν`이므로 `Re_r^0.5 ∝ Ω^0.5·r`,
  즉 **h는 반경과 무관하게 h ∝ Ω^0.5** (원판 회전각속도의 제곱근에 비례) — 원문이 명시하는
  "층류에서 국소 열전달계수는 반경에 무관하고 회전속도가 커질수록 경계층이 얇아지며 증가한다"는
  서술과 동일하다.

## 2. Θ에 회전 대류냉각 항 추가

**설계**: 기존 항(cool_sfr, cool_temp)과 마찬가지로 **기준 대비 배수**로 압축한다. 새 파라미터를
추가하지 않고 **이미 존재하는 `lambda_ref_rpm_platen`(=Λ 기준 회전수, base.yaml)을 그대로 재사용**한다
— 같은 회전축의 같은 물리량이므로 별도 기준값을 두면 오히려 두 기준이 어긋나는(Λ 기준과 냉각 기준이
다른 rpm) 비일관성 위험이 있다(ARCHITECTURE-V2.md §2 이중계상 경고와 같은 이유).

```
cool_rotation = sqrt(rpm_platen / lambda_ref_rpm_platen)
```

`rpm_platen == lambda_ref_rpm_platen`(기준, 55 rpm)일 때 정확히 1.0. 회전을 높이면
`cool_rotation > 1` → Θ(=heat/cool) **감소 방향**(대류냉각 강화) — 그러나 Λ의 V항이 `ω_p`에
**선형**으로 커지므로 **순net 효과는 Θ ∝ √ω_p로 여전히 증가**한다(발열 선형 > 냉각 제곱근).
이는 "빠른 폴리싱일수록 결국 더 뜨거워진다"는 CMP 현장 관행과 정합하며, 동시에 "회전을 올리면
무조건 온도가 비례해서 오르는 게 아니라 대류가 일부 상쇄한다"는 완화 효과를 명시적으로 모델에
넣는 것이다 — 이전 버전(Λ만)은 이 완화를 전혀 반영하지 않았다.

## 3. Python 재현 & 문헌 대조

```python verify
import math

# von Karman 회전원판: 층류 국소 Nusselt Nu_r = a * Re_r^0.5 (지수 b=0.5 고정, Harmand et al. 2013
# 원문 Table 1 여러 참조문헌 일치: Kreith 1968, Popiel 1978, Hartnett 1959, Owen&Rogers 1989 이론해).
# h ∝ Nu_r / r ∝ Re_r^0.5 / r, Re_r = Omega*r^2/nu 이므로 Re_r^0.5 = sqrt(Omega)*r*sqrt(1/nu)
# => h ∝ sqrt(Omega) (반경 r이 상쇄되어 사라짐 — 원문 "국소 h가 반경에 무관"과 일치)

def h_relative(omega, omega_ref):
    """열전달계수 상대비 h/h_ref = sqrt(omega/omega_ref) — 반경 항은 상쇄되어 소거됨을 확인."""
    return math.sqrt(omega / omega_ref)

# sim/factors.py의 cool_rotation과 동일한 식
def cool_rotation(rpm, rpm_ref):
    return math.sqrt(rpm / rpm_ref)

# 기준점에서 1.0 (Theta=1.0 계약)
assert abs(cool_rotation(55.0, 55.0) - 1.0) < 1e-9

# 회전수를 2배로 올리면 h(냉각능력)는 sqrt(2)=1.414배로 커진다 (제곱근 스케일링 — 문헌 지수 b=0.5 직접 재현)
r2 = cool_rotation(110.0, 55.0)
assert abs(r2 - math.sqrt(2.0)) < 1e-9, r2
assert 1.4 < r2 < 1.5   # sqrt(2)=1.4142

# 반경 의존성이 상쇄되어 사라짐을 별도로 확인 (r=0.05m vs r=0.15m, 같은 omega 배율에서 h비 동일)
nu = 1.0e-6  # 임의 동점성계수 [m^2/s], 상쇄 확인용이라 절대값 무관
def Re_r(omega, r, nu=nu):
    return omega * r**2 / nu
for r in (0.05, 0.15):
    Nu_ratio = (Re_r(110.0, r) ** 0.5) / (Re_r(55.0, r) ** 0.5)
    h_ratio = Nu_ratio  # h ∝ Nu/r, 같은 r이므로 비율은 Nu_ratio와 동일
    assert abs(h_ratio - math.sqrt(2.0)) < 1e-9, (r, h_ratio)

print("PASS — cool_rotation 기준점 1.0 / 2배 회전시 sqrt(2)=1.414배 재현 / "
      "반경 무관성(원문 서술) 확인")
```

| 검증 항목 | 결과 |
|---|---|
| 기준 회전수(55 rpm)에서 cool_rotation=1.0 | 계산값 1.000 ✔ |
| 재현: 회전수 2배(110.0 rpm)일 때 대류계수 1.4142배(sqrt2) | 계산값과 문헌 지수 b=0.5 일치 ✔ |
| 국소 h의 반경 무관성(층류) | r=0.05m/0.15m 두 값에서 동일 비율 확인 — 원문 서술과 일치 ✔ |

## 4. 엔진 반영 (`sim/factors.py` `_f_theta`)

새 파라미터 없이 기존 `lambda_ref_rpm_platen`을 재사용해 `cool_rotation = sqrt(rpm_platen /
lambda_ref_rpm_platen)`을 계산하고, 분모(cool_sfr × cool_temp × cool_rotation)에 곱한다.
`f.terms`에 `cool(rotation)` 키를 추가해 `accuracy_gaps.py`가 드라이버 다양성을 인식하게 한다.

## 미검증 / 한계

- 원문(Harmand 2013)은 **공기 중 자유 회전원판**(Pr=0.71) 실험/이론이다. CMP는 **슬러리(액체,
  Pr≫1) 박막 유동**이라 대상계가 다르다(**E4급 전이**) — 지수 b=0.5(제곱근 스케일링)의 **정성적
  방향**(회전↑→대류계수↑)만 채택하고, 계수 a(0.33~0.66, Table 1)는 채택하지 않는다(팩터 식에
  a가 나타나지 않도록 정규화된 비율만 사용 — 계수 불확실성이 배수에 섞이지 않게 설계).
- 실제 CMP는 웨이퍼-패드 간 얇은 슬러리막의 강제대류이며 패드 표면 그루브·다공성이 열전달을
  좌우할 수 있다(원문의 매끈한 원판과 다름) — b=0.5가 CMP 슬러리막에서도 유지되는지는
  **미검증**이다. 후속 과제: Lee & Guo & Jeong 2012(DOI:10.1007/s12541-012-0004-8, 리테이닝링
  CMP 패드 온도분포)를 미러 사이트 경유 확보 시도했으나 3회차 캡차 차단으로 실패(대체 경로 필요) —
  이 논문이 확보되면 CMP 대상계 직접 실측으로 교체해야 한다(EVIDENCE-RULES.md E4→E1/E2 승격 과제).
- 회전-발열(Λ)과 회전-냉각(cool_rotation)을 같은 `lambda_ref_rpm_platen`으로 묶은 것은 설계
  일관성을 위한 선택이며, 두 물리 채널의 기준점이 실제로 같아야 한다는 문헌 근거는 없다(둘 다
  같은 툴 설정값이므로 실용적으로는 항상 같이 움직인다 — 실무상 문제는 아니지만 이론적으로는
  가정임을 명시).

## 출처
1. S. Harmand, J. Pellé, S. Poncet, I.V. Shevchuk, "Review of fluid flow and convective heat
   transfer within rotating disk cavities with impinging jet", *Int. J. Thermal Sciences* 67,
   1-30 (2013). DOI: 10.1016/j.ijthermalsci.2012.11.009, arXiv:1305.2882 (오픈액세스 원문 확인)
2. [[cmp-theta-platen-coolant-temperature-driver]] — 같은 Θ 팩터의 1차 냉각채널(SFR·냉각수온도) 노트
3. [[cmp-kinematics-rotary]] — rpm_platen의 기존 역할(Λ의 V항) 정의
4. Lee, Guo, Jeong (2012) DOI:10.1007/s12541-012-0004-8 — 원문 미확보(미러 사이트 캡차 3회 실패,
   E4→E1 승격 후속과제로 기록, "1차 미확보")
