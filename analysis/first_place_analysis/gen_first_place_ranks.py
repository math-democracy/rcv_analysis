import os
import pandas as pd
import json

american_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data'
australia_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/australia/processed_data'
scotland_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data'
civs_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/civs/processed_data'

output_data = {}

def main():
    american = {}
    for dirpath, dirnames, filenames in os.walk(american_dir):
        for filename in filenames:
            print(filename)
            if filename.endswith('.csv'):
                full_path = os.path.join(dirpath, filename)

                df = pd.read_csv(full_path, low_memory=False)
                value_counts = df['rank1'].value_counts(ascending=False)
                # return list of candidates in descending order of first place votes
                rank = value_counts.to_dict()
                
                american[full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')] = rank

    australia = {}
    for dirpath, dirnames, filenames in os.walk(australia_dir):
        for filename in filenames:
            print(filename)
            if filename.endswith('.csv'):
                full_path = os.path.join(dirpath, filename)

                df = pd.read_csv(full_path, low_memory=False)
                value_counts = df['rank1'].value_counts(ascending=False)
                # return list of candidates in descending order of first place votes
                rank = value_counts.to_dict()
                
                australia[full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')] = rank

    scotland = {}
    for dirpath, dirnames, filenames in os.walk(scotland_dir):
        for filename in filenames:
            print(filename)
            if filename.endswith('.csv'):
                full_path = os.path.join(dirpath, filename)

                df = pd.read_csv(full_path, low_memory=False)
                value_counts = df['rank1'].value_counts(ascending=False)
                # return list of candidates in descending order of first place votes
                rank = value_counts.to_dict()
                
                scotland[full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')] = rank

    civs = {}
    for dirpath, dirnames, filenames in os.walk(civs_dir):
        for filename in filenames:
            print(filename)
            if filename.endswith('.csv'):
                full_path = os.path.join(dirpath, filename)

                df = pd.read_csv(full_path, low_memory=False)
                value_counts = df['rank1'].value_counts(ascending=False)
                # return list of candidates in descending order of first place votes
                rank = value_counts.to_dict()
                
                civs[full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')] = rank

    output_data = {"america": american,
                   "australia": australia,
                   "scotland": scotland,
                   "civs": civs}
    
    output_file = "/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/first_place_ranks.json"
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=4)


if __name__ == '__main__':
    main()