########################################
##### Ballot Modifications
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


###### TODO
## Finish checking over Adam's methods
## Fix True/False flag for modifying ballots

###############################################################################
##### Ballot modifications
###############################################################################


## LNH type 4 (W hurting self with lower rankings)
def laterNoHarm(ballot, winner, loser, cands_ranked):    
    """inputs ballot, winner, and loser"""
    """if winner is ranked and loser is ranked below winner or not ranked,"""
    """move loser up until it is right behind winner"""
    if winner in ballot:
        if (loser not in ballot):
            return ballot.split(winner)[0]+winner+loser+ballot.split(winner)[1], True
        elif ballot.find(winner)<ballot.find(loser): 
            front, back = ballot.split(winner)
            back_front, back_back = back.split(loser)
            return front+winner+loser+back_front+back_back, True
        else:
            return ballot, False
    else:
        return ballot, False
    
    
    
## LNH type 1 (Truncate at L)
def strat_truncate_L(ballot, winner, loser, cands_ranked):
    """inputs ballot and a loser, and truncates the ballot after the loser"""
    if loser in ballot:
        return ballot[:ballot.index(loser)+1], True
    else:
        return ballot, False

## LNH type 2 (Truncate at W)
def strat_truncate_W(ballot, winner, loser, cands_ranked):
    """inputs ballot, winner, and loser"""
    """if loser is ranked above winner, truncates the ballot after the winner"""
    # if winner in ballot:
    if (loser in ballot) and (winner in ballot) and (ballot.find(loser)<ballot.find(winner)):
        return ballot.split(winner, 1)[0], True
    else:
        return ballot, False

## LNH type 3/Burying (Bury W)    
def strat_bury_shallow(ballot, winner, loser, cands_ranked):
    """inputs ballot, winner, and loser"""
    """if loser is ranked above winner, remove winner from ballot"""
    if (loser in ballot) and (winner in ballot) and (ballot.find(loser)<ballot.find(winner)):
        return ballot.split(winner)[0]+ballot.split(winner)[1], True
    else:
        return ballot, False
    
## LNH type 5 (fill up ballot to maximally bury W)
def strat_bury_deep(ballot, winner, loser, cands_ranked):
    """inputs ballot, winner, and loser"""
    """if loser is ranked above winner, fill up ballot with other candidates"""
    """place winner at the bottom"""
    if (loser in ballot) and (winner in ballot) and (ballot.find(loser)<ballot.find(winner)):
        newBallot = ballot.split(winner)[0]+ballot.split(winner)[1]
        for cand in cands_ranked:
            if cand not in newBallot and cand != winner:
                newBallot += cand
        newBallot += winner
        return newBallot, True
    elif loser in ballot and winner not in ballot:
        newBallot = ballot
        for cand in cands_ranked:
            if cand not in newBallot and cand != winner:
                newBallot += cand
        newBallot += winner
        return newBallot, True
    else:
        return ballot, False
    
    
## compromise anomaly (move L to top if L ranked above W)
def strat_compromise(ballot, winner, loser, cands_ranked):
    """inputs ballot, winner, and loser"""
    """if loser ranked above winner, move loser to top of ballot"""
    if (loser in ballot and winner in ballot and ballot.find(loser)<ballot.find(winner)) or (loser in ballot and winner not in ballot):
        front, back = ballot.split(loser)
        return loser+front+back, True
    else:
        return ballot, False
    
## used in monotonicity search
def modifyUp(ballot, winner):
    """inputs a candidate and a ballot"""
    """moves candidate to top of ballot if candidate is in ballot."""
    """Otherwise adds candidate to top of ballot"""
    if winner in ballot:
        return winner + ballot.replace(winner, "")
    else:
        return winner + ballot








#################
#################
# these ones from Adam, not checked yet
# used in the customized IRV searches



def get_secondLow(my_dict):
    """inputs dictionary, returns key for second-lowest value"""
    for key, value in my_dict.items():
         if value == sorted([*my_dict.values()])[1]:
             return key

def swapOneTwo(ballot):
    """inputs a ballot, and swaps position of first and second place"""
    
    if len(ballot) == 2:
        modified = ballot[1] + ballot[0]
    elif len(ballot) > 2:
        modified = ballot[1] + ballot[0] + ballot[2:]
    else:
        print("incorrect application of swapOneTwo function")
    return modified

def swapOneLoser(ballot, loser):
    """inputs a ballot with a bullet vote, puts loser above bullet vote"""
    modified = loser + ballot
    return modified

def swapLoserUp(string,loser): 
    """Inputs string and loser.  moves loser up to top of ballot if loser is
    on ballot, otherwise adds loser to top of ballot"""
    #netring = string.copy(deep=True) 
    if string.find(loser) == -1:
        string = loser + string
    else:
        string = loser + string.replace(loser, "")
    return string

def moveToTop(ballot, loser):
    """takes in a ballot and candidate, and moves that candidate to top of ballot"""
    if loser in ballot:
        return str(loser) + str(ballot.replace(loser,''))
    else:
        return ballot
    



############
############
## these functions used for voter strategy with polling info
## poll_result ranks all candidates by their first place votes
## in order of best to worst

def compromise_top_n(ballot, poll_result, n, bury_deep=True):
    """takes in ballot, identifies n contenders from top of poll"""
    """n/2 most preferred contenders move to top of poll""" 
    """bottom n/2 are buried, deep or shallow"""
    cons = poll_result[:n]
    
    ranked_cons = [cand for cand in ballot if cand in cons]
    if len(ranked_cons)<=n/2:
        top_cons = ranked_cons
        bottom_ranked_cons = []
        bottom_unranked_cons = [cand for cand in cons if cand not in ranked_cons]
        # add unranked contenders from worst to best
        bottom_unranked_cons.reverse()
    else:
        top_cons = ranked_cons[:int(n/2)]
        bottom_ranked_cons = ranked_cons[int(n/2):]
        bottom_unranked_cons = [cand for cand in cons if cand not in ranked_cons]
        # add unranked contenders from worst to best
        bottom_unranked_cons.reverse()
        
    ranked_noncons = [cand for cand in ballot if cand not in cons]
    if bury_deep:
        unranked_noncons = [cand for cand in poll_result if cand not in ballot and cand not in cons]
        unranked_noncons.reverse()
        new_ballot = top_cons + ranked_noncons + unranked_noncons + bottom_ranked_cons + bottom_unranked_cons
    else:
        new_ballot = top_cons + ranked_noncons + bottom_ranked_cons
        
    return ''.join(new_ballot)
    
def bullet_top_n(ballot, poll_result, n):
    """takes in ballot, truncates to bullet if top cand is in top n in poll"""
    if ballot[0] in poll_result[:n]:
        return ballot[0]
    else:
        return ballot
    
def protect_top_n(ballot, poll_result, n, bury_deep=True):
    """takes in ballot, identifies top n cands to protect"""
    """identifies candidates who outpolled candidates to protect"""
    """buries all threats, deep or shallow"""
    if len(ballot)<=n:
        protect = list(ballot)
    else:
        protect = list(ballot[:n])
    
    threat_indx = max([poll_result.index(cand) for cand in protect])
    threats = [cand for cand in poll_result[:threat_indx] if cand not in protect]
    threats.reverse()
    ranked_nonthreat = [cand for cand in ballot if cand not in threats and cand not in protect]
    if bury_deep:
        unranked = [cand for cand in poll_result if cand not in ballot and cand not in threats]
        unranked.reverse()    
        new_ballot = protect + ranked_nonthreat + unranked + threats
    else:
        ranked_threats = [cand for cand in threats if cand in ballot]
        new_ballot = protect + ranked_nonthreat + ranked_threats
    
    return ''.join(new_ballot)
    
def score_cands(ballot, poll_result, poll_weight=1):
    """takes in ballot, gives all candidates scores"""
    """computes borda score for each candidate from poll_result"""
    """plus borda score from ballot"""
    """then ranks all candidates in ballot by score"""
    scores = {cand: 0 for cand in ballot}
    num_cands = len(poll_result)
    for i in range(num_cands):
        if poll_result[i] in ballot:
            scores[poll_result[i]] += (num_cands-1-i)*poll_weight
            
    for i in range(len(ballot)):
        scores[ballot[i]] += (num_cands-1-i)
        
    new_ballot = list(ballot)
    new_ballot.sort(key=lambda cand: scores[cand], reverse=True)
    
    return ''.join(new_ballot)
    
    
    
    
    
    
    
    