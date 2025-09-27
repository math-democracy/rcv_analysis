import pandas as pd
import os
import json
import csv 

'''
this combines all the interesting parts of each of the results to generate 1 metadata file
'''

folder_path = "" #folder with the individual results like australia_borda_scores_0.1.json

def extract_method_counts(folder_path):
    result = {}
    
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(".json"):
                file_path = os.path.join(dirpath, filename)
                parts = file_path.split('/')
                name = parts[-1].replace('.json', '')
                method = name.split('_')[-3]

                print(parts, method)

                f = name + "-" + method
                
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    
                    if "metadata" in data and "method_counts" in data["metadata"]:
                        entry = {}
                        d = data["metadata"]["method_counts"]
                        elections = data["metadata"]["election_with_changes"]
                        d["elections_with_changes"] = elections
                        d["country"] = name.split("_")[0]
                        d["percentage"] = name.split("_")[-1]
                        d["method"] = method
                        entry.update(d)
                        result[f] = entry
            
    return result

method_counts_list = extract_method_counts(folder_path)

methods = set()
for methods_dict in method_counts_list.values():
    for key in methods_dict.keys():
        if "_fringe" not in key:
            methods.add(key)

initial_columns = ["elections_with_changes", "country", "percentage", "method"]
remaining_columns = sorted(methods - set(initial_columns))
columns = initial_columns + remaining_columns

with open("sorted_by_country.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["filename"] + columns)
    
    for file, methods_dict in method_counts_list.items():
        row = [file] + [methods_dict.get(method, "") for method in columns]
        writer.writerow(row)