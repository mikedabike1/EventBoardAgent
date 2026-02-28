# Preview Email Download Endpoint Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `GET /admin/preview-email` — a browser-downloadable HTML email showing all events for the current calendar month.

**Architecture:** Add a `build_preview_email(events)` function to `newsletter.py` (no Subscriber needed), then wire a new admin endpoint in `main.py` that queries the current month's events and returns the HTML with `Content-Disposition: attachment`.

**Tech Stack:** FastAPI, SQLAlchemy, Python `calendar` stdlib, pytest + httpx TestClient

---

### Task 1: Create a new branch

**Step 1: Create and switch to the feature branch**

```bash
git checkout -b feat/preview-email-endpoint
```

Expected: branch created and checked out.

---

### Task 2: Write `build_preview_email` in `newsletter.py` (TDD)

**Files:**
- Modify: `backend/newsletter.py`
- Test: `backend/tests/test_preview_email.py`

**Step 1: Create the test file with failing tests**

Create `backend/tests/test_preview_email.py`:

```python
"""Tests for build_preview_email and the /admin/preview-email endpoint."""

from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models  # noqa: F401 — registers ORM classes with Base
from backend.database import Base, get_db
from backend.main import app
from backend.newsletter import build_preview_email


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_event(
    title="Friday Night 40K",
    game_name="Warhammer 40,000",
    location_name="Game Vault",
    date_val=date(2026, 2, 15),
    start_time="18:00",
    description="Come play!",
):
    event = MagicMock()
    event.title = title
    event.date = date_val
    event.start_time = start_time
    event.description = description
    event.game_system.name = game_name
    event.location.name = location_name
    return event


# ---------------------------------------------------------------------------
# build_preview_email — unit tests
# ---------------------------------------------------------------------------


class TestBuildPreviewEmail:
    def test_returns_html_string(self):
        html = build_preview_email([_mock_event()])
        assert isinstance(html, str)
        assert html.strip().startswith("<!DOCTYPE html>")

    def test_contains_heading(self):
        html = build_preview_email([_mock_event()])
        assert "All Events This Month" in html

    def test_includes_event_title(self):
        html = build_preview_email([_mock_event(title="Saturday Skirmish")])
        assert "Saturday Skirmish" in html

    def test_includes_game_system(self):
        html = build_preview_email([_mock_event(game_name="Age of Sigmar")])
        assert "Age of Sigmar" in html

    def test_includes_location(self):
        html = build_preview_email([_mock_event(location_name="Dragon's Den")])
        assert "Dragon&#x27;s Den" in html  # html.escape applied

    def test_includes_date(self):
        html = build_preview_email([_mock_event(date_val=date(2026, 2, 15))])
        assert "Feb 15 2026" in html

    def test_empty_events_still_returns_html(self):
        html = build_preview_email([])
        assert "<table" in html
        assert "<tbody>" in html

    def test_missing_start_time_shows_tbd(self):
        html = build_preview_email([_mock_event(start_time=None)])
        assert "TBD" in html

    def test_multiple_events_all_appear(self):
        events = [
            _mock_event(title="Event Alpha"),
            _mock_event(title="Event Beta"),
        ]
        html = build_preview_email(events)
        assert "Event Alpha" in html
        assert "Event Beta" in html
```

**Step 2: Run to confirm tests fail**

```bash
uv run pytest backend/tests/test_preview_email.py::TestBuildPreviewEmail -v
```

Expected: `ImportError` or `AttributeError` — `build_preview_email` does not exist yet.

**Step 3: Implement `build_preview_email` in `backend/newsletter.py`**

Add this function directly after `build_html_email` (before `send_email`):

```python
def build_preview_email(events: list[Event]) -> str:
    rows = ""
    for e in events:
        date_str = e.date.strftime("%a, %b %d %Y")
        time_str = escape(e.start_time or "TBD")
        game_name = escape(e.game_system.name)
        location_name = escape(e.location.name)
        title = escape(e.title)
        description = escape(e.description or "")
        rows += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
          <td style="padding: 10px 12px; white-space: nowrap;">{date_str}</td>
          <td style="padding: 10px 12px; white-space: nowrap;">{time_str}</td>
          <td style="padding: 10px 12px; font-weight: 600; color: #7c3aed;">{game_name}</td>
          <td style="padding: 10px 12px;">{location_name}</td>
          <td style="padding: 10px 12px; font-weight: 500;">{title}</td>
          <td style="padding: 10px 12px; color: #6b7280; font-size: 13px;">{description}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>All Events This Month</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
             background: #f9fafb; margin: 0; padding: 32px 16px;">
  <div style="max-width: 700px; margin: 0 auto; background: white;
              border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <div style="background: #7c3aed; padding: 32px; text-align: center;">
      <h1 style="color: white; margin: 0; font-size: 24px;">&#127922; Wargame Event Finder</h1>
      <p style="color: #ddd6fe; margin: 8px 0 0; font-size: 15px;">All Events This Month</p>
    </div>
    <div style="padding: 32px;">
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
          <thead>
            <tr style="background: #f3f4f6; text-align: left;">
              <th style="padding: 10px 12px; color: #6b7280; font-weight: 600;">Date</th>
              <th style="padding: 10px 12px; color: #6b7280; font-weight: 600;">Time</th>
              <th style="padding: 10px 12px; color: #6b7280; font-weight: 600;">Game</th>
              <th style="padding: 10px 12px; color: #6b7280; font-weight: 600;">Location</th>
              <th style="padding: 10px 12px; color: #6b7280; font-weight: 600;">Event</th>
              <th style="padding: 10px 12px; color: #6b7280; font-weight: 600;">Details</th>
            </tr>
          </thead>
          <tbody>{rows}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</body>
</html>"""
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest backend/tests/test_preview_email.py::TestBuildPreviewEmail -v
```

Expected: all 9 tests PASS.

**Step 5: Commit**

```bash
git add backend/newsletter.py backend/tests/test_preview_email.py
git commit -m "feat: add build_preview_email function to newsletter"
```

---

### Task 3: Add `GET /admin/preview-email` endpoint (TDD)

**Files:**
- Modify: `backend/main.py`
- Modify: `backend/tests/test_preview_email.py` (append new test class)

**Step 1: Add endpoint tests to `backend/tests/test_preview_email.py`**

Append this class to the bottom of the file:

```python
# ---------------------------------------------------------------------------
# /admin/preview-email endpoint — integration tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestPreviewEmailEndpoint:
    def test_returns_200(self, client):
        response = client.get("/admin/preview-email")
        assert response.status_code == 200

    def test_content_type_is_html(self, client):
        response = client.get("/admin/preview-email")
        assert "text/html" in response.headers["content-type"]

    def test_content_disposition_is_attachment(self, client):
        response = client.get("/admin/preview-email")
        disposition = response.headers["content-disposition"]
        assert disposition.startswith("attachment")

    def test_filename_contains_current_month(self, client):
        from datetime import date

        today = date.today()
        expected_slug = today.strftime("%Y-%m")
        disposition = response = client.get("/admin/preview-email").headers[
            "content-disposition"
        ]
        assert expected_slug in disposition

    def test_body_is_valid_html(self, client):
        response = client.get("/admin/preview-email")
        assert "<!DOCTYPE html>" in response.text
        assert "All Events This Month" in response.text
```

**Step 2: Run to confirm tests fail**

```bash
uv run pytest backend/tests/test_preview_email.py::TestPreviewEmailEndpoint -v
```

Expected: 404 Not Found errors — endpoint not yet registered.

**Step 3: Add the endpoint to `backend/main.py`**

Add these imports near the top of the file (after the existing `from datetime import date` line):

```python
import calendar

from fastapi.responses import Response
```

Add this endpoint in the `# Admin` section of `main.py`, after the `trigger_newsletter` endpoint:

```python
@app.get("/admin/preview-email", tags=["admin"])
def preview_email(db: Session = Depends(get_db)):
    today = date.today()
    date_from = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    date_to = today.replace(day=last_day)
    events = crud.get_events(db, date_from=date_from, date_to=date_to)
    html = build_preview_email(events)
    filename = f"preview-email-{today.strftime('%Y-%m')}.html"
    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
```

Also add `build_preview_email` to the import from `newsletter`:

```python
from .newsletter import build_preview_email, run_newsletter
```

**Step 4: Run tests to verify they pass**

```bash
uv run pytest backend/tests/test_preview_email.py::TestPreviewEmailEndpoint -v
```

Expected: all 5 tests PASS.

**Step 5: Run the full test suite**

```bash
uv run pytest backend/tests/ -v
```

Expected: all tests PASS.

**Step 6: Lint**

```bash
uv run ruff check backend/
uv run ruff format --check backend/
```

Expected: no errors. If formatting errors: `uv run ruff format backend/`

**Step 7: Commit**

```bash
git add backend/main.py backend/tests/test_preview_email.py
git commit -m "feat: add GET /admin/preview-email download endpoint"
```
