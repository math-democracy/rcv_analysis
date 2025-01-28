import json
import pandas as pd
import numpy as np
from pref_voting.profiles_with_ties import *
from pref_voting.voting_methods import *
from pref_voting.c1_methods import condorcet

import csv
from collections import Counter, defaultdict
from pref_voting.profiles import Profile

from votekit.cleaning import remove_noncands
from new_csv_loader import new_loader
import votekit.elections as v


file_path = '/Users/belle/Desktop/build/rcv_proposal/american/processed_data/San Francisco/SanFrancisco_11022010_BoardofSupervisorsDistrict10.csv'

def ranking_to_indices(ranking, candidate_to_index):
    ranking_dict = {}
    for rank, candidate in enumerate(ranking, start=1):
        ranking_dict[candidate_to_index.get(candidate, -1)] = rank
    return ranking_dict

def create_profile(file_path):
    election_data = pd.read_csv(file_path)
    column_names_list = election_data.columns.tolist()
    num_ranks=0
    for item in column_names_list:
        if 'rank' in item:
            num_ranks+=1

    # Function to process each voter's rankings, ignoring "overvote"
    def process_rankings(row):
        seen_candidates = set()
        ranking = defaultdict(list)
        rank = 1
        
        for i in range(1, num_ranks+1):
            candidate = row[f'rank{i}']
            if candidate != 'overvote' and candidate != 'skipped' and candidate != 'Skipped' and candidate != 'Write-in' and candidate not in seen_candidates:
                ranking[rank].append(candidate)
                seen_candidates.add(candidate)
                rank += 1
        
        return {c: r for r, cs in ranking.items() for c in cs}

    # Apply the function and count occurrences of each ranking
    election_data['processed_rankings'] = election_data.apply(process_rankings, axis=1)
    ranking_counts = Counter(election_data['processed_rankings'].apply(tuple))

    # Create candidate list and set "Write-in" index last
    candidates = [c for c in set().union(*[r for r in ranking_counts])]

    # Convert rankings to indices format
    candidate_to_index = {candidate: index for index, candidate in enumerate(candidates)}

    # Display the candidates and their indices for reference
    candidates_with_indices = {index: candidate for candidate, index in candidate_to_index.items()}

    # Creating rankings with indices, ignoring ballots with "overvote"
    rankings = [ranking_to_indices(ranking, candidate_to_index) for ranking, count in ranking_counts.items()]
    rcounts = [count for ranking, count in ranking_counts.items()]

    # Create ProfileWithTies object
    profile = ProfileWithTies(rankings, rcounts)
    # profile.display()

    # Treat unranked candidates as tied for last place below ranked candidates for the purposes of the margin graph
    # profile.use_extended_strict_preference()

    # Display the margin graph
    # profile.display_margin_graph()

    return profile, candidates_with_indices

profile, candidates_with_indices = create_profile(file_path)

def v_profile(filename, to_remove = ["undervote", "overvote", "UWI"]):
    return remove_noncands(new_loader(filename)[0], to_remove)

p = v_profile(file_path)

election = v.IRV(profile= p)
# elected = list(v.IRV(profile = p).election_states[-1].elected[0])[0]

print(election)

# for i in range(10):
#     print(candidates_with_indices[instant_runoff_for_truncated_linear_orders(profile)[0]])