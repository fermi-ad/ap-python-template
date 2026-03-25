#!/usr/bin/env bash
set -Eeuo pipefail

APP_CMD="${APP_CMD:-python -m __template_module__.main}"

echo "[start.sh] running: ${APP_CMD}"

exec /bin/bash -lc "${APP_CMD}"
