from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    ROOT / "data" / "raw" / "UNSW_NB15_training-set.csv"
)

REPORT_DIR = ROOT / "reports"
CHART_DIR = REPORT_DIR / "figures"

REQUIRED_COLUMNS = {
    "label",
    "attack_cat",
    "proto",
    "dur",
    "sbytes",
    "dbytes",
}

def load_data():
    if not DATA_PATH.is_file():
        raise FileNotFoundError(DATA_PATH)

    df = pd.read_csv(DATA_PATH)

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df


def quality_summary(df):
    return {
        "missing_cells": int(df.isna().sum().sum()),
        "missing_labels": int(df["label"].isna().sum()),
        "exact_duplicates": int(df.duplicated().sum()),
        "negative_bytes": int(
            (
                (df["sbytes"] < 0) |
                (df["dbytes"] < 0)
            ).sum()
        ),
    }

def main():
    df = load_data()

    print("AEGIS AI - Exploratory Data Analysis")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {df.shape[1]}")

    quality = quality_summary(df)

    print("\nData Quality:")
    print(quality)

    missing_by_column = df.isna().sum()
    missing_by_column = missing_by_column[
        missing_by_column > 0
    ]

    print("\nColumns with missing values:")
    print(missing_by_column.sort_values(ascending=False))

    print(df["label"].value_counts(dropna=False))


if __name__ == "__main__":
    main()