# ['LYLT', 'CTL', 'FVE', 'PRSC', 'HNGR', 'RUTH', 'PLAN', 'MIK', 'CREE', 'MGI', 'QUMU', 'NSCO', 'AKCA', 'QMCC', 'BPR', 'CLR', 'ERI', 'FBC', 'ALR', 'LYLTV', 'BPYU', 'MDLA', 'DSW', 'FLYY', 'PSXP', 'RP', 'UFS', 'CSPR', 'SWM', 'EQM', 'TRWH', 'MAXR', 'COUP', 'ESL', 'LCI', 'USX', 'HOME', 'SNH']: YFTzMissingError('possibly delisted; no timezone found')
# ['TCS', 'RDFN', 'CPE', 'NYCB', 'SAVE', 'BLUE', 'RMBL', 'TUP', 'TAST', 'X', 'ICD', 'NICK', 'GLT', 'BIG']: YFPricesMissingError('possibly delisted; no price data found  (1d 2020-01-01 -> 2025-12-06) (Yahoo error = "No data found, symbol may be delisted")')
# ['GOV', 'MNT', 'KKD', 'GGP']: YFPricesMissingError('possibly delisted; no price data found  (1d 2020-01-01 -> 2025-12-06)')
# ['TPIC']: YFInvalidPeriodError("TPIC: Period 'max' is invalid, must be of the format 1d, 5d, etc.")


tickers = [
    "DXLG","MRCY","HBIO","IRWD","DHC","SNH","ALR","FVE","PAY","UNFI",
    "BIG","UFI","BBBY","FLWS","IFF","ESL","CENX","SCHL","BLUE","COTY",
    "SLG","SBNY","MXL","EBS","XRX","ATRO","TAST","MGI","MPW","BALY",
    "TRWH","TPIC","FNKO","GME","BKD","LYV","HBI","COUP","CNK","UFS","APPS"
]
tickers2 = [
    "SPB","HAIN","PLUG","CRS","GLT","MAGN","LCI","VFC","PENN","QVCC",
    "QVCD","X","GOV","OPI","GAMR","RILY","RILYK","PLAN","GRPN","MPC",
    "BPR","BPYU","GGP","ZIP","UPLD","AMCX","ESLT","DBI","DSW","SSP",
    "PLCE","SMG","HY","CNDT","SMSI","WDC","GT","CLF","FUN","CLMT"
]
tickers3 = [
    "CTOS","MMI","MNT","DK","MEI","LE","TDS","NWL","CMP","TUP",
    "COMM","KLXE","ICD","EQM","MIK","CZR","WFC","WWW","FLYY","SAVE",
    "FBC","FLG","NYCB","PSXP","CZR","MCS","QUMU","TITN","HOME","BVS",
    "SNAP","BNED","OSCR","CZR","ERI","RMBL","CSPR","NSCO","EHAB","AKCA"
]
tickers4 = [
    "ROOT","IART","CAKE","WNC","MAR","TG",
    "CATO","CULP","KKD","CREE","WOLF","KKD",
    "DAL","GTN","IHG","NICK","QMCC","FET",
    "CBRL","USX","MATV","SWM","ADTN","CPE",
    "RIG","WLFC","CTL","LUMN","RUTH","CLR",
    "LXU","MTRX","GPOR","LUV","HELE","VLO",
    "UAL","SLAB","RDFN","TCS"
]
tickers5 = [
    "TCS","FOSL","RP","IOVA","KRO","OIS","TEN","BRY","SALM","EGHT",
    "MDLA","GPRO","TRIP","NINE","WOOF","LSF","AGL","CNDT","VREX","ONEW",
    "WH","CUDA","NFE","ALTG","MAXR","CRNC","HNGR","RMCF","NAII","TTEC",
    "HPK","WEST","ARRY","MODV","PRSC","LYLT","LYLTV","HLLY","CCO","BWEN"
]
added_post_2025dev = []
tickers_dict = tickers + tickers2 + tickers3 + tickers4 + tickers5 + added_post_2025dev

import numpy as np
import yfinance as yf
import pandas as pd
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


import os
folder = "individual"
csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
_barchart = {}
for x in csv_files:
    df = pd.read_csv(os.path.join(folder, x), skiprows=1)
    df = df[~df.iloc[:, 0].astype(str).str.contains("Downloaded from Barchart.com ", na=False)]
    df['ticker'] = x.split("_")[0]
    df['Date'] = df['Date Time'].astype(str)
    df['close'] = df['Close'].astype(float)
    _barchart[x] = df[['Date', 'ticker', 'close', 'Volume']]
pd.concat(_barchart).to_excel('BQR_vol_barchart.xlsx', index=False)