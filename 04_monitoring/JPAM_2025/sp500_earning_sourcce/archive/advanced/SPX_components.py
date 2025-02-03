import pandas as pd
import numpy as np

# Read the Excel file into a dictionary of dataframes
file_path = "04_monitoring/JPAM_2025/sp500_earning_sourcce/advanced/SPX_components.xlsx"  # Replace with your actual file path
dfs = pd.read_excel(file_path, sheet_name=None, skiprows=2)  # None reads all sheets into a dictionary

# Display the sheet names
print(dfs.keys())

# Access a specific sheet
eps = dfs['EPS_Q']
rev = dfs['Rev_Q']
shr = dfs['Share_Q']
# Apply the function to each row (excluding the 'Constituents' column)
eps2 = eps.drop(np.where(eps.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
rev2 = rev.drop(np.where(eps.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')
shr2 = shr.drop(np.where(eps.iloc[:,1]=='#INVALID COMPANY ID')[0]).set_index('Constituents').astype('float')

cols = eps2.columns
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
    _list.append([c, tmp2['net_income'], tmp2['revenue'], tmp2['net_income']/tmp2['revenue'], tmp2['share']])
columns = ['Quarter', 'Earnings', 'Revenue', 'Net Income Margin', 'Shares']
output = pd.DataFrame(_list, columns=columns)

