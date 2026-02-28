# Preview Email Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign `build_preview_email` to produce a branded, calendar-first monthly newsletter with clickable banner, game-system-colored calendar grid, CST-labeled times, no-year dates, and per-event source links.

**Architecture:** Three layered tasks: (1) signature plumbing + env var, (2) new `_build_calendar_html` helper, (3) full `build_preview_email` body update. All changes in `backend/newsletter.py` + `backend/main.py` + `.env.example`. Tests updated throughout with TDD.

**Tech Stack:** Python `calendar` stdlib, `html.escape`, inline-style HTML, pytest + MagicMock

---

### Task 1: Add `website_url` parameter + WEBSITE_URL env var

**Files:**
- Modify: `backend/newsletter.py:88`
- Modify: `backend/main.py`
- Modify: `.env.example`
- Modify: `backend/tests/test_preview_email.py`

**Context:** `build_preview_email` currently takes only `events`. We need to add `website_url: str` and wire it from an env var. The `_mock_event` helper also needs `game_system_id` and `source_url` for upcoming tasks — add them now so we don't touch the helper again.

**Step 1: Update `_mock_event` in the test file**

In `backend/tests/test_preview_email.py`, replace the existing `_mock_event` helper with this version (adds `game_system_id` and `source_url` with defaults, no existing tests break):

```python
def _mock_event(
    title="Friday Night 40K",
    game_name="Warhammer 40,000",
    game_system_id=1,
    location_name="Game Vault",
    date_val=date(2026, 2, 15),
    start_time="18:00",
    description="Come play!",
    source_url="https://example.com/event",
):
    event = MagicMock()
    event.title = title
    event.date = date_val
    event.start_time = start_time
    event.description = description
    event.game_system.name = game_name
    event.game_system.id = game_system_id
    event.location.name = location_name
    event.source_url = source_url
    return event
```

**Step 2: Add `website_url` to all `build_preview_email` calls in tests**

In `backend/tests/test_preview_email.py`, update every call to `build_preview_email(...)` in `TestBuildPreviewEmail` to pass `website_url="https://test.example.com"`. There are 9 calls total — find each `build_preview_email([` and add the keyword argument. Example:

```python
# Before
html = build_preview_email([_mock_event()])
# After
html = build_preview_email([_mock_event()], website_url="https://test.example.com")
```

**Step 3: Run tests to confirm they still pass (before touching newsletter.py)**

```bash
cd /Users/mikealtschwager/Git/EventBoardAgent && uv run pytest backend/tests/test_preview_email.py::TestBuildPreviewEmail -v
```

Expected: 9 PASS (unchanged behavior — `website_url` not in signature yet, but that's fine; we're just verifying the mock update didn't break anything before we change the signature).

Actually — this will FAIL at import time because `build_preview_email` doesn't accept `website_url` yet. That's the expected TDD red state. Continue to Step 4.

**Step 4: Update `build_preview_email` signature in `backend/newsletter.py`**

Change line 88 from:
```python
def build_preview_email(events: list[Event]) -> str:
```
to:
```python
def build_preview_email(events: list[Event], website_url: str) -> str:
```

The body is unchanged for now.

**Step 5: Add `WEBSITE_URL` to `.env.example`**

Append to `.env.example`:
```
# Public URL of the frontend (used in email links)
WEBSITE_URL=http://localhost:8000/
```

**Step 6: Add `import os` and `_WEBSITE_URL` to `backend/main.py`**

`main.py` does not currently import `os`. Add `import os` to the stdlib imports at the top.

Then, after the `load_dotenv()` call (line 19), add:
```python
_WEBSITE_URL = os.getenv("WEBSITE_URL", "http://localhost:8000/")
```

**Step 7: Pass `website_url` in the `preview_email` endpoint in `backend/main.py`**

Find the `preview_email` endpoint. Change:
```python
html = build_preview_email(events)
```
to:
```python
html = build_preview_email(events, website_url=_WEBSITE_URL)
```

**Step 8: Run tests to confirm green**

```bash
cd /Users/mikealtschwager/Git/EventBoardAgent && uv run pytest backend/tests/ -v
```

Expected: 31 PASS.

**Step 9: Lint**

```bash
uv run ruff check backend/ && uv run ruff format --check backend/
```

Expected: no errors. If format issues: `uv run ruff format backend/`

**Step 10: Commit**

```bash
git add backend/newsletter.py backend/main.py backend/tests/test_preview_email.py .env.example
git commit -m "feat: add website_url param to build_preview_email, wire WEBSITE_URL env var

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Add `_build_calendar_html` helper (TDD)

**Files:**
- Modify: `backend/newsletter.py`
- Modify: `backend/tests/test_preview_email.py`

**Context:** This is a new private helper that generates an email-safe inline-style HTML calendar grid for a given year/month, mirroring `frontend/src/components/CalendarView.jsx`. Game system pills use 7 hardcoded hex color pairs matching the frontend's Tailwind classes.

**Step 1: Add failing tests for `_build_calendar_html`**

Append this new test class to `backend/tests/test_preview_email.py`, after `TestBuildPreviewEmail` and before the integration test section:

```python
# ---------------------------------------------------------------------------
# _build_calendar_html — unit tests
# ---------------------------------------------------------------------------


class TestBuildCalendarHtml:
    def _call(self, events, year=2026, month=2):
        from backend.newsletter import _build_calendar_html
        return _build_calendar_html(events, year, month)

    def test_returns_html_string(self):
        html = self._call([])
        assert isinstance(html, str)
        assert "<table" in html

    def test_contains_day_of_week_headers(self):
        html = self._call([])
        for day in ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"):
            assert day in html

    def test_contains_month_label(self):
        html = self._call([], year=2026, month=2)
        assert "February 2026" in html

    def test_event_title_appears_in_correct_cell(self):
        event = _mock_event(title="Big Battle", date_val=date(2026, 2, 15))
        html = self._call([event], year=2026, month=2)
        assert "Big Battle" in html

    def test_overflow_shows_more_label(self):
        events = [
            _mock_event(title=f"Event {i}", date_val=date(2026, 2, 15), game_system_id=i + 1)
            for i in range(5)
        ]
        html = self._call(events, year=2026, month=2)
        assert "+2 more" in html

    def test_legend_shows_game_system_name(self):
        event = _mock_event(game_name="Kings of War", date_val=date(2026, 2, 15))
        html = self._call([event], year=2026, month=2)
        assert "Kings of War" in html

    def test_empty_month_renders_grid(self):
        html = self._call([], year=2026, month=2)
        # February 2026 starts on Sunday (0 blank cells) and has 28 days = 4 rows
        assert html.count("<tr>") >= 5  # 1 header row + 4 week rows

    def test_events_from_other_months_excluded(self):
        event_march = _mock_event(title="March Event", date_val=date(2026, 3, 1))
        html = self._call([event_march], year=2026, month=2)
        # The cell for March 1 is not in the February grid
        assert "March Event" not in html
```

**Step 2: Run to confirm failure**

```bash
cd /Users/mikealtschwager/Git/EventBoardAgent && uv run pytest backend/tests/test_preview_email.py::TestBuildCalendarHtml -v
```

Expected: `ImportError: cannot import name '_build_calendar_html'`

**Step 3: Implement `_build_calendar_html` in `backend/newsletter.py`**

Add these items to `newsletter.py`:

First, update the imports at the top of the file. After `import os`, add:
```python
import calendar as _cal
from datetime import date as _date
```

After the existing `_EMAIL_FROM` constant, add the pill colors constant:
```python
# Pill color pairs (background, text) — mirror CalendarView.jsx PILL_COLORS
_PILL_COLORS = [
    ("#ede9fe", "#5b21b6"),  # purple-100 / purple-800
    ("#e0e7ff", "#3730a3"),  # indigo-100 / indigo-800
    ("#e0f2fe", "#075985"),  # sky-100 / sky-800
    ("#d1fae5", "#065f46"),  # emerald-100 / emerald-800
    ("#fef3c7", "#92400e"),  # amber-100 / amber-800
    ("#ffe4e6", "#9f1239"),  # rose-100 / rose-800
    ("#ccfbf1", "#115e59"),  # teal-100 / teal-800
]
```

Then add the helper function just before `build_html_email`:

```python
def _build_calendar_html(events: list[Event], year: int, month: int) -> str:
    """Return an inline-style HTML calendar grid for the given year/month."""
    today_str = _date.today().isoformat()

    # Group events by ISO date string; collect unique game systems for legend
    events_by_date: dict[str, list[Event]] = {}
    seen_gs: dict[int, str] = {}
    for e in events:
        d = str(e.date)  # date object → "YYYY-MM-DD"
        if d not in events_by_date:
            events_by_date[d] = []
        events_by_date[d].append(e)
        if e.game_system.id not in seen_gs:
            seen_gs[e.game_system.id] = e.game_system.name

    # Build grid cells (Sunday-first)
    first_dow_mon = _cal.monthrange(year, month)[0]   # Monday=0
    first_dow_sun = (first_dow_mon + 1) % 7           # Sunday=0
    days_in_month = _cal.monthrange(year, month)[1]
    cells: list[int | None] = [None] * first_dow_sun + list(range(1, days_in_month + 1))
    while len(cells) % 7:
        cells.append(None)

    # Day-of-week header row
    day_headers = "".join(
        f'<th style="padding:8px 4px;text-align:center;color:#9ca3af;font-size:11px;'
        f'font-weight:600;text-transform:uppercase;letter-spacing:0.05em;'
        f'border-bottom:1px solid #f3f4f6;">{d}</th>'
        for d in ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
    )

    # Build week rows
    rows_html = ""
    for i in range(0, len(cells), 7):
        rows_html += "<tr>"
        for day in cells[i : i + 7]:
            if day is None:
                rows_html += (
                    '<td style="border-right:1px solid #f3f4f6;border-bottom:1px solid #f3f4f6;'
                    'background:#f9fafb;padding:6px;min-width:0;height:80px;"></td>'
                )
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                day_events = events_by_date.get(date_str, [])
                is_today = date_str == today_str
                num_style = (
                    "display:inline-flex;align-items:center;justify-content:center;"
                    "width:22px;height:22px;border-radius:50%;font-size:11px;font-weight:600;"
                    + ("background:#7c3aed;color:white;" if is_today else "color:#374151;")
                )
                pills = ""
                for e in day_events[:3]:
                    bg, fg = _PILL_COLORS[(e.game_system.id - 1) % len(_PILL_COLORS)]
                    pills += (
                        f'<div style="font-size:11px;padding:1px 5px;border-radius:3px;'
                        f'font-weight:500;overflow:hidden;white-space:nowrap;'
                        f'text-overflow:ellipsis;margin-bottom:2px;'
                        f'background:{bg};color:{fg};">{escape(e.title)}</div>'
                    )
                overflow = len(day_events) - 3
                if overflow > 0:
                    pills += (
                        f'<div style="font-size:11px;color:#9ca3af;padding-left:4px;">'
                        f'+{overflow} more</div>'
                    )
                rows_html += (
                    f'<td style="vertical-align:top;padding:6px;'
                    f'border-right:1px solid #f3f4f6;border-bottom:1px solid #f3f4f6;'
                    f'min-width:0;height:80px;">'
                    f'<div style="text-align:right;margin-bottom:4px;">'
                    f'<span style="{num_style}">{day}</span></div>'
                    f'{pills}</td>'
                )
        rows_html += "</tr>"

    # Legend
    legend = "".join(
        f'<span style="font-size:12px;padding:2px 10px;border-radius:9999px;'
        f'font-weight:500;margin-right:6px;'
        f'background:{_PILL_COLORS[(gs_id - 1) % len(_PILL_COLORS)][0]};'
        f'color:{_PILL_COLORS[(gs_id - 1) % len(_PILL_COLORS)][1]};">'
        f'{escape(gs_name)}</span>'
        for gs_id, gs_name in seen_gs.items()
    )
    legend_block = (
        f'<div style="margin-top:10px;line-height:2;">{legend}</div>' if legend else ""
    )

    month_name = _date(year, month, 1).strftime("%B %Y")
    return (
        f'<div style="margin-bottom:24px;">'
        f'<h2 style="font-size:15px;font-weight:600;color:#374151;margin:0 0 12px 0;">'
        f'{month_name}</h2>'
        f'<div style="border-radius:12px;overflow:hidden;border:1px solid #f3f4f6;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
        f'<table style="width:100%;border-collapse:collapse;table-layout:fixed;background:white;">'
        f'<thead><tr>{day_headers}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>'
        f'{legend_block}'
        f'</div>'
    )
```

**Step 4: Run calendar tests to confirm they pass**

```bash
cd /Users/mikealtschwager/Git/EventBoardAgent && uv run pytest backend/tests/test_preview_email.py::TestBuildCalendarHtml -v
```

Expected: 8 PASS.

**Step 5: Run full test suite**

```bash
uv run pytest backend/tests/ -v
```

Expected: 39 PASS.

**Step 6: Lint**

```bash
uv run ruff check backend/ && uv run ruff format --check backend/
```

Expected: no errors.

**Step 7: Commit**

```bash
git add backend/newsletter.py backend/tests/test_preview_email.py
git commit -m "feat: add _build_calendar_html helper to newsletter

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Update `build_preview_email` body with all visual changes (TDD)

**Files:**
- Modify: `backend/newsletter.py:88-142`
- Modify: `backend/tests/test_preview_email.py`

**Context:** Update the function body to: wrap banner in clickable link, rename title, inject calendar block, drop year from dates, append " CST" to times, add source link column. One existing test (`test_includes_date`) must be updated because the date format changes.

**Step 1: Update existing tests that will break**

In `TestBuildPreviewEmail`, find `test_includes_date` and change the assertion:
```python
# Before
def test_includes_date(self):
    html = build_preview_email([_mock_event(date_val=date(2026, 2, 15))], website_url="https://test.example.com")
    assert "Feb 15 2026" in html

# After
def test_includes_date(self):
    html = build_preview_email([_mock_event(date_val=date(2026, 2, 15))], website_url="https://test.example.com")
    assert "Feb 15" in html
    assert "2026" not in html
```

**Step 2: Add new failing tests to `TestBuildPreviewEmail`**

Append these methods inside `TestBuildPreviewEmail` (before the closing of the class):

```python
    def test_banner_links_to_website_url(self):
        html = build_preview_email([_mock_event()], website_url="https://mysite.example.com")
        assert 'href="https://mysite.example.com"' in html

    def test_title_is_m5_magazine(self):
        html = build_preview_email([_mock_event()], website_url="https://test.example.com")
        assert "Metro Milwaukee Miniature Monthly Magazine" in html

    def test_time_shows_cst_label(self):
        html = build_preview_email([_mock_event(start_time="18:00")], website_url="https://test.example.com")
        assert "18:00 CST" in html

    def test_missing_time_still_shows_tbd_not_cst(self):
        html = build_preview_email([_mock_event(start_time=None)], website_url="https://test.example.com")
        assert "TBD" in html
        assert "None" not in html

    def test_source_url_link_appears(self):
        html = build_preview_email(
            [_mock_event(source_url="https://fb.com/event/123")],
            website_url="https://test.example.com",
        )
        assert "https://fb.com/event/123" in html
        assert "↗" in html

    def test_no_source_url_renders_empty_cell(self):
        event = _mock_event(source_url=None)
        event.source_url = None
        html = build_preview_email([event], website_url="https://test.example.com")
        # No broken link icon
        assert html.count("↗") == 0

    def test_calendar_grid_included(self):
        html = build_preview_email([_mock_event()], website_url="https://test.example.com")
        # The calendar helper produces a month label inside an h2
        assert "<h2" in html
        # Day headers appear
        assert "Sun" in html
        assert "Mon" in html
```

**Step 3: Run to confirm new tests fail**

```bash
cd /Users/mikealtschwager/Git/EventBoardAgent && uv run pytest backend/tests/test_preview_email.py::TestBuildPreviewEmail -v
```

Expected: 7 new tests FAIL (feature not yet implemented).

**Step 4: Replace `build_preview_email` body in `backend/newsletter.py`**

Replace the entire `build_preview_email` function (lines 88–142) with:

```python
def build_preview_email(events: list[Event], website_url: str) -> str:
    today = _date.today()
    calendar_html = _build_calendar_html(events, today.year, today.month)
    safe_url = escape(website_url)

    rows = ""
    for e in events:
        date_str = e.date.strftime("%a, %b %d")
        time_val = (e.start_time + " CST") if e.start_time else "TBD"
        time_str = escape(time_val)
        game_name = escape(e.game_system.name)
        location_name = escape(e.location.name)
        title = escape(e.title)
        description = escape(e.description or "")
        source_link = (
            f'<a href="{escape(e.source_url)}" target="_blank"'
            f' style="color:#7c3aed;text-decoration:none;">&#8599;</a>'
            if e.source_url
            else ""
        )
        rows += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
          <td style="padding: 10px 12px; white-space: nowrap;">{date_str}</td>
          <td style="padding: 10px 12px; white-space: nowrap;">{time_str}</td>
          <td style="padding: 10px 12px; font-weight: 600; color: #7c3aed;">{game_name}</td>
          <td style="padding: 10px 12px;">{location_name}</td>
          <td style="padding: 10px 12px; font-weight: 500;">{title}</td>
          <td style="padding: 10px 12px; color: #6b7280; font-size: 13px;">{description}</td>
          <td style="padding: 10px 12px; text-align: center;">{source_link}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Metro Milwaukee Miniature Monthly Magazine</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
             background: #f9fafb; margin: 0; padding: 32px 16px;">
  <div style="max-width: 800px; margin: 0 auto; background: white;
              border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <a href="{safe_url}" style="text-decoration: none; display: block;">
      <div style="background: #7c3aed; padding: 32px; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 24px;">&#127922; Metro Milwaukee Miniature Monthly Magazine</h1>
        <p style="color: #ddd6fe; margin: 8px 0 0; font-size: 15px;">All Events This Month</p>
      </div>
    </a>
    <div style="padding: 32px;">
      {calendar_html}
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
              <th style="padding: 10px 12px; color: #6b7280; font-weight: 600;">Link</th>
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

Note: `↗` is `&#8599;` as a numeric HTML entity to avoid any encoding issues in f-strings. The test checks for the `↗` character, which is what `&#8599;` renders as. Update the test if needed to check for `&#8599;` instead.

Actually — use the literal character in the f-string and the test will match. Swap `&#8599;` back to `↗` in the implementation:
```python
f' style="color:#7c3aed;text-decoration:none;">↗</a>'
```

**Step 5: Run the updated unit tests**

```bash
cd /Users/mikealtschwager/Git/EventBoardAgent && uv run pytest backend/tests/test_preview_email.py::TestBuildPreviewEmail -v
```

Expected: all 16 tests PASS (9 original + 7 new).

**Step 6: Run the full test suite**

```bash
uv run pytest backend/tests/ -v
```

Expected: all 47 tests PASS.

**Step 7: Lint**

```bash
uv run ruff check backend/ && uv run ruff format --check backend/
```

Expected: no errors. Run `uv run ruff format backend/` if format issues arise.

**Step 8: Commit**

```bash
git add backend/newsletter.py backend/tests/test_preview_email.py
git commit -m "feat: redesign preview email — calendar, branded header, CST times, source links

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```
