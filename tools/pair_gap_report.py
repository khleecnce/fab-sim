"""검증 데이터가 요구하는 (첨가제 × 기질) 쌍을 전수로 뽑는다.

왜 이 목록이 먼저인가
────────────────────
전이 시험(tools/transfer_test.py)에서 처음 보는 계열의 절대 MRR 오차가 78% 였다.
원인은 축척이 아니라 **화학 항이 비어 있는 것**이다: 같은 재료계 안에서 실측이
100배 갈리는데, 낮은 쪽은 첨가제로 제거를 의도적으로 억제한 조성이고 그 첨가제의
흡착상수가 쌍 표에 없다. 쌍이 없으면 모델은 억제를 0 으로 보고 높은 쪽 값을
예측한다.

따라서 다음 작업의 단위는 "어느 쌍이 없는가"다. 이 목록이 곧 문헌 조사 발주서이며,
아무 첨가제나 찾는 것보다 **지금 검증을 막고 있는 쌍**부터 채우는 것이 빠르다.

⚠ 추상화 규칙: 물질명은 데이터에서 **읽어서 출력**할 뿐, 판정 기준에 넣지 않는다.
  판정 기준은 "이 계열이 요구하는 쌍이 표에 있는가" 하나다. 아래 정규식은
  텍스트 추출기이지 물리 규칙이 아니다 — 새 첨가제가 오면 여기에 한 줄 늘 뿐
  모델의 물리는 바뀌지 않는다.
"""
import pathlib
import re
import sys
import warnings
from collections import defaultdict

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml                                            # noqa: E402
from sim.inhibitor_pairs import PAIR_TABLE, lookup_dG, adsorption_ruled_out  # noqa: E402

DS = ROOT / "validation" / "datasets"

# 데이터셋 원문에서 첨가제 이름을 뽑는다 (추출기 — 판정 기준 아님)
ADDITIVE_HINTS = re.compile(
    r"(benzotriazole|BTA\b|benzenesulfonic|nicotinic|tolyltriazole|TTA\b|"
    r"mercaptobenzothiazole|MBT\b|glycine|quinaldic|triazole|imidazole|"
    r"citric|oxalic|malonic|tartaric|EDTA)",
    re.IGNORECASE,
)

SUBSTRATE_HINTS = {
    "cu": r"\bCu\b|copper|구리",
    "w": r"\btungsten\b|\bW plug|텅스텐",
    "ta": r"\bTa\b|\bTaN\b|tantalum",
    "ti": r"\bTiN\b|titanium",
    "oxide": r"PETEOS|TEOS|thermal oxide|산화막",
}


def main() -> int:
    need = defaultdict(list)
    for path in sorted(DS.glob("*.yaml")):
        txt = path.read_text(encoding="utf-8")
        raw = yaml.safe_load(txt) or {}
        pack = str(raw.get("pack", ""))
        in_scope = bool(raw.get("in_scope", True))

        adds = {m.group(0).lower() for m in ADDITIVE_HINTS.finditer(txt)}
        if not adds:
            continue
        subs = {k for k, pat in SUBSTRATE_HINTS.items()
                if re.search(pat, txt, re.IGNORECASE)}
        for a in sorted(adds):
            for s in sorted(subs):
                need[(a, s)].append((path.stem, pack, in_scope))

    print("=" * 88)
    print("검증 데이터가 요구하는 (첨가제 × 기질) 쌍 — 표에 있는가")
    print("=" * 88)
    print(f"현재 쌍 표: {len(PAIR_TABLE)}건 등록")
    print()

    have, miss, ruled = [], [], []
    for (a, s), users in sorted(need.items(), key=lambda kv: -len(kv[1])):
        pair = lookup_dG(a, s)
        if pair:
            have.append((a, s, users, pair))
            continue
        reason = adsorption_ruled_out(a, s)
        if reason:
            ruled.append((a, s, users, reason))
        else:
            miss.append((a, s, users, pair))

    print(f"■ 표에 있음 {len(have)}쌍")
    for a, s, users, pair in have:
        print(f"  ✅ {a} × {s:6s}  ΔG={pair.dG_kJ_per_mol:7.2f}  "
              f"[{pair.confidence}]  ← {len(users)}개 계열")

    if ruled:
        print()
        print(f"■ 흡착 없음으로 **선언된** {len(ruled)}쌍 — 조사 대상이 아니다")
        print("   ('아무도 안 쟀다'가 아니라 '그 메커니즘이 없다'. 억제 항이")
        print("    없는 것이 물리적으로 옳으므로 문헌을 더 찾지 마라.)")
        for a, s, users, reason in ruled:
            print(f"  🚫 {a} × {s:6s}  ← {len(users)}개 계열")
            print(f"        근거: {reason[:110]}")

    print()
    print(f"■ 표에 없음 {len(miss)}쌍 — 이것이 다음 문헌 조사 목록이다")
    for a, s, users, _ in miss:
        scoped = [u for u in users if u[2]]
        mark = "🔴" if scoped else "  "
        print(f"  {mark} {a} × {s:6s}  ← {len(users)}개 계열 "
              f"(범위 안 {len(scoped)}개)")
        for name, pack, insc in users[:3]:
            print(f"        {'·' if insc else '○'} {name[:56]} [{pack}]")

    scoped_miss = [m for m in miss if any(u[2] for u in m[2])]
    print()
    print("=" * 88)
    print("우선순위")
    print()
    print(f"  범위 안 계열을 막고 있는 미등록 쌍: **{len(scoped_miss)}쌍**")
    print()
    print("  ⚠ 쌍이 없을 때 모델은 억제를 0 으로 보고 **높은 제거율을 예측**한다.")
    print("    같은 재료계에서 실측이 100배 갈리는 이유가 이것이다 — 첨가제로 제거를")
    print("    의도적으로 억제한 조성을 모델이 '첨가제 없음'과 같게 본다.")
    print()
    print("  ⚠ 쌍을 채울 때 규칙(sim/inhibitor_pairs.py):")
    print("    · 기질을 반드시 적는다. 같은 분자라도 기질이 다르면 다른 줄이다.")
    print("    · 다른 기질 값으로 채우지 않는다 — 5,700배 오차의 원인이었다.")
    print("    · 다층 흡착이면 Langmuir 절편값은 ΔG1(첫층)일 뿐이다.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
