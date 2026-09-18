#!/usr/bin/env python3
"""M5 데모용 합성 CSV 생성기 — data/demo/*.csv.

⛔ SYNTHETIC — 실측 아님. sim.engine.simulate()가 실제로 내는 반경 프로파일
(WaferResult.removed_nm)을 진실값으로 삼고, 거기에 **의도적으로 주입한** 결정론적
편차 + 가우시안 노이즈만 더한다. 실제 fab 데이터를 흉내 낸 것이 아니다.
생성 방식은 data/demo/README.md 에 재현 가능하게 적어둔다(이 파일이 그 정본).

    .venv/bin/python tools/make_demo_csv.py [--seed 20260919]

출력 3개 (data/demo/):
  npw_oxide_silica.csv          — NPW, 정상(GP가 잡을 수 있는 반경방향 편차)
  ptw_oxide_silica.csv          — 같은 팩 PTW
  npw_oxide_silica_drifted.csv  — NPW, 드리프트 탭 시연용(추가 상수 오프셋 주입)

각 CSV는 열 "data_source"에 "SYNTHETIC" 마커를 담는다(README와 함께 이중 표기) —
파일 첫 줄에 '#' 주석을 넣지 않는 이유: sim/demo_app.py 탭3의 업로더가
`pd.read_csv(csv_file)`을 comment 파라미터 없이 그대로 호출하므로, 주석 줄을
넣으면 그 줄이 헤더로 읽혀 데모가 깨진다.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np      # noqa: E402
import pandas as pd     # noqa: E402

from sim.engine import Recipe, simulate   # noqa: E402

OUT_DIR = ROOT / "data" / "demo"

PACK = "oxide_silica"
ANGLES_DEG = [0.0, 90.0, 180.0, 270.0]
N_RADII = 9

NOISE_SIGMA_NM = 0.5     # 측정 반복성 노이즈 표준편차 (nm) — 임의 선택, README에 명시
DEV_AMP_NM = 8.0         # 주입 편차 진폭 (nm)
DEV_L_MM = 40.0          # 주입 편차 파장 척도 (mm) — deviation(r) = DEV_AMP_NM*sin(r/DEV_L_MM)
DRIFT_OFFSET_NM = 30.0   # drifted 파일에만 추가하는 상수 오프셋 (nm)


def _baseline_removed_nm(wafer: str):
    """sim.engine.simulate()가 실제로 내는 반경 프로파일에서 9개 반경을 뽑는다
    (tools/make_synthetic_wafer.py와 동일한 서브샘플 방식)."""
    recipe = Recipe(pack=PACK, wafer=wafer, time_s=60.0)
    res = simulate(recipe)
    idx = np.linspace(0, len(res.radius_m) - 1, N_RADII).round().astype(int)
    r_mm = res.radius_m[idx] * 1000.0
    removed_nm = res.removed_nm[idx]
    return r_mm, removed_nm


def _deviation_nm(r_mm: np.ndarray, *, offset: float = 0.0) -> np.ndarray:
    """의도적으로 주입한 반경방향 편차 — 물리모델의 일부가 아니다."""
    return DEV_AMP_NM * np.sin(r_mm / DEV_L_MM) + offset


def _make_rows(r_mm: np.ndarray, removed_nm: np.ndarray, *, seed: int, offset: float = 0.0):
    rng = np.random.default_rng(seed)
    rows = []
    for theta_deg in ANGLES_DEG:
        for r, truth in zip(r_mm, removed_nm):
            dev = float(_deviation_nm(np.array([r]), offset=offset)[0])
            noise = float(rng.normal(0.0, NOISE_SIGMA_NM))
            measured = float(truth) + dev + noise
            rows.append({
                "r_mm": float(r),
                "theta_deg": float(theta_deg),
                "thickness_nm": measured,
                "data_source": "SYNTHETIC",
            })
    return rows


def make_npw_df(seed: int) -> pd.DataFrame:
    r_mm, removed_nm = _baseline_removed_nm("NPW")
    return pd.DataFrame(_make_rows(r_mm, removed_nm, seed=seed, offset=0.0))


def make_ptw_df(seed: int) -> pd.DataFrame:
    r_mm, removed_nm = _baseline_removed_nm("PTW")
    return pd.DataFrame(_make_rows(r_mm, removed_nm, seed=seed, offset=0.0))


def make_npw_drifted_df(seed: int) -> pd.DataFrame:
    r_mm, removed_nm = _baseline_removed_nm("NPW")
    return pd.DataFrame(_make_rows(r_mm, removed_nm, seed=seed, offset=DRIFT_OFFSET_NM))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260919,
                         help="기준 시드 — npw는 seed, ptw는 seed+1, drifted는 seed+2를 쓴다.")
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    jobs = [
        ("npw_oxide_silica.csv", make_npw_df, args.seed),
        ("ptw_oxide_silica.csv", make_ptw_df, args.seed + 1),
        ("npw_oxide_silica_drifted.csv", make_npw_drifted_df, args.seed + 2),
    ]
    for filename, fn, seed in jobs:
        df = fn(seed)
        out = OUT_DIR / filename
        df.to_csv(out, index=False)
        print(f"{out.relative_to(ROOT)}  ({out.stat().st_size} bytes, {len(df)} rows, seed={seed})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
