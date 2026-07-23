import sqlite3
import pandas as pd
import sys
import os
sys.path.append('src/etl')
from loader import (
    load_file, load_profitandloss, load_balancesheet, load_cashflow,
    load_documents, load_analysis, load_prosandcons, load_sectors,
    load_market_cap, load_stock_prices
)
from validator import deduplicate_annual

import sqlite3
conn = sqlite3.connect("data/nifty100.db")
cursor = conn.execute("PRAGMA foreign_key_check")
results = cursor.fetchall()
print(f"Foreign key violations: {len(results)}")
if results:
    print(results[:10])
conn.close()


def create_database(schema_path, db_path):
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.close()
    print("Database Created at", db_path)


def load_data_into_db(db_path):
    conn = sqlite3.connect(db_path)
    audit_records = []

    def insert_and_log(df, table_name, rows_in):
        rows_out = len(df)
        rejected = rows_in - rows_out
        df.to_sql(table_name, conn, if_exists='append', index=False)
        audit_records.append({
            'table': table_name,
            'rows_in': rows_in,
            'rows_out': rows_out,
            'rejected': rejected
        })
        print(f"  {table_name}: {rows_out} rows loaded")

    # Core files
    df_companies = load_file("data/n100/companies.xlsx")
    insert_and_log(df_companies, 'companies', len(df_companies))

    df_pl = load_profitandloss("data/n100/profitandloss.xlsx")
    rows_in = len(df_pl)
    df_pl, _ = deduplicate_annual(df_pl)
    insert_and_log(df_pl, 'profitandloss', rows_in)

    df_bs = load_balancesheet("data/n100/balancesheet.xlsx")
    rows_in = len(df_bs)
    df_bs, _ = deduplicate_annual(df_bs)
    insert_and_log(df_bs, 'balancesheet', rows_in)

    df_cf = load_cashflow("data/n100/cashflow.xlsx")
    rows_in = len(df_cf)
    df_cf, _ = deduplicate_annual(df_cf)
    insert_and_log(df_cf, 'cashflow', rows_in)

    df_analysis = load_analysis("data/n100/analysis.xlsx")
    insert_and_log(df_analysis, 'analysis', len(df_analysis))

    df_docs = load_documents("data/n100/documents.xlsx")
    df_docs = df_docs.rename(columns={'Year': 'Year', 'Annual_Report': 'Annual_Report'})
    insert_and_log(df_docs, 'documents', len(df_docs))

    df_pros = load_prosandcons("data/n100/prosandcons.xlsx")
    insert_and_log(df_pros, 'prosandcons', len(df_pros))

    # Supplementary files
    df_sectors = load_sectors("data/n100/supporting datasets/sectors.xlsx")
    insert_and_log(df_sectors, 'sectors', len(df_sectors))

    df_mktcap = load_market_cap("data/n100/supporting datasets/market_cap.xlsx")
    insert_and_log(df_mktcap, 'market_cap', len(df_mktcap))

    df_prices = load_stock_prices("data/n100/supporting datasets/stock_prices.xlsx")
    insert_and_log(df_prices, 'stock_prices', len(df_prices))

    conn.close()

    # Write load_audit.csv
    os.makedirs("output", exist_ok=True)
    audit_df = pd.DataFrame(audit_records)
    audit_df.to_csv("output/load_audit.csv", index=False)
    print("\nSaved output/load_audit.csv")
    print(audit_df)


if __name__ == "__main__":
    create_database("db/schema.sql", "data/nifty100.db")
    load_data_into_db("data/nifty100.db")