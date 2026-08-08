"""Trend Analysis Screen - pick a company + metric, see the trend over time."""
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"
st.set_page_config(page_title="Trend Analysis", layout="wide")


@st.cache_data(ttl=600)
def load_history(ticker):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        """SELECT year, sales, net_profit, operating_profit FROM profitandloss
           WHERE company_id = ? AND year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
           ORDER BY year""",
        conn, params=(ticker,),
    )
    conn.close()
    return df


@st.cache_data(ttl=600)
def load_tickers():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT id FROM companies ORDER BY id", conn)
    conn.close()
    return df["id"].tolist()


st.title("Trend Analysis")

ticker = st.selectbox("Company", load_tickers())
metrics = st.multiselect(
    "Metrics to overlay", ["sales", "net_profit", "operating_profit"],
    default=["sales", "net_profit"]
)

history = load_history(ticker)
if not history.empty and metrics:
    chart_df = history.set_index("year")[metrics]
    st.line_chart(chart_df)

    history["sales_yoy_pct"] = history["sales"].pct_change() * 100
    st.subheader("YoY Sales Growth (%)")
    st.bar_chart(history.set_index("year")["sales_yoy_pct"])
else:
    st.info("No data available for this company.")