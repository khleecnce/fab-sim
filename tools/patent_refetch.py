"""표를 가진 특허의 전문을 다시 받아 캐시를 채운다.

왜 필요한가: 첫 수집은 표 구간만 2500자씩 잘라 저장했다. 그런데 특허는
조성표와 결과표를 멀리 떨어뜨려 싣기 때문에, 잘라낸 구간만으로는 둘을
이어 붙일 수 없다. 전문이 있어야 예시번호로 join 할 수 있다.

표가 있는 특허만 대상으로 한다 — 표가 없는 것은 애초에 쓸 데이터가 없다.
"""
from __future__ import annotations

import gzip
import json
import pathlib
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "_patents" / "raw"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
BASE = "https://www.freepatentsonline.com"
DELAY = 1.6


def _get(url: str, tries: int = 4) -> str:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
            return raw.decode("utf-8", "ignore")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(DELAY * (2 ** i))
    raise last if last else RuntimeError("unreachable")


def strip(html: str) -> str:
    import re
    t = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t).replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", t)


def main() -> int:
    targets = []
    for f in sorted(CACHE.glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        if r.get("n_tables", 0) > 0 and not r.get("fulltext"):
            targets.append((f, r))
    print(f"전문 재수집 대상 {len(targets)}건")
    done = fail = 0
    for i, (f, r) in enumerate(targets, 1):
        try:
            html = _get(f"{BASE}/{r['patent']}.html")
            r["fulltext"] = strip(html)
            f.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
            done += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠ {r['patent']}: {type(e).__name__}")
            fail += 1
        if i % 20 == 0:
            print(f"  {i}/{len(targets)} … 성공 {done} 실패 {fail}")
        time.sleep(DELAY)
    print(f"완료: 성공 {done} / 실패 {fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
