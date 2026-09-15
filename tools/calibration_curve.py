"""데이터를 넣으면 실제로 좋아지는가 — 전 데이터셋에서 학습곡선을 잰다.

이것이 개정된 완료 기준의 핵심 측정이다.
절대값을 3 % 로 맞추는 대신, **고객이 자기 데이터를 k 점 넣으면 절대오차가
얼마가 되는가**를 잰다. 반드시 held-out 으로 잰다(배율을 뽑은 점에서
재면 자기 채점이다).
"""
import sys
import pathlib
import warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                    # noqa: E402
from validation.backtest import run_all               # noqa: E402
from sim.calibration.series_scale import fit_series_scale, learning_curve  # noqa: E402


def main() -> int:
    results = run_all()
    rows = []
    for r in results:
        p = np.asarray(getattr(r, "predicted", []), dtype=float)
        o = np.asarray(getattr(r, "observed", []), dtype=float)
        if p.size < 3 or p.size != o.size:  # noqa: PLR2004
            continue
        # ⚠ 계수를 뽑은 데이터(used_for_calibration)는 따로 표시한다.
        #   그 데이터로 성능을 주장하면 자기 채점이다.
        rows.append((r.dataset, p, o, r.in_scope,
                     bool(getattr(r, "used_for_calibration", False))))

    print("=" * 84)
    print("데이터 투입량 → 절대오차 (held-out 측정)")
    print("=" * 84)
    print("⚠ 범위 밖(in_scope: false) 계열은 따로 센다 — 모델이 하지 않겠다고")
    print("  선언한 재료계까지 평균에 넣으면 진단이 흐려진다.")
    print()
    print(f"{'데이터셋':44s} {'n':>3s} {'1점':>7s} {'3점':>7s} {'5점':>7s} {'판정'}")

    improved = flat = worse = 0
    at1, at3, at5 = [], [], []
    oos_at1, oos_at5 = [], []
    oos_n = 0
    for name, p, o, in_scope, is_calib in rows:
        rep = learning_curve(p, o, series=name)
        if rep is None:
            continue
        d = dict(rep.curve)
        v1, v3, v5 = d.get(1), d.get(3), d.get(5)
        mark = ("✅" if rep.verdict.startswith("✅")
                else "🔴" if rep.verdict.startswith("🔴") else "⚠")
        f = lambda x: f"{x:6.1f}%" if x is not None else "     -"   # noqa: E731
        tag = ("  [범위밖]" if not in_scope
               else "  [캘리브]" if is_calib else "")
        print(f"{name[:44]:44s} {p.size:3d} {f(v1)} {f(v3)} {f(v5)}  {mark}{tag}")

        if not in_scope or is_calib:
            oos_n += 1
            if v1 is not None:
                oos_at1.append(v1)
            if v5 is not None:
                oos_at5.append(v5)
            continue      # 집계에서 제외

        if mark == "✅":
            improved += 1
        elif mark == "🔴":
            worse += 1
        else:
            flat += 1
        if v1 is not None:
            at1.append(v1)
        if v3 is not None:
            at3.append(v3)
        if v5 is not None:
            at5.append(v5)

    n_in = improved + flat + worse
    print()
    print("-" * 84)
    print(f"계열 {n_in}개 — 개선 {improved} · 평평 {flat} · 악화 {worse}")
    if at1:
        print()
        print("  투입 점수별 평균 절대오차 (**범위 안** 계열)")
        print(f"    1점 투입 → {np.mean(at1):6.1f}%   (기준 ≤ 30%)")
        if at3:
            print(f"    3점 투입 → {np.mean(at3):6.1f}%")
        if at5:
            print(f"    5점 투입 → {np.mean(at5):6.1f}%   (기준 ≤ 15%)")
    if oos_n:
        print()
        print(f"  집계 제외 {oos_n}개 (범위 밖 + 캘리브레이션 사용분, 참고용)")
        if oos_at1:
            print(f"    1점 투입 → {np.mean(oos_at1):6.1f}%")
        if oos_at5:
            print(f"    5점 투입 → {np.mean(oos_at5):6.1f}%")
        print("    → 이 숫자는 모델 성능이 아니라 **팩 커버리지 밖 외삽**을 보여준다.")

    print()
    print("=" * 84)
    print("해석")
    print("=" * 84)
    print("""
  ✅ 개선  : 축척 학습이 작동한다. 데이터를 넣을수록 절대값이 맞아간다.
  ⚠ 평평  : 남은 오차가 축척이 아니라 **형상**이다. 데이터를 더 넣어도
            줄지 않는다 — 구조를 고쳐야 하는 지점이다.
  🔴 악화  : 한 계열 안에 서로 다른 물리가 섞여 있다(계열 분할 필요).

  ⚠ 이 표는 성능 자랑이 아니라 **진단표**다. '평평'이 많으면 그 축의
    물리가 부족하다는 뜻이고, 그것이 다음에 고칠 목록이 된다.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
