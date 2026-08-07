import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"

st.set_page_config(page_title="Screener", layout="wide")


@st.cache_data(ttl=600)
def load_latest_ratios():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        """SELECT r.*, c.company_name FROM financial_ratios r
           JOIN companies c ON r.company_id = c.id
           WHERE (r.company_id, r.year) IN (
               SELECT company_id, MAX(year) FROM financial_ratios
               WHERE year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
               GROUP BY company_id
           )""",
        conn,
    )
    conn.close()
    return df


st.title("Financial Screener")

df = load_latest_ratios()

st.sidebar.header("Filters")
min_roe = st.sidebar.slider("Min ROE (%)", -20, 60, 10)
max_de = st.sidebar.slider("Max Debt-to-Equity", 0.0, 5.0, 2.0)
min_npm = st.sidebar.slider("Min Net Profit Margin (%)", -20, 50, 0)

filtered = df[
    (df["return_on_equity_pct"] >= min_roe)
    & (df["debt_to_equity"] <= max_de)
    & (df["net_profit_margin_pct"] >= min_npm)
].sort_values("return_on_equity_pct", ascending=False)

st.write(f"**{len(filtered)} companies match your filters**")
display_cols = ["company_id", "company_name", "return_on_equity_pct",
                 "debt_to_equity", "net_profit_margin_pct", "free_cash_flow"]
st.dataframe(filtered[display_cols], use_container_width=True)

csv = filtered[display_cols].to_csv(index=False)
st.download_button("Download results as CSV", csv, "screener_results.csv", "text/csv")