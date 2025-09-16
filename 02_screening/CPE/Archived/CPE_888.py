import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import MonthEnd


# List of tickers (either as a space-separated string or a list)
tickers_dict = {
    'CODI': '2025-06-01',
    'HAIN': '2025-06-01', # from 887 to 888
#    'TDG': '2022-01-01',
#    'TDS': '2023-11-01',
    'NFE': '2024-10-01',
#    'NBR': '2022-11-01',
    #    'CNSL': '2022-11-01',
#    'AGL': '2023-05-01',
#    'CRWV': '2024-10-01', #delisted, acquired
}

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
    'CODI': ['BRK-B', 'MKL', 'CNNE'],# investment company
    'HAIN': ['SMPL', 'MDLZ', 'GIS'], # snacks,
#    'TDG': ['HEI', 'PH', 'SAF'], # aerospace aftermarket + OEM
#    'TDS': ['FYBR', 'LUMN', 'CHTR'], # cable/telco/broadband, sold UScellular to T-Mobile
    'NFE': ['LNG', 'EE', 'GLNG'], # integrated LNG-to-power company
#    'NBR': ['HP', 'PTEN', 'PDS'], #a land-drilling contractor and drilling-tech company.
    'AGL': ['PRVA', 'ALHC'], #tech-enabled Medicare Advantage plan
#    'CRWV': ['AMZN', 'MSFT', 'GOOGL'], #high-density data centers packed with NVIDIA GPU
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
output.to_excel('CPE_888.xlsx')