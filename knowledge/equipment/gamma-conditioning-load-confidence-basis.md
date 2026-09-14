<!-- V2-SECTION: R4-disk | 공동: R1-equipment | 작성 2026-09-14 | 근거: gamma, conditioner, critical load, Rs, pcr-decay | 정본: ARCHITECTURE-V2.md §3 -->
# Γ(컨디셔닝 부하) confidence 하한 3사유 판정 — Rs 보정 폐형식 상계·τ 앵커 항등성·임계하중 제1원리

> `sim/factors.py::_f_gamma()`는 confidence를 `estimated`로 하한하고 그 사유를 3개 적어 두었다
> ([[disk-rpm-load-radius-pcr]] §6). 이 노트는 그 셋을 **하나씩** 판정한다. 목표는 "해소"가 아니라
> 판정이다 — 근거 없는 승격은 오염이다. 결과: (1) 해소, (2) 조건부 하한으로 전환, (3) **미해소**.
> 따라서 기준조건 등급은 그대로 `estimated`다(칸 수 불변).
> 관련: [[conditioner-disk-pad-cutting-model]] [[conditioner-grit-density-protrusion-cutrate]]
> [[cvd-diamond-disk-patterned-grit-array]] [[../cmp/scratch-physics-source-signatures]]
> [[../materials/hertz-gw-contact-mechanics]] [[conditioning-mechanism-asperity-regeneration]]

## 1. 출처

**직접 인용(원문 확보)**
1. Zheng, Zhao & Lu (2023), *Micromachines* 14(9) 1683, DOI: 10.3390/mi14091683 (PMC10536193, CC-BY).
   Table 1 실험조건: 패드 100 RPM·디스크 73 RPM·하중 4 lbf·디스크 유효직경 104.5 mm·평균 다이아몬드
   피치 430 µm·폭 150 µm·돌출 250 µm·스윕 반경 83~308 mm. `papers/PMC10536193.txt`.
2. McAllister et al. (2019), *Micromachines* 10(4) 258, DOI: 10.3390/mi10040258 (PMC6523751, CC-BY).
   본문: "the platen and conditioning disc rotated counter-clockwise at 87 and 60 RPM" — **같은 방향** 회전,
   Rs=0.69. 코퍼스 `data/corpus/fulltext/doi_10.3390_mi10040258.xml`.
3. Kwon et al. (2013), *Tribology International* 67, 272–277, DOI: 10.1016/j.triboint.2013.08.008.
   플래튼 73 rpm·컨디셔너 93 rpm(Rs=1.27), 그릿 밀도 40,000개·피치 410 µm(Table 1).
   `papers/kwon2013-scratch-formation-diamond-conditioners.pdf`.
4. Tsai et al. (2014), *Math. Probl. Eng.* 2014, 913812, DOI: 10.1155/2014/913812 (CC-BY). 실험실 장비:
   컨디셔너 10 rpm·패드 40 rpm(Rs=0.25, 회전 방향 미기재), ∅108 mm 디스크, CDD 그릿 25,000개,
   "less than 10% of diamond grits are engaged". `papers/tsai2014-mpe-radial-cluster-arranged-diamond-disk.pdf`.
5. Saka, Eusner & Chun (2008), *CIRP Annals* 57(1) 341–344, DOI: 10.1016/j.cirp.2008.03.098.
   식(1)–(3) Hertz+Tresca 항복개시(a_Y, δ_Y, P_Y=(π³/48)H³R²/E²), 본문 IC1000 물성 **E_p=0.5 GPa,
   H_p=0.05 GPa**(습식 Berkovich, 국소값 0.01~0.31 GPa 산포, Fig.9). `papers/saka2008-cirp-nanoscale-scratching.pdf`.
6. Pysher, Goers & Zabasajja (3M, 2010), MRS Proc. 1249-E02-04, DOI: 10.1557/proc-1249-e02-04.
   사후 검사로 작동 다이아몬드의 DOP≈15 µm 추정. `papers/3m_diamond_conditioner_design.pdf`.
7. 특허(코퍼스 전문): US8657652B2(Saint-Gobain, 종래 디스크 활성 그릿 25~30%), JP6666749B2(패드 90 rpm·
   드레서 80 rpm), US10822524B2(테이블 17·드레서 20 rpm), US20070011952A1(테이블·디스크 100 rpm 동방향).
8. Lai (2001) MIT 박사논문 — 회전 운동학 상대속도식([[../physics/cmp-kinematics-rotary]]에서 확립,
   [[disk-rpm-load-radius-pcr]] §3이 디스크-패드 쌍에 치환). Lawing (2004) NCCAVS CMPUG 슬라이드 —
   "Below a critical down-force, polish rate will drop … Above critical down-force rate saturates".

**미확보(정직 표기)** — 마모된 다이아몬드 그릿의 **팁 곡률반경** 실측을 찾기 위해 `find_open_access.py`로
질의한 후보 3편: "Aggressive Diamond Characterization and Wear Analysis during CMP"(ECS Trans., DOI:
10.1149/05201.0597ecst), "CMP Active Diamond Characterization and Conditioner Wear"(MRS Proc., DOI:
10.1557/proc-0991-c01-01), "Diamond Conditioner Microwear Effect on Pad Surface Height Distribution in W CMP"
(JJAP, DOI: 10.7567/jjap.50.05ec05). 셋 다 OA 사본 없음 → **1차 미확보**. Tabor 관계(H≈3Y, 소성개시
p_m≈1.1Y)와 원뿔 압입의 자기상사성은 교과서 지식(Johnson 1985 *Contact Mechanics*, Tabor 1951)으로
**2차 인용**이며 원문은 확보하지 않았다 — 단 §4 verify가 Saka(2008) 식(3)과 수치로 대조한다.

## 2. 사유(1) 디스크 자전비 Rs 보정 — μ에 대한 폐형식 상계

### 2.1 유도
[[disk-rpm-load-radius-pcr]] §3의 치환식에서 디스크 위 점 (r̄, θ)의 상대속도는
`|v|/(ω_p r_cc) = sqrt(1 + 2εcosθ + ε²)`, ε = r̄μ, μ = (R_disk/r_cc)(1−Rs), Rs = ω_disk/ω_pad.
Γ는 디스크 **전체**가 패드에 가하는 절삭일률(P·v의 면적 적분)이므로, 균일 압력·균일 그릿밀도 가정
아래 필요한 것은 **면적평균** ⟨|v|⟩다.

θ 평균은 완전타원적분으로 닫힌다: `(1/2π)∮ sqrt(1+2εcosθ+ε²) dθ = (2/π)(1+ε)·E(k)`, k² = 4ε/(1+ε)².
ε<1에서 급수 전개하면 `1 + ε²/4 + ε⁴/64 + O(ε⁶)` (sqrt(1+x)의 x=2εcosθ+ε² 전개 후 ⟨cos²θ⟩=1/2 사용:
1차 항 ε²/2, 2차 항 −(4ε²/2)/8 = −ε²/4, 합 ε²/4). 면적 가중 2r̄dr̄로 r̄∈[0,1] 적분하면

```
⟨|v|⟩_area / (ω_p r_cc) = 1 + μ²/8 + μ⁴/192 + O(μ⁶)       →  c = 1/8
```

⚠ [[disk-rpm-load-radius-pcr]] §6 verify의 "1.00044"는 `np.linspace(0,1,200)`로 **반경 균등**(면적 가중
아님) 샘플이었다 — 그 가중에서는 c=1/12(=0.000434)이고, 물리적으로 옳은 면적 가중은 c=1/8(0.000652)이다.
둘 다 0.1% 미만이라 그 노트의 결론은 바뀌지 않지만, 계수는 여기서 정정한다(**재현 대조**: μ=0.0722에서
면적평균 편차 0.0652 % vs 반경균등 0.0435 %, 아래 verify).

### 2.2 실제로 가능한 μ 범위 (문헌)
| 출처 | 패드/디스크 rpm | Rs | 1−Rs | 비고 |
|---|---|---|---|---|
| Zheng 2023 Table 1 | 100 / 73 | 0.73 | 0.27 | 디스크 R=52.25 mm, 스윕 r_cc 83~308 mm → R/r_cc ≤ 0.63 |
| McAllister 2019 | 87 / 60 | 0.69 | 0.31 | 둘 다 반시계(동방향) 명시 |
| Kwon 2013 | 73 / 93 | 1.27 | −0.27 | 방향 미기재 |
| JP6666749B2 | 90 / 80 | 0.89 | 0.11 | 특허 실시예 |
| US10822524B2 | 17 / 20 | 1.18 | −0.18 | ex-situ 150 N |
| US20070011952A1 | 100 / 100 | 1.00 | 0 | 동방향 명시 |
| Tsai 2014 (실험실) | 40 / 10 | 0.25 | 0.75 | 소형 랩 장비, r_cc 미기재 |

산업 장비 6건은 |1−Rs| ≤ 0.31, 실험실 1건까지 넓히면 ≤ 0.75. R_disk/r_cc는 Zheng의 스윕 내측 반환점
(83 mm)에서 최대 0.63이고, 스윕 구간 균등 체류 가정의 평균 ⟨(R/r_cc)²⟩ = 0.107(∫dr_cc/r_cc² 해석적분).
역회전(1−Rs>1)은 확보한 문헌 어디에도 없다 — **범위 밖은 이 판정의 보증 대상이 아니다**.

### 2.3 verify — 계수 c 해석 vs 수치, 문헌 범위 최대 편차
```python verify
import numpy as np
from scipy.special import ellipe

def theta_avg_numeric(eps, n=20000):
    th = np.linspace(0, 2*np.pi, n, endpoint=False)
    return np.sqrt(1 + 2*eps*np.cos(th) + eps**2).mean()

def theta_avg_closed(eps):
    return (2/np.pi) * (1+eps) * ellipe(4*eps/(1+eps)**2)

# (a) θ 평균 폐형식(완전타원적분) = 수치적분
for eps in (0.05, 0.1, 0.3, 0.5, 0.9):
    assert abs(theta_avg_numeric(eps) - theta_avg_closed(eps)) < 1e-6, eps

def disk_area_avg(mu, n=4000):
    r = (np.arange(n) + 0.5) / n                       # 면적 가중 2r dr (중점법)
    return float(np.sum(theta_avg_closed(r*mu) * 2*r) / n)

def disk_radial_uniform_avg(mu, n=4000):
    r = np.linspace(0, 1, n)                           # disk-rpm-load-radius-pcr §6의 가중(반경 균등)
    return float(np.mean(theta_avg_closed(r*mu)))

series = lambda mu: mu**2/8 + mu**4/192

# (b) 계수 c=1/8 (면적 가중), 1/12 (반경 균등) — μ≤0.5에서 급수와 수치 1e-4 이내
for mu in (0.0722, 0.195, 0.28, 0.47):
    dev = disk_area_avg(mu) - 1
    assert abs(dev - series(mu)) < 1e-4, (mu, dev, series(mu))
    assert abs((disk_radial_uniform_avg(mu) - 1) - mu**2/12) < 2e-4

# (c) Zheng 2023 Table 1 조건 재현: μ=0.0722 → 면적평균 편차 0.065 %, 반경균등 0.043 %(§6의 1.00044)
mu_z = 0.0722
assert abs(disk_area_avg(mu_z) - 1.000652) < 2e-5
assert abs(disk_radial_uniform_avg(mu_z) - 1.000435) < 2e-5

# (d) 문헌 범위: 산업 6건 |1-Rs|<=0.31, 실험실 포함 <=0.75; R_disk/r_cc 순간 최대 0.63(83 mm), 스윕평균 <(R/r_cc)^2>=0.107
R_disk, r_in, r_out = 52.25, 83.0, 308.0             # mm, Zheng 2023 Table 1
ratio_max = R_disk / r_in
ratio_sq_sweep = R_disk**2 * (1/r_in - 1/r_out) / (r_out - r_in)
assert abs(ratio_max - 0.630) < 1e-3 and abs(ratio_sq_sweep - 0.1068) < 1e-3

def worst(one_minus_rs):
    inst = disk_area_avg(ratio_max * one_minus_rs) - 1                  # 내측 반환점 순간값
    sweep = series(np.sqrt(ratio_sq_sweep) * one_minus_rs)              # 스윕 평균(μ²∝⟨(R/r_cc)²⟩)
    return inst, sweep

inst_ind, sweep_ind = worst(0.31)     # 산업 최악(McAllister 2019)
inst_lab, sweep_lab = worst(0.75)     # 실험실 포함 최악(Tsai 2014)
print(f"산업 |1-Rs|=0.31: 내측 순간 {inst_ind*100:.2f}%  스윕평균 {sweep_ind*100:.3f}%")
print(f"실험실 |1-Rs|=0.75: 내측 순간 {inst_lab*100:.2f}%  스윕평균 {sweep_lab*100:.2f}%")
assert inst_ind < 0.01 and sweep_ind < 0.002      # 산업: 순간값도 1% 미만, 스윕평균 0.2% 미만
assert sweep_lab < 0.01 and 0.02 < inst_lab < 0.03  # 실험실 극단: 스윕평균 1% 미만, 순간값은 2~3%

# (e) 디스크 rpm 고정(73)·플래튼 rpm 변화 시 Γ 비율 오차가 스윕평균 1%를 넘는 플래튼 rpm 경계
one_minus_rs_1pct = np.sqrt(0.01 * 8 / ratio_sq_sweep)     # μ²/8 = 1% 되는 |1-Rs|
lo = 73 / (1 + one_minus_rs_1pct); hi = 73 / (1 - one_minus_rs_1pct)
print(f"|1-Rs| 경계 {one_minus_rs_1pct:.3f} → 플래튼 {lo:.0f}~{hi:.0f} rpm 안에서 스윕평균 편차 <1%")
assert 0.85 < one_minus_rs_1pct < 0.88 and lo < 40 and hi > 500
print("PASS: c=1/8 확인, 문헌 범위 내 총량 편차 <1%")
```

### 2.4 판정 — **해소(총량 스칼라에 한해)**
- Γ의 v항 오차는 `[1+dev(μ_now)]/[1+dev(μ_ref)] − 1`이므로 위 최대 편차가 곧 상계다. 확보한 문헌 범위
  전체(|1−Rs| ≤ 0.75, R_disk/r_cc ≤ 0.63)에서 **스윕평균 편차 < 1%**, 산업 조건에서는 < 0.2%다.
  이는 rpm_platen 자체의 표기 해상도(1 rpm/55 rpm ≈ 1.8%)보다 작다.
- 따라서 **Rs 드라이버 부재는 스칼라 총량 Γ의 등급을 제한하는 결측이 아니다.** 단 이 판정은
  **반경별 분포**에 대한 주장이 아니다 — 디스크 에지의 peak-to-peak 14.4%([[disk-rpm-load-radius-pcr]] §4)는
  여전히 존재하며 [[conditioner-sweep-kinematics-pcr-profile]]·[[disk-kinematics-sweep-pcr-prediction-model]]
  (분포 모듈)의 몫으로 남는다. 역회전 레시피(1−Rs>1)가 나타나면 이 상계는 재계산해야 한다.

## 3. 사유(2) PCR 시간감쇠 앵커(τ) — 기준조건에서 항등적으로 무관

### 3.1 사실
5팩 전부 `cond_disk_usage_hours = 0.0`, `cond_ref_disk_usage_hours = 0.0`이고 `_f_gamma`는
`A = pcr_decay(t,1,τ)/pcr_decay(t_ref,1,τ) = exp(−(t−t_ref)/τ)` **비율**만 쓴다. t = t_ref이면 τ가 무엇이든
A ≡ 1. 즉 2차 인용 앵커(TAU_AGING_HOURS≈27.4 h, EVIDENCE-RULES 판정#14)는 **기준조건 Γ에 영향을 줄 수
없다**. 반대로 t ≠ t_ref이면 A = exp(−Δt/τ)라 τ가 결과를 지배한다(20 h에서 τ 10배 → A 0.48→0.93).

### 3.2 verify — τ를 10배·1/10배로 바꿔도 기준조건 Γ 불변, 20 h에서는 변함
```python verify
import sys
sys.path.insert(0, ".")
from sim.engine import Recipe
from sim.factors import compute_factors
import conditioner_pcr_decay as CPD      # sim/tier2_physics (engine이 path에 넣음)

def gamma(pack, **ov):
    return compute_factors(Recipe(pack=pack, pack_overrides=ov).resolve())["gamma"]

tau0 = CPD.TAU_AGING_HOURS
assert abs(tau0 - 27.28) < 0.01, tau0          # 판정#14의 27.4 h (반올림), 정확값 27.284
try:
    for pack in ("oxide_silica", "cu_h2o2_bta", "w_fe_oxidizer", "sti_ceria", "sic_ceria_h2o2"):
        vals = {}
        for k in (1.0, 10.0, 0.1):
            CPD.TAU_AGING_HOURS = tau0 * k
            vals[k] = gamma(pack).value                       # 기준조건 t=t_ref=0
        assert abs(vals[10.0] - vals[1.0]) < 1e-12 and abs(vals[0.1] - vals[1.0]) < 1e-12, (pack, vals)
        assert abs(vals[1.0] - 1.0) < 1e-12                   # 기준조건 Γ=1.0 계약
    # t = t_ref ≠ 0 도 항등 (비율이라서)
    CPD.TAU_AGING_HOURS = tau0
    g_a = gamma("oxide_silica", cond_disk_usage_hours=20.0, cond_ref_disk_usage_hours=20.0).value
    CPD.TAU_AGING_HOURS = tau0 * 10
    g_b = gamma("oxide_silica", cond_disk_usage_hours=20.0, cond_ref_disk_usage_hours=20.0).value
    assert abs(g_a - g_b) < 1e-12 and abs(g_a - 1.0) < 1e-12
    # 반면 t=20 h, t_ref=0 이면 τ가 지배
    CPD.TAU_AGING_HOURS = tau0
    a1 = gamma("oxide_silica", cond_disk_usage_hours=20.0).terms["aging(pcr_decay)"]
    CPD.TAU_AGING_HOURS = tau0 * 10
    a10 = gamma("oxide_silica", cond_disk_usage_hours=20.0).terms["aging(pcr_decay)"]
finally:
    CPD.TAU_AGING_HOURS = tau0
import math
assert abs(a1 - math.exp(-20/tau0)) < 1e-9 and abs(a10 - math.exp(-20/(10*tau0))) < 1e-9
assert abs(a1 - 0.4804) < 1e-3 and abs(a10 - 0.9294) < 1e-3
print(f"기준조건: τ×10, ×0.1에서 Γ 동일(5팩). 20 h: A(τ)={a1:.4f}, A(10τ)={a10:.4f} — τ가 지배")
```

### 3.3 판정 — **조건부 하한으로 전환**
앵커의 2차 인용성(판정#14, 뒤집지 않음)은 사실이지만 그것이 등급을 제한하는 것은 **A가 1에서 벗어나는
조건에서만**이다. `_f_gamma`는 |A−1| > 0.01일 때만 이 사유로 `estimated` 하한을 걸고 notes에 이유를
남기도록 바꿨다(`GAMMA_AGING_CONF_TOL`). 기준조건에서는 이 사유가 등급을 건드리지 않는다.
이것은 부풀리기가 아니라 하한을 **실제로 필요한 곳에만** 거는 것이며, t≠t_ref에서는 지금과 같이
estimated다. (다만 §4의 사유(3)이 남아 기준조건 등급은 결과적으로 estimated 그대로다.)

## 4. 사유(3) 임계하중 — 제1원리 유도와 운전점 대조

### 4.1 유도 (구형 팁 Hertz 접촉의 소성 개시 하중)
반경 R의 강체 구(다이아몬드, E≈1000 GPa ≫ 패드)가 탄성 반무한체(E*)를 누를 때 Hertz:
`a = (3PR/4E*)^{1/3}`, `p_max = 3P/(2πa²) = (6PE*²/(π³R²))^{1/3}`, `p_m = (2/3)p_max`.
Tabor: 소성 개시는 평균접촉압력 `p_m ≈ 1.1Y`(Tresca, ν≈0.3에서 p_max≈1.6Y와 등가) → `p_max = 1.65Y`.
대입해 P에 대해 풀면

```
P_c = π³ R² (1.65·Y)³ / (6 E*²)  ≈ 23.2 · R² Y³ / E*²          (Y = 항복강도, E* ≈ E_p/(1−ν_p²))
δ_c = a_c²/R = (1.65π/2)² (Y/E*)² R                            (개시 시 탄성 압입깊이)
```
Saka et al. (2008) 식(3) `P_Y = (π³/48)·H³R²/E²`은 같은 구조에서 개시 기준을 `p_max = H/2`로 둔 것이다.
Tabor H≈3Y를 넣으면 본 유도의 기준은 `p_max = 0.55H`이므로 두 식의 비는 (0.55/0.5)³ = 1.331 —
아래 verify가 이 비를 재현한다(**대조 일치**). 보수적(P_c가 큰) 쪽인 본 유도를 판정에 쓴다.

**뾰족한 원뿔·각뿔에는 임계하중이 없다.** 이상적 원뿔은 길이 척도가 없어(자기상사) 접촉반경 a ∝ δ,
하중 P ∝ E*·a²·cot(반각)이고 평균압력 `p_m = P/(πa²) ∝ E*·cot(반각)`은 **하중과 무관**하다. 따라서
p_m > 1.1Y 여부는 각도·재료로만 정해져 모든 하중에서 소성이거나 모든 하중에서 탄성이다 — "어느 하중
아래에서 절삭이 멈춘다"는 문턱은 **팁이 마모로 둥글어진 그릿에서만** 생긴다(둥근 팁의 곡률반경 R이
길이 척도를 공급). 그래서 P_c의 크기는 전적으로 R에 달려 있고, R이 (3)의 결정 변수다.

### 4.2 문헌값 확보 현황
| 항목 | 값 | 출처 | 상태 |
|---|---|---|---|
| (a) 패드 탄성률 E_p | 0.5 GPa | Saka 2008 본문(IC1000, 습식) | 확보 |
| (a) 패드 경도 H_p | 0.05 GPa (국소 0.01~0.31) | Saka 2008 본문·Fig.9 | 확보 |
| (a) 항복강도 Y | H/3 ≈ 16.7 MPa | Tabor 관계(2차 인용) | 환산 |
| (a) 대안 E | 1.0 GPa / 0.117 GPa | base.yaml `pad_E_star_pa`(estimated) / [[../materials/pad-hardness-porosity-measurement-methods]] §8 Qi eq(11)(사용 불가 판정) | 감도용 |
| (b) 마모 그릿 팁 반경 R | **미확보** | 후보 3편 OA 없음(§1) | 1차 미확보 |
| (b) 기하 상한 | D/2 = 90 µm (E187 181 µm 그릿), Ring Table 2 β=D/2=95 µm | [[conditioner-disk-spec-recipe-industrial]] §2, [[conditioner-asperity-population-balance]] §5 | 상한만 |
| (b) 참고 | DOP≈15 µm | Pysher 2010 | 깊이이지 반경 아님 |
| (c) 그릿 총수 N_total | π(52.25 mm)²/(430 µm)² = 46,386 | Zheng 2023 Table 1(정방격자 가정) | 계산 |
| (c) 대안 N_total | 25,000 / 40,000 / 17k~60k | Tsai 2014 / Kwon 2013 / Kwon 2013 | 확보 |
| (c) 작동 비율 f_active | <10% / 25~30% / >75%(신설계 청구항) | Tsai 2014 / US8657652B2 Fig.6 / US8657652B2 청구항 1 | 확보 |

### 4.3 verify — P_c, 그릿당 하중, 임계 downforce, 감도분석
```python verify
import math
LBF = 4.4482216152605                       # N, 정의값
F_pack = 4.0 * LBF                          # cond_downforce_lbf=4.0 (5팩 공통, Zheng 2023 Table 1 조건)

# (a) Saka 2008 IC1000 물성 (본문 그대로)
E_p, H_p = 0.5e9, 0.05e9
Y = H_p / 3.0                               # Tabor H≈3Y (2차 인용)
E_star = E_p                                # ν_p=0 → E* 하한 → P_c 상한(보수적)

def P_c(R, Y=Y, E=E_star):                  # §4.1 유도식
    return math.pi**3 * R**2 * (1.65*Y)**3 / (6*E**2)
def P_saka(R, H=H_p, E=E_star):             # Saka 2008 식(3)
    return math.pi**3/48 * H**3 * R**2 / E**2
def delta_c(R, Y=Y, E=E_star):
    return (1.65*math.pi/2)**2 * (Y/E)**2 * R

# 유도식 vs Saka 식(3): 개시 기준 차이(0.55H vs 0.5H)만큼 1.331배 — 대조 일치
assert abs(P_c(50e-6)/P_saka(50e-6) - 1.331) < 0.002
# 기준 대입: R=90 µm → P_c 3.48 mN, R=15 µm → 0.097 mN (R² 스케일)
assert abs(P_c(90e-6)*1e3 - 3.482) < 0.01 and abs(P_c(15e-6)*1e3 - 0.0967) < 0.001
assert abs(P_c(90e-6)/P_c(15e-6) - 36.0) < 0.01

# (c) 그릿 수: Zheng 2023 Table 1 피치 430 µm·유효직경 104.5 mm → 46,386개 (정방격자)
N_total = math.pi * (52.25e-3)**2 / (430e-6)**2
assert abs(N_total - 46386) < 1
f_active = {"tsai_lt10pct": 0.10, "us8657652_conv": 0.30}
per_grit = {k: F_pack / (N_total * f) for k, f in f_active.items()}     # N
assert abs(per_grit["tsai_lt10pct"]*1e3 - 3.835) < 0.01
assert abs(per_grit["us8657652_conv"]*1e3 - 1.278) < 0.01

# 중심 사례(가정 R=15 µm, f=10%): 하중/P_c ≈ 40배, 임계 downforce 0.10 lbf
ratio_central = per_grit["tsai_lt10pct"] / P_c(15e-6)
Fc_central_lbf = N_total * 0.10 * P_c(15e-6) / LBF
print(f"중심 사례 R=15µm,f=10%: 그릿당 {per_grit['tsai_lt10pct']*1e3:.2f} mN vs P_c {P_c(15e-6)*1e3:.3f} mN "
      f"→ {ratio_central:.0f}배, 임계 downforce {Fc_central_lbf:.3f} lbf")
assert 39 < ratio_central < 41 and 0.09 < Fc_central_lbf < 0.11

# 감도분석: 각 입력을 P_c가 커지는(보수적) 쪽으로 밀었을 때 결론(오더 차이)이 유지되는가
flips = {}
# (b) R → 기하 상한 D/2 = 90 µm (팁 반경 문헌 미확보)
flips["R=90um"] = per_grit["tsai_lt10pct"] / P_c(90e-6)              # 1.10배
# (c) N_active → 60k×30% = 18,000 (Kwon 2013 최대밀도 × US8657652B2 종래 상한), R=90 µm
flips["R=90um,N=18000"] = (F_pack/18000) / P_c(90e-6)                  # 0.28배
# (a) E → 0.117 GPa (Qi 2003 eq11 추정, 사용불가 판정이지만 감도용), R=20 µm
flips["E=0.117GPa,R=20um"] = per_grit["tsai_lt10pct"] / P_c(20e-6, E=0.117e9)   # 1.2배
# (a) H 국소 상한 0.31 GPa (Saka Fig.9), R=15 µm
flips["H=0.31GPa,R=15um"] = per_grit["tsai_lt10pct"] / P_c(15e-6, Y=0.31e9/3)   # 0.17배
for k, v in flips.items():
    print(f"  보수적 밀기 {k}: 하중/P_c = {v:.2f}배")
assert all(v < 10 for v in flips.values()), "보수적 밀기에서도 오더 차이가 남으면 해소 가능 — 그렇지 않다"
assert flips["R=90um,N=18000"] < 1 and flips["H=0.31GPa,R=15um"] < 1   # 부호까지 뒤집힘(운전점이 임계 아래)

# 임계 downforce의 범위: (R, N_active) 조합에 따라 0.02~14 lbf — 운전점 4 lbf를 가로지른다
Fc = {(R, N): N * P_c(R) / LBF for R in (15e-6, 90e-6) for N in (850, 4640, 18000)}
assert min(Fc.values()) < 0.02 and max(Fc.values()) > 14
assert min(Fc.values()) < 4.0 < max(Fc.values())
print("임계 downforce 범위(lbf):", {f"R={R*1e6:.0f}um,N={N}": round(v, 3) for (R, N), v in Fc.items()})

# 보조: 개시 시 탄성 압입깊이 δ_c ≤ 0.67 µm(R=90 µm) ≪ 3M DOP 15 µm → 작동 그릿은 개시를 훨씬 넘어 있다
assert delta_c(90e-6)*1e6 < 0.7 and 15.0 / (delta_c(90e-6)*1e6) > 20
print("PASS: 임계하중 판정 — 입력 불확실성이 결론을 뒤집는다(미해소)")
```

### 4.4 판정 — **미해소(하한 유지)**
- 중심 사례(R=15 µm 가정, 작동 10%)만 보면 그릿당 하중이 P_c의 약 40배, 임계 downforce ≈ 0.10 lbf로
  운전점(4 lbf)에서 멀다. 그러나 이 결론은 **팁 반경 R의 가정에 R²로 걸려 있고**, R의 1차 문헌값이 없다.
- 보수적 밀기 4건 중 어느 하나만으로도 오더 차이가 사라지고(1.1배, 1.2배), 두 건은 부호까지 뒤집혀
  운전점이 임계 **아래**가 된다(0.28배, 0.17배). 임계 downforce의 범위(0.02~14 lbf)가 4 lbf를 가로지른다.
- 판정 규칙대로 **하한 유지**. 부족한 것은 구체적으로 (b) 마모 그릿 팁 곡률반경의 실측(§1 후보 3편 중
  1편이라도 원문 확보), 그리고 (a) IC1000류의 항복강도 자체(경도→Y 환산이 아닌 직접값)다. 이 둘이
  확보돼 R ≤ 30 µm·Y/E* ≥ 0.03이 확인되면 P_c ≤ 0.4 mN으로 하중 하한(1 mN)보다 작아져 재판정할 수 있다.
- 보조 관찰(판정 근거 아님): 3M DOP 15 µm(Pysher 2010)는 개시 압입깊이 δ_c(≤0.67 µm)의 20배 이상이므로
  **작동 중인** 그릿은 소성 영역 깊숙이 있다 — 그러나 3M의 하중이 미기재라 F_c를 구속하지 못한다.
- 별개 비선형(주의): Lawing (2004)의 "critical down-force"는 연마율(MRR)이 컨디셔너 하중에 **포화**하는
  상단 무릎이지 절삭 개시 문턱이 아니다([[conditioning-mechanism-asperity-regeneration]] §3). Γ(부하 스칼라)의
  정의 밖이며, Γ를 소비하는 S 쪽 과제로 남긴다.

## 5. 종합 — `_f_gamma` 반영
| 사유 | 판정 | 코드 반영 |
|---|---|---|
| (1) Rs 보정 | 해소(총량 스칼라 한정, 문헌 범위 내 스윕평균 <1%) | docstring "해소"로 갱신, notes 문구 수정 |
| (2) τ 앵커 | 조건부 — 기준조건 무관, \|A−1\|>0.01일 때만 하한 | `GAMMA_AGING_CONF_TOL`, 조건부 note |
| (3) 임계하중 | **미해소** — 입력 불확실성이 결론을 뒤집음 | 무조건 `estimated` 하한 유지 |

기준조건 Γ 등급: `estimated` 그대로(칸 수 불변). Γ **값**은 한 곳도 바뀌지 않는다
(`tests/test_gamma_confidence_basis.py`가 5팩·t=0/20/50 h에서 고정). EVIDENCE-RULES 판정#22.

## 6. 미검증·한계
- (1)의 상계는 균일 압력·균일 그릿밀도 가정이다. 디스크 짐벌·에지 압력 집중은 미반영(분포 모듈 몫).
- 역회전(1−Rs>1) 레시피는 문헌에서 확인하지 못했다 — 나타나면 §2.3 (d)를 재계산.
- (3)의 R은 **1차 미확보**, Y는 H/3 환산(2차 인용), 패드는 평탄 반무한체 가정(애스퍼리티 위 접촉이면
  응력 집중으로 P_c가 더 작아지므로 이 가정은 보수적이다). 3M DOP는 기준면 정의라 "침투 깊이"로 읽는
  것은 해석이다.
- N_total의 정방격자 환산은 디스크 전면이 그릿으로 덮였다는 가정(edge exclusion 무시)이라 상한 쪽이다.
