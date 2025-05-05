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
import traceback
import json
from collections import Counter
import matplotlib.pyplot as plt

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
    base_name = '../../raw_data/preference_profiles/' + election_location
    ## version for HPC
    # base_name = './data/' + election_location

    lxn_count = 0
    for folder_name in os.listdir(base_name):
    ## test folder in scotland
    # for folder_name in ['s-lanarks17-ballots']:
    ## test folder in america
    # for folder_name in ['Portland, ME']:
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



lxns_scot = get_election_data('scotland')
nums_scot = [lxn[2] for lxn in lxns_scot]

lxns_aus = get_election_data('australia')
nums_aus = [lxn[2] for lxn in lxns_aus]

lxns_usa = get_election_data('america')
nums_usa = [lxn[2] for lxn in lxns_usa]

plt.subplots()
plt.hist(nums_scot)
plt.title('Scottish election sizes')

plt.subplots()
plt.hist(nums_aus)
plt.title('Australian election sizes')

plt.subplots()
plt.hist(nums_usa)
plt.title('American election sizes')


for lxn in lxns_usa:
    if lxn[2]>15:
        print(lxn[0])











# ##############################################################
# ##### run searches, no multiprocessing
# ##############################################################

# start_time = time.time()

# print('##### Collecting election data #####')
# lxn_list = get_election_data(election_group)

# print(time.time()-start_time)


# print('##### Searching for anomalies #####')
# print('###################################')
# # vote_methods = [IRV, smith_irv, Borda_PM, Borda_OM, Borda_AVG, minimax, smith_minimax, ranked_pairs, plurality, condorcet_plurality, plurality_runoff, bucklin]
# # vote_methods = [minimax, minimax_fast]
# # vote_methods = [IRV]

# # for method in vote_methods:
    
    
# start_time = time.time()
# # print(method.__name__)

# nums_times = []

# anomaly_data = []
# for i in range(len(lxn_list)):
# # for i in [2]:
    
#     sys.stdout.write('\r')
#     sys.stdout.write('\r')
#     sys.stdout.write(f'Election {i+1}'+':' + lxn_list[i][0] + '                      ')
#     sys.stdout.flush()
    
#     lxn, profile, num_cands = lxn_list[i]
    
#     lxn_start = time.time()
    
#     data = frac_general_search(profile, num_cands, minimax, strat_compromise, 1)
#     # data = frac_noShowCondPlur(profile, num_cands, 1)
#     # data = noShowIRV(profile, num_cands)
    
#     nums_times.append([num_cands, time.time()-lxn_start])
    
#     if data:
#         anomaly_data.append(data)
        
# print(time.time()-start_time)    
# print(len(anomaly_data))
# print('###################################')














