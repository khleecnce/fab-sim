#!/usr/bin/env python3
"""SDS 캐비닛 클릭 → ② Slurry 패널이 열리는지 실제 브라우저에서 검증한다."""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

CHROME = Path.home() / ".cache/puppeteer/chrome/mac_arm-152.0.7977.54/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
PORT = 9334
RUN = Path.home() / "fab-sim/.run"
OUT = Path("/tmp/viz3d")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    token = (RUN / "token").read_text().strip()
    url = f"http://127.0.0.1:8848/3d?t={token}"
    proc = subprocess.Popen(
        [str(CHROME), "--headless=new", f"--remote-debugging-port={PORT}",
         "--remote-allow-origins=*", "--use-gl=angle", "--use-angle=swiftshader",
         "--enable-unsafe-swiftshader", "--no-sandbox", "--hide-scrollbars",
         "--window-size=1280,860", url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                tg = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=5))
                if any(t["type"] == "page" for t in tg):
                    break
            except Exception:
                pass
            time.sleep(0.5)
        page = next(t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json")) if t["type"] == "page")
        from websocket import create_connection
        conn = create_connection(page["webSocketDebuggerUrl"], timeout=60)
        mid = [0]

        def send(method, **p):
            mid[0] += 1
            conn.send(json.dumps({"id": mid[0], "method": method, "params": p}))
            while True:
                m = json.loads(conn.recv())
                if m.get("id") == mid[0]:
                    if "error" in m:
                        raise RuntimeError(f"{method}: {m['error']}")
                    return m.get("result", {})

        def ev(expr):
            r = send("Runtime.evaluate", expression=expr, returnByValue=True)
            return r["result"].get("value")

        send("Page.enable"); send("Runtime.enable")
        time.sleep(9)

        bad = 0

        # 1) SDS 프록시가 씬에 있나
        n = ev("(() => { let c=0; tool.traverse(o=>{ if(o.userData && o.userData.id==='SDS') c++; }); return c; })()")
        print(f"  {'OK  ' if n == 1 else 'FAIL'} SDS 클릭 프록시 개수 = {n} (1 이어야 함)")
        bad += (n != 1)

        # 2) STATION 설명 등록
        has = ev("!!(STATION.SDS && STATION.SDS.label)")
        print(f"  {'OK  ' if has else 'FAIL'} STATION.SDS 설명 등록")
        bad += (not has)

        # 3) 캐비닛 내부 부품이 실제로 캐비닛 경계 안에 있나
        #    툴 좌표 X0..X1=-1.55..-0.15, Y0..Y1=3.05..4.95 → 월드 x, -z
        inside = ev("""(() => {
            let total=0, out=0;
            tool.traverse(o=>{
              if(!o.isMesh || !o.geometry || !o.geometry.boundingSphere) o.geometry && o.geometry.computeBoundingSphere();
              if(!o.isMesh) return;
              const p = new THREE.Vector3(); o.getWorldPosition(p);
              // SDS 영역 후보: 월드 x in [-1.6,-0.1], z in [-5.0,-3.0]
              if(p.x > -1.65 && p.x < -0.05 && p.z < -2.95 && p.z > -5.05){
                total++;
                if(p.y < 0.0 || p.y > 2.3) out++;   // 바닥 아래나 캐비닛 위로 튀어나감
              }
            });
            return JSON.stringify({total, out});
        })()""")
        d = json.loads(inside)
        print(f"  {'OK  ' if d['total'] > 15 and d['out'] == 0 else 'FAIL'} SDS 영역 메시 {d['total']}개, 높이 이탈 {d['out']}개")
        bad += (d["total"] <= 15 or d["out"] != 0)

        # 4) 클릭 → ② Slurry 패널 전환
        ev("goFocus('SDS')")
        time.sleep(1.5)
        tab = ev("(document.querySelector('#tabs .tab.on')||{}).textContent||''")
        panel = ev("(document.querySelector('#body h2, #body .ptitle')||{}).textContent||''")
        body = ev("(document.getElementById('body')||{}).textContent||''")
        okslurry = "Slurry" in (tab or "") or "Slurry" in (panel or "")
        print(f"  {'OK  ' if okslurry else 'FAIL'} SDS 클릭 → 활성 탭 = {tab!r}")
        bad += (not okslurry)

        haspid = ev("!!document.getElementById('pidBox')")
        print(f"  {'OK  ' if haspid else 'FAIL'} 패널에 P&ID 블록 존재")
        bad += (not haspid)

        # 조성 필드도 같은 패널에 있나 (통합 확인)
        both = ("Abrasive" in body) and ("Supply Path" in body or "Flow Rate" in body)
        print(f"  {'OK  ' if both else 'FAIL'} 한 패널에 조성 + 공급 동시 존재")
        bad += (not both)

        shot = send("Page.captureScreenshot", format="png")
        p = OUT / "05_sds_clicked.png"
        p.write_bytes(base64.b64decode(shot["data"]))
        print(f"  wrote {p}")

        print("\nALL PASS" if bad == 0 else f"\n{bad} FAILURE(S)")
        conn.close()
        return 1 if bad else 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
