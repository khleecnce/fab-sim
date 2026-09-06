#!/usr/bin/env python3
"""조사 범위(SCOPE.yaml) 해석기 — 에이전트별 유효 범위를 계산하고 검색어를 만든다.

왜 (2026-09-05 사용자 지시): 지금까지 에이전트가 무엇을 검색할지 스스로 정했다.
사용자는 CMP 실무자인데 그 판단을 넣을 통로가 없었다. 이 파일이 통로다.

  python3 tools/scope.py --agent film-cu           # 유효 범위 확인
  python3 tools/scope.py --agent film-cu --queries # 검색어 생성
  python3 tools/scope.py --check "논문 제목" --agent film-cu   # 이 자료 써도 되나
  python3 tools/scope.py --list                    # 재정의된 에이전트 목록
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
SCOPE_F = ROOT / "agents" / "SCOPE.yaml"


def _load() -> dict:
    try:
        import yaml
    except ImportError:
        print("PyYAML 필요: pip install pyyaml", file=sys.stderr)
        raise SystemExit(2)
    if not SCOPE_F.exists():
        raise SystemExit(f"{SCOPE_F} 없음")
    return yaml.safe_load(SCOPE_F.read_text()) or {}


def effective(agent: str) -> Dict[str, Any]:
    """defaults + 에이전트 재정의를 병합한 유효 범위."""
    cfg = _load()
    d = cfg.get("defaults", {})
    a = (cfg.get("agents") or {}).get(agent, {}) or {}

    # 소스: defaults 리스트를 dict로 → 에이전트 재정의 덮어쓰기
    sources = {s["id"]: dict(s) for s in d.get("sources", [])}
    for sid, over in (a.get("sources") or {}).items():
        if sid in sources:
            sources[sid].update(over or {})
        else:
            sources[sid] = {"id": sid, "enabled": True, "weight": 0.5,
                            **(over or {})}

    method = {**d.get("method", {}), **(a.get("method") or {})}
    exclude = {**d.get("exclude", {}), **(a.get("exclude") or {})}
    # 키워드 제외는 합집합 (에이전트가 추가만 하고 defaults를 지우지 못하게)
    exclude["keywords"] = list(dict.fromkeys(
        (d.get("exclude", {}).get("keywords") or [])
        + ((a.get("exclude") or {}).get("keywords") or [])))

    return {
        "agent": agent,
        "focus": a.get("focus", "").strip(),
        "sources": sources,
        "enabled_sources": [s for s in sources.values() if s.get("enabled", True)],
        "method": method,
        "exclude": exclude,
        "keywords_include": a.get("keywords_include", []),
        "has_override": bool(a),
    }


def queries(agent: str) -> List[str]:
    """검색어 생성 — 에이전트 키워드 × 활성 소스 유형."""
    e = effective(agent)
    base = e["keywords_include"] or [agent.replace("-", " ") + " CMP"]
    out = []
    for kw in base:
        out.append(kw)
        for s in sorted(e["enabled_sources"], key=lambda x: -x.get("weight", 0))[:3]:
            if s["id"] == "patent":
                out.append(f"{kw} patent")
            elif s["id"] == "thesis":
                out.append(f"{kw} thesis filetype:pdf")
            elif s["id"] == "standard":
                out.append(f"{kw} SEMI standard specification")
    yrs = e["method"].get("prefer_recent_years")
    if yrs:
        out = [q + f" after:{2026 - int(yrs)}" if "after:" not in q else q for q in out]
    return list(dict.fromkeys(out))


def check(title: str, agent: str) -> Dict[str, Any]:
    """이 자료를 써도 되는가. (허용/제외 + 사유)"""
    e = effective(agent)
    t = title.lower()
    reasons = []
    for kw in e["exclude"].get("keywords") or []:
        if kw.lower() in t:
            reasons.append(f"제외 키워드 '{kw}'")
    yr = re.search(r"(19|20)\d{2}", title)
    before = e["exclude"].get("before_year")
    if yr and before and int(yr.group()) < int(before):
        classics = e["method"].get("classic_exceptions") or []
        if not any(c.split()[0].lower() in t for c in classics):
            reasons.append(f"{yr.group()} < before_year {before} (고전 예외 아님)")
    return {"allowed": not reasons, "reasons": reasons, "agent": agent}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent")
    ap.add_argument("--queries", action="store_true")
    ap.add_argument("--check")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.list:
        cfg = _load()
        for name, spec in (cfg.get("agents") or {}).items():
            print(f"{name:24} {(spec.get('focus') or '').strip().splitlines()[0][:70]}")
        return 0

    if not a.agent:
        ap.error("--agent 필요")

    if a.check:
        r = check(a.check, a.agent)
        print(json.dumps(r, ensure_ascii=False) if a.json else
              ("✓ 허용" if r["allowed"] else "✗ 제외 — " + "; ".join(r["reasons"])))
        return 0 if r["allowed"] else 1

    if a.queries:
        for q in queries(a.agent):
            print(q)
        return 0

    e = effective(a.agent)
    if a.json:
        print(json.dumps(e, ensure_ascii=False, indent=2))
        return 0
    print(f"■ 조사 범위 — {a.agent}"
          + ("" if e["has_override"] else "  (재정의 없음 · defaults 사용)"))
    if e["focus"]:
        print(f"\n  집중:\n    {e['focus']}")
    print("\n  허용 소스 (가중치 순)")
    for s in sorted(e["enabled_sources"], key=lambda x: -x.get("weight", 0)):
        print(f"    {s.get('weight', 0):.1f}  {s.get('label', s['id'])}")
    off = [s for s in e["sources"].values() if not s.get("enabled", True)]
    if off:
        print("  금지 소스: " + ", ".join(s.get("label", s["id"]) for s in off))
    m = e["method"]
    print(f"\n  방법: 단원당 최대 {m.get('max_sources_per_unit')}건 · "
          f"1차 최소 {m.get('min_primary_per_unit')}건 · "
          f"최근 {m.get('prefer_recent_years')}년 우선")
    print(f"        DOI검증 {m.get('require_doi_check')} · "
          f"verify블록 {m.get('require_verify_block')} · "
          f"유료폴백 {m.get('paywall_fallback')}")
    x = e["exclude"]
    if x.get("keywords"):
        print(f"\n  제외 키워드: {', '.join(x['keywords'])}")
    if x.get("before_year"):
        print(f"  {x['before_year']}년 이전 제외 (고전 예외: "
              f"{', '.join(m.get('classic_exceptions', [])[:3])}…)")
    if e["keywords_include"]:
        print("\n  검색어 씨앗")
        for k in e["keywords_include"]:
            print(f"    · {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
