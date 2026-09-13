"""여러 표를 예시번호로 이어 "조성 → 제거율" 한 줄을 만든다.

왜 별도 단계인가
────────────────
특허는 조성과 결과를 **다른 표**에 싣는다.

    TABLE 1  Slurry#  Abrasive(wt%)  H2O2(wt%)  pH      ← 조성
    TABLE 4  Slurry#  Co RR(Å/min)   TiN RR(Å/min)      ← 결과

표 하나만 보면 "결과표에 변하는 조성 축이 없다"며 버리게 된다(실제로
34개 결과표 중 20개가 그렇게 버려졌다). 예시번호(Slurry#, Ex#, CS-1…)가
외래키이므로 그것으로 join 해야 비로소 쓸 수 있는 한 줄이 나온다.

무엇을 신뢰하는가
────────────────
· 열 이름이 복원된(confident) 표만 쓴다.
· 라벨이 **겹치는 표끼리만** 잇는다. 겹치지 않으면 다른 실험이다.
· 같은 역할의 열이 여러 표에 있으면 **더 구체적인 쪽**(조성표)을 쓴다.

⚠ 라벨이 겹치지 않으면 억지로 순서대로 맞추지 않는다.
  표 순서가 같으리라는 보장이 없고, 어긋나면 조용히 틀린 데이터가 된다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from patent_tables2 import Table, parse_tables

__all__ = ["JoinedSeries", "join_tables", "series_from_patent"]

AXIS_ROLES = ("wt_pct", "ppm", "ph", "size_nm", "pressure", "rpm", "flow")

# 물리적으로 가능한 범위 — 열 정렬이 어긋났는지 자동 판정한다.
# 값이 이 범위를 벗어나면 그 열은 이름과 다른 것을 담고 있다는 뜻이므로
# **버린다**. (실측: pH 열에 3333·1667 이 들어온 사례가 있었다.
#  그대로 채택했다면 검증 데이터가 조용히 오염됐을 것이다.)
PLAUSIBLE: Dict[str, Tuple[float, float]] = {
    "ph":       (0.0, 14.0),
    "wt_pct":   (0.0, 100.0),
    "ppm":      (0.0, 1_000_000.0),
    "size_nm":  (0.1, 100_000.0),
    "pressure": (0.0, 1000.0),      # psi 또는 kPa
    "rpm":      (0.0, 2000.0),
    "flow":     (0.0, 10_000.0),
    "rate":     (0.0, 1_000_000.0),  # Å/min 또는 nm/min
}


def _plausible(role: str, vals: List[float]) -> bool:
    """이 열의 값들이 그 역할에 물리적으로 맞는가."""
    lo, hi = PLAUSIBLE.get(role, (float("-inf"), float("inf")))
    seen = [v for v in vals if not math.isnan(v)]
    if not seen:
        return False
    return all(lo <= v <= hi for v in seen)


@dataclass
class JoinedSeries:
    """한 특허에서 뽑은 '조성 → 제거율' 계열."""
    patent: str
    labels: List[str]
    axes: Dict[str, List[float]]          # 축 이름 → 라벨 순 값
    rates: Dict[str, List[float]]         # 제거율 열 이름 → 라벨 순 값
    varying: List[str]                    # 실제로 변하는 축
    source_tables: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.labels)


def _col_values(t: Table, ci: int) -> Dict[str, float]:
    return {lab: vals[ci] for lab, vals in t.rows.items() if ci < len(vals)}


def _axis_name(t: Table, ci: int) -> str:
    """열 이름 + 역할로 축 이름을 만든다 (물질명은 그대로 둔다 — 출처 표기용)."""
    raw = t.columns[ci] if ci < len(t.columns) else f"col{ci}"
    return f"{raw.strip()}|{t.roles[ci]}"


def join_tables(patent: str, tables: List[Table]) -> Optional[JoinedSeries]:
    conf = [t for t in tables if t.confident and t.rows]
    if not conf:
        return None

    rate_tabs = [t for t in conf if "rate" in t.roles]
    if not rate_tabs:
        return None

    # 가장 많은 행을 가진 결과표를 기준으로 삼는다
    base = max(rate_tabs, key=lambda t: len(t.rows))
    labels = sorted(base.rows)

    rates: Dict[str, List[float]] = {}
    for ci, role in enumerate(base.roles):
        if role != "rate":
            continue
        col = _col_values(base, ci)
        rates[_axis_name(base, ci)] = [col.get(l, math.nan) for l in labels]

    axes: Dict[str, List[float]] = {}
    used: List[str] = [f"{base.name}(결과)"]

    # 같은 표 안의 축
    for ci, role in enumerate(base.roles):
        if role in AXIS_ROLES:
            col = _col_values(base, ci)
            vals = [col.get(l, math.nan) for l in labels]
            if not _plausible(role, vals):
                continue          # 이름과 값이 안 맞는 열 — 버린다
            axes[_axis_name(base, ci)] = vals

    # 다른 표에서 축을 가져온다 — 라벨이 겹칠 때만
    for t in conf:
        if t is base:
            continue
        overlap = set(t.rows) & set(labels)
        if len(overlap) < max(2, len(labels) // 2):
            continue
        got = False
        for ci, role in enumerate(t.roles):
            if role not in AXIS_ROLES:
                continue
            col = _col_values(t, ci)
            name = _axis_name(t, ci)
            if name in axes:
                continue
            vals = [col.get(l, math.nan) for l in labels]
            if not _plausible(role, vals):
                continue
            axes[name] = vals
            got = True
        if got:
            used.append(f"{t.name}(조성)")

    if not axes:
        return None

    varying = []
    for name, vals in axes.items():
        seen = {v for v in vals if not math.isnan(v)}
        if len(seen) > 1:
            varying.append(name)

    return JoinedSeries(patent=patent, labels=labels, axes=axes,
                        rates=rates, varying=varying, source_tables=used)


def series_from_patent(patent: str, fulltext: str) -> Optional[JoinedSeries]:
    return join_tables(patent, parse_tables(fulltext))
