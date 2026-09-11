"""ψ(표면 보호도) 분산제 흡착 경로 계약 테스트.

브리프: oxide_silica/sic_ceria_h2o2/sti_ceria 세 팩은 inhibitor_mM(금속 부동태
억제제)이 없어 ψ가 unmodeled로 신고됐다. ψ의 정의를 '표면 흡착 보호'로 넓혀
폴리머 분산제 흡착(PVA/PVP) 경로를 추가했다 — 이 테스트는 그 경로가
Li et al. 2021 §6 실측값을 그대로 재현하는지, unmodeled였던 세 팩이
modeled/partial로 바뀌었는지를 계약으로 고정한다. 새 숫자는 만들지 않는다.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.chemistry import _dispersant_protection_term          # noqa: E402
from sim.engine import Recipe                                   # noqa: E402
from sim.factors import compute_factors                         # noqa: E402
from sim.params import ParamPack, Param                         # noqa: E402


def _fake_pack(**params) -> ParamPack:
    return ParamPack(name="fake", params={
        k: Param(key=k, value=v, confidence="literature") for k, v in params.items()
    })


# ═══════════════════ 1~4: _dispersant_protection_term 순수함수 계약

def test_pva_relative_mrr_matches_li2021():
    notes = []
    v = _dispersant_protection_term(_fake_pack(dispersant_type="PVA"), notes)
    assert v == pytest.approx(2604.0 / 2700.0, rel=0.005)


def test_pvp_relative_mrr_matches_li2021():
    notes = []
    v = _dispersant_protection_term(_fake_pack(dispersant_type="PVP"), notes)
    assert v == pytest.approx(2486.0 / 2700.0, rel=0.005)


@pytest.mark.parametrize("kind", ["PAA", "PAM"])
def test_paa_pam_negligible_inhibition(kind):
    notes = []
    v = _dispersant_protection_term(_fake_pack(dispersant_type=kind), notes)
    assert v == pytest.approx(1.0, abs=1e-9)


def test_no_dispersant_type_returns_none():
    notes = []
    v = _dispersant_protection_term(_fake_pack(), notes)
    assert v is None


# ═══════════════════ 5~6: factors.compute_factors() 통합 — unmodeled 해소

def test_oxide_silica_psi_is_modeled():
    factors = compute_factors(Recipe(pack="oxide_silica").resolve())
    psi = factors["psi"]
    assert psi.status == "modeled"


@pytest.mark.parametrize("pack", ["sti_ceria", "sic_ceria_h2o2"])
def test_ceria_packs_psi_is_modeled_via_cross_system_transfer(pack):
    factors = compute_factors(Recipe(pack=pack).resolve())
    psi = factors["psi"]
    assert psi.status in ("modeled", "partial")
    assert psi.confidence == "estimated", (
        "세리아 팩은 oxide_silica에서 dispersant_type을 상속받은 교차계 전이라 "
        "literature보다 낮은 estimated여야 한다.")


# ═══════════════════ 7: 기준 1.0 계약 회귀 방지

@pytest.mark.parametrize("kind", ["NONE", "PAA", "PAM"])
def test_negligible_dispersant_override_keeps_psi_at_unity(kind):
    factors = compute_factors(
        Recipe(pack="oxide_silica", pack_overrides={"dispersant_type": kind}).resolve())
    psi = factors["psi"]
    assert psi.value == pytest.approx(1.0, abs=1e-9)
