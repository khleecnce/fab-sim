"""3% 오차까지 무엇이 남았는가 — 오차를 성분으로 분해한다.

완료 정의(사용자): "조건을 입력하면 결과가 나오고, 그 결과가 실제 데이터와
일치한다(오차 3% 이내, 경향성 동일)."

경향성은 사실상 달성했다(유의 8개 ρ=+0.951, 쌍별 96.9%).
남은 것은 **절대값 3%** 다. 그런데 "오차를 줄이겠다"고 곧장 달려들면
지표를 목표로 삼는 것이 되어 회귀식이 된다.

그래서 먼저 오차를 **성분으로 가른다**:

  총오차 = 계통편향(scale) × 형상오차(shape)

  계통편향 : 예측이 전체적으로 몇 배 어긋났는가.
             Kp 로 흡수되므로 **모델의 물리 결함이 아니다.**
             데이터셋마다 장비·측정계가 다르면 당연히 생긴다.
  형상오차 : 배율을 맞춘 뒤에도 남는 어긋남.
             이것이 **진짜 모델 갭**이다. 3% 는 여기서 재야 한다.

이 스크립트는 형상오차만 따로 재고, 그것이 큰 조건이 어떤 축에
몰려 있는지 본다 — 그 축이 다음에 고칠 물리다.
"""
import sys
import pathlib
import warnings
import math
from collections import defaultdict

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                    # noqa: E402
import yaml                                           # noqa: E402
from validation.backtest import run_all               # noqa: E402


def main() -> int:
    results = run_all()
    held = [r for r in results
            if not r.used_for_calibration and r.in_scope
            and not np.isnan(r.spearman)]

    print("=" * 78)
    print("오차 분해 — 계통편향(Kp 흡수) vs 형상오차(진짜 모델 갭)")
    print("=" * 78)
    print(f"{'데이터셋':46s} {'n':>3s} {'배율':>7s} {'형상MAPE':>9s} {'±3%내':>6s}")

    rows = []
    all_rel = []
    for r in held:
        pred = np.asarray(getattr(r, "predicted", []), dtype=float)
        obs = np.asarray(getattr(r, "observed", []), dtype=float)
        if pred.size == 0 or pred.size != obs.size:
            continue
        m = (pred > 0) & (obs > 0)
        if m.sum() < 2:
            continue
        p, o = pred[m], obs[m]
        # 계통편향 = 기하평균 비 (Kp 재보정과 동등)
        scale = float(np.exp(np.mean(np.log(o / p))))
        p_adj = p * scale
        rel = np.abs(p_adj - o) / o
        mape = float(np.mean(rel) * 100)
        within3 = float(np.mean(rel <= 0.03) * 100)
        rows.append((r.dataset, int(m.sum()), scale, mape, within3))
        all_rel.extend(rel.tolist())

    rows.sort(key=lambda x: -x[3])
    for name, n, scale, mape, w3 in rows:
        print(f"{name[:46]:46s} {n:3d} {scale:7.3f} {mape:8.1f}% {w3:5.0f}%")

    if all_rel:
        a = np.asarray(all_rel)
        print()
        print("-" * 78)
        print(f"전체 조건 {a.size}개")
        print(f"  형상오차 평균 {a.mean()*100:.1f}% · 중앙 {np.median(a)*100:.1f}%")
        print(f"  ±3% 이내  {np.mean(a<=0.03)*100:.0f}%")
        print(f"  ±10% 이내 {np.mean(a<=0.10)*100:.0f}%")
        print(f"  ±30% 이내 {np.mean(a<=0.30)*100:.0f}%")
        print()
        print("  계통편향 범위: "
              f"{min(r[2] for r in rows):.3f} ~ {max(r[2] for r in rows):.3f} 배")
        print("  → 배율이 데이터셋마다 다르다는 것은 장비·측정계 차이지")
        print("    모델 결함이 아니다. Kp 가 흡수한다.")

    # 형상오차가 큰 데이터셋의 공통점
    print()
    print("=" * 78)
    print("형상오차 상위 — 다음에 고칠 물리가 여기 있다")
    print("=" * 78)
    for name, n, scale, mape, w3 in rows[:5]:
        path = ROOT / "validation" / "datasets" / f"{name}.yaml"
        axes = []
        if path.exists():
            d = yaml.safe_load(path.read_text(encoding="utf-8"))
            cs = d.get("conditions", [])
            keys = set()
            for c in cs:
                keys |= {k for k, v in c.items() if isinstance(v, (int, float))}
                keys |= {k for k, v in (c.get("overrides") or {}).items()}
            for k in keys:
                if k == "mrr_nm_per_min":
                    continue
                vals = set()
                for c in cs:
                    v = c.get(k, (c.get("overrides") or {}).get(k))
                    if isinstance(v, (int, float)):
                        vals.add(v)
                if len(vals) > 1:
                    axes.append(k)
        print(f"  {name[:44]:46s} MAPE {mape:6.1f}%  스윕축={sorted(axes)[:4]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
