import pandas as pd
import requests
import time

# --- Configuration ---
#API_KEY = "PTIKPYJ08KJ0X8T5"  # Replace with your actual key
#API_KEY = "DLTHXPRVU26T0J2K"
#API_KEY = "1PJAD8TJTI99U5V4"
#API_KEY = 'BUPOTKIYO88O640R'
BASE_URL = "https://www.alphavantage.co"

def get_data(endpoint, symbol, quarter):
    # The 'stable' version requires 'symbol' to be a parameter (?symbol=HELE)
    # instead of part of the path (.../income-statement/HELE)
    if quarter:
        url = f"{BASE_URL}/query?function={endpoint}&symbol={symbol}&quarter={quarter}&apikey={API_KEY}"
    else:
        url = f"{BASE_URL}/query?function={endpoint}&symbol={symbol}&apikey={API_KEY}"

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

def format_data(df, vars):
    tmp = df.sort_values('fiscalDateEnding', ascending=True)\
            .set_index(['fiscalDateEnding', 'reportedCurrency'])\
            .apply(pd.to_numeric, errors='coerce')
    return tmp[vars]
# Financials is one day delay
symbol = 'YETI'
endpoint='INCOME_STATEMENT'
df = get_data(endpoint, symbol, quarter=False)
inc_stmt = pd.DataFrame(df['quarterlyReports'])
_var = ['grossProfit','totalRevenue', 'costOfRevenue',
        'operatingIncome','operatingExpenses', 'sellingGeneralAndAdministrative',
        'netIncome', 'netInterestIncome', 'incomeTaxExpense',
        'ebit','ebitda']
inc_stmt2 = format_data(inc_stmt, _var)
time.sleep(5)

endpoint='BALANCE_SHEET'
df = get_data(endpoint, symbol, quarter=False)
bs_stmt = pd.DataFrame(df['quarterlyReports'])
_var = ['currentNetReceivables', 'inventory', 'currentAccountsPayable',
        'cashAndCashEquivalentsAtCarryingValue', 'shortLongTermDebtTotal', 'commonStockSharesOutstanding']
bs_stmt2 = format_data(bs_stmt, _var)
time.sleep(5)

endpoint='CASH_FLOW'
df = get_data(endpoint, symbol, quarter=False)
cf_stmt = pd.DataFrame(df['quarterlyReports'])
_var = ['operatingCashflow', 'capitalExpenditures', 'depreciationDepletionAndAmortization']
cf_stmt2 = format_data(cf_stmt, _var)
time.sleep(5)

df_final = inc_stmt2.join(cf_stmt2).join(bs_stmt2).reset_index()

# --- 1. Helper & Scoring Functions (Retained) ---
def format_numbers(value):
    if pd.isna(value) or value == "N/A" or value == 999 or value == -999: return "N/A"
    if isinstance(value, str): return value
    if abs(value) >= 1e9: return f"{value / 1e9:.2f}B"
    if abs(value) >= 1e6: return f"{value / 1e6:.2f}M"
    if abs(value) >= 1e3: return f"{value / 1e3:.2f}K"
    return f"{value:.2f}"


def map_to_op_lev(v):
    if v is None or pd.isna(v) or v == 999: return 75
    thresholds = [(0.5, 15), (1.0, 25), (1.75, 35), (2.5, 42), (3.25, 45),
                  (3.75, 48), (4.25, 52), (4.75, 55), (5.25, 58), (6.25, 65)]
    for limit, score in thresholds:
        if v < limit: return score
    return 75
def map_to_icr(v):
    if v is None or pd.isna(v) or v == 999: return 15
    thresholds = [(30, 15), (15, 25), (12, 35), (9.75, 42), (7.75, 45),
                  (5, 48), (4.5, 52), (4, 55), (2.5, 58), (1.5, 65)]
    for limit, score in thresholds:
        if v > limit: return score
    return 75
def map_to_ni(v):
    # Expects 'v' in Thousands (matches original logic scale)
    if v is None or pd.isna(v): return 75
    thresholds = [(4000, 15), (1000, 25), (200, 35), (75, 42), (50, 45),
                  (25, 48), (15, 52), (5, 55), (0, 58), (-20, 65)]
    for limit, score in thresholds:
        if v > limit: return score
    return 75
def map_to_fcf(v):
    if v is None or pd.isna(v) or v == 999: return 15
    thresholds = [(50, 15), (40, 25), (30, 35), (23, 42), (20, 45),
                  (17, 48), (15, 52), (12, 55), (7, 58), (5.5, 65)]
    for limit, score in thresholds:
        if v > limit: return score
    return 75


# --- 2. Calculation Engine ---
def calculate_metrics_row(row_dict, label):
    """
    Calculates metrics using direct dictionary keys.
    """
    # Safe extraction (default to 0)
    ebitda = row_dict.get('ebitda', 0)
    debt = row_dict.get('shortLongTermDebtTotal', 0)
    rev = row_dict.get('totalRevenue', 0)
    cogs = row_dict.get('costOfRevenue', 0)
    sga = row_dict.get('sellingGeneralAndAdministrative',0)

    gp = row_dict.get('grossProfit',0)
    rev_cogs_sga = rev - cogs - sga
    oi = row_dict.get('operatingIncome',0)
    ni = row_dict.get('netIncome', 0)

    dso = 365 * row_dict.get('currentNetReceivables', 0) / rev
    dio = 365 * row_dict.get('inventory', 0) / cogs
    dpo = 365 * row_dict.get('currentAccountsPayable', 0) / cogs

    # EBITDA and EBIT calculation: Net Interest = Income - Expense
    net_int_val = row_dict.get('netInterestIncome', 0)
    da = row_dict.get('depreciationDepletionAndAmortization', 0)
    tax = row_dict.get('incomeTaxExpense', 0)
    ebitda = ni + tax - net_int_val + da
    ebit = ni + tax - net_int_val

    # Free Cash Flow = OCF + CapEx (CapEx is usually negative)
    ocf = row_dict.get('operatingCashflow', 0)
    capex = row_dict.get('capitalExpenditures', 0)
    fcf_val = ocf + capex

    # --- Ratios ---
    # 1. Debt / EBITDA
    debt_ebitda = debt / ebitda if ebitda > 0 else 999

    # 2. ICR (EBITDA / Net Interest Expense)
    icr = ebitda / abs(net_int_val) if net_int_val < 0 and ebitda > 0 else -999

    # 3. FCF / Debt %
    fcf_debt_pct = 100 * fcf_val / debt if debt > 0 else 999

    # 4. profit margin %
    gp_margin = 100 * gp / rev
    op_margin = 100 * rev_cogs_sga / rev
    op2_margin = 100 * oi / rev
    ni_margin = 100 * ni / rev

    # --- Scores ---
    # Note: We scale 'ni' by 1e3 because map_to_ni expects thousands
    score_op_lev = map_to_op_lev(debt_ebitda)
    score_icr = map_to_icr(icr)
    score_ni = map_to_ni(ni / 1e3)
    score_fcf = map_to_fcf(fcf_debt_pct)

    bqr = (score_op_lev * 0.35 + score_icr * 0.15 + score_ni * 0.25 + score_fcf * 0.25)

    return {
        'Period': label,
        'Statement Date': row_dict.get('fiscalDateEnding'),

        # Balance sheet items
        'DSO': dso,
        'DIO': dio,
        'DPO': dpo,
        'FCF': fcf_val,
        'CCC': dso + dio - dpo,

        # Financials
        'Sale': rev,
        'Rev-CoGS / Sale (%)': gp_margin,
        'Rev-CoGS-SG&A / Sale (%)': op_margin,
        'Op. Income / Sale (%)': op2_margin,
        'Net Profit / Sale (%)': ni_margin,

        # EBITDA
        'Net Income': ni,
        'D & A': da,
        'Net Int Inc': net_int_val,
        'Tax Provision': tax,
        'EBITDA': ebitda,

        # Adjusted EBITDA
        'Adjustments to EBITDA': 'TBD',
        'Adj. EBITDA': 'TBD',
        'Covenant EBITDA': 'TBD',
        'Cash': row_dict.get('cashAndCashEquivalentsAtCarryingValue', 0),
        'Debt': debt,
        'OCF': ocf,
        'CapEx': capex,

        # Ratios & Outputs
        'Total Debt / Adj Ebitda': debt_ebitda,
        'Adj Ebitda / Interest Expense': icr,
        'Net Income before extraordinary': ni,
        '(NCO-CAPEX) / Total Debt (%)': fcf_debt_pct,

        # Scores
        'Score: Operating Leverage': score_op_lev,
        'Score: ICR': score_icr,
        'Score: Net Income': score_ni,
        'Score: FCF/Debt': score_fcf,
        'BQR': bqr,


    }


# --- 3. Main Processor (Rolling LTM) ---
def process_new_dataset(df_raw, num_ltm_periods=12):
    """
    df_raw: Your dataframe with specific new columns.
    num_ltm_periods: How many LTM quarters to generate backwards.
    """
    # 1. Date Sort (Oldest -> Newest conversion)
    df = df_raw.copy()
    df['fiscalDateEnding'] = pd.to_datetime(df['fiscalDateEnding'])
    # Sort DESCENDING so index 0 is the most recent date
    df = df.sort_values(by='fiscalDateEnding', ascending=False).reset_index(drop=True)

    # 2. Ensure Numeric Format
    numeric_cols = ['totalRevenue', 'ebitda', 'interestIncome', 'interestExpense',
                    'netIncome', 'operatingCashflow', 'capitalExpenditures',
                    'depreciationDepletionAndAmortization', 'shortLongTermDebtTotal',
                    'cashAndCashEquivalentsAtCarryingValue', 'incomeTaxExpense',
                    'currentNetReceivables', 'inventory', 'currentAccountsPayable', 'costOfRevenue']

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    results = []

    # 3. Rolling LTM Loop
    max_loops = min(num_ltm_periods, len(df) - 3)

    for i in range(max_loops):
        # Slice 4 quarters (current + 3 previous)
        window = df.iloc[i: i + 4]

        # Consolidate LTM Data
        ltm_vals = {
            'fiscalDateEnding': window.iloc[0]['fiscalDateEnding'].strftime('%Y-%m-%d'),

            # Flow Items (Sum them up)
            'grossProfit': window['grossProfit'].sum(),
            'totalRevenue': window['totalRevenue'].sum(),
            'costOfRevenue': window['costOfRevenue'].sum(),
            'sellingGeneralAndAdministrative': window['sellingGeneralAndAdministrative'].sum(),
            'operatingIncome': window['operatingIncome'].sum(),
            'netInterestIncome': window['netInterestIncome'].sum(),
            'incomeTaxExpense': window['incomeTaxExpense'].sum(),
            'netIncome': window['netIncome'].sum(),

            'operatingCashflow': window['operatingCashflow'].sum(),
            'capitalExpenditures': window['capitalExpenditures'].sum(),
            'depreciationDepletionAndAmortization': window['depreciationDepletionAndAmortization'].sum(),

            # Normalized Stock Items (taking average of recent four quarters)
            'currentNetReceivables': window['currentNetReceivables'].mean(),
            'inventory': window['inventory'].mean(),
            'currentAccountsPayable': window['currentAccountsPayable'].mean(),

            # Stock Items (Take Snapshot of most recent)
            'shortLongTermDebtTotal': window.iloc[0]['shortLongTermDebtTotal'],
            'cashAndCashEquivalentsAtCarryingValue': window.iloc[0]['cashAndCashEquivalentsAtCarryingValue'],
        }

        # Labeling
        if i == 0:
            label = "LTM (Current)"
        elif i % 4 == 0:
            label = f"LTM (-{i // 4} Years)"
        else:
            label = f"LTM (-{i}Q)"

        results.append(calculate_metrics_row(ltm_vals, label))

    # 4. Final Output Formatting
    final_df = pd.DataFrame(results)
    final_df.set_index('Period', inplace=True)
    return final_df.T


ticker_list = ['HELE', 'NWL', 'SPB', 'YETI', 'LCUT']
for symbol in ticker_list:
    print(f"\n Exporting Time Series for {symbol}")
    output = process_new_dataset(df_final)
    print(output.applymap(format_numbers).iloc[:,:4])
    output.reset_index().to_csv(f"{symbol}_{output.iloc[0][0]}.csv", index=False)













#
#
#
# endpoint='SHARES_OUTSTANDING'
# df = get_data(endpoint, symbol, quarter=False)
# shares = pd.DataFrame(df['quarterlyReports'])
#
#
# quarter='2026Q1'
# endpoint='EARNINGS_CALL_TRANSCRIPT'
# earn_call = get_data(endpoint, symbol, quarter)
#
# import textwrap
# # Assuming your list is stored in 'transcript_list'
# transcript_list = earn_call['transcript']
# print(f"--- Transcript ({len(transcript_list)} segments) ---\n")
#
# for line in transcript_list:
#     # Get speaker and content
#     speaker = line.get('name') or line.get('speaker') or "Speaker"
#     content = line.get('content', '')
#
#     # 1. Print the Speaker's name (bolded with asterisks if markdown is supported)
#     print(f"**{speaker}**:")
#
#     # 2. Wrap the text to 80 characters (standard reading width)
#     # This breaks long lines into multiple shorter lines
#     wrapped_text = textwrap.fill(content, width=80)
#     print(wrapped_text)
#     print("-" * 40)  # Add a separator line for readability
#     print()
#
#
#
