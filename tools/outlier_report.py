"""이상치 판정 규칙을 전 데이터셋에 적용해 무엇이 갈리는지 본다.

⚠ 이 스크립트는 규칙을 **적용만** 한다. 규칙을 조정해 지표를 올리는 데
  쓰면 안 된다 — 그 순간 규칙이 지표의 함수가 된다.
"""
import sys
import pathlib
import warnings
from collections import Counter

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                     # noqa: E402
from validation.backtest import run_all                # noqa: E402
from tools.outlier_rules import classify_point, bimodal_scale_split  # noqa: E402


def main() -> int:
    results = run_all()
    tally: Counter = Counter()
    print("=" * 84)
    print("이상치 판정 — 규칙 적용 결과 (지표를 보지 않고 판정)")
    print("=" * 84)

    splits = []
    per_ds = []
    for r in results:
        p = np.asarray(getattr(r, "predicted", []), dtype=float)
        o = np.asarray(getattr(r, "observed", []), dtype=float)
        if p.size == 0 or p.size != o.size:
            continue
        pack = getattr(r, "pack", "") or ""
        rows = getattr(r, "rows", None) or []
        notes_all = " ".join(getattr(r, "notes", []) or [])
        # C3(미지 상수)은 엔진이 그 조건에서 낸 경고로 판정한다.
        # 데이터셋 노트만 보면 못 잡히므로 실제 시뮬레이션 노트를 받아온다.
        if pack:
            try:
                from sim.engine import Recipe, simulate
                import sim.models  # noqa: F401
                probe = simulate(Recipe(pack=pack), model="tier2.gw_physical_kp")
                for fac in probe.factors.values():
                    notes_all += " " + " ".join(getattr(fac, "notes", []) or [])
            except Exception:
                pass

        codes = []
        for i in range(p.size):
            # 조건 입력은 최상위와 overrides 양쪽에 흩어져 있다.
            # 평탄화하지 않으면 게이트 판정이 볼 값이 없어 전부 C5 가 된다.
            inputs = {}
            if i < len(rows) and isinstance(rows[i], dict):
                src = dict(rows[i])
                ov = src.get("overrides")
                if isinstance(ov, dict):
                    src.update(ov)
                inputs = {k: float(v) for k, v in src.items()
                          if isinstance(v, (int, float)) and not isinstance(v, bool)}
            v = classify_point(float(p[i]), float(o[i]), inputs, pack, notes_all)
            codes.append(v.code)
            tally[v.code] += 1
        c = Counter(codes)
        per_ds.append((r.dataset, p.size, c, getattr(r, "in_scope", True)))

        sp = bimodal_scale_split(p, o)
        if sp is not None:
            splits.append((r.dataset, sp[2]))

    print(f"{'데이터셋':46s} {'n':>3s}  판정 분포")
    for name, n, c, in_scope in per_ds:
        dist = " ".join(f"{k}:{v}" for k, v in sorted(c.items()))
        tag = "" if in_scope else " [범위밖]"
        print(f"{name[:46]:46s} {n:3d}  {dist}{tag}")

    print()
    print("-" * 84)
    print("전체 판정 분포")
    LABEL = {
        "C1": "물리 불가 — 제거 (데이터 전사 오류)",
        "C2": "정의역 밖 — 제거 (외삽, 게이트 기록)",
        "C3": "미지 상수 — 순위만 유지 (R8 발행)",
        "C4": "계열 혼재 — 분할",
        "C5": "설명 불가 — **남긴다** (진짜 모델 갭)",
    }
    total = sum(tally.values())
    for k in ("C1", "C2", "C3", "C4", "C5"):
        if tally[k]:
            print(f"  {k}  {tally[k]:4d}점 ({tally[k]/total*100:4.1f}%)  {LABEL[k]}")

    if splits:
        print()
        print("-" * 84)
        print("C4 — 계열 분할 후보 (제거가 아니라 분할이다)")
        for name, msg in splits:
            print(f"  · {name}")
            print(f"      {msg}")

    print()
    print("=" * 84)
    print(f"""
  제거 대상    : C1 + C2 = {tally['C1'] + tally['C2']}점
  순위만 유지  : C3 = {tally['C3']}점
  남기는 이상치: C5 = {tally['C5']}점  ← 이것이 다음에 고칠 물리다

  ⚠ C5 를 제거하면 지표는 오르지만 모델은 그대로다.
    설명할 수 없는 이상치는 지우지 않는다.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
