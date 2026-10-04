"""
Insurance Claims SQL Analysis
=============================
Creates a local SQLite database from the Medical Cost Personal Dataset,
runs the business queries in queries.sql, and saves the result tables
(as CSV) and charts (as PNG) into outputs/.

Each row of the dataset is treated as one policyholder / claim record,
and the `charges` column is treated as the claim amount in USD.

Run:
    python claims_analysis.py
"""

from pathlib import Path
import sqlite3

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "insurance.db"
SQL_PATH = BASE_DIR / "queries.sql"
OUTPUT_DIR = BASE_DIR / "outputs"
DATA_URL = (
    "https://raw.githubusercontent.com/stedy/Machine-Learning-with-R-datasets/"
    "master/insurance.csv"
)

# Output CSV name for each query, in the order the queries appear in queries.sql
QUERY_OUTPUT_NAMES = [
    "q1_claims_by_region",
    "q2_claims_by_smoker",
    "q3_claims_by_age_band",
    "q4_claims_by_children",
    "q5_top_claim_segments",
    "q6_smoker_ratio_by_region",
]


def load_dataset() -> pd.DataFrame:
    """Load the dataset and apply light, explicit cleaning."""
    df = pd.read_csv(DATA_URL)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.dropna().copy()
    df["age"] = df["age"].astype(int)
    df["children"] = df["children"].astype(int)
    df["charges"] = df["charges"].astype(float)
    for col in ("sex", "smoker", "region"):
        df[col] = df[col].astype(str).str.strip().str.lower()
    return df


def create_database(df: pd.DataFrame) -> sqlite3.Connection:
    """(Re)create the SQLite database with a single `claims` table."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("claims", conn, index=False)
    return conn


def split_queries(sql_text: str) -> list[str]:
    """Split queries.sql into individual executable SELECT statements."""
    statements = []
    for chunk in sql_text.split(";"):
        # Keep only chunks that contain a SELECT; comments are fine for SQLite.
        if "select" in chunk.lower():
            statements.append(chunk.strip() + ";")
    return statements


def run_queries(conn: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Execute every query in queries.sql and save each result as CSV."""
    queries = split_queries(SQL_PATH.read_text(encoding="utf-8"))
    if len(queries) != len(QUERY_OUTPUT_NAMES):
        raise ValueError(
            f"Expected {len(QUERY_OUTPUT_NAMES)} queries in queries.sql, "
            f"found {len(queries)}"
        )
    results: dict[str, pd.DataFrame] = {}
    for name, query in zip(QUERY_OUTPUT_NAMES, queries):
        result = pd.read_sql_query(query, conn)
        result.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)
        results[name] = result
        print(f"\n--- {name} ---")
        print(result.to_string(index=False))
    return results


def make_charts(results: dict[str, pd.DataFrame]) -> None:
    """Create the summary charts from the query results."""
    # Chart 1: average claim by region (from Q1)
    by_region = results["q1_claims_by_region"].sort_values("avg_charge")
    plt.figure(figsize=(8, 5))
    plt.barh(by_region["region"], by_region["avg_charge"], color="#3b6ea5")
    plt.xlabel("Average claim (USD)")
    plt.title("Average insurance claim by region")
    for i, v in enumerate(by_region["avg_charge"]):
        plt.text(v, i, f" ${v:,.0f}", va="center")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "avg_claim_by_region.png", dpi=150)
    plt.close()

    # Chart 2: average claim by smoker status (from Q2)
    by_smoker = results["q2_claims_by_smoker"]
    labels = [
        "Smoker" if s == "yes" else "Non-smoker" for s in by_smoker["smoker"]
    ]
    colors = ["#c0392b" if s == "yes" else "#3b6ea5" for s in by_smoker["smoker"]]
    plt.figure(figsize=(7, 5))
    plt.bar(labels, by_smoker["avg_charge"], color=colors)
    plt.ylabel("Average claim (USD)")
    plt.title("Average insurance claim: smoker vs non-smoker")
    for label, v in zip(labels, by_smoker["avg_charge"]):
        plt.text(label, v, f"${v:,.0f}", ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "avg_claim_smoker_vs_non_smoker.png", dpi=150)
    plt.close()

    # Chart 3 (extra): smoker vs non-smoker average claim, grouped by region (Q6)
    ratio = results["q6_smoker_ratio_by_region"]
    x = range(len(ratio))
    plt.figure(figsize=(9, 5))
    plt.bar([i - 0.2 for i in x], ratio["avg_non_smoker_charge"],
            width=0.4, label="Non-smoker", color="#3b6ea5")
    plt.bar([i + 0.2 for i in x], ratio["avg_smoker_charge"],
            width=0.4, label="Smoker", color="#c0392b")
    plt.xticks(list(x), ratio["region"])
    plt.ylabel("Average claim (USD)")
    plt.title("Average claim by region and smoker status")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "avg_claim_by_region_and_smoker.png", dpi=150)
    plt.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading dataset...")
    df = load_dataset()
    print(f"Rows: {len(df):,} | Columns: {', '.join(df.columns)}")

    conn = create_database(df)
    try:
        count = pd.read_sql_query("SELECT COUNT(*) AS n FROM claims", conn)
        print(f"SQLite table `claims` created in {DB_PATH.name}: "
              f"{int(count.loc[0, 'n']):,} rows")
        results = run_queries(conn)
    finally:
        conn.close()

    make_charts(results)
    print(f"\nDone. CSV tables and charts saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
