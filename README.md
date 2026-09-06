# SiteLens

SiteLens is an AI Website Reverse Engineer. You give it a public website URL,
and it eventually analyzes what's observable from the outside — structure,
pages, technologies, network requests, assets, performance, design patterns,
SEO, accessibility, and likely architecture — then explains how the site
probably works.

SiteLens is built to clearly separate **observed facts** from **inferred
information**, and it never pretends to have access to private source code,
databases, credentials, or backend infrastructure that isn't publicly
observable.

## Current status: Part 1 — Foundation

This is the first increment. It only sets up the working skeleton:

- A landing page where you can submit a URL
- A backend that validates the URL and creates a `Scan` record
- A scan page that shows placeholder pipeline steps alongside the real scan
  status returned by the backend

**No actual website analysis happens yet.** There is no crawling, no
Playwright, no AI, no technology detection, no network/performance/SEO/
accessibility analysis, and no architecture inference. Submitting a URL only
creates a scan record with status `QUEUED`. That's the honest, current
behavior — later parts will build the real pipeline on top of this
foundation.

## Tech stack

**Frontend:** React, TypeScript, Vite, Tailwind CSS, React Router, Lucide React

**Backend:** Python, FastAPI, SQLAlchemy, Alembic

**Database:** PostgreSQL-compatible. SQLite is used by default for local
development (zero setup); PostgreSQL is available via `docker-compose` and is
a drop-in swap via `DATABASE_URL` — no code changes required either way.

## Project structure

```text
sitelens/
├── frontend/          # React + Vite app
│   └── src/
│       ├── api/       # Typed API client (create/get scan, get status)
│       ├── components/
│       ├── lib/        # Client-side URL validation
│       └── pages/      # Landing, ScanPage
├── backend/           # FastAPI app
│   └── app/
│       ├── api/        # Route handlers (scans)
│       ├── db/         # Engine/session setup
│       ├── schemas/     # Pydantic request/response models
│       ├── models.py    # SQLAlchemy Scan model
│       ├── url_validation.py
│       ├── config.py
│       └── main.py
│   └── alembic/         # Migrations
├── README.md
├── .env.example
├── .gitignore
└── docker-compose.yml
```

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env    # sets VITE_API_BASE_URL to point at the backend
npm run dev
```

The app runs at `http://localhost:5173`.

To type-check or build for production:

```bash
npx tsc --noEmit
npm run build
```

## Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Configure the database (optional — defaults to a local SQLite file):

```bash
cp ../.env.example .env
# edit .env if you want DATABASE_URL to point somewhere else
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

The API runs at `http://localhost:8000`, with interactive docs at
`http://localhost:8000/docs`.

## Database & migrations

The `Scan` model lives in `backend/app/models.py`:

```text
id, url, normalized_url, status, created_at, completed_at, error
```

Run migrations (creates the `scans` table):

```bash
cd backend
alembic upgrade head
```

To create a new migration after changing models:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

### Switching to PostgreSQL

Set `DATABASE_URL` in `backend/.env` to a PostgreSQL connection string, e.g.:

```text
DATABASE_URL=postgresql+psycopg://sitelens:sitelens@localhost:5432/sitelens
```

Then re-run `alembic upgrade head` against that database. The `psycopg`
driver is already included in `requirements.txt`, so no extra install is
needed. This is exactly the connection string `docker-compose` wires up
automatically for the `db` service (see below).

## Environment variables

All variables are documented in `.env.example` at the project root.

| Variable | Used by | Purpose | Default |
|---|---|---|---|
| `DATABASE_URL` | backend | SQLAlchemy connection string | `sqlite:///./sitelens.db` |
| `CORS_ORIGINS` | backend | Comma-separated allowed origins | `http://localhost:5173` |
| `VITE_API_BASE_URL` | frontend | Base URL the frontend calls | `http://localhost:8000` |
| `POSTGRES_USER` | docker-compose | Postgres username | `sitelens` |
| `POSTGRES_PASSWORD` | docker-compose | Postgres password | `sitelens` |
| `POSTGRES_DB` | docker-compose | Postgres database name | `sitelens` |

None of these defaults are real secrets — they're local development
placeholders. Use your own values (and a real secrets manager) for any
non-local environment.

## Running the project

**Option A — without Docker (SQLite, fastest for local dev):**

1. Start the backend (see Backend setup above) — runs on port 8000
2. Start the frontend (see Frontend setup above) — runs on port 5173
3. Open `http://localhost:5173`

**Option B — with Docker (PostgreSQL):**

```bash
docker compose up --build
```

This starts:
- `db` — PostgreSQL 16, with a persisted named volume
- `backend` — FastAPI, connected to `db` via `DATABASE_URL` (waits for
  Postgres's healthcheck before starting)
- `frontend` — Vite dev server

You'll still need to run migrations against the containerized database once
it's up:

```bash
docker compose exec backend alembic upgrade head
```

### Try it

Open the app, enter a URL like `https://example.com`, and submit. You'll be
redirected to `/scan/:scanId`, which shows the placeholder pipeline steps and
the real `QUEUED` status returned by the backend. Try an invalid value (no
`http://`/`https://`, or a malformed host) and confirm it's rejected before
it ever reaches the backend.

## API

```text
POST /api/scans                     Create a scan (validates + normalizes the URL, status=QUEUED)
GET  /api/scans/{scan_id}           Get full scan details
GET  /api/scans/{scan_id}/status    Get just the scan's status
```

## Current limitations

- No website is actually analyzed — scans are created and stay `QUEUED`
- No crawling, browser automation, or network capture of any kind
- No AI involvement anywhere in this codebase yet
- No technology detection, performance/SEO/accessibility checks, or
  architecture inference
- No scan history or dashboard beyond a single scan's status page
- SSRF protection is limited to basic URL/scheme validation — it does not
  yet block private/internal IP ranges, follow redirects safely, or guard
  against DNS rebinding. That hardening belongs with the real scanner and
  will be added when that pipeline exists.

## Roadmap (future parts)

- **Scanner pipeline**: Playwright-based capture of a live page (DOM,
  screenshots, network requests)
- **Technology detection**: identify frameworks, libraries, CMS, hosting,
  and infra signals from observable evidence
- **Network analysis**: catalog requests, endpoints, third-party services,
  and headers
- **Performance analysis**: load timing, asset weight, render-blocking
  resources
- **SEO & accessibility analysis**: meta tags, structured data, a11y audits
- **Architecture inference**: an AI-generated explanation of the site's
  likely architecture, clearly labeled as inferred rather than observed
- **AI synthesis**: a natural-language summary tying all findings together
- **Scan history**: list and revisit past scans
- **Fuller dashboard**: richer visualization of everything above

None of the above is implemented in this repository yet.
