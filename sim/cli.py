#!/usr/bin/env python3
"""FabSim CLI — 레시피를 넣고 웨이퍼 결과를 받는다.

  python -m sim.cli --pressure 3.0 --rpm-wafer 60 --rpm-platen 55 --time 60
  python -m sim.cli --wafer PTW --pattern-density 0.4 --model tier1.pattern_density
  python -m sim.cli --zones 3.0,3.0,4.5 --zone-edges 0.5,0.8,1.0 --json
  python -m sim.cli --list-models

출력의 ⚠ 항목은 "이 값은 못 낸다/확신 못 한다"는 정직한 보고다. 무시하지 마라.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sim.models  # noqa: F401,E402  (모델 등록 부작용)
from sim.engine import Recipe, simulate, available_models  # noqa: E402


def _floats(s):
    return [float(x) for x in s.split(",")] if s else None


def main() -> int:
    ap = argparse.ArgumentParser(prog="fabsim", description="CMP 시뮬레이터")
    ap.add_argument("--list-models", action="store_true")
    ap.add_argument("--model", default="tier2.gw_physical_kp")
    ap.add_argument("--wafer", choices=["NPW", "PTW"], default="NPW")
    ap.add_argument("--film", default="oxide",
                    choices=["oxide", "nitride", "poly", "cu", "w"])
    ap.add_argument("--pressure", type=float, default=3.0, help="psi")
    ap.add_argument("--rpm-wafer", type=float, default=60.0)
    ap.add_argument("--rpm-platen", type=float, default=55.0)
    ap.add_argument("--time", type=float, default=60.0, help="초")
    ap.add_argument("--kp", type=float, default=1.6e-13, help="Preston 계수 [m/Pa]")
    ap.add_argument("--zones", type=str, help="존 압력 psi, 쉼표구분 (예: 3.0,3.0,4.5)")
    ap.add_argument("--zone-edges", type=str, help="존 경계 정규화반경 (예: 0.5,0.8,1.0)")
    ap.add_argument("--edge-amp", type=float, default=0.0, help="엣지 압력 집중 진폭")
    ap.add_argument("--pattern-density", type=float, help="PTW 평균 패턴 밀도 0~1")
    ap.add_argument("--pad-hours", type=float, help="패드 누적 사용시간")
    ap.add_argument("--thickness", type=float, help="초기 막두께 nm (잔막 계산)")
    ap.add_argument("--points", type=int, default=81, help="측정점 수")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--profile", action="store_true", help="반경별 프로파일 출력")
    a = ap.parse_args()

    if a.list_models:
        for m in available_models():
            print(m)
        return 0

    meta = {}
    if a.pattern_density is not None:
        meta["pattern_density"] = str(a.pattern_density)
    if a.pad_hours is not None:
        meta["pad_hours"] = str(a.pad_hours)

    r = Recipe(wafer=a.wafer, film=a.film, pressure_psi=a.pressure,
               rpm_wafer=a.rpm_wafer, rpm_platen=a.rpm_platen, time_s=a.time,
               kp_m_per_pa=a.kp, zone_pressures_psi=_floats(a.zones),
               zone_edges_norm=_floats(a.zone_edges), edge_pressure_amp=a.edge_amp,
               initial_thickness_nm=a.thickness, n_points=a.points, meta=meta)

    try:
        res = simulate(r, model=a.model)
    except KeyError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1

    if a.json:
        out = res.summary()
        if a.profile:
            out["radius_mm"] = (res.radius_m * 1000).round(2).tolist()
            out["mrr_nm_per_min"] = res.mrr_nm_per_min.round(3).tolist()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    m = res.metrics
    basis = "잔막" if res.remaining_nm is not None else "제거량"
    print(f"■ FabSim — {a.model}")
    print(f"  입력: {r.wafer}/{r.film} · {r.pressure_psi} psi · "
          f"웨이퍼 {r.rpm_wafer}rpm / 플래튼 {r.rpm_platen}rpm · {r.time_s:g}s")
    if r.zone_pressures_psi:
        print(f"        존압력 {r.zone_pressures_psi} psi @ {r.zone_edges_norm}")
    mrr = res.mrr_nm_per_min
    print(f"\n  제거율   평균 {np.mean(mrr):8.2f} nm/min  "
          f"(min {np.min(mrr):.2f} / max {np.max(mrr):.2f})")
    print(f"  제거량   평균 {np.mean(res.removed_nm):8.2f} nm ({r.time_s:g}초)")
    if res.remaining_nm is not None:
        print(f"  잔막     평균 {np.mean(res.remaining_nm):8.2f} nm "
              f"(초기 {r.initial_thickness_nm:g} nm)")
    print(f"\n  균일도 — {basis} 기준 ({m.n_points}pt)")
    print(f"    정의: {m.definition.split('|')[0].strip()}")
    print(f"    TTV          {m.ttv_nm:8.3f} nm")
    print(f"    radial range {m.radial_range_pct:8.3f} %   (문헌default, 방위각평균반경프로파일)")
    print(f"    radial(관행) {m.radial_maxring_range_nm:8.3f} nm  (링 #{m.radial_maxring_range_ring}, 회사관행)")
    print(f"    CV           {m.cv_pct:8.3f} %")
    print(f"    WIWNU(½R)    {m.wiwnu_halfrange_pct:8.3f} %   "
          f"WIWNU(3σ) {m.wiwnu_3sigma_pct:.3f} %")

    미산출 = [k for k, v in (("조도 Ra", res.roughness_ra_nm),
                          ("dishing", res.dishing_nm),
                          ("erosion", res.erosion_nm),
                          ("금속오염", res.metal_contamination),
                          ("결함밀도", res.defect_density)) if v is None]
    if 미산출:
        print(f"\n  미산출: {', '.join(미산출)} — 담당 에이전트 학습 대기 중")
    if res.notes:
        print("\n  ⚠ 모델 한계 보고:")
        for n in res.notes:
            print(f"    · {n}")
    if a.profile:
        print("\n  반경 프로파일 (mm → nm/min)")
        for rr, vv in zip(res.radius_m[::8] * 1000, res.mrr_nm_per_min[::8]):
            bar = "█" * int(vv / max(res.mrr_nm_per_min) * 40)
            print(f"    {rr:6.1f}  {vv:8.2f}  {bar}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
