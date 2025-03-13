import pandas as pd
import json
import re
from collections import defaultdict
import ast

file_path = '/Users/belle/Desktop/build/rcv_proposal/analysis/spoiler/results/america_results.csv'  # Replace with your actual file path
og = '/Users/belle/Desktop/build/rcv_proposal/results/current/america.csv'

df = pd.read_csv(file_path)

# Get row where no candidates were removed
original_row = pd.read_csv(og)

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

def merge_chars(string_list):
    lst = ast.literal_eval(string_list)

    if all(isinstance(item, str) and len(item) == 1 for item in lst):
        return "['" + "".join(lst) + "']"
    return string_list 


for _, row in df.iterrows():
    file = row['file'].lstrip("/")

    candidate_removed = row['candidate_removed']
    # irv_results = ast.literal_eval(row['irv-rank'])
    total_files.add(file)
    
    if candidate_removed != 'none':  
        if file not in winners:
            winners[file] = []
        file_changes = {'candidate_removed': candidate_removed, 'changes': {}}
        # irv_winner = next(candidate for candidate, data in irv_results.items() if data['status'] == 'Elected')
        # spoiler_party = extract_party(candidate_removed)
        try:
            for method in original_winners[file]:
                baseline_winner = merge_chars(original_winners[file][method].strip("{}").strip("'"))
                new_winner = merge_chars(row[method].strip("{}").strip("'"))
                
                # baseline_winner_irv_round = irv_results[baseline_winner]['round'] if baseline_winner in irv_results else 'N/A'

                # if "," in baseline_winner:
                #     baseline_winner_irv_round = ""
                #     for win in baseline_winner.replace(" '", "").replace("'", "").strip().split(','):
                #         baseline_winner_irv_round = baseline_winner_irv_round + (str(irv_results[win]['round']) if win in irv_results else 'N/A') + " "
                
                # # new_winner_irv_round = irv_results[new_winner]['round'] if new_winner in irv_results else 'N/A' 

                # if "," in new_winner:
                #     new_winner_irv_round = ""
                #     for win in new_winner.replace(" '", "").replace("'", "").split(','):
                #         new_winner_irv_round = new_winner_irv_round + (str(irv_results[win]['round']) if win in irv_results else 'N/A') + " "
                    
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
                    # print(r['file'], r['numCands'])
                    continue

                if baseline_winner != new_winner:
                    # new_winner_party = extract_party(row[method])
                    
                    file_changes['changes'][method] = {
                        'baseline_winner': baseline_winner,
                        # 'baseline_winner_irv_round': baseline_winner_irv_round,
                        # 'baseline_winner_irv_winner': baseline_winner == irv_winner,
                        'new_winner': new_winner,
                        # 'new_winner_irv_round': new_winner_irv_round,
                        # 'new_winner_irv_winner': new_winner == irv_winner,
                        # 'irv_rounds' : irv_results[irv_winner]['round'] if irv_winner in irv_results else 'N/A'
                        # 'same_party': spoiler_party == new_winner_party
                    }
        except:
            print('oops ', file)
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
  
baseline_winner_irv_count = 0
baseline_winner_irv_ranks = defaultdict(int)

new_winner_irv_count = 0
new_winner_irv_ranks = defaultdict(int)

for file_changes in winners.values():
    num_spoilers = len(file_changes)
    # if (num_spoilers == 14):
    #     for c in file_changes:
    #         print(c['changes'])
    spoiler_counts[num_spoilers] = spoiler_counts.get(num_spoilers, 0) + 1
    # for entry in file_changes:
    #     changes = entry["changes"]
            
        # for method, results in changes.items():
            # Count baseline winner occurrences
            # if results["baseline_winner_irv_winner"]:
            #     baseline_winner_irv_count += 1
            # baseline_winner_irv_ranks[results["baseline_winner_irv_round"]] += 1
            
            # Count new winner occurrences
            # if results["new_winner_irv_winner"]:
            #     new_winner_irv_count += 1
            # new_winner_irv_ranks[results["new_winner_irv_round"]] += 1

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
    "method_combinations": dict(sorted(final_combination_counts.items(), key=lambda x: x[1], reverse=True)),
    "baseline_winner_irv_count" : baseline_winner_irv_count,
    "baseline_winner_irv_ranks": baseline_winner_irv_ranks,
    "new_winner_irv_count" : new_winner_irv_count,
    "new_winner_irv_ranks" : new_winner_irv_ranks
}

output_data = {
    "metadata": metadata,
    "winners": winners
}

output_file = "winners_with_metadata.json"
with open(output_file, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Grouped changes with metadata have been exported to {output_file}")
