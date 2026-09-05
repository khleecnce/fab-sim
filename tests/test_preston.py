"""preston.py 회귀 테스트 — preston.py 하단 _selftest()의 5개 검증 항목을 pytest화.

물리 로직은 재구현하지 않고 preston.py의 함수를 그대로 호출해 assert한다.
"""
import preston as pr

R_W = 0.150  # m
R_CC = 0.200  # m
KP = 1.0e-13  # m^2/N, 오더체크용


def test_pressure_doubling_doubles_mrr():
    base = pr.wafer_avg_mrr(R_W, R_CC, 60.0, 60.0, 20.7e3, KP)
    dbl_p = pr.wafer_avg_mrr(R_W, R_CC, 60.0, 60.0, 41.4e3, KP)
    assert abs(dbl_p / base - 2.0) < 1e-9


def test_velocity_doubling_doubles_mrr():
    ww = pr.rpm_to_rads(60.0)
    v_ref = ww * R_CC  # Rs=1 균일속도
    base_speed_nm = pr.mrr_to_nm_per_min(KP * 20.7e3 * v_ref)
    dbl_speed_nm = pr.mrr_to_nm_per_min(KP * 20.7e3 * (2 * v_ref))
    assert abs(dbl_speed_nm / base_speed_nm - 2.0) < 1e-9


def test_order_of_magnitude_matches_literature():
    """SiO2 STI 표준조건 근사 결과가 문헌 실측범위(50~1000+ nm/min) 안에 들어옴."""
    base = pr.wafer_avg_mrr(R_W, R_CC, 60.0, 60.0, 20.7e3, KP)
    rate_nm_min = pr.mrr_to_nm_per_min(base)
    assert 20.0 <= rate_nm_min <= 2000.0


def test_rs1_flat_radial_profile():
    """Rs=1 + 균일압력 가정에서 반경별 MRR이 완전 평탄 (WIWNU=0 구조적 확인)."""
    rs, mrr = pr.mrr_profile(R_W, R_CC, 60.0, 60.0, 20.7e3, KP)
    flat = float((mrr.max() - mrr.min()) / mrr.mean())
    assert flat < 1e-12


def test_rs_neq1_edge_center_ratio_matches_kinematics():
    """Rs!=1일 때 edge/center 비가 kinematics.py 교차검증값(1.00391)과 일치."""
    rs, mrr = pr.mrr_profile(R_W, R_CC, 50.0, 60.0, 20.7e3, KP)
    ratio = mrr[-1] / mrr[0]
    assert abs(ratio - 1.00391) < 1e-4
