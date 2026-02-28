import json
import re
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import or_, update
from sqlalchemy.orm import Session

from .models import Event, GameSystem, Location, Subscriber
from .schemas import EventSubmitIn


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------


def get_locations(db: Session) -> list[Location]:
    return db.query(Location).order_by(Location.name).all()


def get_or_create_location(db: Session, name: str) -> Location:
    location = db.query(Location).filter(Location.name == name).first()
    if not location:
        location = Location(name=name)
        db.add(location)
        db.flush()
    return location


# ---------------------------------------------------------------------------
# Game Systems
# ---------------------------------------------------------------------------


def get_game_systems(db: Session) -> list[GameSystem]:
    return db.query(GameSystem).order_by(GameSystem.name).all()


def _make_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def get_or_create_game_system(db: Session, name: str) -> GameSystem:
    gs = db.query(GameSystem).filter(GameSystem.name == name).first()
    if not gs:
        slug = _make_slug(name)
        # ensure slug uniqueness by appending a counter if needed
        base_slug = slug
        counter = 1
        while db.query(GameSystem).filter(GameSystem.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        gs = GameSystem(name=name, slug=slug)
        db.add(gs)
        db.flush()
    return gs


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


def get_events(
    db: Session,
    location_id: int | None = None,
    game_system_ids: list[int] | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Event]:
    query = db.query(Event).filter(Event.is_expired.is_(False))

    if location_id is not None:
        query = query.filter(Event.location_id == location_id)
    if game_system_ids:
        query = query.filter(Event.game_system_id.in_(game_system_ids))
    if date_from is not None:
        query = query.filter(Event.date >= date_from)
    if date_to is not None:
        query = query.filter(Event.date <= date_to)

    return query.order_by(Event.date.asc()).offset(skip).limit(limit).all()


def upsert_event(
    db: Session, record: dict, location: Location, game_system: GameSystem
) -> tuple[Event, bool]:
    existing = db.query(Event).filter(Event.dedup_hash == record["dedup_hash"]).first()

    if existing:
        existing.last_seen_at = record.get("last_seen_at") or _utcnow()
        existing.source_url = record.get("source_url", existing.source_url)
        existing.is_expired = False  # re-seen events are no longer expired
        return existing, False

    event = Event(
        location_id=location.id,
        game_system_id=game_system.id,
        title=record["title"],
        date=record["date"],
        start_time=record.get("time"),
        description=record.get("description"),
        source_url=record.get("source_url"),
        source_type=record.get("source_type"),
        last_seen_at=record.get("last_seen_at") or _utcnow(),
        dedup_hash=record["dedup_hash"],
    )
    db.add(event)
    return event, True


def create_user_event(db: Session, data: EventSubmitIn, user_sub: str) -> Event:
    """Create an event submitted by a logged-in user, pending admin review."""
    from .importer import compute_dedup_hash

    location = get_or_create_location(db, data.location_name.strip())
    game_system = get_or_create_game_system(db, data.game_system.strip())
    dedup_hash = compute_dedup_hash(
        data.location_name, data.game_system, data.title, str(data.date), data.time
    )
    record = {
        "title": data.title.strip(),
        "date": data.date,
        "time": data.time,
        "description": data.description,
        "source_url": data.source_url,
        "source_type": data.source_type,
        "dedup_hash": dedup_hash,
    }
    existing = db.query(Event).filter(Event.dedup_hash == dedup_hash).first()
    if existing:
        existing.last_seen_at = _utcnow()
        existing.submitted_by = user_sub
        existing.submission_status = "pending_review"
        existing.is_expired = False
        return existing

    event = Event(
        location_id=location.id,
        game_system_id=game_system.id,
        title=record["title"],
        date=record["date"],
        start_time=record.get("time"),
        description=record.get("description"),
        source_url=record.get("source_url"),
        source_type=record.get("source_type"),
        last_seen_at=_utcnow(),
        dedup_hash=dedup_hash,
        submitted_by=user_sub,
        submission_status="pending_review",
    )
    db.add(event)
    return event


def get_pending_events(db: Session) -> list[Event]:
    """Return events awaiting admin review, ordered by date."""
    return (
        db.query(Event)
        .filter(Event.submission_status == "pending_review")
        .order_by(Event.date.asc())
        .all()
    )


def review_event(db: Session, event_id: int, action: str) -> Event:
    """Approve or reject a user-submitted event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Event not found")
    if action == "approve":
        event.submission_status = "approved"
    else:
        event.submission_status = "rejected"
        event.is_expired = True
    db.flush()
    return event


def expire_old_events(db: Session, days: int = 30) -> int:
    cutoff = date.today() - timedelta(days=days)
    result = db.execute(
        update(Event)
        .where(Event.date < cutoff, Event.is_expired.is_(False))
        .values(is_expired=True)
    )
    return result.rowcount


# ---------------------------------------------------------------------------
# Subscribers
# ---------------------------------------------------------------------------


def get_active_subscribers(db: Session) -> list[Subscriber]:
    return db.query(Subscriber).filter(Subscriber.is_active.is_(True)).all()


def get_events_for_subscriber(db: Session, subscriber: Subscriber) -> list[Event]:
    location_ids = json.loads(subscriber.location_ids or "[]")
    game_system_ids = json.loads(subscriber.game_system_ids or "[]")

    if not location_ids and not game_system_ids:
        return []

    conditions = []
    if location_ids:
        conditions.append(Event.location_id.in_(location_ids))
    if game_system_ids:
        conditions.append(Event.game_system_id.in_(game_system_ids))

    return (
        db.query(Event)
        .filter(
            or_(*conditions),
            Event.is_expired.is_(False),
            Event.date >= date.today(),
        )
        .order_by(Event.date.asc())
        .all()
    )


def create_or_update_subscriber(
    db: Session, email: str, location_ids: list[int], game_system_ids: list[int]
) -> Subscriber:
    sub = db.query(Subscriber).filter(Subscriber.email == email).first()
    if sub:
        sub.location_ids = json.dumps(location_ids)
        sub.game_system_ids = json.dumps(game_system_ids)
        sub.is_active = True
    else:
        sub = Subscriber(
            email=email,
            location_ids=json.dumps(location_ids),
            game_system_ids=json.dumps(game_system_ids),
        )
        db.add(sub)
    db.flush()
    return sub
