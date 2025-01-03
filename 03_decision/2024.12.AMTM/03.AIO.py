import pandas as pd
import numpy as np
import warnings
warnings.simplefilter("ignore", category=FutureWarning)
import re

# File paths
target = 'AMTM'
folder = f'2024.12.{target}'
tv_date = '2024-12-27'
folder_screen = 'C:\\Users\\longh\\Desktop\\X\\02_screening'
folder_decision = 'C:\\Users\\longh\\Desktop\\X\\03_decision'
path_tv = f'{folder_screen}\\023_TradingView\\industry_trend_{tv_date}.csv'
path_fin = f'{folder_screen}\\022_Anomalies\\fundamental.xlsx'
path_sp = f'{folder_decision}\\03.decision.xlsx'
path_scope = f'{folder_decision}\\{folder}\\01.scoping.xlsx'
output_path = f'{folder_decision}\\{folder}\\03.AIO.xlsx'

# Parameters
metrics_tv = [
    'Performance % 1 week',
    'Performance % 1 month',
    'Performance % 3 months',
    'Performance % 6 months',
    'Performance % Year to date',
    'Performance % 1 year'
]
group_tv = ['Industry']

metrics_fin = [ #LTM: Last Twelve Month
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

metrics_sp = {
    "SIZE" : [
        'Exchange',
        'Primary Industry',
        'Market Capitalization ($M)',
        'Total Enterprise Value (CIQ) ($M)',
        'Total Enterprise Value (SNL) ($M)'],
    "Valuation": [
        'Diluted EPS Excl. Extra Items ($) FQ0',
        'Price/ EPS Before Extra (x)',
        'Diluted EPS Incl. Extra Items ($) FQ0',
        'Price/ EPS After Extra (x)',
        'Price/ Tangible Book (x)',
        'Price/ Book (x)',
        'Price/ Net FCF (x)',
        'Price/ Levered FCF (x)',
        'Price/ Last Quarter Levered FCF (x)',
        'TEV/ Revenue (x) LTM',
        'TEV/ EBITDA (x) LTM',
        'TEV/ EBITDA2 (x) LTM',
    ],
    "Growth": [
        'Month of Fiscal Year End ',
        'Revenue($M) FY0',
        'Revenue($M) FY-1',
        'Revenue($M) FY-2',
        'Revenue($M) FY-3',
        'Revenue($M) LTM',
        'Revenue($M) LTM-1',
        'Revenue($M) LTM-2',
        'Revenue($M) LTM-3',
    ],
    "Profitability": [
        'Gross Profit Margin (%) FY0',
        'Gross Profit Margin (%) LTM',
        'EBITDA Margin (%) FY0',
        'EBITDA Margin (%) LTM',
    ],
    "Ownership": [
        'Common Shares O/S(M)  FQ0',
        'Common Shares O/S(M) FQ-1',
        'Common Shares O/S(M) FQ-4',
        'Float Shares (M)',
        'Float as a Percent of Current Shares Outstanding (%)',
        'Number of Institutional Investors',
        'Shares Owned - All Institutions (M, actual)',
        'Percent Owned - All Institutions (%)',
    ],
    "Momentum": [
        "Price Change % 1W",
        "Price Change % 1M",
        "Price Change % 3M",
        "Price Change % 52W",
        "Price Change % MTD",
        "Price Change % QTD",
        "Price Change % YTD",
        "Avg wkly Vol/ Share Out (%) 1W",
        "Avg wkly Vol/ Share Out (%) 1M",
        "Avg wkly Vol/ Share Out (%) 3M",
        "Avg daily Vol/ One Year Avg Daily Vol (%) 1W",
        "Avg daily Vol/ One Year Avg Daily Vol (%) 1M",
        "Avg daily Vol/ One Year Avg Daily Vol (%) 3M",
    ],
    "Misc": ['Symbol']
}
group_sp="Primary Industry"

def extract_ticker(info):
    match = re.search(r'\([A-Za-z]+:([A-Z]+)\)', info)
    return match.group(1) if match else None

def process_grouped_data(df0, group, metrics, prefix):
    # Group by the specified columns and calculate count and mean
    df = df0.copy()
    df[metrics] = df[metrics].astype(float)
    grouped = df.groupby(group)
    cnt = grouped['Symbol'].count()
    avg = grouped[metrics].mean()
    avg_formatted = avg.applymap(lambda x: round(x, 2))

    # Calculate percentile ranks and format as percentages
    quantile = avg.rank(method="average", pct=True) * 100
    quantile.columns = [f"R_{col}" for col in quantile.columns]
    quantile_formatted = quantile.applymap(lambda x:  round(x, 0))

    # Concatenate results and set MultiIndex columns
    result = pd.concat([cnt, avg_formatted, quantile_formatted], axis=1)
    result.columns = pd.MultiIndex.from_product([[prefix], result.columns])
    return result


# Load data with specified data types and columns
df_tv = pd.read_csv(path_tv)

df_scope = pd.read_excel(path_scope, sheet_name='final').dropna()

df_fin = pd.read_excel(path_fin, sheet_name='9-dim-Scores').iloc[4:]

df_sp = pd.read_excel(path_sp,sheet_name='Sheet1', skiprows=1).iloc[3:]

# Process TradingView data
tv_total = process_grouped_data(df_tv, group_tv, metrics_tv, prefix='Total')
tv_lt_10b = process_grouped_data(df_tv[df_tv['Market capitalization'] < 10e9], group_tv, metrics_tv, prefix='LT_10B')
tv_combined = pd.concat([tv_total, tv_lt_10b], axis=1)

# Process S&P Capital IQ data for ticker
df_sp['Symbol'] = df_sp['Entity Name '].apply(extract_ticker)
df_sp.set_index(['Entity Name ', 'Entity ID '], inplace=True)
# Define column ranges and corresponding metric categories
column_ranges = {
    'SIZE': slice(0, 5),
    'Valuation': slice(5, 17),
    'Growth': slice(17, 26),
    'Profitability': slice(26, 30),
    'Ownership': slice(30, 38),
    'Momentum': slice(38, 51),
    'Misc': slice(51, 52),
}
# for industry_trend
dfs = {}  # Use a more descriptive variable name instead of _
for category, col_slice in column_ranges.items():
    if category in ('SIZE', 'Momentum', 'Misc'):
        tmp = df_sp.iloc[:, col_slice]
        tmp.columns = metrics_sp[category]
        dfs[category] = tmp
df_sp2 = pd.concat(dfs.values(), axis=1)

sp_total = process_grouped_data(
    df_sp2, group_sp, metrics_sp['Momentum'], prefix='Total')
df_sp_tmp = df_sp2[df_sp2['Market Capitalization ($M)'].astype('float') < 10e3].copy()
sp_lt_10b = process_grouped_data(
    df_sp2, group_sp, metrics_sp['Momentum'], prefix='LT_10B')
sp_combined = pd.concat([sp_total, sp_lt_10b], axis=1)


# Rename columns based on metric categories
dfs = {}  # Use a more descriptive variable name instead of _dfs
for category, col_slice in column_ranges.items():
    tmp = df_sp.iloc[:, col_slice]
    colnames = metrics_sp[category]
    if category in ('Growth'):
        tmp.iloc[:, 1:] = tmp.iloc[:, 1:]/1000
        tmp['1-Year Growth (%), FY'] = (tmp.iloc[:, 1] / tmp.iloc[:, 2].replace(0, np.nan) - 1) * 100
        tmp['3-Year CAGR Growth (%), FY'] = (tmp.iloc[:, 1] / tmp.iloc[:, 4].replace(0, np.nan) - 1) * 100
        tmp['1-Year Growth (%), LTM'] = (tmp.iloc[:, 5] / tmp.iloc[:, 6].replace(0, np.nan) - 1) * 100
        tmp['3-Year CAGR Growth (%), LTM'] = (tmp.iloc[:, 5] / tmp.iloc[:, 8].replace(0, np.nan) -1)*100
        colnames = metrics_sp[category] \
                   + ['1-Year Growth (%), FY', '3-Year CAGR Growth (%), FY', '1-Year Growth (%), LTM', '3-Year CAGR Growth (%), LTM']
    if category in ('Ownership'):
        tmp.iloc[:, :4] = tmp.iloc[:, :4]/1e6
        tmp.iloc[:, 6] = tmp.iloc[:, 6]/1e6
    tmp.columns = pd.MultiIndex.from_product([[category], colnames])
    dfs[category] = tmp
df_sp2 = pd.concat(dfs.values(), axis=1)

# Process data at Ticker Level
tickers = df_scope.Ticker.to_list() + [target]

df_sp2_filter = df_sp2[df_sp2.iloc[:, 55].isin(tickers)]

df_tv_filter = df_tv[df_tv['Symbol'].isin(tickers)].set_index('Symbol')[metrics_tv]

df_fin['Symbol'] = df_fin['SPGTable'].apply(extract_ticker)
df_fin_filter = df_fin[df_fin['Symbol'].isin(tickers)][metrics_fin].set_index('Symbol')

df_combined = pd.concat([df_tv_filter, df_fin_filter], axis=1)

# Write results to Excel
with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    sp_combined.to_excel(writer, sheet_name='from.tv')
    tv_combined.to_excel(writer, sheet_name='from.sp')
    df_combined.to_excel(writer, sheet_name='ticker.screening')
    df_sp2_filter.T.to_excel(writer, sheet_name='ticker.vertical')
    df_sp2_filter.to_excel(writer, sheet_name='ticker.horizontal')


