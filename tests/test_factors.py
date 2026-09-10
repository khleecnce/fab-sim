"""병합 파라미터(sim/factors.py) 계약 테스트 — ARCHITECTURE-V2.md §2.

여기서 고정하는 것은 **물리가 아니라 계약**이다:
  ① 기준 조건에서 모든 팩터가 정확히 1.0 (이중 계상 방지)
  ② 입력을 바꾸면 출력이 실제로 바뀐다 (V1의 핵심 결함 회귀 방지)
  ③ 미모델링을 조용한 1.0으로 숨기지 않는다
  ④ 장비축과 소모품축이 섞이지 않는다 (사용자 확정 규칙)
  ⑤ 문헌 실측 재현 (pH 정점형)
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.engine import Recipe, simulate                      # noqa: E402
from sim.factors import (compute_factors, mrr_multiplier, coverage,   # noqa: E402
                         FACTOR_SPEC, MRR_COUPLED,
                         AXIS_EQUIPMENT, AXIS_CONSUMABLE)


def _factors(pack="oxide_silica", **overrides):
    return compute_factors(Recipe(pack=pack, pack_overrides=overrides).resolve())


def _mean_mrr(pack="oxide_silica", **overrides):
    r = simulate(Recipe(pack=pack, pack_overrides=overrides))
    return float(np.mean(r.mrr_nm_per_min))


# ═══════════════════════════════ ① 기준 조건 = 1.0 (이중 계상 방지)

def test_all_factors_are_unity_at_reference_condition():
    """기준 조건에서 모든 팩터는 정확히 1.0이어야 한다.

    왜 이게 가장 중요한 테스트인가: Kp는 이미 특정 조성·조건에서 역산된 값이다.
    팩터를 절대값으로 곱하면 같은 효과를 두 번 센다 — 2026-09-06에 Cu MRR이
    20배 붕괴한 사고가 정확히 이것이었다.
    """
    for key, f in _factors().items():
        if f.value is None:
            continue
        assert f.value == pytest.approx(1.0, abs=1e-9), (
            f"{f.symbol} {f.name}이 기준 조건에서 {f.value}다 — 1.0이어야 한다. "
            f"'_ref' 파라미터가 현재 조건과 다르면 이중 계상이 된다.")


def test_mrr_multiplier_is_unity_at_reference():
    mult, _ = mrr_multiplier(_factors())
    assert mult == pytest.approx(1.0, abs=1e-9)


def test_engine_does_not_double_count_chemistry():
    """엔진은 chemistry_factor와 factors.χ를 **둘 다** 곱하면 안 된다.

    χ는 chemistry.py의 산화제·세리아 항을 승계했다. 결합 지점이 두 곳이면
    화학이 제곱으로 들어간다.
    """
    import inspect
    from sim import engine
    src = inspect.getsource(engine.simulate)
    # 주석은 걷어내고 **실행되는 코드**만 본다 — 주석에 함수명을 언급했다고
    # 실패하면 테스트가 문서를 못 쓰게 만든다.
    code_only = "\n".join(
        line for line in src.splitlines()
        if not line.lstrip().startswith("#"))
    assert "chemistry_factor(" not in code_only, (
        "simulate()가 chemistry_factor를 직접 호출한다 — factors.χ가 이미 "
        "그 항을 승계했으므로 화학을 두 번 세게 된다.")


# ═══════════════════════════════ ② 입력이 실제로 출력을 바꾼다 (V1 결함 회귀)

@pytest.mark.parametrize("key,ref,expect_sign", [
    ("abrasive_wt_pct", 20.0, +1),        # 농도↑ → MRR↑ (문헌 직접 서술)
    ("pad_hardness_shore_d", 60.0, -1),   # 경도↑ → MRR↓ (H^-1.5)
    ("asperity_density_per_m2", 1e11, +1),
])
def test_consumable_inputs_actually_move_mrr(key, ref, expect_sign):
    """소모품 인자를 바꾸면 MRR이 **실제로** 변해야 한다.

    V1의 핵심 결함이 여기였다: --sensitivity에서 pH·입자크기·패드조도가 전부
    탄성도 0.000이었다. 소재 개발자용 도구인데 조성을 바꿔도 결과가 같았다.
    """
    lo = _mean_mrr(**{key: ref * 0.9})
    hi = _mean_mrr(**{key: ref * 1.1})
    assert lo != pytest.approx(hi, rel=1e-6), (
        f"{key}를 ±10% 바꿨는데 MRR이 안 변한다 — 엔진에 연결되지 않았다.")
    assert np.sign(hi - lo) == expect_sign, (
        f"{key} 증가 시 MRR 방향이 {np.sign(hi-lo)}인데 {expect_sign}이어야 한다.")


def test_ph_moves_mrr():
    """pH는 정점형이라 부호 테스트가 아니라 '변하는가'로 묻는다."""
    assert _mean_mrr(slurry_ph=10.0) != pytest.approx(_mean_mrr(slurry_ph=11.0), rel=1e-6)


# ═══════════════════════════════ ③ 미모델링을 숨기지 않는다

def test_stab_reference_at_default_time_is_unity():
    """S(시간 안정성)는 기본 time_s=60s(=1 min, Jeong 2024 관측 하한)에서 1.0.

    2026-09-09 정확도루프: Jeong et al. 2024(doi:10.3390/ma17081817) Fig.9
    로그감쇠 회귀로 partial 모델을 부여했다. ln(1)=0이라 t=1 min에서
    정확히 1.0이 되어 기준 1.0 계약을 유지한다.
    """
    f = _factors()["stab"]
    assert f.status == "partial"
    assert f.value == pytest.approx(1.0, abs=1e-9)


def test_stab_decreases_with_longer_polish_time():
    """time_s를 늘리면 S가 로그감쇠로 줄어든다 (Jeong 2024 Fig.9, 접촉수 반토막에도

    MRR은 −17%만 줄어드는 완만한 로그형 드리프트 — 방향만 신뢰, 절대값은 literature).
    """
    short = compute_factors(Recipe(pack="oxide_silica", time_s=60).resolve())["stab"].value
    long_ = compute_factors(Recipe(pack="oxide_silica", time_s=600).resolve())["stab"].value
    assert long_ < short, "10분 연속연마가 1분보다 S가 낮아야 한다(glazing 드리프트)"
    assert 0.7 < long_ < 1.0, f"10 min S={long_}가 문헌 관측범위(−17%~−30%)를 벗어남"


def test_stab_clamped_outside_observed_range():
    """관측범위(1~10 min) 밖은 clamp — 외삽으로 거짓 정밀도를 내지 않는다."""
    at_10 = compute_factors(Recipe(pack="oxide_silica", time_s=600).resolve())["stab"].value
    at_60min = compute_factors(Recipe(pack="oxide_silica", time_s=3600).resolve())["stab"].value
    assert at_60min == pytest.approx(at_10), "10 min 초과는 t=10 min 값으로 clamp되어야 한다"


def test_stab_confidence_downgraded_for_non_silica_packs():
    """원 데이터가 콜로이달 실리카/IC1000 단일계라 다른 연마입자는 estimated로 강등."""
    silica = compute_factors(Recipe(pack="oxide_silica", time_s=600).resolve())["stab"]
    alumina = compute_factors(Recipe(pack="cu_h2o2_bta", time_s=600).resolve())["stab"]
    assert silica.confidence == "literature"
    assert alumina.confidence == "estimated"


# ═══════════════════════════════ τ 슬러리 전달 — 실측이 직관을 기각한 축

def test_tau_porosity_reproduces_prasad_8_percent():
    """기공률 15→45%(3배)에 MRR은 **8%만** 오른다 (Prasad 2013 III.D.3).

    ⚠ 이 테스트가 지키는 것: "슬러리를 더 많이 나르면 MRR이 비례해 오른다"는
      직관은 실측으로 기각됐다. 저자 스스로 비례 증가를 기대했다가 빗나갔다고
      적었다("nominal increase"). 누군가 이 지수를 '상식적으로' 키우면
      여기서 잡힌다.
    """
    lo = _factors(pad_porosity_pct=15.0, pad_ref_porosity_pct=15.0)["tau"].value
    hi = _factors(pad_porosity_pct=45.0, pad_ref_porosity_pct=15.0)["tau"].value
    assert lo == pytest.approx(1.0)
    assert hi / lo == pytest.approx(1.08, abs=0.005), (
        f"기공률 3배에 τ가 {hi/lo:.4f}배 — 문헌은 1.08배다. "
        "비례 가정으로 퇴행했을 수 있다.")


def test_tau_groove_width_is_not_monotonic():
    """그루브 폭 η은 600 µm에서 정점이고 900 µm에서 오히려 내려간다.

    Mu 2016 Table 3 (3 PSI): 300→9.9%, 600→13.4%, 900→12.8%
    ⚠ 단조 증가 모델("넓힐수록 잘 흐른다")로 바꾸면 여기서 잡힌다. 실측은
      V_groove와 V_total이 함께 커져 q_actual 비율이 안 변한다고 말한다.
    """
    t300 = _factors(groove_width_um=300.0)["tau"].value
    t600 = _factors(groove_width_um=600.0)["tau"].value
    t900 = _factors(groove_width_um=900.0)["tau"].value
    assert t600 > t300, "600 µm가 300 µm보다 나아야 한다(η 9.9→13.4%)"
    assert t900 < t600, (
        f"900 µm({t900:.5f})가 600 µm({t600:.5f})보다 크다 — 단조 모델로 "
        "퇴행했다. 실측은 정체·감소다.")


def test_tau_does_not_extrapolate_outside_measured_range():
    """실측 범위(300~900 µm) 밖은 외삽하지 않고 끝값으로 고정한다."""
    assert _factors(groove_width_um=200.0)["tau"].value == pytest.approx(
        _factors(groove_width_um=300.0)["tau"].value)
    assert _factors(groove_width_um=1200.0)["tau"].value == pytest.approx(
        _factors(groove_width_um=900.0)["tau"].value)
    f = _factors(groove_width_um=200.0)["tau"]
    assert any("범위" in n and "밖" in n for n in f.notes), (
        "외삽 구간인데 경고하지 않는다.")


def test_tau_effect_is_weak_not_zero():
    """τ는 약하게라도 MRR을 움직여야 한다 — '반응 없음'과 '약한 반응'은 다르다."""
    a = _mean_mrr(groove_width_um=300.0)
    b = _mean_mrr(groove_width_um=600.0)
    assert a != pytest.approx(b, rel=1e-9), "그루브를 바꿔도 MRR이 전혀 안 변한다"
    assert abs(b / a - 1.0) < 0.10, (
        f"그루브 폭 변화가 MRR을 {abs(b/a-1)*100:.1f}% 바꾼다 — 실측 대비 과하다. "
        "τ 결합은 약해야 한다(지수 0.07).")


def test_tau_admits_profile_coupling_is_missing():
    """τ의 진짜 효과(반경 프로파일)가 미구현임을 스스로 신고해야 한다."""
    f = _factors()["tau"]
    assert any("프로파일" in n for n in f.notes), (
        "τ가 '평균 MRR이 아니라 프로파일을 지배한다'는 한계를 숨기고 있다.")


def test_unmodeled_factors_are_excluded_from_mrr():
    """미모델링 팩터는 MRR 배수에 1.0으로도 참여하지 않고 '제외'로 보고된다."""
    fs = _factors()
    _, notes = mrr_multiplier(fs)
    for k in MRR_COUPLED:
        if fs[k].status == "unmodeled":
            assert any("미모델링" in n and fs[k].name in n for n in notes)


def test_missing_size_exponent_does_not_invent_a_value():
    """입경 지수가 팩에 없으면 항을 만들지 않고 경고한다.

    Li et al. 2021은 입경을 정점형(~80nm 최대)이라고 정성 서술만 했고 원문
    수식은 OCR 손상으로 노트조차 assert하지 않았다. 단조 멱함수를 지어내면
    한쪽 구간만 맞고 정점을 놓친다.
    """
    f = _factors()["kappa"]
    assert "size" not in f.terms, "팩에 지수가 없는데 입경 항을 만들어냈다."
    assert any("입경" in n and "미적용" in n for n in f.notes)


# ═══════════════════════════════ ④ 축 분리 (사용자 확정 규칙)

def test_delta_is_unity_when_d99_equals_reference():
    """Δ 손상 유발도 — 기준 조건(D99==ref D99)에서 1.0 계약.

    sti_ceria(및 상속하는 sic_ceria_h2o2)에 Hitachi US8439995B2 Example 1
    (D99=700nm)을 baseline으로 이식했다 — 팩의 실제 조성값이 아니라 화학종
    (세리아, oxide/STI CMP) 일치를 근거로 한 what-if 기준점이다.
    """
    f = _factors(pack="sti_ceria")["delta"]
    assert f.value == pytest.approx(1.0, abs=1e-9)
    assert f.status == "partial"


def test_delta_increases_with_larger_d99_per_hitachi_exponent():
    """D99가 커지면 Δ가 실측 지수(n=1.44, US8439995B2)로 늘어난다.

    문헌 4점: D99 500->2500nm(5배)일 때 스크래치 10->100(10배).
    n=log(10)/log(5)=1.4306 — sti_ceria 팩의 damage_exponent=1.44와 근접
    (팩은 500nm가 아니라 700nm를 기준점으로 잡았으므로 완전히 같은 배수는
    아니다. 방향·오더만 검증한다).
    """
    f_ref = _factors(pack="sti_ceria")["delta"]
    f_big = _factors(pack="sti_ceria", abrasive_d99_nm=2500.0)["delta"]
    assert f_big.value > f_ref.value
    # US8439995B2: D99 700->2500nm(3.571배)에서 스크래치 20->100(5배 근방)
    # 이 팩의 n=1.44 기준으로는 3.571^1.44 = 6.25배 예측 -- 문헌 원값(5배,
    # 20->100)보다 다소 크다(기준점을 500이 아니라 700으로 잡았기 때문).
    # 순위(단조 증가)와 오더(같은 자릿수)만 검증 -- 절대 일치는 주장하지 않는다.
    ratio = f_big.value / f_ref.value
    assert 3.0 < ratio < 10.0, f"오더 이탈: {ratio:.2f}배 (문헌 5배 근방 기대)"


def test_delta_excluded_from_mrr_multiplier():
    """Δ는 MRR_COUPLED가 아니다 — 손상 지표이지 제거율 배수가 아니다.

    실측(백테스트)이 지지하기 전까지는 MRR에 곱해 넣지 않는다(사용자 원칙:
    "MRR_COUPLED 편입은 held-out이 지지할 때만").
    """
    assert "delta" not in MRR_COUPLED
    mult_ref, _ = mrr_multiplier(_factors(pack="sti_ceria"))
    mult_big, _ = mrr_multiplier(_factors(pack="sti_ceria", abrasive_d99_nm=2500.0))
    assert mult_ref == pytest.approx(mult_big), (
        "Δ 변화가 MRR에 새어 들어갔다 -- delta는 MRR_COUPLED 밖에 있어야 한다.")


def test_equipment_and_consumable_axes_do_not_mix():
    """장비 팩터의 driver 파트에 소모품이 섞이면 안 되고, 그 역도 안 된다.

    사용자 확정 규칙: "장비는 세가지 consumable과 묶이면 안된다."
    섞이면 "슬러리를 바꿀까 RPM을 올릴까"에 답할 수 없다 — 그 비교가 이 도구의
    존재 이유다.
    """
    consumable_parts = {"slurry", "pad", "disk"}
    for key, (sym, name, axis, parts) in FACTOR_SPEC.items():
        if axis == AXIS_EQUIPMENT:
            assert not (set(parts) & consumable_parts), (
                f"장비축 팩터 {sym} {name}의 파트에 소모품이 섞였다: {parts}")
        else:
            assert "tool" not in parts, (
                f"소모품축 팩터 {sym} {name}에 장비가 섞였다: {parts}")


def test_wafer_is_never_a_factor():
    """웨이퍼는 대상막질이지 조절 파라미터가 아니다 (사용자 확정)."""
    for key, (sym, name, axis, parts) in FACTOR_SPEC.items():
        assert "wafer" not in parts, (
            f"{sym} {name}이 웨이퍼를 driver로 삼는다 — 웨이퍼는 디폴트 대상값이라 "
            "파라미터에 포함시키면 안 된다.")


def test_equipment_factors_do_not_multiply_mrr_directly():
    """장비 팩터는 MRR 배수에 들어가지 않는다 — Preston이 이미 P·V를 쓴다.

    Λ을 또 곱하면 P·V가 제곱으로 들어간다.
    """
    for key in MRR_COUPLED:
        assert FACTOR_SPEC[key][2] == AXIS_CONSUMABLE, (
            f"{key}가 MRR에 곱해지는데 장비축이다 — Preston과 이중 계상된다.")


# ═══════════════════════════════ ⑤ 문헌 실측 재현

def test_ph_peak_reproduces_li2021_measurements():
    """Li et al. 2021 (doi:10.1149/2162-8777/ac3e44) Fig.1 재현.

        pH 10.0 → 1551 Å/min
        pH 11.0 → 1727 Å/min  (정점, +11.3%)
        pH 12.5 → 1407 Å/min  (−18.5% from peak)

    ⚠ 절대값이 아니라 **비율**을 검증한다. Kp는 다른 조건에서 역산됐으므로
    절대 MRR은 이 논문과 다르다 — 순위·비율만 비교 가능하다.
    """
    m10 = _mean_mrr(slurry_ph=10.0)
    m11 = _mean_mrr(slurry_ph=11.0)
    m125 = _mean_mrr(slurry_ph=12.5)

    assert m11 > m10 and m11 > m125, "pH 11.0이 정점이 아니다 — 정점형 거동 실패"
    assert m11 / m10 == pytest.approx(1727 / 1551, rel=0.02), (
        f"pH 10→11 상승비 {m11/m10:.4f}, 문헌 {1727/1551:.4f}")
    assert m125 / m10 == pytest.approx(1407 / 1551, rel=0.02), (
        f"pH 10→12.5 비 {m125/m10:.4f}, 문헌 {1407/1551:.4f}")


def test_ph_monotonic_model_would_have_failed():
    """단조 모델이었다면 pH 12.5를 과대평가했을 것 — 그걸 명시적으로 고정한다.

    이 테스트가 있는 이유: 누군가 '단순화'하려고 정점형을 단조로 되돌리면
    pH 12.5 예측이 정점보다 높아진다. 소재 개발자에게 **틀린 방향**을 가리키는
    것이라 부정확한 정도가 아니라 위험하다.
    """
    assert _mean_mrr(slurry_ph=12.5) < _mean_mrr(slurry_ph=11.0), (
        "pH 12.5가 정점(11.0)보다 높다 — 단조 모델로 퇴행했다.")


def test_pad_hardness_follows_h_minus_1_5():
    """MRR ∝ H^-1.5 (knowledge/cmp/particle-wafer-interaction... §4, verify PASS)."""
    h0, h1 = 60.0, 66.0
    m0 = _mean_mrr(pad_hardness_shore_d=h0)
    m1 = _mean_mrr(pad_hardness_shore_d=h1)
    assert m1 / m0 == pytest.approx((h1 / h0) ** -1.5, rel=1e-6)


# ═══════════════════════════════ 커버리지 정직성

def test_coverage_counts_only_real_connections():
    cov = coverage(_factors())
    assert cov["total"] == len(FACTOR_SPEC)
    assert set(cov["modeled"]) & set(cov["unmodeled"]) == set()
    # 미모델링 축이 남아 있다는 사실 자체가 보고돼야 한다 — 100%를 가장하지 않는다
    assert cov["score"] < 1.0, (
        "커버리지가 100%로 나온다 — τ·S 등 미연결 축이 있는데 숨기고 있다.")


def test_every_factor_declares_drivers_or_explains_absence():
    """모든 팩터는 자기 driver를 신고하거나, 없는 이유를 notes에 남긴다.

    이게 있어야 "κ를 올리려면 무엇을 만지나"에 기계가 답한다.
    """
    for key, f in _factors().items():
        if not f.drivers:
            assert f.notes, f"{f.symbol} {f.name}이 driver도 설명도 없다"


def test_factor_result_is_json_serializable():
    """UI(API)가 그대로 실어 보낼 수 있어야 한다."""
    import json
    res = simulate(Recipe(pack="oxide_silica"))
    s = json.dumps(res.summary()["factors"], ensure_ascii=False)
    assert "kappa" in s and "symbol" in s
