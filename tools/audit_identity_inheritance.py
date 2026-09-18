# -*- coding: utf-8 -*-
"""정체성 상속 감사 — 남의 재료 계수를 물려받고 있는 팩을 기계가 신고한다.

왜 있는가 (EVIDENCE-RULES.md 판정#59, 그리고 그 앞의 #34·#48·#52):
    같은 유형의 결함이 네 번 반복됐다. 파라미터 팩이 `base:` 로 상속을 하는데,
    자식이 **재료를 바꿨는데도** 부모의 재료 고유 계수를 조용히 물려받는다.
      · 판정#34 — sic 팩이 sti_ceria 의 IEP 정전창(산성용)을 상속해 자기 pH 계수를 가림
      · 판정#48 — sic 팩이 실리카 부모의 연마입자 농도를 상속
      · 판정#52 — 근거 문헌과 파라미터가 서로 다른 팩에 흩어짐
      · 판정#59 — sic_alumina_kmno4 가 `abrasive` 키 자체를 'ceria' 로 상속,
                  알루미나 슬러리에 세리아 화학항이 켜져 있었다
    매번 사람이 우연히 발견했다. 이 도구는 그 발견을 상시화한다.

무엇을 신고하는가:
    상속(own=False)받은 파라미터 K 에 대해,
      (1) K 가 어느 **재료축**에 속하는지 이름으로 분류하고(아래 AXIS_PREFIX),
      (2) 그 축의 재료가 **나**와 **K 를 실제로 선언한 조상**에서 다르면
    신고한다. 축을 분류할 수 없는 키는 신고하지 않는다(과잉 신고 금지) —
    대신 `--unclassified` 로 따로 볼 수 있다.

왜 "축"이 필요한가:
    축 없이 대조하면 `pad_ra_m`(패드 표면거칠기)이 "연마입자가 다르다"는 이유로
    신고된다. 패드 물성은 연마입자와 무관하다 — 그런 신고가 섞이면 도구를 아무도
    안 보게 된다. 축 분류가 이 도구의 핵심이고, 분류 못 하는 키를 조용히
    통과시키는 것이 의도된 보수성이다.

⚠ 이 도구는 **신고만 한다**. 무엇이 진짜 결함이고 무엇이 정당한 상속인지는
   사람(또는 판정)이 정한다. 예: sti_ceria 가 oxide_silica 에서 `ph_peak` 를
   물려받는 것은 둘 다 **산화막(oxide) 연마**라 막질축에서는 일치하고
   연마입자축에서만 다르다 — 그게 결함인지는 그 항이 연마입자 고유 물리인지에
   달렸다. 그래서 출력은 "결함 N건"이 아니라 "재료 불일치 상속 N건"이다.

사용:
    PYTHONPATH=. .venv/bin/python tools/audit_identity_inheritance.py
    PYTHONPATH=. .venv/bin/python tools/audit_identity_inheritance.py --unclassified
    PYTHONPATH=. .venv/bin/python tools/audit_identity_inheritance.py --json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.params import load_pack  # noqa: E402

# 재료 정체성을 나타내는 키 — 이 값이 다르면 "다른 재료"다.
IDENTITY_KEYS = {
    "abrasive": "연마입자",
    "film": "막질",
    "oxidizer": "산화제",
    "inhibitor": "억제제",
    "chelator_species": "착화제",
}

# 파라미터 이름 접두사 → 그 파라미터가 귀속되는 재료축.
# **보수적으로만 채운다** — 애매한 것은 넣지 않는다(넣으면 오탐이 난다).
AXIS_PREFIX: Dict[str, str] = {
    # 연마입자 고유
    "abrasive": "abrasive",
    "ce3": "abrasive",          # Ce3+ 분율 — 세리아 전용
    "ceria": "abrasive",        # ceria_tooth_* — 세리아 전용
    # 막질 고유
    "film": "film",
    "substrate": "film",
    # 산화제 고유
    "oxidizer": "oxidizer",
    # 억제제 고유
    "inhibitor": "inhibitor",
    # 착화제 고유
    "chelator": "chelator_species",
}

# 접두사로 안 잡히는 개별 키의 축 지정(근거를 주석으로 남긴다).
AXIS_EXACT: Dict[str, str] = {
    # 막질의 등전점 — 어느 막을 연마하느냐로 정해진다(sim/factors.py::_f_chi 가
    # 세리아 IEP 창의 창 경계를 이 값으로 잡는다).
    "wafer_iep_ph": "film",
    # 세리아가 SiN 을 억제해 만드는 선택비 — 연마입자·막질 양쪽에 걸리지만
    # 세리아 고유 물리이므로 연마입자축으로 본다.
    "oxide_nitride_selectivity": "abrasive",
    # shield_* = 표면 흡착 보호(PAA·아미노산 등 첨가제) — 억제제축.
    # COMPLETION.md "ψ 산화막 계" 절이 ψ 를 '표면 흡착 보호'로 정의한 것에 따른다.
    "shield_additive_wt_pct": "inhibitor",
    "shield_ref_wt_pct": "inhibitor",
    "shield_langmuir_K": "inhibitor",
    "shield_hill_n": "inhibitor",
    "shield_strength_k": "inhibitor",
    "shield_nitride_langmuir_K": "inhibitor",
    "shield_nitride_hill_n": "inhibitor",
    "shield_nitride_strength_k": "inhibitor",
}

# 명시적으로 **축 없음**으로 선언하는 키 — 재료가 달라도 상속이 정당하다.
# (여기 넣는 것은 "괜찮다"는 주장이므로 근거를 반드시 적는다.)
AXIS_NONE: Dict[str, str] = {
    "hamaker_j": "입자-매질-기판 3자 상수라 한 축에 귀속되지 않는다. 별도 판정 대상.",
    "damage_exponent": "기계적 손상 깊이 지수 — 재료 고유인지 공정 고유인지 미확정.",
    "dispersant_type": "분산제는 연마입자와 짝이지만 별도 축으로 선언된 적이 없다.",
    "slurry_viscosity_pa_s": "슬러리 전체 물성 — 단일 재료축에 귀속 불가.",
}


def _packs() -> List[str]:
    return [p.stem for p in sorted((ROOT / "knowledge" / "params").glob("*.yaml"))
            if p.stem != "base"]


def _axis_of(key: str) -> Optional[str]:
    if key in AXIS_NONE:
        return None
    if key in AXIS_EXACT:
        return AXIS_EXACT[key]
    if key in IDENTITY_KEYS:          # 정체성 키 자체(판정#59 가 걸린 자리)
        return key
    return AXIS_PREFIX.get(key.split("_")[0])


def _identity(pack_name: str) -> Dict[str, Optional[str]]:
    pk = load_pack(pack_name)
    return {k: (str(pk.get(k)) if pk.has(k) else None) for k in IDENTITY_KEYS}


def audit() -> Dict[str, Any]:
    mismatches: List[Dict[str, Any]] = []
    unclassified: List[Dict[str, Any]] = []
    ident_cache: Dict[str, Dict[str, Optional[str]]] = {}

    def ident(name: str) -> Dict[str, Optional[str]]:
        if name not in ident_cache:
            ident_cache[name] = _identity(name)
        return ident_cache[name]

    for p in _packs():
        pk = load_pack(p)
        me = ident(p)
        for key in sorted(pk.params):
            if pk.has_own(key):
                continue
            owner = pk.param(key).owner
            if owner in (pk.name, "base", None):
                continue
            try:
                theirs = ident(owner)
            except Exception:
                continue
            axis = _axis_of(key)
            if axis is None:
                if key not in AXIS_NONE:
                    unclassified.append({"pack": p, "key": key, "owner": owner})
                continue
            mine_v, their_v = me.get(axis), theirs.get(axis)
            if mine_v and their_v and mine_v != their_v:
                mismatches.append({
                    "pack": p, "key": key, "owner": owner, "axis": axis,
                    "axis_label": IDENTITY_KEYS[axis],
                    "mine": mine_v, "theirs": their_v,
                })
    return {"mismatches": mismatches, "unclassified": unclassified}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="기계 판독용 JSON 출력")
    ap.add_argument("--unclassified", action="store_true",
                    help="축을 분류하지 못한 상속 키도 함께 출력(감사 사각지대)")
    a = ap.parse_args()
    res = audit()
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    ms = res["mismatches"]
    print("재료 불일치 상속: %d건" % len(ms))
    if not ms:
        print("  (없음)")
    cur = None
    for m in ms:
        if m["pack"] != cur:
            cur = m["pack"]
            print("\n  [%s]" % cur)
        print("    %-30s <- %-18s  %s: %s(나) vs %s(%s)"
              % (m["key"], m["owner"], m["axis_label"],
                 m["mine"], m["theirs"], m["owner"]))
    if a.unclassified:
        uc = res["unclassified"]
        print("\n축 미분류 상속 키: %d건 (감사 사각지대 — 신고 대상 아님)" % len(uc))
        seen = set()
        for u in uc:
            if u["key"] in seen:
                continue
            seen.add(u["key"])
            print("    %-30s (%s <- %s)" % (u["key"], u["pack"], u["owner"]))
    print("\n※ 이 도구는 신고만 한다. 정당한 상속인지 결함인지는 판정이 정한다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
