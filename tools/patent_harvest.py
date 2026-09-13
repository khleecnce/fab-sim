"""공개 특허에서 CMP 실시예 데이터를 대량 수집한다.

왜 필요한가
──────────
검증 데이터셋이 20개뿐이고 파라미터 팩이 5개뿐이었다. 이유는 데이터가 없어서가
아니라 **수집 경로를 만들지 않아서**였다 — CMP 슬러리 특허는 수천 건이 공개돼
있고, 그 대부분이 실시예 표에 "조성 → 제거율"을 인쇄된 숫자로 싣고 있다.
표에서 읽은 숫자는 그래프 픽셀 판독과 달리 판독 오차가 0이다.

수집 경로
────────
FreePatentsOnline(FPO)이 전문 HTML을 그대로 준다.
(Google Patents·Espacenet·EPO OPS·PatentsView는 이 환경에서 403/503으로 막힘.)

    검색 : /result.html?query_txt=...   → 특허번호 목록
    전문 : /<번호>.html                  → 실시예 표 포함 전문

이 스크립트가 하는 일
───────────────────
1) 질의어로 특허번호를 모은다 (여러 페이지)
2) 각 전문을 받아 실시예 표 후보 구간을 뽑는다
3) "조성 축이 변하고 제거율이 함께 적힌" 표만 남긴다
4) 원문 그대로 캐시에 저장한다 (해석은 다음 단계에서)

⚠ 이 단계에서 숫자를 해석하지 않는다. 수집과 해석을 섞으면 잘못 읽은 값이
  조용히 데이터셋이 된다. 여기서는 **원문 보존**만 한다.

⚠ 서버에 부담을 주지 않도록 요청 간 지연을 둔다.
"""

from __future__ import annotations

import gzip
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request
from typing import Dict, Iterable, List, Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "_patents" / "raw"
INDEX = ROOT / "_patents" / "index.jsonl"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
BASE = "https://www.freepatentsonline.com"
DELAY_S = 1.5          # 서버 예의
TIMEOUT_S = 40


def _get(url: str, timeout: int = TIMEOUT_S, tries: int = 4) -> str:
    """재시도 포함 GET.

    ⚠ 이 서버는 연속 요청에 'Connection reset by peer'(errno 54)를 자주 낸다.
      한 번 실패했다고 포기하면 수집이 0건으로 끝난다(실제로 겪었다).
      지수적으로 기다리며 다시 시도한다.
    """
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
            return raw.decode("utf-8", "ignore")
        except Exception as e:            # noqa: BLE001
            last = e
            time.sleep(DELAY_S * (2 ** i))
    raise last if last else RuntimeError("unreachable")


def search(query: str, pages: int = 3) -> List[str]:
    """질의어로 특허번호를 모은다."""
    found: List[str] = []
    for p in range(1, pages + 1):
        q = urllib.parse.quote(query)
        url = f"{BASE}/result.html?query_txt={q}&submit=&patents=on&p={p}"
        try:
            html = _get(url)
        except Exception as e:
            print(f"  ⚠ 검색 {p}쪽 실패: {type(e).__name__}", file=sys.stderr)
            break
        nums = re.findall(r'/(\d{7,8})\.html', html)
        new = [n for n in dict.fromkeys(nums) if n not in found]
        if not new:
            break
        found.extend(new)
        print(f"  {p}쪽: +{len(new)}건 (누적 {len(found)})")
        time.sleep(DELAY_S)
    return found


def _strip(html: str) -> str:
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", t)


# 제거율 단위 — 특허마다 표기가 제각각이다
RATE_UNITS = [r"Å\s*/\s*min", r"A\s*/\s*min", r"angstrom[s]?\s*/\s*min",
              r"nm\s*/\s*min", r"µm\s*/\s*min", r"um\s*/\s*min"]
RATE_RE = re.compile("|".join(RATE_UNITS), re.I)

# 조성 축 — 이 중 하나가 표 안에서 변해야 쓸모가 있다
COMP_HINTS = ["wt %", "wt. %", "wt%", "ppm", "pH", "mol", "concentration",
              "abrasive", "oxidizer", "H 2 O 2", "H2O2", "inhibitor",
              "particle size", "nm "]


def extract_tables(text: str) -> List[Dict[str, object]]:
    """실시예 표 후보 구간을 뽑는다 (해석하지 않음)."""
    out = []
    for m in re.finditer(r"TABLE\s+[\dIVX]+", text, re.I):
        start = m.start()
        seg = text[start:start + 2500]
        if not RATE_RE.search(seg):
            continue
        hits = [h for h in COMP_HINTS if h.lower() in seg.lower()]
        if len(hits) < 2:
            continue
        nums = re.findall(r"\d[\d,]*\.?\d*", seg)
        out.append({
            "header": m.group(0),
            "composition_axes": hits[:8],
            "numeric_tokens": len(nums),
            "text": seg,
        })
    return out


def harvest_one(num: str) -> Optional[Dict[str, object]]:
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{num}.json"
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))
    try:
        html = _get(f"{BASE}/{num}.html")
    except Exception as e:
        return {"patent": num, "error": f"{type(e).__name__}: {e}"}
    text = _strip(html)
    title_m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    tables = extract_tables(text)
    rec = {
        "patent": num,
        "title": (title_m.group(1).strip() if title_m else ""),
        "url": f"{BASE}/{num}.html",
        "n_tables": len(tables),
        "tables": tables,
        "has_rate": bool(RATE_RE.search(text)),
        "chars": len(text),
        # ⚠ 전문을 통째로 남긴다.
        #   표 구간만 잘라 두었더니 조성표와 결과표가 멀리 떨어진 특허에서
        #   결과표가 통째로 사라졌고, 나중에 join 하려 할 때 되살릴 방법이
        #   없었다. 재수집은 비싸고 서버에도 부담이다 — 원문 보존이 원칙.
        "fulltext": text,
    }
    cached.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    return rec


QUERIES = {
    # 막질별로 나눠 질의한다 — 한 질의로는 한쪽 계에 쏠린다.
    "oxide": 'SPEC/"chemical mechanical polishing" AND SPEC/"removal rate" AND SPEC/"silica" AND SPEC/"oxide film"',
    "ceria": 'SPEC/"chemical mechanical polishing" AND SPEC/"ceria" AND SPEC/"removal rate"',
    "tungsten": 'SPEC/"chemical mechanical polishing" AND SPEC/"tungsten" AND SPEC/"removal rate"',
    "copper": 'SPEC/"chemical mechanical polishing" AND SPEC/"copper" AND SPEC/"removal rate" AND SPEC/"inhibitor"',
    "poly_si": 'SPEC/"chemical mechanical polishing" AND SPEC/"polysilicon" AND SPEC/"removal rate"',
    "nitride": 'SPEC/"chemical mechanical polishing" AND SPEC/"silicon nitride" AND SPEC/"removal rate"',
    "sic": 'SPEC/"chemical mechanical polishing" AND SPEC/"silicon carbide" AND SPEC/"removal rate"',
    "tin_barrier": 'SPEC/"chemical mechanical polishing" AND SPEC/"titanium nitride" AND SPEC/"removal rate"',
}


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default="all", help="수집할 막질군 (기본 all)")
    ap.add_argument("--pages", type=int, default=3)
    ap.add_argument("--limit", type=int, default=40, help="군당 전문 수집 상한")
    args = ap.parse_args()

    groups = QUERIES if args.group == "all" else {args.group: QUERIES[args.group]}
    INDEX.parent.mkdir(parents=True, exist_ok=True)

    total_new = 0
    with INDEX.open("a", encoding="utf-8") as idx:
        for gname, q in groups.items():
            print(f"\n=== {gname} ===")
            nums = search(q, pages=args.pages)
            print(f"  검색 결과 {len(nums)}건 → 전문 {min(len(nums), args.limit)}건 수집")
            kept = 0
            for i, num in enumerate(nums[:args.limit]):
                rec = harvest_one(num)
                if not rec or rec.get("error"):
                    continue
                rec["group"] = gname
                if rec["n_tables"] > 0:
                    kept += 1
                    idx.write(json.dumps(rec | {"tables": len(rec["tables"])},
                                         ensure_ascii=False) + "\n")
                total_new += 1
                if (i + 1) % 10 == 0:
                    print(f"    {i+1}/{min(len(nums), args.limit)} … 표 보유 {kept}건")
                time.sleep(DELAY_S)
            print(f"  → 실시예 표를 가진 특허 {kept}건")

    print(f"\n총 {total_new}건 처리. 캐시: {CACHE}")
    print(f"색인: {INDEX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
