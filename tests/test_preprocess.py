import unittest
import pandas as pd

from pipeline.preprocess import (
    validate_schema,
    clean_labels,
    clean_core_numeric,
    build_ml_view,
)


class TestPreprocessing(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "id": [1, 2, 3],
            "label": [0, 1, 1],
            "attack_cat": ["Normal", "DoS", "Exploits"],
            "proto": ["tcp", "udp", "tcp"],
            "service": ["http", "-", "dns"],
            "state": ["FIN", "CON", "FIN"],
            "dur": [0.1, 0.2, 0.3],
            "sbytes": [100, 200, 300],
            "dbytes": [50, 60, 70],
            "spkts": [2, 3, 4],
            "dpkts": [1, 2, 3],
        })

    def test_valid_schema(self):
        self.assertTrue(validate_schema(self.df))

    def test_missing_column(self):
        df = self.df.drop(columns=["label"])

        with self.assertRaises(ValueError):
            validate_schema(df)

    def test_invalid_label(self):
        self.df.loc[0, "label"] = 5

        clean, rejected = clean_labels(self.df)

        self.assertEqual(len(clean), 2)
        self.assertEqual(len(rejected), 1)

    def test_negative_bytes(self):
        self.df.loc[0, "sbytes"] = -100

        clean, rejected = clean_core_numeric(self.df)

        self.assertEqual(len(clean), 2)
        self.assertEqual(len(rejected), 1)

    def test_invalid_numeric_string(self):
        self.df["dur"] = self.df["dur"].astype(object)
        self.df.loc[0, "dur"] = "invalid"

        clean, rejected = clean_core_numeric(self.df)

        self.assertEqual(len(clean), 2)
        self.assertEqual(len(rejected), 1)

    def test_ml_features_no_leakage(self):
        X, y = build_ml_view(self.df)

        self.assertNotIn("label", X.columns)
        self.assertNotIn("attack_cat", X.columns)
        self.assertNotIn("id", X.columns)
        self.assertEqual(len(X), len(y))


if __name__ == "__main__":
    unittest.main()