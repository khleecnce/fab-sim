"""모바일 뷰포트 스모크 — 폰 화면에서 실제로 쓸 수 있는지 눈으로 확인한다.

데스크톱 smoke3d.py와 별개인 이유: 깨지는 지점이 다르다.
  · 패널 400px가 화면을 먹어 3D가 사라지는가 (레이아웃)
  · 터치로 회전·줌·선택이 되는가 (mousedown/wheel은 폰에서 안 온다)
  · 캔버스가 0px로 잡히는가 (flex:1 + height 조합이 모바일에서 다르게 계산된다)

사용법 (서버가 :8848):
  /tmp/pwv/bin/python3 smoke_mobile.py
결과: /tmp/m_*.png + 상태 출력. ERRORS가 비어도 화면은 눈으로 봐야 한다.
"""
import asyncio, glob, os, json

URL = os.environ.get("FABSIM_URL", "http://localhost:8848/3d")
cands = sorted(glob.glob(os.path.expanduser(
    "~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-*/chrome-headless-shell")))
EXE = cands[-1] if cands else None
IPHONE = {"width": 390, "height": 844}          # iPhone 14/15 세로
LAND = {"width": 844, "height": 390}


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=[
            "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await b.new_context(viewport=IPHONE, device_scale_factor=3,
                                  is_mobile=True, has_touch=True,
                                  user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                                             "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
        pg = await ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
        await pg.goto(URL, wait_until="load")
        await pg.wait_for_timeout(4000)
        await pg.screenshot(path="/tmp/m_portrait.png")

        geo = await pg.evaluate("""()=>{
          const v=document.getElementById('view'), s=document.getElementById('side'),
                c=rend.domElement, t=document.getElementById('mtoggle');
          return {viewH:v.clientHeight, viewW:v.clientWidth, sideW:s.clientWidth,
                  canvasW:c.clientWidth, canvasH:c.clientHeight,
                  toggleShown:getComputedStyle(t).display!=='none',
                  stacked:getComputedStyle(document.getElementById('app')).flexDirection,
                  touchAction:getComputedStyle(c).touchAction,
                  tabH:document.querySelector('.tab').getBoundingClientRect().height};}""")
        print("GEO", json.dumps(geo))
        assert geo["stacked"] == "column", "모바일에서 세로 스택이 아니다"
        assert geo["canvasW"] > 300 and geo["canvasH"] > 180, f"캔버스가 너무 작다 {geo}"
        assert geo["touchAction"] == "none", "canvas touch-action이 none이 아니다(스크롤에 가로채임)"
        assert geo["toggleShown"], "Controls 접기 버튼이 안 보인다"

        # ⚠ 레이아웃이 맞아도 **컨트롤이 화면 밖으로 밀려나 있으면** 못 쓴다.
        # 첫 구현에서 #out(결과 20여 줄)이 자기 높이를 다 차지해 슬라이더가 든
        # #body가 0px로 눌렸다. 스크린샷을 봐야만 잡히는 유형이라 수치로 못 박는다.
        ctl = await pg.evaluate("""()=>{
          const b=document.getElementById('body');
          const r=b.querySelectorAll('input[type=range]');
          return {bodyH:b.clientHeight, ranges:r.length,
                  firstTop: r.length ? Math.round(r[0].getBoundingClientRect().top) : null};}""")
        print("CONTROLS", ctl)
        assert ctl["bodyH"] > 150, f"설정 패널(#body)이 눌려 있다 {ctl}"
        assert ctl["ranges"] >= 1, "슬라이더가 하나도 렌더되지 않았다"

        # ── 터치 회전
        y0 = await pg.evaluate("camGoal.yaw")
        await pg.touchscreen.tap(195, 150)          # 워밍업 (탭 자체도 오류 없이 돌아야 한다)
        await pg.wait_for_timeout(300)
        await pg.evaluate("""()=>{
          const c=rend.domElement, r=c.getBoundingClientRect();
          const mk=(t,pts)=>{const e=new TouchEvent(t,{bubbles:true,cancelable:true,
            touches:pts,targetTouches:pts,changedTouches:pts});c.dispatchEvent(e);};
          const T=(x,y)=>new Touch({identifier:1,target:c,clientX:x,clientY:y});
          mk('touchstart',[T(200,120)]); mk('touchmove',[T(280,120)]); mk('touchend',[]);
        }""")
        await pg.wait_for_timeout(300)
        y1 = await pg.evaluate("camGoal.yaw")
        print(f"TOUCH-ORBIT yaw {y0:.3f} -> {y1:.3f}  (달라야 회전 동작)")
        assert abs(y1 - y0) > 1e-3, "터치 드래그로 카메라가 안 돈다"

        # ── 핀치 줌
        # ⚠ 방향에 주의: 시작 dist가 ZOOM 하한(level0=3.0)에 붙어 있으면 확대 방향
        # 핀치는 클램프에 걸려 변화가 0이다. 그래서 **오므리기(축소)** 로 시험한다.
        d0 = await pg.evaluate("camGoal.dist")
        await pg.evaluate("""()=>{
          const c=rend.domElement;
          const mk=(t,pts)=>{c.dispatchEvent(new TouchEvent(t,{bubbles:true,cancelable:true,
            touches:pts,targetTouches:pts,changedTouches:pts}));};
          const T=(id,x,y)=>new Touch({identifier:id,target:c,clientX:x,clientY:y});
          mk('touchstart',[T(1,100,300),T(2,300,300)]);
          mk('touchmove',[T(1,170,300),T(2,230,300)]);   // 오므리면 = 축소(dist 증가)
          mk('touchend',[]);
        }""")
        await pg.wait_for_timeout(300)
        d1 = await pg.evaluate("camGoal.dist")
        print(f"PINCH dist {d0:.3f} -> {d1:.3f}  (오므렸으니 커져야 함)")
        assert d1 > d0 + 1e-3, "핀치 줌이 안 먹는다"

        # ── 패널 접기
        await pg.click("#mtoggle")
        await pg.wait_for_timeout(700)
        col = await pg.evaluate("""()=>({cls:document.body.className,
            viewH:document.getElementById('view').clientHeight,
            canvasH:rend.domElement.clientHeight})""")
        print("COLLAPSE", col)
        assert "panel-collapsed" in col["cls"]
        assert col["canvasH"] > geo["canvasH"] * 1.4, f"접었는데 캔버스가 안 커졌다 {col}"
        await pg.screenshot(path="/tmp/m_collapsed.png")
        await pg.click("#mtoggle"); await pg.wait_for_timeout(500)

        # ── 시뮬레이션 실행이 폰에서도 되는가 (엔진 왕복)
        await pg.evaluate("document.getElementById('body').scrollTop=99999")
        ran = await pg.evaluate("""async()=>{
          const r = await fetch('/api/simulate/v2',{method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({pack:'oxide_silica',model:'tier2.gw_physical_kp'})});
          const d = await r.json();
          return {status:r.status, mrr:d.mean_mrr_nm_min};}""")
        print("SIMULATE", ran)
        assert ran["status"] == 200 and ran["mrr"], "폰 컨텍스트에서 시뮬레이션 실패"

        # ── 가로 모드
        await pg.set_viewport_size(LAND)
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path="/tmp/m_landscape.png")
        print("LAND", await pg.evaluate("""()=>({canvasW:rend.domElement.clientWidth,
            canvasH:rend.domElement.clientHeight})"""))

        print("ERRORS:", errs[:10])
        await b.close()

asyncio.run(main())
