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



## LNH type 1 (Truncate at L)
def truncBalAtL(ballot, winner, loser):
    """inputs ballot and a loser, and truncates the ballot after the loser"""
    if loser in ballot:
        return ballot[:ballot.index(loser)+1], True
    else:
        return ballot, False

## LNH type 2 (Truncate at W)
def truncBalAtW(ballot, winner, loser):
    """inputs ballot, winner, and loser"""
    """if loser is ranked above winner, truncates the ballot after the winner"""
    # if winner in ballot:
    if (loser in ballot) and (winner in ballot) and (ballot.find(loser)<ballot.find(winner)):
        return ballot.split(winner, 1)[0], True
    else:
        return ballot, False

## LNH type 3/Burying (Bury W)    
def buryWinBal(ballot, winner, loser):
    """inputs ballot, winner, and loser"""
    """if loser is ranked above winner, remove winner from ballot"""
    if (loser in ballot) and (winner in ballot) and (ballot.find(loser)<ballot.find(winner)):
        return ballot.split(winner)[0]+ballot.split(winner)[1], True
    else:
        return ballot, False
    
## LNH type 4 (W hurting self with lower rankings)
def boostLinBal(ballot, winner, loser):    
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
    
## compromise anomaly (move L to top if L ranked above W)
def LtoTop(ballot, winner, loser):
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
    

