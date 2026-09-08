"""병합 파라미터 (Merged Factors) — ARCHITECTURE-V2.md §2의 구현.

왜 이게 필요한가
────────────────
입력 필드가 468개다. "무엇이 결과를 어떻게 바꾸는지" 파악이 불가능하다.
연관 인자를 물리적으로 묶어 **10개 파라미터**로 만들고, 각 파라미터가
①결과를 어떻게 바꾸는가 ②그걸 바꾸려면 무엇을 만져야 하는가를 동시에 답하게 한다.

분리 규칙 (사용자 확정, 2026-09-08)
────────────────────────────────
- **장비축(Λ Π Θ Γ)과 소모품축(κ χ ψ τ Δ S)을 섞지 않는다.** 장비는 부하를 가하고,
  소모품은 그 부하에 반응한다. 섞으면 "슬러리를 바꿔야 하나 RPM을 올려야 하나"에
  답할 수 없다 — 그 비교가 이 도구의 존재 이유다.
- **웨이퍼는 팩터가 아니다.** 대상막질이자 기준선이지 조절 손잡이가 아니다.

설계 계약 (어기면 V1의 실패가 반복된다)
──────────────────────────────────
1. **모든 팩터는 기준 조건에서 정확히 1.0.** 절대값을 쓰면 Kp에 이미 반영된 효과를
   두 번 센다 — 2026-09-06 Cu MRR 20배 붕괴가 그 사고였다.
2. **파라미터가 없으면 조용히 1.0을 쓰지 않고 `status='unmodeled'`로 신고한다.**
   조용한 1.0은 "화학을 반영했다"는 거짓말이 된다.
3. **각 팩터는 자기 drivers(어느 입력에서 왔나)를 신고한다.** 이게 있어야
   "κ를 올리려면 무엇을 만지나"에 기계가 답한다.
4. 팩터를 붙였으면 스캔해 응답 곡선을 눈으로 확인한다. 단위테스트 통과는 증거가 아니다
   (Langmuir θ가 1mM에서 0.97로 포화해 2mM/5mM이 구분 안 됐던 전례).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # 순환 import 방지 — engine이 factors를 쓴다
    from sim.engine import ResolvedRecipe

# ─────────────────────────────────────────────────────────── 축 정의
AXIS_EQUIPMENT = "equipment"
AXIS_CONSUMABLE = "consumable"

#: 팩터 → (기호, 이름, 축, 어느 파트가 driver인가)
#: `parts`는 UI에서 "이걸 바꾸려면 어느 탭을 열어야 하나"로 쓰인다.
FACTOR_SPEC = {
    # ── 장비축 — 소모품과 묶지 않는다
    "lambda": ("Λ", "기계 부하 강도", AXIS_EQUIPMENT, ["tool"]),
    "pi":     ("Π", "반경 하중 분포", AXIS_EQUIPMENT, ["tool"]),
    "theta":  ("Θ", "열·유동 부하",   AXIS_EQUIPMENT, ["tool"]),
    "gamma":  ("Γ", "컨디셔닝 부하",  AXIS_EQUIPMENT, ["tool"]),
    # ── 소모품축 — 슬러리·패드·디스크가 함께 결정
    "kappa":  ("κ", "접촉 강도",     AXIS_CONSUMABLE, ["slurry", "pad", "disk"]),
    "chi":    ("χ", "화학 반응성",   AXIS_CONSUMABLE, ["slurry"]),
    "psi":    ("ψ", "표면 보호도",   AXIS_CONSUMABLE, ["slurry"]),
    "tau":    ("τ", "슬러리 전달",   AXIS_CONSUMABLE, ["slurry", "pad", "disk"]),
    "delta":  ("Δ", "손상 유발도",   AXIS_CONSUMABLE, ["slurry", "pad", "disk"]),
    "stab":   ("S", "시간 안정성",   AXIS_CONSUMABLE, ["slurry", "pad", "disk"]),
}

#: 팩터가 MRR에 곱해지는가, 아니면 진단 전용인가.
#: ⚠ 여기에 넣는 순간 이중 계상 위험이 생긴다 — 기준 1.0 계약을 반드시 확인할 것.
#: τ는 결합이 매우 약하다(지수 0.07) — 그래도 넣는 이유는 사용자가 그루브를
#: 바꿨을 때 "아무 반응 없음"과 "약하게 반응함"을 구분해야 하기 때문이다.
#: 실측이 말하는 것은 '효과 없음'이 아니라 '효과가 작음'이다.
MRR_COUPLED = {"chi", "psi", "kappa", "tau"}


@dataclass
class Factor:
    """병합 파라미터 하나. 값 + 근거 + 무엇을 만지면 바뀌는가."""
    key: str
    symbol: str
    name: str
    axis: str
    parts: List[str]
    value: Optional[float] = None          # 기준 조건 대비 배수 (기준=1.0)
    status: str = "unmodeled"              # modeled | partial | unmodeled
    drivers: Dict[str, float] = field(default_factory=dict)   # 입력 필드 → 현재값
    terms: Dict[str, float] = field(default_factory=dict)     # 항별 기여
    confidence: str = "unverified"         # verified | literature | estimated | unverified
    sources: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def mrr_coupled(self) -> bool:
        return self.key in MRR_COUPLED

    def describe(self) -> str:
        if self.status == "unmodeled":
            return (f"{self.symbol} {self.name}: 미모델링 — "
                    f"필요 파라미터가 팩에 없다. '영향 없음'이 아니다.")
        parts = ", ".join(f"{k}×{v:.3f}" for k, v in self.terms.items())
        tail = f" = {parts}" if parts else ""
        return f"{self.symbol} {self.name}: {self.value:.3f}{tail} [{self.confidence}]"

    def to_dict(self) -> Dict:
        return {
            "key": self.key, "symbol": self.symbol, "name": self.name,
            "axis": self.axis, "parts": self.parts,
            "value": self.value, "status": self.status,
            "drivers": self.drivers, "terms": self.terms,
            "confidence": self.confidence, "sources": self.sources,
            "notes": self.notes, "mrr_coupled": self.mrr_coupled,
        }


def _new(key: str) -> Factor:
    sym, name, axis, parts = FACTOR_SPEC[key]
    return Factor(key=key, symbol=sym, name=name, axis=axis, parts=list(parts))


def _worst_conf(*confs: str) -> str:
    """여러 근거를 합칠 때 신뢰도는 가장 약한 것을 따른다."""
    order = ["verified", "measured", "literature", "estimated", "unverified"]
    idx = max((order.index(c) if c in order else len(order) - 1) for c in confs) \
        if confs else len(order) - 1
    return order[min(idx, len(order) - 1)]


def _pack_conf(pack, *keys: str) -> str:
    confs = []
    for k in keys:
        if pack.has(k):
            try:
                confs.append(pack.param(k).confidence or "unverified")
            except Exception:
                confs.append("unverified")
    return _worst_conf(*confs) if confs else "unverified"


# ═══════════════════════════════════════════════════ 장비축 (Equipment)

def _f_lambda(rr: "ResolvedRecipe") -> Factor:
    """Λ 기계 부하 강도 = P·V (Preston 곱, 단위면적 마찰일률).

    Preston MRR = Kp·P·V 에서 Kp를 뺀 나머지 전부. 장비가 웨이퍼에 가하는
    기계적 부하를 단일 숫자로 압축한 것이다.

    기준: 팩의 pressure_psi × (그 조건의 상대속도). 기준 조건에서 1.0.
    """
    f = _new("lambda")
    P = float(rr.pressure_psi)
    # 상대속도 대표값: 웨이퍼 중심(r=r_cc)에서의 전형 상대속도.
    # 회전 CMP의 상대속도는 Rs=1일 때 반경 무관하게 ω_p·r_cc 이다
    # (knowledge/physics/cmp-kinematics-rotary.md — verify PASS).
    omega_p = float(rr.rpm_platen) * 2.0 * math.pi / 60.0
    V = omega_p * float(rr.center_offset_m)
    f.drivers = {
        "pressure_psi": P,
        "rpm_platen": float(rr.rpm_platen),
        "rpm_wafer": float(rr.rpm_wafer),
        "center_offset_m": float(rr.center_offset_m),
    }
    pk = rr.pack
    P_ref = float(pk.get_or("lambda_ref_pressure_psi", P))
    rpm_ref = float(pk.get_or("lambda_ref_rpm_platen", float(rr.rpm_platen)))
    rcc_ref = float(pk.get_or("lambda_ref_center_offset_m", float(rr.center_offset_m)))
    V_ref = rpm_ref * 2.0 * math.pi / 60.0 * rcc_ref
    denom = P_ref * V_ref
    if denom <= 0:
        f.notes.append("⚠ 기준 P·V가 0 이하 — Λ 계산 불가")
        return f
    f.value = (P * V) / denom
    f.terms = {"P": P / P_ref if P_ref else 1.0, "V": V / V_ref if V_ref else 1.0}
    f.status = "modeled"
    f.confidence = _pack_conf(pk, "pressure_psi", "rpm_platen", "center_offset_m")
    f.sources = ["knowledge/physics/cmp-kinematics-rotary.md",
                 "knowledge/cmp/preston-luo-dornfeld-mrr.md"]
    f.notes.append(f"P·V = {P*V:.4g} psi·m/s (기준 대비 {f.value:.3f}배)")
    if not pk.has("lambda_ref_pressure_psi"):
        f.notes.append("⚠ lambda_ref_* 가 팩에 없어 기준=현재 조건으로 폴백 "
                       "— Λ이 항상 1.0이 되어 비교 기능이 죽는다. 팩에 기준을 명시하라.")
    return f


def _f_pi(rr: "ResolvedRecipe") -> Factor:
    """Π 반경 하중 분포 — 존압력·리테이너링이 만드는 P(r) 형상.

    Λ이 '얼마나 세게'라면 Π는 '어디를 세게'다. TTV/WIWNU를 지배하는 축이고,
    Λ과 직교해야 한다(전체를 키우면 Λ, 기울기를 바꾸면 Π).

    정의: 정규화 P(r)/P̄ 의 엣지/센터 비. 균일하면 1.0.
    """
    f = _new("pi")
    zp = rr.zone_pressures_psi
    amp = float(rr.edge_pressure_amp or 0.0)
    f.drivers = {"edge_pressure_amp": amp}
    if zp:
        for i, v in enumerate(zp):
            f.drivers[f"zone_pressures_psi[{i}]"] = float(v)
    if not zp and amp == 0.0:
        f.value = 1.0
        f.status = "modeled"
        f.terms = {"uniform": 1.0}
        f.confidence = "verified"   # 균일은 정의상 참
        f.notes.append("균일 압력 — Π=1.0 (존압력·엣지집중 없음)")
        return f
    if zp:
        mean = sum(float(v) for v in zp) / len(zp)
        if mean <= 0:
            f.notes.append("⚠ 존 평균 압력이 0 이하 — Π 계산 불가")
            return f
        f.value = float(zp[-1]) / mean          # 최외곽 존 / 평균
        f.terms = {"edge_zone_ratio": f.value}
        f.status = "modeled"
        f.confidence = "literature"
        f.sources = ["knowledge/equipment/cmp-multizone-carrier-radial-response.md"]
        f.notes.append(f"최외곽 존/평균 = {f.value:.3f} (>1 엣지강조, <1 엣지완화)")
    else:
        f.value = 1.0 + amp
        f.terms = {"edge_amp": f.value}
        f.status = "partial"
        f.confidence = "estimated"
        f.notes.append(f"엣지 압력 집중 진폭 {amp:g} 만 반영 — 존압력 없음")
    if not rr.pack.has("retaining_ring_pressure_psi"):
        f.notes.append("⚠ 리테이닝 링 압력이 팩에 없다 — 엣지 프로파일의 주요 축이 빠졌다. "
                       "담당 tool-platen-head.")
    return f


def _f_theta(rr: "ResolvedRecipe") -> Factor:
    """Θ 열·유동 부하 — 마찰 발열과 슬러리 냉각/공급의 균형.

    발열은 Λ에 비례하고(마찰일률), 냉각·공급은 SFR에 비례한다.
    온도는 Arrhenius로 화학속도를, 유량은 신선 슬러리 공급을 지배한다.

    ⚠ 절대 온도가 아니라 **기준 대비 부하비**다. 실제 ΔT 예측은
    knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md 의
    모델이 담당하고, 여기서는 팩터로 압축만 한다.
    """
    f = _new("theta")
    pk = rr.pack
    if not pk.has("sfr_ml_min"):
        f.notes.append("⚠ Θ 미모델링: SFR(슬러리 유량)이 팩·레시피에 없다. "
                       "유량은 실제 툴에서 가장 자주 만지는 손잡이인데 엔진에 통로가 없다. "
                       "담당 tool-platen-head.")
        f.drivers = {}
        return f
    sfr = float(pk.get("sfr_ml_min"))
    sfr_ref = float(pk.get_or("sfr_ref_ml_min", sfr))
    lam = _f_lambda(rr)
    f.drivers = {"sfr_ml_min": sfr}
    f.drivers.update(lam.drivers)
    if sfr_ref <= 0 or lam.value is None:
        f.notes.append("⚠ 기준 SFR 또는 Λ 결측 — Θ 계산 불가")
        return f
    # 부하비 = 발열(Λ) / 냉각(SFR). 기준 조건에서 1.0.
    f.value = lam.value / (sfr / sfr_ref)
    f.terms = {"heat(Λ)": lam.value, "cool(SFR)": sfr / sfr_ref}
    f.status = "partial"
    f.confidence = _worst_conf(_pack_conf(pk, "sfr_ml_min"), "estimated")
    f.sources = ["knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md",
                 "knowledge/equipment/cmp-rpm-ratio-flowrate-temperature-mrr-stability.md"]
    f.notes.append("⚠ 발열/냉각을 1차 비례로 압축했다 — 실제 열저항·체류시간은 "
                   "미반영. 절대 ΔT는 별도 열모델이 담당한다.")
    if not pk.has("sfr_ref_ml_min"):
        f.notes.append("⚠ sfr_ref_ml_min 없어 기준=현재값 폴백 — SFR 변화가 Θ에 안 잡힌다.")
    return f


def _f_gamma(rr: "ResolvedRecipe") -> Factor:
    """Γ 컨디셔닝 부하 — 디스크가 패드에 가하는 단위시간 절삭일.

    ⚠ 여기는 **장비 설정**(하중·스윕·duty)만 담는다. 디스크의 형상(그릿 밀도·
    돌출)은 소모품이므로 κ/τ 쪽으로 간다. 이 분리를 지켜야 "디스크를 바꿀까
    컨디셔너 세팅을 바꿀까"에 답할 수 있다.
    """
    f = _new("gamma")
    pk = rr.pack
    needed = ["cond_downforce_lbf", "cond_sweep_cpm", "cond_duty_pct"]
    have = [k for k in needed if pk.has(k)]
    if not have:
        f.notes.append("⚠ Γ 미모델링: 컨디셔너 하중·스윕·duty 중 어느 것도 팩에 없다. "
                       "패드 절삭률(PCR)이 MRR 안정성을 지배하는데 통로가 없다. "
                       "담당 disk-conditioner.")
        return f
    F = float(pk.get_or("cond_downforce_lbf", 0.0))
    sweep = float(pk.get_or("cond_sweep_cpm", 0.0))
    duty = float(pk.get_or("cond_duty_pct", 100.0))
    f.drivers = {"cond_downforce_lbf": F, "cond_sweep_cpm": sweep, "cond_duty_pct": duty}
    F_ref = float(pk.get_or("cond_ref_downforce_lbf", F or 1.0))
    sweep_ref = float(pk.get_or("cond_ref_sweep_cpm", sweep or 1.0))
    duty_ref = float(pk.get_or("cond_ref_duty_pct", duty or 100.0))
    denom = F_ref * sweep_ref * duty_ref
    if denom <= 0:
        f.notes.append("⚠ 기준 컨디셔닝 부하가 0 — Γ 계산 불가")
        return f
    f.value = (F * sweep * duty) / denom
    f.terms = {"force": F / F_ref if F_ref else 1.0,
               "sweep": sweep / sweep_ref if sweep_ref else 1.0,
               "duty": duty / duty_ref if duty_ref else 1.0}
    f.status = "modeled" if len(have) == len(needed) else "partial"
    f.confidence = _worst_conf(_pack_conf(pk, *have), "estimated")
    f.sources = ["knowledge/equipment/conditioner-disk-pad-cutting-model.md",
                 "knowledge/equipment/disk-rpm-load-radius-pcr.md"]
    if f.status == "partial":
        missing = [k for k in needed if k not in have]
        f.notes.append(f"⚠ 부분 모델링 — 결측: {', '.join(missing)}")
    f.notes.append("⚠ force×sweep×duty 곱 형태는 절삭일률의 1차 근사다 — "
                   "임계하중(critical downforce) 아래에서는 절삭이 안 일어난다는 "
                   "비선형이 미반영. disk-conditioner 노트 참조.")
    return f


# ═══════════════════════════════════════════════════ 소모품축 (Consumable)

def _f_kappa(rr: "ResolvedRecipe") -> Factor:
    """κ 접촉 강도 = 활성 입자 수 × 입자당 압입 깊이.

    **세 파트가 함께 결정하는 대표 팩터다.**
      - 슬러리: 입경 R, 함량 → 접촉 입자 수
      - 패드:   경도 H, 탄성률 → 입자당 하중과 압입
      - 디스크: asperity 밀도 → 실접촉 면적

    물리: δ_p = F/(2πR·H) 이고 제거 단면 A_f ∝ δ_p^1.5 ⟹ **MRR ∝ H^-1.5**
    (knowledge/cmp/particle-wafer-interaction-... §4, verify PASS).

    ⚠ 화학적 연화(χ)도 같은 H를 통해 들어간다. **두 번 세지 않도록** κ는
    '기계적 경도'만, χ는 '화학이 만든 경도 변화분'만 담당한다.
    """
    f = _new("kappa")
    pk = rr.pack
    terms: Dict[str, float] = {}
    srcs: List[str] = []

    # ① 슬러리: 입자 함량 → 접촉 입자 수 (1차: 선형)
    if pk.has("abrasive_wt_pct"):
        c = float(pk.get("abrasive_wt_pct"))
        f.drivers["abrasive_wt_pct"] = c
        c_ref = float(pk.get_or("abrasive_ref_wt_pct", c))
        if c_ref > 0 and c > 0:
            # Li et al. 2021(doi:10.1149/2162-8777/ac3e44)이 인용한 두 극한 모델:
            #   표면적 지배  R ∝ C0^(1/3)
            #   압입 지배    R ∝ C0^(4/3)
            # 논문이 직접 서술·검증한 것은 **방향(농도↑→MRR↑)뿐**이고 어느 지수가
            # 맞는지는 미확정이다. 기본값은 보수적으로 표면적 극한(1/3)을 쓰고,
            # 팩이 명시하면 그걸 따른다.
            n = float(pk.get_or("abrasive_conc_exponent", 1.0 / 3.0))
            terms["conc"] = (c / c_ref) ** n
            srcs.append("knowledge/cmp/abrasive-size-concentration-"
                        "ph-K-additive-mrr-quantitative.md")
            f.notes.append(f"⚠ 농도 지수 n={n:.3f} — 문헌은 1/3(표면적)~4/3(압입) 두 극한만 "
                           "제시하고 어느 쪽인지 정하지 않았다. 순위는 신뢰, 크기는 "
                           "캘리브레이션 대상.")
            # Luo-Dornfeld 포화: 7 wt% 이상에서 RR 불변이 관측된 계가 있다.
            sat = pk.get_or("abrasive_saturation_wt_pct", None)
            if sat is not None and c > float(sat):
                f.notes.append(f"⚠ 입자 함량 {c:g} wt%가 포화농도 {float(sat):g} wt%를 "
                               "넘었다 — 실제로는 더 넣어도 MRR이 안 오른다"
                               "(Luo-Dornfeld 포화영역). 현재 항은 계속 증가시키므로 "
                               "이 구간 예측은 과대평가다.")

    # ② 슬러리: 입경 → 입자당 압입 (δ_p ∝ 1/R)
    if pk.has("abrasive_size_nm"):
        d = float(pk.get("abrasive_size_nm"))
        f.drivers["abrasive_size_nm"] = d
        d_ref = float(pk.get_or("abrasive_ref_size_nm", d))
        if d_ref > 0 and d > 0:
            # ⚠ 입경 방향의 지수는 **문헌이 확정하지 못했다.**
            # Li et al. 2021은 40→80→130 nm에서 MRR이 80 nm에 정점을 갖는다고
            # 정성 서술하지만(압입지배→표면적지배 전환), 원문 Eq.3-4의 지수·부호가
            # OCR로 뒤섞여 노트조차 입경 방향을 assert하지 않았다.
            # 그러므로 **지수를 지어내지 않는다.** 팩이 명시할 때만 적용한다.
            n_size = pk.get_or("abrasive_size_exponent", None)
            if n_size is None:
                f.notes.append(
                    "⚠ 입경 항 미적용: 지수(abrasive_size_exponent)가 팩에 없다. "
                    "문헌은 정점형(~80nm 최대)이라고만 서술하고 지수를 확정하지 "
                    "못했으므로 임의값을 쓰지 않는다 — 입경을 바꿔도 κ가 변하지 "
                    "않는다는 뜻이다. 단조 지수를 넣으면 정점 거동을 놓친다.")
            else:
                terms["size"] = (d / d_ref) ** float(n_size)
                srcs.append("knowledge/cmp/abrasive-size-concentration-"
                            "ph-K-additive-mrr-quantitative.md")
                f.notes.append(
                    f"⚠ 입경 지수 {float(n_size):g}는 팩이 지정한 값이다. 문헌은 "
                    "정점형(40→80nm 증가, 80→130nm 감소)이라 단조 멱함수로는 "
                    "한쪽 구간만 맞는다 — 적용 범위를 확인하라.")

    # ③ 패드: 경도 → MRR ∝ H^-1.5
    if pk.has("pad_hardness_shore_d"):
        h = float(pk.get("pad_hardness_shore_d"))
        f.drivers["pad_hardness_shore_d"] = h
        h_ref = float(pk.get_or("pad_ref_hardness_shore_d", h))
        if h_ref > 0 and h > 0:
            terms["pad_hardness"] = (h / h_ref) ** (-1.5)
            srcs.append("knowledge/materials/pad-hardness-porosity-"
                        "measurement-methods.md")
            f.notes.append("⚠ Shore D는 경도의 대리지표다. H^-1.5의 H는 압입경도"
                           "(GPa)인데 Shore D↔GPa 환산이 비선형이라 순위는 맞아도 "
                           "절대값은 캘리브레이션이 필요하다.")

    # ④ 디스크: asperity 밀도 → 실접촉 면적
    if pk.has("asperity_density_per_m2"):
        n_a = float(pk.get("asperity_density_per_m2"))
        f.drivers["asperity_density_per_m2"] = n_a
        n_ref = float(pk.get_or("asperity_ref_density_per_m2", n_a))
        if n_ref > 0 and n_a > 0:
            terms["asperity"] = (n_a / n_ref) ** 0.5
            srcs.append("knowledge/physics/gw-contact.md")
            f.notes.append("⚠ asperity 밀도 지수 0.5는 GW 접촉에서 실접촉면적이 "
                           "밀도의 제곱근에 가깝게 증가한다는 근사다 — 미검증.")

    if not terms:
        f.notes.insert(0, "⚠ κ 미모델링: 입자 함량·입경·패드 경도·asperity 밀도가 "
                          "전부 팩에 없다. 소모품을 바꿔도 결과가 안 변한다 "
                          "— 이것이 V1의 핵심 결함이었다.")
        return f

    val = 1.0
    for v in terms.values():
        val *= v
    f.value = val
    f.terms = terms
    # 네 항이 다 있어야 modeled. 하나라도 빠지면 partial.
    f.status = "modeled" if len(terms) >= 4 else "partial"
    f.confidence = _worst_conf(
        _pack_conf(pk, "abrasive_wt_pct", "abrasive_size_nm",
                   "pad_hardness_shore_d", "asperity_density_per_m2"),
        "estimated")
    f.sources = sorted(set(srcs))
    if f.status == "partial":
        f.notes.append(f"⚠ 부분 모델링 — 반영된 항 {len(terms)}/4: "
                       f"{', '.join(terms)}")
    return f


def _ph_peak_term(pack, notes: List[str]) -> Optional[float]:
    """pH → MRR, **정점형(peaked)** 거동.

    왜 별도 항인가:
      chemistry.py의 `_ph_softening_term`은 경도비를 pH의 **단조 선형**으로 본다.
      그런데 실측은 정점형이다 — Li et al. 2021 (doi:10.1149/2162-8777/ac3e44, Fig.1,
      20 wt% 실리카·K⁺ 0.25 M·SiO₂ 막):

          pH 10.0 → 1551 Å/min
          pH 11.0 → 1727 Å/min   ← 정점
          pH 12.5 → 1407 Å/min

      메커니즘도 두 갈래다: pH↑는 Si-O-Si 가수분해로 표면을 연화시켜 MRR을 올리지만
      (10→11, +11.3%), 과잉 OH⁻는 입자·표면을 동시에 강한 음전하로 만들어 정전 반발이
      기계적 접촉을 막아 MRR을 떨어뜨린다(11→12.5, −18.5%).

      **단조 모델을 쓰면 pH 12.5를 과대평가한다.** 소재 개발자가 pH를 올려보는
      시뮬레이션에서 이건 틀린 방향을 가리키는 것이라 그냥 부정확한 정도가 아니다.

    형태: 정점에서 1차 미분이 0인 가장 단순한 형태로 2차 감쇠를 쓴다.
        f(pH) = 1 - a·(pH - pH_peak)²
      계수 a는 실측 두 점(10.0, 12.5)에서 비대칭이므로 양쪽을 따로 맞춘다.
      ⚠ 2차 형태 자체는 문헌이 제시한 게 아니라 3점을 지나는 최소 가정이다.
    """
    if not (pack.has("slurry_ph") and pack.has("ph_peak") and pack.has("ph_ref")):
        return None
    ph = float(pack.get("slurry_ph"))
    ph_pk = float(pack.get("ph_peak"))
    ph_ref = float(pack.get("ph_ref"))

    # 실측 3점에서 뽑은 양쪽 곡률. 팩이 덮어쓸 수 있게 열어둔다.
    # 좌: (11.0 - 10.0)=1.0 떨어질 때 1727→1551 = 0.898 ⟹ a_lo = 0.102
    # 우: (12.5 - 11.0)=1.5 떨어질 때 1727→1407 = 0.815 ⟹ a_hi = 0.185/2.25 = 0.0823
    a_lo = float(pack.get_or("ph_curvature_low", 0.102))
    a_hi = float(pack.get_or("ph_curvature_high", 0.0823))

    def _rel(x: float) -> float:
        d = x - ph_pk
        a = a_lo if d < 0 else a_hi
        return max(1.0 - a * d * d, 0.05)   # 물리적으로 0 이하가 될 수 없다

    cur, ref = _rel(ph), _rel(ph_ref)
    if ref <= 0:
        return None
    notes.append(
        f"pH {ph:g} (정점 {ph_pk:g}, 기준 {ph_ref:g}) → 상대 {cur/ref:.3f}. "
        "실측 3점(Li 2021 Fig.1) 기반 정점형. "
        "⚠ 2차 감쇠 형태는 3점을 지나는 최소 가정이지 문헌 폐형식이 아니다.")
    if ph > 12.5 or ph < 10.0:
        notes.append(f"⚠ pH {ph:g}는 실측 범위(10.0~12.5) 밖이다 — 외삽이다.")
    return cur / ref


def _ph_ceria_electrostatic_term(pack, notes: List[str]) -> Optional[float]:
    """세리아 슬러리의 pH → MRR — **정전 인력 창(window)** 거동.

    실리카 슬러리의 pH 정점(11.0)과는 **메커니즘도, 방향도 다르다.**
    실리카 팩의 `_ph_peak_term`을 세리아에 상속시켜 쓰면 pH 10에서 최대라고
    예측하는데, 실측은 정반대다:

      Dandu 2009 (doi:10.1149/1.3230624, Fig.2a, SiO₂ / 0.25 wt% 세리아 60 nm / 4 psi):
          pH 2.0 →   4.3 nm/min
          pH 3.0 →  95.3
          pH 3.5 → 276.3
          pH 4.0 → 347.4  ┐
          pH 5.0 → 344.3  │ 플래토 (~350)
          pH 5.5 → 350.4  ┘
          pH 6.0 →  99.3  ← 급락
          pH 8.0 →  69.4
          pH 10  →  64.3

    물리 (knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §4, verify PASS):
      표면전하 부호 = sign(IEP − pH). 세리아 IEP ≈ 6.8, 실리카 IEP ≈ 2.5.
      **두 IEP 사이(2.5 < pH < 6.8)에서만** 세리아(+)·실리카(−)가 반대부호라
      정전 인력이 입자를 웨이퍼로 끌어당겨 Si-O-Ce 결합을 촉진한다. 그 창 밖에서는
      같은 부호로 반발한다 → MRR 급락. pH 6 부근은 세리아 IEP에 근접해 제타≈0,
      응집까지 겹친다.

    구현: 창 안에서 플래토, 양 끝에서 IEP까지 시그모이드 감쇠. 창 밖 잔류값은
    실측(pH 8~10에서 정점의 ~19%)에서 뽑는다.
      ⚠ 시그모이드 폭·잔류율은 Dandu 한 편의 실측 3구간에서 역산한 값이다.
        형태 자체가 문헌 폐형식은 아니다 — 순위·창 위치는 물리(IEP)가 주고,
        기울기는 캘리브레이션 대상이다.

    ⚠⚠ 알려진 반례 — 숨기지 않는다 (2026-09-08 백테스트):
      Netzband & Dunn 2020 (doi:10.1149/2162-8777/ab8393, 열산화막, 1 wt% 세리아,
      2.25 cm² 벤치탑 쿠폰)은 pH 4→19.8, 6→11.3, 8→20.0, 10→21.3 nm/min으로
      **pH 10이 최고**다. 이 모델은 pH 10을 잔류 18%로 예측하므로 그 데이터셋에서
      ρ=−0.80이 나온다. 이 모델을 넣기 전 dandu2009는 ρ=−0.525였고 넣은 뒤
      +0.933이 됐다 — 한쪽을 맞추면 다른 쪽이 깨지는 **진짜 상충**이다.

      왜 다른가(가설, 미검증): Netzband의 전체 MRR 폭은 11~21(2배)인 반면 Dandu는
      4~350(80배)이다. Netzband는 쿠폰 실험이라 접촉 압력·슬러리 교체가 양산
      폴리셔와 다르고, 1 wt%는 0.25 wt%보다 입자가 4배 많아 정전 반발이 있어도
      기계 접촉이 유지될 수 있다. 즉 정전 창은 **저농도·양산 스케일에서 지배적**이고
      고농도·쿠폰에서는 부차적일 수 있다. 이걸 농도 의존 창 깊이로 넣으려면
      두 논문 사이를 잇는 중간 농도 데이터가 필요하다 — 지금은 없다.

      선택: 양산 스케일(사용자의 실제 사용 조건)을 맞추는 Dandu를 따른다.
      Netzband 조건(고농도·쿠폰)에서는 이 모델이 틀릴 수 있음을 notes로 신고한다.
    """
    if str(pack.get_or("abrasive", "")) != "ceria":
        return None
    if not (pack.has("slurry_ph") and pack.has("abrasive_iep_ph")):
        return None
    ph = float(pack.get("slurry_ph"))
    iep_ceria = float(pack.get("abrasive_iep_ph"))            # ~6.8
    iep_wafer = float(pack.get_or("wafer_iep_ph", 2.5))       # 실리카 산화막
    ph_ref = float(pack.get_or("ph_ref", ph))

    # 실측 역산 파라미터 — 팩이 덮어쓸 수 있다.
    # ⚠ 창 밖 잔류값은 **양쪽이 다르다** — 물리가 다르기 때문이다:
    #   산성 쪽(pH<2.5): 둘 다 (+)이나 실리카는 IEP 직하라 거의 무전하 → 인력도
    #     반발도 약하고 세리아 자체가 용출 → 거의 0 (실측 1%).
    #   염기 쪽(pH>6.8): 둘 다 (−) 강반발이지만 Si-O-Ce chemical tooth는 살아 있어
    #     기계적 접촉만으로도 일부 제거 → ~18% 잔류.
    #   단일 잔류값으로는 이 둘을 동시에 못 맞춘다(격자탐색 log-err 5.3 vs 0.02).
    res_lo = float(pack.get_or("ph_window_residual_acid", 0.01))
    res_hi = float(pack.get_or("ph_window_residual_base", 0.18))
    k_lo = float(pack.get_or("ph_window_k_low", 5.0))
    k_hi = float(pack.get_or("ph_window_k_high", 10.0))
    mid_lo = float(pack.get_or("ph_window_mid_low", iep_wafer + 0.7))     # 3.2
    mid_hi = float(pack.get_or("ph_window_mid_high", iep_ceria - 1.0))    # 5.8

    def _win(x: float) -> float:
        lo = 1.0 / (1.0 + math.exp(-k_lo * (x - mid_lo)))
        hi = 1.0 / (1.0 + math.exp(k_hi * (x - mid_hi)))
        return res_lo * (1.0 - lo) + res_hi * (1.0 - hi) * lo + lo * hi

    cur, ref = _win(ph), _win(ph_ref)
    if ref <= 0:
        return None
    notes.append(
        f"세리아 정전 창: pH {ph:g} (창 {iep_wafer:g}~{iep_ceria:g}, 기준 {ph_ref:g}) "
        f"→ 상대 {cur/ref:.3f}. 창 안에서 세리아(+)·실리카(−) 인력, 밖에서 반발. "
        "⚠ 창 위치는 IEP 물리, 기울기·잔류율은 Dandu 2009 실측 역산 — 미검증.")
    if ph >= iep_ceria - 0.5:
        notes.append(f"⚠ pH {ph:g}는 세리아 IEP({iep_ceria:g}) 근접 — 제타≈0, "
                     "응집·스크래치 위험(Δ↑). 분산제 없이는 실무 부적합.")
    return cur / ref


def _f_chi(rr: "ResolvedRecipe") -> Factor:
    """χ 화학 반응성 — 표면 연화·산화가 만드는 MRR 배수.

    기존 sim/chemistry.py를 승계하되, pH는 **정점형 항으로 교체**한다
    (단조 연화항은 pH 11 위를 과대평가한다 — `_ph_peak_term` docstring 참조).
    억제 항은 여기가 아니라 ψ가 가져간다 — 방향이 반대이고, 사용자가
    "함량 변화에 따른 성능 변화"를 볼 때 촉진과 억제를 분리해 봐야 한다.
    """
    from sim.chemistry import (_oxidizer_term, _ceria_term, _ph_softening_term)
    f = _new("chi")
    pk = rr.pack
    notes: List[str] = []
    terms: Dict[str, float] = {}

    # pH 항 선택 — **재료계별로 다르다.** 메커니즘이 다른 재료에 같은 항을 쓰면
    # 부호까지 틀린다(실리카 IEP 2.5 vs 세리아 6.8 → 정전 상호작용이 반대 방향).
    #   세리아: IEP 창 모델 (Dandu 2009)
    #   실리카: 정점형 (Li 2021), 없으면 단조 연화 폴백
    # ⚠ sti_ceria 팩이 oxide_silica를 base로 상속하므로, 세리아를 먼저 확인하지
    #   않으면 실리카의 pH 11 정점 항이 세리아에 잘못 적용된다 — 2026-09-08
    #   dandu2009 백테스트에서 ρ=−0.525(음의 상관)로 드러난 결함이 바로 이것이다.
    if str(pk.get_or("abrasive", "")) == "ceria" and pk.has("abrasive_iep_ph"):
        ph_terms = [("ph_ceria_window", _ph_ceria_electrostatic_term)]
    elif pk.has("ph_peak") and pk.has("ph_ref"):
        ph_terms = [("ph_peak", _ph_peak_term)]
    else:
        ph_terms = [("ph_softening", _ph_softening_term)]

    for name, fn in ([("oxidizer", _oxidizer_term),
                      ("ceria_tooth", _ceria_term)] + ph_terms):
        v = fn(pk, notes)
        if v is not None:
            terms[name] = v
    for k in ("oxidizer_wt_pct", "slurry_ph", "ce3_fraction",
              "booster_mM", "chelator_mM"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass
    if not terms:
        f.notes.append("⚠ χ 미모델링: 산화제·pH·세리아 파라미터가 팩에 없다. "
                       "화학 효과는 Kp에 뭉뚱그려진 상태 — 조성을 바꿔도 안 변한다.")
        f.notes.extend(notes)
        return f
    val = 1.0
    for v in terms.values():
        val *= v
    f.value = val
    f.terms = terms
    f.status = "modeled" if len(terms) >= 2 else "partial"
    f.confidence = _worst_conf(
        _pack_conf(pk, "oxidizer_wt_pct", "slurry_ph", "ce3_fraction"), "estimated")
    f.sources = ["knowledge/cmp/ceria-slurry-ce-redox-selectivity.md",
                 "knowledge/cmp/particle-wafer-interaction-"
                 "mechanical-chemical-balance.md"]
    f.notes.extend(notes)
    if len(terms) > 1:
        f.notes.append("⚠ 화학 항들을 독립으로 보고 곱했다 — pH-흡착, 산화제-세리아 "
                       "산화환원 커플링은 미모델링.")
    if not pk.has("booster_mM"):
        f.notes.append("⚠ R/R booster(glycine 등)가 팩에 없다 — 막질별 선택비를 만드는 "
                       "주요 축인데 통로가 없다. 담당 R2-slurry.")
    return f


def _f_psi(rr: "ResolvedRecipe") -> Factor:
    """ψ 표면 보호도 — 억제제 피복이 만드는 제거 억제 배수 (≤1).

    χ와 분리한 이유: 사용자가 배합을 조정할 때 "촉진을 올릴까 억제를 낮출까"는
    서로 다른 결정이다. 하나의 화학 배수로 뭉치면 그 판단이 사라진다.
    디싱/에로전은 이 항이 지배한다.
    """
    from sim.chemistry import _inhibitor_term
    f = _new("psi")
    pk = rr.pack
    notes: List[str] = []
    v = _inhibitor_term(pk, notes)
    for k in ("inhibitor_mM", "surfactant_ppm"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass
    if v is None:
        f.notes.append("⚠ ψ 미모델링: 억제제 파라미터(inhibitor_mM + 흡착상수)가 "
                       "팩에 없다. Cu/W 디싱 제어를 시뮬레이션할 수 없다.")
        f.notes.extend(notes)
        return f
    f.value = v
    f.terms = {"inhibitor": v}
    f.status = "modeled"
    f.confidence = _worst_conf(_pack_conf(pk, "inhibitor_mM"), "unverified")
    f.sources = ["knowledge/cmp/cu-bta-inhibition.md"]
    f.notes.extend(notes)
    if not pk.has("surfactant_ppm"):
        f.notes.append("⚠ surfactant가 미연결 — 계면활성제도 피복을 통해 억제에 "
                       "기여하는데 통로가 없다.")
    return f


def _f_tau(rr: "ResolvedRecipe") -> Factor:
    """τ 슬러리 전달 — 접촉부에 도달하는 신선 슬러리 유효분율.

    ⚠⚠ 이 팩터의 가장 중요한 사실: **"슬러리를 더 많이 나르면 MRR이 비례해서
    오른다"는 직관은 실측으로 기각됐다.**

    근거 ①  Prasad 2013 (doi:10.1557/jmr.2013.173, III.D.3, Mirra 툴 TEOS):
      동일 수지경도·유사 기공크기에서 기공률 %P만 15%→45%로 30%p 올렸는데
      평균 RR 증가는 **단 8%**("nominal increase", 원문 표현). 저자 스스로
      "기공=슬러리 저장소이므로 비례 증가"를 기대했다가 빗나갔다고 적었다.

    근거 ②  Mu et al. 2016 (doi:10.1016/j.mee.2016.02.035, Table 3):
      그루브 폭 → 슬러리 이용효율 η (3 PSI 기준)
          300 µm → η 9.9%
          600 µm → η 13.4%   (+35% 상대)
          900 µm → η 12.8%   (정체·미세 감소)
      **단조가 아니다.** 600 µm 부근에서 꺾인다. 넓힐수록 좋다는 가정은
      틀렸다 — V_groove와 V_total이 함께 커져 q_actual 비율이 안 변하기 때문이다
      (저류 부피가 과하면 정체 슬러리가 늘어난다).

    그래서 이 구현은 두 가지를 지킨다:
      1. η는 **실측 3점 보간**으로 낸다(단조 멱함수 금지 — 정체 구간을 놓친다).
      2. η→MRR 결합은 **매우 약하게** 들어간다. 지수는 Prasad 데이터에서 역산:
         보유용량 3배(15→45%)에 RR 1.08배 ⟹ n = ln(1.08)/ln(3) ≈ 0.07.
         ⚠ 이건 기공률 실험에서 뽑아 그루브 축에 적용한 **교차 대입**이라
         미검증이다. 순위(전달이 나아지면 조금 낫다)만 신뢰하고 크기는
         캘리브레이션 대상이다.

    τ가 진짜로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다.
    Prasad III.D.2: 기공 2 µm 패드는 중심이 슬러리 기아로 처지고 엣지가 올라
    엣지-중심 RR 차이가 200 nm/min을 넘었다. 그 프로파일 결합은 아직 미구현이며
    이 사실을 notes에 싣는다.
    """
    f = _new("tau")
    pk = rr.pack
    for k in ("groove_depth_mm", "groove_pitch_mm", "groove_width_um",
              "pad_porosity_pct", "slurry_viscosity_pa_s"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass
    if not f.drivers:
        f.notes.append("⚠ τ 미모델링: 그루브 형상·기공률·점도가 팩에 없다.")
        return f

    # ── η(그루브 폭) — Mu 2016 Table 3 실측 3점 선형보간 ──────────
    ETA_W = [300.0, 600.0, 900.0]        # µm
    ETA_V = [0.099, 0.134, 0.128]        # 슬러리 이용효율 (3 PSI)
    terms: Dict[str, float] = {}
    srcs: List[str] = []

    w = pk.get_or("groove_width_um", None)
    w_ref = pk.get_or("groove_ref_width_um", None)
    if w is not None and w_ref is not None:
        def _eta(x: float) -> float:
            x = float(x)
            if x <= ETA_W[0]:
                # 300 µm 아래는 실측이 없다 — 외삽하지 않고 끝값으로 고정한다
                return ETA_V[0]
            if x >= ETA_W[-1]:
                return ETA_V[-1]
            for i in range(len(ETA_W) - 1):
                if ETA_W[i] <= x <= ETA_W[i + 1]:
                    t = (x - ETA_W[i]) / (ETA_W[i + 1] - ETA_W[i])
                    return ETA_V[i] + t * (ETA_V[i + 1] - ETA_V[i])
            return ETA_V[-1]

        e_cur, e_ref = _eta(w), _eta(float(w_ref))
        if e_ref > 0:
            n = float(pk.get_or("tau_mrr_exponent", 0.07))
            terms["groove_eta"] = (e_cur / e_ref) ** n
            srcs.append("knowledge/materials/pad-groove-geometry-"
                        "contact-area-flow-resistance.md §2")
            f.notes.append(
                f"그루브 폭 {float(w):g} µm → 슬러리 이용효율 η={e_cur*100:.1f}% "
                f"(기준 {float(w_ref):g} µm, η={e_ref*100:.1f}%). "
                "⚠ η는 600 µm 부근에서 정체·반전한다 — 넓힐수록 좋지 않다"
                "(Mu 2016 Table 3 실측).")
            if float(w) < ETA_W[0] or float(w) > ETA_W[-1]:
                f.notes.append(f"⚠ 그루브 폭 {float(w):g} µm는 실측 범위"
                               f"({ETA_W[0]:g}~{ETA_W[-1]:g} µm) 밖 — 끝값으로 고정했다"
                               "(외삽하지 않는다).")

    # ── 기공률 → 보유용량 (Prasad 2013: 매우 약한 효과) ────────────
    por = pk.get_or("pad_porosity_pct", None)
    por_ref = pk.get_or("pad_ref_porosity_pct", None)
    if por is not None and por_ref is not None and float(por_ref) > 0:
        n = float(pk.get_or("tau_mrr_exponent", 0.07))
        terms["porosity"] = (float(por) / float(por_ref)) ** n
        srcs.append("knowledge/materials/pad-porosity-slurry-transport-mrr.md §5")
        f.notes.append(
            f"기공률 {float(por):g}% (기준 {float(por_ref):g}%). "
            "⚠ 실측상 기공률 15→45%(3배)에도 RR은 8%만 올랐다 — 비례 가정은 "
            "기각됐다(Prasad 2013). 지수 0.07은 그 8%에서 역산한 값이다.")

    if not terms:
        f.notes.append(
            "⚠ τ 입력은 있으나 **엔진에 연결되지 않았다** — 기준값"
            "(groove_ref_width_um / pad_ref_porosity_pct)이 팩에 없어 배수를 낼 수 "
            "없다. 조용히 1.0을 쓰면 '그루브를 반영했다'는 거짓말이 된다.")
        f.notes.append(f"현재 입력값: {f.drivers}")
        return f

    val = 1.0
    for v in terms.values():
        val *= v
    f.value = val
    f.terms = terms
    f.status = "partial"
    f.confidence = "unverified"
    f.sources = sorted(set(srcs))
    f.notes.append(
        "⚠ τ의 MRR 결합 지수(tau_mrr_exponent=0.07)는 기공률 실험에서 역산해 "
        "그루브 축에 교차 대입한 값이다 — 미검증. 순위만 신뢰하라.")
    f.notes.append(
        "⚠ τ가 실제로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다. "
        "기공 2 µm 패드에서 중심이 슬러리 기아로 처지고 엣지-중심 RR 차이가 "
        "200 nm/min을 넘었다(Prasad 2013 III.D.2). 이 프로파일 결합은 미구현 — "
        "담당 R3-pad × R2-slurry.")
    return f


def _f_delta(rr: "ResolvedRecipe") -> Factor:
    """Δ 손상 유발도 — 스크래치·결함 발생 경향.

    대입자 tail(D99)이 지배한다. 평균 입경이 아니라 **꼬리**가 스크래치를 만든다.
    """
    f = _new("delta")
    pk = rr.pack
    for k in ("abrasive_d99_nm", "abrasive_size_nm", "aggregate_ratio"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass
    if not pk.has("abrasive_d99_nm"):
        f.notes.append(
            "⚠ Δ 미모델링: 대입자 tail(abrasive_d99_nm)이 팩에 없다. "
            "스크래치는 평균 입경이 아니라 꼬리가 만든다 — D50만으로는 예측 불가. "
            "담당 R2-slurry × defect. 실무에서 가장 자주 문제되는 축인데 통로가 없다.")
        return f
    d99 = float(pk.get("abrasive_d99_nm"))
    d99_ref = float(pk.get_or("abrasive_ref_d99_nm", d99))
    if d99_ref <= 0:
        return f
    # 스크래치 깊이 ∝ 입자 크기, 발생률은 그보다 가파르다고 알려져 있으나
    # 지수는 문헌 폐형식이 없다 — 팩에서 받는다.
    n = float(pk.get_or("damage_exponent", 3.0))
    val = (d99 / d99_ref) ** n
    f.value = val
    f.terms = {"d99": val}
    f.status = "partial"
    f.confidence = "unverified"
    f.notes.append(f"⚠ 손상 지수 n={n:g}는 문헌 폐형식이 없어 팩에서 받는 가정값이다. "
                   "순위(큰 입자가 더 긁는다)만 신뢰하고 절대값은 쓰지 마라.")
    return f


def _f_stab(rr: "ResolvedRecipe") -> Factor:
    """S 시간 안정성 — 연속 연마 중 MRR 드리프트.

    패드 마모·glazing, 디스크 그릿 탈락, 슬러리 응집이 함께 만든다.
    ⚠ 현재 엔진은 단발 런만 계산한다 — 시간축이 없다.
    """
    f = _new("stab")
    pk = rr.pack
    for k in ("pad_usage_hours", "pad_wafer_count", "disk_usage_hours"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass
    f.notes.append(
        "⚠ S 미모델링: 엔진에 시간축(연속 웨이퍼 진행)이 없다. 패드 수명 곡선·"
        "glazing·그릿 탈락은 노트로는 연구됐으나 sim/에 들어오지 않았다. "
        "담당 R3-pad × R4-disk 공동. 마모 모델은 GW와 ad-hoc이 정반대 결과를 내는 "
        "미해결 모순이 있어(corr≈-1) 임의로 한쪽을 고르지 않는다.")
    return f


# ═══════════════════════════════════════════════════ 집계

_BUILDERS = {
    "lambda": _f_lambda, "pi": _f_pi, "theta": _f_theta, "gamma": _f_gamma,
    "kappa": _f_kappa, "chi": _f_chi, "psi": _f_psi,
    "tau": _f_tau, "delta": _f_delta, "stab": _f_stab,
}


def compute_factors(rr: "ResolvedRecipe") -> Dict[str, Factor]:
    """레시피 하나에서 10개 병합 파라미터를 전부 계산한다.

    실패한 팩터는 예외를 던지지 않고 status='unmodeled'로 돌아온다 —
    미모델링을 숨기지 않는 것이 이 층의 핵심 계약이다.
    """
    out: Dict[str, Factor] = {}
    for key, fn in _BUILDERS.items():
        try:
            out[key] = fn(rr)
        except Exception as e:      # 팩터 하나가 죽어도 나머지는 봐야 한다
            f = _new(key)
            f.notes.append(f"⚠ 계산 중 예외: {type(e).__name__}: {e}")
            out[key] = f
    return out


def mrr_multiplier(factors: Dict[str, Factor]) -> tuple[float, List[str]]:
    """MRR에 곱해질 총 배수와 그 근거 문구.

    ⚠ MRR_COUPLED에 든 팩터만 곱한다. 기준 조건에서 각 팩터가 1.0이므로
    총 배수도 1.0이어야 한다 — 이 성질은 테스트로 고정돼 있다.
    """
    mult = 1.0
    notes: List[str] = []
    for key in sorted(MRR_COUPLED):
        f = factors.get(key)
        if f is None:
            continue
        if f.status == "unmodeled" or f.value is None:
            notes.append(f"[{f.symbol} {f.name}] 미모델링 — MRR에 반영 안 됨")
            continue
        mult *= f.value
        notes.append(f"[{f.symbol} {f.name}] ×{f.value:.4f} ({f.status}, {f.confidence})")
    return mult, notes


def coverage(factors: Dict[str, Factor]) -> Dict[str, object]:
    """팩터 커버리지 — 얼마나 많은 축이 실제로 살아 있는가.

    V2의 완주 판정(§3)이 읽는 값이다. '노트 몇 편'이 아니라 이 숫자가 진도다.
    """
    modeled = [k for k, f in factors.items() if f.status == "modeled"]
    partial = [k for k, f in factors.items() if f.status == "partial"]
    unmodeled = [k for k, f in factors.items() if f.status == "unmodeled"]
    return {
        "total": len(factors),
        "modeled": sorted(modeled),
        "partial": sorted(partial),
        "unmodeled": sorted(unmodeled),
        "score": round((len(modeled) + 0.5 * len(partial)) / max(len(factors), 1), 3),
    }
