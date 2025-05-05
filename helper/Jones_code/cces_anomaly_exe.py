
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
from anomaly_search_class import *


#####TODO
## 




###############################################################################
###############################################################################
##### parameters
## github repo version
# data_path = './CCES_data'
## HPC version
data_path = '/home/aschult2/Desktop/CCES_data'
frac = 1
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

def gen_search_for_anomaly(params):
    lxn_method, ballot_mod, file_path, profile, num_cands = params
    
    for vote_frac in vote_fracs:
        data = frac_general_search(profile, num_cands, lxn_method, ballot_mod, vote_frac)
        if data:
            return [lxn_method.__name__, ballot_mod.__name__, file_path, num_cands] + data
    
    return [lxn_method.__name__, ballot_mod.__name__, file_path, num_cands]
    
###############################################################################
###############################################################################

def IRV_upMonoSearch(params):
    foo1, foo2, file_path, profile, num_cands = params
    
    for vote_frac in vote_fracs:
        data = frac_upMonoIRV(profile, num_cands, vote_frac)
        if data:
            return ['IRV', 'upMono', file_path, num_cands] + data
    
    return ['IRV', 'upMono', file_path, num_cands]
    
def IRV_downMonoSearch(params):
    foo1, foo2, file_path, profile, num_cands = params
    
    for vote_frac in vote_fracs:
        data = frac_downMonoIRV(profile, num_cands, vote_frac)
        if data:
            return ['IRV', 'downMono', file_path, num_cands] + data
    
    return ['IRV', 'downMono', file_path, num_cands]
    
def IRV_noShowSearch(params):
    foo1, foo2, file_path, profile, num_cands = params
    
    for vote_frac in vote_fracs:
        data = frac_noShowIRV(profile, num_cands, vote_frac)
        if data:
            return ['IRV', 'noShow', file_path, num_cands] + data
    
    return ['IRV', 'noShow', file_path, num_cands]
    
def PR_upMonoSearch(params):
    foo1, foo2, file_path, profile, num_cands = params
    for vote_frac in vote_fracs:
        data = frac_upMonoPR(profile, num_cands, vote_frac)
        if data:
            return ['plurality_runoff', 'upMono', file_path, num_cands] + data
    
    return ['plurality_runoff', 'upMono', file_path, num_cands]
    
def PR_noShowSearch(params):
    foo1, foo2, file_path, profile, num_cands = params
    
    for vote_frac in vote_fracs:
        data = frac_noShowPR(profile, num_cands, vote_frac)
        if data:
            return ['plurality_runoff', 'noShow', file_path, num_cands] + data
    
    return ['plurality_runoff', 'noShow', file_path, num_cands]
    
def bucklin_noShowSearch(params):
    foo1, foo2, file_path, profile, num_cands = params
    
    for vote_frac in vote_fracs:
        data = frac_noShowBucklin(profile, num_cands, vote_frac)
        if data:
            return ['bucklin', 'noShow', file_path, num_cands] + data
    
    return ['bucklin', 'noShow', file_path, num_cands]
    
def smith_plur_noShowSearch(params):
    foo1, foo2, file_path, profile, num_cands = params
    
    for vote_frac in vote_fracs:
        data = frac_noShowSmithPlur(profile, num_cands, vote_frac)
        if data:
            return ['smith_plurality', 'noShow', file_path, num_cands] + data
    
    return ['smith_plurality', 'noShow', file_path, num_cands]
    
def smith_irv_noShowSearch(params):
    foo1, foo2, file_path, profile, num_cands = params
    
    for vote_frac in vote_fracs:
        data = frac_noShowSmithIRV(profile, num_cands, vote_frac)
        if data:
            return ['smith_irv', 'noShow', file_path, num_cands] + data
    
    return ['smith_irv', 'noShow', file_path, num_cands]
    

###############################################################################
###############################################################################

def sort_search(params):
    try:
        if type(params[0])==str:
            if params[0]=='IRV' and params[1]=='upMono':
                return IRV_upMonoSearch(params)
            if params[0]=='IRV' and params[1]=='downMono':
                return IRV_downMonoSearch(params)
            if params[0]=='IRV' and params[1]=='noShow':
                return IRV_noShowSearch(params)
            if params[0]=='plurality_runoff' and params[1]=='upMono':
                return PR_upMonoSearch(params)
            if params[0]=='plurality_runoff' and params[1]=='noShow':
                return PR_noShowSearch(params)
            if params[0]=='bucklin' and params[1]=='noShow':
                return bucklin_noShowSearch(params)
            if params[0]=='smith_plurality' and params[1]=='noShow':
                return smith_plur_noShowSearch(params)
            if params[0]=='smith_irv' and params[1]=='noShow':
                return smith_irv_noShowSearch(params)
        else:
            return gen_search_for_anomaly(params)
    except:
        print('###############################################')
        print('###############################################')
        print('Error in election:', params[2])
        print('Election method:', params[0])
        print('Running search:', params[1])
        print(traceback.format_exc())
        print('###############################################')
        print('###############################################')
        return [params[0], params[1], params[2], params[4]]
    
        




###############################################################################
###############################################################################
##### Run this code
###############################################################################
###############################################################################
vote_fracs = [1 - i/frac for i in range(frac)]
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
            
            if not os.path.exists(destination_base+'/anomalies/'+full_model_name):
                os.makedirs(destination_base+'/anomalies/'+full_model_name)
                
            
            
            lxn_list = get_cces(data_path+'/'+cces_file, model)
            
            
            ##### testing singlethreaded
            # for lxn in lxn_list:
            #     print(lxn[0])
            #     data = frac_upMonoPR(lxn[1], 3, 1)
    
            
            ##### prepare to search for anomalies
            lxn_methods = [plurality, plurality_runoff, IRV, smith_irv, smith_plurality, 
                           minimax, smith_minimax, ranked_pairs, 
                           Borda_PM, Borda_OM, Borda_AVG, bucklin]
    
            ballot_mod_methods = [laterNoHarm, strat_compromise, strat_truncate_L, strat_truncate_W, strat_bury_shallow, strat_bury_deep]
            full_anomaly_types = ['upMono', 'downMono', 'noShow'] + [ballot_mod.__name__ for ballot_mod in ballot_mod_methods]
    
            search_combos = {}
            for lxn_method in lxn_methods:
                for ballot_mod in ballot_mod_methods:
                    combo_name = lxn_method.__name__ + '_' + ballot_mod.__name__
                    ## list is file_names, num_cands, old_winner, new_winner, modified_ballots
                    search_combos[combo_name] = [[], [], [], [], []]
            ## adding the eight odd anomalies
            search_combos['IRV_upMono'] = [[], [], [], [], []]
            search_combos['IRV_downMono'] = [[], [], [], [], []]
            search_combos['IRV_noShow'] = [[], [], [], [], []]
            search_combos['plurality_runoff_upMono'] = [[], [], [], [], []]
            search_combos['plurality_runoff_noShow'] = [[], [], [], [], []]
            search_combos['bucklin_noShow'] = [[], [], [], [], []]
            search_combos['smith_plurality_noShow'] = [[], [], [], [], []]
            search_combos['smith_irv_noShow'] = [[], [], [], [], []]
    
            gen_lxn_list = []
            for lxn in lxn_list:
                for lxn_method in lxn_methods:
                    for ballot_mod in ballot_mod_methods:
                        gen_lxn_list.append([lxn_method, ballot_mod]+lxn)
            for lxn in lxn_list:
                gen_lxn_list.append(['IRV', 'upMono']+lxn)
                gen_lxn_list.append(['IRV', 'downMono']+lxn)
                gen_lxn_list.append(['IRV', 'noShow']+lxn)
                gen_lxn_list.append(['plurality_runoff', 'upMono']+lxn)
                gen_lxn_list.append(['plurality_runoff', 'noShow']+lxn)
                gen_lxn_list.append(['bucklin', 'noShow']+lxn)
                gen_lxn_list.append(['smith_plurality', 'noShow']+lxn)
                gen_lxn_list.append(['smith_irv', 'noShow']+lxn)
                
            pool = multiprocessing.Pool(processes=mp_pool_size)
            massive_results = pool.map(sort_search, gen_lxn_list)
        
            with open(destination_base+'/anomalies/'+full_model_name+'/massive_results_data.json', "w") as f:
                json.dump(massive_results, f, cls=NpEncoder)
            
            ## data frame for top line results 
            summary_results = pd.DataFrame(-1, index = full_anomaly_types, 
                    columns = [lxn_method.__name__ for lxn_method in lxn_methods])
            for lxn_method in lxn_methods:
                for ballot_mod in ballot_mod_methods:
                    summary_results[lxn_method.__name__][ballot_mod.__name__] = 0
            summary_results['IRV']['upMono'] = 0
            summary_results['IRV']['downMono'] = 0
            summary_results['IRV']['noShow'] = 0
            summary_results['plurality_runoff']['upMono'] = 0
            summary_results['plurality_runoff']['noShow'] = 0
            summary_results['bucklin']['noShow'] = 0
            summary_results['smith_plurality']['noShow'] = 0
            summary_results['smith_irv']['noShow'] = 0

            for lxn in massive_results:
                if len(lxn)>4:
                    lxn_method = lxn[0]
                    ballot_mod = lxn[1]
                    summary_results[lxn_method][ballot_mod] += 1
                    combo_name = lxn_method + '_' + ballot_mod
                    search_combos[combo_name][0].append(lxn[2])
                    search_combos[combo_name][1].append(lxn[3])
                    search_combos[combo_name][2].append(lxn[4])
                    search_combos[combo_name][3].append(lxn[5])
                    search_combos[combo_name][4].append(lxn[6])
            
            summary_results.to_csv(destination_base+'/anomalies/'+full_model_name+'/top_line_results.csv')    


            for combo_name in search_combos.keys():
                full_list = search_combos[combo_name]
                ballot_counts = []
                for y in full_list[4]:
                    count = 0
                    for x in y:
                        if x:
                            if type(x[-1])!=str:
                                count += x[-1]
                    ballot_counts.append(count)
                change_list = ballot_counts
                df_dict = {'file_name': full_list[0], 'num_cands': full_list[1], 
                            'old_winner': full_list[2], 'new_winner': full_list[3],
                            'ballot_change_num':change_list, 'modified_ballots': full_list[4]}
                csv_data = pd.DataFrame(df_dict)
                csv_data.to_csv(destination_base+'/anomalies/'+full_model_name+'/'+combo_name+'.csv')
                
                
        













