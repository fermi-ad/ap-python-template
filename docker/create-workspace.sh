if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "Storage startup error: source create-workspace.sh instead of executing it" >&2
  exit 1
fi

STORAGE_ROOT=/mnt/storage

if ! command -v mountpoint >/dev/null 2>&1; then
  echo "Storage startup error: mountpoint is not installed" >&2
  exit 1
fi

if ! mountpoint -q -- "$STORAGE_ROOT"; then
  echo "Storage startup error: $STORAGE_ROOT is not a mounted volume" >&2
  exit 1
fi

APP_STORAGE="$STORAGE_ROOT/ap-python-starter-kit"
if ! mkdir -p -- "$APP_STORAGE"; then
  echo "Storage startup error: cannot create $APP_STORAGE" >&2
  exit 1
fi

# Test an actual write; checking permissions alone may not be sufficient.
if ! probe=$(mktemp "$APP_STORAGE/.write-test.XXXXXX"); then
  echo "Storage startup error: $APP_STORAGE is not writable" >&2
  exit 1
fi
rm -- "$probe"

DATE=$(date -u +"%Y%m%d_%H%M%S_${HOSTNAME}")
JOB_DIR="$APP_STORAGE/$DATE"
if ! mkdir -p -- "$JOB_DIR"; then
  echo "Storage startup error: cannot create $JOB_DIR" >&2
  exit 1
fi

if ! cd -- "$JOB_DIR"; then
  echo "Storage startup error: cannot change directory to $JOB_DIR" >&2
  exit 1
fi
