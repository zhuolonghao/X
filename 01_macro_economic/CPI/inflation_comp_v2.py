import os
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

print("Starting the job")
import time


# https://www.bls.gov/cpi/tables/supplemental-files/
#folder_path = os.getcwd()
# List all .xlsx files in the folder
folder_path = "C:\\Users\\longh\\Desktop\\X\\01_macro_economic\\CPI"
xlsx_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
xlsx_files2 = [f for f in xlsx_files if f.startswith('news-release-table7')]

output = pd.DataFrame()
for f in xlsx_files2:
    df = pd.read_excel(f"{folder_path}\\{f}", skiprows=3).iloc[:,0:4].dropna(axis=0)
    yyyymm = os.path.basename(f).split('-')[-1].split('.')[0]
    df.columns = ['Level', 'Expenditure', 'Importance', 'CPI']
    df['Contribution'] = df['Importance'] * df['CPI'].astype('float')/100
    df['date'] = yyyymm
    df['Cleaned_Expenditure'] = df['Expenditure'].str.replace(r'\(\d+\)', '', regex=True).str.strip()
    output = pd.concat([output, df], ignore_index=True)
output.columns = ['Level', 'Expenditure', 'Importance',  'CPI', 'Contribution', 'date', 'Cleaned_Expenditure']


print("Exporting to inflation_comp.xlsx")
time.sleep(3)
rows = output['Level'] <= 5
output = output[rows]
output_path = f'{folder_path}\inflation_comp_v2.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    output.to_excel(writer, sheet_name='all', index=False)




