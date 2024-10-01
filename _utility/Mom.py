def all_returns(base=base):
    df = base.copy()
    df['m0_m1'] = df.groupby('ticker')['close'].pct_change(1,fill_method=None)
    df['m0_m3'] = df.groupby('ticker')['close'].pct_change(3,fill_method=None)
    df['m0_m6'] = df.groupby('ticker')['close'].pct_change(6,fill_method=None)
    df['m0_m12'] = df.groupby('ticker')['close'].pct_change(12,fill_method=None)
    df['m0_m24'] = df.groupby('ticker')['close'].pct_change(24,fill_method=None)
    df['m6_m12'] = df.groupby('ticker')['m0_m6'].shift(6)
    df['m1_m2'] = df.groupby('ticker')['m0_m1'].shift(1)
    df['m1_m11_avg'] = df.groupby('ticker')['m1_m2'].transform(lambda x: x.rolling(10, 6).mean())
    df['m23_m24'] = df.groupby('ticker')['m0_m1'].shift(23)
    df['m35_m36'] = df.groupby('ticker')['m0_m1'].shift(35)
    df['m47_m48'] = df.groupby('ticker')['m0_m1'].shift(47)
    df['m59_m60'] = df.groupby('ticker')['m0_m1'].shift(59)
    df['m71_m72'] = df.groupby('ticker')['m0_m1'].shift(71)
    df['m83_m84'] = df.groupby('ticker')['m0_m1'].shift(83)
    df['m95_m96'] = df.groupby('ticker')['m0_m1'].shift(95)
    df['m107_m108'] = df.groupby('ticker')['m0_m1'].shift(107)
    df['m119_m120'] = df.groupby('ticker')['m0_m1'].shift(119)
    df['season_y02_y05'] = df[['m23_m24', 'm35_m36', 'm47_m48', 'm59_m60']].mean(axis=1)
    df['season_y06_y10'] = df[['m71_m72', 'm83_m84', 'm95_m96', 'm107_m108', 'm119_m120']].mean(axis=1)

    df['age'] = df.groupby('ticker')['close'].cumcount()
    df['vol_6m'] = df.groupby('ticker')['volume'].transform(lambda x: x.rolling(6, 5).mean())

    col0 = ['ticker', 'date_ym', 'close','m0_m1','m0_m3','m0_m6','m0_m12','m0_m24','m6_m12','m1_m11_avg']
    col1 = ['season_y02_y05','season_y06_y10']
    col2 = ['age','vol_6m']
    cols = col0 + col1 + col2
    return df[cols]
