import json
import pandas as pd
import numpy as np
from pref_voting.profiles_with_ties import *
from pref_voting.voting_methods import *
from pref_voting.c1_methods import condorcet

import csv
from collections import Counter, defaultdict
from pref_voting.profiles import Profile

# Function to convert rankings (in tuple format) to indices and create dictionaries as keys
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
            if candidate != 'overvote' and candidate != 'skipped' and candidate not in seen_candidates:
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

    return profile, file_path, candidates_with_indices

def run_voting_methods(profile, file_path, candidates_with_indices):
    data = {'file': file_path.replace('/Users/belle/Desktop/build/rcv_proposal/', '')}
    ## PLURALITY ##
    try:
        if len(plurality(profile)) == 1:
            data['plurality'] = candidates_with_indices[plurality(profile)[0]]
        else:
            data['plurality'] = "NULL"
    except Exception as e:
        data['plurality'] = "ERROR"

    ## Plurality With Runoff PUT ##
    try:
        if len(plurality_with_runoff_put(profile)) == 1:
            data['plurality_with_runoff_put'] = candidates_with_indices[plurality_with_runoff_put(profile)[0]]
        else:
            data['plurality_with_runoff_put'] = "NULL"
    except Exception as e:
        data['plurality_with_runoff_put'] = "ERROR"

    ## Instant Runoff for Truncated Linear Orders ##
    try:
        if len(instant_runoff_for_truncated_linear_orders(profile)) == 1:
            data['instant_runoff_for_truncated_linear_orders'] = candidates_with_indices[instant_runoff_for_truncated_linear_orders(profile)[0]]
        else:
            data['instant_runoff_for_truncated_linear_orders'] = "NULL"
    except Exception as e:
        data['instant_runoff_for_truncated_linear_orders'] = "ERROR"

    ## Bottom-Two-Runoff Instant Runoff PUT ##
    try:
        if len(bottom_two_runoff_instant_runoff_put(profile)) == 1:
            data['bottom_two_runoff_instant_runoff_put'] = candidates_with_indices[bottom_two_runoff_instant_runoff_put(profile)[0]]
        else:
            data['bottom_two_runoff_instant_runoff_put'] = "NULL"
    except Exception as e:
        data['bottom_two_runoff_instant_runoff_put'] = "ERROR"

    ## Instant Runoff PUT ##
    try:
        if len(instant_runoff_put(profile)) == 1:
            data['instant_runoff_put'] = candidates_with_indices[instant_runoff_put(profile)[0]]
        else:
            data['instant_runoff_put'] = "NULL"
    except Exception as e:
        data['instant_runoff_put'] = "ERROR"

    ## BORDA ##
    try:
        if len(borda_for_profile_with_ties(profile)) == 1:
            data['borda_for_profile_with_ties'] = candidates_with_indices[borda_for_profile_with_ties(profile)[0]]
        else:
            data['borda_for_profile_with_ties'] = "NULL"
    except Exception as e:
        data['borda_for_profile_with_ties'] = "ERROR"

    ## CONDORCET ##
    try:
        if len(condorcet(profile)) == 1:
            data['condorcet'] = candidates_with_indices[condorcet(profile)[0]]
        else:
            data['condorcet'] = "NULL"
    except Exception as e:
        data['condorcet'] = "ERROR"

    ## CONDORCET IRV ##
    try:
        if len(condorcet_irv(profile)) == 1:
            data['condorcet_irv'] = candidates_with_indices[condorcet_irv(profile)[0]]
        else:
            data['condorcet_irv'] = "NULL"
    except Exception as e:
        data['condorcet_irv'] = "ERROR"

    ## WEAK CONDORCET ##
    try:
        if len(weak_condorcet(profile)) == 1:
            data['weak_condorcet'] = candidates_with_indices[weak_condorcet(profile)[0]]
        else:
            data['weak_condorcet'] = "NULL"
    except Exception as e:
        data['weak_condorcet'] = "ERROR"

    ## BENHAM ##
    try:
        if len(benham(profile)) == 1:
            data['benham'] = candidates_with_indices[benham(profile)[0]]
        else:
            data['benham'] = "NULL"
    except Exception as e:
        data['benham'] = "ERROR"

    ## MINIMAX ##
    try:
        if len(minimax(profile)) == 1:
            data['minimax'] = candidates_with_indices[minimax(profile)[0]]
        else:
            data['minimax'] = "NULL"
    except Exception as e:
        data['minimax'] = "ERROR"

    ## Ranked Pairs ##
    try:
        if len(ranked_pairs(profile)) == 1:
            data['ranked_pairs'] = candidates_with_indices[ranked_pairs(profile)[0]]
        else:
            data['ranked_pairs'] = "NULL"
    except Exception as e:
        data['ranked_pairs'] = "ERROR"

    ## TOP CYCLE ##
    try:
        if len(top_cycle(profile)) == 1:
            data['top_cycle'] = candidates_with_indices[top_cycle(profile)[0]]
        else:
            data['top_cycle'] = "NULL"
    except Exception as e:
        data['top_cycle'] = "ERROR"

    ## COPELAND ##
    try:
        if len(copeland(profile)) == 1:
            data['copeland'] = candidates_with_indices[copeland(profile)[0]]
        else:
            data['copeland'] = "NULL"
    except Exception as e:
        data['copeland'] = "ERROR"

    ## DAUNOU ##
    try:
        if len(daunou(profile)) == 1:
            data['daunou'] = candidates_with_indices[daunou(profile)[0]]
        else:
            data['daunou'] = "NULL"
    except Exception as e:
        data['daunou'] = "ERROR"


    return data