import pandas as pd
import os
import json

borda_file = '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/borda_scores/scotland_borda_scores.json'
mention_file =  '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/mention_scores/scotland_mention_scores.json'
first_place_file = '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/scotland_first_place_ranks.json'

with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/metadata/party_breakdown.json') as file:
    party_breakdown = json.load(file)
    
def run_on_files(condense_method, data_dir):
    output_file = f'/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/vote_split/metadata/first_place_votes/{condense_method}.json'

    data = {}

    for dirpath, dirnames, filenames in os.walk(data_dir):
            for filename in filenames:
                print("RUNNING: ", filename)
                if filename.endswith('.csv'):
                    full_path = os.path.join(dirpath, filename)
                    
                    df = pd.read_csv(full_path, low_memory=False, dtype=str)

                    candidates = set()
                    for c in df.columns:
                        if 'rank' in c: 
                            candidates.update(list(df[c].unique()))

                    if 'skipped' in candidates:
                        candidates.remove('skipped')

                    value_counts = df['rank1'].value_counts(ascending=False).to_dict()
                    total_votes = float(sum(value_counts.values()))
                    
                    pct_of_total = dict.fromkeys(candidates,0)

                    for candidate in candidates:
                        if candidate in value_counts:
                            cand_first_count = value_counts[candidate]
                        else:
                            cand_first_count = 0

                        pct_of_total[candidate] = cand_first_count / total_votes

                    pct_of_total = {k: v for k, v in sorted(pct_of_total.items(), key=lambda item: item[1], reverse=True)}
                    data[full_path.replace(data_dir + '/','')] = pct_of_total

    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

# condense_method = f'first_place_condense_scotland'
# data_dir = '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/processed_data'

# data_dirs = ['/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/borda_score/processed_data',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/mention_score/processed_data',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/first_place_score/processed_data',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/borda_tiebreaker/processed_data',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/mention_tiebreaker/processed_data',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/first_place_tiebreaker/processed_data',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/keep_first_mentioned',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/keep_last_mentioned',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/australia/processed_data',
#              '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data']

# condense_methods = ['borda_score_scotland',
#                     'mention_score_scotland',
#                     'first_place_score_scotland',
#                     'borda_tiebreaker_scotland',
#                     'mention_tiebreaker_scotland',
#                     'first_place_tiebreaker_scotland',
#                     'keep_first_scotland',
#                     'keep_last_scotland',
#                     'uncondensed_america',
#                     'uncondensed_australia',
#                     'uncondensed_scotland']

condense_methods = {'/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/borda_score/processed_data': 'borda_score_scotland',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/mention_score/processed_data': 'mention_score_scotland',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/first_place_score/processed_data': 'first_place_score_scotland',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/borda_tiebreaker/processed_data': 'borda_tiebreaker_scotland',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/mention_tiebreaker/processed_data': 'mention_tiebreaker_scotland',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/first_place_tiebreaker/processed_data': 'first_place_tiebreaker_scotland',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/keep_first_mentioned': 'keep_first_scotland',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/condensed_elections/keep_last_mentioned': 'keep_last_scotland',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data': 'uncondensed_america',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/australia/processed_data': 'uncondensed_australia',
                    '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data': 'uncondensed_scotland',}

for k in condense_methods:
    print(condense_methods[k])
    run_on_files(condense_methods[k],k)