import pandas as pd
import json
import numpy as np

file_path = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/pref_voting/processed_results/scottish_results.csv'  # Replace with file path
df = pd.read_csv(file_path)

methods = ['plurality', 'IRV', 'top-two', 'borda-pm', 'top-3-truncation', 'condorcet', 'minimax', 'smith', 'smith-minimax', 'ranked-pairs']
num_cands_kept = 4

elections_with_no_condorcet_winner = 0
no_condorcet_elections = []

elections_with_condorcet_error = 0
condorcet_error_elections = []

elections_with_writein_condorcet = 0
writetin_condorcet_elections = []

files = {}
method_counts = dict.fromkeys(methods, 0)
elections_with_changes = 0

for _, row in df.iterrows():
    #if row['file'].split('/')[-1] in processed:
    changes = {}

    #if row['irv'] != row['condorcet'] and row['condorcet'] != "False":
    if row['instant_runoff_for_truncated_linear_orders'] != row['condorcet'] and row['condorcet'] != "ERROR" and row['condorcet'] is not np.NaN and row['instant_runoff_for_truncated_linear_orders'] is not np.NaN:
        changes = {
            'irv': row['instant_runoff_for_truncated_linear_orders'],
            'condorcet': row['condorcet']
        }

    if row['condorcet'] == "ERROR":
        elections_with_condorcet_error += 1
        condorcet_error_elections.append(row['file'])

    if row['condorcet'] == "Write-in":
        elections_with_writein_condorcet += 1
        writetin_condorcet_elections.append(row['file'])

    if row['condorcet'] == "False" or row['condorcet'] is np.nan:
        #print(row['condorcet'])
        elections_with_no_condorcet_winner += 1
        no_condorcet_elections.append(row['file'])

    if len(changes) > 0:
        elections_with_changes += 1
    
    files[row['file']] = changes

# calculate file statistics
total_files = len(df)

metadata = {
    "total_elections": total_files,
    "num_elections_with_difference_bw_irv_condorcet": elections_with_changes,
    #"num_elections_with_no_condorcet_winner": elections_with_no_condorcet_winner,
    "num_elections_with_condorcet_error": elections_with_condorcet_error,
    "elections_with_writein_condorcet": elections_with_writein_condorcet,
    #"method_counts": method_counts,
}

output_data = {
    "metadata": metadata,
    "elections_with_no_condorcet_winner": no_condorcet_elections,
    "elections_with_condorcet_error": condorcet_error_elections,
    "elections_with_writein_condorcet": writetin_condorcet_elections,
    "changes": files
}

# write to output file
output_file = "/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/condorcet_check/pref_voting_results/scotland.json"
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Grouped changes with metadata have been exported to {output_file}")