import json
import pandas as pd
import numpy as np
from typing import Optional

import os
import sys
sys.path.append(os.path.abspath('pref_voting/'))

#for loading files and converting into profiles for both votekit and pref_voting packages
from new_csv_loader import new_loader
import pref_voting_methods as creator

#existing voting methods in both votekit and pref_voting. Default packages should ideally be assigned based on which package does each method better!
import votekit.elections as v
import pref_voting.voting_methods as p #

#cleaning and other logistics
from votekit.cleaning import remove_noncands
from votekit.ballot import Ballot
from votekit.pref_profile import PreferenceProfile
from votekit.graphs import PairwiseComparisonGraph
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#profile conversion for both votekit and pref_voting packages
#--------------------------------------------------------------------------------------------------------------------------------------------------#

#votekit
def v_profile(filename, to_remove = ["undervote", "overvote", "UWI"]):
    return remove_noncands(new_loader(filename)[0], to_remove)

#pref_voting
def p_profile(filename):
    return creator.create_profile(filename)
#
# Head-to-Head counts for a votekit profile - borrowed from votekit.PairwiseComparisonGraph
#  

def head2head_count(
    prof: PreferenceProfile, 
    cand_1: str, 
    cand_2: str
):
    count = 0
    bal = prof.ballots
    for b in bal:
        rank_list = b.ranking
        for s in rank_list:
            if cand_1 in s:
                count += b.weight
                break
            elif cand_2 in s:
                break
    return count
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Plurality - can choose package
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Plurality(
    filename: str,
    package: str = "pref_voting"
):
    
    elected="unknown"
    if package=="pref_voting":
        prof, file_path, candidates_with_indices = p_profile(filename)
        el = p.plurality(prof, candidates_with_indices)[0]
        elected = candidates_with_indices[el]
    
    else:
        prof= v_profile(filename)
        elected = list(v.Plurality(profile = prof).election_states[-1].elected[0])[0]

    
    return elected
    
#-------------------------------------------------------------------------------------------------------------------------------------------------  
#IRV - can choose package
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def IRV(
    filename: str, 
    package :str = "votekit"
):
    elected = "unknown"
    if package=="votekit":
        prof= v_profile(filename)
        elected = list(v.IRV(profile = prof).election_states[-1].elected[0])[0]
    
        
    else:
        prof, file_path, candidates_with_indices = p_profile(filename)
        el = p.instant_runoff_for_truncated_linear_orders(prof, candidates_with_indices)[0]
        elected = candidates_with_indices[el]
        
      
    return elected
        

#top-two IRV

def TopTwo(
    filename: str
):  
    elected = "unknown"
    prof=v_profile(filename)
    elected = list(v.TopTwo(profile = prof).election_states[-1].elected[0])[0]
        
    return elected
        
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Borda methods - we use votekit
#right now Borda is the only method that takes in cands_to_keep. Must change so that every single method does this. 
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Borda_PM(
    filename: str,
    cands_to_keep: list[str] #include UWI in this if we want to keep it. If we want to keep everyone feed in full list of candidates
):
    prof= v_profile(filename)
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))
        
    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    max_score=len(prof.candidates)-1 ##this will be equal to len(non_UWI_cands)-1 if UWI not in cands_to_keep, and to len(cands_to_keep)-1 if UWI is in cands_to_keep
    ballots = prof.ballots
    el_scores= {c:0 for c in cands_to_keep}
    for i in range(1,len(prof.candidates)+1):
        bal = [b for b in ballots if len(b.ranking) == i]
        for b in bal:
            cands_in_b = []
            for c in cands_to_keep:
                for y in b.ranking:
                    if c in y:
                        cands_in_b.append(c)
                        break
            not_in_b = [{c} for c in cands_to_keep if c not in cands_in_b]
            b=Ballot(ranking = list(b.ranking) + not_in_b, weight = b.weight)
            vector = list(range(max_score,max_score-i,-1))+[0 for k in range(len(cands_to_keep)-i)] 
        p = PreferenceProfile(ballots = bal)
        el = v.Borda(profile = p, score_vector = vector).election_states[0].scores
        for c in cands_to_keep:
            if c not in el:
                el[c]=0
            el_scores[c]+=el[c]
    winning_score = max(el_scores.values())
    elected = [c for c in cands_to_keep if el_scores[c]==winning_score]
    return elected
    
#Borda OM
def Borda_OM(
    filename: str,
    cands_to_keep: list[str] 
):
    prof= v_profile(filename)
    if 'skipped' in cands_to_keep:
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))
        
    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands)

    max_score=len(prof.candidates)-1 
    ballots = prof.ballots
    el_scores= {c:0 for c in cands_to_keep}
    for i in range(1,len(prof.candidates)+1):
        bal = [b for b in ballots if len(b.ranking) == i]
        for b in bal:
            cands_in_b = []
            for c in cands_to_keep:
                for y in b.ranking:
                    if c in y:
                        cands_in_b.append(c)
                        break
            not_in_b = [{c} for c in cands_to_keep if c not in cands_in_b]
            b=Ballot(ranking = list(b.ranking) + not_in_b, weight = b.weight)
            vector = list(range(max_score,max_score-i,-1))+[max_score-i for k in range(len(cands_to_keep)-i)] 
        p = PreferenceProfile(ballots = bal)
        el = v.Borda(profile = p, score_vector = vector).election_states[0].scores
        for c in cands_to_keep:
            if c not in el:
                el[c]=0
            el_scores[c]+=el[c]
    winning_score = max(el_scores.values())
    elected = [c for c in cands_to_keep if el_scores[c]==winning_score]
    return elected



#Borda AVG
def Borda_AVG(
    filename: str,
    cands_to_keep: list[str] 
):
    prof= v_profile(filename)
    if 'skipped' in cands_to_keep:
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))
        
    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) 

    max_score=len(prof.candidates)-1 
    ballots = prof.ballots
    el_scores= {c:0 for c in cands_to_keep}
    for i in range(1,len(prof.candidates)+1):
        bal = [b for b in ballots if len(b.ranking) == i]
        for b in bal:
            cands_in_b = []
            for c in cands_to_keep:
                for y in b.ranking:
                    if c in y:
                        cands_in_b.append(c)
                        break
            not_in_b = [{c} for c in cands_to_keep if c not in cands_in_b]
            b=Ballot(ranking = list(b.ranking) + not_in_b, weight = b.weight)
            vector = list(range(max_score,max_score-i,-1))+[(max_score-i)/2 for k in range(len(cands_to_keep)-i)] 
        p = PreferenceProfile(ballots = bal)
        el = v.Borda(profile = p, score_vector = vector).election_states[0].scores
        for c in cands_to_keep:
            if c not in el:
                el[c]=0
            el_scores[c]+=el[c]
    winning_score = max(el_scores.values())
    elected = [c for c in cands_to_keep if el_scores[c]==winning_score]
    return elected



#top3 truncation using 3-2-1. converts to 2-1 if we are only keeping 2 candidates
def Top3Truncation(
    filename: str,
    cands_to_keep: list[str]
):
    prof= v_profile(filename)
    if 'skipped' in cands_to_keep:
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))
        
    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) 
    if len(prof.candidates)==0:
        return 'skipped'
    elif len(prof.candidates)==1:
        return prof.candidates[0]
    
    if len(prof.candidates)==2:
        vector = [2,1]
        
    else:
        vector = [3,2,1]+[0 for i in range(len(prof.candidates) -3)]
    elected = list(v.Borda(profile = prof, score_vector = vector).election_states[-1].elected[0])[0]
    return elected
    
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Condorcet methods - we use votekit
#--------------------------------------------------------------------------------------------------------------------------------------------------#

#regular Condorcet: returns Condorcet winner if there exists once, else returns []
def Condorcet(
    filename: str
):
    prof= v_profile(filename)
    elected = list(v.DominatingSets(profile = prof).election_states[-1].elected[0])[0]
    if len(elected)>1:
        elected = []
    return elected


#Smith set: returns Smith set as a list
def Smith(
    filename: str
):
    prof= v_profile(filename)
    elected = list(v.DominatingSets(profile = prof).election_states[-1].elected[0])[0]
    return elected

#Smith Plurality
def Smith_Plurality(
    filename: str
):
    prof= v_profile(filename)
    smith = list(v.DominatingSets(profile = prof).election_states[-1].elected[0])[0]
    if len(smith)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in smith]
        prof = remove_noncands(prof, noncands) 
    elected = list(v.Plurality(profile = prof).election_states[-1].elected[0])[0]
    return elected


#Smith-IRV
def Smith_IRV(
    filename: str
):
    prof= v_profile(filename)
    smith = list(v.DominatingSets(profile = prof).election_states[-1].elected[0])[0]
    if len(smith)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in smith]
        prof = remove_noncands(prof, noncands) 
    elected = list(v.IRV(profile = prof).election_states[-1].elected[0])[0]
    return elected


#minimax: returns list of minimax winners
def Minimax(
    filename: str
):
    prof= v_profile(filename)
    cands = [c for c in prof.candidates if c!="skipped"]
    defeat_margins={c:0 for c in cands}
    for c in cands:
        defeat_margins[c] = 0
        for y in cands:
            margin = head2head_count(prof,y,c) - head2head_count(prof,c,y)
            if margin> defeat_margins[c]:
                    defeat_margins[c] = margin
    elected = [c for c in defeat_margins if defeat_margins[c]==min(defeat_margins.values())]          
    return elected
    

#Smith-minimax
def Smith_Minimax(
    filename: str
):
    prof= v_profile(filename)
    smith = list(v.DominatingSets(profile = prof).election_states[-1].elected[0])[0]
    if len(smith)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in smith]
        prof = remove_noncands(prof, noncands) 
    cands = [c for c in prof.candidates if c!="skipped"]
    defeat_margins={c:0 for c in cands}
    for c in cands:
        defeat_margins[c] = 0
        for y in cands:
            margin = head2head_count(prof,y,c) - head2head_count(prof,c,y)
            if margin>defeat_margins[c]:
                    defeat_margins[c] = margin
    elected = [x for x in defeat_margins if defeat_margins[x]==min(defeat_margins.values())]          
    
    return elected


#ranked pairs
#def Ranked_Pairs(
 #   filename: str
#):
#    prof, file_path, candidates_with_indices = p_profile(filename)
#    el = p.ranked_pairs(prof)
#    elected = [candidates_with_indices[c] for c in el]
#   return elected


#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Bucklin - custom, but uses votekit. Returns list of winners
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Bucklin(
    filename: str,
    
):
    elected =[]
    prof = v_profile(filename)
    num_cands = len(prof.candidates)
    maj = sum(b.weight for b in prof.ballots)/2
    for i in range(num_cands):
        bal = prof.ballots
        for b in bal:
            b= Ballot(ranking = b.ranking[:i+1], weight = b.weight)
        new_prof = PreferenceProfile(ballots = bal)
        el_scores = v.Borda(profile = prof, score_vector = [1 for k in range(i+1)]).election_states[0].scores
        if max(el_scores.values())>maj:
            elected = [c for c in el_scores if el_scores[c]>maj and c!="skipped"]
            break
    if elected == []:
        elected = [c for c in el_scores if el_scores[c]==max(el_scores.values()) and c!="skipped"] ##I'm not sure this can happen
    return elected
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Approval
#--------------------------------------------------------------------------------------------------------------------------------------------------#
def Approval(
    filename: str,
    cands_to_keep: list[str]
):
    prof= v_profile(filename)
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))
        
    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    ballots = prof.ballots
    el_scores= {c:0 for c in cands_to_keep}
    for b in ballots:
        for s in b.ranking:
            for c in list(s):
                el_scores[c]+=b.weight
    winning_score = max(el_scores.values())
    elected = [c for c in cands_to_keep if el_scores[c]==winning_score]
    return elected

#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Others
#--------------------------------------------------------------------------------------------------------------------------------------------------#
