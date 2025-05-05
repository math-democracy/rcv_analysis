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
election_group = 'civs'
frac = 1
mp_pool_size = 6
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
    ## test folder in scotland
    # for folder_name in ['s-lanarks17-ballots']:
    ## test folder in america
    # for folder_name in ['Portland, ME']:
        for file_name in os.listdir(base_name+'/'+folder_name):
            lxn_count += 1
            file_path = base_name+'/'+folder_name+'/'+file_name
            
            if file_name in american_ban_list:
                continue
            
            # if '712acb95' not in file_name:
            #     continue
            
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
if not os.path.exists(election_group+'_anomalies'):
    os.makedirs(election_group+'_anomalies')

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


if __name__ == '__main__':  
    ## get data
    lxn_list = get_election_data(election_group)
    
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
    
    
    ## search for general anomalies
    pool = multiprocessing.Pool(processes=mp_pool_size)
    massive_results = pool.map(sort_search, gen_lxn_list)
    
    with open(election_group+"_anomalies/massive_results_data.json", "w") as f:
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
    
    summary_results.to_csv(election_group+'_anomalies/top_line_results.csv')    


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
        csv_data.to_csv(election_group+'_anomalies/'+combo_name+'.csv')
    
    











##############################################################
##### run searches, no multiprocessing
##############################################################

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
    
#     # data = frac_general_search(profile, num_cands, plurality_runoff, strat_compromise, 1)
#     data = frac_noShowBucklin(profile, num_cands, 1)
#     # data = noShowIRV(profile, num_cands)
#     # data = frac_upMonoIRV(profile, num_cands, 1)
    
#     nums_times.append([num_cands, time.time()-lxn_start])
    
#     if data:
#         anomaly_data.append(data)
        
# print(time.time()-start_time)    
# print(len(anomaly_data))
# print('###################################')















###########################
##### look for elections with top 4-cycles that could have condorcet no shows
###########################

# cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
#               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
#               'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
#               'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

# election_group = 'scotland'
# lxn_list = get_election_data(election_group)
# for lxn in lxn_list:
#     name, profile, num_cands = lxn
#     cands = cand_names[:num_cands]
#     smith_set, new_profile = restrict_to_smith(profile, cands)
#     if len(smith_set)>3:
#         print(name)
        

# for lxn in lxn_list:
#     name, profile, num_cands = lxn
#     cands = cand_names[:num_cands]
#     print(minimax(profile, cands))
#     smith_set, profile = restrict_to_smith(profile, cands)
#     print(len(smith_set))
#     print(smith_set)
#     print(new_profile)    
#     num_cands = len(smith_set)
#     cands = smith_set
#     margins = np.zeros((num_cands, num_cands))
    
#     for c1 in range(num_cands):
#         for c2 in range(c1+1, num_cands):
#             c1_let = cands[c1]
#             c2_let = cands[c2]
#             ## number of votes c1 gets over c2 in H2H
#             margin = 0
            
#             for k in range(len(profile)):
#                 ballot = profile.at[k, 'ballot']
#                 count = profile.at[k, 'Count']
#                 ## ballot ranks both c1 and c2
#                 if c1_let in ballot and c2_let in ballot:
#                     if ballot.find(c1_let) < ballot.find(c2_let):
#                         margin += count
#                     else:
#                         margin -= count
#                 ## ballot only ranks c1       
#                 elif c1_let in ballot:
#                     margin += count
#                 ## ballot only ranks c2
#                 elif c2_let in ballot:
#                     margin -= count
            
#             margins[c1, c2] = margin
#             margins[c2, c1] = -1*margin
#     print(margins)



