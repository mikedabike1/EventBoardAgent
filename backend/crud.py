import json
import re
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import or_, update
from sqlalchemy.orm import Session

from .models import Event, GameSystem, Store, Subscriber


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ---------------------------------------------------------------------------
# Stores
# ---------------------------------------------------------------------------

def get_stores(db: Session) -> list[Store]:
    return db.query(Store).order_by(Store.name).all()


def get_or_create_store(db: Session, name: str) -> Store:
    store = db.query(Store).filter(Store.name == name).first()
    if not store:
        store = Store(name=name)
        db.add(store)
        db.flush()
    return store


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
    store_id: int | None = None,
    game_system_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Event]:
    query = db.query(Event).filter(Event.is_expired.is_(False))

    if store_id is not None:
        query = query.filter(Event.store_id == store_id)
    if game_system_id is not None:
        query = query.filter(Event.game_system_id == game_system_id)
    if date_from is not None:
        query = query.filter(Event.date >= date_from)
    if date_to is not None:
        query = query.filter(Event.date <= date_to)

    return (
        query.order_by(Event.date.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def upsert_event(
    db: Session, record: dict, store: Store, game_system: GameSystem
) -> tuple[Event, bool]:
    existing = db.query(Event).filter(Event.dedup_hash == record["dedup_hash"]).first()

    if existing:
        existing.last_seen_at = record.get("last_seen_at") or _utcnow()
        existing.source_url = record.get("source_url", existing.source_url)
        existing.is_expired = False  # re-seen events are no longer expired
        return existing, False

    event = Event(
        store_id=store.id,
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
    store_ids = json.loads(subscriber.store_ids or "[]")
    game_system_ids = json.loads(subscriber.game_system_ids or "[]")

    if not store_ids and not game_system_ids:
        return []

    conditions = []
    if store_ids:
        conditions.append(Event.store_id.in_(store_ids))
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
    db: Session, email: str, store_ids: list[int], game_system_ids: list[int]
) -> Subscriber:
    sub = db.query(Subscriber).filter(Subscriber.email == email).first()
    if sub:
        sub.store_ids = json.dumps(store_ids)
        sub.game_system_ids = json.dumps(game_system_ids)
        sub.is_active = True
    else:
        sub = Subscriber(
            email=email,
            store_ids=json.dumps(store_ids),
            game_system_ids=json.dumps(game_system_ids),
        )
        db.add(sub)
    db.flush()
    return sub
