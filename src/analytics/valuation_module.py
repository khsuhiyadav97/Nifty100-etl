import sqlite3
import pandas as pd

DB_PATH = "data/nifty100.db"
OUTPUT_PATH = "output/valuation_summary.xlsx"


def load_valuation_data(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    query = """
        SELECT r.company_id, c.company_name, s.broad_sector,
               r.free_cash_flow,
               m.market_cap_crore, m.pe_ratio, m.pb_ratio, m.ev_ebitda,
               m.dividend_yield_pct
        FROM financial_ratios r
        JOIN companies c ON r.company_id = c.id
        LEFT JOIN sectors s ON r.company_id = s.company_id
        LEFT JOIN (
            SELECT * FROM market_cap
            WHERE (company_id, year) IN (
                SELECT company_id, MAX(year) FROM market_cap GROUP BY company_id
            )
        ) m ON r.company_id = m.company_id
        WHERE (r.company_id, r.year) IN (
            SELECT company_id, MAX(year) FROM financial_ratios
            WHERE year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
            GROUP BY company_id
        )
    """
    return pd.read_sql(query, conn).drop_duplicates(subset="company_id")


def compute_fcf_yield(fcf, market_cap_crore):
    if pd.isna(market_cap_crore) or market_cap_crore == 0:
        return None
    return (fcf / market_cap_crore) * 100


def flag_valuation(pe_ratio, sector_median_pe):
    if pd.isna(pe_ratio) or pd.isna(sector_median_pe) or sector_median_pe == 0:
        return "N/A"
    if pe_ratio > sector_median_pe * 1.5:
        return "Caution (Overvalued)"
    elif pe_ratio < sector_median_pe * 0.7:
        return "Discount (Undervalued)"
    return "Fair Value"


def build_valuation_summary(db_path=DB_PATH):
    df = load_valuation_data(db_path)

    sector_median_pe = df.groupby("broad_sector")["pe_ratio"].transform("median")

    df["fcf_yield_pct"] = df.apply(
        lambda r: compute_fcf_yield(r["free_cash_flow"], r["market_cap_crore"]), axis=1
    )
    df["valuation_flag"] = [
        flag_valuation(pe, med) for pe, med in zip(df["pe_ratio"], sector_median_pe)
    ]

    return df.sort_values("fcf_yield_pct", ascending=False)


if __name__ == "__main__":
    summary = build_valuation_summary()
    print(summary[["company_id", "broad_sector", "pe_ratio", "fcf_yield_pct", "valuation_flag"]].head(15).to_string(index=False))
    print(f"\nTotal companies: {len(summary)}")
    print("\nValuation flag distribution:")
    print(summary["valuation_flag"].value_counts())

    summary.to_excel(OUTPUT_PATH, index=False)
    print(f"\nSaved {OUTPUT_PATH}")

    flags = summary[summary["valuation_flag"] != "Fair Value"]
    flags[["company_id", "broad_sector", "pe_ratio", "valuation_flag"]].to_csv(
        "output/valuation_flags.csv", index=False
    )
    print(f"Saved output/valuation_flags.csv ({len(flags)} flagged companies)")