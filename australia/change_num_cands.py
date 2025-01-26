import pandas as pd
import os

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/australia/processed_data'

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if (filename.endswith('csv')):
            print(filename)
            full_path = os.path.join(dirpath, filename)
            df = pd.read_csv(full_path)
            rank = [c for c in df.columns if 'rank' in c]
            num_cands = rank[-1].replace('rank','')
            df['numCands'] = num_cands
            df.to_csv(full_path)
       
