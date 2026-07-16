import pandas as pd
from normaliser import normalize_ticker, normalize_year

def load_file(filename):
        df = pd.read_excel(filename, header=1)
        df['id'] = df['id'].apply(normalize_ticker)
        return df
if __name__ == "__main__":
        filename = "data/n100/companies.xlsx"
        df = load_file(filename)
        print(df.head())

def load_profitandloss(filename2):
        df = pd.read_excel(filename2, header=1)
        df["company_id"] = df["company_id"].apply(normalize_ticker)
        df["year"] = df["year"].apply(normalize_year)
        return df
if __name__ == "__main__":
        filename2 = "data/n100/profitandloss.xlsx"
        df2 = load_profitandloss(filename2)
        print(df2[['company_id', 'year']].head())