from fredapi import Fred
import pandas as pd
from datetime import datetime

def convert_to_quarter(date_str):
    # Parse the date
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    # Determine the quarter
    quarter = (date_obj.month - 1) // 3 + 1
    # Construct the new date format
    quarter_date = f"{date_obj.year}-{(quarter - 1) * 3 + 1:02d}-01"
    return quarter_date

cycles = ['1990-01-03', '1990-07-12', '1997-10-08', '1998-07-20', '1999-07-19', '2000-03-27', '2000-03-27',
          '2000-09-05', '2007-10-10', '2015-07-21', '2018-01-26', '2018-09-21', '2020-02-20', '2022-01-04'
          ]
cycles_dict = {}
for c in cycles:
    quarter_date = convert_to_quarter(c)
    quarterly_dates = pd.date_range(end=quarter_date, periods=21, freq='QS')
    cycles_dict[c] = quarterly_dates
cycles = {'1990_Oil_Shock': '1990-07-01',  '2000_Tech_bubble': '2001-03-01',
          '2008_GFC': '2007-12-01', '2020_Covid': '2020-02-01'}
for k, c in cycles.items():
    quarter_date = convert_to_quarter(c)
    quarterly_dates = pd.date_range(end=quarter_date, periods=21, freq='QS')
    cycles_dict[k] = quarterly_dates


API_KEY = 'f8b03deb401f42867b7ffe3edef02db2'
# Initialize FRED API
fred = Fred(api_key=API_KEY)


vars_list = {
    'Real GDP':
        ['GDPC1', 'pc1'],
    'Labor Productivity':
        ['OUTNFB', 'pc1'],
    'GDP Component: Personal Consumption':
        ['DPCERY2Q224SBEA', 'lin'],
    'GDP Component: Private Investment':
        ['A008RY2Q224SBEA', 'lin'],
    'GDP Component: Govt Spending':
        ['A822RY2Q224SBEA', 'lin'],
    'Consumer: mortgage 30DPD':
        ['DRSFRMACBS', 'lin'],
    'Consumer: creidt card 30DPD':
        ['DRCCLACBS', 'lin'],
    'Consumer: other credits 30DPD':
        ['DROCLACBS', 'lin'],
    'Consumer: Real disposable income':
        ['DSPIC96', 'pc1'],
    'Consumer: saving rate':
        ['PSAVERT', 'lin'],
    'Manufacturer: industrial production':
        ['INDPRO', 'pc1'],
    'Labor Market: unemployment rate':
        ['UNRATE', 'lin'],
    'Labor Market: wage growth':
        ['AHETPI', 'pc1'],
    'Labor Market: job openings':
        ['JTSJOL', 'lin'],
    'Price: Headline CPI':
        ['CPIAUCSL', 'pc1'],
    'Price: Core CPI':
        ['CPILFESL', 'pc1'],
    'Price: Headline PCE':
        ['PCEPI', 'pc1'],
    'Price: Core PCE':
        ['PCEPILFE', 'pc1'],
    'Price: Oil Price':
        ['DCOILWTICO', 'lin'],
    'Price: HPI':
        ['CSUSHPISA', 'pc1'],
    'Price: UST_10Y_minus_2Y':
        ['T10Y2Y', 'lin'],
    'Price: Baa_minus_FFT':
        ['BAAFF', 'lin'],
    'Price: FFT':
        ['FEDFUNDS', 'lin'],
}

dfs = {}
for k, v in vars_list.items():
    data = fred.get_series(v[0], units=v[1], frequency='q', aggregation_method='avg')
    dfs[k] = data
df = pd.concat(dfs.values(), axis=1)
df.columns = dfs.keys()

dfs = {}
for c,dates in cycles_dict.items():
    rows = df.index.isin(dates)
    tmp = df[rows].copy()
    nrows =tmp.shape[0]
    tmp['relative_dt'] = [x+1 - nrows for x in range(nrows)]
    tmp['cycle'] = c
    dfs[c] = tmp

tmp =df.tail(20).copy().dropna(axis=0)
nrows = tmp.shape[0]
tmp['relative_dt'] = [x - nrows for x in range(nrows)]
tmp['cycle'] = 'NOW'
dfs['now'] = tmp

output = pd.concat(dfs.values(),axis=0)
output = output.reset_index()

output2 = pd.melt(output,
        id_vars=['index', 'relative_dt', 'cycle'],
        var_name="variable",
        value_name="Value")
output2.to_excel('business_cycle_checks.xlsx')