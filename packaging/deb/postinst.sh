#!/bin/sh
set -e

if ! getent group wireprobe >/dev/null; then
    addgroup --system wireprobe
fi

if ! getent passwd wireprobe >/dev/null; then
    adduser --system --ingroup wireprobe --no-create-home --home /nonexistent \
        --shell /usr/sbin/nologin wireprobe
fi

chown -R wireprobe:wireprobe /etc/wireprobe

if [ -d /run/systemd/system ]; then
    systemctl daemon-reload >/dev/null 2>&1 || true
    systemctl enable wireprobe.service >/dev/null 2>&1 || true
fi

exit 0
