#!/usr/bin/env python3
"""구성요소 스키마 로더·검증기 — knowledge/components/*.yaml

  python3 tools/components.py --list                 계열별 요약
  python3 tools/components.py --show slurry          그룹·필드 전체
  python3 tools/components.py --check                스키마 유효성 (CI)
  python3 tools/components.py --gaps                 미연결(not_wired) 항목만
  python3 tools/components.py --coverage             연결률 통계
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "knowledge" / "components"

VALID_STATUS = {"wired", "partial", "not_wired"}
VALID_ORIGIN = {"user", "researched"}
VALID_CONF = {"verified", "literature", "estimated", "unverified"}


def load_all() -> Dict[str, dict]:
    import yaml
    out = {}
    for f in sorted(DIR.glob("*.yaml")):
        d = yaml.safe_load(f.read_text()) or {}
        d["_file"] = str(f.relative_to(ROOT))
        out[d.get("component", f.stem)] = d
    return out


def fields_of(spec: dict) -> Iterator[Tuple[dict, dict]]:
    for g in spec.get("groups", []):
        for fl in g.get("fields", []):
            yield g, fl


def validate(spec: dict) -> List[str]:
    bad = []
    name = spec.get("component", "?")
    if not spec.get("owner"):
        bad.append(f"{name}: owner 없음")
    for g, fl in fields_of(spec):
        p = f"{name}.{g.get('id')}.{fl.get('key')}"
        if fl.get("status") not in VALID_STATUS:
            bad.append(f"{p}: status='{fl.get('status')}' 잘못됨")
        if fl.get("origin") not in VALID_ORIGIN:
            bad.append(f"{p}: origin='{fl.get('origin')}' 잘못됨")
        if fl.get("confidence") and fl["confidence"] not in VALID_CONF:
            bad.append(f"{p}: confidence='{fl['confidence']}' 잘못됨")
        # 조사로 추가한 항목은 근거가 있어야 한다 — 지어내기 방지
        if fl.get("origin") == "researched" and not (fl.get("source") or fl.get("note")):
            bad.append(f"{p}: origin=researched인데 source/note 없음 (근거 필수)")
        # wired인데 maps_to가 없으면 거짓말
        if fl.get("status") == "wired" and not fl.get("maps_to"):
            bad.append(f"{p}: status=wired인데 maps_to 없음")
        # maps_to가 실제 팩 키인지
        if fl.get("maps_to"):
            try:
                sys.path.insert(0, str(ROOT))
                from sim.params import load_pack, available_packs
                keys = set()
                for pk in available_packs():
                    keys |= set(load_pack(pk).params)
                if fl["maps_to"] not in keys:
                    bad.append(f"{p}: maps_to='{fl['maps_to']}' 가 어떤 팩에도 없음")
            except Exception:
                pass
    return bad


def stats(spec: dict) -> dict:
    s = {"wired": 0, "partial": 0, "not_wired": 0, "user": 0, "researched": 0}
    for _, fl in fields_of(spec):
        s[fl.get("status", "not_wired")] = s.get(fl.get("status", "not_wired"), 0) + 1
        s[fl.get("origin", "researched")] = s.get(fl.get("origin", "researched"), 0) + 1
    s["total"] = s["wired"] + s["partial"] + s["not_wired"]
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--show")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--gaps", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    specs = load_all()

    if not specs:
        print(f"{DIR} 에 스키마가 없다")
        return 1

    if a.check:
        bad = []
        for spec in specs.values():
            bad += validate(spec)
        for b in bad:
            print("✗", b)
        print(f"\n{len(specs)}개 계열 · 오류 {len(bad)}건")
        return 1 if bad else 0

    if a.list or a.coverage:
        tot = {"wired": 0, "partial": 0, "not_wired": 0, "user": 0, "researched": 0}
        print(f"{'계열':<14}{'담당':<20}{'그룹':>4}{'필드':>5}{'연결':>6}{'부분':>5}{'미연결':>7}")
        for name, spec in specs.items():
            s = stats(spec)
            for k in tot:
                tot[k] += s.get(k, 0)
            print(f"{name:<14}{spec.get('owner','?'):<20}"
                  f"{len(spec.get('groups',[])):>4}{s['total']:>5}"
                  f"{s['wired']:>6}{s['partial']:>5}{s['not_wired']:>7}")
        t = tot["wired"] + tot["partial"] + tot["not_wired"]
        print(f"\n합계 {t}개 필드 · 연결 {tot['wired']} ({tot['wired']/t*100:.0f}%) · "
              f"부분 {tot['partial']} · 미연결 {tot['not_wired']}")
        print(f"출처: 사용자 지시 {tot['user']} · 조사 추가 {tot['researched']}")
        return 0

    if a.gaps:
        for name, spec in specs.items():
            rows = [(g, fl) for g, fl in fields_of(spec)
                    if fl.get("status") == "not_wired"]
            if not rows:
                continue
            print(f"\n■ {name} — 미연결 {len(rows)}건 (담당 {spec.get('owner')})")
            for g, fl in rows:
                own = g.get("owner", spec.get("owner"))
                print(f"  [{own:<18}] {g['id']}.{fl['key']:<24} {fl.get('label','')}")
        return 0

    if a.show:
        spec = specs.get(a.show)
        if not spec:
            print(f"'{a.show}' 없음. 가능: {list(specs)}")
            return 1
        if a.json:
            print(json.dumps(spec, ensure_ascii=False, indent=2))
            return 0
        print(f"■ {spec['component']} — {spec.get('description','')}")
        print(f"  담당: {spec.get('owner')}  ·  {spec['_file']}\n")
        mark = {"wired": "●", "partial": "◐", "not_wired": "○"}
        for g in spec.get("groups", []):
            tag = "사용자" if g.get("origin") == "user" else "조사"
            print(f"  ▸ {g['label']}  [{tag}] 담당 {g.get('owner', spec.get('owner'))}")
            if g.get("why"):
                print(f"    {g['why'].strip().splitlines()[0]}")
            for fl in g.get("fields", []):
                m = mark.get(fl.get("status"), "?")
                u = f" [{fl['unit']}]" if fl.get("unit") else ""
                mp = f" → {fl['maps_to']}" if fl.get("maps_to") else ""
                print(f"      {m} {fl['key']:<26}{fl.get('label','')}{u}{mp}")
            print()
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
