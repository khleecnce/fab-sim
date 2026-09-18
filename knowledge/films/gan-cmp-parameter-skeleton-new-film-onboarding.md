# 신소재 파라미터 세트 골격 정의 — GaN(질화갈륨)을 사례로

> Lv3-2. 물질명 하나에 매몰되지 않기 위해, 이 노트의 목적은 "GaN 값 몇 개를 구하는 것"이
> 아니라 **"새 막질이 sim/tier2 에 들어올 때 어떤 물성 축이 있어야 모델이 서는가"** 라는
> 절차를 GaN 사례로 검증하는 것이다. `knowledge/params/*.yaml` 은 읽기만 했고 수정하지
> 않았다(sic_ceria_h2o2.yaml, w_fe_oxidizer.yaml, oxide_silica.yaml, base.yaml 대조 확인).

## 0. 왜 GaN인가

전력/RF 반도체용 GaN CMP는 2000년대부터 축적된 1차 문헌이 있고(콜로이달 실리카 슬러리가
표준), 최근에는 "화학적으로 너무 안정해서 상온 슬러리로는 잘 안 깎인다"는 문제를 광전기화학
(UV 보조) CMP로 우회하는 흐름이 있다 — 이것이 **기존 5팩(Cu/W/Co-Ru-Mo/SiC/산화막) 어디에도
없는 새로운 물리 축(광량)을 요구한다는 것**을 보여주는 좋은 사례라 선택했다. 코퍼스에 CMP+GaN
교집합 논문이 30건 이상 있어(`corpus.py`, `WHERE title LIKE '%GaN%' AND title LIKE '%CMP%'`)
"실제로 정량 데이터가 있는" 요건도 만족한다.

## 1. 절차 — 새 막질 온보딩 체크리스트

기존 팩(`sic_ceria_h2o2.yaml`이 가장 완성도 높은 최근 사례)이 실제로 요구하는 키를 그대로
따라가면, 새 막질 하나를 들일 때 확인해야 할 것은 아래 6개 범주로 나뉜다.

| # | 범주 | 대응 yaml 키(기존 팩 관찰) | 왜 필요한가 |
|---|------|---------------------------|------------|
| 1 | 기계(경도) | `film_bulk_hardness_pa` | `regime_adapter.py::alpha_from_bulk_bound` — 접촉이 탄성(α=2/3)인지 소성(α=3/2)인지 결정. **이것이 유일하게 코드가 실제로 소비하는 기계 물성이다** — 탄성계수는 소비처가 없다(§2.2). |
| 2 | 화학(반응 경로) | `oxidizer`, `oxidizer_langmuir_K`, `oxidizer_langmuir_species`, `oxidizer_wt_pct`(+`_ref`) | χ 항. 산화제가 표면을 무른 산화물로 바꾸고 연마입자가 그것을 벗긴다는 Kaufman형 경쟁모델의 산화제 쪽 절반. |
| 3 | 화학(정전기) | `wafer_iep_ph`, `slurry_ph`, `ph_ref`, `ph_softening_per_unit`(+`_ref`) | 등전점 기준 슬러리 pH 위치로 입자-표면 정전 인력/반발, 표면 연화 정도를 결정. |
| 4 | 연마입자-막질 쌍 | `abrasive`, `abrasive_size_nm`(+peak/exponent류), `abrasive_conc_exponent`, `abrasive_wt_pct`(+`_ref`), `abrasive_density_kg_m3` | κ 항(접촉강도) + 피복률. 입자 자체는 슬러리 공급업체 물성이라 막질과 독립이지만, 입경-MRR 정점 위치는 막질/화학계마다 다르다(sic_ceria §"세리아 입경-MRR 정점" 참조). |
| 5 | Preston 계수 자체 | `kp_m_per_pa` | 이 저장소의 설계원칙(ARCHITECTURE-V2.md, base.yaml 주석)상 **막질이 바뀌면 반드시 이 값도 새로 역산해야 한다** — 상속 금지(sic_ceria.yaml 판정#49가 정확히 이 사고를 다룬다: SiO2용 Kp를 SiC에 그대로 물려써서 164배 과대예측). |
| 6 | 진단 전용(손상) | `damage_exponent`, `scratch_threshold_nm`, `pad_asperity_hardness_max_pa`(공용) | Δ항. 스크래치 임계값 — 화학종마다 다를 수 있으나 현재 5팩 모두 공통 base 값을 씀. |

**이 표 자체가 이번 단원의 산출물이다.** 아래 §2 는 이 6범주를 GaN에 대입했을 때 "문헌에
있음"과 "없음(→R8 실측 필요)"을 가른 결과다.

## 2. GaN 대입 결과

### 2.1 경도 (범주 1) — **문헌 있음**

Dong, Zhang, Peng, Jin, Wan, Xue, Yi (2022), *Materials* 15(3), 1210,
DOI: 10.3390/ma15031210 (MDPI, Gold OA, 원문 확보·fitz 전문 판독). Hysitron TI 980
Berkovich 나노압입, c면 wurtzite GaN 단결정(HVPE, 무결함), 하중 10 mN, 20회 이상 압입 평균:

> "For the unirradiated GaN single crystals, the hardness is 19.2 ± 0.2 GPa,
> consistent with reported values in the literature [8,9]."

→ `film_bulk_hardness_pa = 1.92e10` (범위 ±0.2 GPa 로 매우 좁음 — 단결정 3축 방향 c면 값).
같은 표(Table 1)에 이온조사량에 따른 경도 증가(19.2→23.2 GPa)도 있으나 CMP 대상은 비조사
GaN이므로 무관.

### 2.2 탄성계수 (범주 1의 일부) — **문헌 탐색 실패 + 구조적으로 안 쓰인다**

같은 논문이 Hertzian 탄성접촉식 `P = (4/3)E*√R h^(3/2)` 을 도입은 하지만, 다이아몬드 압입자의
`E_i=1141 GPa, ν_i=0.07`만 명시하고 **GaN 자체의 환산탄성계수 E*나 영률 수치는 본문에 없다**
(그래프로만 제시, §3 Fig.2 피팅). 별도로 찾은 두 논문도 실패했다:
- Wei, Zhang, Zhang 외(2021), *Chin. Phys. B*, DOI: 10.1088/1674-1056/abfd9e —
  abstract에 "c면에서 육각형 대칭 전위슬립"만 있고 H·E 수치는 본문(구독 필요)에만 있어
  **초록만 확인, 미확보**.
- Polian, Grimsditch, Grzegory (1996), *J. Appl. Phys.* 79(6) 3343,
  DOI: 10.1063/1.361236 — 이 저장소 스코프가 요구하는 무료 전문 경로(Unpaywall/Semantic
  Scholar 초록 API)가 전부 막혀(`abstract: null`, AIP 403) **탐색 실패**로 종결.

⚠ 이 실패는 **결과에 영향이 없다** — sim/regime_adapter.py 의 α 판정
(`alpha_from_bulk_bound`)이 실제로 코드에서 쓰는 입력은 `film_bulk_hardness_pa` 하나뿐이고,
탄성계수는 어느 파일에도 소비처가 없다(§1 표 확인용으로 `grep -i modulus knowledge/params/*.yaml`
결과 base.yaml 의 패드 E* 3건뿐, 막질 E는 0건). base.yaml 이 "웨이퍼가 패드보다 400배 이상
강성이라 단일물체식으로 수렴한다"고 가정하는 지점(pad_E_star_pa 주석)에서도, 그 부등식은
**어떤 결정질 고체든(E > 수십 GPa) 패드 E*=131.6 MPa 을 가볍게 넘으므로** GaN E의 정밀값이
없어도 그 가정은 정성적으로 안전하다(§4 verify (a)에서 수치로 확인).
→ **결론: "탄성계수가 필요하다"는 절차서의 직관은 이 저장소의 현재 구현에서는 틀렸다.**
필요한 것은 하드니스뿐이고, 탄성계수는 (a) 미확보이며 (b) 확보해도 쓸 곳이 없다.

### 2.3 화학/반응 경로 (범주 2) — **문헌 있음, 그러나 기존 산화제 모델 정의역 밖**

GaN은 III-V 반도체 중에서도 화학적으로 매우 불활성이라(넓은 밴드갭·강한 Ga-N 결합),
상온·상압 습식 산화제만으로는 W/Cu처럼 빠르게 산화막을 만들지 못한다. 그래서 최근 문헌은
**자외선(UV) 조사로 광생성 정공(photo-hole)을 만들어 산화를 촉진**하는 광전기화학
CMP(photoelectrochemical-mechanical polishing, PECMP)로 수렴한다:

Wei, Zhang, Zhang, Ma, Yuan(2022), *ECS J. Solid State Sci. Technol.* 11, DOI:
10.1149/2162-8777/ac5807 (IOP, 전문은 봇차단(Radware Captcha)으로 미확보 — **WebFetch로
초록만 확인**). 초록 원문:

> "MRR of GaN was as high as 404.6 nm h⁻¹ by using the sodium hypochlorite as the oxidant
> under UV, with surface roughness (Ra) of 1.61 nm; MRR of GaN was 380.3 nm h⁻¹ by using
> H2O2 as the oxidant under UV, with surface roughness (Ra) of 0.065 nm."

→ (Wei et al. 2022) NaOCl+UV: 404.6 nm/h(6.743 nm/min), H2O2+UV: 380.3 nm/h(6.338 nm/min). **UV 없는 대조군
수치는 초록에 없다** — 그러나 "UV 하에서"라는 조건절 자체가 저자들이 UV 유무를 독립변수로
다뤘다는 뜻이고, 아래 §2.4의 Aida 2011(비-UV, 17 nm/h)과 비교하면 22~24배 차이가 나 방향은
일치한다(다만 슬러리·pH·압력이 다른 논문이라 순수 UV 효과로 귀속할 수 없다 — 교란변수 있음,
E4급 교차비교).

Xian, Zhang, Liu, Wu, Wang, Liu, Cui(2024), *ECS J. Solid State Sci. Technol.*, DOI:
10.1149/2162-8777/ad1c89 (CC-BY, 전문은 봇차단으로 미확보, Semantic Scholar 초록 확인).
K2S2O8(과황산칼륨, 강산화제) 첨가가 표면조도 개선에 유효함을 보고(Sq 7.7→0.78 nm) — 이
논문은 **연마율(MRR) 자체를 초록에서 보고하지 않는다**(조도 최적화가 목적). → 산화제 종
축은 채워지지만 정량 Langmuir K 축(오차제_langmuir_K류)은 **미확보**.

→ **구조적 함의**: 기존 `sim/chemistry.py` 의 산화제 항(예: SiC 팩의
`oxidizer_langmuir_K`)은 "농도만 바뀌는 정적 화학"을 전제한다. GaN은 그 축 위에 **"UV
조사 여부/광량"이라는 완전히 새로운 독립변수**가 곱해진다 — 이는 어떤 기존 5팩에도 없는
입력이다(Co/Ru/Mo/SiC/산화막 전부 암실·상온 습식화학). 새 축 자체가 팩 스키마에 없으므로
"문헌 없음"이 아니라 **"물어볼 칸이 없다"**는 것이 이번 조사의 핵심 발견이다(§5 구현요청).

### 2.4 Preston 계수 (범주 5) — **문헌 있으나 P·V 짝을 못 구해 역산 불가**

콜로이달 실리카를 쓴 비-UV 표준 CMP 문헌:
Aida, Takeda, Koyama, Katakura, Sunakawa, Doi(2011), *J. Electrochem. Soc.* 158(12) H1206,
DOI: 10.1149/2.024112jes (IOP, 전문 봇차단·Semantic Scholar도 초록 비공개 — **WebFetch로
논문 페이지 메타/일부 텍스트만 확인**):

> "Removal rate of GaN was 17 nm/h under typical polishing conditions. An atomically flat
> surface with Ra = 0.1 nm was achieved after CMP."

MRR = 17 nm/h = 0.2833 nm/min. **그러나 "typical polishing conditions"의 압력·상대속도
수치가 WebFetch로 접근한 범위(초록+메타데이터)에는 없다** — 본문 표에만 있을 것으로
추정되나 IOP 봇차단으로 확인 실패. → `kp_m_per_pa` 를 **자기선언 역산할 1차 데이터가
없다**(sic_ceria.yaml의 Wang et al. DOE처럼 P·V·조성·MRR이 모두 나온 표를 찾지 못함).

> ⚠ 1차 출처 확보 실패(부분): Aida 2011·Wei 2022·Xian 2024 세 편 모두 **원문 PDF가 IOP
> Radware 봇차단(캡차)에 막혀 있다** — DOI/초록/일부 인용 텍스트만 WebFetch로 확인했다.
> 시도한 경로: `find_open_access.py`(Unpaywall landing만 반환, pdf 필드 없음),
> curl 직접(HTML 캡차 페이지 회신), `/xml` 엔드포인트(Radware 캡차), WebFetch(초록까지만
> 렌더링). Semantic Scholar API로 Aida 2011은 `abstract: null`(퍼블리셔가 필드 삭제).
> **R8 필요**: 이 세 논문의 압력·rpm·시간 표(보통 Table 1~2)를 확보하면 `kp_m_per_pa`
> 자기선언이 즉시 가능하다.

### 2.5 등전점(IEP, 범주 3) — **직접 문헌 없음 → Ga2O3 대리값(교차물질)**

GaN 자체(질화물 표면)의 등전점을 보고한 1차 문헌은 이번 조사(코퍼스 316건 GaN 관련 문서
전수 제목 스캔 + WebSearch)에서 찾지 못했다. 대신 **CMP 화학이 실제로 겨냥하는 표면
산화생성물인 β-Ga2O3**(GaN을 산화시키면 만들어지는 바로 그 화학종, §2.3)의 제타전위 문헌은
확보했다:

Mandal, Arts, Knoops, Cuenca, Klemencic, Williams(2021), *Carbon* 183, DOI:
10.1016/j.carbon.2021.04.100 (arXiv:2104.01048, 원문 PDF 직접 확보·fitz 전문 판독).
β-Ga2O3(단결정, Tamura Corporation 상용 CMP 웨이퍼 — **이미 한 번 CMP된 기판**이라는 점도
교차확인) 제타전위 vs pH 실측:

> "The ζ-potential of the β-Ga2O3 substrate was measured and it was found to be negative
> with an isoelectric point at pH ∼4.6."

→ `wafer_iep_ph ≈ 4.6`(β-Ga2O3 기준). ⚠ **교차물질 전이(E4)**: GaN 표면이 아니라 GaN이
산화됐을 때 생기는 화학종의 IEP다. 그러나 이 대리값은 sic_ceria.yaml이 "SiC **분말**
IEP(4.9)를 SiC **단결정 웨이퍼** IEP로 전이"한 것(§ wafer_iep_ph 주석, EVIDENCE-RULES E4)과
**같은 등급의 근거**이며, 오히려 GaN의 경우는 "산화되지 않은 GaN 자체"가 아니라 "CMP가 화학
반응으로 실제 만들어내는 표면종"의 IEP라는 점에서 **더 직접적**이다(SiC는 최소한 산화되지
않는데, GaN은 CMP 중 정확히 Ga2O3 유사종으로 바뀐다 — §2.3).

### 2.6 연마입자-막질 쌍 (범주 4) — **부분 있음**

세 문헌(Aida 2011, Wei 2022, Xian 2024) 전부 **콜로이달 실리카**를 연마입자로 쓴다 —
`abrasive: silica`, 기존 `oxide_silica.yaml` 팩과 **같은 연마입자**라 밀도
(`abrasive_density_kg_m3`, SiO2 2200 kg/m³)는 그대로 상속 가능하다(연마입자 고유물성이라
막질 무관, base.yaml/sic_ceria.yaml과 같은 논리). 그러나 **입경(nm)·입경-MRR 정점 곡선은
GaN 전용 실측이 없다** — 세 논문 모두 초록/메타 수준에서는 입경을 명시하지 않는다(본문
Table 접근 실패, §2.4와 같은 봇차단 사유).

## 3. 축별 요약표

| 축 | yaml 키 | GaN 값 | 상태 | 근거 |
|---|---|---|---|---|
| 경도 | `film_bulk_hardness_pa` | 1.92e10 Pa (19.2 GPa) | **문헌 있음** | Dong 2022, DOI 10.3390/ma15031210 |
| 탄성계수 | (스키마에 없음) | — | **탐색 실패 + 모델 미소비** | §2.2 |
| 등전점 | `wafer_iep_ph` | ≈4.6 (Ga2O3 대리) | **문헌 있음(교차물질)** | Mandal 2021, DOI 10.1016/j.carbon.2021.04.100 |
| 슬러리 pH | `slurry_ph`/`ph_ref` | — | **미확보(R8)** | 봇차단, §2.4 |
| 산화제 종 | `oxidizer` | H2O2/NaOCl/K2S2O8 후보 있음(정량 K는 없음) | **부분** | Wei 2022, Xian 2024 |
| 산화제 형상(K) | `oxidizer_langmuir_K` | — | **미확보(R8)** | 봇차단 |
| Preston 계수 | `kp_m_per_pa` | — (MRR은 있으나 P·V 없음) | **미확보(R8, 자기역산 불가)** | §2.4 |
| 연마입자 종 | `abrasive` | silica | **문헌 있음** | Aida 2011 외 2건 |
| 입경 | `abrasive_size_nm` | — | **미확보(R8)** | 봇차단 |
| 연마입자 밀도 | `abrasive_density_kg_m3` | 2200 kg/m³(상속 가능) | **문헌 있음(간접)** | oxide_silica.yaml과 동일 연마입자 |
| 손상지수 | `damage_exponent`, `scratch_threshold_nm` | — | **미확보** | GaN 스크래치-D99 실측 문헌 없음 |
| **광량(신규 축)** | **스키마 자체가 없음** | UV 유무가 방향성 확인(§2.3) | **모델 구조 결손** | §5 구현요청 |

## 4. 검증 코드

`(a)` GaN이 실제로 탄성 접촉 레짐에 있는지(§2.2의 "탄성계수 없어도 안전하다" 주장의 근거),
`(b)` 다른 막질(산화막)의 Preston 계수를 GaN에 그대로 물려쓰면 얼마나 틀리는지 — 두 개의
"Preston 외 항"을 계산해 문헌 MRR 오더와 대조한다.

```python verify
# (a) 접촉 레짐 판정 — GW 수치적분이 준 3psi 실접촉압력(base.yaml 문서값, 14.9 MPa,
#     knowledge/params/base.yaml real_contact_area_ratio 주석 + sic_ceria_h2o2.yaml
#     "이때 실접촉 압력은 14.9 MPa" 재인용) 대비 GaN 경도.
H_GaN_pa = 19.2e9          # Dong et al. 2022, DOI 10.3390/ma15031210, Table 1 (0 fluence)
local_contact_pressure_pa = 14.9e6  # base.yaml GW 수치적분 (E*=1.316e8Pa, R=50um, eta=2e8/m^2, 3psi)

ratio = local_contact_pressure_pa / H_GaN_pa
assert ratio < 0.01, f"GaN이 예상과 달리 소성역에 근접 (ratio={ratio:.2e})"
# GaN(19.2GPa)은 이 저장소의 어떤 막질(산화막 9GPa, W 12GPa, SiC 26GPa)보다도 경도가
# 낮지 않은 축에 속하므로, 3psi 표준조건에서는 탄성 레짐(alpha=2/3)이 항상 나온다 —
# "탄성계수를 몰라도 안전하다"는 §2.2 주장의 정량적 근거.
print(f"(a) local_P/H = {ratio:.2e} -> 탄성 레짐 확정 (플라스틱 문턱 1.0 대비 {1/ratio:.0f}배 여유)")

# (b) 산화막용 Preston 계수를 GaN에 그대로 물려쓰면? (oxide_silica.yaml 캘리브레이션점
#     그대로 사용: kp=1.0e-13 m^2/N, P=20.7kPa, V=0.8 m/s)
kp_silica = 1.0e-13   # knowledge/params/oxide_silica.yaml kp_m_per_pa
P_pa = 20700.0
V_mps = 0.8
mrr_borrowed_m_s = kp_silica * P_pa * V_mps
mrr_borrowed_nm_min = mrr_borrowed_m_s * 1e9 * 60

mrr_lit_nm_min = 17.0 / 60.0  # Aida et al. 2011, DOI 10.1149/2.024112jes, "17 nm/h"

overprediction_x = mrr_borrowed_nm_min / mrr_lit_nm_min
assert overprediction_x > 50, (
    f"예상보다 잘 맞음(x{overprediction_x:.1f}) — 재확인 필요"
)
print(f"(b) 산화막 Kp 차용 예측 {mrr_borrowed_nm_min:.2f} nm/min vs "
      f"문헌실측 {mrr_lit_nm_min:.4f} nm/min -> {overprediction_x:.0f}배 과대예측")
# 어긋난 채로 보고한다: GaN(19.2GPa)은 산화막(9GPa)보다 겨우 2.1배 더 단단할 뿐인데
# MRR은 350배 이상 차이난다 — 즉 이 격차의 대부분은 경도차가 아니라 **화학(챤 불활성 +
# 산화제 미보조)**에서 온다는 뜻이다. 원인 전체를 정량 분해하진 못했다(미검증) — 조성비
# 추정일 뿐이며, 상수 (a)의 탄성/소성 판정과 달리 이 (b)는 "왜 이만큼 차이나는지"까지는
# 설명하지 못하는 채로 남긴다.
```

실행 결과(2026-09-18): `(a) local_P/H = 7.76e-04 -> 탄성 레짐 확정 (플라스틱 문턱 1.0 대비
1289배 여유)`, `(b) 산화막 Kp 차용 예측 99.36 nm/min vs 문헌실측 0.2833 nm/min -> 351배
과대예측`. 두 assert 모두 통과 — (a)는 "예상대로 안전하다"는 확인, (b)는 "예상대로 크게
어긋난다"(그래서 GaN 전용 Kp 자기선언이 반드시 필요하다)는 확인이다.

## 5. 구현 요청 (sim/ 은 이 에이전트가 건드리지 않는다 — 근거만 남긴다)

### [P12] 광량(UV) 축 — 기존 5팩 스키마에 아예 없는 신규 차원
- **무엇을**: `sim/chemistry.py`의 χ(산화제)항이 "농도만의 함수"라는 암묵 전제를 갖는데,
  GaN처럼 화학적으로 불활성인 막질은 **자외선 조사 유무·광량(mW/cm²)이 산화 반응 자체를
  켜고 끄는 독립 게이트**로 작동한다(§2.3). 레시피에 `uv_assist: bool`(또는
  `uv_intensity_mw_cm2: float`) 필드를 신설하고, `oxidizer_langmuir_K`류 상수에
  `requires_uv: true` 메타를 붙여, UV 없이 이 상수를 쓰면 경고가 나가게 할 것.
- **근거·검증문헌값**: Wei et al. 2022, DOI: 10.1149/2162-8777/ac5807 — "MRR of GaN was as
  high as 404.6 nm h⁻¹ ... under UV"(NaOCl), "380.3 nm h⁻¹ ... under UV"(H2O2). UV 없는
  대조 수치는 원문 봇차단으로 미확보(§2.4 실패 보고)이나, 저자들이 굳이 "under UV"라고
  조건절을 붙인 것 자체가 UV가 독립 인자임을 시사한다. **회귀 테스트**: `uv_assist=false`
  입력에서 GaN 팩의 산화제 항이 (자기선언된 값이 있어도) 저활성 폴백으로 떨어져야 한다 —
  지금 스키마로는 이 폴백을 표현할 필드 자체가 없다.
- **우선순위**: 낮음(GaN 팩 자체가 아직 없음). 그러나 스키마 결손이라 팩 신설보다 먼저
  풀어야 하는 선행 작업이다 — 팩만 만들면 이 축이 조용히 무시된다(다른 5팩처럼).

### [P13] IEP 교차물질(산화생성물) 전이 규칙의 명문화
- **무엇을**: `wafer_iep_ph`가 지금은 "막질 자체의 등전점"이라는 암묵 전제로 쓰이는데,
  GaN처럼 **CMP 화학이 표면을 다른 화학종(Ga2O3)으로 바꿔놓고 그 화학종의 IEP가 실제
  연마 계면을 지배하는 경우**가 있다(SiC의 산화막 CMP와 원리적으로 다르다 — SiC는
  산화되지 않은 채 기계적으로 깎이지만 GaN은 CMP 중 산화물로 변한다, §2.5). 파라미터
  문서(README든 base.yaml 주석이든)에 "wafer_iep_ph는 막질 자체가 아니라 **CMP가 실제로
  형성하는 표면종의 IEP**를 우선한다"는 규칙을 명문화할 것 — 지금은 5팩 전부(산화막/Cu/W
  등) 우연히 막질=표면종이 같아서 이 구분이 드러나지 않았다.
- **근거**: Mandal et al. 2021, DOI: 10.1016/j.carbon.2021.04.100 — β-Ga2O3 IEP pH 4.6.
- **우선순위**: 낮음(문서화 작업, 코드 변경 없음).

## 6. 한계 (정직하게 남긴다)

- **1차 출처 부분 확보 실패**: Aida 2011·Wei 2022·Xian 2024 세 편의 원문 PDF는 IOP
  Radware 봇차단으로 끝내 못 열었다 — 압력·rpm·입경·정확한 pH 등 본문 표 값이 전부 이
  실패에 묶여 있다. `kp_m_per_pa` 자기선언은 이번 회차에 불가능했다.
- **IEP는 교차물질(Ga2O3) 대리값**이며 GaN 자체 표면 실측이 아니다(§2.5).
- **탄성계수는 문헌도 못 찾았고, 찾아도 현재 모델이 소비하지 않는다**(§2.2) — 이것도
  하나의 결론이다: 절차서의 직관("경도·탄성계수가 필요하다")이 실제 코드 소비처와 다를 수
  있다는 것을 이번 회차가 확인했다.
- **광전기화학(UV) 축은 스키마 자체가 없다**(§5 [P12]) — 이건 "문헌 없음"이 아니라
  "질문할 칸이 없다"는, 이번 조사에서 가장 중요한 구조적 발견이다.
- **검증 (b)의 351배 격차를 화학/광조사/입경 중 무엇이 얼마씩 차지하는지는 분해하지
  못했다** — 방향(어긋난다)과 크기 오더(2~3자릿수)만 확인했다.

[[../cmp/sic-ceria-abrasive-particle-size-chen2017-rsc]] 와 같은 방식으로, 이 노트도 다음
회차(GaN 팩이 실제로 만들어질 경우)의 선행조사로 남긴다. 관련: [[high-k-2d-material-cmp-trends]]
(고유전체/2D 소재의 "연속체 모델 정의역 이탈" 패턴이 여기서는 "산화제 모델 정의역 이탈"로
재현된다).
