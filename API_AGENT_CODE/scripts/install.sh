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

# systemd unit（如果你希望跟随代码版本更新 unit）
sudo cp -f systemd/api-agent.service /etc/systemd/system/api-agent.service
sudo systemctl daemon-reload
sudo systemctl enable api-agent.service
