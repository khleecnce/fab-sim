"""팩 기본값이 데이터셋의 조성과 어긋나는 곳을 찾는다 — 조용한 오판의 원인.

발견 경위 (2026-09-15)
─────────────────────
알칼리 pH 항을 구현하고 데이터셋을 만들었는데 ρ = -0.707 이 나왔다.
원인: 그 데이터셋 원문이 "BTA 없음"이라 적고 있는데 `inhibitor_mM` 을
조건에 명시하지 않아 **팩 기본값 1.0 이 상속**됐다. 레짐 판정이
"억제제 있음"으로 뒤집혀 항이 통째로 꺼졌다.
명시하자 ρ = +1.000 (p=0.008).

왜 기계가 잡아야 하는가
──────────────────────
데이터셋 문서에는 "BTA 없음", "억제제 무첨가" 가 **한국어·영어 산문**으로
적혀 있고, 조건 블록에는 숫자가 없다. 사람이 읽으면 명백하지만 기계는
팩 기본값을 조용히 쓴다 — 예외도 경고도 없다.

이 결함은 특히 위험하다: **레짐을 가르는 변수**에서 일어나면 항이 통째로
꺼지거나 반대 레짐으로 가서 부호까지 뒤집힌다.

판정 규칙
─────────
문서에 "X 없음/무첨가/free of X" 서술이 있는데 대응 키가 조건에 0 으로
전달되지 않으면 신고한다. 반대로 "X 함유" 서술이 있는데 0 으로 전달돼도
신고한다.
"""
import pathlib
import re
import sys
import warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml                                            # noqa: E402
from sim.params import load_pack                       # noqa: E402

DS = ROOT / "validation" / "datasets"

# (서술 정규식, 대응 키, 사람이 읽는 축 이름)
ABSENCE_RULES = [
    (re.compile(r"(BTA|benzotriazole|억제제|inhibitor)[^\n]{0,16}"
                r"(없|무첨가|미함유|free|absent|without)"
                r"|(없|무첨가|미함유|without|free of|no)[^\n]{0,16}"
                r"(BTA|benzotriazole|억제제|inhibitor)", re.IGNORECASE),
     "inhibitor_mM", "억제제"),
    (re.compile(r"(산화제|oxidizer|H2O2|H₂O₂|과산화수소)[^\n]{0,16}"
                r"(없|무첨가|미함유|free|absent|without)"
                r"|(없|무첨가|미함유|without|free of|no)[^\n]{0,16}"
                r"(산화제|oxidizer|H2O2|H₂O₂)", re.IGNORECASE),
     "oxidizer_wt_pct", "산화제"),
]


def _flat(c: dict) -> dict:
    out = dict(c)
    ov = out.get("overrides")
    if isinstance(ov, dict):
        out.update(ov)
    return out


def main() -> int:
    print("=" * 88)
    print("문서는 '없다'는데 팩 기본값이 '있다'로 들어가는 곳")
    print("=" * 88)
    print("⚠ 레짐을 가르는 변수에서 일어나면 항이 꺼지거나 부호가 뒤집힌다.")
    print("  예외도 경고도 없이 조용히 일어난다.")
    print()

    total = 0
    for path in sorted(DS.glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        raw = yaml.safe_load(text) or {}
        conds = raw.get("conditions") or []
        pack_name = str(raw.get("pack", ""))
        if not conds or not pack_name:
            continue
        try:
            pk = load_pack(pack_name)
        except Exception:
            continue

        probs = []
        for rx, key, label in ABSENCE_RULES:
            if not rx.search(text):
                continue
            # 조건에 그 키가 0 으로 전달되는가
            vals = [_flat(c).get(key) for c in conds if key in _flat(c)]
            if not vals:
                default = pk.get_or(key, None)
                if isinstance(default, (int, float)) and float(default) > 0:
                    probs.append(
                        f"🔴 {label}: 문서는 '없음'이라 적는데 조건에 {key} 가 "
                        f"없어 **팩 기본값 {default:g} 이 상속**된다. "
                        "레짐 판정이 뒤집힐 수 있다.")
            else:
                # ⚠ 값이 전달되고 있으면 신고하지 않는다.
                #   "0 wt% 조건도 포함" 같은 서술이 '없음' 규칙에 걸리는데,
                #   그 데이터셋은 축을 스윕 중이고 0 조건을 이미 갖고 있다.
                #   거짓 경보가 나면 이 감사기는 곧 무시당한다.
                pass
        if probs:
            print(f"■ {path.stem}  [{pack_name}]")
            for p in probs:
                print(f"    {p}")
            total += len(probs)

    print()
    print("-" * 88)
    if total:
        print(f"결함 {total}건 — 조건에 0 을 **명시**해야 한다.")
        print("  팩 기본값은 '그 팩의 기준 조성'이지 '이 데이터셋의 조성'이 아니다.")
    else:
        print("✅ 문서 서술과 전달값이 일치한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
