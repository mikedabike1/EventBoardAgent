import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

from sqlalchemy.orm import Session

from . import crud
from .models import Event, Subscriber

logger = logging.getLogger(__name__)

# Read SMTP config once at import time so os.getenv isn't called per-email.
_SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
_SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
_SMTP_USER = os.getenv("SMTP_USER", "")
_SMTP_PASS = os.getenv("SMTP_PASS", "")
_EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@wargameevents.local")


def build_html_email(subscriber: Subscriber, events: list[Event]) -> str:
    rows = ""
    for e in events:
        date_str = e.date.strftime("%a, %b %d %Y")
        # escape all user-supplied / crawled content before embedding in HTML
        time_str = escape(e.start_time or "TBD")
        game_name = escape(e.game_system.name)
        store_name = escape(e.store.name)
        title = escape(e.title)
        description = escape(e.description or "")
        rows += f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
          <td style="padding: 10px 12px; white-space: nowrap;">{date_str}</td>
          <td style="padding: 10px 12px; white-space: nowrap;">{time_str}</td>
          <td style="padding: 10px 12px; font-weight: 600; color: #7c3aed;">{game_name}</td>
          <td style="padding: 10px 12px;">{store_name}</td>
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
              <th style="padding: 10px 12px; color: #6b7280; font-weight: 600;">Store</th>
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
    subscribers = crud.get_active_subscribers(db)
    sent = skipped = errors = 0

    for sub in subscribers:
        events = crud.get_events_for_subscriber(db, sub)
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
