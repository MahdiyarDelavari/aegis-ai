from pathlib import Path
import pandas as pd
import numpy as np
import json

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


def save_outputs(raw, clean, rejected, feature_columns):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    clean.to_csv(
        OUTPUT_DIR / "training_clean.csv",
        index=False
    )

    rejected.to_csv(
        OUTPUT_DIR / "rejected_rows.csv",
        index=False
    )

    report = {
        "source_rows": int(len(raw)),
        "clean_rows": int(len(clean)),
        "rejected_rows": int(len(rejected)),
        "rejection_reasons": {
            str(k): int(v)
            for k, v in rejected["reject_reason"]
                .value_counts().items()
        },
        "missing_cells_in_clean_data": int(
            clean.isna().sum().sum()
        ),
        "label_distribution": {
            str(k): int(v)
            for k, v in clean["label"].value_counts().items()
        },
        "feature_columns": list(feature_columns),
    }

    report_path = REPORT_DIR / "preprocessing_summary.json"

    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return report_path

def main():
    print("=" * 70)
    print("AEGIS AI - DATA PREPROCESSING")
    print("=" * 70)

    # 1. Load
    raw_df = load_source()
    print("Source rows:", len(raw_df))

    # 2. Schema validation
    validate_schema(raw_df)
    print("Schema validation passed")

    # 3. Label validation
    labeled_df, rejected_labels = clean_labels(raw_df)

    # 4. Numeric validation
    clean_df, rejected_numeric = clean_core_numeric(
        labeled_df
    )

    # 5. Combine rejected rows
    rejected_df = pd.concat(
        [rejected_labels, rejected_numeric],
        ignore_index=True
    )

    # 6. Build ML feature view
    X, y = build_ml_view(clean_df)

    # 7. Ensure no records were lost
    assert len(clean_df) + len(rejected_df) == len(raw_df)

    # 8. Save results
    report_path = save_outputs(
        raw_df,
        clean_df,
        rejected_df,
        X.columns
    )

    print("=" * 70)
    print("PREPROCESSING COMPLETED")
    print("=" * 70)

    print("Clean rows:", len(clean_df))
    print("Rejected rows:", len(rejected_df))
    print("Feature shape:", X.shape)
    print("Target shape:", y.shape)
    print("Report:", report_path)


if __name__ == "__main__":
    main()