# Design: Preview Email Redesign

**Date:** 2026-02-27
**Status:** Approved

## Summary

Redesign `build_preview_email` to produce a richly formatted monthly newsletter:
- Branded header ("Metro Milwaukee Miniature Monthly Magazine") linking to the website
- Inline HTML calendar grid (mirroring the frontend `CalendarView` component) before the event table
- Per-event source URL links
- Dates without year, times labelled as CST
- Website URL configurable via `WEBSITE_URL` env var

## Changes

### `backend/newsletter.py`

**New private helper: `_build_calendar_html(events, year, month) -> str`**
- 7-column HTML table with inline styles
- Day-of-week header row: Sun–Sat
- Leading blank cells for day-of-week offset
- Each day cell shows up to 3 event pills (colored by game system), then "+N more" if overflow
- 7 pill color pairs (background + text hex) matching the frontend's Tailwind classes:
  - purple-100/800, indigo-100/800, sky-100/800, emerald-100/800, amber-100/800, rose-100/800, teal-100/800
- Game-system color legend row below the grid
- Today's date highlighted with a purple circle

**Updated: `build_preview_email(events, website_url) -> str`**
- New `website_url: str` parameter
- Banner `<div>` wrapped in `<a href="{website_url}">` (white text preserved)
- Title: "Metro Milwaukee Miniature Monthly Magazine"
- Subtitle: "All Events This Month"
- Calendar block inserted between the header and the event table (calls `_build_calendar_html`)
- Date format: `"%a, %b %d"` (no year)
- Time display: `"{time} CST"` (no conversion — times already stored as CST)
- Event table rows: additional `↗` link cell — `<a href="{source_url}">↗</a>` if `source_url` present, else empty

**New module-level constant:**
```python
_WEBSITE_URL = os.getenv("WEBSITE_URL", "http://localhost:8000/")
```

### `backend/main.py`

- `preview_email` endpoint passes `website_url=_WEBSITE_URL` (imported from newsletter) — or reads `WEBSITE_URL` directly and passes it through

### `.env.example`

Add:
```
WEBSITE_URL=http://localhost:8000/
```

## What is not in scope

- Navigation controls (Prev/Next month) — static calendar for the current month only
- Interactive day-click panel — email is static HTML
- Changing `build_html_email` (subscriber emails unchanged)
- Timezone conversion (times are already CST)
