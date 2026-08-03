import sqlite3
import pandas as pd
import yaml

DB_PATH = "data/nifty100.db"
CONFIG_PATH = "config/screener_config.yaml"


def load_config(path=CONFIG_PATH):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_latest_ratios(db_path=DB_PATH):
    """Get each company's most recent year of ratios, merged with latest
    market_cap data (P/E, P/B, dividend yield) for valuation-based screens.
    """
    conn = sqlite3.connect(db_path)

    ratios_query = """
        SELECT * FROM financial_ratios
        WHERE (company_id, year) IN (
            SELECT company_id, MAX(year) FROM financial_ratios
            WHERE year GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
            GROUP BY company_id
        )
    """
    ratios = pd.read_sql(ratios_query, conn)

    mktcap_query = """
        SELECT * FROM market_cap
        WHERE (company_id, year) IN (
            SELECT company_id, MAX(year) FROM market_cap GROUP BY company_id
        )
    """
    mktcap = pd.read_sql(mktcap_query, conn)
    conn.close()

    # Merge on company_id only (years may not align between the two tables)
    merged = ratios.merge(
        mktcap.drop(columns=["year"]), on="company_id", how="left"
    )
    return merged


def apply_filters(df, filters):
    """Apply a dict of {column: {min/max: value}} filters to a DataFrame."""
    result = df.copy()
    for column, bounds in filters.items():
        if column not in result.columns:
            continue
        if "min" in bounds:
            result = result[result[column] >= bounds["min"]]
        if "max" in bounds:
            result = result[result[column] <= bounds["max"]]
    return result


def run_screener(preset_name, config=None, df=None, db_path=DB_PATH):
    """Run a named preset from the config and return the ranked result."""
    if config is None:
        config = load_config()
    if df is None:
        df = load_latest_ratios(db_path)

    preset = config["presets"].get(preset_name)
    if preset is None:
        raise ValueError(f"Unknown preset: {preset_name}")

    filtered = apply_filters(df, preset["filters"])

    rank_by = preset.get("rank_by")
    ascending = preset.get("rank_order", "desc") == "asc"
    if rank_by and rank_by in filtered.columns:
        filtered = filtered.sort_values(rank_by, ascending=ascending)

    return filtered


if __name__ == "__main__":
    config = load_config()
    universe = load_latest_ratios()
    print(f"Full universe size: {len(universe)} companies\n")

    for preset_name in config["presets"]:
        result = run_screener(preset_name, config, df=universe)
        pct = (len(result) / len(universe)) * 100
        print(f"=== {preset_name}: {len(result)} companies ({pct:.0f}% of universe) ===")
        print(result[["company_id", "year"]].head(8).to_string(index=False))
        print()