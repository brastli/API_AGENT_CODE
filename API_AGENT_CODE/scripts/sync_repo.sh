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
  git reset --hard "origin/${BRANCH}"
else
  echo "[sync] no repo, cloning..."
  rm -rf "$REPO_DIR"/*
  git clone --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
fi
