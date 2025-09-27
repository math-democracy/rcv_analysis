import pandas as pd
import json
import re
from collections import defaultdict
import ast

file_path = ''  # spoiler results file
og = '' # original results file

df = pd.read_csv(file_path)
original_row = pd.read_csv(og)
original_winners = {}
for _, row in original_row.iterrows():
    file = row['file']
    original_winners[file] = {col: row[col] for col in df.columns if col not in ['file', 'candidate_removed']} #create object w/ same columns/key as the spoiler

winners = {}
total_files = set()

def extract_party(candidate_name):
    party_regex = r"\((.*?)\)"
    match = re.search(party_regex, candidate_name)
    return match.group(1) if match else None

def normalize(value):
    try:
        # Convert numeric strings to floats first
        value = float(value)
        # Convert to int if it has no decimal part
        if value.is_integer():
            return int(value)
        return value
    except ValueError:
        # Handle non-numeric strings
        return str(value)

def merge_chars(string_list):
    lst = ast.literal_eval(string_list)

    if all(isinstance(item, str) and len(item) == 1 for item in lst):
        return "['" + "".join(lst) + "']"
    return string_list 


for _, row in df.iterrows():
    file = row['file'].lstrip("/")

    candidate_removed = row['candidate_removed']
    total_files.add(file)
    
    if candidate_removed != 'none':  
        if file not in winners:
            winners[file] = []
        file_changes = {'candidate_removed': candidate_removed, 'changes': {}}
        try:
            for method in original_winners[file]:
                baseline_winner = merge_chars(original_winners[file][method].strip("{}").strip("'"))
                new_winner = merge_chars(row[method].strip("{}").strip("'"))
                
                # Skip if original winner is the candidate removed since that will definitely change winner
                baseline_arr = ast.literal_eval(baseline_winner)
                if str(normalize(candidate_removed.strip("{}").strip("'"))) in baseline_arr or row[method] == "unknown":
                    continue
                
                if 'write' in candidate_removed or 'Write' in candidate_removed or 'UWI' in candidate_removed:
                    r = original_row[original_row['file'] == file]
                    if int(r['numCands']) < 3:
                        print(r['numCands'])
                        continue

                if new_winner == "[None]":
                    r = original_row[original_row['file'] == file]
                    continue

                if baseline_winner != new_winner:
                    
                    file_changes['changes'][method] = {
                        'baseline_winner': baseline_winner,
                        'new_winner': new_winner,
                    }
        except:
            print('oops ', file)
        if file_changes['changes']: 
            winners[file].append(file_changes)

        if (len(winners[file]) == 0):
            del winners[file]
    

election_with_changes = len(winners)
method_counts = defaultdict(set)
method_combinations = defaultdict(set)
spoiler_counts = {}

for election, changes in winners.items():
    all_methods = set()
    for change in changes:
        all_methods.update(change['changes'].keys())  # Add all methods to a set for the election

    for method in all_methods:
        method_counts[method].add(election)

    if all_methods:
        sorted_methods = sorted(all_methods)  # Ensure consistent ordering
        combination_key = ", ".join(sorted_methods)
        method_combinations[combination_key].add(election)

final_method_counts = {method: len(elections) for method, elections in method_counts.items()}
final_combination_counts = {combination: len(elections) for combination, elections in method_combinations.items()}

for file_changes in winners.values():
    num_spoilers = len(file_changes)
    spoiler_counts[num_spoilers] = spoiler_counts.get(num_spoilers, 0) + 1


metadata = {
    "total_elections": len(total_files),
    "election_with_changes": election_with_changes,
    "spoiler_counts": dict(sorted(spoiler_counts.items(), key=lambda x: x[1], reverse=True)),
    "method_counts": dict(sorted(final_method_counts.items(), key=lambda x: x[1], reverse=True)),
    "method_combinations": dict(sorted(final_combination_counts.items(), key=lambda x: x[1], reverse=True))
}

output_data = {
    "metadata": metadata,
    "winners": winners
}

output_file = "winners_with_metadata.json"
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Grouped changes with metadata have been exported to {output_file}")
