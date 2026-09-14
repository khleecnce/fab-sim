<!-- V2-SECTION: R2-slurry | 근거: chemistry, cobalt, ruthenium, complexing agent, EDA, citric acid, oxidizer-free | 정본: ARCHITECTURE-V2.md §3 -->
# 코발트·루테늄 CMP의 착화제(EDA·시트르산) — χ가 놓치고 있는 "산화제 이외" 화학 드라이버와 무산화제 기계 하한 (slurry-chemistry Lv3-1)

> 에이전트: slurry-chemistry Lv3-1 | 작성일: 2026-09-14
> 선행: [[oxidizer-redox-potential-decomposition-metal-suitability]] (산화제 E°가 만드는 열역학 구동력),
> [[inhibitor-chelator-adsorption-isotherm-passivation]] (Cu용 억제제=흡착 vs 킬레이트=착화의 정성 구도 — 이 노트는 그 구도를
> **Co·Ru라는 다른 금속계**에서 정량 재현하고, χ 파라미터 팩에 실제로 빠져 있는 드라이버로 좁힌다),
> [[stop-layer-chemistry-design-principles-oxide-nitride-cu-barrier-w-oxide]] (Class B/C 금속 CMP의 산화환원 축 구분),
> [[low-level-metal-cobalt-ruthenium-cross-contamination]]
>
> **겨냥하는 갭**: `validation/MODEL-BASIS.md` χ 절 — `cu_h2o2_bta`·`w_fe_oxidizer` 두 팩은 드라이버가
> `[oxidizer_wt_pct, slurry_ph]`로 선언돼 있지만 실제 활성 항은 `oxidizer` 하나뿐이다(`slurry_ph`는 선언만 되고 미사용).
> 이 노트는 "산화제 농도 말고 무엇이 χ를 움직이는가"를 Co/Ru 1차 문헌 수치로 못박고, 그 드라이버가 **왜 지금 `slurry_ph`
> 자리에 숨어있는 게 아니라 별도 축(착화제 농도)이어야 하는지**를 보인다. 또한 **무산화제(oxidizer=0) 슬러리가 실측으로
> 존재**한다는 사실 자체가 `oxidizer_mech_floor`(현재 φ=0.14, W계 단일 출처)의 재료계 간 일반성을 시험하는 두 번째·세 번째
> 독립 관측을 준다.

## 1. 1차 출처 (실존 확인·전문 확보)

- **Xu, Ma, Liu, Tan, Zhang, Wang, Song (2022)**, "Effect of ethylenediamine on CMP performance of ruthenium in
  H2O2-based slurries," *RSC Adv.* 12, 228–240, DOI: https://doi.org/10.1039/d1ra08243d (Crossref 확인, 전문 확보
  `papers/xu2021-ru-eda-cmp-d1ra08243d.pdf`, 이미 로컬 코퍼스에 있던 파일 — 재사용). Ru CMP에서 **에틸렌디아민(EDA)
  착화제**가 산화제(H2O2)와 독립이 아니라 산화물에만 반응하는 **곱셈형 게이트**임을 CMP 실험·전기화학·XPS로 정량 확립.
- **Popuri, Sagi, Alety, Peethala, Amanapu, Patlolla, Babu (2017)**, "Citric Acid as a Complexing Agent in Chemical
  Mechanical Polishing Slurries for Cobalt Films for Interconnect Applications," *ECS J. Solid State Sci. Technol.*
  6(9) P594–P602, DOI: https://doi.org/10.1149/2.0111709jss (CC-BY, 전문 확보 `papers/popuri2017-jsst-co-citric-acid-cmp.pdf`
  — [[inhibitor-chelator-adsorption-isotherm-passivation]] §1이 이미 이 논문을 pKa 출처로 인용했으나 **정량 RR/DR 데이터는
  거기서 다루지 않았다** — 이 노트가 신규로 추출). Co CMP에서 **시트르산**이 시트르산·과산화수소·pH 3축을 이룰 때 나타나는
  포화형 반응과 무산화제(순수 기계) 하한을 정량 제공.
- 로컬 코퍼스(`data/corpus/corpus.sqlite`, OA 1197건 중) 검색으로 Co CMP 관련 1차 논문 20건 이상을 추가 확인했으나
  (예: 아스파르트산·글루타치온·디에탄올아민 등 착화제/억제제 논문) 이 단원의 스코프(화학 반응성 축, 최대 6건)를 넘어서므로
  본문에는 인용하지 않음 — "못 찾았다"가 아니라 "범위 상한으로 제외"로 기록.

## 2. 겨냥한 갭의 정확한 위치

`validation/MODEL-BASIS.md` χ 절(팩별 상태 표)을 보면:

| 팩 | 드라이버(선언) | 항(실사용) |
|---|---|---|
| cu_h2o2_bta | oxidizer_wt_pct, slurry_ph | oxidizer×1.000 |
| w_fe_oxidizer | oxidizer_wt_pct, slurry_ph | oxidizer×1.000 |

`slurry_ph`가 드라이버로 선언만 되고 항에 없다는 것은 두 가지로 해석될 수 있다: (a) pH는 사실 χ에 안 들어가야 하는데
잘못 선언됐다, 또는 (b) pH가 들어갈 자리가 있는데 그 자리를 만드는 화학종(착화제)이 파라미터 팩 자체에 없어서 죽어있다.
Ru·Co 문헌은 **(b)가 맞다**는 것을 보여준다 — pH는 산화물 자체의 안정성(§3)뿐 아니라 **착화제의 양성자화 상태**를 통해서도
χ에 들어가는데, 지금 팩에는 착화제 농도 필드 자체가 없다.

## 3. Ru CMP: EDA는 산화제의 대체물이 아니라 곱셈 게이트다 (Xu 2022)

Ru은 안정한 귀금속에 가까운 금속이라(표준전위 Ru²⁺/Ru +0.45 V vs SHE, 논문 §3.6) 단독 산화제만으로는 CMP 제거율이
잘 안 오른다. Xu 2022는 5 wt% SiO2·pH 9 슬러리에서 H2O2와 EDA(에틸렌디아민, 2개의 아미노기를 가진 착화제)를 **각각
단독으로, 그리고 함께** 스윕해 다음을 정량했다(Fig. 1–2 본문 수치):

- H2O2 단독(EDA=0): 0→0.15 wt%까지 RR 상승 후 0.15 wt% 초과부터 하락 — **정점형**(cu_h2o2_bta/oxide_silica의
  기존 pH 정점형 함수와 같은 형태가, 여기서는 오히려 오염축인 산화제 축에서도 나타난다는 교차 확증).
- EDA 단독(H2O2=0, 즉 **산화제 농도=0의 무산화제 조건**): RR이 EDA 0→40 mM 범위에서 **48~67 Å/min 사이를 오르내릴
  뿐 단조 증가하지 않는다** — "착화제만으로는 거의 효과 없음"(논문 결론 문장 그대로).
- H2O2(0.15 wt%, 정점 농도로 고정) + EDA 0→40 mM: RR이 **116 → 375 Å/min**로 뚜렷이 상승.
- XPS(Table 3): EDA 처리 후 표면 Ru 금속 피크 비율이 47.5%→58.9%로 늘고 RuO2·RuO3 산화물 피크가 줄어든다 — EDA가
  **산화물을 벗겨내지 금속 Ru 자체를 공격하지 않는다**는 직접 증거.

이 세 조건을 합치면 메커니즘이 명확해진다: EDA는 질소 lone pair로 **이미 산화제가 만든 RuO2·RuO3와 착물**을 만들어
용해를 촉진할 뿐, 산화물이 없으면(H2O2=0) 착화할 대상이 없어 거의 무력하다. 즉 **곱셈 게이트**(oxidizer가 0이면
complexing 항도 사실상 1)이지, χ에 독립 가법항으로 넣을 대상이 아니다.

```python verify
# Xu, Ma, Liu, Tan, Zhang, Wang, Song 2022, RSC Adv. 12, 228-240, DOI: 10.1039/d1ra08243d
# Fig.2: Ru RR (5 wt% SiO2, pH 9), 0.15 wt% H2O2 (peak conc) + EDA 0->40 mM: 116 -> 375 Angstrom/min
# Fig.2b: H2O2 = 0 (oxidizer-free), EDA 0->40 mM 전 구간에서 RR 48~67 Angstrom/min 사이 요동(단조 증가 아님)
RR_ref_no_EDA = 116.0    # 0.15 wt% H2O2, EDA 0 mM
RR_ref_EDA40 = 375.0     # 0.15 wt% H2O2, EDA 40 mM
RR_floor_lo = 48.0       # oxidizer = 0, EDA 스윕 하한
RR_floor_hi = 67.0       # oxidizer = 0, EDA 스윕 상한

floor_frac_lo = RR_floor_lo / RR_ref_no_EDA
floor_frac_hi = RR_floor_hi / RR_ref_no_EDA
assert 0.35 < floor_frac_lo < floor_frac_hi < 0.65

# 곱셈 게이트 가설: 기준 산화제 농도에서 EDA가 만드는 "복합제 배수"
complexing_gain_at_ref_oxidizer = RR_ref_EDA40 / RR_ref_no_EDA
assert 3.0 < complexing_gain_at_ref_oxidizer < 3.5

print(f"[Xu 2022, DOI:10.1039/d1ra08243d] oxidizer=0 기계 하한 비율 = "
      f"{floor_frac_lo:.2f}~{floor_frac_hi:.2f} (W계 φ=0.14보다 높음 — 재료계 다름, §5)")
print(f"[Xu 2022] 기준 산화제 농도에서 EDA 0->40mM 배수 = {complexing_gain_at_ref_oxidizer:.2f}배")
```
문헌값과 대조한 재현 결과: oxidizer=0 기계 하한 비율 0.41~0.58배(48/116~67/116), EDA 0→40mM 배수 3.23배 —
둘 다 위 assert 통과, Xu 2022 Fig.1–2의 116·375·48·67 Å/min 그대로 재계산한 값이다.

전기화학 데이터(Table 1, Tafel 피팅)는 착화제 농도가 부식전류밀도 Jcorr를 통해 얼마나 표면 반응성을 올리는지 독립적으로
보여준다:

```python verify
import numpy as np
# Xu et al. 2022, RSC Adv. 12, 228 Table 1 (Ru 개회로전위 Tafel 외삽), DOI: 10.1039/d1ra08243d
EDA_mM = np.array([10, 20, 30, 40])                       # 0 mM은 로그축 제외
Jcorr = np.array([3.451e-5, 4.536e-5, 6.313e-5, 1.111e-4])  # A/cm^2
Jcorr_0mM = 5.843e-6                                       # EDA=0 mM, 배수 계산용

logE, logJ = np.log(EDA_mM), np.log(Jcorr)
slope, intercept = np.polyfit(logE, logJ, 1)
pred = np.exp(intercept) * EDA_mM ** slope
r2 = 1 - np.sum((Jcorr - pred) ** 2) / np.sum((Jcorr - Jcorr.mean()) ** 2)
fold_0_to_40 = Jcorr[-1] / Jcorr_0mM

assert 0.5 < slope < 1.2      # 대략 선형에 가까운 거듭제곱 — 문헌 폐형식은 아님, 4점 최소자승
assert r2 > 0.8
assert 18.0 < fold_0_to_40 < 20.0

print(f"[Xu 2022 Table 1] Jcorr ~ EDA_mM^{slope:.2f} (R^2={r2:.2f}); "
      f"0->40mM 부식전류 배수 = {fold_0_to_40:.1f}배")
```
문헌값과 대조한 재현 결과: Jcorr ~ EDA_mM^0.78(R²=0.84), 0→40mM 배수 19.0배 — Table 1의 5.843e-6→1.111e-4 A/cm²를
그대로 재계산한 값이다. 지수 0.78은 **이 논문 4점의 최소자승 피팅**이지 문헌 폐형식이 아니다 — 등급은 literature(단일
논문, 단일 재료계).

## 4. Co CMP: 시트르산도 같은 문법(산화물에만 반응) — 그리고 포화·과잉산화제 억제 (Popuri 2017)

Popuri 2017은 CVD Co 박막을 3 wt% 콜로이달 실리카·H2O2·시트르산(50 mM)으로 pH 4~10 전 구간에서 스윕했다. 핵심
발견 세 가지:

1. **무산화제·무착화제 기계 하한**: pH 4, 물+3 wt% 실리카만(H2O2=0, 시트르산=0)으로도 **RR ≈ 140 nm/min**이 나온다
   (§4.1, 본문 "RR of ~140 nm/min with 3 wt% silica were measured at pH 4"). 이는 Cu/W 계 문헌(`oxidizer_mech_floor`,
   US20110186542A1)과 마찬가지로 **산화제가 전혀 없어도 순수 기계 연마가 0이 아니다**는 것을 Co 금속에서 다시 확인한
   독립 사례다.
2. **시트르산의 산화물 특이성**: "시트르산이 Co 산화물과 착물[Co(C6H5O7)2]³⁻을 만든다"(초록)는 서술과, H2O2를 0→0.1→1→5
   wt%로 올리며 시트르산을 고정했을 때 RR이 **정점형**(0.1 wt%에서 낮음 → 1 wt%에서 325–400 nm/min 최고 → 5 wt%에서
   재하락)으로 움직인다는 관측(§4.3, Fig. 3)은 Ru/EDA와 **같은 문법**: 착화제는 산화물이 있어야 일하고, 산화제가
   과잉이면(5 wt%) 오히려 "산화 속도가 착화 속도를 추월"해서(원문 표현) RR·DR이 함께 떨어진다.
3. **착화제 농도 자체도 포화한다**: 시트르산을 50→500 mM로 올리면 100 mM을 넘어서는 더 이상 RR이 오르지 않는다(§4.3,
   "increasing citric acid concentration beyond 100 mM does not increase Co RRs") — 저자들은 이 지점부터 **산화막
   생성 속도(=산화제 농도가 정하는 rate-limiting step)** 가 병목이 된다고 해석한다. 즉 착화제 항도 무한정 선형이 아니라
   **자기 자신의 포화농도**를 갖는 별도 항이어야 한다(기존 `abrasive_wt_pct`의 포화형 항과 같은 구조, 다른 화학종).

```python verify
# Popuri, Sagi, Alety, Peethala, Amanapu, Patlolla, Babu 2017, ECS JSST 6(9) P594-P602
# DOI: 10.1149/2.0111709jss
# Fig.1: pH 4, 물+3wt% 실리카만(oxidizer=0, chelator=0) -> RR ~ 140 nm/min (본문 수치)
# Fig.3: 3wt% 실리카 + 1wt% H2O2 + 50mM 시트르산, pH 7-8에서 RR 정점 325-400 nm/min (본문 수치, 중간값 사용)
RR_floor_water_only = 140.0     # pH 4, 산화제·착화제 둘 다 0
RR_peak_chem = (325.0 + 400.0) / 2  # 1 wt% H2O2 + 50 mM 시트르산 정점 범위의 중간값

floor_frac = RR_floor_water_only / RR_peak_chem
assert 0.30 < floor_frac < 0.45

print(f"[Popuri 2017, DOI:10.1149/2.0111709jss] Co 기계 하한 비율(참고치) = {floor_frac:.2f} "
      f"— ⚠ pH도 4->7~8로 함께 바뀌어 φ의 순수 단일변수 측정은 아님(§5)")
```
문헌값과 대조한 재현 결과: Co 기계 하한 비율 0.39배(140/362.5) — assert 통과, 단 §5에서 밝히듯 pH 교란이 있어
참고치다.

## 5. 산화제 기계 하한 φ — 세 재료계를 나란히 놓으면 "평균 내지 마라"가 맞다

| 재료계 | φ (oxidizer=0 RR / 기준 RR) | 통제 정도 | 출처 |
|---|---|---|---|
| W (H2O2, 15조건) | 0.117~0.189 (평균 0.142) | 산화제만 스윕, 나머지 고정 — **가장 통제됨** | US20110186542A1 |
| Ru (H2O2=0, EDA만 스윕) | 0.41~0.58 | 산화제만 0/0.15wt%로 스위칭, SiO2·pH 고정 — **통제됨** | Xu 2022 |
| Co (물만 vs H2O2+시트르산 정점) | ≈0.39 (참고치) | pH도 4→7-8로 같이 바뀜 — **교란 있음** | Popuri 2017 |

`validation/MODEL-BASIS.md`는 이미 "금속막 CMP 관측 대역 0.12~0.27, 4계 독립 수렴"이라고 적어 φ=0.14를 그 중앙값으로
쓰고 있다. 이번에 새로 확보한 Ru 값(0.41~0.58)은 그 대역을 크게 벗어난다. **평균내지 말라**는 SCOPE 원칙에 따라 판정하면:
Ru은 귀금속에 가까워 산화물 자체가 상대적으로 무르고(§3, RuO2·2H2O·RuO3는 밀착 산화막이 아니라 다공질) 기계 연마가
차지하는 몫이 원래 더 크다고 해석하는 것이 W/Cu 계(Pourbaix상 더 견고한 부동태 산화막)와 **다른 레짐**이라는 설명과
정합적이다 — 재질에 따라 φ 자체가 달라질 수 있다는 뜻이지, 기존 대역이 틀렸다는 뜻이 아니다. Co 값(0.39)은 pH가 같이
바뀌어 순수 φ로 못 쓰지만(→ "참고치"로만 표기) Ru 값과 같은 방향(0.3대 이상)이라 서로 교차확증은 된다.

## 6. 구현 관점 요약 (상세 수식·근거·우선순위는 PROFILE.md `## 구현 요청`에 기재)

- χ 파라미터 팩에 **`complexing_agent_conc_mM`** 필드가 없다 — 있어야 `slurry_ph` 드라이버가 죽어있지 않고 착화제의
  양성자화 분율을 통해 실제로 쓰일 자리가 생긴다.
- 착화제 항은 산화제 항에 **곱해야** 한다(가법이 아님) — oxidizer=0이면 착화제 농도를 아무리 올려도 효과가 거의 없다는
  것이 Ru·Co 양쪽에서 재현됐다(§3–4).
- 착화제 항도 산화제 항처럼 **자체 포화농도**를 가진다(Co: 임계 ~100 mM) — 단순 선형/거듭제곱이 아니라 상한이 있는 함수.
- `oxidizer_mech_floor` φ는 **재료(금속종)마다 다른 값을 가질 자유도**가 필요하다 — 현재처럼 전 팩 공통 φ=0.14를 쓰면
  Ru계(φ 실측 0.41~0.58)에서 무산화제 조건의 MRR을 과소평가한다.

## 7. 한계·미검증

- Ru·Co 각각 **단일 논문**에서 뽑은 값이다(문헌 서열상 "통제실측"이지만 재료계당 1건 — 교차확증 부족). 다른 착화제
  (구아니딘, EDTA, 아스파르트산 등, 코퍼스에 20건 이상 존재)로 일반화되는지는 미검증.
- Co의 φ≈0.39는 §5에서 밝혔듯 pH가 같이 바뀌는 교란이 있어 **순수 φ가 아니라 참고치**다.
- Jcorr(부식전류밀도)를 CMP 제거율의 직접 대리변수로 쓰는 것은 화학용해 성분에는 타당하나 CMP는 기계-화학
  시너지가 있어 Jcorr↑가 곧 RR↑ 비율과 같다는 보장은 없다 — 이 노트는 "방향과 대략적 크기"만 주장하고 절대 배수
  전이는 미검증으로 남긴다.
- 착화제 포화농도(Co: ~100 mM)의 함수형(Langmuir형인지, 다른 포화형인지)은 원문에 그래프만 있고 수치표가 없어
  **폐형식을 못 얻었다** — "포화가 있다/없다"의 정성 판정만 확실하고, 정확한 반포화농도(K_half)는 미검증.
- EDA·시트르산 모두 **BEOL 배리어/라이너 금속(Ru) 또는 라이너(Co)** 용도 문헌이지 순수 인터커넥트 벌크 Cu 대체를
  겨냥한 게 아니다 — 이 노트의 결론(곱셈 게이트·포화)이 Cu 자체(예: 글리신-Cu, 이미 [[inhibitor-chelator-adsorption-isotherm-passivation]]
  §5–7에서 정량화됨)에도 같은 형태로 적용되는지는 두 노트를 나란히 놓아 봐야 하며, 이 노트에서 직접 재현하지 않았다.
