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



# from pref_voting.profiles_with_ties import ProfileWithTies
# from pref_voting.margin_based_methods import ranked_pairs as pv_rp
# from pref_voting.margin_based_methods import minimax as pv_mm
# from pref_voting.other_methods import bucklin as pv_buck


###########################################################
###########################################################
###### helper functions
###########################################################
###########################################################

## Reads preference profile in list, returns dataframe
def createBallotDF(list_profile):
    column_names=['ballot','Count']
    data=pd.DataFrame(columns = column_names)
    for k in range(1,len(list_profile)):
        if list_profile[k][0]=='0':
            break
        #print(k)
        first_space=list_profile[k].find(' ')
        count=int(list_profile[k][0:first_space])
        end=list_profile[k].find(' 0')
        ballot=list_profile[k][first_space+1:end+1]
        
        if '10 ' in ballot:
            ballot=ballot.replace('10 ','J ')
        if '11 ' in ballot:
            ballot=ballot.replace('11 ','K ')
        if '12 ' in ballot:
            ballot=ballot.replace('12 ','L ')
        if '13 ' in ballot:
            ballot=ballot.replace('13 ', 'M ')
        if '14 ' in ballot:
            ballot=ballot.replace('14 ', 'N ')
        if '15 ' in ballot:
            ballot=ballot.replace('15 ','O ')
        if '16 ' in ballot:
            ballot=ballot.replace('16 ','P ')
        if '17 ' in ballot:
            ballot=ballot.replace('17 ','Q ')
        if '18 ' in ballot:
            ballot=ballot.replace('18 ','R ')
        if '19 ' in ballot:
            ballot=ballot.replace('19 ','S ')
        if '20 ' in ballot:
            ballot=ballot.replace('20 ','T ')
        if '21 ' in ballot:
            ballot=ballot.replace('21 ','U ')
        if '22 ' in ballot:
            ballot=ballot.replace('22 ','V ')
        if '23 ' in ballot:
            ballot=ballot.replace('23 ','W ')
        if '24 ' in ballot:
            ballot=ballot.replace('24 ','X ')
        if '25 ' in ballot:
            ballot=ballot.replace('25 ','Y ')
        if '26 ' in ballot:
            ballot=ballot.replace('26 ','Z ')
        if '27 ' in ballot:
            ballot=ballot.replace('27 ','a ')
        if '28 ' in ballot:
            ballot=ballot.replace('28 ','b ')
        if '29 ' in ballot:
            ballot=ballot.replace('29 ','c ')
        if '30 ' in ballot:
            ballot=ballot.replace('30 ','d ')
        if '31 ' in ballot:
            ballot=ballot.replace('31 ','e ')
        if '32 ' in ballot:
            ballot=ballot.replace('32 ','f ')
        if '33 ' in ballot:
            ballot=ballot.replace('33 ', 'g ')
        if '34 ' in ballot:
            ballot=ballot.replace('34 ', 'h ')
        if '35 ' in ballot:
            ballot=ballot.replace('35 ','i ')
        if '36 ' in ballot:
            ballot=ballot.replace('36 ','j ')
        if '37 ' in ballot:
            ballot=ballot.replace('37 ','k ')
        if '38 ' in ballot:
            ballot=ballot.replace('38 ','l ')
        if '39 ' in ballot:
            ballot=ballot.replace('39 ','m ')
        if '40 ' in ballot:
            ballot=ballot.replace('40 ','n ')
        if '41 ' in ballot:
            ballot=ballot.replace('41 ','o ')
        if '42 ' in ballot:
            ballot=ballot.replace('42 ','p ')
        if '43 ' in ballot:
            ballot=ballot.replace('43 ', 'q ')
        if '44 ' in ballot:
            ballot=ballot.replace('44 ', 'r ')
        if '45 ' in ballot:
            ballot=ballot.replace('45 ','s ')
        if '46 ' in ballot:
            ballot=ballot.replace('46 ','t ')
        if '47 ' in ballot:
            ballot=ballot.replace('47 ','u ')
        if '48 ' in ballot:
            ballot=ballot.replace('48 ','v ')
        if '49 ' in ballot:
            ballot=ballot.replace('49 ','w ')
        if '50 ' in ballot:
            ballot=ballot.replace('50 ','x ')
        if '51 ' in ballot:
            ballot=ballot.replace('51 ','y ')
        if '52 ' in ballot:
            ballot=ballot.replace('52 ','z ')
        if '1 ' in ballot:
            ballot=ballot.replace('1 ','A ')
        if '2 ' in ballot:
            ballot=ballot.replace('2 ','B ')
        if '3 ' in ballot:
            ballot=ballot.replace('3 ','C ')
        if '4 ' in ballot:
            ballot=ballot.replace('4 ','D ')
        if '5 ' in ballot:
            ballot=ballot.replace('5 ','E ')
        if '6 ' in ballot:
            ballot=ballot.replace('6 ','F ')
        if '7 ' in ballot:
            ballot=ballot.replace('7 ','G ')
        if '8 ' in ballot:
            ballot=ballot.replace('8 ','H ')
        if '9 ' in ballot:
            ballot=ballot.replace('9 ','I ')
        

        while ' ' in ballot:
            ballot=ballot.replace(' ','')

        row={'Count':[float(count)], 'ballot':[ballot]}
        df2=pd.DataFrame(row)
        #data=data.append(df2, ignore_index=True)
        data = pd.concat([data, df2], ignore_index=True)
        
    return data


    
## unchecked
## used in IRV function
def truncate(number, digits) -> float: #truncates according to Scotland rules
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


##################################################################
##################################################################
##### election methods
##################################################################
##################################################################

###########################################################
## Adapted from Dave's Borda_PM code 
def Borda_PM(profile, num_cands):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cand_List1 = cand_names[:num_cands]
    
    #find candidates from profile
    # cand_List1=[] #make list of all candidates, only candidates listed in top two ranks (issue for cvis?)
    
    # for k in range(len(profile)):
    #     if profile.at[k,'ballot']!='':
    #         if profile.at[k,'ballot'][0] in cand_List1:
    #             pass
    #         else:
    #             cand_List1.append(profile.at[k,'ballot'][0])
    #     if len(profile.at[k,'ballot'])>1:
    #         if profile.at[k,'ballot'][1] in cand_List1:
    #             pass
    #         else:
    #             cand_List1.append(profile.at[k,'ballot'][1])
    # #get number of candidates
    # num_cands = len(cand_List1)
    
    max_score = num_cands - 1
    
    #rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    #cands = pd.unique(pref_profile[rank_columns].values.ravel()).tolist()
    #cands = [cand for cand in cands if cand != 'skipped']
    
    cand_scores = {cand: 0 for cand in cand_List1}
    for k in range(len(profile)):
        count = profile.at[k, 'Count']
        curBal= profile.at[k, 'ballot']
        for i in range(0,len(curBal)):
            
            candidate = curBal[i]
            if candidate in cand_List1:
                cand_scores[candidate] += (max_score - (i )) * count
            else:
                print("Candidate in ballot that is not in candidate list")
    # print(cand_scores)
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return winners

def Borda_OM(profile, num_cands):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cand_List1 = cand_names[:num_cands]
    
    # #find candidates from profile
    # cand_List1=[] #make list of all candidates, only candidates listed in top two ranks (issue for cvis?)
    
    # for k in range(len(profile)):
    #     if profile.at[k,'ballot']!='':
    #         if profile.at[k,'ballot'][0] in cand_List1:
    #             pass
    #         else:
    #             cand_List1.append(profile.at[k,'ballot'][0])
    #     if len(profile.at[k,'ballot'])>1:
    #         if profile.at[k,'ballot'][1] in cand_List1:
    #             pass
    #         else:
    #             cand_List1.append(profile.at[k,'ballot'][1])
    # #get number of candidates
    # num_cands = len(cand_List1)
    
    max_score = num_cands - 1
    
    #rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    #cands = pd.unique(pref_profile[rank_columns].values.ravel()).tolist()
    #cands = [cand for cand in cands if cand != 'skipped']
    
    cand_scores = {cand: 0 for cand in cand_List1}
    for k in range(len(profile)):
        count = profile.at[k, 'Count']
        curBal= profile.at[k, 'ballot']
        for i in range(0,len(curBal)):
            
            candidate = curBal[i]
            if candidate in cand_List1:
                cand_scores[candidate] += (max_score - (i )) * count
            else:
                print("Candidate in ballot that is not in candidate list")
        
        # add score for all candidates not on ballot
        for cand in cand_List1:
            if cand not in curBal:
                cand_scores[cand] += (max_score - len(curBal)) * count
        
    # print(cand_scores)
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return winners

def Borda_AVG(profile, num_cands):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cand_List1 = cand_names[:num_cands]
    
    # #find candidates from profile
    # cand_List1=[] #make list of all candidates, only candidates listed in top two ranks (issue for cvis?)
    
    # for k in range(len(profile)):
    #     if profile.at[k,'ballot']!='':
    #         if profile.at[k,'ballot'][0] in cand_List1:
    #             pass
    #         else:
    #             cand_List1.append(profile.at[k,'ballot'][0])
    #     if len(profile.at[k,'ballot'])>1:
    #         if profile.at[k,'ballot'][1] in cand_List1:
    #             pass
    #         else:
    #             cand_List1.append(profile.at[k,'ballot'][1])
    # #get number of candidates
    # num_cands = len(cand_List1)
    
    max_score = num_cands - 1
    
    #rank_columns = [col for col in pref_profile.columns if col.startswith('rank')]
    #cands = pd.unique(pref_profile[rank_columns].values.ravel()).tolist()
    #cands = [cand for cand in cands if cand != 'skipped']
    
    cand_scores = {cand: 0 for cand in cand_List1}
    for k in range(len(profile)):
        count = profile.at[k, 'Count']
        curBal= profile.at[k, 'ballot']
        for i in range(0,len(curBal)):
            
            candidate = curBal[i]
            if candidate in cand_List1:
                cand_scores[candidate] += (max_score - (i )) * count
            else:
                print("Candidate in ballot that is not in candidate list")
        
        # add score for all candidates not on ballot
        missing_cand_num = num_cands - len(curBal) 
        avg_points = (missing_cand_num - 1)/2
        for cand in cand_List1:
            if cand not in curBal:
                cand_scores[cand] += avg_points * count
        
    # print(cand_scores)
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return winners

###########################################################


def IRV(frame3, cand_num): #program to run STV election, from Adam
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    hopefuls = cand_names[:cand_num]

    frame2 = frame3.copy(deep=True)
    """Inputs election, n=number of candidates, S=number of seats=1.  Returns winner, 
    as a list with a single entry"""
    #Quota is floor of number of ballots divided by (S+1), plus 1
    winners=[]
    # hopefuls=[]
    eliminatedCand=[]
    elimFrames={}
    tempWinners={}
    quota=math.floor(sum(frame2['Count'])/(2))+1
    
# Adam's method of extracting candidates from ballots
#     list1=[]
#     for k in range(len(frame2)):
#         if frame2.at[k,'ballot']!='':
#             if frame2.at[k,'ballot'][0] in list1:
#                 pass
#             else:
#                 list1.append(frame2.at[k,'ballot'][0])
#         if len(frame2.at[k,'ballot'])>1:
#             if frame2.at[k,'ballot'][1] in list1:
#                 pass
#             else:
#                 list1.append(frame2.at[k,'ballot'][1])
#         if len(frame2.at[k,'ballot'])>2:
#             if frame2.at[k,'ballot'][2] in list1:
#                 pass
#             else:
#                 list1.append(frame2.at[k,'ballot'][2])
#         if len(frame2.at[k,'ballot'])>3:
#             if frame2.at[k,'ballot'][3] in list1:
#                 pass
#             else:
#                 list1.append(frame2.at[k,'ballot'][3])
# #     for k in range(len(frame2)):
# #         if frame2.at[k,'ballot']!='':
# #             if frame2.at[k,'ballot'][0] in list1:
# #                 pass
# #             else:
# #                 list1.append(frame2.at[k,'ballot'][0])
# #     if len(list1)!=n:
# #         print("length of list1 is not equal to number of candidates n. Length of list1 = " +str(len(list1)) + 
# #              " and n = " + str(n))
#     cand_dict={}
#     for i in range(len(list1)):#range(n)
#         cand_dict[i]=list1[i]
#         hopefuls.append(list1[i]) #create initial list of hopefuls
 
    #Get each candidate's initial number of votes this round
    vote_counts={}
    
    for k in range(len(frame2)):
        if frame2.at[k,'ballot']!='':
            if frame2.at[k,'ballot'][0] in vote_counts.keys():
                vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
            else:
                vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']
    
    max_count=max(vote_counts.values())
    while len(winners)<1:
        
        max_count=max(vote_counts.values())
        #somebody is elected and we have to transfer their votes
        if max_count>=quota:
            #There might be multiple people elected this round; save them as a sorted dictionary
            votes_for_winners={k:vote_counts[k] for k in vote_counts.keys() if vote_counts[k]>=quota }
            votes_for_winners=dict(sorted(votes_for_winners.items(),key=lambda x: x[1], reverse=True))
            
            #If we try to elect too many people, need to drop someone who surpassed quota
            if len(winners)+len(votes_for_winners)>1:
                
                for k in range(len(winners)+len(votes_for_winners)-1):
                    winners.append(list(votes_for_winners.keys())[k])
            
            else:
                winners=winners+list(votes_for_winners.keys())
                for cand in winners:
                    if cand in hopefuls:
                        hopefuls.remove(cand) #remove winner from hopefuls list
                
                while len(votes_for_winners)>0:
                    
                    cand=list(votes_for_winners.keys())[0]
    
                    if cand not in winners:
                        winners.append(cand)
                        hopefuls.remove(cand)
                    if len(winners)==1:
                        return winners
                    #print("cand elected", cand)
                    
                    weight=truncate((vote_counts[cand]-quota)/vote_counts[cand],5) #calculate weight for transfer
                    for k in range(len(frame2)): 
                        if frame2.at[k,'ballot']!='':
                            if frame2.at[k,'ballot'][0]==cand: #make fractional votes
                                frame2.at[k,'Count']=frame2.at[k,'Count']*weight
                                for x in winners:
                                    if x in frame2.at[k,'ballot']: #remove winner from ballots
                                        frame2.at[k,'ballot']=frame2.at[k,'ballot'].replace(x,'')
                            else: #remove winner from ballot
                                if cand in frame2.at[k,'ballot']:
                                     frame2.at[k,'ballot']=frame2.at[k,'ballot'].replace(cand,'')
                    votes_for_winners.pop(cand)
                    vote_counts={}
                    
                    for k in range(len(frame2)): #calculate new vote counts
                        if frame2.at[k,'ballot']!='':
                            if frame2.at[k,'ballot'][0] in vote_counts.keys():
                                vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                            else:
                                vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']

                    votes_for_winners={k:vote_counts[k] for k in vote_counts.keys() if vote_counts[k]>=quota }
                    votes_for_winners=dict(sorted(votes_for_winners.items(),key=lambda x: x[1], reverse=True))
                    for cand in votes_for_winners.keys():
                        if cand not in winners:
                            winners.append(cand)
                            hopefuls.remove(cand)
                    if len(winners)==1:
                        return winners
                    frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
        #nobody is elected by surpassing quota, but the number
        #of candidates left equals 1
        elif len(hopefuls)+len(winners)==1:
            return winners+hopefuls
        
        #remove weakest cand and transfer their votes with weight one
        else:
            min_count=min(i for i in vote_counts.values() if i>0)
            count=0
            for votes in vote_counts:
                if votes==min_count:
                    count+=1
            if count>1: #this basically never happens, but it is here just in case
                print("tie in candidate to remove")
                return

            eliminated_cand = list(vote_counts.keys())[list(vote_counts.values()).index(min_count)] 
            
            elimFrames[len(eliminatedCand)]=frame2.copy(deep=True) #save pref sched data at this level
            tempWinners[len(eliminatedCand)]=copy.deepcopy(winners) #save winners at this level
            eliminatedCand.append(eliminated_cand)
            if eliminated_cand in hopefuls:
                hopefuls.remove(eliminated_cand)
            
            for k in range(len(frame2)): #remove eliminated candidate from ballots
                if eliminated_cand in frame2.iloc[k]['ballot']:
                    frame2.at[k,'ballot']=frame2.at[k,'ballot'].replace(eliminated_cand,'')
            for k in range(len(frame2)):
                if frame2.at[k,'ballot']=='':
                    frame2.drop(k)
            vote_counts={} 
            for k in range(len(frame2)): #calculate new vote counts
                if frame2.at[k,'ballot']!='':
                    if frame2.at[k,'ballot'][0] in vote_counts.keys():
                        vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                    else:
                        vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']
                        
            max_count=max(vote_counts.values())
            if len(hopefuls)+len(winners)==1:
                return winners+hopefuls
            frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
    return winners #as a list--in this case, should return a list of just one winner

def minimax(profile, cand_num):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    ##### compute H2H margins
    margins = np.zeros((cand_num, cand_num))
    H2H_list = []
    
    for c1 in range(cand_num):
        for c2 in range(c1+1, cand_num):
            c1_let = cand_names[c1]
            c2_let = cand_names[c2]
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
            
            if margin > 0.0:
                H2H_list.append([(c1, c2), margin])
            else:
                H2H_list.append([(c2, c1), -1*margin])
    
    worst_loss = margins.min(axis=1)
    # win_indx = np.where(worst_loss == max(worst_loss))[0][0]
    # return [cand_names[win_indx]]
    win_indxs = [i for i in range(cand_num) if worst_loss[i] == max(worst_loss)]
    return [cand_names[indx] for indx in win_indxs]
    
def ranked_pairs(profile, cand_num):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    ##### compute H2H margins
    margins = np.zeros((cand_num, cand_num))
    H2H_list = []
    
    for c1 in range(cand_num):
        for c2 in range(c1+1, cand_num):
            c1_let = cand_names[c1]
            c2_let = cand_names[c2]
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
            return [cand_names[c1]]
    
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
        if loser not in is_worse[winner]:
            ## update winner's is_better
            is_better[winner] = is_better[winner].union({loser})
            is_better[winner] = is_better[winner].union(is_better[loser])
            if len(is_better[winner]) == cand_num-1:
                return [cand_names[winner]]
                
            ## update everyone better than winner
            for cand in is_worse[winner]:
                is_better[cand] = is_better[cand].union(is_better[winner])
                if len(is_better[cand]) == cand_num-1:
                    return [cand_names[cand]]
                
            ## update loser's is_worse
            is_worse[loser] = is_worse[loser].union({winner})
            is_worse[loser] = is_worse[loser].union(is_worse[winner])
            ## update everyone worse than loser
            for cand in is_better[loser]:
                is_worse[cand] = is_worse[cand].union(is_worse[loser])

# should be good, not checked against prefvoting
def bucklin(profile, cand_num):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:cand_num]
    
    # Initialize scores for candidates to 0
    scores = {cand: 0.0 for cand in cands}
    threshold = profile['Count'].sum() / 2  # Majority threshold
    
    # print(scores)
    for round_indx in range(cand_num):
        # update scores for the current round
        for k in range(len(profile)):
            ballot = profile.at[k, 'ballot']
            if len(ballot) > round_indx:
                cand = ballot[round_indx]
                scores[cand] += profile.at[k, 'Count']
    
    # rank_columns = [col for col in profile.columns if col.startswith('rank')]
    # for round_idx in range(1, len(rank_columns) + 1):
    #     # Update scores for the current round
    #     for k in range(len(profile)):
    #         count = profile.at[k, 'Count']
    #         for i in range(1, round_idx + 1):
    #             rank_col = f'rank{i}'
    #             candidate = profile.at[k, rank_col]
    #             if candidate in cands:
    #                 scores[candidate] += count

        # print(scores)
        # Check if any candidate has surpassed the majority threshold
        surpassing_candidates = {cand: score for cand, score in scores.items() if score > threshold}
        if surpassing_candidates:
            max_score = max(surpassing_candidates.values())
            winners = [cand for cand, score in surpassing_candidates.items() if score == max_score]
            return winners  # Return the candidate(s) with the most votes above the threshold

    # At the end of all rounds, if no majority is reached
    max_score = max(scores.values())
    winners = [cand for cand, score in scores.items() if score == max_score]
    return winners

# should be good, not checked against prefvoting
def plurality(profile, cand_num):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    cands = cand_names[:cand_num]
    # Initialize scores for candidates to 0
    scores = {cand: 0.0 for cand in cands}
    
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        scores[ballot[0]] += profile.at[k, 'Count']
    
    # Winner has most first place votes
    max_score = max(scores.values())
    winners = [cand for cand, score in scores.items() if score == max_score]
    return winners

# compute smith set, create new ballot profile restricting to smith set
def restrict_to_smith(profile, cand_num):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    ##### compute H2H margins
    margins = np.zeros((cand_num, cand_num))
    H2H_list = []
    
    for c1 in range(cand_num):
        for c2 in range(c1+1, cand_num):
            c1_let = cand_names[c1]
            c2_let = cand_names[c2]
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
            
            if margin > 0.0:
                H2H_list.append([(c1, c2), margin])
            else:
                H2H_list.append([(c2, c1), -1*margin])
    
    ## calculate smith set
    copeland_scores = {}
    for i in range(cand_num):
        score = 0.0
        for j in range(cand_num):
            if i != j:
                if margins[i,j]>0:
                    score += 1
                elif margins[i,j] == 0:
                    score += 0.5
        copeland_scores[i] = score

    ## at this point just the copeland set
    smith_set = [i for i in range(cand_num) if copeland_scores[i]==max(copeland_scores.values())]
     
    ## add iteratively add candidates who beat someone in the set
    finished = False
    while not finished:
        finished = True
        for i in smith_set:
            for j in range(cand_num):
                if j not in smith_set and margins[j, i] >= 0:
                    smith_set.append(j)
                    finished = False
    
    smith_set_lets = [cand_names[i] for i in smith_set]
    
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
            
    ## construct new ballot profile
    column_names=['ballot','Count']
    new_profile=pd.DataFrame(columns = column_names)
                
    for ballot in new_ballots:
        row={'Count':[float(new_ballots[ballot])], 'ballot':[ballot]}
        single_df=pd.DataFrame(row)
        #data=data.append(df2, ignore_index=True)
        new_profile = pd.concat([new_profile, single_df], ignore_index=True)
        
    return smith_set_lets, new_profile

def smith_irv(profile, cand_num):
    smith_set, new_profile = restrict_to_smith(profile, cand_num)
    return IRV(new_profile, cand_num)

def smith_minimax(profile, cand_num):
    smith_set, new_profile = restrict_to_smith(profile, cand_num)
    return minimax(new_profile, cand_num)

def plurality_runoff(profile, cand_num):
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
    cands = cand_names[:cand_num]
    # Initialize scores for candidates to 0
    scores = {cand: 0.0 for cand in cands}
    
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        scores[ballot[0]] += profile.at[k, 'Count']
    
    # keep two candidates with highest scores
    cands.sort(key=lambda cand: scores[cand], reverse = True)
    second_round_cands = cands[:2]
    
    c1, c2 = second_round_cands
    scores = {cand: 0.0 for cand in second_round_cands}
    for k in range(len(profile)):
        ballot = profile.at[k, 'ballot']
        if c1 in ballot and c2 in ballot:
            if ballot.find(c1)<ballot.find(c2):
                scores[c1] += profile.at[k, 'Count']
            else:
                scores[c2] += profile.at[k, 'Count']
        elif c1 in ballot:
            scores[c1] += profile.at[k, 'Count']
        elif c2 in ballot:
            scores[c2] += profile.at[k, 'Count']
    
    # Winner has most first place votes
    max_score = max(scores.values())
    winners = [cand for cand, score in scores.items() if score == max_score]
    return winners
    


########################################################
##### Execute code
########################################################






###################################
##### Compare my functions to results file
###################################

region_name = 'scotland'

pref_folder_base = '../../raw_data/preference_profiles/'
base_name = pref_folder_base + region_name

current_folder = '../../results/current/'
current_results_path = current_folder+region_name

current_results = pd.read_csv(current_results_path+'.csv')
lxn_list = list(current_results['file'])

lxn_names = []
for folder_name in os.listdir(base_name):
    for file_name in os.listdir(base_name+'/'+folder_name):
        file_path = base_name+'/'+folder_name+'/'+file_name
        
        if folder_name+'/'+file_name in lxn_list:
            current_result_indx = lxn_list.index(folder_name+'/'+file_name)
        else:
            # ward_word = file_name[file_name.find('ward'):file_name.find('ward')+7]
            # current_result_indx = [i for i in range(len(current_results)) if (folder_name in lxn_list[i]) and (ward_word in lxn_list[i])][0]
            continue
        
        lxn_names.append(file_path)   
        # print(file_path)
        
        # if len(lxn_names)<75:
        #     continue
    
        sys.stdout.write('\r')
        sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
        sys.stdout.flush()
        
        File=open(file_path,'r', encoding='utf-8')
        #print(str(filename))
        lines=File.readlines()

        first_space=lines[0].find(' ')
        num_cands=int(lines[0][0:first_space])
        if num_cands>52:
            print("Cannot handle this many candidates in election " + str(file_name) + ".  Has " + 
                  str(num_cands) + " candidates.")
            continue
            
        data = createBallotDF(lines)
        
        cand_names = lines[-num_cands:]
        cand_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                      'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                      'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        cand_name_dict = {}
        for i in range(num_cands):
            cand_name_dict[cand_letters[i]] = cand_names[i][:-1]

        #######################################
        ##### check election data
        #######################################
        if num_cands != current_results.at[current_result_indx, 'numCands']:
            print('#############################')
            print('Different number of candidates')
            print(num_cands, current_results.at[current_result_indx, 'numCands'])
            print(folder_name +'/' + file_name)
            print('#############################')
            
        
        my_win_let = plurality(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'plurality']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = plurality(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'plurality'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners plurality')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')
        
        my_win_let = IRV(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'IRV']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = IRV(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'IRV'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners IRV')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')
            
        my_win_let = Borda_PM(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'borda-pm']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = Borda_PM(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'borda-pm'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners Borda PM')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')
        
        my_win_let = Borda_OM(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'borda-om-no-uwi']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = Borda_OM(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'borda-om-no-uwi'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners Borda OM')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')
            # print(breakhere)

        my_win_let = Borda_AVG(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'borda-avg-no-uwi']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = Borda_AVG(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'borda-avg-no-uwi'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners Borda AVG')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')

        my_win_let = minimax(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'minimax']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = minimax(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'minimax'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners minimax')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')

        my_win_let = smith_irv(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'smith_irv']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = smith_irv(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'smith_irv'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners Smith IRV')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')
            
        my_win_let = smith_minimax(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'smith-minimax']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = smith_minimax(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'smith-minimax'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners Smith minimax')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')

        my_win_let = ranked_pairs(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'ranked-pairs']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = ranked_pairs(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'ranked-pairs'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners Ranked Pairs')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')

        my_win_let = bucklin(data, num_cands)[0]
        my_win = cand_name_dict[my_win_let]
        cr_win = current_results.at[current_result_indx, 'bucklin'][2:-2]
        if my_win != cr_win:
            print('#############################')
            print('Different winners Bucklin')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')

        my_win_let = plurality_runoff(data, num_cands)
        my_win = [cand_name_dict[x] for x in my_win_let]
        cr_win = current_results.at[current_result_indx, 'top-two']
        cr_win = cr_win.split("'")
        cr_win = [x for x in cr_win if '(' in x]
        if set(my_win) != set(cr_win):
        # my_win_let = plurality_runoff(data, num_cands)[0]
        # my_win = cand_name_dict[my_win_let]
        # cr_win = current_results.at[current_result_indx, 'top-two'][2:-2]
        # if my_win != cr_win:
            print('#############################')
            print('Different winners plurality runoff')
            print(my_win)
            print(cr_win)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')
            
        my_smith, new_profile = restrict_to_smith(data, num_cands)
        my_smith = [cand_name_dict[x] for x in my_smith]
        cr_smith = current_results.at[current_result_indx, 'smith']
        cr_smith = cr_smith.split("'")
        cr_smith = [x for x in cr_smith if '(' in x]
        if set(my_smith) != set(cr_smith):
            print('#############################')
            print('Different Smith sets')
            print(my_smith)
            print(cr_smith)
            print(folder_name +'/' + file_name)
            print(num_cands)
            print('#############################')
            # print(breakhere)









