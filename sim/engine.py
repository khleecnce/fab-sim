"""
FabSim 통합 엔진 — 입력(Recipe) → 시뮬레이션 → 출력(WaferResult) 단일 API.

왜 이 파일이 있나 (2026-09-05 사용자 지시 "시뮬레이션 툴은 언제 착수?" → 지금):
  tier1/tier2 모듈은 각자 인자 시그니처가 달라 따로 논다. 새 물리가 어디에 붙는지 기준이 없다.
  이 파일이 그 기준이다. 물리 모듈은 1바이트도 고치지 않고 여기서 조립만 한다.

원칙
  1. Recipe(입력)와 WaferResult(출력)는 dataclass — 스키마가 코드다. 필드 추가 = 스키마 변경 = 커밋 로그에 남는다.
  2. 출력 지표는 sim/metrics/uniformity.py(wafer-metrology 소유)가 계산한다. 엔진은 두께 필드만 만든다.
  3. 물리 모듈은 `Model` 프로토콜로 등록한다. 지금은 Preston 반경 모델 하나. tier2/캘리브레이션은 같은 자리에 끼운다.
  4. 없는 것은 None. 지어내지 않는다 (roughness·contamination은 담당 에이전트 활성 전까지 None).

사용
  >>> from sim.engine import Recipe, simulate
  >>> r = Recipe(wafer="NPW", film="oxide", pressure_psi=3.0, rpm_wafer=60, rpm_platen=55, time_s=60)
  >>> res = simulate(r)
  >>> res.metrics.ttv_nm, res.metrics.radial_range_pct, res.metrics.cv_pct
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional, Protocol

import numpy as np

# 물리 모듈은 스크립트 직접 실행을 전제로 bare import를 쓴다 (tests/conftest.py와 동일 처리)
_ROOT = Path(__file__).resolve().parent
for _p in ("tier1_empirical", "tier2_physics", "integration"):
    _d = str(_ROOT / _p)
    if _d not in sys.path:
        sys.path.insert(0, _d)
if str(_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(_ROOT.parent))

from sim.metrics.uniformity import compute_metrics, UniformityMetrics  # noqa: E402
from sim.params import ParamPack, load_pack, available_packs  # noqa: E402
from sim.chemistry import chemistry_factor, ChemistryEffect  # noqa: E402,F401
from sim.factors import compute_factors, mrr_multiplier, coverage, Factor  # noqa: E402

PSI_TO_PA = 6894.757


# ───────────────────────────────────────────────────────────── 입력 스키마
@dataclass
class Recipe:
    """한 번의 CMP 런을 정의하는 모든 입력. 각 필드의 소유 에이전트를 주석으로 남긴다.

    ⚠ 물리 상수는 여기가 아니라 **파라미터 팩**(knowledge/params/*.yaml)이 소유한다.
      Recipe는 "이번 런에 사람이 정하는 것"(압력·rpm·시간)만 담는다.
      기본값 None인 필드는 팩에서 채워진다 — from_pack()이 그 일을 한다.
      이렇게 나눠야 "팩만 바꿔서 Cu를 돌린다"가 성립한다.
    """
    # 어떤 물성 묶음으로 돌릴 것인가 — 이 한 줄이 시뮬레이션의 정체성이다
    pack: str = "oxide_silica"
    # wafer-type / film-*
    wafer: Literal["NPW", "PTW"] = "NPW"
    film: Optional[str] = None              # None이면 팩의 film
    wafer_radius_m: Optional[float] = None
    # tool-platen-head
    pressure_psi: Optional[float] = None
    rpm_wafer: Optional[float] = None
    rpm_platen: Optional[float] = None
    center_offset_m: Optional[float] = None     # r_cc: 웨이퍼 중심–플래튼 중심 거리
    zone_pressures_psi: Optional[List[float]] = None   # 멀티존 헤드. None=균일
    zone_edges_norm: Optional[List[float]] = None      # 존 경계 (0~1, 정규화 반경)
    edge_pressure_amp: float = 0.0          # 엣지 압력 집중 진폭 (0=없음)
    time_s: float = 60.0
    # slurry-* / pad-* / disk-* — 팩이 소유. None이면 팩값
    kp_m_per_pa: Optional[float] = None
    # wafer-metrology — 측정 체계
    n_points: Optional[int] = None
    edge_exclusion_m: Optional[float] = None
    # 초기 두께 (잔막 계산용). None이면 제거량만 보고
    initial_thickness_nm: Optional[float] = None
    # 자유 확장 (캘리브레이션 태그, 로트 ID 등)
    meta: Dict[str, str] = field(default_factory=dict)
    # 팩 값을 이번 런에만 덮어쓴다 — 민감도 스캔·DOE의 통로.
    # 팩 파일을 고치지 않고 "이 값만 5% 올리면?"을 물을 수 있어야 한다.
    pack_overrides: Dict[str, float] = field(default_factory=dict)

    # 팩에서 채워야 하는 필드 → 팩의 키 이름
    _FROM_PACK = {
        "film": "film", "wafer_radius_m": "wafer_radius_m",
        "pressure_psi": "pressure_psi", "rpm_wafer": "rpm_wafer",
        "rpm_platen": "rpm_platen", "center_offset_m": "center_offset_m",
        "kp_m_per_pa": "kp_m_per_pa", "n_points": "n_points",
        "edge_exclusion_m": "edge_exclusion_m",
    }

    def resolve(self) -> "ResolvedRecipe":
        """팩을 읽어 빈 필드를 채운다. 없는 값은 KeyError로 즉시 실패한다.

        조용한 기본값을 쓰지 않는 게 핵심이다 — Cu 팩을 돌렸는데 산화막 Kp가
        말없이 쓰이면 결과 전체가 거짓말이 된다.
        """
        pk = load_pack(self.pack)
        if self.pack_overrides:
            # 이번 런에만 적용되는 덮어쓰기. 원본 팩은 건드리지 않는다(캐시 오염 방지).
            import copy as _copy
            from sim.params import Param
            pk = _copy.deepcopy(pk)
            for k, v in self.pack_overrides.items():
                if k in pk.params:
                    p = pk.params[k]
                    pk.params[k] = Param(key=k, value=v, unit=p.unit, source=p.source,
                                         confidence=p.confidence,
                                         note=(p.note + " [런 오버라이드]").strip())
                else:
                    pk.params[k] = Param(key=k, value=v, confidence="unverified",
                                         note="런 오버라이드 — 팩에 없던 값")
        vals = {}
        used: List[str] = []
        for attr, key in self._FROM_PACK.items():
            cur = getattr(self, attr)
            if cur is None:
                vals[attr] = pk.get(key)     # 없으면 ParamMissing
                used.append(key)
            else:
                vals[attr] = cur
        return ResolvedRecipe(base=self, pack=pk, used_keys=used, **vals)


@dataclass
class ResolvedRecipe:
    """팩으로 빈칸을 채운 뒤의 레시피 — 모델은 이것만 본다(전부 non-None)."""
    base: Recipe
    pack: ParamPack
    used_keys: List[str]
    film: str
    wafer_radius_m: float
    pressure_psi: float
    rpm_wafer: float
    rpm_platen: float
    center_offset_m: float
    kp_m_per_pa: float
    n_points: int
    edge_exclusion_m: float

    # 팩에 없는(사람이 정하는) 필드는 원본에서 그대로 위임
    @property
    def wafer(self) -> str: return self.base.wafer
    @property
    def time_s(self) -> float: return self.base.time_s
    @property
    def zone_pressures_psi(self): return self.base.zone_pressures_psi
    @property
    def zone_edges_norm(self): return self.base.zone_edges_norm
    @property
    def edge_pressure_amp(self) -> float: return self.base.edge_pressure_amp
    @property
    def initial_thickness_nm(self): return self.base.initial_thickness_nm
    @property
    def meta(self) -> Dict[str, str]: return self.base.meta

    def p(self, key: str):
        """팩 값 직접 조회 — 모델이 추가 물성을 필요로 할 때."""
        v = self.pack.get(key)
        if key not in self.used_keys:
            self.used_keys.append(key)
        return v


# ───────────────────────────────────────────────────────────── 출력 스키마
@dataclass
class WaferResult:
    recipe: Recipe
    radius_m: np.ndarray                 # 반경 격자
    mrr_nm_per_min: np.ndarray           # 반경별 제거율
    removed_nm: np.ndarray               # 반경별 제거량 (time_s 후)
    remaining_nm: Optional[np.ndarray]   # 잔막 (initial_thickness 있을 때)
    metrics: UniformityMetrics           # WIWNU·TTV·radial TTV·CV 등 — wafer-metrology 정의
    # 담당 에이전트 활성 전까지 None — 지어내지 않는다
    roughness_ra_nm: Optional[float] = None        # wafer-metrology Lv2-1
    dishing_nm: Optional[float] = None             # PTW만. pattern_density 연결 시
    erosion_nm: Optional[float] = None
    metal_contamination: Optional[Dict[str, float]] = None   # surface-contamination
    defect_density: Optional[float] = None         # defect-scientist
    # 윤활 레짐 진단 — MRR과 무관한 순수 진단. tribologist Lv2 (cmp-lubrication-regimes.md)
    lubrication_regime: Optional[str] = None       # "boundary"/"mixed"/"hydrodynamic"
    cmp_sommerfeld_number: Optional[float] = None
    cof_stribeck_estimate: Optional[float] = None
    # 슬러리 필름두께 스케일 진단 — MRR과 무관. Thakurta(2001) Eq.19 z0
    # (cmp-slurry-flow-lubrication-film-thickness.md). z0는 h_min의 스케일이지 정확한 값이 아니다.
    film_z0_scale_um: Optional[float] = None
    film_lubrication_note: Optional[str] = None
    model: str = ""
    notes: List[str] = field(default_factory=list)
    # 병합 파라미터 (ARCHITECTURE-V2 §2) — 이 런에서 각 축이 얼마였나.
    # UI가 "무엇을 만지면 무엇이 바뀌나"를 그리는 근거이자, 미모델링 축을 드러내는 통로.
    factors: Dict[str, "Factor"] = field(default_factory=dict)
    # 이 결과가 어떤 물성에서 나왔나 — 숫자의 출처 추적
    pack: str = ""
    film: str = ""
    provenance: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def summary(self) -> Dict:
        m = self.metrics
        return {
            "model": self.model, "pack": self.pack,
            "wafer": self.recipe.wafer, "film": self.film,
            "mean_mrr_nm_min": float(np.mean(self.mrr_nm_per_min)),
            "ttv_nm": m.ttv_nm, "radial_range_pct": m.radial_range_pct,
            "radial_maxring_range_nm": m.radial_maxring_range_nm, "cv_pct": m.cv_pct,
            "wiwnu_halfrange_pct": m.wiwnu_halfrange_pct, "wiwnu_3sigma_pct": m.wiwnu_3sigma_pct,
            "roughness_ra_nm": self.roughness_ra_nm, "dishing_nm": self.dishing_nm,
            "metal_contamination": self.metal_contamination,
            "lubrication_regime": self.lubrication_regime,
            "cmp_sommerfeld_number": self.cmp_sommerfeld_number,
            "cof_stribeck_estimate": self.cof_stribeck_estimate,
            "film_z0_scale_um": self.film_z0_scale_um,
            "film_lubrication_note": self.film_lubrication_note,
            "factors": {k: f.to_dict() for k, f in self.factors.items()},
            "factor_coverage": coverage(self.factors) if self.factors else None,
            "notes": self.notes,
        }


# ───────────────────────────────────────────────────────────── 모델 등록
class Model(Protocol):
    name: str
    def mrr_radial(self, recipe: "ResolvedRecipe", radius_m: np.ndarray) -> np.ndarray: ...
    # 선택: 모델이 자기 한계를 스스로 보고한다(미해결 물리·미검증 가정).
    # 구현하지 않아도 되지만, 아는 한계를 숨기면 그게 할루시네이션이다.
    def notes(self, recipe: "ResolvedRecipe") -> List[str]: ...


class PrestonRadialModel:
    """Tier1: Preston MRR = Kp·P·V, V는 kinematics.py 상대속도장의 자전 평균. 압력은 wiwnu.py 프로파일."""
    name = "tier1.preston_radial"

    def mrr_radial(self, recipe: "ResolvedRecipe", radius_m: np.ndarray) -> np.ndarray:
        import wiwnu as W            # sim/tier1_empirical/wiwnu.py (1바이트도 수정 안 함)
        p0 = recipe.pressure_psi * PSI_TO_PA
        if recipe.zone_pressures_psi:
            # wiwnu.p_zoned는 경계가 [0, ..., 1] (len=N+1)이어야 한다.
            # Recipe.zone_edges_norm은 끝점만 준다(len=N) → 0을 앞에 붙인다.
            # 이걸 안 하면 searchsorted가 전부 같은 존으로 보내 존압력이 무시된다
            # (2026-09-05 test_zone_pressure_applied가 잡은 실제 버그).
            edges = list(recipe.zone_edges_norm or
                         np.linspace(0, 1, len(recipe.zone_pressures_psi) + 1)[1:])
            if edges[0] != 0.0:
                edges = [0.0] + edges
            pfn = W.p_zoned(np.asarray(edges),
                            np.asarray(recipe.zone_pressures_psi) * PSI_TO_PA)
        elif recipe.edge_pressure_amp > 0:
            pfn = W.p_edge_concentration(p0, amp=recipe.edge_pressure_amp)
        else:
            pfn = W.p_uniform(p0)
        rs, mrr = W.mrr_radial(recipe.wafer_radius_m, recipe.center_offset_m,
                               recipe.rpm_wafer, recipe.rpm_platen, recipe.kp_m_per_pa,
                               pfn, n_r=len(radius_m))
        # wiwnu.mrr_radial은 자기 격자를 쓴다 → 요청 격자로 보간
        return np.interp(radius_m, rs, mrr)


_MODELS: Dict[str, Model] = {}


def register(model: Model) -> None:
    _MODELS[model.name] = model


register(PrestonRadialModel())


def _lubrication_diagnostics(rr: "ResolvedRecipe") -> Dict[str, object]:
    """윤활 레짐 진단(So·λ·COF) — MRR 경로와 완전히 독립적인 진단 계산.

    근거: knowledge/physics/cmp-lubrication-regimes.md §2,§5 (self-test 11/11 PASS).
    slurry_viscosity_pa_s·pad_ra_m이 팩에 없으면(tribologist 미적용 팩) roughness_ra_nm과
    같은 지위로 조용히 None — 지어내지 않는다.
    """
    out: Dict[str, object] = {"lubrication_regime": None, "cmp_sommerfeld_number": None,
                              "cof_stribeck_estimate": None}
    if not (rr.pack.has("slurry_viscosity_pa_s") and rr.pack.has("pad_ra_m")):
        return out
    try:
        import cmp_lubrication_regime as CLR   # sim/tier2_physics (1바이트도 수정 안 함)
        from sim.tier1_empirical import kinematics as kin
        mu = rr.p("slurry_viscosity_pa_s")
        Ra = rr.p("pad_ra_m")
        p_mean = rr.pressure_psi * PSI_TO_PA
        U_mean = kin.speed_stats(rr.wafer_radius_m, rr.center_offset_m,
                                 rr.rpm_wafer, rr.rpm_platen)["mean"]
        # groove 가중항은 미검증(노트 §2) → δeff≈Ra 근사만 쓴다
        d_eff = CLR.delta_eff(Ra, 0.0, 1.0)
        so = CLR.cmp_sommerfeld(mu, U_mean, p_mean, d_eff)
        lam = so   # λ≈So 근사(δeff≈σ 가정, 노트 §5) — 정량 항등식 아님
        out["lubrication_regime"] = CLR.regime_from_lambda(lam)
        out["cmp_sommerfeld_number"] = so
        out["cof_stribeck_estimate"] = CLR.cof_stribeck(so)
    except Exception as e:
        out["_note"] = f"윤활 레짐 진단 실패({e}) — lubrication_regime 등 None으로 둠"
    return out


def _film_thickness_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """슬러리 필름두께 길이 스케일 z0 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/slurry_film_lubrication.py (Thakurta et al. 2001 Eq.19,
    knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md §4).
    z0 = sqrt(2·μ·ω2·R1·R2 / P_app). 모듈 docstring이 명시하듯 z0는 무차원화 기준
    길이 스케일이며 정확한 최소필름두께 h_min이 아니다(전체 2-D Reynolds PDE 수치해 미이식).
    slurry_viscosity_pa_s가 팩에 없으면 roughness_ra_nm과 같은 지위로 조용히 None.
    """
    out: Dict[str, object] = {"film_z0_scale_um": None, "film_lubrication_note": None}
    if not rr.pack.has("slurry_viscosity_pa_s"):
        return out
    try:
        import slurry_film_lubrication as SFL   # sim/tier2_physics (1바이트도 수정 안 함)
        from sim.tier1_empirical import kinematics as kin
        mu = rr.p("slurry_viscosity_pa_s")
        omega2 = kin.rpm_to_rads(rr.rpm_platen)
        R1 = rr.wafer_radius_m
        R2 = rr.center_offset_m
        P_app = rr.pressure_psi * PSI_TO_PA
        z0_m = SFL.z0_length_scale(mu, omega2, R1, R2, P_app)
        out["film_z0_scale_um"] = float(z0_m) * 1e6
        out["film_lubrication_note"] = (
            "film_z0_scale_um은 Thakurta(2001) Eq.19의 길이 스케일 z0이며 정확한 최소필름두께 "
            "h_min이 아니다 — h_min/z0는 d0/z0 등 무차원군의 함수이고 전체 2-D Reynolds PDE "
            "수치해는 미이식 (knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md §4,§7)")
    except Exception as e:
        out["_note"] = f"필름두께 스케일 진단 실패({e}) — film_z0_scale_um None으로 둠"
    return out


# ───────────────────────────────────────────────────────────── 실행
def simulate(recipe: Recipe, model: str = "tier1.preston_radial") -> WaferResult:
    """레시피를 팩으로 해석한 뒤 실행한다.

    핵심 순서: resolve()가 먼저다. 팩에 없는 물성을 요구하면 여기서 KeyError로
    죽는다 — 조용히 기본값을 쓰고 그럴듯한 숫자를 뱉는 것보다 낫다.
    """
    if model not in _MODELS:
        raise KeyError(f"등록되지 않은 모델: {model}. 사용 가능: {list(_MODELS)}")
    rr = recipe.resolve()          # ← 팩 해석. 여기가 이 설계의 전부다.
    notes: List[str] = []
    r_max = rr.wafer_radius_m - rr.edge_exclusion_m
    radius = np.linspace(0.0, r_max, rr.n_points)
    impl = _MODELS[model]
    mrr_m_s = impl.mrr_radial(rr, radius)
    # ── 병합 파라미터 결합 (ARCHITECTURE-V2.md §2 · sim/factors.py) ────────
    # ⚠ 여기서 chemistry_factor()를 직접 곱하지 않는다. factors.χ가 그것을
    #   승계했으므로 둘 다 곱하면 **화학을 두 번 센다** — 2026-09-06 Cu MRR
    #   20배 붕괴가 정확히 그 사고였다. 결합 지점은 이 한 곳뿐이다.
    #   MRR에 곱해지는 것은 factors.MRR_COUPLED(κ·χ·ψ)만이고, 나머지 팩터
    #   (Λ Π Θ Γ τ Δ S)는 진단·설계 정보로만 실린다.
    factors = compute_factors(rr)
    fmult, fnotes = mrr_multiplier(factors)
    mrr_m_s = mrr_m_s * fmult
    notes.append(f"병합 파라미터 MRR 배수 ×{fmult:.4f}")
    notes.extend(fnotes)
    for _f in factors.values():
        notes.extend(_f.notes)
    # 모델이 스스로 한계를 보고할 기회 — 지어내지 않고 모르는 것을 드러낸다
    if hasattr(impl, "notes"):
        notes.extend(impl.notes(rr))  # type: ignore[attr-defined]
    mrr_nm_min = mrr_m_s * 1e9 * 60.0
    removed = mrr_nm_min * (rr.time_s / 60.0)
    remaining = None
    if rr.initial_thickness_nm is not None:
        remaining = rr.initial_thickness_nm - removed
        if np.any(remaining < 0):
            notes.append("잔막 음수 — 오버폴리시. time_s 또는 initial_thickness 확인")
    if rr.wafer == "PTW" and model != "tier1.pattern_density":
        notes.append("PTW인데 패턴 모델을 쓰지 않았다 — model='tier1.pattern_density'로 실행하라. "
                     "지금 값은 NPW 등가")
    # 윤활 레짐 진단 — MRR 경로와 완전히 독립. 팩에 슬러리 점도·패드 Ra가 없으면 조용히 None.
    lube = _lubrication_diagnostics(rr)
    if lube.get("_note"):
        notes.append(lube["_note"])
    elif lube["lubrication_regime"] is not None:
        notes.append("윤활 레짐 진단(So·λ·COF)은 λ≈So 근사(δeff≈σ 가정)이며 "
                     "COF 절대값은 정성적 오더 추정, 실측 캘리브레이션 필요 "
                     "(knowledge/physics/cmp-lubrication-regimes.md §5,§7)")
    # 슬러리 필름두께 스케일 z0 진단 — MRR 경로와 완전히 독립. 팩에 슬러리 점도가 없으면 조용히 None.
    film = _film_thickness_diagnostic(rr)
    if film.get("_note"):
        notes.append(film["_note"])
    elif film["film_lubrication_note"] is not None:
        notes.append(film["film_lubrication_note"])
    # 이 런에 실제로 쓰인 값 중 검증 안 된 것을 결과에 실어 보낸다.
    # 팩 전체가 아니라 '쓰인 것'만 — 안 쓴 값의 미검증은 이 결과와 무관하다.
    weak = [k for k in rr.used_keys
            if rr.pack.has(k) and rr.pack.param(k).confidence in
            ("estimated", "unverified", "unknown")]
    if weak:
        notes.append(
            f"⚠ 미검증 물성 사용: {', '.join(sorted(weak))} "
            f"(팩 '{rr.pack.name}'). 절대값을 신뢰하지 말고 경향만 보라. "
            f"해결: 실데이터 캘리브레이션.")
    metrics = compute_metrics(radius, removed if remaining is None else remaining,
                              n_points=rr.n_points)
    return WaferResult(recipe=recipe, radius_m=radius, mrr_nm_per_min=mrr_nm_min,
                       removed_nm=removed, remaining_nm=remaining, metrics=metrics,
                       lubrication_regime=lube["lubrication_regime"],
                       cmp_sommerfeld_number=lube["cmp_sommerfeld_number"],
                       cof_stribeck_estimate=lube["cof_stribeck_estimate"],
                       film_z0_scale_um=film["film_z0_scale_um"],
                       film_lubrication_note=film["film_lubrication_note"],
                       model=model, notes=notes, factors=factors,
                       pack=rr.pack.name, film=rr.film,
                       provenance=rr.pack.provenance(rr.used_keys))


def available_models() -> List[str]:
    return list(_MODELS)


if __name__ == "__main__":
    import json
    # 같은 엔진·같은 조건에 팩만 갈아끼운다 — 이게 이 설계의 목적이다
    for pack in ("oxide_silica", "sti_ceria", "cu_h2o2_bta"):
        r = Recipe(pack=pack, time_s=60, initial_thickness_nm=800.0, edge_pressure_amp=0.15)
        res = simulate(r)
        s = res.summary()
        print(f"[{pack:14s}] film={s['film']:6s} "
              f"MRR={s['mean_mrr_nm_min']:7.1f} nm/min  TTV={s['ttv_nm']:6.1f} nm")
