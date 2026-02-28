"""Unit tests for build_preview_email."""

from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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


# ---------------------------------------------------------------------------
# build_preview_email — unit tests
# ---------------------------------------------------------------------------


class TestBuildPreviewEmail:
    def test_returns_html_string(self):
        html = build_preview_email([_mock_event()], website_url="https://test.example.com")
        assert isinstance(html, str)
        assert html.strip().startswith("<!DOCTYPE html>")

    def test_contains_heading(self):
        html = build_preview_email([_mock_event()], website_url="https://test.example.com")
        assert "All Events This Month" in html

    def test_includes_event_title(self):
        html = build_preview_email(
            [_mock_event(title="Saturday Skirmish")], website_url="https://test.example.com"
        )
        assert "Saturday Skirmish" in html

    def test_includes_game_system(self):
        html = build_preview_email(
            [_mock_event(game_name="Age of Sigmar")], website_url="https://test.example.com"
        )
        assert "Age of Sigmar" in html

    def test_includes_location(self):
        html = build_preview_email(
            [_mock_event(location_name="Dragon's Den")], website_url="https://test.example.com"
        )
        assert "Dragon&#x27;s Den" in html  # html.escape applied

    def test_includes_date(self):
        html = build_preview_email(
            [_mock_event(date_val=date(2026, 2, 15))], website_url="https://test.example.com"
        )
        assert "Feb 15 2026" in html

    def test_empty_events_still_returns_html(self):
        html = build_preview_email([], website_url="https://test.example.com")
        assert "<table" in html
        assert "<tbody>" in html

    def test_missing_start_time_shows_tbd(self):
        html = build_preview_email(
            [_mock_event(start_time=None)], website_url="https://test.example.com"
        )
        assert "TBD" in html

    def test_multiple_events_all_appear(self):
        events = [
            _mock_event(title="Event Alpha"),
            _mock_event(title="Event Beta"),
        ]
        html = build_preview_email(events, website_url="https://test.example.com")
        assert "Event Alpha" in html
        assert "Event Beta" in html


# ---------------------------------------------------------------------------
# /admin/preview-email endpoint — integration tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
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
        import re

        disposition = client.get("/admin/preview-email").headers["content-disposition"]
        # filename must be preview-email-YYYY-MM.html (month-stamped)
        assert re.search(r'filename="preview-email-\d{4}-\d{2}\.html"', disposition)

    def test_body_is_valid_html(self, client):
        response = client.get("/admin/preview-email")
        assert "<!DOCTYPE html>" in response.text
        assert "All Events This Month" in response.text


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
        # February 2026 has 28 days starting on Sunday = 4 full rows
        assert html.count("<tr>") >= 5  # 1 header row + 4 week rows

    def test_events_from_other_months_excluded(self):
        event_march = _mock_event(title="March Event", date_val=date(2026, 3, 1))
        html = self._call([event_march], year=2026, month=2)
        assert "March Event" not in html
