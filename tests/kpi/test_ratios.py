import sys
sys.path.append('src/analytics')

from ratios_clean import (
    net_profit_margin, operating_profit_margin,
    return_on_equity, return_on_capital_employed
)
from leverage_ratios_clean import debt_to_equity, interest_coverage, asset_turnover
from cagr import calc_cagr
from cashflow_kpis import free_cash_flow, cfo_pat_ratio, capex_intensity


# --- Profitability ---

def test_npm_normal():
    assert net_profit_margin(100, 500) == 20.0

def test_npm_zero_sales():
    assert net_profit_margin(100, 0) is None

def test_opm_normal():
    assert operating_profit_margin(150, 500) == 30.0

def test_opm_zero_sales():
    assert operating_profit_margin(150, 0) is None

def test_roe_positive_equity():
    assert return_on_equity(100, 400, 100) == 20.0

def test_roe_negative_equity():
    assert return_on_equity(100, -400, 100) is None

def test_roe_zero_equity():
    assert return_on_equity(100, 0, 0) is None

def test_roce_normal():
    result = return_on_capital_employed(200, 50, 400, 100, 200)
    assert round(result, 2) == round((150 / 700) * 100, 2)

def test_roce_zero_capital():
    assert return_on_capital_employed(200, 50, 0, 0, 0) is None


# --- Leverage & Efficiency ---

def test_de_debtfree():
    ratio, flag = debt_to_equity(0, 400, 100)
    assert ratio == 0

def test_de_high_leverage_flagged():
    ratio, flag = debt_to_equity(3000, 400, 100, is_financial=False)
    assert flag is True

def test_de_high_leverage_financial_not_flagged():
    ratio, flag = debt_to_equity(3000, 400, 100, is_financial=True)
    assert flag is False

def test_icr_debtfree():
    ratio, label = interest_coverage(200, 20, 0)
    assert ratio is None and label == "Debt Free"

def test_icr_safe():
    ratio, label = interest_coverage(200, 20, 50)
    assert label == "Safe"

def test_asset_turnover_normal():
    assert asset_turnover(500, 250) == 2.0

def test_asset_turnover_zero_assets():
    assert asset_turnover(500, 0) is None


# --- CAGR ---

def test_cagr_normal_growth():
    cagr, flag = calc_cagr(100, 161, 5)
    assert flag is None and round(cagr, 1) == 10.0

def test_cagr_turnaround():
    cagr, flag = calc_cagr(-100, 200, 3)
    assert cagr is None and flag == "TURNAROUND"

def test_cagr_zero_base():
    cagr, flag = calc_cagr(0, 200, 3)
    assert cagr is None and flag == "ZERO_BASE"


# --- Cash Flow ---

def test_fcf_calculation():
    assert free_cash_flow(300, -100) == 200

def test_cfo_pat_high_quality():
    ratio, label = cfo_pat_ratio(150, 100)
    assert label == "High Quality Earnings"

def test_capex_intensity_asset_light():
    intensity, label = capex_intensity(-10, 1000)
    assert label == "Asset-Light"