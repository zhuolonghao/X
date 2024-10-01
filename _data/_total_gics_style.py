import os, re, time, shutil
import datetime
import webbrowser as web
import pandas as pd
import numpy as np
import os

date = '202408'

_etf = {
    'sector':    	 ['VTI', 'https://institutional.vanguard.com/investments/product-details/fund/0970'],
    'mega_growth': 	 ['MGK', 'https://institutional.vanguard.com/investments/product-details/fund/3138'],
    'mega_value':  	 ['MGV', 'https://institutional.vanguard.com/investments/product-details/fund/3139'],
    'large_growth':  ['VUG', 'https://institutional.vanguard.com/investments/product-details/fund/0967'],
    'large_value': 	 ['VTV', 'https://institutional.vanguard.com/investments/product-details/fund/0966'],
    'mid_growth': 	 ['VOT', 'https://institutional.vanguard.com/investments/product-details/fund/0932'],
    'mid_value': 	 ['VOE', 'https://institutional.vanguard.com/investments/product-details/fund/0935'],
    'small_growth':  ['VBK', 'https://institutional.vanguard.com/investments/product-details/fund/0938'],
    'small_value': 	 ['VBR', 'https://institutional.vanguard.com/investments/product-details/fund/0937'],
    'sp500': 		 ['VOO', 'https://institutional.vanguard.com/investments/product-details/fund/0968'],
    'sp400': 		 ['IVOO',  'https://institutional.vanguard.com/investments/product-details/fund/3342'],
}

###########################################################################################################
# GICS_8/Style/Size
###########################################################################################################

writer = pd.ExcelWriter(rf".\_data\{date}.xlsx")
for key, values in _etf.items():
    ticker, link = values
    web.open(link)
    input("Checkpoint: Download ETF holdings manually. Press Enter once done")
    try:
        path = r"C:\Users\longh\Downloads\ProductDetailsHoldings_.csv"
        raw = pd.read_csv(path, skiprows=4, usecols=list(range(1, 10)), header=None)
        last_row = np.where(raw.iloc[:, 0].isna())[0][0]
        df = pd.DataFrame(raw.values[1:last_row], columns=raw.iloc[0]).drop_duplicates()
        df.to_excel(writer, sheet_name=f"{key}", index=False)
    except Exception as e:
        print(e)
    print(f"---{ticker}_{key}: {df.shape}")
    os.remove(path)
writer.close()


###########################################################################################################
# create metadata
###########################################################################################################

_total = {}
reader = pd.ExcelFile(rf".\_data\{date}.xlsx")
for nm in reader.sheet_names:
    df = reader.parse(nm)
    df.columns = [x.lower() for x in df.columns]
    cols = ['sedol', 'ticker', 'holdings name', '% of fund*', 'market', 'sector']
    rows = df['ticker'].str.contains('-')
    df = df[~rows][cols]
    if nm != 'sector':
        df = df[['sedol', '% of fund*']].rename(columns={'% of fund*': nm})
    _total[nm] = df.set_index('sedol')
total = pd.concat(_total.values(), axis=1).dropna(subset='ticker')
total.to_excel("./_data/_total_gics_style.xlsx")
