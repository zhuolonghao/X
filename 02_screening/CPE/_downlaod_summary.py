def _summary(download):

    # List of tickers (either as a space-separated string or a list)
    tickers_dict = []
    tickers_dict2 = []
    for b in BQR:
        if b[0] not in tickers_dict:
            tickers_dict.append(b[0])
            for bb in b[1]:
                tickers_dict2.append({'ticker': b[0], 'start_date': bb[0],
                                      'ticker_alt': b[0] + '.' + bb[1] + '.' + bb[0][:4] + bb[0][5:7]})
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
        close.set_index(['Date', 'ticker']) \
            .join(vol.set_index(['Date', 'ticker'])) \
            .to_excel('BQR_vol.xlsx')

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

    return [close_final, summary]

close_final, summary=_summary(download=False)

close_final = close_final.sort_values(['ticker', 'Date'])
close_final['Trailing.20.vol'] = close_final.groupby('ticker')['Volume']\
    .transform(lambda x: x.rolling(window=20, min_periods=20).mean())
close_final['Trailing.50.vol'] = close_final.groupby('ticker')['Volume']\
    .transform(lambda x: x.rolling(window=50, min_periods=50).mean())
close_final = close_final[close_final['rn']>=0]
close_final['ret'] = close_final.groupby('ticker')['close'].pct_change(fill_method=None)
close_final['cum_ret_d0'] = close_final.groupby('ticker')['ret']\
    .transform(lambda x: (1 + x).cumprod() - 1)

close_final = close_final\
        .drop(columns=['rn_0', 'year', 'year2', 'month', 'month2'])\
        .rename(columns={'start_date': 'CAR_date', 'start_date2': 'Price_date'})