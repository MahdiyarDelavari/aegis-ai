import psycopg
from fastapi import HTTPException

from pipeline.db import get_connection


def get_db():
    try:
        with get_connection() as conn:
            yield conn

    except psycopg.OperationalError as error:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        ) from error