import sqlite3
import pandas as pd
import sys
sys.path.append('src/etl')
from loader import load_file, load_profitandloss, load_balancesheet

def create_database(schema_path, db_path):
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.close()
    print("Database Created at", db_path)

def load_data_into_db(db_path):
    conn = sqlite3.connect(db_path)

    df_companies = load_file("data/n100/companies.xlsx")
    df_pl = load_profitandloss("data/n100/profitandloss.xlsx")
    df_bs = load_balancesheet("data/n100/balancesheet.xlsx")

    df_companies.to_sql('companies', conn, if_exists='append', index=False)
    df_pl.to_sql('profitandloss', conn, if_exists='append', index=False)
    df_bs.to_sql('balancesheet', conn, if_exists='append', index=False)

    conn.close()
    print("Data loaded into database")

if __name__ == "__main__":
    create_database("db/schema.sql", "data/nifty100.db")
    load_data_into_db("data/nifty100.db")
