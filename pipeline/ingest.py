import math
from pathlib import Path

import numpy as np
import pandas as pd
from psycopg.types.json import Jsonb

from pipeline.db import get_connection

ROOT = Path(__file__).resolve().parent.parent

CLEAN_PATH = ROOT / "data" / "processed" / "training_clean.csv"

BATCH_SIZE = 1000
SOURCE_SPLIT = "training"

FIXED_COLUMNS = {
    "id", "label", "attack_cat",
    "proto", "service", "state",
    "dur", "sbytes", "dbytes",
    "spkts", "dpkts",
}


def normalize(value):
    if isinstance(value, np.generic):
        value = value.item()

    if value is None or pd.isna(value):
        return None

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value



def make_flow_params(record):
    source_id = normalize(record["id"])

    if (
        isinstance(source_id, bool)
        or not isinstance(source_id, (int, float))
        or (
            isinstance(source_id, float)
            and not source_id.is_integer()
        )
    ):
        raise ValueError("Invalid source record ID")

    extra_features = {
        key: normalize(value)
        for key, value in record.items()
        if key not in FIXED_COLUMNS
    }

    return (
        SOURCE_SPLIT,
        int(source_id),
        int(record["label"]),
        normalize(record["attack_cat"]),
        normalize(record["proto"]),
        normalize(record["service"]),
        normalize(record["state"]),
        normalize(record["dur"]),
        normalize(record["sbytes"]),
        normalize(record["dbytes"]),
        normalize(record["spkts"]),
        normalize(record["dpkts"]),
        Jsonb(extra_features),
    )


UPSERT_FLOW_SQL = """
INSERT INTO network_flows (
    source_split, source_id,
    label, attack_cat, proto, service, state,
    dur, sbytes, dbytes, spkts, dpkts,
    extra_features
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s
)
ON CONFLICT (source_split, source_id)
DO UPDATE SET
    label = EXCLUDED.label,
    attack_cat = EXCLUDED.attack_cat,
    proto = EXCLUDED.proto,
    service = EXCLUDED.service,
    state = EXCLUDED.state,
    dur = EXCLUDED.dur,
    sbytes = EXCLUDED.sbytes,
    dbytes = EXCLUDED.dbytes,
    spkts = EXCLUDED.spkts,
    dpkts = EXCLUDED.dpkts,
    extra_features = EXCLUDED.extra_features
"""

def ingest_flows(conn):
    if not CLEAN_PATH.is_file():
        raise FileNotFoundError(CLEAN_PATH)

    total = 0
    seen_ids = set()

    for chunk in pd.read_csv(
        CLEAN_PATH,
        chunksize=BATCH_SIZE
    ):
        records = chunk.to_dict(orient="records")
        params = [make_flow_params(r) for r in records]

        for row in params:
            source_id = row[1]

            if source_id in seen_ids:
                raise ValueError(
                    f"Duplicate source ID: {source_id}"
                )

            seen_ids.add(source_id)

        with conn.cursor() as cursor:
            cursor.executemany(
                UPSERT_FLOW_SQL,
                params
            )

        total += len(params)
        print(f"Processed {total:,} flows")

    return total



def main():
    with get_connection() as conn:
        count = ingest_flows(conn)

    print(f"Completed: {count:,} flows processed")


if __name__ == "__main__":
    main()