########################################
##### Anomaly search class
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

from election_class import *
from ballot_modifications_class import *

##### TODO
## decide what to do with undetermined elections
## bring in Adam's IRV searches
## perhaps modify bucklin, plurality_runoff methods to return more info


###############################################################################
##### Anomaly search algorithms
##### general_search works with all election methods
##### more targeted searches are for specific election methods
###############################################################################

def general_search(profile, num_cands, voteMethod, mod_ballot_method, diagnostic=False):
    
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
    
    losers = cands.copy()
    losers.remove(W)
    if diagnostic:
        print(losers)

    modified_ballot_list = []
    for L in losers:
        ## Make a copy of original profile to modify
        new_profile = profile.copy(deep=True)
        for k in range(len(new_profile)):
            # if new_profile.at[k,'ballot']!='':
            ## change the ballot in some way
            curBal = new_profile.at[k,'ballot']
            modBal, modified = mod_ballot_method(curBal, W, L)
            new_profile.at[k,'ballot'] = modBal
            if modified:
                modified_ballot_list.append([curBal, modBal, profile.at[k, 'Count']])
                
        newWinners = voteMethod(new_profile, cands)[0]
        if len(newWinners)!=1:
            print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
            continue
        newWinner = newWinners[0]
        
        if L == newWinner:
            return [W, L, modified_ballot_list]
    
    return []

###############################################################################
###############################################################################

def noShowBucklin(profile, num_cands, diagnostic=False):
    # search through the election. If at any stage a loser is beating the winner, 
    # see if ballots that rank loser above winner but are not yet being counted
    # can be thrown out to lower the quota so that loser wins without having to 
    # advance to next round of counts
    
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    winners = bucklin(profile, cands)
    if len(winners)>1:
        # hard to define an anomaly if there is not a single winner
        return []
    winner = winners[0]
    losers = cands.copy()
    losers.remove(winner)
    
    if diagnostic:
        print(winner)
        print(losers)
    
    # Initialize scores for candidates to 0
    scores = {cand: 0.0 for cand in cands}
    threshold = profile['Count'].sum() / 2  # Majority threshold
    
    if diagnostic:
        print(scores)
        print(threshold)
    for round_indx in range(num_cands):
        # update scores for the current round
        for k in range(len(profile)):
            ballot = profile.at[k, 'ballot']
            if len(ballot) > round_indx:
                cand = ballot[round_indx]
                scores[cand] += profile.at[k, 'Count']

        if diagnostic:
            print(scores)
        # check if any candidate has higher score than winner
        for loser in losers:
            if scores[loser] > scores[winner]:
                remove_ballots = []
                remove_ballot_total = 0
                for k in range(len(profile)):
                    ballot = profile.at[k, 'ballot']
                    if ballot.find(loser)>round_indx:
                        if (winner not in ballot) or (ballot.find(winner) > ballot.find(loser)):
                            remove_ballots.append(ballot)
                            remove_ballot_total += profile.at[k, 'Count']
                if threshold - remove_ballot_total/2 < scores[loser]:
                    return [winner, loser]

    return []

###############################################################################
###############################################################################

def upMonoPR(profile, num_cands, diagnostic=False):
    # run original election to get winner and contender
    # see if any upstart candidates defeat winner in h2h
    # check if winner can be moved above contender in enough ballots so that
    # upstart advances to second round instead of contender
    # confirm that upstart defeats winner
    
    
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    # Initialize scores for candidates to 0
    scores = {cand: 0.0 for cand in cands}
    
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        scores[ballot[0]] += profile.at[k, 'Count']
    
    if diagnostic:
        print(scores)
    
    # keep two candidates with highest scores
    second_round_cands = cands.copy()
    second_round_cands.sort(key=lambda cand: scores[cand], reverse = True)
    second_round_cands = second_round_cands[:2]
    
    c1, c2 = second_round_cands
    scores2 = {cand: 0.0 for cand in second_round_cands}
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        if c1 in ballot and c2 in ballot:
            if ballot.find(c1)<ballot.find(c2):
                scores2[c1] += profile.at[k, 'Count']
            else:
                scores2[c2] += profile.at[k, 'Count']
        elif c1 in ballot:
            scores2[c1] += profile.at[k, 'Count']
        elif c2 in ballot:
            scores2[c2] += profile.at[k, 'Count']
    
    # Winner has most first place votes
    max_score = max(scores2.values())
    winners = [cand for cand, score in scores2.items() if score == max_score]
    if len(winners)>1:
        print('##### Multiple winners #####')
        return []
    
    if diagnostic:
        print(scores2)
        print(winners)
        
    ranked_cands = sorted(list(scores.keys()), key = lambda cand: scores[cand], reverse = True)
    if diagnostic:
        print(ranked_cands)
    
    if scores[ranked_cands[2]]==scores[ranked_cands[1]]:
        print('##### multiple contenders #####')
        return []
    
    winner = winners[0]
    
    ## find candidates that could beat winner in H2H
    margins = np.zeros((num_cands, num_cands))
    
    for c1 in range(num_cands):
        for c2 in range(c1+1, num_cands):
            c1_let = cand_names[c1]
            c2_let = cand_names[c2]
            # number of votes c1 gets over c2 in H2H
            margin = 0
            
            for k in range(len(profile)):
                ballot = profile.at[k, 'ballot']
                count = profile.at[k, 'Count']
                ## ballot ranks both c1 and c2
                if c1_let in ballot and c2_let in ballot:
                    if ballot.find(c1_let) < ballot.find(c2_let):
                        margin += count
                    else:
                        margin -= count
                ## ballot only ranks c1       
                elif c1_let in ballot:
                    margin += count
                ## ballot only ranks c2
                elif c2_let in ballot:
                    margin -= count
            
            margins[c1, c2] = margin
            margins[c2, c1] = -1*margin
    
    
    upstarts = [cand_names[c1] for c1 in range(num_cands) if margins[c1, cands.index(winner)]>0]
    if diagnostic:
        print(margins)
        print(cands)
        print(upstarts)
    
    for upstart in upstarts:
        if diagnostic:
            print(upstart)
        ## check if upstart can make it to second round and defeat winner
        upstart_win_margin = margins[cand_names.index(upstart), cand_names.index(winner)]
        
        need_to_lose = ranked_cands[:ranked_cands.index(upstart)]
        need_to_lose.remove(winner)
        gaps = {cand: scores[cand] - scores[upstart] for cand in need_to_lose}
        risky_ballots = {cand: 0 for cand in need_to_lose}
        if diagnostic:
            print(gaps)
        
        new_profile = profile.copy(deep = True)
        for k in range(len(new_profile)):
            ballot = new_profile.at[k, 'ballot']
            cur_lead = ballot[0]
            if cur_lead in need_to_lose:
                if (upstart not in ballot and winner in ballot) or (upstart in ballot and winner in ballot and ballot.find(winner)<ballot.find(upstart)):
                    ## move winner to top
                    new_profile.at[k, 'ballot'] = modifyUp(ballot, winner)                   
                    gaps[cur_lead] -= new_profile.at[k, 'Count']
                if (upstart in ballot and winner in ballot and ballot.find(upstart)<ballot.find(winner)) or (winner not in ballot and upstart not in ballot):
                    risky_ballots[cur_lead] += new_profile.at[k, 'Count']
        
        if max(gaps.values()) < 0:
            ## upstart should advance to second round and beat winner
            ## check election
            new_win = plurality_runoff(new_profile, cands)
            if new_win[0] == upstart:
                return [winner, upstart]
            else:
                print('##### Error with safe ballots #####')
        else:
            ## check if risky ballots can be removed
            upstart_can_advance = True
            for cand in need_to_lose:
                if gaps[cand]>risky_ballots[cand]:
                    upstart_can_advance = False
                    break
            
            ballots_to_change = {}
            for cand in need_to_lose:
                if gaps[cand] >= 0:
                    ballots_to_change[cand] = gaps[cand]
            if sum(ballots_to_change.values()) + len(ballots_to_change) > upstart_win_margin:
                upstart_can_advance = False
            
            if diagnostic:
                print(ballots_to_change)
            if upstart_can_advance:
                ## remove just enough risky ballots
                for k in range(len(profile)):
                    ballot = new_profile.at[k, 'ballot']
                    cur_lead = ballot[0]
                    if cur_lead in ballots_to_change.keys():
                        if (upstart in ballot and winner in ballot and ballot.find(upstart)<ballot.find(winner)) or (winner not in ballot and upstart not in ballot):
                            if ballots_to_change[cur_lead] < 0:
                                ## already removed enough ballots, no need to remove more
                                pass
                            elif ballots_to_change[cur_lead] >= (new_profile.at[k, 'Count']+1):
                                ## change all ballots
                                new_profile.at[k, 'ballot'] = modifyUp(ballot, winner)
                                ballots_to_change[cur_lead] -= new_profile.at[k, 'Count']
                                new_profile.at[k, 'Count'] = 0
                            else:
                                ## only change enough ballots
                                ## add new row to new_profile
                                new_ballot = modifyUp(ballot, winner)
                                new_profile.at[k, 'Count'] -= (ballots_to_change[cur_lead] + 1)
                                row={'Count':[ballots_to_change[cur_lead]], 'ballot':[new_ballot]}
                                df2=pd.DataFrame(row)
                                new_profile = pd.concat([new_profile, df2], ignore_index=True)
                                ballots_to_change[cur_lead] = -1
                            
                ## test election having removed the risky ballots
                new_win = plurality_runoff(new_profile, cands)
                if new_win[0] == upstart:        
                    return [winner, upstart]
                
                else:
                    if diagnostic:
                        print(winner)
                        print(upstart)
                        print(new_win)
                        print(need_to_lose)
                        print(upstart_win_margin)
                        print(gaps)
                        print(ballots_to_change)
                    print('##### Error with risky ballots #####')
            
    return []

###############################################################################
###############################################################################

def noShowPR(profile, num_cands, diagnostic=False):
    ## check if any upstart can beat winner in h2h
    ## see if any contender supporters could no show and let upstart advance
    ## to second round
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:num_cands]
    
    ## Initialize scores for candidates to 0
    scores = {cand: 0.0 for cand in cands}
    
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        scores[ballot[0]] += profile.at[k, 'Count']
        
    if diagnostic:
        print(scores)
    
    ## keep two candidates with highest scores
    second_round_cands = cands.copy()
    second_round_cands.sort(key=lambda cand: scores[cand], reverse = True)
    second_round_cands = second_round_cands[:2]
    
    c1, c2 = second_round_cands
    scores2 = {cand: 0.0 for cand in second_round_cands}
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        if c1 in ballot and c2 in ballot:
            if ballot.find(c1)<ballot.find(c2):
                scores2[c1] += profile.at[k, 'Count']
            else:
                scores2[c2] += profile.at[k, 'Count']
        elif c1 in ballot:
            scores2[c1] += profile.at[k, 'Count']
        elif c2 in ballot:
            scores2[c2] += profile.at[k, 'Count']
    
    # Winner has most first place votes
    max_score = max(scores2.values())
    winners = [cand for cand, score in scores2.items() if score == max_score]
    if len(winners)>1:
        print('##### Multiple winners #####')
        return []
    
    ranked_cands = sorted(list(scores.keys()), key = lambda cand: scores[cand], reverse = True)
    if diagnostic:
        print(winners)
        print(scores2)
        print(ranked_cands)
    
    if scores[ranked_cands[2]]==scores[ranked_cands[1]]:
        print('##### multiple contenders #####')
        return []
    
    winner = winners[0]
    
    ## find candidates that could beat winner in H2H
    margins = np.zeros((num_cands, num_cands))
    
    for c1 in range(num_cands):
        for c2 in range(c1+1, num_cands):
            c1_let = cand_names[c1]
            c2_let = cand_names[c2]
            ## number of votes c1 gets over c2 in H2H
            margin = 0
            
            for k in range(len(profile)):
                ballot = profile.at[k, 'ballot']
                count = profile.at[k, 'Count']
                ## ballot ranks both c1 and c2
                if c1_let in ballot and c2_let in ballot:
                    if ballot.find(c1_let) < ballot.find(c2_let):
                        margin += count
                    else:
                        margin -= count
                ## ballot only ranks c1       
                elif c1_let in ballot:
                    margin += count
                ## ballot only ranks c2
                elif c2_let in ballot:
                    margin -= count
            
            margins[c1, c2] = margin
            margins[c2, c1] = -1*margin
    
    upstarts = [cand_names[c1] for c1 in range(num_cands) if margins[c1, cands.index(winner)]>0]
    if diagnostic:
        print(margins)
        print(cands)
        print(upstarts)
    
    for upstart in upstarts:
        if diagnostic:
            print(upstart)
        ## check if upstart can make it to second round and defeat winner
        need_to_lose = ranked_cands[:ranked_cands.index(upstart)]
        
        new_profile = profile.copy(deep = True)
        for k in range(len(new_profile)):
            ballot = new_profile.at[k, 'ballot']
            cur_lead = ballot[0]
            if cur_lead in need_to_lose:
                if (upstart in ballot and winner not in ballot) or (upstart in ballot and winner in ballot and ballot.find(upstart)<ballot.find(winner)):
                    new_profile.at[k, 'Count'] = 0
        
        new_win = plurality_runoff(new_profile, cands)
        if new_win[0] == upstart:
            return [winner, upstart]
        
    return []


















