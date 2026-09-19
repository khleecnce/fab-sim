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
from tools.completion import (                          # noqa: E402
    _packs, CONF_RANK, MIN_CONF, OK_STATUS, c2_closures,
)

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


def analyze(include_closed: bool = False) -> Tuple[Dict[str, List[str]], List[dict]]:
    """(병목키 → 그 키가 막는 칸 목록, 칸별 상세)

    ⚠ 2026-09-20(판정#79): **종결된 칸은 기본으로 제외한다.**
    `validation/C2-CLOSURES.yaml`에 유효 등록된 칸은 3회차 소진으로 영구 종결된
    것이라 "고치면 오른다"가 성립하지 않는다 — 그런데 이 도구는 그걸 모르고
    계속 1위로 올렸고, 실제로 Δ/cu_alkaline_benzenesulfonic 이 종결 직후에도
    1위로 남아 있었다. 종결 칸을 순위에 두면 다음 회차가 **4회차를 돌게 된다**
    (EVIDENCE-RULES 3회차 규칙 위반을 도구가 유도하는 꼴). --include-closed 로
    감사 목적의 전체 보기는 여전히 가능하다.
    """
    closures = c2_closures()
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
            cl = closures.get((key, pack))
            closed = bool(cl and cl.get("valid"))
            if closed and not include_closed:
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
            # 드라이버가 전부 OK 인데 팩터 등급이 미달이면 원인은 다른 곳이다.
            # ⚠ 이걸 "코드 기본값"으로 단정하면 안 된다 — 팩터 등급은 드라이버
            #   외에 **형상 파라미터**(지수·정점·이득·Langmuir 상수)도 _pack_conf
            #   로 함께 읽기 때문이고, 그쪽이 원인인 경우가 실제로 있었다
            #   (χ/sic_ceria_h2o2: 드라이버 3개는 measured 인데 산화제 Langmuir
            #   상수가 estimated, 부트스트랩 CI 0.32~2.70). 단정하면 다음 회차가
            #   코드를 뒤지다 시간을 버린다.
            # 그래서 팩터 등급과 **같은 등급인 비드라이버 팩 키**를 후보로 낸다 —
            # 그 중 하나가 약한 고리다. 후보가 0개면 그때는 코드 하한이다.
            weak_nondriver: List[str] = []
            if not bad:
                dnames = {d.split("(")[0] for d in (f.drivers or {})}
                for pk_key, meta in params.items():
                    if pk_key in dnames or not isinstance(meta, dict):
                        continue
                    c = meta.get("confidence")
                    if c == f.confidence:
                        weak_nondriver.append(f"{pk_key}({c})")
            cells.append({
                "closed": closed,
                "closure_judgments": (cl or {}).get("judgments", []),
                "factor": key, "pack": pack, "status": f.status,
                "confidence": f.confidence, "why": "C1" if not ok_status else "C2",
                "bad_params": bad,
                "weak_nondriver": sorted(weak_nondriver),
                "drivers": list((f.drivers or {}).keys()),
            })
    return blockers, cells


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", action="store_true")
    ap.add_argument("--include-closed", action="store_true",
                    help="C2-CLOSURES.yaml 로 영구 종결된 칸도 순위에 포함(감사용). "
                         "기본은 제외 — 종결 칸을 병목으로 내면 다음 회차가 4회차를 돈다.")
    a = ap.parse_args()
    blockers, cells = analyze(include_closed=a.include_closed)

    if a.cells:
        print(f"미충족 칸 {len(cells)}개\n")
        for c in sorted(cells, key=lambda x: (x["why"], x["factor"], x["pack"])):
            sym = FACTOR_SPEC[c["factor"]][0]
            mark = ""
            if c.get("closed"):
                mark = "  [종결 " + "·".join(c.get("closure_judgments") or []) + "]"
            print(f"[{c['why']}] {sym} {c['factor']}/{c['pack']}  "
                  f"status={c['status']} conf={c['confidence']}{mark}")
            if c["bad_params"]:
                print(f"      막는 키: {', '.join(c['bad_params'])}")
            elif c["why"] == "C1":
                print(f"      드라이버 없음(미모델링) — 유도 필요")
            elif c.get("weak_nondriver"):
                w = c["weak_nondriver"]
                print(f"      드라이버는 모두 OK — 약한 고리는 **형상 파라미터** 쪽이다."
                      f" 같은 등급({c['confidence']})인 비드라이버 팩 키 {len(w)}개:")
                print(f"        {', '.join(w[:8])}"
                      + (f" … 외 {len(w)-8}개" if len(w) > 8 else ""))
                print(f"      → 이 중 이 팩터가 실제로 읽는 키를 승격하라"
                      f" (drivers={c['drivers']})")
            else:
                print(f"      ⚠ 드라이버 OK · 같은 등급인 팩 키도 없음 →"
                      f" **코드 하한이 원인**. 근거 주석을 확인하라"
                      f" (tools/confidence_cap_audit.py, drivers={c['drivers']})")
        return 0

    n_closed = sum(1 for c in cells if c.get("closed"))
    if not a.include_closed:
        print("병목 파라미터 — 승격 시 오르는 칸 수 순"
              "  (영구 종결 칸 제외, 전체는 --include-closed)\n")
    else:
        print(f"병목 파라미터 — 승격 시 오르는 칸 수 순"
              f"  (⚠ 종결 {n_closed}칸 포함 — 감사용, 작업 대상 아님)\n")
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
    # ⚠ 2026-09-20: 드라이버가 전부 OK 인 칸은 위 표에 **한 줄도 안 나온다**
    #   (blockers dict 는 bad driver 에서만 채워진다). 종결 칸 제외를 켜고 나니
    #   표가 통째로 비어 "남은 병목 없음"으로 오독될 여지가 생겼다 — 실제로는
    #   형상 파라미터가 막는 칸이 남아 있다. 여기서 그 칸들을 명시한다.
    orphan = [c for c in cells if not c["bad_params"] and c["why"] == "C2"]
    if orphan:
        print(f"\n⚠ 위 표에 안 잡히는 미충족 칸 {len(orphan)}개 — 드라이버는 전부 OK 이고")
        print("   **형상 파라미터(지수·정점·이득·Langmuir 상수)** 가 막는 칸이다.")
        print("   자세히: python tools/blockers.py --cells\n")
        for c in sorted(orphan, key=lambda x: (x["factor"], x["pack"])):
            sym = FACTOR_SPEC[c["factor"]][0]
            print(f"      {sym} {c['factor']}/{c['pack']}  conf={c['confidence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
