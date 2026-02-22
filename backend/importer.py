import hashlib
import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from . import crud

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
EXPIRY_DAYS = 30


def compute_dedup_hash(store_name: str, game_system: str, title: str, event_date: str) -> str:
    raw = f"{store_name}|{game_system}|{title}|{event_date}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()


def normalize_record(raw: dict) -> dict | None:
    required = ["store_name", "game_system", "title", "date"]
    for field in required:
        if not raw.get(field):
            logger.warning("Skipping record missing field '%s': %s", field, raw)
            return None

    record = dict(raw)
    record["store_name"] = record["store_name"].strip()
    record["game_system"] = record["game_system"].strip()
    record["title"] = record["title"].strip()
    record["dedup_hash"] = compute_dedup_hash(
        record["store_name"],
        record["game_system"],
        record["title"],
        record["date"],
    )

    # Parse date string → datetime.date object (required by SQLAlchemy Date column)
    try:
        record["date"] = date.fromisoformat(str(record["date"]))
    except (ValueError, TypeError):
        logger.warning("Skipping record with invalid date '%s'", record.get("date"))
        return None

    if record.get("last_seen_at"):
        try:
            record["last_seen_at"] = datetime.fromisoformat(record["last_seen_at"])
        except ValueError:
            record["last_seen_at"] = datetime.now(timezone.utc)
    else:
        record["last_seen_at"] = datetime.now(timezone.utc)

    return record


def load_json_file(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


def run_import(db: Session, data_dir: Path = DATA_DIR) -> dict:
    files = sorted(data_dir.glob("*.json"))
    if not files:
        logger.warning("No JSON files found in %s", data_dir)
        return {"processed": 0, "created": 0, "updated": 0, "expired": 0, "errors": 0}

    processed = created = updated = errors = 0

    for file in files:
        logger.info("Importing %s", file.name)
        try:
            records = load_json_file(file)
        except Exception as exc:
            logger.error("Failed to load %s: %s", file, exc)
            continue

        for raw in records:
            record = normalize_record(raw)
            if not record:
                errors += 1
                continue

            processed += 1
            store = crud.get_or_create_store(db, record["store_name"])
            game_system = crud.get_or_create_game_system(db, record["game_system"])
            _, was_created = crud.upsert_event(db, record, store, game_system)
            if was_created:
                created += 1
            else:
                updated += 1

    expired = crud.expire_old_events(db, days=EXPIRY_DAYS)
    db.commit()

    result = {
        "processed": processed,
        "created": created,
        "updated": updated,
        "expired": expired,
        "errors": errors,
    }
    logger.info("Import complete: %s", result)
    return result
