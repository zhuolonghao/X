import pandas as pd
import requests
from functools import reduce

my_items ={
    'All industry ex-high tech': 'Total_ex._computers,_communications_eq.,_and_semiconductors"',
    'Computer Equip': 'Computer_and_peripheral_equipment_NAICS=3341"',
    'Communication Equip': 'Communications_equipment_NAICS=3342"',
    'Semiconductors': 'Semiconductor_and_other_electronic_component_NAICS=3344"',
    'O&G E&P': 'Oil_and_gas_extraction_NAICS=211"',
    'O&G Support': 'Support_activities_for_mining_NAICS=213"',
    'Utility Electric': 'Electric_power_generation,_transmission,_and_distribution_NAICS=2211"',
    'Utility Natural Gas': 'Natural_gas_distribution_NAICS=2212"',
    'Auto and Parts': 'Motor_vehicles_and_parts_NAICS=3361-3"',
    'Auto': 'Automobile_and_light_duty_motor_vehicle_NAICS=33611"',
}
# for x in dfs1.keys():
#     if '213' in x.lower():
#         print(x)


# Step 1: Fetch the data from the URL
url = 'https://www.federalreserve.gov/releases/g17/ipdisk/ip_sa.txt' # industrial production
#url = 'https://www.federalreserve.gov/releases/g17/ipdisk/cap_sa.txt' # industrial capacity
#url = 'https://www.federalreserve.gov/releases/g17/ipdisk/utl_sa.txt' # industrial utilization
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Data fetched successfully.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
# Step 2: Read the raw text into a string
raw_text = response.text
lines = raw_text.splitlines()
dfs1 = {}
for i, line in enumerate(lines):
    items = line.strip().split()
    if any(char.isalpha() for char in items[1]):
        if i > 1:
            df = pd.DataFrame(data).set_index(0)
            df.columns = [x+1 for x in range(12)]
            dfs1[var_nm] = df
        var_nm = '_'.join(items[1:])
        data = []
    else:
        data.append(items[1:])

# Step 1: Fetch the data from the URL
url = 'https://www.federalreserve.gov/releases/g17/ipdisk/cap_sa.txt' # industrial capacity
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Data fetched successfully.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
# Step 2: Read the raw text into a string
raw_text = response.text
lines = raw_text.splitlines()
dfs2 = {}
for i, line in enumerate(lines):
    items = line.strip().split()
    if any(char.isalpha() for char in items[1]):
        if i > 1:
            df = pd.DataFrame(data).set_index(0)
            df.columns = [x+1 for x in range(12)]
            dfs2[var_nm] = df
        var_nm = '_'.join(items[1:])
        data = []
    else:
        data.append(items[1:])


# Step 1: Fetch the data from the URL
url = 'https://www.federalreserve.gov/releases/g17/ipdisk/utl_sa.txt' # industrial utilization
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Data fetched successfully.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
# Step 2: Read the raw text into a string
raw_text = response.text
lines = raw_text.splitlines()
dfs3 = {}
for i, line in enumerate(lines):
    items = line.strip().split()
    if any(char.isalpha() for char in items[1]):
        if i > 1:
            df = pd.DataFrame(data).set_index(0)
            df.columns = [x+1 for x in range(12)]
            dfs3[var_nm] = df
        var_nm = '_'.join(items[1:])
        data = []
    else:
        data.append(items[1:])

#
# for x in dfs3.keys():
#     if '3341' in x.lower():
#         print(x)

dfs = {}
for i, k in my_items.items():
    ip = pd.melt(dfs1[k].reset_index(names='year'), id_vars='year', var_name='month',
                 value_name='Ind.Prod')
    cap = pd.melt(dfs2[k].reset_index(names='year'), id_vars='year', var_name='month',
                 value_name='Capacity')
    utl = pd.melt(dfs3[k].reset_index(names='year'), id_vars='year', var_name='month',
                 value_name='Utilization')
    merged_df = reduce(lambda left, right: pd.merge(left, right, on=['year', 'month'], how='inner'), [ip, cap, utl])
    merged_df['Date'] =  pd.to_datetime(merged_df['year'].astype(str) + '-' + merged_df['month'].astype(str) + '-01')
    merged_df['variable'] = i
    dfs[i] = merged_df
pd.concat(dfs.values())\
    .to_excel('manufacturing.xlsx', index=False)