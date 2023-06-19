import pandas as pd
import numpy as np

def replace_county_with_state(x):
    return str(x).replace('County', 'State')

def replace_nan(x):
    return str(x).replace('nan', "")

Q_id_list = ["Q1", "Q2", "Q3", "Q4", "Q7", "Q12", "Q13", "Q17", "Q18", "Q22", "Q23", "Q24", "Q26", "Q28", "Q34", "Q36", "Q37"]

Queries_df = pd.read_csv("./resources/rules3.tsv", sep='\t')


Queries_df['Graph ID'].fillna(method='ffill', inplace=True)
print(Queries_df.head())
states_df = Queries_df[Queries_df['Graph ID'].isin(Q_id_list)]
states_df = states_df.applymap(replace_county_with_state)
states_df.loc[states_df['Graph ID'].duplicated(), 'Graph ID'] = np.nan
states_df = states_df.applymap(replace_nan)
print(states_df.head(20))

states_df.to_csv('./resources/state_rules.tsv', na_rep='', sep='\t', index=False)












