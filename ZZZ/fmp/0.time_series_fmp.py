import pandas as pd
import requests

# --- Configuration ---
API_KEY = "5nTvG2lrPgVl9QBo7AadhieWKbjUQtUm"  # Replace with your actual key
BASE_URL = "https://financialmodelingprep.com/stable"

def get_fmp_data(endpoint, symbol, limit=5):
    # The 'stable' version requires 'symbol' to be a parameter (?symbol=HELE)
    # instead of part of the path (.../income-statement/HELE)
    url = f"{BASE_URL}/{endpoint}?symbol={symbol}&apikey={API_KEY}&limit={limit}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()

        # Check if the API returned an empty list (no data found)
        if not data:
            print(f"Warning: API returned empty data for {endpoint}")
            return []

        return data
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error fetching {endpoint}: {err}")
        return []
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return []

symbol = 'HELE'
inc_stmt = get_fmp_data("income-statement", symbol)
peers = get_fmp_data("", symbol)

df = pd.DataFrame(inc_stmt).T






# --- Helper Functions ---
def format_numbers(value):
    if pd.isna(value) or value == "N/A": return "N/A"
    if isinstance(value, str): return value
    if 0 < abs(value) < 2: return f"{value * 100:.1f}%"
    if abs(value) >= 1e9: return f"{value / 1e9:.2f}B"
    if abs(value) >= 1e6: return f"{value / 1e6:.2f}M"
    if abs(value) >= 1e3: return f"{value / 1e3:.2f}K"
    return f"{value:.1f}"


# --- Scoring Functions (Same as your original) ---
def map_to_op_lev(v):
    if v is None or pd.isna(v): return 75
    thresholds = [(0.5, 15), (1.0, 25), (1.75, 35), (2.5, 42), (3.25, 45), (3.75, 48), (4.25, 52), (4.75, 55),
                  (5.25, 58), (6.25, 65)]
    for limit, score in thresholds:
        if v < limit: return score
    return 75


# --- Main Logic ---
def get_stock_metrics_fmp(symbol):
    # Fetch Annual Data (Income Statement, Balance Sheet, Cash Flow)
    inc_stmt = get_fmp_data("income-statement", symbol)
    bal_sheet = get_fmp_data("balance-sheet-statement", symbol)
    cash_flow = get_fmp_data("cash-flow-statement", symbol)

    if not inc_stmt or not bal_sheet or not cash_flow:
        print(f"No data found for {symbol}")
        return None

    results = []
    # FMP returns a list of dicts (one per year)
    for i in range(len(inc_stmt)):
        ic = inc_stmt[i]
        bs = bal_sheet[i]
        cf = cash_flow[i]

        # FMP Key Names (slightly different from yfinance)
        rev = ic.get('revenue', 0)
        ebitda = ic.get('ebitda', 0)
        debt = bs.get('totalDebt', 0)
        int_exp = ic.get('interestExpense', 0)
        ocf = cf.get('operatingCashFlow', 0)
        capex = cf.get('capitalExpenditure', 0)
        fcf = ocf + capex  # Capex is usually negative in FMP

        # Calculate Ratios
        debt_ebitda = round(debt / ebitda, 2) if ebitda != 0 else 999
        icr = round(ebitda / abs(int_exp), 2) if int_exp != 0 else 999

        # CCC Calculation
        cogs = ic.get('costOfRevenue', 0)
        ar = bs.get('netReceivables', 0)
        inv = bs.get('inventory', 0)
        ap = bs.get('accountPayables', 0)

        dso = (365 * ar / rev) if rev != 0 else 0
        dio = (365 * inv / cogs) if cogs != 0 else 0
        dpo = (365 * ap / cogs) if cogs != 0 else 0

        metrics = {
            'Period': f"FY {ic.get('calendarYear')}",
            'Date': ic.get('date'),
            'Revenue': format_numbers(rev),
            'EBITDA': format_numbers(ebitda),
            'Net Income': format_numbers(ic.get('netIncome', 0)),
            'Debt': format_numbers(debt),
            'FCF': format_numbers(fcf),
            'Total Debt / EBITDA': debt_ebitda,
            'Interest Coverage': icr,
            'CCC': f"{dso + dio - dpo:.1f} Days",
            'Score: Op Leverage': map_to_op_lev(debt_ebitda),
            # Add your other scores here...
        }
        results.append(metrics)

    df = pd.DataFrame(results).set_index('Period').T
    return df


# --- Execution ---
ticker = "AAPL"
df_fmp = get_stock_metrics_fmp(ticker)
if df_fmp is not None:
    print(f"\nFinancial Analysis for {ticker} (via FMP)")
    print(df_fmp)