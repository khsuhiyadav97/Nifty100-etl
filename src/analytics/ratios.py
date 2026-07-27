import sqlite3
import pandas as pd


def calc_npm(net_profit, sales):
    """Net Profit Margin = net_profit / sales * 100. None if sales is 0."""
    if sales == 0 or pd.isna(sales):
        return None
    return (net_profit / sales) * 100


def calc_opm(operating_profit, sales):
    """Operating Profit Margin = operating_profit / sales * 100. None if sales is 0."""
    if sales == 0 or pd.isna(sales):
        return None
    return (operating_profit / sales) * 100


def calc_roe(net_profit, equity_capital, reserves):
    """Return on Equity = net_profit / (equity+reserves) * 100. None if equity <= 0."""
    equity_total = equity_capital + reserves
    if equity_total <= 0 or pd.isna(equity_total):
        return None
    return (net_profit / equity_total) * 100


def calc_roce(operating_profit, depreciation, equity_capital, reserves, borrowings):
    """Return on Capital Employed = EBIT / (equity+reserves+borrowings) * 100."""
    ebit = operating_profit - depreciation
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0 or pd.isna(capital_employed):
        return None
    return (ebit / capital_employed) * 100


def build_ratios_table(db_path):
    conn = sqlite3.connect(db_path)

    query = """
        SELECT p.company_id, p.year, p.sales, p.net_profit, p.operating_profit,
               p.depreciation, p.opm_percentage,
               b.equity_capital, b.reserves, b.borrowings
        FROM profitandloss p
        JOIN balancesheet b ON p.company_id = b.company_id AND p.year = b.year
    """
    df = pd.read_sql(query, conn)
    conn.close()

    results = []
    for _, row in df.iterrows():
        npm = calc_npm(row['net_profit'], row['sales'])
        opm_calc = calc_opm(row['operating_profit'], row['sales'])
        roe = calc_roe(row['net_profit'], row['equity_capital'], row['reserves'])
        roce = calc_roce(row['operating_profit'], row['depreciation'],
                          row['equity_capital'], row['reserves'], row['borrowings'])

        results.append({
            'company_id': row['company_id'],
            'year': row['year'],
            'net_profit_margin_pct': npm,
            'operating_profit_margin_pct': opm_calc,
            'return_on_equity_pct': roe,
            'return_on_capital_pct': roce
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    ratios_df = build_ratios_table("data/nifty100.db")
    print(ratios_df.head(10))
    print(f"\nTotal rows: {len(ratios_df)}")
    print(f"NPM nulls: {ratios_df['net_profit_margin_pct'].isna().sum()}")
    print(f"ROE nulls: {ratios_df['return_on_equity_pct'].isna().sum()}")
    print(f"ROCE nulls: {ratios_df['return_on_capital_pct'].isna().sum()}")