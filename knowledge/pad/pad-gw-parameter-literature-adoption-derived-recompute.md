<!-- V2-SECTION: R3-pad | 근거: pad, GW, contact, E_star, asperity, real contact area | 정본: ARCHITECTURE-V2.md §3 -->
# GW 패드 3키 문헌값 반영 + 파생 접촉량(real_contact_area_ratio·active_particle_density) 재적분

> 작성일: 2026-09-15 | 대상: `knowledge/params/base.yaml` 5개 키, `sim/sensitivity.py` 스캔 범위
> 선행: [[pad-material-gw-effective-modulus-asperity-distribution]](값 대조·권고를 만든 노트),
> [[../materials/hertz-gw-contact-mechanics]], [[../materials/pad-asperity-density-gw-literature-values]]
> 과제: 정확도 갭 CONFIDENCE 1~2위(5팩 공통 `pad_E_star_pa`·`pad_asperity_radius_m`·`pad_height_beta_inv_m`).

## 1. 무엇을 했나

직전 회차([[pad-material-gw-effective-modulus-asperity-distribution]])가 이 세 키의 1차 출처를
찾아 "현재값이 문헌보다 2.6~8.4배 과대 / 10배 과소 / 6.7배 과소"임을 확인하고 **권고로만** 남겼다.
이번 회차는 그 권고를 팩에 실제로 반영하고, **세 키에서 파생되는 두 값**(`real_contact_area_ratio`,
`active_particle_density_per_m2`)을 같은 코드로 다시 풀었다. 파생값을 함께 고치지 않으면 팩 안에서
서로 모순된 두 개의 패드 표면이 공존한다.

| 키 | 이전 | 이후 | 근거 |
|---|---|---|---|
| `pad_E_star_pa` | 1.0e9 (estimated) | **1.316e8** (literature) | Bozkaya & Müftü 2009 JES 156(12) H890, DOI: 10.1149/1.3231691, Table I: E_s=100 MPa(hard)·ν=0.49 → E*=131.6 MPa. 독립 3값(119 / 131.6 / 380 MPa)의 **중앙값** |
| `pad_asperity_radius_m` | 5.0e-6 (estimated) | **5.0e-5** (literature) | 같은 Table I(DOI: 10.1149/1.3231691) "Pad summit radius R_s = 50 µm(base), 25~100 µm" + Shi & Ring 2010 Microelectron. Eng., DOI: 10.1016/j.mee.2010.04.010, k_s=2e4/m → 50 µm |
| `pad_height_beta_inv_m` | 0.3e-6 (estimated) | **2.0e-6** (literature) | Sorooshian 2005 학위논문(Univ. of Arizona) p.358 Fig. A.1, Borucki et al. 2004 인용, λ=2.0 µm — **지수분포**(fab-sim과 동일 분포족) 유일 1차값 |
| `real_contact_area_ratio` | 5.8e-4 (estimated) | **1.393e-3** (estimated 유지) | 위 3키로 GW 재적분 (§3) |
| `active_particle_density_per_m2` | 1.845e7 (estimated) | **4.434e6** (estimated 유지) | 같은 재적분의 접촉 자리 수 (§3) |

**중앙값을 쓴 이유**(평균이 아니라): 세 값 중 Sorooshian 380 MPa 만 한 자릿수 위쪽 끝이다.
세 점에서 평균은 이상치 하나에 끌려가고, 중앙값은 안 끌려간다. 문헌 범위 1.19e8~3.8e8 Pa 는
그대로 노트·YAML note 에 적어 what-if 스캔이 그 안에서 돌게 했다.

## 2. 이번 회차가 새로 발견한 것 — source 문구와 실제 입력이 달랐다

`real_contact_area_ratio` 의 source 는 "입력 물성은 pad_asperity_radius_m·asperity_density_per_m2
와 **일관**" 이라고 적혀 있었다. 실제로는 아니었다. note 가 스스로 밝힌 적분 입력은
(E*=100 MPa, R=5 µm, 1/β=2 µm) 인데 당시 팩 값은 (E*=1.0e9 Pa, R=5 µm, 1/β=0.3 µm) 였다 —
E* 가 10배, 1/β 가 6.7배 어긋난다. 즉 **그 5.8e-4 는 우연히도 이번에 채택한 문헌값에 훨씬 가까운
조건에서 계산된 값**이었고, 팩 값으로 정직하게 풀면 1.50e-4 가 나온다(§3 verify 에서 assert).

이건 값 오류가 아니라 **출처 문구가 재현 불가능했던 사례**다. 파생값은 입력 키를 바꿀 때 반드시
같이 풀어야 한다는 규칙이 여기서 나온다.

## 3. GW 재적분 — 계산과 검증

3 psi, 300 mm 웨이퍼(A_n=π·0.15² m²), η=2.0e8 /m² 고정. 분리거리 d 를 W(d)=P·A_n 이 되도록
푼 뒤 그 d 에서 실접촉비와 접촉 자리 밀도를 읽는다.

```python verify
import math
from scipy.optimize import brentq
from scipy import integrate

# ── GW 지수분포 수치적분 (sim/tier2_physics/gw_contact.py 와 같은 식) ──────────
def gw(d, beta, eta, A_n, E_star, R):
    zmax = d + 60.0 / beta
    pdf = lambda z: beta * math.exp(-beta * z)
    n_frac, _ = integrate.quad(pdf, d, zmax)
    a_int, _ = integrate.quad(lambda z: (z - d) * pdf(z), d, zmax)
    f_int, _ = integrate.quad(lambda z: (z - d) ** 1.5 * pdf(z), d, zmax)
    return (eta * A_n * n_frac,
            math.pi * R * eta * A_n * a_int,
            (4.0 / 3.0) * E_star * math.sqrt(R) * eta * A_n * f_int)

A_n = math.pi * 0.15 ** 2
W_target = 3.0 * 6894.757 * A_n      # 3 psi
ETA = 2.0e8

def solve(E_star, R, binv):
    beta = 1.0 / binv
    d = brentq(lambda x: gw(x, beta, ETA, A_n, E_star, R)[2] - W_target, 1e-9, 200 * binv, xtol=1e-12)
    n, A_r, _ = gw(d, beta, ETA, A_n, E_star, R)
    return d, A_r / A_n, n / A_n, W_target / A_r

# (a) 옛 팩 실제값으로 풀면 5.8e-4 가 재현되지 않는다 — §2 의 핵심 주장
d_old, ar_old, np_old, _ = solve(1.0e9, 5.0e-6, 0.3e-6)
print(f"옛 팩값 재적분: A_r/A_n={ar_old:.4g} (YAML 에 적혀 있던 값 5.8e-4)")
assert abs(ar_old - 5.8e-4) / 5.8e-4 > 0.5, "옛 팩값으로는 5.8e-4 가 재현되지 않아야 한다(재현되면 §2 주장이 틀린 것)"
assert abs(ar_old - 1.50e-4) / 1.50e-4 < 0.02, "옛 팩값의 참값은 1.50e-4"

# (b) note 가 밝힌 옛 적분 입력(E*=100 MPa, R=5um, 1/beta=2um)으로는 5.8e-4 가 재현된다
_, ar_note, np_note, _ = solve(100e6, 5.0e-6, 2.0e-6)
assert abs(ar_note - 5.8e-4) / 5.8e-4 < 0.01, "note 가 적은 입력으로는 재현돼야 한다"
assert abs(np_note - 1.845e7) / 1.845e7 < 0.01, "접촉 자리 밀도도 같은 입력에서 재현"
print(f"옛 note 입력 재현: A_r/A_n={ar_note:.4g}, n/A_n={np_note:.4g} /m^2  → 출처 문구와 팩 값이 불일치했음이 확정")

# (c) 새 문헌값으로 푼 결과 = 이번에 YAML 에 넣은 값
d_new, ar_new, np_new, p_real = solve(1.316e8, 5.0e-5, 2.0e-6)
print(f"새 문헌값: d={d_new*1e6:.2f} um, A_r/A_n={ar_new:.4g}, n/A_n={np_new:.4g} /m^2, P_real={p_real/1e6:.2f} MPa")
assert abs(ar_new - 1.393e-3) / 1.393e-3 < 0.01, "YAML real_contact_area_ratio 와 일치해야 함"
assert abs(np_new - 4.434e6) / 4.434e6 < 0.01, "YAML active_particle_density_per_m2 와 일치해야 함"

# (d) 레짐 판정은 값 교체 전후로 불변이어야 한다 — 실접촉압력 << 산화막 경도(~9 GPa) = 탄성 레짐
H_oxide = 9e9
assert p_real < H_oxide / 100, "탄성 접촉 레짐(실접촉압력이 경도보다 두 자릿수 작음)"
assert 10e6 < p_real < 20e6, "새 조건 실접촉압력은 14.9 MPa 부근"

# (e) 방향성: 돌기가 크고(R 10x) 무르고(E* 1/7.6) 거칠어지면(1/beta 6.7x)
#     접촉 자리는 줄고 자리당 면적은 커진다
assert np_new < np_old and ar_new > ar_old, "자리 수 감소 · 실접촉비 증가"
print(f"자리 수 {np_old/np_new:.1f}배 감소, 실접촉비 {ar_new/ar_old:.1f}배 증가")
```

실행 결과(위 블록 (a)~(e) 가 전부 assert 로 고정한다): 옛 팩값 A_r/A_n = 1.497e-4 —
YAML 에 적혀 있던 5.8e-4 의 1/3.9 다. note 가 밝힌 입력으로는 5.797e-4 · 1.845e7 /m² 로 정확히
재현되므로 **YAML 의 "일관" 문구가 틀렸다는 것이 수치로 확정**됐다. 새 문헌값(출처: 위 §1 표의
DOI: 10.1149/1.3231691 · DOI: 10.1016/j.mee.2010.04.010 · Sorooshian 2005 p.358)으로 풀면
d=7.62 µm, A_r/A_n=1.393e-3, n/A_n=4.434e6 /m², 실접촉압력 14.85 MPa 이고, 이 네 수치는
YAML 값과 1% 이내로 일치함이 블록 (c)(d) 의 assert 로 검사된다.

## 4. 스캔 범위도 문헌 대역으로 좁혔다

`sim/sensitivity.py` 의 `pad_E_star_pa` 스캔 범위가 (3e8, 3e9) 였다. 새 기본값 1.316e8 은 **이
범위 안에 있지도 않다** — 민감도 스캔이 팩 운전점을 포함하지 않는 대역에서만 돌고 있었다는
뜻이다. 세 키 모두 문헌 관측 대역으로 교체했다:

| 키 | 이전 스캔 범위 | 이후 | 근거 |
|---|---|---|---|
| `pad_E_star_pa` | (3e8, 3e9) | (1.19e8, 3.8e8) | 독립 3그룹 실측 하한~상한 |
| `pad_asperity_radius_m` | (1e-6, 2e-5) | (2e-5, 1e-4) | Bozkaya Table I 25~100 µm |
| `pad_height_beta_inv_m` | (1e-7, 1e-6) | (1e-6, 5e-6) | λ=2.0 µm 중심(동일 분포족 1차값 1건뿐이라 대역 근거 약함 — 좁게 염) |

## 5. 한계 (정직 기록)

1. `pad_height_beta_inv_m` 는 **동일 분포족 1차 출처가 1건**(Sorooshian λ=2.0 µm)뿐이다.
   Bozkaya σ_s=5 µm 는 Gaussian SD 라 분포족이 달라 교차검증으로 쓸 수 없다. literature 로
   올렸지만 2번째 지수분포 출처가 나오면 재검증 대상이다.
2. `real_contact_area_ratio`·`active_particle_density_per_m2` 는 **3 psi 대표값**이다.
   압력에 따라 변하는 양이므로 압력 스윕 예측에는 GW 를 런타임에 풀어야 한다 — 이 한계는
   값 교체 전후로 동일하다.
3. 두 파생값의 confidence 는 **estimated 유지**했다. 입력 3키가 literature 가 됐어도 "단층
   가정"(자리 하나에 입자 하나)은 여전히 미검증이기 때문이다. 부풀리지 않는다.
4. 백테스트 유의 평균 ρ 는 0.9442 로 **불변**이다. 이 5키는 MRR 결합 경로(Kp·팩터 곱)에
   직접 들어가지 않고 tier2 진단(접촉응력·레짐 판정)에만 쓰이므로 예측 순위가 안 바뀌는 것이
   정상이다 — 정확도가 좋아졌다고 주장하지 않는다. 좋아진 것은 **내부 정합성**이다.

## 6. 새로 도출한 지식

1. 팩의 파생 파라미터(다른 키에서 계산되는 값)는 **입력 키 교체 시 함께 다시 풀어야 한다**.
   안 그러면 한 팩 안에 서로 모순된 두 개의 물리 상태가 공존하고, 그 불일치는 source 문구가
   "일관"이라고 주장하고 있어서 grep 으로 안 잡힌다. 이번에 3.9배 어긋나 있었다.
2. 민감도 스캔 범위는 **팩 기본값을 포함하는지** 기계적으로 검사할 수 있는 불변식이다.
   포함하지 않으면 그 스캔 결과는 운전점 근방 거동을 설명하지 않는다.
3. 독립 3값의 대표값으로 평균이 아니라 **중앙값**을 쓰면 한 자릿수 이상치(380 MPa)에 안 끌린다.

## 관련 노트
[[pad-material-gw-effective-modulus-asperity-distribution]] ·
[[../materials/hertz-gw-contact-mechanics]] · [[../materials/pad-asperity-density-gw-literature-values]] ·
[[../materials/pad-wear-glazing-mrr-decay]]
