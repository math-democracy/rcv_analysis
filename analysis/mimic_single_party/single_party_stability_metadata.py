import pandas as pd
import json

with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/metadata/party_breakdown.json', 'r') as file:
    party_info = json.load(file)


def gen_metadata(filepath):
    num_cands_kept = 4
    df = pd.read_csv(file_path)

    methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval']
    
    files = {}
    method_counts = dict.fromkeys(methods, 0)
    elections_with_changes = 0
    stable_elections = []

    file_summary = {method: [] for method in methods}

    for _, row in df.iterrows():
        #candidates = party_info[f'raw_data/scotland/processed_data/{row['file'].replace('analysis/mimic_single_party/methods/first_last_mentioned/keep_last/processed_data/','')}']['party_dict']
        #parties = party_info[f'raw_data/scotland/processed_data/{row['file'].replace('analysis/mimic_single_party/methods/first_last_mentioned/keep_last/processed_data/','')}']['parties']
        candidates = party_info[f'{row['file']}']['party_dict']
        parties = party_info[f'{row['file']}']['parties']

        changes = {}
        
        for method in methods:
            if row[method] != "unknown" and row[method] != row[f'top{num_cands_kept}_{method}']:
                changes[method] = {
                    "numCands": row['numCands'],
                    "baseline_winner": row[method],
                    f"top{num_cands_kept}":row[f'top{num_cands_kept}_{method}']
                }
                method_counts[method] += 1
                file_summary[method].append(row['file'])

        if len(changes) > 0:
            elections_with_changes += 1
            files[row['file']] = {
                "changes":changes,
                "candidates": candidates,
                "parties":parties
            }
        else:
            stable_elections.append(row['file'])
            
        # if row['file'] in candidates[country]:
        #     candidate_ranks = candidates[country][row['file']]
        # else:
        #     candidate_ranks = {}

        

    # calculate file statistics
    total_files = len(df)

    metadata = {
        "total_elections": total_files,
        "elections_with_changes": elections_with_changes,
        "method_counts": method_counts,
        "file_summary": file_summary
    }

    output_data = {
        "metadata": metadata,
        "changes": files,
        "stable_elections": stable_elections
    }

    # write to output file
    output_file = file_path[:-4]+ '.json'
    print(output_file)
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")

# gen_metadata('america')
# gen_metadata('australia')
METHOD = 'mention_score'
file_path = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/{METHOD}/scotland_results_top4.csv'  # Replace with file path
gen_metadata(file_path)
# gen_metadata('civs')