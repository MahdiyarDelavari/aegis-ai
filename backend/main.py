from fastapi import FastAPI
from fastapi import Depends

from backend.dependencies import get_db


app = FastAPI(
    title="AEGIS AI API",
    description="Network Traffic Intelligence Platform",
    version="0.5.0"
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "AEGIS AI API"
    }

@app.get("/api/health/db")
def database_health(conn=Depends(get_db)):
    result = conn.execute("SELECT 1").fetchone()

    return {
        "status": "ok",
        "database": "postgresql",
        "connected": result[0] == 1
    }