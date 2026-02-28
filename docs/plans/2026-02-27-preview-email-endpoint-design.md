# Design: Preview Email Download Endpoint

**Date:** 2026-02-27
**Status:** Approved

## Summary

Add a `GET /admin/preview-email` endpoint that generates an HTML email showing all events for the current calendar month and returns it as a browser file download.

## Motivation

Needed to quickly inspect and verify newsletter email rendering without sending to real subscribers or requiring SMTP setup.

## Design

### `backend/newsletter.py`

Add `build_preview_email(events: list[Event]) -> str`.

- Mirrors the HTML structure of `build_html_email` (same table, same inline styles).
- Generic heading: "All Events This Month" — no subscriber-specific greeting.
- No `Subscriber` parameter needed.
- Does not modify or touch `build_html_email`.

### `backend/main.py`

Add `GET /admin/preview-email` under the `admin` tag.

- Compute `date_from` = first day of current calendar month, `date_to` = last day of current calendar month.
- Call `crud.get_events(db, date_from=date_from, date_to=date_to)` — no location/game system filters, returns all non-expired events in that range.
- Call `build_preview_email(events)` to render HTML.
- Return a `Response` with:
  - `media_type="text/html"`
  - `Content-Disposition: attachment; filename="preview-email-YYYY-MM.html"` (month-stamped)
- No file is written to disk; HTML is streamed directly as the download response.

## What is not in scope

- Authentication/authorization (consistent with existing admin endpoints)
- Filtering by location or game system
- Saving the file to disk
