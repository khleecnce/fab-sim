#!/bin/bash
# 데모 배포 트리 동기화 — 여기 나열된 것만 배포된다(연구 노트·논문·코퍼스·크론 도구 제외).
set -e
cd "$(dirname "$0")"; R=../..
rsync -a --delete --exclude __pycache__ $R/sim/ sim/
mkdir -p knowledge/params knowledge/performance knowledge/additives knowledge/wafers validation tools
rsync -a --delete $R/knowledge/params/ knowledge/params/
rsync -a --delete $R/knowledge/performance/ knowledge/performance/
cp $R/knowledge/additives/catalog.yaml knowledge/additives/
cp $R/knowledge/wafers/npw_catalog.yaml knowledge/wafers/
cp $R/validation/MODEL-BASIS.md validation/
cp $R/tools/ingest_measurement.py tools/
cp $R/requirements-demo.txt requirements.txt
echo "synced: $(du -sh . | cut -f1)"
