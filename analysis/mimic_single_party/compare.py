import pandas as pd

single_party = pd.read_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/results/scotland_results_top4.csv')
single_party['merge_key'] = single_party['file'].apply(lambda x: x.replace('analysis/mimic_single_party/data/',''))

multi_party = pd.read_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/scotland_results_top4.csv')
multi_party['merge_key'] = multi_party['file'].apply(lambda x: x.replace('raw_data/scotland/processed_data/',''))

merged = single_party.merge(multi_party, on='merge_key', suffixes=['_single','_multi'])

columns = merged.columns
columns = [x for x in columns if 'top4_' not in x and 'numCands' not in x and 'merge_key' not in x]
columns.sort()
columns.insert(0,'numCands_single')
columns.insert(0,'numCands_multi')
columns.insert(0,'merge_key')

merged = merged[columns]
merged['numCands_single'] = merged['numCands_single'] - 1
merged['numCands_multi'] = merged['numCands_multi'] - 1

merged = merged.rename({'merge_key':'file'})


merged.to_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/results/single_v_multi_comparison.csv', index=False)
#print(merged.columns)
