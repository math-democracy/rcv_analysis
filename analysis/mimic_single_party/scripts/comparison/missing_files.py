import pandas as pd

og = pd.read_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/results/current/scotland.csv')
new = pd.read_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/stability/scotland_results_top4.csv')

list1 = og['file'].tolist()

list2 = new['file'].apply(lambda x: x.replace('raw_data/scotland/processed_data/','')).tolist()
print(len(list1),len(list2))
missing = [l for l in list1 if l not in list2]
for l in missing:
    print(f'"/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data/{l}",')
print(len(missing))