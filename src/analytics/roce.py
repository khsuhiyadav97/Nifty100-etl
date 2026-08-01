import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"

# Approximate sector ROE ranges from the project spec (Section 28: Sector Benchmarks)
SECTOR_ROE_RANGES = {
    "Financials": (12, 22),
    "Energy": (8, 18),
    "Information Technology": (25, 50),
    "Consumer Staples": (20, 45),
    "Healthcare": (15, 30),
    "Consumer Discretionary": (10, 25),
    "Materials": (10, 25),
    "Industrials": (12, 22),
    "Conglomerates": (10, 20),
    "Real Estate": (10, 20),
    "Communication Services": (10, 20),
}
DEFAULT_RANGE = (10, 25)  # fallback for any sector not in the table


def sector_relative_flag(roe_value, broad_sector):
    """Compare ROE against its sector's typical range instead of a universal bar."""
    if roe_value is None or pd.isna(roe_value):
        return "N/A"

    low, high = SECTOR_ROE_RANGES.get(broad_sector, DEFAULT_RANGE)
    if roe_value < low:
        return "Below Sector Range"
    elif roe_value > high:
        return "Above Sector Range"
    return "Within Sector Range"


def load_roce_data(conn):
    """Join computed ROE inputs with sector info and the reference roce_percentage."""
    query = """
        SELECT p.company_id, p.year, p.net_profit,
               b.equity_capital, b.reserves,
               s.broad_sector,
               c.roce_percentage AS reference_roce
        FROM profitandloss p
        JOIN balancesheet b ON p.company_id = b.company_id AND p.year = b.year
        LEFT JOIN sectors s ON p.company_id = s.company_id
        LEFT JOIN companies c ON p.company_id = c.id
    """
    return pd.read_sql(query, conn)


def build_sector_roce_report(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    df = load_roce_data(conn)
    conn.close()

    rows = []
    for _, r in df.iterrows():
        total_equity = r["equity_capital"] + r["reserves"]
        computed_roe = None
        if pd.notna(total_equity) and total_equity > 0:
            computed_roe = (r["net_profit"] / total_equity) * 100

        flag = sector_relative_flag(computed_roe, r["broad_sector"])

        anomaly = None
        if computed_roe is not None and pd.notna(r["reference_roce"]):
            diff = abs(computed_roe - r["reference_roce"])
            if diff > 10:
                anomaly = f"Diff of {diff:.1f} pts vs reference"

        rows.append({
            "company_id": r["company_id"],
            "year": r["year"],
            "broad_sector": r["broad_sector"],
            "computed_roe_pct": computed_roe,
            "sector_flag": flag,
            "reference_roce_pct": r["reference_roce"],
            "anomaly_note": anomaly,
        })

    return pd.DataFrame(rows)


def summarize_and_save(df: pd.DataFrame):
    print(df.head(10))
    print(f"\nTotal rows: {len(df)}")
    print("\nSector flag distribution:")
    print(df["sector_flag"].value_counts())

    anomalies = df[df["anomaly_note"].notna()]
    print(f"\nAnomalies found (>10pt diff vs reference): {len(anomalies)}")

    anomalies.to_csv("output/sector_roce_notes.csv", index=False)
    print("Saved output/sector_roce_notes.csv")


if __name__ == "__main__":
    roce_df = build_sector_roce_report()
    summarize_and_save(roce_df)