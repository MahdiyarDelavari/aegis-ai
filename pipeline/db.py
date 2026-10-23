import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(database_url)


def main():
    with get_connection() as conn:
        result = conn.execute(
            "SELECT current_database(), current_user"
        ).fetchone()

        print("Database:", result[0])
        print("User:", result[1])


if __name__ == "__main__":
    main()