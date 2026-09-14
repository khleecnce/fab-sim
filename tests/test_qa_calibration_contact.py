"""C4 held-out 층의 F4(자기채점)·F2(출처매칭) 오탐/실탐 분리 — 회귀 테스트.

배경: tools/qa_loop.py의 F4는 원래 팩 YAML을 raw 텍스트로 스캔해 주석(#)에 적힌
문장까지 "자기채점"으로 오탐했다(w_fe_oxidizer/US8070843B2). 반대로 진짜 자기채점
(파라미터 note에서 실제로 지수를 뽑은 경우)은 여전히 잡아야 한다. 신고된 부분오염
(calibration_contact)은 F4가 아니라 C4로 격하돼 격리 유발 soft flag 집계에서 빠진다.
F2는 ID(DOI/특허번호)가 파일명에 없어도 (저자+연도) 토큰으로 papers/ 실제 파일을
찾을 수 있어야 하고, 토큰 하나만 맞을 때는 오매칭을 막아야 한다.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import qa_loop as Q  # noqa: E402


def _ds(tmp_path, name, vals, source="doi:10.1000/none", extra=""):
    body = (f"source: >\n  {source}\nused_for_calibration: false\npack: oxide_silica\n"
            f"{extra}conditions:\n")
    for i, v in enumerate(vals):
        body += (f"  - label: c{i}\n    pressure_psi: {1+i}\n    rpm_wafer: 60\n    rpm_platen: 60\n"
                 f"    mrr_nm_per_min: {v}\n    read_method: table\n")
    p = tmp_path / f"{name}.yaml"
    p.write_text(body, encoding="utf-8")
    return p


def test_f4_ignores_comment_only_reference_w_fe_regression():
    """w_fe_oxidizer.yaml:34의 주석 "held-out 검증은 ... US8070843B2 ... 으로만
    한다"는 선언이지 실제 파라미터 값의 출처가 아니다 — F4를 유발하면 안 된다."""
    pack_src = Q._pack_sources()
    ds_path = ROOT / "validation" / "datasets" / "us8070843b2_w_h2o2_series.yaml"
    a = Q.audit_dataset(ds_path, {}, {}, pack_src, {})
    assert not any(f.startswith("F4") for f in a["flags"])


def test_f4_fires_for_note_derived_reference(tmp_path):
    """oxide_silica.yaml의 abrasive_conc_exponent note는 실제로 US9499721B2에서
    지수를 로그-로그 회귀해 뽑았다고 적혀 있다 — 이건 진짜 자기채점, F4가 떠야 한다."""
    pack_src = Q._pack_sources()
    p = _ds(tmp_path, "y", [100, 140, 180], source="US9499721B2")
    a = Q.audit_dataset(p, {}, {}, pack_src, {})
    hits = [f for f in a["flags"] if f.startswith("F4")]
    assert hits and "abrasive_conc_exponent" in hits[0]


def test_calibration_contact_downgrades_f4_to_c4(tmp_path, monkeypatch):
    """calibration_contact를 신고하면 같은 히트가 F4(미신고)가 아니라
    C4(신고된 부분오염)로 격하되고, update_quarantine의 soft flag 집계에서 빠진다."""
    pack_src = Q._pack_sources()
    extra = ("calibration_contact:\n"
             "  - param: abrasive_conc_exponent\n"
             "    pack: oxide_silica\n"
             "    what: 테스트용 신고\n"
             "    axis: abrasive_wt_pct\n")
    p = _ds(tmp_path, "z", [100, 140, 180], source="US9499721B2", extra=extra)
    a = Q.audit_dataset(p, {}, {}, pack_src, {})
    assert not any(f.startswith("F4") for f in a["flags"])
    assert any(f.startswith("C4") for f in a["flags"])

    monkeypatch.setattr(Q, "QUAR", tmp_path / "q.json")
    audits = [{"dataset": "z", "flags": a["flags"], "verified_by_human": False}]
    q = Q.update_quarantine(audits)
    assert "z" not in q     # C4 하나만으론 soft flag 2개 조건을 못 채운다


def test_filename_token_fallback_finds_dandu2009_pdf():
    """papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf 는 파일명에 DOI가
    없어 ID 매칭에 실패하지만, (저자 dandu + 연도 2009) 토큰으로는 찾아야 한다.

    ⚠ papers/*.pdf 는 .gitignore 대상이라 실제 디렉터리를 읽으면 클린 체크아웃/CI에서
    파일이 없어 실패한다(2026-09-15 pre-push 훅이 실제로 잡아냄). 파일명 목록을
    명시적으로 주입해 형제 테스트와 동일하게 hermetic 하게 만든다."""
    all_names = ["dandu2009-jes-selective-sio2-sin-ceria-sti.pdf",
                 "dandu2015-jss-further-slurry-additives-sio2-si3n4-ceria.pdf"]
    sf = Q._find_source_file("doi:10.1149/1.3230624", {}, {}, "dandu2009_sio2_ceria_ph_sweep",
                              all_names)
    assert sf == "dandu2009-jes-selective-sio2-sin-ceria-sti.pdf"


def test_filename_token_fallback_requires_both_tokens():
    """저자 토큰만 맞고 연도가 다르면(dandu 2009 vs 파일의 2015) 매칭되지 않아야
    한다 — 토큰 1개 일치는 오매칭 위험이 크다."""
    all_names = ["dandu2015-jss-further-slurry-additives-sio2-si3n4-ceria.pdf"]
    sf = Q._find_source_file("doi:10.1149/1.3230624", {}, {}, "dandu2009_sio2_ceria_ph_sweep",
                              all_names)
    assert sf is None
