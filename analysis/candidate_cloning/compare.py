import pandas as pd
import json
import re
from collections import defaultdict
import ast
import math
file_path = '/Users/belle/Desktop/build/rcv_proposal/analysis/candidate_cloning/updated_results.csv'  # Replace with your actual file path

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

def main(country):
    # Get row where no candidates were removed
    df = pd.read_csv(file_path)

    df = df[df['country'] == country].iloc[:, 1:]
    original_row = df[df['percentage'] == 'ORIGINAL']

    print(original_row)
    # Store original winners
    original_winners = {}
    for _, row in original_row.iterrows():
        file = row['file'].split('/')[-1]
        original_winners[file] = {col: row[col] for col in df.columns if col not in ['file', 'candidate_cloned', 'country', 'percentage', 'Unnamed: 0', 'numCands']}


    winners = {}
    total_files = set()

    for _, row in df.iterrows():
        file = row['file'].split('/')[-1]
        candidate_cloned = row['candidate_cloned']

        if pd.notna(candidate_cloned):
            candidate_cloned = candidate_cloned.replace(' (UNKNOWN)', '')

        percentage = row['percentage']
        total_files.add(file)
        
        if candidate_cloned != 'none' and candidate_cloned != None and candidate_cloned != "NaN":   
            if file not in winners:
                winners[file] = []
            file_changes = {'candidate_cloned': candidate_cloned, 'percentage': percentage, 'changes': {}}
            
            try:
                for method in original_winners[file]:
                    if (pd.notna(row[method]) and pd.notna(original_winners[file][method])):
                        # baseline = re.sub(r"(?<=[a-zA-Z])'(?=[a-zA-Z])", "", original_winners[file][method])
                        # new = re.sub(r"(?<=[a-zA-Z])'(?=[a-zA-Z])", "", row[method])
                        # candidate_cloned = re.sub(r"(?<=[a-zA-Z])'(?=[a-zA-Z])", "", candidate_cloned)
                        # print(original_winners[file][method])
                        baseline_winner = original_winners[file][method].strip("{}").replace("' ", "").replace(" '", "'").replace("''", "").replace('""', '"').replace('/', "").replace(" (UNKNOWN)", "").replace('\"', '') #.replace("' ", "").replace(" '", "'")
                        new_winner = row[method].strip("{}").replace(" (UNKNOWN)", "").replace("' ", "").replace(" '", "'").replace("''", "").replace('""', '"').replace('/', "").replace('\"', '')#.replace("' ", "").replace(" '", "'")
                        # print(baseline_winner)
                        baseline_arr = ast.literal_eval(baseline_winner)
                        # print(new_winner)
                        # print(row, new_winner)
                        new_arr = ast.literal_eval(new_winner)

                        # candidate_cloned not in baseline_arr
                        if baseline_winner != new_winner and not (candidate_cloned in baseline_arr and 'Cloned_Candidate' in new_arr and str(percentage) == "0.5"):
                            
                            file_changes['changes'][method] = {
                                'baseline_winner': baseline_winner,
                                'new_winner': new_winner,
                                'common_winner': bool(set(baseline_arr) & set(new_arr)),
                                'cloned_winner': candidate_cloned in new_arr,
                                'cloned_loser':  candidate_cloned in baseline_arr
                            }
            except Exception as e:
                # break
                print(f"could not parse {file}, {e}")
                # print(row)
            if file_changes['changes']: 
                winners[file].append(file_changes)

            if (len(winners[file]) == 0):
                del winners[file]
        

    election_with_changes = len(winners)
    method_counts = defaultdict(set)
    method_combinations = defaultdict(set)
    percentage_count = defaultdict(set)
    num_common_winner = set()
    num_cloned_was_winner = set()
    num_cloned_is_winner = set()
    percentage_per_method = defaultdict(lambda: defaultdict(set))


    for election, changes in winners.items():
        all_methods = set()
        for change in changes:
            perc = str(change['percentage'])
            percentage_count[perc].add(election)
        
            methods_affected = change['changes']
            for m in methods_affected:
                percentage_per_method[m][perc].add(election)


            all_methods.update(change['changes'].keys())  # Add all methods to a set for the election
            for m in change['changes'].values():
                if m['common_winner']:
                    num_common_winner.add(election)
                
                if m['cloned_winner']:
                    num_cloned_is_winner.add(election)
                
                if m['cloned_loser']:
                    num_cloned_was_winner.add(election)

        for method in all_methods:
            method_counts[method].add(election)

        if all_methods:
            sorted_methods = sorted(all_methods)  # Ensure consistent ordering
            combination_key = ", ".join(sorted_methods)
            method_combinations[combination_key].add(election)
        

    final_method_counts = {method: len(elections) for method, elections in method_counts.items()}
    final_combination_counts = {combination: len(elections) for combination, elections in method_combinations.items()}
    final_percentage_counts = {method: len(elections) for method, elections in percentage_count.items()}
    final_method_percentage_counts = {
        method: {perc: len(elections) for perc, elections in percentages.items()}
        for method, percentages in percentage_per_method.items()
    }

    metadata = {
        "total_elections": len(total_files),
        "election_with_changes": election_with_changes,
        "number of common candidates": len(num_common_winner),
        "cloned candidate was baseline winner": len(num_cloned_was_winner),
        "cloned candidate is new winner": len(num_cloned_is_winner),
        "percentage_counts": dict(sorted(final_percentage_counts.items(), key=lambda x: x[1], reverse=True)),
        "method_counts": dict(sorted(final_method_counts.items(), key=lambda x: x[1], reverse=True)),
        "method_counts_by_percentage": final_method_percentage_counts
        # "method_combinations": dict(sorted(final_combination_counts.items(), key=lambda x: x[1], reverse=True))
    }

    output_data = {
        "metadata": metadata,
        "winners": winners
    }

    output_file = f"{country}.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")


countries = ['scotland', 'america', 'australia']
for country in countries:
    main(country)