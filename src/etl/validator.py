import pandas as pd
from loader import load_file, load_profitandloss, load_balancesheet

def pk_uniqueness(df, column):
    total_rows = len(df)
    unique_values = df[column].nunique()
    if total_rows != unique_values:
        return "CRITICAL: Duplicate values found"
    return "Pass"

def check_annual_pk_uniqueness(df):
    total_rows = len(df)
    unique_combinations = df[['company_id', 'year']].drop_duplicates().shape[0]
    if total_rows != unique_combinations:
        return "CRITICAL: duplicate (company_id, year) pairs found"
    return "Pass"

def deduplicate_annual(df):
    duplicated_rows = df[df.duplicated(subset=['company_id', 'year'], keep='last')]
    clean_df = df.drop_duplicates(subset=['company_id', 'year'], keep='last')
    return clean_df, duplicated_rows

def check_fk_integrity(child_df, parent_df, child_col, parent_col):
    child_ids = set(child_df[child_col].unique())
    parent_ids = set(parent_df[parent_col].unique())
    orphans = child_ids - parent_ids
    if orphans:
        return f"CRITICAL: {len(orphans)} orphan company_ids found: {orphans}"
    return "Pass"

def check_positive_sales(df):
    bad_rows = df[df['sales'] <= 0]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows with non-positive sales"
    return "Pass"

def check_ticker_format(df, column='company_id'):
    bad_rows = df[~df[column].str.len().between(2, 12)]
    if len(bad_rows) > 0:
        return f"CRITICAL: {len(bad_rows)} tickers with invalid length"
    return "Pass"

def check_bs_balance(df):
    diff_pct = abs(df['total_assets'] - df['total_liabilities']) / df['total_assets']
    bad_rows = df[diff_pct >= 0.01]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows where BS doesn't balance"
    return "Pass"

def check_opm_crosscheck(df):
    calculated_opm = (df['operating_profit'] / df['sales']) * 100
    diff = abs(df['opm_percentage'] - calculated_opm)
    bad_rows = df[diff >= 1.0]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows where OPM mismatch"
    return "Pass"

def check_coverage(df):
    years_per_company = df.groupby('company_id')['year'].nunique()
    low_coverage = years_per_company[years_per_company < 5]
    if len(low_coverage) > 0:
        return f"WARNING: {len(low_coverage)} companies with <5 years of data"
    return "Pass"

if __name__ == "__main__":
    df = load_file("data/n100/companies.xlsx")
    df_pl = load_profitandloss("data/n100/profitandloss.xlsx")
    df_bs = load_balancesheet("data/n100/balancesheet.xlsx")

    print("DQ-01:", pk_uniqueness(df, 'id'))
    print("DQ-02:", check_annual_pk_uniqueness(df_pl))

    clean_df, removed = deduplicate_annual(df_pl)
    print(f"Deduplication: removed {len(removed)} rows, {len(clean_df)} remain")

    print("DQ-03:", check_fk_integrity(df_pl, df, 'company_id', 'id'))
    print("DQ-06:", check_positive_sales(df_pl))
    print("DQ-08:", check_ticker_format(df_pl))
    print("DQ-04:", check_bs_balance(df_bs))
    print("DQ-05:", check_opm_crosscheck(df_pl))
    print("DQ-16:", check_coverage(df_pl))