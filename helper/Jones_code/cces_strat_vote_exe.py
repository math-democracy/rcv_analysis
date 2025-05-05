
import random
import pandas as pd
import math
import operator
import numpy as np
import copy
import csv
import os
import statistics
import warnings
import sys
warnings.simplefilter(action='ignore', category=FutureWarning)
import multiprocessing
import time
import traceback
import json
import pickle

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        # if isinstance(obj, np.floating):
        #     return float(obj)
        # if isinstance(obj, np.ndarray):
        #     return obj.tolist()
        return super(NpEncoder, self).default(obj)



from election_class import *
from ballot_modifications_class import *
from strat_vote_class import *


#####TODO
## 




###############################################################################
###############################################################################
##### parameters
## github repo version
# data_path = './CCES_data'
## HPC version
data_path = '/home/aschult2/Desktop/CCES_data'
vote_frac = 1
mp_pool_size = 6
###############################################################################
###############################################################################





####################################################
##### Functions to run searches
####################################################

def get_cces(path, model):
    cand_names=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    num_cands = int(path[path.find('cands')-1])
    
    # print('reading parquet')

    df = pd.read_parquet(path, engine='pyarrow')

    # print('getting model df')

    model_to_select=model
    #Now filter the dataframe by the model you want, and unpickle the preference profiles
    model_df = df[df['model'] == model_to_select].copy()
    model_df['profile'] = model_df['profile'].apply(lambda x: pickle.loads(x) if isinstance(x, bytes) else x)
    model_df.reset_index(inplace=True)

    # print('getting profile')

    lxn_list = []
    for i in range(len(model_df)):
    # for i in range(100):
        lxn_df = model_df.at[i, 'profile']
        ballot_list = []
        count_list = []
        for j in range(len(lxn_df)):
            count_list.append(lxn_df.at[j, 'Count'])
            ballot = ''
            for k in range(1,6):
                try:
                    if lxn_df.at[j, 'rank'+str(k)]=='skipped':
                        # print('break1')
                        # print(k)
                        break
                    else:
                        ballot += cand_names[int(lxn_df.at[j, 'rank'+str(k)])]
                except:
                    # print('break2')
                    # print(k)
                    break
            ballot_list.append(ballot)

        df_dict = {'ballot': ballot_list, 'Count': count_list}
        profile = pd.DataFrame(df_dict)

        lxn_list.append([i, profile, num_cands])
        
    return lxn_list


    
###############################################################################
###############################################################################

def anom_search_strats_shell(params):
    lxn_method, ballot_mod, file_path, profile, num_cands = params
    
    try:
        return [lxn_method.__name__, ballot_mod.__name__, file_path, num_cands] + anom_search_strats(profile, num_cands, lxn_method, ballot_mod, vote_frac)
    except:
        print('###############################################')
        print('###############################################')
        print('Error in election:', params[2])
        print('Election method:', params[0])
        print('Running search:', params[1])
        print(traceback.format_exc())
        print('###############################################')
        print('###############################################')
        return [params[0], params[1], params[2], params[4], [], 0]


    
        




###############################################################################
###############################################################################
##### Run this code
###############################################################################
###############################################################################
if __name__=='__main__':

    destination_base = './CCES_anom_strat_results'
    
    if not os.path.exists(destination_base):
        os.makedirs(destination_base)
        
    models = ['(True, True, False, False)',
    '(False, True, False, False)',
    '(True, False, False, False)',
    '(True, True, True, False)',
    '(True, True, False, True)',
    '(False, False, True, False)',
    '(False, False, True, True)']
    
    for cces_file in os.listdir(data_path):
    # for cces_file in ['Alabama_distribution1_3cands.parquet']:
        
        if 'Alabama' not in cces_file:
            continue
        
        # print(cces_file)
        for model in models:
            model_string = ''
            for char in model:
                if char in ['T','F']:
                    model_string += char
            # print(model_string)
        
            full_model_name = cces_file[:cces_file.find('.parquet')]+'_'+model_string
            # print(full_model_name)
            
            if not os.path.exists(destination_base+'/stratvoting/'+full_model_name):
                os.makedirs(destination_base+'/stratvoting/'+full_model_name)
                
            
            
            lxn_list = get_cces(data_path+'/'+cces_file, model)
            
            
            ##### testing singlethreaded
            # for lxn in lxn_list:
            #     print(lxn[0])
            #     data = frac_upMonoPR(lxn[1], 3, 1)
    
            
            ##### prepare to search for anomalies
            lxn_methods = [plurality, plurality_runoff, IRV, smith_irv, smith_plurality, 
                           minimax, smith_minimax, ranked_pairs, 
                           Borda_PM, Borda_OM, Borda_AVG, bucklin]
    
            ballot_mod_methods = [strat_compromise, strat_truncate_L, strat_truncate_W, strat_bury_shallow, strat_bury_deep]
            
            gen_lxn_list = []
            for lxn in lxn_list:
                for lxn_method in lxn_methods:
                    for ballot_mod in ballot_mod_methods:
                        gen_lxn_list.append([lxn_method, ballot_mod]+lxn)
                
            pool = multiprocessing.Pool(processes=mp_pool_size)
            massive_results = pool.map(anom_search_strats_shell, gen_lxn_list)
        
            with open(destination_base+'/stratvoting/'+full_model_name+'/massive_results_data.json', "w") as f:
                json.dump(massive_results, f, cls=NpEncoder)
            
            ## data frame for top line results 
            exp_val_table = pd.DataFrame(0, index = [ballot_mod.__name__ for ballot_mod in ballot_mod_methods], 
                                    columns = [lxn_method.__name__ for lxn_method in lxn_methods])
            prob_change_table = pd.DataFrame(0, index = [ballot_mod.__name__ for ballot_mod in ballot_mod_methods], 
                                            columns = [lxn_method.__name__ for lxn_method in lxn_methods])
            
            for lxn in massive_results:
                lxn_method = lxn[0]
                ballot_mod = lxn[1]
                if lxn[4]:
                    exp_val_table.at[ballot_mod, lxn_method] += np.mean(lxn[4])/len(lxn_list)
                prob_change_table.at[ballot_mod, lxn_method] += lxn[5]/len(lxn_list)
        
            exp_val_table.to_csv(destination_base+'/stratvoting/'+full_model_name+'/expected_values.csv')
            prob_change_table.to_csv(destination_base+'/stratvoting/'+full_model_name+'/prob_change_winner.csv')













