#!/usr/bin/env python3
"""슬러리 팩 선택 UI가 사람이 읽는 이름 + 막질군으로 뜨는지 실제 브라우저에서 검증한다."""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

CHROME = Path.home() / ".cache/puppeteer/chrome/mac_arm-152.0.7977.54/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
PORT = 9335
RUN = Path.home() / "fab-sim/.run"
OUT = Path("/tmp/viz3d")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    token = (RUN / "token").read_text().strip()
    proc = subprocess.Popen(
        [str(CHROME), "--headless=new", f"--remote-debugging-port={PORT}",
         "--remote-allow-origins=*", "--use-gl=angle", "--use-angle=swiftshader",
         "--enable-unsafe-swiftshader", "--no-sandbox", "--hide-scrollbars",
         "--window-size=1280,900", f"http://127.0.0.1:8848/3d?t={token}"],
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

        def ev(e):
            return send("Runtime.evaluate", expression=e, returnByValue=True)["result"].get("value")

        send("Page.enable"); send("Runtime.enable")
        time.sleep(9)
        bad = 0

        # 웨이퍼(⑤ Loading Unit)에 pack special 이 있다 → 거기로 이동
        ev("select('wafer')")
        time.sleep(1.5)

        sel = ev("!!document.getElementById('sel-pack')")
        print(f"  {'OK  ' if sel else 'FAIL'} 팩 선택 드롭다운 존재")
        bad += (not sel)

        if sel:
            groups = ev("JSON.stringify(Array.from(document.querySelectorAll('#sel-pack optgroup')).map(g=>g.label))")
            gl = json.loads(groups or "[]")
            ok = len(gl) >= 4
            print(f"  {'OK  ' if ok else 'FAIL'} 막질군 optgroup {len(gl)}개: {gl}")
            bad += (not ok)

            opts = ev("JSON.stringify(Array.from(document.querySelectorAll('#sel-pack option')).map(o=>o.textContent))")
            ol = json.loads(opts or "[]")
            raw = [o for o in ol if "_" in o and o.islower()]
            print(f"  {'OK  ' if not raw else 'FAIL'} 내부 ID 노출 {len(raw)}건" + (f" {raw}" if raw else ""))
            bad += bool(raw)
            for o in ol:
                print(f"        · {o}")

            has_base = any("base" == o.strip() for o in ol)
            print(f"  {'OK  ' if not has_base else 'FAIL'} base(공통값)가 슬러리 목록에서 제외됨")
            bad += has_base

            card = ev("(document.getElementById('packCard')||{}).textContent||''")
            okcard = ("막질" in card) and ("제거 기구" in card)
            print(f"  {'OK  ' if okcard else 'FAIL'} 선택한 팩의 상세 카드 표시")
            bad += (not okcard)

            # 팩을 바꾸면 카드도 바뀌나
            ev("""(() => { const s=document.getElementById('sel-pack');
                   s.value='w_fe_oxidizer'; s.dispatchEvent(new Event('change')); })()""")
            time.sleep(2.0)
            card2 = ev("(document.getElementById('packCard')||{}).textContent||''")
            okswap = "텅스텐" in card2 or "W 플러그" in card2
            print(f"  {'OK  ' if okswap else 'FAIL'} 팩 변경 시 카드 갱신 (W 선택)")
            bad += (not okswap)

        shot = send("Page.captureScreenshot", format="png")
        p = OUT / "06_pack_select.png"
        p.write_bytes(base64.b64decode(shot["data"]))
        print(f"  wrote {p}")

        # 카드가 보이도록 스크롤한 뒤 한 장 더 — 레이아웃을 눈으로 확인하려면 화면에 있어야 한다
        ev("""(() => { const c=document.getElementById('packCard');
               if(c) c.scrollIntoView({block:'center'}); })()""")
        time.sleep(1.2)
        shot2 = send("Page.captureScreenshot", format="png")
        p2 = OUT / "07_pack_card.png"
        p2.write_bytes(base64.b64decode(shot2["data"]))
        print(f"  wrote {p2}")
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
