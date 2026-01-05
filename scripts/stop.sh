#!/usr/bin/env bash
set -euo pipefail

# 如果服务不存在或没启动，不要让部署失败
systemctl stop api-agent.service || true
