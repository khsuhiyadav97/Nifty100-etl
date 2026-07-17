import pandas as pd
from loader import load_file
from loader import load_file, load_profitandloss

def pk_uniqueness(df, column):
    total_rows = len(df)
    unique_values = df[column].nunique()
    if total_rows != unique_values:
        return "CRITICAL: Duplicate values found"
    return "Pass"

def deduplicate_annual(df):
    duplicated_rows = df[df.duplicated(subset=['company_id', 'year'], keep='last')]
    clean_df = df.drop_duplicates(subset=['company_id', 'year'], keep='last')
    return clean_df, duplicated_rows

if __name__ == "__main__":
        filename = "data/n100/companies.xlsx"
        df = load_file(filename)
        print(df.head())
        result = pk_uniqueness(df, 'id')
        print(result)

def check_annual_pk_uniqueness(df):
    total_rows = len(df)
    unique_combinations = df[['company_id', 'year']].drop_duplicates().shape[0]
    if total_rows != unique_combinations:
        return "CRITICAL: duplicate (company_id, year) pairs found"
    return "Pass"

if __name__ == "__main__":
    df_pl = load_profitandloss("data/n100/profitandloss.xlsx")
    print(check_annual_pk_uniqueness(df_pl))

    duplicates = df_pl[df_pl.duplicated(subset=['company_id', 'year'], keep=False)]
    print(duplicates)

    raw_df = pd.read_excel("data/n100/profitandloss.xlsx", header=1)
    failed_rows = raw_df[raw_df['company_id'].isin(['AMBUJACEM', 'HCLTECH', 'SHREECEM'])]
    print(failed_rows[['company_id', 'year']])

    clean_df, removed = deduplicate_annual(df_pl)
    print(f"Removed {len(removed)} duplicate rows")
    print(f"Clean data has {len(clean_df)} rows")

