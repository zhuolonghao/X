import os, re, time, shutil
import pandas as pd
import wikipedia as wp
import io
# Pull SP500
title = 'List of S&P 500 companies'
html = wp.page(title, auto_suggest=False).html()
html_io = io.StringIO(html)
tables = pd.read_html(html_io)
current = tables[0]
tickers =  ['SPY'] + [str(x).replace(".", "-").replace("/", "-") for x in current['Symbol']]

exec(open('_utility/download_tickers_from_yfinance3.py').read())
price = download(tickers=tickers, data_type="price", period="5y", interval="1d")
price.columns = [x.lower() for x in price.columns]
price.sort_values(by=['ticker', 'date_raw'], inplace=True)
price['ret'] = price.groupby(['ticker'])['close'].pct_change()
price2 = price.pivot(index='date_raw', columns='ticker', values='ret').iloc[1:,]

c20 = price2.rolling(20).corr(pairwise=True).xs('SPY', level=1, drop_level=True).drop('SPY', axis=1).mean(axis=1)
c50 = price2.rolling(50).corr(pairwise=True).xs('SPY', level=1, drop_level=True).drop('SPY', axis=1).mean(axis=1)
c65 = price2.rolling(65).corr(pairwise=True).xs('SPY', level=1, drop_level=True).drop('SPY', axis=1).mean(axis=1)

output = pd.concat([
    c20.to_frame().assign(variable='c20'),
    c50.to_frame().assign(variable='c50'),
    c65.to_frame().assign(variable='c65')], axis=0)
output.columns = ['value', 'variable']
output['MA5_max'] = output.groupby('variable')['value'].rolling(5).max().reset_index(0,drop=True)
output['MA5_min'] = output.groupby('variable')['value'].rolling(5).min().reset_index(0,drop=True)
output['MA5_avg'] = output.groupby('variable')['value'].rolling(5).mean().reset_index(0,drop=True)


trend = price[price['ticker'].eq('SPY')].set_index('date_raw')['close']

volume = price.pivot(index='date_raw', columns='ticker', values='volume').drop('SPY', axis=1)
volume['volume'] = volume.sum(axis=1)

output = output.join(trend).join(volume['volume']).reset_index()
output['date'] = output['date_raw'].dt.strftime('%Y-%m-%d')
output.drop('date_raw', axis=1).to_excel(f'codes/A.sp500_implied_correlation_daily/sp500_component.xlsx', index=False)


##########################################
# Buy into MoM + Rev
##########################################
price.sort_values(by=['ticker', 'date_raw'], inplace=True)
price['ret_20d'] = price.groupby(['ticker'])['close'].pct_change(20)
price['ret_60d'] = price.groupby(['ticker'])['close'].pct_change(60)
price['ret_125d'] = price.groupby(['ticker'])['close'].pct_change(125)
price['ret_250d'] = price.groupby(['ticker'])['close'].pct_change(250)
price['ret_250d/125d'] = (1+price['ret_250d']) / (1+price['ret_125d']) - 1

rows = price['ticker'].eq('SPY')
price2 = price[~rows]
trend = price[rows].tail(10)
price3 = price2.groupby('ticker').tail(10).copy()
_dict = {'ret_20d': 'rank_20d', 'ret_60d': 'rank_60d',
         'ret_125d': 'rank_125d', 'ret_250d': 'rank_250d',
         'ret_250d/125d': 'rank_250d/125d'}
for raw, new in _dict.items():
    price3[new] = price3.groupby('date_raw')[raw].rank(ascending=False)
price3['rank_20+60+125'] = price3[['rank_20d', 'rank_60d', 'rank_125d']].mean(axis=1)
price3['rank_20+60+125'] = price3.groupby('date_raw')['rank_20+60+125'].rank(method='dense', ascending=True)

cols1 = ['date_raw', 'ticker', 'close', 'volume']
cols2 = ['rank_20+60+125', 'rank_20d', 'rank_60d', 'rank_125d', 'rank_250d', 'rank_250d/125d']
price4 = pd.concat([price3[cols1+cols2],  trend[cols1]], ignore_index=True)
price4['date'] = price4['date_raw'].dt.strftime('%Y-%m-%d')
price4.drop('date_raw', axis=1).to_excel(f'codes/A.sp500_implied_correlation_daily/sp500_mom_rev.xlsx', index=False)

