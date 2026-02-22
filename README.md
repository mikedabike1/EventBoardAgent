# Wargame Event Finder

A central discovery hub for local miniature wargame events. Browse upcoming events by store and game system, subscribe to a monthly email newsletter, and keep the event database fresh with a flat-file import job.

## Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React 18, Vite, Tailwind CSS, React Router

---

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the API (auto-creates events.db on first start)
uvicorn main:app --reload --port 8000
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
│   ├── requirements.txt
│   └── data/
│       └── sample_events.json
└── frontend/
    └── src/
        ├── pages/       Home, StorePage, GameSystemPage
        └── components/  EventCard, EventList, FilterBar, SubscribeForm
```
