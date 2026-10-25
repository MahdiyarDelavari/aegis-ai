from fastapi import FastAPI
from fastapi import Depends

from backend.dependencies import get_db

from backend.schemas import OverviewResponse

SOURCE_SPLIT = "training"

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

@app.get("/api/overview", response_model=OverviewResponse)
def get_overview(conn=Depends(get_db)):

    row = conn.execute(
        """
        SELECT
            COUNT(*),
            COUNT(*) FILTER (WHERE label = 0),
            COUNT(*) FILTER (WHERE label = 1),
            COUNT(DISTINCT proto)
        FROM network_flows
        WHERE source_split = %s
        """,
        (SOURCE_SPLIT,)
    ).fetchone()

    total, normal, attack, protocols = row

    attack_percentage = (
        round(attack / total * 100, 2)
        if total > 0 else 0.0
    )

    return OverviewResponse(
        total_flows=total,
        normal_flows=normal,
        attack_flows=attack,
        attack_percentage=attack_percentage,
        unique_protocols=protocols
    )