import numpy as np
import yfinance as yf
import pandas as pd

# List of tickers (either as a space-separated string or a list)
BQR6 = {
    'IART': '2025-07-01', # down from 55
    'ADTN': '2025-07-01', # up from 75
    'ZIP': '2025-06-01', # down from 55
    'TBI': '2025-04-01', # down from 58
    'IRWD': '2025-03-01', # down from 58, further down from 65 to 75 on 2025-04-01
    'FTRE': '2025-03-01', # down from 58
    'SLAB': '2025-03-01', # down from 55
    'SSP': '2025-03-01', # down from 58
    'MMI': '2025-03-01', # up from 75
    'SBGI': '2025-02-01', # DOWN FROM 58
    'EDR': '2025-01-01', # DOWN FROM 58
    'MATV': '2025-01-01', # DOWN FROM 58
    'SMTC': '2025-01-01', # UP FROM 75
    'SNAP': '2024-12-01', # UP FROM 75
    'AGL': '2024-12-01', #DOWN FROM 58
    'MXL': '2024-12-01', #DOWN FROM 58
    'CATO': '2024-10-01', #DOWN FROM 58
    'MRCY': '2024-09-01', #DONW FROM 58
    'APPS': '2024-09-01', #DONW FROM 58
    'VFC': '2024-08-01', #DONW FROM 58
    'BA': '2024-08-01', #DONW FROM 58
    'GTN': '2024-08-01', #DONW FROM 58
    'TTEC': '2024-08-01', #DONW FROM 58
    'MEI': '2024-07-01', #DONW FROM 58
    'LTH': '2024-06-01', #DONW FROM 58
    'MODV': '2024-06-01', #DONW FROM 58
    'HE': '2024-05-01', #DONW FROM 58
    'SPHR': '2024-05-01', #DONW FROM 58
    'AKA': '2024-05-01', #DONW FROM 58
}

BQR7 = {
    'OSCR': '2025-08-01',
    'AGL': '2025-08-01',
    'FLY': '2025-08-01',
    'MEI': '2025-07-01',
    'FLWS': '2025-05-01',
    'CODI': '2025-05-01',
    'IRWD': '2025-04-01',
    'FTRE': '2025-04-01',
    'TTEC': '2025-01-01',
    'GT': '2024-12-01',
    'CMP': '2024-12-01',
    'ONEW': '2024-12-01',
    'APPS': '2024-12-01',
    'CRNC': '2024-11-01',
    'NFE': '2024-10-01',
    'WDC': '2024-09-01',
    'PENN': '2024-09-01',
    'BALY': '2024-09-01',
    'MODV': '2024-09-01',
    'SPHR': '2024-08-01',
    'HBIO': '2024-08-01',
    'RDUS': '2024-06-01',
    'MPW': '2024-05-01',
    'MMI': '2024-05-01',
    'SMTC': '2024-04-01',
}

BQR58 = {
    'HBIO'	:'2024-04-01',
    'TELA'	:'2024-04-01',
    'APPS'	:'2024-04-01',
    'BALY'	:'2024-04-01',
    'MODV'	:'2024-04-01',
    'EVC'		:'2024-04-01',
    'OMCL'	:'2024-04-01',
    'BAND'	:'2024-04-01',
    'PENN'	:'2024-04-01',
    'SHYF'	:'2024-04-01',
    'SGH'		:'2024-04-01',
    'VFC'		:'2024-05-01',
    'GDOT'	:'2024-05-01',
    'RDUS'	:'2024-05-01',
    'CATO'	:'2024-05-01',
    'IFF'		:'2024-06-01',
    'EMBC'	:'2024-06-01',
    'TTEC'	:'2024-06-01',
    'QTWO'	:'2024-06-01',
    'FMC'		:'2024-07-01',
    'EFXT'	:'2024-07-01',
    'TTWO'	:'2024-07-01',
    'HRYS'	:'2024-08-01',
    'CRK'		:'2024-08-01',
    'EXTR'	:'2024-08-01',
    'MXL'		:'2024-09-01',
    'TBI'		:'2024-09-01',
    'IRWD'	:'2024-09-01',
    'HNGR'	:'2024-10-01',
    'DKNG'	:'2024-10-01',
    'ALNT'	:'2024-10-01',
    'WLFC'	:'2024-11-01',
    'TG'		:'2024-11-01',
    'APO'		:'2024-11-01',
    'WDC'		:'2024-11-01',
    'OSCR'	:'2024-12-01',
    'PACK'	:'2024-12-01',
    'ZIP'		:'2024-12-01',
    'LFST'	:'2024-12-01',
    'LPRO'	:'2024-12-01',
    'SALT'	:'2024-12-01',
    'FOXF'	:'2024-12-01',
    'CLR'		:'2024-12-01',
    'EXAS'	:'2024-12-01',
    'AMPK'	:'2024-12-01',
    'TDS'		:'2024-12-01',
    'SMG'		:'2024-12-01',
    'NCLH'	:'2025-01-01',
    'PRDO'	:'2025-02-01',
    'DTI'		:'2025-02-01',
    'ASTH'	:'2025-02-01',
    'HBI'		:'2025-03-01',
    'NEOG'	:'2025-03-01',
    'SWX'		:'2025-03-01',
    'DNUT'	:'2025-03-01',
    'CMCO'	:'2025-04-01',
    'CAR'	:'2025-04-01',
    'APPN'	:'2025-04-01',
    'ADP'		:'2025-04-01',
    'JEF'		:'2025-04-01',
    'HI'		:'2025-05-01',
    'LGF.A'	:'2025-05-01',
    'RELY'	:'2025-05-01',
    'EE'		:'2025-05-01',
    'EHAB'	:'2025-06-01',
    'COR'		:'2025-06-01',
    'ASTE'	:'2025-07-01',
    'HE'		:'2025-07-01',
    'WRLD'	:'2025-07-01',
    'AMCX'	:'2025-07-01',
    'PII'		:'2025-07-01',
}

CPE887 = {
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

CPE888 =  {
    'FLY': '2025-08-01',
    'CODI': '2025-06-01',
    'HAIN': '2025-06-01', # from 887 to 888
    'NFE': '2024-10-01',
    'AGL': '2023-05-01',
    'CRWV': '2024-10-01', #delisted, acquired
}

NAC = {
    'SPHR': '2024-09-01',
#    'AUDAQ': '2023-03-01', # delisted
    'EBS': '2024-03-01',
#    'EVHC': '2023-04-01', # delisted
#    'GRPN': '2023-03-01',
#    'TUP': '2023-05-01', # delisted
#    'EE': '2024-08-01',
    'MODV': '2025-01-01',
#    'BMHC': '2025-01-01', # delistd
#    'HON': '2025-02-01',
    'GORV': '2025-05-01',
    'NFE': '2025-07-01',
}

df_BQR58 = pd.DataFrame.from_dict(BQR58, orient='index').reset_index().rename(columns={0:'BQR58'})
df_BQR6 = pd.DataFrame.from_dict(BQR6, orient='index').reset_index().rename(columns={0:'BQR6'})
df_BQR7 = pd.DataFrame.from_dict(BQR7, orient='index').reset_index().rename(columns={0:'BQR7'})
df_CPE887 = pd.DataFrame.from_dict(CPE887, orient='index').reset_index().rename(columns={0:'CPE887'})
df_CPE888 = pd.DataFrame.from_dict(CPE888, orient='index').reset_index().rename(columns={0:'CPE888'})
df_NAC = pd.DataFrame.from_dict(NAC, orient='index').reset_index().rename(columns={0:'NAC'})


merged = df_BQR58.merge(df_BQR6, on="index", how="outer")\
            .merge(df_BQR7, on="index", how="outer") \
            .merge(df_CPE887, on="index", how="outer")\
            .merge(df_NAC, on="index", how="outer")\
            .merge(df_CPE888, on="index", how="outer")
merged.to_csv('strategy_track.csv')