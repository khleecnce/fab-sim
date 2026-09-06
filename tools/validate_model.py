#!/usr/bin/env python3
"""모델 검증 — 시뮬레이션 예측과 실측을 비교한다.

  python3 tools/validate_model.py --run-id run01
  python3 tools/validate_model.py --run-id run01 --pack cu_h2o2_bta
  python3 tools/validate_model.py --run-id run01 --scan-kp   # Kp 역산

이 도구의 목적은 "맞았다"가 아니라 **"어디가 얼마나 틀렸나"**를 보는 것이다.
- 절대값이 틀리면 → Kp 캘리브레이션 문제 (예상됨. Kp는 미검증 오더값이다)
- 형상이 틀리면 → 물리 모델 문제 (심각. 압력·속도 분포가 실제와 다르다)
두 가지를 분리해서 보고한다. 합쳐서 "오차 30%"라고 말하면 진단이 안 된다.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
PARSED = ROOT / "data" / "customer" / "parsed"
REPORTS = ROOT / "data" / "customer" / "reports"

import sim.models  # noqa: F401,E402
from sim.engine import Recipe, simulate  # noqa: E402
from sim.metrics.uniformity import compute_metrics  # noqa: E402


def load_run(run_id: str) -> dict:
    f = PARSED / f"{run_id}.json"
    if not f.exists():
        raise SystemExit(f"{f} 없음. 먼저 ingest_measurement.py 를 실행하십시오.")
    return json.loads(f.read_text())


def measured_profile(run: dict) -> tuple:
    """(radius_mm, value_nm_min, 값 종류). 위치 없으면 (None, 평균, 종류)."""
    pts = run["points"]
    key = next((k for k in ("mrr_nm_min", "removed_nm", "thickness_post_nm")
                if any(k in p for p in pts)), None)
    if key is None:
        raise SystemExit("비교할 측정값이 없다")
    vals = np.array([p[key] for p in pts if key in p], dtype=float)
    if any("radius_mm" in p for p in pts):
        r = np.array([p.get("radius_mm", np.nan) for p in pts if key in p], dtype=float)
    elif all(any(k in p for p in pts) for k in ("x_mm", "y_mm")):
        x = np.array([p.get("x_mm", np.nan) for p in pts if key in p], dtype=float)
        y = np.array([p.get("y_mm", np.nan) for p in pts if key in p], dtype=float)
        r = np.hypot(x, y)
    else:
        return None, vals, key
    ok = ~(np.isnan(r) | np.isnan(vals))
    order = np.argsort(r[ok])
    return r[ok][order], vals[ok][order], key


def build_recipe(run: dict, pack: str, kp: Optional[float] = None) -> Recipe:
    c = run["conditions"]
    over = {}
    if kp is not None:
        over["kp_m_per_pa"] = kp
    dia = c.get("wafer_diameter_mm")
    if dia:
        over["wafer_radius_m"] = float(dia) / 2000.0
    return Recipe(
        pack=pack,
        pressure_psi=c.get("pressure_psi"),
        rpm_wafer=c.get("rpm_wafer"),
        rpm_platen=c.get("rpm_platen"),
        time_s=float(c.get("time_s", 60)),
        n_points=max(len(run["points"]), 21),
        pack_overrides=over,
    )


def compare(run: dict, pack: str, model: str, kp: Optional[float] = None) -> dict:
    r_meas, v_meas, kind = measured_profile(run)
    rec = build_recipe(run, pack, kp)
    res = simulate(rec, model=model)

    # 실측이 제거량이면 시뮬도 제거량으로 맞춘다
    sim_r_mm = res.radius_m * 1000
    sim_v = res.mrr_nm_per_min if kind == "mrr_nm_min" else res.removed_nm
    if kind == "thickness_post_nm":
        return {"error": "잔막 비교는 초기 두께가 필요하다 — pre 컬럼을 넣으십시오"}

    out: Dict[str, Any] = {
        "run_id": run["run_id"], "pack": pack, "model": model,
        "compared_on": kind,
        "kp_used": rec.pack_overrides.get("kp_m_per_pa"),
        "measured": {"n": int(len(v_meas)), "mean": float(np.mean(v_meas)),
                     "min": float(np.min(v_meas)), "max": float(np.max(v_meas)),
                     "std": float(np.std(v_meas))},
        "simulated": {"mean": float(np.mean(sim_v)), "min": float(np.min(sim_v)),
                      "max": float(np.max(sim_v)), "std": float(np.std(sim_v))},
        "notes": res.notes,
    }

    m_mean, s_mean = out["measured"]["mean"], out["simulated"]["mean"]
    out["level"] = {
        "bias_pct": float((s_mean - m_mean) / m_mean * 100) if m_mean else None,
        "ratio": float(s_mean / m_mean) if m_mean else None,
        "verdict": None,
    }
    b = abs(out["level"]["bias_pct"] or 0)
    out["level"]["verdict"] = ("절대값 일치(±10%)" if b < 10 else
                               "절대값 근접(±30%)" if b < 30 else
                               f"절대값 불일치 ({b:.0f}%) — Kp 캘리브레이션 필요")

    # 형상 비교 — 여기가 물리 모델의 진짜 시험대
    if r_meas is not None and len(r_meas) >= 4:
        sim_interp = np.interp(r_meas, sim_r_mm, sim_v)
        # 각자의 평균으로 정규화 → 절대값 편차를 제거하고 형상만 본다
        mn, sn = v_meas / np.mean(v_meas), sim_interp / np.mean(sim_interp)
        resid = sn - mn
        ss_res = float(np.sum(resid ** 2))
        ss_tot = float(np.sum((mn - np.mean(mn)) ** 2))
        out["shape"] = {
            "rmse_norm_pct": float(np.sqrt(np.mean(resid ** 2)) * 100),
            "max_dev_norm_pct": float(np.max(np.abs(resid)) * 100),
            "r2": float(1 - ss_res / ss_tot) if ss_tot > 1e-12 else None,
            "corr": float(np.corrcoef(mn, sn)[0, 1]) if len(mn) > 2 else None,
            "measured_range_pct": float((v_meas.max() - v_meas.min())
                                        / np.mean(v_meas) * 100),
            "sim_range_pct": float((sim_interp.max() - sim_interp.min())
                                   / np.mean(sim_interp) * 100),
        }
        sh = out["shape"]
        amp_m, amp_s = sh["measured_range_pct"], sh["sim_range_pct"]
        # 진폭 비 — 시뮬이 변동을 아예 못 만들면 RMSE가 작아도 실패다.
        # (2026-09-06 합성 시험에서 실측 12.1% vs 시뮬 0.1%인데 "대체로 일치"로
        #  판정한 버그. RMSE만 보면 평탄한 예측이 유리해진다.)
        sh["amplitude_ratio"] = float(amp_s / amp_m) if amp_m > 1e-9 else None
        ar = sh["amplitude_ratio"]
        if amp_m < 1.0:
            sh["verdict"] = "실측 프로파일이 거의 평탄 — 형상 비교의 변별력이 낮다"
        elif ar is not None and (ar < 0.5 or ar > 2.0):
            side = "과소" if ar < 1 else "과대"
            sh["verdict"] = (
                f"형상 불일치 — 시뮬이 반경 변동을 {side}예측한다 "
                f"(실측 진폭 {amp_m:.1f}% vs 시뮬 {amp_s:.2f}%, ×{ar:.3f}). "
                "Kp로 못 고친다. 압력분포·속도장·엣지 효과 모델을 봐야 한다.")
        elif sh["rmse_norm_pct"] < 2:
            sh["verdict"] = "형상 일치"
        elif sh["rmse_norm_pct"] < 5:
            sh["verdict"] = "형상 대체로 일치 — 국소 편차 확인 필요"
        else:
            sh["verdict"] = (f"형상 불일치 (RMSE {sh['rmse_norm_pct']:.1f}%) — "
                             "압력·속도 분포 모델이 실제와 다르다. Kp로 못 고친다.")
        # 균일도 지표 비교
        try:
            mm = compute_metrics(r_meas / 1000, v_meas, n_points=len(v_meas))
            sm = res.metrics
            out["uniformity"] = {
                "measured": {"ttv": mm.ttv_nm, "cv_pct": mm.cv_pct,
                             "radial_sigma_pct": mm.radial_sigma_pct},
                "simulated": {"ttv": sm.ttv_nm, "cv_pct": sm.cv_pct,
                              "radial_sigma_pct": sm.radial_sigma_pct},
            }
        except Exception as e:
            out["uniformity"] = {"error": str(e)}
        out["profile"] = {"radius_mm": r_meas.round(2).tolist(),
                          "measured": v_meas.round(3).tolist(),
                          "simulated": sim_interp.round(3).tolist()}
    else:
        out["shape"] = {"verdict": "위치 정보 없음 — 평균값만 비교했다. "
                                   "형상(프로파일) 검증 불가"}
    return out


def scan_kp(run: dict, pack: str, model: str) -> dict:
    """실측 평균을 맞추는 Kp를 역산한다. Preston 계열은 MRR ∝ Kp라 1회로 끝난다."""
    base = compare(run, pack, model)
    if base.get("error"):
        return base
    ratio = base["level"]["ratio"]
    rec = build_recipe(run, pack)
    kp0 = rec.resolve().kp_m_per_pa
    kp_fit = kp0 / ratio if ratio else kp0
    fitted = compare(run, pack, model, kp=kp_fit)
    return {"kp_pack": kp0, "kp_fitted": kp_fit,
            "factor": kp_fit / kp0, "after_fit": fitted}


def print_report(c: dict):
    if c.get("error"):
        print("✗", c["error"])
        return
    print(f"■ 검증 — run '{c['run_id']}' · 팩 {c['pack']} · 모델 {c['model']}")
    print(f"  비교 대상: {c['compared_on']}\n")
    m, s = c["measured"], c["simulated"]
    print(f"  {'':12}{'실측':>12}{'시뮬':>12}{'차이':>12}")
    print(f"  {'평균':12}{m['mean']:>12.2f}{s['mean']:>12.2f}"
          f"{s['mean']-m['mean']:>+12.2f}")
    print(f"  {'최소':12}{m['min']:>12.2f}{s['min']:>12.2f}")
    print(f"  {'최대':12}{m['max']:>12.2f}{s['max']:>12.2f}")
    print(f"  {'표준편차':10}{m['std']:>12.3f}{s['std']:>12.3f}")

    print(f"\n  ① 절대값: {c['level']['verdict']}")
    print(f"     편차 {c['level']['bias_pct']:+.1f}%  (시뮬/실측 = {c['level']['ratio']:.3f})")

    sh = c.get("shape", {})
    print(f"\n  ② 형상: {sh.get('verdict','—')}")
    if "rmse_norm_pct" in sh:
        print(f"     정규화 RMSE {sh['rmse_norm_pct']:.2f}% · "
              f"최대편차 {sh['max_dev_norm_pct']:.2f}% · "
              f"R² {sh['r2']:.3f}" if sh.get("r2") is not None else "")
        print(f"     실측 진폭 {sh['measured_range_pct']:.2f}% vs "
              f"시뮬 진폭 {sh['sim_range_pct']:.2f}%")

    u = c.get("uniformity")
    if u and "measured" in u:
        print(f"\n  ③ 균일도 지표")
        print(f"     {'':16}{'실측':>10}{'시뮬':>10}")
        for k, lbl in (("ttv", "TTV [nm]"), ("cv_pct", "CV [%]"),
                       ("radial_sigma_pct", "radial σ [%]")):
            print(f"     {lbl:16}{u['measured'][k]:>10.3f}{u['simulated'][k]:>10.3f}")

    if c.get("notes"):
        print("\n  ⚠ 모델 한계 보고")
        for n in c["notes"]:
            print(f"     · {n}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--pack", default="oxide_silica")
    ap.add_argument("--model", default="tier2.gw_physical_kp")
    ap.add_argument("--scan-kp", action="store_true", help="실측에 맞는 Kp 역산")
    ap.add_argument("--save", action="store_true", help="리포트 저장")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    run = load_run(a.run_id)
    if run.get("blockers"):
        print("✗ 비교 불가:")
        for b in run["blockers"]:
            print("  ·", b)
        return 1

    if a.scan_kp:
        r = scan_kp(run, a.pack, a.model)
        print(f"■ Kp 역산 — run '{a.run_id}'\n")
        print(f"  팩 Kp    {r['kp_pack']:.3e} m/Pa")
        print(f"  실측 Kp  {r['kp_fitted']:.3e} m/Pa   (×{r['factor']:.3f})")
        print(f"\n  → 팩의 Kp가 실측 대비 {abs(1/r['factor']-1)*100:.0f}% "
              f"{'높다' if r['factor'] < 1 else '낮다'}. "
              "Kp는 미검증 오더값이므로 이 정도 차이는 예상된 것이다.")
        print("\n  [Kp 보정 후]")
        print_report(r["after_fit"])
        c = r["after_fit"]
        c["kp_scan"] = {k: v for k, v in r.items() if k != "after_fit"}
    else:
        c = compare(run, a.pack, a.model)
        print_report(c)

    if a.json:
        c.pop("profile", None)
        print(json.dumps(c, ensure_ascii=False, indent=2))
    if a.save:
        REPORTS.mkdir(parents=True, exist_ok=True)
        f = REPORTS / f"{a.run_id}_{datetime.now():%Y%m%d_%H%M}.json"
        f.write_text(json.dumps(c, ensure_ascii=False, indent=1))
        print(f"\n  저장 → {f.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
