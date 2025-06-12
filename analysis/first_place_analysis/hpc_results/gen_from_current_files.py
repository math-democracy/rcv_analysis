import pandas as pd
import json
from collections import Counter
import csv
import os
import ast

country = 'america'
file_path = f'/Users/karenxiao/MyPythonCode/ranked_choice_voting/hpc_results/stability/results/Alabama_distribution1_3cands_top4stability_FFTF.csv'  # Replace with file path

df = pd.read_csv(file_path)
#/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/hpc_results/results
data_file = file_path.replace('/hpc_results/stability/','/rcv_proposal/analysis/first_place_analysis/hpc_results/')
#print(data_file)
methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval','smith']

first_place_ranks = pd.read_csv(file_path.replace('/stability/results/','/gen_scores/results/first_place_scores/').replace('_top4stability',''))

with open(data_file, mode='w', newline='') as file:
    pass  # This will clear the file contents

all_data = {}

for i, row in df.iterrows():
    ranks = first_place_ranks.iloc[i].to_dict()
    ranks = {k: v for k, v in sorted(ranks.items(), key=lambda item: item[1], reverse=True)}
    ranks = list(ranks.keys())
    
    all_data['file'] = row['file']
    
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

        