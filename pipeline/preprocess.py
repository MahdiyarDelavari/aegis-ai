from pathlib import Path
import pandas as pd
import numpy as np


ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    ROOT / "data" / "raw" / "UNSW_NB15_training-set.csv"
)

OUTPUT_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports"

CORE_NUMERIC_COLUMNS = [
    "dur",
    "sbytes",
    "dbytes",
    "spkts",
    "dpkts",
]

REQUIRED_COLUMNS = {
    "id",
    "label",
    "attack_cat",
    "proto",
    "service",
    "state",
    "dur",
    "sbytes",
    "dbytes",
    "spkts",
    "dpkts",
}


def validate_schema(df):
    if df.empty:
        raise ValueError("Dataset is empty")

    if df.columns.duplicated().any():
        raise ValueError("Duplicate column names detected")

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    return True


def load_source():
    if not INPUT_PATH.is_file():
        raise FileNotFoundError(INPUT_PATH)

    return pd.read_csv(INPUT_PATH)


def clean_labels(df):
    labels = pd.to_numeric(
        df["label"],
        errors="coerce"
    )

    valid_mask = labels.isin([0, 1])

    clean = df.loc[valid_mask].copy()
    rejected = df.loc[~valid_mask].copy()

    clean["label"] = labels.loc[valid_mask].astype("int8")

    rejected["reject_reason"] = "invalid_label"

    return clean, rejected


def clean_core_numeric(df):
    result = df.copy()

    for column in CORE_NUMERIC_COLUMNS:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce"
        )

    numeric_data = result[CORE_NUMERIC_COLUMNS]

    invalid_mask = (
        numeric_data.isna().any(axis=1)
        | (numeric_data < 0).any(axis=1)
        | ~np.isfinite(
            numeric_data.to_numpy(dtype=float)
        ).all(axis=1)
    )

    clean = result.loc[~invalid_mask].copy()
    rejected = result.loc[invalid_mask].copy()

    rejected["reject_reason"] = "invalid_core_numeric"

    return clean, rejected

def build_ml_view(df):
    excluded_columns = [
        "id",
        "label",
        "attack_cat",
    ]

    X = df.drop(columns=excluded_columns)
    y = df["label"].copy()

    return X, y

def main():
    df = load_source()

    validate_schema(df)
    print("Schema validation passed!")

    print("AEGIS AI - Data Preprocessing")
    print(f"Loaded rows: {len(df):,}")

    clean_df, rejected_labels = clean_labels(df)

    print("Valid labels:", len(clean_df))
    print("Rejected labels:", len(rejected_labels))

    clean_df, rejected_numeric = clean_core_numeric(
        clean_df
    )

    print("Rows after numeric validation:", len(clean_df))
    print("Invalid numeric rows:", len(rejected_numeric))

    X, y = build_ml_view(clean_df)

    print("Feature Matrix:", X.shape)
    print("Target Vector:", y.shape)


if __name__ == "__main__":
    main()