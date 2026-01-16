
import yfinance as yf
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def format_numbers(value):
    """Converts a number into a string with K, M, or B suffixes."""
    if value is None: return "N/A"

    # Handle percentages (values usually < 2 in your logic)
    if 0 <= abs(value) < 2:
        return f"{value * 100:.1f}%"

    abs_val = abs(value)
    if abs_val >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif abs_val >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif abs_val >= 1_000:
        return f"{value / 1_000:.2f}k"
    else:
        return str(round(value, 1))

def safe_get(data_series, key, divisor=1e3):
    """
    Safely retrieves a key from a Series.
    Returns 0 if the key is missing.
    """
    return data_series.get(key, 0) / divisor


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

def get_stock_metrics(ticker_symbol):
    """Pulls and calculates financial metrics for a single ticker."""
    try:
        ticker = yf.Ticker(ticker_symbol)

        # Pull Financial Statements
        cf = ticker.quarterly_cashflow
        bs = ticker.quarterly_balance_sheet
        ic = ticker.quarterly_financials
        info = ticker.info

        date_obj = cf.columns[0]
        stmt_date = date_obj.strftime('%Y-%m-%d') if hasattr(date_obj, 'strftime') else str(date_obj)

        # Calculate LTM (Last Twelve Months) by summing last 4 quarters
        if cf.shape[1] < 4 or ic.shape[1] < 4 or bs.shape[1] < 4:
            return {"Ticker": ticker_symbol, "Error": "Incomplete Q data"}

        cf_ltm = cf.iloc[:, :4].sum(axis=1)
        ic_ltm = ic.iloc[:, :4].sum(axis=1)
        bs_avg = bs.iloc[:, :4].mean(axis=1)

        # Extraction logic with fallbacks for missing keys
        data = {
            'Ticker': ticker_symbol,
            'mkt_cap': info['marketCap']/1e6,
            'EV': info['enterpriseValue']/1e6,
            'avg vol (3M)': format_numbers(info['averageDailyVolume3Month']),
            'avg vol (10D)': format_numbers(info['averageDailyVolume10Day']),
            'o/s shares': format_numbers(info['floatShares']),
            '% Insider': format_numbers(info['heldPercentInsiders']),
            '% Inst.': format_numbers(info['heldPercentInstitutions']),
            '% Short': format_numbers(info['shortPercentOfFloat']),
            'DSO': format_numbers(365 * bs_avg['Accounts Receivable']/ic_ltm['Total Revenue']),
            'DIO': format_numbers(365 * bs_avg['Inventory']/ic_ltm['Cost Of Revenue']),
            'DPO': format_numbers(365 * bs_avg['Accounts Payable']/ic_ltm['Cost Of Revenue']),
            "cash": bs.iloc[:, 0]['Cash And Cash Equivalents'] / 1e3,
            "debt": bs.iloc[:, 0]['Total Debt'] / 1e3,
            'revenue_yoy': ic.iloc[:, 0]['Total Revenue'] / ic.iloc[:, 4]['Total Revenue'] - 1,
            'revenue': ic_ltm['Total Revenue'] / 1e3,
            'op income': calculate_op_income_waterfall(ic_ltm),
            'EBITDA': ic_ltm['EBITDA'] / 1e3,
            'Net Income': ic_ltm['Net Income Continuous Operations'] / 1e3,
            'Adj. EBITDA': ic_ltm['Normalized EBITDA'] / 1e3,
            'D & A': cf_ltm['Depreciation And Amortization'] / 1e3,
            'Net Int Inc': safe_get(ic_ltm, 'Net Interest Income'),
            'Tax Provision': ic_ltm['Tax Provision'] / 1e3,
            'Adj. Net Income': safe_get(ic_ltm, 'Normalized EBITDA')
                               - safe_get(cf_ltm, 'Depreciation And Amortization')
                               - safe_get(ic_ltm, 'Tax Provision')
                               + safe_get(ic_ltm, 'Net Interest Income'),
            'CapEx': cf_ltm['Capital Expenditure'] / 1e3,
            'OCF': cf_ltm['Operating Cash Flow'] / 1e3,
            "BQR's FCF": (cf_ltm['Operating Cash Flow'] + cf_ltm['Capital Expenditure']) / 1e3,
            'Financial Date': stmt_date,
            "Total Debt / Adj Ebitda": round(bs.iloc[:, 0]['Total Debt'] / ic_ltm['Normalized EBITDA'],2) if ic_ltm['Normalized EBITDA'] >0 else 999,
            "Adj Ebitda / Interest Expense": round(ic_ltm['Normalized EBITDA'] / - safe_get(ic_ltm, 'Net Interest Income', divisor=1), 2) if safe_get(ic_ltm, 'Net Interest Income') < 0 else 999,
            'Net Profit before extraordinary': safe_get(ic_ltm, 'Normalized EBITDA')
                               - safe_get(cf_ltm, 'Depreciation And Amortization')
                               - safe_get(ic_ltm, 'Tax Provision')
                               + safe_get(ic_ltm, 'Net Interest Income'),
            "(NCO-CAPEX) / Total Debt (%)": round(100*(cf_ltm['Operating Cash Flow'] + cf_ltm['Capital Expenditure']) / bs.iloc[:, 0]['Total Debt'],2) if bs.iloc[:, 0]['Total Debt'] >0 else 999,
        }
        return data

    except Exception as e:
        return {"Ticker": ticker_symbol, "Error": str(e)}


def map_to_op_lev(v):
    thresholds = [
        (0.5, 15),
        (1.0, 25),
        (1.75, 35),
        (2.5, 42),
        (3.25, 45),
        (3.75, 48),
        (4.25, 52),
        (4.75, 55),
        (5.25, 58),
        (6.25, 65)
    ]
    for limit, score in thresholds:
        if v < limit:
            return score
    return 75

def map_to_icr(v):
    thresholds = [
        (30, 15),
        (15, 25),
        (12, 35),
        (9.75, 42),
        (7.75, 45),
        (5, 48),
        (4.5, 52),
        (4, 55),
        (2.5, 58),
        (1.5, 65)
    ]
    for limit, score in thresholds:
        if v >= limit:
            return score
    return 75

def map_to_ni(v):
    thresholds = [
        (4000, 15),
        (1000, 25),
        (200, 35),
        (75, 42),
        (50, 45),
        (25, 48),
        (15, 52),
        (5, 55),
        (0, 58),
        (-20, 65)
    ]
    for limit, score in thresholds:
        if v/1e3 >= limit:
            return score
    return 75

def map_to_fcf(v):
    thresholds = [
        (50, 15),
        (40, 25),
        (30, 35),
        (23, 42),
        (20, 45),
        (17, 48),
        (15, 52),
        (12, 55),
        (7, 58),
        (5.5, 65)
    ]
    for limit, score in thresholds:
        if v >= limit:
            return score
    return 75
# --- Execution ---
# List of your dozen stocks
ticker_list = ["HELE", 'YETI', 'NWL', 'SPB']
#ticker_list = ["PLCE", 'CRI', 'GAP']
#ticker_list = ["SLAB", 'STM', 'TXN', 'NXPI', 'MCHP', 'AVGO', 'QCOM', 'SYNA']  # first five

all_results = []
print(f"Fetching data for {len(ticker_list)} stocks...")
for symbol in ticker_list:
    print(f"Processing {symbol}...")
    metrics = get_stock_metrics(symbol)
    metrics['BQR'] = (map_to_op_lev(metrics['Total Debt / Adj Ebitda']) * 0.35
                      + map_to_icr(metrics['Adj Ebitda / Interest Expense']) * 0.15
                      + map_to_ni(metrics['Net Profit before extraordinary']) * 0.25
                      + map_to_fcf(metrics['(NCO-CAPEX) / Total Debt (%)']) * 0.25)
    metrics['Net Profit before extraordinary'] = "{:.1f}M".format(metrics['Net Profit before extraordinary']/1e3)
    all_results.append(metrics)
# Create a clean Table
df = pd.DataFrame(all_results)
print("\n--- Summary Table ---")
print(df.to_string(index=False))
# Optional: Export to CSV
df.T.reset_index().to_csv(f"peer_analysis_{ticker_list[0]}.csv", index=False)