#!/usr/bin/env python3
"""완성 격자를 막고 있는 **파라미터 단위** 병목표.

왜 필요한가
────────────
`completion.py check`는 "κ/cu_h2o2_bta: confidence=estimated"까지만 말한다.
그런데 실제로 고쳐야 하는 것은 팩터가 아니라 **팩 YAML의 어느 키**다.
팩터 confidence는 드라이버 파라미터들의 `_worst_conf`이므로, 한 키가
estimated면 그 팩터 칸 전체가 내려앉는다 — 즉 **키 하나를 승격하면 여러 칸이
동시에 올라간다.** 이 도구는 "어느 키를 고치면 몇 칸이 오르는가"를 세어
작업 순서를 정한다.

사용:
    python tools/blockers.py            # 병목 키를 영향 칸수 순으로
    python tools/blockers.py --cells    # 칸별로 어느 키가 막는지
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sim.factors import FACTOR_SPEC                    # noqa: E402
from sim.engine import Recipe, simulate                # noqa: E402
from tools.completion import _packs, CONF_RANK, MIN_CONF, OK_STATUS  # noqa: E402

import yaml  # noqa: E402


def _pack_params(pack: str, _seen: Optional[List[str]] = None) -> Dict[str, dict]:
    """팩 YAML의 파라미터를 **상속 체인 전체**를 따라가며 병합한다.

    ⚠ 팩은 다단계로 상속한다(예: sic_ceria_h2o2 → base: sti_ceria →
    base: oxide_silica → base: base). 예전 구현은 자기 파일 + base.yaml만
    봐서, 중간 팩(sti_ceria/oxide_silica)에만 정의된 abrasive_wt_pct 같은
    키를 못 찾아 항상 unverified로 오판했다(sic_ceria_h2o2·sti_ceria 5칸
    가짜 병목의 원인, 2026-09-13 발견·수정). `sim.params.load_pack`과 같은
    "base" 체인 규칙을 그대로 따른다.
    """
    _seen = _seen or []
    if pack in _seen:
        return {}
    _seen = _seen + [pack]
    p = ROOT / "knowledge" / "params" / f"{pack}.yaml"
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}
    out = dict((d.get("params") or {}))
    parent = d.get("base")
    if parent and parent != pack:
        for k, v in _pack_params(parent, _seen).items():
            out.setdefault(k, v)
    elif pack != "base":
        base = ROOT / "knowledge" / "params" / "base.yaml"
        if base.exists():
            bd = yaml.safe_load(base.read_text(encoding="utf-8")) or {}
            for k, v in (bd.get("params") or {}).items():
                out.setdefault(k, v)
    return {k: v for k, v in out.items() if isinstance(v, dict)}


def analyze() -> Tuple[Dict[str, List[str]], List[dict]]:
    """(병목키 → 그 키가 막는 칸 목록, 칸별 상세)"""
    blockers: Dict[str, List[str]] = defaultdict(list)
    cells: List[dict] = []
    for pack in _packs():
        params = _pack_params(pack)
        rr = simulate(Recipe(pack=pack))
        fs = rr.factors or {}
        for key, f in fs.items():
            ok_status = f.status in OK_STATUS
            conf_ok = CONF_RANK.get(f.confidence or "", 0) >= CONF_RANK[MIN_CONF]
            if ok_status and conf_ok:
                continue
            bad: List[str] = []
            for dk_raw in (f.drivers or {}):
                # ⚠ 일부 팩터(Γ의 cond_sweep_cpm 등)는 진단용 표시를 위해
                # drivers 키에 "(coverage_only,not_multiplied)" 같은 꼬리표를
                # 붙인다 — 실제 params.yaml 키는 꼬리표가 없으므로 그대로 조회하면
                # 항상 매치 실패(unverified 오판)한다. 괄호 앞부분으로 정규화해
                # 실제 파라미터 confidence를 조회한다(2026-09-13 발견·수정).
                dk = dk_raw.split("(")[0]
                meta = params.get(dk) or {}
                c = meta.get("confidence", "unverified")
                if CONF_RANK.get(c, 0) < CONF_RANK[MIN_CONF]:
                    bad.append(f"{dk_raw}({c})")
                    blockers[f"{pack}:{dk}"].append(f"{key}/{pack}")
            cells.append({
                "factor": key, "pack": pack, "status": f.status,
                "confidence": f.confidence, "why": "C1" if not ok_status else "C2",
                "bad_params": bad,
                "drivers": list((f.drivers or {}).keys()),
            })
    return blockers, cells


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", action="store_true")
    a = ap.parse_args()
    blockers, cells = analyze()

    if a.cells:
        print(f"미충족 칸 {len(cells)}개\n")
        for c in sorted(cells, key=lambda x: (x["why"], x["factor"], x["pack"])):
            sym = FACTOR_SPEC[c["factor"]][0]
            print(f"[{c['why']}] {sym} {c['factor']}/{c['pack']}  "
                  f"status={c['status']} conf={c['confidence']}")
            if c["bad_params"]:
                print(f"      막는 키: {', '.join(c['bad_params'])}")
            elif c["why"] == "C1":
                print(f"      드라이버 없음(미모델링) — 유도 필요")
            else:
                print(f"      ⚠ 드라이버는 모두 OK인데 conf 미달 — 코드 기본값이 원인"
                      f" (drivers={c['drivers']})")
        return 0

    print("병목 파라미터 — 승격 시 오르는 칸 수 순\n")
    rank = sorted(blockers.items(), key=lambda kv: -len(kv[1]))
    for k, v in rank:
        print(f"{len(v):2d}칸  {k}")
        print(f"      → {', '.join(sorted(v))}")
    # 키 이름만 모아 같은 키가 여러 팩에서 반복되는지 본다
    bykey: Dict[str, int] = defaultdict(int)
    for k, v in blockers.items():
        bykey[k.split(":", 1)[1]] += len(v)
    print("\n키 이름별 합계(팩 무관) — 하나의 문헌으로 여러 팩을 동시에 올릴 후보\n")
    for k, n in sorted(bykey.items(), key=lambda kv: -kv[1]):
        print(f"{n:2d}칸  {k}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
