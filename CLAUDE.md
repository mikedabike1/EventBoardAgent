# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

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

Copy `.env.example` to `backend/.env`. In dev, set `VITE_API_URL=http://localhost:8000` in `frontend/.env` so the frontend hits the FastAPI server directly (the Vite proxy in `vite.config.js` covers `/api` prefix paths only, which are not currently used).

Also set Auth0 frontend vars in `frontend/.env`:
```
VITE_AUTH0_DOMAIN=your-tenant.us.auth0.com
VITE_AUTH0_CLIENT_ID=your-spa-client-id
VITE_AUTH0_AUDIENCE=https://eventboard-api
```

---

## Architecture

**Stack**: FastAPI + SQLAlchemy (SQLite) backend; React 19 + Vite + Tailwind CSS frontend.

### Authentication

**Auth flow**: Auth0 JWT (RS256) via `@auth0/auth0-react` on the frontend; `PyJWT[crypto]` + Auth0 JWKS validation on the backend.

- Roles (`admin`, `user`) are injected as a custom claim `https://eventboard/roles` by an Auth0 Post-Login Action.
- Backend dependency `require_admin` accepts either a valid JWT with the admin role **or** the `X-Admin-Secret` header (service key for cron jobs).
- Backend dependency `require_user` requires any valid JWT.
- Public routes (browse events, subscribe) require no authentication.

**Auth0 setup** (manual, one-time):
1. Create tenant → Single Page Application → copy `Domain` and `Client ID` to `frontend/.env`
2. Create API resource with identifier `https://eventboard-api` → copy to `AUTH0_AUDIENCE`
3. Set callback URL to `http://localhost:5173` (dev) and production URL
4. Create roles `admin` and `user` in Auth0 dashboard
5. Add Post-Login Action:
   ```js
   exports.onExecutePostLogin = async (event, api) => {
     const roles = event.authorization?.roles ?? [];
     api.accessToken.setCustomClaim('https://eventboard/roles', roles);
   };
   ```
6. Assign roles to users via Auth0 dashboard

### Backend

All routes are registered in `backend/main.py`. The data layer is `backend/databridge.py`. `main.py` imports it as `crud` (`from . import databridge as crud`).

Key modules:
- `models.py` — SQLAlchemy ORM: `Location`, `GameSystem`, `Event`, `Subscriber`
- `schemas.py` — Pydantic I/O schemas: `LocationOut`, `EventOut`, `EventIn`, `EventSubmitIn`, `ReviewAction`, `SubscribeIn/Out`
- `databridge.py` — all DB operations; includes `create_user_event()`, `get_pending_events()`, `review_event()`
- `auth.py` — JWT validation (`decode_token`), FastAPI deps (`require_user`, `require_admin`); replaces the old `_verify_admin` header check
- `importer.py` — reads JSON files from `backend/data/`, normalizes records, deduplicates by SHA256 hash of `location_name|game_system|title|date|time`, expires events older than 30 days
- `newsletter.py` — builds HTML email table and sends via SMTP
- `database.py` — SQLite engine at `./events.db`, session factory, `create_tables()` + `_migrate_events_table()` called at app startup

**Event deduplication**: `importer.compute_dedup_hash(location_name, game_system, title, date)` → SHA256 hex. On conflict the existing event is updated (`last_seen_at`, `source_url`, `is_expired=False`) rather than inserted.

**Production serving**: When `frontend/dist/` exists, FastAPI mounts it as static files and serves `index.html` for all non-API routes (SPA fallback).

**CORS**: `allow_origins` is set from the `ALLOWED_ORIGINS` env var (comma-separated). Defaults to `http://localhost:5173,http://localhost:8000`. `allow_credentials=True` is required for JWT auth headers.

### Backend API Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/events` | public | List/filter events |
| POST | `/events` | admin | Create event (direct, no review) |
| POST | `/events/batch` | admin | Batch create events |
| POST | `/events/submit` | user | Submit event for admin review |
| GET | `/locations` | public | List locations |
| GET | `/games` | public | List game systems |
| POST | `/subscribe` | public | Subscribe to email digest |
| POST | `/admin/import` | admin | Ingest data/*.json files |
| POST | `/admin/newsletter` | admin | Send newsletter |
| GET | `/admin/preview-email` | admin | Preview monthly email HTML |
| GET | `/admin/review` | admin | Get pending review queue |
| PATCH | `/admin/events/{id}/review` | admin | Approve or reject submitted event |
| GET | `/health` | public | Health check |

### Frontend

SPA with React Router. Key files:
- `src/App.jsx` — router setup with auth-guarded routes (`/submit`, `/admin`); nav shows Login, Submit Event (when auth'd), Admin (when admin), Email Updates, AuthButton
- `src/main.jsx` — wraps app in `Auth0Provider`
- `src/api.js` — public API calls via axios; also exports `submitEvent()`, `getPendingEvents()`, `reviewEvent()` (token-accepting helpers)
- `src/hooks/useAuthAxios.js` — axios instance that auto-injects Bearer token on every request
- `src/hooks/useIsAdmin.js` — checks `https://eventboard/roles` claim in Auth0 user object
- `src/components/AuthButton.jsx` — login button / user avatar + logout dropdown
- `src/components/RequireAuth.jsx` — route guard for any logged-in user
- `src/components/RequireAdmin.jsx` — route guard for admin role
- `src/pages/SubmitEventPage.jsx` — event submission form (logged-in users)
- `src/pages/AdminReviewPanel.jsx` — approve/reject queue (admin only)
- `src/pages/Home.jsx` — main page: fetches locations + game systems once, fetches events on search
- `src/pages/LocationPage.jsx` — detail page for a single location
- `src/components/FilterBar.jsx` — receives `locations`, `gameSystems`, `filters`, `onChange`, `onSearch` as props
- `src/components/SubscribeForm.jsx` — receives `locations`, `gameSystems` as props

### Database Schema

| Table | Key columns |
|---|---|
| `locations` | `id`, `name`, `city`, `state`, `website`, `discord_url`, `facebook_url` |
| `game_systems` | `id`, `name`, `slug`, `publisher` |
| `events` | `id`, `location_id`, `game_system_id`, `title`, `date`, `start_time`, `description`, `source_url`, `source_type`, `dedup_hash`, `is_expired`, `submitted_by`, `submission_status` |
| `subscribers` | `id`, `email`, `location_ids` (JSON text), `game_system_ids` (JSON text), `is_active` |

`submission_status` values: `"pending_review"` (newly submitted), `"approved"` (admin approved), `"rejected"` (admin rejected — event is also `is_expired=True`). Events ingested via the admin import pipeline have `submission_status=NULL`.

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
