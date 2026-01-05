#!/usr/bin/env bash
set -euo pipefail

# 等待服务起来（最多 30 秒）
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null; then
    echo "[validate] health check OK"
    exit 0
  fi
  sleep 1
done

echo "[validate] health check FAILED"
exit 1
