from normaliser import normalize_ticker, normalize_year

def test_ticker_strip():
    assert normalize_ticker(" tcs ") == "TCS"
    