import numpy as np
import yfinance as yf
import pandas as pd
# https://www.barchart.com/stocks/quotes/TSVT/interactive-chart
# ['BRK.A', 'NBR.GV', 'MAXR', 'PRSC', 'BNYBM81', 'LGTC', 'CLGX', 'EQM', 'FBC', 'CTL', 'LOGM', 'MNI', 'MSG', 'FTREV', 'HNGR', 'SWM', 'QUMU']
# ['NICK', 'TUP', 'VCSA', 'TSVT', 'TAST', 'NYCB', 'BLUE', 'GLT']:
# ['SGP', 'KKD', 'RMK']:
# ['CRVW']:


# List of tickers (either as a space-separated string or a list)
BQR6 = {
    'MRCY': '2024-09-01',
    'MXL': '2024-12-01',
    # 'TAST': 58-65 on '2022-03-01', 65-75 on '2022-09-01', 75-65 on '2023-06-01', 65-58 on '2023-09-01', 58-55 on '2024-01-01'. delisted on '2024-06-01' Popeyes bought BurgerKings
    'MPW': '2024-12-01', # 55-65 ON 2024.03.01, 75 ON 2024.05.01, 65 ON 2024.12.01
    'FNKO': '2025-06-01', # 52-62 ON 2023.03.01, 75 ON 2023.04.01, 65 ON 2024.09, 58 ON 2025.04, 65 ON 2025.06
    'HBI': '2023-09-01',
    'HAIN': '2023-09-01',
    'SMG': '2024-12-01', # 58-65 ON 2023.07, 58 ON 2024.12
    'MMI': '2025-03-01', # 58-65 ON 2023.08, 75 ON 2024-05, 65 2025.03
    'MEI': '2024-07-01',
    'WWW': '2023-04-01', # 58-65 202309, 58 202403, 65 202404
    'MCS': '2023-04-01', # 75-65 202203, 58-65 202304
    'BVS': '2024-01-01', # 58-65 202212, 75 202302 65 202401
    'SNAP': '2024-12-01', # 58-65 202305 75 202309 65 202412
    'EHAB': '2023-10-01', # 55-65 202310
    'CAKE': '2021-06-01',
    'DAL': '2022-11-01',
    'LUV': '2022-09-01', # 75-65 202201 75 202203 65 202209
    'IHG': '2021-04-01',
    'MATV': '2025-01-01', # SWM MERGED WITH ANOTHER AND BECAME MATV
    'WLFC': '2023-11-01', #58-65 202103 75 202203 65 202311
    'IOVA': '2024-03-01',
    'TEN': '2022-09-01', #75-65, 202103 65 202209 ### COMPLEX LOAN RELATIONSHIP BTW CIB AND CB ABL
    'AGL': '2024-12-01', #75-65, 202112, 58 202311, 65 202412, 75 202508
    #'MAXR': '2021-06-01', 75-65, 202106, 75 202109, 65 202209, # DELISTED ON 202305
    'CRNC': '2023-03-01', # 58-65 202303, 75 202411
    'NAII': '2024-09-01', # 55-65 202303, 75 202409,
    'BA': '2024-08-01', # 55-65 202103 58 202305 65 202408
    'HXL': '2022-03-01', # 58-65, 202103, 55 202203,
    'SMTC': '2025-01-01', # 58-65 202305 75 202306 65 202501
    'HE': '2024-04-01', # 42-65 202308 75 202309 65 202404
    ## Below, single event
    'HBIO': '2023-01-01',
    'IRWD': '2025-03-01',
    'PAY': '2025-03-01',
    'IFF': '2024-03-01',
    'SCHL': '2021-06-01',
    'BLUE': '2022-01-01',# delisted
    'COTY': '2021-09-01',
    'EBS': '2022-11-01',
    'XRX': '2022-03-01',
    'MGI': '2021-06-01', #  delisted
    'BKD': '2024-07-01',
    'LYV': '2022-06-01',
    'APPS': '2024-09-01',
    'SPB': '2022-12-01',
    'MG': '2022-01-01',
    'PLUG': '2022-11-01',
    'CRS': '2021-06-01',
    'MAGN': '2022-05-01',
    'VFC': '2024-08-01',
    'TTAN': '2022-02-01',
    'NONE': '2024-01-01', #  delisted
    'NTNX': '2022-01-01',
    'MPC': '2021-09-01',
    'VCSA': '2022-01-01', #  delisted
    'ZIP': '2025-06-01',
    'ESLT': '2023-01-01', # 58-65 ON 202301, 75 202305, 65 202307, 75 202401, 58 202505
    'SSP': '2025-03-01',
    'SMSI': '2022-07-01',
    'WDC': '2023-12-01',
    'FUN': '2021-12-01',
    'TDS': '2023-09-01',
    'NWL': '2024-03-01',
    'CMP': '2024-03-01',
    'TUP': '2022-11-01', #  delisted
    'EQM': '2024-02-01', #  delisted
    'PSXP': '2021-11-01', #  delisted
    'CZR': '2022-01-01',
    'QUMU': '2022-01-01', #  delisted
    'BRK-A': '2023-11-01',
    'TTTN': '2021-10-01', #  delisted
    'FOGO': '2022-06-01', #  delisted
    'OSCR': '2021-02-01',
    'ARCT': '2023-04-01',
    'SWX': '2022-10-01',
    'IART': '2025-07-01',
    'MAR': '2021-03-01',
    'IGT': '2023-12-01', #  delisted
    'CATO': '2024-10-01',
    'DNUT': '2025-07-01',
    'GTN': '2024-08-01',
    'OMCC': '2022-10-01',
    'ADTN': '2025-07-01',
    'CPE': '2021-09-01', #  delisted
    'LUMN': '2023-06-01',
    'CLR': '2021-03-01', #  delisted
    'MTRX': '2021-03-01',
    'GPOR': '2021-07-01',
    'VLO': '2021-09-01',
    'SLAB': '2025-03-01',
    'RP': '2021-04-01',  #  delisted
    'BRY': '2021-09-01',
    'TRIP': '2022-06-01',
    'LOGM': '2022-12-01',  #  delisted
    'CNDT': '2024-12-01', # TWO EINS ARE RELATED
    'WH': '2021-03-01',
    'CUDA': '2023-05-01', #  delisted
    'NFE': '2024-03-01',
    'TTEC': '2024-08-01',
    'HPK': '2023-06-01',
    'LPRO': '2025-07-01',
    'MODVQ': '2024-06-01',  #  delisted
    'QEP': '2021-03-01',  #  delisted
    'HLLY': '2023-02-01',
    'CDEV': '2021-04-01',  #  delisted
    'ZUMZ': '2023-12-01',
    'TBI': '2025-04-01',
    'FTRE': '2025-03-01',
    'NBR': '2022-11-01',
    'CLGX': '2022-07-01',  #  delisted
    'BRID': '2025-07-01',
    'CRBG': '2022-06-01',
    'TRTN': '2021-04-01', #  delisted
    'RCL': '2023-08-01',
    'NE': '2022-08-01',
    'WFRD': '2021-12-01',
    'AYR': '2021-03-01', #  delisted
    'CVE': '2021-01-01',
    'SCHN': '2024-07-01'
}

BQR7 = {
    'HBIO': '2024-08-01',
    #'TELL': new deal on '2024-02-01', NOB on '2024-07-01',
    'FLWS': '2025-05-01', # NOB on '202507'
    'BLUE': '2024-11-01', # DELISTED ON 202506
    'MPW': '2024-05-01',
    'BALY': '2024-09-01',
    'FNKO': '2023-04-01',
    'APPS': '2024-12-01',
    'MAGN': '2022-10-01', # CMLBKNG NEW 202109, MM-CORP ON 202201, CMLBKNG ON 202210, MM-CORP ON 202309, WFCF ON 202411, IBCM ON 202504
    'PENN': '2024-09-01',
    'GRPN': '2022-06-01',
    'ESLT': '2023-05-01',  # 58-65 ON 202301, 75 202305, 65 202307, 75 202401, 58 202505
    'CMP': '2024-12-01',
    'SNAP': '2023-09-01',   # 58-65 202305 75 202309 65 20241
    'ADTN': '2023-11-01',   # 58-75 202311 65 202507
    'WLFC': '2022-03-01',
    'LUMN': '2024-01-01',
    'ONEW': '2024-12-01',
    'NFE': '2024-10-01',
    'WEST': '2024-09-01',
    'SCHN': '2024-06-01',
    'CLGX': '2024-06-01', # 58-65 202207 75 202209
    'SMTC': '2023-06-01',
    ## Below, single event
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
    'HBIO': '2023-01-01', # 58-65 and 887 on same 202301, 58-75 and 859 on same 202408'],
    'FLWS': '2025-06-01', # 58-75 on 202505, 887 on 202506'],
    'SCHL': '2021-09-01', # new deal with 65 on 202109, 887 on 202110'],
    'APPS': '2024-09-01', # 58-65 and 887 on same 202409, 65-75 202412'],
    'HAIN': '2023-07-01', # 58-65 and 887 on 202309'],
    'MG': '2021-08-01', # 58-65 and 887 on 202108, 58-65 202207'],
    'CRS': '2022-06-01', # 55-65 202208, 887 202206'],
    'IMGN': '2023-07-01', # 65-65 887 202305, 65-75 202305, 75-58 & 887 dropped & WFCF takeover 202411'],
    'ESIIT': '2023-01-01', # 58-65 202301, 887 202303'],
    'SMG': '2023-07-01', # 58-65 & 887 202307, 65-58 202412'],
    'NWL': '2024-02-01', # 887 202402 58-65 202403'],
    'CMP': '2025-05-01', # 65-65 & 887 on 202104, 65-75 202412'],
    'SNAP': '2025-05-01', # 75-65 202412, 887 202505'],
    'OSCR': '2022-06-01', # new 65 202108, 887 202206 65-58 202412 887 202502 58-75 202508'],
    'MSG': '2023-01-01', # 58-65 & 887 202303'],
    'MSGS': '2023-01-01', # 58-65 202410, 887 202411'],
    'CATO': '2021-07-01', # 58-65 202109, 887 202111'],
    'MATV': '2025-04-01', # 58-65 202501 887 202504'],
    'CPE': '2021-10-01', # 65-65 202109 58 202111'],
    'RIG': '2022-11-01', # 58-65 202204 887 202203'],
    'HLT': '2021-02-01', # new 65 202108, 887 202202'],
    'ONEW': '2025-02-01', # 58-75 202412, 887 202502'],
    'CRNC': '2022-01-01', # 58-65 202110, 887 202111'],
    'TTEC': '2023-01-01', # 58-65 & 887 202408'],
    'WEST': '2024-03-01', # 65-75 & 887 202409'],
    'MYGN': '2022-10-01', # new 65 202108, 887 202210'],
    'LYLT': '2023-11-01', # 58-65 887 202208'],
    'HLIT': '2022-03-01', # 58-65 202302 887 202305'],
    'SCHN': '2022-01-01', # 58-75 887 202406'],
    'CLGX': '2025-07-01', # delisted'],
    'SMTC': '2023-08-01' # 58-6502305 75 202306 887 202308']
}

CPE888 =  {
    'PAY': '2025-04-01', # new 65 202503, 888 202504'],
    'HAIN': '2025-06-01', # 58-65 & 888 202309'],
    'TDS': '2023-11-01', # 888 202311'],
    'TEN': '2023-01-01', # 888'],
    'AGL': '2023-05-01',
    'FLY': '2025-08-01', # new 75 & 888 on 202508'],
    'CRVW': '2024-10-01', # new 65 & 888 on 202410'],
    'NFE': '2024-10-01', # 65-75 202410'],
    'NBR': '2022-11-01' # 75-65 202211']
}

NAC = {
    'SPHR': '2024-09-01',
        # RCF: 52-58 202304, 65 202401, 75 202408, 85 202409
        # LOB: CMLBKNG TO MIDCORP-MM ON 202201
        # ROLES: MEMBER TO BOOK-RUNNER ON 202108
        # WFC's record was not directly related to SPHR
    'AUDAQ': '2023-03-01', # delisted -LME
        # RCF: 65-75 ON 202009
        # LOB: IBCM engaged TL 202008-202204, RCF 202012-202106
        # Corp History: CBS Radio merged into Entercom in 2017, Entercom later rebranded to Audacy in 2021.
            # 2021-04-09: Ticker Change ETM-to-AUD
            # 2023-05-16: delisting proceedings begin
            # 2023-11-10: delisting is effective
            # 2024-01-07: Chapter 11 bankruptcy
            # 2024-09-30: restructuring finalize, and become private
            # 2025-01-26: Final Chapter 11 decree
    'EBS': '2024-03-01', # Big Lost, EBS hit the bottom in 202403 (Large Vol)
        # RCF: 55-65 202211, 75 202212 NAC 202403
        # LOB: HEALTHCARE -> WFCF 202408
        # LOB: IBCM ENGAGE TL 202401-202408, RCF 202306-202408
        # Corp History:
            # no financial restructuring,
            # Operation Optimization throughout 2024: layoff + asset sale
    'EVHC': '2023-04-01', # delisted before NAC
        # no RCF.   TL NAC 202304
        # LOB: ONLY IBCM
    'GRPN': '2023-03-01', # Big Lost. GRPN hit the bottom in 202303
        # RCF: 65-75 ON 202206, NAC 202303
        # LOB: CMLBKNG in and out of Mid-Corp 202202 - 202209
     'TUP': '2023-05-01', # delisted
        # RCF: 58-65 202211, 75 202302 nac 202305
        # LOB: CMLBKGN 202008 MID-CORP 202205 CMLBKGN 202211 MID-CORP 202309
        # Corp History:
            # Late 2022: violate credit agreements
            # Mar-Apr 2023: missed 10-K, going concern
            # June 2023: debt structuring
            # Aug 2023, mgnt changes / broad refresh
    'RGS': '2022-09-01',
        # RCF: NAC ON 202209
        # LOB: CORP-RETL
    'SBGI': '2021-07-01',
        # RCF: NAC 202107
        # LOB: TMT
     'EE': '2024-08-01',
        # RCF: NAC BQR45 202408
        # LOB: ENGY
    'NFE': '2025-07-01',
        # RCF: 58-65 202403 75 202410 NAC 202507
        # LOB: IBCM ENGAGE FROM 202403-202408, 202505-202508(UP-TO-DATE)
    'MODV': '2025-01-01',
        # RCF: 58-65 202406 75 202409 NAC 202503
        # TL: NAC 202501
        # LOB: MID-CORP
    'LYLT': '2022-12-01',
        # RCF: 58-75 202208 NAC 202212
        # LOB: TMT, IBCM 20225-202206, 202302
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