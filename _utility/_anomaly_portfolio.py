_size_style = ['mega_growth', 'mega_value', 'large_growth', 'large_value', 'mid_growth', 'mid_value', 'small_growth', 'small_value']
_dimension = ['ticker', 'holdings name', 'exchange', 'market', 'sector', 'industry group', 'industry',  'date_ym'] + _size_style
_anomaly = [
    'MomRev', 'MomFirmAge', 'MomVol', 'MomInt', 'MomResiduals6m',
    'MomResiduals12m', 'Mom_m02_m11', 'Mom_m02_m11_pos', 'Season_0205',
    'OffSeason_0205', 'Season_0610', 'OffSeason_0610', 'Season_1115',
    'OffSeason_1115', 'Season_1620', 'OffSeason_1620', 'STreversal',
    'MRreversal', 'LRreversal', 'MomTurnover', 'BM_q', 'EBM_q',
    'AccrualsBM_q', 'EntMult_q', 'CF_q', 'cfp_q', 'GPlag_q',
    'OperProfRDLagAT_q', 'CBOperProfLagAT_q', 'CBOperProfLagAT_alt_q',
    'ChInv_q', 'Investment_q', 'DelDRC_q', 'cash_q', 'tang_q',
    'ShortInterest_q', 'IO_ShortInterest_q', 'Recomm_ShortInterest_q',
    'eps2p_q', 'sale2p_q', 'free_cfp_q', 'roa_q', 'roe_q',
    'Mom_1m', 'Mom_3m', 'Mom_6m', 'Mom_12m', 'Mom_m02m11']

_anomalies = {# this list is based on 1) the economic meaning, and 2) clustering analysis in 01.Assessment
    'momentum': ['Mom_1m', 'Mom_3m', 'Mom_6m', 'Mom_12m', 'Mom_m02m11'],
    'seasonality': ['Season_0205', 'OffSeason_0205', 'Season_0610', 'OffSeason_0610', 'Season_1115', 'OffSeason_1115',
                    'Season_1620', 'OffSeason_1620'],
    'reversal': ['STreversal', 'MRreversal', 'LRreversal'],
    'valuation': ['BM_q', 'eps2p_q', 'sale2p_q', 'EntMult_q', 'cfp_q', 'free_cfp_q'],
    'profitability': ['GPlag_q', 'OperProfRDLagAT_q', 'CBOperProfLagAT_q', 'CBOperProfLagAT_alt_q', 'roa_q', 'roe_q'],
    '13F': ['ShortInterest_q', 'IO_ShortInterest_q', 'Recomm_ShortInterest_q'],
    'NYSE_AMEX': ['Mom_m02_m11', 'Mom_m02_m11_pos', 'MomFirmAge', 'MomVol'],
    'Manufacturers': ['cash_q', 'tang_q'],
    'nonFin': [ 'ChInv_q', 'Investment_q', 'DelDRC_q', 'EBM_q', 'AccrualsBM_q'],
    '6mMom_StMom': ['MomRev', 'MomInt', 'MomTurnover'],
}
_portfolios = {
    'MomRev_StMom': {'MomRev': lambda x: x==True, 'MomTurnover': lambda x: x==True},
    'MomInt_StMom': {'MomInt': lambda x: x==True, 'MomTurnover': lambda x: x==True},
    'high_BM_Low_Accruals': {'AccrualsBM_q': lambda x: x==True},
    'Mom_in_NYSE': {'NYSE_AMEX': lambda x: x>=3/4},
    'Mfg_in_focus': {'Manufacturers': lambda x: x==2/2},
    'Short_Squeeze': {'IO_ShortInterest_q': lambda x: x==True},
    'wgt3_mom1': {'selected, wgt': lambda x: x>3, '6mMom_StMom': lambda x: x>=2/3},
    'wgt3_val1': {'selected, wgt': lambda x: x>3, 'valuation': lambda x: x>=4/6},
    'wgt3_prof1': {'selected, wgt': lambda x: x>3, 'profitability': lambda x: x>=4/6},
}

_etf_s2 = {
    'MGK': 'MG', 'VUG': 'LG','VOT': 'MidG',
    'MGV': 'MV', 'VTV': 'LV','VOE': 'MidV',
    'VBK': 'SG', 'VBR': 'SV','VOO': 'SPY'
}
_etf_s = {
    'XLE': 'Energy',
    'XLB': 'Material',
    'XLU': 'Utility',

    'FDIS': 'Consumer Staple',
    'FSTA': 'Consumer Discretionary',
    'FIDU': 'Industrial',

    'XLC': 'Communication',
    'XLK': 'I.T.',
    'XLV': 'Health Care',

    'XLF': 'Financials',
    'XLRE': 'Real Estate',

}