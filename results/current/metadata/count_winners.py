import pandas as pd
import json
import ast

def count_winners(file):
    df = pd.read_csv(file,dtype=str)

    irv_condorcet_diff = 0
    
    voting_methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']

    winner_counts = {method: {} for method in voting_methods}
    total = 0
    for _, row in df.iterrows():
        total += 1
        for method in voting_methods:
            winners = [x.strip() for x in ast.literal_eval(row[method]) if x]
            num_winners = len(winners)
            if num_winners in winner_counts[method]:
                winner_counts[method][num_winners] += 1
            else:
                winner_counts[method][num_winners] = 1

            # if method == "IRV":
            #     condorcet_winner = [x.strip() for x in ast.literal_eval(row["condorcet"]) if x]
            #     if len(condorcet_winner) > 0:
            #         if winners[0] != condorcet_winner[0]:
            #             print(row['file'])
            #             print(condorcet_winner)
            #             print(winners)
            #             irv_condorcet_diff += 1

            if method == "ranked-pairs":
                winner = [x.strip() for x in ast.literal_eval(row["ranked-pairs"]) if x]
                if len(winner) == 0:
                    print("/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/" + row['file'])

    
    print(irv_condorcet_diff)
    print(total)
    with open('winner_counts.json', 'w') as f:
        json.dump(winner_counts, f, indent=4)
    
    print("Winner counts saved to winner_counts.json")

filepath = '/Users/belle/Desktop/build/rcv/results/current/america.csv'
#filepath = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/results/scotland.csv'
count_winners(filepath)