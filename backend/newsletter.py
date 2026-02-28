import calendar as _cal
import logging
import os
import smtplib
from datetime import date as _date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

from sqlalchemy.orm import Session

from . import databridge
from .models import Event, Subscriber

logger = logging.getLogger(__name__)

# Read SMTP config once at import time so os.getenv isn't called per-email.
_SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
_SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
_SMTP_USER = os.getenv("SMTP_USER", "")
_SMTP_PASS = os.getenv("SMTP_PASS", "")
_EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@wargameevents.local")

# Pill color pairs (bg, text) — mirror CalendarView.jsx PILL_COLORS in the frontend
_PILL_COLORS = [
    ("#ede9fe", "#5b21b6"),  # purple-100 / purple-800
    ("#e0e7ff", "#3730a3"),  # indigo-100 / indigo-800
    ("#e0f2fe", "#075985"),  # sky-100 / sky-800
    ("#d1fae5", "#065f46"),  # emerald-100 / emerald-800
    ("#fef3c7", "#92400e"),  # amber-100 / amber-800
    ("#ffe4e6", "#9f1239"),  # rose-100 / rose-800
    ("#ccfbf1", "#115e59"),  # teal-100 / teal-800
]


def _build_calendar_html(events: list[Event], year: int, month: int) -> str:
    """Return an inline-style HTML calendar grid for the given year/month."""
    today_str = _date.today().isoformat()

    # Group events by ISO date string; collect unique game systems for legend
    events_by_date: dict[str, list[Event]] = {}
    seen_gs: dict[int, str] = {}
    for e in events:
        d = str(e.date)
        if d not in events_by_date:
            events_by_date[d] = []
        events_by_date[d].append(e)
        if e.date.year == year and e.date.month == month and e.game_system.id not in seen_gs:
            seen_gs[e.game_system.id] = e.game_system.name

    # Build grid cells (Sunday-first)
    first_dow_mon = _cal.monthrange(year, month)[0]  # Monday=0
    first_dow_sun = (first_dow_mon + 1) % 7  # Sunday=0
    days_in_month = _cal.monthrange(year, month)[1]
    cells: list[int | None] = [None] * first_dow_sun + list(range(1, days_in_month + 1))
    while len(cells) % 7:
        cells.append(None)

    # Day-of-week header row
    day_headers = "".join(
        f'<th style="padding:8px 4px;text-align:center;color:#9ca3af;font-size:11px;'
        f"font-weight:600;text-transform:uppercase;letter-spacing:0.05em;"
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
                        f"font-weight:500;overflow:hidden;white-space:nowrap;"
                        f"text-overflow:ellipsis;margin-bottom:2px;"
                        f'background:{bg};color:{fg};">{escape(e.title)}</div>'
                    )
                overflow = len(day_events) - 3
                if overflow > 0:
                    pills += (
                        f'<div style="font-size:11px;color:#9ca3af;padding-left:4px;">'
                        f"+{overflow} more</div>"
                    )
                rows_html += (
                    f'<td style="vertical-align:top;padding:6px;'
                    f"border-right:1px solid #f3f4f6;border-bottom:1px solid #f3f4f6;"
                    f'min-width:0;height:80px;">'
                    f'<div style="text-align:right;margin-bottom:4px;">'
                    f'<span style="{num_style}">{day}</span></div>'
                    f"{pills}</td>"
                )
        rows_html += "</tr>"

    # Legend
    legend = "".join(
        f'<span style="font-size:12px;padding:2px 10px;border-radius:9999px;'
        f"font-weight:500;margin-right:6px;"
        f"background:{_PILL_COLORS[(gs_id - 1) % len(_PILL_COLORS)][0]};"
        f'color:{_PILL_COLORS[(gs_id - 1) % len(_PILL_COLORS)][1]};">'
        f"{escape(gs_name)}</span>"
        for gs_id, gs_name in seen_gs.items()
    )
    legend_block = f'<div style="margin-top:10px;line-height:2;">{legend}</div>' if legend else ""

    month_name = _date(year, month, 1).strftime("%B %Y")
    return (
        f'<div style="margin-bottom:24px;">'
        f'<h2 style="font-size:15px;font-weight:600;color:#374151;margin:0 0 12px 0;">'
        f"{month_name}</h2>"
        f'<div style="border-radius:12px;overflow:hidden;border:1px solid #f3f4f6;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
        f'<table style="width:100%;border-collapse:collapse;table-layout:fixed;background:white;">'
        f"<thead><tr>{day_headers}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        f"</table></div>"
        f"{legend_block}"
        f"</div>"
    )


def build_html_email(subscriber: Subscriber, events: list[Event]) -> str:
    rows = ""
    for e in events:
        date_str = e.date.strftime("%a, %b %d %Y")
        # escape all user-supplied / crawled content before embedding in HTML
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
  <title>Your Upcoming Wargame Events</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
             background: #f9fafb; margin: 0; padding: 32px 16px;">
  <div style="max-width: 700px; margin: 0 auto; background: white;
              border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <div style="background: #7c3aed; padding: 32px; text-align: center;">
      <h1 style="color: white; margin: 0; font-size: 24px;">&#127922; Wargame Event Finder</h1>
      <p style="color: #ddd6fe; margin: 8px 0 0; font-size: 15px;">Your upcoming events for this month</p>
    </div>
    <div style="padding: 32px;">
      <p style="color: #374151; margin: 0 0 24px;">
        Hi there! Here are the upcoming events matching your interests:
      </p>
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
      <p style="color: #9ca3af; font-size: 13px; margin: 32px 0 0; text-align: center;">
        You&#39;re receiving this because you subscribed at Wargame Event Finder.<br>
        To unsubscribe or update preferences, reply to this email.
      </p>
    </div>
  </div>
</body>
</html>"""


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
            f' style="color:#7c3aed;text-decoration:none;">↗</a>'
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


def send_email(to_addr: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = _EMAIL_FROM
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(_SMTP_HOST, _SMTP_PORT) as smtp:
        if _SMTP_USER:
            smtp.login(_SMTP_USER, _SMTP_PASS)
        smtp.sendmail(_EMAIL_FROM, [to_addr], msg.as_string())


def run_newsletter(db: Session) -> dict:
    subscribers = databridge.get_active_subscribers(db)
    sent = skipped = errors = 0

    for sub in subscribers:
        events = databridge.get_events_for_subscriber(db, sub)
        if not events:
            skipped += 1
            continue
        try:
            html = build_html_email(sub, events)
            send_email(sub.email, "Your Monthly Wargame Events", html)
            sent += 1
            logger.info("Newsletter sent to %s (%d events)", sub.email, len(events))
        except Exception as exc:
            errors += 1
            logger.error("Failed to send newsletter to %s: %s", sub.email, exc)

    result = {"sent": sent, "skipped": skipped, "errors": errors}
    logger.info("Newsletter run complete: %s", result)
    return result
