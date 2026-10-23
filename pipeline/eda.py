from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


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


def save_charts(class_counts, attack_counts):
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    # Chart 1
    fig, ax = plt.subplots(figsize=(7, 4))

    ax.bar(class_counts.index, class_counts.values)
    ax.set_title("Network Traffic Classes")
    ax.set_ylabel("Number of Flows")

    fig.tight_layout()
    fig.savefig(CHART_DIR / "class_distribution.png", dpi=150)
    plt.close(fig)

    # Chart 2
    sorted_attacks = attack_counts.sort_values()

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.barh(sorted_attacks.index, sorted_attacks.values)
    ax.set_title("Attack Categories")
    ax.set_xlabel("Number of Flows")

    fig.tight_layout()
    fig.savefig(CHART_DIR / "attack_categories.png", dpi=150)
    plt.close(fig)


def write_report(df, quality, classes, attacks, medians):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    lines = [
        "# AEGIS AI — EDA Report",
        "",
        "## Dataset",
        f"- Total rows: {len(df):,}",
        f"- Total columns: {df.shape[1]}",
        "",
        "## Data Quality",
        f"- Missing cells: {quality['missing_cells']}",
        f"- Missing labels: {quality['missing_labels']}",
        f"- Exact duplicates: {quality['exact_duplicates']}",
        f"- Negative byte records: {quality['negative_bytes']}",
        "",
        "## Traffic Classes",
    ]

    for name, count in classes.items():
        percentage = count / len(df) * 100
        lines.append(f"- {name}: {count:,} ({percentage:.2f}%)")

    lines.extend(["", "## Attack Categories"])

    for name, count in attacks.items():
        lines.append(f"- {name}: {count:,}")

    lines.extend(["", "## Median Statistics"])

    for name, row in medians.iterrows():
        lines.append(
            f"- {name}: duration={row['dur']:.2f}s, "
            f"sbytes={row['sbytes']:.2f}, "
            f"dbytes={row['dbytes']:.2f}"
        )

    lines.extend([
        "",
        "## Limitations",
        "- Historical laboratory-generated dataset.",
        "- Class frequencies do not represent live production traffic.",
        "- No ML model has been trained yet.",
    ])

    report_path = REPORT_DIR / "eda_summary.md"

    report_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    return report_path

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


    print_section(9, "NUMERICAL FEATURE ANALYSIS")
    numerical_features = ["dur", "sbytes", "dbytes"]
    median_by_label = (
        df.groupby("label")[numerical_features]
        .median()
        .rename(index={0: "Normal", 1: "Attack"})
        .round(2)
    )
    print(median_by_label)


    print_section(10, "GENERATING CHARTS")
    save_charts(class_counts, attack_counts)
    print("Charts generated successfully!")


    print_section(11, "GENERATING EDA REPORT")
    report_path = write_report(
        df,
        quality,
        class_counts,
        attack_counts,
        median_by_label
    )
    print(f"Report saved: {report_path}")


if __name__ == "__main__":
    main()