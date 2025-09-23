"""This script generates metadata to compare unstable elections between different 
    condensation methods"""
import json
import os

with open('analysis/stability/scotland_results_top4.json') as file:
    stability = json.load(file)

with open('analysis/mimic_single_party/methods/borda_score/scotland_results_top4.json') as file:
    borda = json.load(file)

with open('analysis/mimic_single_party/methods/first_place_score/scotland_results_top4.json') as file:
    first_place = json.load(file)

with open('analysis/mimic_single_party/methods/mention_score/scotland_results_top4.json') as file:
    mention = json.load(file)

unstable_elections = stability['changes']

root_dir = "raw_data/scotland/processed_data"
methods = ['plurality','IRV','top-two','borda-pm','borda-om','borda-avg','top-3-truncation','condorcet','minimax','smith_plurality','smith_irv','smith-minimax','ranked-pairs','bucklin','approval']

files = {}
for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                full_path = os.path.join(dirpath, filename)
                file_key = full_path.replace('','')
                print(filename)
                stable = {m: {} for m in methods}
                for method in methods:
                    

                    if file_key in stability['changes'].keys():
                        if method in stability['changes'][file_key]['changes'].keys():
                            stable[method]['top4plurality'] = False
                        else:
                            stable[method]['top4plurality']  = True
                    elif file_key in stability['stable_elections']:
                        stable[method]['top4plurality']  = True
                    else:
                        stable[method]['top4plurality']  = None

                    if file_key in borda['changes'].keys():
                        if method in borda['changes'][file_key]['changes'].keys():
                            stable[method]['borda'] = False
                        else:
                            stable[method]['borda']  = True
                    elif file_key in borda['stable_elections']:
                        stable[method]['borda']  = True
                    else:
                        stable[method]['borda']  = None
                    
                    if file_key in mention['changes'].keys():
                        if method in mention['changes'][file_key]['changes'].keys():
                            stable[method]['mention'] = False
                        else:
                            stable[method]['mention']  = True
                    elif file_key in mention['stable_elections']:
                        stable[method]['mention']  = True
                    else:
                        stable[method]['mention']  = None

                    if file_key in first_place['changes'].keys():
                        if method in first_place['changes'][file_key]['changes'].keys():
                            stable[method]['first_place'] = False
                        else:
                            stable[method]['first_place']  = True
                    elif file_key in first_place['stable_elections']:
                        stable[method]['first_place']  = True
                    else:
                        stable[method]['first_place']  = None

                files[file_key] = stable

output_file = f"analysis/mimic_single_party/metadata/stable_elections.json"

with open(output_file, "w") as f:
    json.dump(files, f, indent=4)
