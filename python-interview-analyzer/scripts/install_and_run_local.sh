#!/usr/bin/env bash
set -euo pipefail

# One-shot helper to install dependencies (via virtual env) and run the FastAPI server
# with all logs and status output in this terminal.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

VENV_PATH="${VENV_PATH:-.venv}"
PYTHON_BIN="${PYTHON:-python3}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-info}"

INFO="\033[1;34m[INFO]\033[0m"
OK="\033[0;32m[OK]\033[0m"
WARN="\033[1;33m[WARN]\033[0m"
ERR="\033[0;31m[ERR]\033[0m"

msg() { printf "%b %s\n" "$1" "$2"; }

msg "$INFO" "Working directory: $ROOT_DIR"

# Ensure .env exists
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    msg "$WARN" ".env not found. Creating from .env.example"
    cp .env.example .env
    msg "$WARN" "Please edit .env and set OPENAI_API_KEY before starting."
  else
    msg "$ERR" ".env file is missing and .env.example not found."
    exit 1
  fi
fi

# Install dependencies (and create venv) using the setup helper
msg "$INFO" "Installing dependencies via scripts/setup_local.sh (venv: $VENV_PATH)"
VENV_PATH="$VENV_PATH" PYTHON="$PYTHON_BIN" bash scripts/setup_local.sh

# Activate venv for the rest of the session
# shellcheck disable=SC1090
source "$VENV_PATH/bin/activate"
msg "$OK" "Virtual environment activated ($VENV_PATH)"

# Quick system check
msg "$INFO" "Running pre-flight system checks"
if ! python check_system.py; then
  msg "$ERR" "System checks failed. See messages above."
  exit 1
fi

msg "$OK" "All checks passed. Launching server with live logs..."
msg "$INFO" "API docs: http://localhost:${PORT}/docs"
msg "$INFO" "Health:   http://localhost:${PORT}/health"
msg "$INFO" "Press Ctrl+C to stop. Logs will stay in this terminal."

# Run uvicorn in the foreground so status/logs remain in this terminal
exec uvicorn app.main:app \
  --host "$HOST" \
  --port "$PORT" \
  --log-level "$LOG_LEVEL" \
  --reload
