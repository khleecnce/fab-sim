#!/usr/bin/env python3
"""합성 웨이퍼 측정 데이터 생성기 — data/synthetic/*.json (ORG.md §7.4/§7.5).

우리 자신의 엔진(sim.engine.simulate)이 낸 반경 프로파일을 진실값으로 삼고,
측정 반복성을 모사하는 가우시안 노이즈 하나만 얹는다. 회사 데이터·실측 데이터는
쓰지 않는다 — data/customer/ 는 이 스크립트가 건드리지 않는 별도 경로다.

    .venv/bin/python tools/make_synthetic_wafer.py
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from sim.engine import Recipe, simulate  # noqa: E402

OUT_DIR = ROOT / "data" / "synthetic"

# (pack, series_id, seed) — 각 1장씩. 측정 반복성 노이즈 표준편차는 값의 1%(상대) +
# 0.2nm(절대 바닥) — 두께 측정기 재현성 오더(수 옹스트롬~수 nm)를 모사한 것일 뿐
# 특정 장비 스펙 인용은 아니다. # 미검증
_NOISE_REL = 0.01
_NOISE_ABS_NM = 0.2

_ANGLES_DEG = [0.0, 90.0, 180.0, 270.0]
_N_RADII = 9  # 81점 반경 격자를 9점으로 서브샘플 — 실측 웨이퍼맵 밀도에 더 가깝고 파일도 작다


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def make_one(pack: str, wafer_id: str, seed: int) -> dict:
    recipe = Recipe(pack=pack, wafer="NPW", time_s=60.0)
    rr = recipe.resolve()
    res = simulate(recipe)

    idx = np.linspace(0, len(res.radius_m) - 1, _N_RADII).round().astype(int)
    radii_m = res.radius_m[idx]
    removed_nm = res.removed_nm[idx]

    rng = np.random.default_rng(seed)
    points = []
    for theta_deg in _ANGLES_DEG:
        theta_rad = float(np.deg2rad(theta_deg))
        for r_m, truth_nm in zip(radii_m, removed_nm):
            noise_sigma = abs(float(truth_nm)) * _NOISE_REL + _NOISE_ABS_NM
            measured_nm = float(truth_nm) + float(rng.normal(0.0, noise_sigma))
            points.append({
                "r_m": float(r_m),
                "theta_rad": theta_rad,
                "value": measured_nm,
                "unit": "nm",
            })

    record = {
        "wafer_id": wafer_id,
        "wafer_diameter_mm": round(rr.wafer_radius_m * 2 * 1000),
        "notch_direction": "Bottom",
        "edge_exclusion_mm": rr.edge_exclusion_m * 1000.0,
        "coord_kind": "polar",
        "series_id": pack,
        "notes": f"합성 — sim.engine.simulate(pack={pack!r}) 반경 프로파일 + 가우시안 측정노이즈",
        "points": points,
        "_provenance": {
            "generator": "tools/make_synthetic_wafer.py",
            "engine_commit": _git_commit(),
            "seed": seed,
            "warning": "합성 데이터 — 실측 아님",
        },
    }
    return record


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("oxide_silica", "SYN-OXIDE-SILICA-001", 20260918),
        ("cu_h2o2_bta", "SYN-CU-H2O2-BTA-001", 20260919),
    ]
    for pack, wafer_id, seed in jobs:
        record = make_one(pack, wafer_id, seed)
        out = OUT_DIR / f"{wafer_id}.json"
        out.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{out.relative_to(ROOT)}  ({out.stat().st_size} bytes, {len(record['points'])} points)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
