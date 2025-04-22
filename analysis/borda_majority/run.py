import json
import pandas as pd
import ast

def get_majority_favourite(country, filename):
    first_place_file = "/Users/belle/Desktop/build/rcv/analysis/first_place_analysis/first_place_ranks.json"
    with open(first_place_file, "r") as file:
        data = json.load(file)

    country_data = data.get(country, {})

    for path, votes in country_data.items():
        if path.endswith(filename):
            total_votes = sum(votes.values())
            for name, vote_count in votes.items():
                if vote_count > total_votes / 2:
                    return name
            return None
    return None

def check_borda_winner(country):
    
    file = f"/Users/belle/Desktop/build/rcv/results/current/{country}.csv"
    df = pd.read_csv(file)
    result = {}

    for _, row in df.iterrows():
        file = row['file']
        borda_pm = ast.literal_eval(row['borda-pm'])
        borda_om = ast.literal_eval(row['borda-om'])
        borda_avg = ast.literal_eval(row['borda-avg'])

        majority_fav = get_majority_favourite(country, file)

        if majority_fav == None:
            result[file] = None
        else:
            result[file] = {
                "borda_pm": majority_fav in borda_pm,
                "borda_om": majority_fav in borda_om,
                "borda_avg": majority_fav in borda_avg,
                "results": row['borda-pm'] + row['borda-om'] + row['borda-avg'] + majority_fav
            }
    return result

def run_all():
    all_result = {}
    for c in ['america', 'scotland', 'australia']:
        res = check_borda_winner(c)
        all_result[c] = res
    
    with open("output.json", "w") as f:
        json.dump(all_result, f, indent=4)

run_all()