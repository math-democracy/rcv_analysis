
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
import ast

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

def winner_strikes_back(profile, winner1, winner2, num_cands, voteMethod, mod_ballot_method, vote_frac, diagnostic=False):
    
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    # winners = voteMethod(profile, cands, diagnostic=diagnostic)[0]
    # if len(winners)!=1:
    #     print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
    #     return []
    # W=winners[0]
    # if diagnostic:
    #     print(W)
    
    # losers = cands.copy()
    # losers.remove(W)
    # if diagnostic:
    #     print(losers)

    if mod_ballot_method.__name__ == 'strat_bury_deep':
        scores = {cand: 0.0 for cand in cands}
        
        for k in range(len(profile)):
            ballot = profile.at[k, 'ballot']
            scores[ballot[0]] += profile.at[k, 'Count']
        
        cands_ranked = cands.copy()
        cands_ranked.sort(key = lambda x: scores[x])
    else:
        cands_ranked = []
    
    modified_ballot_list = []
    # for L in losers:
    #     if diagnostic:
    #         print(L)
            
            
            
            
            
    ## Make a copy of original profile to modify
    new_profile = profile.copy(deep=True)
    
    for k in range(len(profile)):
        # if new_profile.at[k,'ballot']!='':
        ## change the ballot in some way
        curBal = new_profile.at[k,'ballot']
        count = int(new_profile.at[k, 'Count']*vote_frac)
        modBal, modified = mod_ballot_method(curBal, winner2, winner1, cands_ranked)
        # new_profile.at[k,'ballot'] = modBal
        # if modified:
        if curBal!=modBal:
            modified_ballot_list.append([curBal, modBal, count])
            new_profile.at[k, 'Count'] -= count
            new_profile = pd.concat([new_profile, pd.DataFrame({'ballot': [modBal], 'Count': [count]})], ignore_index=True)
        
    newWinners = voteMethod(new_profile, cands, diagnostic = diagnostic)[0]
    if len(newWinners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return []
    newWinner = newWinners[0]
    
    if winner1 == newWinner:
        return [newWinner]
    
    return []




def check_anomaly(params):
    lxn_method, ballot_mod, lxn_number, profile, winner1, winner2, cands, modified_ballots = params
    
    # ## use with github repo test
    # # file_path = file_name.replace('./data', '../../raw_data/preference_profiles')
    # ## use with HPC
    # file_path = file_name
    
    # profile = get_profile(file_path)
    
    
    # profile = lxn_list[lxn_number][1]
    mod_profile = profile.copy(deep = True)
    ## modify the ballots in modified ballots
    for change in modified_ballots:
        oldBal, modBal, count = change
        mod_prof_indx = mod_profile.index[mod_profile['ballot']==oldBal].tolist()[0]
        mod_profile.at[mod_prof_indx, 'Count'] -= count
        mod_profile = pd.concat([mod_profile, pd.DataFrame({'ballot': [modBal], 'Count': [count]})], ignore_index=True)
    
    ## confirm the correct winners
    if [winner1] != lxn_method(profile, cands, diagnostic = False)[0]:
        print('##### ERROR: INCORRECT WINNER1 #####')
    # else:
    #     print('Old winner1 good')
    if [winner2] != lxn_method(mod_profile, cands, diagnostic = False)[0]:
        print('##### ERROR: INCORRECT WINNER2 #####')
        breakhere
    # else:
    #     print('Old winner2 good')
    
    strike_back_data = winner_strikes_back(mod_profile, winner1, winner2, len(cands), lxn_method, ballot_mod, 1)
    if strike_back_data:
        return [lxn_method, ballot_mod, lxn_number]
    else:
        return []
    #     # print('The winner strikes back!')
    #     strike_back_count += 1
    # # else:
    # #     print('No strike back')
    # anomaly_count += 1


def multiprocess_shell(params):
    try:
        return check_anomaly(params)
    except:
        print('###############################################')
        print('###############################################')
        print('Error in election:', params[2])
        print('Election method:', params[0])
        print('Anomaly type:', params[1])
        print(traceback.format_exc())
        print('###############################################')
        print('###############################################')
        return []




###############################################################################
###############################################################################
##### Run this code
###############################################################################
###############################################################################
strike_back_count = 0
anomaly_count = 0

cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
              'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
              'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
              'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

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
            
            if not os.path.exists(destination_base+'/retaliation/'+full_model_name):
                os.makedirs(destination_base+'/retaliation/'+full_model_name)
                
            
            
            lxn_list = get_cces(data_path+'/'+cces_file, model)
            
            
            ##### testing singlethreaded
            # for lxn in lxn_list:
            #     print(lxn[0])
            #     data = frac_upMonoPR(lxn[1], 3, 1)
    
            
            ##### prepare to search
            lxn_methods = [plurality, plurality_runoff, IRV, smith_irv, smith_plurality, 
                           minimax, smith_minimax, ranked_pairs, 
                           Borda_PM, Borda_OM, Borda_AVG, bucklin]
    
            ballot_mod_methods = [strat_compromise, strat_truncate_L, strat_truncate_W, strat_bury_shallow, strat_bury_deep]
            
            full_anomaly_data = []
            anomaly_counts = pd.DataFrame(0, index = [ballot_mod.__name__ for ballot_mod in ballot_mod_methods], 
                                            columns = [lxn_method.__name__ for lxn_method in lxn_methods])
            strike_back_fracs = pd.DataFrame(0, index = [ballot_mod.__name__ for ballot_mod in ballot_mod_methods], 
                                            columns = [lxn_method.__name__ for lxn_method in lxn_methods])
                
            for lxn_method in lxn_methods:
                for ballot_mod in ballot_mod_methods:
                    csv_name = lxn_method.__name__ + '_' + ballot_mod.__name__ + '.csv'
                    anomaly_data = pd.read_csv(destination_base + '/anomalies/' + full_model_name + '/' + csv_name)
                    anomaly_counts.at[ballot_mod.__name__, lxn_method.__name__] += len(anomaly_data)
                    
                    for k in range(len(anomaly_data)):
                        lxn_number = anomaly_data.at[k, 'file_name']
                        winner1 = anomaly_data.at[k, 'old_winner']
                        winner2 = anomaly_data.at[k, 'new_winner']
                        cands = cand_names[:anomaly_data.at[k, 'num_cands']]
                        modified_ballots = ast.literal_eval(anomaly_data.at[k, 'modified_ballots'])
                        
                        full_anomaly_data.append([lxn_method, ballot_mod, lxn_number, lxn_list[lxn_number][1], winner1, winner2, cands, modified_ballots])
            
              
            pool = multiprocessing.Pool(processes=mp_pool_size)
            massive_results = pool.map(multiprocess_shell, full_anomaly_data)
                    
            lxn_method_list = []
            ballot_mod_list = []
            file_name_list = []
            for result in massive_results:
                anomaly_count += 1
                if result:
                    strike_back_count += 1
                    strike_back_fracs.at[result[1].__name__, result[0].__name__] += 1/anomaly_counts.at[result[1].__name__, result[0].__name__]
                    lxn_method_list.append(result[0].__name__)
                    ballot_mod_list.append(result[1].__name__)
                    file_name_list.append(result[2])
                    
            for lxn_method in lxn_methods:
                for ballot_mod in ballot_mod_methods:
                    if anomaly_counts.at[ballot_mod.__name__, lxn_method.__name__]==0:
                        strike_back_fracs.at[ballot_mod.__name__, lxn_method.__name__] = -1        
            strike_back_fracs.to_csv(destination_base+'/retaliation/'+full_model_name+'/strike_back_fracs.csv')
            
            df_dict = {'file_name': file_name_list, 'election_method': lxn_method_list, 'anomaly_type': ballot_mod_list}
            strike_back_data = pd.DataFrame(df_dict)
            strike_back_data.to_csv(destination_base+'/retaliation/'+full_model_name + '/strike_back_data.csv')            
            
            
            
            
            
           












