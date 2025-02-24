import pandas as pd
import json
from collections import Counter

country = 'american'

def gen_metadata_for_country(country):
    file_path = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/new/{country}.csv'  # Replace with file path
    df = pd.read_csv(file_path)

    methods = ['plurality','IRV','top-two','borda-pm','borda-om-no-uwi','borda-avg-no-uwi','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']
    num_cands_kept = 4

    files = {}
    method_counts = dict.fromkeys(methods, 0)
    third_place_hits = dict.fromkeys(methods, 0)
    third_or_fewer_hits = dict.fromkeys(methods, 0)

    third_place_num_cands = set()
    third_or_fewer_num_cands = set()

    num_elections_with_hits = 0

    cands_vs_place = []

    places = set()

    with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/first_place_ranks.json') as fp_file:
        first_place_ranks = json.load(fp_file)

    for _, row in df.iterrows():
        changes = {}

        none_types = [None,'[None]','[]']

        for method in methods:
            #print(row[f'{method}_rank'])
            if row[method] not in none_types and row[method] != "unknown" and row[method] != "writein" and row['numCands'] > 3 and row[f'{method}_rank'] != 'multiple' and int(row[f'{method}_rank']) >= 3:
                changes[method] = {
                    "num_cands": row['numCands'],
                    "winner": row[method],
                    "rank (out of first place votes)": row[f'{method}_rank']
                }

                cands_vs_place.append(f"{int(row['numCands'])}:{int(row[f'{method}_rank'])}")
                method_counts[method] += 1

                if int(row[f'{method}_rank']) == 3:  
                    third_place_hits[method] += 1
                    third_place_num_cands.add(row['numCands'])
                else:
                    third_or_fewer_hits[method] += 1
                    third_or_fewer_num_cands.add(row['numCands'])

                places.add(int(row[f'{method}_rank']))
                
        if len(changes) > 0:
            changes['ranks'] = first_place_ranks[country][f'raw_data/{country}/processed_data/{row['file']}']
            num_elections_with_hits += 1

        files[row['file']] = changes

    # calculate file statistics
    total_files = len(df)

    metadata = {
        "total_elections": total_files,
        "total_elections_with_hits": num_elections_with_hits,
        "total_method_counts_third_or_lower": method_counts,
        "method_counts_third_place": third_place_hits,
        "method_counts_lower": third_or_fewer_hits,
        "num_cands_for_third_place_hits": list(third_place_num_cands),
        "num_cands_for_third_or_lower_hits": list(third_or_fewer_num_cands),
        "places": list(places),
        "num_cands:place": Counter(cands_vs_place)
    }

    output_data = {
        "metadata": metadata,
        "changes": files
    }

    # write to output file
    output_file = f"/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/new/{country}.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")

def main():
    gen_metadata_for_country('civs')
    gen_metadata_for_country('australia')
    gen_metadata_for_country('american')
    gen_metadata_for_country('scotland')

if __name__ == "__main__":
    main()