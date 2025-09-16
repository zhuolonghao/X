import numpy as np
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import MonthEnd


with open("_consolidate.py") as f:
    code = f.read()
    exec(code)

# List of tickers (either as a space-separated string or a list)
tickers_dict = CPE887

# Download historical data
data = yf.download(list(tickers_dict.keys()), start="2020-01-01")

close = data['Close'].reset_index()
close = pd.melt(close, id_vars='Date', var_name='ticker', value_name='close')
tickers = pd.DataFrame.from_dict(tickers_dict, orient='index').reset_index()
tickers.columns = ['ticker', 'start_date']
#tickers['start_date2'] = pd.to_datetime(tickers['start_date']) + pd.DateOffset(months=1) + pd.Timedelta(days=7)
tickers['start_date2'] = pd.to_datetime(tickers['start_date']) + pd.DateOffset(months=1)
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
close_final.to_excel('CPE_887.xlsx')

######################
automate = pd.read_excel('CPE_887.xlsx').sort_values(['ticker', 'rn'])
automate['Price Date'] = np.where(automate['rn']==0, automate['start_date2'], automate['Date'])
automate2 = automate.groupby(['ticker', 'start_date', 'Price Date', 'rn'], as_index=False)['close'].mean()
automate2['Price Date'] = automate2['Price Date'].astype('str')
automate2['close_lag120'] = automate2.groupby('ticker')['close'].shift(120)
automate2['close_lag25'] = automate2.groupby('ticker')['close'].shift(25)
automate2['close_lead75'] = automate2.groupby('ticker')['close'].shift(-75)
automate2['close_lead150'] = automate2.groupby('ticker')['close'].shift(-150)

automate3 = automate2[ (automate2['rn']>=0) & (automate2['rn']<=150)].copy()
automate3['close_max'] = automate3.groupby('ticker')['close'].transform('max')
automate3['close_min'] = automate3.groupby('ticker')['close'].transform('min')
automate3['Gain Date'] = np.where(automate3['close']==automate3['close_max'], automate3['rn'], np.nan)
automate3['Pain Date'] = np.where(automate3['close']==automate3['close_min'], automate3['rn'], np.nan)
automate3["Gain Date"] = automate3.groupby("ticker")["Gain Date"].transform(
    lambda x: x.fillna(x.max())
)
automate3["Pain Date"] = automate3.groupby("ticker")["Pain Date"].transform(
    lambda x: x.fillna(x.max())
)
automate3["cum_return"] = automate3.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
first_below_10 = automate3.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] < -0.1].head(1), include_groups=False
).reset_index()
first_below_20 = automate3.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()

automate4 = automate2[ (automate2['rn']>=7) & (automate2['rn']<=150)].copy()
automate4["cum_return"] = automate4.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
first_below_10_7D = automate4.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] < -0.1].head(1), include_groups=False
).reset_index()
first_below_20_7D = automate4.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()


automate3['-120D'] = automate3['close'] / automate3['close_lag120'] - 1
automate3['-25D'] = automate3['close'] / automate3['close_lag25'] - 1
automate3['75D'] = automate3['close_lead75'] / automate3['close'] - 1
automate3['150D'] = automate3['close_lead150'] / automate3['close'] - 1
automate3['Gain'] = automate3['close_max'] / automate3['close'] - 1
automate3['Pain'] = automate3['close_min'] / automate3['close'] - 1
automate3['CAR Date'] = automate3['start_date']
automate3['Price'] = automate3['close']

columns = ['ticker', 'CAR Date', 'Price Date', 'Price', '-120D', '-25D', '75D', '150D',
       'Gain', 'Gain Date', 'Pain', 'Pain Date']
rows = automate3['rn'] == 0
output = automate3[rows][columns].set_index('ticker').join(
    first_below_10[['ticker', 'rn']].rename(columns={"rn": "down_10"}).set_index('ticker')).join(
    first_below_20[['ticker', 'rn']].rename(columns={"rn": "down_20"}).set_index('ticker')).join(
    first_below_10_7D[['ticker', 'rn']].rename(columns={"rn": "down_10_7D"}).set_index('ticker')).join(
    first_below_20_7D[['ticker', 'rn']].rename(columns={"rn": "down_20_7D"}).set_index('ticker'))
output.to_csv('strategy.csv')

######################
# #####################
# tickers_dict2 = {
#     'SPHR': ['SPY'],# entertainment, no direct competitors
#     'MODV': ['ADUS', 'BTSG'],# focused on the “last mile” of care for government and managed‑care members
#  }
#
# _dict = {}
# for x, peer in tickers_dict2.items():
#     close_final_ind = close_final[close_final['ticker']==x]
#     data2 = yf.download(peer, start="2020-01-01")
#     benchmark = data2['Close'].reset_index()
#     close_final_ind = pd.merge(close_final_ind, benchmark, on='Date', how='left')
#     close_final_ind_final = close_final_ind[heads]
#     for p in peer:
#         tmp = close_final_ind.copy()
#         tmp['close'] = tmp[p]
#         tmp['ticker'] = tmp['ticker'].transform(lambda x: f"{x}_{p}")
#         tmp = tmp[heads]
#         close_final_ind_final = pd.concat([close_final_ind_final, tmp])
#     _dict[x] = close_final_ind_final
#
# output = pd.concat(_dict.values())
# output.to_excel('MOVING_to_BQR6.xlsx')