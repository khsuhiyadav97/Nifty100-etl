from normaliser import normalize_ticker, normalize_year

def test_ticker_strip():
    assert normalize_ticker(" tcs ") == "TCS"

def test_ticker_lowercase():
    assert normalize_ticker("tcs") == "TCS"

def test_ticker_already_clean():
    assert normalize_ticker("TCS") == "TCS"

def test_ticker_leading_space():
    assert normalize_ticker(" TCS") == "TCS"

def test_ticker_trailing_space():
    assert normalize_ticker("TCS ") == "TCS"

def test_ticker_mixed_case():
    assert normalize_ticker("TcS") == "TCS"

def test_ticker_hyphenated():
    assert normalize_ticker("bajaj-auto") == "BAJAJ-AUTO"

def test_ticker_ampersand():
    assert normalize_ticker("m&m") == "M&M"

def test_ticker_single_char_padding():
    assert normalize_ticker(" a ") == "A"

def test_ticker_numbers():
    assert normalize_ticker("abb123") == "ABB123"

def test_ticker_multiple_spaces():
    assert normalize_ticker("   tcs   ") == "TCS"

def test_ticker_tab_whitespace():
    assert normalize_ticker("\ttcs\t") == "TCS"

def test_ticker_newline_whitespace():
    assert normalize_ticker("\ntcs\n") == "TCS"

def test_ticker_already_uppercase_with_spaces():
    assert normalize_ticker("  TCS  ") == "TCS"

def test_ticker_short_ticker():
    assert normalize_ticker("m") == "M"

def test_year_mar_dash_2digit():
    assert normalize_year("Mar-23") == "2023-03"

def test_year_dec_dash_2digit():
    assert normalize_year("Dec-22") == "2022-12"

def test_year_mar_dash_4digit():
    assert normalize_year("Mar-2023") == "2023-03"

def test_year_dec_dash_4digit():
    assert normalize_year("Dec-2022") == "2022-12"

def test_year_space_4digit():
    assert normalize_year("Dec 2023") == "2023-12"

def test_year_space_4digit_jun():
    assert normalize_year("Jun 2013") == "2013-06"

def test_year_plain_number():
    assert normalize_year("2023") == "2023-01"

def test_year_plain_number_different():
    assert normalize_year("2015") == "2015-01"

def test_year_ttm_uppercase():
    assert normalize_year("TTM") == "TTM"

def test_year_ttm_lowercase():
    assert normalize_year("ttm") == "TTM"

def test_year_ttm_mixed_case():
    assert normalize_year("Ttm") == "TTM"

def test_year_garbage_text():
    assert normalize_year("xyz") == "PARSE-ERROR"

def test_year_extra_text_suffix():
    assert normalize_year("Mar 2016 9m") == "PARSE-ERROR"

def test_year_extra_number_suffix():
    assert normalize_year("Mar 2023 15") == "PARSE-ERROR"

def test_year_empty_string():
    assert normalize_year("") == "PARSE-ERROR"

def test_year_leading_trailing_space():
    assert normalize_year("  Mar-23  ") == "2023-03"

def test_year_feb_dash_2digit():
    assert normalize_year("Feb-24") == "2024-02"

def test_year_jan_space_4digit():
    assert normalize_year("Jan 2020") == "2020-01"

def test_year_int_input():
    assert normalize_year(2023) == "2023-01"

def test_year_none_type():
    assert normalize_year(None) == "PARSE-ERROR"