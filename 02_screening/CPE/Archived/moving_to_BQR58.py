import numpy as np
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import MonthEnd

with open("_consolidate.py") as f:
    code = f.read()
    exec(code)

# List of tickers (either as a space-separated string or a list)
tickers_dict = BQR58

# Download historical data
data = yf.download(list(tickers_dict.keys()), start="2020-01-01")

# 2025.9.13
vol = data['Volume'].reset_index()
vol = pd.melt(vol, id_vars='Date', var_name='ticker', value_name='Volume')

#
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
close_final.set_index(['Date', 'ticker'])\
    .join(vol.set_index(['Date', 'ticker']))\
    .to_excel('MOVING_to_BQR58_vol.xlsx')

######################
automate = pd.read_excel('MOVING_to_BQR58_vol.xlsx').sort_values(['ticker', 'rn'])
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

### Openning trade strategies
first_above_10 = automate3.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] > 0.1].head(1), include_groups=False
).reset_index()
first_below_10 = automate3.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] < -0.1].head(1), include_groups=False
).reset_index()
first_above_20 = automate3.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] > 0.2].head(1), include_groups=False
).reset_index()
first_below_20 = automate3.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()
first_above_30 = automate3.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] > 0.30].head(1), include_groups=False
).reset_index()
first_below_30 = automate3.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
).reset_index()
### Openning trade strategies

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
    first_above_10[['ticker', 'rn']].rename(columns={"rn": "up_10"}).set_index('ticker')).join(
    first_above_20[['ticker', 'rn']].rename(columns={"rn": "up_20"}).set_index('ticker')).join(
    first_above_30[['ticker', 'rn']].rename(columns={"rn": "up_30"}).set_index('ticker')).join(
    first_below_10[['ticker', 'rn']].rename(columns={"rn": "down_10"}).set_index('ticker')).join(
    first_below_20[['ticker', 'rn']].rename(columns={"rn": "down_20"}).set_index('ticker')).join(
    first_below_30[['ticker', 'rn']].rename(columns={"rn": "down_30"}).set_index('ticker'))


result_ret = {}

asap = automate2[(automate2['rn']>=7) & (automate2['rn']<=150)].copy()
asap['close_max'] = asap.groupby('ticker')['close'].transform('max')
asap['close_min'] = asap.groupby('ticker')['close'].transform('min')
asap['Gain Date'] = np.where(asap['close']==asap['close_max'], asap['rn'], np.nan)
asap['Pain Date'] = np.where(asap['close']==asap['close_min'], asap['rn'], np.nan)
asap["Gain Date"] = asap.groupby("ticker")["Gain Date"].transform(
    lambda x: x.fillna(x.max())
)
asap["Pain Date"] = asap.groupby("ticker")["Pain Date"].transform(
    lambda x: x.fillna(x.max())
)
asap["cum_return"] = asap.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
asap["avg_cum_return"] = asap.groupby("ticker")["cum_return"].transform("mean")
first_below_20 = asap.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()
first_below_30 = asap.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
).reset_index()
asap2 = asap[asap['rn']==7].copy()
asap2['Gain_ret'] = asap2['close_max'] / asap2['close'] - 1
asap2['Pain_ret'] = asap2['close_min'] / asap2['close'] - 1
asap2['Gain_ret'] = np.where((asap2['Gain Date'] > 25) , asap2['Gain_ret'], asap2['avg_cum_return'])
asap2['Gain Date'] = np.where((asap2['Gain Date'] > 25), asap2['Gain Date'],999)
columns = ['ticker', 'Gain_ret', 'Gain Date']
asap3 = asap2[columns].set_index('ticker').join(
    first_below_20[['ticker', 'rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'}).set_index('ticker')).join(
    first_below_30[['ticker', 'rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}).set_index('ticker'))
asap3['cum_ret_exit_20'] = np.where((asap3['Gain Date'] < asap3['exit_dt_down_20']) | (asap3['exit_dt_down_20']).isna(), asap3['Gain_ret'], asap3['return_exit_20'])
asap3['ret_date_20'] = np.fmin(asap3['Gain Date'], asap3['exit_dt_down_20'])
asap3['cum_ret_exit_30'] = np.where((asap3['Gain Date'] < asap3['exit_dt_down_30']) | (asap3['exit_dt_down_30']).isna(), asap3['Gain_ret'], asap3['return_exit_30'])
asap3['ret_date_30'] = np.fmin(asap3['Gain Date'], asap3['exit_dt_down_30'])
columns = ['cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
asap3 = asap3[columns]

result_ret['bqr5_asap_20'] = asap3['cum_ret_exit_20'].dropna().to_list()
result_ret['bqr5_asap_30'] = asap3['cum_ret_exit_30'].dropna().to_list()

### Material movement by 10%
h2c = output.reset_index('ticker')
h2c['Action'] = np.maximum(7, np.fmin(h2c['up_10'], h2c['down_10']))
h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
rows = h2c['rn'] >= h2c['Action']
h2c2 = h2c[rows].copy()
h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()
first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
).reset_index()
h2c3 = h2c2.groupby('ticker').head(1).copy()
h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
columns = ['Action', 'Gain_ret', 'Gain Date']
h2c4 = h2c3[columns].join(
    first_below_20[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
    first_below_30[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
h2c_material_10 = h2c4[columns]

result_ret['bqr5_move10_ext20'] = h2c_material_10['cum_ret_exit_20'].dropna().to_list()
result_ret['bqr5_move10_ext30'] = h2c_material_10['cum_ret_exit_30'].dropna().to_list()

### Material movement by 20%
h2c = output.reset_index('ticker')
h2c['Action'] = np.maximum(7, np.fmin(h2c['up_20'], h2c['down_20']))
h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
rows = h2c['rn'] >= h2c['Action']
h2c2 = h2c[rows].copy()
h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()
first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
).reset_index()
h2c3 = h2c2.groupby('ticker').head(1).copy()
h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
columns = ['Action', 'Gain_ret', 'Gain Date']
h2c4 = h2c3[columns].join(
    first_below_20[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
    first_below_30[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
h2c_material_20 = h2c4[columns]

result_ret['bqr5_move20_ext20'] = h2c_material_20['cum_ret_exit_20'].dropna().to_list()
result_ret['bqr5_move20_ext30'] = h2c_material_20['cum_ret_exit_30'].dropna().to_list()



### Material movement by 30%
h2c = output.reset_index('ticker')
h2c['Action'] = np.maximum(7, np.fmin(h2c['up_30'], h2c['down_30']))
h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
rows = h2c['rn'] >= h2c['Action']
h2c2 = h2c[rows].copy()
h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()
first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
).reset_index()
h2c3 = h2c2.groupby('ticker').head(1).copy()
h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
columns = ['Action', 'Gain_ret', 'Gain Date']
h2c4 = h2c3[columns].join(
    first_below_20[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
    first_below_30[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
h2c_material_30 = h2c4[columns]

result_ret['bqr5_move30_ext20'] = h2c_material_30['cum_ret_exit_20'].dropna().to_list()
result_ret['bqr5_move30_ext30'] = h2c_material_30['cum_ret_exit_30'].dropna().to_list()



### Material down by 10%
h2c = output.reset_index('ticker')
h2c['Action'] = np.maximum(7, h2c['down_10'])
h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
rows = h2c['rn'] >= h2c['Action']
h2c2 = h2c[rows].copy()
h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()
first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
).reset_index()
h2c3 = h2c2.groupby('ticker').head(1).copy()
h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
columns = ['Action', 'Gain_ret', 'Gain Date']
h2c4 = h2c3[columns].join(
    first_below_20[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
    first_below_30[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
h2c_down_10 = h2c4[columns]

result_ret['bqr5_down10_ext20'] = h2c_down_10['cum_ret_exit_20'].dropna().to_list()
result_ret['bqr5_down10_ext30'] = h2c_down_10['cum_ret_exit_30'].dropna().to_list()



### Material down by 20%
h2c = output.reset_index('ticker')
h2c['Action'] = np.maximum(7, h2c['down_20'])
h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
rows = h2c['rn'] >= h2c['Action']
h2c2 = h2c[rows].copy()
h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()
first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
).reset_index()
h2c3 = h2c2.groupby('ticker').head(1).copy()
h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
columns = ['Action', 'Gain_ret', 'Gain Date']
h2c4 = h2c3[columns].join(
    first_below_20[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
    first_below_30[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
h2c_down_20 = h2c4[columns]

result_ret['bqr5_down20_ext20'] = h2c_down_20['cum_ret_exit_20'].dropna().to_list()
result_ret['bqr5_down20_ext30'] = h2c_down_20['cum_ret_exit_30'].dropna().to_list()


### Material down by 30%
h2c = output.reset_index('ticker')
h2c['Action'] = np.maximum(7, h2c['down_30'])
h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
rows = h2c['rn'] >= h2c['Action']
h2c2 = h2c[rows].copy()
h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
    lambda x: x.fillna(x.max())
)
h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
).reset_index()
first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
    lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
).reset_index()
h2c3 = h2c2.groupby('ticker').head(1).copy()
h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
columns = ['Action', 'Gain_ret', 'Gain Date']
h2c4 = h2c3[columns].join(
    first_below_20[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
    first_below_30[['rn', 'cum_return']].rename(
        columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
h2c_down_30 = h2c4[columns]

result_ret['bqr5_down30_ext20'] = h2c_down_30['cum_ret_exit_20'].dropna().to_list()
result_ret['bqr5_down30_ext30'] = h2c_down_30['cum_ret_exit_30'].dropna().to_list()



result = output\
    .join(asap3, rsuffix='_asap')\
    .join(h2c_down_10,  rsuffix="_down_10") \
    .join(h2c_down_20, rsuffix="_down_20") \
    .join(h2c_down_30, rsuffix="_down_30") \
    .join(h2c_material_10, rsuffix="_move_10") \
    .join(h2c_material_20, rsuffix="_move_20") \
    .join(h2c_material_30, rsuffix="_move_30")

ret = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in result_ret.items()]))

with pd.ExcelWriter("strategy_BQR58.xlsx", engine="openpyxl") as writer:
    result.to_excel(writer, sheet_name="result",)   # add index=False if you don’t want row numbers
    ret.to_excel(writer, sheet_name="return", index=False)
