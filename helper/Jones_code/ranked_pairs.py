import csv
import numpy as np
import random as rand
from itertools import combinations
import os
import sys


from pref_voting.margin_based_methods import ranked_pairs
from pref_voting.profiles_with_ties import ProfileWithTies



def get_ballots(name):
    bottom=False
    with open(name, encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        for row in csv_reader:
            ## First row contains information about number of candidates and seats
            if line_count == 0:
                indx = row[0].index(' ')
                cand_num = int(row[0][:indx])
                seat_num = int(row[0][indx:])
                ballots = {}
                
                    
            if row[0][0]=='0':
                if len(row[0])==1 or row[0][1]!='.':
                    bottom = True
                
            ## Each row has number of votes, list of candidates, and then 0
            if line_count>0 and not bottom:
                ballot_str = row[0]
                indx = ballot_str.index(' ')
                ballot_num = float(ballot_str[:indx])
                ballot_list = []
                for x in ballot_str[indx:].split():
                    if x !='0':
                        ballot_list.append(int(x))
                ballot = tuple(ballot_list)
                if ballot in ballots:
                    ballots[ballot] += ballot_num
                else:
                    ballots[ballot] = ballot_num

        
            line_count += 1
    
    ## return dictionary of ballots and number of candidates and seats
    return ballots, cand_num, seat_num





def rp_lxn(ballots, cand_num, seat_num):
    ##### compute H2H margins
    margins = np.zeros((cand_num, cand_num))
    H2H_list = []
    
    for c1 in range(1, cand_num+1):
        for c2 in range(c1+1, cand_num+1):
            # number of votes c1 gets over c2 in H2H
            margin = 0
            for ballot, count in ballots.items():
                ## ballot ranks both c1 and c2
                if c1 in ballot and c2 in ballot:
                    for cand in ballot:
                        if cand == c1:
                            margin += count
                            break
                        elif cand == c2:
                            margin -= count
                            break
                ## ballot only ranks c1       
                elif c1 in ballot:
                    margin += count
                ## ballot only ranks c2
                elif c2 in ballot:
                    margin -= count
            
            margins[c1-1, c2-1] = margin
            margins[c2-1, c1-1] = -1*margin
            
            if margin > 0.0:
                H2H_list.append([(c1, c2), margin])
            else:
                H2H_list.append([(c2, c1), -1*margin])
    
    
    ##### check for condorcet winner
    for c1 in range(cand_num):
        winner = True
        for c2 in range(cand_num):
            if margins[c1, c2] < 0.0:
                winner = False
                break
        if winner:
            return c1+1, True
    
    ##### run the ranked pairs algorithm
    H2H_list.sort(key=lambda x: x[1], reverse=True)
    
    # print(margins)
    # print(H2H_list)
    
    is_better = [set() for _ in range(cand_num)]
    is_worse = [set() for _ in range(cand_num)]
    
    for pair in H2H_list:
        winner = pair[0][0]
        loser = pair[0][1]
        
        ## this edge does not create a cycle, is added
        if loser not in is_worse[winner-1]:
            ## update winner's is_better
            is_better[winner-1] = is_better[winner-1].union({loser})
            is_better[winner-1] = is_better[winner-1].union(is_better[loser-1])
            if len(is_better[winner-1]) == cand_num-1:
                return winner, False
                
            ## update everyone better than winner
            for cand in is_worse[winner-1]:
                is_better[cand-1] = is_better[cand-1].union(is_better[winner-1])
                if len(is_better[cand-1]) == cand_num-1:
                    return cand, False
                
            ## update loser's is_worse
            is_worse[loser-1] = is_worse[loser-1].union({winner})
            is_worse[loser-1] = is_worse[loser-1].union(is_worse[winner-1])
            ## update everyone worse than loser
            for cand in is_better[loser-1]:
                is_worse[cand-1] = is_worse[cand-1].union(is_worse[loser-1])





# non_cond_list = ['../preference_profiles/scotland/aberdeenshire22/Ward10-WestGarioch_preferenceprofile_v0001_ward-10-west-garioch_06052022_172124.csv', '../preference_profiles/scotland/angus12-ballots/ForfarandDistrict_angus12-03.csv', '../preference_profiles/scotland/angus22/Ward3-ForfarandDistrict_ward3.csv', '../preference_profiles/scotland/argyll22/Ward2-KintyreandtheIslands_ward2.csv', '../preference_profiles/scotland/dumgal12-ballots/AnnandaleNorthWard_dumgal12-12.csv', '../preference_profiles/scotland/dumgal22/Ward3-DeeandGlenkens_ward3.csv', '../preference_profiles/scotland/fife12-ballots/GlenrothesCentralAndThorntonWard_fife12-16.csv', '../preference_profiles/scotland/glasgow2007 preflib/govan_govan.csv', '../preference_profiles/scotland/n-lanarks17-ballots/Ward4-CumbernauldEast_n-lanarks17-004.csv', '../preference_profiles/scotland/renfs12-ballots/7.JohnstoneSouthElderslie&HowwoodWard_renfs12-07.csv', '../preference_profiles/scotland/sc-borders12-ballots/JedburghandDistrictWard_sc-borders12-09.csv', '../preference_profiles/scotland/w-duns22/Ward2-Leven_west dunbartonshire,2022,ward 2.csv']
# test_list = ['..\preference_profiles\scotland\eilean-siar22\Ward3UibhistaTuath_ward_03_preferenceprofile.csv']

# for file_path in test_list:
#     print('#############################')
#     print(file_path)
#     print('#############################')
#     # ballots, cand_num, seat_num = get_ballots('../preference_profiles/scotland/aberdeen2012/Ward1-Dyce-Bucksburn-Danestone_aberdeen12-01.csv')
#     ballots, cand_num, seat_num = get_ballots(file_path)
    
#     winner, cond_win = rp_lxn(ballots, cand_num, seat_num)
#     print(winner, cond_win)
            
    
#     rankings = []
#     rcounts = []
#     for ballot, count in ballots.items():
#         rcounts.append(count)
#         ranking = {}
#         for indx, cand in enumerate(ballot):
#             ranking[cand] = indx+1
#         for cand in range(1, cand_num+1):
#             if cand not in ballot:
#                 ranking[cand] = len(ballot)+1
#         rankings.append(ranking)
    
#     pv_prof = ProfileWithTies(rankings, rcounts)
#     pv_rc_win = ranked_pairs(pv_prof)
#     print(pv_rc_win)

#     mg = pv_prof.margin_graph()
#     print(mg.margin_matrix)
#     print(mg.edges)





lxn_names = []
lxn_diffs = []

base_name = '../../raw_data/preference_profiles/scotland'
for folder_name in os.listdir(base_name):
    for file_name in os.listdir(base_name+'/'+folder_name):
        file_path = base_name+'/'+folder_name+'/'+file_name
        lxn_names.append(file_path)
        
        sys.stdout.write('\r')
        sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
        sys.stdout.flush()
        
        
        ballots, cand_num, seat_num = get_ballots(file_path)
        
        winner, cond_win = rp_lxn(ballots, cand_num, seat_num)
                
        
        rankings = []
        rcounts = []
        for ballot, count in ballots.items():
            rcounts.append(count)
            ranking = {}
            for indx, cand in enumerate(ballot):
                ranking[cand] = indx+1
            for cand in range(1, cand_num+1):
                if cand not in ballot:
                    ranking[cand] = len(ballot)+1
            rankings.append(ranking)
        
        pv_prof = ProfileWithTies(rankings, rcounts)
        pv_rc_win = ranked_pairs(pv_prof)

        if winner != pv_rc_win[0]:
            lxn_diffs.append([file_name, winner, pv_rc_win[0]])
        

















# lxn_names = []
# condorcet = []
# non_condorcet = []

# base_name = '../preference_profiles/scotland'
# for folder_name in os.listdir(base_name):
#     for file_name in os.listdir(base_name+'/'+folder_name):
#         file_path = base_name+'/'+folder_name+'/'+file_name
#         lxn_names.append(file_path)
        
#         sys.stdout.write('\r')
#         sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
#         sys.stdout.flush()
        
#         # ballots, cand_num, seat_num = get_ballots('../preference_profiles/scotland/aberdeen2012/Ward1-Dyce-Bucksburn-Danestone_aberdeen12-01.csv')
#         ballots, cand_num, seat_num = get_ballots(file_path)
        
#         ##### compute H2H margins
#         margins = np.zeros((cand_num, cand_num))
        
#         for c1 in range(1, cand_num+1):
#             for c2 in range(c1+1, cand_num+1):
#                 # number of votes c1 gets over c2 in H2H
#                 margin = 0
#                 for ballot, count in ballots.items():
#                     ## ballot ranks both c1 and c2
#                     if c1 in ballot and c2 in ballot:
#                         for cand in ballot:
#                             if cand == c1:
#                                 margin += count
#                                 break
#                             elif cand == c2:
#                                 margin -= count
#                                 break
#                     ## ballot only ranks c1       
#                     elif c1 in ballot:
#                         margin += count
#                     ## ballot only ranks c2
#                     elif c2 in ballot:
#                         margin -= count
                
#                 margins[c1-1, c2-1] = margin
#                 margins[c2-1, c1-1] = -1*margin
        
        
#         ##### check for condorcet winner
#         cond_win = False
#         for c1 in range(cand_num):
#             winner = True
#             for c2 in range(cand_num):
#                 if margins[c1, c2] < 0.0:
#                     winner = False
#                     break
#             if winner:
#                 cond_win = True
#                 condorcet.append(file_path)
#                 break
        
#         if not cond_win:
#             non_condorcet.append(file_path)











