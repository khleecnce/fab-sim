"""현재 막혀 있는 미지량 전부에 탈출 경로를 배정한다 — 수치로 판정.

이 스크립트는 주장하지 않고 **측정한다**. 특히 R1(소거)은 미지량을
자릿수 단위로 흔들어 순위가 변하는지 직접 확인한다.
"""
import sys
import pathlib
import warnings
import math

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                    # noqa: E402
from sim.unknown_router import (                      # noqa: E402
    cancellation_test, route_unknown, identifiability, ROUTES,
)
from sim.engine import Recipe, simulate               # noqa: E402
from sim.params import load_pack, Param               # noqa: E402
import sim.models                                     # noqa: E402,F401


# ⚠ 기본 모델(tier1.preston_radial)은 슬러리 물성을 쓰지 않는다 —
#   압력·속도만으로 계산한다. 그 모델로 물성을 흔들면 당연히 출력이
#   변하지 않고, 그것을 "약분된다(R1)"로 오독하면 거짓 해결이 된다.
#   물성 경로를 타는 모델로 재야 한다.
MODEL = "tier2.gw_physical_kp"


def mrr(pack: str, overrides: dict, model: str = MODEL) -> float:
    r = simulate(Recipe(pack=pack, pack_overrides=overrides), model=model)
    return float(np.mean(np.asarray(r.mrr_nm_per_min, dtype=float)))


def sweep_predictor(pack: str, unknown_key: str, sweep_key: str,
                    sweep_vals):
    """미지량을 x로 놓았을 때, 스윕 축을 따라 예측 벡터를 낸다."""
    def predict(x: float):
        out = []
        for v in sweep_vals:
            out.append(mrr(pack, {unknown_key: x, sweep_key: v}))
        return out
    return predict


print("=" * 78)
print("막힌 미지량 → 탈출 경로 판정")
print("=" * 78)

verdicts = []

# ── ① 화학 변질층 유효 경도 H_s ────────────────────────────────
# 문헌 상태: 절대값이 어느 문헌에도 없다. 원 모델조차 벌크값으로 대체했다.
# 게다가 문헌이 서로 모순된다("산화물이 더 단단하다" vs "표면층이 더 무르다").
print("\n── ① 화학 변질층 유효 경도")
pk = load_pack("w_fe_oxidizer")
key = "film_bulk_hardness_pa"
if pk.has(key):
    base = float(pk.get(key))
    probes = [base * f for f in (0.01, 0.1, 1.0, 10.0, 100.0)]
    pred = sweep_predictor("w_fe_oxidizer", key, "pressure_psi",
                           [2.0, 3.0, 4.0, 5.0, 6.0])
    cancels, ev = cancellation_test(pred, probes)
    print(f"   미지량을 {probes[0]:.2e} ~ {probes[-1]:.2e} 로 흔듦 (4자릿수)")
    print(f"   → {ev.get('판정')}")
    print(f"   절대값 로그편차: {ev.get('절대값 로그편차')}")
    v = route_unknown(
        "표면 변질층 유효 경도",
        cancels=cancels,
        bound_known=None if cancels else "H_surface ≤ H_bulk (부등식 확보됨)",
        used_by_terms=2,
    )
    verdicts.append(v)
    print(f"   판정: {v.route} — {v.reason}")
    print(f"   조치: {v.action}")
else:
    print("   (키 없음)")

# ── ② 흡착 상수와 억제 상수 (식별 불가로 기록된 쌍) ────────────
print("\n── ② 흡착 상수 × 억제 상수 (상관 0.929로 분리 불가 기록)")
ok, why = identifiability(n_unknowns=2, n_independent_observations=12,
                          max_pairwise_corr=0.929)
print(f"   과결정 판정: {why}")
v = route_unknown(
    "흡착-억제 상수쌍",
    cancels=False,
    n_unknowns=2, n_observations=12, max_corr=0.929,
    measurable_by="흡착량 독립 측정(수정진동자 저울 또는 전기화학 임피던스) "
                  "— MRR 데이터만으로는 영원히 분리되지 않는다",
    used_by_terms=1,
)
verdicts.append(v)
print(f"   판정: {v.route} — {v.reason}")
print(f"   조치: {v.action}")

# ── ③ 유효 냉각 유량 (공급량 대비 도달량 2~22%, 5~50배 편차) ──
print("\n── ③ 유효 전달 유량 (도달 비율 2~22%로 문헌 편차 큼)")
pkn = "oxide_silica"
pk2 = load_pack(pkn)
if pk2.has("sfr_ml_min"):
    b = float(pk2.get("sfr_ml_min"))
    probes = [b * f for f in (0.02, 0.05, 0.10, 0.22, 1.0)]   # 도달 비율 범위
    pred = sweep_predictor(pkn, "sfr_ml_min", "pressure_psi",
                           [2.0, 3.0, 4.0, 5.0, 6.0])
    cancels, ev = cancellation_test(pred, probes)
    print(f"   도달 비율 2%~100% 범위로 흔듦")
    print(f"   → {ev.get('판정')}")
    v = route_unknown("유효 전달 유량", cancels=cancels,
                      measurable_by="웨이퍼 하부 도달 유량 직접 계측",
                      used_by_terms=1)
    verdicts.append(v)
    print(f"   판정: {v.route} — {v.reason}")
    print(f"   조치: {v.action}")

# ── ④ 산화제 거동의 두 물성 (이번에 새로 필요해진 것) ──────────
print("\n── ④ 산화제 포화 농도 K_sat · 막 강도 탄성도 e_H")
print("   문헌 상태: 두 값 모두 CMP 조건 실측이 없다(감사 §4 미확인 ②).")
ok2, why2 = identifiability(n_unknowns=2, n_independent_observations=5)
print(f"   단일 MRR 곡선(n=5)으로 식별 가능한가: {why2}")
v = route_unknown(
    "산화제 포화농도·막강도 탄성도",
    cancels=False,
    n_unknowns=2, n_observations=5,
    measurable_by="(i) 전위계단법 부동태화 전하밀도 Q(C) "
                  "(ii) AFM 마모깊이 대 농도 — 둘 다 사내 저비용 측정",
    used_by_terms=1,
)
verdicts.append(v)
print(f"   판정: {v.route} — {v.reason}")
print(f"   조치: {v.action}")
print("   ⚠ 이 둘을 팩 파라미터로 그냥 두면 자유 파라미터가 2개 늘어난다.")
print("     R8은 '측정 전까지 이 항을 켜지 않는다'를 뜻한다 — 추정값으로 켜면 피팅이다.")

# ── 요약 ────────────────────────────────────────────────────
print()
print("=" * 78)
print("요약")
print("=" * 78)
from collections import Counter
c = Counter(v.route for v in verdicts)
for r in sorted(c):
    print(f"  {r} {ROUTES[r]}: {c[r]}건")
print()
blocked_old = len(verdicts)
resolved = sum(1 for v in verdicts if v.route in ("R1", "R2", "R3"))
spec = sum(1 for v in verdicts if v.route == "R8")
print(f"  '문헌 없음'으로 멈춰 있던 {blocked_old}건 중")
print(f"    · 값 없이 해결 가능: {resolved}건 (R1/R2/R3)")
print(f"    · 측정 명세로 전환: {spec}건 (R8 — 제품 기능이 된다)")
print(f"    · 항 제거 대상: {sum(1 for v in verdicts if v.route=='R7')}건")
