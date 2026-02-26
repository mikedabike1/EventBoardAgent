#!/usr/bin/env bash
# start.sh — build the frontend and serve the whole app on your LAN.
# Usage:  bash start.sh [port]   (default port: 8000)
set -euo pipefail

PORT=${1:-8000}
ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── 1. Detect LAN IP ─────────────────────────────────────────────────────────
# Try Linux-style, then macOS-style, then fall back to hostname
LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}' || true)
if [[ -z "$LAN_IP" ]]; then
  LAN_IP=$(ipconfig getifaddr en0 2>/dev/null || true)
fi
if [[ -z "$LAN_IP" ]]; then
  LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || true)
fi
if [[ -z "$LAN_IP" ]]; then
  echo "⚠  Could not detect LAN IP. You can still try http://$(hostname):$PORT"
  LAN_IP="$(hostname)"
fi

# ── 2. Build the frontend (relative base URL, no VITE_API_URL needed) ────────
if [[ ! -d "$ROOT/frontend/dist" ]]; then
  echo "▶  Building frontend..."
  cd "$ROOT/frontend"
  npm install --include=dev
  npm run build --silent
  echo "✓  Frontend built → frontend/dist/"
else
  echo "✓  Frontend dist already present, skipping build."
fi

# ── 3. Sync backend deps with uv ─────────────────────────────────────────────
cd "$ROOT"
echo "▶  Syncing Python dependencies..."
uv sync

# ── 4. Import sample data if the DB is empty ─────────────────────────────────
if [[ ! -f "events.db" ]]; then
  echo "▶  Seeding database with sample events..."
  uv run python -c "
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
uv run uvicorn backend.main:app --host 0.0.0.0 --port "$PORT"
