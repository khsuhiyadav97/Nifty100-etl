import pandas as pd
import re
import requests
from loader import load_file, load_profitandloss, load_balancesheet, load_cashflow, load_documents
 
 
def pk_uniqueness(df, column):  # DQ-01
    total_rows = len(df)
    unique_values = df[column].nunique()
    if total_rows != unique_values:
        return "CRITICAL: Duplicate values found"
    return "Pass"
 
 
def check_annual_pk_uniqueness(df):  # DQ-02
    total_rows = len(df)
    unique_combinations = df[['company_id', 'year']].drop_duplicates().shape[0]
    if total_rows != unique_combinations:
        return "CRITICAL: duplicate (company_id, year) pairs found"
    return "Pass"
 
 
def deduplicate_annual(df):  # DQ-02 fix
    duplicated_rows = df[df.duplicated(subset=['company_id', 'year'], keep='last')]
    clean_df = df.drop_duplicates(subset=['company_id', 'year'], keep='last')
    return clean_df, duplicated_rows
 
 
def check_fk_integrity(child_df, parent_df, child_col, parent_col):  # DQ-03
    child_ids = set(child_df[child_col].unique())
    parent_ids = set(parent_df[parent_col].unique())
    orphans = child_ids - parent_ids
    bad_rows = child_df[child_df[child_col].isin(orphans)]
    if orphans:
        return f"CRITICAL: {len(orphans)} orphan company_ids found: {orphans}", bad_rows
    return "Pass", bad_rows
 
 
def check_bs_balance(df):  # DQ-04
    diff_pct = abs(df['total_assets'] - df['total_liabilities']) / df['total_assets']
    bad_rows = df[diff_pct >= 0.01]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows where BS doesn't balance", bad_rows
    return "Pass", bad_rows
 
 
def check_opm_crosscheck(df):  # DQ-05
    calculated_opm = (df['operating_profit'] / df['sales']) * 100
    diff = abs(df['opm_percentage'] - calculated_opm)
    bad_rows = df[diff >= 1.0]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows where OPM mismatch", bad_rows
    return "Pass", bad_rows
 
 
def check_positive_sales(df):  # DQ-06
    bad_rows = df[df['sales'] <= 0]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows with non-positive sales", bad_rows
    return "Pass", bad_rows
 
 
def check_year_format(df):  # DQ-07
    pattern = r'^\d{4}-\d{2}$'
    bad_rows = df[~df['year'].astype(str).str.match(pattern)]
    if len(bad_rows) > 0:
        return f"CRITICAL: {len(bad_rows)} rows with invalid year format", bad_rows
    return "Pass", bad_rows
 
 
def check_ticker_format(df, column='company_id'):  # DQ-08
    bad_rows = df[~df[column].str.len().between(2, 12)]
    if len(bad_rows) > 0:
        return f"CRITICAL: {len(bad_rows)} tickers with invalid length", bad_rows
    return "Pass", bad_rows
 
 
def check_net_cash(df):  # DQ-09
    calculated = df['operating_activity'] + df['investing_activity'] + df['financing_activity']
    diff = abs(df['net_cash_flow'] - calculated)
    bad_rows = df[diff > 10]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows where net cash flow doesn't match components", bad_rows
    return "Pass", bad_rows
 
 
def check_fixed_assets(df):  # DQ-10
    bad_rows = df[df['fixed_assets'] < 0]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows with negative fixed_assets", bad_rows
    return "Pass", bad_rows
 
 
def check_tax_rate(df):  # DQ-11
    bad_rows = df[(df['tax_percentage'] < 0) | (df['tax_percentage'] > 60)]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows with tax_percentage out of range", bad_rows
    return "Pass", bad_rows
 
 
def check_dividend_payout(df):  # DQ-12
    bad_rows = df[df['dividend_payout'] > 200]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows with dividend_payout > 200%", bad_rows
    return "Pass", bad_rows
 
 
def check_url_validity(df, sample_size=None):  # DQ-13
    urls_df = df.dropna(subset=['Annual_Report'])
    if sample_size:
        urls_df = urls_df.sample(min(sample_size, len(urls_df)))
 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    bad_indexes = []
    for idx, row in urls_df.iterrows():
        try:
            response = requests.head(row['Annual_Report'], timeout=5, headers=headers)
            if response.status_code != 200:
                bad_indexes.append(idx)
        except requests.RequestException:
            bad_indexes.append(idx)
 
    bad_rows = urls_df.loc[bad_indexes]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)}/{len(urls_df)} URLs failed or returned non-200", bad_rows
    return "Pass", bad_rows
 
 
def check_eps_sign(df):  # DQ-14
    bad_rows = df[(df['net_profit'] > 0) & (df['eps'] <= 0)]
    if len(bad_rows) > 0:
        return f"WARNING: {len(bad_rows)} rows with EPS/profit sign mismatch", bad_rows
    return "Pass", bad_rows
 
 
def check_bs_strict(df):  # DQ-15
    bad_rows = df[df['total_assets'] != df['total_liabilities']]
    return f"INFO: {len(bad_rows)} rows with exact BS mismatch (informational only)", bad_rows
 
 
def check_coverage(df):  # DQ-16
    years_per_company = df.groupby('company_id')['year'].nunique()
    low_coverage = years_per_company[years_per_company < 5]
    bad_rows = df[df['company_id'].isin(low_coverage.index)]
    if len(low_coverage) > 0:
        return f"WARNING: {len(low_coverage)} companies with <5 years of data", bad_rows
    return "Pass", bad_rows
 
 
def rows_to_records(bad_rows, rule_id, severity, issue):
    """Turn a DataFrame of bad rows into a list of dicts for the CSV report."""
    records = []
    for _, row in bad_rows.iterrows():
        records.append({
            'company_id': row.get('company_id', row.get('id', 'N/A')),
            'year': row.get('year', 'N/A'),
            'rule': rule_id,
            'severity': severity,
            'issue': issue
        })
    return records
 
 
if __name__ == "__main__":
    df = load_file("data/n100/companies.xlsx")
    df_pl = load_profitandloss("data/n100/profitandloss.xlsx")
    df_bs = load_balancesheet("data/n100/balancesheet.xlsx")
    df_cf = load_cashflow("data/n100/cashflow.xlsx")
    df_docs = load_documents("data/n100/documents.xlsx")
 
    all_failures = []
 
    print("DQ-01:", pk_uniqueness(df, 'id'))
 
    print("DQ-02:", check_annual_pk_uniqueness(df_pl))
    clean_df, removed = deduplicate_annual(df_pl)
    print(f"  Deduplication: removed {len(removed)} rows, {len(clean_df)} remain")
    all_failures += rows_to_records(removed, "DQ-02", "CRITICAL", "duplicate (company_id, year) pair")
 
    msg, bad = check_fk_integrity(df_pl, df, 'company_id', 'id')
    print("DQ-03:", msg)
    all_failures += rows_to_records(bad, "DQ-03", "CRITICAL", "orphan company_id, no match in companies table")
 
    msg, bad = check_bs_balance(df_bs)
    print("DQ-04:", msg)
    all_failures += rows_to_records(bad, "DQ-04", "WARNING", "balance sheet does not balance")
 
    msg, bad = check_opm_crosscheck(df_pl)
    print("DQ-05:", msg)
    all_failures += rows_to_records(bad, "DQ-05", "WARNING", "OPM cross-check mismatch")
 
    msg, bad = check_positive_sales(df_pl)
    print("DQ-06:", msg)
    all_failures += rows_to_records(bad, "DQ-06", "WARNING", "non-positive sales")
 
    msg, bad = check_year_format(df_pl)
    print("DQ-07:", msg)
    all_failures += rows_to_records(bad, "DQ-07", "CRITICAL", "invalid year format")
 
    msg, bad = check_ticker_format(df_pl)
    print("DQ-08:", msg)
    all_failures += rows_to_records(bad, "DQ-08", "CRITICAL", "invalid ticker length")
 
    msg, bad = check_net_cash(df_cf)
    print("DQ-09:", msg)
    all_failures += rows_to_records(bad, "DQ-09", "WARNING", "net cash flow does not match components")
 
    msg, bad = check_fixed_assets(df_bs)
    print("DQ-10:", msg)
    all_failures += rows_to_records(bad, "DQ-10", "WARNING", "negative fixed assets")
 
    msg, bad = check_tax_rate(df_pl)
    print("DQ-11:", msg)
    all_failures += rows_to_records(bad, "DQ-11", "WARNING", "tax percentage out of range")
 
    msg, bad = check_dividend_payout(df_pl)
    print("DQ-12:", msg)
    all_failures += rows_to_records(bad, "DQ-12", "WARNING", "dividend payout over 200%")
 
    msg, bad = check_url_validity(df_docs, sample_size=30)
    print("DQ-13:", msg)
    all_failures += rows_to_records(bad, "DQ-13", "WARNING", "annual report URL invalid or unreachable")
 
    msg, bad = check_eps_sign(df_pl)
    print("DQ-14:", msg)
    all_failures += rows_to_records(bad, "DQ-14", "WARNING", "EPS/profit sign mismatch")
 
    msg, bad = check_bs_strict(df_bs)
    print("DQ-15:", msg)
    all_failures += rows_to_records(bad, "DQ-15", "INFO", "exact balance sheet mismatch")
 
    msg, bad = check_coverage(df_pl)
    print("DQ-16:", msg)
    all_failures += rows_to_records(bad, "DQ-16", "WARNING", "company has fewer than 5 years of data")
 
    # Write everything out to the CSV deliverable
    report_df = pd.DataFrame(all_failures)
    report_df.to_csv("output/validation_failures.csv", index=False)
    print(f"\nSaved {len(report_df)} total findings to output/validation_failures.csv")