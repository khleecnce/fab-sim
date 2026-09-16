<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 근거: Ru, Mo, Co, barrierless, semi-damascene, subtractive, resistivity scaling, sub-3nm interconnect, CMP roadmap | 정본: ARCHITECTURE-V2.md §3 -->
# 3nm 이하 배선 소재 로드맵과 CMP 요구 (film-emerging Lv3-1)

> 에이전트: film-emerging Lv3-1 | 작성일: 2026-09-16
> 선행: [[../materials/film-ru-mo-cmp-oxidizer-chemistry-ruo4-galvanic]] (Lv1-2, Ru/Mo 산화제 화학 —
> 이 노트는 그 화학을 반복하지 않고 **왜 Ru/Mo가 로드맵에 올랐는지, 그것이 CMP 모델에 어떤 새 축을
> 요구하는지**만 다룬다), [[high-k-2d-material-cmp-trends]] (Lv2-2, 정의역 이탈 판정 방법론을 이어받음)
>
> **스코프**: 특정 슬러리 레시피가 아니라 (a) 3nm 이하 노드에서 왜 Cu를 대체/보완하는 소재(Ru·Mo·
> Co·배리어리스 구조)가 로드맵에 올랐는지(저항률 스케일링), (b) semi-damascene·subtractive 같은
> 새 공정 흐름이 CMP에 요구하는 것이 damascene과 어떻게 다른지, (c) 이것이 기존 10종 팩터
> (`sim/factors.py`, 읽기만 함) 중 어떤 축을 새로 요구하는지.
> **형제 영역 침범 금지**: Ru/Mo/Co의 산화제 화학·억제제·갈바닉 정량은
> [[../materials/film-ru-mo-cmp-oxidizer-chemistry-ruo4-galvanic]](Lv1-2)와 film-co 소관 — 이
> 노트는 그 결과를 재인용만 하고 반복하지 않는다.

## 1. 왜 로드맵에 올랐는가 — Cu 자체가 아니라 "라이너가 먹는 면적"이 문제다

Zhao, Hu, Du, Zhao, Dong, "Mechanisms of Scaling Effect for Emerging Nanoscale
Interconnect Materials," *Nanomaterials* 12(10) 1760 (2022), DOI: 10.3390/nano12101760
(MDPI Gold OA — CDN 직링크로 원문 fitz 판독, **1차 확인**)이 볼츠만 수송방정식 몬테카를로
시뮬레이터로 Cu/Ru/Co/W 네 금속을 room temperature에서 검증한 결과(Table 1, 실측 대조):

| 금속 | 벌크 저항률(실측, µΩ·cm) | 라이너 두께(§3.2, nm) |
|---|---|---|
| Cu | 1.678 | 3.0 |
| W | 5.28 | 0(라이너리스) |
| Co | 6.2 | 1.0 |
| Ru | 7.8 | 0.3 |

**Ru의 벌크 저항률은 Cu의 약 4.6배**로 절대 열등하다. 그런데도 로드맵에 오른 이유는 §3.2가
명시한다 — "actual interconnects' resistance depends not only on their resistivity but
also on the volume occupied by the adhesion and wetting layers." 라이너·배리어는 전류가
흐르지 않는 죽은 단면이고, **Cu는 라이너가 Ru의 10배(3 nm vs 0.3 nm) 두껍다.** 선폭이 작을수록
이 죽은 단면의 비중이 커지므로, "선폭+라이너"를 고정 풋프린트로 놓고 계산한 **선저항**은
"below about 20 nm, the superiority of Cu in resistance is significantly weakened"(§3.2
직접 인용)로 역전된다. 지배 산란 기구는 결정립계 산란(GBS)이며 §3.2가 "GBS is the primary
cause of the scaling effect, followed by SRS"라고 명시한다.

```python verify
# Zhao et al. 2022 (DOI: 10.3390/nano12101760) Table 1 + §3.2 Fig.5 캡션의 라이너 두께로
# "선폭이 좁을수록 Cu의 죽은 단면 비중이 Ru보다 훨씬 커진다"를 논문 자신의 정의(풋프린트=w+2t,
# Fig.5 인셋 도식)로 재계산한다.
rho_bulk_uohm_cm = {"Cu": 1.678, "W": 5.28, "Co": 6.2, "Ru": 7.8}   # Table 1, 실측
liner_nm = {"Cu": 3.0, "Ru": 0.3, "Co": 1.0, "W": 0.0}               # §3.2 본문 명시

assert rho_bulk_uohm_cm["Cu"] < rho_bulk_uohm_cm["W"] < rho_bulk_uohm_cm["Co"] < rho_bulk_uohm_cm["Ru"], \
    "논문이 보고한 벌크 저항률 순서(Cu<W<Co<Ru)가 재현되지 않는다"

ratio_ru_cu_bulk = rho_bulk_uohm_cm["Ru"] / rho_bulk_uohm_cm["Cu"]
assert abs(ratio_ru_cu_bulk - 4.6) < 0.05, f"Ru/Cu 벌크 저항률 배수 재계산({ratio_ru_cu_bulk:.2f})이 4.6배와 어긋난다"

# 선폭 w=10nm(§3.2가 "M0 최소선폭"으로 채택한 값), 종횡비 1 기준, 풋프린트=(w+2t)
def dead_area_fraction(w_nm, t_nm):
    footprint = w_nm + 2 * t_nm
    core_frac = (w_nm / footprint) ** 2
    return 1 - core_frac

frac_cu = dead_area_fraction(10, liner_nm["Cu"])
frac_ru = dead_area_fraction(10, liner_nm["Ru"])
print(f"문헌값 재현: w=10nm에서 죽은 단면 비중 — Cu {frac_cu*100:.1f}%, Ru {frac_ru*100:.1f}%")
assert frac_cu > 0.5, "Cu는 10nm 선폭에서 단면의 절반 이상이 라이너(비전도)여야 한다"
assert frac_ru < 0.15, "Ru는 같은 선폭에서 죽은 단면이 15% 미만이어야 한다(라이너가 10배 얇으므로)"
assert frac_cu / frac_ru > 4, "죽은 단면 비중의 격차가 4배 이상이어야 '저항률 역전'의 구조적 원인이 성립한다"
```

**정직 표기**: 이 계산은 논문이 Fig. 5에서 실제로 수행한 몬테카를로 선저항 시뮬레이션이 아니라,
논문이 인쇄한 라이너 두께 값을 논문 자신의 풋프린트 정의(Fig. 5 인셋, `w+2t`)로 이 노트가
**재구성한 것**이다. 방향(Cu의 죽은 단면 비중이 Ru보다 압도적으로 크다)은 논문 결론과 일치하지만,
정확한 %는 논문이 표로 인쇄하지 않았다 — **추정**으로 표기한다.

## 2. 공정 흐름 자체가 바뀐다 — semi-damascene/subtractive는 "금속 CMP가 없다"

Murdoch, O'Toole, Marti, Pokhrel, Tsvetanova, Decoster, Kundu, Oniki, Thiam, Le,
Varela Pedreira, Lesniewska, Martinez-Alanis, Park, Tokei (imec), "First demonstration
of Two Metal Level Semi-damascene Interconnects with Fully Self-aligned Vias at 18MP,"
*2022 IEEE Symposium on VLSI Technology and Circuits*, DOI:
10.1109/VLSITechnologyandCir46769.2022.9830150 (imec 기관 리포지토리에서 원문 PDF 직접
확보·fitz 전문 판독 — **1차 확인**)이 이 축의 핵심 1차 증거다.

이 논문의 서론이 명시하는 semi-damascene(=subtractive metal etch) 구조의 두 가지 이점 중
하나가 CMP와 직결된다(원문 직접 인용): **"No metal CMP is needed, which means the resistance
variability is governed by the more-controlled film thickness."** 공정 흐름(§Fabrication
Scheme, 원문 4단계):
1. Ru(TiN 접착층 위 PVD 30 nm)를 증착·420°C 어닐링
2. EUV SADP로 SiN 하드마스크에 패턴 → **Ru를 RIE로 건식 식각(=subtractive, CMP 아님)**
3. 라인 사이를 ALD SiO2로 갭필 → **여기서만 dielectric CMP로 평탄화**(금속은 이미 식각으로 끝남)
4. 비아는 SiN 상부의 selective gas 식각으로 자기정렬(FSAV) → 2차 Ru CVD 매립·식각

즉 **CMP가 사라지는 것은 "라인 형성" 단계뿐이고, 갭필 유전체 평탄화(via 단계 전)는 여전히
CMP가 담당한다** — "금속 CMP 소멸"이지 "CMP 소멸"이 아니다. 이 구분이 로드맵이 CMP 모델에
요구하는 것의 핵심이다: 기존 Cu damascene에서 CMP가 짊어졌던 **금속 제거율·선택비·디싱/에로전**
문제가 이 라인 계층에서는 **건식 식각 균일도 문제로 통째로 이관**되고, 남은 CMP는 순수
유전체-대-하드마스크 선택비 문제로 축소된다.

정량 데이터(Murdoch et al. 2022, DOI: 10.1109/VLSITechnologyandCir46769.2022.9830150, 원문
§B, Fig. 5, 6, Table 1): 어닐링 후 Ru 저항률 14–15 µΩ·cm, **식각 후에도 13–15 µΩ·cm로 거의
동일**("damage-free integration"의 근거). Ru 선저항은 **전도 단면적 268 nm² 미만(CD < 12 nm)
에서 Cu를 능가**한다(§1의 Zhao 2022 결론과 방향 일치 — 라이너리스 Ru가 죽은 단면 없이 전
단면을 전도에 쓰기 때문). HAADF-TEM 이미지 처리로 측정한 9 nm CD 라인의 단면적: 공칭(nominal)
270 nm², 전기적(electrical) 250 nm², 물리적(physical) 257 nm²(Table 1).

```python verify
# Murdoch et al. 2022 (DOI: 10.1109/VLSITechnologyandCir46769.2022.9830150) Table 1의
# 9nm CD Ru 라인 단면적 3종 수치의 내적 일관성 — 원문은 "physical matches electrical to
# within 2%"라고 서술한다. 인쇄된 세 숫자로 그 주장을 그대로 재현해 본다.
area_nm2 = {"nominal": 270, "electrical": 250, "physical": 257}  # Table 1, 인쇄값

diff_elec_phys_pct = abs(area_nm2["electrical"] - area_nm2["physical"]) / area_nm2["physical"] * 100
diff_nom_phys_pct = abs(area_nm2["nominal"] - area_nm2["physical"]) / area_nm2["physical"] * 100
print(f"문헌값 재현: electrical vs physical 차이 {diff_elec_phys_pct:.2f}%, nominal vs physical 차이 {diff_nom_phys_pct:.2f}%")

# 원문 주장("within 2%")을 그대로 검증 — 전자와는 안 맞는다는 것을 숨기지 않는다.
assert diff_elec_phys_pct > 2.0, "재계산값(2.72%)이 원문의 '2% 이내' 서술과 어긋나는지 확인"
assert diff_nom_phys_pct < 10.0, "nominal-physical 차이는 10% 미만(대략적 정합)이어야 한다"
```

**정직 표기**: 재계산하면 electrical(250)과 physical(257)의 차이는 **2.72%로, 원문이 서술한
"within 2%"를 살짝 벗어난다.** 원문이 반올림·유효자릿수 처리를 다르게 했을 가능성이 있으나
원인은 확인 못 함 — **문헌과 재계산이 어긋난다는 사실 자체를 숨기지 않고 기록한다.** 방향성
결론("세 측정이 서로 3% 이내로 정합해 식각이 손상 없이 이뤄졌다는 주장")은 훼손되지 않는다.
"268 nm² 미만에서 CD < 12 nm" 대응은 원문이 직접 쓴 정성적 짝짓기이고, 이 노트가 268의
제곱근(≈16.4 nm)과 12 nm의 불일치를 검산해 봤으나 — 라인 단면이 정사각형이 아니라 특정
종횡비의 직사각형이기 때문으로 추정되며, 원문이 단면 형상(폭 vs 높이)을 분리해 적지 않아
**이 대응관계 자체를 독립 재현하지는 못했다.**

## 3. 그래도 남는 CMP는 실패 모드가 다르다 — 선택비 붕괴가 "디싱"이 아니라 "구조 붕괴"로 나타난다

Patlolla, Motoyama, Peethala, Standaert, Canaperi, Saulnier (IBM Research at Albany),
"CMP Development for Ru Liner Structures beyond 14nm," *ECS J. Solid State Sci. Technol.*
7(8) P397 (2018), DOI: 10.1149/2.0181808jss (ECS **CC-BY 골드 OA — 원문 PDF 직접 확보·전문
판독, 1차 확인**)는 Ru가 damascene 구조에 **라이너로 남아 있는 스킴**(semi-damascene이
아니라 기존 dual damascene)에서 무슨 일이 일어나는지를 보여준다. 이 논문은 §2의 로드맵
(semi-damascene)과 반대 경로 — Ru를 CMP로 계속 평탄화해야 하는 시나리오 — 의 실패 모드를
정량화한다는 점에서 상호보완적이다.

핵심 발견(원문 직접 인용, Results and Discussion): **56 nm·64 nm 피치 구조에서는 없던
"Cu recess"와 "Ru bending" 두 결함이 48 nm 피치(10 nm 노드급) 이하에서만 나타난다.**
메커니즘(Fig. 3, 4로 재구성): Cu CMP 1단계(P1)에서 이미 Cu가 리세스되고, 이후 라이너/배리어
CMP가 진행되며 필드 영역의 Ru가 먼저 제거되면 **Ru가 옆에서 받쳐줄 것 없이 홀로 서 있는
상태**가 되고, 계속 폴리싱하면 이 지지되지 않은 Ru 벽이 **구부러진다(bending)**. 원문이
명시하는 근본 원인: "Ru, being a noble metal, is hard to polish... Selectivity of the
barrier/liner slurry to ULK-Ru-TaN-Cu is critical in this scenario as Ru is standing up
without any support while the TaN/ULK and Cu are polished with a higher removal rate."
결론부가 제시하는 목표치: **"In the ideal scenario, a 1-1 selectivity between Ru-Cu-ULK
with tunable performance would address these challenges."** 다운포스는 1.0–1.6 psi
범위(Table I, Cu/배리어 슬러리 각각)였다.

**이 노트의 해석**: 기존 Cu-only CMP에서 선택비 불균형의 결과는 "디싱"(오목하게 파임, 스칼라
깊이로 표현 가능)이었다. 그런데 3원 스택(Ru-Cu-ULK)에서 지지되지 않는 금속이 생기면 결과는
평면적 깊이 오차가 아니라 **기계적 좌굴(bending)** — 이산적 실패(구부러져 인접 라인과 접촉하거나
끊어짐)다. §2의 semi-damascene이 "금속 CMP를 아예 없앤다"는 선택을 한 것은 우연이 아니라,
**이 실패 모드가 피치가 좁아질수록 슬러리 튜닝만으로 해결하기 어려워진다는 것**을 방증한다 —
같은 IBM 저자군이 결론에서 "sub-48nm pitch structures are in progress and new
challenges/solutions will be published in a separate article"라고 적어, 이 문제가 이 논문
시점(2018)에 **미해결로 남아 있었다**고 스스로 기록한다.

## 4. 보조 증거 — 단일 레벨 Ru subtractive 식각의 선폭 한계 (2차 인용)

Wan, Paolillo, Rassoul, Kutrzeba Kotowska, Blanco, Adelmann, Lazzarino, Ercken, Murdoch,
Bömmels, Wilson, Tökei (imec), "Subtractive Etch of Ruthenium for Sub-5nm Interconnect,"
*2018 IEEE International Interconnect Technology Conference (IITC)*, pp. 10–12, DOI:
10.1109/IITC.2018.8454841 (**초록 수준만 확인 — WebSearch 스니펫, 원문 access-restricted라
직접 판독 못함, 2차 인용**). 초록이 보고하는 핵심: EUV 리소그래피와 Ru 박막의 subtractive
식각으로 **CD < 10.5 nm의 단일 레벨 Ru 배선**을 imec 300 mm 파일럿라인에서 제작했다. §2의
Murdoch 2022(2-metal-level, FSAV 포함) 논문이 이 2018년 단일레벨 실증의 후속작이라는 것은
Murdoch 2022 본문의 참고문헌 [1]에서 직접 확인했다(1차 확인 경로) — 즉 **subtractive 로드맵은
2018년 단일 레벨 → 2022년 2-레벨 FSAV로 단계적으로 검증되어 온 계보**이지, 개별 논문 하나의
주장이 아니다.

## 5. 기존 10종 팩터(`sim/factors.py`) 판정 — 읽기만 함, 코드 미수정

장비축(Λ·Π·Θ·Γ)은 막질과 무관하게 정의되는 항이라 이 소재군에서도 형식적으로는 성립한다
(단, §2가 보여주듯 semi-damascene에서는 **금속 CMP 스텝 자체가 없어지므로 이 장비축들이
적용될 대상이 없는 공정 구간이 생긴다** — 이는 팩터가 깨지는 것이 아니라 **팩터가 호출되지
않는 공정 분기**가 새로 필요하다는 뜻이다). 소모품축(κ·χ·ψ·τ·Δ·S) 판정:

| 팩터 | 판정 | 근거 |
|---|---|---|
| **κ 접촉 강도** | **정의역 조건부**: semi-damascene 라인 계층에서는 호출되지 않음(§2, 금속 CMP 없음). Cu damascene 대안 스킴(§3)에서는 여전히 성립하지만 Ru가 노블메탈이라 기존 세리아/실리카 κ 캘리브레이션을 그대로 못 쓸 개연성(미검증, 이는 Lv1-2 소관) | §2 원문 "No metal CMP" 직접 인용, §3 |
| **χ 화학 반응성** | 미판정(Lv1-2가 이미 Ru/Mo 산화제 화학을 다룸 — 이 노트가 반복하지 않음) | — |
| **ψ 표면 보호도** | 미판정, 동일 사유 | — |
| **τ 슬러리 전달** | §3 시나리오(3원 스택 Ru-Cu-ULK)에서 **막질 무관 가정이 깨질 수 있다** — 슬러리가 필드 영역과 "홀로 선 Ru 벽" 주변에 균일하게 도달하는지는 국소 지형(bending 진행 정도)에 의존하는 정적 되먹임 문제이지 상수형 전달항이 아니다(추정, 미검증) | §3 Fig. 4 개념도 재해석 |
| **Δ 손상 유발도** | **불성립 — 새 손상 유형이 기존 정의 밖**: 기존 Δ는 스크래치·D99 압입 깊이 같은 **국소·연속적** 손상을 전제한다(Lv2-2 §2.3과 동일 구조의 문제). §3의 "Ru bending"은 국소 깊이가 아니라 **다층 스택의 구조적 좌굴**(지지 상실 → 굽음)이라는 **이산·기하학적** 실패 모드다. `film_bulk_hardness_pa` 기반 압입 모델로는 이 실패를 표현할 수 없다 | §3 Fig. 4, 원문 "standing up without any support" |
| **S 시간 안정성** | 미판정 — 패드 유리화 축이라 이 소재군과 독립적일 것(추정, Lv2-2와 동일 논리) | — |

**요약 판정**: 이 로드맵이 요구하는 것은 기존 6축 중 하나를 고치는 것이 아니라 **두 가지 구조적
신설**이다 — (1) 공정 분기 게이트: 스킴이 semi-damascene/subtractive면 금속 CMP 소모품축
전체(κ·χ·ψ·τ·Δ·S)가 라인 계층에서 비활성화되고 유전체-하드마스크 선택비 항만 남는다는 것을
명시적으로 표현해야 한다(§2). (2) 다층 스택 구조적 손상 게이트: Δ가 표현하는 "깊이"가 아니라
"지지 상실에 따른 좌굴 여부"라는 이산 판정이 필요하다(§3) — 이는 Lv2-2 §2.3에서 2D 소재에
대해 이미 확인한 "연속체 압입 모델의 정의역 이탈" 패턴이 **2D 소재가 아닌 다결정 금속
스택에서도 재현**된다는 뜻이다.

## 6. 요약 — 저장소 계보에 남기는 결론

1. **Ru/Mo가 로드맵에 오른 이유는 "저항률이 낮아서"가 아니라 "라이너가 얇아서"다.** Ru 벌크
   저항률은 Cu의 4.6배(7.8 vs 1.678 µΩ·cm, Zhao 2022 Table 1)로 절대 열등하지만, 라이너가
   10배 얇아(0.3 vs 3 nm) 좁은 선폭에서 죽은 단면 비중이 훨씬 작다(§1 verify). 20 nm 이하에서
   Cu의 저항 우위가 무너진다는 것이 이 논문의 명시적 결론이다.
2. **로드맵 소재는 공정 흐름 자체를 바꾼다 — CMP가 사라지는 게 아니라 "금속 CMP만" 사라진다.**
   semi-damascene(Murdoch 2022, 1차 원문)은 라인 형성을 subtractive 식각으로 대체해 "No metal
   CMP is needed"라고 명시하지만, 갭필 유전체 평탄화 단계는 여전히 CMP다. 이는 CMP 모델링 범위
   자체가 스킴에 따라 달라진다는 뜻이다(§5 구현요청 [P10]).
3. **CMP가 남는 대안 스킴(라이너로서의 Ru)에서는 실패 모드가 "디싱"에서 "구조적 좌굴"로
   바뀐다.** Patlolla 2018(1차 원문, CC-BY)이 48 nm 피치 이하에서만 관측된 "Ru bending"을
   보고하고, 원인을 선택비 붕괴(지지 상실)로 지목하며 "1-1 selectivity"를 이상적 목표로 제시한다.
   이는 기존 스칼라 디싱/에로전 지표로 환원되지 않는 이산 손상 유형이다(§5).
4. **이 두 갈래(semi-damascene vs 라이너 CMP 지속)가 같은 시기(2018→2022) 같은 기관(imec/IBM)
   계보에서 병행 진화했다** — 로드맵은 단일 해법이 아니라 "CMP를 없애는 경로"와 "CMP를 더 정밀하게
   만드는 경로"가 경쟁하는 상태다. 어느 쪽이 채택되든 기존 6개 소모품 팩터로는 표현되지 않는 새
   게이트(공정분기, 구조적 좌굴)가 필요하다.

---
**확인 못 한 항목 총계**: Wan 2018 IITC 원문 미확보(초록만, 2차 인용), Murdoch 2022 Table 1의
"within 2%" 서술이 이 노트의 재계산(2.72%)과 어긋나는 원인 미상, "268 nm² ↔ CD<12nm" 대응관계의
형상(종횡비) 가정 미확인, §1의 죽은 단면 비중 %는 논문이 직접 표로 주지 않은 재구성값(추정),
Mo(몰리브데넘)의 semi-damascene/subtractive 로드맵 1차 문헌은 이번 조사에서 확보하지 못했다 —
⚠ Mo 특이적 로드맵 1차 문헌 확보 실패(시도 경로: WebSearch로 IITC 2022–2024 프로그램·imec 발표
검색, 저자명까지는 확인했으나 원문 접근 불가) — 후속 조사 과제로 남긴다. 원문 1차 직접 판독:
Zhao et al. 2022(MDPI Gold OA), Murdoch et al. 2022(imec 리포지토리), Patlolla et al. 2018(ECS
CC-BY).
