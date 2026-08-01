import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"


def debt_to_equity(borrowings, equity_capital, reserves, is_financial=False):
    """D/E = borrowings / (equity_capital + reserves).
    Returns (ratio, high_leverage_flag). Flag is only raised for non-financial
    companies with D/E > 5, since high debt is structurally normal for banks/NBFCs.
    """
    total_equity = equity_capital + reserves
    if pd.isna(total_equity) or total_equity <= 0:
        return None, False
    ratio = borrowings / total_equity
    flagged = (ratio > 5) and not is_financial
    return ratio, flagged


def interest_coverage(operating_profit, other_income, interest):
    """ICR = (operating_profit + other_income) / interest.
    Returns (ratio, label). Label is 'Debt Free' when interest is 0,
    'Safe' when ICR > 3, otherwise 'Risky'.
    """
    if pd.isna(interest) or interest == 0:
        return None, "Debt Free"
    ratio = (operating_profit + other_income) / interest
    label = "Safe" if ratio > 3 else "Risky"
    return ratio, label


def asset_turnover(sales, total_assets):
    """Asset Turnover = sales / total_assets. None if total_assets is 0 or missing."""
    if pd.isna(total_assets) or total_assets == 0:
        return None
    return sales / total_assets


def load_joined_data(conn):
    """Join P&L + Balance Sheet + Sectors (for the Financials carve-out)."""
    query = """
        SELECT p.company_id, p.year, p.sales, p.operating_profit, p.other_income, p.interest,
               b.equity_capital, b.reserves, b.borrowings, b.total_assets,
               s.broad_sector
        FROM profitandloss p
        JOIN balancesheet b
          ON p.company_id = b.company_id AND p.year = b.year
        LEFT JOIN sectors s
          ON p.company_id = s.company_id
    """
    return pd.read_sql(query, conn)


def build_leverage_ratios(db_path=DB_PATH):
    """Compute D/E, ICR, and Asset Turnover for every company-year row."""
    conn = sqlite3.connect(db_path)
    df = load_joined_data(conn)
    conn.close()

    rows = []
    for _, r in df.iterrows():
        is_financial = r["broad_sector"] == "Financials"

        de, high_leverage_flag = debt_to_equity(
            r["borrowings"], r["equity_capital"], r["reserves"], is_financial
        )
        icr, icr_label = interest_coverage(
            r["operating_profit"], r["other_income"], r["interest"]
        )
        turnover = asset_turnover(r["sales"], r["total_assets"])

        rows.append({
            "company_id": r["company_id"],
            "year": r["year"],
            "debt_to_equity": de,
            "high_leverage_flag": high_leverage_flag,
            "interest_coverage": icr,
            "icr_label": icr_label,
            "asset_turnover": turnover,
        })

    return pd.DataFrame(rows)


def summarize(ratios: pd.DataFrame):
    """Print a quick sanity summary of the computed ratios."""
    print(ratios.head(10))
    print(f"\nTotal rows: {len(ratios)}")
    print(f"D/E nulls: {ratios['debt_to_equity'].isna().sum()}")
    print(f"Debt-free companies (ICR label): {(ratios['icr_label'] == 'Debt Free').sum()}")
    print(f"High leverage flags (non-financial, D/E > 5): {ratios['high_leverage_flag'].sum()}")
    print(f"Asset turnover nulls: {ratios['asset_turnover'].isna().sum()}")


if __name__ == "__main__":
    leverage_df = build_leverage_ratios()
    summarize(leverage_df)