import pandas as pd
import json
import os

def gen_metadata(country, file_path):
    num_cands_kept = 4

    if country:
        file_path = f'/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/{country}_results_top{num_cands_kept}.csv'  # Replace with file path
        
        # Open and read the JSON file
        with open('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/first_place_ranks.json', 'r') as file:
            candidates = json.load(file)
    
    #file_path = f'/Users/karenxiao/MyPythonCode/ranked_choice_voting/hpc_results/stability/results/Alabama_distribution1_3cands_top4stability_FFTF.csv'
    df = pd.read_csv(file_path)

    methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval']
    

    files = {}
    method_counts = dict.fromkeys(methods, 0)
    elections_with_changes = 0

    file_summary = {method: [] for method in methods}

    for i, row in df.iterrows():
        #same_party = False

        changes = {}
        
        for method in methods:
            if row[method] != "unknown" and row[method] != row[f'top{num_cands_kept}_{method}']:
                
                # if 'scotland' in file_path and row[method] != "[]" and row[f'top{num_cands_kept}_{method}'] != "[]":
                #     if row[method][2] == "(":
                #         baseline_party = row[method][3:row[method].find(")")]
                #     else:
                #         baseline_party = row[method].rstrip("*")[row[method].rfind("(")+1:-3]

                #     if row[f'top{num_cands_kept}_{method}'][2] == "(":
                #         new_party = row[f'top{num_cands_kept}_{method}'][3:row[f'top{num_cands_kept}_{method}'].find(")")]
                #     else:
                #         new_party = row[f'top{num_cands_kept}_{method}'].rstrip("*")[row[f'top{num_cands_kept}_{method}'].rfind("(")+1:-3]
                    
                #     # if baseline_party == "Ind" and new_party == "Ind" and method != 'bucklin':
                #     #     print(f'{row['file']}, method: {method}, baseline: {row[method]}, top: {row[f'top{num_cands_kept}_{method}']}')

                #     if baseline_party == new_party and baseline_party != 'Ind' and new_party != 'Ind':
                #         same_party = True
                
                changes[method] = {
                    "numCands": row['numCands'],
                    "baseline_winner": row[method],
                    f"top{num_cands_kept}":row[f'top{num_cands_kept}_{method}']
                }
                method_counts[method] += 1
                file_summary[method].append(row['file'])

        if len(changes) > 0:
            elections_with_changes += 1
        
        if country:
            if row['file'] in candidates[country]:
                candidate_ranks = candidates[country][row['file']]
            else:
                candidate_ranks = {}
            files[row['file']] = {
                "changes":changes,
                "candidates": candidate_ranks
            }
        else:
            files[f"{row['file']} / election #{i}"] = {
                "changes": changes
            }

        
    # calculate file statistics
    total_files = len(df)

    metadata = {
        "total_elections": total_files,
        "elections_with_changes": elections_with_changes,
        "method_counts": method_counts,
        #"file_summary": file_summary
    }

    output_data = {
        "metadata": metadata,
        "changes": files
    }

    # write to output file
    if country:
        output_file = f"/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/{country}_results_top{num_cands_kept}.json"
    else:
        output_file = file_path[:-4].replace('/results/','/metadata/') + '.json'
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")

#gen_metadata('america')
# gen_metadata('australia')
# gen_metadata('scotland')
#gen_metadata('civs')

def main():
    root_dir = '/Users/karenxiao/MyPythonCode/ranked_choice_voting/hpc_results/stability/results'
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            print(filename)
            if filename.endswith('.csv') and '5cands' in filename:
                full_path = os.path.join(dirpath, filename)
                gen_metadata(None, full_path)

if __name__ == '__main__':
    #gen_metadata(None, '/Users/karenxiao/MyPythonCode/ranked_choice_voting/hpc_results/stability/results/Alabama_distribution1_5cands_top4stability_TTFF.csv')
    main()