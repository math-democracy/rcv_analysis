import pandas as pd
import ast
import json

def rank_candidates(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    result = {}
    for filename, candidates in data.items():
        sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        total_candidates = len(sorted_candidates)
        bottom_threshold = total_candidates // 3  # Bottom third count
        result[filename] = {}
        # 1 = bottom third, 0 = not bottom third
        for i, (name, _) in enumerate(sorted_candidates):
            result[filename][name] = 1 if i >= total_candidates - bottom_threshold else 0
    return result


def compute_fringe(row, ranks):
    methods = ["plurality","IRV","top-two","borda-pm","borda-om-no-uwi","borda-avg-no-uwi","top-3-truncation","condorcet","minimax","smith_plurality","smith_irv","smith-minimax","ranked-pairs","bucklin","approval"]
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
    filtered_df = filtered_df.drop(columns=['Unnamed: 0'])
    filtered_df = filtered_df[sorted(filtered_df.columns)]
    filtered_df = filtered_df.set_index('file')

    return filtered_df

def filter_columns(row):
    methods = ["plurality","IRV","top-two","borda-pm","borda-om-no-uwi","borda-avg-no-uwi","top-3-truncation","condorcet","minimax","smith_plurality","smith_irv","smith-minimax","ranked-pairs","bucklin","approval"]
    filtered_data = {}
    for method in methods:
        fringe_col = method + "_fringe"
        if fringe_col in row and isinstance(row[fringe_col], list) and 1 in row[fringe_col]:
            filtered_data[method] = row[method]
            filtered_data[fringe_col] = row[fringe_col]
    return filtered_data


ranks = rank_candidates('/Users/belle/Desktop/build/rcv_proposal/analysis/fringe/mention_scores/scotland_mention_scores.json')
df = read_winners(ranks, '/Users/belle/Desktop/build/rcv_proposal/results/current/scotland.csv')
df = parse_data(df)
filtered_json_data = {file: filter_columns(row) for file, row in df.iterrows()}
filtered_json = json.dumps(filtered_json_data, indent=4)

with open('filtered_data2.json', 'w') as f:
    f.write(filtered_json)
