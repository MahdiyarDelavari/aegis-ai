from fastapi import FastAPI
from fastapi import Depends

from backend.dependencies import get_db

from backend.schemas import OverviewResponse
from fastapi import Query

from backend.schemas import FlowPage

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

@app.get("/api/traffic/classes")
def get_traffic_classes(conn=Depends(get_db)):

    rows = conn.execute(
        """
        SELECT
            label,
            COUNT(*) AS flow_count,
            SUM(COUNT(*)) OVER () AS total_count
        FROM network_flows
        WHERE source_split = %s
        GROUP BY label
        ORDER BY label
        """,
        (SOURCE_SPLIT,)
    ).fetchall()

    result = []

    for label, count, total in rows:
        result.append({
            "label": label,
            "name": "Normal" if label == 0 else "Attack",
            "count": count,
            "percentage": round(count / total * 100, 2)
        })

    return result


@app.get("/api/attacks/top")
def get_top_attacks(
    limit: int = Query(10, ge=1, le=30),
    conn=Depends(get_db)
):
    rows = conn.execute(
        """
        SELECT
            attack_cat,
            COUNT(*) AS flow_count,
            ROUND(AVG(dur)::numeric, 3) AS avg_duration
        FROM network_flows
        WHERE source_split = %s
          AND label = 1
        GROUP BY attack_cat
        ORDER BY flow_count DESC, attack_cat
        LIMIT %s
        """,
        (SOURCE_SPLIT, limit)
    ).fetchall()

    return [
        {
            "attack_category": category or "Unknown",
            "count": count,
            "avg_duration": float(avg_duration)
        }
        for category, count, avg_duration in rows
    ]

@app.get("/api/protocols/top")
def get_top_protocols(
    limit: int = Query(10, ge=1, le=30),
    conn=Depends(get_db)
):
    rows = conn.execute(
        """
        SELECT
            proto,
            COUNT(*) AS flow_count,
            SUM(sbytes) AS total_source_bytes,
            SUM(dbytes) AS total_destination_bytes
        FROM network_flows
        WHERE source_split = %s
        GROUP BY proto
        ORDER BY flow_count DESC, proto
        LIMIT %s
        """,
        (SOURCE_SPLIT, limit)
    ).fetchall()

    return [
        {
            "protocol": proto,
            "count": count,
            "source_bytes": source_bytes,
            "destination_bytes": destination_bytes
        }
        for proto, count, source_bytes, destination_bytes in rows
    ]

@app.get("/api/flows", response_model=FlowPage)
def get_flows(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    label: int | None = Query(None, ge=0, le=1),
    conn=Depends(get_db)
):
    where_sql = "WHERE source_split = %s"
    params = [SOURCE_SPLIT]

    if label is not None:
        where_sql += " AND label = %s"
        params.append(label)

    total = conn.execute(
        f"""
        SELECT COUNT(*)
        FROM network_flows
        {where_sql}
        """,
        tuple(params)
    ).fetchone()[0]

    offset = (page - 1) * size

    rows = conn.execute(
        f"""
        SELECT
            source_id,
            label,
            attack_cat,
            proto,
            dur,
            sbytes,
            dbytes
        FROM network_flows
        {where_sql}
        ORDER BY source_id
        LIMIT %s OFFSET %s
        """,
        (*params, size, offset)
    ).fetchall()

    columns = [
        "source_id",
        "label",
        "attack_cat",
        "proto",
        "dur",
        "sbytes",
        "dbytes"
    ]

    items = [
        dict(zip(columns, row))
        for row in rows
    ]

    return {
        "page": page,
        "size": size,
        "total": total,
        "items": items
    }