import sqlite3
import sys
sys.path.append('src/analytics')

from ratios_clean import build_profitability_ratios
from leverage_ratios_clean import build_leverage_ratios
from cashflow_kpis import build_cashflow_kpis

DB_PATH = "data/nifty100.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS financial_ratios (
    company_id TEXT,
    year TEXT,
    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    return_on_capital_pct REAL,
    debt_to_equity REAL,
    interest_coverage REAL,
    asset_turnover REAL,
    free_cash_flow REAL,
    cfo_pat_ratio REAL,
    capex_intensity_pct REAL,
    PRIMARY KEY (company_id, year)
);
"""


def build_combined_ratios_table():
    """Merge profitability, leverage, and cash flow ratios on (company_id, year)."""
    profitability = build_profitability_ratios()
    leverage = build_leverage_ratios()
    cashflow = build_cashflow_kpis()

    merged = profitability.merge(
        leverage[["company_id", "year", "debt_to_equity", "interest_coverage", "asset_turnover"]],
        on=["company_id", "year"], how="outer"
    )
    merged = merged.merge(
        cashflow[["company_id", "year", "free_cash_flow", "cfo_pat_ratio", "capex_intensity_pct"]],
        on=["company_id", "year"], how="outer"
    )
    return merged


def save_to_database(df, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()

    # Fresh reload each run to avoid duplicate-key errors on re-run
    conn.execute("DELETE FROM financial_ratios")
    conn.commit()

    df.to_sql("financial_ratios", conn, if_exists="append", index=False)
    count = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    conn.close()
    return count


if __name__ == "__main__":
    print("Building combined ratios table...")
    ratios = build_combined_ratios_table()
    print(f"Combined rows: {len(ratios)}")

    row_count = save_to_database(ratios)
    print(f"Saved {row_count} rows to financial_ratios table in {DB_PATH}")