
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import MonthEnd

with open("_consolidate.py") as f:
    code = f.read()
    exec(code)

# List of tickers (either as a space-separated string or a list)
tickers_dict = NAC

# Download historical data
data = yf.download(list(tickers_dict.keys()), start="2020-01-01")

close = data['Close'].reset_index()
close = pd.melt(close, id_vars='Date', var_name='ticker', value_name='close')
tickers = pd.DataFrame.from_dict(tickers_dict, orient='index').reset_index()
tickers.columns = ['ticker', 'start_date']
tickers['start_date2'] = pd.to_datetime(tickers['start_date']) + pd.DateOffset(months=1) + pd.Timedelta(days=7)
close = pd.merge(close, tickers, on='ticker', how='left')


rows = close['start_date2'] <= close['Date']
close2 = close[rows].copy()
close2['rn'] = close2.groupby('ticker').cumcount()

rows = close['start_date2'] >= close['Date']
close3 = close[rows].sort_values(['ticker', 'Date'], ascending=False).copy()
close3['rn'] = close3.groupby('ticker').cumcount()
close3['rn'] = - close3['rn']

close_final = pd.concat([close2, close3]).drop_duplicates()
heads = close_final.columns

#####################
tickers_dict2 = {
    'SPHR': ['SPY'],# entertainment, no direct competitors
    'EBS': ['JNJ', 'NVAX', 'DVAX'], # snacks,
    'NFE': ['LNG', 'EE', 'GLNG'], # integrated LNG-to-power company
    'GORV': ['THO', 'WGO', 'CWH'], # a network of RVs
    'MODV': ['ADUS', 'BTSG'],# focused on the “last mile” of care for government and managed‑care members
 #   'HON': ['RTX', 'JCI', 'DOW'], # conglomerate
 }

_dict = {}
for x, peer in tickers_dict2.items():
    close_final_ind = close_final[close_final['ticker']==x]
    data2 = yf.download(peer, start="2020-01-01")
    benchmark = data2['Close'].reset_index()
    close_final_ind = pd.merge(close_final_ind, benchmark, on='Date', how='left')
    close_final_ind_final = close_final_ind[heads]
    for p in peer:
        tmp = close_final_ind.copy()
        tmp['close'] = tmp[p]
        tmp['ticker'] = tmp['ticker'].transform(lambda x: f"{x}_{p}")
        tmp = tmp[heads]
        close_final_ind_final = pd.concat([close_final_ind_final, tmp])
    _dict[x] = close_final_ind_final

output = pd.concat(_dict.values())
output.to_excel('NAC.xlsx')