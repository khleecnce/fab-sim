#!/usr/bin/env python3
"""특허 실시예에서 조성-제거율 데이터를 뽑는다.

왜 특허인가 (2026-09-06):
  백테스트에 필요한 건 "조성을 바꿨더니 MRR이 이렇게 변했다"는 표다. 그런데
  오픈액세스 논문은 대부분 그래프라서 digitized가 강제되고, 그건 검증을 오염시킨다.

  CMP 슬러리 특허는 이 문제가 없다:
    - 실시예(Example)에 조성과 제거율이 **인쇄된 숫자 표**로 들어간다
    - 비교예(Comparative Example)가 같이 있어 조건 간 순위 비교가 바로 된다
    - 전문이 무료이고 저작권 제약이 없다(공개 문서)
  즉 우리가 필요한 데이터 형태와 특허의 서술 관습이 정확히 맞아떨어진다.

## ⚠ 이 스크립트가 하지 않는 것

**자동 추출을 그대로 데이터셋으로 쓰지 않는다.** 특허 표는 구조가 제각각이라
파서가 셀을 잘못 짝지을 수 있고, 그렇게 만든 "검증 데이터"는 검증이 아니라 소음이다.

이 스크립트는 **후보를 좁히고 사람이 확인할 표를 뽑아주는 데까지만** 한다:
  1. 실시예에 MRR 수치가 실제로 있는 특허를 걸러낸다
  2. 그 표를 사람이 읽을 수 있는 텍스트로 덤프한다
  3. 데이터셋 YAML 초안을 만들되 `verified: false`로 표시한다

사람(또는 후속 에이전트)이 원문과 대조해 확인한 뒤에야 `verified: true`가 되고,
그때부터 백테스트 집계에 들어간다. backtest.py가 이 플래그를 강제한다.

## 사용
    python tools/patent_mine.py --search "CMP slurry ceria removal rate"
    python tools/patent_mine.py --fetch US6620215B2
    python tools/patent_mine.py --dump US6620215B2      # 표를 눈으로 확인
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from patent_sources import (classify_assignee, screen_condition,  # noqa: E402
                            internal_consistency, PHYSICAL_RANGE)

_ROOT = Path(__file__).resolve().parent.parent
CACHE = _ROOT / "papers" / "patents"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")

# 제거율 단위 → nm/min 환산. 특허는 Å/min을 압도적으로 많이 쓴다.
RATE_UNITS = {
    "nm/min": 1.0, "nm/minute": 1.0,
    "A/min": 0.1, "Å/min": 0.1, "angstrom/min": 0.1, "A/minute": 0.1,
    "um/min": 1000.0, "µm/min": 1000.0, "micron/min": 1000.0,
}

# 인용목록·참고문헌 표를 걸러내는 신호 (실제 데이터 표가 아니다)
NOISE_MARKERS = ("Cited by", "Priority date", "Publication number",
                 "Legal Events", "Similar Documents", "Family")


# 요청 간격 — 2026-09-06에 1.0초로 돌렸다가 73건 연속 503을 맞았다.
# Google Patents는 짧은 간격의 연속 요청을 차단한다. 느린 게 안 도는 것보다 낫다.
_MIN_INTERVAL = 2.5
_last_request = [0.0]


def fetch(patent_id: str, force: bool = False, retries: int = 3) -> Optional[str]:
    """Google Patents 원문 HTML. 캐시 + 속도제한 + 지수 백오프.

    캐시는 재실행 시 이미 받은 것을 건너뛰게 해준다 — 중단됐다 재개해도
    처음부터 다시 긁지 않는다(수천 건 규모에서 이게 결정적이다).
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{patent_id}.html"
    if cached.exists() and not force:
        return cached.read_text(encoding="utf-8", errors="ignore")

    url = f"https://patents.google.com/patent/{patent_id}/en"
    for attempt in range(retries):
        gap = time.time() - _last_request[0]
        if gap < _MIN_INTERVAL:
            time.sleep(_MIN_INTERVAL - gap)
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", errors="ignore")
            _last_request[0] = time.time()
            cached.write_text(body, encoding="utf-8")
            return body
        except Exception as e:
            _last_request[0] = time.time()
            code = getattr(e, "code", None)
            if code in (429, 503) and attempt < retries - 1:
                back = _MIN_INTERVAL * (3 ** (attempt + 1))
                print(f"  … {patent_id} {code} — {back:.0f}s 대기 후 재시도",
                      file=sys.stderr)
                time.sleep(back)
                continue
            print(f"  ! {patent_id} 실패: {e}", file=sys.stderr)
            return None
    return None


def assignees(page: str) -> List[str]:
    """**이 특허 자신의** 출원인·양수인만 뽑는다.

    ⚠ 2026-09-06에 밟은 함정: `itemprop="assigneeOriginal"`은 페이지 전체에서
    매칭되는데, 그 안에는 **인용 특허(Similar Documents / Cited By) 목록의
    출원인**이 섞여 있다. US6620215B2(실제 출원인 Dynea Canada)를 긁으면
    'JSR Corporation'·'Nihon Microcoating'이 함께 나오고, 화이트리스트가
    JSR에 매칭돼 **신뢰할 수 없는 특허가 게이트를 통과했다.**

    출원인 필터가 데이터 품질의 1차 방어선인데 그게 뚫리면 필터 전체가 무의미하다.
    그래서 문서 메타데이터(<head>의 DC.contributor scheme=assignee)만 신뢰하고,
    본문 스캔은 head에서 아무것도 못 찾았을 때의 폴백으로만 쓴다.
    """
    out: List[str] = []

    # 1순위: <head> 메타데이터 — 이 문서 자신의 출원인만 들어간다
    for m in re.finditer(
            r'<meta\s+name="DC.contributor"\s+content="([^"]+)"\s+scheme="assignee"', page):
        out.append(html.unescape(m.group(1)).strip())

    if not out:
        # 폴백: 본문 상단(인용 섹션 이전)에서만 찾는다
        cut = len(page)
        for marker in ("Similar Documents", "Cited By", "Citations (",
                       "Patent Citations", "id=\"similarDocuments\""):
            i = page.find(marker)
            if i > 0:
                cut = min(cut, i)
        head_zone = page[:cut]
        out += [html.unescape(x).strip() for x in
                re.findall(r'itemprop="assigneeOriginal"[^>]*>([^<]+)<', head_zone)]

    seen, uniq = set(), []
    for n in out:
        if n and n.lower() not in seen:
            seen.add(n.lower())
            uniq.append(n)
    return uniq


def inventors(page: str) -> List[str]:
    return [html.unescape(x).strip() for x in
            re.findall(r'<meta name="DC.contributor" content="([^"]+)"', page)]


def _table_text(tbl: str) -> str:
    txt = re.sub(r"<[^>]+>", " ", tbl)
    return re.sub(r"\s+", " ", html.unescape(txt)).strip()


def data_tables(page: str) -> List[str]:
    """실시예 데이터 표만 남긴다 — 인용목록·법적사건 표를 버린다."""
    out = []
    for tbl in re.findall(r"<table.*?</table>", page, re.S):
        txt = _table_text(tbl)
        if len(txt) < 80:
            continue
        if any(m in txt for m in NOISE_MARKERS):
            continue
        low = txt.lower()
        if not any(k in low for k in ("removal rate", "polishing rate", "rate (",
                                      "removal", "polish")):
            continue
        if not re.search(r"\d", txt):
            continue
        out.append(txt)
    return out


def rate_unit_in(text: str) -> Optional[Tuple[str, float]]:
    for u, f in RATE_UNITS.items():
        if u.lower() in text.lower():
            return u, f
    return None


def assess(patent_id: str, page: str) -> Dict:
    """이 특허가 백테스트 후보로 쓸 만한지 판정한다.

    게이트는 두 단계다:
      1차 = 출원인 신뢰도 (사용자 지시: 대학 또는 CMP 메이저 기업만)
      2차 = 데이터 형태 (실시예·제거율 단위·표)
    1차를 통과 못 하면 데이터가 아무리 좋아도 쓰지 않는다.
    """
    names = assignees(page)
    trusted, category, matched = classify_assignee(names)
    tables = data_tables(page)
    joined = " ".join(tables)
    unit = rate_unit_in(joined) or rate_unit_in(page)
    n_examples = len(set(re.findall(r"Example\s+(\d+)", page)))
    n_comp = len(set(re.findall(r"Comparative Example\s+(\d+)", page)))
    title_m = re.search(r"<title>(.*?)</title>", page, re.S)
    title = html.unescape(title_m.group(1)).strip() if title_m else patent_id

    # 조성 변수가 실제로 언급되는가 (조성 스크리닝 검증에 필요)
    comp_kw = [k for k in ("abrasive", "silica", "ceria", "alumina", "oxidizer",
                           "hydrogen peroxide", "BTA", "benzotriazole", "pH",
                           "concentration", "wt %", "wt%")
               if k.lower() in page.lower()]

    has_data = bool(tables) and unit is not None and (n_examples + n_comp) >= 3
    usable = has_data and trusted
    return {
        "patent": patent_id,
        "title": title[:90],
        "assignees": names[:3],
        "trusted": trusted,
        "category": category,
        "matched_org": matched,
        "data_tables": len(tables),
        "examples": n_examples,
        "comparative": n_comp,
        "rate_unit": unit[0] if unit else None,
        "to_nm_per_min": unit[1] if unit else None,
        "composition_terms": comp_kw[:8],
        "usable": usable,
    }


def dump(patent_id: str, max_tables: int = 6, width: int = 1400) -> None:
    """사람이 눈으로 확인할 수 있게 표를 출력한다.

    자동 파싱 결과를 그냥 믿지 않기 위한 단계다 — 특허 표는 구조가 제각각이라
    셀을 잘못 짝지으면 조용히 틀린 데이터셋이 만들어진다.
    """
    page = fetch(patent_id)
    if not page:
        return
    info = assess(patent_id, page)
    print(json.dumps(info, ensure_ascii=False, indent=2))
    print()
    for i, t in enumerate(data_tables(page)[:max_tables]):
        print(f"─── 표 {i+1} " + "─" * 60)
        print(t[:width])
        print()


def search(query: str, limit: int = 20) -> List[str]:
    """Google Patents XHR 검색 → 특허번호 목록."""
    q = urllib.parse.quote(query)
    url = f"https://patents.google.com/xhr/query?url=q%3D{q}&exp="
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        print(f"검색 실패: {e}", file=sys.stderr)
        return []
    ids = []
    try:
        for cluster in data["results"]["cluster"]:
            for item in cluster.get("result", []):
                pid = item.get("patent", {}).get("publication_number")
                if pid:
                    ids.append(pid)
    except (KeyError, TypeError):
        pass
    return ids[:limit]


# 대량 수집용 검색어 — CMP 소재의 주요 축을 덮는다.
# 한 검색어로는 Google Patents가 상위 수십 건만 주므로 축을 나눠 훑는다.
SWEEP_QUERIES = [
    "chemical mechanical polishing slurry removal rate example",
    "CMP slurry ceria abrasive removal rate",
    "CMP slurry colloidal silica polishing composition example",
    "copper CMP slurry benzotriazole hydrogen peroxide removal rate",
    "tungsten CMP slurry oxidizer removal rate",
    "STI CMP slurry oxide nitride selectivity",
    "polishing composition semiconductor wafer removal rate table",
    "CMP polishing pad removal rate uniformity example",
    "barrier CMP slurry tantalum removal rate",
    "polysilicon CMP slurry removal rate",
]

CORPUS = _ROOT / "validation" / "patent_corpus.json"


def sweep(queries: List[str], per_query: int = 50) -> Dict:
    """여러 검색어로 훑어 신뢰 출원인 특허만 코퍼스에 축적한다.

    사용자 지시(2026-09-06): "전체 데이터 반영하고, 벗어나는 수치는 제외시키고. 데이터 쌓고."
    → 재실행하면 기존 코퍼스에 **누적**된다(이미 본 특허는 건너뛴다).
    """
    corpus: Dict[str, Dict] = {}
    if CORPUS.exists():
        corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    seen_before = len(corpus)

    ids: List[str] = []
    for q in queries:
        found = search(q, per_query)
        print(f"  검색: {q[:52]:52s} → {len(found)}건")
        ids.extend(found)
    uniq = [i for i in dict.fromkeys(ids) if i not in corpus]
    print(f"\n신규 {len(uniq)}건 평가 (기보유 {seen_before}건)")

    consecutive_fail = 0
    for n, pid in enumerate(uniq, 1):
        page = fetch(pid)
        if not page:
            consecutive_fail += 1
            # 2026-09-06: 1초 간격으로 돌렸다가 73건 연속 503(IP 차단)을 맞았다.
            # 차단 상태에서 계속 두드리면 차단이 길어질 뿐이다. 접고 나중에 재개한다.
            if consecutive_fail >= 8:
                print(f"\n⚠ {consecutive_fail}건 연속 실패 — Google Patents 차단으로 보인다. "
                      f"중단한다.\n  코퍼스({len(corpus)}건)는 저장됐고 캐시가 남아 있으니 "
                      f"나중에 --sweep을 다시 실행하면 **이어서** 진행된다.\n"
                      f"  차단은 보통 수십 분~수 시간이면 풀린다.")
                break
            continue
        consecutive_fail = 0
        info = assess(pid, page)
        corpus[pid] = info
        if info["usable"]:
            print(f"  ✓ [{n:3d}/{len(uniq)}] {pid:16s} {info['category']:16s} "
                  f"{info['matched_org'][:34]:34s} 실시예{info['examples']}")
        if n % 25 == 0:
            CORPUS.parent.mkdir(parents=True, exist_ok=True)
            CORPUS.write_text(json.dumps(corpus, ensure_ascii=False, indent=1),
                              encoding="utf-8")

    CORPUS.parent.mkdir(parents=True, exist_ok=True)
    CORPUS.write_text(json.dumps(corpus, ensure_ascii=False, indent=1), encoding="utf-8")
    return corpus


def corpus_summary(corpus: Dict) -> None:
    tot = len(corpus)
    trusted = [v for v in corpus.values() if v.get("trusted")]
    usable = [v for v in corpus.values() if v.get("usable")]
    print("\n" + "=" * 78)
    print(f"코퍼스 {tot}건 | 신뢰 출원인 {len(trusted)}건 | 데이터 사용가능 {len(usable)}건")
    print("=" * 78)
    from collections import Counter
    for cat, n in Counter(v.get("category", "?") for v in corpus.values()).most_common():
        print(f"  {cat:18s} {n:4d}건")
    print("\n  사용가능 특허의 출원기관 상위:")
    for org, n in Counter(v["matched_org"] for v in usable).most_common(12):
        print(f"    {org[:46]:46s} {n:3d}건")


def main() -> int:
    ap = argparse.ArgumentParser(description="CMP 특허 실시예 데이터 후보 수집")
    ap.add_argument("--search", help="Google Patents 검색어")
    ap.add_argument("--fetch", nargs="+", help="특허번호들을 평가")
    ap.add_argument("--dump", help="특허 표를 사람이 읽게 출력")
    ap.add_argument("--sweep", action="store_true",
                    help="여러 검색어로 대량 수집 후 코퍼스에 누적")
    ap.add_argument("--status", action="store_true", help="코퍼스 현황")
    ap.add_argument("--per-query", type=int, default=50)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--out", help="평가 결과 JSON 저장 경로")
    a = ap.parse_args()

    if a.status:
        if not CORPUS.exists():
            print("코퍼스 없음. --sweep 으로 수집하라.")
            return 1
        corpus_summary(json.loads(CORPUS.read_text(encoding="utf-8")))
        return 0

    if a.sweep:
        corpus = sweep(SWEEP_QUERIES, a.per_query)
        corpus_summary(corpus)
        return 0

    if a.dump:
        dump(a.dump)
        return 0

    ids: List[str] = []
    if a.search:
        ids = search(a.search, a.limit)
        print(f"검색 '{a.search}' → {len(ids)}건")
    if a.fetch:
        ids.extend(a.fetch)
    if not ids:
        ap.print_help()
        return 1

    rows = []
    for pid in ids:
        page = fetch(pid)
        if not page:
            continue
        info = assess(pid, page)
        rows.append(info)
        flag = "✓" if info["usable"] else "·"
        print(f" {flag} {pid:16s} 표{info['data_tables']:2d} "
              f"실시예{info['examples']:3d}/비교예{info['comparative']:2d} "
              f"단위={info['rate_unit'] or '—':8s} {info['title'][:48]}")

    usable = [r for r in rows if r["usable"]]
    print(f"\n후보 {len(usable)}/{len(rows)}건 (실시예 3개 이상 + 제거율 단위 존재)")
    print("→ `--dump <특허번호>`로 표를 직접 확인한 뒤 데이터셋을 만들어라.")
    print("  자동 추출값을 검증 없이 쓰면 그건 검증이 아니라 소음이다.")
    if a.out:
        Path(a.out).write_text(json.dumps(rows, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        print(f"  저장: {a.out}")
    return 0


if __name__ == "__main__":
    import urllib.parse
    sys.exit(main())
