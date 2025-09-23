import pandas as pd
import json
from collections import Counter
import ast

country = 'america'

def gen_metadata_for_country(country):
    file_path = f'analysis/first_place_analysis/new/{country}.csv'  # Replace with file path
    df = pd.read_csv(file_path)
    print(df.columns)

    methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']
    num_cands_kept = 4

    files = {}
    method_counts = dict.fromkeys(methods, 0)
    third_place_hits = dict.fromkeys(methods, 0)
    third_or_fewer_hits = dict.fromkeys(methods, 0)

    third_place_num_cands = set()
    third_or_fewer_num_cands = set()

    num_elections_with_hits = 0

    cands_vs_place = []

    fourth_or_lower = {method: [] for method in methods}
    #fourth_or_lower['plurality'].append('plurality')

    places = set()

    with open('analysis/first_place_analysis/first_place_ranks.json') as fp_file:
        first_place_ranks = json.load(fp_file)

    for _, row in df.iterrows():
        changes = {}

        none_types = [None,'[None]','[]']

        for method in methods:
            #print(row[f'{method}_rank'])
            #print(row)
            if row[method] not in none_types and row[method] != "unknown" and row[method] != "writein" and row['numCands'] > 3 and row[f'{method}_rank'] != 'multiple' and int(row[f'{method}_rank']) >= 3:
                changes[method] = {
                    "num_cands": int(row['numCands']),
                    "winner": row[method],
                    "rank (out of first place votes)": int(row[f'{method}_rank'])
                }

                cands_vs_place.append(f"{int(row['numCands'])}:{int(row[f'{method}_rank'])}")
                method_counts[method] += 1

                if int(row[f'{method}_rank']) == 3:  
                    third_place_hits[method] += 1
                    third_place_num_cands.add(row['numCands'])
                else:
                    third_or_fewer_hits[method] += 1
                    third_or_fewer_num_cands.add(row['numCands'])
                    #print(method)
                    first_place_file = first_place_ranks[country][f'raw_data/{country}/processed_data/{row['file']}']
                    if ast.literal_eval(row[method])[0] in first_place_file:
                        diff = first_place_file[list(first_place_file.keys())[0]] - first_place_file[ast.literal_eval(row[method])[0]]
                        # if row['file'] == 'e-renfs17-ballots/Clarkston,NetherleeandWilliamwood_e-renfs17-4.csv':
                        #     print(first_place_file[list(first_place_file.keys())[0]],first_place_file[row[method]])
                        #     print(list(first_place_file.keys())[0], row[method])
                    else:
                        diff = first_place_file[list(first_place_file.keys())[0]] 

                    
                    fourth_or_lower[method].append(f'(place = {int(row[f'{method}_rank'])}, numCands = {int(row['numCands'])}, diff = {diff}, total votes = {sum(first_place_file.values())})  ' + row['file'])
                    

                places.add(int(row[f'{method}_rank']))
                
        if len(changes) > 0:
            changes['first_place_ranks'] = first_place_ranks[country][f'raw_data/{country}/processed_data/{row['file']}']
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
        "num_cands:place": Counter(cands_vs_place),
        "fourth_or_lower": fourth_or_lower
    }

    output_data = {
        "metadata": metadata,
        "changes": files
    }

    # write to output file
    output_file = f"analysis/first_place_analysis/new/{country}.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")

def main():
    #gen_metadata_for_country('civs')
    #gen_metadata_for_country('australia')
    gen_metadata_for_country('america')
    #gen_metadata_for_country('scotland')

if __name__ == "__main__":
    main()