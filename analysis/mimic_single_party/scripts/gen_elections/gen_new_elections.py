import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import os
import pandas as pd
import json
from collections import Counter
from itertools import groupby

files = {}

borda_file = './analysis/fringe/borda_scores/scotland_borda_scores.json'
mention_file =  './analysis/fringe/mention_scores/scotland_mention_scores.json'
first_place_file = './analysis/first_place_analysis/scotland_first_place_ranks.json'

def gen_party_dict(candidates):
    party_dict = {}
    for candidate in candidates:
        if candidate[0] == "(":
            party = candidate[1:candidate.find(")")]
        else:
            left = candidate.rfind("(")
            right = candidate[left:].rfind(")")
            if right == -1:
                right = -1
            else:
                right = left + right
            party = candidate[left+1:right]

        if party != 'Ind' and party != 'UNKNOWN':
            party_dict[candidate] = party
        else:
            party_dict[candidate] = candidate

    return party_dict

# Open and read the JSON file
with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/party_breakdown.json', 'r') as file:
    party_info = json.load(file)

def get_condensed_cands(filepath, method, candidates: Optional[list] = None):
    filename = filepath.split('/')[-1]

    # load scores file based on what metric you wish to condense on
    if method == 'borda':
        with open(borda_file) as file:
            scores = json.load(file)
    elif method == 'mention':
        with open(mention_file) as file:
            scores = json.load(file)
    elif method == 'first_place':
        with open(first_place_file) as file:
            scores = json.load(file)

    # if no candidates given, get candidates
    if candidates is None:
        prof = mm.v_profile(filepath)
        candidates = prof.candidates

    # create dictionary storing each candidate's party
    cands = [c for c in candidates if c != 'skipped']
    candidate_dict = gen_party_dict(cands)

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
    
    # condense candidates based on highest scorer
    if candidate_scores:
        grouped_by_party = {i: [j[0] for j in j] for i, j in groupby(sorted(candidate_dict.items(), key = lambda x : x[1]), lambda x : x[1])}
        cands_to_keep = set()
        for party in grouped_by_party.values():
            keep = [i for i in candidate_dict.keys() if candidate_scores[i] == max(candidate_scores[title] for title in party)]
            cands_to_keep.update(keep)
    else:
        return None

    return list(cands_to_keep)

def process_files_party_bloc(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                print(f'processing: {filename}')
                full_path = os.path.join(dirpath, filename)

                df = pd.read_csv(full_path)

                file_key = full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')
                consolidate_key = party_info[file_key]['party_dict']

                df.replace(consolidate_key, inplace=True)

                output_path = full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data/', '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/data/')
                #print('/'.join(output_path.split('/')[:-1]))
                if not os.path.exists('/'.join(output_path.split('/')[:-1])):
                    os.makedirs('/'.join(output_path.split('/')[:-1]))

                df.to_csv(output_path, index=False)

def process_files_scores(root_dir, method):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                print(f'processing: {filename}')
                full_path = os.path.join(dirpath, filename)
                
                cands_to_keep = get_condensed_cands(full_path, 'borda')




root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data'
process_files(root_dir)
