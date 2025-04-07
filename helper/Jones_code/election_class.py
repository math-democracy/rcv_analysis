########################################
##### Election method class
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


## used in IRV function
def truncate(number, digits) -> float: #truncates according to Scotland rules
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


##### TODO
## slim down to one IRV function that returns everything necessary


###############################################################################
##### Election methods
##### All methods take in a preference profile and a list of candidates
##### diagnostic = True prints out information about the election
##### All methods return a list with winners first, followed by other stuff
###############################################################################

def Borda_PM(profile, cands, diagnostic=False):
    
    num_cands = len(cands)
    max_score = num_cands - 1
    
    ## compute candidate scores
    cand_scores = {cand: 0 for cand in cands}
    for k in range(len(profile)):
        count = profile.at[k, 'Count']
        curBal= profile.at[k, 'ballot']
        for i in range(0,len(curBal)):
            candidate = curBal[i]
            if candidate in cands:
                cand_scores[candidate] += (max_score - (i )) * count
            # else:
            #     print("Candidate in ballot that is not in candidate list")
    
    if diagnostic:
        print(cand_scores)
        
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return [winners]

###############################################################################
###############################################################################

def Borda_OM(profile, cands, diagnostic=False):
    
    num_cands = len(cands)
    max_score = num_cands - 1
    
    ## compute candidate scores
    cand_scores = {cand: 0 for cand in cands}
    for k in range(len(profile)):
        count = profile.at[k, 'Count']
        curBal= profile.at[k, 'ballot']
        for i in range(0,len(curBal)):
            candidate = curBal[i]
            if candidate in cands:
                cand_scores[candidate] += (max_score - (i )) * count
            # else:
            #     print("Candidate in ballot that is not in candidate list")
        
        ## add score for all candidates not on ballot
        for cand in cands:
            if cand not in curBal:
                cand_scores[cand] += (max_score - len(curBal)) * count
       
    if diagnostic:
        print(cand_scores)
        
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return [winners]

###############################################################################
###############################################################################

def Borda_AVG(profile, cands, diagnostic=False):
    
    num_cands = len(cands)
    max_score = num_cands - 1
    
    ## compute candidate scores
    cand_scores = {cand: 0 for cand in cands}
    for k in range(len(profile)):
        count = profile.at[k, 'Count']
        curBal= profile.at[k, 'ballot']
        for i in range(0,len(curBal)):
            candidate = curBal[i]
            if candidate in cands:
                cand_scores[candidate] += (max_score - (i )) * count
            # else:
            #     print("Candidate in ballot that is not in candidate list")
        
        ## add score for all candidates not on ballot
        missing_cand_num = num_cands - len(curBal) 
        avg_points = (missing_cand_num - 1)/2
        for cand in cands:
            if cand not in curBal:
                cand_scores[cand] += avg_points * count
        
    if diagnostic:
        print(cand_scores)
        
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return [winners]

###############################################################################
###############################################################################

def IRV(frame3, cands, diagnostic=False):
    frame2 = frame3.copy(deep=True)
    """Inputs election, Returns winners, losers=eliminated candidates, 
      dictionary of pre-elimination data"""#, dictionary of winners at each step of elimination
    winners=[]
    hopefuls=[]
    eliminatedCand=[]
    elimFrames={}
    tempWinners={}
    quota=math.floor(sum(frame2['Count'])/(2))+1
    
    # list1=[] #gather all the candidate names
    # for k in range(len(frame2)):
    #     for i in range(len(frame2.at[k,'ballot'])):
    #         if frame2.at[k,'ballot'][i] not in list1:
    #             list1.append(frame2.at[k,'ballot'][i])
    list1 = cands
    
    cand_dict={}
    n = len(list1)
    S=1
    for i in range(n):#n
        cand_dict[i]=list1[i]
        hopefuls.append(list1[i])
    
    #Get each candidate's initial number of votes this round
    vote_counts={cand:0 for cand in hopefuls}
    # vote_counts = {}
    
    for k in range(len(frame2)):
            if frame2.at[k,'ballot']!='':
                if frame2.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                else:
                    vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']

        
    max_count=max(vote_counts.values())
    while len(winners)<1:
        
        if diagnostic:
            print(vote_counts)
            
        max_count=max(vote_counts.values())
        
        if max_count>=quota: #somebody is elected 
            #There might be multiple people elected this round; save them as a sorted dictionary
            votes_for_winners={k:vote_counts[k] for k in vote_counts.keys() if vote_counts[k]>=quota }
            votes_for_winners=dict(sorted(votes_for_winners.items(),key=lambda x: x[1], reverse=True))
            
            #If we try to elect too many people, error
            if len(winners)+len(votes_for_winners)>S:
                print("Error in tabulation.  Multiple winners found.")
                for k in range(len(winners)+len(votes_for_winners)-S):
                    winners.append(list(votes_for_winners.keys())[k])
            
            else:
                winners=winners+list(votes_for_winners.keys())
                for cand in winners:
                    if cand in hopefuls:
                        hopefuls.remove(cand)
                
                while len(votes_for_winners)>0:
                    
                    cand=list(votes_for_winners.keys())[0]
    
                    if cand not in winners:
                        winners.append(cand)
                        hopefuls.remove(cand)
                    if len(winners)==1:
                        return winners, eliminatedCand, elimFrames #, tempWinners (don't need tempWinners?)
                    
        #nobody is elected by surpassing quota, but the number
        #of candidates left equals S
        elif len(hopefuls)+len(winners)==1:
            return winners+hopefuls, eliminatedCand, elimFrames #, tempWinners
        
        #remove weakest cand and transfer their votes with weight one
        else:
            min_count=min(i for i in vote_counts.values() if i>=0)
            # min_count=min(i for i in vote_counts.values() if i>0)
            count=0
            for votes in vote_counts:
                if votes==min_count:
                    count+=1
            if count>1:
                print("tie in candidate to remove")
                return

            eliminated_cand = list(vote_counts.keys())[list(vote_counts.values()).index(min_count)] #took str() away
            
            elimFrames[len(eliminatedCand)]=frame2.copy(deep=True)
            #tempWinners[len(eliminatedCand)]=copy.deepcopy(winners)
            #print(frame2)
            eliminatedCand.append(eliminated_cand)
            if eliminated_cand in hopefuls:
                hopefuls.remove(eliminated_cand)
            
            for k in range(len(frame2)):
                if eliminated_cand in frame2.iloc[k]['ballot']:
                    frame2.at[k,'ballot']=frame2.at[k,'ballot'].replace(eliminated_cand,'')
            for k in range(len(frame2)):
                if frame2.at[k,'ballot']=='':
                    frame2.drop(k)
            vote_counts={cand:0 for cand in hopefuls}
           
            for k in range(len(frame2)):
                if frame2.at[k,'ballot']!='':
                    if frame2.at[k,'ballot'][0] in vote_counts.keys():
                        vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                    else:
                        vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']
            #print(vote_counts)
            max_count=max(vote_counts.values())
            if len(hopefuls)+len(winners)==1:
                return winners+hopefuls, eliminatedCand, elimFrames #, tempWinners
            frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
    return [winners, eliminatedCand, elimFrames] #, tempWinners

###############################################################################
###############################################################################

def minimax(profile, cands, diagnostic=False):
    
    num_cands = len(cands)
    
    ## compute H2H margins
    margins = np.zeros((num_cands, num_cands))
    
    for c1 in range(num_cands):
        for c2 in range(c1+1, num_cands):
            c1_let = cands[c1]
            c2_let = cands[c2]
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
            
    worst_loss = margins.min(axis=1)
    winners = [cands[i] for i in range(num_cands) if worst_loss[i] == max(worst_loss)]
    return [winners]
   
###############################################################################
###############################################################################

def ranked_pairs(profile, cands, diagnostic=False):
    
    num_cands = len(cands)
    
    ## compute H2H margins
    margins = np.zeros((num_cands, num_cands))
    H2H_list = []
    
    for c1 in range(num_cands):
        for c2 in range(c1+1, num_cands):
            c1_let = cands[c1]
            c2_let = cands[c2]
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
            
            if margin > 0.0:
                H2H_list.append([(c1, c2), margin])
            else:
                H2H_list.append([(c2, c1), -1*margin])
    
    if diagnostic:
        print(margins)
        print(H2H_list)
        
    ## check for condorcet winner
    for c1 in range(num_cands):
        winner = True
        for c2 in range(num_cands):
            if margins[c1, c2] < 0.0:
                winner = False
                break
        if winner:
            return [[cands[c1]]]
    
    ## run the ranked pairs algorithm
    H2H_list.sort(key=lambda x: x[1], reverse=True)
    
    is_better = [set() for _ in range(num_cands)]
    is_worse = [set() for _ in range(num_cands)]
    
    for pair in H2H_list:
        winner = pair[0][0]
        loser = pair[0][1]
        
        ## this edge does not create a cycle, is added
        if loser not in is_worse[winner]:
            ## update winner's is_better
            is_better[winner] = is_better[winner].union({loser})
            is_better[winner] = is_better[winner].union(is_better[loser])
            if len(is_better[winner]) == num_cands-1:
                return [[cands[winner]]]
                
            ## update everyone better than winner
            for cand in is_worse[winner]:
                is_better[cand] = is_better[cand].union(is_better[winner])
                if len(is_better[cand]) == num_cands-1:
                    return [[cands[cand]]]
                
            ## update loser's is_worse
            is_worse[loser] = is_worse[loser].union({winner})
            is_worse[loser] = is_worse[loser].union(is_worse[winner])
            ## update everyone worse than loser
            for cand in is_better[loser]:
                is_worse[cand] = is_worse[cand].union(is_worse[loser])

###############################################################################
###############################################################################

def bucklin(profile, cands, diagnostic=False):
    
    num_cands = len(cands)
    
    ## Initialize scores for candidates to 0
    scores = {cand: 0.0 for cand in cands}
    threshold = profile['Count'].sum() / 2
    
    if diagnostic:
        print(scores)
        print(threshold)
    
    for round_indx in range(num_cands):
        ## update scores for the current round
        for k in range(len(profile)):
            ballot = profile.at[k, 'ballot']
            if len(ballot) > round_indx:
                cand = ballot[round_indx]
                if cand in cands:
                    scores[cand] += profile.at[k, 'Count']

        if diagnostic:
            print(scores)
            
        ## Check if any candidate has surpassed the majority threshold
        surpassing_candidates = {cand: score for cand, score in scores.items() if score > threshold}
        if surpassing_candidates:
            max_score = max(surpassing_candidates.values())
            winners = [cand for cand, score in surpassing_candidates.items() if score == max_score]
            return [winners]  

    ## At the end of all rounds, if no majority is reached
    max_score = max(scores.values())
    winners = [cand for cand, score in scores.items() if score == max_score]
    return [winners]

###############################################################################
###############################################################################

def plurality(profile, cands, diagnostic=False):
    
    ## Initialize scores for candidates to 0
    scores = {cand: 0.0 for cand in cands}
    
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        if ballot[0] in cands:
            scores[ballot[0]] += profile.at[k, 'Count']
    
    if diagnostic:
        print(scores)
        
    ## Winner has most first place votes
    max_score = max(scores.values())
    winners = [cand for cand, score in scores.items() if score == max_score]
    return [winners]

###############################################################################
###############################################################################

def plurality_runoff(profile, cands, diagnostic=False):
    
    ## doesn't work unless there are two+ candidates
    if len(cands)==1:
        return cands
    
    ## Initialize scores for candidates to 0
    r1scores = {cand: 0.0 for cand in cands}
    
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        if ballot[0] in cands:
            r1scores[ballot[0]] += profile.at[k, 'Count']
    
    ## keep two candidates with highest scores
    cands.sort(key=lambda cand: r1scores[cand], reverse = True)
    second_round_cands = cands[:2]
    
    if diagnostic:
        print(r1scores)
        print(second_round_cands)
    
    ## run two candidate election
    c1, c2 = second_round_cands
    r2scores = {cand: 0.0 for cand in second_round_cands}
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        if c1 in ballot and c2 in ballot:
            if ballot.find(c1)<ballot.find(c2):
                r2scores[c1] += profile.at[k, 'Count']
            else:
                r2scores[c2] += profile.at[k, 'Count']
        elif c1 in ballot:
            r2scores[c1] += profile.at[k, 'Count']
        elif c2 in ballot:
            r2scores[c2] += profile.at[k, 'Count']
            
    if diagnostic:
        print(r2scores)
    
    ## Winner has most first place votes
    max_score = max(r2scores.values())
    winners = [cand for cand, score in r2scores.items() if score == max_score]
    return [winners]

###############################################################################
###############################################################################


def restrict_to_smith(profile, cands, diagnostic=False):
    # compute smith set, create new ballot profile restricting to smith set
    
    num_cands = len(cands)
    
    ## compute H2H margins
    margins = np.zeros((num_cands, num_cands))
    
    for c1 in range(num_cands):
        for c2 in range(c1+1, num_cands):
            c1_let = cands[c1]
            c2_let = cands[c2]
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
            
    if diagnostic:
        print(margins)
    
    ## calculate smith set
    copeland_scores = {}
    for i in range(num_cands):
        score = 0.0
        for j in range(num_cands):
            if i != j:
                if margins[i,j]>0:
                    score += 1
                elif margins[i,j] == 0:
                    score += 0.5
        copeland_scores[i] = score
        
    if diagnostic:
        print(copeland_scores)

    ## at this point, smith_set is just the copeland set
    smith_set = [i for i in range(num_cands) if copeland_scores[i]==max(copeland_scores.values())]
    
    ## add iteratively add candidates who beat someone in the set
    finished = False
    while not finished:
        finished = True
        for i in smith_set:
            for j in range(num_cands):
                if j not in smith_set and margins[j, i] >= 0:
                    smith_set.append(j)
                    finished = False
    
    smith_set_lets = [cands[i] for i in smith_set]
    
    if diagnostic:
        print(smith_set_lets)
    
    ## construct new ballot profile
    ## dictionary first to create efficient ballot profile
    new_ballots = {}
    for k in range(len(profile)):
        old_ballot = profile.at[k, 'ballot']
        new_ballot = ''
        for cand in old_ballot:
            if cand in smith_set_lets:
                new_ballot+=cand
        if new_ballot:
            if new_ballot in new_ballots.keys():
                new_ballots[new_ballot] += profile.at[k, 'Count']
            else:
                new_ballots[new_ballot] = profile.at[k, 'Count']
            
    column_names=['ballot','Count']
    new_profile=pd.DataFrame(columns = column_names)
                
    for ballot in new_ballots:
        row={'Count':[float(new_ballots[ballot])], 'ballot':[ballot]}
        single_df=pd.DataFrame(row)
        new_profile = pd.concat([new_profile, single_df], ignore_index=True)
        
    return [smith_set_lets, new_profile]

###############################################################################
###############################################################################

def smith_irv(profile, cands, diagnostic=False):
    smith_set, new_profile = restrict_to_smith(profile, cands, diagnostic=diagnostic)
    if diagnostic:
        print(smith_set)
    return IRV(new_profile, smith_set, diagnostic=diagnostic)

###############################################################################
###############################################################################

def smith_minimax(profile, cands, diagnostic=False):
    smith_set, new_profile = restrict_to_smith(profile, cands, diagnostic=diagnostic)
    if diagnostic:
        print(smith_set)
    return minimax(new_profile, smith_set, diagnostic=diagnostic)

###############################################################################
###############################################################################
    
def smith_plurality(profile, cands, diagnostic=False):
    smith_set, new_profile = restrict_to_smith(profile, cands, diagnostic=diagnostic)
    if diagnostic:
        print(smith_set)
    return plurality(new_profile, smith_set, diagnostic=diagnostic)