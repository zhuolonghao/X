def all_returns(base=base):
    df = base.copy()
    df['m0_m1'] = df.groupby('ticker')['close'].pct_change(20,fill_method=None)
    df['m0_m3'] = df.groupby('ticker')['close'].pct_change(65,fill_method=None)
    df['m0_m6'] = df.groupby('ticker')['close'].pct_change(125,fill_method=None)
    df['m0_m12'] = df.groupby('ticker')['close'].pct_change(250,fill_method=None)
    df['m6_m12'] = df.groupby('ticker')['m0_m6'].shift(125)
    df['m0_m24'] = -999
    df['m1_m11_avg'] = -999
    df['season_y02_y05'] = -999
    df['season_y06_y10'] = -999

    df['age'] = -999
    df['vol_6m'] = -999

    col0 = ['ticker', 'date_ym', 'close','m0_m1','m0_m3','m0_m6','m0_m12','m0_m24','m6_m12','m1_m11_avg']
    col1 = ['season_y02_y05','season_y06_y10']
    col2 = ['age','vol_6m']
    cols = col0 + col1 + col2
    return df[cols]
