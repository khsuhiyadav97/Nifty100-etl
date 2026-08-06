import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"

st.set_page_config(page_title="Home", layout="wide")


@st.cache_data(ttl=600)
def load_db(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df


st.title("Nifty 100 Overview")

latest = load_db(
    """SELECT * FROM financial_ratios
       WHERE (company_id, year) IN (
           SELECT company_id, MAX(year) FROM financial_ratios
           WHERE year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
           GROUP BY company_id
       )"""
)

col1, col2, col3 = st.columns(3)
col1.metric("Avg ROE", f"{latest['return_on_equity_pct'].mean():.1f}%")
col2.metric("Avg D/E", f"{latest['debt_to_equity'].mean():.2f}")
col3.metric("Avg NPM", f"{latest['net_profit_margin_pct'].mean():.1f}%")

st.subheader("Companies by Sector")
sectors = load_db(
    """SELECT broad_sector, COUNT(*) as count FROM sectors
       GROUP BY broad_sector ORDER BY count DESC"""
)
st.bar_chart(sectors.set_index("broad_sector"))