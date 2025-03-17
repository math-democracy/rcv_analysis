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

def anom_search_for_voters(profile, num_cands, voteMethod, mod_ballot_method, diagnostic=False):
    
    exp_vals = []
    
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

    for L in cands:
        for threat in cands:
            if threat != L:
                if diagnostic:
                    print(L)
                    print(threat)
                ## Make a copy of original profile to modify
                new_profile = profile.copy(deep=True)
                modified_ballot_list = []
                
                for k in range(len(new_profile)):
                    ## change the ballot in some way
                    curBal = new_profile.at[k,'ballot']
                    modBal, modified = mod_ballot_method(curBal, threat, L)
                    new_profile.at[k,'ballot'] = modBal
                    if curBal!=modBal:
                        modified_ballot_list.append([curBal, modBal, profile.at[k, 'Count']])
                
                newWinners = voteMethod(new_profile, cands, diagnostic = diagnostic)[0]
                if len(newWinners)!=1:
                    print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
                    continue
                nW = newWinners[0]
                
                if nW != W:
                    total_value_change = 0
                    ## compute change in value for all voters that modified ballots
                    for group in modified_ballot_list:
                        ogBal = group[0]
                        count = group[2]
                        score_change = vv_borda_avg(ogBal, nW, num_cands) - vv_borda_avg(ogBal, W, num_cands)
                        total_value_change += score_change*count
                    exp_vals.append(total_value_change/sum([g[2] for g in modified_ballot_list]))
            
    return exp_vals





###############################################################################
###############################################################################

def voter_bloc_bullet(profile, num_cands, voteMethod, diagnostic=False):
    
    exp_vals = []
    
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

    for L in cands:
        ## Make a copy of original profile to modify
        new_profile = profile.copy(deep=True)
        modified_ballot_list = []
        
        for k in range(len(new_profile)):
            ## change the ballot in some way
            curBal = new_profile.at[k,'ballot']
            if curBal[0]==L:
                modBal = curBal[0]
                new_profile.at[k,'ballot'] = modBal
                if len(curBal)>1:
                    modified_ballot_list.append([curBal, modBal, profile.at[k, 'Count']])
        
        newWinners = voteMethod(new_profile, cands, diagnostic = diagnostic)[0]
        if len(newWinners)!=1:
            print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
            continue
        nW = newWinners[0]
        
        if nW != W:
            total_value_change = 0
            ## compute change in value for all voters that modified ballots
            for group in modified_ballot_list:
                ogBal = group[0]
                modBal = group[1]
                count = group[2]
                score_change = vv_borda_avg(ogBal, nW, num_cands) - vv_borda_avg(ogBal, W, num_cands)
                total_value_change += score_change*count
                # print(W, nW, ogBal, modBal, score_change)
            exp_vals.append(total_value_change/sum([g[2] for g in modified_ballot_list]))
    
    return exp_vals


















