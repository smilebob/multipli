#!/usr/bin/env bash
set -e

# Script de génération du bundle Flatpak pour Multipli
PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${PKG_DIR}/../.." && pwd)"
APP_ID="org.gnome.Multipli"
BUILD_DIR="/tmp/multipli-flatpak-build"
REPO_DIR="/tmp/multipli-flatpak-repo"
OUTPUT_DIR="${ROOT_DIR}/dist"

mkdir -p "${OUTPUT_DIR}"
rm -rf "${BUILD_DIR}" "${REPO_DIR}"

echo "=== Construction du Flatpak ${APP_ID} ==="
flatpak-builder --force-clean --repo="${REPO_DIR}" "${BUILD_DIR}" "${PKG_DIR}/${APP_ID}.yml"
flatpak build-bundle "${REPO_DIR}" "${OUTPUT_DIR}/${APP_ID}.flatpak" "${APP_ID}"

echo "Bundle Flatpak créé : ${OUTPUT_DIR}/${APP_ID}.flatpak"
