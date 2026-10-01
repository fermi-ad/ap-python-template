#!/bin/bash -l
set -Eeuo pipefail

source /usr/local/bin/create-workspace.sh

exec python -m ap_python_starter_kit.main
