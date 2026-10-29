#!/usr/bin/env bash
set -e

# Script de génération de paquet .deb pour Multipli
# Usage: ./build_deb.sh [amd64|arm64|all]

VERSION="1.0.1"
ARCH="${1:-amd64}"
APP_ID="org.gnome.Multipli"
PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${PKG_DIR}/../.." && pwd)"

echo "=== Construction du paquet .deb pour Multipli v${VERSION} (${ARCH}) ==="

BUILD_ROOT="/tmp/multipli-deb-build-${ARCH}"
rm -rf "${BUILD_ROOT}"
mkdir -p "${BUILD_ROOT}/DEBIAN"
mkdir -p "${BUILD_ROOT}/usr/bin"
mkdir -p "${BUILD_ROOT}/usr/lib/multipli/multipli"
mkdir -p "${BUILD_ROOT}/usr/lib/multipli/locales"
mkdir -p "${BUILD_ROOT}/usr/share/applications"
mkdir -p "${BUILD_ROOT}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${BUILD_ROOT}/usr/share/doc/multipli"

# Fichier control
cat << EOF > "${BUILD_ROOT}/DEBIAN/control"
Package: multipli
Version: ${VERSION}
Section: games
Priority: optional
Architecture: ${ARCH}
Depends: python3, python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1, gir1.2-gstreamer-1.0
Maintainer: Pierre <https://github.com/smilebob/multipli>
Description: Jeu éducatif natif GNOME des tables de multiplication (CE1 au CM2)
 Multipli est une application éducative moderne Libadwaita pour apprendre
 et maîtriser les tables de multiplication du CE1 au CM2 avec multi-profils,
 aventure progressive, chrono 60s et table de Pythagore.
 Distribué sous licence Apache-2.0.
 Code source & suivi : https://github.com/smilebob/multipli
Homepage: https://github.com/smilebob/multipli
Vcs-Browser: https://github.com/smilebob/multipli
Vcs-Git: https://github.com/smilebob/multipli.git
EOF

# Scripts postinst et postrm pour le cache des icônes et menus
cat << 'EOF' > "${BUILD_ROOT}/DEBIAN/postinst"
#!/bin/sh
set -e
if [ "$1" = "configure" ]; then
    update-desktop-database -q /usr/share/applications || true
    gtk-update-icon-cache -q /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 755 "${BUILD_ROOT}/DEBIAN/postinst"

cat << 'EOF' > "${BUILD_ROOT}/DEBIAN/postrm"
#!/bin/sh
set -e
if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    update-desktop-database -q /usr/share/applications || true
    gtk-update-icon-cache -q /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 755 "${BUILD_ROOT}/DEBIAN/postrm"

# Copie des fichiers d'application
cp "${ROOT_DIR}/main.py" "${BUILD_ROOT}/usr/lib/multipli/"
cp -r "${ROOT_DIR}/multipli/"* "${BUILD_ROOT}/usr/lib/multipli/multipli/"
cp -r "${ROOT_DIR}/locales/"* "${BUILD_ROOT}/usr/lib/multipli/locales/"
# Format machine-readable copyright Debian DEP-5
cat << EOF > "${BUILD_ROOT}/usr/share/doc/multipli/copyright"
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: Multipli
Upstream-Contact: Pierre <https://github.com/smilebob/multipli/issues>
Source: https://github.com/smilebob/multipli

Files: *
Copyright: 2026 Pierre & Contributors
License: Apache-2.0

License: Apache-2.0
EOF
cat "${ROOT_DIR}/LICENSE" >> "${BUILD_ROOT}/usr/share/doc/multipli/copyright"
cp "${ROOT_DIR}/LICENSE" "${BUILD_ROOT}/usr/share/doc/multipli/LICENSE"
cp "${ROOT_DIR}/README.md" "${BUILD_ROOT}/usr/share/doc/multipli/"

# Lanceur dans /usr/bin/multipli
cat << 'EOF' > "${BUILD_ROOT}/usr/bin/multipli"
#!/usr/bin/env bash
export PYTHONPATH="/usr/lib/multipli:${PYTHONPATH}"
exec python3 /usr/lib/multipli/main.py "$@"
EOF
chmod 755 "${BUILD_ROOT}/usr/bin/multipli"

# Intégration Desktop et Icône
cp "${ROOT_DIR}/data/icons/${APP_ID}.svg" "${BUILD_ROOT}/usr/share/icons/hicolor/scalable/apps/"
cp "${ROOT_DIR}/data/${APP_ID}.desktop" "${BUILD_ROOT}/usr/share/applications/"

# Construction du .deb
OUTPUT_DIR="${ROOT_DIR}/dist"
mkdir -p "${OUTPUT_DIR}"
DEB_NAME="multipli_${VERSION}_${ARCH}.deb"
dpkg-deb --root-owner-group --build "${BUILD_ROOT}" "${OUTPUT_DIR}/${DEB_NAME}"

rm -rf "${BUILD_ROOT}"
echo "Paquet créé avec succès : ${OUTPUT_DIR}/${DEB_NAME}"
