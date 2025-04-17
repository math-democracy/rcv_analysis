import pandas as pd
import os
import json

borda_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/borda_scores/scotland_borda_scores.json'
mention_file =  '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/mention_scores/scotland_mention_scores.json'
first_place_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/scotland_first_place_ranks.json'

with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/metadata/party_breakdown.json') as file:
    party_breakdown = json.load(file)

def get_condensed_cands(filepath, filename, method):
    if method == 'borda':
        with open(borda_file) as file:
            scores = json.load(file)
    elif method == 'mention':
        with open(mention_file) as file:
            scores = json.load(file)
    elif method == 'first_place':
        with open(first_place_file) as file:
            scores = json.load(file)

    party_info = party_breakdown[filepath]
    candidate_dict = party_info['party_dict']

    # get corresponding scores for filename
    if filename in scores:
        candidate_scores = scores[filename]
    else:
        if filename == '3_dalkeith_preference_profile_open_from_within_ms_word_or_similar.csv':
            new_filename = ['Ward3-Dalkeith_ward_3_dalkeith_preference_profile_open_from_within_ms_word_or_similar.csv']
        elif filename == 'dalkeith_preference_profile_open_from_within_ms_word_or_similar.csv':
            new_filename = ['Ward6-MidlothianSouth_ward_6_midlothian_south_dalkeith_preference_profile_open_from_within_ms_word_or_similar.csv']
        else:
            new_filename = [f for f in scores if f.endswith(filename)]

        candidate_scores = scores[new_filename[0]]
    
    if candidate_scores:
        grouped_by_party = {i: [j[0] for j in j] for i, j in groupby(sorted(candidate_dict.items(), key = lambda x : x[1]), lambda x : x[1])}
        cands_to_keep = set()
        for party in grouped_by_party.values():
            keep = [i for i in candidate_dict.keys() if candidate_scores[i] == max(candidate_scores[title] for title in party)]
            cands_to_keep.update(keep)
    else:
        return None

    return list(cands_to_keep)
    
def run_on_files(condense_method, data_dir):
    output_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/vote_split/metadata/{condense_method}.json'

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

                        pct_of_total[candidate] = round(cand_first_count / total_votes * 100, 2)

                    pct_of_total = {k: v for k, v in sorted(pct_of_total.items(), key=lambda item: item[1], reverse=True)}
                    data[full_path.replace(data_dir + '/','')] = pct_of_total

    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

condense_method = f'first_place_condense_scotland'
data_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/processed_data'
run_on_files(condense_method, data_dir)