#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/ubuntu/API_AGENT_CODE"
REPO_URL="git@github.com:brastli/API_AGENT_CODE.git"
BRANCH="main"

mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

if [ -d ".git" ]; then
  echo "[sync] repo exists, fetching..."
  git fetch --all --prune
  git pull --ff-only origin "${BRANCH}"

else
  echo "[sync] no repo, cloning..."
  rm -rf "$REPO_DIR"/*
  git clone --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
fi

# 密码文件储存在另外一个地方，
# 更新完以后再拷贝到原先的文件里
# 用 aws cli 去 fetch aws里的 secret key 