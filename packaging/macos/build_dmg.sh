#!/usr/bin/env bash
set -e

# Script de génération du paquet .dmg pour macOS (x86_64 et arm64)
# Exécuté dans l'environnement GitHub Actions macOS

VERSION="1.0.0"
APP_NAME="Multipli"
PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${PKG_DIR}/../.." && pwd)"
OUTPUT_DIR="${ROOT_DIR}/dist"
ARCH="$(uname -m)"

echo "=== Construction de ${APP_NAME}.dmg pour macOS (${ARCH}) ==="
mkdir -p "${OUTPUT_DIR}"

APP_DIR="/tmp/${APP_NAME}.app"
rm -rf "${APP_DIR}"
mkdir -p "${APP_DIR}/Contents/MacOS"
mkdir -p "${APP_DIR}/Contents/Resources/locales"

# Copie des fichiers source
cp "${ROOT_DIR}/main.py" "${APP_DIR}/Contents/Resources/"
cp -r "${ROOT_DIR}/multipli" "${APP_DIR}/Contents/Resources/"
cp -r "${ROOT_DIR}/locales/"* "${APP_DIR}/Contents/Resources/locales/"

# Script de démarrage Mac dans MacOS/Multipli
cat << 'EOF' > "${APP_DIR}/Contents/MacOS/Multipli"
#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../Resources" && pwd)"
export PYTHONPATH="${DIR}:${PYTHONPATH}"

# Utiliser Python 3 du système ou de Homebrew
if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
elif [ -f "/opt/homebrew/bin/python3" ]; then
    PY_BIN="/opt/homebrew/bin/python3"
elif [ -f "/usr/local/bin/python3" ]; then
    PY_BIN="/usr/local/bin/python3"
else
    echo "Python 3 introuvable."
    exit 1
fi

exec "${PY_BIN}" "${DIR}/main.py" "$@"
EOF
chmod +x "${APP_DIR}/Contents/MacOS/Multipli"

# Info.plist
cat << EOF > "${APP_DIR}/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Multipli</string>
    <key>CFBundleIdentifier</key>
    <string>org.gnome.Multipli</string>
    <key>CFBundleName</key>
    <string>Multipli</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Génération du .dmg via hdiutil ou create-dmg
DMG_STAGE="/tmp/dmg-stage"
rm -rf "${DMG_STAGE}"
mkdir -p "${DMG_STAGE}"
cp -r "${APP_DIR}" "${DMG_STAGE}/"
ln -s /Applications "${DMG_STAGE}/Applications"

DMG_FILE="${OUTPUT_DIR}/Multipli-${VERSION}-macOS-${ARCH}.dmg"
rm -f "${DMG_FILE}"

if command -v hdiutil >/dev/null 2>&1; then
    hdiutil create -volname "${APP_NAME}" -srcfolder "${DMG_STAGE}" -ov -format UDZO "${DMG_FILE}"
    echo "DMG créé avec succès : ${DMG_FILE}"
else
    echo "hdiutil non disponible sur ce système non-macOS (utilisé dans GitHub Actions runner macos)."
fi
