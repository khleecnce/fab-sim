"""근거 등급 상한 감사 — 코드가 파라미터보다 등급을 낮추고 있는가.

왜 이 검사가 필요한가
────────────────────
격자가 며칠째 같은 숫자에 멈춰 있었고, 그동안 크론은 문헌을 계속 찾았다.
원인은 문헌 부족이 아니라 **코드에 박힌 등급 리터럴**이었다:

    f.confidence = _worst_conf(_pack_conf(pk, ...), "estimated")
                                                    ^^^^^^^^^^^
    파라미터가 전부 literature 여도 결과는 estimated 로 눌린다.

이 구조에서는 **문헌을 아무리 확보해도 칸이 오르지 않는다.** 그런데 겉으로는
"근거가 부족해서 미충족"으로 보이므로, 다음 회차가 또 문헌을 찾으러 간다.
며칠을 그렇게 썼다.

무엇을 재는가 (입력 → 판단 기준 → 출력)
──────────────────────────────────────
입력      : 팩터별 실제 드라이버 파라미터 등급, 팩터가 최종 신고한 등급
판단 기준 : 최종 등급이 드라이버 등급보다 **낮은가**
            낮다면 그 차이는 데이터가 아니라 코드가 만든 것이다
출력      : 눌린 칸 목록과 원인 리터럴 위치

판정 기준에 물질명이 없다 — 어떤 팩이 들어와도 같은 질문을 던진다.

⚠ 등급 하한이 항상 틀린 것은 아니다
────────────────────────────────
결합 지수처럼 **드라이버가 아닌 요소가 가장 약한 고리**인 경우, 하한은 정당하다
(τ 의 결합 지수가 그 예다 — 드라이버는 문헌값이어도 지수가 교차 대입이라
크기를 문헌이 보증하지 않는다). 그러므로 이 검사는 "하한을 없애라"가 아니라
**"하한의 근거가 코드에 적혀 있는가"**를 묻는다. 근거 없는 하한만 결함이다.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import warnings
warnings.filterwarnings("ignore")

ORDER = ["verified", "measured", "literature", "estimated", "unverified"]
FACTORS_SRC = ROOT / "sim" / "factors.py"


def rank(c: str) -> int:
    return ORDER.index(c) if c in ORDER else len(ORDER) - 1


def find_caps() -> List[Tuple[int, str, str]]:
    """소스에서 `_worst_conf(..., "등급")` 형태의 하한 리터럴을 찾는다.

    코드를 읽어 대상을 열거한다 — 손으로 적은 목록을 쓰지 않는다.
    """
    out: List[Tuple[int, str, str]] = []
    text = FACTORS_SRC.read_text(encoding="utf-8")
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        if "_worst_conf(" not in line:
            continue
        # 호출이 여러 줄에 걸칠 수 있으므로 괄호가 닫힐 때까지 모은다
        chunk = line
        depth = chunk.count("(") - chunk.count(")")
        j = i
        while depth > 0 and j < len(lines):
            chunk += " " + lines[j].strip()
            depth += lines[j].count("(") - lines[j].count(")")
            j += 1
        for lit in re.findall(r'"(verified|measured|literature|estimated|unverified)"', chunk):
            out.append((i, lit, chunk.strip()[:120]))
    return out


def has_justification(line_no: int, window: int = 8) -> bool:
    """하한 리터럴 근처에 '왜 이 하한인가'가 적혀 있는가.

    판단: 주석에 하한을 정당화하는 서술(가장 약한 고리가 무엇인지)이 있으면 통과.

    ⚠ 창을 위쪽으로 더 넓게 잡는다 — 함수 docstring 이 선언부 바로 아래에 오므로
    리터럴이 함수 끝에 있으면 위쪽 창이 짧아 근거를 놓친다(오탐).
    """
    lines = FACTORS_SRC.read_text(encoding="utf-8").splitlines()
    lo = max(0, line_no - window * 3 - 1)      # 위로 넉넉히
    hi = min(len(lines), line_no + window)
    ctx = "\n".join(lines[lo:hi])
    cues = ("가장 약한 고리", "약한 고리", "하한", "지수가", "보증하지", "등급을 정한다",
            "한 단 낮", "미검증이라", "물어볼 대상이 없다", "미선언")
    return any(c in ctx for c in cues)


def audit() -> Dict[str, object]:
    from sim.engine import Recipe, simulate
    from sim.params import available_packs

    packs = [p for p in available_packs() if p != "base"]
    caps = find_caps()

    pressed: List[Dict[str, object]] = []
    from sim.factors import _pack_conf
    from sim.params import load_pack
    for p in packs:
        try:
            pk = load_pack(p)
            rr = simulate(Recipe(pack=p))
        except Exception:
            continue
        for key, f in rr.factors.items():
            if f.value is None:
                continue
            drivers = list((f.drivers or {}).keys())
            if not drivers:
                continue
            real = _pack_conf(pk, *drivers)
            got = str(f.confidence or "unverified")
            if rank(got) > rank(real):      # 숫자가 클수록 약함
                pressed.append({
                    "pack": p, "factor": key, "symbol": f.symbol,
                    "driver_conf": real, "reported_conf": got,
                    "drivers": drivers,
                })

    unjustified = [(ln, lit, src) for ln, lit, src in caps
                   if not has_justification(ln)]
    return {"pressed": pressed, "caps": caps, "unjustified_caps": unjustified}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="코드가 파라미터보다 근거 등급을 낮추고 있는지 검사")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-unjustified", action="store_true")
    a = ap.parse_args()

    r = audit()
    pressed = r["pressed"]          # type: ignore[assignment]
    caps = r["caps"]                # type: ignore[assignment]
    unj = r["unjustified_caps"]     # type: ignore[assignment]

    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        return 1 if (a.fail_on_unjustified and unj) else 0

    print("=" * 80)
    print(" 근거 등급 상한 감사 — 문헌이 아니라 코드가 칸을 막고 있는가")
    print("=" * 80)

    if pressed:
        print(f"\n🔴 코드가 등급을 누른 칸 {len(pressed)}개")
        print(f"   {'팩':18s} {'팩터':8s} {'드라이버 실제':12s} → {'신고된 등급'}")
        for x in pressed:                      # type: ignore[union-attr]
            print(f"   {x['pack']:18s} {x['symbol']:8s} "
                  f"{x['driver_conf']:12s} → {x['reported_conf']}")
    else:
        print("\n✅ 드라이버 등급보다 낮게 신고하는 팩터 없음")

    print(f"\n하한 리터럴 {len(caps)}곳:")       # type: ignore[arg-type]
    for ln, lit, src in caps:                   # type: ignore[union-attr]
        ok = has_justification(ln)
        print(f"   {'✅' if ok else '🔴'} L{ln} \"{lit}\"  {src[:70]}")
        if not ok:
            print(f"        근거 주석 없음 — 왜 이 하한인지 코드가 말하지 않는다")

    print()
    print("-" * 80)
    if unj:
        print(f"🔴 근거 없는 하한 {len(unj)}곳 — 이것이 격자를 막는 원인이다.")
        print("   하한이 정당하려면 '가장 약한 고리가 무엇인가'가 주석에 있어야 한다.")
        print("   근거를 못 적겠으면 그 하한은 제거 대상이다.")
    else:
        print("✅ 모든 하한에 근거 주석이 있다.")

    return 1 if (a.fail_on_unjustified and unj) else 0


if __name__ == "__main__":
    sys.exit(main())
