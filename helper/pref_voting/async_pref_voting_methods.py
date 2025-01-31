import json
import pandas as pd
import numpy as np
from pref_voting.profiles_with_ties import *
from pref_voting.voting_methods import *
from pref_voting.c1_methods import condorcet
import aiofiles
import asyncio
import csv
from collections import Counter, defaultdict
from pref_voting.profiles import Profile
from concurrent.futures import ThreadPoolExecutor

# Function to convert rankings (in tuple format) to indices and create dictionaries as keys
def ranking_to_indices(ranking, candidate_to_index):
    ranking_dict = {}
    for rank, candidate in enumerate(ranking, start=1):
        ranking_dict[candidate_to_index.get(candidate, -1)] = rank
    return ranking_dict

async def create_profile(file_path):
    election_data = pd.read_csv(file_path)
    column_names_list = election_data.columns.tolist()
    num_ranks = 0
    for item in column_names_list:
        if 'rank' in item:
            num_ranks += 1

    # Function to process each voter's rankings, ignoring "overvote"
    def process_rankings(row):
        seen_candidates = set()
        ranking = defaultdict(list)
        rank = 1
        
        for i in range(1, num_ranks + 1):
            candidate = row[f'rank{i}']
            if candidate != 'overvote' and candidate != 'skipped' and candidate != 'Skipped' and candidate not in seen_candidates:
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

    return profile, file_path, candidates_with_indices

async def run_voting_methods(profile, file_path, candidates_with_indices):
    data = {'file': file_path.replace('/Users/belle/Desktop/build/rcv_proposal/', '')}
    
    def get_voting_method_result(method_func, method_name):
        try:
            if len(method_func(profile)) == 1:
                return candidates_with_indices[method_func(profile)[0]]
            else:
                return "NULL"
        except Exception as e:
            return "ERROR"

    # Use a ThreadPoolExecutor to run each voting method concurrently
    with ThreadPoolExecutor() as executor:
        methods = [
            ('plurality', plurality),
            ('plurality_with_runoff_put', plurality_with_runoff_put),
            ('instant_runoff_for_truncated_linear_orders', instant_runoff_for_truncated_linear_orders),
            ('bottom_two_runoff_instant_runoff_put', bottom_two_runoff_instant_runoff_put),
            ('instant_runoff_put', instant_runoff_put),
            ('borda_for_profile_with_ties', borda_for_profile_with_ties),
            ('condorcet', condorcet),
            ('condorcet_irv', condorcet_irv),
            ('weak_condorcet', weak_condorcet),
            ('benham', benham),
            ('minimax', minimax),
            ('ranked_pairs', ranked_pairs_with_test),
            ('top_cycle', top_cycle),
            ('copeland', copeland),
            ('daunou', daunou),
        ]
        
        # Run all methods concurrently
        futures = [
            asyncio.to_thread(get_voting_method_result, method_func, method_name)
            for method_name, method_func in methods
        ]
        
        results = await asyncio.gather(*futures)
        
        # Assign results to the data dictionary
        for i, (method_name, _) in enumerate(methods):
            data[method_name] = results[i]

    return data

async def process_file(full_path, filename, data_file, processed_file, all_data):
    print("RUNNING ", filename, "\n")
    profile, file_path, candidates_with_indices = await create_profile(full_path)
    data = await run_voting_methods(profile, file_path, candidates_with_indices)
    all_data.append(data)
    print(data, "\n")

    # Writing data to CSV asynchronously
    async with aiofiles.open(data_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        keys = all_data[0].keys()
        row = [data.get(key, '') for key in keys]
        await writer.writerow(row)

    # Writing processed filename asynchronously
    async with aiofiles.open(processed_file, "a") as ef:
        await ef.write(f"{filename}, ")

# Example usage of the async process
async def main():
    all_data = []
    data_file = "data.csv"
    processed_file = "processed_files.txt"
    # Assuming full_path and filenames are defined earlier
    # Example of processing one file:
    await process_file('file_path_to_process', 'example_file.csv', data_file, processed_file, all_data)

# Run the main function
asyncio.run(main())