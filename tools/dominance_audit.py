"""어떤 인자가 제거율을 지배하는가 — 모델에게 물어보고, 실무 지식과 대조한다.

왜 이렇게 하는가
────────────────
현장 지식은 이렇게 갈린다(막질군별 지배 인자):

    Si·폴리실리콘   → 식각 첨가제가 지배
    TEOS·질화막     → 기계력이 지배 (세리아를 쓰면 화학 이빨이 지배)
    금속(Cu·W·TiN)  → 산화제 농도가 지배

⚠ 이 표를 **코드에 적어 넣으면 안 된다.** 그 순간 새 막질(Ru·Mo·Co)에서
  무력해지고, 우리가 만드는 것이 "절차"가 아니라 "사례집"이 된다.
  (사용자 규칙: 판정 기준에 물질명이 들어가면 실패)

대신 이 표를 **정답지**로 쓴다. 모델이 물성만 보고 같은 답을 내면 물리가
들어 있는 것이고, 다른 답을 내면 그 지점이 결함이다.

측정 방법
────────
각 입력을 조금 흔들어 제거율의 로그 민감도를 잰다:

    S_x = d ln MRR / d ln x      (중심차분)

가장 큰 |S_x| 를 가진 입력이 그 계의 지배 인자다. 이것은 물질명을 쓰지
않는다 — 그냥 모델을 흔들어 본 결과다.

읽는 법: S_x = 1 이면 "x 를 2배로 하면 MRR 이 2배", 0 이면 무반응.
"""
import sys
import pathlib
import math
import warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sim.engine import Recipe, simulate          # noqa: E402
from sim.params import load_pack                 # noqa: E402
import sim.models                                # noqa: E402,F401


# 입력을 물리 경로별로 묶는다 — 묶음 이름에도 물질명은 없다.
FAMILY = {
    "기계": ["pressure_psi", "rpm_platen", "rpm_wafer", "abrasive_wt_pct",
             "abrasive_size_nm", "pad_hardness_shore_d",
             "asperity_density_per_m2"],
    "산화제": ["oxidizer_wt_pct"],
    "화학(표면반응)": ["slurry_ph", "ce3_fraction"],
    "보호막(억제제)": ["inhibitor_mM"],
    "전달": ["sfr_ml_min"],
}
OF_INPUT = {k: fam for fam, keys in FAMILY.items() for k in keys}


def mrr_of(pack: str, overrides: dict) -> float:
    """웨이퍼 평균 제거율.

    ⚠ r.mrr_nm_per_min 은 스칼라가 아니라 **반경 방향 배열**이다.
      float() 로 감싸면 조용히 예외가 나고, 그 예외를 삼키면
      "모든 입력이 무반응"이라는 거짓 결론이 나온다(실제로 겪었다).
    """
    import numpy as _np
    r = simulate(Recipe(pack=pack, pack_overrides=overrides))
    return float(_np.mean(_np.asarray(r.mrr_nm_per_min, dtype=float)))


def sensitivity(pack: str, key: str, rel: float = 0.05):
    """d ln MRR / d ln key — 중심차분."""
    pk = load_pack(pack)
    if not pk.has(key):
        return None
    x0 = pk.get(key)
    try:
        x0 = float(x0)
    except (TypeError, ValueError):
        return None
    if x0 == 0:
        return None
    try:
        hi = mrr_of(pack, {key: x0 * (1 + rel)})
        lo = mrr_of(pack, {key: x0 * (1 - rel)})
    except Exception as e:
        # 조용히 None 을 돌려주면 "무반응"으로 오독된다. 이유를 남긴다.
        print(f"   ⚠ {key}: 계산 실패 — {type(e).__name__}: {e}")
        return None
    if lo <= 0 or hi <= 0:
        return None
    return (math.log(hi) - math.log(lo)) / (math.log(1 + rel) - math.log(1 - rel))


# 현장 지식(정답지). 판정에 쓰지 않고 **대조에만** 쓴다.
EXPECTED = {
    "oxide_silica":   ("기계", "TEOS/산화막 + 실리카 → 기계력 지배"),
    "sti_ceria":      ("화학(표면반응)", "산화막 + 세리아 → 화학 이빨 지배"),
    "cu_h2o2_bta":    ("산화제", "금속 → 산화제 농도 지배"),
    "w_fe_oxidizer":  ("산화제", "금속 → 산화제 농도 지배"),
    "sic_ceria_h2o2": (None, "(현장 지식 표에 없음 — 참고)"),
}

PACKS = list(EXPECTED)


def main() -> int:
    print("=" * 78)
    print("지배 인자 — 모델을 흔들어 잰 값 vs 현장 지식")
    print("=" * 78)

    agree = disagree = 0
    for pack in PACKS:
        pk = load_pack(pack)
        rows = []
        for key in OF_INPUT:
            s = sensitivity(pack, key)
            if s is not None and abs(s) > 1e-6:
                rows.append((abs(s), s, key))
        rows.sort(reverse=True)

        print(f"\n── {pack}")
        if not rows:
            print("   (반응하는 입력이 없다 — 모델이 이 계에서 아무것도 안 한다)")
            disagree += 1
            continue

        for mag, s, key in rows[:5]:
            print(f"   {key:26s} S={s:+.3f}   [{OF_INPUT[key]}]")

        top_fam = OF_INPUT[rows[0][2]]
        # 같은 묶음의 민감도를 합쳐 묶음 단위로도 본다
        fam_sum = {}
        for mag, s, key in rows:
            fam_sum[OF_INPUT[key]] = fam_sum.get(OF_INPUT[key], 0.0) + mag
        fam_rank = sorted(fam_sum.items(), key=lambda kv: -kv[1])
        top_fam_grouped = fam_rank[0][0]
        print(f"   → 지배 묶음: {top_fam_grouped}  "
              f"({', '.join(f'{k} {v:.2f}' for k, v in fam_rank[:3])})")

        exp, why = EXPECTED[pack]
        if exp is None:
            print(f"   ※ {why}")
            continue
        ok = (top_fam_grouped == exp)
        print(f"   {'✅ 일치' if ok else '❌ 불일치'} — 현장 지식: {why}")
        if ok:
            agree += 1
        else:
            disagree += 1
            print(f"      모델은 '{top_fam_grouped}', 현장은 '{exp}'")

    print()
    print("=" * 78)
    print(f"일치 {agree} / 불일치 {disagree}")
    if disagree:
        print()
        print("불일치는 **모델 결함의 위치를 가리킨다.** 정답지를 코드에 적어 넣어")
        print("맞추면 안 된다 — 그것은 물질별 규칙이고, 새 막질에서 무너진다.")
        print("고쳐야 할 것은 그 묶음의 물리가 왜 약하게(또는 세게) 나오는가다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
