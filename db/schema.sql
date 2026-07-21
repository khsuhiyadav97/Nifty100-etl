PRAGMA foreign_keys = ON;

CREATE TABLE  IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    company_name TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
);

CREATE TABLE profitandloss (
    id INTEGER,
    company_id TEXT,
    year TEXT,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm_percentage REAL,
    net_profit REAL,
    eps REAL,
    dividend_payout REAL,
    tax_percentage REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE balancesheet (
    id INTEGER,
    company_id TEXT,
    year TEXT,
    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    total_assets REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);