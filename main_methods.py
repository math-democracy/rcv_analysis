#required
from typing import Optional, Union
import networkx as nx
from itertools import combinations
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

def process_cands(
        prof: PreferenceProfile, 
        cands_to_keep: list
    )-> PreferenceProfile:
    if len(cands_to_keep)<len(prof.candidates):
        noncands = [c for c in prof.candidates if c not in cands_to_keep]
        prof = remove_noncands(prof, noncands) ##at this point prof only has cands_to_keep. Will include UWI iff UWI is in cands_to_keep. This profile has no 'skipped' positions

    return prof

#--------------------------------------------------------------------------------------------------------------------------------------------------#
#profile conversion for both votekit and pref_voting packages
#--------------------------------------------------------------------------------------------------------------------------------------------------#

#votekit
def v_profile(
        filename: str, 
        to_remove: list = ["undervote", "overvote", "UWI","uwi"]
    )-> PreferenceProfile:
    return remove_noncands(new_loader(filename)[0], to_remove)

#pref_voting
#def p_profile(filename):
#    return creator.create_profile(filename)

##ALL ELECTION METHODS TAKE EITHER A FILENAME OR A PREFERENCE PROFILE AS INPUT
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Plurality 
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Plurality(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    elected = list(v.Plurality(profile = prof,tiebreak = tiebreak).election_states[-1].elected[0])[0]
    if not type(elected) is set:
        elected = set([elected])
    
    return elected
    
#-------------------------------------------------------------------------------------------------------------------------------------------------  
#IRV 
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def IRV(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    elected = list(v.IRV(profile = prof,tiebreak =tiebreak).election_states[-1].elected[0])[0]
    if not type(elected) is set:
        elected = set([elected])    
    return elected
        

#top-two IRV

def TopTwo(
    #filename: str,
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:  
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    if len(cands_to_keep)<2:
        return set([None])
    else:
        prof = process_cands(prof, cands_to_keep)
    
        elected = list(v.TopTwo(profile = prof,tiebreak = tiebreak).election_states[-1].elected[0])[0]
        if not type(elected) is set:
            elected = set([elected])

        return elected
        
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Borda methods - we use votekit
#--------------------------------------------------------------------------------------------------------------------------------------------------#

def Borda_PM(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None, #include UWI in this if we want to keep it. If we want to keep everyone feed in full list of candidates
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    max_score=len(prof.candidates)-1 ##this will be equal to len(non_UWI_cands)-1 if UWI not in cands_to_keep, and to len(cands_to_keep)-1 if UWI is in cands_to_keep
    ballots = prof.ballots
    el_scores= {c:0 for c in cands_to_keep}
    for i in range(1,len(prof.candidates)+1):
        bal = [b for b in ballots if len(b.ranking) == i]
        new_ballots = []

        for b in bal:
            cands_in_b = []
            for c in cands_to_keep:
                for y in b.ranking:
                    if c in y:
                        cands_in_b.append(c)
                        break
            not_in_b = [{c} for c in cands_to_keep if c not in cands_in_b]
            new_ballots.append(Ballot(ranking = list(b.ranking) + not_in_b, weight = b.weight))
        if new_ballots!=[]:
            vector = list(range(max_score,max_score-i,-1))+[0 for k in range(len(cands_to_keep)-i)] 
        
            p = PreferenceProfile(ballots = new_ballots)
            el = v.Borda(profile = p, score_vector = vector,tiebreak = tiebreak).election_states[0].scores
            for c in cands_to_keep:
                if c not in el:
                    el[c]=0
                el_scores[c]+=el[c]
    winning_score = max(el_scores.values())
    elected = set([c for c in cands_to_keep if el_scores[c]==winning_score])
    return elected
    
#Borda OM
def Borda_OM(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    max_score=len(prof.candidates)-1 
    ballots = prof.ballots
    el_scores= {c:0 for c in cands_to_keep}
    for i in range(1,len(prof.candidates)+1):
        bal = [b for b in ballots if len(b.ranking) == i]
        new_ballots = []

        for b in bal:
            cands_in_b = []
            for c in cands_to_keep:
                for y in b.ranking:
                    if c in y:
                        cands_in_b.append(c)
                        break
            not_in_b = [{c} for c in cands_to_keep if c not in cands_in_b]
            new_ballots.append(Ballot(ranking = list(b.ranking) + not_in_b, weight = b.weight))
        if new_ballots!=[]:
            vector = list(range(max_score,max_score-i,-1))+[max_score-i for k in range(len(cands_to_keep)-i)] 
            p = PreferenceProfile(ballots = new_ballots)
            el = v.Borda(profile = p, score_vector = vector,tiebreak=tiebreak).election_states[0].scores
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
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None 
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    max_score=len(prof.candidates)-1 
    ballots = prof.ballots
    el_scores= {c:0 for c in cands_to_keep}
    for i in range(1,len(prof.candidates)+1):
        bal = [b for b in ballots if len(b.ranking) == i]
        new_ballots = []
        for b in bal:
            cands_in_b = []
            for c in cands_to_keep:
                for y in b.ranking:
                    if c in y:
                        cands_in_b.append(c)
                        break
            not_in_b = [{c} for c in cands_to_keep if c not in cands_in_b]
            new_ballots.append(Ballot(ranking = list(b.ranking) + not_in_b, weight = b.weight))
        if new_ballots!=[]:
            vector = list(range(max_score,max_score-i,-1))+[(max_score-i)/2 for k in range(len(cands_to_keep)-i)] 
            p = PreferenceProfile(ballots = new_ballots)
            el = v.Borda(profile = p, score_vector = vector,tiebreak=tiebreak).election_states[0].scores
            for c in cands_to_keep:
                if c not in el:
                    el[c]=0
                el_scores[c]+=el[c]
    winning_score = max(el_scores.values())
    elected = set([c for c in cands_to_keep if el_scores[c]==winning_score])
    return elected

#top3 truncation using 3-2-1. converts to 2-1 if we are only keeping 2 candidates
def Top3Truncation(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    if len(prof.candidates)==0:
        return 'skipped'
    elif len(prof.candidates)==1:
        return prof.candidates[0]
    
    if len(prof.candidates)==2:
        vector = [2,1]
        
    else:
        vector = [3,2,1]+[0 for i in range(len(prof.candidates) -3)]
    elected = list(v.Borda(profile = prof, score_vector = vector,tiebreak=tiebreak).election_states[-1].elected[0])[0]
    if not type(elected) is set:
        elected = set([elected])
    
    return elected
    
    
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Condorcet methods - we use votekit
#--------------------------------------------------------------------------------------------------------------------------------------------------#

#regular Condorcet: returns Condorcet winner if there exists once, else returns set()
def Condorcet(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    
    if type(prof)==str:
        prof = v_profile(prof)

    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    elected = Smith(prof)
    if len(elected)>1:
        elected = set()
    return elected


#Smith: returns Smith set - custom code
def Smith(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    cands = prof.candidates
    cand_pairs = combinations(cands, 2)
    
    def head2head_count(cand_a: str, cand_b: str):
        count = 0
        bal = prof.ballots
        for b in bal:
            rank_list = b.ranking
            for s in rank_list:
                if cand_a in s:
                    count += b.weight
                    break
                elif cand_b in s:
                    break
        return count

    pairwise_dict = { a:{c:0 for c in cands if c!=a} for a in cands}
    for (a,c) in cand_pairs:
        if head2head_count(a,c)>head2head_count(c,a):##a beats c
            pairwise_dict[a][c] = 1
        elif head2head_count(a,c)==head2head_count(c,a): ##a and c are tied
            pairwise_dict[a][c] = 0.5
            pairwise_dict[c][a] = 0.5
        else:
            pairwise_dict[c][a] = 1 ##c beats a
    
    
    copeland_scores = {a: sum(pairwise_dict[a].values()) for a in cands}
    copeland_order = [a for (a,_) in sorted(copeland_scores.items(), key = lambda x: x[1], reverse = True)]
    max_copeland = copeland_scores[copeland_order[0]]
    first_non_smith = len(copeland_order)
    l = len(copeland_order)
    first_non_smith = 1
    while first_non_smith<l:
        if copeland_scores[copeland_order[first_non_smith]]!=max_copeland:
            break
        first_non_smith=first_non_smith+1
        
    while first_non_smith<l:
        lower_rows = [k for k in range(first_non_smith,l) if sum(pairwise_dict[copeland_order[k]][copeland_order[i]] for i in range(first_non_smith))!=0]##k is in this set if and only if kth candidate is at least tied with someone in the current smith set
        if lower_rows == []:
            break
        else:
            j = max(lower_rows)
            first_non_smith = max([i for i in range(j,l) if copeland_scores[copeland_order[i]]==copeland_scores[copeland_order[j]]])+1
    elected = set(copeland_order[:first_non_smith])

    return elected

#Smith Plurality
def Smith_Plurality(
    #filename: str
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    smith_set = Smith(prof, cands_to_keep)
    ##after-smith
    prof = process_cands(prof, smith_set)
    

    elected = list(v.Plurality(profile = prof,tiebreak=tiebreak).election_states[-1].elected[0])[0]
    if not type(elected) is set:
        elected = set([elected])
    
    return elected


#Smith-IRV
def Smith_IRV(
    #filename: str
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    smith_set = Smith(prof, cands_to_keep)
    ##after-smith
    prof = process_cands(prof, smith_set)
    

    elected = list(v.IRV(profile = prof,tiebreak=tiebreak).election_states[-1].elected[0])[0]
    if not type(elected) is set:
        elected = set([elected])
    
    return elected

#minimax: returns list of minimax winners
def Minimax(
    #filename: str
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    def head2head_count(cand_a: str, cand_b: str):
        count = 0
        bal = prof.ballots
        for b in bal:
            rank_list = b.ranking
            for s in rank_list:
                if cand_a in s:
                    count += b.weight
                    break
                elif cand_b in s:
                    break
        return count
    
    cands = [c for c in prof.candidates]
    defeat_margins={c:0 for c in cands}
    for c in cands:
        defeat_margins[c] = 0
        for y in cands:
            margin = head2head_count(y,c) - head2head_count(c,y)
            if margin> defeat_margins[c]:
                    defeat_margins[c] = margin
    elected = set([c for c in defeat_margins if defeat_margins[c]==min(defeat_margins.values())])         
    return elected
    

#Smith-minimax
def Smith_Minimax(
    #filename: str
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    smith_set = Smith(prof, cands_to_keep)

    ##after-smith
    prof = process_cands(prof, smith_set)

    def head2head_count(cand_a: str, cand_b: str):
        count = 0
        bal = prof.ballots
        for b in bal:
            rank_list = b.ranking
            for s in rank_list:
                if cand_a in s:
                    count += b.weight
                    break
                elif cand_b in s:
                    break
        return count
    
    cands = prof.candidates
    defeat_margins={c:0 for c in cands}
    for c in cands:
        defeat_margins[c] = 0
        for y in cands:
            margin = head2head_count(y,c) - head2head_count(c,y)
            if margin>defeat_margins[c]:
                    defeat_margins[c] = margin
    elected = set([x for x in defeat_margins if defeat_margins[x]==min(defeat_margins.values())])          
    
    return elected


#ranked pairs
def Ranked_Pairs(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    cands = prof.candidates

    def head2head_count(cand_a: str, cand_b: str):
        count = 0
        bal = prof.ballots
        for b in bal:
            rank_list = b.ranking
            for s in rank_list:
                if cand_a in s:
                    count += b.weight
                    break
                elif cand_b in s:
                    break
        return count
    
    victory_margins : dict = {}
    for c in cands:
        for y in cands:
            if ((c,y) not in victory_margins.keys()) and ((y,c) not in victory_margins.keys()):
                margin = head2head_count(c,y) - head2head_count(y,c)
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
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
    num_cands = len(prof.candidates)
    maj = sum(b.weight for b in prof.ballots)/2
    for i in range(num_cands):
        bal = prof.ballots
        for b in bal:
            b= Ballot(ranking = b.ranking[:i+1], weight = b.weight)
        el_scores = v.Borda(profile = prof, score_vector = [1 for k in range(i+1)],tiebreak=tiebreak).election_states[0].scores
        if max(el_scores.values())>maj:
            elected = set([c for c in el_scores if el_scores[c]==max(el_scores.values()) and c!="skipped"])
            break
    if elected == set():
        elected = set([c for c in el_scores if el_scores[c]==max(el_scores.values()) and c!="skipped"]) ##I'm not sure this can happen
    return elected
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#Approval
#--------------------------------------------------------------------------------------------------------------------------------------------------#
def Approval(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))

    prof = process_cands(prof, cands_to_keep)
    
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

def IRV_With_Explanation(
    prof: Union[PreferenceProfile, str],
    cands_to_keep: Optional[list] = None,
    tiebreak: Optional[str] = None
)-> set:
    if type(prof)==str:
        prof = v_profile(prof)
    
    if not cands_to_keep:
        cands_to_keep = prof.candidates
    if 'skipped' in cands_to_keep:## remove 'skipped' from cands_to_keep
        cands_to_keep = list(filter(lambda c: c != 'skipped', cands_to_keep))
    prof = process_cands(prof, cands_to_keep)
    
    election = str(v.IRV(profile=prof,tiebreak = tiebreak))

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