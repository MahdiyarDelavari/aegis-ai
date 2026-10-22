from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "UNSW_NB15_training-set.csv"
)

def main():
    print("AEGIS AI - Data Explorer")
    print("------------------------")

    if not DATA_PATH.exists():
        print("Dataset not found!")
        return

    df = pd.read_csv(DATA_PATH)

    print("\nDataset Shape:")
    print(df.shape)

    print("\nFirst 5 Rows:")
    print(df.head())

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

if __name__ == "__main__":
    main()