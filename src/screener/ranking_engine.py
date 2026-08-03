"""

Combines multiple ratios into a single 0-100 composite score per company,
using percentile-based normalization (so raw ratios of different scales/units
become comparable) and the weighting scheme from the project spec:

    Profitability (35%): ROE 15%, ROCE 10%, NPM 10%
    Cash Quality (30%):  CFO/PAT 10%, FCF-positive flag 5%   [FCF CAGR to be
                         added once merged with the CAGR module]
    Leverage (15%):      D/E score 10%, ICR score 5%
    Growth (20%):        placeholder until Revenue/PAT CAGR is merged in

For now, weights are re-normalized across only the metrics we have available,
so the score still sums to 100 without the missing growth component silently
dragging every score down.
"""

import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"


def percentile_score(series, higher_is_better=True):
    """Convert a raw metric into a 0-100 percentile-rank score.
    Winsorizes implicitly via rank-based scoring (outliers can't dominate).
    """
    ranks = series.rank(pct=True) * 100
    if not higher_is_better:
        ranks = 100 - ranks
    return ranks


def build_composite_scores(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    query = """
        SELECT * FROM financial_ratios
        WHERE (company_id, year) IN (
            SELECT company_id, MAX(year) FROM financial_ratios
            WHERE year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
            GROUP BY company_id
        )
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # --- Profitability (35%): ROE 15%, ROCE 10%, NPM 10% ---
    roe_score = percentile_score(df["return_on_equity_pct"])
    roce_score = percentile_score(df["return_on_capital_pct"])
    npm_score = percentile_score(df["net_profit_margin_pct"])
    profitability = (roe_score * 0.15 + roce_score * 0.10 + npm_score * 0.10)

    # --- Cash Quality (30% budget, using available 15%): CFO/PAT 10%, FCF flag 5% ---
    cfo_pat_score = percentile_score(df["cfo_pat_ratio"])
    fcf_flag_score = (df["free_cash_flow"] > 0).astype(float) * 100
    cash_quality = (cfo_pat_score * 0.10 + fcf_flag_score * 0.05)

    # --- Leverage (15%): D/E score 10% (lower better), ICR score 5% (higher better) ---
    de_score = percentile_score(df["debt_to_equity"], higher_is_better=False)
    icr_score = percentile_score(df["interest_coverage"].fillna(df["interest_coverage"].max()))
    leverage = (de_score * 0.10 + icr_score * 0.05)

    total_weight_used = 0.15 + 0.10 + 0.10 + 0.10 + 0.05 + 0.10 + 0.05  # = 0.65
    raw_score = profitability + cash_quality + leverage
    composite = raw_score / total_weight_used  # re-normalize to a 0-100 scale

    result = pd.DataFrame({
        "company_id": df["company_id"],
        "year": df["year"],
        "profitability_component": profitability,
        "cash_quality_component": cash_quality,
        "leverage_component": leverage,
        "composite_score": composite,
    })
    return result.sort_values("composite_score", ascending=False)


if __name__ == "__main__":
    scores = build_composite_scores()
    print(scores.head(15).to_string(index=False))
    print(f"\nTotal companies scored: {len(scores)}")
    print(f"Score range: {scores['composite_score'].min():.1f} - {scores['composite_score'].max():.1f}")

    scores.to_excel("output/screener_output.xlsx", index=False)
    print("\nSaved output/screener_output.xlsx")