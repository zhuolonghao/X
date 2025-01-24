#https://github.com/fja05680/sp500/blob/master/sp500.ipynb

run_date = '2025-01-01'
from datetime import datetime
import io
import re
import os
import pandas as pd
import wikipedia as wp

pd.options.mode.chained_assignment = None  # default='warn'
pd.set_option('display.max_rows', 600)

def remove_brackets(text):
    return re.sub(r'\[.*?\]', '', text)

# Pull SP500
# wp.search('xxxx')
title = 'List of S&P 500 companies'
html = wp.page(title, auto_suggest=False).html()
# Convert the HTML content to a file-like object
html_io = io.StringIO(html)
# Extract tables from the HTML content
tables = pd.read_html(html_io)
# assign tables
current = tables[0]
current.columns = [x.lower() for x in current.columns]
changes500 = tables[1]
changes500.columns = ['date', 'added', 'added_nm', 'removed', 'removed_nm', 'reason']
changes = changes500.copy().fillna('---')
changes['date'] = changes['date'].apply(lambda x:     # force date to the Monday of the same week
                                              pd.to_datetime(x)+pd.offsets.Week(n=0, weekday=6)-pd.DateOffset(6))

base = current[['symbol', 'security', 'gics sector', 'gics sub-industry']]
base.columns = ['symbol', 'company', 'gics sector', 'gics sub-industry']
base['date'] = pd.to_datetime(run_date)+pd.offsets.Week(n=0, weekday=6)-pd.DateOffset(6)
dates_change = changes['date'].unique()
current = base.copy()
output = base.copy()
for dt in dates_change:
    tmp = changes[changes['date'].eq(dt)]
    base2 = current.copy()
    base2['date'] = dt
    for row in range(tmp.shape[0]):
        if tmp.iloc[row,3] != '---':
            added_back = [tmp.iloc[row, 3], tmp.iloc[row, 4], None, None, dt]
            base2 = pd.concat([base2, pd.DataFrame([added_back], columns=base2.columns)], ignore_index=True)
        if tmp.iloc[row, 1] != '---':
            base2 = base2[(base2['symbol'] != tmp.iloc[row, 1])]
    current = base2.copy()
    output = pd.concat([output, base2], ignore_index=True)
output500 = output.copy()


output500['year'] = output500['date'].apply(lambda x: f"CY{x.year}")
output500 = output500.sort_values(['date', 'symbol'])
df = output500.groupby(['year','date'], as_index=False)['symbol'].count()
df = df.groupby('year').tail(1)
df.columns = ['year', 'date', 'cnt']
df2 = pd.merge(df, output500, on=['year','date'], how='inner')
metrics = ['year', 'date', 'cnt', 'company', 'gics sector', 'gics sub-industry', 'symbol']


# Write results to Excel
output_path = '04_monitoring\JPAM_2025\sp500_earning_source.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df2[metrics].to_excel(writer, sheet_name='raw', index=False)
