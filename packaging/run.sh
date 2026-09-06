#!/bin/bash
# FabSim Studio 실행 — 전용 venv를 앱 지원 폴더에 만들고 거기서 띄운다.
set -e
APP_SUPPORT="$HOME/Library/Application Support/FabSim"
VENV="$APP_SUPPORT/venv"
LOG="$APP_SUPPORT/studio.log"
mkdir -p "$APP_SUPPORT"

# 개발 저장소가 있으면 그걸 쓰고(코드 수정이 바로 반영), 없으면 설치본을 쓴다
REPO="$HOME/fab-sim"
PY=""
if [ -x "$REPO/.venv/bin/python" ] && [ -f "$REPO/sim/studio.py" ]; then
  PY="$REPO/.venv/bin/python"
  cd "$REPO"
else
  if [ ! -x "$VENV/bin/python" ]; then
    /usr/bin/python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q --upgrade pip >/dev/null 2>&1 || true
    WHEEL=$(ls "$(dirname "$0")"/fabsim-*.whl 2>/dev/null | head -1)
    if [ -n "$WHEEL" ]; then
      "$VENV/bin/pip" install -q "$WHEEL[ui]"
    else
      osascript -e 'display alert "FabSim" message "설치 파일(wheel)을 찾을 수 없습니다."'
      exit 1
    fi
  fi
  PY="$VENV/bin/python"
fi

# 이미 떠 있으면 브라우저만 연다
if nc -z 127.0.0.1 8790 2>/dev/null; then
  open "http://127.0.0.1:8790"; exit 0
fi

nohup "$PY" -m sim.launch >>"$LOG" 2>&1 &
for i in $(seq 1 40); do
  nc -z 127.0.0.1 8790 2>/dev/null && break
  sleep 0.4
done
open "http://127.0.0.1:8790" 2>/dev/null || true
