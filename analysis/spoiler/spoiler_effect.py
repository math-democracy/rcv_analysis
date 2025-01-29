import pandas as pd
import json
import re
from collections import defaultdict

file_path = '/Users/belle/Desktop/build/rcv_proposal/analysis/spoiler/results/america_results2.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# Get row where no candidates were removed
original_row = df[df['candidate_removed'] == 'none']

# Store original winners
original_winners = {}
for _, row in original_row.iterrows():
    file = row['file']
    original_winners[file] = {col: row[col] for col in df.columns if col not in ['file', 'candidate_removed']}

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

for _, row in df.iterrows():
    file = row['file']
    candidate_removed = row['candidate_removed']
    total_files.add(file)
    
    if candidate_removed != 'none':  
        if file not in winners:
            winners[file] = []
        file_changes = {'candidate_removed': candidate_removed, 'changes': {}}
        # spoiler_party = extract_party(candidate_removed)

        for method in original_winners[file]:
            # Skip if original winner is the candidate removed since that will definitely change winner
            if normalize(original_winners[file][method]) == normalize(candidate_removed) or row[method] == "unknown":
                continue
            if row[method] != original_winners[file][method]:
                # new_winner_party = extract_party(row[method])
                file_changes['changes'][method] = {
                    'baseline_winner': original_winners[file][method],
                    'new_winner': row[method],
                    # 'same_party': spoiler_party == new_winner_party
                }

        if file_changes['changes']: 
            winners[file].append(file_changes)

        if (len(winners[file]) == 0):
            del winners[file]
    

election_with_changes = len(winners)
# elections_with_no_changes = sum(1 for changes in winners.values() if not changes)
method_counts = defaultdict(set)
method_combinations = defaultdict(set)
spoiler_counts = {}
# party = {
#     "same": {},
#     "diff": {}
# }

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
    if (num_spoilers == 14):
        for c in file_changes:
            print(c['changes'])
    spoiler_counts[num_spoilers] = spoiler_counts.get(num_spoilers, 0) + 1
    # for change in file_changes:
    #     for c in change["changes"]:
    #     # print(c)
    #         if change["changes"][c]["same_party"]:
    #             try:
    #                 party["same"][c] += 1
    #             except:
    #                 party["same"][c] = 1
                
    #         else:
    #             try:
    #                 party["diff"][c] += 1
    #             except:
    #                 party["diff"][c] = 1


metadata = {
    "total_elections": len(total_files),
    "election_with_changes": election_with_changes,
    "spoiler_counts": dict(sorted(spoiler_counts.items(), key=lambda x: x[1], reverse=True)),
    # "party": party,
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
