#!/usr/bin/env bash
set -Eeuo pipefail

################################ Configuration ################################
######## Edit these defaults or override them through the environment. ########

### Xpra connection settings.
# Xpra session name.
APP_NAME="${APP_NAME:-ap-python-starter-kit}"
# Xpra display number.
XPRA_DISPLAY="${XPRA_DISPLAY:-:100}"
# Xpra authentication method (if any).
XPRA_AUTH="${XPRA_AUTH:-none}"

### Xpra HTML client settings.
# Enable or disable Xpra's HTML client.
XPRA_HTML="${XPRA_HTML:-on}"
# Host and port where Xpra serves its HTML client.
XPRA_BIND_HOST="${XPRA_BIND_HOST:-0.0.0.0}"
XPRA_BIND_PORT="${XPRA_BIND_PORT:-14500}"

### Application and logging settings.
# Command launched by Xpra.
APP_CMD="${APP_CMD:-python -m ap_python_starter_kit.main}"
# Paths for Xpra and application logs.
XPRA_LOG_FILE="${XPRA_LOG_FILE:-/tmp/xpra.log}"
APP_LOG_FILE="${APP_LOG_FILE:-/tmp/app.log}"

### Xpra lifecycle settings.
# Stop Xpra when the launched application process (APP_CMD) exits.
XPRA_EXIT_WITH_CHILDREN="${XPRA_EXIT_WITH_CHILDREN:-yes}"
# Stop Xpra when the application no longer has any windows open.
XPRA_EXIT_WITH_WINDOWS="${XPRA_EXIT_WITH_WINDOWS:-yes}"
# Stop Xpra after this many seconds of server idle time.
XPRA_SERVER_IDLE_TIMEOUT="${XPRA_SERVER_IDLE_TIMEOUT:-300}"

### Directory settings.
# Base directory used for writable runtime paths.
RUNTIME_BASE="${RUNTIME_BASE:-/tmp}"
# Runtime directories used by Xpra and the application user.
XDG_RUNTIME_DIR_DEFAULT="${XDG_RUNTIME_DIR:-${RUNTIME_BASE}/runtime-pyuser}"
XPRA_RUN_DIR_DEFAULT="${XPRA_RUN_DIR:-${RUNTIME_BASE}/xpra}"
USER_RUN_DIR_DEFAULT="${USER_RUN_DIR:-${RUNTIME_BASE}/user-1000}"
###############################################################################

cleanup() {
  echo "[start.sh] shutting down"
  xpra stop "${XPRA_DISPLAY}" >/dev/null 2>&1 || true
}

trap cleanup SIGINT SIGTERM EXIT

mkdir -p "${USER_RUN_DIR_DEFAULT}" "${XDG_RUNTIME_DIR_DEFAULT}" "${XPRA_RUN_DIR_DEFAULT}" /tmp/.X11-unix
chmod 700 "${USER_RUN_DIR_DEFAULT}" "${XDG_RUNTIME_DIR_DEFAULT}" "${XPRA_RUN_DIR_DEFAULT}" || true
if ! chmod 1777 /tmp/.X11-unix 2>/dev/null; then
  echo "[start.sh] warning: could not chmod /tmp/.X11-unix (continuing)" >&2
fi

touch "${APP_LOG_FILE}" "${XPRA_LOG_FILE}"

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR_DEFAULT}"

echo "[start.sh] starting Xpra HTML on ${XPRA_BIND_HOST}:${XPRA_BIND_PORT} display ${XPRA_DISPLAY} (auth=${XPRA_AUTH})"

echo "[start.sh] app cmd: ${APP_CMD}" >"${APP_LOG_FILE}"

xpra start "${XPRA_DISPLAY}" \
  --bind-tcp="${XPRA_BIND_HOST}:${XPRA_BIND_PORT}" \
  --html="${XPRA_HTML}" \
  --auth="${XPRA_AUTH}" \
  --daemon=no \
  --exit-with-children="${XPRA_EXIT_WITH_CHILDREN}" \
  --exit-with-windows="${XPRA_EXIT_WITH_WINDOWS}" \
  --server-idle-timeout="${XPRA_SERVER_IDLE_TIMEOUT}" \
  --start-child="/bin/bash -lc '${APP_CMD} >>\"${APP_LOG_FILE}\" 2>&1'" \
  --pulseaudio=no \
  --notifications=no \
  --bell=no \
  --headerbar=force \
  --mdns=no \
  --dbus-launch=no \
  --dbus-control=no \
  --session-name="${APP_NAME}" \
  --dpi=0 \
  >>"${XPRA_LOG_FILE}" 2>&1 &

READY_HOST="127.0.0.1"
for i in $(seq 1 30); do
  if curl -fsS "http://${READY_HOST}:${XPRA_BIND_PORT}/" >/dev/null 2>&1; then
    echo "[start.sh] Xpra is ready: http://${READY_HOST}:${XPRA_BIND_PORT}/"
    break
  fi

  if ! kill -0 "$!" 2>/dev/null; then
    echo "[start.sh] Xpra exited early. Last log lines:" >&2
    tail -n 200 "${XPRA_LOG_FILE}" >&2 || true
    exit 1
  fi

  sleep 1
  if [ "$i" -eq 30 ]; then
    echo "[start.sh] Xpra failed to become ready. Last log lines:" >&2
    tail -n 200 "${XPRA_LOG_FILE}" >&2 || true
    exit 1
  fi
done

XPRA_PID=$!

# Stream both logs to container stdout.
tail -n +1 -F "${XPRA_LOG_FILE}" "${APP_LOG_FILE}" &
TAIL_PID=$!

wait "${XPRA_PID}"
XPRA_EXIT_CODE=$?

kill "${TAIL_PID}" >/dev/null 2>&1 || true
exit "${XPRA_EXIT_CODE}"
