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
#--------------------------------------------------------------------------------------------------------------------------------------------------#

#right now this is the only method that takes in cands_to_keep. Must change so that every single method does this. 
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
    vector = []
    for i in range(len(prof.candidates)):
        vector.append(max_score-i)
    elected = list(v.Borda(profile = prof, score_vector = vector).election_states[-1].elected[0])[0]
    return elected
  
#Borda OM




#Borda AVG


#top3 truncation using 3-2-1. converts to 2-1 if we are only keeping 2 candidates
def Top3Truncation(
    filename: str,
    cands_to_keep: list[str] #include UWI in this if we want to keep it. If we want to keep everyone feed in full list of candidates
):
    prof= v_profile(filename)
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
    filename: str
):
    prof, file_path, candidates_with_indices = p_profile(filename)
    el = p.condorcet(prof)
    elected = [candidates_with_indices[c] for c in el]
    return elected



#minimax: returns list of minimax winners
def Minimax(
    filename: str
):
    prof, file_path, candidates_with_indices = p_profile(filename)
    el = p.minimax(prof)
    elected = [candidates_with_indices[c] for c in el]
    return elected
    

#Smith set: returns Smith set as a list
def Smith(
    filename: str
):
    prof, file_path, candidates_with_indices = p_profile(filename)
    el = p.top_cycle(prof)
    elected = [candidates_with_indices[c] for c in el]
    return elected


#Smith-IRV: this one is causing errors
def Smith_IRV(
    filename: str
):
    prof, file_path, candidates_with_indices = p_profile(filename)
    el = p.smith_irv(prof)
    elected = [candidates_with_indices[x] for x in el]
    
    return elected
    
#Smith-minimax
def Smith_minimax(
    filename: str
):
    prof, file_path, candidates_with_indices = p_profile(filename)
    el = p.smith_minimax(prof)
    elected = [candidates_with_indices[x] for x in el]
    
    return elected

#ranked pairs
def Ranked_Pairs(
    filename: str
):
    prof, file_path, candidates_with_indices = p_profile(filename)
    el = p.ranked_pairs(prof)
    elected = [candidates_with_indices[c] for c in el]
    return elected


#Condorcet plurality
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Bucklin - this is causing errors. Currently uses pref_voting
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Bucklin(
    filename: str,
    package: str = "pref_voting"
):
    elected = []
    prof, file_path, candidates_with_indices = p_profile(filename)
    el = p.bucklin(prof)
    elected = [candidates_with_indices[x] for x in el]
    
    return elected
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Approval
#--------------------------------------------------------------------------------------------------------------------------------------------------#


#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Others
#--------------------------------------------------------------------------------------------------------------------------------------------------#
    
    
