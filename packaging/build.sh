#!/bin/bash
# FabSim Studio.app 빌드 + 배포 산출물 생성.
#
#   ./packaging/build.sh            # 앱 + wheel
#   ./packaging/build.sh --wheel    # wheel만
#
# 산출물: dist/fabsim-<ver>-py3-none-any.whl, dist/FabSim Studio.app
set -e
cd "$(dirname "$0")/.."
ROOT="$PWD"
VER=$(grep -m1 '^version' pyproject.toml | cut -d'"' -f2)
DIST="$ROOT/dist"
mkdir -p "$DIST"

echo "▶ FabSim $VER"

# ── 1. wheel — 런타임 팩을 패키지 안으로 복사한 뒤 빌드
echo "  wheel 빌드…"
rm -rf "$ROOT/sim/params"
mkdir -p "$ROOT/sim/params"
cp "$ROOT"/knowledge/params/*.yaml "$ROOT/sim/params/"
"$ROOT/.venv/bin/python" -m pip install -q --upgrade build >/dev/null 2>&1 || true
"$ROOT/.venv/bin/python" -m build --wheel --outdir "$DIST" >/dev/null
rm -rf "$ROOT/sim/params"          # 저장소에는 남기지 않는다(정본은 knowledge/params)
WHEEL=$(ls -t "$DIST"/fabsim-*.whl | head -1)
echo "    → $(basename "$WHEEL")"

[ "$1" = "--wheel" ] && exit 0

# ── 2. .app 번들
APP="$DIST/FabSim Studio.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"

cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>FabSim Studio</string>
  <key>CFBundleDisplayName</key><string>FabSim Studio</string>
  <key>CFBundleIdentifier</key><string>com.fabsim.studio</string>
  <key>CFBundleVersion</key><string>$VER</string>
  <key>CFBundleShortVersionString</key><string>$VER</string>
  <key>CFBundleExecutable</key><string>FabSimStudio</string>
  <key>CFBundleIconFile</key><string>icon.icns</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
  <key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST

cc -O2 -o "$APP/Contents/MacOS/FabSimStudio" packaging/launcher.c
cp packaging/run.sh "$APP/Contents/Resources/run.sh"
chmod +x "$APP/Contents/Resources/run.sh"
cp "$WHEEL" "$APP/Contents/Resources/"

# 아이콘 (PIL 있으면 생성, 없으면 생략)
APP_RES="$APP/Contents/Resources" "$ROOT/.venv/bin/python" packaging/make_icon.py 2>/dev/null || echo "    (아이콘 생략)"

codesign --force --deep --sign - "$APP" 2>/dev/null || echo "    (코드서명 생략)"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP" 2>/dev/null || true

echo "    → $APP"
echo
echo "설치:  cp -R '$APP' /Applications/"
echo "실행:  open '$APP'"
