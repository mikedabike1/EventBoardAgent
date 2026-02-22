#!/usr/bin/env bash
# start.sh — build the frontend and serve the whole app on your LAN.
# Usage:  bash start.sh [port]   (default port: 8000)
set -euo pipefail

PORT=${1:-8000}
ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── 1. Detect LAN IP ─────────────────────────────────────────────────────────
LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
if [[ -z "$LAN_IP" ]]; then
  LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi
if [[ -z "$LAN_IP" ]]; then
  echo "⚠  Could not detect LAN IP. You can still try http://$(hostname):$PORT"
  LAN_IP="$(hostname)"
fi

# ── 2. Build the frontend (relative base URL, no VITE_API_URL needed) ────────
echo "▶  Building frontend..."
cd "$ROOT/frontend"
npm run build --silent
echo "✓  Frontend built → frontend/dist/"

# ── 3. Install backend deps if needed ────────────────────────────────────────
cd "$ROOT"
if [[ ! -d ".venv" ]]; then
  echo "▶  Creating Python virtual environment..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r backend/requirements.txt

# ── 4. Import sample data if the DB is empty ─────────────────────────────────
if [[ ! -f "events.db" ]]; then
  echo "▶  Seeding database with sample events..."
  python3 -c "
import sys; sys.path.insert(0, '.')
from backend.database import create_tables, SessionLocal
from backend.importer import run_import
create_tables()
db = SessionLocal()
run_import(db)
db.close()
"
fi

# ── 5. Launch ─────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  App running — open on your phone:"
echo ""
echo "    http://${LAN_IP}:${PORT}"
echo ""
echo "  (phone and laptop must be on the same WiFi)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$ROOT"
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"
