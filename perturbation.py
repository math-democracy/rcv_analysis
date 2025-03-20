#required
from typing import Optional, Union
import networkx as nx
from itertools import combinations
import random
import math
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

##naive method of perturbing a profile by swapping randomly chosen consecutive candidates in a certain proportion of ballots
def swap_perturb(
        prof: PreferenceProfile,
        threshold: float = 0.1,
        )-> PreferenceProfile:
    ballots = prof.ballots
    new_ballots = []
    for i in range(len(ballots)):
        bal = prof.ballots[i]
        
        if len(bal.ranking)==1:
            new_ballots.append(bal)
        else:
            new_ranking = []
            swap_index = random.sample(range(1,len(bal.ranking)),1)[0]
            for j in range(swap_index-1):
                new_ranking.append(bal.ranking[j])
            new_ranking.append(bal.ranking[swap_index])
            new_ranking.append(bal.ranking[swap_index-1])
            for j in range(swap_index+1,len(bal.ranking)):
                new_ranking.append(bal.ranking[j])
            new_ballots = new_ballots+[Ballot(ranking=new_ranking,weight=threshold*bal.weight),Ballot(ranking=bal.ranking,weight=(1-threshold)*bal.weight)]

    new_prof = PreferenceProfile(ballots = new_ballots)
    return new_prof



