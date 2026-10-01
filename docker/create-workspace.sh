#!/bin/bash

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

DATE=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
JOB_DIR="$APP_STORAGE/$DATE"
mkdir -p -- "$JOB_DIR"
cd -- "$JOB_DIR"
