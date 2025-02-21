import pandas as pd
import numpy as np

folder = '02_screening/1_Fundamentals/data'
sheets = ['meta',
    'net_income_q', 'roa_q', 'cfo_q',
    'shares_q', 'leverage_q', 'curr_ratio_q',
    'turnover_q',  'ebitda_margin_q'
]
files = ['SP500_components.xlsx', 'SP400_components.xlsx', 'SP600_components.xlsx']
_dfs = {}
for f in files:
    print(f"read in {f}")
    _dfs2 = {}
    for s in sheets:
        tmp = pd.read_excel(f"{folder}/{f}", sheet_name=s, skiprows=2)
        tmp2 = tmp.drop(np.where(tmp.iloc[:, 1] == '#INVALID COMPANY ID')[0])
        if s != 'meta':
            tmp2 = tmp2.melt(id_vars=['Constituents'], var_name='date')
            tmp2['date'] = tmp2['date'].str[3:] + tmp2['date'].str[:3]
            tmp2['variable'] = s
            _dfs2[s] = tmp2
        else:
            meta = tmp2
    tmp3 = pd.concat(_dfs2, axis=0, ignore_index=True).set_index('Constituents')
    tmp4 = pd.merge(meta, tmp3, on='Constituents', how='inner')
    tmp4['index'] = f[:5]
    _dfs[f] = tmp4

output = pd.concat(_dfs.values(), ignore_index=True)\
output['value_lag4'] = output.groupby(['Constituents','variable'])['value'].shift(-4)

output.to_excel('02_screening/1_Fundamentals/fundamentals.xlsx')
print('Completed')
