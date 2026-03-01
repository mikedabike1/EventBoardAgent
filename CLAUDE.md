# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Local database (docker-compose)

```bash
docker-compose up -d          # start local postgres on :5432
docker-compose down           # stop (data persists in pgdata volume)
docker-compose down -v        # stop + wipe volume
```

### Database migrations (Alembic)

```bash
uv run alembic upgrade head                          # apply all pending migrations
uv run alembic downgrade base                        # roll back all migrations
uv run alembic revision --autogenerate -m "desc"    # generate a new migration from model changes
uv run alembic history                               # list applied migrations
```

### Backend

```bash
uv sync                                                          # install dependencies
uv run uvicorn backend.main:app --reload --port 8000            # start dev server
curl -X POST http://localhost:8000/admin/import                  # ingest backend/data/*.json
```

Linting (CI runs these on every push):
```bash
ruff check backend/          # lint
ruff check --fix backend/    # lint + auto-fix
ruff format backend/         # format
ruff format --check backend/ # format check only
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # Vite dev server at http://localhost:5173
npm run lint   # ESLint
npm run build  # production build into frontend/dist/
```

### Environment

Copy `.env.example` to `backend/.env`. The `DATABASE_URL` variable is **required** — for local dev it points at the docker-compose postgres. In dev, set `VITE_API_URL=http://localhost:8000` in `frontend/.env` so the frontend hits the FastAPI server directly.

**Local dev quick-start:**
```bash
docker-compose up -d
cp .env.example backend/.env          # DATABASE_URL already set for local postgres
uv sync
uv run alembic upgrade head
uv run uvicorn backend.main:app --reload --port 8000
```

---

## Architecture

**Stack**: FastAPI + SQLAlchemy (PostgreSQL via Neon) backend; React 19 + Vite + Tailwind CSS frontend.

### Backend

All routes are registered in `backend/main.py`. The data layer is `backend/databridge.py` (CRUD operations). There is no `crud.py` — it was replaced by `databridge.py`, but `main.py` still imports it as `crud` (`from . import crud, schemas`); this import will break until resolved.

There is a `backend/api/` directory (untracked, in progress) with route fragment files (`events.py`, `locations.py`, `subscriptions.py`) that appear to be splitting `main.py` into separate routers — they are not yet wired into the app.

Key modules:
- `models.py` — SQLAlchemy ORM: `Location`, `GameSystem`, `Event`, `Subscriber`
- `schemas.py` — Pydantic I/O schemas: `LocationOut`, `EventOut`, `EventIn`, `SubscribeIn/Out`
- `databridge.py` — all DB operations (get/create location, game system, events, subscribers)
- `importer.py` — reads JSON files from `backend/data/`, normalizes records, deduplicates by SHA256 hash of `location_name|game_system|title|date`, expires events older than 30 days
- `newsletter.py` — builds HTML email table and sends via SMTP; currently imports `databridge` directly rather than via `crud`
- `database.py` — PostgreSQL engine (reads `DATABASE_URL` env var), session factory, `create_tables()` called at app startup via lifespan; Alembic handles schema migrations

**Event deduplication**: `importer.compute_dedup_hash(location_name, game_system, title, date)` → SHA256 hex. On conflict the existing event is updated (`last_seen_at`, `source_url`, `is_expired=False`) rather than inserted.

**Production serving**: When `frontend/dist/` exists, FastAPI mounts it as static files and serves `index.html` for all non-API routes (SPA fallback). This means the backend serves the full app in production.

### Frontend

SPA with React Router. Key files:
- `src/App.jsx` — router setup; wraps `LocationPage` and `GameSystemPage` in keyed route wrappers to force remount on param change
- `src/api.js` — all API calls via axios; `fetchLocations()` hits `/locations`, `fetchEvents()` maps JS camelCase filter keys to snake_case query params (`locationId` → `location_id`)
- `src/pages/Home.jsx` — main page: fetches locations + game systems once, fetches events on search; filter state lives here and is passed down to `FilterBar`
- `src/pages/LocationPage.jsx` — detail page for a single location
- `src/components/FilterBar.jsx` — receives `locations`, `gameSystems`, `filters`, `onChange`, `onSearch` as props; does not manage its own state
- `src/components/SubscribeForm.jsx` — receives `locations`, `gameSystems` as props; manages its own selection state

### Database Schema

| Table | Key columns |
|---|---|
| `locations` | `id`, `name`, `city`, `state`, `website`, `discord_url`, `facebook_url` |
| `game_systems` | `id`, `name`, `slug`, `publisher` |
| `events` | `id`, `location_id`, `game_system_id`, `title`, `date`, `start_time`, `description`, `source_url`, `source_type`, `dedup_hash`, `is_expired` |
| `subscribers` | `id`, `email`, `location_ids` (JSON text), `game_system_ids` (JSON text), `is_active` |

`Subscriber.location_ids` and `game_system_ids` are stored as JSON strings; `SubscribeOut` uses a `field_validator` to parse them on read.

### Event JSON Ingestion Format

Files in `backend/data/*.json` must be arrays with these fields:

```json
{
  "location_name": "Dragon's Den Games",
  "game_system": "Warhammer 40,000",
  "title": "Friday Night 40K",
  "date": "2026-03-06",
  "time": "18:00",
  "source_url": "https://...",
  "source_type": "facebook"
}
```

Required: `location_name`, `game_system`, `title`, `date`.
