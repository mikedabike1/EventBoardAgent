from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./events.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from . import models  # noqa: F401 - registers models with Base

    Base.metadata.create_all(bind=engine)
    _migrate_events_table()


def _migrate_events_table() -> None:
    """Add new columns to the events table for existing databases."""
    with engine.connect() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(events)"))}
        for col, definition in [
            ("submitted_by", "TEXT"),
            ("submission_status", "TEXT"),
        ]:
            if col not in existing:
                conn.execute(text(f"ALTER TABLE events ADD COLUMN {col} {definition}"))
        conn.commit()
