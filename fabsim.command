#!/bin/bash
# FabSim 시뮬레이터 실행 — 더블클릭하면 서버가 뜨고 브라우저가 열린다.
# 종료: 이 터미널 창에서 Ctrl+C
cd "$(dirname "$0")" || exit 1

PORT=8848
if lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "이미 실행 중입니다 (포트 $PORT)."
else
  echo "FabSim 시작 중..."
  .venv/bin/python -m uvicorn sim.api:app --port $PORT &
  for _ in $(seq 1 30); do
    curl -s -o /dev/null "http://localhost:$PORT/api/health" && break
    sleep 0.5
  done
fi

open "http://localhost:$PORT/3d"
echo ""
echo "  3D 스튜디오 : http://localhost:$PORT/3d"
echo "  API 문서    : http://localhost:$PORT/docs"
echo ""
echo "종료하려면 Ctrl+C"
wait
