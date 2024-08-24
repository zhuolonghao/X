from fredapi import Fred

fred = Fred(api_key='beecf55d03e9987f682fa20b249f9975')

def _ue(series='UNRATE', econ_nm='Unemployment', lag_adjustment=1):
    base = fred.get_series(series, observation_start='2010-01-01').reset_index()
    base.columns = ['date', series]
    base[f"{series}_MA"] = base[series].rolling(window=3).mean()
    base[f"{series}_MA_min"] = base[f"{series}_MA"].rolling(window=12).min()
    base[f"sahm_rule"] = base[f"{series}_MA"] - base[f"{series}_MA_min"]
    base[f'threshold'] = 0.5
    base[f"{econ_nm}"] = f"Benign"
    base.loc[ (base[f"sahm_rule"] > base['threshold']), f"{econ_nm}"] = f"Adverse"
    base['date_adjusted'] = base['date'] + pd.DateOffset(months=lag_adjustment)
    return base[['date', 'date_adjusted', 'threshold', f'{econ_nm}']]

# RECPROUSM156N is not good b/c it's constantly revised, which is not the case for JHGDPBRINDX
def _gdp(series='JHGDPBRINDX', econ_nm='GDP', lag_adjustment=7):
    base = fred.get_series(series, observation_start='2010-01-01')
    base = base.resample('MS').ffill().reset_index()
    base.columns = ['date', series]
    base['threshold'] = 67
    base[f"{econ_nm}"] = f"Benign"
    base.loc[(base[series] > base['threshold']), f"{econ_nm}"] = f"Adverse"
    base['date_adjusted'] = base['date'] + pd.DateOffset(months=lag_adjustment)
    return base[['date', 'date_adjusted', 'threshold', f'{econ_nm}']]

def _inflation(series='UMCSENT', econ_nm='Inflation', freq='m', agg='eop', lag_adjustment=2):
    base = fred.get_series(series, observation_start='2010-01-01').reset_index()
    base.columns = ['date', series]
    base[f"{series}_MA"] = base[series].rolling(window=3).mean()
    base[f"{series}_MA_min"] = base[f"{series}_MA"].rolling(window=12).min()
    base[f"sahm_rule"] = base[f"{series}_MA"] - base[f"{series}_MA_min"]
    base[f'threshold'] = base[f"sahm_rule"].median()
    base[f"{econ_nm}"] = f"Benign"
    base.loc[ (base[f"sahm_rule"] < base['threshold']), f"{econ_nm}"] = f"Adverse"
    base['date_adjusted'] = base['date'] + pd.DateOffset(months=lag_adjustment)
    return base[['date', 'date_adjusted', 'threshold', f'{econ_nm}']]


def _T10Y2Y(series='T10Y2Y', econ_nm='T10Y2Y', lag_adjustment=1):
    base = fred.get_series(series, observation_start='2010-01-01', frequency='m', aggregation_method='eop').reset_index()
    base.columns = ['date', series]
    base[f'threshold'] = 0
    base[f"{econ_nm}"] = f"Benign"
    base.loc[ (base[series] >= base['threshold']), f"{econ_nm}"] = f"Adverse"
    base['date_adjusted'] = base['date'] + pd.DateOffset(months=lag_adjustment)
    return base[['date', 'date_adjusted', 'threshold', f'{econ_nm}']]



