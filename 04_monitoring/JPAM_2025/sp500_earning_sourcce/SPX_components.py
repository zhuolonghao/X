import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

def impute_missing(row):
    x = np.array([i for i in range(len(row)) if not np.isnan(row[i])])  # Indices of known values
    y = np.array([row[i] for i in range(len(row)) if not np.isnan(row[i])])  # Known values

    if len(x) < 2:
        return row  # Skip if not enough data for interpolation

    f = interp1d(x, y, kind="linear", fill_value="extrapolate")

    for i in range(len(row)):
        if np.isnan(row[i]):
            row[i] = f(i)  # Impute missing value using interpolation/extrapolation

    return row


# Read the Excel file into a dictionary of dataframes
file_path = "04_monitoring\JPAM_2025\sp500_earning_sourcce\SPX_components.xlsx"  # Replace with your actual file path
dfs = pd.read_excel(file_path, sheet_name=None, skiprows=1)  # None reads all sheets into a dictionary

# Display the sheet names
print(dfs.keys())



# Access a specific sheet
eps = dfs['EPS_A'].set_index('Constituents')  # Replace 'Sheet1' with the actual sheet name
rev = dfs['Rev_A'].set_index('Constituents')  # Replace 'Sheet1' with the actual sheet name
shr = dfs['Share_A'].set_index('Constituents')  # Replace 'Sheet1' with the actual sheet name

# Apply the function to each row (excluding the 'Constituents' column)
eps2 = eps.drop(index=eps.index[np.where(eps.iloc[:,1]=='#INVALID COMPANY ID')[0][0]]).astype('float')
eps2 = eps2.apply(impute_missing, axis=1).ffill(axis=1).bfill(axis=1)
rev2 = rev.drop(index=eps.index[np.where(eps.iloc[:,1]=='#INVALID COMPANY ID')[0][0]]).astype('float')
rev2 = rev2.apply(impute_missing, axis=1).ffill(axis=1).bfill(axis=1)
shr2 = shr.drop(index=eps.index[np.where(eps.iloc[:,1]=='#INVALID COMPANY ID')[0][0]]).astype('float')
shr2 = shr2.apply(impute_missing, axis=1).ffill(axis=1).bfill(axis=1)

