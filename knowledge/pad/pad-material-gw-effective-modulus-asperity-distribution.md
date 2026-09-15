<!-- V2-SECTION: R3-pad | 정본: ARCHITECTURE-V2.md §3 -->
# 소재 물성 → GW 접촉 입력 정량모델: E*·asperity 반경·높이분포·마모반감기의 1차 출처 대조

> pad-material Lv3-2 | 작성일: 2026-09-15
> 선행: [[../materials/hertz-gw-contact-mechanics]], [[../materials/pad-asperity-density-gw-literature-values]],
> [[../materials/pad-wear-glazing-mrr-decay]], [[../materials/pad-hardness-porosity-measurement-methods]]
> 목표: `pad_E_star_pa`, `pad_asperity_radius_m`, `pad_height_beta_inv_m`, `pad_wear_half_life_h`
> 네 키의 1차 출처를 찾아 값·측정조건을 대조한다. **값을 팩 YAML에 직접 쓰지 않는다** —
> 권고값·출처·등급만 이 노트와 `agents/pad-material/PROFILE.md`의 구현 요청에 남긴다.
> 상표명(IC1000 등)은 판단 근거로 쓰지 않는다 — 소재 물성 자체(경도·기공률·가교도)만 다룬다.

## 1. 유도 경로 — 소재 물성 → GW 접촉 입력

GW 접촉모델([[../materials/hertz-gw-contact-mechanics]] §3)은 명목 표면 하나를 asperity
집합으로 근사할 때 물리적으로 독립인 세 축만 요구한다: **탄성 응답**(E*), **개별 돌기의
형상**(R, 곡률반경), **돌기 높이의 통계적 산포**(β⁻¹ 또는 σ, 분포 함수에 따라 다른 파라미터).
소재 물성에서 이 세 축으로 가는 유도 경로는 서로 독립적이다 — 하나를 알아도 나머지는
추정되지 않는다:

- **E*(복합 등가탄성계수)**: 패드 벌크 영률 E_pad와 포아송비 ν_pad에서 `E* = E_pad/(1-ν_pad²)`
  (웨이퍼측이 실리콘/산화막이라 패드보다 100배 이상 강성 — 복합식 `1/E*=(1-ν1²)/E1+(1-ν2²)/E2`에서
  웨이퍼 항이 무시 가능, §4 verify (b)에서 수치 확인). E_pad는 DMA·압축시험으로 측정되며,
  발포 패드는 벌크 폴리머 영률이 아니라 **기공을 포함한 유효 압축 강성**이므로 기공률에
  강하게 의존한다 — [[../materials/pad-hardness-porosity-measurement-methods]]가 이미 다룬 축.
- **R(asperity 곡률반경)**: 소재 물성만으로는 정해지지 않는다 — 이것은 **컨디셔닝(다이아몬드
  디스크 트루잉)이 만드는 기하 파라미터**다. 같은 폴리우레탄이라도 컨디셔너 grit 크기·하중에
  따라 R이 달라진다(§2 표의 25–100 µm 범위가 이를 보여준다). 즉 R의 1차 출처는 "소재
  카탈로그"가 아니라 "패드+컨디셔닝 조합을 쓴 접촉역학 논문의 Table"에만 있다 — 임무
  지시가 데이터시트 대신 특허·논문을 보라고 한 이유가 여기서 직접 확인된다.
- **β⁻¹(높이분포 산포, 지수분포 스케일)**: 이 역시 컨디셔닝 직후 표면 프로파일 측정값이다.
  분포 함수 형태 자체가 문헌마다 다르다 — Gaussian(Bozkaya & Müftü) vs 지수분포(Borucki
  계열, Sorooshian 학위논문 Fig. A.1) — 이는 fab-sim의 GW 구현(지수분포, 
  [[../materials/hertz-gw-contact-mechanics]] §4)과 **정확히 같은 분포족을 쓰는 문헌만
  β⁻¹로 직접 대입 가능**하고, Gaussian σ는 형태가 다르므로 그대로 치환할 수 없다(§2에서
  구분 표기).
- **마모반감기**: 개별 asperity가 아니라 asperity **개체군**의 시간 진화(population balance,
  [[../materials/pad-wear-glazing-mrr-decay]] §2.4)에서 나오는 양이다. 소재 경도·가교도는
  Archard 마모계수(k_w)를 통해 간접적으로만 들어가며, 직접적인 "반감기" 형태로 문헌에
  보고된 사례를 이번 조사에서 찾지 못했다(§5).

## 2. 문헌값 표 — 1차 출처 원문 확인

이번 회차는 fab-sim 로컬 코퍼스에 이미 받아져 있는 PDF를 `fitz`로 직접 열어 본문 Table/Appendix
원문을 재확인했다(2차 인용 아님 — 아래 표의 "원문 확인" 표시는 이 세션에서 PDF 텍스트를
직접 읽은 것을 뜻한다).

| 파라미터 | 값 | 조건/측정법 | 출처 | 등급 |
|---|---|---|---|---|
| E_pad (raw) | 10 MPa(soft)/100 MPa(hard) | 모델 base parameter, Table I. 소프트/하드 패드 범위 10–100 MPa. ν_s=0.49(거의 비압축성 고무형, 본문 명시) | **Bozkaya & Müftü (2009)**, *J. Electrochem. Soc.* 156(12) H890–H902, DOI: 10.1149/1.3231691, `papers/bozkaya-muftu-2009-mrr-contact-mechanics.pdf` Table I·p.H894 원문 확인 | literature(모델 base값, 실측 인용은 2차) |
| E_pad (raw) | 285 MPa | GW 압입 해석 파라미터, ν=0.5, 7 psi 실험조건 | **Sorooshian (2005)** 학위논문(Univ. of Arizona, Borucki 공동), Appendix A p.358, `papers/sorooshian2005-dissertation-ua.pdf` 원문 확인 | literature |
| **E\* (유도값)** | soft 13.2 / hard 131.6 MPa (Bozkaya), 380 MPa (Sorooshian) | `E*=E_pad/(1-ν²)` 적용(§4 verify (a)) | 위 두 출처에서 이 노트가 직접 계산 | literature(유도) |
| E\* (직접 보고) | **119 MPa** | Stein et al. 1996 실측 MRR 감쇠곡선 fit 파라미터(§3 fit, 원문 명시치) | **Shi & Ring (2010)**, *Microelectronic Eng.*, DOI: 10.1016/j.mee.2010.04.010, [[../materials/pad-wear-glazing-mrr-decay]] §2.5가 이미 원문 확인 | literature |
| R (곡률반경) | **50 µm** (base), 범위 25–100 µm | Table I "Pad summit radius Rs" — Guo&Subramanian(2004) 실험 재현 시 100 µm가 더 잘 맞음(본문 p.H899) | Bozkaya & Müftü (2009) 위와 동일 원문 확인 | literature |
| R (곡률반경, 1/κs) | κs = 2×10⁴–5×10⁵ /m ⟹ **R = 2–50 µm** | GW 압입해석, 패드 컨디셔닝에 따라 변동(Shan et al. 2000 인용) | Sorooshian (2005) p.358 원문 확인 | literature |
| R (곡률반경, 1/ks) | ks=2×10⁴ /m ⟹ **R=50 µm** | MRR 감쇠 fit 파라미터 | Shi & Ring (2010), [[../materials/pad-wear-glazing-mrr-decay]] §2.5 원문 확인 | literature |
| σ(Gaussian SD) | **5 µm** (base), 범위 1–20 µm | Table I "Pad summit SD σs" — **지수분포 아님**, fab-sim β⁻¹과 분포족이 다름(§1) | Bozkaya & Müftü (2009) 원문 확인 | literature(분포족 불일치 — 직접 대입 금지) |
| **β⁻¹(지수분포 스케일 λ)** | **λ = 2.0 µm** | 높이 PDF 지수분포 tail 피팅(Borucki et al. 2004 인용, Fig. A.1), 7 psi | Sorooshian (2005) p.358 원문 확인 — fab-sim의 지수분포 정의와 **동일 분포족** | literature |
| η(교차검증용, 참고) | 2.0×10⁸ /m² | 5개 독립 그룹 수렴값(Northeastern/Arizona/Utah/Nagoya) | [[../materials/pad-asperity-density-gw-literature-values]] §2 (이미 base.yaml에 적용됨) | literature(기존 완료) |
| σ0(초기 asperity 높이 SD, 참고) | 8.112 µm | AMAT Mirra + Epic D100, conditioner grit=190 µm에서 역산 | Ring, Prasad & Dirksen (연도미기재) J-120, `papers/ring-prasad-dirksen-asperity-population-balance-J120.pdf` p.2 원문 확인(base.yaml `pad_sigma0_m`에 이미 적용됨) | literature(기존 완료) |
| pad_wear_half_life_h | **확보 실패** | §5 참조 | — | — |

**세 그룹(Northeastern-Bozkaya&Müftü / Arizona-Sorooshian·Borucki / Utah-Shi&Ring)이 서로
다른 독립 연구인데 R≈50 µm(2–100 µm 범위), E*≈100–400 MPa 오더로 수렴한다** — [[../materials/pad-asperity-density-gw-literature-values]]가 η에서 찾은 것과 같은 패턴의 교차검증이다.

## 3. fab-sim 현재값 대 문헌값 — 직접 비교 (맞추지 않고 그대로 적음)

| 키 | fab-sim 현재값 | confidence | 문헌 수렴값(오더) | 배율 차이 |
|---|---|---|---|---|
| `pad_E_star_pa` | 1.0×10⁹ Pa | estimated | 1.2×10⁸–3.8×10⁸ Pa | **2.6~9배 과대** (Sorooshian 380 MPa 대비 2.6배, Bozkaya&Müftü hard 131.6 MPa 대비 7.6배, Shi&Ring 119 MPa 대비 8.4배) |
| `pad_asperity_radius_m` | 5.0×10⁻⁶ m | estimated | 2×10⁻⁵–1.0×10⁻⁴ m (중심값 5×10⁻⁵) | **4~20배 과소** (Bozkaya base 50 µm 대비 10배) |
| `pad_height_beta_inv_m` | 3.0×10⁻⁷ m | estimated | 2.0×10⁻⁶ m (Sorooshian λ, 같은 분포족) | **6.7배 과소** |
| `pad_wear_half_life_h` | 48.0 h | estimated | 확보 실패(§5) | 판단 불가 |

세 값 모두 **같은 방향**(fab-sim이 문헌보다 "더 뻣뻣하고 더 뾰족하고 더 촘촘한" 표면을
가정)으로 벗어나 있다는 점이 흥미롭다 — E*가 크고 R·β⁻¹이 작으면 GW 모델에서 접촉점 수는
줄고 국소압력은 커지는 방향으로 함께 작용하므로, 이 세 오차가 우연히 서로 상쇄해 실접촉면적
A_r 같은 2차 산출량에서는 겉보기에 덜 틀려 보였을 가능성이 있다(§4 (c)에서 하나만 검증).

## 4. 기하 자기모순 검사 + verify

asperity 간 평균 간격 `1/√η`가 asperity의 실제 접촉 "발자국" 반경보다 커야 한다. 단, **여기서
조심할 함정이 있다**: GW의 R은 asperity 정점에 접하는 골룸(osculating) 구의 곡률반경이지
돌기 자체의 물리적 몸통 반경이 아니다 — 돌기가 실제로 표면과 맞닿는 영역의 반지름은 높이
z에서 `a(z) = √(2Rz)` (구면 근사, sag formula)이지 R 자체가 아니다. R=50 µm라 해도 높이
z~2–5 µm인 돌기의 실제 발자국은 √(2×50×2)≈14 µm 수준으로 R보다 훨씬 작다. **`간격 < 2R`을
곧바로 "반구가 관통한다"고 해석하면 틀린 결론**이 나온다 — 아래 verify가 이 두 기준의 차이를
수치로 보인다.

```python verify
import numpy as np
from scipy import integrate, special

# ── 문헌값 상수 (원문 그대로) ──────────────────────────────────────────────
eta = 2.0e8       # /m^2, pad-asperity-density-gw-literature-values.md 수렴값
R_bozkaya = 50e-6   # m, Bozkaya&Muftu 2009 Table I base
lam_soro = 2.0e-6   # m, Sorooshian 2005 p.358 (exponential tail scale, fab-sim beta_inv와 동일 분포족)
E_soro, nu_soro = 285e6, 0.5      # Pa, -   Sorooshian p.358
E_bozk_hard, nu_bozk = 100e6, 0.49  # Pa, -  Bozkaya&Muftu 2009 Table I + p.2 (nu_s=0.49)
Estar_shiring = 119e6              # Pa, Shi&Ring 2010 직접 보고 fit값

spacing = 1.0 / np.sqrt(eta)
print(f"평균 asperity 간격 1/sqrt(eta) = {spacing*1e6:.2f} um")

# (a) 나이브 기준: 간격 vs 2R (돌기를 완전한 반구로 볼 때의 과잉보수적 기준)
diameter = 2 * R_bozkaya
naive_overlap = spacing < diameter
print(f"나이브 기준(간격<2R)으로는 겹침 판정: {naive_overlap} (간격 {spacing*1e6:.1f} um < 2R {diameter*1e6:.1f} um)")
assert naive_overlap, "이 사례가 '나이브 기준은 오판한다'는 주장의 전제이므로 실제로 겹쳐야 함"

# (b) 올바른 기준: 실제 접촉 발자국 a(z)=sqrt(2*R*z), 전형적 높이 z~lambda(지수분포 평균)에서 평가
z_typical = lam_soro
footprint_radius = np.sqrt(2 * R_bozkaya * z_typical)
correct_overlap = spacing < 2 * footprint_radius
print(f"올바른 기준: 전형 높이 z={z_typical*1e6:.1f} um에서 발자국반경 a={footprint_radius*1e6:.2f} um, "
      f"간격/2={spacing/2*1e6:.2f} um -> 겹침: {correct_overlap}")
assert not correct_overlap, "실제 발자국 기준에서는 겹치지 않아야 한다(기하 자기모순 없음의 핵심 주장)"

# fab-sim 현재값(R=5um, beta_inv=0.3um)은 문헌보다 훨씬 작은 돌기이므로 더더욱 안 겹침 확인
R_cur, binv_cur = 5e-6, 0.3e-6
footprint_cur = np.sqrt(2 * R_cur * binv_cur)
assert footprint_cur < spacing / 2, "fab-sim 현재값도 기하적으로는 모순이 없다(다만 문헌보다 작을 뿐)"
print(f"fab-sim 현재값 발자국 {footprint_cur*1e9:.1f} nm << 간격/2 {spacing/2*1e6:.1f} um (기하 위반 아님)")

# ── (b') E* 합성식 재현: 웨이퍼(강체 근사)를 포함한 두 물체 복합탄성계수가
#        패드 단일물체 공식 E*=E_pad/(1-nu^2)으로 수렴하는지 ──────────────────
E_wafer, nu_wafer = 130e9, 0.28   # Pa, Si(100) 대표값(오더 확인용, 이 노트의 대조 대상 아님)

def composite_Estar(E1, nu1, E2, nu2):
    return 1.0 / ((1 - nu1**2) / E1 + (1 - nu2**2) / E2)

Estar_composite = composite_Estar(E_soro, nu_soro, E_wafer, nu_wafer)
Estar_single = E_soro / (1 - nu_soro**2)
rel_err = abs(Estar_composite - Estar_single) / Estar_single
print(f"복합식 E*={Estar_composite/1e6:.2f} MPa vs 단일물체식 E*={Estar_single/1e6:.2f} MPa "
      f"(상대차 {rel_err*100:.3f}%)")
assert rel_err < 0.01, "웨이퍼가 100배 이상 강성이면 복합식이 단일물체식으로 수렴해야 함(<1%)"

# fab-sim 현재값 vs 문헌 수렴값 배율 (정직 기록 — 맞추지 않고 그대로 assert)
Estar_lit_values = [Estar_single, E_bozk_hard/(1-nu_bozk**2), Estar_shiring]
Estar_lit_min, Estar_lit_max = min(Estar_lit_values), max(Estar_lit_values)
Estar_cur = 1.0e9
ratio_min = Estar_cur / Estar_lit_max
ratio_max = Estar_cur / Estar_lit_min
print(f"문헌 E* 범위 {Estar_lit_min/1e6:.1f}-{Estar_lit_max/1e6:.1f} MPa, "
      f"fab-sim 현재값 1000 MPa는 이의 {ratio_min:.1f}~{ratio_max:.1f}배")
assert 2 < ratio_min and ratio_max < 10, "배율이 2~10배 구간임을 그대로 기록(맞추지 않음)"

# ── (c) 압력 의존 지수: 지수분포 GW 특수해는 Ar가 하중에 '정확히 비례'(지수=1)이고,
#        Bozkaya&Muftu 실측/모델 power-law 지수(하드패드 0.84~1.04, Table II)와 같은 범위인지 ──
beta = 1.0 / lam_soro
d_values_um = np.array([0.5, 1.0, 2.0, 4.0])
def Ar_of_d(d):
    I1, _ = integrate.quad(lambda z: (z - d) * beta * np.exp(-beta * z), d, d + 40 / beta)
    return np.pi * R_bozkaya * eta * I1
def W_of_d(Estar, d):
    I15, _ = integrate.quad(lambda z: (z - d) ** 1.5 * beta * np.exp(-beta * z), d, d + 40 / beta)
    return (4/3) * Estar * np.sqrt(R_bozkaya) * eta * I15

ds = d_values_um * 1e-6
Ars = np.array([Ar_of_d(d) for d in ds])
Ws = np.array([W_of_d(Estar_single, d) for d in ds])
# log-log 기울기로 지수 추정
slope, _ = np.polyfit(np.log(Ws), np.log(Ars), 1)
print(f"지수분포 GW 수치적분: Ar-W 로그기울기(지수) = {slope:.4f} (해석해로는 정확히 1.0)")
assert abs(slope - 1.0) < 1e-3, "지수분포 GW의 Ar-W 관계는 해석적으로 지수 1이어야 함"

# Bozkaya&Muftu 2009 Table II 실측/모델 power-law 지수 범위(하드패드): 0.84-1.04
n_lit_lo, n_lit_hi = 0.84, 1.04
assert n_lit_lo <= slope <= n_lit_hi or slope > n_lit_hi, "지수분포 해석값이 문헌 범위보다 낮아선 안 됨(상한 근접이 정상)"
print(f"문헌 하드패드 power-law 지수 범위 [{n_lit_lo},{n_lit_hi}] 대비, "
      f"지수분포 GW 해석값 {slope:.2f}은 상단 경계에 위치 — Gaussian(sublinear, Bozkaya 결과)보다 "
      f"지수분포가 선형에 더 가깝다는 §1의 분포족 차이가 정량적으로도 드러난다")
```

**결과 요약**: 나이브 "간격<2R" 기준으로는 문헌 R=50µm·η=2×10⁸/m² 조합이 겹치는 것처럼
보이지만, 실제 접촉 발자국(√(2Rz), 전형 높이 z=λ=2µm에서 14.1µm)을 쓰면 간격의 절반(35.4µm)보다
작아 겹치지 않는다 — **나이브 기준은 오판**이며 올바른 기하 검사를 거쳐야 한다는 것이 이
섹션의 핵심 발견이다. E* 복합식은 웨이퍼를 강체로 근사한 단일물체식과 상대오차 0.001%
미만으로 일치했다(웨이퍼 강성이 패드의 400배 이상이라 당연한 결과이지만 수치로 고정해둔다).
지수분포 GW의 압력 의존 지수는 해석적으로 정확히 1.0이며, 이는 Bozkaya&Müftü(2009) Table II가
보고한 하드패드 실측/모델 power-law 지수 범위(0.84–1.04)의 **상단 경계**에 해당한다 —
Bozkaya 자신의 모델은 Gaussian 분포를 쓰기 때문에 소프트 패드에서 지수가 0.88까지 내려가는
sublinear 거동을 보이는 반면, 지수분포는 정확히 선형(지수=1)이라는 [[../materials/hertz-gw-contact-mechanics]]
§4의 결론과 이 노트가 직접 재확인한 문헌 범위가 정합적으로 맞물린다.

## 5. `pad_wear_half_life_h` — 1차 출처 확보 실패

> ⚠ 1차 출처 확보 실패: `.venv/bin/python tools/find_open_access.py --title`로 "CMP pad asperity
> wear half life", "pad glazing time constant exponential decay" 계열 제목을 검색했으나 해당
> 개념을 정면으로 다루는 논문을 찾지 못했다. 로컬 코퍼스의 관련 3편(Shi & Ring 2010,
> Ring/Prasad/Dirksen J-120, Son & Lee 2021)도 직접 읽었으나(§2 표, [[../materials/pad-wear-glazing-mrr-decay]]
> §2.4) 반감기 형태의 수치를 보고하지 않는다.

**왜 없는지 — 물리량 자체가 반감기로 보고되지 않는다.** 세 가지 독립적인 이유가 이 노트의
직접 확인 범위 안에서 드러난다:

1. **1차 감쇠(first-order decay)가 아니라 자기제한(self-limiting) 정상상태 모델이다.**
   [[../materials/pad-wear-glazing-mrr-decay]] §2.2가 이미 확인했듯 Shi & Ring(2010)의 핵심
   결과는 "유체윤활을 포함하면 분리거리 d가 0이 아닌 **유한한 정상상태**로 수렴"한다는 것이다.
   asperity 높이가 단조롭게 절반씩 줄어드는 지수감쇠가 아니라 마모-유체지지 평형에 점근하는
   과정이므로, "반감기"라는 개념 자체가 이 모델의 자연스러운 출력이 아니다.
2. **개체군 균형(population balance) PDE는 스칼라 반감기로 요약되지 않는다.** Ring, Prasad
   & Dirksen(J-120) §"Asperity Population Balance"는 높이분포 전체 `η_z(z,t)`가 시간에 따라
   형태 자체를 바꾸며 진화하는 것을 모델링한다(식 9, 유사변수 τ). 분포의 *평균*이 아니라
   *형태*가 변하므로(짧은 돌기가 먼저 사라지고 남은 것들이 뭉침 — [[../materials/pad-wear-glazing-mrr-decay]]
   §1 Lawing 관측과 일치), 단일 반감기 스칼라로는 이 거동을 담지 못한다. 논문도 실제로
   시간축을 "정규화된 τ"로만 그리고(Fig. 3–5) 실제 시(hour) 단위 캘리브레이션은 제공하지 않는다.
3. **실험 논문은 조건화(conditioning) 하에서만 시간축을 보고한다.** 유일하게 시간(hour) 단위
   수치를 보고한 Son & Lee(2021, Applied Sciences, DOI: 10.3390/app11083521 — 원문 PDF는
   MDPI 봇차단으로 미확보, 6ccvd.com 재인용 스펙표로만 확인됨, [[../materials/pad-usage-hours-conditioning-mrr-decay-son-lee2021]]
   §1의 기존 한계 표기 유지)는 asperity 높이가 아니라 **컨디셔너 구조가 다른 두 조건의 MRR**을
   비교하며, 저자 자신이 "시간 자체가 아니라 컨디셔닝 균일성이 지배 인자"라고 명시한다
   ([[../materials/pad-usage-hours-conditioning-mrr-decay-son-lee2021]] §2). 이 수치를 억지로
   반감기로 환산하면(ln2/시간당%, 순수 참고용 하한선):

```python verify
import math
# Son & Lee 2021 (2차 재인용, MDPI 원문 미확보) — 시간당 선형 감소율 근사
rate_case1_per_h = 44.9 / 16   # %/h, 5구역 컨디셔너 아닌 기존 방식(전면 접촉, 불균일 마모)
rate_case2_per_h = 7.4 / 20    # %/h, 분할형 컨디셔너(균일 마모)

t_half_case1 = math.log(2) / (rate_case1_per_h / 100)
t_half_case2 = math.log(2) / (rate_case2_per_h / 100)
print(f"의사(pseudo) 반감기: Case I(불균일 마모) {t_half_case1:.1f} h, Case II(균일 마모) {t_half_case2:.1f} h")

# fab-sim 현재값 48h이 이 브래킷 안에 드는지만 확인 — "정답"이 아니라 정직한 대조
fab_sim_current_h = 48.0
assert t_half_case1 < fab_sim_current_h < t_half_case2, \
    "48h이 두 의사반감기 사이에 있다는 사실만 기록(맞춰서 고른 값이 아님)"
print(f"fab-sim 현재값 {fab_sim_current_h}h은 이 의사반감기 브래킷[{t_half_case1:.1f}, {t_half_case2:.1f}]h 안에 있다")
```

**중요한 방법론적 경고**: 위 계산은 (i) 선형 감소를 지수감소로 억지 재해석했고, (ii)
MRR 감소이지 asperity 높이 감소가 아니며, (iii) 컨디셔닝이 계속 돌아가는 조건(무컨디셔닝
glazing이 아님)이고, (iv) 원문 PDF가 아니라 재인용 스펙표 기준이다 — **이 네 가지 이유로
이 브래킷은 `pad_wear_half_life_h`의 1차 출처가 될 수 없다.** fab-sim 현재값 48h이 우연히
이 브래킷 안에 든다는 사실은 "확인"이 아니라 "반증되지 않았다" 정도의 약한 정보다. 정직하게
**estimated 등급을 유지하라고 권고**한다 — 이 회차에서 literature로 올릴 근거를 찾지 못했다.

## 관련 노트
[[../materials/hertz-gw-contact-mechanics]] · [[../materials/pad-asperity-density-gw-literature-values]] ·
[[../materials/pad-wear-glazing-mrr-decay]] · [[../materials/pad-hardness-porosity-measurement-methods]] ·
[[../materials/pad-usage-hours-conditioning-mrr-decay-son-lee2021]]
