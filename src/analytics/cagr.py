"""
CAGR Engine 

Computes Compound Annual Growth Rate for Revenue, PAT (Net Profit), and EPS
over 3yr, 5yr, and 10yr windows, per company.

Formula: CAGR (%) = ((end_value / start_value) ** (1/n) - 1) * 100

Edge cases (per the turnaround decision table):
    base > 0, end > 0  -> compute normally
    base > 0, end < 0  -> None (DECLINE_TO_LOSS)
    base < 0, end > 0  -> None (TURNAROUND)
    base < 0, end < 0  -> None (BOTH_NEGATIVE)
    base == 0          -> None (ZERO_BASE)
    < n years history   -> None (INSUFFICIENT)
"""

import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"
WINDOWS = [3, 5, 10]


def calc_cagr(base_value, end_value, n_years):
    """Returns (cagr_pct, flag). flag is None on a normal, valid computation."""
    if base_value == 0 or pd.isna(base_value):
        return None, "ZERO_BASE"
    if base_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"
    if base_value < 0 and end_value > 0:
        return None, "TURNAROUND"
    if base_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    cagr = ((end_value / base_value) ** (1 / n_years) - 1) * 100
    return cagr, None


def get_company_series(conn, company_id):
    """Return a company's yearly sales/net_profit/eps, sorted chronologically.
    Excludes non-standard year labels like 'TTM' or 'PARSE-ERROR'.
    """
    query = """
        SELECT year, sales, net_profit, eps
        FROM profitandloss
        WHERE company_id = ? AND year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
        ORDER BY year
    """
    return pd.read_sql(query, conn, params=(company_id,))


def compute_cagrs_for_company(conn, company_id):
    """Compute Revenue/PAT/EPS CAGR for 3yr, 5yr, 10yr windows for one company."""
    series = get_company_series(conn, company_id)
    results = []

    for n in WINDOWS:
        if len(series) <= n:
            results.append({
                "company_id": company_id, "window": f"{n}yr",
                "revenue_cagr": None, "pat_cagr": None, "eps_cagr": None,
                "flag": "INSUFFICIENT"
            })
            continue

        base_row = series.iloc[-(n + 1)]
        end_row = series.iloc[-1]

        rev_cagr, rev_flag = calc_cagr(base_row["sales"], end_row["sales"], n)
        pat_cagr, pat_flag = calc_cagr(base_row["net_profit"], end_row["net_profit"], n)
        eps_cagr, eps_flag = calc_cagr(base_row["eps"], end_row["eps"], n)

        results.append({
            "company_id": company_id, "window": f"{n}yr",
            "revenue_cagr": rev_cagr, "pat_cagr": pat_cagr, "eps_cagr": eps_cagr,
            "flag": rev_flag or pat_flag or eps_flag
        })

    return results


def build_cagr_table(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    companies = pd.read_sql("SELECT id FROM companies", conn)["id"].tolist()

    all_results = []
    for company_id in companies:
        all_results.extend(compute_cagrs_for_company(conn, company_id))

    conn.close()
    return pd.DataFrame(all_results)


def summarize(cagr_df: pd.DataFrame):
    print(cagr_df.head(15))
    print(f"\nTotal rows: {len(cagr_df)}")
    print("\nFlag counts:")
    print(cagr_df["flag"].value_counts(dropna=False))


if __name__ == "__main__":
    cagr_table = build_cagr_table()
    summarize(cagr_table)