###################################################
##### Code to measure strategic voting payoffs
###################################################

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
import matplotlib.pyplot as plt
import traceback
import json

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
election_group = 'scotland'
vote_frac = 1
mp_pool_size = 6
###############################################################################
###############################################################################






####################################################
##### Functions to run searches
####################################################

def createBallotDF(list_profile, diagnostic=False):
    cand_names=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    ballot_list = []
    count_list = []
    for k in range(1,len(list_profile)):
        if list_profile[k][0]=='0':
            break
        if diagnostic:
            print(k)
        
        this_line = list_profile[k]
        this_line_parts = this_line.split(' ')
        count_list.append(int(this_line_parts[0]))
        ballot = ''.join([cand_names[int(i)-1] for i in this_line_parts[1:-1]])
        ballot_list.append(ballot)
        
    df_dict = {'ballot': ballot_list, 'Count': count_list}
    data = pd.DataFrame(df_dict)
    return data

###############################################################################
###############################################################################

def get_election_data(election_location, specific_lxn=-1, diagnostic=False):
    lxns = []
    ## version for github repo
    # base_name = '../../raw_data/preference_profiles/' + election_location
    ## version for HPC
    base_name = './data/' + election_location

    lxn_count = 0
    for folder_name in os.listdir(base_name):
    # for folder_name in ['clackmannanshire12-ballots']:
        for file_name in os.listdir(base_name+'/'+folder_name):
            lxn_count += 1
            file_path = base_name+'/'+folder_name+'/'+file_name
            
            # print(file_path)
            
            if specific_lxn > 0:
                if lxn_count!=specific_lxn:
                    continue
            
            if diagnostic:
                print(lxn_count, file_path)
        
            # sys.stdout.write('\r')
            # sys.stdout.write(f'Election {lxn_count}'+'         ')
            # sys.stdout.flush()
            
            File=open(file_path,'r', encoding='utf-8')
            lines=File.readlines()
    
            first_space=lines[0].find(' ')
            num_cands=int(lines[0][0:first_space])
            if num_cands>52:
                print("Cannot handle this many candidates in election " + str(file_path) + ".  Has " + 
                      str(num_cands) + " candidates.")
                continue
                
            data = createBallotDF(lines)
            
            lxns.append([file_path, data, num_cands])

    return lxns

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
###############################################################################


if not os.path.exists(election_group+'_stratvoting'):
    os.makedirs(election_group+'_stratvoting')

# lxn_methods = [IRV, smith_irv, Borda_PM, Borda_OM, Borda_AVG, minimax, 
#                 smith_minimax, ranked_pairs, plurality, condorcet_plurality,
#                 plurality_runoff, bucklin]
lxn_methods = [plurality, plurality_runoff, IRV, smith_irv, smith_plurality, 
               minimax, smith_minimax, ranked_pairs, 
               Borda_PM, Borda_OM, Borda_AVG, bucklin]

# ballot_mod_methods = [LtoTop, truncBalAtL, truncBalAtW, buryWinBal, boostLinBal, deepBuryW]
# ballot_mod_methods = [LtoTop, truncBalAtL, truncBalAtW, buryWinBal, deepBuryW]
ballot_mod_methods = [strat_compromise, strat_truncate_L, strat_truncate_W, strat_bury_shallow, strat_bury_deep]


if __name__ == '__main__':  
    ## get data
    lxn_list = get_election_data(election_group)
    # lxn_list = [lxn_list_full[0]]
    
    gen_lxn_list = []
    for lxn in lxn_list:
        for lxn_method in lxn_methods:
            for ballot_mod in ballot_mod_methods:
                gen_lxn_list.append([lxn_method, ballot_mod]+lxn)
    
    ## search for general anomalies
    pool = multiprocessing.Pool(processes=mp_pool_size)
    massive_results = pool.map(anom_search_strats_shell, gen_lxn_list)
    
    with open(election_group+"_stratvoting/massive_results_data.json", "w") as f:
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
    
    

    exp_val_table.to_csv(election_group+'_stratvoting/expected_values.csv')
    prob_change_table.to_csv(election_group+'_stratvoting/prob_change_winner.csv')
    



















###############################################################################

# start_time = time.time()

# print('##### Collecting election data #####')
# lxn_list = get_election_data('scotland')

# print(time.time()-start_time)




# print('##### Measuring strategic voting outcomes #####')
# print('###################################')
# full_exp_vals = []
# full_change_probs

# for i in range(len(lxn_list)):
    
#     sys.stdout.write('\r')
#     sys.stdout.write('\r')
#     sys.stdout.write(f'Election {i+1}'+':' + lxn_list[i][0] + '                      ')
#     sys.stdout.flush()
    
#     lxn, profile, num_cands = lxn_list[i]
    
#     data, change_prob = anom_search_for_voters(profile, num_cands, plurality, LtoTop)
    
#     full_exp_vals.append(data)
#     full_change_probs.append(change_prob)
        
# print(time.time()-start_time)  
# print('###################################')


# flat_exp_vals = []
# for x in full_exp_vals:
#     flat_exp_vals+=x
    
# plt.hist(flat_exp_vals)