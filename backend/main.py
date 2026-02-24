import logging
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import create_tables, get_db
from .importer import compute_dedup_hash, run_import
from .newsletter import run_newsletter

load_dotenv()

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Wargame Event Finder",
    description="API for discovering local miniature wargame events",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


@app.post("/events", response_model=schemas.EventOut, status_code=201, tags=["events"])
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
            payload.store_name, payload.game_system, payload.title, str(payload.date)
        ),
    }
    store = crud.get_or_create_store(db, payload.store_name.strip())
    game_system = crud.get_or_create_game_system(db, payload.game_system.strip())
    event, _ = crud.upsert_event(db, record, store, game_system)
    db.commit()
    db.refresh(event)
    return event


@app.post("/events/batch", tags=["events"])
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
                    item.store_name, item.game_system, item.title, str(item.date)
                ),
            }
            store = crud.get_or_create_store(db, item.store_name.strip())
            game_system = crud.get_or_create_game_system(db, item.game_system.strip())
            _, was_created = crud.upsert_event(db, record, store, game_system)
            if was_created:
                created += 1
            else:
                updated += 1
        except Exception:
            errors += 1
    db.commit()
    return {"created": created, "updated": updated, "errors": errors}


@app.get("/events", response_model=list[schemas.EventOut], tags=["events"])
def list_events(
    store_id: int | None = Query(None, description="Filter by store ID"),
    game_system_id: int | None = Query(None, description="Filter by game system ID"),
    date_from: date | None = Query(None, description="Earliest event date (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="Latest event date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud.get_events(db, store_id, game_system_id, date_from, date_to, skip, limit)


# ---------------------------------------------------------------------------
# Stores
# ---------------------------------------------------------------------------


@app.get("/stores", response_model=list[schemas.StoreOut], tags=["stores"])
def list_stores(db: Session = Depends(get_db)):
    return crud.get_stores(db)


# ---------------------------------------------------------------------------
# Game Systems
# ---------------------------------------------------------------------------


@app.get("/games", response_model=list[schemas.GameSystemOut], tags=["games"])
def list_game_systems(db: Session = Depends(get_db)):
    return crud.get_game_systems(db)


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------


@app.post(
    "/subscribe", response_model=schemas.SubscribeOut, status_code=201, tags=["subscriptions"]
)
def subscribe(payload: schemas.SubscribeIn, db: Session = Depends(get_db)):
    sub = crud.create_or_update_subscriber(
        db, str(payload.email), payload.store_ids, payload.game_system_ids
    )
    db.commit()
    db.refresh(sub)
    return sub


# ---------------------------------------------------------------------------
# Admin (no auth in MVP — protect via network/reverse proxy in production)
# ---------------------------------------------------------------------------


@app.post("/admin/import", tags=["admin"])
def trigger_import(db: Session = Depends(get_db)):
    return run_import(db)


@app.post("/admin/newsletter", tags=["admin"])
def trigger_newsletter(db: Session = Depends(get_db)):
    return run_newsletter(db)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Serve the built frontend (dist/) as static files when it exists.
# MUST be registered last so the catch-all doesn't shadow API routes above.
# ---------------------------------------------------------------------------

_DIST = Path(__file__).parent.parent / "frontend" / "dist"

if _DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str = ""):
        """Return index.html for every non-API route so React Router works."""
        index = _DIST / "index.html"
        return FileResponse(index)
