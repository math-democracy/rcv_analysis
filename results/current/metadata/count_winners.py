import pandas as pd
import json

def count_winners(file):
    df = pd.read_csv(file)
    
    voting_methods = df.columns[3:]
        
    winner_counts = {method: {} for method in voting_methods}
    
    for _, row in df.iterrows():
        for method in voting_methods:
            winners = eval(row[method])
            num_winners = len(winners)

            if num_winners in winner_counts[method]:
                winner_counts[method][num_winners] += 1
            else:
                winner_counts[method][num_winners] = 1
            
            if method == "condorcet" and num_winners == 0:
                # when no condorcet winner
                print(row['file'])
    
    with open('winner_counts.json', 'w') as f:
        json.dump(winner_counts, f, indent=4)
    
    print("Winner counts saved to winner_counts.json")

count_winners('./scotland.csv')