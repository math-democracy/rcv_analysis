import os
from rcv_proposal.australia.aus_parse import parser

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/raw/Australia_Victoria_LegAssembly_2018' # UPDATE TO WHERE BLT DATA IS STORED eg. /Users/xiaokaren/MyPythonCode/ranked_choice_voting/raw/Australia_Victoria_LegAssembly_2022
output_folder = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/processed/' # UPDATE TO WHERE CSV DATA SHOULD BE SAVED eg. /Users/xiaokaren/MyPythonCode/ranked_choice_voting/processed/
output_folder += root_dir.split('/')[-1]

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.zip') or filename.endswith('.xlsx'):
            full_path = os.path.join(dirpath, filename)
            if 'NewSouthWales' in full_path:
                state = 'New South Wales'
            elif 'Victoria' in full_path:
                state = 'Victoria'
            
            parser(state, full_path, output_folder)