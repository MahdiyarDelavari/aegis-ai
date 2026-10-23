from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    ROOT / "data" / "raw" / "UNSW_NB15_training-set.csv"
)

OUTPUT_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports"


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


def main():
    df = load_source()

    validate_schema(df)
    print("Schema validation passed!")

    print("AEGIS AI - Data Preprocessing")
    print(f"Loaded rows: {len(df):,}")


if __name__ == "__main__":
    main()