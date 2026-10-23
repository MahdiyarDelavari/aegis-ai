import json
import unittest

import numpy as np

from pipeline.db import get_connection
from pipeline.ingest import (
    ROOT,
    SOURCE_SPLIT,
    normalize,
    make_flow_params,
)


class TestIngestion(unittest.TestCase):

    def setUp(self):
        self.record = {
            "id": 1,
            "label": 1,
            "attack_cat": "Exploits",
            "proto": "tcp",
            "service": "http",
            "state": "FIN",
            "dur": 0.5,
            "sbytes": 100,
            "dbytes": 200,
            "spkts": 2,
            "dpkts": 3,
            "sttl": 64,
        }

    def test_numpy_scalar(self):
        result = normalize(np.int64(10))
        self.assertEqual(result, 10)

    def test_missing_value(self):
        self.assertIsNone(normalize(np.nan))

    def test_flow_parameters(self):
        params = make_flow_params(self.record)

        self.assertEqual(params[0], "training")
        self.assertEqual(params[1], 1)
        self.assertEqual(params[2], 1)
        self.assertEqual(params[7], 0.5)

    def test_invalid_source_id(self):
        self.record["id"] = None

        with self.assertRaises(ValueError):
            make_flow_params(self.record)

    def test_database_reconciliation(self):
        report = json.loads(
            (ROOT / "reports" / "preprocessing_summary.json")
            .read_text(encoding="utf-8")
        )

        with get_connection() as conn:
            valid = conn.execute(
                """
                SELECT COUNT(*) FROM network_flows
                WHERE source_split = %s
                """,
                (SOURCE_SPLIT,)
            ).fetchone()[0]

            rejected = conn.execute(
                """
                SELECT COUNT(*) FROM rejected_records
                WHERE source_split = %s
                """,
                (SOURCE_SPLIT,)
            ).fetchone()[0]

        self.assertEqual(valid, report["clean_rows"])
        self.assertEqual(rejected, report["rejected_rows"])


if __name__ == "__main__":
    unittest.main()