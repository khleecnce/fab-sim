#!/usr/bin/env python3
"""헤드리스 Chrome을 CDP로 몰아 FabSim 3D를 렌더링하고 스크린샷을 찍는다.

--virtual-time-budget 은 three.js 의 requestAnimationFrame 루프와 맞물려
영영 끝나지 않는다(실제로 300초 타임아웃). 그래서 브라우저를 띄워 두고
CDP로 "충분히 기다렸다가 찍기"를 직접 지시한다.

카메라를 각도별로 돌려가며 여러 장을 찍어, 새로 만든 SDS 캐비닛이
실제로 보이는지 눈으로 확인할 수 있게 한다.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

CHROME = Path.home() / ".cache/puppeteer/chrome/mac_arm-152.0.7977.54/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
PORT = 9333
RUN = Path.home() / "fab-sim/.run"
OUTDIR = Path("/tmp/viz3d")


def cdp_targets():
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=5) as r:
        return json.load(r)


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    token = (RUN / "token").read_text().strip()
    url = f"http://127.0.0.1:8848/3d?t={token}"

    proc = subprocess.Popen(
        [
            str(CHROME),
            "--headless=new",
            f"--remote-debugging-port={PORT}",
            "--remote-allow-origins=*",
            "--use-gl=angle",
            "--use-angle=swiftshader",
            "--enable-unsafe-swiftshader",
            "--no-sandbox",
            "--hide-scrollbars",
            "--window-size=1280,860",
            url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    try:
        # 디버깅 포트가 열릴 때까지
        for _ in range(60):
            try:
                tg = cdp_targets()
                if any(t["type"] == "page" for t in tg):
                    break
            except Exception:
                pass
            time.sleep(0.5)
        else:
            print("FAIL: CDP 포트가 안 열림")
            print(proc.stderr.read().decode()[-2000:])
            return 1

        page = next(t for t in cdp_targets() if t["type"] == "page")
        ws = page["webSocketDebuggerUrl"]

        try:
            from websocket import create_connection  # type: ignore
        except ImportError:
            print("FAIL: websocket-client 없음 → pip install websocket-client")
            return 2

        conn = create_connection(ws, timeout=60)
        mid = [0]

        def send(method, **params):
            mid[0] += 1
            conn.send(json.dumps({"id": mid[0], "method": method, "params": params}))
            while True:
                msg = json.loads(conn.recv())
                if msg.get("id") == mid[0]:
                    if "error" in msg:
                        raise RuntimeError(f"{method}: {msg['error']}")
                    return msg.get("result", {})

        send("Page.enable")
        send("Runtime.enable")
        time.sleep(9)  # three.js 로드 + 첫 프레임

        ok = send("Runtime.evaluate", expression="document.title", returnByValue=True)
        print("title:", ok["result"].get("value"))

        build = send(
            "Runtime.evaluate",
            expression="(document.getElementById('buildTag')||{}).textContent||''",
            returnByValue=True,
        )
        print("build:", build["result"].get("value"))

        # SDS 프록시가 실제로 씬에 등록됐는지
        chk = send(
            "Runtime.evaluate",
            expression="""(() => {
                const errs = (window.__errs||[]).slice(0,3);
                return JSON.stringify({errs});
            })()""",
            returnByValue=True,
        )
        print("errors:", chk["result"].get("value"))

        # 카메라 각도별 촬영
        views = [
            ("01_default", None),
            ("02_from_left", "camCur.yaw=-0.95; camCur.pitch=0.42; camCur.dist=9.5; camCur.target.set(0.2,0.9,-4.0); camGoal.yaw=camCur.yaw; camGoal.pitch=camCur.pitch; camGoal.dist=camCur.dist; camGoal.target.copy(camCur.target); place();"),
            ("03_sds_close", "camCur.yaw=-1.25; camCur.pitch=0.30; camCur.dist=4.2; camCur.target.set(-0.85,1.0,-4.0); camGoal.yaw=camCur.yaw; camGoal.pitch=camCur.pitch; camGoal.dist=camCur.dist; camGoal.target.copy(camCur.target); place();"),
            ("04_top", "camCur.yaw=-0.6; camCur.pitch=1.05; camCur.dist=11; camCur.target.set(0.5,0.8,-4.0); camGoal.yaw=camCur.yaw; camGoal.pitch=camCur.pitch; camGoal.dist=camCur.dist; camGoal.target.copy(camCur.target); place();"),
        ]
        for name, expr in views:
            if expr:
                send("Runtime.evaluate", expression=expr)
                time.sleep(2.5)
            shot = send("Page.captureScreenshot", format="png")
            p = OUTDIR / f"{name}.png"
            p.write_bytes(base64.b64decode(shot["data"]))
            print(f"  wrote {p} ({p.stat().st_size} bytes)")

        conn.close()
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
