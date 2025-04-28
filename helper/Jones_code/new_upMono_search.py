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

from itertools import combinations

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
election_group = 'america'
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
    base_name = '../../raw_data/preference_profiles/' + election_location
    ## version for HPC
    # base_name = './data/' + election_location

    lxn_count = 0
    for folder_name in os.listdir(base_name):
    ## test folder in scotland
    # for folder_name in ['dumgal12-ballots']:
    ## test folder in america
    # for folder_name in ['Portland, ME']:
        for file_name in os.listdir(base_name+'/'+folder_name):
            lxn_count += 1
            file_path = base_name+'/'+folder_name+'/'+file_name
            
            # if file_name in american_ban_list:
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





##############################################################
##############################################################
diagnostic = False

start_time = time.time()

print('##### Collecting election data #####')
lxn_list = get_election_data(election_group)

print(time.time()-start_time)


print('##### Searching for anomalies #####')
print('###################################')


anomaly_list = []
    
## the missing anomaly
# lxn, profile, num_cands = lxn_list[12]


# killer_subset_count = 0
for indx, lxn_data in enumerate(lxn_list):    
    lxn, profile, num_cands = lxn_data
    
    # if 'AbbeyWard' not in lxn:
    #     continue
    
    if diagnostic:
        print('###############################################')
        print(lxn)
        print('###############################################')
    
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    killer_subsets = []
    winners, foo1, foo2 =IRV(profile, cands) #get election data from IRV
    if len(winners)>1:
        print('##### Multiple initial winners #####')
        # return []
    winner = winners[0]
        
    ##### search for killer subsets
    losers = cands.copy()
    losers.remove(winner)
    
    ## only eliminate in round of three or two
    cand_subsets = list(combinations(losers, 2))
    for loser in losers:
        cand_subsets.append((loser))
    
    ## try all possible rounds
    # cand_subsets = []
    # for i in range(2, num_cands-1):
    #     cand_subsets+=list(combinations(losers,i))
    
    ## test if each subset could eliminate winner
    for cand_tuple in cand_subsets:
        subset = list(cand_tuple)
        subset.append(winner)
        
        scores = {cand: 0 for cand in subset}
        for k in range(len(profile)):
            ballot = profile.at[k, 'ballot']
            for c in ballot: 
                if c in subset:
                    scores[c]+=profile.at[k, 'Count']
                    break
            
        if scores[winner] == min(scores.values()) and min(scores.values())!=max(scores.values()):
            # print(lxn + ' : ', winner, subset)
            # print(subset)
            # killer_subset_count += 1
            # break
            killer_subsets.append([subset, scores])



    
    
    ##### try to manipulate votes so everyone not in killer subset is removed first
    for ks in killer_subsets:
        subset, scores = ks
        if diagnostic:
            print(f'##### {subset}')
        killers = subset.copy()
        killers.remove(winner)
        win_gap = min([scores[cand]-scores[winner] for cand in killers])-1
        
        new_profile = profile.copy(deep = True)
        for k in range(len(new_profile)):
            ballot = new_profile.at[k, 'ballot']
            ## if winner is not ranked, don't move up
            if winner not in ballot:
                pass
                # killer = ''
                # for cand in reversed(ballot):
                #     if cand in killers:
                #         killer = cand
                #         break
                # if killer:
                #     prekiller, postkiller = ballot.split(killer)
                #     mod_ballot = prekiller + killer + winner+ postkiller
                #     # print(winner, killers, ballot, mod_ballot)
                #     new_profile.at[k, 'ballot'] = mod_ballot
                # else:
                #     mod_ballot = winner + ballot
                #     # print(winner, killers, ballot, mod_ballot)
                #     new_profile.at[k, 'ballot'] = mod_ballot
            
            ## if winner is ranked, move them up until they are right behind someone in the killer subset
            else:
                cands_ahead, cands_behind = ballot.split(winner)
                killer = ''
                winner_indx = 0
                for cand in reversed(cands_ahead):
                    if cand in killers:
                        winner_indx = ballot.index(cand)+1
                        killer = cand
                        break
                if killer:
                    prekiller, postkiller = cands_ahead.split(killer)
                    mod_ballot = prekiller + killer + winner+ postkiller + cands_behind
                    # print(winner, killers, ballot, mod_ballot)
                    new_profile.at[k, 'ballot'] = mod_ballot
                else:
                    mod_ballot = winner + cands_ahead + cands_behind
                    # print(winner, killers, ballot, mod_ballot)
                    new_profile.at[k, 'ballot'] = mod_ballot
    
        ## run new election, see if winner loses
        new_winners, foo1, foo2 = IRV(new_profile, cands)
        if len(new_winners)>1:
            print('##### Multiple new winners #####')
            # return []
        new_win = new_winners[0]
        
        if new_win != winner:
            anomaly_list.append(lxn)
            # print('Anomaly in ' + lxn)
            break
        
        
        # breakhere
        
        ##### try changing bullet votes
        quota=math.floor(sum(new_profile['Count'])/(2))+1
        hopefuls = cands.copy()
        
        vote_counts = {cand: 0 for cand in hopefuls}
        for k in range(len(new_profile)):
            vote_counts[new_profile.at[k, 'ballot'][0]] += new_profile.at[k, 'Count'] 
        
        if max(vote_counts.values())>quota:
            new_win = [cand for cand in hopefuls if vote_counts[cand] == max(vote_counts.values())][0]
            win_found = True
            if new_win != winner:
                anomaly_list.append(lxn)
                # print('Anomaly in ' + lxn)
        else:
            win_found = False
            
        while not win_found:
            if diagnostic:
                print(hopefuls)
                print(vote_counts, win_gap)
            
            if max(vote_counts.values())>quota:
                new_win = [cand for cand in hopefuls if vote_counts[cand] == max(vote_counts.values())][0]
                win_found = True
                if new_win != winner:
                    anomaly_list.append(lxn)
                    # print('Anomaly in ' + lxn)
                break
            
            min_count=min(i for i in vote_counts.values() if i>=0)
            # min_count=min(i for i in vote_counts.values() if i>0)
            count=0
            for votes in vote_counts:
                if votes==min_count:
                    count+=1
            if count>1:
                print("Tie in candidate to remove")
                new_winners = ''
                win_found = True
                break

            elim_cand = list(vote_counts.keys())[list(vote_counts.values()).index(min_count)] #took str() away
            
            ## safe to remove candidate
            if elim_cand not in subset:
                # red_frame = new_profile.copy(deep = True)
                for k in range(len(new_profile)):
                    ballot = new_profile.at[k, 'ballot']
                    if elim_cand in ballot:
                        new_profile.at[k, 'ballot'] = new_profile.at[k, 'ballot'].replace(elim_cand, '')
                        
                for k in range(len(new_profile)):
                    if new_profile.at[k, 'ballot'] == '':
                        new_profile.drop(k)
                
                hopefuls.remove(elim_cand)
                if diagnostic:
                    print('Eliminated ' + elim_cand)
                
                
                        
            ## its over, old winner is eliminated
            elif elim_cand == winner:
                win_found = True
                anomaly_list.append(lxn)
                # print('Anomaly in ' + lxn)
                break
                
            ## need to try changing outcome by changing bullet votes
            elif elim_cand in killers:
                need_lose_score = min([vote_counts[cand] for cand in hopefuls if cand not in subset])
                for need_lose in hopefuls:
                    if vote_counts[need_lose] == need_lose_score:
                        break
                
                if vote_counts[need_lose] - vote_counts[elim_cand] + 1 > win_gap:
                    ## cant change enough votes without ruining killer subset
                    win_found = True
                    break
                else:
                    need_to_change = vote_counts[need_lose] - vote_counts[elim_cand] + 1
                    for k in range(len(new_profile)):
                        if new_profile.at[k, 'ballot'] == need_lose:
                            if new_profile.at[k, 'Count'] <= need_to_change:
                                new_profile.at[k, 'ballot'] = winner + need_lose
                                need_to_change -= new_profile.at[k, 'Count']
                                win_gap -= new_profile.at[k, 'Count']
                            else:
                                new_profile.at[k, 'Count'] -= need_to_change
                                new_profile = pd.concat([new_profile, pd.DataFrame({'ballot': [winner+need_lose], 'Count': [need_to_change]})], ignore_index=True)
                                win_gap -= need_to_change
                                need_to_change = 0
                    
                    if need_to_change > 0:
                        ## not enough ballots to change
                        print('###########################################')
                        print('There were not enough ballots to change')
                        print(lxn)
                        win_found = True
                        break
                if diagnostic:  
                    print('Lowered score for ' + need_lose)
                                
            ##this should not happen
            else:
                print('ERROR!!!!!!!!!!!!!!!!!!')
        
            
            vote_counts={cand:0 for cand in hopefuls}
            for k in range(len(new_profile)):
                if new_profile.at[k,'ballot']!='':
                    if new_profile.at[k,'ballot'][0] in vote_counts.keys():
                        vote_counts[new_profile.at[k,'ballot'][0]]+=new_profile.iloc[k]['Count']
                    else:
                        vote_counts[new_profile.at[k,'ballot'][0]]=new_profile.iloc[k]['Count']
        
        
        
        
        
        # ##### go through round by round to search for bullet votes to change
        # n = num_cands
        
        # new_winners=[]
        # hopefuls=[]
        # eliminatedCand=[]
        # elimFrames={}
        
        
        # #Get each candidate's initial number of votes this round
        # vote_counts={cand:0 for cand in hopefuls}
        # for k in range(len(new_profile)):
        #         if new_profile.at[k,'ballot'][0] in vote_counts.keys():
        #             vote_counts[new_profile.at[k,'ballot'][0]]+=new_profile.iloc[k]['Count']
        #         else:
        #             vote_counts[new_profile.at[k,'ballot'][0]]=new_profile.iloc[k]['Count']

            
        # max_count=max(vote_counts.values())
        # while len(new_winners)<1:
                
        #     max_count=max(vote_counts.values())
            
        #     if max_count>=quota: #somebody is elected 
        #         #There might be multiple people elected this round; save them as a sorted dictionary
        #         votes_for_winners={k:vote_counts[k] for k in vote_counts.keys() if vote_counts[k]>=quota }
        #         votes_for_winners=dict(sorted(votes_for_winners.items(),key=lambda x: x[1], reverse=True))
                
        #         #If we try to elect too many people, error
        #         if len(new_winners)+len(votes_for_winners)>1:
        #             print("Error in tabulation.  Multiple winners found.")
        #             for k in range(len(new_winners)+len(votes_for_winners)-1):
        #                 new_winners.append(list(votes_for_winners.keys())[k])
                
        #         else:
        #             new_winners=new_winners+list(votes_for_winners.keys())
        #             for cand in new_winners:
        #                 if cand in hopefuls:
        #                     hopefuls.remove(cand)
                    
        #             while len(votes_for_winners)>0:
                        
        #                 cand=list(votes_for_winners.keys())[0]
        
        #                 if cand not in new_winners:
        #                     new_winners.append(cand)
        #                     hopefuls.remove(cand)
        #                 # if len(new_winners)==1:
        #                 #     return new_winners, eliminatedCand, elimFrames #, tempWinners (don't need tempWinners?)
                        
        #     #nobody is elected by surpassing quota, but the number
        #     #of candidates left equals S
        #     elif len(hopefuls)+len(new_winners)==1:
        #         new_winners = new_winners+hopefuls
            
        #     #remove weakest cand and transfer their votes with weight one
        #     else:
        #         min_count=min(i for i in vote_counts.values() if i>=0)
        #         # min_count=min(i for i in vote_counts.values() if i>0)
        #         count=0
        #         for votes in vote_counts:
        #             if votes==min_count:
        #                 count+=1
        #         if count>1:
        #             print("tie in candidate to remove")
        #             new_winners = ['']

        #         eliminated_cand = list(vote_counts.keys())[list(vote_counts.values()).index(min_count)] #took str() away
                
        #         if eliminated_cand in killers:
        #             ## try to change bullet votes so someone else is eliminated
        #             pass
                
        #         else:
        #             elimFrames[len(eliminatedCand)]=new_profile.copy(deep=True)
        #             #tempWinners[len(eliminatedCand)]=copy.deepcopy(winners)
        #             #print(new_profile)
        #             eliminatedCand.append(eliminated_cand)
        #             if eliminated_cand in hopefuls:
        #                 hopefuls.remove(eliminated_cand)
                    
        #             for k in range(len(new_profile)):
        #                 if eliminated_cand in new_profile.iloc[k]['ballot']:
        #                     new_profile.at[k,'ballot']=new_profile.at[k,'ballot'].replace(eliminated_cand,'')
        #             for k in range(len(new_profile)):
        #                 if new_profile.at[k,'ballot']=='':
        #                     new_profile.drop(k)
        #             vote_counts={cand:0 for cand in hopefuls}
                   
        #             for k in range(len(new_profile)):
        #                 if new_profile.at[k,'ballot']!='':
        #                     if new_profile.at[k,'ballot'][0] in vote_counts.keys():
        #                         vote_counts[new_profile.at[k,'ballot'][0]]+=new_profile.iloc[k]['Count']
        #                     else:
        #                         vote_counts[new_profile.at[k,'ballot'][0]]=new_profile.iloc[k]['Count']
        #             #print(vote_counts)
        #             max_count=max(vote_counts.values())
        #             if len(hopefuls)+len(new_winners)==1:
        #                 new_winners = new_winners+hopefuls
        #                 new_profile=pd.DataFrame(new_profile.groupby(['ballot'],as_index=False)['Count'].sum())
        
        
        # ## check if 
        # if len(new_winners)>1:
        #     print('##### Multiple new winners #####')
        #     # return []
        # new_win = new_winners[0]
        
        # if new_win != winner:
        #     print('Anomaly in ' + lxn)
        #     break
        
    

