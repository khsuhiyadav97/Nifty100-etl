import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"
PEER_GROUPS_PATH = "data/n100/supporting datasets/peer_groups.xlsx"

METRICS = [
    "return_on_equity_pct",
    "return_on_capital_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
]


def load_peer_groups(path=PEER_GROUPS_PATH):
    """Load peer_groups.xlsx - already shaped as one row per (group, company)."""
    df = pd.read_excel(path, header=0)
    df["company_id"] = df["company_id"].str.strip().str.upper()
    return df[["peer_group_name", "company_id", "is_benchmark"]]


def save_peer_groups_table(peer_df, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("DROP TABLE IF EXISTS peer_groups")
    peer_df.to_sql("peer_groups", conn, if_exists="replace", index=False)
    conn.close()


def compute_peer_percentiles(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)

    ratios_query = """
        SELECT * FROM financial_ratios
        WHERE (company_id, year) IN (
            SELECT company_id, MAX(year) FROM financial_ratios
            WHERE year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
            GROUP BY company_id
        )
    """
    ratios = pd.read_sql(ratios_query, conn)
    peer_groups = pd.read_sql("SELECT * FROM peer_groups", conn)
    conn.close()

    merged = peer_groups.merge(ratios, on="company_id", how="inner")

    for metric in METRICS:
        merged[f"{metric}_pctile"] = merged.groupby("peer_group_name")[metric].rank(pct=True) * 100

    output_cols = ["peer_group_name", "company_id", "year", "is_benchmark"] + \
                  [f"{m}_pctile" for m in METRICS]
    return merged[output_cols]


if __name__ == "__main__":
    print("Loading peer_groups.xlsx...")
    peer_df = load_peer_groups()
    print(f"Loaded {len(peer_df)} (company, group) memberships across "
          f"{peer_df['peer_group_name'].nunique()} groups")

    save_peer_groups_table(peer_df)
    print("Saved peer_groups table to database")

    percentiles = compute_peer_percentiles()
    print(f"\nComputed percentiles for {len(percentiles)} rows")
    print(percentiles.head(15).to_string(index=False))

    percentiles.to_sql("peer_percentiles", sqlite3.connect(DB_PATH),
                        if_exists="replace", index=False)
    print("\nSaved peer_percentiles table to database")