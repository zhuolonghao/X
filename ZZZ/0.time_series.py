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


def calculate_period_metrics(ic, cf, bs, bs_avg, label, date_obj):
    """
    Applies specific formulas to a given set of statements.
    Added 'date_obj' to handle the specific statement date.
    """
    # Format the date to YYYY-MM-DD string
    stmt_date = date_obj.strftime('%Y-%m-%d') if hasattr(date_obj, 'strftime') else str(date_obj)

    rev = safe_get(ic, 'Total Revenue', 1e3)

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
        'Op Income': calculate_op_income_waterfall(ic_ltm),

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
        "BQR's FCF": (safe_get(cf, 'Operating Cash Flow') + safe_get(cf, 'Capital Expenditure')) / 1e3
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
            col_avg_bs = a_bs.iloc[:, i:i+2].mean(axis=1)

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
ticker_list = ["PLCE", 'CRI', 'GAP']

for symbol in ticker_list:
    df_time_series = get_stock_time_series(symbol)
    print(f"\n Exporting Time Series for {symbol}")
    print(df_time_series.applymap(format_numbers))
    df_time_series.reset_index().to_csv(f"{symbol}.csv", index=False)