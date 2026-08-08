"""Annual Reports Screen - browse a company's annual report links by year."""
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"
st.set_page_config(page_title="Annual Reports", layout="wide")


@st.cache_data(ttl=600)
def load_documents(ticker):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT Year, Annual_Report FROM documents WHERE company_id = ? ORDER BY Year DESC",
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


st.title("Annual Reports")

ticker = st.selectbox("Company", load_tickers())
docs = load_documents(ticker)

if docs.empty:
    st.warning("No annual reports found for this company.")
else:
    for _, row in docs.iterrows():
        if pd.notna(row["Annual_Report"]):
            st.markdown(f"**{row['Year']}** - [View Report]({row['Annual_Report']})")
        else:
            st.markdown(f"**{row['Year']}** - _Report unavailable_")