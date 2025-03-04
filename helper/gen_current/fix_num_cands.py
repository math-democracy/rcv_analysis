import pandas as pd
import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
from helper.new_csv_loader import new_loader
#-------------------------------------------------------------------------------------------
#existing voting methods in votekit 
import votekit.elections as v
#import pref_voting.voting_methods as p #

#-------------------------------------------------------------------------------------------
#cleaning and other logistics
from votekit.cleaning import remove_noncands
from votekit.ballot import Ballot
from votekit.pref_profile import PreferenceProfile

import os

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data'
filenames_col = []
numcands_col = []
#votekit
def v_profile(
        filename: str, 
        to_remove: list = ["undervote", "overvote", "UWI","uwi"]
    )-> PreferenceProfile:
    return remove_noncands(new_loader(filename)[0], to_remove)

def process_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.csv'):
                        print(f'processing: {filename}')
                        full_path = os.path.join(dirpath, filename)
                        prof = v_profile(full_path)

                        cands_drop_skipped = [c for c in prof.candidates if c != 'skipped']

                        numcands_col.append(len(cands_drop_skipped))
                        filenames_col.append(full_path.replace(root_dir+'/',''))
                        
    df = pd.DataFrame({'file':filenames_col,'numCands':numcands_col})
    
    return df

df = process_files(root_dir)

original = pd.read_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/results/current/scotland.csv')
original['merge_key'] = original['file'].apply(lambda x: next((name for name in df['file'] if x.endswith(name.split('/')[1])), None))

new = original.merge(df, how='left', left_on='merge_key', right_on='file')

if len(original) != len(new):
      print('INCONSISTENT LENGTH')

columns = ['file_x', 'numCands_y', 'plurality', 'IRV', 'top-two',
       'borda-pm', 'borda-om-no-uwi', 'borda-avg-no-uwi', 'top-3-truncation',
       'condorcet', 'minimax', 'smith_plurality', 'smith_irv', 'smith-minimax',
       'ranked-pairs', 'bucklin', 'approval', 'smith']
new = new[columns].rename(columns = {'file_x':'file', 'numCands_y':'numCands'})

new.to_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/scotland_new.csv', index=False)

