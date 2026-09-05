#!/usr/bin/env python3
"""무료 전문(Open Access) 자동 수집 — FabSim 지식노트의 '초록만 확인'을 승격시킨다.

배경 (2026-09-05 사용자 지시: "무료는 전체 적용해"):
  노트 21개 중 11개가 유료 저널(IEEE/Springer/Elsevier/Wiley)을 '초록만 확인,
  본문 미검증'으로 인용 중이다. 그런데 유료 저널 논문의 상당수는 **합법적으로**
  무료 전문이 존재한다 — 저자 최종본(green OA), 기관 리포지토리, arXiv 프리프린트,
  PMC. Unpaywall/OpenAlex/Semantic Scholar가 그걸 찾아 준다.

  이게 중요한 이유는 학술 예의가 아니라 **수치 신뢰성**이다. 이미 FabSim에서
  "JJMIE(2026) 속도 비균일도 보고값이 자기 수식과 4배 불일치" 사례가 나왔다.
  2차 인용만으로는 리뷰서가 계수를 잘못 옮긴 건지 정의가 다른 건지 구분이 안 된다.

쓰는 API (전부 무료·공개·robots 허용):
  - Crossref      : 제목 → DOI 해석
  - Unpaywall     : DOI → 합법 무료 전문 위치 (이메일 파라미터 필요)
  - OpenAlex      : DOI/제목 → OA 위치 + 메타데이터 (키 불필요)
  - Semantic Scholar : 제목 → openAccessPdf
  - arXiv         : 제목 검색 → 프리프린트 PDF

⚠ 유료 벽을 우회하는 경로(미러 사이트 등)는 쓰지 않는다. 합법 OA만 모은다.

사용:
  python3 find_open_access.py --scan              # 노트에서 인용 추출 → OA 조회
  python3 find_open_access.py --scan --download   # 찾은 것 papers/ 에 내려받기
  python3 find_open_access.py --title "Luo Dornfeld material removal CMP"
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

ROOT = Path.home() / 'fab-sim'
KNOWLEDGE = ROOT / 'knowledge'
PAPERS = ROOT / 'papers'
INDEX = PAPERS / 'INDEX.json'

# Unpaywall은 이메일 식별을 요구한다(인증이 아니라 남용 방지용 연락처).
MAILTO = os.environ.get('OA_MAILTO', 'khleecnce@gmail.com')
UA = f'FabSim-OA-Collector/1.0 (mailto:{MAILTO})'

PAYWALLED = re.compile(
    r'ieee|springer|elsevier|wiley|sciencedirect|cirp|tribology|'
    r'j\.?\s*electron\.?\s*mater|precis\.?\s*eng', re.I)


def get(url, timeout=25, as_json=True):
    req = urllib.request.Request(url, headers={'User-Agent': UA,
                                               'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return json.loads(raw.decode('utf-8', 'replace')) if as_json else raw


# ---------------------------------------------------------------- 조회 ----

def crossref_doi(title):
    """제목 → DOI. 가장 유사한 1건만."""
    q = urllib.parse.quote(title[:200])
    try:
        d = get(f'https://api.crossref.org/works?query.bibliographic={q}'
                f'&rows=3&mailto={MAILTO}')
        items = d.get('message', {}).get('items', [])
        for it in items:
            t = (it.get('title') or [''])[0]
            if not t:
                continue
            # 제목 토큰이 절반 이상 겹치면 같은 논문으로 본다
            a = set(re.findall(r'[a-z]{4,}', title.lower()))
            b = set(re.findall(r'[a-z]{4,}', t.lower()))
            if a and len(a & b) / len(a) >= 0.45:
                return it.get('DOI'), t
    except Exception:
        pass
    return None, None


def unpaywall(doi):
    try:
        d = get(f'https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}'
                f'?email={MAILTO}')
        if d.get('is_oa'):
            loc = d.get('best_oa_location') or {}
            return {'src': 'Unpaywall', 'pdf': loc.get('url_for_pdf'),
                    'landing': loc.get('url'), 'ver': loc.get('version'),
                    'host': loc.get('host_type'), 'license': loc.get('license')}
    except Exception:
        pass
    return None


def openalex(doi=None, title=None):
    try:
        if doi:
            d = get(f'https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}'
                    f'?mailto={MAILTO}')
        else:
            q = urllib.parse.quote(title[:150])
            r = get(f'https://api.openalex.org/works?search={q}&per-page=1'
                    f'&mailto={MAILTO}')
            hits = r.get('results') or []
            if not hits:
                return None
            d = hits[0]
        oa = d.get('best_oa_location') or d.get('primary_location') or {}
        if oa.get('pdf_url') or (d.get('open_access') or {}).get('is_oa'):
            return {'src': 'OpenAlex', 'pdf': oa.get('pdf_url'),
                    'landing': oa.get('landing_page_url'),
                    'ver': oa.get('version'), 'license': oa.get('license')}
    except Exception:
        pass
    return None


def semantic_scholar(title):
    try:
        q = urllib.parse.quote(title[:150])
        d = get('https://api.semanticscholar.org/graph/v1/paper/search'
                f'?query={q}&limit=1&fields=title,openAccessPdf,externalIds,year')
        hits = d.get('data') or []
        if hits and hits[0].get('openAccessPdf'):
            p = hits[0]['openAccessPdf']
            return {'src': 'SemanticScholar', 'pdf': p.get('url'),
                    'landing': p.get('url'), 'ver': 'unknown'}
    except Exception:
        pass
    return None


def arxiv(title):
    try:
        q = urllib.parse.quote(f'all:{title[:120]}')
        raw = get(f'http://export.arxiv.org/api/query?search_query={q}'
                  f'&max_results=1', as_json=False).decode('utf-8', 'replace')
        m = re.search(r'<id>(http://arxiv\.org/abs/[^<]+)</id>', raw)
        t = re.search(r'<title>([^<]+)</title>\s*<summary', raw, re.S)
        if m:
            a = set(re.findall(r'[a-z]{4,}', title.lower()))
            b = set(re.findall(r'[a-z]{4,}', (t.group(1) if t else '').lower()))
            if a and len(a & b) / len(a) >= 0.45:
                abs_url = m.group(1)
                return {'src': 'arXiv', 'pdf': abs_url.replace('/abs/', '/pdf/'),
                        'landing': abs_url, 'ver': 'submittedVersion'}
    except Exception:
        pass
    return None


def title_overlap(a, b):
    """두 제목의 어휘 겹침 비율(0~1). 잘못된 매칭을 거르는 최후 방어선."""
    wa = set(re.findall(r'[a-z]{4,}', (a or '').lower()))
    wb = set(re.findall(r'[a-z]{4,}', (b or '').lower()))
    return len(wa & wb) / len(wa) if wa else 0.0


def find_oa(title, doi=None):
    """합법 무료 전문을 찾는다. 우선순위: 출판본 > 저자최종본 > 프리프린트.

    ⚠ DOI가 해석되지 않으면(=Crossref가 못 찾으면) 제목 검색만으로 받은 결과는
    믿지 않는다. 실측에서 저널명이 제목으로 들어가 전혀 다른 논문(리그닌
    메타크릴레이트)이 '확보'로 잡혔다. 잘못된 원문은 없느니만 못하다.
    """
    resolved = None
    if not doi:
        doi, resolved = crossref_doi(title)
    for fn in (lambda: unpaywall(doi) if doi else None,
               lambda: openalex(doi, title),
               lambda: semantic_scholar(title),
               lambda: arxiv(title)):
        r = fn()
        if r and (r.get('pdf') or r.get('landing')):
            r['doi'] = doi
            r['matched_title'] = resolved
            # DOI 없이 제목 검색만으로 나온 건 신뢰도가 낮다 — 표시해 둔다
            r['confidence'] = 'doi' if doi else 'title-only'
            return r
    return {'doi': doi, 'matched_title': resolved} if doi else None


# ------------------------------------------------------- 노트에서 추출 ----

CITE = re.compile(
    r'[""]([^""]{25,180})[""]|'          # 따옴표로 감싼 논문 제목
    r'\*([A-Z][^*]{15,120})\*'            # 이탤릭 저널/제목
)

# 저널명·학회명 패턴 — 이게 제목으로 잡히면 엉뚱한 논문을 가져온다.
JOURNAL_ONLY = re.compile(
    r'^(?:[A-Z][a-z]*\.?\s*){0,3}'
    r'(?:J\.|Journal|Trans\.|Transactions|Proc\.|Proceedings|Annals|Int\.|'
    r'Conf\.|Conference|Symp\.|Letters|Review|Manuf\.|Eng\.|Mater\.|Technol\.)'
    r'[\s.\-A-Za-z]*$')


def is_paper_title(t):
    """논문 '제목'인가, 저널명·인용 단편인가."""
    t = t.strip()
    if len(t.split()) < 5:
        return False
    if JOURNAL_ONLY.match(t):
        return False
    # 약어 점(.)이 많고 소문자 단어가 적으면 저널명이다
    if t.count('.') >= 2 and len(re.findall(r'\b[a-z]{4,}\b', t)) < 4:
        return False
    # 본문에서 따온 문장 조각(말줄임표 포함)은 제목이 아니다
    if '...' in t or '…' in t:
        return False
    return True


def extract_citations():
    """노트에서 유료 저널로 보이는 인용을 뽑는다.

    ⚠ 저널명만 잡으면 안 된다. 실측(2026-09-05)에서 "Int. J. Precis. Eng. Manuf."
    같은 저널명이 제목으로 잡혀 **전혀 다른 논문**이 매칭됐다(리그닌 메타크릴레이트,
    지속가능성 리뷰 등). 논문 제목으로 볼 수 있는 것만 남긴다.
    """
    out = []
    for p in sorted(KNOWLEDGE.rglob('*.md')):
        if p.name == 'INDEX.md':
            continue
        text = p.read_text(encoding='utf-8')
        for line in text.splitlines():
            if not PAYWALLED.search(line):
                continue
            for m in CITE.finditer(line):
                t = (m.group(1) or m.group(2) or '').strip()
                if not is_paper_title(t):
                    continue
                out.append({'note': str(p.relative_to(KNOWLEDGE)),
                            'title': t, 'line': line.strip()[:160]})
    # 중복 제거
    seen, uniq = set(), []
    for c in out:
        k = re.sub(r'[^a-z]', '', c['title'].lower())[:50]
        if k in seen:
            continue
        seen.add(k)
        uniq.append(c)
    return uniq


def download(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if not data[:5].startswith(b'%PDF'):
        return False, 'PDF가 아님(로그인 페이지일 수 있음)'
    dest.write_bytes(data)
    return True, f'{len(data)//1024}KB'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scan', action='store_true', help='노트의 유료 인용 전체 조회')
    ap.add_argument('--title', help='단일 제목 조회')
    ap.add_argument('--download', action='store_true')
    ap.add_argument('--limit', type=int, default=60)
    a = ap.parse_args()

    PAPERS.mkdir(exist_ok=True)
    idx = json.loads(INDEX.read_text()) if INDEX.exists() else {}

    if a.title:
        r = find_oa(a.title)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0

    if not a.scan:
        ap.print_help()
        return 1

    cites = extract_citations()[:a.limit]
    print(f'노트에서 유료 저널 인용 {len(cites)}건 추출\n')
    found = 0
    for i, c in enumerate(cites, 1):
        print(f"[{i}/{len(cites)}] {c['title'][:78]}")
        r = find_oa(c['title'])
        time.sleep(0.5)
        if not r or not (r.get('pdf') or r.get('landing')):
            print(f"     ✗ 무료 전문 없음 (doi={r.get('doi') if r else None})")
            continue
        found += 1
        print(f"     ✓ {r['src']} [{r.get('ver')}] {(r.get('pdf') or r['landing'])[:88]}")
        key = re.sub(r'[^a-z0-9]+', '-', c['title'].lower())[:60]
        idx[key] = {**r, 'title': c['title'], 'note': c['note']}
        if a.download and r.get('pdf'):
            dest = PAPERS / f'{key}.pdf'
            if dest.exists():
                print('       (이미 있음)')
            else:
                try:
                    ok, msg = download(r['pdf'], dest)
                    print(f"       {'⬇ ' + msg if ok else '⚠ ' + msg}")
                except Exception as e:
                    print(f'       ⚠ 실패: {type(e).__name__} {str(e)[:60]}')

    INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=1))
    print(f'\n무료 전문 확보 {found}/{len(cites)}건 · 색인: {INDEX}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
