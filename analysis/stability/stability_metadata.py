import pandas as pd
import json

country = 'american'
file_path = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/{country}_results_top4.csv'  # Replace with file path
df = pd.read_csv(file_path)

methods = ['plurality','IRV','top-two','borda-pm','borda-om-no-uwi','borda-avg-no-uwi','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval']
num_cands_kept = 4

files = {}
method_counts = dict.fromkeys(methods, 0)
elections_with_changes = 0


# Open and read the JSON file
with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/first_place_ranks.json', 'r') as file:
    candidates = json.load(file)

#print(candidates['scotland'])

for _, row in df.iterrows():
    #same_party = False

    changes = {}
    
    for method in methods:
        same_party = False
        if row[method] != "unknown" and row[method] != row[f'top{num_cands_kept}_{method}']:
            if 'scotland' in file_path and row[method] != "[]" and row[f'top{num_cands_kept}_{method}'] != "[]":
                if row[method][2] == "(":
                    baseline_party = row[method][3:row[method].find(")")]
                else:
                    baseline_party = row[method].rstrip("*")[row[method].rfind("(")+1:-3]

                if row[f'top{num_cands_kept}_{method}'][2] == "(":
                    new_party = row[f'top{num_cands_kept}_{method}'][3:row[f'top{num_cands_kept}_{method}'].find(")")]
                else:
                    new_party = row[f'top{num_cands_kept}_{method}'].rstrip("*")[row[f'top{num_cands_kept}_{method}'].rfind("(")+1:-3]
                
                # if baseline_party == "Ind" and new_party == "Ind" and method != 'bucklin':
                #     print(f'{row['file']}, method: {method}, baseline: {row[method]}, top: {row[f'top{num_cands_kept}_{method}']}')

                if baseline_party == new_party and baseline_party != 'Ind' and new_party != 'Ind':
                    same_party = True

            if not same_party:
                changes[method] = {
                    "numCands": row['numCands'],
                    "candidates": candidates[country][row['file']],
                    "baseline_winner": row[method],
                    f"top{num_cands_kept}":row[f'top{num_cands_kept}_{method}']
                }
                method_counts[method] += 1

    if len(changes) > 0:
        elections_with_changes += 1
    
    files[row['file']] = changes

# calculate file statistics
total_files = len(df)

metadata = {
    "total_elections": total_files,
    "elections_with_changes": elections_with_changes,
    "method_counts": method_counts,
}

output_data = {
    "metadata": metadata,
    "changes": files
}

# write to output file
output_file = f"/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/{country}_results_top4.json"
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Grouped changes with metadata have been exported to {output_file}")