import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import MonthEnd


# List of tickers (either as a space-separated string or a list)
tickers_dict = {
    'FLWS': '2025-06-01',
    'SBGI': '2025-06-01',  # cannot verify if it's 887 as of 2nd analysis on 8.9.2025 due to legal_os = 0
    'GT': '2025-05-01',
    'SNAP': '2025-04-01',
    'MATV': '2025-04-01',
    'SSP': '2025-04-01',
    'ONEW': '2025-02-01',
    'SMTC': '2025-01-01',     # 'SMTC': '2023-08-01',
    'CATO': '2024-11-01',  # cannot verify if it's 887 as of 2nd analysis on 8.9.2025
    'APPS': '2024-09-01',
    'MODV': '2024-09-01',
    'TTEC': '2024-08-01',
    'MEI': '2024-07-01',
    'DTI': '2024-07-01',
    #    'HAIN': '2023-09-01', # it was 887 first, and then became 888
#    'CRS': '2022-06-01',
#    'GLT': '2022-05-01',   # this is interesting, MM-corp to CMLBKNG to MM-Corp # MERGED WITH NYSE: BERRY
#    'MAGM': '2022-05-01',  # GLT was replaced with MAGM
#    'SMG': '2023-07-01',
#    'NWL': '2024-02-01',
#    'CMP': '2024-03-01',
    #'SNAP': '2025-05-01', #cannot verify if it's 887 as of 2nd analysis on 8.9.2025
    #'OSCR': '2022-06-01', #cannot verify if it's 887 as of 2nd analysis on 8.9.2025
#    'SPHR': '2022-06-01',
    #'DAL': '2022-02-01',
    #'RIG': '2023-11-01', #cannot verify if it's 887 as of 2nd analysis on 8.9.2025
    #'CNK': '2023-06-01', #cannot verify if it's 887 as of 2nd analysis on 8.9.2025
    #'CRNC': '2023-01-01', #cannot verify if it's 887 as of 2nd analysis on 8.9.2025
    #'MYGN': '2022-10-01', #cannot verify if it's 887 as of 2nd analysis on 8.9.2025
    #'LYLT': '2022-08-01', # delisted
    #'HLLY': '2023-05-01', #cannot verify if it's 887 as of 2nd analysis on 8.9.2025
    #'BA': '2022-02-01', #cannot verify if it's 887 as of 2nd analysis on 8.9.2025
#    'CNSL': '2023-11-01', # delisted
#    'HBIO': '2023-01-01',
#    'LTH': '2021-12-01',
#    'MG': '2021-08-01',
#    'MMLP': '2021-07-01',
#    'NFYEF': '2023-01-01',
#    'PDS': '2021-08-01',
#    'PRPL': '2022-04-01'
}




# Download historical data
data = yf.download(list(tickers_dict.keys()), start="2020-01-01")

close = data['Close'].reset_index()
close = pd.melt(close, id_vars='Date', var_name='ticker', value_name='close')
tickers = pd.DataFrame.from_dict(tickers_dict, orient='index').reset_index()
tickers.columns = ['ticker', 'start_date']
tickers['start_date2'] = pd.to_datetime(tickers['start_date']) + pd.DateOffset(months=1) + pd.Timedelta(days=7)
close = pd.merge(close, tickers, on='ticker', how='left')


rows = close['start_date2'] <= close['Date']
close2 = close[rows].copy()
close2['rn'] = close2.groupby('ticker').cumcount()

rows = close['start_date2'] >= close['Date']
close3 = close[rows].sort_values(['ticker', 'Date'], ascending=False).copy()
close3['rn'] = close3.groupby('ticker').cumcount()
close3['rn'] = - close3['rn']

close_final = pd.concat([close2, close3]).drop_duplicates()
heads = close_final.columns

#####################
tickers_dict2 = {
    'FLWS': ['GRPN', 'PETS'],# about gift, highly seasonal
    'SBGI': ['NXST', 'GTN', 'TGNA'],  # TV network and local stations
    'GT': ['SPY', 'QQQ'], #designs, manufactures, distributes, and sells tires
    'MATV': ['AVY', 'MMM'],# specialty materials "films, nets, nonwovens, tapes/adhesives, coatings and release liners"
    'SSP': ['NXST', 'SBGI', 'GTN'],  # TV network and local stations
    'SNAP': ['META','PINS'],
    'CATO': ['CTRN', 'ROST', 'TJX'],  #.S. value-priced specialty apparel retailer
    'DTI': ['INVX', 'NOV', 'WFRD'], #field-services company that designs, manufactures, rents, and services downhole drilling tools
    'ONEW': ['HZO', 'GORV'],  # sells new & pre‑owned boats
    'APPS': ['U', 'APP'],#mobile ad tech (pre-load softwares on device + ad-tech stack to monetize app)
#   'HAIN': ['K', 'CPB'],#health & wellness packaged‑foods company
#    'CRS': ['ATI', 'AA'],#specialty alloys (nickel, cobalt, stainless, titanium), AA is its customers
#    'SMG': ['CENT', 'SPB', 'HYFM'],#consumer lawn & garden products, highly seasonal
    'MEI': ['TEL', 'APH', 'APTV'],#mechatronic products for end markets like auto, and data centers
#    'NWL': ['CLX', 'COTY', 'CL'],#consumer goods manufacturer, marketer, and distributor
#    'CMP': ['IPI'],#salt + plant nutriton
#    'SPHR': ['SPY'],#live entertainment and media company, no direct competitors
    'TTEC': ['CNXC', 'TASK'],#customer‑experience (CX) technology and services company.
    'MODV': ['ADUS', 'BTSG'],# focused on the “last mile” of care for government and managed‑care members
    'SMTC': ['TXN', 'ADI', 'SLAB'],#a fabless chipmaker + IoT company
#    'HBIO': ['BIO', 'BRKR', 'WAT'],#develops and sells life‑science research instruments and related software/consumables
#    'LTH': ['PLNT', 'XPOF'],#Operates premium, resort‑style “athletic country clubs”
#    'MG': ['TISI'],#protect critical infrastructure in energy, power, aerospace/defense, and civil assets
#    'MMLP': ['GEL', 'NS', 'GLP'],#Gulf Coast–focused, specialty midstream for NGL
#    'NFYEF': ['GP'],#buses and motorcoaches
#    'PDS': ['PTEN', 'NBR', 'HP'],# onshore contract drilling for oil & gas
#    'PRPL': ['SNBR'],#manufactures mattresses plus pillows, bedding, and bases
}

_dict = {}
for x, peer in tickers_dict2.items():
    close_final_ind = close_final[close_final['ticker']==x]
    data2 = yf.download(peer, start="2020-01-01")
    benchmark = data2['Close'].reset_index()
    close_final_ind = pd.merge(close_final_ind, benchmark, on='Date', how='left')
    close_final_ind_final = close_final_ind[heads]
    for p in peer:
        tmp = close_final_ind.copy()
        tmp['close'] = tmp[p]
        tmp['ticker'] = tmp['ticker'].transform(lambda x: f"{x}_{p}")
        tmp = tmp[heads]
        close_final_ind_final = pd.concat([close_final_ind_final, tmp])
    _dict[x] = close_final_ind_final

output = pd.concat(_dict.values())
output.to_excel('CPE_887.xlsx')