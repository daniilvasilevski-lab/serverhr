#!/usr/bin/env bash
set -euo pipefail

# Simple local setup helper for running the app without Docker.
# - Creates/activates a virtual environment
# - Verifies connectivity to the package index (PyPI or custom mirror)
# - Installs Python dependencies from requirements.txt

PYTHON_BIN="${PYTHON:-python3}"
VENV_PATH="${VENV_PATH:-.venv}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "[ERROR] ${PYTHON_BIN} not found. Install Python 3.11+ or set PYTHON=/path/to/python." >&2
  exit 1
fi

# 1) Create venv if missing
if [ ! -d "${VENV_PATH}" ]; then
  echo "[INFO] Creating virtual environment at ${VENV_PATH}"
  "${PYTHON_BIN}" -m venv "${VENV_PATH}"
fi

# 2) Activate venv
# shellcheck disable=SC1090
source "${VENV_PATH}/bin/activate"

# 3) Upgrade pip tooling inside the venv
python -m pip install --upgrade pip setuptools wheel

# 4) Quick network check to the package index (helps detect proxy/firewall issues early)
python - <<'PY'
import os
import sys
import urllib.error
import urllib.request

index = os.environ.get("PIP_INDEX_URL", "https://pypi.org/simple").rstrip("/")
probe = f"{index}/fastapi/"

try:
    with urllib.request.urlopen(probe, timeout=10) as resp:
        ok = 200 <= resp.status < 400
        if ok:
            print(f"[OK] Package index reachable: {probe} (status {resp.status})")
        else:
            print(f"[WARNING] Package index responded with status {resp.status}: {probe}")
except urllib.error.URLError as exc:
    print(f"[ERROR] Cannot reach package index {probe}: {exc}")
    print("       If you use a proxy, export https_proxy/http_proxy or set PIP_INDEX_URL to your mirror.")
    print("       To bypass a corporate proxy that blocks CONNECT, try unsetting http_proxy/https_proxy.")
    sys.exit(1)
PY

# 5) Install dependencies
python -m pip install --default-timeout=120 -r requirements.txt

echo "[DONE] Dependencies installed. Activate the venv (source ${VENV_PATH}/bin/activate) and run:"
echo "       uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
