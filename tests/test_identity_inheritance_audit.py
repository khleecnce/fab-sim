# -*- coding: utf-8 -*-
"""정체성 상속 감사 도구의 계약 고정 (EVIDENCE-RULES.md 판정#60).

이 파일이 지키는 것:
  (a) 도구가 판정#59 가 실제로 잡아낸 유형을 잡는다(회귀 방지).
  (b) 오탐을 내지 않는다 — 패드 물성처럼 재료축과 무관한 키는 신고하지 않는다.
  (c) 현재 신고 목록이 **줄지 않는다**(누가 축 분류를 지우면 실패한다).
      늘어나는 것은 막지 않는다 — 새 팩이 생기면 신고가 느는 게 정상이다.
  (d) 도구가 MRR 을 바꾸지 않는다(순수 감사 도구다).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.engine import Recipe, simulate           # noqa: E402
from tools.audit_identity_inheritance import (    # noqa: E402
    AXIS_NONE, IDENTITY_KEYS, _axis_of, audit,
)

# 판정#60 시점의 실측 신고 목록(팩, 키). 이 조합들은 재료가 실제로 어긋난다.
_KNOWN = {
    ("sic_alumina_kmno4", "abrasive_size_nm"),
    ("sic_alumina_kmno4", "abrasive_ref_size_nm"),
    ("sic_alumina_kmno4", "abrasive_size_peak_nm"),
    ("sic_alumina_kmno4", "abrasive_size_exp_below_peak"),
    ("sic_alumina_kmno4", "abrasive_size_exp_above_peak"),
    ("sic_alumina_kmno4", "abrasive_iep_ph"),
    ("sic_alumina_kmno4", "ce3_fraction"),
    ("sic_alumina_kmno4", "ceria_tooth_gain"),
    ("sic_alumina_kmno4", "ceria_tooth_exponent"),
    ("sic_alumina_kmno4", "oxidizer_langmuir_K"),
    ("sic_alumina_kmno4", "oxidizer_langmuir_species"),
}


def test_audit_reports_known_material_mismatches():
    got = {(m["pack"], m["key"]) for m in audit()["mismatches"]}
    missing = _KNOWN - got
    assert not missing, f"감사가 알려진 재료 불일치를 놓쳤다: {sorted(missing)}"


def test_audit_does_not_flag_pad_or_tool_keys():
    """패드·장비 물성은 연마입자/막질과 무관하다 — 신고되면 오탐이다."""
    flagged = {m["key"] for m in audit()["mismatches"]}
    for k in flagged:
        head = k.split("_")[0]
        assert head not in {"pad", "cond", "platen", "rpm", "sfr", "groove",
                            "retaining", "cof", "asperity", "center", "edge"}, k


def test_ceria_specific_params_are_flagged_for_alumina_pack():
    """판정#59 의 본질 — 알루미나 팩이 세리아 고유 계수를 물려받는 것."""
    ms = [m for m in audit()["mismatches"]
          if m["pack"] == "sic_alumina_kmno4" and m["key"].startswith("ce")]
    assert ms, "세리아 고유 계수(ce3_*/ceria_*) 상속이 신고되지 않았다"
    for m in ms:
        assert m["axis"] == "abrasive"
        assert m["mine"] == "alumina" and m["theirs"] == "ceria"


def test_axis_classification_is_explicit_not_guessed():
    """축을 모르는 키는 None 을 돌려야 한다 — 추측해서 신고하지 않는다."""
    assert _axis_of("pad_ra_m") is None
    assert _axis_of("kp_m_per_pa") is None
    for k in AXIS_NONE:
        assert _axis_of(k) is None, k
    # 정체성 키 자체는 자기 축이다(판정#59 가 걸린 자리)
    for k in IDENTITY_KEYS:
        assert _axis_of(k) == k


def test_audit_is_read_only_mrr_unchanged():
    packs = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2",
             "sti_ceria", "w_fe_oxidizer", "sic_alumina_kmno4"]
    before = {p: float(np.mean(simulate(Recipe(pack=p)).mrr_nm_per_min))
              for p in packs}
    audit()
    after = {p: float(np.mean(simulate(Recipe(pack=p)).mrr_nm_per_min))
             for p in packs}
    assert before == after


def test_unclassified_keys_are_reported_separately_not_silently_dropped():
    """감사 사각지대는 숨기지 않고 별도 목록으로 낸다."""
    res = audit()
    assert "unclassified" in res
    # 사각지대가 신고 목록에 섞여 들어가지 않는다
    flagged = {(m["pack"], m["key"]) for m in res["mismatches"]}
    for u in res["unclassified"]:
        assert (u["pack"], u["key"]) not in flagged
