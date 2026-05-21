import pandas as pd
import requests
import time
import os
import ast
from datetime import datetime, timedelta
from pandas.tseries.offsets import MonthEnd

class FMPClient:
    """
    Handles API connections, data retrieval, and rate limiting.
    """

    def __init__(self):
        self.api_key = os.getenv('FMP_API_KEY')
        self.base_url = "https://financialmodelingprep.com/stable"

    def get_data(self, endpoint, symbol):
        """
        Fetches data with built-in error handling.
        """
        # Calculate date range for past 6 months
        to_date = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y-%m-%d')
        from_date_1y = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        if endpoint in ('revenue-product-segmentation', 'revenue-geographic-segmentation'):
            url = f"{self.base_url}/{endpoint}?symbol={symbol}&apikey={self.api_key}"
        elif endpoint in ('historical-price-eod'):
            url = f"{self.base_url}/{endpoint}/full?symbol={symbol}&apikey={self.api_key}"
        elif endpoint in ('news'):
            url = f"{self.base_url}/{endpoint}/stock?symbols={symbol}&from={from_date_1y}&to={to_date}&page=0&limit=100&apikey={self.api_key}"
        elif endpoint in ('sec-filings-search'):
            url = f"{self.base_url}/{endpoint}/symbol?symbol={symbol}&from={from_date}&to={to_date}&page=0&limit=300&apikey={self.api_key}"
        elif endpoint in ('sec-filings-8k'):
            url = f"{self.base_url}/{endpoint}?&from={yesterday}&to={to_date}&page=0&limit=1000&apikey={self.api_key}"
            print(f"{url}")
        else:
            url = f"{self.base_url}/{endpoint}?symbol={symbol}&period=quarter&limit=20&apikey={self.api_key}"
        try:
            print(f"   Fetching {endpoint} for {symbol}...")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Error handling for FMP format
            if isinstance(data, dict) and "Error Message" in data:
                return []
            # Return the RAW LIST (do not convert to DF here)
            return data if isinstance(data, list) else []

        except Exception as e:
            print(f"   Error: {e}")
            return []

class FinancialAnalyzer:
    """
    Handles data processing, formatting, metric calculation, and scoring.
    """

    def __init__(self):
        # Define columns to extract from each statement
        self.id_vars = ['fiscalDateEnding', 'symbol']
        self.inc_vars = ['filingDate', 'fiscalYear', 'period',
                         'grossProfit', 'revenue', 'costOfRevenue',
                         'operatingIncome', 'operatingExpenses', 'sellingGeneralAndAdministrativeExpenses',
                         'netIncome', 'netInterestIncome', 'incomeTaxExpense', 'ebit', 'ebitda',
                         'weightedAverageShsOut', 'weightedAverageShsOutDil']
        self.bs_vars = ['netReceivables', 'inventory',  'accountPayables',
                        'cashAndCashEquivalents', 'totalDebt', 'totalStockholdersEquity']
        self.cf_vars = ['operatingCashFlow', 'investmentsInPropertyPlantAndEquipment', 'freeCashFlow',
                        'stockBasedCompensation', 'depreciationAndAmortization',
                        'netCommonStockIssuance', 'netDebtIssuance']
        self.ev_vars = ['stockPrice', 'numberOfShares', 'marketCapitalization', 'enterpriseValue']
        self.segment_vars = self.id_vars + ['Segment-1 Name', 'Segment-1 %', 'Segment-2 Name', 'Segment-2 %',
                             'Segment-3 Name', 'Segment-3 %', 'Others Name', 'Others %']
        self.METRIC_GROUPS  = {
                    'Fiscal Period': 'Header', 'Statement Date': 'Header', 'Filing Date': 'Header',
                    'Segment-1': 'Revenue & Margin', 'Segment-1 %': 'Revenue & Margin',
                    'Segment-2': 'Revenue & Margin', 'Segment-2 %': 'Revenue & Margin',
                    'Segment-3': 'Revenue & Margin', 'Segment-3 %': 'Revenue & Margin',
                    'Others': 'Revenue & Margin', 'Others %': 'Revenue & Margin',
                    
                    'Revenue Total ($k)': 'Revenue & Margin', 
                    'Rev-CoGS / Rev': 'Revenue & Margin',
                    'Rev-CoGS-SG&A / Rev': 'Revenue & Margin', 
                    'Rev-CoGs-SG&A-Other.OpEx / Rev': 'Revenue & Margin',
                    'Net Income / Rev': 'Revenue & Margin',

                    'Net Income ($k)': 'EBITDA', 'D & A ($k)': 'EBITDA', 'Net Interest Expense ($k)': 'EBITDA',
                    'Tax Provision ($k)': 'EBITDA', 'EBITDA ($k)': 'EBITDA', 'Stock-Based Comp ($k)': 'EBITDA',
                    'Others Adj.': 'EBITDA', 'Adj. EBITDA': 'EBITDA', 'Covenant EBITDA': 'EBITDA',

                    'Stock Price': 'Capital Structure', 'O/S Shares': 'Capital Structure',
                    'Market Capitalization ($k)': 'Capital Structure', 'Cash ($k)': 'Capital Structure',
                    'Debt ($k)': 'Capital Structure', 'Enterprise Value ($k)': 'Capital Structure',
                    'netCommonStockIssuance ($k)': 'Capital Structure', 'netDebtIssuance ($k)': 'Capital Structure',
                    
                    'DSO': 'Liquidity & Cash Flow', 'DIO': 'Liquidity & Cash Flow',
                    'DPO': 'Liquidity & Cash Flow', 'CCC': 'Liquidity & Cash Flow',
                    'OCF ($k)': 'Liquidity & Cash Flow', 'CapEx ($k)': 'Liquidity & Cash Flow', 'FCF ($k)': 'Liquidity & Cash Flow',
                    
                    'Total Debt / Equity': 'BQR-Mid-Mkt',
                    'Total Debt / Adj Ebitda': 'BQR', 'Adj Ebitda / Interest Expense': 'BQR',
                    'Net Income before extraordinary ($k)': 'BQR', '(NCO-CAPEX) / Total Debt': 'BQR',
                    'Score: Operating Leverage': 'BQR', 'Score: ICR': 'BQR',
                    'Score: Net Income': 'BQR', 'Score: FCF/Debt': 'BQR', 'BQR': 'BQR'
                    }

    @staticmethod
    def safe_div(n, d, default=0):
        """Prevents ZeroDivisionError by checking the denominator."""
        return n / d if d and d != 0 else default


    def process_segments(self, row):
        def safe_float(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0  # Or whatever default makes sense

        raw_data = row['data']

        # --- Step A: Robust Type Handling ---
        # Check if the data is already a dict, a string, or null
        if isinstance(raw_data, dict):
            d = raw_data
        elif isinstance(raw_data, str) and raw_data.strip():
            try:
                d = ast.literal_eval(raw_data)
            except (ValueError, SyntaxError):
                return pd.Series()
        else:
            # Handles None, NaN, or empty strings
            return pd.Series()

        # --- Step B: Calculation Logic ---
        total_rev = sum(value for k, value in d.items() if isinstance(value, (int, float)))
        # Sort segments by revenue
        sorted_segs = sorted(d.items(), key=lambda x: safe_float(x[1]), reverse=True)
        # Initialize record with base columns
        res = {
            'symbol': row['symbol'],
            'fiscalYear': row['fiscalYear'],
            'fiscalDateEnding': pd.to_datetime(row['date']).to_period('M').strftime("%Y-%m-%d"),
            'Total_Revenue': total_rev  # Formatted with commas for readability
        }

        # --- Step C: Extract Top 3 ---
        top_3 = sorted_segs[:3]
        for i in range(1, 4):
            if i <= len(top_3):
                name, val = top_3[i - 1]
                res[f'Segment-{i} Name'] = name
                res[f'Segment-{i} %'] = f"{self.safe_div(val, total_rev)*100:.1f}%" if total_rev != 0 else "-"
            else:
                res[f'Segment-{i} Name'] = '-'
                res[f'Segment-{i} %'] = "-"

        # --- Step D: Create Catch-all for 4th onwards ---
        others = sorted_segs[3:]
        if others:
            other_rev = sum(v for k, v in others if isinstance(v, (int, float)))
            other_names = ", ".join([k for k, v in others])
            res['Others Name'] = other_names
            res['Others %'] = f"{self.safe_div(other_rev, total_rev)*100:.1f}%" if total_rev != 0 else "-"  
        else:
            res['Others Name'] = '-'
            res['Others %'] = "-"

        return pd.Series(res)

    def _format_statement(self, raw_data, vars_to_keep):
        """Helper to convert raw JSON list to formatted DataFrame"""
        # Fix: Proper check for an empty list
        if not raw_data or len(raw_data) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)

        # FMP returns 'date', rename it to match your id_vars list
        if 'date' in df.columns:
            df = df.rename(columns={'date': 'fiscalDateEnding'})
        # Filter id_vars to only those that exist in the dataframe
        current_id_vars = [v for v in self.id_vars if v in df.columns]
        # Convert to numeric and set index
        df['fiscalDateEnding'] = pd.to_datetime(df['fiscalDateEnding'])\
            .dt.to_period('M').dt.strftime("%Y-%m-%d")
        df = df.sort_values('fiscalDateEnding', ascending=True)
        df = df.set_index(current_id_vars)
        # Ensure all numeric columns stay numeric, but preserve filing and period values.
        non_numeric_columns = {'filingDate', 'period'}
        numeric_columns = [c for c in df.columns if c not in non_numeric_columns]
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        available_vars = [v for v in vars_to_keep if v in df.columns]
        return df[available_vars]

    def build_merged_dataframe(self, inc_data, bs_data, cf_data, ev_data, segment_data):
        """Joins Income, Balance Sheet, and Cash Flow into one chronological DataFrame"""
        inc_df = self._format_statement(inc_data, self.inc_vars)
        bs_df = self._format_statement(bs_data, self.bs_vars)
        cf_df = self._format_statement(cf_data, self.cf_vars)
        ev_df = self._format_statement(ev_data, self.ev_vars)

        # GUARD RAIL: Only fail if core financial data is missing
        if inc_df.empty or cf_df.empty or bs_df.empty or ev_df.empty:
            return pd.DataFrame()
        # Join the core financial data
        merged_df = inc_df.join(cf_df, how='outer') \
            .join(bs_df, how='outer') \
            .join(ev_df, how='outer')
        # OPTIONAL JOIN: Join segments if they exist, otherwise fill with '-'
        if not segment_data.empty:
            # Filter segment_vars to only those that actually exist in segment_data
            existing_vars = [v for v in self.segment_vars if v in segment_data.columns]
            seg_df = segment_data[existing_vars].set_index(self.id_vars)
            merged_df = merged_df.join(seg_df, how='left')
        # ENSURE COLUMNS EXIST: Even if segment data was missing,
        # we must ensure the columns exist so process_ltm_data doesn't crash
        for col in ['Segment-1 Name', 'Segment-1 %', 'Segment-2 Name', 'Segment-2 %',
                    'Segment-3 Name', 'Segment-3 %', 'Others Name', 'Others %']:
            if col not in merged_df.columns:
                merged_df[col] = "-"

        return merged_df.reset_index()

    # --- Scoring & Helper Methods (Static) ---
    @staticmethod
    def map_to_op_lev(v):
        if v is None or pd.isna(v) or v == 999: return 75
        thresholds = [(0.5, 15), (1.0, 25), (1.75, 35), (2.5, 42), (3.25, 45),
                      (3.75, 48), (4.25, 52), (4.75, 55), (5.25, 58), (6.25, 65)]
        for limit, score in thresholds:
            if v < limit: return score
        return 75

    @staticmethod
    def map_to_icr(v):
        if v is None or pd.isna(v) or v == 999: return 15
        thresholds = [(30, 15), (15, 25), (12, 35), (9.75, 42), (7.75, 45),
                      (5, 48), (4.5, 52), (4, 55), (2.5, 58), (1.5, 65)]
        for limit, score in thresholds:
            if v > limit: return score
        return 75

    @staticmethod
    def map_to_ni(v):
        if v is None or pd.isna(v): return 75
        # v expected in Thousands
        thresholds = [(4000, 15), (1000, 25), (200, 35), (75, 42), (50, 45),
                      (25, 48), (15, 52), (5, 55), (0, 58), (-20, 65)]
        for limit, score in thresholds:
            if v > limit: return score
        return 75

    @staticmethod
    def map_to_fcf(v):
        if v is None or pd.isna(v) or v == 999: return 15
        thresholds = [(50, 15), (40, 25), (30, 35), (23, 42), (20, 45),
                      (17, 48), (15, 52), (12, 55), (7, 58), (5.5, 65)]
        for limit, score in thresholds:
            if v > limit: return score
        return 75

    @staticmethod
    def format_numbers(value):
        if pd.isna(value) or value == "N/A" or value == 999 or value == -999: return "N/A"
        if isinstance(value, str): return value
        if abs(value) >= 1e9: return f"{value / 1e9:.2f}B"
        if abs(value) >= 1e6: return f"{value / 1e6:.2f}M"
        if abs(value) >= 1e3: return f"{value / 1e3:.2f}K"
        return f"{value:.2f}"

    def calculate_metrics_row(self, row_dict, label):
        """Calculates financial ratios and scores for a single period"""
        # Safe extraction
        rev = row_dict.get('revenue', 0)
        cogs = row_dict.get('costOfRevenue', 0)
        sga = row_dict.get('sellingGeneralAndAdministrativeExpenses', 0)
        gp = row_dict.get('grossProfit', 0)
        rev_cogs_sga = rev - cogs - sga
        oi = row_dict.get('operatingIncome', 0)
        ni = row_dict.get('netIncome', 0)

        # Working Capital
        dso = 365 * self.safe_div(row_dict.get('netReceivables', 0), rev)
        dio = 365 * self.safe_div(row_dict.get('inventory', 0), cogs)
        dpo = 365 * self.safe_div(row_dict.get('accountPayables', 0), cogs)

        # EBITDA/Flows
        net_int_val = row_dict.get('netInterestIncome', 0)
        da = row_dict.get('depreciationAndAmortization', 0)
        tax = row_dict.get('incomeTaxExpense', 0)
        ebitda = ni + tax - net_int_val + da
        sbc = row_dict.get('stockBasedCompensation',0)

        ocf = row_dict.get('operatingCashFlow', 0)
        capex = row_dict.get('investmentsInPropertyPlantAndEquipment', 0)
        fcf_val = row_dict.get('freeCashFlow', 0)
        debt = row_dict.get('totalDebt', 0)
        equity = row_dict.get('totalStockholdersEquity', 0)

        # Ratios
        debt_equity = debt / equity if equity > 0 else 999
        debt_ebitda = debt / ebitda if ebitda > 0 else 999
        icr = ebitda / abs(net_int_val) if net_int_val < 0 and ebitda > 0 else -999
        fcf_debt_pct = fcf_val / debt if debt > 0 else 999

        # Scores
        score_op_lev = self.map_to_op_lev(debt_ebitda)
        score_icr = self.map_to_icr(icr)
        score_ni = self.map_to_ni(ni / 1e6)
        score_fcf = self.map_to_fcf(100 * fcf_debt_pct)
        bqr = (score_op_lev * 0.35 + score_icr * 0.15 + score_ni * 0.25 + score_fcf * 0.25)

        return {
            'Period': label,
            'Fiscal Period': f"{int(row_dict.get('fiscalYear', 0))}-{row_dict.get('period')}",
            'Statement Date': row_dict.get('fiscalDateEnding'),
            'Filing Date': row_dict.get('filingDate'),

            'Segment-1': row_dict.get('Segment-1 Name') or '-',
            'Segment-1 %': row_dict.get('Segment-1 %') or '-',
            'Segment-2': row_dict.get('Segment-2 Name') or '-',
            'Segment-2 %': row_dict.get('Segment-2 %') or '-',
            'Segment-3': row_dict.get('Segment-3 Name') or '-',
            'Segment-3 %': row_dict.get('Segment-3 %') or '-',
            'Others': row_dict.get('Others Name') or '-',
            'Others %': row_dict.get('Others %') or '-',
            'Revenue Total ($k)': f"{rev/1e3:,.0f}",
            'Rev-CoGS / Rev': f"{100 * self.safe_div(gp, rev):.2f}%",
            'Rev-CoGS-SG&A / Rev': f"{100 * self.safe_div(rev - cogs - sga, rev):.2f}%",
            'Rev-CoGs-SG&A-Other.OpEx / Rev': f"{100 * self.safe_div(oi, rev):.2f}%",
            'Net Income / Rev': f"{100 * self.safe_div(ni, rev):.2f}%",

            'Net Income ($k)': f"{ni/1e3:,.0f}", 
            'D & A ($k)': f"{da/1e3:,.0f}", 
            'Net Interest Expense ($k)': f"{-net_int_val/1e3:,.0f}",
            'Tax Provision ($k)': f"{tax/1e3:,.0f}", 
            'EBITDA ($k)': f"{ebitda/1e3:,.0f}", 
            'Stock-Based Comp ($k)': f"{sbc/1e3:,.0f}"   ,
            'Others Adj.': 'TBD', 
            'Adj. EBITDA': 'TBD', 
            'Covenant EBITDA': 'TBD',

            'Stock Price': f"{row_dict.get('stockPrice', 0):,.2f}",
            'O/S Shares': f"{row_dict.get('numberOfShares', 0):,.0f}",
            'Market Capitalization ($k)': f"{row_dict.get('marketCapitalization', 0)/1e3:,.0f}",
            'Cash ($k)': f"{row_dict.get('cashAndCashEquivalents', 0)/1e3:,.0f}",
            'Debt ($k)': f"{debt/1e3:,.0f}",
            'Enterprise Value ($k)':  f"{row_dict.get('enterpriseValue', 0)/1e3:,.0f}",
            'netCommonStockIssuance ($k)': f"{row_dict.get('netCommonStockIssuance', 0)/1e3:,.0f}",
            'netDebtIssuance ($k)': f"{row_dict.get('netDebtIssuance', 0)/1e3:,.0f}",
            # liquidity & Cash flow
            'DSO': f"{dso:.1f}", 'DIO': f"{dio:.1f}", 'DPO': f"{dpo:.1f}", 
            'CCC': f"{dso + dio - dpo:.1f}",
            
            'OCF ($k)': f"{ocf/1e3:,.0f}", 
            'CapEx ($k)': f"{capex/1e3:,.0f}", 
            'FCF ($k)': f"{fcf_val/1e3:,.0f}",

            'Total Debt / Equity': f"{debt_equity:.1f}x",
            'Total Debt / Adj Ebitda': f"{debt_ebitda:.1f}x", 
            'Adj Ebitda / Interest Expense': f"{icr:.1f}x",
            'Net Income before extraordinary ($k)': f"{ni/1e3:,.0f}", 
            '(NCO-CAPEX) / Total Debt': f"{100*fcf_debt_pct:.2f}%",
            'Score: Operating Leverage': score_op_lev, 
            'Score: ICR': score_icr,
            'Score: Net Income': score_ni, 
            'Score: FCF/Debt': score_fcf, 
            'BQR': f"{bqr:.1f}"
        }

    def process_ltm_data(self, df_raw, num_ltm_periods=50):
        """Generates Rolling LTM data from the merged dataframe"""
        if df_raw.empty: return pd.DataFrame()

        df = df_raw.copy()
        df['fiscalDateEnding'] = pd.to_datetime(df['fiscalDateEnding'])
        df = df.sort_values(by='fiscalDateEnding', ascending=False).reset_index(drop=True)

        # Ensure Fillna for calculations
        df = df.fillna(0)

        results = []
        max_loops = min(num_ltm_periods, len(df) - 3)

        for i in range(max_loops):
            window = df.iloc[i: i + 4]

            # Aggregate LTM values
            ltm_vals = {
                'fiscalDateEnding': window.iloc[0]['fiscalDateEnding'].strftime('%Y-%m-%d'),
                'filingDate': window.iloc[0]['filingDate'],
                'fiscalYear': window.iloc[0]['fiscalYear'],
                'period': window.iloc[0]['period'],
                # Flows (Sum)
                'grossProfit': window['grossProfit'].sum(),
                'revenue': window['revenue'].sum(),
                'costOfRevenue': window['costOfRevenue'].sum(),
                'sellingGeneralAndAdministrativeExpenses': window['sellingGeneralAndAdministrativeExpenses'].sum(),
                'operatingIncome': window['operatingIncome'].sum(),
                'netInterestIncome': window['netInterestIncome'].sum(),
                'incomeTaxExpense': window['incomeTaxExpense'].sum(),
                'netIncome': window['netIncome'].sum(),
                'operatingCashFlow': window['operatingCashFlow'].sum(),
                'investmentsInPropertyPlantAndEquipment': window['investmentsInPropertyPlantAndEquipment'].sum(),
                'freeCashFlow': window['freeCashFlow'].sum(),
                'depreciationAndAmortization': window['depreciationAndAmortization'].sum(),
                'stockBasedCompensation': window['stockBasedCompensation'].sum(),
                # Stock / Avg Items
                'netReceivables': window['netReceivables'].mean(),
                'inventory': window['inventory'].mean(),
                'accountPayables': window['accountPayables'].mean(),
                # Snapshots
                'totalDebt': window.iloc[0]['totalDebt'],
                'totalStockholdersEquity': window.iloc[0]['totalStockholdersEquity'],
                'cashAndCashEquivalents': window.iloc[0]['cashAndCashEquivalents'],
                'netCommonStockIssuance': window.iloc[0]['netCommonStockIssuance'],
                'netDebtIssuance': window.iloc[0]['netDebtIssuance'],
                'Segment-1 Name': window.iloc[0]['Segment-1 Name'],
                'Segment-1 %': window.iloc[0]['Segment-1 %'],
                'Segment-2 Name': window.iloc[0]['Segment-2 Name'],
                'Segment-2 %': window.iloc[0]['Segment-2 %'],
                'Segment-3 Name': window.iloc[0]['Segment-3 Name'],
                'Segment-3 %': window.iloc[0]['Segment-3 %'],
                'Others Name': window.iloc[0]['Others Name'],
                'Others %': window.iloc[0]['Others %'],
                'stockPrice': window.iloc[0]['stockPrice'],
                'numberOfShares': window.iloc[0]['numberOfShares'],
                'marketCapitalization': window.iloc[0]['marketCapitalization'],
                'enterpriseValue': window.iloc[0]['enterpriseValue'],
            }

            if i == 0:
                label = "LTM (Current)"
            elif i % 4 == 0:
                label = f"LTM (-{i // 4} Years)"
            else:
                label = f"LTM (-{i}Q)"

            results.append(self.calculate_metrics_row(ltm_vals, label))

        final_df = pd.DataFrame(results)
        if not final_df.empty:
            final_df.set_index('Period', inplace=True)
            return final_df.T
        return pd.DataFrame()

    def add_category(self, final_df):
        # ... (all your existing loop logic remains the same) ...

        if not final_df.empty:
            row_categories = [self.METRIC_GROUPS.get(metric, 'Other') for metric in final_df.index]

            # 3. Build the MultiIndex (Level 0 = Category, Level 1 = Metric Name)
            final_df.index = pd.MultiIndex.from_arrays(
                [row_categories, final_df.index],
                names=['Category', 'Metric']
            )

            return final_df
        return pd.DataFrame()
