#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/ubuntu/API_AGENT_CODE"
cd "$APP_DIR"

python3 -m venv .venv || true
"$APP_DIR/.venv/bin/pip" install -U pip
if [ -f requirements.txt ]; then
  "$APP_DIR/.venv/bin/pip" install -r requirements.txt
fi

sudo systemctl restart api-agent
echo "[post_deploy] restarted api-agent"
