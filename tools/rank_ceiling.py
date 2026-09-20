#!/usr/bin/env python3
"""C4 held-out ρ의 구조적 상한(rank ceiling) — 판정#91.

`tools/completion.py`의 C4는 팩별 "유의 held-out 평균 ρ ≥ RHO_MIN"을 요구한다.
모델이 서로 다른 조건에 **같은 예측값**을 내면(동점 그룹), 그 그룹 내부의 관측
순서를 예측이 전달할 방법이 없으므로 어떤 파라미터 조합으로도 도달 불가능한
ρ 상한이 생긴다. 이 도구는 `validation/backtest.py`가 실제로 조건을 Recipe로
바꾸는 경로(`_recipe_from` + `simulate`)를 그대로 써서 그 상한을 계산한다.

⚠ 근사하지 마라: 데이터셋 YAML의 키를 직접 읽어 그룹을 짓는 것은 모델이 그
키를 실제로 쓰는지(연결됐는지, 지수가 0이 아닌지)를 확인하지 않은 추측이다.
반드시 `backtest.simulate(backtest._recipe_from(cond, pack))`을 실행한 뒤 그
출력값의 동일 여부로 그룹을 지어야 한다(knowledge/cmp/
c4-heldout-rank-ceiling-structural-bound.md §3 참조 — 이 차이가 실제로
tw202115224a에서 12 vs 2 그룹이라는 결과 차이를 냈다).
"""
from __future__ import annotations

import argparse
import itertools
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "validation") not in sys.path:
    sys.path.insert(0, str(_ROOT / "validation"))

import backtest  # noqa: E402  (perm_p_value·spearman_rho·run_all·_recipe_from 재사용)


def _ranks(v: List[float]) -> List[float]:
    """backtest.spearman_rho 내부 ranks()와 동일 로직(동점은 평균순위)."""
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def group_by_prediction(pred: List[float]) -> Dict[float, List[int]]:
    """동일 예측값(반올림 9자리 — backtest.run_dataset의 동일 분산-0 판정과 같은 정밀도)을
    한 그룹으로 묶는다. 인덱스를 값으로 매핑한다."""
    groups: Dict[float, List[int]] = {}
    for i, p in enumerate(pred):
        key = round(float(p), 9)
        groups.setdefault(key, []).append(i)
    return groups


def optimal_group_order_rho(pred: List[float], obs: List[float]) -> float:
    """동점 예측 그룹의 최적 배치에서 나오는 ρ 상한 (폐형식).

    동점 그룹 내부는 예측이 동일하므로 자유도는 그룹의 '순서'뿐이다(그룹 내부
    순열은 예측 순위에 아무 영향이 없다 — 어차피 동점 평균순위로 묶인다).
    그룹을 관측 평균순위 오름차순으로 배치하면 Spearman(=순위 Pearson)이
    최대화된다: 고정된 y-순위 벡터에 대해 블록 상수인 x를 y-블록평균 오름차순
    으로 정렬하는 것은 재배열 부등식(rearrangement inequality)의 표준 결과다
    (공분산 Σ(x_i-x̄)(y_i-ȳ)는 두 수열을 같은 방향으로 정렬할 때 최대).

    이 함수는 그 폐형식을 계산만 한다 — **최적성 자체의 증명은 주장이지 확인이
    아니다.** tests/test_rank_ceiling.py가 G≤8인 데이터셋에서 이 결과를
    `brute_force_group_order_rho`(전수 G! 순열)와 대조해 기계로 확인한다.
    """
    n = len(pred)
    if n < 3:
        return float("nan")
    y_ranks = _ranks(obs)
    groups = group_by_prediction(pred)
    order = sorted(groups.keys(),
                    key=lambda k: statistics.mean(y_ranks[i] for i in groups[k]))
    level = {k: float(i) for i, k in enumerate(order)}
    assigned = [level[round(float(p), 9)] for p in pred]
    return backtest.spearman_rho(assigned, obs)


def brute_force_group_order_rho(pred: List[float], obs: List[float]) -> float:
    """폐형식 대조용 전수 순열 탐색. G! 이 계산량이라 G≤8 정도에서만 쓴다."""
    groups = group_by_prediction(pred)
    keys = list(groups.keys())
    best = float("-inf")
    for perm in itertools.permutations(range(len(keys))):
        level = {keys[i]: float(perm[i]) for i in range(len(keys))}
        assigned = [level[round(float(p), 9)] for p in pred]
        rho = backtest.spearman_rho(assigned, obs)
        if rho > best:
            best = rho
    return best


def n_groups(pred: List[float]) -> int:
    return len(group_by_prediction(pred))


@dataclass
class CeilingResult:
    dataset: str
    pack: str
    n: int
    groups: int
    rho_ceiling: float
    ceiling_p: Optional[float]
    actual_rho: float
    achievement: Optional[float]   # actual_rho / rho_ceiling


def compute_all(model: str = "tier2.gw_physical_kp") -> List[CeilingResult]:
    """`validation/backtest.py`가 이미 계산한 predicted/observed(=_recipe_from
    +simulate 를 실행한 결과, run_dataset 내부와 완전히 같은 값)를 그대로
    재사용한다 — 별도 경로로 다시 계산하면 두 도구가 몰래 갈라질 수 있다."""
    out: List[CeilingResult] = []
    for r in backtest.run_all(model=model):
        if r.n < 3 or not r.predicted or np.isnan(r.spearman):
            continue
        g = n_groups(r.predicted)
        ceil_rho = optimal_group_order_rho(r.predicted, r.observed)
        ceil_p = backtest.perm_p_value(ceil_rho, r.n)
        achievement = None
        if ceil_rho and not np.isnan(ceil_rho) and abs(ceil_rho) > 1e-12:
            achievement = r.spearman / ceil_rho
        out.append(CeilingResult(r.dataset, r.pack, r.n, g, ceil_rho, ceil_p,
                                  r.spearman, achievement))
    return out


def format_line(r: CeilingResult) -> str:
    p = f"p={r.ceiling_p:.4f}" if r.ceiling_p is not None else "p=—"
    ach = f"{r.achievement*100:5.1f}%" if r.achievement is not None else "    —"
    return (f"{r.dataset:44s} n={r.n:3d}  groups={r.groups:3d}  "
            f"ρ_ceiling={r.rho_ceiling:+.4f} ({p})  "
            f"actual ρ={r.actual_rho:+.4f}  달성률={ach}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true",
                    help="상한<1.0 인 것만이 아니라 전체 데이터셋을 출력")
    ap.add_argument("--pack", default=None, help="이 팩 이름으로 필터")
    args = ap.parse_args()

    results = compute_all()
    if args.pack:
        results = [r for r in results if r.pack == args.pack]
    if not args.all:
        results = [r for r in results if r.rho_ceiling < 1.0 - 1e-9]

    print("=" * 100)
    print("C4 held-out 구조적 상한(rank ceiling) — 모델이 실제로 보는 고유 입력 그룹 기준")
    print("(backtest.py의 실제 _recipe_from+simulate 경로로 그룹을 짓는다. 근사 아님)")
    print("=" * 100)
    if not results:
        print("(조건에 맞는 데이터셋 없음)")
        return 0
    for r in sorted(results, key=lambda r: r.rho_ceiling):
        print(format_line(r))
        if r.ceiling_p is not None and r.ceiling_p >= backtest.BacktestResult.P_THRESHOLD:
            print("    · ⚠ 상한 자체가 유의 문턱(p<0.05)을 못 넘는다 — "
                  "어떤 모델로도 이 held-out을 영원히 유의하게 만들 수 없다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
