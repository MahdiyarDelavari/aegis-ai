import unittest
import pandas as pd

from pipeline.eda import (
    class_distribution,
    quality_summary,
)


class TestEDA(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            "label": [0, 1, 1],
            "attack_cat": ["Normal", "DoS", "Exploits"],
            "proto": ["tcp", "udp", "tcp"],
            "dur": [0.1, 0.2, 0.3],
            "sbytes": [100, 200, 300],
            "dbytes": [50, 60, 70],
        })

    def test_class_distribution(self):
        counts = class_distribution(self.df)

        self.assertEqual(counts["Normal"], 1)
        self.assertEqual(counts["Attack"], 2)

    def test_missing_values(self):
        quality = quality_summary(self.df)

        self.assertEqual(quality["missing_cells"], 0)

    def test_detect_missing_value(self):
        self.df.loc[0, "dur"] = None

        quality = quality_summary(self.df)

        self.assertEqual(quality["missing_cells"], 1)

    def test_negative_bytes(self):
        self.df.loc[0, "sbytes"] = -100

        quality = quality_summary(self.df)

        self.assertEqual(quality["negative_bytes"], 1)


if __name__ == "__main__":
    unittest.main()