"""앱 아이콘 생성 — 웨이퍼 원 + 제거율 프로파일 호. PIL 없으면 조용히 종료."""
import os, subprocess, tempfile
from pathlib import Path
try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit(0)

res = Path(os.environ.get("APP_RES", "."))
d = Path(tempfile.mkdtemp()) / "icon.iconset"
d.mkdir(parents=True)
for s in (16, 32, 64, 128, 256, 512, 1024):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    g = ImageDraw.Draw(im)
    p = s / 8
    g.rounded_rectangle([p/2, p/2, s-p/2, s-p/2], radius=s/6, fill=(22, 27, 34, 255))
    g.ellipse([p*1.4, p*1.4, s-p*1.4, s-p*1.4],
              outline=(121, 192, 255, 255), width=max(1, s//32))
    g.arc([p*2.3, p*2.3, s-p*2.3, s-p*2.3], 200, 340,
          fill=(126, 231, 135, 255), width=max(1, s//26))
    im.save(d / f"icon_{s}x{s}.png")
subprocess.run(["iconutil", "-c", "icns", str(d), "-o", str(res / "icon.icns")],
               check=False)
