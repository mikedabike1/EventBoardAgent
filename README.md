# Wargame Event Finder

A central discovery hub for local miniature wargame events. Browse upcoming events by store and game system, subscribe to a monthly email newsletter, and keep the event database fresh with a flat-file import job.

![CI](https://github.com/mikedabike1/EventBoardAgent/actions/workflows/ci.yml/badge.svg)

## Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React 19, Vite, Tailwind CSS, React Router

---

## Quick Start

### Backend

```bash
# Install uv if you don't have it: https://docs.astral.sh/uv/getting-started/installation/
uv sync

# Run the API (auto-creates events.db on first start)
uv run uvicorn backend.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI.

### Import sample events

```bash
curl -X POST http://localhost:8000/admin/import
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:5173**

---

## Environment

Copy `.env.example` to `backend/.env` and fill in SMTP values for the newsletter.
For local email testing, use [Mailpit](https://mailpit.axllent.org/) (`SMTP_PORT=1025`).

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/events` | List events (filters: `store_id`, `game_system_id`, `date_from`, `date_to`) |
| `GET` | `/stores` | List all stores |
| `GET` | `/games` | List all game systems |
| `POST` | `/subscribe` | Subscribe to newsletter |
| `POST` | `/admin/import` | Ingest flat JSON files from `backend/data/` |
| `POST` | `/admin/newsletter` | Send monthly newsletter to all subscribers |

---

## Event Ingestion

Drop JSON files into `backend/data/`. Each file can be an array of event objects:

```json
[
  {
    "store_name": "Dragon's Den Games",
    "game_system": "Warhammer 40,000",
    "title": "Friday Night 40K",
    "date": "2026-03-07",
    "time": "18:00",
    "description": "Open play, all levels welcome.",
    "source_url": "https://example.com/events/123",
    "source_type": "facebook",
    "last_seen_at": "2026-02-20T12:00:00"
  }
]
```

Events are deduplicated by a hash of `store_name + game_system + title + date`.
Events older than 30 days are automatically expired on each import run.

---

## Linting

CI runs automatically on every push and pull request. To run the same checks locally:

### Backend — [ruff](https://docs.astral.sh/ruff/)

```bash
# install dev dependencies (includes ruff)
pip install -r backend/requirements-dev.txt

# check for errors
ruff check backend/

# auto-fix all fixable errors
ruff check --fix backend/

# check formatting (ruff replaces black)
ruff format --check backend/

# apply formatting
ruff format backend/
```

Ruff is configured in `pyproject.toml`. Rules enabled: `E/W` (pycodestyle), `F` (pyflakes), `I` (isort), `UP` (pyupgrade), `B` (bugbear), `C4` (comprehensions), `SIM` (simplify).

### Frontend — [ESLint](https://eslint.org/)

```bash
cd frontend

# check for errors
npm run lint
```

ESLint is configured in `frontend/eslint.config.js`. Rules include `eslint:recommended`, `react-hooks`, and `react-refresh`.

---

## Project Structure

```
EventBoardAgent/
├── backend/
│   ├── main.py          FastAPI app
│   ├── database.py      SQLAlchemy engine + session
│   ├── models.py        ORM models
│   ├── schemas.py       Pydantic schemas
│   ├── crud.py          DB operations
│   ├── importer.py      Flat file ingestion
│   ├── newsletter.py    HTML email generator + sender
│   └── data/
│       └── sample_events.json
└── frontend/
    └── src/
        ├── pages/       Home, StorePage, GameSystemPage
        └── components/  EventCard, EventList, FilterBar, SubscribeForm
```
