"""알칼리 가지: 갈라진 두 k 가 'BTA 유무'인가 'pH 구간'인가를 데이터로 가른다.

왜 이 판정이 먼저인가
────────────────────
노트(cu-cmp-ph-mechanism.md §5.3)가 두 축이 얽혀 있다고 적고 스코프 밖으로
남겼다. 그 판단은 그 시점에 옳았다 — 데이터 두 계열로는 분리가 안 됐다.

그런데 지금은 검증 데이터가 늘었다. 구리 계열이 pH 3 / 7.2 / 8.5 / 9 / 10 / 11.1
로 퍼져 있고, BTA 유무도 갈린다. **2×2 로 놓이면 분리된다.**

분리되지 않으면 모델링하지 않는다 — 두 축이 얽힌 채로 항을 만들면
그 항은 물리가 아니라 그 데이터셋의 지문이 된다.

⚠ 추상화: 판정 기준에 물질명을 넣지 않는다. 기준은
  "억제제가 선언돼 있는가(유/무)" × "pH 가 골보다 위인가 아래인가" 두 축이다.
"""
import pathlib
import re
import sys
import warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                     # noqa: E402
import yaml                                            # noqa: E402

DS = ROOT / "validation" / "datasets"
VALLEY_PH = 6.25          # S3(pH 6) 와 S4(pH 6.5) 의 중간 — 골 위치

# 억제제 존재 여부 판정 (물질명이 아니라 '억제 작용기를 가진 첨가제가 선언됐는가')
INHIBITOR_PRESENT = re.compile(
    r"benzotriazole|\bBTA\b|triazole|imidazole|mercaptobenzothiazole|"
    r"\bMBT\b|nicotinic|quinaldic|tolyltriazole",
    re.IGNORECASE,
)


def main() -> int:
    print("=" * 84)
    print("구리 알칼리 가지 — 두 축이 분리되는가")
    print("=" * 84)
    print(f"골 위치 pH {VALLEY_PH} 기준 (S3=6.0, S4=6.5 의 중간)")
    print()

    cells = {}
    for path in sorted(DS.glob("*.yaml")):
        txt = path.read_text(encoding="utf-8")
        raw = yaml.safe_load(txt) or {}
        if str(raw.get("pack", "")) != "cu_h2o2_bta":
            continue
        conds = raw.get("conditions") or []
        phs, mrrs = [], []
        for c in conds:
            flat = dict(c)
            ov = flat.get("overrides")
            if isinstance(ov, dict):
                flat.update(ov)
            ph = flat.get("slurry_ph")
            mrr = flat.get("mrr_nm_per_min")
            if isinstance(ph, (int, float)) and isinstance(mrr, (int, float)):
                phs.append(float(ph))
                mrrs.append(float(mrr))
        if not phs:
            # pH 가 조건에 없으면 헤더 주석에서라도 읽는다(전달 누락 진단용)
            m = re.search(r"pH\s*([0-9]+(?:\.[0-9]+)?)", txt)
            note = f"pH≈{m.group(1)} (조건에 미전달)" if m else "pH 불명"
            print(f"  ⚠ {path.stem[:52]:52s} {note}")
            continue

        # ⚠ 원문 전체를 훑으면 "BTA 없음" 같은 **부정 서술**도 양성으로 잡힌다.
        #   실제로 그 오판이 났다(BTA 미함유 계열이 '억제제 유'로 분류됨).
        #   부정 표현이 붙어 있으면 '무'로 읽는다.
        neg = re.search(
            r"(BTA|benzotriazole|억제제)[^\n]{0,12}(없|미함유|무첨가|없음|free|without)"
            r"|(없|미함유|무첨가|without|free of)[^\n]{0,12}(BTA|benzotriazole|억제제)",
            txt, re.IGNORECASE)
        has_inh = bool(INHIBITOR_PRESENT.search(txt)) and not neg
        side = "알칼리" if float(np.mean(phs)) > VALLEY_PH else "산성"
        cells.setdefault((side, has_inh), []).append(
            (path.stem, np.array(phs), np.array(mrrs)))

    print()
    print(f"{'구간':8s} {'억제제':8s} {'계열':44s} {'n':>3s} {'k [/pH]':>9s} {'R²':>7s}")
    ks = {}
    for (side, has_inh), items in sorted(cells.items()):
        for name, phs, mrrs in items:
            if len(set(phs.tolist())) < 2:
                print(f"{side:8s} {'유' if has_inh else '무':8s} "
                      f"{name[:44]:44s} {len(phs):3d}   pH 단일값 — 기울기 불가")
                continue
            # ln(MRR) = a - k·pH  →  k 는 양수면 pH 증가 시 감소
            A = np.vstack([phs, np.ones_like(phs)]).T
            sol, *_ = np.linalg.lstsq(A, np.log(mrrs), rcond=None)
            slope, icept = sol
            pred = A @ sol
            ss_res = float(np.sum((np.log(mrrs) - pred) ** 2))
            ss_tot = float(np.sum((np.log(mrrs) - np.mean(np.log(mrrs))) ** 2))
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
            k = -float(slope)
            ks.setdefault((side, has_inh), []).append((name, k, r2, len(phs)))
            print(f"{side:8s} {'유' if has_inh else '무':8s} "
                  f"{name[:44]:44s} {len(phs):3d} {k:9.4f} {r2:7.4f}")

    print()
    print("-" * 84)
    print("셀별 요약 (2×2 가 채워지면 두 축이 분리된다)")
    grid = {}
    for (side, has_inh), items in ks.items():
        vals = [k for _, k, _, _ in items]
        grid[(side, has_inh)] = float(np.mean(vals))
        print(f"  {side} / 억제제 {'유' if has_inh else '무'}: "
              f"k = {np.mean(vals):.4f}  ({len(items)}계열)")

    print()
    print("=" * 84)
    filled = len(grid)
    print(f"채워진 셀: {filled}/4")
    print()
    if filled >= 3:
        print("  ✅ 분리 가능 — 두 축의 효과를 각각 읽을 수 있다.")
    else:
        print("  ❌ 아직 분리 불가 — 한 축을 고정한 데이터가 더 필요하다.")
        print("     ⚠ 이 상태에서 항을 만들면 두 효과가 한 계수에 뭉쳐")
        print("       그 데이터셋의 지문이 된다. 만들지 마라.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
