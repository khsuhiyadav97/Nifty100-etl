"""
Cash Flow Intelligence Engine 

Computes cash-flow quality KPIs per company-year:
    - Free Cash Flow (FCF)
    - CFO / PAT ratio (earnings quality)
    - CapEx Intensity
    - Capital Allocation Pattern (sign-based classification of CFO/CFI/CFF)
"""

import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"

PATTERN_LABELS = {
    (True, True, True): "Aggressive Expansion",      # CFO+, CFI+, CFF+
    (True, True, False): "Divesting & Repaying",      # CFO+, CFI+, CFF-
    (True, False, True): "Reinvest & Raise Capital",  # CFO+, CFI-, CFF+
    (True, False, False): "Reinvestor / Shareholder Returns",  # CFO+, CFI-, CFF-
    (False, True, True): "Distress (Asset Sale + Borrowing)",  # CFO-, CFI+, CFF+
    (False, True, False): "Distress (Asset Sale, Repaying)",   # CFO-, CFI+, CFF-
    (False, False, True): "Distress (Funding Ops via Debt)",   # CFO-, CFI-, CFF+
    (False, False, False): "Severe Distress",         # CFO-, CFI-, CFF-
}


def free_cash_flow(cfo, cfi):
    """FCF = CFO + CFI. Negative allowed (flagged elsewhere if persistent)."""
    return cfo + cfi


def cfo_pat_ratio(cfo, net_profit):
    """CFO/PAT ratio. >1.0 = high quality earnings, <0.5 = accrual risk. None if PAT=0."""
    if pd.isna(net_profit) or net_profit == 0:
        return None, None
    ratio = cfo / net_profit
    if ratio > 1.0:
        label = "High Quality Earnings"
    elif ratio < 0.5:
        label = "Accrual Risk"
    else:
        label = "Moderate"
    return ratio, label


def capex_intensity(cfi, sales):
    """CapEx Intensity = |CFI| / sales * 100. <3% = asset-light, >8% = capital intensive."""
    if pd.isna(sales) or sales == 0:
        return None, None
    intensity = abs(cfi) / sales * 100
    if intensity < 3:
        label = "Asset-Light"
    elif intensity > 8:
        label = "Capital Intensive"
    else:
        label = "Moderate"
    return intensity, label


def capital_allocation_pattern(cfo, cfi, cff):
    """Classify company-year into one of 8 patterns based on CFO/CFI/CFF signs."""
    key = (cfo > 0, cfi > 0, cff > 0)
    return PATTERN_LABELS[key]


def load_cashflow_joined(conn):
    query = """
        SELECT c.company_id, c.year, c.operating_activity, c.investing_activity,
               c.financing_activity, p.sales, p.net_profit
        FROM cashflow c
        JOIN profitandloss p ON c.company_id = p.company_id AND c.year = p.year
    """
    return pd.read_sql(query, conn)


def build_cashflow_kpis(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    df = load_cashflow_joined(conn)
    conn.close()

    rows = []
    for _, r in df.iterrows():
        cfo, cfi, cff = r["operating_activity"], r["investing_activity"], r["financing_activity"]

        fcf = free_cash_flow(cfo, cfi)
        ratio, quality_label = cfo_pat_ratio(cfo, r["net_profit"])
        intensity, intensity_label = capex_intensity(cfi, r["sales"])
        pattern = capital_allocation_pattern(cfo, cfi, cff)

        rows.append({
            "company_id": r["company_id"],
            "year": r["year"],
            "free_cash_flow": fcf,
            "cfo_pat_ratio": ratio,
            "earnings_quality": quality_label,
            "capex_intensity_pct": intensity,
            "capex_label": intensity_label,
            "capital_allocation_pattern": pattern,
        })

    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame):
    print(df.head(10))
    print(f"\nTotal rows: {len(df)}")
    print("\nEarnings quality distribution:")
    print(df["earnings_quality"].value_counts(dropna=False))
    print("\nCapital allocation pattern distribution:")
    print(df["capital_allocation_pattern"].value_counts())


if __name__ == "__main__":
    kpi_df = build_cashflow_kpis()
    summarize(kpi_df)