import json
import pandas as pd
import ast

def get_condorcet_loser(country, filename):
    with open("./losers.json", "r") as file:
        data = json.load(file)
    
    country_data = data.get(country, {})

    filename = filename.split("/")[-1]
    loser = country_data[filename]
    if loser != None:
        loser = loser[0]

    return loser

def check_condorcet_loser(country):
    
    file = f"../../results/current/{country}.csv"
    df = pd.read_csv(file)
    result = {}

    methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']

    for _, row in df.iterrows():
        file = row['file']
        condorcet_loser = get_condorcet_loser(country, file)
        res = {}
        winners = ""
        for m in methods:
            r = ast.literal_eval(row[m])
            res[m] = condorcet_loser in r
        if condorcet_loser == None:
            result[file] = None
        else:
            winners += str(condorcet_loser)
            res["winners"] = winners
            result[file] = res
    return result

def run_all():
    all_result = {}
    for c in ['america', 'australia', 'scotland']:
        res = check_condorcet_loser(c)
        all_result[c] = res
    
    with open("results.json", "w") as f:
        json.dump(all_result, f, indent=4)

run_all()