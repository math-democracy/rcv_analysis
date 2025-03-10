import pandas as pd
import json
import ast

with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/party_breakdown.json', 'r') as file:
    party_info = json.load(file)

def get_party(candidate):
    if candidate == '[]':
        return candidate
    
    if candidate[3] == "(":
        party = candidate[1:candidate.find(")")]
    else:
        left = candidate.rfind("(")
        right = candidate[left:].rfind(")")
        if right == -1:
            right = -1
        else:
            right = left + right
        party = candidate[left+1:right]

    if party != 'Ind' and party != 'UNKNOWN':
        return f"['{party}']"
    else:
        return candidate
    
def gen_metadata(country):
    num_cands_kept = 4
    file_path = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/results/single_v_multi_comparison.csv'  # Replace with file path
    df = pd.read_csv(file_path)

    methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval']
    
    files = {}
    method_counts = dict.fromkeys(methods, 0)
    nonbloc_counts = dict.fromkeys(methods, 0)
    total_counts = dict.fromkeys(methods, 0)
    non_bloc_files = {method: [] for method in methods}
    no_single_winner = dict.fromkeys(methods, 0) #{method: [] for method in methods}
    elections_with_changes = 0

    # # Open and read the JSON file
    # with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/first_place_ranks.json', 'r') as file:
    #     candidates = json.load(file)

    #print(candidates['scotland'])
    total_hits = 0
    bloc_hits = 0
    non_bloc_hits = 0

    file_summary = {method: [] for method in methods}

    for _, row in df.iterrows():
        #same_party = False

        changes = {}

        candidates = party_info[f'raw_data/scotland/processed_data/{row['file']}']['party_dict']
        parties = party_info[f'raw_data/scotland/processed_data/{row['file']}']['parties']

        for method in methods:
            #print(len(row[f'{method}_multi']))
            #total_hits += 1
            total_counts[method] += 1
            if get_party(row[f'{method}_multi']) != row[f'{method}_single']:
                total_hits += 1
                changes[method] = {
                    "multi_party_winner": row[f'{method}_multi'],
                    "single_party_winner": row[f'{method}_single']
                }
                method_counts[method] += 1
                file_summary[method].append(row['file'])
                parties = party_info[f'raw_data/scotland/processed_data/{row['file']}']['parties']
                #print(row[f'{method}_single'])
                #print(row['file'], ast.literal_eval(row[f'{method}_single'])[0], parties, parties[ast.literal_eval(row[f'{method}_single'])[0]])
                if row[f'{method}_single'] != '[]' and ast.literal_eval(row[f'{method}_single'])[0] in parties and ast.literal_eval(row[f'{method}_single'])[0] != 'Ind' and ast.literal_eval(row[f'{method}_single'])[0] != 'UNKNOWN' and parties[ast.literal_eval(row[f'{method}_single'])[0]] > 1:
                    
                    bloc_hits += 1
                else:
                    nonbloc_counts[method] += 1
                    if row[f'{method}_single'] == '[]':
                        no_single_winner[method] += 1
                    non_bloc_hits += 1
                    non_bloc_files[method].append(row['file'])
                    #print(row['file'])

        if len(changes) > 0:
            elections_with_changes += 1
            
        # if row['file'] in candidates[country]:
        #     candidate_ranks = candidates[country][row['file']]
        # else:
        #     candidate_ranks = {}

        if changes:
            

            files[row['file']] = {
                "changes":changes,
                "candidates":candidates,
                "parties":parties
                #"candidates": candidate_ranks
            }

    # calculate file statistics
    total_files = len(df)

    metadata = {
        "total_elections": total_files,
        "elections_with_changes": elections_with_changes,
        "total_method_count": total_hits,
        "new_winner_from_bloc": bloc_hits,
        "new_winner_not_from_bloc": non_bloc_hits,
        "new_winner_not_from_bloc_ounts": nonbloc_counts,
        "no_single_winner": no_single_winner,
        "method_counts": method_counts,
        "non_bloc_winner_files": non_bloc_files
        #"file_summary": file_summary
    }

    output_data = {
        "metadata": metadata,
        "changes": files
    }

    # write to output file
    output_file = f"/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/results/single_v_multi_comparison.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")

# gen_metadata('america')
# gen_metadata('australia')
gen_metadata('scotland')
# gen_metadata('civs')