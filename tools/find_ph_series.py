"""검증된 특허 파서(patent_tables2 + patent_join)로 **pH 스윕 계열**을 찾는다.

왜 새 파서를 짜지 않는가
───────────────────────
`tools/patent_tables2.py` 는 열 머리글을 읽어 역할을 배정하고 정답 특허에서
5/5 일치를 확인한 파서다. `tools/patent_join.py` 는 조성표와 결과표를
예시번호로 잇고 역할별 물리범위 검사까지 한다.

같은 일을 다시 짜면 그 검증을 처음부터 다시 해야 한다. 재사용한다.

이 도구가 추가로 하는 것은 하나: **pH 축으로 스윕된 계열만 골라내고,
억제제 유무로 2×2 격자의 어느 칸을 채우는지 판정**한다.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
# patent_join 이 형제 모듈을 bare import 하므로 tools/ 도 경로에 넣는다
sys.path.insert(0, str(ROOT / "tools"))

from patent_join import series_from_patent                # noqa: E402

RAW = ROOT / "_patents" / "raw"
OUT = ROOT / "_patents" / "cu_ph_series.json"
VALLEY_PH = 6.25

INHIB = re.compile(
    r"benzotriazole|\bBTA\b|tolyltriazole|\bTTA\b|triazole|imidazole|"
    r"mercaptobenzothiazole|\bMBT\b|quinaldic|nicotinic|azole",
    re.IGNORECASE)
NEG = re.compile(
    r"(BTA|benzotriazole|inhibitor|azole)[^.\n]{0,24}(free|absent|without|no\s)"
    r"|(free of|without|containing no)\s+\w{0,12}\s?"
    r"(BTA|benzotriazole|inhibitor|azole)", re.IGNORECASE)
CU = re.compile(r"\bcopper\b|\bCu\b", re.IGNORECASE)


def main() -> int:
    files = sorted(RAW.glob("*.json"))
    found, scanned = [], 0
    for f in files:
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        txt = d.get("fulltext") or ""
        if not txt:
            continue
        scanned += 1
        try:
            s = series_from_patent(str(d.get("patent")), txt)
        except Exception:
            continue
        if s is None:
            continue
        # ⚠ 축 키는 '원래 열이름|역할' 형식이다 (예: 'pH|ph', '(wt %)|wt_pct').
        #   키를 통째로 비교하면 영영 안 맞는다 — **역할 접미사**로 찾는다.
        axes = getattr(s, "axes", None) or {}
        ph = None
        for k, v in axes.items():
            if str(k).rsplit("|", 1)[-1].strip().lower() in ("ph", "slurry_ph"):
                ph = v
                break
        if not ph or len(set(ph)) < 3:
            continue
        span = max(ph) - min(ph)
        if span < 1.0:
            continue

        has_inh = bool(INHIB.search(txt)) and not NEG.search(txt)
        alk = sum(1 for p in ph if p > VALLEY_PH)
        cell = ("알칼리" if alk >= 3 else
                "산성" if (len(ph) - alk) >= 3 else "혼합")
        found.append({
            "patent": str(d.get("patent")),
            "title": str(d.get("title", ""))[:64],
            "cell": cell, "inhibitor": has_inh,
            "ph": ph, "rate": getattr(s, "rates", None),
            "n": len(ph), "span": span,
            "is_cu": bool(CU.search(txt)),
        })

    OUT.write_text(json.dumps(found, ensure_ascii=False, indent=1), encoding="utf-8")
    print("=" * 88)
    print(f"전문 {scanned}건 파싱 → pH 스윕 계열 {len(found)}건")
    print("=" * 88)

    want = {("산성", False), ("알칼리", True)}
    prio = [h for h in found if (h["cell"], h["inhibitor"]) in want]
    print(f"\n■ 빈 칸을 채울 후보 {len(prio)}건")
    for h in sorted(prio, key=lambda x: -x["n"]):
        print(f"  {h['cell']:4s} 억제제{'유' if h['inhibitor'] else '무'} "
              f"{h['patent']:>10s} n={h['n']:2d} "
              f"pH {min(h['ph']):.1f}~{max(h['ph']):.1f}  {h['title'][:40]}")

    print(f"\n■ 그 외 {len(found) - len(prio)}건")
    for h in sorted((x for x in found if x not in prio),
                    key=lambda x: -x["n"])[:12]:
        print(f"  {h['cell']:4s} 억제제{'유' if h['inhibitor'] else '무'} "
              f"{h['patent']:>10s} n={h['n']:2d} "
              f"pH {min(h['ph']):.1f}~{max(h['ph']):.1f}  {h['title'][:40]}")
    print(f"\n→ {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
