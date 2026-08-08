"""Sector Analysis Screen - bubble chart + sector median KPIs."""
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"
st.set_page_config(page_title="Sector Analysis", layout="wide")


@st.cache_data(ttl=600)
def load_sector_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        """SELECT s.broad_sector, r.company_id, r.return_on_equity_pct,
                  r.net_profit_margin_pct, r.debt_to_equity
           FROM sectors s
           JOIN financial_ratios r ON s.company_id = r.company_id
           WHERE (r.company_id, r.year) IN (
               SELECT company_id, MAX(year) FROM financial_ratios
               WHERE year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
               GROUP BY company_id
           )""",
        conn,
    )
    conn.close()
    return df


st.title("Sector Analysis")

df = load_sector_data()
sector_medians = df.groupby("broad_sector")[
    ["return_on_equity_pct", "net_profit_margin_pct", "debt_to_equity"]
].median().round(2)

st.subheader("Median KPIs by Sector")
st.dataframe(sector_medians, use_container_width=True)

st.subheader("Sector Median ROE")
st.bar_chart(sector_medians["return_on_equity_pct"])