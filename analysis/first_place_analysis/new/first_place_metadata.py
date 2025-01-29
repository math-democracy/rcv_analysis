import pandas as pd
import json

file_path = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/new/results/american.csv'  # Replace with file path
df = pd.read_csv(file_path)

methods = ['plurality', 'IRV', 'top-two', 'borda-pm', 'top-3-truncation', 'condorcet', 'minimax', 'smith', 'smith-minimax', 'ranked-pairs']
num_cands_kept = 4

files = {}
method_counts = dict.fromkeys(methods, 0)
third_place_hits = dict.fromkeys(methods, 0)
third_or_fewer_hits = dict.fromkeys(methods, 0)


for _, row in df.iterrows():
    changes = {}

    for method in methods:
        if row[method] != "unknown" and row[method] != "writein" and row['numCands'] > 3 and row[f'{method}_rank'] >= 3:
            changes[method] = {
                "winner": row[method],
                "rank (out of first place votes)": row[f'{method}_rank']
            }
            method_counts[method] += 1

            if row[f'{method}_rank'] == 3:  
                third_place_hits[method] += 1
            else:
                third_or_fewer_hits[method] += 1
    
    files[row['file']] = changes

# calculate file statistics
total_files = len(df)

metadata = {
    "total_elections": total_files,
    "total_method_counts_third_or_lower": method_counts,
    "method_counts_third_place": third_place_hits,
    "method_counts_lower": third_or_fewer_hits
}

output_data = {
    "metadata": metadata,
    "changes": files
}

# write to output file
output_file = "/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/new/american_without_write_in.json"
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Grouped changes with metadata have been exported to {output_file}")