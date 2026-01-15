import pandas as pd
import yfinance as yf


# --- Helper Functions ---
def format_numbers(value):
    """Formats large numbers for readability."""
    if pd.isna(value) or value == "N/A": return "N/A"
    if isinstance(value, str): return value
    if abs(value) < 2: return f"{value * 100:.1f}%"
    if abs(value) >= 1e9: return f"{value / 1e9:.2f}B"
    if abs(value) >= 1e6: return f"{value / 1e6:.2f}M"
    if abs(value) >= 1e3: return f"{value / 1e3:.2f}K"
    return f"{value:.1f}"


def safe_get(series, key, divisor=1):
    """Safely retrieves a value from a Series, returns 0 if missing."""
    return series.get(key, 0) / divisor

def calculate_op_income_waterfall(df):
    # 1. Attempt to get manual components
    # Note: yfinance uses 'Selling General Administrative' (no 'And')
    rev = df.get('Total Revenue')
    cor = df.get('Cost Of Revenue')
    sga = df.get('Selling General And Administration')

    # Check if all manual components exist and are not NaN
    manual_components = [rev, cor, sga]

    if all(v is not None for v in manual_components) and not any(pd.isna(manual_components)):
        return (rev - cor - sga) / 1e3

    # 2. Fallback: Use reported Operating Income
    # If that is also missing, return 0
    return df.get('Operating Income', 0) / 1e3

# --- Mapping Functions (15-75 Scoring) ---
def map_to_op_lev(v):
    if v is None or pd.isna(v): return 999
    thresholds = [(0.5, 15), (1.0, 25), (1.75, 35), (2.5, 42), (3.25, 45),
                  (3.75, 48), (4.25, 52), (4.75, 55), (5.25, 58), (6.25, 65)]
    for limit, score in thresholds:
        if v < limit: return score
    return 75

def map_to_icr(v):
    if v is None or pd.isna(v) or v == 999: return 999
    thresholds = [(30, 15), (15, 25), (12, 35), (9.75, 42), (7.75, 45),
                  (5, 48), (4.5, 52), (4, 55), (2.5, 58), (1.5, 65)]
    for limit, score in thresholds:
        if v > limit: return score
    return 75

def map_to_ni(v):
    if v is None or pd.isna(v): return 999
    thresholds = [(4000, 15), (1000, 25), (200, 35), (75, 42), (50, 45),
                  (25, 48), (15, 52), (5, 55), (0, 58), (-20, 65)]
    for limit, score in thresholds:
        if v/1e3 > limit: return score
    return 75

def map_to_fcf(v):
    if v is None or pd.isna(v) or v == 999: return 999
    thresholds = [(50, 15), (40, 25), (30, 35), (23, 42), (20, 45),
                  (17, 48), (15, 52), (12, 55), (7, 58), (5.5, 65)]
    for limit, score in thresholds:
        if v > limit: return score
    return 75

def calculate_period_metrics(ic, cf, bs, bs_avg, label, date_obj):
    """
    Applies specific formulas to a given set of statements.
    Added 'date_obj' to handle the specific statement date.
    """
    # Format the date to YYYY-MM-DD string
    stmt_date = date_obj.strftime('%Y-%m-%d') if hasattr(date_obj, 'strftime') else str(date_obj)

    rev = safe_get(ic, 'Total Revenue', 1e3)

    ebitda_val = ic.get('Normalized EBITDA', ic.get('EBITDA', 0))
    debt_val = bs.get('Total Debt', 0)
    net_int_val = ic.get('Net Interest Income', 0)
    fcf_val = cf.get('Operating Cash Flow', 0) + cf.get('Capital Expenditure', 0)

    # Logic for the 4 Metrics (with 999 fallbacks)
    debt_ebitda = round(debt_val / ebitda_val, 2) if ebitda_val > 0 else 999
    icr = round(ebitda_val / abs(net_int_val), 2) if net_int_val < 0 else 999
    ni_extra = (safe_get(ic, 'Normalized EBITDA')
                - safe_get(cf, 'Depreciation And Amortization')
                - safe_get(ic, 'Tax Provision')
                + safe_get(ic, 'Net Interest Income'))
    fcf_debt_pct = round(100 * fcf_val / debt_val, 2) if debt_val > 0 else 999

    metrics = {
        'Period': label,
        'Statement Date': stmt_date,  # <--- New Row Added Here

        'DSO': format_numbers(365 * bs_avg['Accounts Receivable'] / ic['Total Revenue']),
        'DIO': format_numbers(365 * bs_avg['Inventory'] / ic['Cost Of Revenue']),
        'DPO': format_numbers(365 * bs_avg['Accounts Payable'] / ic['Cost Of Revenue']),

        # Balance Sheet Snapshots (End of Period)
        "Cash": safe_get(bs, 'Cash And Cash Equivalents', 1e3),
        "Debt": safe_get(bs, 'Total Debt', 1e3),

        # P&L Metrics
        'Revenue': rev,
        'Op Income': calculate_op_income_waterfall(ic),

        'EBITDA': safe_get(ic, 'EBITDA', 1e3),
        'Net Income': safe_get(ic, 'Net Income Continuous Operations', 1e3),
        'Adj. EBITDA': safe_get(ic, 'Normalized EBITDA', 1e3),

        # Cash Flow & Adjustments
        'D & A': safe_get(cf, 'Depreciation And Amortization', 1e3),
        'Net Int Inc': safe_get(ic, 'Net Interest Income', 1e3),
        'Tax Provision': safe_get(ic, 'Tax Provision', 1e3),

        # Complex Calculations
        'Adj. Net Income': (safe_get(ic, 'Normalized EBITDA')
                            - safe_get(cf, 'Depreciation And Amortization')
                            - safe_get(ic, 'Tax Provision')
                            + safe_get(ic, 'Net Interest Income')) / 1e3,

        'CapEx': safe_get(cf, 'Capital Expenditure', 1e3),
        'OCF': safe_get(cf, 'Operating Cash Flow', 1e3),
        "BQR's FCF": (safe_get(cf, 'Operating Cash Flow') + safe_get(cf, 'Capital Expenditure')) / 1e3,
        'COGS': safe_get(ic, 'Cost Of Revenue', 1),
        'AR': (bs_avg['Accounts Receivable']),
        'INV': (bs_avg['Inventory']),
        'AP': (bs_avg['Accounts Payable']),

        # --- THE FOUR REQUESTED METRICS ---
        'Total Debt / Adj Ebitda': debt_ebitda,
        'Adj Ebitda / Interest Expense': icr,
        'Net Profit before extraordinary': f"{ni_extra / 1e6:.1f}M",
        '(NCO-CAPEX) / Total Debt (%)': fcf_debt_pct,
        # --- THE MAPPED SCORES ---
        'Score: Operating Leverage': map_to_op_lev(debt_ebitda),
        'Score: ICR': map_to_icr(icr),
        'Score: Net Income': map_to_ni(ni_extra/1e3),
        'Score: FCF/Debt': map_to_fcf(fcf_debt_pct),
        'BQR': map_to_op_lev(debt_ebitda)*0.35 + map_to_icr(icr)*0.15 + map_to_ni(ni_extra/1e3)*0.25 + map_to_fcf(fcf_debt_pct)*0.25
    }
    return metrics


def get_stock_time_series(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)

        # 1. Fetch Quarterly (for LTM) and Annual (for FY) data
        q_ic = ticker.quarterly_financials
        q_cf = ticker.quarterly_cashflow
        q_bs = ticker.quarterly_balance_sheet

        a_ic = ticker.financials
        a_cf = ticker.cashflow
        a_bs = ticker.balance_sheet

        results = []

        # --- A. Construct LTM Periods (Recent 2 Quarters) ---
        if q_ic.shape[1] >= 5 and q_cf.shape[1] >= 5:
            for i in range(2):
                # Sum 4 quarters for P&L/Cashflow
                ltm_ic = q_ic.iloc[:, i:i + 4].sum(axis=1)
                ltm_cf = q_cf.iloc[:, i:i + 4].sum(axis=1)
                avg_bs = q_bs.iloc[:, i:i + 4].mean(axis=1)
                # Take snapshot for Balance Sheet (End of the specific quarter)
                ltm_bs = q_bs.iloc[:, i]

                # Dynamic Label
                label = "LTM (Current)" if i == 0 else f"LTM (-{i}Q)"

                # Extract the date from the column header (Most recent quarter in the sums)
                date_obj = q_ic.columns[i]

                results.append(calculate_period_metrics(ltm_ic, ltm_cf, ltm_bs, avg_bs, label, date_obj))
        else:
            print(f"Warning: {ticker_symbol} has insufficient quarterly data for 2 LTM periods.")

        # --- B. Construct Annual Periods (Last 3 Years) ---
        years_available = min(3, a_ic.shape[1])
        for i in range(years_available):
            col_ic = a_ic.iloc[:, i]
            col_cf = a_cf.iloc[:, i]
            col_bs = a_bs.iloc[:, i]
            col_avg_bs = a_bs.iloc[:, i]

            # Extract Year and Date
            period_date = a_ic.columns[i]  # This is the Timestamp
            label = f"FY {period_date.year}"

            results.append(calculate_period_metrics(col_ic, col_cf, col_bs, col_avg_bs, label, period_date))

        # --- C. Build DataFrame ---
        df = pd.DataFrame(results)
        df.set_index('Period', inplace=True)
        df = df.T
        return df

    except Exception as e:
        print(f"Error processing {ticker_symbol}: {e}")
        return None


# --- Execution ---
#ticker_list = ["HELE", 'YETI', 'LCUT', 'NWL', 'SPB']
#ticker_list = ["FLWS"]
#ticker_list = ["PLCE", 'CRI', 'GAP']
#ticker_list = ["SLAB", 'STM', 'TXN', 'NXPI', 'MCHP', 'AVGO', 'QCOM', 'SYNA']  # first five
ticker_list = ["HELE", 'YETI', 'NWL', 'SPB']

for symbol in ticker_list:
    df_time_series = get_stock_time_series(symbol)
    print(f"\n Exporting Time Series for {symbol}")
    print(df_time_series.applymap(format_numbers))
    df_time_series.reset_index().to_csv(f"{symbol}.csv", index=False)