#!/bin/bash
# FabSim 상시 가동 — LaunchAgent(ai.hermes.fabsim.plist)가 이 스크립트를 지킨다.
#
# 왜 스크립트인가: launchd는 프로세스 하나만 지켜준다. 우리는 둘(API 서버 +
# cloudflared 터널)이 필요하고, 터널 URL이 바뀔 때마다 텔레그램으로 알려야 한다.
# 이 스크립트가 둘을 띄우고 foreground에 남아 launchd의 KeepAlive 대상이 된다.
#
# 설계 원칙 (Hermes 게이트웨이 plist와 같은 패턴):
#   · RunAtLoad + KeepAlive → 재부팅·크래시에도 알아서 살아난다
#   · 토큰은 파일에 고정 → 재시작해도 링크가 안 바뀐다(Quick Tunnel 주소만 바뀜)
#   · 주소가 바뀌면 텔레그램으로 새 링크를 보낸다 → 사용자가 찾아다닐 필요 없음
set -u
ROOT="$HOME/fab-sim"
RUN="$ROOT/.run"
PORT="${FABSIM_PORT:-8848}"
mkdir -p "$RUN"

# ── 토큰: 한 번 만들면 계속 쓴다 (재시작해도 링크 유효) ──────────────
TOKF="$RUN/token"
if [ ! -s "$TOKF" ]; then
  "$ROOT/.venv/bin/python" -c "import secrets;print(secrets.token_urlsafe(12))" > "$TOKF"
fi
TOKEN="$(cat "$TOKF")"
export FABSIM_TOKEN="$TOKEN"

notify() {   # 텔레그램 알림. 실패해도 서비스를 멈추지 않는다.
  local msg="$1"
  local bt cid
  bt="$(grep -m1 '^TELEGRAM_BOT_TOKEN=' "$HOME/.hermes/.env" | cut -d= -f2-)"
  cid="$(grep -m1 '^TELEGRAM_HOME_CHANNEL=' "$HOME/.hermes/.env" | cut -d= -f2-)"
  [ -n "$bt" ] && [ -n "$cid" ] || return 0
  # ⚠ 속도 제한: 어떤 이유로든 재시작 루프가 생기면 알림이 폭주한다
  # (2026-09-11: 포트 충돌로 40초마다 새 주소가 발송됨). 1시간에 3건까지만 허용.
  local stampf="$RUN/notify_stamps" now cnt
  now=$(date +%s)
  cnt=0
  if [ -f "$stampf" ]; then
    awk -v n="$now" '$1 > n-3600' "$stampf" > "$stampf.tmp" 2>/dev/null && mv "$stampf.tmp" "$stampf"
    cnt=$(wc -l < "$stampf" | tr -d ' ')
  fi
  if [ "${cnt:-0}" -ge 3 ]; then
    echo "$(date) notify suppressed (rate limit: $cnt in last hour)" >> "$RUN/api.log"
    return 0
  fi
  echo "$now" >> "$stampf"
  curl -s -m 20 -o /dev/null -X POST "https://api.telegram.org/bot${bt}/sendMessage" \
    --data-urlencode "chat_id=${cid}" \
    --data-urlencode "text=${msg}" \
    --data-urlencode "disable_web_page_preview=true" || true
}

cleanup() {
  [ -n "${API_PID:-}" ] && kill "$API_PID" 2>/dev/null
  [ -n "${TUN_PID:-}" ] && kill "$TUN_PID" 2>/dev/null
  exit 0
}
trap cleanup TERM INT

# ── 0. 중복 기동 방지 ──────────────────────────────────────────
# ⚠ 이게 없으면 무한 재시작 루프가 돈다(2026-09-11 실제 발생):
#   누군가 8848을 수동으로 점유 → 여기 uvicorn이 "address already in use"로 즉사
#   → 30초 뒤 감시 루프가 cleanup → launchd KeepAlive가 통째로 재기동
#   → **터널도 새로 생성되어 새 주소를 텔레그램 발송** → 40초마다 무한 반복.
# 포트를 이미 누가 쓰고 있으면 새로 띄우지 말고, 그 서버를 그대로 인정한다.
PORT_OWNER="$(lsof -ti:"$PORT" 2>/dev/null | head -1)"
if [ -n "$PORT_OWNER" ]; then
  if curl -s -o /dev/null -m 3 "http://127.0.0.1:$PORT/api/health"; then
    # 정상 서비스 중 — 우리가 낄 자리가 없다. 알림 없이 조용히 대기만 한다.
    echo "$(date) port $PORT already served by pid $PORT_OWNER — standing by" >> "$RUN/api.log"
    ADOPTED=1
  else
    # 포트는 잡혔는데 헬스체크 실패 = 좀비. 정리하고 우리가 띄운다.
    echo "$(date) stale holder pid $PORT_OWNER on $PORT — killing" >> "$RUN/api.log"
    kill -9 "$PORT_OWNER" 2>/dev/null
    sleep 2
  fi
fi

# ── 1. API 서버 ────────────────────────────────────────────────
cd "$ROOT" || exit 1
if [ "${ADOPTED:-0}" != "1" ]; then
  "$ROOT/.venv/bin/python" -m uvicorn sim.api:app --host 0.0.0.0 --port "$PORT" \
    >> "$RUN/api.log" 2>&1 &
  API_PID=$!
  UP=0
  for _ in $(seq 1 60); do
    curl -s -o /dev/null -m 2 "http://127.0.0.1:$PORT/api/health" && { UP=1; break; }
    kill -0 "$API_PID" 2>/dev/null || break      # 이미 죽었으면 기다릴 이유가 없다
    sleep 0.5
  done
  # 못 떴으면 터널을 만들지 않는다 — 안 그러면 죽은 서버를 가리키는 새 주소만 계속 발송된다
  if [ "$UP" != "1" ]; then
    echo "$(date) api failed to start — backing off 300s (no tunnel, no notify)" >> "$RUN/api.log"
    kill "$API_PID" 2>/dev/null
    sleep 300
    exit 1
  fi
fi

# ── 2. Cloudflare Quick Tunnel ─────────────────────────────────
# 계정·도메인 없이 쓰는 대신 주소가 실행마다 바뀐다. 그래서 바뀔 때마다 알린다.
CF="$HOME/.local/bin/cloudflared"
URL=""
if [ -x "$CF" ]; then
  : > "$RUN/tunnel.log"
  "$CF" tunnel --url "http://localhost:$PORT" --no-autoupdate \
    >> "$RUN/tunnel.log" 2>&1 &
  TUN_PID=$!
  for _ in $(seq 1 60); do
    URL="$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$RUN/tunnel.log" | head -1)"
    [ -n "$URL" ] && break
    sleep 1
  done
fi

LAN="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)"
{
  echo "token=$TOKEN"
  echo "lan=http://${LAN}:${PORT}/3d?t=${TOKEN}"
  [ -n "$URL" ] && echo "tunnel=${URL}/3d?t=${TOKEN}"
} > "$RUN/urls.txt"

# 주소 갱신 알림은 사용자 지시로 중단(2026-09-11). 주소는 .run/urls.txt에만 기록한다.
# 다시 켜려면 아래 NOTIFY_URL_CHANGE=1 로 바꾼다.
NOTIFY_URL_CHANGE=0
PREV="$RUN/last_url"
if [ -n "$URL" ] && [ "$URL" != "$(cat "$PREV" 2>/dev/null)" ]; then
  echo "$URL" > "$PREV"
  if [ "$NOTIFY_URL_CHANGE" = "1" ]; then
    notify "📱 FabSim 모바일 주소가 갱신됐습니다

밖에서: ${URL}/3d?t=${TOKEN}
같은 Wi-Fi: http://${LAN}:${PORT}/3d?t=${TOKEN}

(맥 재시작·터널 재연결 시 앞 주소는 바뀝니다. Wi-Fi 주소는 그대로입니다.)"
  fi
fi

# ── 3. 감시 루프 ───────────────────────────────────────────────
# 둘 중 하나라도 죽으면 스크립트를 끝낸다 → launchd(KeepAlive)가 통째로 다시 띄운다.
# 여기서 개별 재시작을 구현하면 launchd와 이중 관리가 되어 상태를 알 수 없게 된다.
# ⚠ 단, 죽었을 때 즉시 끝내면 launchd가 곧바로 재기동해 폭주한다. 잠깐 쉬고 나간다
#   (launchd ThrottleInterval 과 별개로, 터널 재생성 비용을 줄이기 위한 안전판).
die() {
  echo "$(date) $1 — restarting in 20s" >> "$RUN/api.log"
  sleep 20
  cleanup
}
while true; do
  sleep 30
  # ADOPTED(남의 서버에 얹힌 경우)면 PID 대신 헬스체크로 살아있는지 본다
  if [ "${ADOPTED:-0}" = "1" ]; then
    curl -s -o /dev/null -m 5 "http://127.0.0.1:$PORT/api/health" || die "adopted api gone"
  else
    kill -0 "$API_PID" 2>/dev/null || die "api died"
  fi
  if [ -n "${TUN_PID:-}" ]; then
    kill -0 "$TUN_PID" 2>/dev/null || die "tunnel died"
  fi
done
