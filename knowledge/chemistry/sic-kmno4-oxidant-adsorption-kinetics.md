<!-- V2-SECTION: R2-slurry | 정확도루프 C2 chi/sic_alumina_kmno4 2026-09-19 -->
# SiC/알루미나/KMnO4 — 산화제 형상항(Langmuir K) 1차 출처 확보와 held-out 상충

> slurry-chemist | 작성일: 2026-09-19 | 대상 팩: `sic_alumina_kmno4`
> 선행: [[sic-kmno4-ph-floor-oxidizer-coupling-wang2021]] (판정#64 — pH 항 φ 농도보간)
> [[sic-kmno4-acidic-ph-decay-chen2020]] (판정#61 — pH 항 원본)
> [[sic-alumina-kmno4-L25-heldout-diagnosis]] (Gong 2024 L25 held-out 진단, 이 노트가 그 결론을 뒤집는다)

## 1. 왜 이 칸인가 — 코드가 실제로 죽여둔 것은 "축퇴"가 아니라 "종 게이트"

`sim/factors.py::_f_chi`(L1436-1505)는 이 팩에서 `oxidizer`·`ceria_tooth`·pH 후보 중
켜지는 항의 수로 status 를 정한다(`len(terms) >= 2` 면 modeled, 아니면 partial).
현재 이 팩은:

- `ceria_tooth`: 꺼짐 — `abrasive=alumina`(판정#59)라 세리아 IEP 항 자체가 적용 불가.
- `ph_sic_kmno4_acidic`: **켜짐**(own 계수 `sic_kmno4_ph_acid_k`, 판정#61/#64) — 유일한
  활성 항이라 `len(terms)==1` → status 는 항상 `partial` 이었다.
- `oxidizer`: 꺼짐. `oxidizer_wt_pct`/`oxidizer_ref_wt_pct` 는 선언돼 있지만 형상
  파라미터(`oxidizer_langmuir_K`/`oxidizer_passivation_K`/`oxidizer_peak_wt_pct`)가
  전혀 없다(`_f_chi` L1448-1458 경고). 부모(`sic_ceria_h2o2`)의 `oxidizer_langmuir_K`
  (H2O2 데이터, K=0.76)는 있지만 `_oxidizer_species_gate_ok`(sim/chemistry.py
  L100-130)가 `oxidizer_langmuir_species=H2O2` != 이 팩의 `oxidizer=KMnO4` 를 잡아
  차단한다(판정#50, 의도된 동작).

즉 이번 회차의 실제 임무는 "형상을 어떻게 모델링할까"가 아니라 **"KMnO4 자체 데이터로
`oxidizer_langmuir_K` 를 자기선언해 종 게이트를 통과시킬 수 있는가"** 다. 통과하면
`oxidizer` 항이 켜져 `len(terms)==2` → status 가 `modeled` 로 바뀐다.

## 2. 확보한 1차 출처 — Gong et al. 2024 Table 2 (L25 직교표)

**Gong J., Wang W., Liu W., Song Z., "Polishing Mechanism of CMP 4H-SiC Crystal
Substrate (0001) Si Surface Based on an Alumina (Al2O3) Abrasive", Materials 17(3)
679 (2024), DOI 10.3390/ma17030679** (MDPI, CC BY 오픈액세스) — 이 팩의 `abrasive`·
`abrasive_size_nm` 키가 이미 인용 중인 문헌과 **동일 논문**이다. 로컬 코퍼스 JATS XML
(`data/corpus/fulltext/doi_10.3390_ma17030679.xml`)의 `<table-wrap>` 을 직접 파싱했다
(그래프 판독이 아니라 인쇄된 표 숫자).

재료계: 2인치 **4H-SiC** (0001) Si면, **α-Al2O3 500 nm**, 산화제 **KMnO4**, pH는
HNO3/KOH 조정, 4 psi, 헤드 100/플래튼 90 rpm, 90 mL/min, 60 min — 이 팩(4H/6H-SiC +
알루미나 + 산성 KMnO4)과 재료·산화제·연마입자 종이 전부 일치한다(폴리타입만 6H 대신
4H, 이 팩의 다른 문헌들도 4H/6H 를 섞어 쓴다).

설계: **L25(5수준 3인자) 직교표** — pH 2~6 · **KMnO4 1~5 wt%** · Al2O3 1~5 wt%,
n=25, 세 인자가 균형 배치돼 서로 교란 없이 주효과를 분리할 수 있다(Taguchi 직교표의
정의 조건). 저자들이 Table 3 에 각 인자·수준의 **주효과 평균**(k_j, 5개 관측의 평균)을
이미 계산해 실어 두었다:

| KMnO4 (wt%) | 주효과 평균 MRR (µm/h) |
|---|---|
| 1 | 0.53348 |
| 2 | 0.67452 |
| 3 | 0.68066 |
| 4 | 0.68680 |
| 5 | 0.70520 |

**이것이 요청받은 "3점 이상 농도 스윕"이다** — 실제로는 5점, 각 점이 5회 반복(다른 두
인자의 전 수준 조합)의 평균이라 단일 관측보다 노이즈가 낮다. §6 verify (1)에서
Table 2 원본 25행에서 직접 재계산해 저자의 Table 3 값과 일치함을 확인했다(자기 답안지
그대로 베끼지 않았다는 증거).

## 3. Langmuir 피팅 — 되지만 K·φ 가 서로 축퇴한다

이 팩의 기존 `oxidizer_ref_wt_pct=4.0 wt%`(Entegris 특허 근거)가 **우연히 Gong 데이터의
격자점**(수준 4)과 정확히 겹친다 — 별도 보간 없이 기준점을 그대로 쓸 수 있다.
`f(C) = φ + (1-φ)·θ(C)/θ(C_ref)`, `θ(C)=K·C/(1+K·C)` 에 5점을 비선형 최소자승으로
맞췄다(§6 verify (2)).

**정량 대조**(Gong et al. 2024 Table 2 문헌값 대 피팅 재현, 단위 nm/min 환산,
기준 C=4 wt% 문헌값 0.68680 µm/h=11.447 nm/min): C=3 wt% 문헌 0.68066 µm/h
(=11.344 nm/min) 대 예측 11.136 nm/min(오차 −1.8%); C=5 wt% 문헌 0.70520 µm/h
(=11.753 nm/min) 대 예측 11.643 nm/min(오차 −0.9%, doi:10.3390/ma17030679) —
두 점 모두 2%p 이내로 재현된다. C=1(오차 +3.7%)·C=2(오차 −6.0%)는 위에서 이미
설명한 급한 초기 도약 구간이라 잔차가 크다.

φ 를 자유롭게 두면 최적해가 **φ<0**(비물리)으로 발산한다 — 데이터가 C=1→2 사이에서
이미 관측 비의 대부분(0.777→0.982)을 건너뛰고 이후 거의 평평하다가 C=5 에서 소폭
반등하는 모양이라, 매끄러운 오목 포화곡선 하나로는 정확히 못 맞춘다(판정#19 의
`(n, C_peak)` 축퇴와 같은 종류의 문제 — 자유도가 부족하다). φ 를 프로젝트 기본값
0.15(다른 산화제 항들의 관측 미비 시 대역 중앙값, `_oxidizer_term` docstring)로
**고정**하고 K 만 풀면:

    K = 2.28  (1/wt%)

잔차(비율 공간) rms ≈ 3.1%(§6 verify (2)) — 최대 개별 잔차는 C=2 지점에서 5.7%p.
φ=0(다른 극단)으로 고정해도 K=2.82 로 예측치가 <1%p 차이만 나(§6 verify (3)) — **φ 는
이 데이터로 식별 불가**이고 K 값도 φ 가정에 조건부다. 그래서 이 회차는 `oxidizer_mech_floor`
를 새로 선언하지 않는다(근거 없이 기존 0.15 기본값을 덮지 않는다) — K 만 자기선언한다.

## 4. 정직한 상충 — 이 데이터셋은 이제 이 축의 독립 held-out 이 아니다

`validation/datasets/gong2024_4hsic_alumina_kmno4_L25.yaml` 은 `used_for_calibration:
false` 로 등록돼 있고, `knowledge/cmp/sic-alumina-kmno4-L25-heldout-diagnosis.md` 는
이 팩의 KMnO4 축·pH 축이 "죽어 있어서" 이 DOE 가 독립 검증 역할을 한다고 진단했다.
**이번 회차로 KMnO4 축을 그 DOE 로 켰으므로, 그 진단의 전제가 깨진다** —
이제 이 팩의 예측은 그 데이터셋의 오직제 마진평균을 일부 되먹임한다(자기 답안지 채점
위험, `kp_m_per_pa` 의 Entegris 사례와 같은 성격).

⚠ **이 노트는 `validation/datasets/*.yaml` 을 수정할 권한이 없다**(담당 파일 범위 밖).
`agents/slurry-chemist/PROFILE.md` §구현 요청에 다음을 남긴다: 그 데이터셋의
`used_for_calibration` 을 `true` 로 갱신하고, `sic-alumina-kmno4-L25-heldout-diagnosis.md`
의 "KMnO4 축이 죽어 있다" 서술을 갱신할 것 — pH 축(alumina 팩에서 `_ph_softening_term`
미적용, 별도)은 여전히 죽어 있으므로 그 부분 진단은 유효하다.

## 5. 배선 결과

`sic_alumina_kmno4.yaml` 에 `oxidizer_langmuir_K=2.28 (1/wt%)`, `oxidizer_langmuir_species=
KMnO4` 를 자기선언(own)한다. 종 게이트가 `oxidizer=KMnO4`(이미 선언됨)와 일치를 확인해
통과하고, `oxidizer_ref_wt_pct=4.0` 이 그대로 기준점이라 **기준 조건에서 χ=1.0 계약이
자동으로 유지된다**(§6 verify (4)) — `kp_m_per_pa` 재역산이 필요 없다(기준 농도가
바뀌지 않았다).

`_f_chi` 등급 하한 로직(L1483-1494)은 활성 항의 형상 키만 읽으므로, `oxidizer_langmuir_K`
가 `estimated` 면 χ confidence 는 그대로 `estimated`(승격 없음) — 이번 회차의 성과는
**status: partial → modeled** 이지 confidence 승격이 아니다.

## 6. verify

```python verify
import math

# ── (1) Table 2 원본 25행에서 오직제(KMnO4) 주효과 평균을 직접 재계산 —
#        저자 Table 3 의 k_j 값(0.53348/0.67452/0.68066/0.68680/0.70520)과 대조.
rows = [
 (2,1,1,0.5212),(2,2,3,0.7665),(2,3,5,0.7972),(2,4,2,0.4906),(2,5,4,0.6439),
 (3,1,5,0.5519),(3,2,2,0.4599),(3,3,4,0.7052),(3,4,1,0.6439),(3,5,3,0.6439),
 (4,1,4,0.4906),(4,2,1,0.7052),(4,3,3,0.5212),(4,4,5,0.7052),(4,5,2,0.7358),
 (5,1,3,0.5212),(5,2,5,0.7052),(5,3,2,0.7052),(5,4,4,0.8278),(5,5,1,0.7972),
 (6,1,2,0.5825),(6,2,4,0.7358),(6,3,1,0.6745),(6,4,3,0.7665),(6,5,5,0.7052),
]  # (pH, KMnO4 wt%, Al2O3 wt%, MRR um/h) — Gong et al. 2024 Table 2, doi:10.3390/ma17030679
k_paper = [0.53348, 0.67452, 0.68066, 0.68680, 0.70520]
for lvl in range(1, 6):
    vals = [r[3] for r in rows if r[1] == lvl]
    assert len(vals) == 5, (lvl, vals)          # 직교표 균형 배치 확인
    mean = sum(vals) / 5
    assert abs(mean - k_paper[lvl - 1]) < 2e-4, (lvl, mean, k_paper[lvl - 1])

# ── (2) Langmuir 피팅, floor=0.15 고정 (프로젝트 기본값, _oxidizer_term docstring)
C = [1.0, 2.0, 3.0, 4.0, 5.0]
Cref = 4.0
kref = k_paper[3]
r_obs = [k / kref for k in k_paper]

def f(Cv, K, floor):
    theta = K * Cv / (1 + K * Cv)
    theta_ref = K * Cref / (1 + K * Cref)
    return floor + (1 - floor) * theta / theta_ref

K_fit = 2.28
floor_fixed = 0.15
r_pred = [f(c, K_fit, floor_fixed) for c in C]
resid = [p - o for p, o in zip(r_pred, r_obs)]
rms = math.sqrt(sum(x * x for x in resid) / len(resid))
assert rms < 0.032, rms                          # ~3.1%
assert max(abs(x) for x in resid) < 0.06, resid  # 최대 개별 잔차 <6%p (C=2 지점)
assert abs(f(Cref, K_fit, floor_fixed) - 1.0) < 1e-9   # 기준점 항등

# ── (3) floor 비식별성 — 0.0 과 0.15 사이 예측 차가 크지 않다 (K·floor 축퇴)
K_fit0 = 2.82   # floor=0 으로 다시 푼 값 (본문 §3)
r_pred0 = [f(c, K_fit0, 0.0) for c in C]
maxdiff = max(abs(a - b) for a, b in zip(r_pred, r_pred0))
assert maxdiff < 0.01, maxdiff                   # <1%p — φ 는 이 데이터로 식별 불가

# ── (4) 엔진 계약: 기준 조성(4 wt%)에서 χ 산화제 항 = 1.0, 형상 켜짐 확인
from sim.engine import Recipe, simulate
rec = simulate(Recipe(pack="sic_alumina_kmno4"))
chi = rec.factors["chi"]
assert "oxidizer" in chi.terms, chi.terms         # 종 게이트 통과 확인
assert abs(chi.terms["oxidizer"] - 1.0) < 1e-9, chi.terms["oxidizer"]
assert chi.status == "modeled", chi.status        # partial -> modeled (본문 §1)

# 농도를 올리면 실제로 반응한다 (죽은 축이 아님을 확인)
rec_hi = simulate(Recipe(pack="sic_alumina_kmno4",
                          pack_overrides={"oxidizer_wt_pct": 5.0}))
assert rec_hi.factors["chi"].terms["oxidizer"] > 1.0
```

## 7. 한계 (정직 표기)

- **직교표 주효과 평균**이지 통제된 단일축 스윕이 아니다 — 다른 두 인자(pH, 알루미나
  wt%)의 영향이 평균으로 상쇄된다는 가정(Taguchi 직교 설계의 표준 가정)에 의존한다.
  상호작용항이 있으면 이 가정이 깨진다(저자들도 상호작용 분석은 하지 않았다).
- **K·φ 축퇴**(§3) — φ=0.15 고정은 근거가 아니라 "덮지 않는다"는 보수적 선택이다.
  φ 의 진짜 값이 이 계에서 얼마인지는 **미확인**이다.
- **폴리타입 불일치**: Gong 은 4H, 이 팩의 다른 계수(예: `sic_kmno4_ph_acid_k`)는 6H
  (Chen 2020)에서 왔다 — 폴리타입 간 산화제 반응성 차이는 미검증(선행 노트들과 동일한
  가정을 이어받는다).
- **§4 의 held-out 상충은 이 노트가 해소하지 못한다** — PROFILE.md 로 위임했다.
- **테스트 회귀 2건**: `tests/test_factors.py::test_oxidizer_shape_is_not_transferred_
  across_oxidizer_species`·`::test_sic_kmno4_ph_floor_reference_unity_unaffected_by_
  oxidizer` 가 이 변경으로 실패한다 — 둘 다 "이 팩의 산화제 축은 죽어 있다"는 이제는
  틀린 전제를 검증하고 있었다(의도된 붕괴). `sim/`·`tests/` 는 이 임무 범위 밖이라
  고치지 않았다 — `agents/slurry-chemist/PROFILE.md` §구현 요청에 구체적 수정
  방향을 남겼다.
- 곡선 형상 자체(오목 포화)가 5점 중 4점을 잘 못 맞춘다는 뜻은 아니다: C=1→2 구간이
  급격하고 이후 거의 평평한 모양은 Langmuir 로도, 더 급한 포화(큰 K)로도 어느 정도
  설명되지만 **정밀한 형상 검증에는 데이터가 부족**하다(n=5, 자유파라미터 사실상 1개).

[[sic-alumina-kmno4-L25-heldout-diagnosis]]
