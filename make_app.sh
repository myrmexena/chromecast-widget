#!/bin/bash
# Génère "Chromecast Widget.app" dans ~/Applications (indexé par Spotlight).
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/Applications/Chromecast Widget.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$REPO/assets/AppIcon.icns" "$APP/Contents/Resources/AppIcon.icns"
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Chromecast Widget</string>
  <key>CFBundleDisplayName</key><string>Chromecast Widget</string>
  <key>CFBundleIdentifier</key><string>local.chromecast-widget</string>
  <key>CFBundleIconFile</key><string>AppIcon</string>
  <key>CFBundleExecutable</key><string>launcher</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleVersion</key><string>1.0</string>
  <key>NSLocalNetworkUsageDescription</key><string>Détecter et contrôler les Chromecast du réseau.</string>
  <key>NSBonjourServices</key><array><string>_googlecast._tcp</string></array>
</dict></plist>
PLIST
cat > "$APP/Contents/MacOS/launcher" <<LAUNCH
#!/bin/bash
cd "$REPO"
"$REPO/.venv/bin/python" app.py
LAUNCH
chmod +x "$APP/Contents/MacOS/launcher"
codesign --force --deep -s - "$APP" 2>/dev/null && echo "Signé (ad hoc)"
echo "Créé : $APP"
