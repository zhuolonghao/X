# Let's download key information of companies in investable universe
import pandas as pd
from functools import reduce

date_fin = 202405

###########################################################
# References
###########################################################
ref = pd.read_excel("./_data/_total_gics_style.xlsx")
tickers = [str(x).replace(".", "-").replace("/", "-") for x in ref['ticker']]
ref = ref.rename(columns={'sector': 'gics'})

###########################################################
# Download prices
###########################################################
exec(open('_utility/download_tickers_from_yfinance3.py').read())
#df = download(tickers=tickers, data_type="price", period="10y", interval="1mo")
#df.to_parquet(r'./codes/C.value_finder_monthly/price_monthly.parquet', compression='zstd', index=False)
#print('Completed: Monthly price')
df = download(tickers=tickers, data_type="price", period="1y", interval="1d")
df.to_parquet(r'./codes/C.value_finder_monthly/price_daily.parquet', compression='zstd', index=False)
print('Completed: Daily price')
df = download(tickers=tickers, data_type="finQ")
df.to_parquet(r'./codes/C.value_finder_monthly/finQ.parquet', compression='zstd', index=False)
print('Completed: Financials, Quarterly')


###########################################################
# Price-based factors
###########################################################
base = pd.read_parquet('./codes/C.value_finder_monthly/price_daily.parquet')
base.columns = [x.lower() for x in base.columns]
exec(open('_utility/Mom_daily.py').read())
mom = all_returns(base=base)
mom = mom.sort_values(['ticker', 'date_ym']).groupby('ticker').tail(1)
rows = mom['date_ym'] >= str(date_fin)
mom = mom[rows].drop(columns='date_ym')


###########################################################
# Valuation
###########################################################
finQ = pd.read_parquet(r'./codes/C.value_finder_monthly/finQ.parquet')
finQ.columns = [x.lower() for x in finQ.columns]
finQ = finQ.sort_values(['ticker', 'date_ym'])
finQ['cash'] = finQ[['cashandcashequivalents', 'cashcashequivalentsandshortterminvestments']].max(axis=1)
finQ['tax'] = finQ[['totaltaxpayable', 'incometaxpayable']].max(axis=1)
finQ['debt_current'] = finQ[['currentdebtandcapitalleaseobligation', 'currentdebt']].max(axis=1)
# missing values in these variables are not systematic
for v in ['tax', 'reconcileddepreciation']:
    finQ[v] = finQ[v].fillna(0)
for v in ['tax', 'currentassets', 'cash', 'currentliabilities', 'debt_current']:
    finQ[f"{v}_chg"] = finQ[v] - finQ.groupby('ticker')[v].shift(4)
finQ['accruals_lvl'] = \
    (finQ['currentassets_chg'] - finQ['cash_chg']) \
    - (finQ['currentliabilities_chg'] - finQ['debt_current_chg'] - finQ['tax_chg'])
finQ['accruals'] = 100*finQ['accruals_lvl'] / finQ['totalassets']
finQ['accruals_after_depr_lvl'] = \
    (finQ['currentassets_chg'] - finQ['cash_chg']) \
    - (finQ['currentliabilities_chg'] - finQ['debt_current_chg'] - finQ['tax_chg']) \
    - finQ['reconcileddepreciation']
finQ['accruals_after_depr'] = 100*finQ['accruals_after_depr_lvl'] / finQ['totalassets']
cols = ['ticker', 'date_ym','accruals', 'accruals_after_depr']
rows = finQ['date_ym'] >= str(date_fin)
finQ = finQ[cols][rows].groupby('ticker').tail(1)


others = pd.read_parquet('./codes/B.short_squeeze_biweekly/others.parquet')
others.columns = [x.lower() for x in others.columns]
others['shortpercentoffloat'] = others['sharesshort'] / (others['sharesoutstanding'])
cols = ['ticker', 'longname', 'exchange', 'sector', 'industry',
        'pricetobook', 'sharesoutstanding']
others = others[cols]

###########################################################
# Merge
###########################################################
_dfs = [ref, mom, others, finQ]
output = reduce(lambda left, right:
                pd.merge(left, right, on=['ticker'], how='inner'), _dfs)
output.to_excel('./codes/C.value_finder_monthly/value_finder.xlsx', index=False)

###########################################################
# Merge: Industry, Size/Style
###########################################################
_dfs = [ref, mom]
output = reduce(lambda left, right:
                pd.merge(left, right, on=['ticker'], how='inner'), _dfs)
output = output.rename(columns={'% of fund*': 'total'})
cols = [
    'mega_growth', 'mega_value', 'large_growth', 'large_value',
    'mid_growth', 'mid_value','small_growth', 'small_value']
metrics = ['m0_m1', 'm0_m3', 'm0_m6', 'm6_m12']
metrics_vw = [f'{x}_vw' for x in metrics]
output[metrics_vw] = output[metrics]
output[cols+metrics+metrics_vw] = output[cols+metrics+metrics_vw].astype(float)

_dfs = {}
for ss in cols:
    rows = (output[ss] >= 0)
    tmp = output[rows].copy()
    ew = pd.DataFrame([tmp[metrics].mean()])
    vw = pd.DataFrame([(tmp[metrics_vw].multiply(tmp[ss], axis=0)/100).sum()])
    _dfs[ss] = pd.concat([ew, vw], axis=1).assign(
        group='size_style', group_key=ss, group_members=sum(tmp['m0_m1'].notna()))
for sector in output.gics.unique():
    rows = (output.gics.eq(sector))
    tmp = output[rows].copy()
    tmp['wgts'] = tmp['total'] / tmp['total'].sum()
    ew = pd.DataFrame([tmp[metrics].mean()])
    vw = pd.DataFrame([(tmp[metrics_vw].multiply(tmp['wgts'], axis=0) / 100).sum()])
    _dfs[sector] = pd.concat([ew, vw], axis=1).assign(
        group='industry', group_key=sector, group_members=sum(tmp['m0_m1'].notna()))
output2 = pd.concat(_dfs.values())
output2.to_excel('./codes/C.value_finder_monthly/value_finder_mom.xlsx', index=False)
