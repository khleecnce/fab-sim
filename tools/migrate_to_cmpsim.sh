#!/bin/bash
# fab-sim → CMP-Sim/legacy 재이관 (2026-09-20). 1차 이관(09-15 18:54) 이후 199커밋·노트 93편 추가분.
#
# 원칙: legacy는 "검증된 것만". 크론 도구·3D UI·테스트·논문 PDF·코퍼스 DB는 제외(용량·직무발명·재작성 금지 규칙).
# 이번엔 연구 노트(knowledge/*.md 전체)와 근거 보고서·완성 기준·판정 원장을 추가한다 — newfabsim이
# "왜 이 값인가"를 물을 때 답이 노트에 있기 때문.
set -e
SRC=~/fab-sim; DST=~/CMP-Sim/legacy
cd "$SRC"
[ -z "$(git status --short sim knowledge/params validation/datasets)" ] || { echo "✗ fab-sim에 미커밋 엔진/팩/데이터셋 변경 있음"; git status --short sim knowledge/params validation/datasets; exit 1; }

rsync -a --delete --exclude __pycache__ --exclude 'web/' sim/ "$DST/sim/"
rsync -a --delete --exclude 'web/' sim/web/demo.html "$DST/sim/" 2>/dev/null || true
rsync -a --delete knowledge/params/ "$DST/knowledge/params/"
rsync -a --delete knowledge/performance/ "$DST/knowledge/performance/"
rsync -a --delete knowledge/additives/ "$DST/knowledge/additives/"
rsync -a --delete knowledge/wafers/ "$DST/knowledge/wafers/"
rsync -a --delete knowledge/cmp/ "$DST/knowledge/cmp/"
rsync -a --delete knowledge/materials/ "$DST/knowledge/materials/"
rsync -a --delete knowledge/equipment/ "$DST/knowledge/equipment/"
rsync -a --delete validation/datasets/ "$DST/validation/datasets/"
mkdir -p "$DST/validation" "$DST/tools" "$DST/papers"
cp validation/MODEL-BASIS.md validation/RESULTS.md validation/ledger.jsonl validation/loop_ledger.jsonl validation/completion_last.json "$DST/validation/"
cp validation/backtest.py "$DST/validation/"
cp EVIDENCE-RULES.md COMPLETION.md ARCHITECTURE-V2.md HANDOFF.md "$DST/"
# 검증 도구 4개 — 재작성 금지 대상이 아니라 "그대로 실행"하라고 넘긴다
cp tools/completion.py tools/qa_loop.py tools/accuracy_gaps.py tools/check_knowledge.py tools/verify_claims.py tools/ingest_measurement.py "$DST/tools/"
# 원문 텍스트(QA 감사가 대조하는 것)만 — PDF 제외
rsync -a --include '*.txt' --include '*.xml' --exclude '*' papers/ "$DST/papers/"
# 테스트 — 계약(기준 1.0, ParamMissing, 격리)을 코드로 전달
rsync -a --delete tests/ "$DST/tests/"

cat > "$DST/HANDOVER-2.md" <<EOF
# legacy 2차 이관 — $(date '+%Y-%m-%d %H:%M') · fab-sim $(git rev-parse --short HEAD)

1차(09-15 18:54) 이후 fab-sim 199커밋분. 격자 $(./.venv/bin/python tools/completion.py check 2>/dev/null | head -1 | grep -o '[0-9]*/50'), 테스트 $(ls tests/*.py | wc -l | tr -d ' ')파일.

## 이번에 추가된 것
- knowledge/{cmp,materials,equipment}/ 연구 노트 전체($(ls knowledge/cmp knowledge/materials knowledge/equipment | grep -c '\.md$')편) — 파라미터의 "왜"
- validation/MODEL-BASIS.md 근거 보고서(자동 생성물), RESULTS.md, ledger.jsonl(QA 원장 #1~), completion_last.json
- COMPLETION.md(완성 기준 C1~C8), ARCHITECTURE-V2.md, EVIDENCE-RULES.md 최신(판정 #38까지)
- tools/: completion.py·qa_loop.py·accuracy_gaps.py·check_knowledge.py·verify_claims.py — **그대로 실행**(legacy/ 기준 경로로 돌리려면 ROOT 조정 필요)
- tests/ 전체 — 기준 1.0 계약·ParamMissing·격리 규칙이 코드로
- papers/*.txt — QA 감사 F1이 대조하는 원문(PDF 제외)

## 이관 안 한 것
- 3D UI(sim/web/studio3d.html), 크론 프롬프트(agents/), 코퍼스 DB(data/corpus 173MB), 논문 PDF(678MB), 런 DB
- 비공개 데모: https://fabsim-demo.vercel.app (토큰 ~/.fabsim-demo-token, deploy/demo/sync.sh) — fab-sim 트리 그대로 유지
EOF
echo "synced $(du -sh $DST | cut -f1)"
