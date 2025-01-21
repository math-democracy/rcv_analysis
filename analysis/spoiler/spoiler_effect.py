import pandas as pd
import json
import re
file_path = '/Users/belle/Desktop/build/rcv_proposal/analysis/spoiler/results/civs_results.csv'  # Replace with your actual file path
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
    

# Calculate file statistics
election_with_changes = len(winners)
# elections_with_no_changes = sum(1 for changes in winners.values() if not changes)
method_counts = {}
method_combinations = {}
spoiler_counts = {}
# party = {
#     "same": {},
#     "diff": {}
# }

for file_changes in winners.values():
    for change in file_changes:
        methods_changed = list(change['changes'].keys())
        
        # Count individual methods
        for method in methods_changed:
            method_counts[method] = method_counts.get(method, 0) + 1
        
        # Count combinations of methods
        if methods_changed:
            methods_changed.sort()  # Ensure consistent ordering
            combination_key = ", ".join(methods_changed)
            method_combinations[combination_key] = method_combinations.get(combination_key, 0) + 1
        
        # for c in change["changes"]:
        #     # print(c)
        #     if change["changes"][c]["same_party"]:
        #         try:
        #             party["same"][c] += 1
        #         except:
        #             party["same"][c] = 1
                
        #     else:
        #         try:
        #             party["diff"][c] += 1
        #         except:
        #             party["diff"][c] = 1

    num_spoilers = len(file_changes)
    if (num_spoilers == 14):
        for c in file_changes:
            print(c['changes'])
    spoiler_counts[num_spoilers] = spoiler_counts.get(num_spoilers, 0) + 1

metadata = {
    "total_elections": len(total_files),
    "election_with_changes": election_with_changes,
    "spoiler_counts": spoiler_counts,
    # "party": party,
    "method_counts": method_counts,
    "method_combinations": method_combinations
}

output_data = {
    "metadata": metadata,
    "winners": winners
}

output_file = "winners_with_metadata.json"
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Grouped changes with metadata have been exported to {output_file}")
