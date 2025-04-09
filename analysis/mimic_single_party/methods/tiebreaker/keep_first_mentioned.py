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

    #party_groups = {i: [j[0] for j in j] for i, j in groupby(sorted(candidates.items(), key = lambda x : x[1]), lambda x : x[1])}

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

def keep_by_score(filepath, output, scores):
    ballots, cands, candidate_parties = get_ballots_cands(filepath)

    # get corresponding scores for filename
    filename = filepath.split('/')[-1]
    if filepath.split('/')[-1] in scores:
        candidate_scores = scores[filename]
    else:
        if filename == '3_dalkeith_preference_profile_open_from_within_ms_word_or_similar.csv':
            new_filename = ['Ward3-Dalkeith_ward_3_dalkeith_preference_profile_open_from_within_ms_word_or_similar.csv']
        elif filename == 'dalkeith_preference_profile_open_from_within_ms_word_or_similar.csv':
            new_filename = ['Ward6-MidlothianSouth_ward_6_midlothian_south_dalkeith_preference_profile_open_from_within_ms_word_or_similar.csv']
        else:
            new_filename = [f for f in scores if f.endswith(filename)]

        candidate_scores = scores[new_filename[0]]

    # create a ranking based on borda score
    candidate_scores = dict(sorted(candidate_scores.items(), reverse=True, key=lambda item: item[1]))

    new_ballots = []

    for ballot in ballots:
        party_dict = {}

        # range starts from 1 and goes to the second last bc first entry is quantity and last is 0
        for i in range(1,len(ballot)-1):
            party = candidate_parties[ballot[i]]
            if party in party_dict:
                party_dict[party].append((ballot[i],cands[ballot[i]-1]))
            else:
                party_dict[party] = [(ballot[i],cands[ballot[i]-1])]

        cands_to_keep = []

        for party in party_dict:
            candidates = party_dict[party]
            if len(candidates) == 1:
                cands_to_keep.append(candidates[0][0])
            else:
                keep, score = candidates[0][0], get_score(candidate_scores, candidates[0])
                for c in candidates:
                    c_score = get_score(candidate_scores, c)
                    if c_score >= score:
                        keep, score = c[0], c_score

                cands_to_keep.append(keep)

        new_ballot = []
        for i in range(1,len(ballot)-1):
            if ballot[i] in cands_to_keep:
                new_ballot.append(ballot[i])

        new_ballot.append(0)
        new_ballot.insert(0,ballot[0])

        new_ballots.append(new_ballot)

        # print(ballot)
        # print(party_dict)
        # print(new_ballot)
        # print(candidate_scores, '\n')

    new_pref_profile = {
        "num_positions": None,
        "num_candidates": len(cands),
        "ballots": new_ballots,
        "candidates": cands,
    }

    parse_to_csv(new_pref_profile, f"{output}/{filepath.split('/')[-1]}")

def get_score(scores, cand):
    if cand[1] in scores:
        return scores[cand[1]]
    else:
        for i in scores:
            if cand[1] in i:
                return scores[i]
            
    return None
        
def parse_to_csv(data, outfilepath):
    #candidates = [normalize_parties(c) for c in data['candidates']]
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
    root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/preference_profiles/scotland' # UPDATE TO WHERE BLT DATA IS STORED eg. /Users/belle/Downloads/Scotland data, LEAP parties
    method = 'first_place'

    if method == 'last' or method == 'first':
        output_folder = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_last_mentioned/keep_{method}/processed_data' # UPDATE TO WHERE CSV DATA SHOULD BE SAVED eg. /Users/belle/Desktop/build/rcv_proposal/data
    else:
        output_folder = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/{method}/processed_data'
    
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
                    elif method == 'first':
                        print(f"RUNNING KEEP FIRST: {filename}")
                        keep_first(full_path, output)
                    elif method == 'borda':
                        print(f"RUNNING KEEP BORDA: {filename}")
                        with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/borda_scores/scotland_borda_scores.json') as file:
                            borda_scores = json.load(file)
                        keep_by_score(full_path, output, borda_scores)
                    elif method == 'mention':
                        print(f"RUNNING KEEP MENTION: {filename}")
                        with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/mention_scores/scotland_mention_scores.json') as file:
                            mention_scores = json.load(file)
                        keep_by_score(full_path, output, mention_scores)
                    elif method == 'first_place':
                        print(f"RUNNING KEEP FIRST PLACE: {filename}")
                        with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/scotland_first_place_ranks.json') as file:
                            first_place_scores = json.load(file)
                        keep_by_score(full_path, output, first_place_scores)

                    with open(f'{output_folder[:-14]}{method}_PROCESSED.txt', mode='a') as processed_file:
                        processed_file.write(f'"{filename}",\n')
                except Exception as e:
                    with open(f'{output_folder[:-14]}{method}_ERROR.txt', mode='a') as error_file:
                        error_file.write(f'"{filename}",\n')
                
if __name__ == '__main__':
    # with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/borda_scores/scotland_borda_scores.json') as file:
    #     borda_scores = json.load(file)
    # filepath = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/preference_profiles/scotland/n-ayrshire22/Ward08-IrvineEast_Preference-Profile-Irvine-East_copy.csv'
    # keep_by_score(filepath, '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/borda/processed_data', borda_scores)
    main()