import sqlite3

conn = sqlite3.connect("data/nifty100.db")

queries = {
    "1. Total companies": "SELECT COUNT(*) FROM companies",
    "2. Total P&L rows": "SELECT COUNT(*) FROM profitandloss",
    "3. Total balance sheet rows": "SELECT COUNT(*) FROM balancesheet",
    "4. Total cash flow rows": "SELECT COUNT(*) FROM cashflow",
    "5. Companies per sector": """
        SELECT broad_sector, COUNT(*) as company_count
        FROM sectors GROUP BY broad_sector ORDER BY company_count DESC
    """,
    "6. Top 5 companies by ROE": """
        SELECT id, roe_percentage FROM companies
        ORDER BY roe_percentage DESC LIMIT 5
    """,
    "7. Companies with negative net profit (any year)": """
        SELECT DISTINCT company_id FROM profitandloss WHERE net_profit < 0
    """,
    "8. Average sales by year (last 5 years)": """
        SELECT year, ROUND(AVG(sales),0) as avg_sales
        FROM profitandloss WHERE year >= '2020-01'
        GROUP BY year ORDER BY year
    """,
    "9. Null check - companies missing website": """
        SELECT COUNT(*) FROM companies WHERE website IS NULL
    """,
    "10. Year coverage distribution": """
        SELECT year_count, COUNT(*) as num_companies FROM (
            SELECT company_id, COUNT(*) as year_count
            FROM profitandloss GROUP BY company_id
        ) GROUP BY year_count ORDER BY year_count
    """
}

for title, sql in queries.items():
    print(f"\n=== {title} ===")
    for row in conn.execute(sql):
        print(row)

conn.close()