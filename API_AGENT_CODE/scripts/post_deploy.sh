#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/home/ubuntu/deploy/api_agent"
APP_DIR="${TARGET_DIR}/API_AGENT_CODE"
SERVICE="api-agent"

echo "[post_deploy] start: $(date -Is)"
echo "[post_deploy] target=${TARGET_DIR}"

# 1) 绝对禁止部署目录存在 .venv（避免覆盖运行中 python -> text file busy）
if [[ -d "${TARGET_DIR}/.venv" ]]; then
  echo "[post_deploy] removing ${TARGET_DIR}/.venv"
  rm -rf "${TARGET_DIR}/.venv"
fi

# 2) 确保目录权限一致（避免后续写文件/日志失败）
echo "[post_deploy] chown ${TARGET_DIR}"
chown -R ubuntu:ubuntu "${TARGET_DIR}"

# 3) 预检查：main.py 是否存在（可按你的入口调整）
if [[ ! -f "${APP_DIR}/main.py" ]]; then
  echo "[post_deploy] ERROR: ${APP_DIR}/main.py not found"
  exit 1
fi

# 4) 重启服务（更稳：先 stop 再 start）
echo "[post_deploy] restarting ${SERVICE}"
systemctl daemon-reload
systemctl stop "${SERVICE}" || true
systemctl start "${SERVICE}"

# 5) 健康检查：服务必须是 active
systemctl is-active --quiet "${SERVICE}"
echo "[post_deploy] done: $(date -Is)"
