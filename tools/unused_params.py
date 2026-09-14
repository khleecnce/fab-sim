"""선언해 두고 쓰지 않는 물성을 전수로 찾는다.

⚠⚠ 이 검사의 가장 큰 함정 — 기준점에서 탐침하면 전부 '미사용'으로 보인다
────────────────────────────────────────────────────────────────────
모델의 상대항은 `(x/x_ref)^n` 꼴이다. 팩의 기본 조건은 정의상 x = x_ref
이므로 그 지점에서는 **지수 n 을 무엇으로 바꿔도 항이 정확히 1.0** 이다.
따라서 기본 조건에서 지수를 흔들면 출력이 비트 단위로 같고, 그것을
'미사용'으로 읽으면 멀쩡한 물리를 결함으로 신고하게 된다.

실제로 겪었다: 1차 실행이 "75% 가 선언만 되고 쓰이지 않음"을 보고했으나,
검산하니 농도를 기준(20)에서 40 으로 옮긴 뒤에는 지수가 정상 작동했다.

    농도 40 에서   지수 0.167 → κ 1.122
                   지수 0.333 → κ 1.260
                   지수 0.666 → κ 1.587     ← 정상

그래서 이 검사는 두 단계로 한다:
  1단계 기준점에서 탐침 → 여기서 변하면 확실히 사용 중
  2단계 기준점을 **벗어난 조건**에서 다시 탐침
        (상대항이 1이 아니게 만든 뒤 지수·계수를 흔든다)
  두 단계 모두에서 변화가 없을 때만 '미사용'으로 신고한다.

왜 이 검사가 필요한가
────────────────────
물성을 적어 두면 "그 물리가 모델에 있다"고 착각하게 된다. 정말로 계산에
들어가지 않으면 (1) 근거 등급을 올려도 예측이 안 변하고 (2) 새 슬러리에
그 값을 요구해 놓고 무시하는 셈이 된다.
"""
import sys
import pathlib
import warnings
import json

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np                                # noqa: E402
from sim.engine import Recipe, simulate           # noqa: E402
from sim.params import load_pack                  # noqa: E402
import sim.models                                 # noqa: E402,F401

MODELS = ["tier1.preston_radial", "tier2.gw_physical_kp"]
PACKS = ["oxide_silica", "sti_ceria", "cu_h2o2_bta",
         "w_fe_oxidizer", "sic_ceria_h2o2"]

SKIP_KEYS = {"time_s", "n_points", "initial_thickness_nm"}

# ⚠ 배율 탐침(×0.01, ×100)은 세기 변수에서 **비물리 값**을 만든다.
#   pH 5.5 를 ×100 하면 550 이 되는데, 모델이 그 구간을 포화로 잘라내면
#   출력이 변하지 않고 검사기는 '미사용'으로 오판한다.
#   (실측: pH 는 3→5.5→8 에서 MRR 90→314→59 로 확실히 작동하는데
#    ×0.01/×100 탐침에서는 무반응으로 보였다.)
#   정의역이 있는 양은 **그 범위 안의 값**으로 탐침해야 한다.
DOMAIN_PROBES = {
    "slurry_ph": [2.0, 4.0, 7.0, 10.0, 12.0],
    "wafer_iep_ph": [2.0, 4.0, 6.0, 9.0],
    "abrasive_iep_ph": [2.0, 4.0, 6.0, 9.0],
    "pad_hardness_shore_d": [30.0, 55.0, 80.0],
    "ce3_fraction": [0.05, 0.2, 0.5],
}

# 기준점에서 벗어나게 만들 짝 — 본값을 옮기면 상대항이 1이 아니게 된다.
# ⚠ _ref 는 건드리지 않는다. 함께 옮기면 다시 1이 되어 아무 의미가 없다.
OFFSET_DRIVERS = {
    "abrasive_wt_pct": 2.0,
    "abrasive_size_nm": 2.0,
    "oxidizer_wt_pct": 2.0,
    "inhibitor_mM": 2.0,
    "slurry_ph": 1.3,
    "pad_hardness_shore_d": 1.4,
    "sfr_ml_min": 2.0,
    "pressure_psi": 1.5,
}


def observe(pack, overrides, model):
    """MRR 뿐 아니라 **모든 팩터 값**을 함께 관측한다.

    ⚠ MRR 만 보면 '계산은 되는데 MRR 에 반영되지 않는' 팩터를 미사용으로
      오판한다. 실제로 결함 팩터(delta)는 입력에 따라 0.08~1.61 로 정상
      반응하지만 MRR 은 전혀 변하지 않았다 — 이것은 '미사용'이 아니라
      **'계산되지만 결과에 연결되지 않음'** 이라는 다른 종류의 결함이다.
      둘을 구분해야 고칠 곳을 알 수 있다.
    """
    r = simulate(Recipe(pack=pack, pack_overrides=overrides), model=model)
    mrr = float(np.mean(np.asarray(r.mrr_nm_per_min, dtype=float)))
    facs = tuple(
        (k, (round(f.value, 12) if isinstance(f.value, (int, float)) else None))
        for k, f in sorted(r.factors.items())
    )
    return mrr, facs


def _offset_context(pack):
    """기준점에서 벗어난 조건을 만든다."""
    pk = load_pack(pack)
    ctx = {}
    for k, mult in OFFSET_DRIVERS.items():
        if pk.has(k):
            try:
                ctx[k] = float(pk.get(k)) * mult
            except (TypeError, ValueError):
                pass
    return ctx


def probe(pack, key, model, ctx):
    pk = load_pack(pack)
    if not pk.has(key):
        return None
    try:
        x0 = float(pk.get(key))
    except (TypeError, ValueError):
        return None
    if x0 == 0:
        return None

    # 정의역이 정해진 양은 그 범위 안에서, 나머지는 배율로 탐침한다.
    if key in DOMAIN_PROBES:
        probe_vals = DOMAIN_PROBES[key]
    else:
        probe_vals = [x0 * f for f in (0.01, 1.0, 100.0)]

    def run(base_ctx):
        mrrs, facs = [], []
        for pv in probe_vals:
            o = dict(base_ctx)
            o[key] = pv
            try:
                m, f = observe(pack, o, model)
            except Exception:
                return None
            if m != m:
                return None
            mrrs.append(m)
            facs.append(f)
        return mrrs, facs

    def verdict(res):
        if res is None:
            return None
        mrrs, facs = res
        mrr_moves = len(set(mrrs)) > 1
        fac_moves = len(set(facs)) > 1
        if mrr_moves:
            return "used"
        if fac_moves:
            return "orphan"      # 계산은 되는데 MRR 에 연결 안 됨
        return "dead"

    v1 = verdict(run({}))
    if v1 == "used":
        return {"unused": False, "kind": "used", "where": "기준점"}
    v2 = verdict(run(ctx))
    if v2 is None:
        return None
    if v2 == "used":
        return {"unused": False, "kind": "used", "where": "기준점 밖"}
    if "orphan" in (v1, v2):
        return {"unused": False, "kind": "orphan",
                "where": "팩터는 반응하나 MRR 에 반영되지 않음"}
    return {"unused": True, "kind": "dead", "where": "양쪽 모두 무반응"}


def main() -> int:
    report = {}
    for model in MODELS:
        print("=" * 76)
        print(f"모델: {model}")
        print("=" * 76)
        tot_unused = tot_used = tot_orphan = 0
        per_pack = {}
        for pack in PACKS:
            pk = load_pack(pack)
            ctx = _offset_context(pack)
            keys = [k for k in sorted(pk.params)
                    if pk.has_own(k) and k not in SKIP_KEYS
                    and not k.endswith("_ref")]
            unused, used, orphan = [], [], []
            for k in keys:
                r = probe(pack, k, model, ctx)
                if r is None:
                    continue
                kind = r.get("kind")
                if kind == "used":
                    used.append(k)
                elif kind == "orphan":
                    orphan.append(k)
                else:
                    unused.append(k)
            per_pack[pack] = {"unused": unused, "used": used,
                              "orphan": orphan}
            tot_unused += len(unused)
            tot_used += len(used)
            tot_orphan += len(orphan)
            print(f"\n── {pack}   사용 {len(used):2d} / "
                  f"고아 {len(orphan):2d} / 미사용 {len(unused):2d}")
            if orphan:
                print("     [고아] 계산되지만 MRR 에 반영 안 됨:")
                for k in orphan[:6]:
                    print(f"      · {k}")
            for k in unused[:8]:
                print(f"      · (미사용) {k}")
            if len(unused) > 8:
                print(f"      … 외 {len(unused)-8}개")
        total = tot_used + tot_unused + tot_orphan
        pct = (tot_unused / total * 100) if total else 0
        print(f"\n  합계: 사용 {tot_used} / 고아 {tot_orphan} / "
              f"미사용 {tot_unused} ({pct:.0f}%)")
        print()
        report[model] = {"used": tot_used, "unused": tot_unused,
                         "orphan": tot_orphan, "per_pack": per_pack}

    out = ROOT / "validation" / "unused_params.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    both = None
    for model in MODELS:
        s = set()
        for pack, d in report[model]["per_pack"].items():
            s |= {(pack, k) for k in d["unused"]}
        both = s if both is None else (both & s)
    both = both or set()
    print("=" * 76)
    print(f"**모든 모델에서 미사용** (진짜 구멍): {len(both)}칸")
    for k in sorted({k for _, k in both}):
        n = sum(1 for _, kk in both if kk == k)
        print(f"   {k:34s} {n}팩")
    print(f"\n→ {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
