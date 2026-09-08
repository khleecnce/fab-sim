<!-- V2-SECTION: R1-equipment | 공동: R3-pad | 분배완료 2026-09-08 | 근거: friction, lubric, 마찰, 토크 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 마찰계수 실측 — MIT 로터리 폴리셔 Cu CMP, 접촉모드 우세와 Preston 상수 붕괴 (Lai 2001)

> 에이전트: tribologist Lv3-2 | 작성일: 2026-09-08
> [[cmp-lubrication-regimes]] [[tribology-friction-wear-stribeck]] [[preston-luo-dornfeld-mrr]] [[frictional-heating-temperature-arrhenius-coupling]]

## 1차 출처
동일 연구그룹(MIT, Saka/Lai/Chun/Suh)의 동료심사 논문으로 신뢰성을 보강한다:
Saka, N., Lai, J.-Y., Chun, J.-H., Suh, N.P. (2001), "Mechanisms of the Chemical Mechanical Polishing (CMP) Process in Integrated Circuit Fabrication," CIRP Annals 50(1), 233-238, DOI: 10.1016/S0007-8506(07)62112-X (Crossref로 실존 확인, 초록만 확인 — 패턴 스케일 접촉역학 모델을 다루며 본 노트가 인용하는 접촉모드 COF·Preston 상수 붕괴 수치와는 별개 주제, 저자그룹의
학위논문(아래) 신뢰성을 보강하는 용도로만 사용).

Jiun-Yu Lai, *Mechanics, Mechanisms, and Modeling of the Chemical Mechanical Polishing
Process*, Ph.D. Thesis, Massachusetts Institute of Technology, 2001.
DSpace@MIT handle: https://hdl.handle.net/1721.1/8860 (공개 열람, MIT 소속 저자 서버
사본 https://web.mit.edu/cmp/publications/thesis/jiunyulai/ch2.pdf 로 원문 PDF 직접 확보,
미러 사이트 불필요). `tools/scope.py --check` ✓ 통과(학위논문 weight 0.7, tribologist 허용범위).
Ch.2 "Characterization and Optimization of the CMP Process"만 본 노트의 근거로 사용.

## 1. 왜 이 단원인가 — Lv1-2([[cmp-lubrication-regimes]])의 미검증 항목 해소 시도
Lv1-2 노트는 So·λ 레짐 경계를 **특허 명세(2차)와 일반 트라이볼로지 관례**로만 확정했고,
"CMP가 실제로 boundary/mixed에 머무는가, 아니면 hydroplaning도 가능한가"는 정성 논증
(ℓ_hd ≪ Ra)에 의존했다. 이 노트는 **실측 COF 데이터를 가진 1차 학위논문**으로 그 결론을
교차검증한다.

## 2. 실험 조건 (Table 2.1–2.4)
- 장비: 로터리 CMP 폴리셔, 300mm Al 플래튼, 부하/토크센서 실시간 측정
  (분해능 0.067 N, 0.001 N·m)
- 웨이퍼: Si + 20nm TiN + 1µm PVD Cu 블랭킷, 100mm
- 슬러리: 중성(pH 7) α-Al₂O₃ (0.3µm, 2-3 vol%), 점도 η=0.03 Pa·s
- 패드: Rodel IC1400 (IC1000 top + 서브패드), groove 250µm폭×375µm깊이, 1.5mm 피치
- 스윕: p=14, 48 kPa / v=0.05~3.91 m/s → ηv_R/p 를 4~5 오더에 걸쳐 스캔

## 3. 핵심 결과 1 — 접촉모드 COF 실측값과 Coulomb 불변성
Fig. 2.5: ηv_R/p가 작을 때(저속·고압) **COF = 0.40~0.49**, 압력·속도에 거의 무관
(Coulomb 마찰 법칙 성립 — §2.4.1). ηv_R/p 임계값 이후 급락해 0.1 이하로. 저 ηv_R/p 영역이
"접촉모드"임을 SEM(Fig 2.6, 패드 표면 소성변형·기공 막힘)으로 물리적 증거까지 제시.

**본 저장소 기존 모델(`cmp_lubrication_regime.cof_stribeck`, mu_bl=0.30)과 비교**:
현재 모듈의 boundary COF 상수는 산화막(oxide) CMP 문헌 오더(0.23~0.40, ResearchGate
2차 인용)를 기준으로 잡았다. 이 실측(Cu CMP)의 접촉모드 COF는 **0.40~0.49로 그 상한을
넘거나 근접** — 재료(Cu vs oxide)에 따라 boundary COF가 달라짐을 1차 자료로 확인.
`mu_bl=0.30`은 Cu 접촉모드를 과소평가한다(§5 검증).

## 4. 핵심 결과 2 — 실험적으로 hydroplaning 레짐에 도달하지 못함
§2.4.2: v_R을 3.91 m/s까지 올려도(전형 CMP의 5배 이상) 측정된 최저 COF조차
**0.001보다 훨씬 크다** → 문헌에서 가정한 hydroplaning(COF~0.001, film~50µm)은
"단 한 번도 재현되지 않았다"고 저자가 명시. 이유 3가지 제시:
1. 2차원 slurry flow의 side-leakage로 1차원 Reynolds 해석 무효
2. 압력중심 y_cp>0.5D(항상 출구쪽 치우침) vs 짐벌점 설계(중심) 불일치 → 받침각 붕괴
3. **필름두께가 복합 RMS 거칠기의 3배를 넘어야 hydroplaning 가능**(§2.4.2 마지막 문단) —
   이는 [[cmp-lubrication-regimes]] §3의 **λ≥3 → hydrodynamic 경계값과 수치적으로 일치**한다.
   Lv1-2는 이 "λ=3" 경계를 Bhushan(2013)·tribonet.org 같은 **일반 트라이볼로지 2차 인용**으로만
   확정했었는데, 이 학위논문은 **CMP 자체의 1차원 Reynolds 해석에서 독립적으로 같은 배수(3배)를
   도출**한다 — 두 출처가 다른 경로로 같은 수치에 도달했다는 점에서 λ=3 경계의 신뢰도가
   Lv1-2 시점보다 올라갔다(단, 여전히 "패드 waviness 7-16µm 미만" 조건은 실무 패드에서
   비현실적이라고 저자가 지적 — **CMP는 구조적으로 boundary/mixed에 갇힌다**는 결론 강화).

## 5. 핵심 결과 3 — Preston 상수의 붕괴와 비보편적 지수
Fig 2.7-2.8, §2.4.3: 접촉모드(저 ηv_R/p)에서는 정규화 MRR과 k_p가 압력·속도 무관
(k_p≈0.2×10⁻⁶ MPa⁻¹ @14kPa, 0.1×10⁻⁶ MPa⁻¹ @48kPa). 전이점 이후(mixed) k_p 는:
- 14 kPa: k_p ∝ (ηv_R/p)^(-1)
- 48 kPa: k_p ∝ (ηv_R/p)^(-0.5)

**지수가 압력별로 다르다(-1 vs -0.5)** — 저자도 "Preston 상수가 상수가 아님을 명백히
보여준다"고 결론. 이는 [[preston-luo-dornfeld-mrr]]가 다루는 Kp 상수성 가정에 대한
**정량적 반례**이며, 접촉면적비(α,β)가 ηv_R/p에 따라 변한다는 §2.2.5의 혼합모드
마찰모델(F=[αμ_a+βμ_p+(1-α-β)μ_l]·A)과 일관된다. **지수 -1/-0.5의 차이가 압력의존적인
물리적 이유는 원문에도 명시적 설명이 없음 — 미검증(원인 미상)으로 남긴다.**

## 6. Python 검증
```python verify
import math

# --- 1) 실측 접촉모드 COF 범위 (Fig 2.5, 본문 직접 인용값) ---
mu_contact_lo, mu_contact_hi = 0.40, 0.49
assert 0.35 < mu_contact_lo < mu_contact_hi < 0.55, \
    f"Lai(2001) 접촉모드 COF 범위 {mu_contact_lo}-{mu_contact_hi}"

# --- 2) 기존 모듈 cof_stribeck의 mu_bl=0.30이 Cu 접촉모드 실측을 과소평가함을 확인 ---
import sys, pathlib
sys.path.insert(0, str(pathlib.Path.home() / "fab-sim"))
from sim.tier2_physics.cmp_lubrication_regime import cof_stribeck

# 매우 낮은 So(접촉모드 극한)에서 모델 COF는 mu_bl에 수렴해야 함
cof_model_boundary = cof_stribeck(So=1e-6, mu_bl=0.30)
assert abs(cof_model_boundary - 0.30) < 0.01, \
    f"So→0 극한에서 cof_stribeck는 mu_bl로 수렴해야 함, got {cof_model_boundary:.4f}"
# 그 값이 Lai(2001) 실측 Cu 접촉모드 하한(0.40)보다 낮음 = 모델이 Cu를 과소평가
assert cof_model_boundary < mu_contact_lo, (
    f"모델 mu_bl={cof_model_boundary:.2f} < 실측 Cu 접촉모드 하한 {mu_contact_lo} "
    f"→ 기존 oxide 기준 mu_bl=0.30은 Cu CMP 접촉모드 COF를 과소평가 (재료별 분리 필요)"
)

# --- 3) hydroplaning 필름두께 임계(3x RMS roughness)가 lambda_ratio 경계(λ>=3)와 일치 ---
from sim.tier2_physics.cmp_lubrication_regime import regime_from_lambda
film_over_roughness_ratio = 3.0  # Lai(2001) §2.4.2: "film thickness must be > 3x composite RMS roughness"
assert regime_from_lambda(film_over_roughness_ratio) == "hydrodynamic", \
    "Lai(2001)의 3배 임계가 기존 λ>=3 hydrodynamic 경계 정의와 정합해야 함"
assert regime_from_lambda(film_over_roughness_ratio - 0.01) != "hydrodynamic", \
    "3배 미만은 hydrodynamic 미달이어야 함(경계 sanity)"

# --- 4) Preston 상수 지수 비보편성 — 두 압력조건 지수가 다름을 수치로 남김(주장 그대로, 재현 아님) ---
exp_14kPa, exp_48kPa = -1.0, -0.5
assert exp_14kPa != exp_48kPa, "Lai(2001): kp 지수가 압력에 따라 다름(비보편) — Preston 상수성 가정 반례"

print("PASS: Lai(2001) 실측 COF·hydroplaning 임계·Preston 지수 비교 4건 확인")
```

## 7. 한계 / 미검증
- 이 실험은 **Cu CMP 단일 시스템**(중성 Al₂O₃ 슬러리)이다. oxide CMP의 boundary COF
  (0.23~0.40, Lv1-2 근거)와 직접 비교하면 재료·화학이 다르므로 "재료별 μ_boundary가
  다르다"는 결론은 **정성적으로만** 확립되고, 정량적 재료 상수표는 아직 없음 — 미검증.
- hydroplaning 3배 임계의 **정확한 유도식**(Eq 2.20-2.37)은 OCR 손상(그리스 문자·아래첨자
  깨짐)으로 본 노트에서 재현하지 않았다 — 결과 수치(h1=22µm, h2=19µm, μ≈0.004 @η=0.005
  Pa·s, v=0.8m/s, p=48kPa)는 원문 인용만 하고 **직접 재계산은 하지 않음(미검증)**.
- Preston 지수(-1, -0.5)가 압력에 따라 왜 다른지 물리적 설명 없음 — **원인 미상, 미검증**.
- 이 논문은 2001년 발표로 IC1400(구세대 패드)·Al 플래튼 기준. 최신 패드(IC1010 등)로
  일반화 가능한지는 **확인 못함**.
- k_p 절대값(0.1~0.2×10⁻⁶ MPa⁻¹)은 Cu 계열 타 연구(Stavreva 1995/97, Luo 1998)와
  Fig 2.7-2.8에서 함께 플롯되어 있으나 그 문헌들의 원문은 미확보 — **2차 확인 안 함**.
