import pandas as pd
import numpy as np

folder = '02_screening/023_Momentums/data'
meta_sp500 = pd.read_excel(f"{folder}/meta.xlsx", sheet_name='sp500')
meta_sp500 = meta_sp500.drop(np.where(meta_sp500.iloc[:,1]=='#INVALID COMPANY ID')[0])
meta_sp400 = pd.read_excel(f"{folder}/meta.xlsx", sheet_name='sp400')
meta_sp400 = meta_sp400.drop(np.where(meta_sp400.iloc[:,1]=='#INVALID COMPANY ID')[0])
meta_sp600 = pd.read_excel(f"{folder}/meta.xlsx", sheet_name='sp600')
meta_sp600 = meta_sp600.drop(np.where(meta_sp600.iloc[:,1]=='#INVALID COMPANY ID')[0])

meta = pd.concat([meta_sp500,meta_sp400, meta_sp600], ignore_index=True)
meta['Constituents'] = meta['Constituents'].str\
    .replace(r'NasdaqGS', 'NASDAQ', regex=True)\
    .replace(r'NasdaqCM', 'NASDAQ', regex=True)\
    .replace(r'NasdaqGM', 'NASDAQ', regex=True)\
    .replace(r'NYSEAM', 'NYSE', regex=True)
price = pd.read_csv(f"{folder}/momentums.csv").drop('Industry', axis=1)
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
df.to_excel(f"02_screening/023_Momentums/momentums.xlsx")