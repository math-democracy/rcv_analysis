import pandas as pd
import json
from collections import Counter
import csv
import os
import ast

country = 'america'
file_path = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/results/current/{country}.csv'  # Replace with file path
df = pd.read_csv(file_path)

data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/new/{country}.csv'

methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']

with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/first_place_ranks.json') as fp_file:
    first_place_ranks = json.load(fp_file)

#print(all_data)
if os.stat(data_file).st_size > 0:
    # Clear the file by opening it in write mode
    with open(data_file, mode='w', newline='') as file:
        pass  # This will clear the file contents

for _, row in df.iterrows():
    #print(row['file'])
    all_data = {}
    ranks = first_place_ranks[country][f'raw_data/{country}/processed_data/{row['file']}']
    
    ranks = list(ranks.keys())
    
    all_data['file'] = row['file']
    all_data['numCands'] = row['numCands']
    
    for method in methods:
        all_data[method] = row[method]
        if len(ast.literal_eval(row[method])) == 1:
            if ast.literal_eval(row[method])[0] and ast.literal_eval(row[method])[0] in ranks:
                all_data[f'{method}_rank'] = ranks.index(ast.literal_eval(row[method])[0]) + 1
            elif ast.literal_eval(row[method])[0] not in ranks:
                all_data[f'{method}_rank'] = len(ranks) + 1
            else:
                all_data[f'{method}_rank'] = None
        elif len(ast.literal_eval(row[method])) == 0:
            all_data[f'{method}_rank'] = None
        else:
            all_data[f'{method}_rank'] = 'multiple'   

    if all_data:

        with open(data_file, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write the header if the file is empty
            if os.stat(data_file).st_size == 0:
                header = all_data.keys()
                writer.writerow(header)

            
            writer.writerow(all_data.values())

        