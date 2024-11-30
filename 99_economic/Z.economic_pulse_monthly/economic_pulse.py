import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import beaapi
from functools import reduce
import seaborn as sns
sns.set(style='ticks')
from matplotlib.backends.backend_pdf import PdfPages

years = ['2020', '2021', '2022', '2023', '2024']

lvl1 = ['DPCERA', 'DGDSRA', 'DDURRA', 'DSERRA']
lvl2 = lvl1 + ['DMOTRA', 'DFDHRA', 'DREQRA', 'DODGRA', 'DFXARA', 'DCLORA', 'DGOERA', 'DONGRA', 'DHCERA', 'DHUTRA', 'DHLCRA', 'DTRSRA', 'DRCARA', 'DFSARA', 'DIFSRA', 'DOTSRA']
lvl3 = ['DPCERA', 'DGDSRA', 'DDURRA', 'DNMVRA', 'DNPVRA', 'DMVPRA', 'DFFFRA', 'DAPPRA', 'DUTERA', 'DTOORA', 'DVAPRA', 'DSPGRA', 'DWHLRA', 'DRBKRA', 'DMSCRA', 'DJRYRA', 'DTAERA', 'DEBKRA', 'DLUGRA', 'DTCERA', 'DNDGRA', 'DTFDRA', 'DAOPRA', 'DFFDRA', 'DGARRA', 'DWGCRA', 'DMBCRA', 'DCICRA', 'DOCCRA', 'DMFLRA', 'DFULRA', 'DPHMRA', 'DREIRA', 'DHOURA', 'DOPCRA', 'DTOBRA', 'DNEWRA', 'DSERRA', 'DHSGRA', 'DTENRA', 'DOWNRA', 'DFARRA', 'DGRHRA', 'DUTLRA', 'DWRSRA', 'DELGRA', 'DELCRA', 'DGHERA', 'DOUTRA', 'DPHYRA', 'DDENRA', 'DPMSRA', 'DHPNRA', 'DHSPRA', 'DNRSRA', 'DMVSRA', 'DVMRRA', 'DOVSRA', 'DPUBRA', 'DGRDRA', 'DAITRA', 'DWATRA', 'DRLSRA', 'DAVPRA', 'DGAMRA', 'DOTRRA', 'DFSERA', 'DPMBRA', 'DFOORA', 'DACCRA', 'DFNLRA', 'DIMPRA', 'DOFIRA', 'DINSRA', 'DLIFRA', 'DFINRA', 'DHINRA', 'DTINRA', 'DCOMRA', 'DTCSRA', 'DPSSRA', 'DINTRA', 'DTEDRA', 'DHEDRA', 'DNEHRA', 'DVEDRA', 'DPRSRA', 'DPERRA', 'DSOCRA', 'DHHMRA', 'DFTRRA']

beakey = '0FAD9DAD-B778-42E9-BA0E-454F0DE7BC7D'
_real = {}
_price = {}
_pce = {}
for y in years:
    _real[y] = beaapi.get_data(beakey, datasetname='NIPA', TableName='T20803', Frequency='M', Year=y)
    _price[y] = beaapi.get_data(beakey, datasetname='NIPA', TableName='T20804', Frequency='M', Year=y)
    _pce[y] = beaapi.get_data(beakey, datasetname='NIPA', TableName='T20805', Frequency='M', Year=y)


real = pd.concat(_real.values(), axis=0).sort_values(['SeriesCode', 'TimePeriod'])
price = pd.concat(_price.values(), axis=0).sort_values(['SeriesCode', 'TimePeriod'])
pce = pd.concat(_pce.values(), axis=0).sort_values(['SeriesCode', 'TimePeriod'])

for name, lag in {'YoY': 12}.items():
    real['pct_chg'] = real.groupby(['SeriesCode'])['DataValue'].pct_change(lag)
    rows = real['SeriesCode'].isin(lvl2)
    df = real[rows].copy()
    zero = pd.DataFrame({'TimePeriod': df['TimePeriod'].unique(), 'SeriesCode': '------------',
                         'LineDescription': '----------', 'pct_chg': 0})
    df = pd.concat([df, zero], axis=0)
    df['LineDescription'] = df['LineDescription'].str[:20]
    df['rank'] = df.groupby('TimePeriod')['pct_chg'].transform(lambda x: x.rank())
    if lag == 12:
        df.to_excel('pce_real.xlsx', index=False)


lvl2 = [ x[:-1] + 'C' for x in lvl2]
for name, lag in { 'YoY': 12}.items():
    pce['pct_chg'] = pce.groupby(['SeriesCode'])['DataValue'].pct_change(lag)
    rows = pce['SeriesCode'].isin(lvl2)
    df = pce[rows].copy()
    zero = pd.DataFrame({'TimePeriod': df['TimePeriod'].unique(), 'SeriesCode': '------------',
                         'LineDescription': '----------', 'pct_chg': 0})
    df = pd.concat([df, zero], axis=0)
    df['LineDescription'] = df['LineDescription'].str[:20]
    df['rank'] = df.groupby('TimePeriod')['pct_chg'].transform(lambda x: x.rank())
    if lag == 12:
        df.to_excel('pce.xlsx', index=False)



price['pct_chg'] = price.groupby(['SeriesCode'])['DataValue'].pct_change(12)
lvl2 = [ x[:-1] + 'G' for x in lvl2]
rows = price['SeriesCode'].isin(lvl2)
df = price[rows].copy()
zero = pd.DataFrame({'TimePeriod': df['TimePeriod'].unique(), 'SeriesCode': '------------',
                     'LineDescription': '----------', 'pct_chg': 0})
df = pd.concat([df, zero], axis=0)
df['LineDescription'] = df['LineDescription'].str[:20]
df['rank'] = df.groupby('TimePeriod')['pct_chg'].transform(lambda x: x.rank())
df.to_excel('pce_pi.xlsx', index=False)


###########################################################################################
_real = {}
_price = {}
_pce = {}
for y in years:
    try:
        _real[y] = beaapi.get_data(beakey, datasetname='NIPA', TableName='T20403', Frequency='Q', Year=y)
        _price[y] = beaapi.get_data(beakey, datasetname='NIPA', TableName='T20404', Frequency='Q', Year=y)
        _pce[y] = beaapi.get_data(beakey, datasetname='NIPA', TableName='T20405', Frequency='Q', Year=y)
    except:
        print(f'Year {y} is not available')

Qreal = pd.concat(_real.values(), axis=0).sort_values(['SeriesCode', 'TimePeriod'])
Qprice = pd.concat(_price.values(), axis=0).sort_values(['SeriesCode', 'TimePeriod'])
Qpce = pd.concat(_pce.values(), axis=0).sort_values(['SeriesCode', 'TimePeriod'])


for name, lag in { 'YoY': 4}.items():
    Qreal['pct_chg'] = Qreal.groupby(['SeriesCode'])['DataValue'].pct_change(lag)
    rows = Qreal['SeriesCode'].isin(lvl3)
    df = Qreal[rows].copy()
    zero = pd.DataFrame({'TimePeriod': df['TimePeriod'].unique(), 'SeriesCode': '------------',
                         'LineDescription': '----------', 'pct_chg': 0})
    df = pd.concat([df, zero], axis=0)
    df['rank'] = df.groupby('TimePeriod')['pct_chg'].transform(lambda x: x.rank())
    if lag == 4:
        df.to_excel('pce_real_detail.xlsx', index=False)
 


lvl3 = [ x[:-1] + 'C' for x in lvl3]
for name, lag in { 'YoY': 4}.items():
    Qpce['pct_chg'] = Qpce.groupby(['SeriesCode'])['DataValue'].pct_change(lag)
    rows = Qpce['SeriesCode'].isin(lvl3)
    df = Qpce[rows].copy()
    zero = pd.DataFrame({'TimePeriod': df['TimePeriod'].unique(), 'SeriesCode': '------------',
                         'LineDescription': '----------', 'pct_chg': 0})
    df = pd.concat([df, zero], axis=0)
    df['rank'] = df.groupby('TimePeriod')['pct_chg'].transform(lambda x: x.rank())
    if lag == 4:
        df.to_excel('pce_detail.xlsx', index=False)


Qprice['pct_chg'] = Qprice.groupby(['SeriesCode'])['DataValue'].pct_change(4)
lvl3 = [ x[:-1] + 'G' for x in lvl3]
rows = Qprice['SeriesCode'].isin(lvl3)
df = Qprice[rows].copy()
zero = pd.DataFrame({'TimePeriod': df['TimePeriod'].unique(), 'SeriesCode': '------------',
                     'LineDescription': '----------', 'pct_chg': 0})
df = pd.concat([df, zero], axis=0)
df['rank'] = df.groupby('TimePeriod')['pct_chg'].transform(lambda x: x.rank())
df.to_excel('pce_pi_detail.xlsx', index=False)
