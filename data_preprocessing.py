import pandas as pd

df = pd.read_excel('outcome/metab249+30+31example.xlsx', sheet_name='metabolite249', index_col=0)
df = df.drop(['title', 'Order', 'Suborder', 'Group', 'Subgroup'], axis=1)
df_meta = pd.read_excel('outcome/metab249+30+31example.xlsx', sheet_name='Sheet3', index_col=0)

df_result = df.merge(df_meta, how='left', on='field_id')
list_col = df_result.columns.to_list()
list_new_col = list_col[0:1] + list_col[-7:] + list_col[1:-7]
df_result = df_result[list_new_col]
df_result = df_result.sort_values(['drug_exposure', 'Order', 'Suborder']).reset_index(drop=True)
df_result.to_csv('outcome/metab_all.csv')