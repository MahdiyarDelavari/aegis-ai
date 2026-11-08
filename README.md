
# AEGIS AI

An AI-powered network traffic analysis
and threat detection platform.

## Tech Stack

- Python
- PostgreSQL
- Pandas / NumPy
- Matplotlib
- Scikit-learn
- FastAPI
- HTML / CSS / JavaScript

## Features (Planned)

- Network Data Ingestion
- Data Cleaning and Validation
- Traffic Analytics
- Machine Learning Threat Detection
- Incident Monitoring
- Interactive Web Dashboard

## Dashboard

The frontend is a dependency-free HTML, CSS, and JavaScript dashboard served
by FastAPI. It provides:

- Traffic composition and attack-category analytics
- Protocol activity summaries
- Paginated flow exploration with label filters
- Pipeline run history
- API health and refresh state

Start the API from the repository root:

```bash
uvicorn backend.main:app --reload
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000). The dashboard calls
the API under the same origin, so no separate frontend build step is required.

## Project Status

Phase 1: Foundation / dashboard surfaces connected to analytics API
