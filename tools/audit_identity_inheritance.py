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
    # χ pH 정점형 항(_ph_peak_term, Li et al. 2021 doi:10.1149/2162-8777/ac3e44,
    # 20wt% 실리카 Fig.1)의 정점 위치. sim/factors.py::_f_chi 2차 패스 자체가
    # 이 계열 후보를 "고유 계수를 선언한 조상의 abrasive"로 게이팅한다(판정#59) —
    # abrasive: alumina 만 자기선언하고 이 값이 폴백되면 "실리카 곡선을 산성
    # 알루미나계에 씌운 오염값"이 실측으로 확인됐다(EVIDENCE-RULES 판정#59 ③).
    # 연마입자축.
    "ph_peak": "abrasive",
    # ph_peak 와 **같은 문헌·같은 곡선의 정점 높이**(pH10→11 MRR 비 1.113, 동일
    # Li 2021 Fig.1) — 다른 축으로 갈라지면 그 자체가 결함이므로 ph_peak 와
    # 동일하게 연마입자축. 현재는 sim 어디서도 값으로 소비되지 않는 근거 기록용
    # 키다(tests/test_no_orphan_pack_keys.py 의 _KNOWN_ORPHANS 참조, χ pH 항은
    # ph_curvature_low/high 로 형상을 만들고 이 비를 따로 곱하지 않는다 — 곱하면
    # Kp 와 이중계상). 축 배정은 "지금 쓰이는가"가 아니라 "이 숫자가 어느 재료
    # 실측인가"를 묻는 것이라 orphan 이어도 ph_peak 와 갈라둘 이유가 없다.
    "ph_mrr_at_peak_rel": "abrasive",
    # χ pH 연화항(_ph_softening_term)의 pH 1단위당 경도비 감쇠 계수.
    # knowledge/params/sic_ceria_h2o2.yaml 자신의 note가 직접 근거를 댄다:
    # "이 값은 SiC 표면 화학에서 나왔다. Si 산화막의 pH 의존성은 다르다
    # (...) 다른 재료계로 옮기지 마라." — 무엇을 깎느냐(SiC 표면 가수분해/연화)
    # 가 계수를 정하지, 어느 연마입자·산화제로 깎느냐가 정하지 않는다는 것이
    # 문헌 역산 당시(판정#34 계보)의 명시적 주장이다. 막질축.
    # ⚠ sic_alumina_kmno4 가 이 키를 상속하는 유일한 팩인데, 그 팩의 film 도
    # sic_4h 로 소유 조상(sic_ceria_h2o2)과 동일해 막질축에서는 애초에 불일치가
    # 없다 — 즉 이 상속은 "재료가 달라도 정당"한 사례가 아니라 "애초에 재료가
    # 같아서" 감사가 조용한 것이다(연마입자·산화제만 다르다). 현재는
    # sim/factors.py::_f_chi 1차 패스가 own `sic_kmno4_ph_acid_k`(판정#61)를
    # 먼저 골라 이 항 자체가 비활성(dead)이다 — 그 own 키가 제거/리네임되면
    # 이 축 배정이 즉시 유효해진다(그때도 film 일치이므로 신고되지 않는 것이
    # 맞다; 산성 pH=2.3 을 알칼리 pH 9~11 역산 계수로 외삽하는 별개의 위험은
    # 이 감사의 범위 밖이다).
    "ph_softening_per_unit": "film",
}

# 패드/장비 하드웨어 물성 — 어느 IDENTITY_KEYS 축에도 속하지 않는다(감사 사각지대가
# 아니라 "축이 없는 게 맞다"는 적극적 판정). sim/equipment_outputs.py:98-100·
# sim/engine.py:589-595 가 유일한 소비처이고, 둘 다 pad_ra_m 을
# slurry_viscosity_pa_s 와 함께 Sommerfeld 수/Stribeck 윤활 진단에만 쓴다 —
# abrasive/film/oxidizer/inhibitor/chelator_species 어느 것도 이 계산에 들어가지
# 않는다(패드 표면거칠기는 패드 제조사·컨디셔닝의 함수다). tools/audit_identity_
# inheritance.py 자신의 모듈 docstring(§"왜 축이 필요한가")이 이미 pad_ra_m 을
# "축 없이 대조하면 오탐이 섞이는" 표준 예로 든다 — 그 서술을 코드로 확정한다.
_PAD_RA_M_NOTE = (
    "패드 표면거칠기 — sim/equipment_outputs.py:98-100, sim/engine.py:589-595의 "
    "윤활 진단(Sommerfeld/Stribeck)에서만 slurry_viscosity_pa_s와 함께 쓰인다. "
    "5개 IDENTITY_KEYS(연마입자/막질/산화제/억제제/착화제) 중 어느 것도 이 계산에 "
    "들어가지 않는다 — 패드는 재료 정체성이 아니라 소모품/장비 축이다."
)

# 명시적으로 **축 없음**으로 선언하는 키 — 재료가 달라도 상속이 정당하다.
# (여기 넣는 것은 "괜찮다"는 주장이므로 근거를 반드시 적는다. 근거가 "그런 축을
# 아직 못 찾았다"뿐이면 그렇게 정직하게 적는다 — 문헌 근거가 있는 것처럼 쓰지 않는다.)
AXIS_NONE: Dict[str, str] = {
    "pad_ra_m": _PAD_RA_M_NOTE,
    "hamaker_j": (
        "미검증 — 귀속 근거 미확보. 3자(입자-매질-기판) 상수라 원칙적으로도 단일 "
        "축 귀속이 어렵고, tests/test_no_orphan_pack_keys.py 의 _KNOWN_ORPHANS가 "
        "이미 확인한 대로 sim/tier2_physics/dlvo_colloid.py는 self-test에서 A를 "
        "인자로만 받고 팩을 조회하지 않는다 — 현재 sim 어디서도 이 팩 값을 읽지 "
        "않는 고아 키라 축을 배정해도 검증할 실행 경로가 없다."
    ),
    "damage_exponent": (
        "미검증 — 귀속 근거 상충. 팩 note 들이 서로 다른 축을 정당화 근거로 쓴다: "
        "oxide_silica.yaml(\"막질 일치(산화막 CMP)이나 연마입자 불일치(세리아 vs "
        "콜로이달 실리카)\")·w_fe_oxidizer.yaml(\"막질·공정 완전 일치\")은 막질축을 "
        "근거로 값을 전이했는데, cu_h2o2_bta.yaml은 정반대로 막질이 다른데도"
        "(텅스텐→구리) \"연마입자·촉매 계열 유사성\"을 근거로 같은 값을 전이했다. "
        "base.yaml 자신도 \"재료 고유인지 공정 고유인지 미확정\"이라 적는다. "
        "축을 강제 배정하면 이 상충 중 하나는 반드시 틀린다 — 사각지대로 남긴다. "
        "(참고: 현재 실제 상속은 전부 base.yaml 경유뿐이라 — 5팩이 전부 own 선언 — "
        "audit()의 `owner in (..., \"base\", None): continue` 규칙에 걸려 이미 신고 "
        "대상이 아니다. 축 배정은 지금 당장 신고 건수를 바꾸지 않는다.)"
    ),
    "dispersant_type": (
        "미검증 — 귀속 근거 미확보. sim/chemistry.py::_dispersant_protection_term의 "
        "DISPERSANT_MRR_RELATIVE 표는 Li et al. 2021 §6의 실리카 슬러리 실측값이고 "
        "'분산제는 입자 표면에 흡착한다'는 메커니즘상 연마입자축이 그럴듯한 "
        "후보이지만, 그 흡착 선호도가 연마입자 화학종(실리카 vs 알루미나 등)에 "
        "따라 달라진다는 것을 직접 보인 문헌은 확보하지 못했다 — PAA/PVA 류는 "
        "일반 고분자 분산제로 입자 특이성이 없을 수도 있다. 함수 docstring도 "
        "이를 억제제축(IDENTITY_KEYS의 inhibitor)과 명시적으로 분리해 둔 상태라 "
        "그쪽으로도 옮길 근거가 없다. 그럴듯한 가설과 확인된 근거를 구분해 "
        "사각지대로 남긴다."
    ),
    "slurry_viscosity_pa_s": (
        "슬러리 **전체** 물성(연마입자 wt%·첨가제 농도 등 다성분이 함께 정한다) — "
        "pad_ra_m 과 정확히 같은 소비처(sim/equipment_outputs.py:98-100, "
        "sim/engine.py:589-595의 윤활 진단)에서 같은 이유로 쓰인다. 단일 "
        "IDENTITY_KEYS 축의 '고유 계수'가 아니라 혼합물 전체의 측정값이라 "
        "원칙적으로 한 재료축에 귀속시키는 것 자체가 범주 오류다 — pad_ra_m 과 "
        "동급의 근거 있는 AXIS_NONE(미검증이 아니다)."
    ),
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
