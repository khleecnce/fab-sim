"""후보 특허의 **표 안**에서 pH 열과 제거율 열을 실제로 뽑는다.

왜 한 단계 더 필요한가
─────────────────────
find_cu_ph_sweeps.py 는 본문 전체에서 pH 숫자를 긁으므로 청구항의 범위 서술
("pH 1 to 14")까지 잡힌다. 그 상태로 데이터셋을 만들면 존재하지 않는 스윕을
검증 기준으로 삼게 된다 — 지금까지 쌓은 검증이 통째로 무의미해진다.

그래서 **표 단위**로 내려가 다음을 모두 만족할 때만 채택한다:
  ① 한 표 안에 pH 열과 제거율 열이 함께 있다
  ② pH 가 표 안에서 최소 1.0 단위 이상 변한다
  ③ pH 값이 물리 범위(0.5~14) 안이다
  ④ 제거율이 양수다

⚠ 정확도 우선, 수율 후순위. 열 이름이 확실히 복원된 표만 쓰고 애매하면 버린다.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RAW = ROOT / "_patents" / "raw"
OUT = ROOT / "_patents" / "cu_ph_table_hits.json"

PH_COL = re.compile(r"^\s*p\s*H\s*$|^\s*pH\b", re.IGNORECASE)
RATE_COL = re.compile(
    r"removal\s*rate|polish(?:ing)?\s*rate|\bRR\b|\bMRR\b|Å\s*/\s*min|A\s*/\s*min|"
    r"nm\s*/\s*min|rate\s*\(", re.IGNORECASE)
CU_COL = re.compile(r"\bcu\b|copper", re.IGNORECASE)
NUM = re.compile(r"-?\d+(?:\.\d+)?")


def cells(table) -> list:
    """표를 2차원 문자열 배열로 정규화한다."""
    if isinstance(table, list) and table and isinstance(table[0], list):
        return [[str(c) for c in row] for row in table]
    if isinstance(table, str):
        return [re.split(r"\s{2,}|\t|\|", ln.strip())
                for ln in table.split("\n") if ln.strip()]
    return []


def main() -> int:
    hits = []
    for f in sorted(RAW.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        tables = d.get("tables") or []
        if not tables:
            continue
        for ti, t in enumerate(tables):
            grid = cells(t)
            if len(grid) < 3:
                continue
            # 머리글 행 찾기 — pH 열과 rate 열이 같은 행에 있어야 한다
            for hi in range(min(4, len(grid))):
                hdr = grid[hi]
                ph_i = next((j for j, c in enumerate(hdr) if PH_COL.search(c)), None)
                rate_js = [j for j, c in enumerate(hdr) if RATE_COL.search(c)]
                if ph_i is None or not rate_js:
                    continue
                # 구리 제거율 열 우선
                cu_js = [j for j in rate_js if CU_COL.search(hdr[j])]
                rate_i = (cu_js or rate_js)[0]

                phs, rates = [], []
                for row in grid[hi + 1:]:
                    if max(ph_i, rate_i) >= len(row):
                        continue
                    mp = NUM.search(row[ph_i])
                    mr = NUM.search(row[rate_i])
                    if not mp or not mr:
                        continue
                    p, r = float(mp.group()), float(mr.group())
                    if 0.5 <= p <= 14.0 and r > 0:
                        phs.append(p)
                        rates.append(r)
                if len(phs) >= 3 and (max(phs) - min(phs)) >= 1.0:
                    hits.append({
                        "patent": d.get("patent"),
                        "title": str(d.get("title", ""))[:70],
                        "table": ti,
                        "n": len(phs),
                        "ph": phs,
                        "rate": rates,
                        "rate_col": hdr[rate_i][:40],
                        "is_cu_col": bool(cu_js),
                    })
                break

    OUT.write_text(json.dumps(hits, ensure_ascii=False, indent=1), encoding="utf-8")
    print("=" * 84)
    print(f"표 안에서 pH 스윕 + 제거율이 함께 확인된 표: {len(hits)}건")
    print("=" * 84)
    for h in sorted(hits, key=lambda x: -x["n"])[:20]:
        span = max(h["ph"]) - min(h["ph"])
        print(f"  {h['patent']:>10s} T{h['table']}  n={h['n']:2d}  "
              f"pH {min(h['ph']):.1f}~{max(h['ph']):.1f} (폭 {span:.1f})  "
              f"{'Cu열' if h['is_cu_col'] else '일반'}  {h['title'][:44]}")
    print(f"\n→ {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
