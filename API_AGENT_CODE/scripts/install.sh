#!/usr/bin/env bash
set -euo pipefail

cd /home/ubuntu/API_AGENT_CODE

# 基础依赖（Ubuntu）
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip

# venv & deps
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip

if [ -f requirements.txt ]; then
  python3 -m pip install -r requirements.txt
else
  # 没有 requirements.txt 就至少保证 fastapi/uvicorn 有
  python3 -m pip install fastapi "uvicorn[standard]"
fi

# systemd unit
sudo cp -f systemd/api-agent.service /etc/systemd/system/api-agent.service
sudo systemctl daemon-reload
sudo systemctl enable api-agent.service

# [新增] 恢复 config.ini (从 /tmp 备份目录移回)
# 这一步是为了防止 CodeDeploy 覆盖文件时导致配置丢失
if [ -f /tmp/config.ini.bak ]; then
    echo "[restore] Restoring config.ini from backup..."
    mv /tmp/config.ini.bak /home/ubuntu/API_AGENT_CODE/config.ini
fi

# [新增] 必须修改权限，否则 ubuntu 用户无法运行服务
# 这一步必须在文件恢复之后执行，确保 config.ini 的归属权也是 ubuntu
sudo chown -R ubuntu:ubuntu /home/ubuntu/API_AGENT_CODE