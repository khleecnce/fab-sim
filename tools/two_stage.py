#!/usr/bin/env python3
"""2단계 최적화 — 실측 병합 → 물리·화학 모델 → 두 단계에서 실측에 근접시킨다.

사용자 지시 (2026-09-09):
  "CMP 공정 모델링은 병행하되, 실제데이터 merge단계 -> 물리학, 화학에 의한 모델링 ->
   두가지 단계에서 최적화하여 실제 데이터에 근접한 값 예측"

단계 정의 (역할이 다르므로 섞지 않는다)
──────────────────────────────────────
Stage A — 실측 병합 (data merge). 대상: **절대값**.
  모든 실측(validation/datasets held-out + data/store 사용자 실측)을 팩별로 모아
  예측 대비 비율의 분포를 본다. 물리 형상은 건드리지 않고 Kp 하나(팩별 스칼라)만 맞춘다.
  → 출력: 팩별 Kp 보정 배수 + 산포. 산포가 크면 "조건이 섞였다"는 신호이지 Kp 문제가
    아니다(그건 Stage B 몫).
  ⚠ held-out을 Kp 보정에 쓰면 그 데이터셋은 이후 절대값 검증에 못 쓴다. 그래서 Stage A
    는 **순위 지표(ρ)를 절대 건드리지 않는다** — 스칼라 곱은 순위 불변이다. 검증 무결성이
    수학적으로 보존된다.

Stage B — 물리·화학 모델 (form). 대상: **형상** (조건 간 상대 변화).
  Kp를 고정한 채, 팩터(χ pH·산화제, κ 입자·경도, τ 전달…)의 형상 파라미터 중
  confidence ≠ verified 인 것만 좁은 범위에서 탐색해 held-out ρ와 log-잔차 형상을 개선한다.
  탐색 범위는 문헌이 준 값의 ±(estimated 50%, literature 20%)로 제한 — 문헌 밖으로
  나가는 것은 최적화가 아니라 할루시네이션이다. verified 파라미터는 건드리지 않는다.
  → 출력: 파라미터 제안 + 전/후 ρ·잔차 + 어느 데이터셋이 개선/악화됐는지.
  ⚠ 자동 적용하지 않는다. 제안을 파일로 남기고 QA 루프(qa_loop --strict)가 통과할 때만
    사람이/크론이 팩에 반영한다.

명령
  two_stage.py stageA [--pack P]          — 팩별 Kp 보정 배수 산출 (실측 병합)
  two_stage.py stageB [--pack P] [--budget N] — 형상 파라미터 탐색 제안
  two_stage.py report                      — 두 단계 전후 요약
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "validation"))

OUT_DIR = ROOT / "validation" / "two_stage"
DS_DIR = ROOT / "validation" / "datasets"


# ───────────────────────────────────────────── 공통
def _datasets_for(pack: str) -> List[Tuple[str, Dict]]:
    out = []
    for f in sorted(DS_DIR.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if d.get("pack") != pack or d.get("in_scope") is False:
            continue
        out.append((f.stem, d))
    return out


def _predict(pack: str, cond: Dict, extra_overrides: Optional[Dict] = None) -> Optional[float]:
    import backtest
    from sim.engine import simulate
    rec = backtest._recipe_from(cond, pack)
    if extra_overrides:
        ov = dict(rec.pack_overrides or {})
        ov.update(extra_overrides)
        rec = type(rec)(**{**rec.__dict__, "pack_overrides": ov})
    try:
        import numpy as _np
        return float(_np.mean(simulate(rec).mrr_nm_per_min))
    except Exception:
        return None


def _spearman(x: List[float], y: List[float]) -> float:
    import backtest
    return backtest.spearman_rho(x, y)


def _pack_params(pack: str) -> Dict[str, Dict]:
    p = ROOT / "knowledge" / "params" / f"{pack}.yaml"
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return d.get("params", {})


# ───────────────────────────────────────────── Stage A
def stage_a(pack: str, include_store: bool = True) -> Dict[str, Any]:
    """팩별 Kp 배수. held-out(ρ 불변) + 사용자 실측(data/store)."""
    ratios, rows = [], []
    for name, d in _datasets_for(pack):
        if d.get("used_for_calibration"):
            continue
        for c in d.get("conditions", []):
            meas = c.get("mrr_nm_per_min")
            if meas is None:
                continue
            pred = _predict(pack, c)
            if pred and pred > 0 and meas > 0:
                ratios.append(meas / pred)
                rows.append({"dataset": name, "label": c.get("label"), "meas": meas, "pred": round(pred, 2),
                             "ratio": round(meas / pred, 4), "read": c.get("read_method")})
    store_n = 0
    if include_store:
        try:
            from sim.store import list_measurements
            for m in list_measurements(limit=1000):
                if m.get("pack_hint") != pack or m.get("mrr_mean") is None:
                    continue
                pred = _predict(pack, m["conditions"])
                if pred and pred > 0:
                    ratios.append(m["mrr_mean"] / pred)
                    rows.append({"dataset": "user_store", "label": m.get("label"), "meas": m["mrr_mean"],
                                 "pred": round(pred, 2), "ratio": round(m["mrr_mean"] / pred, 4), "read": "user"})
                    store_n += 1
        except Exception:
            pass
    if not ratios:
        return {"pack": pack, "n": 0, "kp_multiplier": 1.0, "note": "실측 0건 — 보정 없음"}
    logs = sorted(math.log(r) for r in ratios)
    med = math.exp(logs[len(logs) // 2])
    q1, q3 = math.exp(logs[len(logs) // 4]), math.exp(logs[(3 * len(logs)) // 4])
    spread = (q3 - q1) / med
    by_ds = defaultdict(list)
    for r in rows:
        by_ds[r["dataset"]].append(r["ratio"])
    per_ds = {k: {"n": len(v), "median_ratio": round(sorted(v)[len(v) // 2], 3)} for k, v in by_ds.items()}
    # 데이터셋 간 중앙값이 3배 이상 갈리면 "조건이 다른 계"다 — Kp 하나로 못 맞춘다
    meds = [v["median_ratio"] for v in per_ds.values()]
    split = (max(meds) / min(meds)) if len(meds) > 1 and min(meds) > 0 else 1.0
    note = (f"실측 {len(ratios)}건(사용자 {store_n}) 중앙값 비 {med:.3f} → Kp ×{med:.3f}. IQR/중앙값 {spread:.2f}. "
            f"데이터셋 간 편차 {split:.1f}배.")
    if split > 3:
        note += (" ⚠ 데이터셋마다 절대값 체계가 다르다(pH·입자·패드가 다른 계) — Kp 하나로 못 맞춘다. "
                 "Stage B(형상)가 그 차이를 흡수해야 하고, 안 되면 팩을 조건별로 분리해야 한다.")
    return {"pack": pack, "n": len(ratios), "user_n": store_n, "kp_multiplier": round(med, 4),
            "spread_iqr": round(spread, 3), "dataset_split": round(split, 2), "per_dataset": per_ds,
            "note": note, "rows": rows}


# ───────────────────────────────────────────── Stage B
TUNABLE_CONF = {"estimated": 0.5, "literature": 0.2, "unverified": 0.5}


def _tunables(pack: str) -> Dict[str, Tuple[float, float, float]]:
    """형상 파라미터 후보 → (기준값, min, max). verified·식별자·Kp는 제외."""
    out = {}
    for k, p in _pack_params(pack).items():
        v = p.get("value") if isinstance(p, dict) else p
        conf = (p.get("confidence") if isinstance(p, dict) else "") or ""
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            continue
        if k in ("kp_m_per_pa",) or k.endswith("_ref") or k.endswith("_ref_wt_pct") or k.endswith("_ref_mM"):
            continue     # 기준점은 1.0 계약이라 건드리면 이중계상
        if conf not in TUNABLE_CONF:
            continue
        w = TUNABLE_CONF[conf]
        lo, hi = v * (1 - w), v * (1 + w)
        if v == 0:
            continue
        out[k] = (float(v), float(min(lo, hi)), float(max(lo, hi)))
    return out


def _score(pack: str, overrides: Dict[str, float], kp_mult: float) -> Tuple[float, float, int]:
    """held-out 전체: 평균 ρ(데이터셋별, n≥4만) 와 log-잔차 표준편차(형상), 조건수."""
    rhos, logres, n = [], [], 0
    for name, d in _datasets_for(pack):
        if d.get("used_for_calibration"):
            continue
        xs, ys = [], []
        for c in d.get("conditions", []):
            meas = c.get("mrr_nm_per_min")
            if meas is None:
                continue
            pred = _predict(pack, c, overrides)
            if pred and pred > 0 and meas > 0:
                xs.append(pred * kp_mult); ys.append(meas)
                logres.append(math.log(meas / (pred * kp_mult)))
        if len(xs) >= 4:
            rhos.append(_spearman(xs, ys)); n += len(xs)
    if not rhos:
        return float("nan"), float("nan"), 0
    mu = sum(logres) / len(logres)
    sd = math.sqrt(sum((x - mu) ** 2 for x in logres) / max(len(logres) - 1, 1))
    return sum(rhos) / len(rhos), sd, n


def stage_b(pack: str, kp_mult: float, budget: int = 60, grid: int = 5) -> Dict[str, Any]:
    tun = _tunables(pack)
    base_rho, base_sd, n = _score(pack, {}, kp_mult)
    result = {"pack": pack, "kp_multiplier": kp_mult, "n_conditions": n, "tunables": tun,
              "baseline": {"rho": round(base_rho, 4), "log_resid_sd": round(base_sd, 4)}, "trials": [], "proposal": None}
    if not tun or n == 0:
        result["note"] = "탐색할 형상 파라미터가 없거나(전부 verified) held-out이 없다."
        return result
    # 좌표 하강: 파라미터 하나씩 격자 탐색, 개선되면 채택. budget = 총 시뮬 호출 상한(대략).
    cur, cur_rho, cur_sd = {}, base_rho, base_sd
    calls = 0
    for k, (v0, lo, hi) in tun.items():
        best = None
        for g in range(grid):
            val = lo + (hi - lo) * g / (grid - 1)
            trial = dict(cur); trial[k] = val
            rho, sd, _ = _score(pack, trial, kp_mult); calls += 1
            result["trials"].append({"param": k, "value": round(val, 6), "rho": round(rho, 4), "sd": round(sd, 4)})
            # 목적: ρ 우선, 동률이면 형상 잔차 sd
            if not math.isnan(rho) and (best is None or (rho, -sd) > (best[1], -best[2])):
                best = (val, rho, sd)
            if calls >= budget:
                break
        if best and ((best[1] - cur_rho) > 0.01 or (abs(best[1] - cur_rho) <= 0.01 and best[2] < cur_sd - 0.02)):
            cur[k] = best[0]; cur_rho, cur_sd = best[1], best[2]
        if calls >= budget:
            break
    if cur:
        result["proposal"] = {"overrides": {k: round(v, 6) for k, v in cur.items()},
                              "rho": round(cur_rho, 4), "log_resid_sd": round(cur_sd, 4),
                              "delta_rho": round(cur_rho - base_rho, 4), "delta_sd": round(cur_sd - base_sd, 4)}
        result["note"] = ("제안은 자동 적용되지 않는다. 팩에 반영하려면 각 파라미터 note에 '2단계 최적화 제안 "
                          f"{time.strftime('%Y-%m-%d')}: 문헌값 {'/'.join(f'{k}={tun[k][0]}' for k in cur)} → 제안값' 을 남기고 "
                          "qa_loop.py run --strict 가 PASS일 때만 커밋하라.")
    else:
        result["note"] = "문헌 범위 안에서 ρ를 0.01 넘게 올리는 형상 변경이 없다 — 현재 형상이 문헌 범위 내 최적. 개선은 새 항(미모델링 팩터) 추가로만 가능."
    return result


# ───────────────────────────────────────────── CLI
def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a_ = sub.add_parser("stageA"); a_.add_argument("--pack"); a_.add_argument("--no-store", action="store_true")
    b_ = sub.add_parser("stageB"); b_.add_argument("--pack"); b_.add_argument("--budget", type=int, default=60)
    sub.add_parser("report")
    a = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    from sim.params import available_packs
    packs = [a.pack] if getattr(a, "pack", None) else [p for p in available_packs() if p != "base"]

    if a.cmd == "stageA":
        for p in packs:
            r = stage_a(p, include_store=not a.no_store)
            (OUT_DIR / f"{p}.stageA.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[{p}] n={r['n']} Kp×{r['kp_multiplier']} spread={r.get('spread_iqr')} split={r.get('dataset_split')}")
            print("   ", r["note"])
            for k, v in (r.get("per_dataset") or {}).items():
                print(f"      {k:50} n={v['n']:3} median ratio {v['median_ratio']}")
    elif a.cmd == "stageB":
        for p in packs:
            fa = OUT_DIR / f"{p}.stageA.json"
            kp = json.loads(fa.read_text())["kp_multiplier"] if fa.exists() else 1.0
            r = stage_b(p, kp, budget=a.budget)
            (OUT_DIR / f"{p}.stageB.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[{p}] Kp×{kp} n={r['n_conditions']} baseline ρ={r['baseline']['rho']} sd={r['baseline']['log_resid_sd']}")
            print(f"    tunables: {list(r['tunables'].keys())}")
            if r["proposal"]:
                pr = r["proposal"]
                print(f"    → 제안 ρ={pr['rho']} (Δ{pr['delta_rho']:+}) sd={pr['log_resid_sd']} (Δ{pr['delta_sd']:+}): {pr['overrides']}")
            print("   ", r.get("note", ""))
    elif a.cmd == "report":
        for p in packs:
            fa, fb = OUT_DIR / f"{p}.stageA.json", OUT_DIR / f"{p}.stageB.json"
            A = json.loads(fa.read_text()) if fa.exists() else {}
            B = json.loads(fb.read_text()) if fb.exists() else {}
            print(f"== {p}")
            print(f"  A 실측병합: n={A.get('n', 0)} Kp×{A.get('kp_multiplier', '-')} 데이터셋간 편차 {A.get('dataset_split', '-')}배")
            if B:
                print(f"  B 형상: baseline ρ={B['baseline']['rho']} → " + (f"제안 ρ={B['proposal']['rho']} {B['proposal']['overrides']}" if B.get("proposal") else "개선 없음(문헌 범위 내 최적)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
