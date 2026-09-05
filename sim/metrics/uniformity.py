"""
균일도·두께 지표 라이브러리 — wafer-metrology 에이전트 소유 (엔진 출력 스키마).

⚠ 상태: **잠정(provisional)**. 지표 정의는 wafer-metrology 에이전트가 Lv1-2 단원에서
공개 문헌(SEMI 표준, Lee & Boning 1999, 장비사 계측 매뉴얼 등)을 학습해 확정한다.
아래 정의는 흔히 쓰이는 형태를 임시로 둔 것이며, 학습 결과와 다르면 **학습 결과가 이긴다**.
근거 노트가 생기면 이 docstring을 그 노트 링크로 교체할 것.

잠정 정의:
  TTV            = max − min                        [nm]  (SEMI MF1530 계열 정의 확인 필요)
  radial TTV     = 반경 링별 (max−min) 중 최대       [nm]  (링 분할 방식·링 수는 미확정)
  CV             = σ / μ × 100                        [%]
  WIWNU half-range = (max−min)/(2·mean) × 100         [%]   (Lee & Boning 1999에 등장하는 정의 중 하나)
  WIWNU 3σ       = 3σ / mean × 100                    [%]
  edge rebound   = 엣지 링 평균 − 인접 내측 링 평균     [nm]  (미검증 — 문헌 정의 확인 필요)

WIWNU는 산업 표준이 없다(process-integrator 판단, wiwnu-pressure-velocity 노트) → 병기 원칙.
값만 인용하지 말고 정의를 함께 보고할 것.

입력은 두 형태를 받는다:
  1) 반경 프로파일 (radius[], value[])            — 시뮬레이터 출력, 축대칭 가정
  2) 측정 포인트 (x[], y[], value[])               — 실측. 반경 링은 r을 n_rings로 등분(잠정)
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional
from numpy.typing import ArrayLike

import numpy as np


@dataclass
class UniformityMetrics:
    n_points: int
    mean_nm: float
    min_nm: float
    max_nm: float
    sigma_nm: float
    ttv_nm: float
    radial_ttv_nm: float
    radial_ttv_ring: int          # 어느 링에서 최대가 났나 (0=중심)
    ring_ttv_nm: list             # 링별 TTV 전부 (보고서 그래프용)
    cv_pct: float
    wiwnu_halfrange_pct: float
    wiwnu_3sigma_pct: float
    edge_rebound_nm: Optional[float]
    definition: str = ("PROVISIONAL — wafer-metrology Lv1-2 학습 후 확정 | TTV=max-min | radialTTV=max over rings of (ring max-min) | "
                       "CV=σ/μ·100 | WIWNU_hr=(max-min)/(2·mean)·100 | WIWNU_3σ=3σ/mean·100")

    def as_dict(self):
        return asdict(self)


def _ring_index(r: np.ndarray, r_max: float, n_rings: int) -> np.ndarray:
    idx = np.floor(r / r_max * n_rings).astype(int)
    return np.clip(idx, 0, n_rings - 1)


def compute_metrics(radius_m: ArrayLike, value_nm: ArrayLike,
                    n_points: int = 81, n_rings: int = 8) -> UniformityMetrics:
    """반경 프로파일 입력. 축대칭 가정 → 각 반경이 곧 하나의 링.
    n_rings로 프로파일을 링으로 묶어 radial TTV를 계산한다(실측 8링 관행과 맞춤)."""
    r = np.asarray(radius_m, float)
    v = np.asarray(value_nm, float)
    return _metrics_from_rings(r, v, n_points=n_points, n_rings=n_rings)


def compute_metrics_points(x_m: ArrayLike, y_m: ArrayLike, value_nm: ArrayLike,
                           n_rings: int = 8) -> UniformityMetrics:
    """실측 포인트 입력 (x,y). 반경으로 변환해 링을 나눈다."""
    x = np.asarray(x_m, float); y = np.asarray(y_m, float); v = np.asarray(value_nm, float)
    r = np.hypot(x, y)
    return _metrics_from_rings(r, v, n_points=len(v), n_rings=n_rings)


def _metrics_from_rings(r: np.ndarray, v: np.ndarray, n_points: int, n_rings: int) -> UniformityMetrics:
    if len(v) == 0:
        raise ValueError("빈 입력")
    mean = float(np.mean(v)); sig = float(np.std(v, ddof=0))
    vmin = float(np.min(v)); vmax = float(np.max(v))
    r_max = float(np.max(r)) if np.max(r) > 0 else 1.0
    ring = _ring_index(r, r_max, n_rings)
    ring_ttv = []
    for k in range(n_rings):
        vk = v[ring == k]
        ring_ttv.append(float(vk.max() - vk.min()) if len(vk) > 1 else 0.0)
    radial_ttv = max(ring_ttv)
    ring_argmax = int(np.argmax(ring_ttv))
    # 엣지 리바운드: 마지막 링 평균 − 그 안쪽 링 평균
    edge = None
    if n_rings >= 2:  # noqa
        last = v[ring == n_rings - 1]; prev = v[ring == n_rings - 2]
        if len(last) and len(prev):
            edge = float(last.mean() - prev.mean())
    return UniformityMetrics(
        n_points=int(n_points), mean_nm=mean, min_nm=vmin, max_nm=vmax, sigma_nm=sig,
        ttv_nm=vmax - vmin, radial_ttv_nm=radial_ttv, radial_ttv_ring=ring_argmax,
        ring_ttv_nm=ring_ttv,
        cv_pct=(sig / mean * 100.0) if mean else float("nan"),
        wiwnu_halfrange_pct=((vmax - vmin) / (2 * mean) * 100.0) if mean else float("nan"),
        wiwnu_3sigma_pct=(3 * sig / mean * 100.0) if mean else float("nan"),
        edge_rebound_nm=edge,
    )


def _selftest():
    # 1) 완전 균일 → 전 지표 0
    r = np.linspace(0, 0.147, 81); v = np.full(81, 500.0)
    m = compute_metrics(r, v)
    assert m.ttv_nm == 0 and m.radial_ttv_nm == 0 and m.cv_pct == 0, m
    # 2) 선형 기울기 500→520: TTV=20, 각 링 TTV ≈ 20/8 → radial ≈ 2.5, 엣지 리바운드 +
    v = np.linspace(500, 520, 81)
    m = compute_metrics(r, v)
    assert abs(m.ttv_nm - 20) < 1e-9, m.ttv_nm
    assert 2.0 < m.radial_ttv_nm < 3.0, m.radial_ttv_nm
    assert m.edge_rebound_nm is not None and m.edge_rebound_nm > 0
    # 3) 중심 링만 튀는 경우: radial TTV 최대가 링 0에서
    v = np.full(81, 500.0); v[:5] = [500, 510, 500, 490, 500]
    m = compute_metrics(r, v)
    assert m.radial_ttv_ring == 0 and abs(m.radial_ttv_nm - 20) < 1e-9, (m.radial_ttv_ring, m.radial_ttv_nm)
    # 4) 포인트 입력 = 프로파일 입력과 같은 정의
    th = np.linspace(0, 2 * np.pi, 81, endpoint=False)
    rr = np.linspace(0, 0.147, 81)
    mp = compute_metrics_points(rr * np.cos(th), rr * np.sin(th), np.linspace(500, 520, 81))
    assert abs(mp.ttv_nm - 20) < 1e-9
    # 5) CV 정의
    v = np.array([100.0, 110.0]); m = compute_metrics(np.array([0.0, 0.1]), v, n_rings=1)
    assert abs(m.cv_pct - (5 / 105 * 100)) < 1e-9
    print("metrics self-test 5/5 PASS")


if __name__ == "__main__":
    _selftest()
