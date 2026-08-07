import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"

st.set_page_config(page_title="Peer Comparison", layout="wide")


@st.cache_data(ttl=600)
def load_peer_percentiles():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM peer_percentiles", conn)
    conn.close()
    return df


st.title("Peer Comparison")

df = load_peer_percentiles()
groups = sorted(df["peer_group_name"].unique())
selected_group = st.selectbox("Select peer group", groups)

group_df = df[df["peer_group_name"] == selected_group].sort_values(
    "return_on_equity_pct_pctile", ascending=False
)

st.subheader(f"{selected_group} - {len(group_df)} companies")

display_df = group_df[[
    "company_id", "is_benchmark",
    "return_on_equity_pct_pctile", "return_on_capital_pct_pctile",
    "net_profit_margin_pct_pctile", "debt_to_equity_pctile"
]].rename(columns={
    "return_on_equity_pct_pctile": "ROE %ile",
    "return_on_capital_pct_pctile": "ROCE %ile",
    "net_profit_margin_pct_pctile": "NPM %ile",
    "debt_to_equity_pctile": "D/E %ile",
})

st.dataframe(
    display_df.style.background_gradient(
        cmap="RdYlGn", subset=["ROE %ile", "ROCE %ile", "NPM %ile", "D/E %ile"]
    ),
    use_container_width=True,
)