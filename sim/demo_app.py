"""
FabSim Phase 0 — Streamlit 데모 UI v0.

압력·RPM·존압력 슬라이더로 tier1_empirical의 Preston MRR 모델(kinematics.py +
preston.py)을 실시간 구동해 반경별 MRR 프로파일과 요약 지표를 보여준다.

실행: source .venv/bin/activate && streamlit run sim/demo_app.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

_TIER1_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tier1_empirical")
if _TIER1_DIR not in sys.path:
    sys.path.insert(0, _TIER1_DIR)

from kinematics import kinematic_number, relative_velocity, rpm_to_rads, wafer_grid  # noqa: E402
from preston import local_mrr, mrr_profile, mrr_to_nm_per_min, wafer_avg_mrr  # noqa: E402
from process_time import endpoint_time, removed_thickness  # noqa: E402

st.set_page_config(page_title="FabSim — CMP MRR 데모 v0", layout="wide")

st.title("FabSim — CMP MRR 데모 v0")
st.caption(
    "Tier1 경험식(Preston), 균일/존압력 가정, 문헌 재현 검증된 v0 모델 — "
    "실제 공정 예측 정밀도 보증 아님"
)

st.sidebar.header("공정 변수")
R_w_mm = st.sidebar.slider("웨이퍼 반경 R_w (mm)", 50.0, 300.0, 150.0, step=1.0)
r_cc_mm = st.sidebar.slider("회전축 간 거리 r_cc (mm)", 50.0, 400.0, 200.0, step=1.0)
rpm_w = st.sidebar.slider("RPM (웨이퍼)", 1.0, 200.0, 60.0, step=1.0)
rpm_p = st.sidebar.slider("RPM (패드)", 1.0, 200.0, 60.0, step=1.0)
kp = st.sidebar.number_input(
    "Kp (Preston 계수, m^2/N)", min_value=1e-15, max_value=1e-10,
    value=1e-13, step=1e-14, format="%.2e",
)

st.sidebar.header("압력")
zone_mode = st.sidebar.checkbox("존압력 사용 (center/mid/edge)")

R_w = R_w_mm / 1000.0
r_cc = r_cc_mm / 1000.0

pressure_fn = None
if zone_mode:
    p_center = st.sidebar.slider("압력 — center (kPa)", 1.0, 100.0, 20.7, step=0.1)
    p_mid = st.sidebar.slider("압력 — mid (kPa)", 1.0, 100.0, 20.7, step=0.1)
    p_edge = st.sidebar.slider("압력 — edge (kPa)", 1.0, 100.0, 20.7, step=0.1)

    r1, r2 = R_w / 3.0, 2.0 * R_w / 3.0

    def pressure_fn(r, _r1=r1, _r2=r2, _pc=p_center, _pm=p_mid, _pe=p_edge):
        if r <= _r1:
            return _pc * 1e3
        if r <= _r2:
            return _pm * 1e3
        return _pe * 1e3

    P_pa = None
else:
    P_kpa = st.sidebar.slider("압력 P (kPa)", 1.0, 100.0, 20.7, step=0.1)
    P_pa = P_kpa * 1e3

rs, mrr_m_s = mrr_profile(R_w, r_cc, rpm_w, rpm_p, P_pa, kp, pressure_fn=pressure_fn)
mrr_nm_min = mrr_to_nm_per_min(mrr_m_s)

if zone_mode:
    X, Y, W = wafer_grid(R_w, n_r=121)
    r_grid = np.hypot(X, Y)
    p_grid = np.vectorize(pressure_fn)(r_grid)
    ww, wp = rpm_to_rads(rpm_w), rpm_to_rads(rpm_p)
    m_grid = local_mrr(X, Y, ww, wp, r_cc, p_grid, kp)
    avg_mrr_m_s = float(np.average(m_grid.ravel(), weights=W.ravel()))
else:
    avg_mrr_m_s = wafer_avg_mrr(R_w, r_cc, rpm_w, rpm_p, P_pa, kp)

avg_mrr_nm_min = mrr_to_nm_per_min(avg_mrr_m_s)
mu = kinematic_number(R_w, r_cc, rpm_w, rpm_p)
wiwnu = (mrr_nm_min.max() - mrr_nm_min.min()) / mrr_nm_min.mean() * 100.0

col_plot, col_metrics = st.columns([2, 1])

with col_plot:
    st.subheader("반경별 MRR 프로파일")
    fig, ax = plt.subplots()
    ax.plot(rs * 1000.0, mrr_nm_min)
    ax.set_xlabel("반경 (mm)")
    ax.set_ylabel("MRR (nm/min)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with col_metrics:
    st.subheader("요약 지표")
    st.metric("웨이퍼 평균 MRR", f"{avg_mrr_nm_min:.1f} nm/min")
    st.metric("kinematic number (μ)", f"{mu:.4f}")
    st.metric("운동학 비균일도 2|μ|", f"{2 * abs(mu) * 100:.2f} %")
    st.metric("WIWNU (프로파일 기준)", f"{wiwnu:.2f} %")

st.sidebar.header("공정시간 (유량 축은 미포함 — 지식 부재로 별도 구현 예정)")
target_nm = st.sidebar.slider("목표 제거두께 (nm)", 1.0, 2000.0, 200.0, step=1.0)
target_m = target_nm * 1e-9
t_end_sec = endpoint_time(target_m, avg_mrr_m_s)

st.subheader("공정시간 적분")
col_time_plot, col_time_metrics = st.columns([2, 1])
with col_time_plot:
    fig2, ax2 = plt.subplots()
    ax2.plot(rs * 1000.0, removed_thickness(rs, mrr_m_s, t_end_sec) * 1e9)
    ax2.set_xlabel("반경 (mm)")
    ax2.set_ylabel("제거두께 (nm)")
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)
with col_time_metrics:
    st.metric("목표두께 도달 예상시간 (웨이퍼 평균 MRR 기준)", f"{t_end_sec:.1f} s")
