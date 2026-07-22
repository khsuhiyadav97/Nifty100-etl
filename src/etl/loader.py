import pandas as pd
from normaliser import normalize_ticker, normalize_year


def load_file(filename):
    df = pd.read_excel(filename, header=1)
    df['id'] = df['id'].apply(normalize_ticker)
    return df


def load_profitandloss(filename):
    df = pd.read_excel(filename, header=1)
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    return df


def load_balancesheet(filename):
    df = pd.read_excel(filename, header=1)
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    return df


def load_cashflow(filename):
    df = pd.read_excel(filename, header=1)
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    df["year"] = df["year"].apply(normalize_year)
    return df


def load_documents(filename):
    df = pd.read_excel(filename, header=1)
    df["company_id"] = df["company_id"].apply(normalize_ticker)
    return df


if __name__ == "__main__":
    df = load_file("data/n100/companies.xlsx")
    print(df.head())

    df_pl = load_profitandloss("data/n100/profitandloss.xlsx")
    print(df_pl[['company_id', 'year']].head())