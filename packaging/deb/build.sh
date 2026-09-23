#!/usr/bin/env bash
# Build a .deb package for wireprobe using fpm.
# Usage: build.sh <version> <output-dir>
set -euo pipefail

VERSION="${1:?usage: build.sh <version> <output-dir>}"
OUTPUT_DIR="${2:?usage: build.sh <version> <output-dir>}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAGE_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGE_DIR"' EXIT

mkdir -p "$STAGE_DIR/usr/lib/wireprobe" "$STAGE_DIR/usr/bin" "$STAGE_DIR/etc/wireprobe" \
    "$STAGE_DIR/usr/lib/systemd/system" "$STAGE_DIR/usr/share/doc/wireprobe"

cp -r "$ROOT_DIR/wireprobe/app" "$STAGE_DIR/usr/lib/wireprobe/"
cp "$ROOT_DIR/wireprobe/__init__.py" "$ROOT_DIR/wireprobe/fabfile.py" "$STAGE_DIR/usr/lib/wireprobe/"
cp "$ROOT_DIR/wireprobe/settings.yml.example" "$STAGE_DIR/etc/wireprobe/settings.yml.example"
cp "$ROOT_DIR/packaging/deb/wireprobe.service" "$STAGE_DIR/usr/lib/systemd/system/wireprobe.service"
cp "$ROOT_DIR/packaging/deb/copyright" "$STAGE_DIR/usr/share/doc/wireprobe/copyright"

# Normalize permissions: source files carry whatever mode git/the editor left
# them with, Debian policy wants 0755 dirs / 0644 files (executables excepted).
find "$STAGE_DIR" -type d -exec chmod 0755 {} +
find "$STAGE_DIR" -type f -exec chmod 0644 {} +
install -m 0755 "$ROOT_DIR/packaging/deb/wireprobe" "$STAGE_DIR/usr/bin/wireprobe"

mkdir -p "$OUTPUT_DIR"

fpm -s dir -t deb \
    --force \
    --chdir "$STAGE_DIR" \
    --name wireprobe \
    --version "$VERSION" \
    --architecture all \
    --category net \
    --vendor "OpenPrunus" \
    --description "WireGuard tunnel health probe
Monitors WireGuard peer handshakes and sends a Telegram and/or
email notification when a client's tunnel goes up or down." \
    --url "https://github.com/OpenPrunus/wireprobe/" \
    --maintainer "Benjamin Gounine <prunus@ecuri.es>" \
    --depends python3 \
    --depends python3-yaml \
    --depends python3-decorator \
    --depends python3-fabric \
    --depends python3-invoke \
    --depends python3-urllib3 \
    --depends adduser \
    --after-install "$ROOT_DIR/packaging/deb/postinst.sh" \
    --before-remove "$ROOT_DIR/packaging/deb/prerm.sh" \
    --package "$OUTPUT_DIR/wireprobe_${VERSION}_all.deb" \
    usr etc
