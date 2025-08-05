########################################
##### Strategic voting value class
########################################

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
import time

from election_class import *
from ballot_modifications_class import *


##### TODO
## 



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
##### Test strategic voting strategies
##### measures value for the voters
###############################################################################

def anom_search_strats(profile, num_cands, voteMethod, mod_ballot_method, vote_frac, diagnostic=False):
    
    exp_vals = []
    change_counts = 0
    
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    winners = voteMethod(profile, cands, diagnostic=diagnostic)[0]
    if len(winners)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        return [[], 0]
    W=winners[0]
    if diagnostic:
        print(W)
    
    if mod_ballot_method.__name__ == 'strat_bury_deep':
        scores = {cand: 0.0 for cand in cands}
        
        for k in range(len(profile)):
            ballot = profile.at[k, 'ballot']
            scores[ballot[0]] += profile.at[k, 'Count']
        
        cands_ranked = cands.copy()
        cands_ranked.sort(key = lambda x: scores[x])
    else:
        cands_ranked = []

    for L in cands:
        for threat in cands:
            if threat != L:
    # for i in range(num_cands):
    #     L = cands[i]
    #     for j in range(i+1, num_cands):
    #         threat = cands[j]
                if diagnostic:
                    print(L)
                    print(threat)
                ## Make a copy of original profile to modify
                new_profile = profile.copy(deep=True)
                modified_ballot_list = []
                
                for k in range(len(new_profile)):
                    ## change the ballot in some way
                    curBal = new_profile.at[k,'ballot']
                    count = int(new_profile.at[k, 'Count']*vote_frac)
                    modBal, modified = mod_ballot_method(curBal, W, L, cands_ranked)
                    # new_profile.at[k,'ballot'] = modBal
                    # if modified:
                    if curBal!=modBal:
                        modified_ballot_list.append([curBal, modBal, count])
                        new_profile.at[k, 'Count'] -= count
                        new_profile = pd.concat([new_profile, pd.DataFrame({'ballot': [modBal], 'Count': [count]})], ignore_index=True)
                
                newWinners = voteMethod(new_profile, cands, diagnostic = diagnostic)[0]
                if len(newWinners)!=1:
                    print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
                    continue
                nW = newWinners[0]
                
                if nW != W:
                    change_counts += 1
                    total_value_change = 0
                    ## compute change in value for all voters that modified ballots
                    for group in modified_ballot_list:
                        ogBal = group[0]
                        count = group[2]
                        score_change = vv_borda_avg(ogBal, nW, num_cands) - vv_borda_avg(ogBal, W, num_cands)
                        total_value_change += score_change*count
                    exp_vals.append(total_value_change/sum([g[2] for g in modified_ballot_list]))
            
    return [exp_vals, change_counts/(num_cands*(num_cands-1))]





















