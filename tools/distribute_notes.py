#!/usr/bin/env python3
"""노트를 V2 5개 리서치 섹션에 분배한다 — ARCHITECTURE-V2.md §4.

사용자 지시(2026-09-08):
  "지금까지 학습한 데이터는 각 섹션에 잘 나눠서 분배하도록하고 분배완료된건
   주석처리해서 향후 헷갈리지 않도록한다"

분배 방식
────────
노트를 **옮기지 않는다.** 경로를 바꾸면 노트끼리의 [[위키링크]]와 팩의
`source:` 참조가 전부 깨진다(팩 66개 파라미터가 노트 경로를 가리킨다).
대신 노트 상단에 **V2 섹션 배지**를 주석으로 박는다:

    <!-- V2-SECTION: R2-slurry | 분배완료 2026-09-08 | ARCHITECTURE-V2.md §3 -->

이러면 ①grep으로 섹션별 집계가 되고 ②어느 노트가 아직 미분배인지 즉시 보이고
③기존 링크·출처가 하나도 안 깨진다.

⚠ 분류는 규칙 기반이고, 확신이 없으면 `R0-unassigned`로 두고 사람이 본다.
   억지로 배정해 놓으면 "분배 완료"라는 거짓 신호가 된다.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOW = ROOT / "knowledge"

MARK_RE = re.compile(r"<!--\s*V2-SECTION:\s*([A-Za-z0-9\-]+)")

SECTIONS = {
    "R1-equipment": "① 장비 — 폴리셔 설정·출력값 (Λ Π Θ Γ)",
    "R2-slurry":    "② 슬러리 — 입자·첨가제 조성 (χ ψ Δ)",
    "R3-pad":       "③ 패드 — 재질·경도·그루브 (κ τ)",
    "R4-disk":      "④ 디스크 — 그릿·본딩·컨디셔닝 (κ Γ)",
    "R5-wafer":     "⑤ 웨이퍼 — 대상막질·계측·판정 (기준선)",
    "R0-unassigned": "미분배 — 사람이 판단 필요",
}

#: (섹션, 가중치, 패턴). 파일명·본문 첫 2000자에서 찾는다.
#: ⚠ 순서가 아니라 **점수 합**으로 정한다 — 한 노트가 여러 축에 걸치는 게 정상이다.
#:
#: ⚠ 가중치 조정 이력 (2026-09-08): 첫 배점에서 두 가지 오분류가 나왔다.
#:   ① 컨디셔너 노트 대부분이 R4가 아니라 R3(패드)로 갔다. "pad"라는 단어가
#:      컨디셔너 문서에 필연적으로 많이 나오기 때문이다(디스크는 패드를 깎는다).
#:      → 디스크 고유어(grit/diamond/conditioner/PCR)의 가중치를 패드보다 높였다.
#:   ② 마찰발열·Stribeck이 R2(슬러리)로 갔다. 점도·슬러리 언급이 많아서다.
#:      → 장비 출력값(마찰·열·모터)은 R1 고유 축이므로 가중치를 올렸다.
#:   교훈: 키워드 빈도는 '문서가 무엇에 관한 것인가'와 다르다. 종속 개념이
#:   주제어보다 자주 등장할 수 있다.
RULES = [
    ("R1-equipment", 4, r"tool-architecture|platen|carrier|retaining[- ]ring|"
                        r"multizone|zone[- ]pressure|endpoint|epd|모터|motor|"
                        r"virtual-metrology|sampling|torque|토크"),
    ("R1-equipment", 3, r"friction|마찰|lubric|윤활|stribeck|heating|발열|"
                        r"thermal|arrhenius|temperature|온도|kinematic|"
                        r"rpm|flowrate|유량"),
    ("R2-slurry", 3, r"slurry|abrasive|ceria|silica|colloid|zeta|dlvo|oxidizer|"
                     r"inhibitor|bta|chelat|surfactant|additive|pourbaix|"
                     r"redox|passivation|입자|슬러리"),
    ("R2-slurry", 2, r"chemistry|화학|selectivity|선택비|particle-wafer|\bph\b"),
    ("R3-pad", 3, r"^pad-|groove|subpad|porosity|glazing|shore|viscoelast|"
                  r"polyurethane|pu-pad|패드|기공"),
    # 디스크 고유어는 패드보다 무겁게 — 컨디셔너 문서엔 'pad'가 필연적으로 많다
    ("R4-disk", 5, r"conditioner|conditioning|^disk-|disk-design|diamond|grit|"
                   r"dresser|pcr|cut[- ]?rate|컨디셔너|디스크|다이아"),
    ("R4-disk", 3, r"sweep|asperity-regeneration|break[- ]?in"),
    ("R5-wafer", 3, r"^wafer-|npw|ptw|metrology|wiwnu|ttv|uniformity|flatness|"
                    r"roughness|dishing|erosion|step[- ]height|thickness|"
                    r"contamination|txrf|defect|^film-|웨이퍼|잔막"),
    ("R5-wafer", 2, r"pattern-|pattern[- ]density"),
]

# 물리 총론은 한 섹션이 독점하지 않는다 — 협업 대상이라 명시적으로 표시한다.
SHARED = re.compile(r"preston|luo-dornfeld|hertz|gw-contact|tribology|"
                    r"contact-mechanics", re.I)


def classify(path: Path, text: str) -> tuple[str, str, str]:
    """(주섹션, 공동섹션, 근거). 애매하면 R0-unassigned.

    ⚠ 초기 구현은 최고점이 2등의 1.5배 미만이면 전부 R0으로 보냈다. 그 결과
      77편 중 48편이 미분배로 나왔다 — 분류기가 못 한 게 아니라 **CMP 노트가
      원래 두 축에 걸치는 게 정상**이기 때문이다("패드 그루브가 슬러리를 어떻게
      나르나"는 R3이자 R2다). 그걸 전부 미분배로 버리면 분배가 무의미해진다.

      그래서 경합은 실패가 아니라 **협업 신호**로 다룬다: 1등을 주섹션,
      2등을 공동섹션으로 기록한다. 사용자가 요구한 "5개 리서치 파트가 협업"이
      바로 이 관계다. 진짜 미분배는 매칭이 아예 없을 때뿐이다.
    """
    hay = (path.name + "\n" + text[:2000]).lower()
    score: Counter = Counter()
    hits: dict = {}
    for sec, w, pat in RULES:
        found = re.findall(pat, hay, re.I)
        if found:
            score[sec] += w * min(len(found), 4)
            hits.setdefault(sec, set()).update(f.lower() for f in found[:4])
    if not score:
        return "R0-unassigned", "", "매칭 키워드 없음 — 사람이 판단"
    top = score.most_common(2)
    sec, sc = top[0]
    co = ""
    if len(top) > 1 and top[1][1] >= sc * 0.5:
        co = top[1][0]          # 절반 이상 득점하면 공동 담당
    why = ", ".join(sorted(hits.get(sec, ()))[:5])
    return sec, co, f"근거: {why}"


def existing_mark(text: str):
    m = MARK_RE.search(text)
    return m.group(1) if m else None


def apply_mark(path: Path, sec: str, co: str, why: str, shared: bool,
               dry: bool) -> str:
    text = path.read_text(encoding="utf-8")
    cur = existing_mark(text)
    if cur:
        return f"skip (이미 {cur})"
    tail = " | 물리 총론 — 여러 섹션 공유" if shared else ""
    cotxt = f" | 공동: {co}" if co else ""
    mark = (f"<!-- V2-SECTION: {sec}{cotxt} | 분배완료 2026-09-08 | "
            f"{why}{tail} | 정본: ARCHITECTURE-V2.md §3 -->\n")
    if not dry:
        path.write_text(mark + text, encoding="utf-8")
    return f"→ {sec}" + (f" (+{co})" if co else "")


def main() -> int:
    ap = argparse.ArgumentParser(description="노트를 V2 5개 섹션에 분배")
    ap.add_argument("--apply", action="store_true", help="실제로 파일에 배지를 쓴다")
    ap.add_argument("--status", action="store_true", help="분배 현황만 집계")
    args = ap.parse_args()

    notes = sorted(p for p in KNOW.rglob("*.md")
                   if p.name != "INDEX.md" and "components" not in p.parts)
    if not notes:
        print("노트를 찾지 못했다", file=sys.stderr)
        return 1

    tally: Counter = Counter()
    collab: Counter = Counter()
    unassigned = []
    for p in notes:
        text = p.read_text(encoding="utf-8")
        cur = existing_mark(text)
        if cur:
            tally[cur] += 1
            if cur == "R0-unassigned":
                unassigned.append(p.relative_to(KNOW))
            continue
        if args.status:
            tally["(미분배)"] += 1
            continue
        sec, co, why = classify(p, text)
        shared = bool(SHARED.search(p.name))
        res = apply_mark(p, sec, co, why, shared, dry=not args.apply)
        tally[sec] += 1
        if co:
            # 쌍은 순서 무관이다 — 정렬해 세지 않으면 R3×R4와 R4×R3가 따로 잡힌다
            collab[" × ".join(sorted([sec, co]))] += 1
        if sec == "R0-unassigned":
            unassigned.append(p.relative_to(KNOW))
        print(f"{str(p.relative_to(KNOW)):68s} {res}")

    print("\n" + "=" * 72)
    print(f"{'섹션':16s} {'노트수':>6s}  설명")
    print("-" * 72)
    for key, label in SECTIONS.items():
        print(f"{key:16s} {tally.get(key,0):6d}  {label}")
    if tally.get("(미분배)"):
        print(f"{'(배지 없음)':16s} {tally['(미분배)']:6d}  --apply로 분배하라")
    print(f"{'합계':16s} {sum(tally.values()):6d}")
    if collab:
        print(f"\n■ 협업 축 (두 섹션이 함께 소유하는 노트) — 사용자 요구 '5개 파트가 협업'")
        for pair, n in collab.most_common():
            print(f"   {pair:34s} {n:3d}편")
    if unassigned:
        print(f"\n⚠ 사람 판단 필요 {len(unassigned)}편 (억지 배정하지 않았다):")
        for u in unassigned:
            print(f"   - {u}")
    if not args.apply and not args.status:
        print("\n(드라이런이었다. 실제 적용은 --apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
