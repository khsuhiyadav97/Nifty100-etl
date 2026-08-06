import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"

st.set_page_config(
    page_title="Nifty 100 Financial Intelligence",
    page_icon="\U0001F4CA",
    layout="wide",
)


@st.cache_data(ttl=600)
def load_db(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def main():
    st.sidebar.title("Nifty 100 Platform")
    st.sidebar.markdown("Financial Intelligence Dashboard")

    st.title("Nifty 100 Financial Intelligence Platform")
    st.markdown("Welcome. Use the pages in the sidebar to explore companies, "
                "run the screener, and compare peers.")

    companies = load_db("SELECT COUNT(*) as n FROM companies")
    ratios = load_db("SELECT COUNT(*) as n FROM financial_ratios")

    col1, col2 = st.columns(2)
    col1.metric("Companies Tracked", int(companies["n"][0]))
    col2.metric("Ratio Records", int(ratios["n"][0]))


if __name__ == "__main__":
    main()