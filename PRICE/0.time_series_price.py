from financial_tools import AlphaVantageClient, FinancialAnalyzer, FMPClient
import pandas as pd
import numpy as np
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
# --- Configuration ---

API_KEY = "PTIKPYJ08KJ0X8T5"
active = [
    "ADTN", "AGL", "ALTG", "AMCX", "APPS", "ARRY", "ATRO", "BA", "BALY", "BFX",
    "BGI", "BIG", "BKD", "BLUE", "BNED", "BRID", "BRY", "BVS", "BWEN", "CAKE",
    "CATO", "CBRL", "CCO", "CENX", "CLF", "CLMT", "CMP", "CNK", "COMM", "CPE",
    "CRBG", "CRNC", "CRS", "CTOS", "DAL", "DBI", "DHC", "DK", "DXLG", "EBS",
    "EGHT", "EHAB", "ESLT", "FARM", "FBC", "FET", "FLG", "FLWS", "FNKO",
    "FOSL", "FTRE", "FUN", "FVE", "GAMR", "GLT", "GME", "GPOR", "GPRO", "GPS",
    "GRPN", "GT", "GTN", "HAIN", "HBI", "HBIO", "HE", "HELE", "HLLY", "HPK",
    "HXL", "HY", "IART", "ICD", "IFF", "IHG", "IOVA", "IRWD", "JAKK", "JELD",
    "KALU", "KLXE", "KRO", "LCI", "LE", "LSF", "LUMN", "LUV", "LXU", "MAGN",
    "MAR", "MATV", "MCS", "MDLA", "MEI", "MPW", "MRCY", "MTRX", "MXL", "NAII",
    "NBR", "NE", "NFE", "NICK", "NINE", "NSCO", "NWL", "NYCB", "OIS", "OMCC",
    "ONEW", "OPI", "OSCR", "PAY", "PENN", "PLCE", "PLUG", "QVCC", "QVCD",
    "RCL", "RILY", "RILYK", "RMBL", "ROOT", "SALM", "SAVE", "SCHL", "SCHN", "SLAB",
    "SLG", "SMG", "SMSI", "SMTC", "SNAP", "SPB", "SSP", "SUMR", "SWM", "TAST",
    "TBI", "TCS", "TDS", "TEN", "TG", "TITN", "TPIC", "TRIP",  "TTEC",
    "UAL", "UFI", "UFS", "UNFI", "USX", "VFC", "VLO", "VREX", "WDC", "WFC",
    "WFRD", "WH", "WLFC", "WNC", "WOLF", "WOOF", "WWW", "X", "XRX", "ZIP", "ZUMZ", 'DNUT'
]

delisted = [
    "BBBY", "SBNY", "ALR", "COUP", "PLAN", "BPR", "BPYU", "GGP",
    "MIK", "AKCA", "CLR", "RP", "MDLA", "CUDA", "MAXR", "HNGR",
    "LYLT", "LYLTV", "CSPR", "RDUS", "MMI", "MNI", "TUP", "FLYY",
    "PSXP", "QUMU", "HOME", "NSCO", "RUTH", "CLGX", "WEST", "RDFN",

]

TICKER_LIST = delisted

# --- Instantiate the Classes ---
client1 = FMPClient()
# --- Run the Logic ---
all_data = []
for symbol in TICKER_LIST:
    print(f"\n--- Processing {symbol} ---")

    data = client1.get_data('historical-price-eod', symbol)
    if data:
        all_data.append(pd.DataFrame(data))
    else:
        print(f"------------------------- No historical data found for: {symbol}")
    # Optional: respect rate limits based on your plan (Free is 250 requests/day)
    time.sleep(0.1)

# Combine all into one master DataFrame
master_df = pd.concat(all_data, ignore_index=True)