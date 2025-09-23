"""This file generates condensed elections data for the following condensation methods:
    keep_first_mentioned, keep_last_mentioned"""
import pandas as pd
import numpy as np
import csv
import os
import re
import json
from itertools import groupby

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

def keep_first(filepath, output):
    ballots, cands, candidate_parties = get_ballots_cands(filepath)

    new_ballots = []

    for ballot in ballots:
        party_ballot = []
        for i in range(1,len(ballot)-1):
            party_ballot.append(candidate_parties[ballot[i]])
        
        keep = []
        seen_parties = set()
        for i in range(0, len(party_ballot)):
            if party_ballot[i] not in seen_parties:
                
                keep.append(ballot[i+1])
                seen_parties.add(party_ballot[i])
        
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


def keep_last(filepath, output):
    ballots, cands, candidate_parties = get_ballots_cands(filepath)

    new_ballots = []
    for ballot in ballots:
        party_ballot = []
        for i in range(1,len(ballot)-1):
            party_ballot.append(candidate_parties[ballot[i]])

        keep = []
        seen_parties = set()
        for i in range(len(party_ballot)-1, -1, -1):
            if party_ballot[i] not in seen_parties:
                keep.insert(0,ballot[i+1])
                seen_parties.add(party_ballot[i])
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
    root_dir = 'raw_data/preference_profiles/scotland' # UPDATE TO WHERE BLT DATA IS STORED eg. /Users/belle/Downloads/Scotland data, LEAP parties
    method = 'last'
    output_folder = f'analysis/mimic_single_party/methods/first_last_mentioned/keep_{method}/processed_data' # UPDATE TO WHERE CSV DATA SHOULD BE SAVED eg. /Users/belle/Desktop/build/rcv_proposal/data

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                full_path = os.path.join(dirpath, filename)
                lowest_folder = os.path.basename(os.path.dirname(full_path))
                output = os.path.join(output_folder, lowest_folder)

                if not os.path.exists(output):
                    os.makedirs(output)

                try:
                    if method == 'last':
                        print(f"RUNNING KEEP LAST: {filename}")
                        keep_last(full_path, output)
                    else:
                        print(f"RUNNING KEEP FIRST: {filename}")
                        keep_first(full_path, output)

                    with open(f'analysis/mimic_single_party/methods/first_last_mentioned/keep_{method}/supporting_files/keep_{method}_PROCESSED.txt', mode='a') as processed_file:
                        processed_file.write(f'"{filename}",\n')
                except Exception as e:
                    with open(f'analysis/mimic_single_party/methods/first_last_mentioned/keep_{method}/supporting_files/keep_{method}_ERROR.txt', mode='a') as error_file:
                        error_file.write(f'"{filename}",\n')
                
if __name__ == '__main__':
    main()