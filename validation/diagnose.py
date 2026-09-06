"""백테스트 오차 진단 — 어느 조건에서, 어떤 축에서 틀렸나.

목적: ρ가 낮다는 사실만으로는 다음 작업을 못 정한다.
      "기계항(P·V) 자체가 무력한가" vs "우리 모델이 기계항을 잘못 계산하나"를 가른다.
"""
import sys
from pathlib import Path

import numpy as np
import yaml

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
from sim.engine import Recipe, simulate  # noqa: E402
import sim.models  # noqa: E402,F401
from validation.backtest import spearman_rho, DATASET_DIR  # noqa: E402


def diag(path):
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    conds = raw["conditions"]
    obs, pred, pv = [], [], []
    for c in conds:
        r = simulate(Recipe(pack=raw.get("pack", "oxide_silica"),
                            pressure_psi=c["pressure_psi"],
                            rpm_wafer=c["rpm_wafer"], rpm_platen=c["rpm_platen"]),
                     model="tier2.gw_physical_kp")
        pred.append(float(np.mean(r.mrr_nm_per_min)))
        obs.append(float(c["mrr_nm_per_min"]))
        pv.append(c["pressure_psi"] * max(c["rpm_wafer"], c["rpm_platen"]))

    print(f"\n### {path.stem}  n={len(obs)}")
    print(f"  ρ(model, obs)   = {spearman_rho(pred, obs):+.3f}")
    print(f"  ρ(P·rpm, obs)   = {spearman_rho(pv, obs):+.3f}   ← 기계항 자체의 상한")
    print(f"  ρ(P, obs)       = {spearman_rho([c['pressure_psi'] for c in conds], obs):+.3f}")
    print(f"  ρ(rpm, obs)     = {spearman_rho([max(c['rpm_wafer'], c['rpm_platen']) for c in conds], obs):+.3f}")
    print(f"  ρ(model, P·rpm) = {spearman_rho(pred, pv):+.3f}   ← 모델이 곧 Preston인가")
    # 최악 조건 3개
    err = sorted(zip(conds, pred, obs), key=lambda t: -abs(t[1] - t[2]) / t[2])
    print("  최대 오차 조건:")
    for c, p, o in err[:3]:
        print(f"    {c['label'][:60]:60s} 예측{p:8.1f}  실측{o:8.2f}  ({p/o:5.1f}x)")


if __name__ == "__main__":
    for p in sorted(DATASET_DIR.glob("*.yaml")):
        if not p.stem.startswith("_"):
            diag(p)
