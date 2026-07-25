import sqlite3

conn = sqlite3.connect("data/nifty100.db")

# 1. the company with <5 years of data
print("=== Companies with <5 years of P&L data ===")
query1 = """
SELECT company_id, COUNT(*) as year_count
FROM profitandloss
GROUP BY company_id
HAVING year_count < 5
"""
for row in conn.execute(query1):
    print(row)

# 2. 5 random companies and show their year coverage
print("\n=== Year coverage for 5 random companies ===")
query2 = """
SELECT company_id, COUNT(*) as year_count, MIN(year) as earliest, MAX(year) as latest
FROM profitandloss
GROUP BY company_id
ORDER BY RANDOM()
LIMIT 5
"""
for row in conn.execute(query2):
    print(row)

conn.close()