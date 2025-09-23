"""This file generates condensed elections for the following methods: 
    borda_score, mention_score, first_place_score"""
import pandas as pd
import numpy as np
import csv
import os
import re
import json
from itertools import groupby

borda_file = 'analysis/fringe/borda_scores/scotland_borda_scores.json'
mention_file =  'analysis/fringe/mention_scores/scotland_mention_scores.json'
first_place_file = 'analysis/first_place_analysis/scotland_first_place_ranks.json'

with open('analysis/mimic_single_party/metadata/party_breakdown.json') as file:
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
    

def get_party(candidate):
    if candidate == '[]':
        return candidate
    
    if candidate[3] == "(":
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
        return f"{party}"
    else:
        return candidate

def get_ballots_cands(filepath):
    with open(filepath, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]

    lines = [re.sub(r',\s*$', '', line) for line in lines] #to deal with , at the end of csv files
    
    metadata = lines[0].split()
    num_candidates = int(metadata[0])
    
    ballots = []
    i = 1
    
    while lines[i].strip() != "0":
        ballot_line = lines[i].strip()
        ballots.append(list(map(int, ballot_line.split())))
        i += 1

    candidate_start_index = len(ballots) + 2

    candidate_parties = {i:'' for i in range(1,num_candidates)}
    candidates = []
    for i in range(0,num_candidates):
        party = get_party(lines[candidate_start_index + i])
        candidate_parties[i+1] = party
        candidates.append(lines[candidate_start_index + i])

    return ballots, candidates, candidate_parties

def keep_cands(filepath, output, condensed_cands):
    ballots, cands, candidate_parties = get_ballots_cands(filepath)

    print(cands)
    print(candidate_parties)
    print(condensed_cands)
    

    new_ballots = []

    for ballot in ballots:
        keep = []
        for i in range(1,len(ballot)-1):
            print(f"'{cands[ballot[i]-1]}'", condensed_cands)
            if cands[ballot[i]-1] in condensed_cands:
                keep.append(ballot[i])
                
        keep.append(0)
        keep.insert(0,ballot[0])

        new_ballots.append(keep)

    new_pref_profile = {
        "num_positions": None,
        "num_candidates": len(cands),
        "ballots": new_ballots,
        "candidates": cands,
    }

    parse_to_csv(new_pref_profile, f"{output}/{filepath.split('/')[-1]}")


def parse_to_csv(data, outfilepath):
    candidates = data['candidates']
    ranks = ["rank" + str(i + 1) for i in range(len(candidates))]
    ballots = [b for b in data['ballots']]

    voter_id = 0

    all_votes = []
    for ballot in ballots:
        for voter in range(ballot[0]):
            c = {"voterId": voter_id}
            c.update({rank: "skipped" for rank in ranks})
            for index, vote in enumerate(ballot[1:-1]):
                c[ranks[index]] = candidates[vote - 1]
            c['numSeats'] = data['num_positions']
            c['numCands'] = data['num_candidates']
            voter_id += 1
            all_votes.append(c)
    
    keys = all_votes[0].keys()

    print(f'WRITING TO: {outfilepath}')
    with open(outfilepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(keys)
        for vote in all_votes:
            row = [vote.get(key, '') for key in keys]
            writer.writerow(row)

def main():
    root_dir = 'raw_data/preference_profiles/scotland' # UPDATE TO WHERE BLT DATA IS STORED
    method = 'mention'
    output_folder = f'analysis/mimic_single_party/condensed_elections/{method}_score/processed_data'
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if (filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt')):
                full_path = os.path.join(dirpath, filename)
                lowest_folder = os.path.basename(os.path.dirname(full_path))
                output = os.path.join(output_folder, lowest_folder)
                
                if not os.path.exists(output):
                    os.makedirs(output)
                
                condensed_cands = get_condensed_cands(full_path.replace('raw_data/preference_profiles/scotland','raw_data/scotland/processed_data'), filename, method)
                for i in range(len(condensed_cands)):
                    condensed_cands[i] = condensed_cands[i].rstrip().lstrip()
                
                keep_cands(full_path, output, condensed_cands)

                
if __name__ == '__main__':
    main()