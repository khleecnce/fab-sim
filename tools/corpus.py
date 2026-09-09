#!/usr/bin/env python3
"""CMP 코퍼스 DB — 특허·논문·오픈데이터를 전부 한 곳에 모아 순차 학습의 원천으로 쓴다.

사용자 지시 (2026-09-09):
  "특허, 논문, 오픈 소스 등 가능한 데이터는 모든걸 수집해서 DB화 해줘. CMP 관련이면
   모든 걸 다 수집해. 그리고 그 데이터를 순차적으로 학습해"

규모 실측 (2026-09-09): OpenAlex CMP 문헌 19,235건(OA 11,956), Europe PMC 전문 OA 989건,
특허는 Google Patents sweep(기존 tools/patent_mine.py). 건당 ~1초 → 수 시간짜리
백그라운드 작업이지 "불가능"이 아니다.

DB 구조 (SQLite, data/corpus/corpus.sqlite — 본문은 커밋 안 함, 메타·상태만 커밋 가능)
  documents   — id, kind(patent|paper|dataset), title, ids(doi/patent/pmcid), year, source,
                oa_url, fulltext_path, status, relevance, harvested_ts
  extractions — doc_id, kind(mrr_table|param|claim), payload_json, status(auto|verified|rejected)
  queue       — 순차 학습 큐: doc_id, priority, stage(fetch|extract|learn|merge), attempts, note

상태 흐름 (순차 학습)
  discovered → fetched(전문 확보) → extracted(표·수치 자동 추출, status=auto)
    → verified(사람/QA 대조 통과) → merged(validation/datasets 또는 knowledge/params 반영)
  각 단계는 멱등이며 크론이 `corpus.py next --stage <s>`로 한 건씩 받아간다.

관련성 점수 relevance (0~1): 제목·초록의 CMP 키워드 밀도 + 슬러리/패드/디스크 키워드.
  낮은 것도 버리지 않는다(사용자: "CMP 관련이면 모든 걸") — 우선순위만 낮춘다.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "data" / "corpus"
DB = DB_DIR / "corpus.sqlite"
FULLTEXT = DB_DIR / "fulltext"
UA = {"User-Agent": "fab-sim corpus harvester (mailto:khleecnce@gmail.com)"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
  id            TEXT PRIMARY KEY,
  kind          TEXT NOT NULL,
  title         TEXT,
  doi           TEXT, patent TEXT, pmcid TEXT, openalex TEXT,
  year          INTEGER,
  source        TEXT,
  oa_url        TEXT,
  fulltext_path TEXT,
  abstract      TEXT,
  relevance     REAL DEFAULT 0,
  status        TEXT DEFAULT 'discovered',
  harvested_ts  REAL,
  updated_ts    REAL,
  meta_json     TEXT
);
CREATE INDEX IF NOT EXISTS idx_doc_status ON documents(status, relevance DESC);
CREATE TABLE IF NOT EXISTS extractions (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id     TEXT NOT NULL,
  kind       TEXT NOT NULL,
  payload    TEXT NOT NULL,
  status     TEXT DEFAULT 'auto',
  note       TEXT,
  ts         REAL
);
CREATE TABLE IF NOT EXISTS queue (
  doc_id    TEXT PRIMARY KEY,
  stage     TEXT NOT NULL,
  priority  REAL DEFAULT 0,
  attempts  INTEGER DEFAULT 0,
  note      TEXT,
  ts        REAL
);
"""

CMP_TERMS = ["chemical mechanical polishing", "chemical mechanical planarization", "cmp slurry",
             "cmp pad", "polishing slurry", "planarization", "removal rate", "abrasive", "ceria",
             "colloidal silica", "conditioner", "dishing", "erosion", "wiwnu", "pad conditioning",
             "preston", "tungsten cmp", "copper cmp", "oxide cmp", "sti cmp", "post-cmp cleaning"]


def _conn() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    FULLTEXT.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.executescript(_SCHEMA)
    return c


def _get(url: str, timeout: int = 30, raw: bool = False, retries: int = 5):
    """429/5xx는 지수 백오프로 재시도 — 수확기가 한 번의 rate-limit에 죽으면 나머지를 다 잃는다."""
    import urllib.error, urllib.request as _ur
    delay = 2.0
    for i in range(retries):
        try:
            r = _ur.urlopen(_ur.Request(url, headers=UA), timeout=timeout).read()
            return r if raw else json.loads(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < retries - 1:
                time.sleep(delay); delay = min(delay * 2, 60)
                continue
            raise
    raise RuntimeError("unreachable")


def relevance(title: str, abstract: str = "") -> float:
    t = f"{title or ''} {abstract or ''}".lower()
    hits = sum(1 for k in CMP_TERMS if k in t)
    core = any(k in t for k in ("chemical mechanical polishing", "chemical mechanical planarization", "cmp slurry", "cmp pad"))
    return min(1.0, (0.5 if core else 0.0) + 0.08 * hits)


def upsert(c: sqlite3.Connection, doc: Dict[str, Any]) -> bool:
    """새 문서면 True. 이미 있으면 메타만 보강."""
    now = time.time()
    cur = c.execute("SELECT id, status FROM documents WHERE id=?", (doc["id"],)).fetchone()
    if cur:
        c.execute("UPDATE documents SET title=COALESCE(?,title), doi=COALESCE(?,doi), pmcid=COALESCE(?,pmcid), "
                  "oa_url=COALESCE(?,oa_url), abstract=COALESCE(?,abstract), updated_ts=? WHERE id=?",
                  (doc.get("title"), doc.get("doi"), doc.get("pmcid"), doc.get("oa_url"), doc.get("abstract"), now, doc["id"]))
        return False
    c.execute("INSERT INTO documents (id,kind,title,doi,patent,pmcid,openalex,year,source,oa_url,abstract,relevance,status,harvested_ts,updated_ts,meta_json) "
              "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (doc["id"], doc["kind"], doc.get("title"), doc.get("doi"), doc.get("patent"), doc.get("pmcid"),
               doc.get("openalex"), doc.get("year"), doc.get("source"), doc.get("oa_url"), doc.get("abstract"),
               relevance(doc.get("title", ""), doc.get("abstract", "")), "discovered", now, now,
               json.dumps(doc.get("meta", {}), ensure_ascii=False)))
    c.execute("INSERT OR IGNORE INTO queue (doc_id, stage, priority, ts) VALUES (?,?,?,?)",
              (doc["id"], "fetch", relevance(doc.get("title", ""), doc.get("abstract", "")), now))
    return True


# ───────────────────────────────────────────── 수확기
def harvest_openalex(c, query: str, max_pages: int = 50, oa_only: bool = True) -> int:
    """OpenAlex — 문헌 메타 전수. 커서 페이징, 페이지당 200."""
    n = 0
    cursor = "*"
    flt = "open_access.is_oa:true" if oa_only else None
    for _ in range(max_pages):
        u = f"https://api.openalex.org/works?search={urllib.parse.quote(query)}&per-page=200&cursor={cursor}"
        if flt:
            u += f"&filter={flt}"
        d = _get(u)
        for w in d.get("results", []):
            doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
            oa = (w.get("open_access") or {}).get("oa_url")
            pmcid = None
            ids = w.get("ids") or {}
            if ids.get("pmcid"):
                pmcid = ids["pmcid"].split("/")[-1]
            abstract = None
            inv = w.get("abstract_inverted_index")
            if inv:
                pos = {}
                for word, idxs in inv.items():
                    for i in idxs:
                        pos[i] = word
                abstract = " ".join(pos[i] for i in sorted(pos))[:3000]
            did = f"doi:{doi}" if doi else f"openalex:{w['id'].split('/')[-1]}"
            n += upsert(c, {"id": did, "kind": "paper", "title": w.get("title"), "doi": doi, "pmcid": pmcid,
                            "openalex": w["id"], "year": w.get("publication_year"), "source": "openalex",
                            "oa_url": oa, "abstract": abstract,
                            "meta": {"cited_by": w.get("cited_by_count"), "type": w.get("type")}})
        c.commit()
        cursor = (d.get("meta") or {}).get("next_cursor")
        if not cursor or not d.get("results"):
            break
        time.sleep(1.0)
    return n


def harvest_europepmc(c, query: str, max_pages: int = 20) -> int:
    """Europe PMC — 전문 OA만. XML 전문 URL을 바로 준다."""
    n = 0
    cursor = "*"
    for _ in range(max_pages):
        u = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
             + urllib.parse.quote(f"({query}) AND OPEN_ACCESS:y") + f"&format=json&pageSize=100&cursorMark={cursor}")
        d = _get(u)
        for r in d.get("resultList", {}).get("result", []):
            pmcid = r.get("pmcid")
            doi = r.get("doi")
            did = f"doi:{doi}" if doi else (f"pmc:{pmcid}" if pmcid else None)
            if not did:
                continue
            n += upsert(c, {"id": did, "kind": "paper", "title": r.get("title"), "doi": doi, "pmcid": pmcid,
                            "year": int(r["pubYear"]) if r.get("pubYear") else None, "source": "europepmc",
                            "oa_url": f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML" if pmcid else None,
                            "abstract": (r.get("abstractText") or "")[:3000]})
        c.commit()
        nxt = d.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(0.2)
    return n


def harvest_patents_from_corpus(c) -> int:
    """기존 tools/patent_mine.py 코퍼스(validation/patent_corpus.json)를 흡수."""
    p = ROOT / "validation" / "patent_corpus.json"
    if not p.exists():
        return 0
    d = json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for k, v in d.items():
        n += upsert(c, {"id": f"patent:{k}", "kind": "patent", "patent": k, "title": v.get("title"),
                        "source": "patent_mine", "oa_url": f"https://patents.google.com/patent/{k}/en",
                        "meta": {kk: vv for kk, vv in v.items() if kk != "title"}})
    c.commit()
    return n


def harvest_google_patents(c, query: str, pages: int = 5) -> int:
    """Google Patents XHR 검색(비공식) — 결과 번호만 수집. 본문은 fetch 단계."""
    n = 0
    for pg in range(pages):
        u = f"https://patents.google.com/xhr/query?url=q%3D{urllib.parse.quote(query)}%26page%3D{pg}&exp="
        try:
            d = _get(u)
        except Exception:
            break
        res = (d.get("results") or {}).get("cluster") or []
        got = 0
        for cl in res:
            for r in cl.get("result", []):
                pt = r.get("patent") or {}
                num = pt.get("publication_number")
                if not num:
                    continue
                got += 1
                n += upsert(c, {"id": f"patent:{num}", "kind": "patent", "patent": num, "title": pt.get("title"),
                                "year": int(pt["publication_date"][:4]) if pt.get("publication_date") else None,
                                "source": "google_patents", "oa_url": f"https://patents.google.com/patent/{num}/en",
                                "abstract": pt.get("snippet"), "meta": {"assignee": pt.get("assignee"), "query": query}})
        c.commit()
        if not got:
            break
        time.sleep(1.0)
    return n


def harvest_local_papers(c) -> int:
    """papers/ 에 이미 있는 전문을 흡수 (INDEX.json + 파일명)."""
    n = 0
    for f in (ROOT / "papers").glob("*"):
        if f.suffix.lower() not in (".xml", ".txt", ".pdf"):
            continue
        stem = f.stem
        m = re.match(r"(?i)^(PMC\d+)", stem)
        pm = re.match(r"(?i)^((?:US|TW|KR|JP|EP|WO)\d{4,}[A-Z]?\d?)", stem)
        if m:
            did, kind = f"pmc:{m.group(1).upper()}", "paper"
        elif pm:
            did, kind = f"patent:{pm.group(1).upper()}", "patent"
        else:
            did, kind = f"local:{hashlib.sha1(stem.encode()).hexdigest()[:12]}", "paper"
        new = upsert(c, {"id": did, "kind": kind, "title": stem, "source": "local_papers", "pmcid": m.group(1).upper() if m else None,
                         "patent": pm.group(1).upper() if pm else None})
        c.execute("UPDATE documents SET fulltext_path=?, status=CASE WHEN status='discovered' THEN 'fetched' ELSE status END WHERE id=?",
                  (str(f.relative_to(ROOT)), did))
        c.execute("UPDATE queue SET stage='extract' WHERE doc_id=? AND stage='fetch'", (did,))
        n += new
    c.commit()
    return n


# ───────────────────────────────────────────── fetch / extract
def fetch_one(c, doc_id: str) -> Optional[str]:
    """전문 확보 → fulltext/<id>.txt|xml. 실패 시 None (queue.attempts++)."""
    d = c.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not d:
        return None
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", doc_id)
    text, ext = None, "txt"
    try:
        if d["kind"] == "patent" and d["patent"]:
            html = _get(f"https://patents.google.com/patent/{d['patent']}/en", raw=True).decode("utf-8", "ignore")
            t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
            text = re.sub(r"<[^>]+>", " ", t)
        elif d["pmcid"]:
            xml = _get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{d['pmcid']}/fullTextXML", raw=True).decode("utf-8", "ignore")
            if len(xml) > 2000:
                text, ext = xml, "xml"
        if text is None and d["oa_url"] and d["oa_url"].lower().endswith(".pdf") is False and "europepmc" not in (d["oa_url"] or ""):
            # OA 랜딩/HTML — 시도만
            raw = _get(d["oa_url"], raw=True)
            if raw[:4] == b"%PDF":
                (FULLTEXT / f"{safe}.pdf").write_bytes(raw)
                text, ext = None, "pdf"
                path = FULLTEXT / f"{safe}.pdf"
                c.execute("UPDATE documents SET fulltext_path=?, status='fetched', updated_ts=? WHERE id=?",
                          (str(path.relative_to(ROOT)), time.time(), doc_id))
                c.execute("UPDATE queue SET stage='extract', ts=? WHERE doc_id=?", (time.time(), doc_id))
                c.commit()
                return str(path)
            t = raw.decode("utf-8", "ignore")
            t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
            t = re.sub(r"<[^>]+>", " ", t)
            if len(t) > 5000:
                text = t
    except Exception as e:
        c.execute("UPDATE queue SET attempts=attempts+1, note=?, ts=? WHERE doc_id=?", (f"fetch: {type(e).__name__}", time.time(), doc_id))
        c.commit()
        return None
    if not text or len(text) < 2000:
        c.execute("UPDATE queue SET attempts=attempts+1, note='fetch: no fulltext', ts=? WHERE doc_id=?", (time.time(), doc_id))
        c.commit()
        return None
    path = FULLTEXT / f"{safe}.{ext}"
    path.write_text(text, encoding="utf-8")
    c.execute("UPDATE documents SET fulltext_path=?, status='fetched', updated_ts=? WHERE id=?",
              (str(path.relative_to(ROOT)), time.time(), doc_id))
    c.execute("UPDATE queue SET stage='extract', ts=? WHERE doc_id=?", (time.time(), doc_id))
    c.commit()
    return str(path)


_RATE_RX = re.compile(r"(?i)(removal\s*rate|polish(?:ing)?\s*rate|MRR|RR)\b[^.\n]{0,120}?(\d{2,5}(?:[.,]\d+)?)\s*(Å/min|A/min|nm/min|angstrom(?:s)?/min|μm/min|um/min)")
_TABLE_RX = re.compile(r"(?i)(TABLE|Table)\s+(\d+[A-Z]?)")


def extract_one(c, doc_id: str) -> Dict[str, Any]:
    """전문에서 MRR 수치·표 위치·조성 키워드를 자동 추출(status=auto). 사람이 verify."""
    d = c.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not d or not d["fulltext_path"]:
        return {}
    p = ROOT / d["fulltext_path"]
    if p.suffix == ".pdf":
        c.execute("UPDATE queue SET stage='learn', note='pdf: OCR 필요', ts=? WHERE doc_id=?", (time.time(), doc_id))
        c.commit()
        return {"note": "pdf"}
    t = p.read_text(encoding="utf-8", errors="ignore")
    rates = [(m.group(2), m.group(3)) for m in _RATE_RX.finditer(t)][:200]
    tables = sorted(set(m.group(2) for m in _TABLE_RX.finditer(t)))
    comp = {k: len(re.findall(rf"(?i)\b{k}\b", t)) for k in
            ["silica", "ceria", "alumina", "H2O2", "hydrogen peroxide", "BTA", "benzotriazole", "glycine", "KOH", "pH",
             "wt%", "ppm", "psi", "rpm", "ml/min", "mL/min", "Shore", "groove", "conditioner", "diamond"]}
    comp = {k: v for k, v in comp.items() if v}
    payload = {"n_rate_mentions": len(rates), "rate_samples": rates[:30], "tables": tables[:40],
               "composition_terms": comp, "len": len(t)}
    score = min(1.0, 0.1 * len(rates) + 0.05 * len(tables) + 0.02 * len(comp))
    c.execute("INSERT INTO extractions (doc_id, kind, payload, status, ts) VALUES (?,?,?,?,?)",
              (doc_id, "scan", json.dumps(payload, ensure_ascii=False), "auto", time.time()))
    c.execute("UPDATE documents SET status='extracted', relevance=MAX(relevance, ?), updated_ts=? WHERE id=?",
              (score, time.time(), doc_id))
    c.execute("UPDATE queue SET stage='learn', priority=?, ts=? WHERE doc_id=?", (score, time.time(), doc_id))
    c.commit()
    return payload


# ───────────────────────────────────────────── 큐 / 상태
def next_item(c, stage: str, skip_attempts: int = 3) -> Optional[Dict]:
    r = c.execute("SELECT q.*, d.title, d.kind, d.relevance FROM queue q JOIN documents d ON d.id=q.doc_id "
                  "WHERE q.stage=? AND q.attempts<? ORDER BY q.priority DESC, d.relevance DESC, q.ts ASC LIMIT 1",
                  (stage, skip_attempts)).fetchone()
    return dict(r) if r else None


def mark(c, doc_id: str, stage: str, note: str = "") -> None:
    c.execute("UPDATE queue SET stage=?, note=?, ts=? WHERE doc_id=?", (stage, note, time.time(), doc_id))
    st = {"learn": "extracted", "merge": "verified", "done": "merged"}.get(stage)
    if st:
        c.execute("UPDATE documents SET status=?, updated_ts=? WHERE id=?", (st, time.time(), doc_id))
    c.commit()


def status(c) -> Dict[str, Any]:
    out = {"documents": {}, "queue": {}, "extractions": 0}
    for r in c.execute("SELECT kind, status, COUNT(*) n FROM documents GROUP BY kind, status"):
        out["documents"].setdefault(r["kind"], {})[r["status"]] = r["n"]
    for r in c.execute("SELECT stage, COUNT(*) n FROM queue GROUP BY stage"):
        out["queue"][r["stage"]] = r["n"]
    out["extractions"] = c.execute("SELECT COUNT(*) FROM extractions").fetchone()[0]
    out["total"] = c.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    out["with_fulltext"] = c.execute("SELECT COUNT(*) FROM documents WHERE fulltext_path IS NOT NULL").fetchone()[0]
    return out


# ───────────────────────────────────────────── CLI
QUERIES_PAPER = [
    '"chemical mechanical polishing"', '"chemical mechanical planarization"', '"CMP slurry"',
    '"CMP pad" conditioning', 'ceria slurry oxide polishing', 'colloidal silica slurry removal rate',
    'copper CMP benzotriazole', 'tungsten CMP oxidizer', 'shallow trench isolation CMP selectivity',
    'post-CMP cleaning PVA brush', 'CMP dishing erosion pattern density', 'pad asperity contact CMP model',
]
QUERIES_PATENT = [
    "chemical mechanical polishing slurry removal rate examples", "CMP polishing composition ceria removal rate",
    "CMP slurry colloidal silica oxide removal rate table", "copper CMP slurry benzotriazole example removal rate",
    "tungsten CMP slurry hydrogen peroxide removal rate example", "polishing pad groove hardness removal rate example",
    "pad conditioner diamond disk cut rate example", "STI CMP ceria selectivity nitride removal rate example",
    "post CMP cleaning composition example defect", "CMP slurry dispersant defect example removal rate",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="CMP 코퍼스 DB")
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("harvest", help="메타 수확 (openalex|europepmc|patents|local|all)")
    h.add_argument("source", nargs="?", default="all"); h.add_argument("--pages", type=int, default=10)
    h.add_argument("--query", help="단일 검색어")
    f = sub.add_parser("fetch", help="전문 확보"); f.add_argument("-n", type=int, default=20)
    e = sub.add_parser("extract", help="자동 추출"); e.add_argument("-n", type=int, default=50)
    nx = sub.add_parser("next", help="다음 학습 항목 1건"); nx.add_argument("--stage", default="learn")
    mk = sub.add_parser("mark"); mk.add_argument("doc_id"); mk.add_argument("stage"); mk.add_argument("--note", default="")
    sub.add_parser("status")
    sh = sub.add_parser("show"); sh.add_argument("doc_id")
    a = ap.parse_args()
    c = _conn()

    if a.cmd == "harvest":
        tot = 0
        if a.source in ("local", "all"):
            n = harvest_local_papers(c); print(f"local papers/: +{n}"); tot += n
        if a.source in ("patents", "all"):
            n = harvest_patents_from_corpus(c); print(f"patent_corpus.json: +{n}"); tot += n
            for q in ([a.query] if a.query else QUERIES_PATENT):
                n = harvest_google_patents(c, q, pages=a.pages); print(f"google patents '{q[:40]}': +{n}"); tot += n
        if a.source in ("europepmc", "all"):
            for q in ([a.query] if a.query else QUERIES_PAPER[:3]):
                n = harvest_europepmc(c, q, max_pages=a.pages); print(f"europepmc '{q[:40]}': +{n}"); tot += n
        if a.source in ("openalex", "all"):
            for q in ([a.query] if a.query else QUERIES_PAPER):
                n = harvest_openalex(c, q, max_pages=a.pages); print(f"openalex '{q[:40]}': +{n}"); tot += n
        print(f"신규 {tot}건. 현황: {json.dumps(status(c), ensure_ascii=False)}")
    elif a.cmd == "fetch":
        ok = 0
        for _ in range(a.n):
            it = next_item(c, "fetch")
            if not it:
                break
            r = fetch_one(c, it["doc_id"])
            ok += bool(r)
            print(("✓ " if r else "✗ ") + it["doc_id"], (it.get("title") or "")[:70])
            time.sleep(0.5)
        print(f"fetched {ok}/{a.n}")
    elif a.cmd == "extract":
        for _ in range(a.n):
            it = next_item(c, "extract")
            if not it:
                break
            p = extract_one(c, it["doc_id"])
            print(f"{it['doc_id']:40} rates={p.get('n_rate_mentions', '-')} tables={len(p.get('tables', []))}")
    elif a.cmd == "next":
        it = next_item(c, a.stage)
        if it:
            ex = c.execute("SELECT payload FROM extractions WHERE doc_id=? ORDER BY id DESC LIMIT 1", (it["doc_id"],)).fetchone()
            it["extraction"] = json.loads(ex["payload"]) if ex else None
            d = c.execute("SELECT fulltext_path, oa_url, doi, patent FROM documents WHERE id=?", (it["doc_id"],)).fetchone()
            it.update(dict(d))
        print(json.dumps(it or {"none": True}, ensure_ascii=False, indent=2))
    elif a.cmd == "mark":
        mark(c, a.doc_id, a.stage, a.note); print("ok")
    elif a.cmd == "status":
        print(json.dumps(status(c), ensure_ascii=False, indent=2))
    elif a.cmd == "show":
        d = c.execute("SELECT * FROM documents WHERE id=?", (a.doc_id,)).fetchone()
        print(json.dumps(dict(d) if d else {}, ensure_ascii=False, indent=2))
        for ex in c.execute("SELECT kind, status, payload FROM extractions WHERE doc_id=?", (a.doc_id,)):
            print(ex["kind"], ex["status"], ex["payload"][:800])
    return 0


if __name__ == "__main__":
    sys.exit(main())
