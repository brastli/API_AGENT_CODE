#!/usr/bin/env bash
set -euo pipefail

SERVICE="api-agent"
RUN_DIR="/home/ubuntu/API_AGENT_CODE"

# 这个脚本在 .../API_AGENT_CODE/scripts/post_deploy.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"   # => .../API_AGENT_CODE

echo "[post_deploy] bundle=${BUNDLE_DIR}"
echo "[post_deploy] run_dir=${RUN_DIR}"

# 先停服务，避免边覆盖边运行
systemctl stop "${SERVICE}" || true

# 同步代码（排除 .venv/.git 等）
rsync -a --delete \
  --exclude '.venv' \
  --exclude '.git' \
  --exclude '__pycache__' \
  "${BUNDLE_DIR}/" "${RUN_DIR}/"

chown -R ubuntu:ubuntu "${RUN_DIR}"

# 如需跟随代码更新 unit，就取消注释：
# cp -f "${RUN_DIR}/systemd/api-agent.service" /etc/systemd/system/api-agent.service

systemctl daemon-reload
systemctl start "${SERVICE}"
systemctl is-active --quiet "${SERVICE}"
echo "[post_deploy] done"


date -Is | sudo tee /home/ubuntu/deploy/api_agent/DEPLOYED_AT >/dev/null
sudo sha256sum /home/ubuntu/deploy/api_agent/API_AGENT_CODE/main.py | sudo tee /home/ubuntu/deploy/api_agent/MAIN_SHA256 >/dev/null
