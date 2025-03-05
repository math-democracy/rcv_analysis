###################################################
##### Code to search for anomalies
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

from election_class import *
from search_algorithm_class import *
from ballot_modifications_class import *


#####TODO
## 



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
        # ballot = [cand_names[int(i)-1] for i in this_line_parts[1:-1]]
        ballot = ''.join([cand_names[int(i)-1] for i in this_line_parts[1:-1]])
        ballot_list.append(ballot)
        
    df_dict = {'ballot': ballot_list, 'Count': count_list}
    data = pd.DataFrame(df_dict)
    return data

###############################################################################
###############################################################################

def get_election_data(election_location, specific_lxn=-1, diagnostic=False):
    lxns = []
    base_name = '../../raw_data/preference_profiles/' + election_location

    lxn_count = 0
    # for folder_name in os.listdir(base_name):
    for folder_name in ['aberdeenshire22']:
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

def gen_search_for_anomaly(params):
    file_path, profile, num_cands = params
    
    full_result_list = []
    
    for lxn_method in lxn_methods:
        for ballot_mod in ballot_mod_methods:
            
            search_result = general_search(profile, num_cands, lxn_method, ballot_mod)
            if search_result:
                full_result_list.append([lxn_method.__name__, ballot_mod.__name__, file_path, num_cands] + search_result)
    
    return full_result_list








election_group = 'scotland'
if not os.path.exists(election_group):
    os.makedirs(election_group)

lxn_methods = [IRV, smith_irv, Borda_PM, Borda_OM, Borda_AVG, minimax, 
               smith_minimax, ranked_pairs, plurality, condorcet_plurality,
               plurality_runoff, bucklin]

ballot_mod_methods = [LtoTop, truncBalAtL, truncBalAtW, buryWinBal, boostLinBal]

search_combos = {}
for lxn_method in lxn_methods:
    for ballot_mod in ballot_mod_methods:
        combo_name = lxn_method.__name__ + '_' + ballot_mod.__name__
        ## list is file_names, num_cands old_winner, new_winner, modified_ballots
        search_combos[combo_name] = [[], [], [], [], []]

if __name__ == '__main__':  
    ## get data
    lxn_list = get_election_data(election_group)
    
    ## search for anomalies
    pool = multiprocessing.Pool(processes=5)
    massive_results = pool.map(gen_search_for_anomaly, lxn_list)
    
    ## process and save results
    summary_results = pd.DataFrame(0, index = [ballot_mod.__name__ for ballot_mod in ballot_mod_methods], 
                                   columns = [lxn_method.__name__ for lxn_method in lxn_methods])
    
    for lxn in massive_results:
        for anomaly in lxn:
            lxn_method = anomaly[0]
            ballot_mod = anomaly[1]
            summary_results[lxn_method][ballot_mod] += 1
            combo_name = lxn_method + '_' + ballot_mod
            search_combos[combo_name][0].append(anomaly[2])
            search_combos[combo_name][1].append(anomaly[3])
            search_combos[combo_name][2].append(anomaly[4])
            search_combos[combo_name][3].append(anomaly[5])
            search_combos[combo_name][4].append(anomaly[6])

    summary_results.to_csv(election_group+'/top_line_results.csv')
    

for combo_name in search_combos.keys():
    full_list = search_combos[combo_name]
    df_dict = {'file_name': full_list[0], 'num_cands': full_list[1], 
               'old_winner': full_list[2], 'new_winner': full_list[3],
               'modified_ballots': full_list[4]}
    csv_data = pd.DataFrame(df_dict)
    csv_data.to_csv(election_group+'/'+combo_name+'.csv')










# start_time = time.time()

# print('##### Collecting election data #####')
# lxn_list = get_election_data('scotland')

# print(time.time()-start_time)



# print('##### Searching for anomalies #####')
# vote_methods = [IRV, smith_irv, Borda_PM, Borda_OM, Borda_AVG, minimax, smith_minimax, ranked_pairs, plurality, condorcet_plurality, plurality_runoff, bucklin]

# for method in vote_methods:
#     print(method.__name__)
#     anomaly_data = []
#     for i in range(len(lxn_list)):
        
#         sys.stdout.write('\r')
#         sys.stdout.write(f'Election {i+1}'+'         ')
#         sys.stdout.flush()
        
#         lxn, profile, num_cands = lxn_list[i]
        
#         data = general_search(profile, num_cands, method, LtoTop)
        
#         if data:
#             anomaly_data.append(data)
#     print(len(anomaly_data))














