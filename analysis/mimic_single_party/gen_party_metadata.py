import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import votekit.elections as v
import os
import pandas as pd
import json
from collections import Counter
from itertools import groupby

with open('./rcv_proposal/analysis/mimic_single_party/metadata/party_breakdown.json') as file:
    party_breakdown = json.load(file)

borda_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/borda_scores/scotland_borda_scores.json'
mention_file =  '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/mention_scores/scotland_mention_scores.json'
first_place_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/scotland_first_place_ranks.json'


files = {}
def party_blocs(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                print(f'processing: {filename}')
                full_path = os.path.join(dirpath, filename)
                prof = mm.v_profile(full_path)
                candidates = [c for c in prof.candidates if c != 'skipped']

                parties = []
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

                    parties.append(party)
            
                borda_cands = get_condensed_cands(full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/',''), filename, 'borda')
                mention_cands = get_condensed_cands(full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/',''), filename, 'mention')
                first_place_cands = get_condensed_cands(full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/',''), filename, 'first_place')
                prof =  mm.v_profile(full_path)
                plurality_cands = get_cands_to_keep(prof,len(prof.candidates),4)

                #print(candidates, parties)
                info = {'num_cands': {'og': len(candidates), 'parties': len(Counter(parties)), 'borda': len(borda_cands), 'mention': len(mention_cands), 'first_place': len(first_place_cands)},
                        'candidates': candidates,
                        'party_dict': party_dict,
                        'parties': Counter(parties),
                        'borda_cands': borda_cands,
                        'mention_cands': mention_cands,
                        'first_place_cands': first_place_cands,
                        'plurality_cands': plurality_cands}
                
                files[full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')] = info

    return files

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

    if filename in scores:
        candidate_scores = scores[filename]
        grouped_by_party = {i: [j[0] for j in j] for i, j in groupby(sorted(candidate_dict.items(), key = lambda x : x[1]), lambda x : x[1])}
        cands_to_keep = set()
        for party in grouped_by_party.values():
            keep = [i for i in candidate_dict.keys() if candidate_scores[i] == max(candidate_scores[title] for title in party)]
            cands_to_keep.update(keep)
    else:
        cands_to_keep = []
        if method == 'borda':
            with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/metadata/no_borda_score.txt', "a") as no_borda:
                no_borda.write(f"'{filepath}',\n")

    return list(cands_to_keep)

def get_cands_to_keep(profile, num_cands, num_to_keep):
    # get top4 plurality winners
        # if there are less than 5 candidates, then top4 and top5 are both the whole candidate list
    if num_cands > num_to_keep:
        cands_to_keep = v.Plurality(profile=profile, m=num_to_keep, tiebreak='random').election_states[-1].elected
        cands_to_keep = [list(w)[0] for w in cands_to_keep]
    else:
        cands_to_keep = profile.candidates

    return cands_to_keep

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data'
method = 'party_blocs'

def main():
    if method == 'party_blocs':
        party_blocs(root_dir)

    output_file = f"/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/metadata/{method}.json"
    with open(output_file, "w") as f:
        json.dump(files, f, indent=4)

if __name__ == '__main__':
    main()