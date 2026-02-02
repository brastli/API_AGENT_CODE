#!/usr/bin/env bash
set -e

# 如果服务器上存在 config.ini，先把它备份到临时目录
if [ -f /home/ubuntu/API_AGENT_CODE/config.ini ]; then
    echo "[backup] Found existing config.ini, backing up..."
    cp /home/ubuntu/API_AGENT_CODE/config.ini /tmp/config.ini.bak
else
    echo "[backup] No config.ini found to backup."
fi