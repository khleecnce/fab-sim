"""화학-기계 결합층 — 슬러리 화학이 제거율을 어떻게 바꾸는가.

왜 이 파일이 있나 (2026-09-06 사용자 지시):
  "당연히 화학적인것도 반영해야해. 슬러리첨가제나 세리아같은 입자는 화학작용이 메이저잖아"

그 전까지 엔진은 슬러리 화학 전체를 Preston 계수 Kp **상수 하나**에 뭉뚱그렸다.
산화제 농도를 바꾸든 BTA를 넣든 세리아를 쓰든 결과가 똑같았다 — 즉 소재 개발자가
정작 만지는 변수(조성)에 시뮬레이터가 반응하지 않았다. 그건 소재사용 툴이 아니다.

## 물리적 통로: 화학은 '표면 경도'를 통해 기계에 연결된다

CMP 제거는 화학 단독도 기계 단독도 아니다. 문헌(Luo-Dornfeld, Kaufman)이 말하는 것은
**화학이 표면을 연화시키고 기계가 그 연화층을 긁어낸다**는 시너지다.

  knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md §4:
    소성 압입   δ_p = F/(2πR·H)         ∝ H⁻¹
    plowing 홈  A_f = (4/3)√(2R)·δ_p^1.5 ∝ H⁻¹·⁵
    → 화학적 연화로 H를 4배 낮추면 제거 체적은 4^1.5 = 8배 (노트 verify PASS)

따라서 이 모듈의 계약은 하나다:

    화학 조건 → 유효 경도비 (H_eff/H_0) → MRR 배수 = (H_0/H_eff)^1.5

이렇게 두면 화학과 기계가 각자 자기 자리를 지킨다. 기계 쪽(GW 접촉·압력·속도)은
1바이트도 안 고치고, 화학은 배수 하나로 들어온다.

## ⚠ 이중 계상 함정 (2026-09-06 실제로 밟았다)

첫 구현에서 Cu MRR이 450 → 22.5 nm/min로 20배 떨어졌다. 원인은 물리가 아니라 회계다.

  팩의 `kp_m_per_pa`는 **이미 BTA가 든 실제 슬러리의 문헌 MRR에서 역산한 값**이다.
  거기에 억제 항 (1-θ)=0.05를 또 곱하면 억제를 두 번 적용한 것이 된다.

그래서 이 층의 계약은 "화학 효과의 절대량"이 아니라 **기준 조건 대비 상대 변화**다:

    factor = f(현재 조성) / f(기준 조성)

`*_ref` 파라미터가 그 기준점이고, 기준 조성에서는 factor가 정확히 1.0이 되어
Kp가 그대로 나온다. 조성을 바꿀 때만 배수가 생긴다.

**이것이 스크리닝 도구로서 옳은 동작이다** — 우리가 답할 질문은 "MRR이 절대 몇이냐"가
아니라 "BTA를 1mM에서 2mM로 올리면 어느 쪽이 더 깎이냐"이기 때문이다.

## 다루는 화학 (전부 팩 파라미터로 제어)

1. **산화제** — Kaufman 경쟁: 농도↑ → 산화층 생성↑이지만 과하면 부동태막이 두꺼워져
   오히려 제거 저해. 단봉 곡선(slurry_components.mrr_oxidizer).
2. **억제제(BTA 등)** — Langmuir 피복 θ가 표면을 덮어 제거를 막는다. (1-θ) 가중.
3. **세리아 chemical tooth** — Si-O-Ce 화학결합(DFT −111~−258 kJ/mol)이 실리카를
   직접 뜯어낸다. 물리흡착 기반 실리카 슬러리와 메커니즘이 다르다. Ce³⁺ 분율이 활성점.
4. **pH** — 표면 전하·용해도를 통해 연화에 기여. 지금은 IEP로부터의 거리로 단순화.

## ⚠ 정직성 규약 (이 모듈에서 특히 중요하다)

화학은 물리보다 훨씬 불확실하다. 그래서:
- 모든 계수는 팩에서 온다. 코드에 화학 상수를 박지 않는다.
- **절대값을 주장하지 않는다.** 이 층이 내는 것은 "기준 조건 대비 몇 배"이고,
  기준 조건 자체는 여전히 캘리브레이션이 필요하다.
- 팩에 화학 파라미터가 없으면 배수 1.0(화학 효과 없음)을 반환하고 **그 사실을 notes에
  적는다.** 조용히 1.0을 쓰면 "화학을 반영했다"는 거짓말이 된다.
- 이 층의 목표는 순위(A 조성 vs B 조성)를 맞히는 것이지 절대 MRR이 아니다
  (POSITIONING.md §3: 데모 대체가 아니라 스크리닝).
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

_ROOT = Path(__file__).resolve().parent
for _p in ("tier1_empirical", "tier2_physics", "integration"):
    _d = str(_ROOT / _p)
    if _d not in sys.path:
        sys.path.insert(0, _d)

import slurry_components as SC  # noqa: E402  (sim/tier2_physics/slurry_components.py)

# 화학적 연화 → 제거체적 지수. plowing 기하에서 유도된 값이지 튜닝 파라미터가 아니다.
# A_f ∝ H^-1.5 (knowledge/cmp/particle-wafer-interaction-... §4, verify PASS)
SOFTENING_EXPONENT = 1.5


@dataclass
class ChemistryEffect:
    """화학이 만든 MRR 배수와 그 근거."""
    factor: float                       # 기준 조건 대비 MRR 배수
    terms: Dict[str, float] = field(default_factory=dict)   # 항별 기여
    notes: List[str] = field(default_factory=list)
    active: bool = False                # 화학 파라미터가 실제로 있었는가

    def describe(self) -> str:
        if not self.active:
            return "화학층 비활성 (팩에 화학 파라미터 없음) — 배수 1.0"
        parts = ", ".join(f"{k}×{v:.3f}" for k, v in self.terms.items())
        return f"화학 배수 {self.factor:.3f} = {parts}"


def _oxidizer_term(pack, notes: List[str]) -> Optional[float]:
    """산화제 농도 → 기준 농도 대비 상대 MRR (Kaufman 단봉).

    기준 농도(oxidizer_ref_wt_pct, 없으면 현재 농도)에서 1.0이 되도록 나눈다.
    Kp가 그 기준 조성에서 역산된 값이므로 이중 계상을 피하려면 반드시 상대값이어야 한다.
    """
    if not (pack.has("oxidizer_wt_pct") and pack.has("oxidizer_peak_wt_pct")):
        return None
    C = float(pack.get("oxidizer_wt_pct"))
    C_peak = float(pack.get("oxidizer_peak_wt_pct"))
    if C_peak <= 0:
        notes.append("⚠ oxidizer_peak_wt_pct ≤ 0 — 산화제 항 건너뜀")
        return None
    n = float(pack.get_or("oxidizer_curve_n", 2.0))
    if pack.has("oxidizer_ref_wt_pct"):
        C_ref = float(pack.get("oxidizer_ref_wt_pct"))
    else:
        # ⚠ 기준값이 없으면 '현재 농도'로 폴백할 수밖에 없는데, 그러면 항상 자기
        # 자신과 비교하게 되어 배수가 영원히 1.0이다 = 산화제를 바꿔도 반응이 없다.
        # 2026-09-06 민감도 분석에서 산화제가 '미모델링'으로 오진된 원인이었다.
        # 조용히 넘어가지 않고 경고한다.
        C_ref = C
        notes.append("⚠ oxidizer_ref_wt_pct가 팩에 없어 기준=현재 농도로 폴백했다 "
                     "— 산화제 변화가 MRR에 반영되지 않는다. 팩에 기준 농도를 명시하라.")
    cur = float(SC.mrr_oxidizer(C, C_peak, mrr_peak=1.0, n=n))
    ref = float(SC.mrr_oxidizer(C_ref, C_peak, mrr_peak=1.0, n=n))
    if ref <= 0:
        return None
    # 기계적 바닥(mechanical floor): 산화제 0에서도 순수 연마로 MRR이 남는 계가 있다.
    # W/Fe·H2O2 특허 실시예(US20110186542A1, 15조건)에서 H2O2 0 wt%의 MRR이 3 wt% 대비
    # 12~19%로 일정하게 관측됐다 — Kaufman 단봉은 C=0에서 0이라 이를 못 담는다.
    # floor가 팩에 없으면 0(기존 거동 그대로) — 있는 팩만 바뀐다.
    floor = float(pack.get_or("oxidizer_mech_floor", 0.0))
    if floor > 0:
        cur = floor + (1.0 - floor) * cur
        ref = floor + (1.0 - floor) * ref
    return cur / ref


def _inhibitor_term(pack, notes: List[str]) -> Optional[float]:
    """억제제 피복률 → 제거 가능 면적 비율.

    BTA가 Cu 표면을 덮으면 그만큼 제거가 막힌다. Langmuir 등온식.

    ⚠ 왜 (1-θ)를 그대로 쓰지 않는가 (2026-09-06 수정):
      BTA 1mM에서 θ=0.97이라 (1-θ)=0.03이 하한 0.05에 걸리고, 그 위 농도는 전부
      0.05로 포화된다 = **2mM과 5mM의 구분이 사라진다.** 스캔해보면 배수가 1.000으로
      완전히 평평했다. 억제제 농도를 비교하려는 사용자에게 이건 고장난 도구다.

      Langmuir는 '단분자층 피복'이라 θ→1에서 포화되는 게 맞지만, 실제 CMP의 억제
      강도는 피복률만이 아니라 막의 치밀도·재생속도에도 달려 있어 고농도에서도
      계속 세진다. 그래서 잔여 제거 가능률을 (1-θ)가 아니라 **(1-θ)^m 꼴이 아닌,
      막 강도에 대한 지수 감쇠**로 둔다:

          잔여율 = exp(-k_inhib · θ_norm),  θ_norm = K·C/(1+K·C) 의 단조 증가분

      단 이렇게 하면 형상 파라미터 k_inhib가 새로 생긴다 — 문헌값이 없으므로
      팩에서 받고 confidence=unverified로 표기한다. 순위(더 넣으면 덜 깎인다)는
      보존되고, 절대값은 캘리브레이션 대상이다.
    """
    if not pack.has("inhibitor_mM"):
        return None
    C_molar = float(pack.get("inhibitor_mM")) * 1e-3
    if pack.has("inhibitor_dG_ads_kJ"):
        K = SC.K_from_dG_ads(float(pack.get("inhibitor_dG_ads_kJ")) * 1000.0)
    elif pack.has("inhibitor_K_L_per_mol"):
        K = float(pack.get("inhibitor_K_L_per_mol"))
    else:
        notes.append("⚠ inhibitor_mM은 있으나 흡착상수(dG 또는 K)가 없어 억제 항 건너뜀")
        return None
    k_inhib = float(pack.get_or("inhibitor_strength_k", 3.0))

    def _residual(C: float) -> float:
        """농도 C에서 남는 제거 가능률. θ 포화 후에도 단조 감소한다."""
        theta = SC.langmuir_coverage(C, K)
        return math.exp(-k_inhib * theta)

    # 기준 농도 대비 상대값 — Kp가 이미 이 억제제를 포함한 슬러리에서 역산됐으므로
    # 절대값을 곱하면 억제를 두 번 세게 된다(2026-09-06 실제 발생: Cu 20배 하락).
    if pack.has("inhibitor_ref_mM"):
        C_ref = float(pack.get("inhibitor_ref_mM")) * 1e-3
    else:
        C_ref = C_molar
        notes.append("⚠ inhibitor_ref_mM이 팩에 없어 기준=현재 농도로 폴백했다 "
                     "— 억제제 변화가 MRR에 반영되지 않는다.")
    ref = _residual(C_ref)
    if ref <= 0:
        return None
    notes.append(
        f"억제제 {C_molar*1e3:g} mM (기준 {C_ref*1e3:g} mM), θ="
        f"{SC.langmuir_coverage(C_molar, K):.3f}. "
        "⚠ 고농도 감쇠 형상(inhibitor_strength_k)은 문헌값 없음 — 캘리브레이션 대상.")
    return _residual(C_molar) / ref


DISPERSANT_MRR_RELATIVE = {
    "NONE": 1.0,
    "PAA": 1.0,      # Li 2021 §6: "negligible" 저해
    "PAM": 1.0,      # Li 2021 §6: "hardly changed"
    "PVA": 2604.0 / 2700.0,   # -3.6%, Li 2021 §6 Fig.14-15 실측
    "PVP": 2486.0 / 2700.0,   # -7.9%, Li 2021 §6 Fig.14-15 실측
}


def _dispersant_protection_term(pack, notes: List[str]) -> Optional[float]:
    """분산제 흡착 → MRR 저해 배수. ψ의 '표면 흡착 보호' 경로(억제제와 별도).

    Li et al. 2021 (ECS JSS Technol. 10, 123008) §6 실측: 30wt% SiO2 콜로이달
    실리카 슬러리(80nm, pH 11.0, 0.32M K+, 기본 MRR=2700 Å/min)에 분산제를
    첨가했을 때의 MRR 저해를 그대로 옮긴다 — 새 지수·상수는 만들지 않는다.

    ⚠ **반드시 기준 대비 비율로 돌려준다.** 절대 저해율(PVA=0.964)을 그대로
    쓰면 기준 조건에서 ψ≠1.0이 되어 Kp에 이미 반영된 효과를 두 번 센다
    (factors.py 설계계약 §1). 2026-09-11에 실제로 이 사고가 났다 —
    기본 팩이 dispersant_type=PVA인데 절대값 0.964를 반환해
    test_all_factors_are_unity_at_reference_condition 이 FAIL했다.

    `dispersant_ref_type`이 팩에 없으면 **"NONE"(분산제 없음)**을 기준으로 삼는다 —
    그게 Li 2021의 기준선(2700 Å/min)이므로 문헌 의미를 그대로 보존한다.
    다만 팩의 Kp가 특정 분산제 조성에서 역산됐다면 그 팩은 반드시
    `dispersant_ref_type`을 선언해야 한다. 선언하지 않으면 기준 조건에서
    ψ≠1.0이 되어 `test_all_factors_are_unity_at_reference_condition`이 잡아낸다.
    """
    if not pack.has("dispersant_type"):
        return None
    kind = str(pack.get("dispersant_type")).strip().upper()
    if kind not in DISPERSANT_MRR_RELATIVE:
        notes.append(
            f"⚠ dispersant_type='{kind}'는 Li 2021 §6 실측 테이블에 없어 "
            "분산제 보호 항을 건너뛴다.")
        return None
    ref_kind = str(pack.get_or("dispersant_ref_type", "NONE")).strip().upper()
    if ref_kind not in DISPERSANT_MRR_RELATIVE:
        notes.append(
            f"⚠ dispersant_ref_type='{ref_kind}'가 실측 테이블에 없다 — "
            f"기준을 현재 종류({kind})로 대체한다.")
        ref_kind = kind
    rel = DISPERSANT_MRR_RELATIVE[kind] / DISPERSANT_MRR_RELATIVE[ref_kind]
    if kind == ref_kind:
        notes.append(
            f"분산제 흡착 보호: {kind} = 기준 조성이라 배수 1.000 "
            "(Kp가 이 조성에서 역산됐다 — 절대 저해율을 다시 곱하면 이중 계상). "
            "다른 분산제로 바꾸면 그 상대비가 반영된다"
            "(knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md §6, "
            "Li et al. 2021 실측).")
    else:
        notes.append(
            f"분산제 흡착 보호: {kind}/{ref_kind}(기준) → MRR 상대배수 {rel:.3f} "
            f"[절대 저해율 {kind}={DISPERSANT_MRR_RELATIVE[kind]:.3f}, "
            f"{ref_kind}={DISPERSANT_MRR_RELATIVE[ref_kind]:.3f}] "
            "(knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md §6, "
            "Li et al. 2021 실측)")
    return rel


def _ceria_term(pack, notes: List[str]) -> Optional[float]:
    """세리아 chemical tooth — Ce³⁺ 활성점이 Si-O-Ce 결합을 만든다.

    근거: knowledge/cmp/ceria-slurry-ce-redox-selectivity.md
      - 규산 흡착 −111~−258 kJ/mol = 화학흡착 (물리흡착 −20~−40 대비 훨씬 강함)
      - Netzband & Dunn 2020: H₂O₂ 0.5wt%에서 Ce³⁺% 최대 → oxide MRR 5.5배

    ⚠ 이 항은 세리아 슬러리에만 적용된다(abrasive == 'ceria'). 실리카에 쓰면 안 된다 —
    메커니즘 자체가 다르다.
    ⚠ Ce³⁺ 분율과 MRR의 함수형은 문헌에 폐형식으로 없다. 선형 비례로 두되
    그 사실을 notes에 밝힌다. 이건 가정이지 검증된 물리가 아니다.

    함수형 — 왜 순수 비례가 아니라 두 경로의 합인가 (2026-09-13 정정):
      이전 형태 1 + gain·(f/f_ref − 1) 은 gain=1 에서 f→0 일 때 정확히 0 이 됐다.
      즉 "활성점이 없으면 제거율 0" 이라는 주장인데, 이는 물리적으로 거짓이다.
      활성점이 하나도 없어도 입자는 여전히 단단한 산화물이고, 하중을 받아 표면을
      긁는 **기계적 경로**가 남는다(이 노트 §1: 실리카·알루미나는 경도·접촉역학이
      지배하는 거의 순수 기계 연마 — 같은 경로가 세리아에서 사라질 이유가 없다).
      세리아의 특징은 기계 경로가 없다는 게 아니라 그 위에 화학 경로가 **더해져서**
      지배적이 된다는 것이다.

      그래서 제거를 두 경로의 합으로 쓴다:
          f(θ) = (1−a) + a·(θ/θ_ref)
      a = 기준 조건에서 화학(활성점) 경로가 차지하는 분율.
      θ→0 에서 (1−a) 로 유한하게 남고(기계 경로), θ=θ_ref 에서 정확히 1 이다.

      a 는 실측에서 나온다. Netzband & Dunn 2020 은 H₂O₂ 로 Ce³⁺% 를 올려 산화막
      MRR 이 상용 대비 5.5 배가 됐다고 보고한다. 화학 경로가 5.5 배 구간을
      만들어냈다면 기준 조건에서 기계 경로의 몫은 대략 1/5.5 ≈ 0.18 이므로
      a ≈ 0.82. 팩이 ceria_mechanical_floor 로 (1−a) 를 직접 주면 그것을 쓴다.

      ⚠ 이 분해 자체가 문헌의 폐형식이 아니라 5.5배 관측에서 역산한 가정이다.
      다만 극한에서 물리적으로 옳다는 점이 이전 형태와 다르다.
    """
    if str(pack.get_or("abrasive", "")) != "ceria":
        return None
    if not pack.has("ce3_fraction"):
        return None
    f = float(pack.get("ce3_fraction"))
    f_ref = float(pack.get_or("ce3_fraction_ref", 0.15))
    if f_ref <= 0:
        return None
    gain = float(pack.get_or("ceria_tooth_gain", 1.0))
    # 기계 바닥값 — 활성점이 0 이어도 남는 몫. 기본 1/5.5 (Netzband 5.5배에서 역산).
    floor = float(pack.get_or("ceria_mechanical_floor", 1.0 / 5.5))
    floor = min(max(floor, 0.0), 1.0)
    a = (1.0 - floor) * gain
    notes.append(
        f"세리아 chemical tooth: Ce³⁺ 분율 {f:.3f} (기준 {f_ref:.3f}). "
        f"화학 경로 {a * 100:.0f}% + 기계 경로 {floor * 100:.0f}% 로 분해 — "
        "활성점이 0 이어도 입자는 단단한 산화물이라 기계적 제거가 남는다. "
        "⚠ Ce³⁺–MRR 함수형은 문헌에 폐형식이 없어 활성점 수에 선형으로 가정했고, "
        "분해 비율은 Netzband & Dunn 2020 의 5.5배 관측에서 역산했다 — 미검증.")
    return floor + a * (f / f_ref)


def _ph_softening_term(pack, notes: List[str]) -> Optional[float]:
    """pH → 표면 연화 기여 (경도비를 통해 들어간다).

    ⚠ 가장 약한 항이다. pH가 용해도·표면전하를 바꾸는 건 확실하지만, 그것이
    '유효 경도'로 얼마나 번역되는지는 재료·슬러리마다 다르고 우리에겐 데이터가 없다.
    팩이 명시적으로 ph_softening_per_unit을 주지 않으면 **아예 적용하지 않는다.**
    """
    if not (pack.has("slurry_ph") and pack.has("ph_softening_ref")
            and pack.has("ph_softening_per_unit")):
        return None
    ph = float(pack.get("slurry_ph"))
    ph_ref = float(pack.get("ph_softening_ref"))
    k = float(pack.get("ph_softening_per_unit"))
    # 경도비 H/H0 = 1 - k*(pH - pH_ref), 하한 0.2로 클램프(경도가 0이 되진 않는다)
    h_ratio = max(1.0 - k * (ph - ph_ref), 0.2)
    notes.append(f"pH 연화: pH {ph:g} → 유효경도비 {h_ratio:.3f} "
                 "(⚠ 선형 가정, 미검증)")
    return h_ratio ** (-SOFTENING_EXPONENT)


def chemistry_factor(pack) -> ChemistryEffect:
    """팩의 화학 파라미터를 읽어 MRR 배수를 만든다.

    각 항은 독립이라 가정하고 곱한다. 실제로는 상호작용이 있다(예: pH가 BTA 흡착에
    영향) — 그 커플링은 아직 모델링하지 않았고, 이 사실을 notes에 남긴다.
    """
    notes: List[str] = []
    terms: Dict[str, float] = {}

    for name, fn in (("oxidizer", _oxidizer_term),
                     ("inhibitor", _inhibitor_term),
                     ("ceria_tooth", _ceria_term),
                     ("ph_softening", _ph_softening_term)):
        v = fn(pack, notes)
        if v is not None:
            terms[name] = v

    if not terms:
        return ChemistryEffect(
            factor=1.0, terms={}, active=False,
            notes=["화학층 비활성: 팩에 화학 파라미터(oxidizer/inhibitor/ce3_fraction 등)가 "
                   "없어 MRR에 화학 효과를 반영하지 않았다. Kp에 뭉뚱그려진 상태."])

    factor = 1.0
    for v in terms.values():
        factor *= v

    if len(terms) > 1:
        notes.append("⚠ 화학 항들을 독립으로 보고 곱했다. 실제로는 pH-흡착, 산화제-세리아 "
                     "산화환원 같은 커플링이 있다 — 미모델링.")
    return ChemistryEffect(factor=factor, terms=terms, notes=notes, active=True)
