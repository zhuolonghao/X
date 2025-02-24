import pandas as pd
import numpy as np
import os
folder = f'C:\\Users\\longh\\Desktop\\X\\02_screening\\2_Momentums\\data'
meta = pd.read_excel(f"{folder}\\meta_full.xlsx", sheet_name='total_market')
meta = meta.drop(np.where(meta.iloc[:,2]=='#INVALID COMPANY ID')[0])

meta['Constituents'] = meta['Constituents'].str\
    .replace(r'NasdaqGS', 'NASDAQ', regex=True)\
    .replace(r'NasdaqCM', 'NASDAQ', regex=True)\
    .replace(r'NasdaqGM', 'NASDAQ', regex=True) \
    .replace(r'NASDAQGS', 'NASDAQ', regex=True) \
    .replace(r'NASDAQCM', 'NASDAQ', regex=True) \
    .replace(r'NASDAQGM', 'NASDAQ', regex=True) \
    .replace(r'NYSEAM', 'NYSE', regex=True)
price = pd.read_csv(f"{folder}\\momentums.csv").drop('Industry', axis=1)
price['Constituents'] = price['Exchange']+ ':' + price['Symbol']

meta = meta.set_index('Constituents')
price = price.set_index('Constituents')

df = pd.merge(meta, price, how='left', left_index=True, right_index=True)
df['vol_1m / shares'] = df['Avg_wkly_vol_over_1M / Shares Out'].rank(pct=True)
df['vol_3m / shares'] = df['Avg_wkly_vol_over_3M / Shares Out'].rank(pct=True)
df['vol_1m / 1-yr avg vol'] = df['Avg_Daily_vol_over_1m / one-year avg daily_vol'].rank(pct=True)
df['vol_3m / 1-yr avg vol'] = df['Avg_Daily_vol_over_3m / one-year avg daily_vol'].rank(pct=True)
df['vol / vol_MA_10d'] = df['Relative Volume 1 day'].rank(pct=True)
df['vol / vol_MA_10w'] = df['Relative Volume 1 week'].rank(pct=True)
df['vol / vol_MA_10m'] = df['Relative Volume 1 month'].rank(pct=True)
df.to_excel(f"C:\\Users\\longh\\Desktop\\X\\02_screening\\2_Momentums\\momentums_full.xlsx")
print("Completed")
