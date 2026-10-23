from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    ROOT / "data" / "raw" / "UNSW_NB15_training-set.csv"
)

OUTPUT_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports"


def load_source():
    if not INPUT_PATH.is_file():
        raise FileNotFoundError(INPUT_PATH)

    return pd.read_csv(INPUT_PATH)


def main():
    df = load_source()

    print("AEGIS AI - Data Preprocessing")
    print(f"Loaded rows: {len(df):,}")


if __name__ == "__main__":
    main()