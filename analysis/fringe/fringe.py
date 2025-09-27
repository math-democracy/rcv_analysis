import pandas as pd
import ast
import json
from collections import defaultdict

# rank candidates within each elections using the score of choice (in our analysis, borda average or mention)
# and determine whether a candidate is considered fringe given the threshold.
def rank_candidates(file_path, threshold):
    with open(file_path, 'r') as file:
        data = json.load(file)
    result = {}
    for filename, candidates in data.items():
        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        first_place_score = sorted_candidates[0][1] if sorted_candidates else 0
        result[filename] = {}
        # 1 = is_below_x, 0 = not is_below_x
        for _, (name, score) in enumerate(sorted_candidates):
            is_below_x = score < threshold * first_place_score
            result[filename][name] = 1 if (is_below_x) else 0
    return result

# apply the candidate ranks to the winners for each election and method
def compute_fringe(row, ranks):
    methods = ["plurality","IRV","top-two","borda-pm","borda-om","borda-avg","top-3-truncation","condorcet","minimax","smith_plurality","smith_irv","smith-minimax","ranked-pairs","bucklin","approval","smith"]
    file = row['file'].split('/')[-1]
    result = {}
    for method in methods:
        row_name = method + "_fringe"
        winners = ast.literal_eval(row[method])
        result[row_name] = [ranks.get(file, {}).get(winner, None) for winner in winners]
    return pd.Series(result)

def read_winners(ranks, file):
    df = pd.read_csv(file)
    df = df.join(df.apply(compute_fringe, axis=1, args=(ranks,)))
    return df


def parse_data(df):
    fringe_columns = [col for col in df.columns if col.endswith('_fringe')]
    filtered_df = df[df[fringe_columns].applymap(lambda x: isinstance(x, list) and 1 in x).any(axis=1)]
    filtered_df = filtered_df[sorted(filtered_df.columns)]
    filtered_df = filtered_df.set_index('file')
    return filtered_df

def filter_columns(row):
    methods = ["plurality","IRV","top-two","borda-pm","borda-om","borda-avg","top-3-truncation","condorcet","minimax","smith_plurality","smith_irv","smith-minimax","ranked-pairs","bucklin","approval","smith"]
    filtered_data = {}
    for method in methods:
        fringe_col = method + "_fringe"
        if fringe_col in row and isinstance(row[fringe_col], list) and 1 in row[fringe_col]:
            filtered_data[method] = row[method]
            filtered_data[fringe_col] = row[fringe_col]
    return filtered_data

def main(scores, file, threshold, country, type):
    ranks = rank_candidates(scores, threshold)
    df = read_winners(ranks, file)
    df = parse_data(df)
    filtered_json_data = {file: filter_columns(row) for file, row in df.iterrows()}

    #caldulate metadata for the specific file
    fringe_count = {}
    method_counts = defaultdict(set)
    election_with_changes = len(filtered_json_data)

    for election, changes in filtered_json_data.items():
        all_methods = set()
        for change in changes:
            all_methods.update([change])
        for method in all_methods:
            method_counts[method].add(election)

    for file_changes in filtered_json_data.values():
        num_spoilers = len(file_changes)
        fringe_count[num_spoilers] = fringe_count.get(num_spoilers, 0) + 1

    final_method_counts = {method: len(elections) for method, elections in method_counts.items()}

    metadata = {
        "election_with_changes": election_with_changes,
        "spoiler_counts": dict(sorted(fringe_count.items(), key=lambda x: x[1], reverse=True)),
        "method_counts": dict(sorted(final_method_counts.items(), key=lambda x: x[1], reverse=True))
    }

    output_data = {
        "metadata": metadata,
        "winners": filtered_json_data
    }

    output_file = f"{country}_{type}_{threshold}.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)

for type in ['mention_scores', 'borda_scores']:
    for country in ['america', 'australia', 'civs', 'scotland']:
        # you can use f'{country}' to dynamically set the file path 
        scores_file = "" #eg. the borda scores file or mention scores file
        election_results = "" #path to election results
        # using for loop to change fringeness definition from 0.1-0.9 percent of the first place
        
        for i in range(1, 10):
            main(scores_file, election_results, (i/10), country, type)