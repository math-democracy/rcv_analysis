import pandas as pd
import json

file_path = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/scotland_results_top4.csv'  # Replace with file path
df = pd.read_csv(file_path)

methods = ['plurality', 'IRV', 'top-two', 'borda-pm', 'top-3-truncation', 'condorcet', 'minimax', 'smith', 'smith-minimax', 'ranked-pairs']
num_cands_kept = 4

files = {}
method_counts = dict.fromkeys(methods, 0)
elections_with_no_changes = 0

for _, row in df.iterrows():
    changes = {}

    for method in methods:
        if row[method] != row[f'top{num_cands_kept}_{method}']:
            changes[method] = {
                "baseline_winner": row[method],
                f"top{num_cands_kept}":row[f'top{num_cands_kept}_{method}']
            }
            method_counts[method] += 1

    if len(changes) == 0:
        elections_with_no_changes += 1
    
    files[row['file']] = changes

# calculate file statistics
total_files = len(df)

metadata = {
    "total_elections": total_files,
    "elections_with_no_changes": elections_with_no_changes,
    "method_counts": method_counts,
}

output_data = {
    "metadata": metadata,
    "changes": files
}

# write to output file
output_file = "/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/scotland.json"
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Grouped changes with metadata have been exported to {output_file}")