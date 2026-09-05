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
  >>> res.metrics.ttv_nm, res.metrics.radial_ttv_nm, res.metrics.cv_pct
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

PSI_TO_PA = 6894.757


# ───────────────────────────────────────────────────────────── 입력 스키마
@dataclass
class Recipe:
    """한 번의 CMP 런을 정의하는 모든 입력. 각 필드의 소유 에이전트를 주석으로 남긴다."""
    # wafer-type / film-*
    wafer: Literal["NPW", "PTW"] = "NPW"
    film: Literal["oxide", "nitride", "poly", "cu", "w"] = "oxide"
    wafer_radius_m: float = 0.150
    # tool-platen-head
    pressure_psi: float = 3.0
    rpm_wafer: float = 60.0
    rpm_platen: float = 55.0
    center_offset_m: float = 0.180          # r_cc: 웨이퍼 중심–플래튼 중심 거리
    zone_pressures_psi: Optional[List[float]] = None   # 멀티존 헤드. None=균일
    zone_edges_norm: Optional[List[float]] = None      # 존 경계 (0~1, 정규화 반경)
    edge_pressure_amp: float = 0.0          # 엣지 압력 집중 진폭 (0=없음)
    time_s: float = 60.0
    # slurry-* / pad-* / disk-* — 지금은 유효 Preston 계수 하나로 뭉뚱그림. tier2 연결 시 분해된다.
    kp_m_per_pa: float = 1.6e-13
    # wafer-metrology — 측정 체계
    n_points: int = 81
    edge_exclusion_m: float = 0.003
    # 초기 두께 (잔막 계산용). None이면 제거량만 보고
    initial_thickness_nm: Optional[float] = None
    # 자유 확장 (캘리브레이션 태그, 로트 ID 등)
    meta: Dict[str, str] = field(default_factory=dict)


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
    model: str = ""
    notes: List[str] = field(default_factory=list)

    def summary(self) -> Dict:
        m = self.metrics
        return {
            "model": self.model, "wafer": self.recipe.wafer, "film": self.recipe.film,
            "mean_mrr_nm_min": float(np.mean(self.mrr_nm_per_min)),
            "ttv_nm": m.ttv_nm, "radial_ttv_nm": m.radial_ttv_nm, "cv_pct": m.cv_pct,
            "wiwnu_halfrange_pct": m.wiwnu_halfrange_pct, "wiwnu_3sigma_pct": m.wiwnu_3sigma_pct,
            "roughness_ra_nm": self.roughness_ra_nm, "dishing_nm": self.dishing_nm,
            "metal_contamination": self.metal_contamination,
            "notes": self.notes,
        }


# ───────────────────────────────────────────────────────────── 모델 등록
class Model(Protocol):
    name: str
    def mrr_radial(self, recipe: Recipe, radius_m: np.ndarray) -> np.ndarray: ...
    # 선택: 모델이 자기 한계를 스스로 보고한다(미해결 물리·미검증 가정).
    # 구현하지 않아도 되지만, 아는 한계를 숨기면 그게 할루시네이션이다.
    def notes(self, recipe: Recipe) -> List[str]: ...


class PrestonRadialModel:
    """Tier1: Preston MRR = Kp·P·V, V는 kinematics.py 상대속도장의 자전 평균. 압력은 wiwnu.py 프로파일."""
    name = "tier1.preston_radial"

    def mrr_radial(self, recipe: Recipe, radius_m: np.ndarray) -> np.ndarray:
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


# ───────────────────────────────────────────────────────────── 실행
def simulate(recipe: Recipe, model: str = "tier1.preston_radial") -> WaferResult:
    if model not in _MODELS:
        raise KeyError(f"등록되지 않은 모델: {model}. 사용 가능: {list(_MODELS)}")
    notes: List[str] = []
    r_max = recipe.wafer_radius_m - recipe.edge_exclusion_m
    radius = np.linspace(0.0, r_max, recipe.n_points)
    impl = _MODELS[model]
    mrr_m_s = impl.mrr_radial(recipe, radius)
    # 모델이 스스로 한계를 보고할 기회 — 지어내지 않고 모르는 것을 드러낸다
    if hasattr(impl, "notes"):
        notes.extend(impl.notes(recipe))  # type: ignore[attr-defined]
    mrr_nm_min = mrr_m_s * 1e9 * 60.0
    removed = mrr_nm_min * (recipe.time_s / 60.0)
    remaining = None
    if recipe.initial_thickness_nm is not None:
        remaining = recipe.initial_thickness_nm - removed
        if np.any(remaining < 0):
            notes.append("잔막 음수 — 오버폴리시. time_s 또는 initial_thickness 확인")
    if recipe.wafer == "PTW" and model != "tier1.pattern_density":
        notes.append("PTW인데 패턴 모델을 쓰지 않았다 — model='tier1.pattern_density'로 실행하라. "
                     "지금 값은 NPW 등가")
    if recipe.film != "oxide":
        notes.append(f"film={recipe.film}: 막질별 Kp 미분화 — film-{recipe.film} 에이전트 활성 후 반영. 지금은 kp_m_per_pa 그대로")
    metrics = compute_metrics(radius, removed if remaining is None else remaining,
                              n_points=recipe.n_points)
    return WaferResult(recipe=recipe, radius_m=radius, mrr_nm_per_min=mrr_nm_min,
                       removed_nm=removed, remaining_nm=remaining, metrics=metrics,
                       model=model, notes=notes)


def available_models() -> List[str]:
    return list(_MODELS)


if __name__ == "__main__":
    import json
    r = Recipe(pressure_psi=3.0, rpm_wafer=60, rpm_platen=55, time_s=60,
               initial_thickness_nm=800.0, edge_pressure_amp=0.15)
    res = simulate(r)
    print(json.dumps(res.summary(), ensure_ascii=False, indent=2))
