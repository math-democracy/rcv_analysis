
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
compromise_n = 2
bullet_n = 1
protect_n = 1
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
##### Voter value functions
###############################################################################

def vv_borda_avg(ballot, cand, num_cands):
    max_score = num_cands - 1
    if cand in ballot:
        return max_score - ballot.index(cand)
    else:
        missing_num = num_cands-len(ballot)
        return (missing_num-1)/2


###############################################################################
##### Functions to modify profiles
###############################################################################

def voters_compromise(profile, voteMethod, num_cands, n, vote_frac=1, bury_deep=True, poll_noise=0, diagnostic=False):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    winners = voteMethod(profile, cands, diagnostic=diagnostic)[0]
    if len(winners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return []
    W=winners[0]
    if diagnostic:
        print(W)
        
    scores = {cand: 0.0 for cand in cands}
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        scores[ballot[0]] += profile.at[k, 'Count']
    if poll_noise>0:
        for cand in cands:
            scores[cand] += rand.uniform(-poll_noise, poll_noise)
    poll_result = cands.copy()
    poll_result.sort(key = lambda x: scores[x], reverse=True)
    if diagnostic:
        print(scores)
        print(poll_result)
        
    new_profile = profile.copy(deep = True)
    modified_ballot_list = []
    
    for k in range(len(new_profile)):
        ## change the ballot in some way
        curBal = new_profile.at[k,'ballot']
        count = int(new_profile.at[k, 'Count']*vote_frac)
        modBal = compromise_top_n(curBal, poll_result, n, bury_deep=bury_deep)
        if curBal!=modBal:
            modified_ballot_list.append([curBal, modBal, count])
            new_profile.at[k, 'Count'] -= count
            new_profile = pd.concat([new_profile, pd.DataFrame({'ballot': [modBal], 'Count': [count]})], ignore_index=True)
    
    newWinners = voteMethod(new_profile, cands, diagnostic = diagnostic)[0]
    if len(newWinners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return []
    nW = newWinners[0]
    
    if nW != W:
        total_value_change = 0
        total_change_count = 0
        for l in modified_ballot_list:
            curBal, modBal, count = l
            total_value_change += (vv_borda_avg(curBal, nW, num_cands) - vv_borda_avg(curBal, W, num_cands))*count
            total_change_count += count
        return [W, nW, total_value_change/total_change_count, poll_result.index(nW)]
    else:
        return []
        
###############################################################################
###############################################################################

def voters_bullet(profile, voteMethod, num_cands, n, vote_frac=1, poll_noise=0, diagnostic=False):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    winners = voteMethod(profile, cands, diagnostic=diagnostic)[0]
    if len(winners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return []
    W=winners[0]
    if diagnostic:
        print(W)
        
    scores = {cand: 0.0 for cand in cands}
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        scores[ballot[0]] += profile.at[k, 'Count']
    if poll_noise>0:
        for cand in cands:
            scores[cand] += rand.uniform(-poll_noise, poll_noise)
    poll_result = cands.copy()
    poll_result.sort(key = lambda x: scores[x], reverse=True)
    if diagnostic:
        print(scores)
        print(poll_result)
        
    new_profile = profile.copy(deep = True)
    modified_ballot_list = []
    
    for k in range(len(new_profile)):
        ## change the ballot in some way
        curBal = new_profile.at[k,'ballot']
        count = int(new_profile.at[k, 'Count']*vote_frac)
        modBal = bullet_top_n(curBal, poll_result, n)
        if curBal!=modBal:
            modified_ballot_list.append([curBal, modBal, count])
            new_profile.at[k, 'Count'] -= count
            new_profile = pd.concat([new_profile, pd.DataFrame({'ballot': [modBal], 'Count': [count]})], ignore_index=True)
    
    newWinners = voteMethod(new_profile, cands, diagnostic = diagnostic)[0]
    if len(newWinners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return []
    nW = newWinners[0]
    
    if nW != W:
        total_value_change = 0
        total_change_count = 0
        for l in modified_ballot_list:
            curBal, modBal, count = l
            total_value_change += (vv_borda_avg(curBal, nW, num_cands) - vv_borda_avg(curBal, W, num_cands))*count
            total_change_count += count
        return [W, nW, total_value_change/total_change_count, poll_result.index(nW)]
    else:
        return []

###############################################################################
###############################################################################

def voters_protect(profile, voteMethod, num_cands, n, vote_frac=1, bury_deep=True, poll_noise=0, diagnostic=False):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    winners = voteMethod(profile, cands, diagnostic=diagnostic)[0]
    if len(winners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return []
    W=winners[0]
    if diagnostic:
        print(W)
        
    scores = {cand: 0.0 for cand in cands}
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        scores[ballot[0]] += profile.at[k, 'Count']
    if poll_noise>0:
        for cand in cands:
            scores[cand] += rand.uniform(-poll_noise, poll_noise)
    poll_result = cands.copy()
    poll_result.sort(key = lambda x: scores[x], reverse=True)
    if diagnostic:
        print(scores)
        print(poll_result)
        
    new_profile = profile.copy(deep = True)
    modified_ballot_list = []
    
    for k in range(len(new_profile)):
        ## change the ballot in some way
        curBal = new_profile.at[k,'ballot']
        count = int(new_profile.at[k, 'Count']*vote_frac)
        modBal = protect_top_n(curBal, poll_result, n, bury_deep=bury_deep)
        if curBal!=modBal:
            modified_ballot_list.append([curBal, modBal, count])
            new_profile.at[k, 'Count'] -= count
            new_profile = pd.concat([new_profile, pd.DataFrame({'ballot': [modBal], 'Count': [count]})], ignore_index=True)
    
    newWinners = voteMethod(new_profile, cands, diagnostic = diagnostic)[0]
    if len(newWinners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return []
    nW = newWinners[0]
    
    if nW != W:
        total_value_change = 0
        total_change_count = 0
        for l in modified_ballot_list:
            curBal, modBal, count = l
            total_value_change += (vv_borda_avg(curBal, nW, num_cands) - vv_borda_avg(curBal, W, num_cands))*count
            total_change_count += count
        return [W, nW, total_value_change/total_change_count, poll_result.index(nW)]
    else:
        return []

###############################################################################
###############################################################################

def voters_score(profile, voteMethod, num_cands, poll_weight=1, vote_frac=1, bury_deep=True, poll_noise=0, diagnostic=False):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    winners = voteMethod(profile, cands, diagnostic=diagnostic)[0]
    if len(winners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return []
    W=winners[0]
    if diagnostic:
        print(W)
        
    scores = {cand: 0.0 for cand in cands}
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        scores[ballot[0]] += profile.at[k, 'Count']
    if poll_noise>0:
        for cand in cands:
            scores[cand] += rand.uniform(-poll_noise, poll_noise)
    poll_result = cands.copy()
    poll_result.sort(key = lambda x: scores[x], reverse=True)
    if diagnostic:
        print(scores)
        print(poll_result)
        
    new_profile = profile.copy(deep = True)
    modified_ballot_list = []
    
    for k in range(len(new_profile)):
        ## change the ballot in some way
        curBal = new_profile.at[k,'ballot']
        count = int(new_profile.at[k, 'Count']*vote_frac)
        modBal = score_cands(curBal, poll_result, poll_weight=poll_weight)
        if curBal!=modBal:
            modified_ballot_list.append([curBal, modBal, count])
            new_profile.at[k, 'Count'] -= count
            new_profile = pd.concat([new_profile, pd.DataFrame({'ballot': [modBal], 'Count': [count]})], ignore_index=True)
    
    newWinners = voteMethod(new_profile, cands, diagnostic = diagnostic)[0]
    if len(newWinners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return []
    nW = newWinners[0]
    
    if nW != W:
        total_value_change = 0
        total_change_count = 0
        for l in modified_ballot_list:
            curBal, modBal, count = l
            total_value_change += (vv_borda_avg(curBal, nW, num_cands) - vv_borda_avg(curBal, W, num_cands))*count
            total_change_count += count
        return [W, nW, total_value_change/total_change_count, poll_result.index(nW)]
    else:
        return []

###############################################################################
###############################################################################

def sort_search(params):
    lxn_method, strategy, file_path, profile, num_cands = params
    
    try:
        if strategy == voters_compromise:
            return [lxn_method.__name__, strategy.__name__, file_path, num_cands] + voters_compromise(profile, lxn_method, num_cands, compromise_n)
        elif strategy == voters_bullet:
            return [lxn_method.__name__, strategy.__name__, file_path, num_cands] + voters_bullet(profile, lxn_method, num_cands, bullet_n)
        elif strategy == voters_protect:
            return [lxn_method.__name__, strategy.__name__, file_path, num_cands] + voters_protect(profile, lxn_method, num_cands, protect_n)
        elif strategy == voters_score:
            return [lxn_method.__name__, strategy.__name__, file_path, num_cands] + voters_score(profile, lxn_method, num_cands)
        else:
            print('###############################')
            print('##### ERROR: STRATEGY BAD #####')
            print(strategy.__name__)
            print('###############################')
            return [strategy.__name__] 
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
            
            if not os.path.exists(destination_base+'/polling/'+full_model_name):
                os.makedirs(destination_base+'/polling/'+full_model_name)
                
            
            
            lxn_list = get_cces(data_path+'/'+cces_file, model)
            
            
            ##### testing singlethreaded
            # for lxn in lxn_list:
            #     print(lxn[0])
            #     data = frac_upMonoPR(lxn[1], 3, 1)
    
            
            ##### prepare to search for anomalies
            lxn_methods = [plurality, plurality_runoff, IRV, smith_irv, smith_plurality, 
                           minimax, smith_minimax, ranked_pairs, 
                           Borda_PM, Borda_OM, Borda_AVG, bucklin]
    
            voter_strategies = [voters_compromise, voters_bullet, voters_protect, voters_score]
            
            gen_lxn_list = []
            for lxn in lxn_list:
                for lxn_method in lxn_methods:
                    for strategy in voter_strategies:
                        gen_lxn_list.append([lxn_method, strategy]+lxn)
                
            pool = multiprocessing.Pool(processes=mp_pool_size)
            massive_results = pool.map(sort_search, gen_lxn_list)
        
            with open(destination_base+'/polling/'+full_model_name+'/massive_results_data.json', "w") as f:
                json.dump(massive_results, f, cls=NpEncoder)
            
            prob_change_table = pd.DataFrame(0, index = [strategy.__name__ for strategy in voter_strategies], 
                                    columns = [lxn_method.__name__ for lxn_method in lxn_methods])
            exp_val_table = pd.DataFrame(0, index = [strategy.__name__ for strategy in voter_strategies], 
                                            columns = [lxn_method.__name__ for lxn_method in lxn_methods])
            new_win_pos_dict = {}
            
            for lxn in massive_results:
                lxn_method = lxn[0]
                strategy = lxn[1]
                combo = lxn_method+'_'+strategy
                if combo not in new_win_pos_dict.keys():
                    new_win_pos_dict[combo] = []
                if len(lxn)>4:
                    prob_change_table.at[strategy, lxn_method] += 1/len(lxn_list)
                    exp_val_table.at[strategy, lxn_method] += np.mean(lxn[6])/len(lxn_list)
                    new_win_pos_dict[combo].append(lxn[7])
                    
                    
            exp_val_table.to_csv(destination_base+'/polling/'+full_model_name+'/expected_values.csv')
            prob_change_table.to_csv(destination_base+'/polling/'+full_model_name+'/prob_change_winner.csv')
            
            new_win_exp_pos_table = pd.DataFrame(0, index = [strategy.__name__ for strategy in voter_strategies], 
                                            columns = [lxn_method.__name__ for lxn_method in lxn_methods])
        
            exp_val_table = pd.DataFrame(0, index = [strategy.__name__ for strategy in voter_strategies], 
                                            columns = [lxn_method.__name__ for lxn_method in lxn_methods])
            for lxn_method in [x.__name__ for x in lxn_methods]:
                for strategy in [y.__name__ for y in voter_strategies]:
                    if new_win_pos_dict[lxn_method+'_'+strategy]:
                        new_win_exp_pos_table.at[strategy, lxn_method] = np.mean(new_win_pos_dict[lxn_method+'_'+strategy])
                    else:
                        new_win_exp_pos_table.at[strategy, lxn_method] = -1
                        
            new_win_exp_pos_table.to_csv(destination_base+'/polling/'+full_model_name+'/winner_poll_positions.csv')
                
        
        











