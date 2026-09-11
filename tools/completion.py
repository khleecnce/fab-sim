#!/usr/bin/env python3
"""모델링 완성 판정 + 근거 보고서 — COMPLETION.md의 C1~C5·C8을 기계로 판정한다.

사용자 지시 (2026-09-10):
  "모델링 완성을 목표로해" / "완성된 후에는 오류가 없도록 루프를 돌려서 검증해. 그리고 각 모델이
   정의 된 근거, 파라미터가 도출된 근거를 나중에 나에게 보고해"

  completion.py check    — 팩터×팩 격자 판정. exit 0 = 완성, 1 = 미완(무엇이 남았는지 출력).
                            완성 후에는 매 회차 이 명령이 게이트다(한 칸이라도 되돌아가면 exit 1).
  completion.py report   — validation/MODEL-BASIS.md 생성: 팩터별 모델 정의 근거(문헌·관계식) +
                            파라미터 도출 근거(팩 YAML의 source/note/confidence 그대로).
                            손으로 쓰지 않는다 — 코드와 팩이 말하는 것만 적는다.
  completion.py gaps     — 미완 칸을 갭 랭커 형식으로 (accuracy_gaps.py가 흡수)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "validation"))

CONF_RANK = {"verified": 3, "literature": 2, "estimated": 1, "unverified": 0, "unknown": 0, "": 0}
OK_STATUS = {"modeled", "partial"}
MIN_CONF = "literature"
RHO_MIN = 0.85


def _packs() -> List[str]:
    from sim.params import available_packs
    return [p for p in available_packs() if p != "base"]


def grid() -> Dict[str, Dict[str, Any]]:
    """{factor: {pack: Factor.to_dict()}}"""
    from sim.engine import Recipe, simulate
    from sim.factors import FACTOR_SPEC
    out: Dict[str, Dict[str, Any]] = {k: {} for k in FACTOR_SPEC}
    for p in _packs():
        try:
            r = simulate(Recipe(pack=p))
            for k in FACTOR_SPEC:
                f = (r.factors or {}).get(k)
                out[k][p] = f.to_dict() if f else {"status": "missing", "confidence": "", "sources": [], "notes": []}
        except Exception as e:
            for k in FACTOR_SPEC:
                out[k][p] = {"status": "error", "confidence": "", "sources": [], "notes": [f"{type(e).__name__}: {e}"]}
    return out


def sensitivity_alive() -> Dict[str, bool]:
    """C3: MRR 결합 팩터가 반응하는가 — 기준 팩에서 드라이버를 흔들어 MRR 변화 확인."""
    import numpy as np
    from sim.engine import Recipe, simulate
    from sim.factors import MRR_COUPLED
    probes = {"kappa": ("abrasive_wt_pct", 1.3), "chi": ("slurry_ph", None), "psi": ("inhibitor_mM", 2.0),
              "tau": ("groove_width_um", 1.5)}
    alive = {}
    for k in sorted(MRR_COUPLED):
        key, mult = probes.get(k, (None, None))
        ok = False
        for p in _packs():
            try:
                base = float(np.mean(simulate(Recipe(pack=p)).mrr_nm_per_min))
                from sim.params import load_pack
                pk = load_pack(p)
                if key is None or not pk.has(key):
                    continue
                v = float(pk.get(key))
                nv = (v + 1.0) if mult is None else v * mult
                alt = float(np.mean(simulate(Recipe(pack=p, pack_overrides={key: nv})).mrr_nm_per_min))
                if abs(alt - base) / max(base, 1e-9) > 1e-4:
                    ok = True
                    break
            except Exception:
                continue
        alive[k] = ok
    return alive


def heldout_by_pack() -> Dict[str, Dict[str, Any]]:
    """C4: 팩별 유의 held-out 수와 평균 ρ."""
    import backtest
    res = backtest.run_all()
    ds = {}
    for f in (ROOT / "validation" / "datasets").glob("*.yaml"):
        if f.name.startswith("_"):
            continue
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        ds[f.stem] = d.get("pack")
    out: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"n_sig": 0, "rhos": [], "n_total": 0})
    for r in res:
        p = ds.get(r.dataset)
        if not p:
            continue
        out[p]["n_total"] += 1
        if r.in_scope and not r.used_for_calibration and r.significant:
            out[p]["n_sig"] += 1
            out[p]["rhos"].append(r.spearman)
    for p in _packs():
        o = out[p]
        o["mean_rho"] = round(sum(o["rhos"]) / len(o["rhos"]), 4) if o["rhos"] else None
    return dict(out)


def notes_with_verify(factor: str, g: Optional[Dict] = None) -> List[str]:
    """C5: 이 팩터의 Factor.sources 가 가리키는 노트 중 verify 블록(```python + assert)이 있는 것.
    코드가 실제로 근거로 대는 노트만 센다 — 기호 태그 검색은 노트가 태그를 안 달아 전부 놓쳤다.

    ⚠ sources 문자열은 사람이 읽을 형태로 적혀 있어 그대로 경로로 쓸 수 없다:
      - "knowledge/....md §5"  처럼 절 번호가 붙는다
      - "Jeong et al. 2024, Materials 17(8) ..." 처럼 경로가 아닌 서지인용도 섞인다
    절 번호를 떼고, 경로처럼 생긴 것만 파일로 해석한다. 이 정규화가 없으면 verify 블록이
    실제로 있는 노트를 '없음'으로 오판한다(2026-09-11 C5 5축 전부가 이 버그였다).
    """
    srcs = set()
    if g:
        for p, c in g.get(factor, {}).items():
            for s in (c.get("sources") or []):
                srcs.add(s)
    hits = []
    for s in srcs:
        # "path.md §5" → "path.md"  (절 번호·괄호주석 제거)
        cand = re.split(r"\s+§", s)[0].strip()
        if ".md" in cand:
            cand = cand[: cand.index(".md") + 3]
        if not cand.endswith(".md"):
            continue        # 서지인용 문자열 — 파일이 아니다
        f = ROOT / cand if not cand.startswith("/") else Path(cand)
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        if "```python" in t and ("assert" in t or "verify" in t.lower()):
            hits.append(cand)
    return sorted(set(hits))


def check(verbose: bool = True) -> Dict[str, Any]:
    from sim.factors import FACTOR_SPEC, MRR_COUPLED
    g = grid()
    packs = _packs()
    fails: List[str] = []
    # C1/C2
    for k in FACTOR_SPEC:
        for p in packs:
            c = g[k][p]
            if c["status"] not in OK_STATUS:
                fails.append(f"C1 {FACTOR_SPEC[k][0]} {k}/{p}: status={c['status']}")
            elif CONF_RANK.get(c.get("confidence", ""), 0) < CONF_RANK[MIN_CONF]:
                fails.append(f"C2 {FACTOR_SPEC[k][0]} {k}/{p}: confidence={c.get('confidence')}")
    # C3
    alive = sensitivity_alive()
    for k, ok in alive.items():
        if not ok:
            fails.append(f"C3 {FACTOR_SPEC[k][0]} {k}: MRR 결합인데 어떤 팩에서도 반응 없음")
    # C4
    ho = heldout_by_pack()
    for p in packs:
        o = ho.get(p, {"n_sig": 0, "mean_rho": None})
        if o["n_sig"] < 1:
            fails.append(f"C4 {p}: 유의 held-out 0건")
        elif o["mean_rho"] is not None and o["mean_rho"] < RHO_MIN:
            fails.append(f"C4 {p}: 유의 평균 ρ {o['mean_rho']} < {RHO_MIN}")
    # C5
    c5 = {}
    for k in FACTOR_SPEC:
        c5[k] = notes_with_verify(k, g)
        if not c5[k]:
            fails.append(f"C5 {FACTOR_SPEC[k][0]} {k}: verify 블록 있는 근거 노트 없음")
    total_cells = len(FACTOR_SPEC) * len(packs)
    done_cells = sum(1 for k in FACTOR_SPEC for p in packs
                     if g[k][p]["status"] in OK_STATUS and CONF_RANK.get(g[k][p].get("confidence", ""), 0) >= CONF_RANK[MIN_CONF])
    result = {"ts": time.time(), "complete": not fails, "cells_done": done_cells, "cells_total": total_cells,
              "fails": fails, "sensitivity": alive, "heldout": ho, "c5_notes": c5}
    if verbose:
        print(f"완성 판정: {'✅ 완성' if not fails else '❌ 미완'}  — 격자 {done_cells}/{total_cells}칸 충족")
        by = defaultdict(list)
        for f in fails:
            by[f[:2]].append(f)
        for c in ("C1", "C2", "C3", "C4", "C5"):
            if by[c]:
                print(f"  {c} ({len(by[c])}):")
                for f in by[c][:12]:
                    print("    ", f[3:])
                if len(by[c]) > 12:
                    print(f"     … +{len(by[c]) - 12}")
    return result


def _param_basis(pack: str) -> List[Dict[str, Any]]:
    p = ROOT / "knowledge" / "params" / f"{pack}.yaml"
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    rows = []
    for k, v in (d.get("params") or {}).items():
        if not isinstance(v, dict):
            continue
        rows.append({"key": k, "value": v.get("value"), "unit": v.get("unit", ""), "source": v.get("source", ""),
                     "confidence": v.get("confidence", ""), "note": (v.get("note") or "").strip()})
    return rows


def report() -> Path:
    """validation/MODEL-BASIS.md — 코드·팩·노트가 말하는 근거만."""
    from sim.factors import FACTOR_SPEC, MRR_COUPLED
    import inspect
    import sim.factors as F
    g = grid()
    res = check(verbose=False)
    packs = _packs()
    L = [f"# FabSim 모델 근거 보고서 (MODEL-BASIS)\n\n생성: {time.strftime('%Y-%m-%d %H:%M')} · 커밋 기준 자동 생성 — 손으로 고치지 말고 코드/팩/노트를 고쳐라.\n",
         f"완성 판정: **{'완성' if res['complete'] else '미완'}** ({res['cells_done']}/{res['cells_total']}칸). "
         f"미충족 {len(res['fails'])}건은 끝에.\n",
         "## 0. 결합식\n", "```\nMRR(r) = Kp · P(r) · V(r) · κ · χ · ψ · τ        (기준 조건에서 κ=χ=ψ=τ=1)\n"
         "Λ, Π 는 P·V 자체의 분해(장비축), Θ·Γ·Δ·S 는 출력·진단 축 — MRR에 곱하지 않는다.\n```\n",
         "Kp는 팩마다 문헌 한 점에서 역산한 값이라 절대값은 그 조성·조건에 묶인다. 팩터는 전부 **기준 대비 배수**이므로 "
         "Kp와 이중 계상되지 않는다(`tests/test_factors.py`가 기준 1.0 계약을 강제).\n"]
    for k, (sym, name, axis, parts) in FACTOR_SPEC.items():
        fn = getattr(F, f"_f_{k}", None)
        doc = inspect.getdoc(fn) or "(docstring 없음)"
        L.append(f"\n## {sym} {name} (`{k}`) — 축: {axis} · 파트: {', '.join(parts)} · MRR 결합: {'예' if k in MRR_COUPLED else '아니오(진단)'}\n")
        L.append("### 모델 정의 근거 (코드 docstring 그대로)\n")
        L.append("```\n" + doc.strip() + "\n```\n")
        L.append("### 팩별 상태\n\n| 팩 | status | confidence | 항(terms) | 드라이버 | 출처 |\n|---|---|---|---|---|---|")
        for p in packs:
            c = g[k][p]
            terms = ", ".join(f"{a}×{b:.3f}" for a, b in (c.get("terms") or {}).items()) or "—"
            drv = ", ".join((c.get("drivers") or {}).keys()) or "—"
            src = "; ".join(s.split("/")[-1][:40] for s in (c.get("sources") or [])) or "—"
            L.append(f"| {p} | {c['status']} | {c.get('confidence','')} | {terms} | {drv} | {src} |")
        notes = set()
        for p in packs:
            for n in (g[k][p].get("notes") or []):
                notes.add(n)
        if notes:
            L.append("\n엔진이 스스로 보고하는 한계:\n")
            for n in sorted(notes)[:8]:
                L.append(f"- {n}")
        c5 = res["c5_notes"].get(k) or []
        L.append(f"\n근거 노트(verify 블록 보유): {', '.join(f'`{x}`' for x in c5) if c5 else '**없음** (C5 미충족)'}\n")
    L.append("\n## 파라미터 도출 근거 (팩 YAML의 source/note/confidence 그대로)\n")
    for p in packs:
        L.append(f"\n### 팩 `{p}`\n\n| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |\n|---|---|---|---|---|---|")
        for r in _param_basis(p):
            note = r["note"].replace("\n", " ").replace("|", "/")[:160]
            src = str(r["source"]).replace("|", "/")[:60]
            L.append(f"| {r['key']} | {r['value']} | {r['unit']} | {r['confidence']} | {src} | {note} |")
    L.append("\n## 검증 (특허·논문 held-out)\n\n| 팩 | 데이터셋 | 유의 | 유의 평균 ρ |\n|---|---|---|---|")
    for p in packs:
        o = res["heldout"].get(p, {})
        L.append(f"| {p} | {o.get('n_total', 0)} | {o.get('n_sig', 0)} | {o.get('mean_rho', '—')} |")
    L.append("\n## 미충족 항목\n")
    for f in res["fails"]:
        L.append(f"- {f}")
    if not res["fails"]:
        L.append("- 없음 — 완성 기준 전부 충족")
    out = ROOT / "validation" / "MODEL-BASIS.md"
    out.write_text("\n".join(L), encoding="utf-8")
    return out


def gaps() -> List[Dict[str, Any]]:
    res = check(verbose=False)
    out = []
    for f in res["fails"]:
        c = f[:2]
        out.append({"kind": f"COMPLETION-{c}", "score": {"C1": 90, "C3": 85, "C4": 88, "C2": 45, "C5": 40}.get(c, 30),
                    "what": f, "action": {"C1": "문헌 정량 관계 확보 → 팩 파라미터 → factors.py 항 → 기준 1.0 테스트",
                                          "C2": "파라미터별 1차 출처(DOI/특허) 확보 → 값 대조 → confidence 승격",
                                          "C3": "결합 통로가 끊겼다 — MRR_COUPLED와 항 결합 확인",
                                          "C4": "특허 실시예/논문 SI에서 n≥4 DOE 데이터셋 추가",
                                          "C5": "근거 노트에 ```python verify 블록(문헌값 재현 assert) 추가"}.get(c, ""),
                    "why": "COMPLETION.md 기준"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check"); sub.add_parser("report"); sub.add_parser("gaps")
    a = ap.parse_args()
    if a.cmd == "check":
        r = check()
        (ROOT / "validation" / "completion_last.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0 if r["complete"] else 1
    if a.cmd == "report":
        p = report(); print(f"→ {p}")
        return 0
    if a.cmd == "gaps":
        print(json.dumps(gaps(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
