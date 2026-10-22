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


def main():
    df = load_data()

    print("AEGIS AI - Exploratory Data Analysis")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {df.shape[1]}")


if __name__ == "__main__":
    main()