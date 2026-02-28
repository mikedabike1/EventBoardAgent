#!/usr/bin/env python3
"""Monthly newsletter cron job for Render.

Schedule: every Saturday at 08:00 UTC (render.yaml sets "0 8 * * 6").
This script exits early on any Saturday that is *not* the second-to-last
Saturday of the month, so only one real send happens per month.

Environment variables (all required on Render, optional for local testing):
  API_URL              Base URL of the EventBoard API, e.g. https://api.onrender.com
  ADMIN_SECRET         Shared secret for X-Admin-Secret header (optional)
  HEALTH_POLL_TIMEOUT  Max seconds to wait for the API to wake up (default 300)
"""

import calendar
import json
import os
import sys
import time
from datetime import date
from urllib.error import URLError
from urllib.request import Request, urlopen


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------


def is_second_last_saturday(today: date) -> bool:
    """Return True if *today* is the second-to-last Saturday of its month."""
    cal = calendar.monthcalendar(today.year, today.month)
    # calendar.SATURDAY == 5; monthcalendar rows are Mon-Sun, 0 means absent
    saturdays = [week[calendar.SATURDAY] for week in cal if week[calendar.SATURDAY] != 0]
    if len(saturdays) < 2:
        # Pathological month with fewer than 2 Saturdays — skip
        return False
    return today.day == saturdays[-2]


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only — no extra deps required)
# ---------------------------------------------------------------------------


def poll_health(api_url: str, max_wait_secs: int = 300) -> bool:
    """Poll GET /health until 200 OK or *max_wait_secs* is exhausted.

    Uses exponential backoff starting at 5 s, capped at 60 s.
    Returns True if the API responded with 200, False on timeout.
    """
    health_url = api_url.rstrip("/") + "/health"
    delay = 5
    elapsed = 0

    print(f"Polling {health_url} (timeout={max_wait_secs}s) …", flush=True)

    while elapsed < max_wait_secs:
        try:
            with urlopen(Request(health_url), timeout=10) as resp:
                if resp.status == 200:
                    print(f"  API is up after {elapsed}s.", flush=True)
                    return True
        except (URLError, OSError) as exc:
            print(f"  [{elapsed}s] health check failed: {exc}", flush=True)

        time.sleep(delay)
        elapsed += delay
        delay = min(delay * 2, 60)

    return False


def trigger_newsletter(api_url: str, admin_secret: str) -> dict:
    """POST /admin/newsletter and return the parsed JSON response."""
    url = api_url.rstrip("/") + "/admin/newsletter"
    headers = {"Content-Type": "application/json"}
    if admin_secret:
        headers["X-Admin-Secret"] = admin_secret

    req = Request(url, data=b"{}", headers=headers, method="POST")
    with urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    today = date.today()

    # ── 1. Date guard ──────────────────────────────────────────────────────
    if not is_second_last_saturday(today):
        print(
            f"Today is {today} ({today.strftime('%A')}) — "
            "not the second-to-last Saturday of the month. Nothing to do.",
            flush=True,
        )
        return 0

    print(f"Second-to-last Saturday confirmed ({today}). Running newsletter …", flush=True)

    # ── 2. Config ──────────────────────────────────────────────────────────
    api_url = os.environ.get("API_URL", "").rstrip("/")
    if not api_url:
        print("ERROR: API_URL environment variable is not set.", file=sys.stderr)
        return 1

    admin_secret = os.environ.get("ADMIN_SECRET", "")
    max_wait = int(os.environ.get("HEALTH_POLL_TIMEOUT", "300"))

    # ── 3. Wait for the API to wake up ─────────────────────────────────────
    if not poll_health(api_url, max_wait_secs=max_wait):
        print(
            f"ERROR: API did not respond within {max_wait}s. Aborting.",
            file=sys.stderr,
        )
        return 1

    # ── 4. Trigger newsletter ──────────────────────────────────────────────
    print("Triggering newsletter …", flush=True)
    result = trigger_newsletter(api_url, admin_secret)
    print(f"Newsletter result: {result}", flush=True)

    if result.get("errors", 0) > 0:
        print(
            f"WARNING: {result['errors']} email(s) failed to send.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
