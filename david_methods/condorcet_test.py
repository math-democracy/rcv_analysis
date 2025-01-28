import pandas as pd
import json

file_path = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/processed_results/american_results.csv'  # Replace with file path
df = pd.read_csv(file_path)

methods = ['plurality', 'IRV', 'top-two', 'borda-pm', 'top-3-truncation', 'condorcet', 'minimax', 'smith', 'smith-minimax', 'ranked-pairs']
num_cands_kept = 4

elections_with_no_condorcet_winner = 0
no_condorcet_elections = []

files = {}
method_counts = dict.fromkeys(methods, 0)
elections_with_no_changes = 0

for _, row in df.iterrows():
    changes = {}

    if row['irv'] != row['condorcet'] and row['condorcet'] != "False":
        changes = {
            'irv': row['irv'],
            'condorcet': row['condorcet']
        }

    if row['condorcet'] == "False":
        elections_with_no_condorcet_winner += 1
        no_condorcet_elections.append(row['file'])

    if len(changes) == 0:
        elections_with_no_changes += 1
    
    files[row['file']] = changes

# calculate file statistics
total_files = len(df)

metadata = {
    "total_elections": total_files,
    "num_elections_with_no_difference_bw_irv_condorcet": elections_with_no_changes,
    "num_elections_with_no_condorcet_winner": elections_with_no_condorcet_winner,
    #"method_counts": method_counts,
}

output_data = {
    "metadata": metadata,
    "elections_with_no_condorcet_winner": no_condorcet_elections,
    "changes": files
}

# write to output file
output_file = "/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/condorcet_check/american.json"
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Grouped changes with metadata have been exported to {output_file}")