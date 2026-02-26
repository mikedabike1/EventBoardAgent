"""
Unit tests for event deduplication logic.

Deduplication key: location_name | game_system | title | date | time
Two events are the same if all five components match (case-insensitively).
"""

from datetime import date as date_type

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models  # noqa: F401 — registers ORM classes with Base
from backend.database import Base
from backend.databridge import get_or_create_game_system, get_or_create_location, upsert_event
from backend.importer import compute_dedup_hash

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def db():
    """In-memory SQLite session, torn down after each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


_DEFAULT_DATE_STR = "2026-03-06"
_DEFAULT_DATE = date_type.fromisoformat(_DEFAULT_DATE_STR)


def _make_record(
    location_name="Game Vault",
    game_system="Warhammer 40,000",
    title="Friday Night 40K",
    date=_DEFAULT_DATE,
    time=None,
    **kwargs,
):
    """Build a minimal event record dict as databridge.upsert_event expects.

    ``date`` must be a ``datetime.date`` object (what SQLAlchemy's Date column accepts).
    The dedup hash is computed from the ISO string of the date, matching importer behaviour.
    """
    date_str = date.isoformat() if isinstance(date, date_type) else date
    return {
        "location_name": location_name,
        "game_system": game_system,
        "title": title,
        "date": date_type.fromisoformat(date_str) if isinstance(date_str, str) else date,
        "time": time,
        "dedup_hash": compute_dedup_hash(location_name, game_system, title, date_str, time),
        **kwargs,
    }


# ---------------------------------------------------------------------------
# compute_dedup_hash — pure function tests
# ---------------------------------------------------------------------------


class TestComputeDedupHash:
    def test_same_inputs_produce_same_hash(self):
        h1 = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06", "18:00")
        h2 = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06", "18:00")
        assert h1 == h2

    def test_different_time_produces_different_hash(self):
        h_morning = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06", "10:00")
        h_evening = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06", "18:00")
        assert h_morning != h_evening

    def test_no_time_and_empty_string_are_equivalent(self):
        h_none = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06", None)
        h_empty = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06", "")
        assert h_none == h_empty

    def test_case_insensitive(self):
        h_lower = compute_dedup_hash("game vault", "40k", "event", "2026-03-06", "18:00")
        h_upper = compute_dedup_hash("GAME VAULT", "40K", "EVENT", "2026-03-06", "18:00")
        assert h_lower == h_upper

    def test_different_location_produces_different_hash(self):
        h1 = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06")
        h2 = compute_dedup_hash("Dragon's Den", "40K", "Event", "2026-03-06")
        assert h1 != h2

    def test_different_game_system_produces_different_hash(self):
        h1 = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06")
        h2 = compute_dedup_hash("Game Vault", "Age of Sigmar", "Event", "2026-03-06")
        assert h1 != h2

    def test_different_date_produces_different_hash(self):
        h1 = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06")
        h2 = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-07")
        assert h1 != h2

    def test_different_title_produces_different_hash(self):
        h1 = compute_dedup_hash("Game Vault", "40K", "Friday Night", "2026-03-06")
        h2 = compute_dedup_hash("Game Vault", "40K", "Saturday Morning", "2026-03-06")
        assert h1 != h2

    def test_time_none_differs_from_explicit_time(self):
        h_none = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06", None)
        h_time = compute_dedup_hash("Game Vault", "40K", "Event", "2026-03-06", "18:00")
        assert h_none != h_time


# ---------------------------------------------------------------------------
# upsert_event — database integration tests
# ---------------------------------------------------------------------------


class TestUpsertEventDeduplication:
    def test_identical_event_returns_same_row(self, db):
        record = _make_record(time="18:00")
        loc = get_or_create_location(db, record["location_name"])
        gs = get_or_create_game_system(db, record["game_system"])

        event1, created1 = upsert_event(db, record, loc, gs)
        db.commit()

        event2, created2 = upsert_event(db, record, loc, gs)
        db.commit()

        assert created1 is True
        assert created2 is False
        assert event1.id == event2.id

    def test_identical_event_updates_last_seen_at(self, db):
        from datetime import UTC, datetime, timedelta

        record = _make_record(time="18:00")
        loc = get_or_create_location(db, record["location_name"])
        gs = get_or_create_game_system(db, record["game_system"])

        event1, _ = upsert_event(db, record, loc, gs)
        db.commit()
        original_last_seen = event1.last_seen_at

        later = datetime.now(UTC) + timedelta(hours=1)
        record2 = {**record, "last_seen_at": later}
        event2, was_created = upsert_event(db, record2, loc, gs)
        db.commit()

        assert was_created is False
        # SQLite stores datetimes without timezone; compare as naive UTC values.
        assert event2.last_seen_at == later.replace(tzinfo=None)
        assert event2.last_seen_at != original_last_seen

    def test_same_location_game_date_different_time_creates_two_events(self, db):
        record_morning = _make_record(time="10:00")
        record_evening = _make_record(time="18:00")

        loc = get_or_create_location(db, "Game Vault")
        gs = get_or_create_game_system(db, "Warhammer 40,000")

        event_morning, created_morning = upsert_event(db, record_morning, loc, gs)
        db.commit()

        event_evening, created_evening = upsert_event(db, record_evening, loc, gs)
        db.commit()

        assert created_morning is True
        assert created_evening is True
        assert event_morning.id != event_evening.id

    def test_same_location_game_date_no_time_is_single_event(self, db):
        record1 = _make_record(time=None)
        record2 = _make_record(time=None)

        loc = get_or_create_location(db, "Game Vault")
        gs = get_or_create_game_system(db, "Warhammer 40,000")

        event1, created1 = upsert_event(db, record1, loc, gs)
        db.commit()

        event2, created2 = upsert_event(db, record2, loc, gs)
        db.commit()

        assert created1 is True
        assert created2 is False
        assert event1.id == event2.id

    def test_different_game_system_creates_two_events(self, db):
        record_40k = _make_record(game_system="Warhammer 40,000", time="18:00")
        record_aos = _make_record(game_system="Age of Sigmar", title="Friday AoS", time="18:00")
        record_aos["dedup_hash"] = compute_dedup_hash(
            record_aos["location_name"],
            record_aos["game_system"],
            record_aos["title"],
            record_aos["date"],
            record_aos["time"],
        )

        loc = get_or_create_location(db, "Game Vault")
        gs_40k = get_or_create_game_system(db, "Warhammer 40,000")
        gs_aos = get_or_create_game_system(db, "Age of Sigmar")

        event1, created1 = upsert_event(db, record_40k, loc, gs_40k)
        db.commit()

        event2, created2 = upsert_event(db, record_aos, loc, gs_aos)
        db.commit()

        assert created1 is True
        assert created2 is True
        assert event1.id != event2.id

    def test_different_location_creates_two_events(self, db):
        record1 = _make_record(location_name="Game Vault", time="18:00")
        record2 = _make_record(location_name="Dragon's Den", time="18:00")
        record2["dedup_hash"] = compute_dedup_hash(
            record2["location_name"],
            record2["game_system"],
            record2["title"],
            record2["date"],
            record2["time"],
        )

        loc1 = get_or_create_location(db, "Game Vault")
        loc2 = get_or_create_location(db, "Dragon's Den")
        gs = get_or_create_game_system(db, "Warhammer 40,000")

        event1, created1 = upsert_event(db, record1, loc1, gs)
        db.commit()

        event2, created2 = upsert_event(db, record2, loc2, gs)
        db.commit()

        assert created1 is True
        assert created2 is True
        assert event1.id != event2.id

    def test_dedup_is_case_insensitive_via_hash(self, db):
        record_lower = _make_record(
            location_name="game vault",
            game_system="warhammer 40,000",
            title="friday night 40k",
            time="18:00",
        )
        record_upper = _make_record(
            location_name="GAME VAULT",
            game_system="WARHAMMER 40,000",
            title="FRIDAY NIGHT 40K",
            time="18:00",
        )

        loc = get_or_create_location(db, "game vault")
        gs = get_or_create_game_system(db, "warhammer 40,000")

        # Both records compute to the same hash regardless of case
        assert record_lower["dedup_hash"] == record_upper["dedup_hash"]

        event1, created1 = upsert_event(db, record_lower, loc, gs)
        db.commit()

        event2, created2 = upsert_event(db, record_upper, loc, gs)
        db.commit()

        assert created1 is True
        assert created2 is False
        assert event1.id == event2.id

    def test_expired_event_is_unexipred_on_duplicate_submit(self, db):
        record = _make_record(time="18:00")
        loc = get_or_create_location(db, record["location_name"])
        gs = get_or_create_game_system(db, record["game_system"])

        event, _ = upsert_event(db, record, loc, gs)
        event.is_expired = True
        db.commit()

        # Re-submitting the same event (same dedup hash) should revive it
        event2, was_created = upsert_event(db, record, loc, gs)
        db.commit()

        assert was_created is False
        assert event2.is_expired is False
