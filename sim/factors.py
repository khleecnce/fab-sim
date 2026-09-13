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
        f.sources = ["knowledge/equipment/cmp-multizone-carrier-radial-response.md"]
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

    발열은 두 독립 채널의 곱이다: Λ(웨이퍼-패드 마찰, 기존)과 리테이닝 링 압력(링-패드 마찰,
    Lee/Guo/Jeong 2012, doi:10.1007/s12541-012-0004-8, knowledge/physics/cmp-theta-retaining-
    ring-pressure-heat-channel.md — Table 1 총마찰력 선형회귀 R²>0.99). 냉각은 세 독립 채널로
    이루어진다: ①슬러리 유량(SFR, 대류 물질교환) ②플래튼 냉각수 온도(열전달 구동력 ΔT)
    ③플래튼 회전속도(회전 대류냉각, von Karman 회전원판 Nu∝Re^0.5 — Harmand et al. 2013,
    doi:10.1016/j.ijthermalsci.2012.11.009, knowledge/physics/cmp-theta-rotation-convective-
    cooling-driver.md). rpm_platen은 Λ의 발열(V=ω·r_cc, 선형)에도 쓰이지만 냉각 쪽에서는
    제곱근으로 스케일링돼 순net 효과는 완화될 뿐 상쇄되지 않는다(같은 노트 §2).
    Yuh 2015(doi:10.1007/s40684-015-0041-8)가 SFR·온도를 독립 실험축으로 스윕했다
    (knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md §1).
    온도는 Arrhenius로 화학속도를, 유량은 신선 슬러리 공급을 지배한다.

    ⚠ 회전 냉각 채널은 전체 냉각의 일부만 차지한다(2026-09-13 정정): White 2003 원문 열저항
    네트워크(정상상태 검증판은 sim/tier2_physics/cmp_theta_steady_state_heat_balance.py,
    frictional-heating-temperature-arrhenius-coupling.md §8.2/§8.4)에 따르면 냉각은
    G_slurry(엔탈피 수송, 회전무관)+G_pad(전도, 회전무관)+G_air(회전 대류, √Ω)의 병렬합이고
    Shin 2025 중앙 케이스 분해가 슬러리 74%/패드 19%/공기 7%임을 준다. 과거에는 cool_rotation
    전체를 √Ω로 스케일해 이 7% 채널의 효과를 냉각 전체(100%)에 적용했다 — 회전 냉각 효과를
    심하게 과대평가한 것이다(§8.4 "정정 후보"로 기록되어 있었음). 지금은 가중평균
    (1-W_AIR_FRACTION)·1.0 + W_AIR_FRACTION·√Ω로 그 7%만 반영한다. W_AIR_FRACTION=0.07은
    단일 케이스(Shin 2025 중앙값)에서 나온 근사치이고 범위는 6~8%다(§8.4 최소/최대 케이스) —
    구조적 결측(§8.5: 웨이퍼/헤드 경로 미모델링, L_pad 유효길이, h_air CMP 실측, 완전 열교환
    가정)이 전혀 닫히지 않았으므로 confidence는 여전히 estimated다.

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
    cool_sfr = sfr / sfr_ref
    cool_temp = 1.0   # 냉각수 온도 항 없으면 기준으로 폴백 (조용히 1.0 = 기존 partial 계약 유지)
    if pk.has("platen_coolant_temp_c") and pk.has("platen_hot_side_ref_c"):
        T_coolant = float(pk.get("platen_coolant_temp_c"))
        T_ref = float(pk.get_or("platen_coolant_ref_c", T_coolant))
        T_hot = float(pk.get("platen_hot_side_ref_c"))
        # 발산 가드: 냉각수온도가 열원온도에 근접하면 clip
        # (knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md §4)
        T_coolant_clip = min(T_coolant, T_hot - 0.5)
        driving_ref = T_hot - T_ref          # 기준 냉각 구동력(항상 >0, Recipe 검증 불필요)
        driving_now = T_hot - T_coolant_clip  # 이번 런 냉각 구동력 — 냉각수 찰수록 커짐(냉각효과↑)
        if driving_ref > 0:
            cool_temp = driving_now / driving_ref
        f.drivers["platen_coolant_temp_c"] = T_coolant
    # 회전 대류냉각 채널 — von Karman 회전원판 Nu∝Re_r^0.5 (층류, 지수 b=0.5 문헌 일치,
    # knowledge/physics/cmp-theta-rotation-convective-cooling-driver.md §1-2).
    # 새 파라미터 없이 Λ와 같은 lambda_ref_rpm_platen을 재사용(같은 회전축, 이중기준 방지).
    #
    # ⚠ 정정(2026-09-13): 이 회전 채널(G_air)은 전체 냉각 컨덕턴스(G_slurry+G_pad+G_air)의
    # 일부(W_AIR_FRACTION)만 차지한다 — frictional-heating-temperature-arrhenius-coupling.md
    # §8.4 Shin 2025 "중앙 케이스" 정상상태 열저항 네트워크 분해: 슬러리 74% / 패드 19% /
    # 공기 7%. 나머지 두 채널(G_slurry, G_pad)은 회전수와 무관(§8.2)한데도 과거 코드는
    # √Ω 스케일을 냉각 전체에 곱해 회전 냉각 효과를 심하게 과대평가했다(§8.4 "정정 후보").
    # 가중평균으로 고친다: 안 변하는 (1-W_AIR_FRACTION) 채널은 1.0, 공기 채널만 √Ω.
    # W_AIR_FRACTION은 단일 케이스(Shin 2025 중앙값)에서 나온 근사치이며 범위는 6~8%다
    # (§8.4 표의 최소/최대 케이스). 구조적 결측(§8.5)이 해소된 게 아니므로 confidence는
    # estimated로 유지한다.
    W_AIR_FRACTION = 0.07
    rpm_platen = float(rr.rpm_platen)
    rpm_ref = float(pk.get_or("lambda_ref_rpm_platen", rpm_platen or 1.0))
    rotation_ratio = math.sqrt(rpm_platen / rpm_ref) if rpm_ref > 0 else 1.0
    cool_rotation = (1.0 - W_AIR_FRACTION) * 1.0 + W_AIR_FRACTION * rotation_ratio
    # 리테이닝 링 압력 — 웨이퍼-패드 마찰(Λ)과 독립인 추가 발열원(Lee/Guo/Jeong 2012 Table 1,
    # knowledge/physics/cmp-theta-retaining-ring-pressure-heat-channel.md). 총 마찰력 F_wafer+F_ring이
    # RR압력에 선형(R²>0.99)이라는 실측을 기준 대비 배수로 압축한다. 없으면 1.0 폴백(기존 partial 계약 유지).
    heat_ring = 1.0
    if pk.has("retaining_ring_pressure_psi"):
        rr_psi = float(pk.get("retaining_ring_pressure_psi"))
        rr_ref = float(pk.get_or("retaining_ring_ref_psi", rr_psi))
        # Lee/Guo/Jeong 2012 Table 1 정규화 회귀계수 (기준 5psi=1.0):
        # a_norm=0.6145/(0.6145+0.07692*5)=0.6145/0.9991, b_norm=0.07692/0.9991
        A_COEF, B_COEF = 0.6145, 0.07692
        denom_ref = A_COEF + B_COEF * rr_ref
        if denom_ref > 0:
            heat_ring = (A_COEF + B_COEF * rr_psi) / denom_ref
        f.drivers["retaining_ring_pressure_psi"] = rr_psi
    # 부하비 = 발열(Λ×ring) / [냉각(SFR) × 냉각(온도) × 냉각(회전대류)]. 기준 조건에서 1.0.
    f.value = (lam.value * heat_ring) / (cool_sfr * cool_temp * cool_rotation)
    f.terms = {"heat(Λ)": lam.value, "heat(ring)": heat_ring, "cool(SFR)": cool_sfr,
               "cool(coolant_temp)": cool_temp, "cool(rotation)": cool_rotation}
    # 완전성 판정: SFR은 진입 가드에서 이미 필수(없으면 조기 return). 나머지 4채널
    # (heat(ring)/cool(coolant_temp)/cool(rotation)/heat(Λ))이 전부 실제 팩 파라미터로
    # 구동되면(문헌 4건: Lee/Guo/Jeong 2012, Yuh 2015, Harmand 2013, frictional-heating
    # coupling 노트) modeled — kappa/chi와 동일하게 "필요 항 전부 있으면 modeled" 규칙을
    # 적용한다. 이전 3회차(bcc2e5a/84c8e36/7382ab3)가 드라이버를 다 채웠는데도 이 줄이
    # 무조건 partial을 리턴해 accuracy_gaps가 영원히 PARTIAL을 반환하던 버그를 수정.
    have_all_channels = (
        pk.has("platen_coolant_temp_c") and pk.has("platen_hot_side_ref_c")
        and pk.has("retaining_ring_pressure_psi") and lam.value is not None
    )
    f.status = "modeled" if have_all_channels else "partial"
    f.confidence = _worst_conf(_pack_conf(pk, "sfr_ml_min"), "estimated")
    f.sources = ["knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md",
                 "knowledge/equipment/cmp-rpm-ratio-flowrate-temperature-mrr-stability.md",
                 "knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md",
                 "knowledge/physics/cmp-theta-rotation-convective-cooling-driver.md",
                 "knowledge/physics/cmp-theta-retaining-ring-pressure-heat-channel.md"]
    f.notes.append("⚠ 발열/냉각을 1차 비례로 압축했다 — 실제 열저항·체류시간은 "
                   "미반영. 절대 ΔT는 별도 열모델이 담당한다.")
    if not pk.has("sfr_ref_ml_min"):
        f.notes.append("⚠ sfr_ref_ml_min 없어 기준=현재값 폴백 — SFR 변화가 Θ에 안 잡힌다.")
    if "platen_coolant_temp_c" not in f.drivers:
        f.notes.append("⚠ platen_coolant_temp_c 없어 냉각수온도 항 1.0 폴백 — "
                       "cmp-theta-platen-coolant-temperature-driver.md §2 참조, 담당 tool-platen-head.")
    if "retaining_ring_pressure_psi" not in f.drivers:
        f.notes.append("⚠ retaining_ring_pressure_psi 없어 링 발열 항 1.0 폴백 — "
                       "cmp-theta-retaining-ring-pressure-heat-channel.md §3 참조, 담당 tool-platen-head.")
    return f


def _f_gamma(rr: "ResolvedRecipe") -> Factor:
    """Γ 컨디셔닝 부하 — 디스크가 패드에 가하는 단위시간 절삭일 (Preston형).

    Zheng et al.(2023) Eq.11: PCR = Kp·P·v_rel. v_rel(디스크-패드 상대속도)의
    지배항은 disk-rpm-load-radius-pcr.md §4가 유도·검증한 **디스크 중심 속도
    ω_p·r_cc**다 — 이 항은 디스크 자전비(Rs=ω_disk/ω_pad)와 무관하게 정확하고,
    같은 문헌조건(Rs=0.73)에서 디스크 전체 평균 v/(ω_p·r_cc)는 1.0004(0.04%
    편차)로 사실상 완전히 지배적이다(§7 verify). r_cc는 레시피가 아니라 스윕
    기구 형상(같은 장비)이므로 F·v 비율에서 상쇄돼, v 항을 rpm_platen(같은
    플래튼) 비율만으로 근사할 수 있다 — Λ이 이미 쓰는 것과 동일 근사(§7 참조).

    **cond_sweep_cpm(스윕 왕복수 n_a)은 v_rel 식에 나타나지 않는다** — 반경별
    궤적밀도·체류시간 분포(어디를 깎는가)를 결정하는 별개 축이다
    (conditioner-sweep-algorithm-trajectory-density.md,
    conditioner-sweep-kinematics-pcr-profile.md). Γ는 반경 무관 스칼라(총
    절삭 부하)이므로 sweep_cpm을 곱하지 않는다 — 곱하면 서로 다른 물리량
    (회전 상대속도 vs 왕복수)을 이중 계상하는 것이었다(2026-09-11 정정, 이전
    버전은 force×sweep×duty로 sweep을 속도 대리항처럼 썼다).

    confidence는 여전히 `estimated`로 하한한다 — 이유(문헌 근거 포함):
    (1) 디스크 내 상대속도의 Rs 보정항은 무시할 수 없다(에지 peak-to-peak
    14.4%, §7) — disk RPM 드라이버가 팩에 없어 정량 반영이 불가능하다.
    (2) 컨디셔너 자체의 PCR 시간적 소진(50h에 초기값의 16%로 감쇠,
    conditioner-disk-pad-cutting-model.md §3) — `cond_disk_usage_hours`가
    팩에 있으면 sim/tier2_physics/conditioner_pcr_decay.py의
    `pcr_decay()`(TAU_AGING_HOURS≈27.4h, Entegris 2차인용 앵커 50h→16% 역산)로
    반영된다. 없으면 여전히 디스크가 신품(aging 배수=1.0)이라고 암묵 가정한다.
    이 앵커 자체가 2차 인용(Palmgren 2004 원문 미확보)이므로 confidence 하한은
    유지한다. (3) 임계하중(critical downforce) 아래에서는 절삭이 안 일어난다는
    비선형이 F 선형항에 미반영이다. (1)과 (3)은 완화 가능한 근사가 아니라
    구조적 결측이므로, 개별 드라이버가 literature 등급이어도 모델 자체의
    신뢰도는 그보다 낮게 유지한다.

    ⚠ 여기는 **장비 설정**(하중·회전속도·duty)만 담는다. 디스크의 형상(그릿
    밀도·돌출)은 소모품이므로 κ/τ 쪽으로 간다. 이 분리를 지켜야 "디스크를
    바꿀까 컨디셔너 세팅을 바꿀까"에 답할 수 있다.
    """
    f = _new("gamma")
    pk = rr.pack
    needed = ["cond_downforce_lbf", "cond_duty_pct"]
    have = [k for k in needed if pk.has(k)]
    if not have:
        f.notes.append("⚠ Γ 미모델링: 컨디셔너 하중·duty 중 어느 것도 팩에 없다. "
                       "패드 절삭률(PCR)이 MRR 안정성을 지배하는데 통로가 없다. "
                       "담당 disk-conditioner.")
        return f
    F = float(pk.get_or("cond_downforce_lbf", 0.0))
    duty = float(pk.get_or("cond_duty_pct", 100.0))
    omega_p = float(rr.rpm_platen)
    f.drivers = {"cond_downforce_lbf": F, "rpm_platen": omega_p, "cond_duty_pct": duty}
    if pk.has("cond_sweep_cpm"):
        # 진단용 로깅만 — Γ 크기에는 곱하지 않는다(위 docstring 참조).
        f.drivers["cond_sweep_cpm(coverage_only,not_multiplied)"] = float(
            pk.get_or("cond_sweep_cpm", 0.0))
    F_ref = float(pk.get_or("cond_ref_downforce_lbf", F or 1.0))
    omega_ref = float(pk.get_or("lambda_ref_rpm_platen", omega_p or 1.0))
    duty_ref = float(pk.get_or("cond_ref_duty_pct", duty or 100.0))

    pcr_now = 1.0
    pcr_ref = 1.0
    if pk.has("cond_disk_usage_hours"):
        import conditioner_pcr_decay as CPD   # sim/tier2_physics (1바이트도 수정 안 함)
        t_hours = float(pk.get("cond_disk_usage_hours"))
        t_ref_hours = float(pk.get_or("cond_ref_disk_usage_hours", 0.0))
        pcr_now = CPD.pcr_decay(t_hours, 1.0, CPD.TAU_AGING_HOURS)
        pcr_ref = CPD.pcr_decay(t_ref_hours, 1.0, CPD.TAU_AGING_HOURS)
        f.drivers["cond_disk_usage_hours"] = t_hours

    denom = F_ref * omega_ref * duty_ref * pcr_ref
    if denom <= 0:
        f.notes.append("⚠ 기준 컨디셔닝 부하가 0 — Γ 계산 불가")
        return f
    f.value = (F * omega_p * duty * pcr_now) / denom
    f.terms = {"force": F / F_ref if F_ref else 1.0,
               "velocity(rpm_platen)": omega_p / omega_ref if omega_ref else 1.0,
               "duty": duty / duty_ref if duty_ref else 1.0,
               "aging(pcr_decay)": pcr_now / pcr_ref if pcr_ref else 1.0}
    f.status = "modeled" if len(have) == len(needed) else "partial"
    f.confidence = _worst_conf(_pack_conf(pk, *have, "rpm_platen"), "estimated")
    f.sources = ["knowledge/equipment/conditioner-disk-pad-cutting-model.md",
                 "knowledge/equipment/disk-rpm-load-radius-pcr.md"]
    if f.status == "partial":
        missing = [k for k in needed if k not in have]
        f.notes.append(f"⚠ 부분 모델링 — 결측: {', '.join(missing)}")
    f.notes.append("⚠ force×velocity(rpm_platen)×duty 곱 형태는 절삭일률의 1차 근사다 — "
                   "임계하중(critical downforce) 아래에서는 절삭이 안 일어난다는 "
                   "비선형이 미반영. disk-conditioner 노트 참조.")
    f.notes.append("⚠ velocity 항은 rpm_platen(패드 RPM)만 쓴다 — 디스크 자전비(Rs) 보정은 "
                   "disk-rpm-load-radius-pcr.md §7 기준 디스크 평균으로는 <0.1%지만 디스크 "
                   "에지에서는 peak-to-peak 14.4%까지 벌어진다(cond_disk_rpm 드라이버 부재로 "
                   "정량 반영 불가 — 반경별 분포는 별도 모듈의 몫).")
    f.notes.append("⚠ cond_sweep_cpm은 Γ 크기에 곱하지 않는다 — 문헌(disk-rpm-load-radius-pcr.md, "
                   "conditioner-sweep-algorithm-trajectory-density.md)에 따르면 스윕 왕복수는 "
                   "v_rel 식에 없고 반경별 궤적밀도(공간분포)만 결정한다. 총 절삭 부하가 아니다.")
    if not pk.has("cond_disk_usage_hours"):
        f.notes.append("⚠ cond_disk_usage_hours 없음 — 디스크 신품 가정(aging 배수=1.0), "
                       "PCR 시간적 소진(conditioner-disk-pad-cutting-model.md §3) 미반영.")
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
            # 이 두 값 자체는 2차 인용(E5)이라 어느 쪽인지 미확정이었으나, US9499721B2
            # (Cabot, 콜로이달 실리카 TEOS, E1 직접 실측 24점, TABLE 18)의 전역
            # 로그-로그 회귀가 n≈0.30을 줘 표면적 극한(1/3) 쪽으로 판정됐다
            # (EVIDENCE-RULES.md — E1이 E5를 이긴다;
            # knowledge/cmp/abrasive-concentration-mrr-saturation-contact-probability.md §5).
            # 기본값 1/3을 유지하고, 팩이 명시하면 그걸 따른다.
            # ⚠ 같은 데이터가 국소 지수 붕괴(0.5→1.0wt%에서 0.56, 2.5→3.0wt%에서 0.11)를
            # 보여 순수 거듭제곱 자체는 고농도 포화를 구조적으로 표현 못 한다 — 지수값
            # 판정과는 별개 문제이며 함수형 교체는 이 결함 해소 범위 밖(같은 노트 §8 참조).
            n = float(pk.get_or("abrasive_conc_exponent", 1.0 / 3.0))
            terms["conc"] = (c / c_ref) ** n
            srcs.append("knowledge/cmp/abrasive-size-concentration-"
                        "ph-K-additive-mrr-quantitative.md")
            srcs.append("knowledge/cmp/abrasive-concentration-mrr-saturation-"
                        "contact-probability.md")
            f.notes.append(f"⚠ 농도 지수 n={n:.3f} — 표면적 극한(1/3)은 US9499721B2 E1 실측 "
                           "전역회귀(n≈0.30)로 압입 극한(4/3)보다 우세하다고 판정됐다(같은 "
                           "데이터가 국소 지수는 0.56→0.11로 붕괴 — 순수 거듭제곱은 고농도 "
                           "포화를 못 담는다는 별개의 구조적 한계는 남아있음).")
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
            # 2026-09-13: Li et al. 2021 Eq.3-4를 pdfplumber 벡터좌표로 재추출해
            # 지수·부호가 확정됐다(knowledge/cmp/abrasive-size-concentration-ph-K-additive-
            # mrr-quantitative.md §4 2026-09-13 정정). 팩이 정점형 3파라미터
            # (abrasive_size_peak_nm·abrasive_size_exp_below_peak·abrasive_size_exp_above_peak)를
            # 명시하면 piecewise 곡선을 쓴다 — 단일 멱함수보다 우선한다(정점 거동을 담기
            # 때문). 없으면 기존 단일지수/null 경로로 폴백한다.
            peak_nm = pk.get_or("abrasive_size_peak_nm", None)
            exp_below = pk.get_or("abrasive_size_exp_below_peak", None)
            exp_above = pk.get_or("abrasive_size_exp_above_peak", None)
            if peak_nm is not None and exp_below is not None and exp_above is not None:
                peak_nm = float(peak_nm)
                exp_below = float(exp_below)
                exp_above = float(exp_above)

                def _piecewise_curve(x: float) -> float:
                    # 정점에서 두 식이 연속이 되도록 peak**exp_below를 앵커로 삼는다.
                    if x <= peak_nm:
                        return x ** exp_below
                    return (peak_nm ** exp_below) * (x / peak_nm) ** exp_above

                c_d, c_ref = _piecewise_curve(d), _piecewise_curve(d_ref)
                if c_ref > 0:
                    terms["size"] = c_d / c_ref
                    srcs.append("knowledge/cmp/abrasive-size-concentration-"
                                "ph-K-additive-mrr-quantitative.md §4")
                    f.notes.append(
                        f"입경 정점형 반영: peak={peak_nm:g}nm 기준 d={d:g}nm(지수 "
                        f"{'below' if d<=peak_nm else 'above'}={exp_below if d<=peak_nm else exp_above:g}), "
                        f"d_ref={d_ref:g}nm. Li et al. 2021 Eq.3-4(압입 지배 φ^{exp_below:.3g}, "
                        f"표면적 지배 φ^{exp_above:.3g})를 벡터좌표 재추출로 확정한 값 — "
                        "이 계(콜로이달 실리카/SiO2)에 한정, 정점 위치·지수의 타 화학종 "
                        "일반화는 미검증.")
                n_size = None  # 아래 단일지수 분기를 건너뛴다
            else:
                n_size = pk.get_or("abrasive_size_exponent", None)
            if peak_nm is not None and exp_below is not None and exp_above is not None:
                pass
            elif n_size is None:
                f.notes.append(
                    "⚠ 입경 항 미적용: 지수(abrasive_size_exponent)가 팩에 없다. "
                    "문헌은 정점형(~80nm 최대)이라고만 서술하고 지수를 확정하지 "
                    "못했으므로 임의값을 쓰지 않는다 — 입경을 바꿔도 κ가 변하지 "
                    "않는다는 뜻이다. 단조 지수를 넣으면 정점 거동을 놓친다.")
            elif float(n_size) == 0.0:
                # 지수 0은 "모른다"가 아니라 "효과가 없다"는 **검증된 결론**이다.
                # 값은 1.0이라 무반응이지만, 근거가 있으므로 항으로 계상한다
                # (미모델링과 구분되어야 한다 — EVIDENCE-RULES.md 판정 #1).
                terms["size"] = 1.0
                srcs.append("knowledge/cmp/abrasive-size-null-result-"
                            "force-partition-theory.md")
                f.notes.append(
                    "입경 지수 0 — **검증된 영(null) 결과**. 교란(입자 형상)을 제거한 "
                    "부분집합에서 입경-MRR 상관이 비유의(ρ≈0.03~0.15)하고, Chen "
                    "단층모델의 면밀도 d⁻²×압입 d⁺² 상쇄가 같은 결론을 준다. "
                    "'지수 미확정'이 아니라 '이 계에서 입경은 지배인자가 아님'이다. "
                    "적용 범위 밖(응집체 비율 높은 슬러리)에는 형상 팩터가 따로 필요하다.")
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
                           "절대값은 캘리브레이션이 필요하다. Qi/Joyce/Boyce 2003"
                           "(DOI:10.5254/1.3547752, 위 노트 §8)이 범용 탄성체용 "
                           "Shore D→탄성률 해석해(eq.11)를 주지만 confidence는 "
                           "못 올린다 — ①62D 앵커점에서 FEA 대비 49% 편향만 확인"
                           "됐고 60D에서의 편향 크기는 모름, ②범용 가황고무 대상"
                           "(폴리우레탄 미검증), ③애초에 그 논문의 E는 압입경도가 "
                           "아니라 단축인장 탄성률이라 물리량 자체가 다르다.")

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

    # ── 산성 영역(pH ≲ 6.0) 골(valley) 로그이차 가지 ─────────────────────
    # 2026-09-10 (오전) RESPONSE_DEAD 대응으로 멱함수(단조 감소, n=5, pH6.0 반등 제외)를
    # 넣었으나 tools/response_map.py 재판정 결과 RESPONSE_CONFLICT로 전환됐다 — 문헌
    # (cn109609035b n=7, pH2.0~6.0)은 **골**(pH~5 부근 최소 후 pH6.0 반등)인데 멱함수는
    # 단조 감소만 표현해 방향이 계속 달랐다. knowledge/cmp/silica-cmp-ph-acidic-repulsion-
    # choi-power-law.md §3(2026-09-10 저녁 갱신)에 따라 cn109609035b **7점 전체**(반등점
    # 포함)에 log(MRR) = a·pH² + b·pH + c 2차 회귀를 다시 적합했다 — 이 로그공간 2차식
    # 자체가 골(아래로 볼록) 형태를 갖는다. 피팅 구간(pH 2.0~6.0) **안에서만** 쓴다 —
    # 밖으로 나가면 급격히 발산해(pH 9 외삽 시 실측 대비 압도적 과대) 비물리적이므로,
    # 전환 경계 위(6.0~9.0, Choi 2004가 서술한 전환 pH)는 골 값(pH6.0)에서 염기 정점식
    # 값(pH9.0)까지 로그-선형 보간한다(데이터 없음 — 미검증 전이).
    ph_acid_max = float(pack.get_or("ph_acid_transition", 6.0))     # cn109609035b 데이터 상한
    ph_trans_hi = float(pack.get_or("ph_transition_upper", 9.0))    # Choi 2004 서술 전환점
    # cn109609035b 7점(pH2.0~6.0, 반등 포함) log(mrr)=a·pH²+b·pH+c 최소제곱 계수.
    # knowledge/cmp/silica-cmp-ph-acidic-repulsion-choi-power-law.md §3 verify 블록에서
    # 동일 계수를 재현·assert한다 — 여기 상수를 바꾸면 그 노트도 갱신해야 한다.
    ph_acid_a2 = float(pack.get_or("ph_acid_quad_a", 0.336472))
    ph_acid_b2 = float(pack.get_or("ph_acid_quad_b", -3.228411))
    ph_acid_c2 = float(pack.get_or("ph_acid_quad_c", 7.349046))

    def _quad(x: float) -> float:
        d = x - ph_pk
        a = a_lo if d < 0 else a_hi
        return max(1.0 - a * d * d, 0.05)   # 물리적으로 0 이하가 될 수 없다

    def _acid_raw(x: float) -> float:
        """cn109609035b 로그이차 골 피팅 — pH 2.0~6.0 보간 전용(외삽 금지, 호출측이 클램프)."""
        return math.exp(ph_acid_a2 * x * x + ph_acid_b2 * x + ph_acid_c2)

    def _rel(x: float) -> float:
        if x <= ph_acid_max:
            x_eff = max(x, 1.5)                         # 조사범위(pH≥2) 밖 발산 방지
            anchor = _quad(ph_acid_max)                  # 염기 정점식 경계값(6.0)
            ratio = _acid_raw(x_eff) / _acid_raw(ph_acid_max)   # 경계에서 1 → 연속
            return anchor * ratio
        if x <= ph_trans_hi:
            # 전이구간(6.0~9.0): 데이터 없음 — 로그-선형 보간(외삽 아님, 양끝 고정 보간)
            lo_v = max(_quad(ph_acid_max), 1e-6)
            hi_v = max(_quad(ph_trans_hi), 1e-6)
            t = (x - ph_acid_max) / (ph_trans_hi - ph_acid_max)
            return math.exp(math.log(lo_v) + t * (math.log(hi_v) - math.log(lo_v)))
        return _quad(x)

    cur, ref = _rel(ph), _rel(ph_ref)
    if ref <= 0:
        return None
    notes.append(
        f"pH {ph:g} (정점 {ph_pk:g}, 기준 {ph_ref:g}) → 상대 {cur/ref:.3f}. "
        "실측 3점(Li 2021 Fig.1) 기반 정점형(pH≳9.0), "
        f"산성(pH≤{ph_acid_max:g})은 골 형태 로그이차(cn109609035b n=7, 반등 포함 피팅). "
        "⚠ 염기 정점식은 3점을 지나는 최소 가정, 산성 골 로그이차는 n=7 피팅 — 둘 다 문헌 폐형식은 아니다. "
        f"⚠ {ph_acid_max:g}~{ph_trans_hi:g} 전환구간은 데이터 없어 로그-선형 보간(미검증 외삽).")
    if ph < ph_acid_max:
        notes.append(f"⚠ pH {ph:g}는 골 로그이차 보간 구간 — n=7(pH 2.0~6.0, 반등 포함) 피팅, "
                     "log-MSE 0.356, 개별점 최대 ±37%(pH5.0) 편차(원인 미상).")
    if ph_acid_max < ph < ph_trans_hi:
        notes.append(f"⚠ pH {ph:g}는 전환구간(데이터 없음) — 로그-선형 보간값이다.")
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
    """ψ 표면 보호도 — 표면 흡착 보호(억제제 피복 또는 분산제 흡착)가 만드는
    제거 억제 배수 (≤1).

    χ와 분리한 이유: 사용자가 배합을 조정할 때 "촉진을 올릴까 억제를 낮출까"는
    서로 다른 결정이다. 하나의 화학 배수로 뭉치면 그 판단이 사라진다.
    디싱/에로전은 이 항이 지배한다.

    ψ 정의 확장(COMPLETION.md): 원래는 Cu/W용 금속 부동태 억제제(BTA 등)만
    모델링했다. 하지만 oxide_silica/sic_ceria_h2o2/sti_ceria 세 팩은 금속이
    아니라 실리카/세리아 슬러리라 inhibitor_mM이 없다 — 그렇다고 표면 흡착
    보호가 없는 게 아니라, 통로가 폴리머 분산제 흡착(PVA/PVP)으로 바뀐 것뿐이다.
    그래서 억제제 항이 없을 때 분산제 흡착 항으로 폴백한다.
    """
    from sim.chemistry import _inhibitor_term, _dispersant_protection_term
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
    if v is not None:
        f.value = v
        f.terms = {"inhibitor": v}
        f.status = "modeled"
        f.confidence = _worst_conf(_pack_conf(pk, "inhibitor_mM"), "unverified")
        f.sources = ["knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md",
                     "knowledge/cmp/inhibitor-chelator-adsorption-isotherm-passivation.md"]
        f.notes.extend(notes)
        if not pk.has("surfactant_ppm"):
            f.notes.append("⚠ surfactant가 미연결 — 계면활성제도 피복을 통해 억제에 "
                           "기여하는데 통로가 없다.")
        return f

    dnotes: List[str] = []
    dv = _dispersant_protection_term(pk, dnotes)
    if pk.has("dispersant_type"):
        try:
            f.drivers["dispersant_type"] = pk.get("dispersant_type")
        except (TypeError, ValueError):
            pass
    if dv is None:
        f.notes.append("⚠ ψ 미모델링: 억제제 파라미터(inhibitor_mM + 흡착상수)도, "
                       "분산제 파라미터(dispersant_type)도 팩에 없다. 표면 흡착 보호를 "
                       "시뮬레이션할 수 없다.")
        f.notes.extend(notes)
        f.notes.extend(dnotes)
        return f
    f.value = dv
    f.terms = {"dispersant": dv}
    f.status = "modeled"
    f.confidence = _pack_conf(pk, "dispersant_type")
    f.sources = ["knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md §6"]
    f.notes.append("ψ 정의 확장: 표면 흡착 보호(passivation/adsorption shield) — "
                   "이 팩은 금속 부동태가 아니라 폴리머 분산제 흡착 경로")
    f.notes.extend(dnotes)
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
    # ⚠ τ의 confidence는 드라이버(기공률·그루브폭·점도)가 아니라 **결합 지수**가 결정한다.
    # 드라이버는 전부 literature여도 tau_mrr_exponent=0.07이 기공률 실험에서 역산해
    # 그루브 축에 교차 대입한 값이라, τ의 크기 자체는 문헌이 보증하지 않는다.
    # 팩이 지수의 근거를 명시(tau_exponent_confidence)하면 그것을 쓰고,
    # 없으면 드라이버 최악등급보다 한 단 낮춘다 — 지수가 가장 약한 고리이기 때문이다.
    _driver_conf = _pack_conf(pk, "groove_width_um", "pad_porosity_pct",
                              "slurry_viscosity_pa_s")
    f.confidence = str(pk.get_or("tau_exponent_confidence", "unverified"))
    f.sources = sorted(set(srcs))
    f.notes.append(
        f"⚠ τ 등급={f.confidence}: 드라이버(기공률·그루브폭·점도)는 {_driver_conf} 등급이지만 "
        "τ의 **결합 지수**(tau_mrr_exponent=0.07)가 기공률 실험에서 역산해 그루브 축에 "
        "교차 대입한 값이라 크기를 문헌이 보증하지 않는다 — 가장 약한 고리가 등급을 정한다. "
        "순위만 신뢰하라.")
    f.notes.append(
        "⚠ τ가 실제로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다. "
        "기공 2 µm 패드에서 중심이 슬러리 기아로 처지고 엣지-중심 RR 차이가 "
        "200 nm/min을 넘었다(Prasad 2013 III.D.2). 이 프로파일 결합은 미구현 — "
        "담당 R3-pad × R2-slurry.")
    return f


def _f_delta(rr: "ResolvedRecipe") -> Factor:
    """Δ 손상 유발도 — 스크래치·결함 발생 경향.

    대입자 tail(D99)이 지배한다. 평균 입경이 아니라 **꼬리**가 스크래치를 만든다.

    ⚠ 2026-09-13 추가: `aggregate_ratio`(콜로이드 불안정화 정도, 0~1) 항을 곱셈으로
    추가했다. 근거: Basim & Moudgil 2002 (J. Colloid Interface Sci. 256(1) 137-142,
    doi:10.1006/jcis.2002.8352) — NaCl 0.2M(이 계의 CCC=0.25M 미달, 벌크 광산란
    입도계로는 **평균 입경이 전혀 안 바뀜**)인데도 AFM 최대표면변형(Rmax)이
    25nm→50nm로 **2배** 증가했다(원문 Table 1). 즉 d99가 포착 못 하는 "일시적
    (transient) 응집체"에 의한 손상 경로가 d99 경로와 독립적으로 존재한다는 것이
    실측으로 확인됐다(knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism.md
    §3, §6). `aggregate_ratio=1.0`을 "이 논문의 NaCl 0.2M 불안정화 정도"로 정의하고
    그 조건에서 관측된 배수(2.0)로 계수를 고정했다: `1 + aggregate_ratio`.
    ⚠⚠ 이 계수는 **n=1(단일 데이터점)**에서 나온 값이다 — 화학종(실리카 학술
    모델계)·조건(7.0 psi, IC1000/Suba IV) 특유의 값이며 다른 화학종·조건으로의
    일반화는 미검증이다. 순위(불안정화가 클수록 손상↑)만 신뢰하라. 팩 기본값은
    `aggregate_ratio=0.0`(무영향, 항×1.0)이라 기존 팩·기준 조건의 Δ 계약은 안 깨진다.
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
    d99_term = (d99 / d99_ref) ** n
    # aggregate_ratio 항 — 기본 0.0이면 (1+0)=1.0으로 no-op, 기준 조건 Δ=1.0 계약 보존.
    agg_ratio = float(pk.get_or("aggregate_ratio", 0.0))
    agg_term = 1.0 + agg_ratio
    val = d99_term * agg_term
    f.value = val
    f.terms = {"d99": d99_term, "aggregate": agg_term}
    f.status = "partial"
    f.confidence = "unverified"
    f.sources = ["knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md",
                 "knowledge/cmp/lpc-scratch-density-tail-correlation.md",
                 "knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism.md"]
    f.notes.append(f"⚠ 손상 지수 n={n:g}는 문헌 폐형식이 없어 팩에서 받는 가정값이다. "
                   "순위(큰 입자가 더 긁는다)만 신뢰하고 절대값은 쓰지 마라. "
                   "⚠ n=3.0 기본값은 US8439995B2(Hitachi, 세리아 D99-스크래치 4점 실측) "
                   "회귀값 n≈1.44(R²=0.997)보다 약 2배 가파르다 — knowledge/cmp/"
                   "abrasive-d99-scratch-hitachi-us8439995.md §3. 교차확증: "
                   "lpc-scratch-density-tail-correlation.md(Remsen 2006, fumed silica)도 "
                   "선형(n≈1 근방)을 지지 — n=3.0이 과대추정일 가능성. 표본이 작아(세리아 "
                   "1개 화학종, 실질 독립 3점) 기본값을 즉시 교체하지 않았다(구현 요청으로 "
                   "PROFILE.md에 기록).")
    if agg_ratio != 0.0:
        f.notes.append(f"⚠ aggregate_ratio={agg_ratio:g} 항 발동(×{agg_term:.3f}) — "
                       "Basim&Moudgil 2002 NaCl 0.2M 단일 데이터점(n=1) 기반, 화학종/조건 "
                       "외삽 미검증. knowledge/slurry/colloidal-destabilization-lpc-"
                       "defect-mechanism.md §3.")
    return f


def _f_stab(rr: "ResolvedRecipe") -> Factor:
    """S 시간 안정성 — 컨디셔닝 없는 연속 연마 중 MRR 드리프트(로그감쇠).

    출처: Jeong, Shin, Jeong, Jeong, Jeong (2024), "Novel Probability Density
    Function of Pad Asperity by Wear Effect over Time in CMP", Materials 17(8),
    1817, doi:10.3390/ma17081817 (PMC11051262, 전문 확보). Fig.9 정규화 MRR
    (IC1000 패드·콜로이달 실리카·SiO2 블랭킷·컨디셔닝 없이 1~10분 연속연마,
    2/5 psi 두 조건 pooled)를 rate=a+b·ln(t[min]) 로그감쇠 회귀(R²=0.74,
    지식노트 knowledge/materials/pad-glazing-mechanism-mrr-decay.md §4(D)가
    로그형이 선형보다 우수함을 별도로 확인)로 피팅해 시간축 인자로 편입.
    기준 조건(Recipe 기본 time_s=60s=1 min)에서 정확히 1.0 — ln(1)=0.

    ⚠ 도메인 한계: (1) 원 데이터는 실리카/IC1000 단일계이며 세리아·알루미나
    슬러리·다른 패드로의 외삽은 미검증(confidence=estimated로 강등).
    (2) 1~10분 범위 밖은 clamp(외삽 금지, 값 고정). (3) 이 회귀는 무-컨디셔닝
    단발 연마의 초기 드리프트만 담는다 — 컨디셔닝 사이클·패드 수명(수십 시간)
    누적 마모는 여전히 미모델링(담당 R3-pad×R4-disk, 실데이터 없음).
    """
    f = _new("stab")
    pk = rr.pack
    for k in ("pad_usage_hours", "pad_wafer_count", "disk_usage_hours"):
        if pk.has(k):
            try:
                f.drivers[k] = float(pk.get(k))
            except (TypeError, ValueError):
                pass

    t_min = rr.time_s / 60.0
    f.drivers["time_s"] = rr.time_s

    # Jeong et al. 2024 Fig.9, pooled(2psi+5psi) 로그감쇠 회귀 계수
    # (knowledge/materials/pad-glazing-mechanism-mrr-decay.md §4(D) verify 블록에서
    #  개별 압력별 R²>0.65 확인, pooled 계수는 이 파일 docstring 재현으로 별도 산출)
    a_fit, b_fit = 1.1478, -0.1109
    t_clamped = min(max(t_min, 1.0), 10.0)
    val = (a_fit + b_fit * math.log(t_clamped)) / a_fit

    f.value = val
    f.terms = {"time_min_log_decay": val}
    f.status = "partial"
    abrasive = str(pk.get_or("abrasive", "")).lower()
    f.confidence = "literature" if abrasive == "silica" else "estimated"
    f.sources.append(
        "Jeong et al. 2024, Materials 17(8) 1817, doi:10.3390/ma17081817 (PMC11051262) Fig.9")
    f.sources.append("knowledge/materials/pad-glazing-mechanism-mrr-decay.md")
    if t_min > 10.0:
        f.notes.append(
            f"⚠ time_s={rr.time_s:.0f}s({t_min:.1f} min)가 문헌 관측범위(1~10 min)를 "
            "초과해 t=10 min 값으로 clamp했다 — 장시간 외삽 아님, 과소추정 가능.")
    if t_min < 1.0:
        f.notes.append(
            f"⚠ time_s={rr.time_s:.0f}s({t_min:.2f} min)가 관측 최솟값(1 min) 미만이라 "
            "t=1 min(=1.0) 값으로 clamp했다.")
    if abrasive != "silica":
        f.notes.append(
            f"⚠ 원 데이터는 콜로이달 실리카/IC1000 단일계다 — 이 팩의 연마입자"
            f"({abrasive or '미상'})로의 외삽은 미검증(confidence=estimated). "
            "fumed vs colloidal 실리카만도 감쇠율이 5배 차이 난다"
            "(knowledge/materials/pad-glazing-mechanism-mrr-decay.md §3, Lawing 2004) — "
            "다른 화학종은 그 이상 벗어날 수 있다.")
    f.notes.append(
        "⚠ 컨디셔닝 사이클·수십 시간 규모 패드 수명 누적 마모는 여전히 미모델링 "
        "(무-컨디셔닝 단발 1~10분 데이터만 반영). 담당 R3-pad × R4-disk.")
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
