#!/usr/bin/env bash
set -euo pipefail

cd /home/ubuntu/API_AGENT_CODE

# 1. 基础依赖
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip

# 2. 虚拟环境
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip

if [ -f requirements.txt ]; then
  python3 -m pip install -r requirements.txt
else
  python3 -m pip install fastapi "uvicorn[standard]"
fi

# 3. Systemd 服务
sudo cp -f systemd/api-agent.service /etc/systemd/system/api-agent.service
sudo systemctl daemon-reload
sudo systemctl enable api-agent.service

# ==========================================
# 核心修正：只写入，不还原！
# ==========================================
echo "[config] Force generating config.ini..."

# 无论之前文件是什么，直接覆盖写入正确内容
cat <<EOF > config.ini
[mysql]
host = api-agent-mysql.cl6uumosm1qb.us-east-2.rds.amazonaws.com
port = 3306
user = admin
password = 12345678
database = api_agent_db
pool_size = 5
EOF

# 4. 权限修正 (必须在生成文件之后)
sudo chown -R ubuntu:ubuntu /home/ubuntu/API_AGENT_CODE