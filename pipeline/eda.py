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


def class_distribution(df):
    return (
        df["label"]
        .value_counts()
        .reindex([0, 1], fill_value=0)
        .rename(index={0: "Normal", 1: "Attack"})
    )


def print_section(number, title):
    print("\n" + "=" * 80)
    print(f"SECTION {number}: {title}")
    print("=" * 80)


def main():
    df = load_data()

    print_section(1, "DATASET OVERVIEW")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {df.shape[1]}")

    quality = quality_summary(df)

    print_section(2, "DATA QUALITY SUMMARY")
    print(quality)

    missing_by_column = df.isna().sum()
    missing_by_column = missing_by_column[
        missing_by_column > 0
    ]

    print_section(3, "MISSING VALUES BY COLUMN")
    print(missing_by_column.sort_values(ascending=False))

    print_section(4, "LABEL DISTRIBUTION")
    print(df["label"].value_counts(dropna=False))

    class_counts = class_distribution(df)

    print_section(5, "TRAFFIC CLASS DISTRIBUTION")
    print(class_counts)

    percentages = (class_counts / len(df)) * 100

    print_section(6, "CLASS PERCENTAGES")
    print(percentages.round(2))

    print_section(7, "ATTACK CATEGORIES")

    attack_counts = (
        df.loc[df["label"] == 1, "attack_cat"]
        .fillna("Unknown")
        .value_counts()
    )

    print(attack_counts)


    print_section(8, "TOP 10 NETWORK PROTOCOLS")

    top_protocols = df["proto"].value_counts().head(10)

    print(top_protocols)


if __name__ == "__main__":
    main()