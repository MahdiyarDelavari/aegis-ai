
# AEGIS AI

AEGIS AI is a network traffic intelligence platform for ingesting, cleaning,
analyzing, and monitoring network-flow data.

## What is included

- **Data pipeline:** ingestion, preprocessing, exploratory analysis, and
  PostgreSQL persistence
- **Analytics API:** FastAPI endpoints for overview metrics, traffic classes,
  attack categories, protocols, flows, pipeline runs, and health checks
- **Web dashboard:** responsive, dependency-free HTML/CSS/JavaScript frontend
  served directly by FastAPI
- **Reporting:** dataset quality, class distribution, attack categories, and
  preprocessing summaries in `reports/`

Machine-learning threat detection and incident workflows are planned but are
not enabled yet.

## Tech stack

- Python 3.12+
- FastAPI and Uvicorn
- PostgreSQL
- Pandas, NumPy, Matplotlib, and scikit-learn
- HTML, CSS, and JavaScript modules

## Run locally

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

2. Copy the environment template and configure the database connection:

   ```bash
   cp .env.example .env
   ```

3. Start PostgreSQL:

   ```bash
   docker compose up -d db
   ```

4. Start the API and dashboard from the repository root:

   ```bash
   .venv/bin/uvicorn backend.main:app --reload
   ```

5. Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

The dashboard and API share the same origin, so there is no separate frontend
build or development server.

## API endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Check API availability |
| `GET /api/health/db` | Check PostgreSQL connectivity |
| `GET /api/overview` | Get headline flow metrics |
| `GET /api/traffic/classes` | Get normal/attack distribution |
| `GET /api/attacks/top` | Get the most common attack categories |
| `GET /api/protocols/top` | Get the most active protocols |
| `GET /api/flows` | Browse paginated network flows |
| `GET /api/pipeline/runs` | Review ingestion history |

Interactive API documentation is available at
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Project layout

```text
backend/     FastAPI application, schemas, and database dependency
frontend/    Dashboard HTML, CSS, and JavaScript
pipeline/    Data ingestion, preprocessing, EDA, and database helpers
reports/     Generated summaries and figures
sql/         PostgreSQL schema and analytics queries
tests/       Unit and API tests
```

## Validation

Run the API and frontend smoke tests with:

```bash
.venv/bin/python -m unittest tests.test_api -q
```

Run the full test suite with:

```bash
.venv/bin/python -m unittest discover -s tests -q
```

Some ingestion tests require a configured `DATABASE_URL` and a reachable
PostgreSQL instance.

## Project status

**Phase 1 — Foundation:** data pipeline, analytics API, and dashboard surfaces
are implemented. Machine-learning detection and incident monitoring remain
future phases.
