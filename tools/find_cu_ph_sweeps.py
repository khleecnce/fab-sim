"""확보한 특허 전문에서 **pH 스윕 + 억제제 유무**를 갖춘 표를 찾는다.

목적
────
구리 알칼리 가지의 k 가 'pH 구간' 때문인지 '억제제 유무' 때문인지 분리하려면
2×2 격자의 빈 두 칸을 채워야 한다:
  · 산성  / 억제제 무
  · 알칼리 / 억제제 유

⚠ 판정 기준에 물질명을 넣지 않는다. 기준은 세 가지다:
  ① pH 가 최소 1 단위 이상 스윕되는가
  ② 그 표의 조성 설명에 억제 작용기 첨가제가 선언됐는가(유/무)
  ③ 제거율 열이 함께 있는가
"""
import json
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RAW = ROOT / "_patents" / "raw"

INHIB = re.compile(
    r"benzotriazole|\bBTA\b|tolyltriazole|\bTTA\b|triazole|imidazole|"
    r"mercaptobenzothiazole|\bMBT\b|quinaldic|nicotinic",
    re.IGNORECASE)
NEG = re.compile(
    r"(BTA|benzotriazole|inhibitor)[^.\n]{0,20}(free|absent|without|no\s)"
    r"|(free of|without|no)\s+(BTA|benzotriazole|inhibitor)", re.IGNORECASE)
CU = re.compile(r"\bcopper\b|\bCu\b", re.IGNORECASE)
PH_VAL = re.compile(r"\bpH\b[^\n]{0,40}?([0-9]+\.[0-9]|[0-9]{1,2})\b", re.IGNORECASE)
RATE = re.compile(r"removal rate|polish(?:ing)? rate|\bRR\b|Å/min|A/min|nm/min",
                  re.IGNORECASE)


def main() -> int:
    if not RAW.exists():
        print(f"❌ 특허 캐시 없음: {RAW}")
        return 1
    # 캐시는 JSON 이고 전문은 'fulltext' 키에 있다(365건 중 108건 보유).
    files = sorted(RAW.glob("*.json"))
    print("=" * 84)
    print(f"특허 캐시 {len(files)}건에서 구리 pH 스윕 표 탐색")
    print("=" * 84)

    hits = []
    n_full = 0
    for f in files:
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        txt = d.get("fulltext") or ""
        if not txt:
            continue
        n_full += 1
        if not CU.search(txt) or not RATE.search(txt):
            continue
        phs = {float(m.group(1)) for m in PH_VAL.finditer(txt)
               if 0.5 <= float(m.group(1)) <= 14.0}
        if len(phs) < 3:
            continue
        span = max(phs) - min(phs)
        if span < 1.0:
            continue
        has_inh = bool(INHIB.search(txt)) and not NEG.search(txt)
        alk = [p for p in phs if p > 6.25]
        acid = [p for p in phs if p <= 6.25]
        cell = ("알칼리" if len(alk) >= 3 else "산성" if len(acid) >= 3 else "혼합")
        title = str(d.get("title", ""))[:40]
        hits.append((f"{f.stem} {title}", cell, has_inh, sorted(phs), span))

    print(f"전문 보유 {n_full}건 · 구리+제거율+pH스윕 후보 {len(hits)}건")
    want = {("산성", False), ("알칼리", True)}
    prio = [h for h in hits if (h[1], h[2]) in want]
    other = [h for h in hits if (h[1], h[2]) not in want]

    print(f"\n■ 빈 칸을 채울 후보 {len(prio)}건 (우선)")
    for stem, cell, inh, phs, span in sorted(prio, key=lambda x: -x[4])[:15]:
        print(f"  {cell:4s} 억제제{'유' if inh else '무'}  {stem[:46]:46s} "
              f"pH폭 {span:4.1f}  {phs[:7]}")

    print(f"\n■ 그 외 pH 스윕 후보 {len(other)}건")
    for stem, cell, inh, phs, span in sorted(other, key=lambda x: -x[4])[:12]:
        print(f"  {cell:4s} 억제제{'유' if inh else '무'}  {stem[:46]:46s} "
              f"pH폭 {span:4.1f}  {phs[:7]}")

    out = ROOT / "_patents" / "cu_ph_candidates.json"
    out.write_text(json.dumps(
        [{"patent": s, "cell": c, "inhibitor": i, "ph": p, "span": sp}
         for s, c, i, p, sp in hits], ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"\n→ {out.relative_to(ROOT)} 에 {len(hits)}건 기록")
    print("\n⚠ 이 목록은 **후보**다. pH 가 본문 여기저기 흩어져 잡혔을 수 있으므로")
    print("  실제 표를 열어 '한 표 안에서 pH 만 변하는가'를 확인해야 한다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
