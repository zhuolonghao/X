def _bin(x,q):
    """
    :param x: pd.series that contains anomaly values
    :param q: integer that indicates the nummber of bins
    :return: categorical labels, from low to high
    """
    x1 = x.rank(ascending=True, method='dense')
    _max = x1.max()
    _binInterval = np.linspace(0, _max, num=q+1)
    _binLabel = np.linspace(1, 10, num=q)
    return pd.cut(x1, bins=_binInterval, labels=_binLabel)
