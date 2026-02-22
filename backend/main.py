import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import create_tables, get_db
from .importer import run_import
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
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@app.get("/events", response_model=list[schemas.EventOut], tags=["events"])
def list_events(
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    game_system_id: Optional[int] = Query(None, description="Filter by game system ID"),
    date_from: Optional[date] = Query(None, description="Earliest event date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Latest event date (YYYY-MM-DD)"),
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

@app.post("/subscribe", response_model=schemas.SubscribeOut, status_code=201, tags=["subscriptions"])
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
