#!/usr/bin/env python3
"""모바일에서 FabSim 열기 — LAN 또는 공개 터널 URL을 만들고 QR을 터미널에 찍는다.

사용자 지시(2026-09-08): "모바일에서 시뮬레이터 실행할수있게해"

두 가지 경로가 있고, 상황이 다르다.

  lan     폰과 맥이 **같은 Wi-Fi**에 있을 때. http://192.168.x.x:8848/3d
          가장 빠르고 아무 데도 데이터가 안 나간다. 회사·카페 게스트 Wi-Fi는
          단말 간 통신을 막는(AP isolation) 경우가 많아 안 될 수 있다.
  tunnel  밖에서(LTE·다른 망) 볼 때. Cloudflare Quick Tunnel로 https URL 생성.
          **공개 URL이므로 토큰을 강제한다** — 없으면 누구나 시뮬레이터와
          런 DB(data/store)를 연다. 링크에 ?t=<토큰>이 붙고 첫 접속에 쿠키로 굳는다.
          계정·설정 불필요하지만 URL은 실행할 때마다 바뀌고 맥을 끄면 죽는다.

사용법
  tools/mobile.py                # 자동: 같은 Wi-Fi면 LAN, 아니면 안내
  tools/mobile.py --tunnel       # 공개 https URL (토큰 자동 생성)
  tools/mobile.py --both
  tools/mobile.py --stop         # 서버·터널 종료

폰에서 '홈 화면에 추가'하면 주소창 없는 전체화면 앱이 된다(/manifest.webmanifest).
"""
from __future__ import annotations

import argparse
import os
import re
import secrets
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("FABSIM_PORT", 8848))
RUN = ROOT / ".run"
PID_API, PID_TUN = RUN / "api.pid", RUN / "tunnel.pid"
LOG_API, LOG_TUN = RUN / "api.log", RUN / "tunnel.log"
TOKEN_F = RUN / "token"


def lan_ip() -> str | None:
    """이 맥이 LAN에서 갖는 주소. 127.0.0.1은 폰에서 못 쓴다."""
    for iface in ("en0", "en1"):
        try:
            ip = subprocess.run(["ipconfig", "getifaddr", iface],
                                capture_output=True, text=True, timeout=3).stdout.strip()
            if ip:
                return ip
        except Exception:
            pass
    try:                                    # 폴백: 외부로 향하는 소켓의 로컬 주소
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip if not ip.startswith("127.") else None
    except Exception:
        return None


def port_open(host: str = "127.0.0.1") -> bool:
    with socket.socket() as s:
        s.settimeout(0.6)
        return s.connect_ex((host, PORT)) == 0


def qr(url: str) -> None:
    """터미널 QR. segno가 없으면 URL만 보여준다 — 실패해도 흐름을 막지 않는다."""
    try:
        import segno
        segno.make(url, error="m").terminal(compact=True)
    except Exception:
        print("  (QR 생략: .venv/bin/pip install segno)")


def start_api(token: str | None) -> None:
    RUN.mkdir(exist_ok=True)
    if port_open():
        cur = TOKEN_F.read_text().strip() if TOKEN_F.exists() else ""
        if (token or "") != cur:
            print(f"⚠ 포트 {PORT}에 이미 서버가 떠 있는데 토큰 설정이 다릅니다.")
            print("  --stop 으로 끄고 다시 실행하십시오.")
            sys.exit(1)
        print(f"· 서버 이미 실행 중 (포트 {PORT})")
        return
    env = dict(os.environ, FABSIM_PORT=str(PORT), FABSIM_HOST="0.0.0.0")
    if token:
        env["FABSIM_TOKEN"] = token
        TOKEN_F.write_text(token)
    elif TOKEN_F.exists():
        TOKEN_F.unlink()
    py = ROOT / ".venv" / "bin" / "python"
    with LOG_API.open("w") as lg:
        p = subprocess.Popen(
            [str(py if py.exists() else sys.executable), "-m", "uvicorn",
             "sim.api:app", "--host", "0.0.0.0", "--port", str(PORT)],
            cwd=ROOT, env=env, stdout=lg, stderr=subprocess.STDOUT,
            start_new_session=True)
    PID_API.write_text(str(p.pid))
    for _ in range(60):
        if port_open():
            print(f"· 서버 기동 (pid {p.pid}, 포트 {PORT})")
            return
        time.sleep(0.5)
    print(f"✗ 서버가 뜨지 않았습니다. 로그: {LOG_API}")
    sys.exit(1)


def start_tunnel() -> str | None:
    """Cloudflare Quick Tunnel. URL은 stderr 로그에 뜬다 — stdout이 아니다."""
    cf = None
    for c in (Path.home() / ".local/bin/cloudflared", Path("/opt/homebrew/bin/cloudflared")):
        if c.exists():
            cf = str(c)
            break
    if not cf:
        print("✗ cloudflared가 없습니다. 설치:")
        print("  curl -sL https://github.com/cloudflare/cloudflared/releases/latest/"
              "download/cloudflared-darwin-arm64.tgz | tar xz -C ~/.local/bin")
        return None
    with LOG_TUN.open("w") as lg:
        p = subprocess.Popen([cf, "tunnel", "--url", f"http://localhost:{PORT}",
                              "--no-autoupdate"],
                             stdout=lg, stderr=subprocess.STDOUT, start_new_session=True)
    PID_TUN.write_text(str(p.pid))
    for _ in range(60):
        time.sleep(0.5)
        txt = LOG_TUN.read_text(errors="ignore")
        m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", txt)
        if m:
            return m.group(0)
        if p.poll() is not None:
            break
    print(f"✗ 터널 URL을 못 받았습니다. 로그: {LOG_TUN}")
    return None


def stop() -> None:
    for f in (PID_TUN, PID_API):
        if not f.exists():
            continue
        try:
            os.killpg(os.getpgid(int(f.read_text())), signal.SIGTERM)
            print(f"· 종료: {f.stem}")
        except Exception as e:
            print(f"· {f.stem} 종료 실패(이미 죽었을 수 있음): {e}")
        f.unlink(missing_ok=True)
    TOKEN_F.unlink(missing_ok=True)
    # ⚠ SIGTERM 직후에도 포트는 몇 초 더 잡혀 있다. 여기서 기다리지 않으면
    # `--stop && --tunnel` 처럼 이어 실행할 때 "이미 실행 중"으로 오판한다.
    for _ in range(20):
        if not port_open():
            return
        time.sleep(0.3)


def main() -> int:
    ap = argparse.ArgumentParser(description="모바일에서 FabSim 열기")
    ap.add_argument("--tunnel", action="store_true", help="공개 https URL (밖에서 접속)")
    ap.add_argument("--lan", action="store_true", help="같은 Wi-Fi 전용 (기본)")
    ap.add_argument("--both", action="store_true")
    ap.add_argument("--stop", action="store_true")
    a = ap.parse_args()

    if a.stop:
        stop()
        return 0

    want_tunnel = a.tunnel or a.both
    want_lan = a.lan or a.both or not want_tunnel

    token = secrets.token_urlsafe(9) if want_tunnel else None
    start_api(token)

    print()
    if want_lan:
        ip = lan_ip()
        if ip:
            url = f"http://{ip}:{PORT}/3d"
            if token:
                url += f"?t={token}"
            print(f"■ 같은 Wi-Fi에서 (폰과 맥이 같은 공유기)\n  {url}\n")
            qr(url)
        else:
            print("■ LAN 주소를 찾지 못했습니다 (Wi-Fi 연결 확인). --tunnel 을 쓰십시오.")
        print()

    if want_tunnel:
        url = start_tunnel()
        if url:
            full = f"{url}/3d?t={token}"
            print(f"■ 밖에서 (LTE·다른 망) — 공개 https, 토큰 필요\n  {full}\n")
            qr(full)
            print("\n  ⚠ 이 URL은 공개입니다. 토큰이 링크에 포함돼 있으니 공유하지 마십시오.")
            print("  ⚠ 실행할 때마다 URL이 바뀌고, 맥을 끄거나 --stop 하면 죽습니다.")
        print()

    print("─" * 60)
    print("  폰에서: 공유 → '홈 화면에 추가' 하면 주소창 없는 전체화면 앱이 됩니다.")
    print("  조작: 1손가락 드래그=회전 · 2손가락=줌 · 탭=부위 선택 · Controls 버튼=패널 접기")
    print(f"  종료: tools/mobile.py --stop     로그: {LOG_API}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
