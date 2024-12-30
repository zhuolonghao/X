import pandas as pd
import warnings
warnings.simplefilter("ignore", category=FutureWarning)
import re

# Parameters
metrics_tv = [ #LTM: Last Twelve Month
     'Symbol',
     'Net Income > 0',                  #                               ||  Column Q
     'Cash flow from Op > 0',           #                               ||  Column S
     'CFO > Net Income',                # Earning Quality               ||  Column S - Q
     'Delta RoA > 0',  # RoA = Net.Income/Total.Asset  ||  Column AF - AG
     'Delta LT Debt / Asset < 0',       # LT.Debt/Total.Asset           ||  Column AH - AI
     'Delta C Asset / Liability > 0',   # Curr.Asset/Curr.Liability     ||  Column AJ - AK
     'Delta EBIT Margin > 0',           # EBIT/Revenue                  ||  Column AL - AM
     'Delta Rev / Asset > 0',           # Revenue/total.Asset           ||  Column AN - AO
     'Delta O/S shares < 0',            # Common Shares Outstanding     ||  Column AC - AD
     'sum'
]

metrics_tv2 = ['Symbol',
    'Performance % 1 week',
    'Performance % 1 month',
    'Performance % 3 months',
    'Performance % 6 months',
    'Performance % Year to date',
    'Performance % 1 year'
]
# Function to extract the ticker symbol
def extract_ticker(info):
    match = re.search(r'\([A-Za-z]+:([A-Z]+)\)', info)
    return match.group(1) if match else None

# File paths
folder = '2024.12.AMTM'
tv_date = '2024-12-27'
path_tv = f'C:\\Users\\longh\\Desktop\\X\\02_screening\\023_TradingView\\industry_trend_{tv_date}.csv'
path_fin = f'C:\\Users\\longh\\Desktop\\X\\02_screening\\022_Anomalies\\fundamental.xlsx'
path_sp = f'C:\\Users\\longh\\Desktop\\X\\03_decision\\_template_peer_analysis.xlsx'
path_scope = f'C:\\Users\\longh\\Desktop\\X\\03_decision\\{folder}\\01.scoping.xlsx'
output_path = f'C:\\Users\\longh\\Desktop\\X\\03_decision\\{folder}\\04.peer_analysis.xlsx'

# Load data with specified data types and columns
df_tv = pd.read_csv(path_tv)

df_scope = pd.read_excel(path_scope, sheet_name='final').dropna()

df_fin = pd.read_excel(path_fin, sheet_name='9-dim-Scores').iloc[4:]

df_sp = pd.read_excel(path_sp, skiprows=1, sheet_name='Sheet3').iloc[3:]

# Process fundamental data
tickers = df_scope.Ticker.to_list() + ['AMTM']

# Process fundamental data
df_fin['Symbol'] = df_fin['SPGTable'].apply(extract_ticker)
df_fin_filter = df_fin[df_fin['Symbol'].isin(tickers)][metrics_tv]
df_fin_filter = df_fin_filter.set_index('Symbol').astype(int)

# Process TradingView data
df_tv_filter = df_tv[df_tv['Symbol'].isin(tickers)][metrics_tv2]
df_tv_formatted = df_tv_filter.set_index('Symbol').applymap(lambda x: f"{x:.2f}%")
df_combined = pd.concat([df_fin_filter, df_tv_formatted], axis=1)

# Process Capital IQ data
df_sp['Symbol'] = df_sp['Entity Name '].apply(extract_ticker)

