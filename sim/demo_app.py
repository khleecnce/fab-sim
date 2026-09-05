"""
FabSim Phase 0 — Streamlit 데모 UI.

탭1: 압력·RPM·존압력 슬라이더로 tier1_empirical의 Preston MRR 모델(kinematics.py +
     preston.py)을 실시간 구동해 반경별 MRR 프로파일과 요약 지표를 보여준다.
탭2: WIWNU(반경 스케일) × 패턴밀도(다이 스케일) 결합 제거율 맵
     (wiwnu.py + pattern_density.py + wiwnu_pattern_combined.py, 이미 self-test/pytest
     통과된 기존 모듈을 그대로 노출 — 이 탭 추가로 세 모듈 파일은 수정하지 않음).

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
from wiwnu import p_uniform, p_edge_concentration  # noqa: E402
from pattern_density import effective_density  # noqa: E402
from wiwnu_pattern_combined import combined_removal_map, _area_weighted_2d  # noqa: E402

st.set_page_config(page_title="FabSim — CMP MRR 데모", layout="wide")

st.title("FabSim — CMP MRR 데모")
st.caption(
    "Tier1 경험식(Preston), 균일/존압력 가정, 문헌 재현 검증된 v0 모델 — "
    "실제 공정 예측 정밀도 보증 아님"
)

tab1, tab2 = st.tabs(["Preston MRR v0", "WIWNU × 패턴밀도 결합 맵"])

with tab1:
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
    wiwnu_pct = (mrr_nm_min.max() - mrr_nm_min.min()) / mrr_nm_min.mean() * 100.0

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
        st.metric("WIWNU (프로파일 기준)", f"{wiwnu_pct:.2f} %")

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

with tab2:
    st.caption(
        "반경-패턴 분리가능(separable) 1차 근사 — 반경별 blanket 제거율 K(r)과 "
        "다이내부 유효밀도 rho_eff(x)가 서로 독립이라고 가정하며, 엣지에서 패턴 영향이 "
        "증폭되는 것과 같은 교차항은 포함하지 않는다. 모든 반경 위치의 다이가 동일한 "
        "내부 패턴 분포를 갖는다고 가정(엣지 다이의 스크라이브 절단·회전 효과 미반영), "
        "패턴밀도 유효화 필터는 실제 탄성패드 굽힘 유래 타원형(elliptic) 커널 대신 "
        "가우시안으로 근사한 미검증 근사다 — MASTER-PLAN.md 진행 로그 참조."
    )

    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        st.markdown("**웨이퍼/공정 변수**")
        R_w2_mm = st.slider("웨이퍼 반경 R_w (mm)", 50.0, 300.0, 150.0, step=1.0, key="t2_rw")
        r_cc2_mm = st.slider("회전축 간 거리 r_cc (mm)", 50.0, 400.0, 200.0, step=1.0, key="t2_rcc")
        rpm_w2 = st.slider("RPM (웨이퍼)", 1.0, 200.0, 50.0, step=1.0, key="t2_rpmw")
        rpm_p2 = st.slider("RPM (패드)", 1.0, 200.0, 60.0, step=1.0, key="t2_rpmp")
        kp2 = st.number_input(
            "Kp (Preston 계수, m^2/N)", min_value=1e-15, max_value=1e-10,
            value=1e-13, step=1e-14, format="%.2e", key="t2_kp",
        )

    with col_in2:
        st.markdown("**압력 프로파일**")
        profile_mode = st.radio(
            "프로파일 종류", ["균일 (uniform)", "엣지 압력집중 (edge-concentration)"],
            key="t2_profile_mode",
        )
        P_kpa2 = st.slider("기준 압력 P0 (kPa)", 1.0, 100.0, 20.7, step=0.1, key="t2_p0")
        if profile_mode == "균일 (uniform)":
            p_norm_fn = p_uniform(P_kpa2 * 1e3)
        else:
            amp_edge = st.slider("엣지 압력집중 amp", 0.0, 1.0, 0.30, step=0.01, key="t2_amp_edge")
            n_edge = st.slider("엣지 집중도 n", 1.0, 20.0, 8.0, step=1.0, key="t2_n_edge")
            p_norm_fn = p_edge_concentration(P_kpa2 * 1e3, amp=amp_edge, n=n_edge)

    with col_in3:
        st.markdown("**다이 패턴밀도 (합성 예시)**")
        amp_pattern = st.slider("패턴밀도 진폭", 0.0, 0.45, 0.20, step=0.01, key="t2_amp_pat")
        period_mm = st.slider("패턴 주기 (mm)", 1.0, 10.0, 4.0, step=0.5, key="t2_period")
        PL_mm = st.slider("평탄화 길이 PL (mm)", 0.5, 10.0, 3.0, step=0.5, key="t2_pl")

    x_die = np.linspace(0.0, 20.0, 401)  # mm — wiwnu_pattern_combined._selftest() 예시 재현
    rho_local = 0.5 + amp_pattern * np.sin(2 * np.pi * x_die / period_mm)
    rho_eff_die = effective_density(x_die, rho_local, PL=PL_mm)

    R_w2 = R_w2_mm / 1000.0
    r_cc2 = r_cc2_mm / 1000.0
    radial_positions = np.linspace(1e-6, R_w2, 81)

    result = combined_removal_map(
        radial_positions, rho_eff_die, R_w2, r_cc2, rpm_w2, rpm_p2, kp2, p_norm_fn,
    )
    metrics_2d = _area_weighted_2d(result["rs"], result["RR"])

    col_map, col_metrics2 = st.columns([2, 1])
    with col_map:
        st.subheader("결합 제거율 맵 RR(r, x)")
        fig3, ax3 = plt.subplots()
        im = ax3.imshow(
            result["RR"],
            extent=[x_die.min(), x_die.max(), radial_positions.min() * 1000.0,
                    radial_positions.max() * 1000.0],
            origin="lower", aspect="auto", cmap="viridis",
        )
        ax3.set_xlabel("다이내부 위치 x (mm)")
        ax3.set_ylabel("웨이퍼 반경 r (mm)")
        fig3.colorbar(im, ax=ax3, label="제거율 (m/s, K 단위 그대로)")
        st.pyplot(fig3)

    with col_metrics2:
        st.subheader("결합 WIWNU 지표 (면적가중)")
        st.metric("sigma_pct (CV)", f"{metrics_2d['sigma_pct']:.2f} %")
        st.metric("half_range_pct", f"{metrics_2d['half_range_pct']:.2f} %")
        st.metric("평균 제거율", f"{metrics_2d['mean']:.3e} m/s")
