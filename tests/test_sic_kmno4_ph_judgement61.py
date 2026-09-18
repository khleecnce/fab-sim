"""판정#61 — sic_alumina_kmno4 팩의 pH 축 배선 계약.

근거 노트: knowledge/cmp/sic-kmno4-acidic-ph-decay-chen2020.md
1차 출처: Chen et al. 2020, DOI 10.1134/S1070427220060099, Fig. 1(a).

판정#59 가 이 팩의 pH 항을 (남의 재료 계수라서) 껐고, 이 판정이 자기 재료계
문헌으로 다시 켰다. 아래 계약이 지키는 것:
  1. 기준 조건에서 배수 1.0 (Kp 이중 계상 방지)
  2. 산성→알칼리 단조 감소 (실리카 정점형·세리아 IEP 창과 부호가 반대)
  3. 게이트 — 계수를 직접 선언하지 않은 팩은 이 항을 주워가지 않는다
  4. 다른 5팩의 χ 분기 선택·값 불변
"""
import math
import pytest

from sim.params import load_pack
from sim.engine import Recipe, ResolvedRecipe, simulate
from sim.factors import _f_chi, _ph_sic_kmno4_acidic_term

PACK = "sic_alumina_kmno4"


def _rr(pack_name, **over):
    pk = load_pack(pack_name)
    for k, v in over.items():
        pk.params[k].value = v
    return pk, ResolvedRecipe(
        base=Recipe(pack=pack_name), pack=pk, used_keys=[], film=None,
        wafer_radius_m=0.15, pressure_psi=4.0, rpm_wafer=90, rpm_platen=90,
        center_offset_m=0.12, kp_m_per_pa=float(pk.get("kp_m_per_pa")),
        n_points=81, edge_exclusion_m=0.003)


def test_ph_term_is_unity_at_pack_reference():
    pk = load_pack(PACK)
    assert pk.has_own("sic_kmno4_ph_acid_k")
    v = _ph_sic_kmno4_acidic_term(pk, [])
    assert v == pytest.approx(1.0, abs=1e-12)


def test_ph_term_decreases_monotonically_toward_alkaline():
    pk = load_pack(PACK)
    vals = []
    for ph in (2.0, 4.0, 6.0, 8.0, 10.0):
        pk.params["slurry_ph"].value = ph
        vals.append(_ph_sic_kmno4_acidic_term(pk, []))
    assert all(vals[i] > vals[i + 1] for i in range(4)), vals
    # Chen 2020 Fig.1(a) 판독: pH2→10 이 3.56배 — 형상 계수가 그 배수를 담는다
    assert vals[0] / vals[4] == pytest.approx(3.56, rel=0.05)


def test_ph_term_reproduces_chen2020_si_face_points():
    """팩에 넣은 k·φ 가 판독 5점을 3 % 이내로 재현한다(노트 §3)."""
    pk = load_pack(PACK)
    base = 192.38
    tops = [102.53, 145.10, 161.69, 165.93, 167.11]
    s = 400.0 / 23.272
    obs_abs = [(base - t) * s for t in tops]
    obs = [v / obs_abs[0] for v in obs_abs]
    pred = []
    for ph in (2.0, 4.0, 6.0, 8.0, 10.0):
        pk.params["slurry_ph"].value = ph
        pk.params["ph_ref"].value = 2.0          # 판독 기준점으로 정규화
        pred.append(_ph_sic_kmno4_acidic_term(pk, []))
    for o, p in zip(obs, pred):
        assert abs(p / o - 1) < 0.03, (o, p)


def test_ph_term_is_gated_to_packs_that_declare_the_coefficient():
    for name in ("oxide_silica", "sti_ceria", "cu_h2o2_bta",
                 "w_fe_oxidizer", "sic_ceria_h2o2"):
        assert _ph_sic_kmno4_acidic_term(load_pack(name), []) is None, name


def test_chi_is_no_longer_unmodeled_and_unity_at_reference():
    pk, rr = _rr(PACK)
    f = _f_chi(rr)
    assert f.status != "unmodeled", f.status
    assert "ph_sic_kmno4_acidic" in f.terms, f.terms
    assert f.value == pytest.approx(1.0, abs=1e-9)


def test_mrr_now_responds_to_ph_on_this_pack():
    """판정#59 이후 죽어 있던 축이 살아났는지 — 엔진 끝단에서 확인."""
    import numpy as np
    out = {}
    for ph in (2.0, 6.0, 10.0):
        w = simulate(Recipe(pack=PACK, pack_overrides={"slurry_ph": ph}))
        out[ph] = float(np.mean(w.mrr_nm_per_min))
    assert out[2.0] > out[6.0] > out[10.0], out
    assert out[2.0] / out[10.0] > 3.0, out


@pytest.mark.parametrize("name", ["oxide_silica", "sti_ceria", "cu_h2o2_bta",
                                  "w_fe_oxidizer", "sic_ceria_h2o2"])
def test_other_packs_chi_branch_unchanged(name):
    """다른 팩이 이 새 분기를 고르지 않는다(후보 추가의 부작용 차단)."""
    pk, rr = _rr(name)
    f = _f_chi(rr)
    assert "ph_sic_kmno4_acidic" not in f.terms, (name, f.terms)
