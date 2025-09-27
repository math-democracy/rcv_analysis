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

# compare majority winner to the winner of different methods
def check_winner(country):
    
    file = f"/Users/belle/Desktop/build/rcv/results/current/{country}.csv"
    df = pd.read_csv(file)
    result = {}

    methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']

    for _, row in df.iterrows():
        file = row['file']
        majority_fav = get_majority_favourite(country, file)
        res = {}
        winners = ""
        for m in methods:
            r = ast.literal_eval(row[m])
            res[m] = majority_fav in r

            if majority_fav not in r:
                winners += f"{m}-{r[0]}"

        if majority_fav == None:
            result[file] = None
        else:
            winners += majority_fav
            res["winners"] = winners
            result[file] = res
    return result

def run_all():
    all_result = {}
    for c in ['america', 'scotland', 'australia']:
        res = check_winner(c)
        all_result[c] = res
    
    with open("output.json", "w") as f:
        json.dump(all_result, f, indent=4)

run_all()