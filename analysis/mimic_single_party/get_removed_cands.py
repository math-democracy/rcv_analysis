import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import votekit.elections as vk
import pandas as pd
import multiprocessing
import csv
import os
import json

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_last_mentioned/keep_first/processed_data'

with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/scotland_first_place_ranks.json') as file:
    first_place_ranks = json.load(file)

def get_cands_to_keep(profile, num_cands, num_cands_to_keep):
    # get top4 plurality winners
        # if there are less than 5 candidates, then top4 and top5 are both the whole candidate list
    if num_cands > num_cands_to_keep:
        cands_to_keep_set = vk.Plurality(profile=profile, m=num_cands_to_keep, tiebreak='random').election_states[-1].elected
        cands_to_keep_set = [list(set(f)) for f in cands_to_keep_set]
        cands_to_keep = []
        for l in cands_to_keep_set:
            for c in l:
                cands_to_keep.append(c)
    else:
        cands_to_keep = list(profile.candidates)

    return cands_to_keep

for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                if filename == 'Ward06-Kilwinning_Preference-Profile-Kilwinning_copy.csv':
                    full_path = os.path.join(dirpath, filename)
                    
                    v =  mm.v_profile(full_path)

                    cands_to_keep = get_cands_to_keep(v, len(v.candidates), 4)
                    #print(cands_to_keep)
                    first_place = first_place_ranks[filename]
                    print(first_place)
                    first_place = sorted(first_place, key=first_place.get, reverse=True)[:4]
                    print(first_place)
                    # if sorted(first_place) != sorted(cands_to_keep):
                    #     print(filename, cands_to_keep, first_place)


                