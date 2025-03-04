import pandas as pd
import json
import ast

def count_winners(file):
    df = pd.read_csv(file,dtype=str)
    
    voting_methods = [c for c in df.columns if c!='file' and c!='Unnamed: 0' and c!='numCands' and 'rank' not in c]

    winner_counts = {method: {} for method in voting_methods}
    
    for _, row in df.iterrows():
        for method in voting_methods:
            winners = [x.strip() for x in ast.literal_eval(row[method]) if x]
            num_winners = len(winners)

            if num_winners in winner_counts[method]:
                winner_counts[method][num_winners] += 1
            else:
                winner_counts[method][num_winners] = 1

            # if method == "condorcet" and num_winners == 0:
            #     # when no condorcet winner
            #     #print(row['file'])
            #     break
    
    with open('winner_counts.json', 'w') as f:
        json.dump(winner_counts, f, indent=4)
    
    print("Winner counts saved to winner_counts.json")

filepath = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/results/current/scotland.csv'
#filepath = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/results/scotland.csv'
count_winners(filepath)