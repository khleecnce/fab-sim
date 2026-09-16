<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 근거: high-k, HfO2, ZrO2, Al2O3, 2D material, graphene, MoS2, hBN, CMP | 정본: ARCHITECTURE-V2.md §3 -->
# 고유전체·2D 소재 CMP 동향 (film-emerging Lv2-2)

> 에이전트: film-emerging Lv2-2 | 작성일: 2026-09-16
> 선행: [[../materials/film-co-interconnect-cmp-corrosion-galvanic-inhibitor]] (Lv1-1),
> [[../materials/film-ru-mo-cmp-oxidizer-chemistry-ruo4-galvanic]] (Lv1-2),
> [[../cmp/gst-chalcogenide-cmp-soft-film-defect-control]] (Lv2-1),
> [[../cmp/delta-damage-model-synthesis]] (Δ 손상모델 원 노트 — 이 노트 §3에서 그 상수를 그대로 재사용)
>
> **스코프**: (a) 고유전체(HfO2/ZrO2/Al2O3 게이트 유전체) — 경도·화학안정성이 SiO2와 어떻게
> 다른가, 기존 세리아·실리카 슬러리 제거가 왜 어려운가. (b) 2D 소재(MoS2/graphene/hBN) — 층상
> vdW 결합에서 Preston형 압입 제거 가정이 성립하는가, 압력 하한(박리 임계) 게이트 존재 여부.
> (c) 기존 10종 팩터(Λ,Π,Θ,Γ,κ,χ,ψ,τ,Δ,S — `sim/factors.py`, 읽기만 함) 중 이 소재군에서
> 성립하지 않는 항 판정.
> **형제 영역 침범 금지**: 기존 W/Cu/Co/Ru/Mo/질화막/폴리실리콘/산화막 CMP는 다루지 않는다 —
> 이 노트가 HfO2를 SiO2와 비교하는 것은 소재 자체(film-oxide 소관)를 다루기 위해서가 아니라
> **HfO2가 다른 이유**를 말하기 위한 대조군으로만 쓴다.

## 1. 고유전체(HfO2/ZrO2/Al2O3) — 경도가 아니라 화학이 만드는 어려움

### 1.1 경도는 SiO2와 같은 자릿수다 — "무르다/단단하다"의 문제가 아니다

Kull, Piirsoo, Tarre, Mändar, Tamm, Jõgiaas, "Hardness, Modulus, and Refractive Index of
Plasma-Assisted Atomic-Layer-Deposited Hafnium Oxide Thin Films Doped with Aluminum Oxide,"
*Nanomaterials* 13(10) 1607 (2023), DOI: 10.3390/nano13101607 (MDPI Gold OA — WebFetch로 PMC판
직접 확인)의 나노압입 실측:

| 막질 | 경도 H | 탄성계수 E |
|---|---|---|
| ALD HfO2(무도핑) | ≈ 10.5 ± 1.5 GPa | ≈ 160 ± 20 GPa |
| Al2O3 도핑 HfO2(최고 조성) | ≈ 15 GPa | ≈ 184 GPa |
| ALD Al2O3(순수) | ≈ 10.5 ± 0.8 GPa | ≈ 137 ± 7 GPa |

Fu et al. 2001(저장소 재인용값, [[../materials/film-co-interconnect-cmp-corrosion-galvanic-inhibitor]]
계보의 CMP 유효경도 표)이 쓰는 SiO2 CMP 유효경도는 ≈ 10 GPa(10¹⁰ Pa) 오더다. 즉 **HfO2의
나노압입 경도(10.5 GPa)는 SiO2의 CMP 유효경도와 거의 같은 자릿수**다 — GST(Lv2-1, SiO2보다
한 자리 낮음)와는 반대로, HfO2는 "무른 막이라 스크래치가 잘 난다"는 서사가 성립하지 않는다.
`sim/abrasive_mechanics.py`의 α 판정(읽기만, 코드 미수정) 기준에서도 HfO2는 SiO2와 같은
레짐(고경도 입자 기준 α 판정 경계 부근)에 놓이므로, **κ(접촉 강도) 항 자체의 함수형은 SiO2
쪽 모델을 그대로 재사용할 수 있다** — 이 소재군에서 κ가 깨지는 것은 아니다(§3.1).

### 1.2 진짜 문제는 χ — 표준 슬러리 화학이 HfO2를 활성화하지 못한다

같은 코퍼스에서 확보한 두 1차 문헌(둘 다 초록만 확인, 원문 IOP 봉쇄):

- Yuan et al., "Optimization and Mechanism on Chemical Mechanical Planarization of Hafnium
  Oxide for RRAM Devices," *ECS J. Solid State Sci. Technol.* 3(7) P243 (2014),
  DOI: 10.1149/2.0131407jss (초록 WebFetch로 확인 — 저자명은 초록에 없어 미기재).
- "Exploration of Novel Slurry on Hafnium Oxide Films Chemical Mechanical Planarization,"
  *ECS Trans.* 60(1) 647 (2014), DOI: 10.1149/06001.0647ecst (초록 WebFetch로 확인).

첫 논문의 초록이 그대로 보고하는 것: **표준 실리카 슬러리에서 HfO2 연마율은 5 nm/min에
불과**하고, 첨가제 NaBF4(불화붕산나트륨)를 넣으면 **95.5 nm/min로 19.1배 상승**한다. 저자들은
Preston식 자체를 `RR = kPV`(순수 기계항)에서 **`RR = kPV + Rc`**(정적 화학 제거항 Rc 추가)로
수정해야 데이터가 맞는다고 명시한다. 두 번째 논문은 실리카 입경·농도·pH를 스윕해 "10 wt%
~39.9 nm 실리카, pH 6"을 최적 조건으로 보고한다 — 이 역시 표준 실리카만으로는 낮은 RR을
벗어나지 못하고 첨가제·입경 조합이 지배 변수임을 시사한다.

```python verify
# 표준(첨가제 無) 슬러리와 NaBF4 첨가 슬러리의 HfO2 연마율 배수
# 출처: Yuan et al. 2014, ECS JSS 3(7) P243, DOI:10.1149/2.0131407jss (초록, WebFetch 확인)
RR_baseline_nm_min = 5.0       # 표준 실리카 슬러리, 초록 명시
RR_NaBF4_nm_min = 95.5         # NaBF4 첨가, 초록 명시
ratio = RR_NaBF4_nm_min / RR_baseline_nm_min

assert abs(ratio - 19.1) < 0.1, f"초록의 19배 서술과 재계산 배수({ratio:.2f})가 어긋난다"
print(f"문헌값 대조: RR 5 nm/min → 95.5 nm/min, 배수 {ratio:.1f}배 — 초록의 19배 서술과 일치(재현 성공)")
```

**왜 화학이 안 먹는가 — 식각 데이터로 교차확인**: WebSearch 스니펫이 인용하는 "Etching of
Zirconium Oxide, Hafnium Oxide, and Hafnium Silicates in Dilute Hydrofluoric Acid Solutions,"
*J. Mater. Res.* 19(6) (2004), DOI: 10.1557/jmr.2004.0149 (DOI 실존만 `find_open_access.py`로
확인, 원문 미확보 — **2차 인용**)에 따르면 **어닐링(≈700°C) 전의 as-deposited HfO2는 HF에
쉽게 녹지만(10:1 HF에서 ≈80 Å/min), 어닐링 후 결정화되면 거의 안 녹는다**고 한다. 즉 HfO2의
화학적 내식성은 절대적인 것이 아니라 **결정 상태(비정질 vs 다결정)에 강하게 의존**하며, 소자
공정에서 쓰는 HfO2는 대개 어닐링된 결정질이라 표준 산성/알칼리 슬러리의 화학 경로(세리아
IEP 창, 실리카 정점형, W 산성역 — `sim/factors.py::_f_chi`의 기존 3분기)가 전부 겨냥하지 않는
"불화물 착화" 계열 활성화가 필요하다는 뜻이다(§3.2).

**확인 못 함**: HfO2 나노압입 경도(§1.1)와 CMP 논문(§1.2)이 같은 결정 상태(비정질/다결정)를
가리키는지는 각 원문을 다 못 읽어 교차검증하지 못했다. 두 수치를 같은 표에 놓았지만 **막의
증착·후처리 조건이 다를 수 있음을 배제 못 한다**.

## 2. 2D 소재(graphene/hBN/MoS2) — "제거율"이 아니라 "생존"을 묻는 소재군

### 2.1 문헌 자체가 CMP를 다르게 쓴다 — 폴리싱 대상이 아니라 캡핑/배리어층

로컬 코퍼스·검색 양쪽에서 "2D 소재를 깎아서 없앤다"는 의미의 CMP 논문은 찾지 못했다(§2.4
정직 표기). 대신 실제로 확보된 1차 문헌은 전부 **2D 소재가 Cu 배선 공정의 CMP 단계를
'살아남아야' 하는 캡핑/확산방지층**으로 다룬다:

- Okasha, "Improved reliability of ultra-low-k dielectric with hBN capping layer for CMOS
  interconnect," MPhil thesis, HKUST (2023), DOI: 10.14711/thesis-991013223049703412 (**원문
  PDF 직접 확보·fitz로 전문 판독 — 1차 확인**). 이 논문의 목적 자체가 "hBN이 CMP 공정에서
  low-k 유전체 캡핑재로 쓸 수 있는가"이고, 판정 기준은 **연마율이 아니라 AFM 탐침
  힘-변위(force-displacement) 곡선으로 잰 접착력(adhesion force)**이다.
- Lo, Catalano, Smithe, Wang, Zhang, Pop, Kim, Chen, "Two-Dimensional h-BN and MoS2 as
  Diffusion Barriers for Ultra-Scaled Copper Interconnects," arXiv:1706.10178(**원문 PDF
  직접 확보·fitz로 전문 판독 — 1차 확인**, 이후 *npj 2D Mater. Appl.* 게재판 존재하나 이
  아카이브판만 원문 확인). 여기서도 목적은 "얇을수록 좋은 확산방지막"이며 본문에 CMP·polish·
  van der Waals 언급이 전혀 없다(§2.4에서 이 부재 자체를 기록) — 즉 **이 소재군의 CMP
  관련성 대부분은 "연마 대상"이 아니라 "연마 공정에서 손상 없이 남아 있어야 하는 하부층"**
  이라는 것이 문헌 지형 자체가 보여주는 사실이다.

### 2.2 실측값 — 접착력(nN)이지 제거율(nm/min)이 아니다

HKUST 논문(§2.1, 원문 표 3.5·4.1 직접 판독)의 AFM 접착력 실측치:

| 계면 | 접착력 |
|---|---|
| low-k / Si3N4(10 nm) | 14.7 nN |
| low-k / hBN(단층, 1L) | 21.9 nN |
| low-k / hBN(수 층, few-layer) | 29.2 nN |
| low-k / [hBN(1L)+Si3N4(10nm)] 복합 | 14.5 nN |
| Cu / low-k, Si3N4 캡 | 21 nN |
| Cu / low-k, hBN(few-layer) 캡 | 91~92 nN |

원문 결론(직접 인용): "hBN과 low-k의 접착력은 CMP 공정을 견디기에 충분히 강하며(strong
enough to withstand CMP processing), Si3N4/LTO 접착력과 비슷하거나 그보다 높다." 같은
논문이 인용하는 Zong et al., "Probing the adhesion interactions of graphene on silicon oxide
by nanoindentation," *Carbon* 103, 63 (2016), DOI: 10.1016/j.carbon.2016.02.079 (DOI 실존만
확인, 원문 미확보 — **2차 인용**)의 graphene-SiO2 접착력 범위 10~50 nN도 같은 자릿수라고
서술한다.

**해석의 한계(정직 표기)**: 이 힘은 AFM 탐침이 수직으로 잡아당길 때의 박리력(pull-off
force)이지, 실제 CMP에서 패드 돌기·입자가 가하는 **수직 압입 + 수평 전단**의 조합 하중이
아니다. "CMP를 견딘다"는 결론은 이 논문 저자의 정성적 해석이며, 이 노트가 그 해석을 검증한
것은 아니다.

### 2.3 기하학적 논증 — 왜 압입 기반 제거 모델이 원천적으로 안 맞는가

[[../cmp/delta-damage-model-synthesis]] §4가 이미 문헌 상수로 확정한 **패드 돌기 최대경도
`pad_asperity_hardness_max_pa` = 3.1×10⁸ Pa**(Eusner et al. 2009, *J. Electrochem. Soc.*
156(7) H528, DOI: 10.1149/1.3121964, Fig.15 — 저장소 기존 노트 재사용)와, 같은 노트가 5개
팩에 대해 이미 계산해 둔 **스크래치 최대 압입깊이 δ_max = (D99/2)·(H_p,max/H_film)**의
결과값(재인용, 압력 무관 상한)을 그대로 가져와 2D 단층 두께와 비교한다.

단층 두께는 Hess, "Thickness of elemental and binary single atomic monolayers," *Nanoscale
Horizons* 5, 385 (2020), DOI: 10.1039/c9nh00658c (DOI 실존 확인, EuropePMC로 서지사항만
확인·수치는 WebSearch 스니펫 — **2차 인용**)가 다룬 범위인 graphene ≈ 0.32~0.345 nm,
hBN ≈ 0.25~0.41 nm(기판·어닐링 조건에 따라)를 쓴다.

```python verify
# δ_max(기존 5개 팩, Eusner 2009/Saka 2008 상수)가 2D 단층 두께를 얼마나 초과하는가
# 출처: knowledge/cmp/delta-damage-model-synthesis.md §6-1 재인용값 (Eusner 2009 Table IV 재현)
delta_max_by_film_nm = {
    "Cu": 65.0,               # D99 500 nm, H_Cu=1.22 GPa
    "SiO2(세리아 D99=700nm)": 12.0,
    "SiC": 4.0,
    "SiO2(실리카 D99=250nm)": 4.0,
    "W": 3.0,                 # 5팩 중 최솟값
}
# 단층 두께 — Hess 2020 (DOI:10.1039/c9nh00658c) 대상 범위, 2차 인용(WebSearch 스니펫)
monolayer_thickness_nm = {
    "graphene": 0.335,
    "hBN": 0.33,
}

min_delta_max = min(delta_max_by_film_nm.values())
for mat, t in monolayer_thickness_nm.items():
    ratio = min_delta_max / t
    print(f"문헌값 대조: {mat} 단층({t} nm, Hess 2020) vs δ_max(W, {min_delta_max} nm, Eusner 2009) = {ratio:.0f}배 초과")
    assert ratio > 5, "기존 CMP 레짐의 최소 압입깊이도 2D 단층 두께를 수 배 이상 초과해야 논증 성립"
```

**논증의 의미**: 기존 5개 팩(Cu·SiO2 두 종·SiC·W) 중 δ_max가 **가장 작은 W(3 nm)조차** graphene
단층(0.335 nm)의 약 9배, hBN 단층(0.33 nm)의 약 9배다. 즉 **HfO2·SiO2·Cu·W·SiC 어느 소재를
겨냥해 조정한 CMP 조건이든, 그 조건이 만드는 최소 압입깊이는 이미 2D 단층 전체 두께를
훌쩍 넘는다.** `sim/factors.py`의 κ·Δ가 전제하는 "압입깊이 δ ∝ 하중^(2/3), 제거 단면적
∝ δ^1.5"라는 연속체 모델은 **깎여 나갈 벌크가 압입깊이보다 훨씬 두꺼움을 암묵적으로
가정**하는데, 단층 2D 소재는 이 가정이 원천적으로 성립하지 않는다 — 접촉이 일어나면 "얕게
깎이는 것"이 아니라 "뚫리거나(파단) 그대로 남는 것(하부층에 보호돼 접촉 자체가 없음)"의
이분법이 된다. 이는 §2.1~2.2에서 실제 문헌이 "제거율"이 아니라 "접착력(버티는가/떨어지는가)"
만 측정하는 이유와 정확히 들어맞는다 — **문헌의 측정 관행 자체가 이 기하학적 논증을 뒷받침
하는 간접 증거**다.

⚠ 이 논증은 이 노트가 기존 저장소 상수(Eusner 2009·Saka 2008 재인용치)와 별도 문헌(Hess 2020)
수치를 **조합해 새로 계산한 것**이지, 어느 논문이 "2D 소재는 CMP 압입 모델이 안 맞는다"고
직접 서술한 것을 인용한 게 아니다. **추정**으로 표기한다.

### 2.4 압력 하한(박리 임계)을 찾지 못한 이유 — ①과 ②가 함께 작동

과제 지시가 요구하는 구분: "①아무도 안 쟀다"인가 "②그 메커니즘이 애초에 대상이 아니다"인가.
이 노트의 결론은 **둘 다**다.

- **② 구조적 이유가 먼저다**: §2.1의 문헌 지형이 보여주듯, 2D 소재는 실제 배선 공정에서
  "폴리싱으로 깎아 없애는 막"이 아니라 "다른 막(Cu, low-k) 위에 얹혀 그 밑에서 확산을
  막는 캡핑층"으로 쓰인다. 캡핑층은애초에 CMP가 "일정 두께를 벗겨내는" 대상이 아니라
  "표면에 남아 손상되지 않아야 하는" 대상이므로, "압력을 얼마 이상 주면 몇 nm/min씩
  깎인다"는 Preston형 질문 자체가 이 소재군의 실제 사용 목적과 맞지 않는다.
- **① 그럼에도 안 잰 값이 있다**: 캡핑층이 "손상 없이 남는가"를 묻는다면, 그 손상 임계는
  §2.2의 접착력(nN, 수직 pull-off)이 아니라 **CMP 패드가 실제로 가하는 압력(psi)에서
  전단+압입 복합하중이 접착 파괴를 일으키는 임계 압력**이어야 정확하다. 이 값을 직접 잰
  1차 문헌은 이번 조사에서 찾지 못했다 — HKUST 논문도 AFM 정적 접착력만 측정했지, 실제
  웨이퍼를 CMP 장비에 넣고 압력을 스윕해 hBN 캡이 언제 벗겨지는지 본 실험은 아니다.
  **이 값은 "아직 아무도 안 쟀다"(①)로 분류한다.**

## 3. 기존 10종 팩터(`sim/factors.py`) 판정 — 읽기만 함, 코드 미수정

장비축(Λ 기계부하·Π 반경하중분포·Θ 열유동부하·Γ 컨디셔닝부하)은 웨이퍼 막질과 무관하게
정의되는 항이라 이 소재군에서도 그대로 성립한다(판정 대상에서 제외 — 물질명이 안 들어가는
축이므로 애초에 깨질 이유가 없다). 소모품축(κ·χ·ψ·τ·Δ·S) 여섯 개만 판정한다.

| 팩터 | 고유전체(HfO2 등) | 2D 소재(graphene/hBN/MoS2) |
|---|---|---|
| **κ 접촉 강도** | **성립**(§1.1) — 경도가 SiO2와 같은 자릿수라 기존 Hertz 압입 함수형 그대로 적용 가능 | **불성립**(§2.3) — 압입깊이가 단층 두께를 구조적으로 초과, "얕게 깎는다"는 연속체 가정 자체가 무의미 |
| **χ 화학 반응성** | **기존 3분기 다 불일치**(§1.2) — 세리아 IEP·실리카 정점·W 산성역 중 어느 것도 "불화물 착화"를 겨냥하지 않음. 새 분기 필요(§4 구현요청) | 판정 불가 — 벌크 제거 자체가 일어나지 않으므로 "화학이 표면을 무르게 한다"는 정의가 적용될 대상이 없음(②, §2.4) |
| **ψ 표면 보호도** | 미확보 — HfO2 특이적 흡착 억제제 문헌을 찾지 못함 | 판정 불가(κ와 같은 이유, ②) — 다만 §2.2의 접착력 자체가 일종의 "보호"를 재는 다른 물리량일 수 있음(추정, 미검증) |
| **τ 슬러리 전달** | 미판정 — 웨이퍼 스케일 슬러리 유동은 막질 무관 항이라 원칙적으로 성립할 것으로 보이나 HfO2 특이적 데이터 없음 | 미판정 — 같은 이유. 캡핑층 위로 슬러리가 지나가는 것 자체는 성립하는 개념이라 κ·χ만큼 확실히 불성립하진 않음 |
| **Δ 손상 유발도** | **성립 여지 있음** — §1.1 경도가 SiO2와 같은 자릿수이므로 D99 꼬리·치수상한 모델을 그대로 이식할 여지(미검증, HfO2 D99 데이터 없음) | **불성립**(§2.3과 동일 논증) — δ_max 상한 공식 자체가 "막 두께 ≫ 압입깊이"를 전제하는데 단층에서는 반대(δ_max ≫ 막 두께)라 "Δ 배수가 몇 배"라는 연속 비교가 무의미. 손상은 이분법(뚫림/무사)이지 배수가 아니다 |
| **S 시간 안정성** | 미판정 — 패드 유리화 모델은 패드 물성 축이라 웨이퍼 막질과 독립적일 것(추정) | 미판정 — 동일 |

**요약 판정**: 고유전체는 **κ가 살고 χ가 새 분기를 요구**하는 소재군(기존 모델의 부분
확장), 2D 소재는 **κ·Δ가 정의역 밖**이라 벌크 제거 모델 대신 "접착 파괴 이분법" 같은
별도 모델이 필요한 소재군 — 같은 "신소재"라도 기존 모델과의 관계가 정반대다.

## 4. 요약 — 저장소 계보에 남기는 결론

1. **HfO2는 무른 막이 아니다.** 나노압입 경도(≈10.5 GPa)가 SiO2 CMP 유효경도(≈10 GPa)와
   같은 자릿수라, GST(Lv2-1, 한 자리 낮음)와 정반대로 "경도가 다르다"는 서사가 안 통한다.
   대신 **표준 실리카 슬러리만으로는 RR 5 nm/min에 그치고, NaBF4 같은 불화물 착화 첨가제로
   19배 상승**한다(§1.2 verify) — Preston식이 `kPV`에서 `kPV+Rc`로 화학항을 요구할 만큼
   화학 의존도가 크다. 결정 상태(비정질/어닐링)에 따라 HF 식각률이 크게 갈린다는 교차 관찰과
   방향이 맞는다.
2. **2D 소재(graphene/hBN/MoS2)의 CMP 문헌은 "제거율"이 아니라 "접착력"을 잰다.** 확보한
   1차 문헌(HKUST 2023 학위논문) 자체가 hBN을 "CMP를 견뎌야 하는 캡핑층"으로 다루며 AFM
   pull-off 힘(14.7~92 nN)으로 판정한다. 이는 우연이 아니라 **δ_max(기존 5팩 최솟값도
   3 nm)가 단층 두께(≈0.33 nm)를 9배 이상 초과**하기 때문이라는 기하학적 이유가 있다(§2.3,
   이 노트의 추정 논증). κ·Δ의 연속체 압입 모델은 이 소재군의 정의역 밖이다.
3. **압력 하한(박리 임계)의 부재는 ①·② 둘 다다** — 2D 소재가 애초에 "깎이는 대상"이 아니라서
   Preston형 질문 자체가 안 맞는다는 것(②)과, 그럼에도 "실제 CMP 압력에서 캡핑층이 언제
   벗겨지는가"라는 더 정확한 질문에 답하는 1차 실험은 아직 없다는 것(①)을 함께 적는다.
4. **구현 요청은 PROFILE.md로 넘긴다**(sim/ 미수정 원칙) — χ에 "불화물 착화" 분기 신설(HfO2),
   κ·Δ에 "단층 2D 소재는 연속체 압입 모델 정의역 밖" 게이트 추가(과도한 δ_max/막두께 비에서
   자동으로 "제거율" 대신 "접착 파괴 이분법" 모드로 전환) 두 가지.

---
**확인 못 한 항목 총계**: HfO2 CMP 논문 2건·식각 논문 1건 원문 미확보(초록/2차 인용만),
Zong 2016 원문 미확보(2차 인용), ψ·τ·S의 두 소재군 판정 전부 미확보(표 §3에 명시),
2D 소재 실제 CMP 압력 스윕 박리 실험 전무(§2.4, ① 사유로 기록). 원문 1차 직접 판독:
Kull et al. 2023(HfO2 경도, MDPI OA), Okasha 2023 HKUST 학위논문(hBN 접착력), Lo et al.
arXiv:1706.10178(hBN/MoS2 확산방지, CMP 언급 부재 자체를 확인), Hess 2020 서지사항(EuropePMC).
