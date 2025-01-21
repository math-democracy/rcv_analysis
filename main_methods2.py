import json
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.abspath('pref_voting/'))
from new_csv_loader import new_loader
import pref_voting_methods as creator

#existing voting methods in both votekit and pref_voting. Default packages should ideally be assigned based on which package does each method better!
import votekit.elections as v

import pref_voting.voting_methods as p #

#cleaning and other logistics
from votekit.cleaning import remove_noncands
from votekit.pref_profile import PreferenceProfile


def process_cands(prof, cands_to_keep):
    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    return prof
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#profile conversion for both votekit and pref_voting packages
#--------------------------------------------------------------------------------------------------------------------------------------------------#

#votekit
def v_profile(filename, to_remove = ["undervote", "overvote", "UWI"]):
    return remove_noncands(new_loader(filename)[0], to_remove)

#pref_voting
def p_profile(filename):
    return creator.create_profile(filename)
    

#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Plurality - can choose package
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Plurality(
    prof,
    cands_to_keep,
    candidates_with_indices = None,
    package: str = "pref_voting"
):
    elected="unknown"
    if package=="pref_voting":
        el = p.plurality(prof, cands_to_keep)[0]
        elected = candidates_with_indices[el]
    
    else:
        elected = list(v.Plurality(profile = prof).election_states[-1].elected[0])[0]

    
    return elected
    
#-------------------------------------------------------------------------------------------------------------------------------------------------  
#IRV - can choose package
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def IRV(
    prof, 
    cands_to_keep: list[str] = None,
    candidates_with_indices = None,
    package :str = "votekit",
):
    elected = "unknown"
    if package=="votekit":
        prof = process_cands(prof, cands_to_keep)
        elected = list(v.IRV(profile = prof).election_states[-1].elected[0])[0]
    
        
    else:
        el = p.instant_runoff_for_truncated_linear_orders(prof, candidates_with_indices)
        elected = candidates_with_indices[el[0]]
        
      
    return elected
        

#top-two IRV

def TopTwo(
    prof,
    cands_to_keep
):  
    elected = "unknown"
    try:
        if len(cands_to_keep) >= 2:
            prof = process_cands(prof, cands_to_keep)
            elected = list(v.TopTwo(profile = prof).election_states[-1].elected[0])[0]
    except Exception as e:
        elected = "unknown"
            
    return elected
        
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Borda methods - we use votekit
#--------------------------------------------------------------------------------------------------------------------------------------------------#

#right now this is the only method that takes in cands_to_keep. Must change so that every single method does this. 
def Borda_PM(
    prof,
    cands_to_keep, #include UWI in this if we want to keep it. If we want to keep everyone feed in full list of candidates
    candidates_with_indices = None
):
    # if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
    #     cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))
        
    # prof = process_cands(prof, cands_to_keep)

    # max_score=len(prof.candidates)-1 ##this will be equal to len(non_UWI_cands)-1 if UWI not in cands_to_keep, and to len(cands_to_keep)-1 if UWI is in cands_to_keep
    # vector = []
    # for i in range(len(prof.candidates)):
    #     vector.append(max_score-i)

    # elected = list(v.Borda(profile = prof, score_vector = vector).election_states[-1].elected[0])[0]
    # return elected
    if len(p.borda_for_profile_with_ties(prof)) == 1:
        return candidates_with_indices[p.borda_for_profile_with_ties(prof)[0]]
    else:
        return "unknown"
  
#Borda OM




#Borda AVG


#top3 truncation using 3-2-1. converts to 2-1 if we are only keeping 2 candidates
def Top3Truncation(
    prof,
    cands_to_keep: list[str] #include UWI in this if we want to keep it. If we want to keep everyone feed in full list of candidates
):
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))
        
    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions
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
#Condorcet methods - we use pref_voting
#--------------------------------------------------------------------------------------------------------------------------------------------------#

#regular Condorcet: returns Condorcet winner if there exists once, else returns everyone
def Condorcet(
    prof,
    candidates_with_indices,
    cands_to_keep
):
    elected = []
    try:
        el = p.condorcet(prof, cands_to_keep)
        elected = candidates_with_indices[el[0]]
    except Exception as e:
        return 'ERROR'

    return elected



#minimax: returns list of minimax winners
def Minimax(
    prof,
    candidates_with_indices,
    cands_to_keep
):
    el = p.minimax(prof, cands_to_keep)
    elected = candidates_with_indices[el[0]]
    return elected
    

#Smith set: returns Smith set as a list
def Smith(
    prof,
    candidates_with_indices,
    cands_to_keep
):
    el = p.top_cycle(prof,cands_to_keep)
    elected = candidates_with_indices[el[0]]
    return elected


#Smith-IRV: this one is causing errors
def Smith_IRV(
    prof,
    candidates_with_indices,
    cands_to_keep
):
    el = p.smith_irv(prof,cands_to_keep)
    elected = [candidates_with_indices[x] for x in el]
    
    return elected
    
#Smith-minimax
def Smith_minimax(
    prof,
    candidates_with_indices,
    cands_to_keep
):
    el = p.smith_minimax(prof,cands_to_keep)
    elected = candidates_with_indices[el[0]]
    
    return elected

#ranked pairs
def Ranked_Pairs(
    prof,
    candidates_with_indices,
    cands_to_keep
):
    el = p.ranked_pairs(prof,cands_to_keep)
    elected = candidates_with_indices[el[0]]
    return elected


#Condorcet plurality
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Bucklin - this is causing errors. Currently uses pref_voting
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Bucklin(
    prof,
    candidates_with_indices,
    package: str = "pref_voting"
):
    elected = []

    if package == "pref_voting":
        el = p.bucklin(prof)
        elected = [candidates_with_indices[x] for x in el]
        
    return elected
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Approval
#--------------------------------------------------------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Others
#--------------------------------------------------------------------------------------------------------------------------------------------------#