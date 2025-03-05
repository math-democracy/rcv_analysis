import json
import pandas as pd
import numpy as np
import csv
from collections import Counter, defaultdict
import time
import sys
import os



# Function to process each voter's rankings, ignoring "overvote"
def process_rankings(row):
    seen_candidates = set()
    ranking = defaultdict(list)
    rank = 1
    
    for i in range(1, num_ranks+1):
        candidate = row[f'rank{i}']
        if candidate != 'overvote' and candidate != 'skipped' and candidate not in seen_candidates:
            ranking[rank].append(candidate)
            seen_candidates.add(candidate)
            rank += 1
    
    return {c: r for r, cs in ranking.items() for c in cs}

# Function to convert rankings (in tuple format) to indices and create dictionaries as keys
def ranking_to_indices(ranking, candidate_to_index):
    ranking_dict = {}
    for rank, candidate in enumerate(ranking, start=1):
        ranking_dict[candidate_to_index.get(candidate, -1)] = rank
    return ranking_dict

def process_csv(file_name):
    election_data = pd.read_csv(file_path)
    
    ### used for scottish/australian
    # seat_num = election_data['numSeats'][0]
    ### used for american/civs
    if 'Num seats' in election_data.keys():
        seat_num = election_data['Num seats'][0]
    elif 'Num Seats' in election_data.keys():
        seat_num = election_data['Num Seats'][0]
    else:
        seat_num = 0
    
    # Apply the function and count occurrences of each ranking
    election_data['processed_rankings'] = election_data.apply(process_rankings, axis=1)
    # print(election_data)
    ranking_counts = Counter(election_data['processed_rankings'].apply(tuple))

    # Create candidate list and set "Write-in" index last
    candidates = [c for c in set().union(*[r for r in ranking_counts])]

    # Convert rankings to indices format
    candidate_to_index = {candidate: index for index, candidate in enumerate(candidates)}

    # Display the candidates and their indices for reference
    candidates_with_indices = {index: candidate for candidate, index in candidate_to_index.items()}
    # print(candidates_with_indices)

    # Creating rankings with indices, ignoring ballots with "overvote"
    rankings = [ranking_to_indices(ranking, candidate_to_index) for ranking, count in ranking_counts.items()]
    rcounts = [count for ranking, count in ranking_counts.items()]

    return rankings, rcounts, candidates_with_indices, seat_num  

def get_num_ranks(file_name):
    election_data = pd.read_csv(file_path)
    column_names_list = election_data.columns.tolist()
    num_ranks=0
    for item in column_names_list:
        if 'rank' in item:
            num_ranks+=1
    return num_ranks





lxn_names = []
##### Scottish data
base_name = '../../raw_data/scotland/processed_data'
destination_base = '../../raw_data/preference_profiles/scotland'
##### Australia data
# base_name = '../australia/processed_data'
# destination_base = '../preference_profiles/australia'
##### American data
# base_name = '../american'
# destination_base = '../preference_profiles/american'

for folder_name in os.listdir(base_name):
    destination_folder_name = destination_base + '/' + folder_name
    if not os.path.exists(destination_folder_name):
        os.makedirs(destination_folder_name)
    
    for file_name in os.listdir(base_name+'/'+folder_name):
        file_path = base_name+'/'+folder_name+'/'+file_name
        lxn_names.append(file_path)
        destination_path = destination_base+'/'+folder_name+'/'+file_name    
    
        sys.stdout.write('\r')
        sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
        sys.stdout.flush()

        num_ranks = get_num_ranks(file_path)
        rankings, rcounts, cands_with_inds, seat_num = process_csv(file_path)
        
        rows = [[str(len(cands_with_inds))+' '+str(seat_num)]]
        
        ballot_list = []
        for i in range(len(rankings)):
            cand_list = [cand+1 for cand in rankings[i].keys()]
            # cand_list = list(rankings[i].keys())
            ballot_list.append([rcounts[i], cand_list])
        
        ballot_list.sort(key = lambda x: x[1])
        
        for ballot in ballot_list:
            string = str(ballot[0])
            for cand in ballot[1]:
                string += ' '+str(cand)
            string += ' 0'
            rows.append([string])
        
        rows.append(['0'])
        
        for name in cands_with_inds.values():
            rows.append([name])
            
        
        with open(destination_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

        
        
            
            
        
        
        
##### CIVS data (no subfolders for this data)
# base_name = '../civs'
# destination_base = '../preference_profiles/civs'

# for file_name in os.listdir(base_name):
#     file_path = base_name+'/'+file_name
#     lxn_names.append(file_path)
#     destination_path = destination_base+'/'+file_name    

#     sys.stdout.write('\r')
#     sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
#     sys.stdout.flush()

#     num_ranks = get_num_ranks(file_path)
#     rankings, rcounts, cands_with_inds, seat_num = process_csv(file_path)
    
#     rows = [[str(len(cands_with_inds))+' '+str(seat_num)]]
    
#     ballot_list = []
#     for i in range(len(rankings)):
#         cand_list = [cand+1 for cand in rankings[i].keys()]
#         # cand_list = list(rankings[i].keys())
#         ballot_list.append([rcounts[i], cand_list])
    
#     ballot_list.sort(key = lambda x: x[1])
    
#     for ballot in ballot_list:
#         string = str(ballot[0])
#         for cand in ballot[1]:
#             string += ' '+str(cand)
#         string += ' 0'
#         rows.append([string])
    
#     rows.append(['0'])
    
#     for name in cands_with_inds.values():
#         rows.append([name])
        
    
#     with open(destination_path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerows(rows)

        
        
        



