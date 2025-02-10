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
meta['ticker'] = meta['Constituents'].str\
    .replace(r'NasdaqGS', 'NASDAQ', regex=True)\
    .replace(r'NasdaqCM', 'NASDAQ', regex=True)\
    .replace(r'NasdaqGM', 'NASDAQ', regex=True)\
    .replace(r'NYSEAM', 'NYSE', regex=True)
price = pd.read_csv(f"{folder}/momentums.csv")
price['ticker'] = price['Exchange']+ ':' + price['Symbol']

meta = meta.set_index('ticker')
price = price.set_index('ticker')

df = pd.merge(meta, price, how='left', left_index=True, right_index=True)