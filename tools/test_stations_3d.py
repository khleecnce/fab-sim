#!/usr/bin/env python3
"""3D 씬의 **모든 스테이션**이 실제로 렌더되고 클릭 가능한지 한 번에 잠근다.

왜 필요한가 (ux_audit R6):
  코드에 `proxy("FI", ...)` 가 있다는 것은 증거가 아니다. 2026-09-11 SDS 캐비닛은
  부품 40개를 넣었는데 첫 렌더에서 **빈 흰 상자**였고(불투명 패널), 좌표 규약을 헷갈려
  부품이 케이스 밖으로 새기도 했다. 문법 검사도 pytest 도 이걸 못 잡는다.

무엇을 검사하나 — 스테이션마다:
  ① 클릭 프록시가 씬에 정확히 1개 등록됐는가
  ② STATION 설명(label/desc)이 있는가
  ③ 프록시 위치에 실제 지오메트리가 있는가 (빈 껍데기 프록시 방지)
  ④ 클릭하면 예외 없이 동작하고, 담당 탭이 있으면 그 탭이 열리는가
  ⑤ 콘솔 오류가 없는가

실행: .venv/bin/python tools/test_stations_3d.py
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

CHROME = Path.home() / ".cache/puppeteer/chrome/mac_arm-152.0.7977.54/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
PORT = 9336
RUN = Path.home() / "fab-sim/.run"
OUT = Path("/tmp/viz3d")

# 스테이션별 최소 기대치 — 너무 빡빡하면 정상 변경에 깨지고,
# 너무 느슨하면 빈 상자를 통과시킨다. "적어도 이만큼은 있어야 한다" 수준.
MIN_MESHES = {
    "FI": 20,    # 로드포트 3 + FOUP + 로봇
    "CL": 15,    # 5개 모듈 + 핸들러
    "P1": 20,    # 플래튼·패드·캐리어·디스크·노즐
    "P2": 5,
    "P3": 5,
    "TS": 5,
    "CAR": 5,
    "SDS": 25,   # 드럼2·탱크·펌프·필터2·유량계·배관
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    if not CHROME.exists():
        print(f"SKIP: Chrome for Testing 없음 ({CHROME})")
        return 0
    token = (RUN / "token").read_text().strip()
    proc = subprocess.Popen(
        [str(CHROME), "--headless=new", f"--remote-debugging-port={PORT}",
         "--remote-allow-origins=*", "--use-gl=angle", "--use-angle=swiftshader",
         "--enable-unsafe-swiftshader", "--no-sandbox", "--hide-scrollbars",
         "--window-size=1280,860", f"http://127.0.0.1:8848/3d?t={token}"],
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
        else:
            print("FAIL: CDP 연결 실패 — 서버가 떠 있는지 확인하십시오")
            return 1

        page = next(t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                    if t["type"] == "page")
        from websocket import create_connection
        conn = create_connection(page["webSocketDebuggerUrl"], timeout=60)
        mid = [0]
        console_errors = []

        def send(method, **p):
            mid[0] += 1
            conn.send(json.dumps({"id": mid[0], "method": method, "params": p}))
            while True:
                m = json.loads(conn.recv())
                if m.get("method") == "Runtime.exceptionThrown":
                    console_errors.append(str(m["params"]).replace("\n", " ")[:160])
                if m.get("id") == mid[0]:
                    if "error" in m:
                        raise RuntimeError(f"{method}: {m['error']}")
                    return m.get("result", {})

        def ev(e):
            return send("Runtime.evaluate", expression=e, returnByValue=True)["result"].get("value")

        send("Page.enable"); send("Runtime.enable")
        time.sleep(9)
        bad = 0

        stations = json.loads(ev("JSON.stringify(Object.keys(STATION))") or "[]")
        print(f"스테이션 {len(stations)}개: {', '.join(stations)}\n")

        for st in stations:
            if st == "TOOL":           # 전체 뷰 — 프록시 없음이 정상
                continue
            n_proxy = ev(f"proxies.filter(p=>p.userData.id==='{st}').length")
            has_desc = ev(f"!!(STATION['{st}'] && STATION['{st}'].desc)")

            # 프록시 반경 안에 실제 메시가 몇 개인가 (빈 껍데기 방지)
            n_mesh = ev(f"""(() => {{
                const px = proxies.find(p=>p.userData.id==='{st}');
                if(!px) return -1;
                const c = new THREE.Vector3(); px.getWorldPosition(c);
                px.geometry.computeBoundingSphere();
                const R = px.geometry.boundingSphere.radius * 1.15;
                let n = 0;
                tool.traverse(o=>{{
                  if(!o.isMesh || o.material === M.hotspot) return;
                  const p = new THREE.Vector3(); o.getWorldPosition(p);
                  if(p.distanceTo(c) <= R) n++;
                }});
                return n;
            }})()""")

            want = MIN_MESHES.get(st, 3)
            ok_proxy = (n_proxy == 1)
            ok_mesh = (n_mesh >= want)
            mark = "OK  " if (ok_proxy and has_desc and ok_mesh) else "FAIL"
            print(f"  {mark} {st:5s} 프록시={n_proxy} 설명={'Y' if has_desc else 'N'} "
                  f"내부메시={n_mesh} (최소 {want})")
            if not (ok_proxy and has_desc and ok_mesh):
                bad += 1

            # 클릭이 예외 없이 도는가 + 담당 탭 전환
            try:
                ev(f"goFocus('{st}')")
                time.sleep(0.5)
                part = ev(f"(STATION_PART['{st}']||'')")
                if part:
                    # 탭 요소의 파트 키는 data-k 다 (data-part 아님 — 실제 DOM 확인)
                    on = ev("(document.querySelector('#tabs .tab.on')||{}).dataset.k||''")
                    if on != part:
                        print(f"       FAIL 클릭 시 '{part}' 탭이 열려야 하는데 '{on}'")
                        bad += 1
            except Exception as e:
                print(f"       FAIL 클릭에서 예외: {e}")
                bad += 1

        ev("goLevel(0)")
        time.sleep(1.5)
        shot = send("Page.captureScreenshot", format="png")
        (OUT / "08_all_stations.png").write_bytes(base64.b64decode(shot["data"]))
        print(f"\n  wrote {OUT/'08_all_stations.png'}")

        if console_errors:
            print(f"  FAIL 콘솔 오류 {len(console_errors)}건")
            for e in console_errors[:3]:
                print(f"        {e}")
            bad += 1
        else:
            print("  OK   콘솔 오류 없음")

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
