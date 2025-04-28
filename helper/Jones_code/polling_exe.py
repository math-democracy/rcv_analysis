###################################################
##### Code to see if anomalies can be reversed
##### by reciprocal behavior
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
import ast
import random as rand
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


#####TODO 
## 


###############################################################################
###############################################################################
##### parameters
election_group = 'america'
frac = 1
mp_pool_size = 6
compromise_n = 4
bullet_n = 2
protect_n = 2
###############################################################################
###############################################################################

american_ban_list = ['Easthampton_11022021_Mayor.csv',
                     'Oakland_11042014_Mayor.csv',
                     'Cambridge_11032009_CityCouncil.csv',
                     'Cambridge_11032015_CityCouncil.csv',
                     'Cambridge_11042003_CityCouncil.csv',
                     'Cambridge_11052013_CityCouncil.csv',
                     'Cambridge_11062001_CityCouncil.csv',
                     'Cambridge_11062007_CityCouncil.csv',
                     'Cambridge_11072017_CityCouncil.csv',
                     'Cambridge_11072017_SchoolCommittee.csv',
                     'Cambridge_11072023_CityCouncil.csv',
                     'Cambridge_11082005_CityCouncil.csv',
                     'Cambridge_11082011_CityCouncil.csv',
                     'Cambridge_11152019_CityCouncil.csv',
                     'Minneapolis_11022021_Mayor.csv',
                     'Minneapolis_11052013_Mayor.csv',
                     'Minneapolis_11072017_Mayor.csv',
                     'NewYorkCity_06222021_DEMCouncilMember26thCouncilDistrict.csv',
                     'PortlandOR_110524_Mayor.csv',
                     'Portland_D1_2024.csv',
                     'Portland_D2_2024.csv',
                     'Portland_D3_2024.csv',
                     'Portland_D4_2024.csv',
                     'SanFrancisco_11022004_BoardofSupervisorsDistrict5.csv',
                     'SanFrancisco_11022010_BoardofSupervisorsDistrict10.csv',
                     'SanFrancisco_11062007_Mayor.csv',
                     'SanFrancisco_11082011_Mayor.csv',
                     'Berkeley_11042014_CityAuditor.csv',
                     'Oakland_11062018_SchoolDirectorDistrict2.csv',
                     'Oakland_11082016_CityAttorney.csv',
                     'SanLeandro_11082016_CountyCouncilDistrict4.csv',
                     'SanLeandro_11082016_CountyCouncilDistrict6.csv',
                     'SanFrancisco_11052024_Treasurer.csv',
                     'SanFrancisco_11062018_PublicDefender.csv',
                     'SanFrancisco_11082022_AssessorRecorder.csv',
                     'SanFrancisco_11082022_BoardofSupervisorsD2.csv']



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
    # for folder_name in ['aberdeenshire22']:
        for file_name in os.listdir(base_name+'/'+folder_name):
            lxn_count += 1
            file_path = base_name+'/'+folder_name+'/'+file_name
            
            if file_name in american_ban_list:
                continue
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
if not os.path.exists(election_group+'_polling'):
    os.makedirs(election_group+'_polling')

# lxn_methods = [IRV, smith_irv, Borda_PM, Borda_OM, Borda_AVG, minimax, 
#                 smith_minimax, ranked_pairs, plurality, condorcet_plurality,
#                 plurality_runoff, bucklin]
lxn_methods = [plurality, plurality_runoff, IRV, smith_irv, smith_plurality, 
               minimax, smith_minimax, ranked_pairs, 
               Borda_PM, Borda_OM, Borda_AVG, bucklin]

voter_strategies = [voters_compromise, voters_bullet, voters_protect, voters_score]


if __name__ == '__main__':  
    ## get data
    lxn_list = get_election_data(election_group)
    
    gen_lxn_list = []
    for lxn in lxn_list:
        for lxn_method in lxn_methods:
            for strategy in voter_strategies:
                gen_lxn_list.append([lxn_method, strategy]+lxn)
    
    
    ## search for general anomalies
    pool = multiprocessing.Pool(processes=mp_pool_size)
    massive_results = pool.map(sort_search, gen_lxn_list)
    
    with open(election_group+"_polling/massive_results_data.json", "w") as f:
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
            
            
    exp_val_table.to_csv(election_group+'_polling/expected_values.csv')
    prob_change_table.to_csv(election_group+'_polling/prob_change_winner.csv')
    
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
                
    new_win_exp_pos_table.to_csv(election_group+'_polling/winner_poll_positions.csv')
    
    
    
    




##############################################################
##### run searches, no multiprocessing
##############################################################



# print('##### Collecting election data #####')
# lxn_list = get_election_data('scotland')

# print('##### Measuring outcomes #####')
# changed_elections = []
# for i in range(len(lxn_list)):
    
#     sys.stdout.write('\r')
#     sys.stdout.write('\r')
#     sys.stdout.write(f'Election {i+1}'+':' + lxn_list[i][0] + '                      ')
#     sys.stdout.flush()
    
#     lxn, profile, num_cands = lxn_list[i]
    
#     data = voters_score(profile, IRV, num_cands)
    
#     if data:
#         changed_elections.append([lxn]+data)
        

