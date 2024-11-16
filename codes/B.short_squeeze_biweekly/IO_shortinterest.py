# Let's download key information of companies in investable universe
import webbrowser as web
web.open('https://www.finra.org/finra-data/browse-catalog/equity-short-interest/data')
# download the most recent short interest data
# by NYSE

import pandas as pd

exec(open('_utility/download_tickers_from_yfinance3.py').read())
ref = pd.read_excel("./_data/_total_gics_style.xlsx")
tickers = [str(x).replace(".", "-").replace("/", "-") for x in ref['ticker']]
_dfs = [_download_others.remote(t) for t in tickers]
data = pd.concat(ray.get(_dfs), axis=0, ignore_index=True)
data = data.replace('Infinity', None)
data.to_parquet(r'./codes/B.short_squeeze_biweekly/others.parquet', compression='zstd', index=False)
print('Completed: other information')
data.columns = [x.lower() for x in data.columns]
cols = ['ticker', 'longname', 'exchange', 'sector', 'industry', 'heldpercentinstitutions', 'floatshares']
data = data[cols]
data = data.rename(columns={'floatshares': 'sharesoutstanding'})

# short_interest = pd.concat([
#     pd.read_csv(r"C:/Users/longh/Downloads/equityshortinterest.zip", compression='zip'),
#     pd.read_csv(r"C:/Users/longh/Downloads/equityshortinterest (1).zip", compression='zip')
#     ])
short_interest = pd.read_csv(r"C:/Users/longh/Downloads/equityshortinterest.zip", compression='zip')
short_interest['ticker'] = short_interest['Symbol'].transform(lambda x: x.replace(".", "-").replace("/", "-"))
short_interest['sharesshort'] = short_interest['Current Short']
short_interest['shareshort_prev'] = short_interest['Previous Short']
cols = ['ticker', 'Market', 'Settlement Date', 'sharesshort', 'shareshort_prev']
short_interest = short_interest[cols]

data2 = pd.merge(data, short_interest, on=['ticker'], how='left')
data2['short%outs'] = data2['sharesshort'] / data2['sharesoutstanding']
data2['short%outs_prev'] = data2['shareshort_prev'] / data2['sharesoutstanding']
data2.to_excel(r'./codes/B.short_squeeze_biweekly/IO_short.xlsx', index=False)

import os
os.remove(r"C:/Users/longh/Downloads/equityshortinterest.zip")
#os.remove(r"C:/Users/longh/Downloads/equityshortinterest (1).zip")