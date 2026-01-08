#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/ubuntu/API_AGENT_CODE"
cd "$APP_DIR"

# 依赖安装（可选，但建议保留）
python3 -m venv .venv || true
"$APP_DIR/.venv/bin/pip" install -U pip
if [ -f requirements.txt ]; then
  "$APP_DIR/.venv/bin/pip" install -r requirements.txt
fi

sudo systemctl restart api-agent
sudo systemctl is-active --quiet api-agent
echo "[post_deploy] api-agent restarted"
