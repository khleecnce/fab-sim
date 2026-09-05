#!/usr/bin/env python3
"""지식노트 품질 게이트 — 병렬 학습에서 졸작이 섞이는 것을 막는다.

배경(2026-09-04 사용자 지시: "품질중심이지"):
  FabSim 학습을 병렬로 돌려 기간을 단축하되, 속도 때문에 노트가 얕아지면
  의미가 없다. 사람 눈으로 5개를 매번 검수할 수 없으므로 코드가 자른다.

기준은 기존 합격 노트(hertz-gw-contact-mechanics.md,
preston-luo-dornfeld-mrr.md)에서 역산했다. 그 둘이 통과해야 기준이 정당하다.

사용:
  python check_knowledge.py knowledge/materials/새노트.md
  python check_knowledge.py --all          # 전체 회귀 검사
종료코드 0=통과, 1=미달(위반 항목 출력)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path.home() / 'fab-sim'
KNOWLEDGE = ROOT / 'knowledge'

MIN_LINES = 40           # 합격 노트 최소가 51줄 — 여유를 두되 스텁은 거른다
MIN_CITATIONS = 3        # 연도 표기 인용 최소 3건
MIN_SECTIONS = 3         # ## 절 최소 3개
MIN_LINKS = 1            # [[상호링크]] 최소 1개 — 고립 노트 방지

YEAR = re.compile(r'(?:\((?:19|20)\d{2}\)|(?:19|20)\d{2}-\d{2}|'
                  r'(?:et al\.?|,)\s*(?:19|20)\d{2}\b|'
                  r'\*[^*]+\*\s*\(?(?:19|20)\d{2})')
URL = re.compile(r'https?://|doi[:.]|arxiv|PMC\d+|\.(?:org|edu|jp|com)\b', re.I)
WIKILINK = re.compile(r'\[\[[^\]]+\]\]')
SECTION = re.compile(r'^##\s+', re.M)
# "검증했다"고 주장하려면 근거가 함께 있어야 한다.
VERIFY_CLAIM = re.compile(r'재현|검증|문헌값|sanity|대조')
# 정직성 표지: 확인 못 한 것을 확인 못 했다고 쓰는가
HONESTY = re.compile(r'미검증|추정|확인 못|불명|출처 불명|2차 인용')


def check(path: Path) -> list[str]:
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    bad: list[str] = []

    if len(lines) < MIN_LINES:
        bad.append(f'분량 부족: {len(lines)}줄 < {MIN_LINES}줄 (스텁 의심)')

    cites = len(YEAR.findall(text))
    urls = len(URL.findall(text))
    if cites < MIN_CITATIONS and urls < MIN_CITATIONS:
        bad.append(f'출처 부족: 연도인용 {cites}건 / URL·DOI {urls}건 '
                   f'(둘 중 하나가 {MIN_CITATIONS}건 이상이어야 함)')

    if len(SECTION.findall(text)) < MIN_SECTIONS:
        bad.append(f'구조 부족: ## 절 {len(SECTION.findall(text))}개 < {MIN_SECTIONS}개')

    if len(WIKILINK.findall(text)) < MIN_LINKS:
        bad.append('상호링크 없음: [[다른노트]] 최소 1개 — 고립된 노트는 지식베이스가 아니다')

    if not VERIFY_CLAIM.search(text):
        bad.append('검증 흔적 없음: 수식/수치를 문헌값과 대조한 서술이 없다')

    if not HONESTY.search(text):
        bad.append('정직성 표지 없음: 확인하지 못한 항목을 "미검증/추정"으로 '
                   '명시하지 않았다 (전부 확신하는 노트는 신뢰할 수 없다)')

    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='*')
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()

    targets = ([p for p in KNOWLEDGE.rglob('*.md') if p.name != 'INDEX.md']
               if a.all else [Path(p) for p in a.paths])
    if not targets:
        print('검사할 노트가 없다')
        return 1

    failed = 0
    for p in targets:
        if not p.exists():
            print(f'✗ {p} — 파일 없음')
            failed += 1
            continue
        bad = check(p)
        rel = p.relative_to(KNOWLEDGE) if KNOWLEDGE in p.parents else p
        if bad:
            failed += 1
            print(f'✗ {rel}')
            for b in bad:
                print(f'    - {b}')
        else:
            print(f'✓ {rel}')

    print(f'\n{len(targets) - failed}/{len(targets)} 통과')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
