import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"


def net_profit_margin(net_profit, sales):
    """NPM (%) = net_profit / sales * 100. None if sales is 0 or missing."""
    if pd.isna(sales) or sales == 0:
        return None
    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    """OPM (%) = operating_profit / sales * 100. None if sales is 0 or missing."""
    if pd.isna(sales) or sales == 0:
        return None
    return (operating_profit / sales) * 100


def return_on_equity(net_profit, equity_capital, reserves):
    """ROE (%) = net_profit / (equity_capital + reserves) * 100. None if equity <= 0."""
    total_equity = equity_capital + reserves
    if pd.isna(total_equity) or total_equity <= 0:
        return None
    return (net_profit / total_equity) * 100


def return_on_capital_employed(operating_profit, depreciation,
                                equity_capital, reserves, borrowings):
    """ROCE (%) = EBIT / (equity + reserves + borrowings) * 100.
    EBIT = operating_profit - depreciation. None if capital employed <= 0.
    """
    ebit = operating_profit - depreciation
    capital_employed = equity_capital + reserves + borrowings
    if pd.isna(capital_employed) or capital_employed <= 0:
        return None
    return (ebit / capital_employed) * 100


def load_pl_balancesheet_joined(conn):
    """Join P&L and Balance Sheet on (company_id, year)."""
    query = """
        SELECT p.company_id, p.year, p.sales, p.net_profit, p.operating_profit,
               p.depreciation, p.opm_percentage,
               b.equity_capital, b.reserves, b.borrowings
        FROM profitandloss p
        JOIN balancesheet b
          ON p.company_id = b.company_id AND p.year = b.year
    """
    return pd.read_sql(query, conn)


def build_profitability_ratios(db_path=DB_PATH):
    """Compute NPM, OPM, ROE, ROCE for every company-year row."""
    conn = sqlite3.connect(db_path)
    df = load_pl_balancesheet_joined(conn)
    conn.close()

    ratios = pd.DataFrame({
        "company_id": df["company_id"],
        "year": df["year"],
        "net_profit_margin_pct": df.apply(
            lambda r: net_profit_margin(r["net_profit"], r["sales"]), axis=1),
        "operating_profit_margin_pct": df.apply(
            lambda r: operating_profit_margin(r["operating_profit"], r["sales"]), axis=1),
        "return_on_equity_pct": df.apply(
            lambda r: return_on_equity(r["net_profit"], r["equity_capital"], r["reserves"]), axis=1),
        "return_on_capital_pct": df.apply(
            lambda r: return_on_capital_employed(
                r["operating_profit"], r["depreciation"],
                r["equity_capital"], r["reserves"], r["borrowings"]), axis=1),
    })
    return ratios


def summarize(ratios: pd.DataFrame):
    """Print a quick sanity summary: row count + null count per ratio."""
    print(ratios.head(10))
    print(f"\nTotal rows: {len(ratios)}")
    for col in ["net_profit_margin_pct", "operating_profit_margin_pct",
                "return_on_equity_pct", "return_on_capital_pct"]:
        print(f"{col}: {ratios[col].isna().sum()} nulls")


if __name__ == "__main__":
    ratios_df = build_profitability_ratios()
    summarize(ratios_df)