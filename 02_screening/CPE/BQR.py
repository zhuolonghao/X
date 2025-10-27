import numpy as np
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import MonthEnd

download = False

with open("_consolidate.py") as f:
    code = f.read()
    exec(code)

# List of tickers (either as a space-separated string or a list)
tickers_dict = []
tickers_dict2 = []
for b in BQR:
    if b[0] not in tickers_dict:
        tickers_dict.append(b[0])
        for bb in b[1]:
            tickers_dict2.append({'ticker': b[0], 'start_date': bb[0], 'ticker_alt': b[0]+'.'+bb[1]+'.'+bb[0][:4]+bb[0][5:7]})
    else:
        print(b[0])

if download:
    # Download historical data
    data = yf.download(tickers_dict, start="2020-01-01")

    # 2025.9.13
    vol = data['Volume'].reset_index()
    vol = pd.melt(vol, id_vars='Date', var_name='ticker', value_name='Volume')
    close = data['Close'].reset_index()
    close = pd.melt(close, id_vars='Date', var_name='ticker', value_name='close')
    close.set_index(['Date', 'ticker'])\
        .join(vol.set_index(['Date', 'ticker']))\
        .to_excel('BQR_vol.xlsx')

#################################
# Summary parts: start
#################################
close = pd.read_excel('BQR_vol.xlsx')
tickers = pd.DataFrame(tickers_dict2, columns=['ticker', 'start_date', 'ticker_alt'])
tickers['start_date2'] = pd.to_datetime(tickers['start_date']) + pd.DateOffset(months=1)
tickers['GroupIndex'] = tickers.groupby('ticker').cumcount() + 1

close_dict = {}
for i in range(1, tickers['GroupIndex'].max()+1):
    tickers2 = tickers[tickers['GroupIndex']==i]
    close_dict[i] = pd.merge(close, tickers, on='ticker', how='inner')
close = pd.concat(close_dict.values(), ignore_index=True)
close = close.drop(columns=['ticker']).rename(columns={'ticker_alt': 'ticker'})


close_final = close.drop_duplicates().sort_values(['ticker', 'Date'])
close_final['rn'] = close_final.groupby('ticker').cumcount()
rows = close_final['Date'] >= close_final['start_date2']
d0 = close_final[rows].groupby('ticker').first().reset_index()
d0['rn_0'] = d0['rn']
close_final = pd.merge(close_final, d0[['ticker', 'rn_0']], on='ticker', how='left')
close_final['rn'] = close_final['rn'] - close_final['rn_0']
# tmp = close_final[close_final['ticker']=='ADTN.58-75.202311']
cols = ['Date', 'close', 'Volume', 'start_date', 'ticker', 'start_date2', 'GroupIndex', 'rn']

# Meta
close_final['CAR Date'] = close_final['start_date']
close_final['Price Date'] = close_final['start_date2']
close_final['Price'] = close_final['close'].round(2)
cols = ['ticker', 'CAR Date', 'Price Date', 'Price']
rows = close_final['rn'] == 0
meta = close_final[rows][cols]

### Given date and find return
close_final['year'] = close_final['Date'].dt.year
close_final['month'] = close_final['Date'].dt.month
close_final['year2'] = close_final['start_date2'].dt.year
close_final['month2'] = close_final['start_date2'].dt.month

date_return = close_final.groupby(['ticker', 'year', 'month']).first().reset_index()
date_return['return'] = date_return['close'] / date_return.groupby('ticker')['close'].shift(1) - 1
date_return['T6M.cum'] = date_return['close'] / date_return.groupby('ticker')['close'].shift(6) - 1
date_return['T3M.cum'] = date_return['close'] / date_return.groupby('ticker')['close'].shift(3) - 1
date_return['N3M.cum'] = date_return.groupby('ticker')['close'].shift(-3) / date_return['close'] - 1
date_return['N6M.cum'] = date_return.groupby('ticker')['close'].shift(-6) / date_return['close'] - 1
date_return['M-6'] = date_return.groupby('ticker')['return'].shift(6)
date_return['M-5'] = date_return.groupby('ticker')['return'].shift(5)
date_return['M-4'] = date_return.groupby('ticker')['return'].shift(4)
date_return['M-3'] = date_return.groupby('ticker')['return'].shift(3)
date_return['M-2'] = date_return.groupby('ticker')['return'].shift(2)
date_return['M0'] = date_return['return']
date_return['M-1'] = date_return.groupby('ticker')['return'].shift(1)
date_return['M+1'] = date_return.groupby('ticker')['return'].shift(-1)
date_return['M+2'] = date_return.groupby('ticker')['return'].shift(-2)
date_return['M+3'] = date_return.groupby('ticker')['return'].shift(-3)
date_return['M+4'] = date_return.groupby('ticker')['return'].shift(-4)
date_return['M+5'] = date_return.groupby('ticker')['return'].shift(-5)
date_return['M+6'] = date_return.groupby('ticker')['return'].shift(-6)

rows = (date_return['year'] == date_return['year2']) & (date_return['month'] == date_return['month2'])
cols = ['ticker',
        'M-6', 'M-5', 'M-4', 'M-3', 'M-2', 'M-1', 'M0',
        'M+1', 'M+2', 'M+3', 'M+4', 'M+5', 'M+6', 'T6M.cum', 'T3M.cum', 'N3M.cum', 'N6M.cum']
date_return = date_return[rows][cols]

### volume
volume = close_final.copy()

volume['vol'] = volume.groupby(['ticker', 'year', 'month'])['Volume'].transform('mean')/1e6
volume['vol'] = volume['vol']
volume = volume.groupby(['ticker', 'year', 'month']).first().reset_index()
volume['M-6'] = volume.groupby('ticker')['vol'].shift(6)
volume['M-5'] = volume.groupby('ticker')['vol'].shift(5)
volume['M-4'] = volume.groupby('ticker')['vol'].shift(4)
volume['M-3'] = volume.groupby('ticker')['vol'].shift(3)
volume['M-2'] = volume.groupby('ticker')['vol'].shift(2)
volume['M-1'] = volume.groupby('ticker')['vol'].shift(1)
volume['M0'] = volume['vol']
volume['M+1'] = volume.groupby('ticker')['vol'].shift(-1)
volume['M+2'] = volume.groupby('ticker')['vol'].shift(-2)
volume['M+3'] = volume.groupby('ticker')['vol'].shift(-3)
volume['M+4'] = volume.groupby('ticker')['vol'].shift(-4)
volume['M+5'] = volume.groupby('ticker')['vol'].shift(-5)
volume['M+6'] = volume.groupby('ticker')['vol'].shift(-6)
volume['T6M.avg'] = volume[['M-6', 'M-5', 'M-4', 'M-3', 'M-2', 'M-1']].mean(axis=1, skipna=True)
volume['T3M.avg'] = volume[['M-3', 'M-2', 'M-1']].mean(axis=1, skipna=True)
volume['N3M.avg'] = volume[['M+1', 'M+2', 'M+3', 'M+4', 'M+5', 'M+6']].mean(axis=1, skipna=True)
volume['N6M.avg'] = volume[['M+1', 'M+2', 'M+3']].mean(axis=1, skipna=True)
rows = (volume['year'] == volume['year2']) & (volume['month'] == volume['month2'])
cols = ['ticker',
        'M-6', 'M-5', 'M-4', 'M-3', 'M-2', 'M-1', 'M0',
        'M+1', 'M+2', 'M+3', 'M+4', 'M+5', 'M+6', 'T6M.avg', 'T3M.avg', 'N3M.avg', 'N6M.avg']
volume = volume[rows][cols]

### Given return and find date
rows = (close_final['rn']>=0) & (close_final['rn']<=150)
return_date= close_final[rows].sort_values(['ticker', 'rn'])
return_date["cum_return"] = return_date.groupby("ticker")["close"] \
                     .transform(lambda x: x / x.iloc[0] - 1)
first_above_10 = return_date.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] >= 0.1].head(1), include_groups=False
).reset_index()
first_below_10 = return_date.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] <= -0.1].head(1), include_groups=False
).reset_index()
first_above_20 = return_date.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] >= 0.2].head(1), include_groups=False
).reset_index()
first_below_20 = return_date.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] <= -0.2].head(1), include_groups=False
).reset_index()
first_above_30 = return_date.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] >= 0.30].head(1), include_groups=False
).reset_index()
first_below_30 = return_date.groupby("ticker", ).apply(
    lambda g: g.loc[g["cum_return"] <= -0.3].head(1), include_groups=False
).reset_index()

return_date = first_above_10[['ticker', 'rn']].rename(columns={"rn": "up.10%"}).set_index('ticker').join(
    first_above_20[['ticker', 'rn']].rename(columns={"rn": "up.20%"}).set_index('ticker')).join(
    first_above_30[['ticker', 'rn']].rename(columns={"rn": "up.30%"}).set_index('ticker')).join(
    first_below_10[['ticker', 'rn']].rename(columns={"rn": "down.10%"}).set_index('ticker')).join(
    first_below_20[['ticker', 'rn']].rename(columns={"rn": "down.20%"}).set_index('ticker')).join(
    first_below_30[['ticker', 'rn']].rename(columns={"rn": "down.30%"}).set_index('ticker'))
return_date = return_date.astype('Int64').reset_index()

return_date2 = first_above_10[['ticker', 'Date']].rename(columns={"Date": "up.10%"}).set_index('ticker').join(
    first_above_20[['ticker', 'Date']].rename(columns={"Date": "up.20%"}).set_index('ticker')).join(
    first_above_30[['ticker', 'Date']].rename(columns={"Date": "up.30%"}).set_index('ticker')).join(
    first_below_10[['ticker', 'Date']].rename(columns={"Date": "down.10%"}).set_index('ticker')).join(
    first_below_20[['ticker', 'Date']].rename(columns={"Date": "down.20%"}).set_index('ticker')).join(
    first_below_30[['ticker', 'Date']].rename(columns={"Date": "down.30%"}).set_index('ticker'))
for col in return_date2.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']):
    return_date2[col] = return_date2[col].dt.strftime('%Y-%m-%d')
return_date2 = return_date2.reset_index()

### highest / lowest
rows = (close_final['rn']>=0) & (close_final['rn']<=150)
gain_pain= close_final[rows].sort_values(['ticker', 'rn'])

gain_pain['close_max'] = gain_pain.groupby('ticker')['close'].transform('max')
gain_pain['close_min'] = gain_pain.groupby('ticker')['close'].transform('min')
gain_pain['highest_rn'] = np.where(gain_pain['close']==gain_pain['close_max'], gain_pain['rn'], np.nan)
gain_pain["highest_rn"] = gain_pain.groupby("ticker")["highest_rn"].transform(
    lambda x: x.fillna(x.min())
)
gain_pain['lowest_rn'] = np.where(gain_pain['close']==gain_pain['close_min'], gain_pain['rn'], np.nan)
gain_pain["lowest_rn"] = gain_pain.groupby("ticker")["lowest_rn"].transform(
    lambda x: x.fillna(x.min())
)
gain_pain['highest_date'] = np.where(gain_pain['close']==gain_pain['close_max'], gain_pain['Date'].dt.strftime('%Y-%m-%d'), pd.NaT)
gain_pain["highest_date"] = gain_pain.groupby("ticker")["highest_date"].transform(
    lambda x: x.bfill()
)
gain_pain['lowest_date'] = np.where(gain_pain['close']==gain_pain['close_min'], gain_pain['Date'].dt.strftime('%Y-%m-%d'), pd.NaT)
gain_pain["lowest_date"] = gain_pain.groupby("ticker")["lowest_date"].transform(
    lambda x: x.bfill()
)
rows = (gain_pain['rn']==0)
cols = ['ticker', 'highest', 'highest_rn', 'highest_date', 'lowest', 'lowest_rn', 'lowest_date']
gain_pain['highest_rn'] = gain_pain['highest_rn'].astype('Int64')
gain_pain['lowest_rn'] = gain_pain['lowest_rn'].astype('Int64')
gain_pain['highest'] = gain_pain['close_max'] / gain_pain['close'] - 1
gain_pain['lowest'] = gain_pain['close_min'] / gain_pain['close'] - 1
gain_pain = gain_pain[rows][cols]



summary = meta.set_index('ticker').join(
        date_return.set_index('ticker')).join(
        return_date.set_index('ticker')).join(
        return_date2.set_index('ticker'), lsuffix='.days', rsuffix='.date').join(
        gain_pain.set_index('ticker')).join(
        volume.set_index('ticker'), lsuffix='.ret', rsuffix='.vol')

summary.to_excel('summary.xlsx')
summary[['T6M.cum', 'T3M.cum', 'N3M.cum', 'N6M.cum',]].mean(numeric_only=True)


#################################
# Summary parts: end
#################################



#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# ######################
# automate = close_final.sort_values(['ticker', 'rn'])
# automate['Price Date'] = np.where(automate['rn']==0, automate['start_date2'], automate['Date'])
# automate2 = automate.groupby(['ticker', 'start_date', 'Price Date', 'rn'], as_index=False)['close'].mean()
# automate2['Price Date'] = automate2['Price Date'].astype('str')
# automate2['close_lag120'] = automate2.groupby('ticker')['close'].shift(120)
# automate2['close_lag25'] = automate2.groupby('ticker')['close'].shift(25)
# automate2['close_lead75'] = automate2.groupby('ticker')['close'].shift(-75)
# automate2['close_lead150'] = automate2.groupby('ticker')['close'].shift(-150)
#
# automate3 = automate2[ (automate2['rn']>=0) & (automate2['rn']<=150)].copy()
# automate3['close_max'] = automate3.groupby('ticker')['close'].transform('max')
# automate3['close_min'] = automate3.groupby('ticker')['close'].transform('min')
# automate3['Gain Date'] = np.where(automate3['close']==automate3['close_max'], automate3['rn'], np.nan)
# automate3['Pain Date'] = np.where(automate3['close']==automate3['close_min'], automate3['rn'], np.nan)
# automate3["Gain Date"] = automate3.groupby("ticker")["Gain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# automate3["Pain Date"] = automate3.groupby("ticker")["Pain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# automate3["cum_return"] = automate3.groupby("ticker")["close"] \
#                      .transform(lambda x: x / x.iloc[0] - 1)
#
# ### Openning trade strategies
# first_above_10 = automate3.groupby("ticker", ).apply(
#     lambda g: g.loc[g["cum_return"] > 0.1].head(1), include_groups=False
# ).reset_index()
# first_below_10 = automate3.groupby("ticker", ).apply(
#     lambda g: g.loc[g["cum_return"] < -0.1].head(1), include_groups=False
# ).reset_index()
# first_above_20 = automate3.groupby("ticker", ).apply(
#     lambda g: g.loc[g["cum_return"] > 0.2].head(1), include_groups=False
# ).reset_index()
# first_below_20 = automate3.groupby("ticker", ).apply(
#     lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
# ).reset_index()
# first_above_30 = automate3.groupby("ticker", ).apply(
#     lambda g: g.loc[g["cum_return"] > 0.30].head(1), include_groups=False
# ).reset_index()
# first_below_30 = automate3.groupby("ticker", ).apply(
#     lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
# ).reset_index()
# ### Openning trade strategies
#
# automate3['-120D'] = automate3['close'] / automate3['close_lag120'] - 1
# automate3['-25D'] = automate3['close'] / automate3['close_lag25'] - 1
# automate3['75D'] = automate3['close_lead75'] / automate3['close'] - 1
# automate3['150D'] = automate3['close_lead150'] / automate3['close'] - 1
# automate3['Gain'] = automate3['close_max'] / automate3['close'] - 1
# automate3['Pain'] = automate3['close_min'] / automate3['close'] - 1
# automate3['CAR Date'] = automate3['start_date']
# automate3['Price'] = automate3['close']
#
# columns = ['ticker', 'CAR Date', 'Price Date', 'Price', '-120D', '-25D', '75D', '150D',
#        'Gain', 'Gain Date', 'Pain', 'Pain Date']
# rows = automate3['rn'] == 0
# output = automate3[rows][columns].set_index('ticker').join(
#     first_above_10[['ticker', 'rn']].rename(columns={"rn": "up_10"}).set_index('ticker')).join(
#     first_above_20[['ticker', 'rn']].rename(columns={"rn": "up_20"}).set_index('ticker')).join(
#     first_above_30[['ticker', 'rn']].rename(columns={"rn": "up_30"}).set_index('ticker')).join(
#     first_below_10[['ticker', 'rn']].rename(columns={"rn": "down_10"}).set_index('ticker')).join(
#     first_below_20[['ticker', 'rn']].rename(columns={"rn": "down_20"}).set_index('ticker')).join(
#     first_below_30[['ticker', 'rn']].rename(columns={"rn": "down_30"}).set_index('ticker'))
#
#
# result_ret = {}
#
# asap = automate2[(automate2['rn']>=7) & (automate2['rn']<=150)].copy()
# asap['close_max'] = asap.groupby('ticker')['close'].transform('max')
# asap['close_min'] = asap.groupby('ticker')['close'].transform('min')
# asap['Gain Date'] = np.where(asap['close']==asap['close_max'], asap['rn'], np.nan)
# asap['Pain Date'] = np.where(asap['close']==asap['close_min'], asap['rn'], np.nan)
# asap["Gain Date"] = asap.groupby("ticker")["Gain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# asap["Pain Date"] = asap.groupby("ticker")["Pain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# asap["cum_return"] = asap.groupby("ticker")["close"] \
#                      .transform(lambda x: x / x.iloc[0] - 1)
# asap["avg_cum_return"] = asap.groupby("ticker")["cum_return"].transform("mean")
# first_below_20 = asap.groupby("ticker", ).apply(
#     lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
# ).reset_index()
# first_below_30 = asap.groupby("ticker", ).apply(
#     lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
# ).reset_index()
# asap2 = asap[asap['rn']==7].copy()
# asap2['Gain_ret'] = asap2['close_max'] / asap2['close'] - 1
# asap2['Pain_ret'] = asap2['close_min'] / asap2['close'] - 1
# asap2['Gain_ret'] = np.where((asap2['Gain Date'] > 25) , asap2['Gain_ret'], asap2['avg_cum_return'])
# asap2['Gain Date'] = np.where((asap2['Gain Date'] > 25), asap2['Gain Date'],999)
# columns = ['ticker', 'Gain_ret', 'Gain Date']
# asap3 = asap2[columns].set_index('ticker').join(
#     first_below_20[['ticker', 'rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'}).set_index('ticker')).join(
#     first_below_30[['ticker', 'rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}).set_index('ticker'))
# asap3['cum_ret_exit_20'] = np.where((asap3['Gain Date'] < asap3['exit_dt_down_20']) | (asap3['exit_dt_down_20']).isna(), asap3['Gain_ret'], asap3['return_exit_20'])
# asap3['ret_date_20'] = np.fmin(asap3['Gain Date'], asap3['exit_dt_down_20'])
# asap3['cum_ret_exit_30'] = np.where((asap3['Gain Date'] < asap3['exit_dt_down_30']) | (asap3['exit_dt_down_30']).isna(), asap3['Gain_ret'], asap3['return_exit_30'])
# asap3['ret_date_30'] = np.fmin(asap3['Gain Date'], asap3['exit_dt_down_30'])
# columns = ['cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
# asap3 = asap3[columns]
#
# result_ret['bqr6_asap_20'] = asap3['cum_ret_exit_20'].dropna().to_list()
# result_ret['bqr6_asap_30'] = asap3['cum_ret_exit_30'].dropna().to_list()
#
# ### Material movement by 10%
# h2c = output.reset_index('ticker')
# h2c['Action'] = np.maximum(7, np.fmin(h2c['up_10'], h2c['down_10']))
# h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
# rows = h2c['rn'] >= h2c['Action']
# h2c2 = h2c[rows].copy()
# h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
# h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
# h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
# h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
# h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
#                      .transform(lambda x: x / x.iloc[0] - 1)
# h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
# first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
# ).reset_index()
# first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
# ).reset_index()
# h2c3 = h2c2.groupby('ticker').head(1).copy()
# h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
# h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
# h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
# h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
# columns = ['Action', 'Gain_ret', 'Gain Date']
# h2c4 = h2c3[columns].join(
#     first_below_20[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
#     first_below_30[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
# h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
# h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
# h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
# h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
# columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
# h2c_material_10 = h2c4[columns]
#
# result_ret['bqr6_move10_ext20'] = h2c_material_10['cum_ret_exit_20'].dropna().to_list()
# result_ret['bqr6_move10_ext30'] = h2c_material_10['cum_ret_exit_30'].dropna().to_list()
#
# ### Material movement by 20%
# h2c = output.reset_index('ticker')
# h2c['Action'] = np.maximum(7, np.fmin(h2c['up_20'], h2c['down_20']))
# h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
# rows = h2c['rn'] >= h2c['Action']
# h2c2 = h2c[rows].copy()
# h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
# h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
# h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
# h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
# h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
#                      .transform(lambda x: x / x.iloc[0] - 1)
# h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
# first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
# ).reset_index()
# first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
# ).reset_index()
# h2c3 = h2c2.groupby('ticker').head(1).copy()
# h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
# h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
# h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
# h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
# columns = ['Action', 'Gain_ret', 'Gain Date']
# h2c4 = h2c3[columns].join(
#     first_below_20[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
#     first_below_30[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
# h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
# h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
# h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
# h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
# columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
# h2c_material_20 = h2c4[columns]
#
# result_ret['bqr6_move20_ext20'] = h2c_material_20['cum_ret_exit_20'].dropna().to_list()
# result_ret['bqr6_move20_ext30'] = h2c_material_20['cum_ret_exit_30'].dropna().to_list()
#
#
#
# ### Material movement by 30%
# h2c = output.reset_index('ticker')
# h2c['Action'] = np.maximum(7, np.fmin(h2c['up_30'], h2c['down_30']))
# h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
# rows = h2c['rn'] >= h2c['Action']
# h2c2 = h2c[rows].copy()
# h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
# h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
# h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
# h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
# h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
#                      .transform(lambda x: x / x.iloc[0] - 1)
# h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
# first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
# ).reset_index()
# first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
# ).reset_index()
# h2c3 = h2c2.groupby('ticker').head(1).copy()
# h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
# h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
# h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
# h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
# columns = ['Action', 'Gain_ret', 'Gain Date']
# h2c4 = h2c3[columns].join(
#     first_below_20[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
#     first_below_30[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
# h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
# h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
# h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
# h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
# columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
# h2c_material_30 = h2c4[columns]
#
# result_ret['bqr6_move30_ext20'] = h2c_material_30['cum_ret_exit_20'].dropna().to_list()
# result_ret['bqr6_move30_ext30'] = h2c_material_30['cum_ret_exit_30'].dropna().to_list()
#
#
#
# ### Material down by 10%
# h2c = output.reset_index('ticker')
# h2c['Action'] = np.maximum(7, h2c['down_10'])
# h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
# rows = h2c['rn'] >= h2c['Action']
# h2c2 = h2c[rows].copy()
# h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
# h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
# h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
# h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
# h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
#                      .transform(lambda x: x / x.iloc[0] - 1)
# h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
# first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
# ).reset_index()
# first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
# ).reset_index()
# h2c3 = h2c2.groupby('ticker').head(1).copy()
# h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
# h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
# h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
# h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
# columns = ['Action', 'Gain_ret', 'Gain Date']
# h2c4 = h2c3[columns].join(
#     first_below_20[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
#     first_below_30[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
# h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
# h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
# h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
# h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
# columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
# h2c_down_10 = h2c4[columns]
#
# result_ret['bqr6_down10_ext20'] = h2c_down_10['cum_ret_exit_20'].dropna().to_list()
# result_ret['bqr6_down10_ext30'] = h2c_down_10['cum_ret_exit_30'].dropna().to_list()
#
#
#
# ### Material down by 20%
# h2c = output.reset_index('ticker')
# h2c['Action'] = np.maximum(7, h2c['down_20'])
# h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
# rows = h2c['rn'] >= h2c['Action']
# h2c2 = h2c[rows].copy()
# h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
# h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
# h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
# h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
# h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
#                      .transform(lambda x: x / x.iloc[0] - 1)
# h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
# first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
# ).reset_index()
# first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
# ).reset_index()
# h2c3 = h2c2.groupby('ticker').head(1).copy()
# h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
# h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
# h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
# h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
# columns = ['Action', 'Gain_ret', 'Gain Date']
# h2c4 = h2c3[columns].join(
#     first_below_20[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
#     first_below_30[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
# h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
# h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
# h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
# h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
# columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
# h2c_down_20 = h2c4[columns]
#
# result_ret['bqr6_down20_ext20'] = h2c_down_20['cum_ret_exit_20'].dropna().to_list()
# result_ret['bqr6_down20_ext30'] = h2c_down_20['cum_ret_exit_30'].dropna().to_list()
#
#
# ### Material down by 30%
# h2c = output.reset_index('ticker')
# h2c['Action'] = np.maximum(7, h2c['down_30'])
# h2c = asap.set_index('ticker').join(h2c[['ticker', 'Action']].set_index('ticker'))
# rows = h2c['rn'] >= h2c['Action']
# h2c2 = h2c[rows].copy()
# h2c2['close_max'] = h2c2.groupby('ticker')['close'].transform('max')
# h2c2['close_min'] = h2c2.groupby('ticker')['close'].transform('min')
# h2c2['Gain Date'] = np.where(h2c2['close']==h2c2['close_max'], h2c2['rn'], np.nan)
# h2c2['Pain Date'] = np.where(h2c2['close']==h2c2['close_min'], h2c2['rn'], np.nan)
# h2c2["Gain Date"] = h2c2.groupby("ticker")["Gain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["Pain Date"] = h2c2.groupby("ticker")["Pain Date"].transform(
#     lambda x: x.fillna(x.max())
# )
# h2c2["cum_return"] = h2c2.groupby("ticker")["close"] \
#                      .transform(lambda x: x / x.iloc[0] - 1)
# h2c2["avg_cum_return"] = h2c2.groupby("ticker")["cum_return"].transform("mean")
# first_below_20 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.2].head(1), include_groups=False
# ).reset_index()
# first_below_30 = h2c2.groupby("ticker", as_index=False).apply(
#     lambda g: g.loc[g["cum_return"] < -0.3].head(1), include_groups=False
# ).reset_index()
# h2c3 = h2c2.groupby('ticker').head(1).copy()
# h2c3['Gain_ret'] = h2c3['close_max'] / h2c3['close'] - 1
# h2c3['Pain_ret'] = h2c3['close_min'] / h2c3['close'] - 1
# h2c3["Gain_ret"] = h2c3["Gain_ret"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), h2c3["avg_cum_return"])
# h2c3["Gain Date"] = h2c3["Gain Date"].where((h2c3["Gain Date"] >= (25+h2c3["Action"])), 999)
# columns = ['Action', 'Gain_ret', 'Gain Date']
# h2c4 = h2c3[columns].join(
#     first_below_20[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_20", 'cum_return': 'return_exit_20'})).join(
#     first_below_30[['rn', 'cum_return']].rename(
#         columns={"rn": "exit_dt_down_30", 'cum_return': 'return_exit_30'}))
# h2c4['cum_ret_exit_20'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_20']) | (h2c4['exit_dt_down_20']).isna(), h2c4['Gain_ret'], h2c4['return_exit_20'])
# h2c4['ret_date_20'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_20'])
# h2c4['cum_ret_exit_30'] = np.where((h2c4['Gain Date'] < h2c4['exit_dt_down_30']) | (h2c4['exit_dt_down_30']).isna(), h2c4['Gain_ret'], h2c4['return_exit_30'])
# h2c4['ret_date_30'] = np.fmin(h2c4['Gain Date'], h2c4['exit_dt_down_30'])
# columns = ['Action', 'cum_ret_exit_20', 'ret_date_20', 'cum_ret_exit_30', 'ret_date_30']
# h2c_down_30 = h2c4[columns]
#
# result_ret['bqr6_down30_ext20'] = h2c_down_30['cum_ret_exit_20'].dropna().to_list()
# result_ret['bqr6_down30_ext30'] = h2c_down_30['cum_ret_exit_30'].dropna().to_list()
#
#
#
# result = output\
#     .join(asap3, rsuffix='_asap')\
#     .join(h2c_down_10,  rsuffix="_down_10") \
#     .join(h2c_down_20, rsuffix="_down_20") \
#     .join(h2c_down_30, rsuffix="_down_30") \
#     .join(h2c_material_10, rsuffix="_move_10") \
#     .join(h2c_material_20, rsuffix="_move_20") \
#     .join(h2c_material_30, rsuffix="_move_30")
#
# ret = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in result_ret.items()]))
#
# result2 = result.reset_index()
# result2[['ticker', 'from', 'to', 'period']] = result2['ticker'].str.extract(r'([A-Z]+)\.(\d+)-(\d+)\.(\d+)')
#
# with pd.ExcelWriter("strategy_BQR.xlsx", engine="openpyxl") as writer:
#     result.to_excel(writer, sheet_name="result",)   # add index=False if you don’t want row numbers
#     result2.to_excel(writer, sheet_name="result2",)   # add index=False if you don’t want row numbers
#     ret.to_excel(writer, sheet_name="return", index=False)
#
