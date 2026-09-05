"""conditioner_sweep_kinematics.py 회귀 테스트 — _self_test()의 5항목을 pytest화."""
import math
import numpy as np

import conditioner_sweep_kinematics as csk


def test_static_position_invariant():
    T = np.linspace(0, 100, 50)
    x, y, r = csk.diamond_trajectory(T, R_p=150.0, R_a=80.0, R_i=40.0,
                                      n_p=0.0, n_a=0.0, n_d=0.0,
                                      beta_s=0.0, beta_max=math.pi / 3)
    assert np.allclose(x, x[0])
    assert np.allclose(y, y[0])


def test_table1_conditions_trajectory_bounded():
    T2 = np.arange(0, 20, 0.01)
    x2, y2, r2 = csk.diamond_trajectory(T2, R_p=190.0, R_a=115.0, R_i=52.0,
                                         n_p=100.0, n_a=19.0, n_d=73.0,
                                         beta_s=math.radians(20), beta_max=math.radians(60))
    r_max = 190.0 + 115.0 + 52.0
    r_min = max(0.0, 190.0 - 115.0 - 52.0)
    assert np.all(r2 <= r_max + 1e-6)
    assert np.all(r2 >= r_min - 1e-6)


def test_sweep_speed_phase_scaling():
    n_a1, n_a2 = 10.0, 20.0
    beta_s, beta0, beta_max = 0.0, math.pi / 6, math.pi / 3
    Tc = np.array([3.0])
    b1 = csk.disk_center_beta(Tc, n_a1, beta_s, beta0, beta_max)
    b2_half = csk.disk_center_beta(Tc / 2.0 * (n_a2 / n_a1), n_a2, beta_s, beta0, beta_max)
    assert np.allclose(b1, b2_half, atol=1e-9)


def test_pca_zero_outside_reach():
    bin_centers, pca = csk.pcr_radial_profile(
        duration_s=8.0, dt=0.005, R_p=190.0, R_a=115.0, disk_radius=52.0,
        n_p=100.0, n_a=19.0, n_d=73.0,
        beta_s=math.radians(5), beta_max=math.radians(40),
        n_particles=10, r_bins=25)
    r_reach_max = 190.0 + 115.0 + 52.0
    outside_mask = bin_centers > r_reach_max + 5.0
    assert (not np.any(outside_mask)) or np.allclose(pca[outside_mask], 0.0)


def test_pca_profile_has_nonzero_coverage():
    bin_centers, pca = csk.pcr_radial_profile(
        duration_s=8.0, dt=0.005, R_p=190.0, R_a=115.0, disk_radius=52.0,
        n_p=100.0, n_a=19.0, n_d=73.0,
        beta_s=math.radians(5), beta_max=math.radians(40),
        n_particles=10, r_bins=25)
    assert np.count_nonzero(pca) / len(pca) > 0.05
