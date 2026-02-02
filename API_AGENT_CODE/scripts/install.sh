#!/usr/bin/env bash
set -euo pipefail

# 1. [关键] 去除可能存在的 Windows 换行符，防止脚本无法运行
sed -i 's/\r$//' "$0" || true

cd /home/ubuntu/API_AGENT_CODE

# 2. 基础依赖 (建议暂时注释掉 apt-get 以排除干扰，如果需要请取消注释)
# sudo apt-get update -y
# sudo apt-get install -y python3 python3-venv python3-pip

# 3. 虚拟环境
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip

if [ -f requirements.txt ]; then
  python3 -m pip install -r requirements.txt
else
  python3 -m pip install fastapi "uvicorn[standard]"
fi

# 4. Systemd 服务
sudo cp -f systemd/api-agent.service /etc/systemd/system/api-agent.service
sudo systemctl daemon-reload
sudo systemctl enable api-agent.service

# ==========================================
# 核心修正：使用 sudo tee 强力写入
# ==========================================
echo "[config] Force generating config.ini..."

# 使用 sudo tee 确保即使权限有问题也能写入，并屏蔽输出
sudo tee config.ini > /dev/null <<EOF
[mysql]
host = api-agent-mysql.cl6uumosm1qb.us-east-2.rds.amazonaws.com
port = 3306
user = admin
password = 12345678
database = api_agent_db
pool_size = 5
EOF

# 打印一下结果，方便去 CodeDeploy 日志里看有没有写进去
echo "[config] Current content of config.ini:"
cat config.ini

# 5. 权限修正
sudo chown -R ubuntu:ubuntu /home/ubuntu/API_AGENT_CODE