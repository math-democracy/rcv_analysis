import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import os
import pandas as pd
import json
from collections import Counter

files = {}

# Open and read the JSON file
with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/party_breakdown.json', 'r') as file:
    party_info = json.load(file)
def process_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                print(f'processing: {filename}')
                full_path = os.path.join(dirpath, filename)

                df = pd.read_csv(full_path)

                file_key = full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')
                consolidate_key = party_info[file_key]['party_dict']

                df.replace(consolidate_key, inplace=True)

                output_path = full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data/', '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/data/')
                #print('/'.join(output_path.split('/')[:-1]))
                if not os.path.exists('/'.join(output_path.split('/')[:-1])):
                    os.makedirs('/'.join(output_path.split('/')[:-1]))

                df.to_csv(output_path, index=False)

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data'
process_files(root_dir)
