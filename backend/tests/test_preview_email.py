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
        today = date.today()
        expected_slug = today.strftime("%Y-%m")
        disposition = client.get("/admin/preview-email").headers["content-disposition"]
        assert expected_slug in disposition

    def test_body_is_valid_html(self, client):
        response = client.get("/admin/preview-email")
        assert "<!DOCTYPE html>" in response.text
        assert "All Events This Month" in response.text
