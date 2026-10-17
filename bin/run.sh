#!/usr/bin/env bash
# Canonical run command for this app. Safe + idempotent:
#   - creates the venv + installs deps ONLY if missing (no network needed on normal restarts)
#   - loads .env (PORT, DATABASE_URL, SECRET_KEY, ...)
#   - exec's uvicorn (systemd supervises/restarts/boot-persists)
# Run by hand:  bin/run.sh      Under systemd:  app@<dir>.service calls this.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/uvicorn ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
[ -f .env ] && { set -a; . ./.env; set +a; }
exec .venv/bin/uvicorn asgi:app --host 127.0.0.1 --port "${PORT:-8000}"
