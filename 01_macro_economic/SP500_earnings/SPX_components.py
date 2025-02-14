import pandas as pd
import numpy as np

# Read the Excel file into a dictionary of dataframes
file_path = "04_monitoring\JPAM_2025\sp500_earning_sourcce\data\SP500_components.xlsx"  # Replace with your actual file path
dfs = pd.read_excel(file_path, sheet_name=None, skiprows=2)  # None reads all sheets into a dictionary

# Display the sheet names
print(dfs.keys())

# Access a specific sheet
eps = dfs['EPS_Q']
rev = dfs['Rev_Q']
shr = dfs['Share_Q']
meta = dfs['meta']
# Apply the function to each row (excluding the 'Constituents' column)
eps2 = eps.drop(np.where(eps.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
rev2 = rev.drop(np.where(rev.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
shr2 = shr.drop(np.where(shr.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
meta2 = meta.drop(np.where(meta.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents')

cols = eps2.columns
sectors = meta2['Sector'].unique()
output_sec = pd.DataFrame()
_list = []
for c in cols:
    e = eps2[c]
    r = rev2[c]
    s = shr2[c]
    tmp = pd.concat([e, r, s], axis=1).dropna()
    tmp.columns = ['eps', 'revenue', 'share']
    tmp['net_income'] = tmp['eps'] * tmp['share']
    tmp['revenue'] = tmp['revenue'] * 1000
    tmp2 = tmp.sum()
    c2 = c[3:]+c[1:3]
    _list.append([c2, tmp2['net_income'], tmp2['revenue'], tmp2['net_income']/tmp2['revenue'], tmp2['share']])
    for sec in sectors:
        tickers_in_sector = meta2[meta2['Sector'].eq(sec)]
        tmp2 = pd.concat([tickers_in_sector, tmp], axis=1).dropna()
        tmp2 = tmp2.reset_index()
        tmp2['Quarter'] = c2
        tmp2['Index'] = 'SP500'
        output_sec = pd.concat([output_sec, tmp2])
columns = ['Quarter', 'Earnings', 'Revenue', 'Net Income Margin', 'Shares']
output = pd.DataFrame(_list, columns=columns)


################################################################################

# Read the Excel file into a dictionary of dataframes
file_path = "04_monitoring\JPAM_2025\sp500_earning_sourcce\data\SP400_components.xlsx"  # Replace with your actual file path
dfs = pd.read_excel(file_path, sheet_name=None, skiprows=2)  # None reads all sheets into a dictionary

# Display the sheet names
print(dfs.keys())

# Access a specific sheet
eps = dfs['EPS_Q']
rev = dfs['Rev_Q']
shr = dfs['Share_Q']
meta = dfs['meta']
# Apply the function to each row (excluding the 'Constituents' column)
eps3 = eps.drop(np.where(eps.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
rev3 = rev.drop(np.where(rev.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
shr3 = shr.drop(np.where(shr.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
meta3 = meta.drop(np.where(meta.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents')

cols = eps3.columns
_list = []
for c in cols:
    e = eps3[c]
    r = rev3[c]
    s = shr3[c]
    tmp = pd.concat([e, r, s], axis=1).dropna()
    tmp.columns = ['eps', 'revenue', 'share']
    tmp['net_income'] = tmp['eps'] * tmp['share']
    tmp['revenue'] = tmp['revenue'] * 1000
    tmp2 = tmp.sum()
    c2 = c[3:] + c[1:3]
    _list.append([c2, tmp2['net_income'], tmp2['revenue'], tmp2['net_income']/tmp2['revenue'], tmp2['share']])
    for sec in sectors:
        tickers_in_sector = meta3[meta3['Sector'].eq(sec)]
        tmp2 = pd.concat([tickers_in_sector, tmp], axis=1).dropna()
        tmp2 = tmp2.reset_index()
        tmp2['Quarter'] = c2
        tmp2['Index'] = 'SP400'
        output_sec = pd.concat([output_sec, tmp2])
columns = ['Quarter', 'Earnings', 'Revenue', 'Net Income Margin', 'Shares']
output2 = pd.DataFrame(_list, columns=columns)


################################################################################

# Read the Excel file into a dictionary of dataframes
file_path = "04_monitoring\JPAM_2025\sp500_earning_sourcce\data\SP600_components.xlsx"  # Replace with your actual file path
dfs = pd.read_excel(file_path, sheet_name=None, skiprows=2)  # None reads all sheets into a dictionary

# Display the sheet names
print(dfs.keys())

# Access a specific sheet
eps = dfs['EPS_Q']
rev = dfs['Rev_Q']
shr = dfs['Share_Q']
meta = dfs['meta']
# Apply the function to each row (excluding the 'Constituents' column)
eps4 = eps.drop(np.where(eps.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
rev4 = rev.drop(np.where(rev.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
shr4 = shr.drop(np.where(shr.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
meta4 = meta.drop(np.where(meta.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents')


cols = eps3.columns
_list = []
for c in cols:
    e = eps4[c]
    r = rev4[c]
    s = shr4[c]
    tmp = pd.concat([e, r, s], axis=1).dropna()
    tmp.columns = ['eps', 'revenue', 'share']
    tmp['net_income'] = tmp['eps'] * tmp['share']
    tmp['revenue'] = tmp['revenue'] * 1000
    tmp2 = tmp.sum()
    c2 = c[3:] + c[1:3]
    _list.append([c2, tmp2['net_income'], tmp2['revenue'], tmp2['net_income']/tmp2['revenue'], tmp2['share']])
    for sec in sectors:
        tickers_in_sector = meta4[meta4['Sector'].eq(sec)]
        tmp2 = pd.concat([tickers_in_sector, tmp], axis=1).dropna()
        tmp2 = tmp2.reset_index()
        tmp2['Quarter'] = c2
        tmp2['Index'] = 'SP600'
        output_sec = pd.concat([output_sec, tmp2])
columns = ['Quarter', 'Earnings', 'Revenue', 'Net Income Margin', 'Shares']
output3 = pd.DataFrame(_list, columns=columns)


with pd.ExcelWriter("04_monitoring\JPAM_2025\sp500_earning_sourcce\SPX_components.xlsx") as writer:
    output.to_excel(writer, sheet_name='sp500', index=False)
    output2.to_excel(writer, sheet_name='sp400', index=False)
    output3.to_excel(writer, sheet_name='sp600', index=False)
    output_sec.to_excel(writer, sheet_name='total_sector', index=False)
