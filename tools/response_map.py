#!/usr/bin/env python3
"""응답 지도 — "어떤 인자를 어떻게 움직이면 결과가 어떻게 바뀌나"를 팩 전체에 대해 재고,
그 응답 형상을 문헌 실측 형상과 **같은 구간에서** 대조한다.

사용자 지시 (2026-09-08):
  "특허든 문헌이든 오픈소스 데이터든, 그냥 단순히 그 데이터를 시뮬레이션하는게 목적이
   아님. 신규 셋업을 위해서 공정 및 슬러리 개발하는게 목적이고 이 개발의 tool로서
   시뮬레이션을 사용하려는거임. 그런 관점에서 볼 때 적용시, 특정 슬러리 하나하나
   구분하는것보단 어떤 요인이 결과를 어떻게 바꾸는지 파악하는데 중점을 둬"

왜 별도 도구인가 — 기존 두 도구는 목표함수가 다르다
────────────────────────────────────────────────
  · `backtest.py`  : "이 논문의 이 슬러리를 맞히나" — 데이터셋(=특정 슬러리) 단위 채점.
                     순위 ρ가 높아도 **어떤 인자가 그 순위를 만들었는지는 모른다.**
  · `--sensitivity`: 현재 한 점에서의 국소 기울기. **정점·골·포화를 못 본다**
                     (정점 위에 앉아 있으면 탄성도 0이라 "무영향"과 구분이 안 된다).

신규 셋업용 개발 도구가 답해야 하는 질문은 그 둘이 아니라 이것이다:

    "이 인자를 이 구간에서 움직이면 결과가 어느 방향으로 얼마나 가나,
     그리고 그 방향이 문헌에서 관측된 방향과 같은가?"

이 도구는 인자 하나를 스윕해 **응답 형상**(단조↑/단조↓/정점/골/포화/무반응)과
**변화폭**(max/min)을 내고, 같은 인자를 단독 변화시킨 문헌 데이터셋에서 관측된 형상과
대조한다. 판정은 다섯 중 하나:

  ✅ AGREE      모델 형상 = 문헌 형상            → 그 구간에서 방향 예측에 써도 된다
  ❌ CONFLICT   방향이 반대 / 정점·골을 놓침      → **틀린 방향을 가리킨다. 가장 위험**
  ⚠ NO-DATA    모델은 반응하는데 문헌 근거 없음   → 응답 형상이 지어낸 것일 수 있다
  🕳 DEAD       문헌은 변하는데 모델 무반응       → 개발 도구로서 그 축이 통째로 비어 있다
  ·  N/A        이 팩에 그 인자 자체가 없다       → 갭이 아니다(Cu 팩에 Ce³⁺ 등)

CONFLICT와 DEAD가 최우선 갭이다. accuracy_gaps.py의 UNMODELED가 "팩터 코드가
미모델링"이라는 **코드 상태**를 보는 반면, 여기는 **입력→출력 실제 응답**을 본다.
팩터가 modeled여도 응답이 평평하면(이중 계상 상쇄·포화·Kp 역산 흡수) 여기서만 잡힌다.

## 비교의 정직성 — 여기서 틀리기 쉬운 세 가지

1. **구간을 맞춰라.** 모델을 실무 범위 전체(pH 2~11)로 스윕하고 문헌은 산성만(pH 2~6)
   보면 "모델 단조↑ vs 문헌 골"이라는 가짜 충돌이 난다. 판정용 스윕은 **문헌 x 범위로
   다시** 돌린다.
2. **여러 데이터셋을 풀링할 땐 절대 스케일을 지워라.** 논문마다 장비·막질이 달라
   MRR 절대값이 다르다. 각 데이터셋을 자기 중앙값으로 나눈 뒤 x로 정렬해 합친다.
3. **캘리브레이션 출처는 판정에서 뺀다.** 그 데이터로 팩 상수를 뽑았으면 형상이
   맞는 게 당연하다 — 자기 답안지 채점이다. 표에는 `(calib)`로 따로 보인다.
   교란(한 데이터셋에서 인자가 2개 이상 동시 변화, 직교표 L9 등)도 판정에서 뺀다.

사용법
  tools/response_map.py                     # 전 팩 × 전 인자 요약표
  tools/response_map.py --pack oxide_silica
  tools/response_map.py --knob slurry_ph    # 인자 하나의 스윕 곡선 + 문헌 점
  tools/response_map.py --gaps              # CONFLICT/DEAD 랭킹 (크론 배차용)
  tools/response_map.py --evidence          # 문헌에서 뽑은 형상 원장
  tools/response_map.py --json
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.engine import Recipe, simulate  # noqa: E402
import sim.models  # noqa: E402,F401
from sim.params import available_packs, load_pack  # noqa: E402
from sim.sensitivity import FACTORS, CANCELLED_BY_CALIBRATION, UNMODELED_HINT  # noqa: E402

MODEL = "tier2.gw_physical_kp"
N_STEPS = 9
FLAT_TOL = 0.02      # (max/min - 1) 이 이하면 무반응
EDGE_FRAC = 0.15     # 정점/골이 양 끝에서 이만큼 안쪽에 있어야 인정
MIN_LIT_N = 3


# ── 응답 형상 분류 ────────────────────────────────────────────
def classify(xs: List[float], ys: List[float]) -> Tuple[str, float]:
    """(x로 정렬된) 스윕 결과를 형상 라벨과 변화폭(max/min)으로 요약."""
    if len(ys) < 3 or min(ys) <= 0:
        return "invalid", float("nan")
    span = max(ys) / min(ys)
    if span - 1.0 < FLAT_TOL:
        return "flat", span
    n = len(ys)
    i_max, i_min = int(np.argmax(ys)), int(np.argmin(ys))

    def inner(i: int) -> bool:
        return EDGE_FRAC * (n - 1) <= i <= (1 - EDGE_FRAC) * (n - 1)

    # 정점/골 판정은 "끝점보다 얼마나 튀어나왔나"로 보강한다 —
    # 노이즈 한 점이 안쪽에 있다고 정점이라 부르면 안 된다.
    ends = (ys[0], ys[-1])
    if inner(i_max) and ys[i_max] / max(ends) > 1.05:
        return "peak", span
    if inner(i_min) and min(ends) / ys[i_min] > 1.05:
        return "valley", span
    if ys[-1] > ys[0]:
        d1 = abs(ys[n // 2] - ys[0])
        d2 = abs(ys[-1] - ys[n // 2])
        if d1 > 0 and d2 / d1 < 0.2:
            return "saturating", span
        return "up", span
    return "down", span


SHAPE_KO = {"up": "단조↑", "down": "단조↓", "peak": "정점", "valley": "골",
            "saturating": "포화↑", "flat": "무반응", "invalid": "계산불가",
            "unknown": "-", "na": "없음"}

# 방향이 같다고 인정하는 (모델, 문헌) 쌍. 포화↑와 단조↑는 같은 방향으로 본다
# — 실무 판단("올리면 오른다")이 동일하기 때문이다. 정점/골은 서로 다르면 충돌이다.
SAME_DIR = {("up", "up"), ("saturating", "up"), ("up", "saturating"),
            ("saturating", "saturating"), ("down", "down"),
            ("peak", "peak"), ("valley", "valley")}


def verdict_of(model_shape: str, lit_shape: str) -> str:
    if model_shape == "na":
        return "N/A"
    if lit_shape in ("unknown", None):
        return "NO-DATA" if model_shape not in ("flat", "invalid") else "BLANK"
    if model_shape in ("flat", "invalid"):
        return "DEAD"
    return "AGREE" if (model_shape, lit_shape) in SAME_DIR else "CONFLICT"


# EVIDENCE-RULES.md 판정으로 "무반응(DEAD)"이 아니라 "검증된 영(null) 결과"로 종결된 (팩, 인자) 쌍.
# 이 표에 있으면 DEAD 갭으로 다시 배차하지 않는다 — 무한 재시도를 막기 위한 장치
# (EVIDENCE-RULES.md §금지: "판정을 미루고 미반영으로 남기는 것은 3회차까지만 허용").
NULL_CONFIRMED = {
    ("cu_h2o2_bta", "abrasive_size_nm"):
        "EVIDENCE-RULES.md 판정 #1 (2026-09-11): 교란(형상) 분리 후 순수구형 부분집합 "
        "비유의(ρ≈0.03~0.15) + Chen thesis 단층모델 d⁻²×d⁺² 상쇄 이론이 합의 — "
        "cu_h2o2_bta 계에서 입경은 MRR 지배인자가 아님. 지수 0.0은 검증된 결론.",
}


VERDICT_MARK = {"AGREE": "✅", "CONFLICT": "❌", "NO-DATA": "⚠", "DEAD": "🕳", "NULL_CONFIRMED": "∅",
                "MISSING": "🔲", "BLANK": "·", "N/A": "·"}


# ── 모델 스윕 ────────────────────────────────────────────────
def _recipe(pack: str, f, x: float) -> Recipe:
    if f.where == "recipe":
        return Recipe(pack=pack, **{f.key: x})
    return Recipe(pack=pack, pack_overrides={f.key: x})


def _pack_has(pack: str, f) -> bool:
    """이 팩에 이 인자가 실제로 있는가. 없으면 갭이 아니라 N/A다."""
    if f.where == "recipe":
        return True
    try:
        return load_pack(pack).has(f.key)
    except Exception:
        return False


def sweep(pack: str, f, rng: Optional[Tuple[float, float]] = None,
          n: int = N_STEPS) -> Optional[Dict]:
    rng = rng or f.practical_range
    if not rng:
        return None
    lo, hi = rng
    if lo <= 0 or hi <= lo:
        return None
    xs = [math.exp(t) for t in np.linspace(math.log(lo), math.log(hi), n)]
    ok, mrr, ttv = [], [], []
    for x in xs:
        try:
            r = simulate(_recipe(pack, f, x), model=MODEL)
        except Exception:
            continue
        ok.append(float(x))
        mrr.append(float(np.mean(r.mrr_nm_per_min)))
        ttv.append(float(r.metrics.ttv_nm))
    if len(ok) < 3:
        return None
    shape, span = classify(ok, mrr)
    tshape, tspan = classify(ok, ttv)
    return {"xs": ok, "mrr": mrr, "ttv": ttv, "shape": shape, "span": span,
            "ttv_shape": tshape, "ttv_span": tspan, "range": [lo, hi]}


def why_flat(f) -> str:
    if f.key in CANCELLED_BY_CALIBRATION:
        return "[유형C] Kp 역산이 효과를 상쇄 — 서로 다른 패드의 실측 2점이 있어야 풀린다(M3)"
    if f.key in UNMODELED_HINT:
        return UNMODELED_HINT[f.key]
    return "엔진이 이 인자를 쓰지 않는다 — '영향 없음'이 아니라 '미구현'이다"


# ── 문헌 증거 ────────────────────────────────────────────────
def _quarantined() -> set:
    """qa_loop 가 격리한 데이터셋 — 응답 판정에서도 빼야 한다.

    ⚠ 왜 필요하냐면, 백테스트(validation/backtest.py)는 quarantine.json 을 적용하는데
    이 도구는 안 봐서 **격리된 데이터가 여기서만 증거로 살아 있었다**(2026-09-15 발견:
    us9200180b2_cu_abrasive_series 가 F4 캘리브레이션 오염으로 격리된 상태에서
    cu_h2o2_bta/pH 판정의 유일한 근거였다). 한 저장소 안에서 같은 데이터가 한 도구에는
    부적격이고 다른 도구에는 적격이면, 갭 랭킹 전체를 못 믿는다.
    """
    f = ROOT / "validation" / "quarantine.json"
    if not f.exists():
        return set()
    try:
        return set(json.loads(f.read_text(encoding="utf-8")).keys())
    except Exception:
        return set()


QUARANTINED = _quarantined()


@dataclass
class Evidence:
    key: str
    dataset: str
    pack: Optional[str]
    n: int
    shape: str
    span: float
    x_lo: float
    x_hi: float
    xs: List[float]
    ys: List[float]          # 데이터셋 중앙값으로 정규화한 MRR
    confounded: bool
    n_varying: int
    in_scope: bool
    calib: bool
    read: str

    quarantined: bool = False

    def usable(self) -> bool:
        return (not self.confounded and self.in_scope and not self.calib
                and not self.quarantined and self.n >= MIN_LIT_N)


def _cond_value(cond: Dict, key: str) -> Optional[float]:
    ov = cond.get("overrides") or {}
    src = ov if key in ov else cond
    if key not in src:
        return None
    try:
        return float(src[key])
    except (TypeError, ValueError):
        return None


# 데이터셋 조건 딕셔너리에서 '입력'이 아닌 키(출력·메타)를 걸러내는 패턴.
# 이걸 안 걸면 measured_mrr_* 같은 결과 컬럼이 교란요인으로 잡혀 정상 데이터셋이
# 통째로 판정에서 빠진다.
_NON_DRIVER_KEYS = {"label", "overrides", "notes", "note", "read_method",
                    "mrr_nm_per_min", "source", "comment"}
_OUTPUT_LIKE = re.compile(
    r"(^measured_|mrr|removal_rate|roughness|defect|dishing|erosion|"
    r"ttv|wiwnu|nonuniform|selectivity|_out$)", re.I)


def _drivers(conds: List[Dict]) -> List[str]:
    """이 데이터셋에서 **실제로 움직인 입력** 전부.

    ⚠ 왜 FACTORS 키로 한정하면 안 되나 — 교란 판정은 "모델이 아는 축"이 아니라
    "실험에서 변한 축" 기준이어야 한다. abrasive_wt_pct 처럼 FACTORS 에 없는
    입력이 같이 움직이는데 그걸 못 보면, 교란 데이터셋을 '단독 변화'로 착각해
    판정에 쓴다(2026-09-15 발견: us9200180b2_cu_abrasive_series 가 실리카
    0.5→20 wt% 와 pH 9.2→10.0 을 동시에 움직였는데 pH 단독 증거로 채점돼
    cu_h2o2_bta/pH 에 DEAD 를 찍고 있었다).
    """
    cand = set()
    for c in conds:
        for k in list(c.keys()) + list((c.get("overrides") or {}).keys()):
            if k in _NON_DRIVER_KEYS or _OUTPUT_LIKE.search(k):
                continue
            cand.add(k)
    out = []
    for k in sorted(cand):
        vals = [_cond_value(c, k) for c in conds]
        if any(v is None for v in vals):
            continue          # 일부 조건에만 있는 키는 축으로 못 쓴다
        if len({round(v, 9) for v in vals}) >= 2:
            out.append(k)
    return out


def _strata(conds: List[Dict], key: str, others: List[str]) -> List[List[Dict]]:
    """나머지 입력을 전부 고정한 부분집합(층)으로 쪼갠다.

    완전교차 DOE(예: pH 4수준 × 실리카 5수준)는 통째로 보면 '2인자 동시변화'라
    판정에서 빠지지만, 실리카를 고정한 층 안에서는 pH 가 **단독으로** 변한다.
    그 층이 곧 통제된 증거다. 버리지 말고 층별로 쓴다.
    """
    groups: Dict[Tuple, List[Dict]] = {}
    for c in conds:
        sig = tuple(round(_cond_value(c, o), 9) for o in others)
        groups.setdefault(sig, []).append(c)
    ok = []
    for g in groups.values():
        xs = {round(_cond_value(g_i, key), 9) for g_i in g}
        if len(xs) >= MIN_LIT_N:
            ok.append(g)
    return ok


def literature_evidence() -> List[Evidence]:
    out: List[Evidence] = []
    keys = [f.key for f in FACTORS]
    for path in sorted((ROOT / "validation" / "datasets").glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        d = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        conds = [c for c in (d.get("conditions") or [])
                 if c.get("mrr_nm_per_min") is not None]
        if len(conds) < MIN_LIT_N:
            continue
        pack = d.get("pack")
        in_scope = d.get("in_scope") is not False
        calib = bool(d.get("used_for_calibration"))
        drivers = _drivers(conds)
        reads = {c.get("read_method", "?") for c in conds}
        read = "digitized" if "digitized" in reads else "table"
        for k in keys:
            vals = [_cond_value(c, k) for c in conds]
            if any(v is None for v in vals):
                continue
            if len({round(v, 9) for v in vals}) < MIN_LIT_N:
                continue
            others = [o for o in drivers if o != k]
            strata = _strata(conds, k, others) if others else [conds]
            if strata:
                # 통제된 층이 있다 → 층마다 자기 중앙값으로 정규화해 합친다.
                # (층끼리 절대 스케일이 다르므로 정규화 없이 합치면 형상이 뭉갠다.)
                pts = []
                for g in strata:
                    med = float(np.median([float(c["mrr_nm_per_min"]) for c in g])) or 1.0
                    pts += [(_cond_value(c, k), float(c["mrr_nm_per_min"]) / med)
                            for c in g]
                pts.sort()
                confounded = False
                n_varying = 1
            else:
                # 통제된 층이 없다 → 종전대로 전체를 쓰되 교란으로 표시해 판정에서 뺀다.
                med = float(np.median([float(c["mrr_nm_per_min"]) for c in conds])) or 1.0
                pts = sorted((_cond_value(c, k), float(c["mrr_nm_per_min"]) / med)
                             for c in conds)
                confounded = True
                n_varying = len(drivers)
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if min(ys) <= 0:
                continue
            shape, span = classify(xs, ys)
            out.append(Evidence(
                k, path.stem, pack, len(pts), shape, span, xs[0], xs[-1], xs, ys,
                confounded=confounded, n_varying=n_varying,
                in_scope=in_scope, calib=calib, read=read,
                quarantined=path.stem in QUARANTINED))
    return out


def pooled(ev: List[Evidence], key: str, pack: str) -> Optional[Dict]:
    """판정에 쓸 문헌 형상. 같은 팩·in_scope·비교란·비캘리브레이션만 풀링한다.

    데이터셋마다 절대 스케일이 다르므로 각자 중앙값으로 정규화한 뒤(Evidence 생성 시
    이미 처리) x로 정렬해 합친다. 겹치는 구간이 있으면 형상이 그대로 드러난다.
    """
    use = [e for e in ev if e.key == key and e.pack == pack and e.usable()]
    if not use:
        return None
    pts = sorted((x, y) for e in use for x, y in zip(e.xs, e.ys))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    shape, span = classify(xs, ys)
    return {"shape": shape, "span": span, "n": len(xs),
            "x_lo": xs[0], "x_hi": xs[-1],
            "datasets": [e.dataset for e in use],
            "digitized": any(e.read == "digitized" for e in use),
            "xs": xs, "ys": ys}


# ── 리포트 조립 ──────────────────────────────────────────────
def build(packs: List[str]) -> Dict:
    ev = literature_evidence()
    rows = []
    for p in packs:
        for f in FACTORS:
            if not _pack_has(p, f):
                # 팩에 파라미터가 없다. 문헌 증거도 없으면 갭이 아니지만(Cu 팩의 Ce³⁺),
                # 문헌이 그 인자로 MRR이 변한다고 말하는데 팩에 칸조차 없으면
                # 그건 조용한 N/A가 아니라 **누락**이다 — 소재 개발자가 못 만지는 축이 된다.
                lit0 = pooled(ev, f.key, p)
                rows.append({"pack": p, "key": f.key, "label": f.label,
                             "domain": f.domain, "model_shape": "na", "span": float("nan"),
                             "ttv_shape": "na",
                             "lit_shape": lit0["shape"] if lit0 else "unknown",
                             "lit_n": lit0["n"] if lit0 else 0,
                             "lit_sets": lit0["datasets"] if lit0 else [],
                             "lit_digitized": bool(lit0 and lit0["digitized"]),
                             "verdict": "MISSING" if lit0 else "N/A",
                             "note": "이 팩에 이 파라미터 자체가 없다 — 팩 YAML에 "
                                     "문헌값으로 추가해야 인자가 살아난다",
                             "xs": [], "mrr": [], "ttv": [], "cmp_range": None,
                             "lit_pts": list(zip(lit0["xs"], lit0["ys"])) if lit0 else []})
                continue
            full = sweep(p, f)
            if full is None:
                continue
            lit = pooled(ev, f.key, p)
            # ── 판정은 문헌과 같은 구간에서 다시 스윕해 비교한다
            if lit and lit["x_hi"] > lit["x_lo"] > 0:
                cmp_sw = sweep(p, f, (lit["x_lo"], lit["x_hi"])) or full
                cmp_range = [lit["x_lo"], lit["x_hi"]]
            else:
                cmp_sw, cmp_range = full, None
            v = verdict_of(cmp_sw["shape"], lit["shape"] if lit else "unknown")
            note = why_flat(f) if cmp_sw["shape"] == "flat" else ""
            # DEAD여도 EVIDENCE-RULES.md가 이미 "검증된 영 결과"로 종결한 축이면
            # 무한 재배차를 막는다 — 갭이 사라지는 게 아니라 종류가 바뀐다.
            if v == "DEAD" and (p, f.key) in NULL_CONFIRMED:
                v = "NULL_CONFIRMED"
                note = NULL_CONFIRMED[(p, f.key)]
            rows.append({
                "pack": p, "key": f.key, "label": f.label, "domain": f.domain,
                "model_shape": cmp_sw["shape"], "span": cmp_sw["span"],
                "full_shape": full["shape"], "full_span": full["span"],
                "ttv_shape": cmp_sw["ttv_shape"],
                "lit_shape": lit["shape"] if lit else "unknown",
                "lit_n": lit["n"] if lit else 0,
                "lit_sets": lit["datasets"] if lit else [],
                "lit_digitized": bool(lit and lit["digitized"]),
                "verdict": v,
                "note": note,
                "cmp_range": cmp_range,
                "xs": full["xs"], "mrr": full["mrr"], "ttv": full["ttv"],
                "lit_pts": list(zip(lit["xs"], lit["ys"])) if lit else [],
            })
    return {"rows": rows, "evidence": [e.__dict__ for e in ev]}


ORDER = {"CONFLICT": 0, "DEAD": 1, "MISSING": 2, "AGREE": 3, "NO-DATA": 4,
         "BLANK": 5, "N/A": 6, "NULL_CONFIRMED": 7}


def print_table(rep: Dict, pack_filter: Optional[str], show_na: bool) -> None:
    rows = [r for r in rep["rows"] if not pack_filter or r["pack"] == pack_filter]
    if not show_na:
        rows = [r for r in rows if r["verdict"] != "N/A"]
    print("■ 응답 지도 — 인자를 움직이면 결과가 어떻게 바뀌나 (문헌 형상과 같은 구간에서 대조)")
    print("  ✅일치 ❌충돌(모델이 틀린 방향을 가리킴) 🕳모델무반응(문헌有) "
          "🔲팩에 파라미터 없음(문헌有) ⚠문헌근거없음 ·둘다없음")
    by_pack: Dict[str, List[Dict]] = {}
    for r in rows:
        by_pack.setdefault(r["pack"], []).append(r)
    for p, rs in by_pack.items():
        print()
        print(f"  ── {p}")
        print(f"     {'인자':18s} {'영역':10s} {'모델':7s} {'변화폭':>7s} "
              f"{'TTV':6s} {'문헌':7s} {'n':>3s}  판정")
        print("     " + "-" * 82)
        for r in sorted(rs, key=lambda r: (ORDER[r["verdict"]], -(r["span"] if r["span"] == r["span"] else 0))):
            span = "-" if r["span"] != r["span"] else f"{r['span']:6.2f}x"
            print(f"     {r['label']:18s} {r['domain']:10s} "
                  f"{SHAPE_KO[r['model_shape']]:7s} {span:>7s} "
                  f"{SHAPE_KO[r['ttv_shape']]:6s} {SHAPE_KO.get(r['lit_shape'],'-'):7s} "
                  f"{(r['lit_n'] or '-'):>3}  {VERDICT_MARK[r['verdict']]} {r['verdict']}")
    cnt = lambda v: len([r for r in rows if r["verdict"] == v])
    print()
    print(f"  요약: ❌충돌 {cnt('CONFLICT')} · 🕳모델무반응 {cnt('DEAD')} · "
          f"🔲팩누락 {cnt('MISSING')} · ✅일치 {cnt('AGREE')} · "
          f"⚠문헌없음 {cnt('NO-DATA')} · ·미구현+문헌없음 {cnt('BLANK')}")
    print("  → 충돌·무반응이 0이 될 때까지 이 도구는 '방향 예측용'이라고만 말할 수 있다.")


def print_knob(rep: Dict, key: str) -> None:
    rows = [r for r in rep["rows"] if r["key"] == key and r["verdict"] != "N/A"]
    rows = [r for r in rows if r["xs"] or r["lit_pts"]]
    if not rows:
        print(f"인자 '{key}'가 어느 팩에도 없다. --list 로 목록 확인.")
        return
    for r in rows:
        print(f"■ {r['label']} ({r['key']}) · 팩 {r['pack']}")
        print(f"  실무범위 전체: {SHAPE_KO[r.get('full_shape', r['model_shape'])]}, "
              f"{r.get('full_span', r['span']):.2f}x")
        if r["cmp_range"]:
            print(f"  문헌 대조구간 {r['cmp_range'][0]:g}~{r['cmp_range'][1]:g}: "
                  f"모델 {SHAPE_KO[r['model_shape']]} vs 문헌 {SHAPE_KO[r['lit_shape']]}")
        if r["note"]:
            print(f"  ⚠ {r['note']}")
        top = max(r["mrr"]) if r["mrr"] else 1.0
        for x, y, t in zip(r["xs"], r["mrr"], r["ttv"]):
            bar = "█" * int(round(30 * y / top))
            print(f"   x={x:<12.4g} MRR {y:9.2f}  TTV {t:8.2f}  {bar}")
        if r["lit_pts"]:
            print(f"  문헌 실측(각 데이터셋 중앙값=1로 정규화, {', '.join(r['lit_sets'])}"
                  f"{' ⚠digitized' if r['lit_digitized'] else ''}):")
            ltop = max(y for _, y in r["lit_pts"])
            for x, y in r["lit_pts"]:
                print(f"   x={x:<12.4g} rel {y:7.3f}          "
                      f"{'▒' * int(round(30 * y / ltop))}")
        else:
            print("  문헌: 이 팩에서 이 인자를 단독 변화시킨 in-scope 데이터셋이 0건")
        print(f"  판정: {VERDICT_MARK[r['verdict']]} {r['verdict']}")
        print()


def print_gaps(rep: Dict) -> None:
    gaps = [r for r in rep["rows"]
            if r["verdict"] in ("CONFLICT", "DEAD", "MISSING", "NO-DATA")]
    gaps.sort(key=lambda r: (ORDER[r["verdict"]],
                             -(r["span"] if r["span"] == r["span"] else 0)))
    print("■ 응답 갭 랭킹 — 개발 도구로서 못 믿을 축부터 (인자 단위, 슬러리 단위 아님)")
    for i, r in enumerate(gaps[:25], 1):
        rngs = (f"{r['cmp_range'][0]:g}~{r['cmp_range'][1]:g}" if r["cmp_range"] else "-")
        if r["verdict"] == "CONFLICT":
            act = (f"구간 {rngs}에서 모델은 {SHAPE_KO[r['model_shape']]}인데 문헌은 "
                   f"{SHAPE_KO[r['lit_shape']]} ({', '.join(r['lit_sets'])}, n={r['lit_n']}). "
                   f"sim/factors.py의 해당 항을 그 구간에서 재현하도록 고쳐라.")
        elif r["verdict"] == "MISSING":
            act = (f"문헌({', '.join(r['lit_sets'])}, n={r['lit_n']})은 이 인자로 MRR이 "
                   f"{SHAPE_KO[r['lit_shape']]}로 변하는데 knowledge/params/{r['pack']}.yaml에 "
                   f"'{r['key']}' 칸 자체가 없다. 그 문헌값을 source와 함께 팩에 추가하라.")
        elif r["verdict"] == "DEAD":
            act = (f"문헌({', '.join(r['lit_sets'])}, n={r['lit_n']})은 이 인자로 MRR이 "
                   f"{SHAPE_KO[r['lit_shape']]}로 변하는데 모델은 무반응. {r['note']}")
        else:
            act = (f"모델은 {SHAPE_KO[r['model_shape']]}({r['span']:.1f}x)로 반응하는데 "
                   f"이 팩에서 이 인자 단독 시리즈가 0건 — 응답 형상에 근거가 없다. "
                   f"특허 실시예·논문 SI에서 이 인자만 바꾼 n≥4를 확보하라"
                   f"(tools/patent_mine.py).")
        print(f"  {i:2d}. [{r['verdict']:8s}] {r['pack']}/{r['label']}")
        print(f"       {act}")


def print_evidence(rep: Dict) -> None:
    print("■ 문헌 형상 원장 — 어떤 데이터셋이 어떤 인자를 단독으로 움직였나")
    print(f"  {'인자':20s} {'데이터셋':46s} {'팩':16s} {'n':>3s} {'형상':6s} {'폭':>7s}  비고")
    print("  " + "-" * 116)
    for e in rep["evidence"]:
        tags = []
        if e["confounded"]:
            tags.append(f"교란({e['n_varying']}인자 동시변화 — 판정제외)")
        if not e["in_scope"]:
            tags.append("범위밖")
        if e["calib"]:
            tags.append("캘리브레이션출처(자기채점 — 판정제외)")
        if e.get("quarantined"):
            tags.append("🔒qa_loop 격리(판정제외)")
        if e["read"] == "digitized":
            tags.append("그래프판독")
        print(f"  {e['key']:20s} {e['dataset']:46s} {str(e['pack']):16s} "
              f"{e['n']:3d} {SHAPE_KO[e['shape']]:6s} {e['span']:6.2f}x  "
              f"{' / '.join(tags)}")


def main() -> int:
    ap = argparse.ArgumentParser(description="응답 지도 — 인자→결과 형상 대조")
    ap.add_argument("--pack", default=None)
    ap.add_argument("--knob", default=None, help="인자 키 하나의 스윕 곡선 + 문헌 점")
    ap.add_argument("--gaps", action="store_true")
    ap.add_argument("--evidence", action="store_true")
    ap.add_argument("--list", action="store_true", help="인자 키 목록")
    ap.add_argument("--all", action="store_true", help="N/A(팩에 없는 인자)도 표시")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.list:
        for f in FACTORS:
            print(f"{f.key:26s} {f.label:18s} {f.domain:11s} {f.practical_range}")
        return 0

    packs = [a.pack] if a.pack else [p for p in available_packs() if p != "base"]
    rep = build(packs)

    if a.json:
        print(json.dumps(rep, ensure_ascii=False, default=float))
    elif a.evidence:
        print_evidence(rep)
    elif a.knob:
        print_knob(rep, a.knob)
    elif a.gaps:
        print_gaps(rep)
    else:
        print_table(rep, a.pack, a.all)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
