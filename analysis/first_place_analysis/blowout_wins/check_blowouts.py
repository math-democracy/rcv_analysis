import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import csv
import json
import os
import pandas as pd

with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/first_place_ranks.json') as file:
    first_place_ranks = json.load(file)

def get_blowout_wins(threshold):
    blowout_wins = {'america': [], 'scotland': [], 'australia': [], 'civs': []}

    for country in first_place_ranks.keys():
        for file in first_place_ranks[country]:
            ranks = first_place_ranks[country][file]
            
            candidates = list(ranks.keys())
            if len(candidates) >= 2:
                first_place = candidates[0]
                second_place = candidates[1]
                
                if ranks[second_place] < ranks[first_place] * threshold:
                    blowout_wins[country].append(file)

    return blowout_wins

def main():
    # blowout win is defined to be an election where the cand who got second most first 
    # place votes got (threshold)%  of the cand who got the most first place votes
    threshold = 0.6
    blowout_wins = get_blowout_wins(threshold)

    all_data = {
        "num_america": len(blowout_wins['america']),
        "num_scotland": len(blowout_wins['scotland']),
        "num_australia": len(blowout_wins['australia']),
        "num_civs": len(blowout_wins['civs']),
        "files": blowout_wins
    }

    # write to output file
    output_file = f"/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/blowout_wins/blowout_wins{threshold}.json"
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4)

    print(f"Grouped changes with metadata have been exported to {output_file}")

if __name__ == "__main__":
    main()