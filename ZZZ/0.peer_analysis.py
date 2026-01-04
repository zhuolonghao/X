
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

def get_stock_metrics(ticker_symbol):
    """Pulls and calculates financial metrics for a single ticker."""
    try:
        ticker = yf.Ticker(ticker_symbol)

        # Pull Financial Statements
        cf = ticker.quarterly_cashflow
        bs = ticker.quarterly_balance_sheet
        ic = ticker.quarterly_financials
        info = ticker.info

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
            'op income': ic_ltm['Total Revenue'] / 1e3 - ic_ltm['Cost Of Revenue'] / 1e3 - ic_ltm['Selling General And Administration'] / 1e3 ,
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
            "BQR's FCF": (cf_ltm['Operating Cash Flow'] + cf_ltm['Capital Expenditure']) / 1e3
        }
        return data

    except Exception as e:
        return {"Ticker": ticker_symbol, "Error": str(e)}


# --- Execution ---
# List of your dozen stocks
ticker_list = ["HELE", 'YETI', 'LCUT', 'NWL', 'SPB']

all_results = []
print(f"Fetching data for {len(ticker_list)} stocks...")

for symbol in ticker_list:
    print(f"Processing {symbol}...")
    metrics = get_stock_metrics(symbol)
    all_results.append(metrics)

# Create a clean Table
df = pd.DataFrame(all_results)
print("\n--- Summary Table ---")
print(df.to_string(index=False))

# Optional: Export to CSV
df.T.reset_index().to_csv("peer_analysis.csv", index=False)