import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"

st.set_page_config(page_title="Company Profile", layout="wide")


@st.cache_data(ttl=600)
def load_db(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


st.title("Company Profile")

companies = load_db("SELECT id, company_name FROM companies ORDER BY id")
ticker = st.selectbox("Search by ticker", companies["id"].tolist())

company_info = load_db(
    "SELECT * FROM companies WHERE id = ?", (ticker,)
).iloc[0]

st.subheader(f"{company_info['company_name']} ({ticker})")
if pd.notna(company_info.get("about_company")):
    st.caption(company_info["about_company"])

# --- KPI tiles from latest financial_ratios row ---
latest_ratios = load_db(
    """SELECT * FROM financial_ratios
       WHERE company_id = ? AND year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
       ORDER BY year DESC LIMIT 1""",
    (ticker,),
)

if not latest_ratios.empty:
    r = latest_ratios.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ROE", f"{r['return_on_equity_pct']:.1f}%" if pd.notna(r["return_on_equity_pct"]) else "N/A")
    col2.metric("ROCE", f"{r['return_on_capital_pct']:.1f}%" if pd.notna(r["return_on_capital_pct"]) else "N/A")
    col3.metric("D/E", f"{r['debt_to_equity']:.2f}" if pd.notna(r["debt_to_equity"]) else "N/A")
    col4.metric("NPM", f"{r['net_profit_margin_pct']:.1f}%" if pd.notna(r["net_profit_margin_pct"]) else "N/A")
else:
    st.info("No ratio data available for this company.")

# --- 10-year revenue & profit trend ---
st.subheader("Revenue & Profit Trend")
history = load_db(
    """SELECT year, sales, net_profit FROM profitandloss
       WHERE company_id = ? AND year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
       ORDER BY year""",
    (ticker,),
)

if not history.empty:
    chart_data = history.set_index("year")[["sales", "net_profit"]]
    chart_data.columns = ["Sales (Cr)", "Net Profit (Cr)"]
    st.bar_chart(chart_data)
else:
    st.info("No historical P&L data available.")