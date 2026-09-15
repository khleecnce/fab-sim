"""팩이 드라이버를 선언하지 않아 항이 죽어 있는 곳을 전수로 찾는다.

발견 경위 (2026-09-15)
─────────────────────
cu_h2o2_bta 팩에 abrasive_wt_pct 가 아예 없었다. 실행 시 override 로만
주입되니 기준점(abrasive_ref_wt_pct)이 없고, 기준점이 없으면 상대항
(x/x_ref)^n 을 계산할 수 없어 항이 통째로 침묵한다.
증상이 조용하다 — 예외도 NaN 도 아니고 그냥 "아무리 바꿔도 안 변한다".
실제로 실리카 2/3/4 wt% 에서 예측 MRR 이 완전히 동일했다.

무엇을 검사하는가
────────────────
각 팩에 대해, 검증 데이터셋이 실제로 스윕하는 축을 모아
그 축이 **팩에 본값과 기준점을 모두 갖고 있는지** 본다.

  · 본값 없음        → override 로만 들어온다. 기준점이 없으면 항이 죽는다.
  · 기준점 없음      → 상대항을 만들 수 없다. 침묵하거나 자기 자신과 비교한다.
  · 둘 다 있음       → 정상

⚠ 물질명 없음. 데이터셋이 무엇을 흔드는지와 팩이 무엇을 아는지만 대조한다.
"""
import sys
import pathlib
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml                                        # noqa: E402
from sim.params import load_pack                   # noqa: E402

DATA = ROOT / "validation" / "datasets"

# 본값 → 기준점 이름 규칙 (접미/접두 둘 다 쓰인다)
REF_CANDIDATES = {
    "abrasive_wt_pct": ["abrasive_ref_wt_pct"],
    "abrasive_size_nm": ["abrasive_ref_size_nm"],
    "abrasive_d99_nm": ["abrasive_ref_d99_nm"],
    "oxidizer_wt_pct": ["oxidizer_ref_wt_pct"],
    "inhibitor_mM": ["inhibitor_ref_mM"],
    "slurry_ph": ["ph_ref", "ph_softening_ref"],
    "pad_hardness_shore_d": ["pad_ref_hardness_shore_d"],
    "asperity_density_per_m2": ["asperity_ref_density_per_m2"],
    "sfr_ml_min": ["sfr_ref_ml_min"],
    "pressure_psi": [],          # 절대량 — 기준점 불필요
    "rpm_platen": [],
    "rpm_wafer": [],
}


def swept_axes():
    """데이터셋별로 실제 스윕하는 축을 모은다."""
    per_pack = defaultdict(set)
    for f in sorted(DATA.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        try:
            d = yaml.safe_load(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        pack = d.get("pack")
        if not pack:
            continue
        cs = d.get("conditions", [])
        keys = set()
        for c in cs:
            keys |= {k for k, v in c.items() if isinstance(v, (int, float))}
            keys |= set((c.get("overrides") or {}).keys())
        for k in keys:
            if k in ("mrr_nm_per_min",):
                continue
            vals = set()
            for c in cs:
                v = c.get(k, (c.get("overrides") or {}).get(k))
                if isinstance(v, (int, float)):
                    vals.add(v)
            if len(vals) > 1:
                per_pack[pack].add(k)
    return per_pack


def main() -> int:
    per_pack = swept_axes()
    print("=" * 78)
    print("검증 데이터가 흔드는 축을 팩이 계산할 수 있는가")
    print("=" * 78)

    total_bad = 0
    for pack in sorted(per_pack):
        try:
            pk = load_pack(pack)
        except Exception as e:  # noqa: BLE001
            print(f"\n── {pack}: 로드 실패 {e}")
            continue
        bad = []
        ok = []
        for axis in sorted(per_pack[pack]):
            if axis not in REF_CANDIDATES:
                continue
            refs = REF_CANDIDATES[axis]
            has_val = pk.has(axis)
            has_ref = (not refs) or any(pk.has(r) for r in refs)
            if has_val and has_ref:
                ok.append(axis)
            else:
                why = []
                if not has_val:
                    why.append("본값 없음(override 전용)")
                if not has_ref:
                    why.append(f"기준점 없음({'/'.join(refs)})")
                bad.append((axis, " + ".join(why)))
        print(f"\n── {pack}   정상 {len(ok)} / 결함 {len(bad)}")
        for axis, why in bad:
            print(f"   🔴 {axis:26s} {why}")
            total_bad += 1

    print()
    print("=" * 78)
    if total_bad:
        print(f"🔴 죽은 축 {total_bad}개 — 데이터가 흔드는데 모델이 반응하지 못한다.")
        print("   본값과 기준점을 **함께** 선언해야 한다. 기준점만 넣으면")
        print("   자기 자신과 비교하게 되어 배수가 영원히 1.0 이다.")
    else:
        print("✅ 검증 데이터가 흔드는 모든 축을 팩이 계산할 수 있다.")
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
