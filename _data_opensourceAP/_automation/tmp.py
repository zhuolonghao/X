import pandas as pd
import numpy as np
time_frame = ['2006', '2007',  '2017', '2018', '2019']

df = pd.read_excel("_data_opensourceAP/2024/PredictorPortsFull.xlsx", sheet_name='PredictorPortsFull')
df['year'] = df['date'].dt.strftime('%Y')
rows = df['year'].isin(time_frame)
df = df[rows]

df.head(10)
df_grp0 = df.groupby(['signalname','port'])['Nlong'].mean().reset_index()
df_grp0 = df_grp0.groupby('signalname').tail(2).groupby('signalname').head(1).set_index('signalname')
df_grp = df.groupby(['signalname','port'])['ret'].mean().reset_index()
df_grp['diff'] = df_grp.groupby('signalname')['ret'].diff()
df_grp['diff_sign'] = np.where(df_grp['diff'] > 0, 1, -1)
df_grp['diff_sign_sum'] = df_grp.groupby('signalname')['diff_sign'].cumsum()
df_grp['index'] = df_grp.groupby('signalname').cumcount()+1

df_grp_shorten = df_grp.groupby('signalname').tail(2)
df_grp_ls = df_grp_shorten.groupby('signalname').tail(1)
df_grp_cnt = df_grp_shorten.groupby('signalname').head(1)

df_grp_cnt_filter = df_grp_cnt[abs(df_grp_cnt['diff_sign_sum']) > 0.5*df_grp_cnt['index']]
df_grp_ls_filter = df_grp_ls[abs(df_grp_ls['ret']) > 0.5]
outcome = pd.merge(df_grp_cnt_filter, df_grp_ls_filter['signalname'], on='signalname', how='inner')
outcome2 = df_grp_ls[abs(df_grp_ls['ret']) > 1]

signalnames = set(outcome.signalname.to_list() + outcome2.signalname.to_list() )
df_grp_wide = pd.pivot_table(df_grp, index='signalname', columns='port', values='ret')
df_grp_wide[df_grp_wide.index.isin(signalnames)]\
    .join(df_grp0, how='left')\
    .sort_values('LS', ascending=False)\
    .to_excel("_data_opensourceAP/2024/outcome.xlsx")