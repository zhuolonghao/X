import os
import pandas as pd
import numpy as np

folder_path = "C:\\Users\\longh\\Desktop\\X\\04_monitoring\\JPAM_2025\\inflation_components"
# List all .xlsx files in the folder
xlsx_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
xlsx_files2 = [f for f in xlsx_files if f.startswith('news-release-table7')]

entries = {
    'Food_at_home': [2, 'Food at home'],
    'Energy': [1, 'Energy'],
    'Shelter': [3, 'Shelter'],
    'Auto Insurance': [5, 'Motor vehicle insurance'],
    'Core_goods': [2, 'Commodities less food and energy commodities'],
    'Dining': [2, 'Food away from home'],
    'Core_svcs': [[2, 'Services less energy services'], [3, 'Shelter'], [5, 'Motor vehicle insurance']],
}

entries2 = {
    'Rest': [1, 'All items less food, shelter, energy, and used cars and trucks'],
    'Food': [1, 'Food'],
    'Energy': [1, 'Energy'],
    'Shelter': [3, 'Shelter'],
    'Used cars/trucks': [4, 'Used cars and trucks'],
}

entries3 = {
    'New Car': [4, 'New vehicles'],
    'Used Car': [4, 'Used cars and trucks'],
    'Auto Insurance': [5, 'Motor vehicle insurance'],
    'Auto Parts': [4, 'Motor vehicle parts and equipment'],
    'Auto Repair': [5, 'Motor vehicle maintenance and repair'],
}

entries4 = {
    'Dining': [2, 'Food away from home'],
    'Entertainment': [5, 'Other recreation services(4)'],
    'Hotel': [5, 'Lodging away from home(4)'],
    'Airlines': [6, 'Airline fares'],
    'Beverage': [4, 'Alcoholic beverages away from home'],
    'Car Rental': [5, 'Car and truck rental(4)'],
}

output = pd.DataFrame()
for f in xlsx_files2:
    df = pd.read_excel(f"{folder_path}\\{f}", skiprows=3).iloc[:,0:4].dropna(axis=0)
    yyyymm = os.path.basename(f).split('-')[-1].split('.')[0]
    df.columns = ['Level', 'Expenditure', 'Importance', 'CPI']
    df['Contribution'] = df['Importance'] * df['CPI'].astype('float')/100
    df['date'] = yyyymm
    for k, e in entries.items():
        if k == 'Core_svcs':
            rows_plus = (df.iloc[:,1] == 'Services less energy services')
            rows_minus = (df.iloc[:, 1] == 'Shelter')
            rows_minus2 = (df.iloc[:, 1] == 'Motor vehicle insurance')
            importance = df[rows_plus].iloc[:, 2].values[0] \
                         - df[rows_minus].iloc[:, 2].values[0] \
                         - df[rows_minus2].iloc[:, 2].values[0]
            contribution = (df[rows_plus].iloc[:,2:4].product(axis=1)/100).values[0] \
                           - (df[rows_minus].iloc[:,2:4].product(axis=1)/100).values[0] \
                            - (df[rows_minus2].iloc[:,2:4].product(axis=1)/100).values[0]
        else:
            rows = (df.iloc[:, 0] == e[0]) & (df.iloc[:, 1] == e[1])
            importance = df[rows].iloc[:, 2].values[0]
            contribution = (df[rows].iloc[:,2:4].product(axis=1)/100).values[0]
        tmp = pd.DataFrame([[1000, k, importance, contribution, yyyymm, -999]])
        output = pd.concat([output, tmp], ignore_index=True)
    for k, e in entries2.items():
        rows = (df.iloc[:, 0] == e[0]) & (df.iloc[:, 1] == e[1])
        cpi = df[rows].iloc[:, 3].values[0]
        importance = df[rows].iloc[:, 2].values[0]
        contribution = (df[rows].iloc[:,2:4].product(axis=1)/100).values[0]
        tmp = pd.DataFrame([[2000, k, importance, contribution, yyyymm, cpi]])
        output = pd.concat([output, tmp], ignore_index=True)
    for k, e in entries3.items():
        rows = (df.iloc[:, 0] == e[0]) & (df.iloc[:, 1] == e[1])
        cpi = df[rows].iloc[:, 3].values[0]
        importance = df[rows].iloc[:, 2].values[0]
        contribution = (df[rows].iloc[:,2:4].product(axis=1)/100).values[0]
        tmp = pd.DataFrame([[3000, k, importance, contribution, yyyymm, cpi]])
        output = pd.concat([output, tmp], ignore_index=True)
    for k, e in entries4.items():
        rows = (df.iloc[:, 0] == e[0]) & (df.iloc[:, 1] == e[1])
        cpi = df[rows].iloc[:, 3].values[0]
        importance = df[rows].iloc[:, 2].values[0]
        contribution = (df[rows].iloc[:,2:4].product(axis=1)/100).values[0]
        tmp = pd.DataFrame([[4000, k, importance, contribution, yyyymm, cpi]])
        output = pd.concat([output, tmp], ignore_index=True)
output.columns = ['Level', 'Expenditure', 'Importance',  'Contribution', 'date', 'CPI']

output_path = f'{folder_path}\inflation_comp.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    output.to_excel(writer, sheet_name='all', index=False)





