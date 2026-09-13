"""과적합 감시 — 모델이 데이터를 설명하는가, 외우는가.

왜 이 도구가 필요한가
────────────────────
검증 지표(ρ, MAPE)는 좋아지는 방향이 하나뿐이라 **올리는 것 자체가 목적이 되기
쉽다.** 지표를 올리는 방법은 두 가지인데 겉보기로는 구분되지 않는다:

    (a) 물리를 제대로 넣었다        → 본 적 없는 조건에서도 맞는다
    (b) 자유 파라미터를 늘렸다      → 맞춘 조건에서만 맞는다

(b)는 지표상으로 (a)보다 우수해 보이기까지 한다. 그래서 사람이 눈으로 막을 수
없고, 기계가 별도 기준으로 감시해야 한다.

이 도구가 보는 것 (입력 → 판단 기준 → 출력)
─────────────────────────────────────────
G1 자유도 예산
   입력: 손으로 선언된 파라미터 수, 검증 조건 수
   판단: 조건/파라미터 비. 낮으면 모델이 데이터를 외울 여지가 크다.
   출력: 비율과 등급

G2 유도 비율
   입력: 파라미터별로 '이론에서 계산된 것'인지 '손으로 넣은 것'인지
   판단: 유도된 파라미터는 자유도를 소비하지 않는다 — 물성이 정하기 때문이다.
         손으로 넣은 비율이 높을수록 회귀식에 가깝다.
   출력: 유도 비율

G3 편중
   입력: 팩별 손선언 파라미터 수
   판단: 특정 계에만 파라미터가 몰리면 그것은 절차가 아니라 그 계 전용 보정이다.
   출력: 편중 지수 (최대/중앙)

G4 일반화 격차
   입력: 캘리브레이션에 쓴 데이터의 성능, 쓰지 않은 데이터의 성능
   판단: 둘의 격차가 크면 맞춘 곳에서만 맞는다는 뜻이다.
   출력: 격차

G5 근거 등급 분포
   입력: 파라미터별 confidence
   판단: unverified/estimated 비중이 높은데 지표가 좋으면, 그 성능은 근거가
         아니라 조정에서 나왔을 가능성이 크다.
   출력: 등급별 분포

어느 판단 기준에도 물질명이 없다. 어떤 슬러리가 들어와도 같은 질문을 던진다.

⚠ 이 도구는 "과적합이다/아니다"를 단정하지 않는다. 단정할 수 있는 통계가 아니다.
   대신 **위험 신호**를 정량화해, 지표가 올랐을 때 그것이 어느 쪽인지 물어보게 한다.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

# 손으로 정하는 성격의 파라미터를 식별한다.
#
# ⚠ 기준점(_ref)은 자유도가 **아니다.** 기준점은 "어느 조건에서 축척(Kp)을
#   역산했는가"를 가리키는 좌표일 뿐이고, 본값과 함께 움직이면 예측을 바꾸지
#   않는다(비가 기준점 선택과 무관해야 한다는 것이 모델의 계약이다).
#   기준점을 자유도로 세면 자유도가 두 배로 부풀어, 실제로는 없는 위험을
#   보고하게 된다. 그래서 제외한다.
#
# 자유도로 세는 것: 곡선의 **모양**을 정하는 값 — 지수·정점 위치·이득·바닥값.
# 이들은 바꾸면 예측 형상이 바뀌므로 데이터를 외울 여지를 만든다.
FIT_MARKERS = ("_exponent", "exp_", "_peak", "peak_", "_gain",
               "_floor", "_coeff", "_factor")

# 기준점은 명시적으로 제외한다(위 설명 참조).
REF_MARKERS = ("_ref", "ref_")

# 물성(측정 가능한 값)은 자유도가 아니다 — 재면 정해지기 때문이다.
MEASURED_MARKERS = ("_pa", "_nm", "_m2", "_per_m2", "_mm", "_um", "_psi",
                    "_wt_pct", "_mM", "_pct", "_s", "_c", "_cpm")

GRADE_ORDER = ["unverified", "estimated", "literature", "measured", "verified"]


@dataclass
class Signal:
    code: str
    label: str
    value: float
    verdict: str          # ok | watch | risk
    detail: str
    advice: str = ""


def _packs() -> List[str]:
    from sim.params import available_packs
    return [p for p in available_packs() if p != "base"]


def _is_fit_param(key: str) -> bool:
    """이 파라미터가 자유도를 소비하는가.

    판단: 이름이 '어느 조건에서 맞췄는가'를 담는 역할이면 자유도다.
          측정하면 정해지는 물성이면 자유도가 아니다.
    """
    k = key.lower()
    if any(m in k for m in REF_MARKERS):
        return False          # 기준점은 좌표이지 자유도가 아니다
    if any(m in k for m in FIT_MARKERS):
        return True
    return False


def collect_params() -> Dict[str, Dict[str, object]]:
    """팩별로 '직접 선언한' 파라미터와 그 성격을 모은다."""
    from sim.params import load_pack
    out: Dict[str, Dict[str, object]] = {}
    for p in _packs():
        try:
            pk = load_pack(p)
        except Exception:
            continue
        own = [k for k in pk.params if pk.has_own(k)]
        fit = [k for k in own if _is_fit_param(k)]
        grades: Dict[str, int] = {}
        for k in own:
            try:
                g = str(pk.param(k).confidence or "unknown")
            except Exception:
                g = "unknown"
            grades[g] = grades.get(g, 0) + 1
        out[p] = {"own": own, "fit": fit, "grades": grades}
    return out


def count_conditions() -> Dict[str, int]:
    """검증 조건 수 — 캘리브레이션에 쓴 것과 아닌 것을 나눈다."""
    held = calib = 0
    for f in sorted((ROOT / "validation" / "datasets").glob("*.yaml")):
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if f.stem.startswith("_"):
            continue
        n = len([c for c in (d.get("conditions") or [])
                 if "mrr_nm_per_min" in c])
        if not d.get("in_scope", True):
            continue
        if d.get("used_for_calibration", False):
            calib += n
        else:
            held += n
    return {"held_out": held, "calibration": calib}


def derived_fraction() -> Optional[float]:
    """지수 중 이론에서 유도되는 비율.

    유도된 값은 물성이 정하므로 자유도를 소비하지 않는다. 이 비율이 오르면
    같은 데이터로도 과적합 위험이 내려간다.
    """
    try:
        from sim.params import load_pack
        from sim.regime_adapter import exponents_for
    except Exception:
        return None
    tot = der = 0
    for p in _packs():
        try:
            ex = exponents_for(load_pack(p), 3.0)
        except Exception:
            continue
        tot += 1
        if ex.get("derived"):
            der += 1
    return (der / tot) if tot else None


def generalization_gap() -> Optional[Dict[str, float]]:
    """캘리브레이션에 쓴 데이터와 쓰지 않은 데이터의 성능 격차.

    격차가 크면 '맞춘 곳에서만 맞는다'는 뜻이다. 지표 자체보다 이 격차가
    과적합을 더 직접적으로 가리킨다.
    """
    sys.path.insert(0, str(ROOT / "validation"))
    try:
        import backtest as BT
    except Exception:
        return None
    import numpy as np

    groups: Dict[str, List[float]] = {"held": [], "calib": []}
    for f in sorted((ROOT / "validation" / "datasets").glob("*.yaml")):
        if f.stem.startswith("_"):
            continue
        try:
            res = BT.run_dataset(f)
        except Exception:
            continue
        # 결과 객체가 스스로 신고하는 값을 쓴다 — YAML 을 두 번 해석하면
        # 해석이 갈릴 수 있다(속성명·기본값 규칙은 backtest 가 정본).
        if not getattr(res, "in_scope", True):
            continue
        rho = getattr(res, "spearman", None)
        if rho is None or rho != rho:
            continue
        key = "calib" if getattr(res, "used_for_calibration", False) else "held"
        groups[key].append(float(rho))

    if not groups["held"] or not groups["calib"]:
        return None
    return {
        "calibration_rho": float(np.mean(groups["calib"])),
        "held_out_rho": float(np.mean(groups["held"])),
        "gap": float(np.mean(groups["calib"]) - np.mean(groups["held"])),
    }


def run(verbose: bool = True) -> List[Signal]:
    sig: List[Signal] = []
    params = collect_params()
    conds = count_conditions()

    fit_total = sum(len(v["fit"]) for v in params.values())  # type: ignore[arg-type]
    own_total = sum(len(v["own"]) for v in params.values())  # type: ignore[arg-type]
    held = conds["held_out"]

    # ── G1 자유도 예산 ─────────────────────────────────────────────
    ratio = (held / fit_total) if fit_total else float("inf")
    verdict = "ok" if ratio >= 10 else ("watch" if ratio >= 5 else "risk")
    sig.append(Signal(
        "G1", "자유도 예산 (검증조건 / 자유파라미터)", round(ratio, 2), verdict,
        f"held-out 조건 {held}개 vs 손선언 자유파라미터 {fit_total}개",
        "비가 낮으면 모델이 데이터를 설명하는 게 아니라 외울 여지가 커진다. "
        "올리는 방법은 둘 뿐이다 — 조건을 늘리거나, 파라미터를 이론으로 "
        "유도해 자유도에서 빼거나. 후자가 근본적이다."))

    # ── G2 유도 비율 ───────────────────────────────────────────────
    dfrac = derived_fraction()
    if dfrac is not None:
        verdict = "ok" if dfrac >= 0.8 else ("watch" if dfrac >= 0.4 else "risk")
        sig.append(Signal(
            "G2", "지수 유도 비율", round(dfrac, 3), verdict,
            f"지수를 이론에서 계산해내는 팩의 비율 {dfrac*100:.0f}%",
            "유도된 값은 물성이 정하므로 자유도를 소비하지 않는다. 이 비율이 "
            "오르면 같은 데이터로도 과적합 위험이 내려간다."))

    # ── G3 편중 ────────────────────────────────────────────────────
    counts = sorted(len(v["fit"]) for v in params.values())  # type: ignore[arg-type]
    if counts:
        import statistics
        med = statistics.median(counts) or 1
        skew = max(counts) / med
        verdict = "ok" if skew <= 2 else ("watch" if skew <= 3.5 else "risk")
        worst = max(params.items(), key=lambda kv: len(kv[1]["fit"]))  # type: ignore[arg-type]
        sig.append(Signal(
            "G3", "파라미터 편중 (최대/중앙)", round(skew, 2), verdict,
            f"가장 많은 계가 {len(worst[1]['fit'])}개, 중앙값 {med:.0f}개",
            "특정 계에만 파라미터가 몰리면 그것은 일반 절차가 아니라 그 계 전용 "
            "보정이다. 다른 계에 적용했을 때 성립하는지 확인하라."))

    # ── G4 일반화 격차 ─────────────────────────────────────────────
    gap = generalization_gap()
    if gap:
        g = gap["gap"]
        verdict = "ok" if g <= 0.1 else ("watch" if g <= 0.25 else "risk")
        sig.append(Signal(
            "G4", "일반화 격차 (캘리브레이션 ρ − held-out ρ)", round(g, 3), verdict,
            f"캘리브레이션 ρ={gap['calibration_rho']:+.3f} · "
            f"held-out ρ={gap['held_out_rho']:+.3f}",
            "격차가 크면 맞춘 곳에서만 맞는다는 뜻이다. 지표 자체보다 이 격차가 "
            "과적합을 더 직접적으로 가리킨다."))

    # ── G5 근거 등급 분포 ──────────────────────────────────────────
    allg: Dict[str, int] = {}
    for v in params.values():
        for g, n in (v["grades"] or {}).items():  # type: ignore[union-attr]
            allg[g] = allg.get(g, 0) + n
    weak = sum(allg.get(g, 0) for g in ("unverified", "estimated", "unknown"))
    frac_weak = weak / own_total if own_total else 0.0
    verdict = "ok" if frac_weak <= 0.3 else ("watch" if frac_weak <= 0.5 else "risk")
    sig.append(Signal(
        "G5", "약한 근거 비율", round(frac_weak, 3), verdict,
        f"unverified+estimated {weak} / 전체 {own_total} · 분포 {allg}",
        "약한 근거 비중이 높은데 지표가 좋다면, 그 성능은 근거가 아니라 조정에서 "
        "나왔을 가능성이 크다. 지표와 근거는 함께 올라야 한다."))

    if verbose:
        _print(sig, params, conds)
    return sig


def _print(sig: List[Signal], params, conds) -> None:
    ICON = {"ok": "✅", "watch": "🟡", "risk": "🔴"}
    print("=" * 78)
    print(" 과적합 감시 — 모델이 데이터를 설명하는가, 외우는가")
    print("=" * 78)
    for s in sig:
        print(f"{ICON[s.verdict]} [{s.code}] {s.label}: {s.value}")
        print(f"     {s.detail}")
        if s.verdict != "ok":
            print(f"     → {s.advice}")
    print("-" * 78)
    risk = sum(1 for s in sig if s.verdict == "risk")
    watch = sum(1 for s in sig if s.verdict == "watch")
    print(f"위험 {risk} · 주의 {watch} · 정상 {len(sig)-risk-watch}")
    print()
    print("팩별 자유파라미터:")
    for p, v in sorted(params.items(), key=lambda kv: -len(kv[1]["fit"])):
        print(f"  {p:20s} {len(v['fit']):2d}개  {sorted(v['fit'])}")


def main() -> int:
    ap = argparse.ArgumentParser(description="과적합 위험 신호 측정")
    ap.add_argument("--json", action="store_true", help="JSON 으로 출력")
    ap.add_argument("--fail-on-risk", action="store_true",
                    help="위험 신호가 있으면 exit 1")
    a = ap.parse_args()

    sig = run(verbose=not a.json)
    if a.json:
        print(json.dumps([asdict(s) for s in sig], ensure_ascii=False, indent=2))
    if a.fail_on_risk and any(s.verdict == "risk" for s in sig):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
