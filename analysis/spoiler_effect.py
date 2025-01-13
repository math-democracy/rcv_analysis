import pandas as pd
import json

file_path = '/Users/belle/Desktop/build/rcv_proposal/analysis/results/australian_results.csv'  # Replace with your actual file path
df = pd.read_csv(file_path)

# get row where no candidates were removed
original_row = df[df['candidate_removed'] == 'none']

# store original winners
original_winners = {}
for _, row in original_row.iterrows():
    file = row['file']
    original_winners[file] = {col: row[col] for col in df.columns if col not in ['file', 'candidate_removed']}

winners = {}

for _, row in df.iterrows():
    file = row['file']
    candidate_removed = row['candidate_removed']
    
    if candidate_removed != 'none':  
        if file not in winners:
            winners[file] = []
        file_changes = {'candidate_removed': candidate_removed, 'changes': {}}
        for method in original_winners[file]:
            # skip if original winner is the candidate removed since that will definitely change winner
            if original_winners[file][method] == candidate_removed or row[method] == "unknown":
                continue
            if row[method] != original_winners[file][method]:
                file_changes['changes'][method] = {
                    'baseline_winner': original_winners[file][method],
                    'new_winner': row[method]
                }
        if file_changes['changes']: 
            winners[file].append(file_changes)

# calculate file statistics
total_files = len(winners)
elections_with_no_changes = sum(1 for changes in winners.values() if not changes)
method_counts = {}

for file_changes in winners.values():
    for change in file_changes:
        for method in change['changes']:
            method_counts[method] = method_counts.get(method, 0) + 1

metadata = {
    "total_elections": total_files,
    "elections_with_no_changes": elections_with_no_changes,
    "method_counts": method_counts,
}

output_data = {
    "metadata": metadata,
    "winners": winners
}

output_file = "winners_with_metadata.json"
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Grouped changes with metadata have been exported to {output_file}")