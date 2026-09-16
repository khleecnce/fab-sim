"""viscoelastic_maxwell.py 엔진 등록 회귀 — 패드 공정 하중주파수 역진단 5필드.

근거: sim/tier2_physics/viscoelastic_maxwell.py::maxwell_storage_loss/tan_delta(원본 무수정),
sim/tier1_empirical/kinematics.py::rpm_to_rads(원본 무수정),
knowledge/materials/pad-viscoelasticity-dma.md §3(Maxwell), §7(a)(ω=1/τ0 → E'/E=0.5 항등식).

설계: τ0(패드 실측 이완시간) 문헌값이 없어(노트 §4 자백) De를 지어낼 수 없다 — 대신
ω_process 후보 2개(플래튼 회전 ω_rot, 애스퍼리티 접촉 ω_asperity)를 역산하고 τ_crit=1/ω를
낸다. ω_asperity는 개별 asperity 압입깊이 delta가 필요한데 _gw_contact_state_diagnostic이
내는 값(분리거리 d, 앙상블 적분 A_r/W/n_contacts)에는 없어 항상 None + 스킵사유
(GW 패드 파라미터가 어느 팩에도 없다는 사실과 무관하게, 구조적으로 얻을 수 없다).
pad_relaxation_time_s는 현재 어느 팩도 미선언이라 De는 항상 None이 정상이다.
"""
import math

import numpy as np
import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _pad_loading_frequency_diagnostic
from sim.params import available_packs, Param
from sim.tier1_empirical import kinematics as kin
import viscoelastic_maxwell as VM

_ALL_PACKS = [p for p in available_packs() if p != "base"]


def test_omega_rot_matches_2pi_rpm_over_60_for_all_packs():
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _pad_loading_frequency_diagnostic(rr)
        expected = 2.0 * math.pi * rr.rpm_platen / 60.0
        assert out["pad_loading_omega_rot_rad_s"] == pytest.approx(expected)
        assert out["pad_loading_omega_rot_rad_s"] == pytest.approx(kin.rpm_to_rads(rr.rpm_platen))


def test_omega_rot_absolute_scale_base_pack():
    # base.yaml rpm_platen=55.0 rpm (literature) → omega_rot 절대값을 못박는다
    # (판정 근거: 과거 21,600km 오답이 상대 테스트만으로 8건 통과한 전례 — 절대 스케일 필수).
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    assert rr.rpm_platen == pytest.approx(55.0)
    out = _pad_loading_frequency_diagnostic(rr)
    assert out["pad_loading_omega_rot_rad_s"] == pytest.approx(5.759586531581287, rel=1e-9)


def test_tau_crit_identity_is_inverse_of_omega_rot():
    rr = Recipe(pack="sti_ceria", time_s=60).resolve()
    out = _pad_loading_frequency_diagnostic(rr)
    omega = out["pad_loading_omega_rot_rad_s"]
    tau_crit = out["pad_relaxation_time_threshold_s"]["rot"]
    assert tau_crit == pytest.approx(1.0 / omega)


def test_omega_asperity_always_none_with_skip_reason_in_note():
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _pad_loading_frequency_diagnostic(rr)
        assert out["pad_loading_omega_asperity_rad_s"] is None
        assert out["pad_relaxation_time_threshold_s"]["asperity"] is None
        assert out["pad_deborah_number"]["asperity"] is None
        assert "delta" in out["pad_loading_frequency_note"]


def test_deborah_number_none_without_tau0_declared():
    rr = Recipe(pack="w_fe_oxidizer", time_s=60).resolve()
    assert not rr.pack.has("pad_relaxation_time_s")
    out = _pad_loading_frequency_diagnostic(rr)
    assert out["pad_deborah_number"]["rot"] is None
    assert "pad_relaxation_time_s" in out["pad_loading_frequency_note"]


def test_deborah_number_and_tan_delta_match_maxwell_analytic_when_tau0_injected():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    tau0 = 0.02  # s, test-probe 주입값 — 문헌값 아님
    rr.pack.params["pad_relaxation_time_s"] = Param(
        key="pad_relaxation_time_s", value=tau0, unit="s",
        source="test-probe", confidence="estimated")
    out = _pad_loading_frequency_diagnostic(rr)
    omega = out["pad_loading_omega_rot_rad_s"]
    de = out["pad_deborah_number"]["rot"]
    assert de["tau0_s"] == pytest.approx(tau0)
    assert de["De"] == pytest.approx(tau0 * omega)

    Es_expect, El_expect = VM.maxwell_storage_loss([omega], 1.0, tau0)
    td_expect = VM.tan_delta(Es_expect, El_expect)
    assert de["E_storage_ratio"] == pytest.approx(float(Es_expect[0]))
    assert de["E_loss_ratio"] == pytest.approx(float(El_expect[0]))
    assert de["tan_delta"] == pytest.approx(float(td_expect[0]))


def test_storage_ratio_is_half_when_tau0_equals_relaxation_threshold():
    # 노트 §7(a) 항등식: omega = 1/tau0 → E'/E = 0.5
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    omega_rot = kin.rpm_to_rads(rr.rpm_platen)
    tau0 = 1.0 / omega_rot
    rr.pack.params["pad_relaxation_time_s"] = Param(
        key="pad_relaxation_time_s", value=tau0, unit="s",
        source="test-probe", confidence="estimated")
    out = _pad_loading_frequency_diagnostic(rr)
    assert out["pad_deborah_number"]["rot"]["De"] == pytest.approx(1.0)
    assert out["pad_deborah_number"]["rot"]["E_storage_ratio"] == pytest.approx(0.5, abs=1e-9)


def test_diagnostic_does_not_change_mrr():
    r = Recipe(pack="oxide_silica", time_s=60)
    res_with = simulate(r)

    orig = E._pad_loading_frequency_diagnostic
    E._pad_loading_frequency_diagnostic = lambda rr: {
        "pad_loading_omega_rot_rad_s": 999.0,
        "pad_loading_omega_asperity_rad_s": None,
        "pad_relaxation_time_threshold_s": {"rot": 999.0, "asperity": None},
        "pad_deborah_number": {"rot": None, "asperity": None},
        "pad_loading_frequency_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._pad_loading_frequency_diagnostic = orig

    assert np.array_equal(res_with.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert res_forced.pad_loading_omega_rot_rad_s == 999.0


def test_all_packs_full_simulate_wires_the_field():
    for pack in _ALL_PACKS:
        res = simulate(Recipe(pack=pack, time_s=60))
        assert res.pad_loading_omega_rot_rad_s is not None
        assert res.pad_loading_omega_rot_rad_s > 0
        assert res.pad_loading_frequency_note is not None


def test_original_viscoelastic_maxwell_module_unmodified():
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", "sim/tier2_physics/viscoelastic_maxwell.py"],
        cwd=E.__file__.rsplit("/sim/", 1)[0])
    assert result.returncode == 0, "viscoelastic_maxwell.py에 diff가 있다 — 원본 무수정 위반"
