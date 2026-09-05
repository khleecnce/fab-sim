"""gw_contact.py 회귀 테스트 — 하단 _self_test()의 5개 검증 항목을 pytest화.

물리 로직은 재구현하지 않고 gw_contact.py의 함수를 그대로 호출해 assert한다.
"""
import math

import numpy as np

import gw_contact as gw

E_STAR = 1e9  # Pa, 등가탄성계수 오더
R = 5e-6  # m, asperity 반경 오더


def test_hertz_force_scales_as_delta_power_1p5():
    """압입깊이 2배 -> 힘은 2^1.5배 (Hertz 비선형 스케일링)."""
    F1 = gw.hertz_force(1e-7, E_STAR, R)
    F2 = gw.hertz_force(2e-7, E_STAR, R)
    ratio = F2 / F1
    expect = 2 ** 1.5
    assert abs(ratio - expect) / expect < 1e-9


def test_hertz_contact_radius_consistency():
    """접촉면적으로부터 역산한 반경 a에 대해 a^2 = R*delta가 성립."""
    delta = 1.5e-7
    area = gw.hertz_contact_area(delta, R)
    a = math.sqrt(area / math.pi)
    assert abs(a ** 2 - R * delta) / (R * delta) < 1e-9


def test_gw_area_load_ratio_independent_of_separation():
    """지수분포 GW 모델의 A_r/W 비율이 분리거리 d와 무관하며 폐형식과 일치."""
    beta = 1.0 / 0.3e-6
    eta = 1e11
    A_n = 1e-4
    ratios_numeric = []
    for d in [0.0, 0.2e-6, 0.5e-6]:
        r = gw.gw_numeric(d, beta, eta, A_n, E_STAR, R)
        ratios_numeric.append(r["A_r"] / r["W"])
    analytic = gw.gw_analytic_ratio(beta, E_STAR, R)
    max_dev = max(abs(rn - analytic) / analytic for rn in ratios_numeric)
    assert max_dev < 1e-3


def test_area_vs_load_slope_matches_analytic_ratio():
    """asperity 밀도 eta를 바꿔가며 만든 (W, A_r) 쌍의 선형회귀 기울기가 폐형식과 일치."""
    beta = 1.0 / 0.3e-6
    A_n = 1e-4
    d_fixed = 0.3e-6
    etas = [0.5e11, 1e11, 2e11, 4e11]
    Ws, Ars = [], []
    for e in etas:
        r = gw.gw_numeric(d_fixed, beta, e, A_n, E_STAR, R)
        Ws.append(r["W"])
        Ars.append(r["A_r"])
    slope = np.polyfit(Ws, Ars, 1)[0]
    analytic = gw.gw_analytic_ratio(beta, E_STAR, R)
    assert abs(slope - analytic) / analytic < 1e-3


def test_plasticity_index_order_of_magnitude():
    """전형적 CMP 패드 조건에서 소성지수 psi가 합리적 오더 범위 내에 있음 (정밀 판정 아님)."""
    H = 50e6
    psi = gw.plasticity_index(E_STAR, H, 0.3e-6, R)
    assert 0.01 < psi < 100
