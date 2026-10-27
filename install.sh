#!/usr/bin/env bash
set -e

APP_NAME="multipli"
APP_ID="org.gnome.Multipli"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INSTALL_BIN="$HOME/.local/bin"
INSTALL_APPS="$HOME/.local/share/applications"
INSTALL_ICONS="$HOME/.local/share/icons/hicolor/scalable/apps"
INSTALL_DATA="$HOME/.local/share/${APP_NAME}"

if [ "$1" == "--uninstall" ]; then
    echo "Désinstallation de Multipli..."
    rm -f "${INSTALL_BIN}/${APP_NAME}"
    rm -f "${INSTALL_APPS}/${APP_ID}.desktop"
    rm -f "${INSTALL_ICONS}/${APP_ID}.svg"
    rm -rf "${INSTALL_DATA}"
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    echo "Multipli a été désinstallé avec succès."
    exit 0
fi

echo "Installation de Multipli dans l'environnement GNOME..."

mkdir -p "${INSTALL_BIN}"
mkdir -p "${INSTALL_APPS}"
mkdir -p "${INSTALL_ICONS}"
mkdir -p "${INSTALL_DATA}"

# Copie des fichiers de code et de données
cp -r "${SRC_DIR}/main.py" "${INSTALL_DATA}/"
cp -r "${SRC_DIR}/multipli" "${INSTALL_DATA}/"
cp -r "${SRC_DIR}/locales" "${INSTALL_DATA}/"

# Création du lanceur dans ~/.local/bin
cat << 'EOF' > "${INSTALL_BIN}/${APP_NAME}"
#!/usr/bin/env bash
APP_DATA="$HOME/.local/share/multipli"
export PYTHONPATH="${APP_DATA}:${PYTHONPATH}"
exec python3 "${APP_DATA}/main.py" "$@"
EOF
chmod +x "${INSTALL_BIN}/${APP_NAME}"

# Installation de l'icône
cp "${SRC_DIR}/data/icons/${APP_ID}.svg" "${INSTALL_ICONS}/"

# Installation du fichier .desktop
sed "s|Exec=multipli|Exec=${INSTALL_BIN}/${APP_NAME}|g" "${SRC_DIR}/data/${APP_ID}.desktop" > "${INSTALL_APPS}/${APP_ID}.desktop"
chmod +x "${INSTALL_APPS}/${APP_ID}.desktop"

update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo "Installation terminée avec succès !"
echo "Vous pouvez maintenant lancer Multipli depuis vos applications GNOME ou via la commande : multipli"
