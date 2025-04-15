import pandas as pd

METHOD = 'first_place'
# filepath = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/{METHOD}_score/stability/scotland_results_top4.csv'
# filepath = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_last_mentioned/keep_first/scotland_results_top4.csv'

filepath = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/{METHOD}/scotland_results_top4.csv'
df = pd.read_csv(filepath)

cols_to_keep = [c for c in df.columns if not c.startswith('top4')]
print(df.columns)
print(cols_to_keep)

df = df[cols_to_keep]
print(df.columns)

df.to_csv(filepath[:-16]+'current.csv', index=False)