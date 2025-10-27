def _exit(down, exit):
    # Action Date
    meta = down[down['rn'] == down['rn_trigger']][['Date', 'rn', 'close']]
    meta.columns = ['trade-in_date', 'trade-in_day', 'trade-in_price']

    # Exit: best return
    exit_best = down.join(
        summary[['highest', 'highest_rn', 'highest_date']], how='left')
    exit_best = exit_best[exit_best['rn'] == exit_best['highest_rn']].copy()
    # Exit: up 20%
    cond = (
        (down['cum_ret'] > exit['up'][0]) |
        (down['cum_ret'] < exit['up'][1]) |
        (down['rn'] > exit['up'][2])
    )
    exit_up20pct = (
        down[cond]
        .groupby('ticker')
        .first()
    )
    # Exit: pull back by 20%
    down['max_close'] = down['close'].cummax()
    down['pull_pack'] = down['close'] / down['max_close'] - 1
    cond = (
        (down['pull_pack'] < exit['pull.back'][0]) |
        (down['rn'] > exit['pull.back'][1])
    )
    exit_fallback20pct = (
        down[cond]
        .groupby('ticker')
        .first()
    )
    # Combine exit strategies
    cols = ['Date', 'rn', 'close', 'cum_ret']
    down2 = meta.join(
        exit_best[cols]).join(
        exit_up20pct[cols], lsuffix='_best', rsuffix='_up20pct').join(
        exit_fallback20pct[cols].add_suffix('_fallback20pct')
    )
    for col in down2.select_dtypes(include=['datetime64[ns]']):
        down2[col] = down2[col].dt.strftime('%Y-%m-%d')

    return down2