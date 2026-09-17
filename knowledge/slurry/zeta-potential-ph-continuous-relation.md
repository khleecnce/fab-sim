<!-- V2-SECTION: R2-slurry | 작성 2026-09-18 | 근거: zeta, ph, continuous, iep, colloid -->
# ζ(pH) 연속 관계식 — 실리카·세리아·알루미나 (S12-RESIDUAL-JUDGMENT §2-3 블로커 해소용)

> 배경: `sim/tier2_physics/metal_contamination_surface.py::boltzmann_surface_enrichment`는
> `zeta_mV`(연속값)를 입력받는데, 저장소에 있던 것은 `ZETA_MV_BY_PH`(같은 파일 57행) 4구간
> 정성 카테고리("IEP/약산성/중성/약알칼리")뿐이었다. `slurry_ph`(연속, 6팩 전부)를 그 4구간에
> 매핑하려면 없는 임계값을 발명해야 해서 등록이 막혀 있었다. 이 노트는 그 블로커를 문헌
> 1차 확보로 풀기 위한 조사다. [[colloid-zeta-dlvo-slurry-stability]] §2·§5,
> [[../cmp/ph-ionic-strength-zeta-dissolution-selectivity-pourbaix]] §2가 이미 IEP 총론과
> Nernst 상한(−59.16 mV/pH)을 세워뒀다 — 이 노트는 그 위에 **실측 연속 곡선**을 얹는다.
> `dlvo_colloid.py::stability_qualitative`도 IEP 거리 기반 정성 판정만 쓰고 있어(88~92행
> "임계값 1.0/2.0은 미검증(arbitrary)"), 여기서 확보한 연속식이 서면 그쪽 정량화도 부수적으로
> 가능해진다(이번 과제 범위 밖, 등록은 하지 않음).

> ⚠ 이 노트는 **문헌 확보 조사**이며, `sim/tier2_physics/*.py` 코드나 `knowledge/params/*.yaml`
> 값은 건드리지 않는다. 엔진 등록도 하지 않는다.

## 0. 이온세기 의존성 — ζ는 pH만의 함수가 아니다

전기이중층 압축([[colloid-zeta-dlvo-slurry-stability]] §3, Debye 길이 $\kappa^{-1}\propto 1/\sqrt I$)
때문에 같은 pH라도 배경전해질 농도가 다르면 |ζ|가 달라진다(고이온세기 → 이중층 압축 →
|ζ| 감소, Grahame 식). 아래 §1의 실리카·세리아 곡선(Dandu 2009)은 **배경전해질 농도가
논문에 명시돼 있지 않다**(HNO₃/KOH로 pH만 적정, 지지전해질 별도 첨가 언급 없음 — 통상
묽은 산·염기 자체가 낮은 이온세기를 준다고 추정되나 mM 단위 수치는 원문에 없음).
CMP 슬러리 실사용 조건(계면활성제·킬레이트·산화제 수 wt%, 이온세기 통상 수십~수백 mM)과
**직접 비교 불가 — 조건 불일치**로 취급해야 한다. 즉 아래 표의 절대 mV 값은 "이 논문의
저이온세기 조건에서의 값"이며, 팩의 실제 슬러리 조성에 그대로 대입할 수 없다. 재현 가능한
것은 **부호·IEP 위치·기울기 오더**뿐이다.

## 1. 실리카(SiO2, 콜로이달) — Dandu et al. 2009 (1차, OA, 원문 확보)

출처: P. R. Dandu Veera, S. Peddeti, S. V. Babu, "Selective Chemical Mechanical Polishing of
Silicon Dioxide over Silicon Nitride for Shallow Trench Isolation Using Ceria Slurries,"
*J. Electrochem. Soc.* 156(12) H936–H943 (2009). DOI: 10.1149/1.3230624.
파일: `papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf` (기존 확보분, 이번에 재사용).
Fig. 9 "Zeta potential data for colloidal silica (~50 nm)" — "10% Silica"(첨가제 없음) 곡선.

- **본문 명시값**: "Bare silica particles have an IEP at pH <2." (본문 §Zeta potential data)
- **그래프 판독값(근사, 첨가제 없음 곡선)** — 축 읽기이며 디지털화 원자료가 아님, ±2 mV 오차 가정:

| pH | ζ (mV, 그래프 판독) |
|---|---|
| 2 | −10 |
| 4 | −16 |
| 6 | −22 |
| 8 | −28 |
| 10 | −31 |
| 12 | −33 |

- **선형근사 기울기**(pH 2→8 구간, 판독값 (−10)→(−28)): **약 −3.0 mV/pH**.
  [[../cmp/ph-ionic-strength-zeta-dissolution-selectivity-pourbaix]] §2가 "실리카는 아-Nern스트,
  수 mV/pH대"라 2차 인용으로 서술한 것과 **오더가 정합**(1차 실측 재확인).
- 유효 pH 범위: 2–12 (그래프 범위 그대로).
- 이온세기: 불명(§0) — HNO₃/KOH 적정, 지지전해질 농도 미기재.
- 온도: 원문 미기재(실온 추정, 명시 안 됨).
- **팩 선언값 대조**: `knowledge/params/oxide_silica.yaml` `abrasive_iep_ph=2.5`
  (출처: `knowledge/cmp/ceria-slurry-ce-redox-selectivity.md`) vs Dandu 2009 "<2".
  → **병기**: 팩 2.5, Dandu 문헌 <2. 둘 다 "실리카 IEP는 매우 낮은 산성역"이라는 점에서
  방향은 일치하나 정확한 수치는 다르다 — 어느 쪽도 고르지 않고 차이만 명시한다.
  ([[colloid-zeta-dlvo-slurry-stability]] §5도 "IEP≈2, 2차 인용"이라 이미 유사한 불일치를 기록해둠.)

## 2. 세리아(CeO2) — Dandu et al. 2009 (1차, OA, 원문 확보, 같은 논문)

Fig. 8 "Zeta potential of Ceria with and without additive" — "0.25% Ceria"(첨가제 없음) 곡선,
d_mean≈60 nm.

- **본문 명시값**: "pure ceria has an IEP of ~8, i.e., positively charged from pH 2 to 8 and
  negatively charged up to pH 12."
- **그래프 판독값(근사)**:

| pH | ζ (mV, 그래프 판독) |
|---|---|
| 2 | +70 |
| 3 | +73 (피크) |
| 4 | +73 |
| 5 | +65 |
| 6 | +40 |
| 7 | +15 |
| 8 | ~0 (IEP, 본문과 일치) |
| 9 | −10 |
| 10 | −20 |
| 11 | −22 |
| 12 | −22 |

- **IEP 근방 선형근사 기울기**(pH 6→9, 판독값 (+40)→(−10)): **약 −16.7 mV/pH**
  (Nernst 상한 −59.16 mV/pH의 절반 이하 — 아-Nern스트지만 실리카보다 훨씬 가파름,
  세리아 표면 자리밀도·특이흡착 차이로 해석 가능. 정량 메커니즘은 미검증).
- 유효 pH 범위: 2–12.
- 이온세기: 불명(§0), 실리카와 동일 조건(같은 논문·같은 실험 세트).
- 온도: 원문 미기재.
- **팩 선언값 대조**: `knowledge/params/sti_ceria.yaml` `abrasive_iep_ph=6.8`
  (출처: `knowledge/cmp/ceria-slurry-ce-redox-selectivity.md`) vs Dandu 2009 "~8".
  → **병기**: 팩 6.8, Dandu 문헌 ~8. 둘 다 "세리아 IEP는 약알칼리 근방"이라는 점에서 방향
  일치, 절대값은 1.2 pH 차이 — 어느 쪽도 고르지 않는다.
  [[colloid-zeta-dlvo-slurry-stability]] §5는 "IEP≈6.5, 2차 인용"이라 적어 세 값(6.5/6.8/8)이
  모두 제각각이다 — 세리아 IEP는 전처리(하소 여부)·입경·문헌마다 편차가 크다는 뜻으로 해석.
- `sic_ceria_h2o2` 팩도 같은 세리아 입자 — 위 값 그대로 적용.

## 3. 알루미나(Al2O3) — Gopal & Talbot 2006 (1차, 원문 확보 성공)

`knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md` §5가 "초록만 확인"이라 표기했던
Tanuja Gopal, Jan B. Talbot, "Effects of CMP Slurry Chemistry on the Zeta Potential of
Alumina Abrasives," *J. Electrochem. Soc.* 153(7) G622–G629 (2006). DOI: 10.1149/1.2198128.
원문 PDF를 Unpaywall 경로(iopscience.iop.org 직접, OA)로 확보 성공.
파일: `papers/gopal2006-jes-cmp-slurry-chemistry-zeta-alumina.pdf` (신규 등록, `papers/INDEX.json`).

- **본문 명시값(Fig. 1, 알루미나 슬러리 + 1 mM KNO3, 첨가제 없음, 지지전해질만)**:
  "The zeta potential decreased from a high of 58 mV at pH 3.5 to −24 mV at pH 10."
  "As the pH approached the IEP of 9, the effective particle diameter increases significantly..."
  → **IEP = 9** (입자클러스터 크기 최대점으로 확인, 본문 1차 수치).
- **선형근사(원문에 명시된 두 끝점 값 그대로, 그래프 판독 아님)**:
  기울기 = (−24 − 58) / (10 − 3.5) = **약 −12.6 mV/pH** (pH 3.5–10 구간 평균).
  아-Nernst(Nernst 상한 −59.16 mV/pH의 약 1/5) — 오더는 세리아(약 −16.7 mV/pH, §2)와 비슷하나
  약간 완만.
- 교차검증(Gopal & Talbot 2006, DOI: 10.1149/1.2198128, 같은 논문 Fig. 3): 0.1 M 글리신 첨가 시
  IEP가 "8.9–9.3"으로 좁은 범위 유지 — 무첨가 IEP=9와 정합적(글리신이 IEP 자체는 거의 안 바꾸고
  안정성만 높임).
- 유효 pH 범위: 3.5–10 (원문 실험 범위. 전체 조사 범위는 pH 3.5–10, "Cu CMP 통상 운용 pH 3–8"이라 서술).
- **이온세기**: 1 mM KNO3 (지지전해질 농도 명시 — 이 논문은 §0에서 지적한 "이온세기 불명"
  문제를 알루미나에 한해 해결한다). CMP 슬러리 실사용 이온세기(수십~수백 mM, 산화제·킬레이트
  포함)보다 훨씬 낮다 — **조건 불일치, 직접 대입 불가**(§0).
- 온도: 25°C(실온), 원문 명시.
- **부가 확인(같은 논문, 실리카 비교용 데이터, Cabot 실리카 + 1mM KNO3)**:
  "The zeta potential decreases from −3 mV at pH 3.5 to −56 mV at pH 10. The IEP was
  unattainable... because the reported IEP is 2." → 실리카 IEP=2를 **또 다른 독립 1차 출처**가
  재확인(Dandu 2009의 "<2"와 정합). 이 실리카 곡선의 기울기 = (−56−(−3))/(10−3.5) ≈ **−8.2 mV/pH**
  — Dandu 2009 그래프 판독 기울기(−3.0 mV/pH, §1)와는 **오더가 다르다**(같은 재료·비슷한 이온세기
  1mM인데도 약 2.7배 차이). 두 값 모두 정직하게 병기하며 어느 쪽도 대표값으로 채택하지 않는다 —
  실리카 ζ-pH 기울기는 제조사·입경·전처리에 따라 문헌 간 편차가 크다는 것 자체가 정직한 결론이다.
- **팩 선언값과의 대조**: 알루미나 IEP를 선언한 `knowledge/params/*.yaml`은 없다(grep 결과
  `abrasive_iep_ph` 키는 `oxide_silica.yaml`·`sti_ceria.yaml`에만 존재, `cu_h2o2_bta.yaml`·
  `w_fe_oxidizer.yaml`·`sic_alumina_kmno4.yaml`엔 없음) — 대조 대상 자체가 없어 병기할 팩값이 없다.
  `knowledge/cmp/ph-ionic-strength-zeta-dissolution-selectivity-pourbaix.md` §2 표의 "Al2O3
  PZC(≈IEP) 8–9"(Sun 2007, 2차 인용)와는 **정합**(9는 그 범위 안).

## 3.5 입자별 요약표

| 입자 | IEP(pH) | 기울기(근사) | 유효 pH 범위 | 이온세기 | 온도 | 출처 DOI |
|---|---|---|---|---|---|---|
| 실리카(콜로이달, Dandu) | <2 (본문) | 약 −3.0 mV/pH (그래프 판독, pH2–8) | 2–12 | 불명(§0) | 불명 | 10.1149/1.3230624 |
| 실리카(콜로이달, Gopal 비교데이터) | 2 (Ref.16 재인용) | 약 −8.2 mV/pH (본문 두 끝점) | 3.5–10 | 1 mM KNO3 | 25°C | 10.1149/1.2198128 |
| 세리아(calcined, ~60nm) | ~8 (본문) | 약 −16.7 mV/pH (그래프 판독, IEP 근방) | 2–12 | 불명(§0) | 불명 | 10.1149/1.3230624 |
| 알루미나 | 9 (본문) | 약 −12.6 mV/pH (본문 두 끝점, pH3.5–10) | 3.5–10 | 1 mM KNO3 | 25°C | 10.1149/1.2198128 |

동일 실리카에 대한 두 독립 문헌의 기울기(−3.0 vs −8.2 mV/pH)가 서로 다르다 — **대표값을 고르지
않고 병기**한다(§3, §4 verify에서 이 불일치를 assert로 고정해 회귀 감시).

## 4. python verify

```python verify
# Dandu 2009 (doi:10.1149/1.3230624) Fig.8/9 그래프 판독값 — 부호·IEP·기울기 오더 재현.
# 절대 mV는 축 판독 근사치(원 디지털화 자료 아님, ±2mV 가정). 문헌 상수를 박고 재현.

# --- 실리카 (Fig.9, 첨가제 없음) ---
silica_ph = [2, 4, 6, 8, 10, 12]
silica_zeta_mV = [-10, -16, -22, -28, -31, -33]

# 부호: 전 구간 음(-) — 본문 "negatively charged in the entire pH range of 2-12"
assert all(z < 0 for z in silica_zeta_mV)

# 단조 감소(더 음성화)
assert all(silica_zeta_mV[i] > silica_zeta_mV[i + 1] for i in range(len(silica_zeta_mV) - 1))

# 선형근사 기울기 (pH2->8): 약 -3 mV/pH, 아-Nernst(수 mV/pH대) 오더와 정합
slope_silica = (silica_zeta_mV[3] - silica_zeta_mV[0]) / (silica_ph[3] - silica_ph[0])
assert -5.0 < slope_silica < -1.0, f"실리카 기울기 {slope_silica:.2f} mV/pH, 기대 범위(-5,-1) 밖"

# --- 세리아 (Fig.8, 첨가제 없음) ---
ceria_ph = [2, 6, 7, 8, 9, 10]
ceria_zeta_mV = [70, 40, 15, 0, -10, -20]

# IEP=8 (본문 명시값과 일치)
idx_iep = ceria_ph.index(8)
assert abs(ceria_zeta_mV[idx_iep]) <= 2, "세리아 IEP=8에서 zeta~0 기대"

# pH<8 양(+), pH>8 음(-) — 본문 "positively charged from pH 2 to 8 ... negatively charged up to pH 12"
assert ceria_zeta_mV[ceria_ph.index(2)] > 0
assert ceria_zeta_mV[ceria_ph.index(9)] < 0

# IEP 근방 기울기(pH6->9): 약 -16.7 mV/pH, |기울기| < Nernst 상한 59.16 mV/pH
slope_ceria = (ceria_zeta_mV[ceria_ph.index(9)] - ceria_zeta_mV[ceria_ph.index(6)]) / (9 - 6)
NERNST_LIMIT_MV_PH = 59.16
assert -25.0 < slope_ceria < -8.0, f"세리아 IEP근방 기울기 {slope_ceria:.2f} mV/pH, 기대 범위(-25,-8) 밖"
assert abs(slope_ceria) < NERNST_LIMIT_MV_PH, "세리아 기울기가 Nernst 상한을 넘으면 물리적으로 이상함"

# 세리아가 실리카보다 IEP 근방에서 훨씬 가파름(자리밀도/특이흡착 차이) — 정성 비교만
assert abs(slope_ceria) > abs(slope_silica)

print(f"실리카 기울기(pH2-8) ≈ {slope_silica:.2f} mV/pH (아-Nernst, 수 mV/pH대와 정합)")
print(f"세리아 IEP=8 near-zero: {ceria_zeta_mV[idx_iep]} mV; 기울기(pH6-9) ≈ {slope_ceria:.2f} mV/pH")
print("PASS: Dandu 2009 Fig.8/9 그래프 판독값의 부호·IEP·기울기 오더 재현")

# --- 팩 선언값과의 IEP 불일치 명시 (병기, 어느 쪽도 고르지 않음) ---
pack_iep_silica = 2.5   # knowledge/params/oxide_silica.yaml abrasive_iep_ph
lit_iep_silica_max = 2.0  # Dandu 2009 "IEP at pH <2" — 상한으로 표기
assert pack_iep_silica != lit_iep_silica_max  # 불일치 존재 자체를 assert로 고정(회귀 감시)

pack_iep_ceria = 6.8    # knowledge/params/sti_ceria.yaml abrasive_iep_ph
lit_iep_ceria = 8.0     # Dandu 2009 "IEP of ~8"
assert pack_iep_ceria != lit_iep_ceria
print(f"불일치 기록: 실리카 팩{pack_iep_silica} vs 문헌<{lit_iep_silica_max}; "
      f"세리아 팩{pack_iep_ceria} vs 문헌~{lit_iep_ceria} (어느 쪽도 채택하지 않음, 병기)")

# --- 알루미나 (Gopal & Talbot 2006, doi:10.1149/1.2198128) 본문 명시 두 끝점 값 그대로 재현 ---
alumina_ph = [3.5, 10]
alumina_zeta_mV = [58, -24]

# IEP=9 근처에서 부호 반전(pH<9 양전하, pH>9 음전하) — 본문 "IEP of 9"
assert alumina_zeta_mV[0] > 0 and alumina_zeta_mV[1] < 0
IEP_ALUMINA = 9.0
assert alumina_ph[0] < IEP_ALUMINA < alumina_ph[1]

slope_alumina = (alumina_zeta_mV[1] - alumina_zeta_mV[0]) / (alumina_ph[1] - alumina_ph[0])
assert -20.0 < slope_alumina < -5.0, f"알루미나 기울기 {slope_alumina:.2f} mV/pH, 기대 범위(-20,-5) 밖"
assert abs(slope_alumina) < NERNST_LIMIT_MV_PH

# 같은 논문의 실리카(Cabot, 1mM KNO3) 비교 데이터 — Dandu 2009 그래프 판독 기울기와 오더 대조
gopal_silica_ph = [3.5, 10]
gopal_silica_zeta_mV = [-3, -56]
slope_gopal_silica = (gopal_silica_zeta_mV[1] - gopal_silica_zeta_mV[0]) / (gopal_silica_ph[1] - gopal_silica_ph[0])
assert -12.0 < slope_gopal_silica < -5.0, f"Gopal 실리카 기울기 {slope_gopal_silica:.2f} mV/pH 기대범위 밖"
# 두 독립 문헌의 실리카 기울기가 서로 다르다는 사실 자체를 정직하게 기록(대표값 채택 안 함)
assert abs(slope_gopal_silica) > abs(slope_silica) * 1.5, "두 문헌 실리카 기울기가 오더가 달라야 함(정직한 불일치 기록)"

print(f"알루미나(Gopal2006) IEP=9, 기울기(pH3.5-10) ≈ {slope_alumina:.2f} mV/pH")
print(f"Gopal2006 실리카 기울기 ≈ {slope_gopal_silica:.2f} mV/pH vs Dandu2009 실리카 기울기 ≈ {slope_silica:.2f} mV/pH "
      f"(같은 재료·비슷한 이온세기인데 오더 차이 — 문헌 간 편차를 그대로 기록)")
print("PASS: Gopal & Talbot 2006 알루미나 IEP·기울기 재현 + 실리카 교차문헌 불일치 기록")
```

## 5. 한계·미검증 (정직 표기)

- Dandu 2009(실리카·세리아)의 mV 값은 **그래프 축 판독 근사치**다(원 디지털화 데이터·원저자
  수치표 아님). IEP(정수 pH)와 부호는 본문 텍스트로 확인된 1차값이지만, 중간 mV 수치는
  ±2~3 mV 오차를 가정해야 한다. Gopal 2006(알루미나·비교실리카)의 mV 값은 **본문에 텍스트로
  명시된 수치**라 판독 오차가 없지만, 두 끝점(pH 3.5, 10)만 있어 그 사이 곡률(선형인지 아닌지)은
  확인하지 못했다 — "선형근사"일 뿐 실측 곡선 형태는 아니다.
- Dandu 2009는 배경전해질(이온세기)이 원문에 명시되지 않아 §0에서 지적한 대로 CMP 실사용
  슬러리 조건과 직접 비교 불가. Gopal 2006은 1 mM KNO3로 명시돼 있으나, 이 역시 CMP 실사용
  이온세기(수십~수백 mM, 산화제·킬레이트 포함)보다 훨씬 낮다 — **두 문헌 모두 조건 불일치,
  직접 대입 불가**. 이 노트가 주는 것은 "부호·IEP·기울기 오더"이며 절대 mV를
  `boltzmann_surface_enrichment(zeta_mV=...)`에 그대로 대입할 근거는 아니다.
- **같은 재료(실리카)에 대한 두 독립 문헌의 기울기가 오더로 다르다**(−3.0 vs −8.2 mV/pH, §3.5) —
  제조사·입경·전처리·측정법 차이로 추정되나 원인은 이 노트에서 규명하지 못했다. 어느 쪽이
  "맞는" 기울기인지 판정하지 않는다.
- 실리카·세리아(Dandu)는 같은 논문의 같은 실험 세트라 **입자 제조사·입경(실리카 colloidal
  ~50nm, 세리아 calcined ~60nm)**이 다르면 값이 달라질 수 있다는 점은 비교 대상이 아니다.
- 알루미나·비교실리카(Gopal)는 pH 3.5–10 범위만 조사됐다 — 강산성역(pH<3.5)의 거동은 미확인.
