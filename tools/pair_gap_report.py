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
from sim.inhibitor_pairs import (PAIR_TABLE, lookup_dG, adsorption_ruled_out,  # noqa: E402
                                _key)

DS = ROOT / "validation" / "datasets"

# 데이터셋 원문에서 첨가제 이름을 뽑는다 (추출기 — 판정 기준 아님)
# ⚠ 단어 경계를 강제한다. 경계가 없으면 팩 이름(`cu_h2o2_bta`)이나 파일명에
#   섞인 부분 문자열까지 첨가제 언급으로 잡혀, 그 첨가제를 쓰지도 않는
#   데이터셋이 조사 목록에 오른다(실측: SiC 데이터셋이 주석 속 팩 이름 때문에
#   'bta × sic' 쌍을 요구하는 것으로 잡혔다).
ADDITIVE_HINTS = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(benzotriazole|BTA|benzenesulfonic|nicotinic|tolyltriazole|TTA|"
    r"mercaptobenzothiazole|MBT|glycine|quinaldic|triazole|imidazole|"
    r"citric|oxalic|malonic|tartaric|EDTA)"
    r"(?![A-Za-z0-9_])",
    re.IGNORECASE,
)

SUBSTRATE_HINTS = {
    "cu": r"\bCu\b|copper|구리",
    "w": r"\btungsten\b|\bW plug|텅스텐",
    "ta": r"\bTa\b|\bTaN\b|tantalum",
    "ti": r"\bTiN\b|titanium",
    "oxide": r"PETEOS|TEOS|thermal oxide|산화막",
}

# 성분이 **없다**고 적은 문장에서 그 성분 이름을 뽑으면 거짓 경보가 된다.
# 실측: "원문의 억제제는 BTA 가 아니라 벤젠술폰산", "BTA 없음", "BTA 무첨가"
# 같은 부정 서술이 전부 '이 데이터셋은 BTA 를 쓴다'로 잡혀, 존재하지도 않는
# 쌍이 문헌 조사 목록에 올라왔다. 이 오판은 예외를 내지 않으므로 목록을
# 눈으로 보기 전까지 드러나지 않는다.
_NEGATION = re.compile(
    r"(없|무첨가|미함유|미첨가|아니|제외|free of|without|absent|no\s)",
    re.IGNORECASE,
)


def _mentions_positively(text: str, pattern: re.Pattern) -> bool:
    """그 성분이 **있다**고 말하는 문장이 하나라도 있는가.

    문장 단위로 보고, 부정 표현이 같은 문장에 있으면 그 언급은 세지 않는다.
    """
    for sent in re.split(r"[.。\n]", text):
        if pattern.search(sent) and not _NEGATION.search(sent):
            return True
    return False


def _substrate_of(raw: dict, pack: str) -> str:
    """이 데이터셋이 **실제로 예측하는** 막질.

    ⚠ 본문 전체에서 막질 이름을 긁으면 안 된다. 특허 표 제목은 한 실험에서
    같이 측정한 다른 막질(PETEOS·TaN·low-k 등)을 전부 나열하므로, 텍스트
    매칭은 Cu 데이터셋을 'oxide 데이터셋'으로도 세어 존재하지 않는 쌍을
    만들어낸다. 검증이 채점하는 것은 팩의 film 하나뿐이다.
    """
    try:
        from sim.params import load_pack
        film = str(load_pack(pack).get("film")).strip().lower()
        if film:
            return {"sio2": "oxide", "silica": "oxide"}.get(film, film)
    except Exception:
        pass
    return ""


def main() -> int:
    need = defaultdict(list)
    for path in sorted(DS.glob("*.yaml")):
        txt = path.read_text(encoding="utf-8")
        raw = yaml.safe_load(txt) or {}
        pack = str(raw.get("pack", ""))
        in_scope = bool(raw.get("in_scope", True))

        adds = {m.group(0).lower() for m in ADDITIVE_HINTS.finditer(txt)
                if _mentions_positively(txt, re.compile(re.escape(m.group(0)),
                                                        re.IGNORECASE))}
        if not adds:
            continue
        # 기질은 본문 텍스트가 아니라 **팩의 film** 이 정한다(위 _substrate_of 주석).
        sub = _substrate_of(raw, pack)
        subs = {sub} if sub else {k for k, pat in SUBSTRATE_HINTS.items()
                                  if re.search(pat, txt, re.IGNORECASE)}
        for a in sorted(adds):
            for s in sorted(subs):
                # 쌍 표와 **같은 정규화**를 거쳐야 한다. 안 그러면 benzotriazole
                # 과 bta 가 별개 줄로 보고돼, 이미 등록된 쌍이 '미확보'로 뜬다.
                ka, ks = _key(a, s)
                need[(ka, ks)].append((path.stem, pack, in_scope))

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
