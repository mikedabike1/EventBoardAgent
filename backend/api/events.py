from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import databridge, schemas
from ..database import get_db
from ..importer import compute_dedup_hash

# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

router = APIRouter()


@router.post("/events", response_model=schemas.EventOut, status_code=201, tags=["events"])
def create_event(payload: schemas.EventIn, db: Session = Depends(get_db)):
    record = {
        "title": payload.title.strip(),
        "date": payload.date,
        "time": payload.time,
        "description": payload.description,
        "source_url": payload.source_url,
        "source_type": payload.source_type,
        "last_seen_at": payload.last_seen_at,
        "dedup_hash": compute_dedup_hash(
            payload.location_name, payload.game_system, payload.title, str(payload.date)
        ),
    }
    location = databridge.get_or_create_location(db, payload.location_name.strip())
    game_system = databridge.get_or_create_game_system(db, payload.game_system.strip())
    event, _ = databridge.upsert_event(db, record, location, game_system)
    db.commit()
    db.refresh(event)
    return event


@router.post("/events/batch", tags=["events"])
def create_events_batch(payload: list[schemas.EventIn], db: Session = Depends(get_db)):
    created = updated = errors = 0
    for item in payload:
        try:
            record = {
                "title": item.title.strip(),
                "date": item.date,
                "time": item.time,
                "description": item.description,
                "source_url": item.source_url,
                "source_type": item.source_type,
                "last_seen_at": item.last_seen_at,
                "dedup_hash": compute_dedup_hash(
                    item.location_name, item.game_system, item.title, str(item.date)
                ),
            }
            location = databridge.get_or_create_location(db, item.location_name.strip())
            game_system = databridge.get_or_create_game_system(db, item.game_system.strip())
            _, was_created = databridge.upsert_event(db, record, location, game_system)
            if was_created:
                created += 1
            else:
                updated += 1
        except Exception:
            errors += 1
    db.commit()
    return {"created": created, "updated": updated, "errors": errors}


@router.get("/events", response_model=list[schemas.EventOut], tags=["events"])
def list_events(
    location_id: int | None = Query(None, description="Filter by location ID"),
    game_system_id: int | None = Query(None, description="Filter by game system ID"),
    date_from: date | None = Query(None, description="Earliest event date (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="Latest event date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return databridge.get_events(db, location_id, game_system_id, date_from, date_to, skip, limit)

