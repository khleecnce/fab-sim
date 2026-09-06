#!/usr/bin/env python3
"""KIPRIS(한국특허정보원) 공개 API로 국내 CMP 특허를 수집한다.

왜 별도 트랙인가 (2026-09-06):
  Google Patents가 IP 차단(503)되면 거기서 멈춘다. KIPRIS는 별도 인프라라 동시에
  돌릴 수 있고, 무엇보다 **동진쎄미켐·솔브레인·케이씨텍·삼성·하이닉스의 국내 출원**이
  여기 있다. 사용자가 지정한 신뢰 출원인 상당수가 한국 기업이므로 이 경로가 중요하다.

⚠ API 키가 필요하다(무료, https://plus.kipris.or.kr 발급).
  키가 없으면 이 스크립트는 **아무것도 지어내지 않고** 발급 안내만 하고 종료한다.
  키는 ~/.hermes/.env 의 KIPRIS_API_KEY 에서 읽는다.

사용:
    python tools/kipris_mine.py --search "CMP 슬러리"
    python tools/kipris_mine.py --status
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from patent_sources import classify_assignee, find_rate_unit  # noqa: E402

_ROOT = Path(__file__).resolve().parent.parent
CORPUS = _ROOT / "validation" / "kipris_corpus.json"
CACHE = _ROOT / "papers" / "kipris"

API = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/patentInfoSearch"

QUERIES = [
    "CMP 슬러리", "화학기계연마 슬러리", "연마 조성물 반도체",
    "CMP 연마액", "세리아 슬러리", "구리 CMP", "텅스텐 CMP",
    "산화막 연마 조성물", "연마 패드 CMP",
]


def api_key() -> Optional[str]:
    k = os.environ.get("KIPRIS_API_KEY")
    if k:
        return k
    env = Path.home() / ".hermes" / ".env"
    if env.exists():
        m = re.search(r"^KIPRIS_API_KEY=(.+)$", env.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip().strip('"').strip("'")
    return None


def search(key: str, query: str, rows: int = 100) -> List[Dict]:
    params = {
        "word": query, "ServiceKey": key,
        "numOfRows": str(rows), "pageNo": "1",
        "patent": "true", "utility": "false",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            body = r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  ! 검색 실패 ({query}): {e}", file=sys.stderr)
        return []
    time.sleep(1.0)

    out = []
    for item in re.findall(r"<item>(.*?)</item>", body, re.S):
        def g(tag):
            m = re.search(rf"<{tag}>(.*?)</{tag}>", item, re.S)
            return (m.group(1).strip() if m else "")
        out.append({
            "app_no": g("applicationNumber"),
            "title": g("inventionTitle"),
            "applicant": g("applicantName"),
            "date": g("applicationDate"),
            "abstract": g("astrtCont")[:400],
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="KIPRIS 국내 CMP 특허 수집")
    ap.add_argument("--search", help="검색어 (미지정 시 기본 세트 전체)")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()

    if a.status:
        if CORPUS.exists():
            d = json.loads(CORPUS.read_text(encoding="utf-8"))
            trusted = [v for v in d.values() if v.get("trusted")]
            print(f"KIPRIS 코퍼스 {len(d)}건 | 신뢰 출원인 {len(trusted)}건")
            from collections import Counter
            for org, n in Counter(v["matched_org"] for v in trusted).most_common(15):
                print(f"  {org[:44]:44s} {n:3d}건")
        else:
            print("KIPRIS 코퍼스 없음.")
        return 0

    key = api_key()
    if not key:
        print("KIPRIS API 키가 없다. 아무것도 수집하지 않고 종료한다.\n")
        print("발급 (무료):")
        print("  1. https://plus.kipris.or.kr 회원가입")
        print("  2. 오픈API → 특허실용신안 정보검색 서비스 신청")
        print("  3. 발급된 키를 ~/.hermes/.env 에 추가:")
        print("       KIPRIS_API_KEY=발급받은키")
        print("\n키 없이 추정 데이터를 만들지 않는다 — 그건 검증이 아니라 소음이다.")
        return 2

    corpus: Dict[str, Dict] = {}
    if CORPUS.exists():
        corpus = json.loads(CORPUS.read_text(encoding="utf-8"))

    queries = [a.search] if a.search else QUERIES
    for q in queries:
        hits = search(key, q)
        print(f"  '{q}' → {len(hits)}건")
        for h in hits:
            if not h["app_no"] or h["app_no"] in corpus:
                continue
            trusted, cat, org = classify_assignee([h["applicant"]])
            h.update({"trusted": trusted, "category": cat, "matched_org": org})
            corpus[h["app_no"]] = h

    CORPUS.parent.mkdir(parents=True, exist_ok=True)
    CORPUS.write_text(json.dumps(corpus, ensure_ascii=False, indent=1), encoding="utf-8")
    trusted = [v for v in corpus.values() if v.get("trusted")]
    print(f"\n코퍼스 {len(corpus)}건 | 신뢰 출원인 {len(trusted)}건 → {CORPUS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
