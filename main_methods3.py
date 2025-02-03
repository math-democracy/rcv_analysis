#required
from typing import Optional
import networkx as nx

#-------------------------------------------------------------------------------------------
#import os
#import sys
#sys.path.append(os.path.abspath('pref_voting/'))
#-------------------------------------------------------------------------------------------

#for loading files and converting into profiles for votekit
from helper.new_csv_loader import new_loader
#import pref_voting_methods as creator

#-------------------------------------------------------------------------------------------
#existing voting methods in votekit 
import votekit.elections as v
#import pref_voting.voting_methods as p #

#-------------------------------------------------------------------------------------------
#cleaning and other logistics
from votekit.cleaning import remove_noncands
from votekit.ballot import Ballot
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
#def p_profile(filename):
#    return creator.create_profile(filename)

#--------------------------------------------------------------------------------------------------------------------------------------------------#
# Head-to-Head counts for a votekit profile - borrowed from votekit.PairwiseComparisonGraph
#--------------------------------------------------------------------------------------------------------------------------------------------------#

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
# Dominating tiers for a votekit profile - borrowed from votekit.PairwiseComparisonGraph
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def dominating_tiers(
    prof: PreferenceProfile
):
    beat_set_size_dict = {}
    cands = [c for c in prof.candidates if c!="skipped"]
    for c in cands:
        beat_set = set()
        for y in cands:
            if c!=y:
                if head2head_count(prof,c,y)>head2head_count(prof,y,c):
                    beat_set.add(y)
        beat_set_size_dict[c] = len(beat_set)
    # We want to return candidates sorted and grouped by beat set size
    tier_dict: dict = {}
    for k, v in beat_set_size_dict.items():
        if v in tier_dict.keys():
            tier_dict[v].add(k)
        else:
            tier_dict[v] = {k}
    tier_list = [tier_dict[k] for k in sorted(tier_dict.keys(), reverse=True)]
    return tier_list
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Plurality 
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Plurality(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    elected = list(v.Plurality(profile = prof).election_states[-1].elected[0])[0]
    if not type(elected) is set:
        elected = set([elected])
    
    return elected
    
#-------------------------------------------------------------------------------------------------------------------------------------------------  
#IRV 
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def IRV(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    elected = list(v.IRV(profile = prof).election_states[-1].elected[0])[0]
    if not type(elected) is set:
        elected = set([elected])    
    return elected
        

#top-two IRV

def TopTwo(
    #filename: str,
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):  
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<2:
        return set([None])
    else:
        if len(cands_to_keep)<len(prof.candidates):
            noncands = [c for c in prof.candidates if c not in cands_to_keep]
            prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

        elected = list(v.TopTwo(profile = prof).election_states[-1].elected[0])[0]
        if not type(elected) is set:
            elected = set([elected])

        return elected
        
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Borda methods - we use votekit
#right now Borda is the only method that takes in cands_to_keep. Must change so that every single method does this. 
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Borda_PM(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None #include UWI in this if we want to keep it. If we want to keep everyone feed in full list of candidates
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
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
    elected = set([c for c in cands_to_keep if el_scores[c]==winning_score])
    return elected
    
#Borda OM
def Borda_OM(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

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
    elected = set([c for c in cands_to_keep if el_scores[c]==winning_score])
    return elected

#Borda AVG
def Borda_AVG(
    #filename: str,
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None 
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

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
    elected = set([c for c in cands_to_keep if el_scores[c]==winning_score])
    return elected

#top3 truncation using 3-2-1. converts to 2-1 if we are only keeping 2 candidates
def Top3Truncation(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
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
    if not type(elected) is set:
        elected = set([elected])
    
    return elected
    
    
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Condorcet methods - we use votekit
#--------------------------------------------------------------------------------------------------------------------------------------------------#

#regular Condorcet: returns Condorcet winner if there exists once, else returns []
def Condorcet(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    elected = dominating_tiers(prof)[0]
    if len(elected)>1:
        elected = set()
    return elected


#Smith set: returns Smith set as a list
def Smith(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    elected = dominating_tiers(prof)[0]
    return elected

#Smith Plurality
def Smith_Plurality(
    #filename: str
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    elected = list(v.Plurality(profile = prof).election_states[-1].elected[0])[0]
    if not type(elected) is set:
        elected = set([elected])
    
    return elected


#Smith-IRV
def Smith_IRV(
    #filename: str
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    elected = list(v.IRV(profile = prof).election_states[-1].elected[0])[0]
    if not type(elected) is set:
        elected = set([elected])
    
    return elected

#minimax: returns list of minimax winners
def Minimax(
    #filename: str
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    cands = [c for c in prof.candidates]
    defeat_margins={c:0 for c in cands}
    for c in cands:
        defeat_margins[c] = 0
        for y in cands:
            margin = head2head_count(prof,y,c) - head2head_count(prof,c,y)
            if margin> defeat_margins[c]:
                    defeat_margins[c] = margin
    elected = set([c for c in defeat_margins if defeat_margins[c]==min(defeat_margins.values())])         
    return elected
    

#Smith-minimax
def Smith_Minimax(
    #filename: str
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    smith = dominating_tiers(prof)[0]
    if len(smith)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in smith]
        prof = remove_noncands(prof, noncands) 
    cands = prof.candidates
    defeat_margins={c:0 for c in cands}
    for c in cands:
        defeat_margins[c] = 0
        for y in cands:
            margin = head2head_count(prof,y,c) - head2head_count(prof,c,y)
            if margin>defeat_margins[c]:
                    defeat_margins[c] = margin
    elected = set([x for x in defeat_margins if defeat_margins[x]==min(defeat_margins.values())])          
    
    return elected


#ranked pairs
def Ranked_Pairs(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    cands = prof.candidates
    victory_margins : dict = {}
    for c in cands:
        for y in cands:
            if ((c,y) not in victory_margins.keys()) and ((y,c) not in victory_margins.keys()):
                margin = head2head_count(prof,c,y) - head2head_count(prof,y,c)
                if margin>0:
                    victory_margins[(c,y)] = margin
                elif margin<0:
                    victory_margins[(y,c)]=-1*margin

    sorted_pairs = sorted(zip(victory_margins.values(),victory_margins.keys()),reverse = True)
    gr = nx.DiGraph()
    present = set()
    for (v,p) in sorted_pairs:
        present.add(p[0])
        present.add(p[1])
    gr.add_nodes_from(list(present))
    for (v,p) in sorted_pairs:
        if not nx.has_path(gr, p[1],p[0]):
            gr.add_edge(p[0],p[1])
    elected = set()
    for c in gr.nodes:
        if gr.in_degree(c)==0:
            elected.add(c)
            break
    if len(cands_to_keep)<2:
        return set([None])
    else:
        return elected

    
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Bucklin - custom, but uses votekit. Returns list of winners
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Bucklin(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    num_cands = len(prof.candidates)
    maj = sum(b.weight for b in prof.ballots)/2
    for i in range(num_cands):
        bal = prof.ballots
        for b in bal:
            b= Ballot(ranking = b.ranking[:i+1], weight = b.weight)
        el_scores = v.Borda(profile = prof, score_vector = [1 for k in range(i+1)]).election_states[0].scores
        if max(el_scores.values())>maj:
            elected = set([c for c in el_scores if el_scores[c]>maj and c!="skipped"])
            break
    if elected == set():
        elected = set([c for c in el_scores if el_scores[c]==max(el_scores.values()) and c!="skipped"]) ##I'm not sure this can happen
    return elected
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Approval
#--------------------------------------------------------------------------------------------------------------------------------------------------#
def Approval(
    prof: PreferenceProfile,
    cands_to_keep: Optional[list[str]] = None
):
    if not cands_to_keep:
        cands_to_keep = prof.candidates
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
    elected = set([c for c in cands_to_keep if el_scores[c]==winning_score])
    return elected

#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Others
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def IRV_With_Explaination(prof):
    cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))
    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions
    
    election = str(v.IRV(profile=prof))

    election_dict = {}
    i = 0
    for line in election.strip().split("\n"):
        if i != 0:
            parts = line.rsplit(maxsplit=2)
            name = parts[0].strip()
            status = parts[1]
            round_number = int(parts[2])
            election_dict[name] = {"status": status, "round": round_number}
        
        i += 1
    return election_dict