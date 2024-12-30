import pandas as pd
import warnings
warnings.simplefilter("ignore", category=FutureWarning)

# Define reusable function for processing grouped data
def process_grouped_data(df, group, metrics, prefix):
    # Group by the specified columns and calculate count and mean
    grouped = df.groupby(group)
    cnt = grouped['Symbol'].count()
    avg = grouped[metrics].mean()
    avg_formatted = avg.applymap(lambda x: round(x,2))
    
    # Calculate percentile ranks and format as percentages
    quantile = avg.rank(method="average", pct=True) * 100
    quantile.columns = [f"Q___{col}" for col in quantile.columns]
    quantile_formatted = quantile.applymap(lambda x: f"{x:.0f}%")
    
    # Concatenate results and set MultiIndex columns
    result = pd.concat([cnt, avg_formatted, quantile_formatted], axis=1)
    result.columns = pd.MultiIndex.from_product([[prefix], result.columns])
    return result

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

metrics_sp = ['1W', '1M', '3M', '52W']
group_sp = ['Unnamed: 7']

# File paths
folder = '2024.12.AMTM'
tv_date = '2024-12-27'
path_tv = f'C:\\Users\\longh\\Desktop\\X\\02_screening\\023_TradingView\\industry_trend_{tv_date}.csv'
path_sp = f'C:\\Users\\longh\\Desktop\\X\\03_decision\\_template_peer_analysis.xlsx'
path_scope = f'C:\\Users\\longh\\Desktop\\X\\03_decision\\{folder}\\01.scoping.xlsx'
output_path = f'C:\\Users\\longh\\Desktop\\X\\03_decision\\{folder}\\03.equity_industry_trend.xlsx'

# Load data with specified data types and columns
df_tv = pd.read_csv(path_tv)

df_sp = pd.read_excel(path_sp, skiprows=4, sheet_name='Sheet3')
df_sp.rename(columns={'Unnamed: 0': 'Symbol'}, inplace=True)

df_scope = pd.read_excel(path_scope, sheet_name='final')

# Process TradingView data
tv_total = process_grouped_data(df_tv, group_tv, metrics_tv, prefix='Total')
tv_lt_10b = process_grouped_data(df_tv[df_tv['Market capitalization'] < 10e9], group_tv, metrics_tv, prefix='LT_10B')
tv_combined = pd.concat([tv_total, tv_lt_10b], axis=1)

# Process S&P Capital IQ data
sp_total = process_grouped_data(df_sp, group_sp, metrics_sp, prefix='Total')
sp_lt_10b = process_grouped_data(df_sp[df_sp['Unnamed: 3'] < 10e3], group_sp, metrics_sp, prefix='LT_10B')
sp_combined = pd.concat([sp_total, sp_lt_10b], axis=1)

# Process targeted peer group
scope = pd.read_excel(path_scope, sheet_name='final')
scope_expand = df_tv[df_tv['Symbol']\
    .isin(scope.Ticker.dropna().tolist())]\
    .set_index(['Symbol', 'Market capitalization'])[metrics_tv]
scope_formatted = scope_expand.applymap(lambda x: round(x,2))

# Write results to Excel
with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    tv_combined.to_excel(writer, sheet_name='from.tv')
    sp_combined.to_excel(writer, sheet_name='from.sp')
    scope_formatted.to_excel(writer, sheet_name='targeted')
