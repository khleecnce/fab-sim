#!/usr/bin/env python3
"""C4 held-out ρ의 구조적 상한(rank ceiling) — 판정#91, 적격 필터·도달가능성 산술 판정#93.

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

## 판정#93 — C4 적격 여부

이 표에 뜨는 "상한이 1.0에 가까운데 달성률이 바닥" 데이터셋 중에는 `tools/
completion.py::heldout_by_pack`이 애초에 C4 집계에 세지 않는 것들이 섞여 있다
(범위 밖 in_scope=false, 캘리브레이션에 쓴 used_for_calibration=true, 또는
비유의). 이런 것의 ρ를 올리려 물리를 건드리면 C4는 한 칸도 안 움직이는데
모델만 오염된다. 그래서 **기본 출력은 C4가 실제로 세는 것만** 낸다 — 적격
여부는 `tools/completion.c4_eligible`을 그대로 import해서 판정한다(재구현
금지 — 판정#58이 바로 이 유형의 결함이었다: `accuracy_gaps.gaps_bias()`가
`used_for_calibration` 필터를 빠뜨려 자기 캘리브레이션 데이터를 재심사하는
순환을 만들었다).

`--all`과 `--include-ineligible`은 **서로 다른 축**이다:
  --all               : 상한<1.0 인 것만이 아니라 상한==1.0 인 것까지 (기존 뜻, 보존)
  --include-ineligible: C4 적격인 것만이 아니라 범위밖/캘리브레이션/비유의도 포함
둘 다 안 주면 "상한<1.0 이면서 C4 적격"만 나온다. 필터가 걸려 표가 비어도
"남은 병목 없음"으로 오독되지 않도록, 걸러진 건수와 사유별 내역은 표가
비었든 아니든 항상 하단에 출력한다.
"""
from __future__ import annotations

import argparse
import bisect
import functools
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
from tools.completion import (  # noqa: E402  (C4 적격 판정의 유일한 소스 — 재구현 금지)
    RHO_MIN, c4_eligible, dataset_pack_map,
)


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


def _exclusion_reason(r: "backtest.BacktestResult") -> Optional[str]:
    """C4 비적격 사유. `c4_eligible`과 반드시 같은 우선순위로 갈라야 한다
    (heldout_by_pack이 세지 않는 이유를 사람이 읽을 말로 바꾼 것뿐, 판정
    자체는 c4_eligible 하나에서 나온다)."""
    if c4_eligible(r):
        return None
    if not r.in_scope:
        return "범위밖"
    if r.used_for_calibration:
        return "캘리브레이션"
    return "비유의"


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
    in_scope: bool = True
    used_for_calibration: bool = False
    significant: bool = False
    eligible: bool = False         # C4 집계에 실제로 세는가 (tools.completion.c4_eligible)
    exclusion_reason: Optional[str] = None   # eligible=False일 때만


def compute_all(model: str = "tier2.gw_physical_kp",
                 raw_results: Optional[list] = None) -> List[CeilingResult]:
    """`validation/backtest.py`가 이미 계산한 predicted/observed(=_recipe_from
    +simulate 를 실행한 결과, run_dataset 내부와 완전히 같은 값)를 그대로
    재사용한다 — 별도 경로로 다시 계산하면 두 도구가 몰래 갈라질 수 있다.

    `raw_results`(선택): 이미 계산한 `backtest.run_all()` 결과를 넘기면 물리
    시뮬레이션을 다시 돌리지 않는다 — 각 데이터셋이 실제로 GW 접촉 모델
    적분을 실행하므로 `run_all()` 자체가 느리다(수십 초); `compute_uncomputable`
    과 같은 호출에서 두 번 돌리지 않도록 호출자가 공유할 수 있게 한다."""
    out: List[CeilingResult] = []
    raw = raw_results if raw_results is not None else backtest.run_all(model=model)
    for r in raw:
        if r.n < 3 or not r.predicted or np.isnan(r.spearman):
            continue
        g = n_groups(r.predicted)
        ceil_rho = optimal_group_order_rho(r.predicted, r.observed)
        ceil_p = backtest.perm_p_value(ceil_rho, r.n)
        achievement = None
        if ceil_rho and not np.isnan(ceil_rho) and abs(ceil_rho) > 1e-12:
            achievement = r.spearman / ceil_rho
        out.append(CeilingResult(
            r.dataset, r.pack, r.n, g, ceil_rho, ceil_p, r.spearman, achievement,
            in_scope=r.in_scope, used_for_calibration=r.used_for_calibration,
            significant=r.significant, eligible=c4_eligible(r),
            exclusion_reason=_exclusion_reason(r),
        ))
    return out


def compute_uncomputable(model: str = "tier2.gw_physical_kp",
                          raw_results: Optional[list] = None) -> List[Dict]:
    """compute_all()이 애초에 행을 만들지 않는 것들(n<3, 예측 없음, 분산 0 →
    ρ=nan). 이들은 '비유의'와 다른 사유("계산 불가")로 별도 집계해야 한다 —
    n=2짜리를 비유의로 섞으면 표본 부족과 신호 부재를 혼동하게 된다."""
    out: List[Dict] = []
    raw = raw_results if raw_results is not None else backtest.run_all(model=model)
    for r in raw:
        if r.n < 3 or not r.predicted or np.isnan(r.spearman):
            out.append({"dataset": r.dataset, "pack": r.pack, "n": r.n,
                        "reason": "계산불가(n<3 또는 분산0)"})
    return out


def format_line(r: CeilingResult) -> str:
    p = f"p={r.ceiling_p:.4f}" if r.ceiling_p is not None else "p=—"
    ach = f"{r.achievement*100:5.1f}%" if r.achievement is not None else "    —"
    tag = "" if r.eligible else f"  [비적격:{r.exclusion_reason}]"
    return (f"{r.dataset:44s} n={r.n:3d}  groups={r.groups:3d}  "
            f"ρ_ceiling={r.rho_ceiling:+.4f} ({p})  "
            f"actual ρ={r.actual_rho:+.4f}  달성률={ach}{tag}")


def _print_filter_breakdown(all_results: List[CeilingResult],
                             uncomputable: List[Dict],
                             shown: List[CeilingResult],
                             pack: Optional[str]) -> None:
    """과잉 필터 방지 장치(⚠): 필터를 켠 뒤 표가 비면 '병목 없음'으로 오독된다.
    걸러진 건수와 사유별 내역을 표가 비었든 아니든 항상 출력한다."""
    pool = all_results if pack is None else [r for r in all_results if r.pack == pack]
    uncomp = uncomputable if pack is None else [u for u in uncomputable if u["pack"] == pack]
    n_scope = sum(1 for r in pool if r.exclusion_reason == "범위밖")
    n_calib = sum(1 for r in pool if r.exclusion_reason == "캘리브레이션")
    n_nsig = sum(1 for r in pool if r.exclusion_reason == "비유의")
    n_ceil1 = sum(1 for r in pool if r.eligible and r.rho_ceiling >= 1.0 - 1e-9)
    print("-" * 100)
    print(f"전체 {len(pool) + len(uncomp)}건 중 표시 {len(shown)}건. 걸러진 내역: "
          f"범위밖 {n_scope}건 · 캘리브레이션 {n_calib}건 · 비유의 {n_nsig}건 · "
          f"계산불가 {len(uncomp)}건" + (f" · 상한==1.0(--all 아니면 숨김) {n_ceil1}건"
                                        if n_ceil1 else ""))
    if uncomp:
        print("    계산불가: " + ", ".join(f"{u['dataset']}(n={u['n']})" for u in uncomp))
    if not shown and (n_scope or n_calib or n_nsig or uncomp):
        print("    ⚠ 표가 비었다 — 이것은 '남은 병목 없음'이 아니라 "
              "'남은 후보가 전부 필터에 걸렸다'는 뜻이다. --include-ineligible 로 확인하라.")


# ═══════════════ 판정#93 — C4 도달가능성 산술 ═══════════════

@functools.lru_cache(maxsize=None)
def _exact_rho_distribution(n: int) -> tuple:
    """n개 항목의 전수 순열(n!, n<=8에서만 현실적)에서 나오는 Spearman ρ **전체
    분포**(오름차순, 중복 포함) — 한 번만 계산해 캐싱한다. `backtest.
    perm_p_value`가 매 후보 ρ마다 새로 n! 전수열거를 반복하면(exact 분기) 후보
    수만큼 배로 느려지므로, 분포를 한 번 만들어 재사용(이분탐색)한다."""
    base = list(range(n))
    vals = sorted(backtest.spearman_rho(base, list(perm))
                  for perm in itertools.permutations(base))
    return tuple(vals)


def _exact_p_value(rho: float, n: int) -> float:
    """`_exact_rho_distribution(n)`을 이분탐색해 `backtest.perm_p_value`와 같은
    정의(≥ rho - 1e-9 인 비율)의 p값을 준다 — 값은 동일해야 한다(둘 다 n!
    전수열거, 근사 아님). 회귀는 tests/test_rank_ceiling_eligibility.py가
    `backtest.perm_p_value`와 직접 대조한다."""
    dist = _exact_rho_distribution(n)
    idx = bisect.bisect_left(dist, rho - 1e-9)
    return (len(dist) - idx) / len(dist)


def achievable_rhos(n: int) -> List[float]:
    """n개 항목의 순열(동점 없음)에서 나올 수 있는 Spearman ρ의 **정확한** 이산
    집합(내림차순). n<=8 (8!=40320)에서만 전수 열거로 쓴다 — 그 이상은
    `min_significant_rho`가 exact=False로 표시하고 연속 근사(이진탐색)를
    대신 쓴다."""
    return sorted({round(v, 9) for v in _exact_rho_distribution(n)}, reverse=True)


@functools.lru_cache(maxsize=None)
def min_significant_rho(n: int, threshold: Optional[float] = None,
                         exact_max_n: int = 8) -> Optional[Dict]:
    """이 n에서 순열검정 p<threshold 를 만족하는 **최소** 달성 가능 ρ.

    n<=exact_max_n: `achievable_rhos`로 실제 이산 성취 가능 집합을 전수 열거해
    그중 최솟값을 찾는다(정확, exact=True). 예: n=6은 1.000, 0.943, 0.886,
    0.829 … 순서로 내려가며 처음 p<0.05 를 만족하는 값을 고른다 — 요구 ρ가
    이 이산 값들 사이 틈에 떨어지면 그 틈을 넘는 다음 값이 필요하다는 뜻이다.
    n>exact_max_n: 순열 전수 열거가 비현실적이라(n!) `backtest.perm_p_value`
    (몬테카를로, 고정 seed=0)를 이진탐색해 연속 근사를 낸다(exact=False) —
    n이 커질수록 이산 격자가 촘촘해져 근사가 실질적 차이를 만들지 않는다.
    이 함수는 (n, threshold)에 대해 순수하므로 `lru_cache`로 재계산을 막는다
    — k=1/k=2 두 번 호출해도 같은 n은 한 번만 전수열거한다.
    """
    th = backtest.BacktestResult.P_THRESHOLD if threshold is None else threshold
    if n < 3:
        return None
    if n <= exact_max_n:
        for rho in sorted(achievable_rhos(n)):
            p = _exact_p_value(rho, n)
            if p < th:
                return {"min_rho": rho, "p": p, "exact": True}
        return None   # 이 n에서는 어떤 순열로도 영원히 유의해질 수 없다
    lo, hi = 0.0, 1.0
    p_hi = backtest.perm_p_value(hi, n)
    if p_hi is None or p_hi >= th:
        return None
    for _ in range(50):
        mid = (lo + hi) / 2.0
        p = backtest.perm_p_value(mid, n)
        if p is not None and p < th:
            hi = mid
        else:
            lo = mid
    return {"min_rho": hi, "p": backtest.perm_p_value(hi, n), "exact": False}


def nearest_achievable_at_least(n: int, target: float,
                                 exact_max_n: int = 8) -> Optional[float]:
    """이 n에서 `target` 이상인 달성 가능 ρ 중 최솟값. n<=exact_max_n만 정확히
    답한다(그 이상은 None — 이산 격자가 촘촘해 실질적 제약이 아니다)."""
    if n > exact_max_n:
        return None
    candidates = [v for v in achievable_rhos(n) if v >= target - 1e-9]
    return min(candidates) if candidates else None


def c4_requirement(pack: str, model: str = "tier2.gw_physical_kp") -> Dict:
    """C4 `pack`이 통과하려면 새 유의 held-out이 몇 건, ρ가 얼마 필요한가.

    C4는 "유의 held-out들의 **평균** ρ >= RHO_MIN"이다. 현재 유의 held-out의
    합을 고정하고, k건을 새로 추가해 평균을 RHO_MIN 이상으로 만들려면:
        (existing_sum + sum_new) / (n_sig + k) >= RHO_MIN
        ⟺ sum_new >= RHO_MIN*(n_sig + k) - existing_sum
    각 후보는 (a) 구조적 상한(rho_ceiling)이 그 몫에 못 미치거나 (b) 상한 자체가
    영원히 비유의(ceiling_p >= 0.05)면 **원리적으로 불가능**하다.
    """
    ds = dataset_pack_map()
    all_results = compute_all(model)
    pack_results = [r for r in all_results if ds.get(r.dataset) == pack]
    sig_rows = [r for r in pack_results if r.eligible]
    # 후보: 범위 안 + 비캘리브레이션이지만 아직 비유의라 못 세는 것들.
    cand_rows = [r for r in pack_results
                 if not r.eligible and r.exclusion_reason == "비유의"]

    n_sig = len(sig_rows)
    existing_sum = sum(r.actual_rho for r in sig_rows)
    current_mean = existing_sum / n_sig if n_sig else None

    reqs = {}
    for k in (1, 2):
        req_sum = RHO_MIN * (n_sig + k) - existing_sum
        cands = []
        # ⚠ k>1 에서 개별 후보의 상한을 **합** 요구치와 직접 비교하면 안 된다.
        #   Spearman 상한은 1.0 이므로 req_sum>1.0 인 순간 모든 후보가 자동으로
        #   '불가능'으로 찍힌다 — 실제로는 둘이 합쳐 넘기면 되는데도 그렇다.
        #   (2026-09-20 실측 결함: k=2 에서 ihnfeldt2008·jani2025·us8501625b2 가
        #    전부 "상한 1.0000 < 요구치 1.8325" 로 불가능 처리됐는데, 바로 아래
        #    쌍별 절은 같은 셋을 '가능'으로 옳게 판정해 한 출력 안에서 모순됐다.)
        #   올바른 개별 판정: **이 후보가 들어가는 실현가능한 k-조합이 하나라도
        #   있는가** — 즉 자기 상한 + (다른 후보 상한 중 큰 k-1개의 합) >= req_sum.
        _usable = sorted(
            (rr.rho_ceiling for rr in cand_rows
             if rr.ceiling_p is not None
             and rr.ceiling_p < backtest.BacktestResult.P_THRESHOLD),
            reverse=True)
        for r in cand_rows:
            _others = list(_usable)
            if (r.ceiling_p is not None
                    and r.ceiling_p < backtest.BacktestResult.P_THRESHOLD):
                _others.remove(r.rho_ceiling)
            best_partner_sum = sum(_others[:k - 1])
            blocked_ceiling = (r.rho_ceiling + best_partner_sum) < req_sum - 1e-9
            blocked_significance = (r.ceiling_p is None
                                     or r.ceiling_p >= backtest.BacktestResult.P_THRESHOLD)
            min_sig = min_significant_rho(r.n)
            nearest = nearest_achievable_at_least(r.n, req_sum)
            possible = not blocked_ceiling and not blocked_significance
            cands.append({
                "dataset": r.dataset, "n": r.n, "rho_ceiling": r.rho_ceiling,
                "ceiling_p": r.ceiling_p, "actual_rho": r.actual_rho,
                "blocked_ceiling": blocked_ceiling,
                "blocked_significance": blocked_significance,
                "min_significant_rho": min_sig,
                "nearest_achievable_at_req": nearest,
                "possible_in_principle": possible,
            })
        reqs[k] = {"req_sum": req_sum,
                    "req_mean_new": req_sum / k,
                    "candidates": cands}

    return {"pack": pack, "n_sig": n_sig, "existing_sum": existing_sum,
            "current_mean": current_mean, "sig_rows": [r.dataset for r in sig_rows],
            "requirements": reqs}


def _print_c4_requirement(info: Dict) -> None:
    print("=" * 100)
    print(f"C4 도달가능성 산술 — 팩 '{info['pack']}' (판정#93)")
    print("=" * 100)
    print(f"현재 유의 held-out {info['n_sig']}건: "
          + (", ".join(info["sig_rows"]) if info["sig_rows"] else "(없음)"))
    if info["current_mean"] is not None:
        print(f"현재 평균 ρ = {info['current_mean']:.4f}  (RHO_MIN={RHO_MIN})")
    for k, req in info["requirements"].items():
        print("-" * 100)
        if k == 1:
            print(f"[k=1건 추가] 새 유의 held-out의 ρ가 >= {req['req_sum']:.4f} 이어야 한다")
        else:
            print(f"[k={k}건 추가] 새 유의 held-out {k}건의 ρ 합이 "
                  f">= {req['req_sum']:.4f} (평균 {req['req_mean_new']:.4f}) 이어야 한다")
        for c in req["candidates"]:
            verdict = "가능(원리적으로)" if c["possible_in_principle"] else "**불가능**"
            reason = ""
            if c["blocked_significance"]:
                reason = " — 구조적 상한 자체가 영원히 비유의(p={:.4f})".format(
                    c["ceiling_p"]) if c["ceiling_p"] is not None else " — 상한 p 계산 불가"
            elif c["blocked_ceiling"]:
                reason = (f" — 구조적 상한 {c['rho_ceiling']:.4f}"
                          + (" < 요구치" if k == 1 else
                             " + 최선의 파트너 조합으로도 합 요구치 미달"))
            ms = c["min_significant_rho"]
            ms_str = (f"ρ>={ms['min_rho']:.4f}({'정확' if ms['exact'] else '근사'})"
                      if ms else "없음(영원히 비유의)")
            print(f"  · {c['dataset']:44s} n={c['n']:3d}  상한={c['rho_ceiling']:+.4f}  "
                  f"현재ρ={c['actual_rho']:+.4f}  최소유의ρ={ms_str}  → {verdict}{reason}")
            if k == 1 and c["nearest_achievable_at_req"] is not None:
                print(f"      이 n에서 요구치 이상인 최소 달성가능값: "
                      f"{c['nearest_achievable_at_req']:.6f}")
    if len(info["requirements"]) == 2:
        c1 = {c["dataset"]: c for c in info["requirements"][1]["candidates"]}
        c2 = info["requirements"][2]["candidates"]
        feasible_pairs = []
        infeasible_pairs = []
        req_sum2 = info["requirements"][2]["req_sum"]
        names = list(c1.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = c1[names[i]], c1[names[j]]
                max_sum = a["rho_ceiling"] + b["rho_ceiling"]
                both_can_be_sig = not a["blocked_significance"] and not b["blocked_significance"]
                feasible = both_can_be_sig and max_sum >= req_sum2 - 1e-9
                entry = (names[i], names[j], max_sum)
                (feasible_pairs if feasible else infeasible_pairs).append(entry)
        print("-" * 100)
        print(f"[k=2 쌍별 실현가능성] 두 후보 상한의 합이 {req_sum2:.4f} 이상이고 "
              "둘 다 상한이 유의해야 한다:")
        for a, b, s in feasible_pairs:
            print(f"  · 가능: {a} + {b}  (상한 합={s:.4f})")
        for a, b, s in infeasible_pairs:
            print(f"  · 불가능: {a} + {b}  (상한 합={s:.4f} < {req_sum2:.4f} "
                  "또는 한쪽이 영원히 비유의)")


def select_rows(all_results: List[CeilingResult], pack: Optional[str] = None,
                 include_ineligible: bool = False,
                 show_all: bool = False) -> List[CeilingResult]:
    """`main()`의 필터링 로직 — 테스트가 `compute_all()`을 다시 돌리지 않고도
    (물리 시뮬레이션 재실행 없이) 필터 결과만 검사할 수 있도록 분리한 순수
    함수. 두 축은 독립이다: `show_all`(상한 필터, 기존 `--all` 뜻)과
    `include_ineligible`(C4 적격 필터, 판정#93 신규)."""
    results = all_results
    if pack:
        results = [r for r in results if r.pack == pack]
    if not include_ineligible:
        results = [r for r in results if r.eligible]
    if not show_all:
        results = [r for r in results if r.rho_ceiling < 1.0 - 1e-9]
    return results


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true",
                    help="상한<1.0 인 것만이 아니라 상한==1.0 인 것까지 전부 출력"
                         "(기존 뜻 그대로 — C4 적격 필터와는 별개 축)")
    ap.add_argument("--include-ineligible", action="store_true",
                    help="C4가 세지 않는 데이터셋(범위밖/캘리브레이션/비유의)도 함께 출력"
                         "(기본은 C4 적격만)")
    ap.add_argument("--pack", default=None, help="이 팩 이름으로 필터")
    ap.add_argument("--c4-requirement", metavar="PACK", default=None,
                    help="이 팩이 C4를 통과하려면 새 유의 held-out이 몇 건·ρ가 얼마 "
                         "필요한지 산술(판정#93)만 출력하고 종료")
    args = ap.parse_args()

    if args.c4_requirement:
        info = c4_requirement(args.c4_requirement)
        _print_c4_requirement(info)
        return 0

    raw = backtest.run_all()
    all_results = compute_all(raw_results=raw)
    uncomputable = compute_uncomputable(raw_results=raw)
    results = select_rows(all_results, pack=args.pack,
                           include_ineligible=args.include_ineligible,
                           show_all=args.all)

    print("=" * 100)
    print("C4 held-out 구조적 상한(rank ceiling) — 모델이 실제로 보는 고유 입력 그룹 기준")
    print("(backtest.py의 실제 _recipe_from+simulate 경로로 그룹을 짓는다. 근사 아님)")
    print("기본 출력: 상한<1.0 이면서 C4 적격(범위 안·비캘리브레이션·유의)인 것만")
    print("=" * 100)
    if not results:
        print("(조건에 맞는 데이터셋 없음)")
    else:
        for r in sorted(results, key=lambda r: r.rho_ceiling):
            print(format_line(r))
            if r.ceiling_p is not None and r.ceiling_p >= backtest.BacktestResult.P_THRESHOLD:
                print("    · ⚠ 상한 자체가 유의 문턱(p<0.05)을 못 넘는다 — "
                      "어떤 모델로도 이 held-out을 영원히 유의하게 만들 수 없다.")
    _print_filter_breakdown(all_results, uncomputable, results, args.pack)
    return 0


if __name__ == "__main__":
    sys.exit(main())
