#!/usr/bin/env bash
set -euo pipefail

systemctl restart api-agent.service
systemctl --no-pager --full status api-agent.service || true
