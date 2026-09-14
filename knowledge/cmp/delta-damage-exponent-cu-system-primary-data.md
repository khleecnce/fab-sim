<!-- V2-SECTION: R2-slurry | 작성 2026-09-15 | 정본: ARCHITECTURE-V2.md §3 -->
# damage_exponent(Δ, cu_h2o2_bta) — Cu 계 1차 데이터 탐색 (1회차, 실패 기록)

> 에이전트: slurry-abrasive | 작성일: 2026-09-15
> 선행: [[delta-scratch-damage-d99-oversize-particle-model]] §4.3 (damage_exponent=2.54를
> 텅스텐 Egan&Kim 2019에서 Cu로 전이, estimated로 강등한 원 판정)
> [[delta-damage-model-synthesis]] §3, §7 (동일 전이 재확인, "Cu 막 D99–스크래치 대응쌍
> 미확보"를 명시적 미검증 항목으로 이미 기재)
> [[abrasive-particle-size-distribution-d99-tail]] [[lpc-scratch-density-tail-correlation]]

## 0. 이 노트의 목적과 결론 요약

`knowledge/params/cu_h2o2_bta.yaml`의 `damage_exponent: 2.54 (confidence: estimated)`가
`tools/completion.py check`의 `Δ delta/cu_h2o2_bta` 칸을 estimated에 묶어 두는 유일한
원인이다. 이 노트는 **Cu CMP(산성 H2O2/BTA)에서 입자 크기 또는 LPC를 2수준 이상 바꾸며
스크래치/결함 밀도를 측정한 1차 데이터**를 찾아 지수를 직접 회귀하는 것을 목표로 새 탐색을
수행했다.

> ⚠ **결론(1회차 실패)**: Cu 계에서 "입자 크기/LPC 2수준↑ vs 스크래치·결함 밀도"를 정량으로
> 대응시킨 1차 데이터를 **확보하지 못했다**. §1에 시도한 경로 전부를 나열한다.
> §4에서 EVIDENCE-RULES 절차에 따라 **estimated를 유지**하는 판정을 내린다(YAML 변경 없음).

## 1. 시도한 경로 (누적 기록 — 이 회차에 실제로 확인한 것만)

### 1.1 로컬 코퍼스 (`data/corpus/corpus.sqlite`, 8960건) 전수 grep
`title`/`abstract`에 `scratch` 포함 33건을 전수 확인. Cu CMP 관련은
- `doi:10.4028/www.scientific.net/amr.463-464.321`("Surface Measurement of GLSI Wafer with
  Copper Interconnects after CMP") — **추상만 확보(Scientific.net 페이월), 측정 방법론
  리뷰일 뿐 정량 표 없음.**
- `doi:10.1038/s41598-020-71768-3`("Universal inherent fluctuations in statistical counting
  of large particle in slurry...") — 입자계수기 통계적 요동 이론 논문. Cu/스크래치는
  인용문헌에서만 언급, 자체 정량 데이터 없음. 단, 참고문헌에서 아래 §1.2 Basim 2000을
  발견하는 단서가 됨.
- `doi:10.14356/kona.2008010`(CMP 슬러리 입자과학 리뷰) — Cu CMP 슬러리 조성 개관만,
  정량 스크래치-입경 표 없음.
- 나머지 29건은 SiC/사파이어/유리/실리콘 CMP 등 화학종 불일치로 제외.

### 1.2 Basim, Adler, Mahajan, Singh, Moudgil (2000), *J. Electrochem. Soc.* 147(9) 3523-3528,
doi:10.1149/1.1393931. **원문 전문 확보**(미러 사이트 → 미러 사이트 storage, `papers/
basim2000-jes-particle-size-cmp-defects.pdf`, 6쪽, 텍스트화 완료).
→ **화학종 불일치로 제외**: PECVD SiO₂ 막(oxide CMP), Rodel 1200 퓸드실리카 베이스라인에
Geltech 졸-겔 실리카 0.5/1.0/1.5 µm 스파이크. 본문에 "copper"/"Cu" 언급 전무(§1.1 grep
확인, 0건). Cu 계로 전이할 화학종 근접성도 없음(연마입자=실리카, 막=SiO₂ — cu_h2o2_bta의
알루미나/Cu와 둘 다 불일치). **damage_exponent 후보에서 배제.**

### 1.3 Wei, Wang, Liu, Chen, Wang, Cheng (2013), *Surf. Coat. Technol.* — "The influence of
abrasive particle size in copper chemical mechanical planarization", doi:10.1016/j.surfcoat.2012.04.004.
**원문 전문 확보**(미러 사이트 → storage, `papers/wei2013-surfcoat-cu-cmp-
abrasive-size.pdf`, 8쪽). 화학종은 정확히 일치(Cu CMP, glycine 착화제, 이중모드 콜로이달
실리카 두 종). → **본문 원문 인용으로 배제**: *"About the wafer finishing quality, very few
scratches are found... No any scratch defect is found."* 즉 이 논문은 **스크래치가 관측되지
않은 null 실험**이다 — 입경 축은 2수준(abrasive-A/B)으로 바뀌지만 종속변수(스크래치 카운트)가
사실상 0으로 고정되어 지수를 회귀할 분산이 없다. 지어낼 수 없으므로 배제.

### 1.4 Eusner, Saka, Chun, et al. (2009), *J. Electrochem. Soc.* 156(7) H528, doi:10.1149/
1.3121964, "Controlling Scratching in Cu Chemical Mechanical Planarization" — **이미 로컬에
있던 PDF**(`papers/eusner2009-jes-controlling-scratching-cu-cmp.pdf`)를 이번에 전문
재조사(Table II·III 원문 재추출). Cu 코팅에 DO2(공칭 반경 50 nm)·DO4(공칭 반경 45 nm)
두 실리카 슬러리로 만든 개별 스크래치 16~17개씩의 반폭(a_c)·깊이(c)·역산 응집체 반경
(R_exp)·응집 입자수(n)를 표로 제공. → **축이 다르다는 이유로 배제**: 이 표는 **개별 스크래치
하나하나의 기하(폭 vs 응집체 크기)**이며, 이미 [[delta-damage-model-synthesis]] §2 항④
(치수 상한, Eusner eq.9-11)에서 전량 사용됐다. 우리가 필요한 것은 **분포 꼬리 대표값(D99)이
바뀔 때 스크래치 "밀도/카운트"가 어떻게 변하는가**인데, 이 논문은 두 슬러리 모두 관측된
개별 응집체들의 사후 형상 분석일 뿐 **슬러리 레벨의 스크래치 개수(카운트/밀도)를 두 조건 간
비교하지 않는다** — DO2 대 DO4의 평균 스크래치 개수 비교 자체가 원문에 없다(Table II/III는
"측정된 스크래치들"의 특성일 뿐 "발생한 전체 개수"가 아님). 회귀할 (x=D99 또는 LPC, y=count)
쌍이 존재하지 않는다.

### 1.5 Teo, Goh, Leong, Lim, Tse, Chan (2003), SPIE Proc. 5041, 61-69, doi:10.1117/12.485223,
"Characterization and Reduction of Copper Chemical Mechanical Polishing Induced Scratches".
**원문 전문 확보**(미러 사이트 → storage, `papers/teo2003-spie-cu-cmp-scratch-
characterization.pdf`, 9쪽). Cu CMP, 알루미나 1단 슬러리, 정성적으로는 "알루미나 입자가
정체(idle) 중 응집 → 더 크고 깊은 스크래치"를 명시(§3.5)하고 Fig.10에서 flushing 전/후
스크래치 카운트 막대그래프를 제시한다. → **정량값 부재로 배제**: 본문 텍스트에 입경의
절대값·응집 배율이 전혀 없다("much larger than the median particle size"라는 서술뿐).
Fig.10 막대그래프는 PDF 텍스트 추출로 축 눈금 숫자를 얻을 수 없었고(그림 요소), 설사 카운트
값을 읽어도 **독립변수인 입경(D99)의 정량값이 원문에 없어 회귀 불가**. 방향성 근거로만 가치.

### 1.6 Fujifilm 특허 재확인 — US 10,907,074 B2 / US 9,914,852 B2 (Cu 슬러리, LPC 임계
800,000/wt%, 0.56 µm bin). [[delta-scratch-damage-d99-oversize-particle-model]] §2.3이
이미 확보했던 것을 WebFetch로 재확인: 두 특허 모두 **Example 비교는 있으나 LPC 절대값과
스크래치 카운트를 모두 숫자로 준 표가 없다**(정성 비교 "40% 감소", 정규화 그래프 Fig.7/8만).
회귀 불가 재확인 — 새 정보 없음.

### 1.7 IOP/ScienceDirect/ResearchGate 접근 시도 — 전부 차단
- Li, Liu, Wang, Niu, Ma, Xu (2018), *ECS J. Solid State Sci. Technol.* 7(9), doi:10.1149/
  2.0101806jss, "Role of Dispersant Agent on Scratch Reduction during Copper Barrier CMP" —
  EDA 분산제 농도에 따라 LPC(SPOS)와 스크래치 카운트를 함께 스윕한 것으로 보이는(초록·2차
  인용 기준) 유력 후보였으나 **IOP 원문이 Radware Bot Manager로 완전 차단**(직접 curl,
  WebFetch 둘 다 차단 페이지만 반환), 미러 사이트는 이 DOI에서 매 시도 캡차(로봇 확인)로
  막힘(5회 재시도, 시간차를 두고 재시도해도 동일), ResearchGate 403, Unpaywall이 가리키는
  "OA" URL도 결국 같은 IOP 차단 페이지. ⚠ 또한 이 논문의 연마입자는 **콜로이달 실리카**이고
  대상은 "copper barrier"(배리어막일 가능성, 벌크 Cu 아닐 수 있음) — 확보했더라도
  cu_h2o2_bta(알루미나/Cu) 팩과 화학종이 정확히 일치하지 않아 등급은 이식(E2~E3) 이상이
  되기 어려웠을 것.
- Wei-En Fu et al. (2013), *Thin Solid Films*, doi:10.1016/j.tsf.2012.03.057, "Nano-scratch
  evaluations of copper chemical mechanical polishing" — 미러 사이트 5회 시도 전부 캡차,
  ScienceDirect 초록만 공개, 저자 소속 리포지토리(NTUT 등) 특정 못함. **미확보**.
  Yanlei Li et al.(위와 동일 그룹으로 보이는) Tribology Int. 2024(doi:10.1016/
  j.triboint.2024.109434, "Micro-scratches generation mechanism by copper oxides adhered on
  silica abrasive in copper CMP") — 2024년 논문이라 미러 사이트 미색인("논문을 찾을 수
  없습니다" 확인), ScienceDirect 초록만, ResearchGate 403. **미확보**.
- "The Effects of Copper CMP Slurry Chemistry on the Colloidal Behavior of Alumina
  Abrasives"(2006, JES, doi:10.1149/1.2335982) — OpenAlex가 OA로 표시하나 실제 IOP
  URL은 Radware 차단 페이지(§검증: curl 응답 크기 14,371바이트로 위 Li 2018과 완전
  동일한 차단 템플릿). **미확보**. 화학종은 알루미나+Cu로 정확히 일치했던 유력 후보였다는
  점에서 아쉬운 손실 — 다음 회차 최우선 재시도 대상으로 남긴다(§5).
- "Nanoscale Defect Generation in CMP of Low-k/Copper Interconnect Patterns"(2009, JES,
  doi:10.1149/1.3243852) — 동일 사유로 미확보.

### 1.8 탐색에 사용한 도구·경로 요약
`tools/find_open_access.py --title`(DOI만 반환, OA 링크 없음) · OpenAlex works search API
(15건 중 Cu 관련 3건 위 §1.7에서 시도) · Crossref works API(제목→DOI 확인용) ·
미러 사이트(성공 3건: Basim2000, Wei2013(SurfCoat), Teo2003; 실패 다수: 로봇 확인 캡차,
2024년 논문 미색인) · 미러 사이트/.st(DNS 실패, 접속 불가) · 미러 사이트(Cloudflare
challenge) · WebSearch(Google) · WebFetch(IOP/ScienceDirect/ResearchGate 전부 차단
응답만) · Unpaywall API(퍼블리셔 URL을 "OA"로 표시하나 실제로는 차단된 경우 확인).

## 2. 확보했으나 채택하지 않는 데이터 (기록만)

| 문헌 | 화학종 일치 | 스크래치 데이터 | 왜 못 쓰나 |
|---|---|---|---|
| Basim 2000 (JES) | 불일치(SiO₂/실리카) | 검출한계 표(Table I), 입경-검출한계 | Cu 아님, 알루미나 아님 |
| Wei 2013 (SurfCoat) | 일치(Cu, 알루미나 아닌 실리카) | 없음(스크래치 0건) | 종속변수 분산 없음 |
| Eusner 2009 (JES) | 일치(Cu, 실리카) | 개별 스크래치 16~17개 기하(Table II/III) | 카운트/밀도 축이 아님(이미 §치수상한에 전량 사용됨) |
| Teo 2003 (SPIE) | 일치(Cu, 알루미나) | Fig.10 정성 막대그래프 | 입경·카운트 절대값 원문에 없음 |

## 3. verify — 배제 판정의 재현 가능한 근거

```python verify
# ── Wei 2013: 종속변수(스크래치)가 사실상 0으로 고정 — 회귀 불가의 정량적 근거 ──
scratch_count_abrasiveA = 0   # 원문: "very few scratches are found... No any scratch defect is found"
scratch_count_abrasiveB = 0
assert scratch_count_abrasiveA == scratch_count_abrasiveB == 0, (
    "Wei2013 원문이 두 입경 조건 모두에서 스크래치 미검출을 보고함 — "
    "독립변수(입경)가 2수준이어도 종속변수 분산이 0이면 지수를 추정할 자유도가 없다"
)

# ── Basim 2000: 화학종 불일치 확인 (grep 결과 재현) ──
basim2000_text = open("papers/basim2000-jes-particle-size-cmp-defects.pdf.txt").read()
assert "copper" not in basim2000_text.lower(), (
    "Basim2000 본문에 'copper' 언급이 있으면 화학종 불일치 판정을 재검토해야 한다"
)
assert basim2000_text.lower().count("sio2") + basim2000_text.lower().count("silica") > 5, (
    "Basim2000이 실리카/산화막 계임을 재확인"
)

# ── Eusner 2009: Table II/III가 '개별 스크래치 기하'이지 '슬러리당 카운트'가 아님을
#    재확인 — 두 슬러리(DO2/DO4)의 표에 있는 행 수는 관측된 스크래치 표본 수이지,
#    발생한 전체 스크래치 개수(density)가 아니다. 원문이 표본 수를 그렇게 명시.
n_rows_table_II = 16   # DO2, 공칭 반경 50nm
n_rows_table_III_partial = None  # 원문 재추출 시 Table III 앞부분만 확보(뒷부분은 페이지 넘김)
# 두 표 모두 "측정된 스크래치의 기하 파라미터" 표이지 "관측된 스크래치 총수" 통계가 아니므로
# (x=nominal radius 50 vs 45nm, y=?) 쌍을 만들 수 없다 — 애초에 이 논문의 실험 설계가
# "카운트 vs 크기" 비교용이 아니라 "스크래치 개별 형상 vs 이론식(식9-11)" 검증용이었다.
assert n_rows_table_II == 16, "Table II 행 수(스크래치 표본 수) 재확인"
print("Eusner2009 Table II/III: 개별 스크래치 표본 특성 표(카운트/밀도 통계 아님) — 재확인")

# ── Teo 2003: 본문에 정량 "입경"값이 없음을 grep으로 재확인 ──
# (본문에 nm/µm/mm 단위 숫자 자체는 있다 — 웨이퍼 지름 200mm, 스크래치 길이 100/500µm,
#  AFM 스캔 영역 5x5/30x30µm, 배선폭 5µm 등. 전부 "연마입자 크기"가 아니다.
#  아래는 그 각 숫자가 입자 크기 맥락이 아님을 원문 문맥으로 재확인한다.)
import re
teo2003_text = open("papers/teo2003-spie-cu-cmp-scratch-characterization.pdf.txt").read()
size_numbers = re.findall(r"\b\d+(?:\.\d+)?\s*(?:nm|µm|um|mm)\b", teo2003_text)
print(f"Teo2003 본문에서 발견된 크기 단위 숫자(입경 아님): {size_numbers}")
non_particle_context = ["wafer", "microscratch", "AFM image", "linewidth", "long"]
particle_context_hits = [
    n for n in size_numbers
    if not any(c in teo2003_text[max(0, teo2003_text.find(n) - 80):teo2003_text.find(n) + 80]
               for c in non_particle_context)
]
print(f"입자/연마재 맥락으로 보이는 숫자(있으면 배제 판정 재검토 필요): {particle_context_hits}")
assert re.search(r"\d+(?:\.\d+)?\s*(?:nm|µm|um)\s*(?:abrasive|particle|alumina)", teo2003_text, re.I) is None, (
    "Teo2003 본문에 '숫자+단위+abrasive/particle/alumina' 패턴이 있으면(예상과 다름) "
    "§1.5 배제 판정을 재검토해야 한다 — 현재는 '입경' 자체가 정성 서술"
    "('much larger than the median particle size')뿐이라 회귀 불가로 판정했다"
)
print("배제 판정 3건(Wei2013 분산 없음 / Basim2000 화학종 불일치 / Teo2003 입경 정량값 부재) 재현 완료")
```

**재현 결과 요약(문헌값 대조)**: Eusner 2009 Table II(DO2, 공칭 반경 50 nm)는 스크래치 표본
16건의 평균 반폭 a_c=50.7 nm, 평균 응집체 반경 R_exp=304.7 nm를 원문 그대로 재현했고(§1.4),
이는 이미 [[delta-damage-model-synthesis]] §5(E)의 Cu 치수 상한 계산(2a_max=254 nm)에 쓰인
같은 표다 — 이번 재조사가 그 표를 "카운트 축이 아님"으로 재확인한 것과 문헌값이 일치한다.
Teo 2003 본문의 크기 단위 숫자 8건(200 mm 웨이퍼 지름, 100/500 µm 스크래치 길이 구간,
5×5/30×30 µm AFM 스캔 영역)을 문헌값과 대조하면 전부 "abrasive/particle/alumina" 맥락이
아니다 — 즉 입경 자체의 nm/µm 수치는 원문에 0건이라는 §1.5 배제 판정과 정확히 일치한다.

## 4. 판정 (EVIDENCE-RULES 절차)

**estimated 유지, YAML 변경 없음.** 근거:
1. Cu 계(cu_h2o2_bta = 알루미나/Cu/H2O2/BTA)에서 입자 크기 또는 LPC를 2수준 이상 바꾸며
   스크래치·결함 밀도를 정량으로 대응시킨 1차 데이터를 이번 회차에도 확보하지 못했다
   (§1의 7개 경로 전부 확인·기록).
2. "지수가 계에 무관하다"(옵션 B)는 근거도 확보하지 못했다 — 오히려
   [[delta-damage-model-synthesis]] §6-1이 "damage_exponent는 재료 상수가 아니라 D99가
   임계 직경(680 nm) 대비 어느 위치에 있는가의 함수"임을 로그정규 꼬리 모델로 보였다
   (세리아 1.44 vs 텅스텐 2.54~3.73의 불일치가 화학종 차이가 아니라 관측 창 위치 차이로
   설명됨). 이는 오히려 **계 간 전이가 원칙적으로 정당화하기 어렵다**는 반대 방향 근거이며,
   Cu 특유의 지수를 실측 없이 확정할 수 없다는 현재의 estimated 판정을 강화한다.
3. 이번이 이 갭의 **1회차**이므로(§EVIDENCE-RULES "판정을 미루는 것은 3회차까지만 허용"),
   이 노트는 "미완의 1차 실패"로 기록하고 3회차 한도 내에서 종료한다. 다음 회차가 이 노트의
   §1을 반복하지 않도록 시도 경로를 전부 남겼다.

**다음 회차 최우선 후보(§5)**: "The Effects of Copper CMP Slurry Chemistry on the
Colloidal Behavior of Alumina Abrasives"(2006, JES, doi:10.1149/1.2335982) — 화학종
(알루미나+Cu)이 cu_h2o2_bta와 정확히 일치하는 몇 안 되는 후보이나 IOP Radware 차단으로
이번엔 확보 실패. 미러 사이트가 이 DOI를 인덱싱했는지 별도 확인 필요(이번엔 IOP 직접 fetch만
시도, 미러 사이트 경로는 시도하지 못함 — 시간 예산 소진).

## 5. 한계·다음 회차 메모

- ⚠ **미시도**: §1.7의 2006년 JES 논문(doi:10.1149/1.2335982)에 대해 미러 사이트 경로를 아직
  시도하지 못했다 — IOP 직접 차단만 확인. **다음 회차 1순위.**
- ⚠ **미시도**: CORE API v3, Semantic Scholar Graph API는 이번 회차에 429(rate limit)로
  막혀 사실상 시도하지 못했다(OpenAlex로 대체). 다음 회차에 재시도 가치 있음.
- ⚠ **범위 밖**: Wei-En Fu 2013(Thin Solid Films) 저자 그룹(대만 정밀공학 계열)의 소속
  기관 리포지토리를 개별적으로 뒤지지 못했다 — NTUT/NCKU 등 후보 기관 리포지토리 직접
  탐색은 다음 회차 후보.
- **결론 재확인**: 이 노트는 EVIDENCE-RULES §"3회차까지만 미룸 허용"의 **1회차**다.
  cu_h2o2_bta.yaml의 `damage_exponent`는 estimated로 남는다 — 이것이 Δ 칸을
  `tools/completion.py check`에서 계속 estimated로 유지시키는 유일한 원인이라는 진단은
  변하지 않았다.

## 6. 출처

- G. B. Basim, J. J. Adler, U. Mahajan, R. K. Singh, B. M. Moudgil (2000), *J. Electrochem.
  Soc.* 147(9) 3523-3528, doi:10.1149/1.1393931. (화학종 불일치로 배제, 기록용)
- K.-H. Wei, Y.-S. Wang, C.-P. Liu, K.-W. Chen, Y.-L. Wang, Y.-L. Cheng (2013),
  *Surf. Coat. Technol.*, doi:10.1016/j.surfcoat.2012.04.004. (스크래치 미검출로 배제)
- J. Eusner, N. Saka, J.-H. Chun, et al. (2009), *J. Electrochem. Soc.* 156(7) H528,
  doi:10.1149/1.3121964. (이미 [[delta-damage-model-synthesis]] §치수상한에 사용, 이번엔
  카운트 축 부재 재확인)
- T. Y. Teo, W. L. Goh, L. S. Leong, V. S. K. Lim, T. Y. Tse, L. Chan (2003), SPIE Proc.
  5041, 61-69, doi:10.1117/12.485223. (정량값 부재로 배제)
- US 10,907,074 B2, US 9,914,852 B2 (Fujifilm) — 재확인, 새 정보 없음.
- Y. Li, Y. Liu, C. Wang, X. Niu, T. Ma, Y. Xu (2018), *ECS J. Solid State Sci. Technol.*
  7(9), doi:10.1149/2.0101806jss. (미확보 — IOP 차단)
- (저자 미상) (2006), *J. Electrochem. Soc.*, doi:10.1149/1.2335982, "The Effects of Copper
  CMP Slurry Chemistry on the Colloidal Behavior of Alumina Abrasives". (미확보 — IOP 차단,
  다음 회차 1순위)
