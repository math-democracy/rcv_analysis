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


## Reads through all data files and applies the specified search
def LNH_search_shell(anomaly_search, vote_method, mod_ballot_method):
    lxn_names = []
    anomaly_lxns = []
    
    base_name = '../../raw_data/preference_profiles/scotland'

    for folder_name in os.listdir(base_name):
    # for folder_name in ['aberdeenshire22']:
        for file_name in os.listdir(base_name+'/'+folder_name):
            file_path = base_name+'/'+folder_name+'/'+file_name
            # if len(file_path)>180:
            #     print(file_path)
            #     continue
            
            lxn_names.append(file_path)   
            # print(file_path)
        
            sys.stdout.write('\r')
            sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
            sys.stdout.flush()
            
            File=open(file_path,'r')
            #print(str(filename))
            lines=File.readlines()

            first_space=lines[0].find(' ')
            num_cands=int(lines[0][0:first_space])
            if num_cands>52:
                print("Cannot handle this many candidates in election " + str(file_name) + ".  Has " + 
                      str(num_cands) + " candidates.")
                continue
            #num_seats=int(lines[0][first_space+1])  was not working for civs data because of 1.0
                # and don't need because num-seats is always 1 for this analysis
                
            data = createBallotDF(lines)
            data_copy=data.copy(deep=True)

            anomaly_data = LNH_search(data_copy, num_cands, vote_method, mod_ballot_method)
            if anomaly_data:
                anomaly_lxns.append((file_path, anomaly_data))

    return anomaly_lxns


## Test function that only searches a few election
def LNH_search_shell_test(anomaly_search, vote_method, mod_ballot_method):
    lxn_names = []
    anomaly_lxns = []
    
    base_name = '../../raw_data/preference_profiles/scotland'

    # for folder_name in os.listdir(base_name):
    for folder_name in ['orkney22']:
        for file_name in os.listdir(base_name+'/'+folder_name):
            file_path = base_name+'/'+folder_name+'/'+file_name
            # if len(file_path)>180:
            #     print(file_path)
            #     continue
            
            lxn_names.append(file_path)   
            # print(file_path)
        
            sys.stdout.write('\r')
            sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
            sys.stdout.flush()
            
            File=open(file_path,'r')
            #print(str(filename))
            lines=File.readlines()

            first_space=lines[0].find(' ')
            num_cands=int(lines[0][0:first_space])
            if num_cands>52:
                print("Cannot handle this many candidates in election " + str(file_name) + ".  Has " + 
                      str(num_cands) + " candidates.")
                continue
            #num_seats=int(lines[0][first_space+1])  was not working for civs data because of 1.0
                # and don't need because num-seats is always 1 for this analysis
                
            data = createBallotDF(lines)
            data_copy=data.copy(deep=True)

            anomaly_data = LNH_search(data_copy, num_cands, vote_method, mod_ballot_method)
            if anomaly_data:
                anomaly_lxns.append((file_path, anomaly_data))

    return anomaly_lxns


## Reads through all data files and applies the specified search
def NS_buck_search_shell():
    lxn_names = []
    anomaly_lxns = []
    
    base_name = '../../raw_data/preference_profiles/scotland'

    for folder_name in os.listdir(base_name):
    # for folder_name in ['aberdeenshire22']:
        for file_name in os.listdir(base_name+'/'+folder_name):
            file_path = base_name+'/'+folder_name+'/'+file_name
            
            lxn_names.append(file_path)   
            # print(file_path)
            
            # if len(lxn_names)<912:
            #     # print(file_path)
            #     continue

            sys.stdout.write('\r')
            sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
            sys.stdout.flush()
            
            File=open(file_path,'r', encoding="utf-8")
            #print(str(filename))
            lines=File.readlines()

            first_space=lines[0].find(' ')
            num_cands=int(lines[0][0:first_space])
            if num_cands>52:
                print("Cannot handle this many candidates in election " + str(file_name) + ".  Has " + 
                      str(num_cands) + " candidates.")
                continue
            #num_seats=int(lines[0][first_space+1])  was not working for civs data because of 1.0
                # and don't need because num-seats is always 1 for this analysis
                
            data = createBallotDF(lines)
            data_copy=data.copy(deep=True)
        
            anomaly_data = noShowBucklin(data_copy, num_cands)
            if anomaly_data:
                anomaly_lxns.append((file_path, anomaly_data))

    return anomaly_lxns


# used to create dictionary format profiles for checking election methods with prefvoting
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


##############################################################
##############################################################
###### Ballot modification methods
##############################################################
##############################################################


## LNH type 1 (Truncate at L)
def truncBalAtL(ballot, winner, loser):
    """inputs ballot and a loser, and truncates the ballot after the loser"""
    if loser in ballot:
        return ballot[:ballot.index(loser)+1]#ballot.split(winner, 1)[0]
    else:
        return ballot

## LNH type 2 (Truncate at W)
def truncBalAtW(ballot, winner, loser):
    """inputs ballot, winner, and loser"""
    """if loser is ranked above winner, truncates the ballot after the winner"""
    # if winner in ballot:
    if (loser in ballot) and (winner in ballot) and (ballot.find(loser)<ballot.find(winner)):
        return ballot.split(winner, 1)[0]
    else:
        return ballot

## LNH type 3/Burying (Bury W)    
def buryWinBal(ballot, winner, loser):
    """inputs ballot, winner, and loser"""
    """if loser is ranked above winner, remove winner from ballot"""
    if (loser in ballot) and (winner in ballot) and (ballot.find(loser)<ballot.find(winner)):
        return ballot.split(winner)[0]+ballot.split(winner)[1]
    else:
        return ballot
    
## LNH type 4 (W hurting self with lower rankings)
def boostLinBal(ballot, winner, loser):    
    """inputs ballot, winner, and loser"""
    """if winner is ranked and loser is ranked below winner or not ranked,"""
    """move loser up until it is right behind winner"""
    if winner in ballot:
        if (loser not in ballot):
            return ballot.split(winner)[0]+winner+loser+ballot.split(winner)[1]
        elif ballot.find(winner)<ballot.find(loser): 
            front, back = ballot.split(winner)
            back_front, back_back = back.split(loser)
            return front+winner+loser+back_front+back_back
        else:
            return ballot
    else:
        return ballot
    
## unchecked
## used in IRV function
def truncate(number, digits) -> float: #truncates according to Scotland rules
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

## unchecked
## used in monotonicity search
def modifyUp(winner, ballot):
    """inputs a candidate and a ballot, and moves candidate to top of ballot if candidate is in ballot. 
    Otherwise adds candidate to top of ballot"""
    if winner in ballot:
        modified = winner + ballot.replace(winner, "")
    else:
        modified = winner + ballot
    return modified

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
    return IRV(new_profile, len(smith_set))

def smith_minimax(profile, cand_num):
    smith_set, new_profile = restrict_to_smith(profile, cand_num)
    return minimax(new_profile, len(smith_set))

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
    
def condorcet_plurality(profile, cand_num):
    smith_set, new_profile = restrict_to_smith(profile, cand_num)
    return plurality(new_profile, len(smith_set))




#################################################################
##### anomaly search functions
#################################################################


## run a search for later no harm anomalies
## exact type specified by mod_ballot_method
def LNH_search(profile, num_cands, voteMethod, mod_ballot_method):
    """takes in pandas preference profile, number of cands and election method to get winner W and searches for anomalies by modifying certain ballots"""
    cand_List1=[] #make list of all candidates, only candidates listed in top two ranks (issue for cvis?)
    
    for k in range(len(profile)):
        if profile.at[k,'ballot']!='':
            if profile.at[k,'ballot'][0] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][0])
        if len(profile.at[k,'ballot'])>1:
            if profile.at[k,'ballot'][1] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][1])
    # print(cand_List1)
    winner = voteMethod(profile, num_cands) #get winner of election using whatever election method #, len(cand_List1), 1
    if len(winner)!=1:
        print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
    W=winner[0]
    # print("Winner is " + str(W))
    
    losers = []
    for X in cand_List1:
        if X!=W:
            losers.append(X)
    #losers == cand_List1.remove(W) #list of losing candidates
    #print(losers)
    mod_frame = profile.copy(deep=True) #make a copy of original data to modify
    for L in losers:
        mod_frame2 = mod_frame.copy(deep=True) #make a copy of original data to modify
        for k in range(len(mod_frame2)):
            if mod_frame2.at[k,'ballot']!='':
                curBal = mod_frame2.at[k,'ballot'] #name the ballot at line k
                mod_frame2.at[k,'ballot'] = mod_ballot_method(curBal, W, L)
        newWinners = voteMethod(mod_frame2, num_cands)
        if len(newWinners)!=1:
            print('##### WARNING: MULTIPLE WINNERS DETECTED ######')
        newWinner = newWinners[0]
        
        if L == newWinner:
            return [W, L]
    
    return []


## stv function for no show anomalies
def STV_temp(frame3,n,S,winners, temp_quota): #this is to be used to run a test election once 
    # some people have been elected
    frame2 = frame3.copy(deep=True)
    """Inputs election, n=number of candidates, S=number of seats.  Returns winners"""
    
    hopefuls=[]
    eliminatedCand=[]
    quota = temp_quota
    list1=[]
    for k in range(len(frame2)):
        if frame2.at[k,'ballot']!='':
            if frame2.at[k,'ballot'][0] in list1:
                pass
            else:
                list1.append(frame2.at[k,'ballot'][0])
        if len(frame2.at[k,'ballot'])>1:
            if frame2.at[k,'ballot'][1] in list1:
                pass
            else:
                list1.append(frame2.at[k,'ballot'][1])
        if len(frame2.at[k,'ballot'])>2:
            if frame2.at[k,'ballot'][2] in list1:
                pass
            else:
                list1.append(frame2.at[k,'ballot'][2])
        if len(frame2.at[k,'ballot'])>3:
            if frame2.at[k,'ballot'][3] in list1:
                pass
            else:
                list1.append(frame2.at[k,'ballot'][3])
                
    cand_dict={}
    for i in range(n):
        cand_dict[i]=list1[i]
        hopefuls.append(list1[i])
        
    #Get each candidate's initial number of votes this round
    vote_counts={}
    
    for k in range(len(frame2)):
            if frame2.at[k,'ballot']!='':
                if frame2.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                else:
                    vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']
    
    max_count=max(vote_counts.values())
    while len(winners)<S:
        
        max_count=max(vote_counts.values())
        #somebody is elected and we have to transfer their votes
        if max_count>=quota:
            #There might be multiple people elected this round; save them as a sorted dictionary
            votes_for_winners={k:vote_counts[k] for k in vote_counts.keys() if vote_counts[k]>=quota }
            votes_for_winners=dict(sorted(votes_for_winners.items(),key=lambda x: x[1], reverse=True))
            
            #If we try to elect too many people, need to drop someone who surpassed quota
            if len(winners)+len(votes_for_winners)>S:
                
                for k in range(len(winners)+len(votes_for_winners)-S):
                    winners.append(list(votes_for_winners.keys())[k])
            
            else:
                winners=winners+list(votes_for_winners.keys())
                #print(winners)
                for cand in winners:
                    if cand in hopefuls:
                        hopefuls.remove(cand)
                
                while len(votes_for_winners)>0:
                    
                    cand=list(votes_for_winners.keys())[0]
    
                    if cand not in winners:
                        winners.append(cand)
                        hopefuls.remove(cand)
                    if len(winners)==S:
                        return winners
                    #print("cand elected", cand)
                    
                    weight=truncate((vote_counts[cand]-quota)/vote_counts[cand],5)
                    
                    #print("weight",weight)
                    for k in range(len(frame2)):
                        if frame2.at[k,'ballot']!='':
                            if frame2.at[k,'ballot'][0]==cand:
                                
                                frame2.at[k,'Count']=frame2.at[k,'Count']*weight
                                for x in winners:
                                    if x in frame2.at[k,'ballot']:
                                        frame2.at[k,'ballot']=frame2.at[k,'ballot'].replace(x,'')
                            else:
                                if cand in frame2.at[k,'ballot']:
                                     frame2.at[k,'ballot']=frame2.at[k,'ballot'].replace(cand,'')
                    votes_for_winners.pop(cand)
                    vote_counts={}
                    
                    for k in range(len(frame2)):
                        if frame2.at[k,'ballot']!='':
                            if frame2.at[k,'ballot'][0] in vote_counts.keys():
                                vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                            else:
                                vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']

                    votes_for_winners={k:vote_counts[k] for k in vote_counts.keys() if vote_counts[k]>=quota }
                    votes_for_winners=dict(sorted(votes_for_winners.items(),key=lambda x: x[1], reverse=True))
                    #print(vote_counts)
                    for cand in votes_for_winners.keys():
                        if cand not in winners:
                            winners.append(cand)
                            hopefuls.remove(cand)
                    if len(winners)==S:
                        return winners
                    frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
        #nobody is elected by surpassing quota, but the number
        #of candidates left equals S
        elif len(hopefuls)+len(winners)==S:
            return winners+hopefuls
        
        #remove weakest cand and transfer their votes with weight one
        else:
            #print(vote_counts)
            min_count=min(i for i in vote_counts.values() if i>0)
            count=0
            for votes in vote_counts:
                if votes==min_count:
                    count+=1
            if count>1:
                print("tie in candidate to remove")
                return

            eliminated_cand = list(vote_counts.keys())[list(vote_counts.values()).index(min_count)] #took str() away
            
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
            vote_counts={}
           
            for k in range(len(frame2)):
                if frame2.at[k,'ballot']!='':
                    if frame2.at[k,'ballot'][0] in vote_counts.keys():
                        vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                    else:
                        vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']
                        
            max_count=max(vote_counts.values())
            if len(hopefuls)+len(winners)==S:
                return winners+hopefuls
            frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
    return winners



def noShowAnomSearch(frame, n, S): 
    """inputs: dataframe of election, n= number of candidates, S= number of seats
    runs election to find winners/losers/frames, then identifies and eliminates votes to find 
    No Show anomalies connected to change in dropout order.  
    outputs if an anomaly exists, and how anomaly happens""" 
 
    quota=math.floor(sum(frame['Count'])/(S+1))+1 #calculate quota   
    winners, losers, elimFrames, winners_dict=STV3(frame,n,S) #Run original STV election, 
#     print("Original winners are: ")
#     print(winners) 
   
    for i in range(len(losers)): #function removes i losers from original data frame, 
        # then searches for all possible anomalies at a given level<=n, right before each "loser" is 
        # eliminated.  outputs if anomaly occurs, and if so, how
        
        #now have temporary dataframe with i losers removed, now check for anomaly at (n-i)-cand level
        tempFrame = elimFrames[i].copy(deep=True)
        tempWinners = copy.deepcopy(winners_dict[i]) #candidates who have already won a seat at this point
        loser = losers[i] #loser is the candidate about to be eliminated
        vote_counts={}
        
        for k in range(len(tempFrame)):
            if tempFrame.at[k,'ballot']!='':
                if tempFrame.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[tempFrame.at[k,'ballot'][0]]+=tempFrame.iloc[k]['Count']
                else:
                    vote_counts[tempFrame.at[k,'ballot'][0]]=tempFrame.iloc[k]['Count']
#         print("")
#         print("Out of " + str(n) + " candidates, results at the " +str(len(vote_counts))+"-candidate level for Elimination Order anomaly:")
        
        checkables = list(vote_counts.keys())
        checkables.remove(loser)#these are the candidates we want to check for anomalies, need to remove winners
        for j in range(len(winners)):
            if winners[j] in checkables:
                checkables.remove(winners[j])
            else:
                pass
        
        loser_gap = {} #calculate gap between each candidate and the loser
        for x in range(len(vote_counts)):
            loser_gap[list(vote_counts.keys())[x]]=vote_counts[list(vote_counts.keys())[x]]-vote_counts[loser]                                                                           
        
        #choose one of the other non-winning candidates C_j and compare to the next-eliminated candidate E.  
        #looking for votes of the form C_j … L_i …, where W_j is NOT present in the … (or, more easily, not present 
        #in the ballot at all).  If there are enough of such votes that removing them would make H drop out 
        #before E, remove them.  If there are not enough, remove them and them look 
        # for the H … L_i … W_j votes.?  If enough of them to surpass E, do it.  If not, 
        #no No-show anomaly of that particular type would be possible.  The code would loop over all losers L_i,
        #then all winners W_j, then all remaining Hopefuls H that are not the L_i, W_j, or next-eliminated 
        #candidate E.
        
        for k in range(len(checkables)):
            gap = loser_gap[checkables[k]] #number of votes separating candidate and loser
            hopefuls = checkables[:] #copy checkables from before, remove C_k, add loser
            hopefuls.remove(checkables[k])
            hopefuls.append(loser)
            for j in range(len(winners)):
                for m in range(len(hopefuls)):
                    tempFrame1 = tempFrame.copy(deep=True)
                    modifiableVotes1 = 0 #modifiableVotes= sum of all ballots that start with C_k L
                    modifiableVotes2 = 0
                    for z in range(len(tempFrame1)): #looking for which votes could be removed
                        currentBallot = tempFrame1.at[z,'ballot']
                        try:
                            currentBallot[0]
                        except: 
                            continue
                        else: 
                            if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winners[j] not in currentBallot:
                                modifiableVotes1 += tempFrame1.at[z,'Count'] #ballots without winner on the ballot
                            if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winners[j] in currentBallot:
                                if currentBallot.index(hopefuls[m])<currentBallot.index(winners[j]):
                                    modifiableVotes2 += tempFrame1.at[z,'Count'] #ballots where winner is ranked below
                    # check if enough votes to change
                    if (modifiableVotes1 + modifiableVotes2) <= (loser_gap[checkables[k]]+1): 
                        continue #print("No anomaly for " + hopefuls[m] + " by removing " + checkables[k] + 
#                               ".  Not enough modifiable votes to change dropout order.")
                    
                    else: #there are enough modifiable ballots to remove.  Remove them in correct order
                        remainingWinners = copy.deepcopy(winners)
                        remainingWinners.remove(winners[j])
                        for c in range(len(tempWinners)):
                            if tempWinners[c] in remainingWinners:
                                remainingWinners.remove(tempWinners[c]) #list of winners who have NOT yet been elected, not winners[j]
                        check = copy.deepcopy(gap)
                        
                        for z in range(len(tempFrame1)): #These steps remove "best" votes to cause No-show anomaly
                            # because they are first filtered through a winner getting a seat
                            if check >= 0:
                                currentBallot = tempFrame1.at[z,'ballot']
                                try:
                                    currentBallot[0]
                                except: 
                                    continue
                                else: #if C_k...H_m... with no W_j on ballot
                                    if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and (winners[j] not in currentBallot):
                                        for y in range(len(remainingWinners)):
                                            if remainingWinners[y] in currentBallot:
                                                if currentBallot.index(remainingWinners[y])<currentBallot.index(hopefuls[m]):
                                                    if check - tempFrame1.at[z,'Count']>=-1: #remove all such ballots
                                                        check = check - tempFrame1.at[z,'Count'] #update check
                                                        tempFrame1.at[z,'Count'] = 0
                                                        
                                                    else: #remove check+1 such ballots
                                                        tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
                                                        check = -1
                                                        
                                    #if C_k...H_m...W_j
                                    elif currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winners[j] in currentBallot:
                                        if currentBallot.index(hopefuls[m])<currentBallot.index(winners[j]):
                                            for y in range(len(remainingWinners)):
                                                if remainingWinners[y] in currentBallot:
                                                    if currentBallot.index(remainingWinners[y])<currentBallot.index(hopefuls[m]):
                                                        if check - tempFrame1.at[z,'Count']>=-1: #remove all such ballots
                                                            check = check - tempFrame1.at[z,'Count']
                                                            tempFrame1.at[z,'Count'] = 0
                                                            
                                                        else: #remove check+1 such ballots
                                                            tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
                                                            check = -1
                                                            
                                    else:
                                        pass
                        # once "best" ballots are removed, remove enough others to surpass gap
                        #modify C_j … L_i …, where W_j is NOT present votes
                        if modifiableVotes1 > check: #remove only loser gap +1 votes
                            for z in range(len(tempFrame1)):
                                if check >= 0:
                                    currentBallot = tempFrame1.at[z,'ballot']
                                    try:
                                        currentBallot[0]
                                    except: 
                                        continue
                                    else:
                                        if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winners[j] not in currentBallot:
                                            if check - tempFrame1.at[z,'Count']>=-1: #remove all such ballots
                                                check = check - tempFrame1.at[z,'Count']
                                                tempFrame1.at[z,'Count'] = 0
                                                
                                            else: #remove check+1 such ballots
                                                tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
                                                check = -1
                                                
                                        else: 
                                            pass
                            # Run STV election on modifed election. If W_j is NOT in winners and H_m is, 
                            # AND all the other winners stay the same, then report anomaly 
                           
                            win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota) #n-i
                            if (hopefuls[m] in win1) and (winners[j] not in win1):# and (set(oldWinners).issubset(set(win1))):
                                ## print results (Adam)
                                # print("")
                                # print("")
                                # print("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove " + str(gap+1) +" "+ checkables[k]+ 
                                # "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot and " +
                                # hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
                                # print("Original winners were " + str(winners))
                                # print("New winners are " + str(win1))
                                # print('Election is ' + filename)
                                # print("")
                                # print("")
                                
                                ## save results to file (Adam)
                                # aust1.write("\n")
                                # aust1.write("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove all " + checkables[k]+ 
                                # "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot AND " +
                                # str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] + " votes and " +
                                # hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
                                # aust1.write("Original winners were " + str(winners))
                                # aust1.write("New winners are " + str(win1))
                                # aust1.write('Election is ' + filename)
                                # aust1.write("\n")
                                
                                ## return results
                                return [winners[j], hopefuls[m]]
                                
                            else:
                                continue
#                                 print("No anomaly for " + hopefuls[m] +" after removing "+ str(gap +1) +" "+ checkables[k]+ 
#                                 "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot. ")
                        else: #remove all modifiable1 ballots, then remove gap+1 modifiable2s
                            for z in range(len(tempFrame1)):
                                currentBallot = tempFrame1.at[z,'ballot']
                                try:
                                    currentBallot[0]
                                except: 
                                    continue
                                else:
                                    if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winners[j] not in currentBallot:
                                        gap = gap - tempFrame1.at[z,'Count']
                                        tempFrame1.at[z,'Count'] = 0 
                                        
                            check = copy.deepcopy(gap)
                            for z in range(len(tempFrame1)):
                                if check >= 0:
                                    currentBallot = tempFrame1.at[z,'ballot']       
                                    try:
                                        currentBallot[0]
                                    except: 
                                        continue
                                    else:
                                        if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winners[j] in currentBallot:
                                            if currentBallot.index(hopefuls[m])<currentBallot.index(winners[j]):
                                                if check - tempFrame1.at[z,'Count']>=-1: #remove all such ballots
                                                    check = check - tempFrame1.at[z,'Count']
                                                    tempFrame1.at[z,'Count'] = 0
                                                    
                                                else: #remove check+1 such ballots
                                                    tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
                                                    check = -1
                                                    
                                        else: 
                                            pass  
                            # Run STV election on modifed election. If W_j is NOT in winners and H_m is, 
                            # AND all the other winners stay the same, then report anomaly 
                            
                            win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota)
                            
                            if (hopefuls[m] in win1) and (winners[j] not in win1):# and (set(oldWinners).issubset(set(win1))):
                                ## print results (Adam)
                                # print("")
                                # print("")
                                # print("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove all " + checkables[k]+ 
                                # "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot AND " +
                                # str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] + " votes and " +
                                # hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
                                # print("Original winners were " + str(winners))
                                # print("New winners are " + str(win1))
                                # print('Election is ' + filename)
                                # print("")
                                # print("")
                                
                                ## save results to file (Adam)
                                # aust.write("\n")
                                # aust1.write("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove all " + checkables[k]+ 
                                # "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot AND " +
                                # str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] + " votes and " +
                                # hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
                                # aust1.write("Original winners were " + str(winners))
                                # aust1.write("New winners are " + str(win1))
                                # aust1.write('Election is ' + filename)
                                # aust1.write("\n")
                                
                                ## return results
                                return [winners[j], hopefuls[m]]
                            
                            else:
                                #print("No anomaly for " + hopefuls[m] +" after removing all " + checkables[k]+ 
                                #"..."+ hopefuls[m] + " votes where " + winners[j] + " is not in the ballot AND " +
                                #str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] +
                                #" votes. ")
                                continue

## shell function for no show search, don't think I will need this            
def noShowSearchAll():
    aust1 = open("CIVSnoShowEvents.txt", "w")
    aust2 = open("CIVStooBigForLetters.txt", "w")
    aust3 = open("CIVSmoreThan15.txt", "w")
    
    directory='Preference Profiles/australia' #'Scotland data, LEAP'
    r=[]
    subdirs = [x[0] for x in os.walk(directory)]
    
    subdirs=subdirs[1:]
    counter=0
    num_elections=0
    
    for subdir in subdirs:
        files=os.listdir(subdir)
        #print(files)
        for file in files:
            #print(subdir,file,count)
            filename=subdir+'/'+file   
            election=file
            if 'DS_Store' not in filename and '.pdf' not in filename:
                num_elections+=1
                File=open(filename,'r')
                #print(str(filename))
                lines=File.readlines()
                #print(lines)
    
                first_space=lines[0].find(' ')
                num_cands=int(lines[0][0:first_space])
                if num_cands>52:
                    print("Cannot handle this many candidates in election " + str(filename) + ".  Has " + 
                          str(num_cands) + " candidates.")
                    aust2.write("Cannot handle this many candidates in election " + str(filename) + ".  Has " + 
                          str(num_cands) + " candidates which is more than 52.")
                    aust2.write("/n")
                    continue
                #num_seats=int(lines[0][first_space+1])  was not working for civs data because of 1.0
                    # and don't need because num-seats is always 1 for this analysis
                column_names=['ballot','Count']
                data=pd.DataFrame(columns = column_names)
                for k in range(1,len(lines)):
                    if lines[k][0]=='0':
                        break
                    #print(k)
                    first_space=lines[k].find(' ')
                    count=int(lines[k][0:first_space])
                    end=lines[k].find(' 0')
                    ballot=lines[k][first_space+1:end+1]
                    
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
                data_copy=data.copy(deep=True)
                print(filename)
                if num_cands>15:
                    print("")
                    print("Too many candidates in " + str(filename) + ". Has " + str(num_cands) + " candidates.")
                    print("")
                    aust3.write("Skipped " + str(filename) + ". Has " + str(num_cands) + " candidates.")
                    aust3.write("/n")
                    continue
                else:
                    noShowAnomSearch(filename, data_copy,num_cands,1)
                print(num_elections)
    aust1.close()
    aust2.close()
    aust3.close()                      



def noShowBucklin(profile, cand_num):
    # search through the election. If at any stage a loser is beating the winner, 
    # see if ballots that rank loser above winner but are not yet being counted
    # can be thrown out to lower the quota so that loser wins without having to 
    # advance to next round of counts
    
    cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cands = cand_names[:cand_num]
    
    winners = bucklin(profile, cand_num)
    if len(winners)>1:
        # hard to define an anomaly if there is not a single winner
        return []
    winner = winners[0]
    losers = cands.copy()
    losers.remove(winner)
    
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

        # print(scores)
        # check if any candidate has higher score than winner
        for loser in losers:
            if scores[loser] > scores[winner]:
                remove_ballots = []
                remove_ballot_total = 0
                for k in range(len(profile)):
                    ballot = profile.at[k, 'ballot']
                    if ballot.find(loser)>round_indx:
                        if (winner not in ballot) or (ballot.find(winner) > ballot.find(loser)):
                            remove_ballots.append(ballot)
                            remove_ballot_total += profile.at[k, 'Count']
                if threshold - remove_ballot_total/2 < scores[loser]:
                    return [winner, loser]

    return []



# upward monotonicity
def monoAnomSearch(filename, frame, n, S): 
    """inputs: dataframe of election, n= number of candidates, S= number of seats
    runs election to find winners/losers/prefData before candidate eliminated, tempWinners,
    then identifies and makes vote swaps to find 
    upward monotonicity anomalies.  Returns if an anomaly exists, and how anomaly happens""" 
    quota=math.floor(sum(frame['Count'])/(S+1))+1 #calculate quota   
    winners, losers, elimFrames, winners_dict=STV3(frame,n,S) #get election data from STV3
    #print("Original winners are ")
    #print(winners)
   
    for i in range(len(losers)): #function looks at real data before ith loser drops, 
        # then searches for all possible anomalies at a given level<=n, right before each "loser" is 
        # eliminated.  outputs if anomaly occurs, and if so, how...could also output other information
#         print("")
#         print("Results at the " +str(n-i)+"-candidate level:")
        
        tempFrame = elimFrames[i].copy(deep=True) #actual data before ith cand is removed 
        tempWinners = copy.deepcopy(winners_dict[i])
        remainingWinners = copy.deepcopy(winners) #put in all winners
        for y in range(len(tempWinners)):
            remainingWinners.remove(tempWinners[y]) #remove people who already got seats
        # remainingWinners are the future winners who are still in the election
        loser = losers[i]
        vote_counts={}
        for k in range(len(tempFrame)):
            if tempFrame.at[k,'ballot']!='':
                if tempFrame.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[tempFrame.at[k,'ballot'][0]]+=tempFrame.iloc[k]['Count']
                else:
                    vote_counts[tempFrame.at[k,'ballot'][0]]=tempFrame.iloc[k]['Count']
#         print("")
#         print("Out of " + str(n) + " candidates, results at the " +str(len(vote_counts))+"-candidate level for Elimination Order anomaly:")
        
#         print(vote_counts)
        quota_gap = {} #track how many votes candidates need to get quota
        for x in range(len(remainingWinners)):
            quota_gap[remainingWinners[x]]=quota-vote_counts[remainingWinners[x]]   
        loser_gap ={} #gap in votes between a candidate and the losing candidate
        for x in range(len(vote_counts)):
            loser_gap[list(vote_counts.keys())[x]]=vote_counts[list(vote_counts.keys())[x]]-vote_counts[loser]                                                                           
                                                                                    
        for j in range(len(remainingWinners)):
            # search for anomalies for each winner W_j=remainingWinners[j]: 
            if quota_gap[remainingWinners[j]] < 0:
                print("No anomaly for " + remainingWinners[j] + ".  Meets quota at " + str(n-i) + "-candidate level." +
                      " NOTE: THIS SHOULD NOT EVER HAPPEN.  IF YOU SEE THIS THEN THERE IS A MISTAKE")
            else:
                checkables = list(vote_counts.keys()) #list of all candidates
                checkables.remove(remainingWinners[j]) #remove winner from checkables
                checkables.remove(loser)#remove loser/next eliminated candidate from checkables 
                
                #we now try to modify C_k...W_j ballots to change dropout order, see if it changes overall result 
                for k in range(len(checkables)): #choose the kth checkable = C_k
                    gap = loser_gap[checkables[k]]
                    if gap > quota_gap[remainingWinners[j]]:
                        pass
#                         print("No anomaly for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
#                         " at the "+ str(n-i) + "-candidate level. " + remainingWinners[j] + 
#                               " meets quota before change in dropout order." )   
                    else: #check for 1-rankings first, most likely to cause anomaly
                        tempFrame1 = tempFrame.copy(deep=True)
                        modifiableVotes1 = 0 #modifiableVotes_kj1 = sum of all ballots that start with C_k W_j
                        for z in range(len(tempFrame1)):
                            currentBallot = tempFrame1.at[z,'ballot']
                            try:
                                currentBallot[1]
                            except: 
                                continue
                            else:
                                if currentBallot[0]==checkables[k] and currentBallot[1]==remainingWinners[j]:
                                    modifiableVotes1 += tempFrame1.at[z,'Count']
                        if modifiableVotes1 > gap: #if so, can change dropout order just by modifying these ballots
                            check = copy.deepcopy(gap)
                            
                            for z in range(len(tempFrame1)):
                                if check>=0:
                                    currentBallot = tempFrame1.at[z,'ballot']
                                    try:
                                        currentBallot[1]
                                    except: 
                                        continue
                                    else:
                                        if currentBallot[0]==checkables[k] and currentBallot[1]==remainingWinners[j]:
                                            if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                #print("Ballot modified is " + tempFrame1.at[z,'ballot'] + " at line "+ str(z))
                                                tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                #print("Ballot modified to " + tempFrame1.at[z,'ballot'])
                                                check = check - tempFrame1.at[z,'Count']
                                                #print("check is now " +str(check))
                                            else: #modify only check+1 such ballots
                                                #print("Ballot modified is " + tempFrame1.at[z,'ballot'] + " at line "+ str(z))
                                                tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
                                                #now add new line to frame with modified ballot
                                                tempFrame1.loc[len(tempFrame1)] = [modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot']), check+1]
                                                check = -1
                                        else:
                                            pass
                            # Run STV election on modifed election.  Check to see if W_j is in new winners list
                            # if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate level.
                            # votes modified to 1 ranking"
                            win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota)
                            if remainingWinners[j] in win1:
                                pass
#                                 print("No anomaly for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
#                                 " at the "+ str(n-i) + "-candidate level. " + remainingWinners[j] + 
#                                   " still wins after change in dropout order." )
                            else:
                                modifiedNum = gap - check
                                data1.write("upward MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                            " at the "+ str(n-i) + "-candidate level for election " + str(filename))
                                print("MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                " at the "+ str(n-i) + "-candidate level!!!! Modifying " + str(modifiedNum) +" "+checkables[k]+ remainingWinners[j]+"_"  
                                  " to " +  remainingWinners[j]+checkables[k]+ "_ makes " + remainingWinners[j]+ " lose their seat.")
                                data1.write("Original winners were " + str(remainingWinners))
                                data1.write("New winners are " + str(win1))
                                data1.write('Modified election is')
                                data1.write("\n")
                                display(tempFrame1)
                        
                        #if C_k W_j ballots were not enough to make up gap, modify all of them and try next mod
                        else:
                                # modify all modifiableVotes C_k W_j votes in reduced_df to become W_j C_k 
                            for z in range(len(tempFrame1)):
                                currentBallot = tempFrame1.at[z,'ballot']
                                try:
                                    currentBallot[1]
                                except: 
                                    continue
                                else:
                                    if currentBallot[0]==checkables[k] and currentBallot[1]==remainingWinners[j]:
                                        tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                        gap = gap - tempFrame1.at[z,'Count']
                            
                            #CHECK THE 2-RANKINGS 
                            # modifiableVotes_kj2 = sum of all ballots that start with C_k ___ W_j  ##that is, 
                                # ballots with C_k in first, W_j in third, anything else in second
                            modifiableVotes2 = 0 #modifiableVotes2 = sum of all ballots that start with C_k ___ W_j
                            for z in range(len(tempFrame1)):
                                currentBallot = tempFrame1.at[z,'ballot']
                                try:
                                    currentBallot[2]
                                except: 
                                    continue
                                else:
                                    if currentBallot[0]==checkables[k] and currentBallot[2]==remainingWinners[j]:
                                        modifiableVotes2 += tempFrame1.at[z,'Count']  

                            if modifiableVotes2 > gap:  # modify gap of the C_k __ W_j votes in modified_df_kj1 to become 
                                                        # W_j C_k ___ votes.
                                
                                check = copy.deepcopy(gap)
                                for z in range(len(tempFrame1)): #tempFrame in place of reduceFrame(frame,losers)[i]
                                    if check>=0:
                                        currentBallot = tempFrame1.at[z,'ballot']
                                        try:
                                            currentBallot[2]
                                        except: 
                                            continue
                                        else:
                                            if currentBallot[0]==checkables[k] and currentBallot[2]==remainingWinners[j]:
                                                if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                    tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                    check = check - tempFrame1.at[z,'Count']

                                                else: #modify only check+1 such ballots
                                                    #take check+1 ballots from current ballot
                                                    tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                    #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                    tempFrame1.loc[len(tempFrame1)] = [modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot']), check+1]
                                                    check = -1
                                            else:
                                                pass
                                        
                                # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                # level. votes modified to 2 rankings"
                                win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota) #n-i?
                                if remainingWinners[j] in win1:
                                    pass
                                    
#                                     print("No anomaly for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
#                                     " at the "+ str(n-i) + "-candidate level. " + remainingWinners[j] + 
#                                       " still wins after change in dropout order." )
                                else:
                                    modifiedNum = gap - check
                                    print("MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                    " at the "+ str(n-i) + "-candidate level!!!! ")
                                    data1.write("upward MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                            " at the "+ str(n-i) + "-candidate level for election " + str(filename))
                                    data1.write("Modifying all 1-rankings and " + str(modifiedNum) + 
                                    " 2-rankings makes " + remainingWinners[j]+ " lose their seat.") 
                                    data1.write("Original winners were " + str(remainingWinners))
                                    data1.write("New winners are " + str(win1))
                                    #data1.write('Modified election is')
                                    data1.write("\n")
                                    display(tempFrame1)
                                
                            else: 
                                # modify all modifiableVotes C ___  W votes in reduced_df to become W_j C_k ___
                                for z in range(len(tempFrame1)):
                                    currentBallot = tempFrame1.at[z,'ballot']
                                    try:
                                        currentBallot[2]
                                    except: 
                                        continue
                                    else:
                                        if currentBallot[0]==checkables[k] and currentBallot[2]==remainingWinners[j]:
                                            tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                            gap = gap - tempFrame1.at[z,'Count']

                                #CHECK THE 3-RANKINGS
                                # modifiableVotes3 = sum of all ballots that start with C_k ___ __ W_j  ##that is, 
                                    # ballots with C_k in first, W_j in fourth, anything else in between
                                modifiableVotes3 = 0 
                                for z in range(len(tempFrame1)):
                                    currentBallot = tempFrame1.at[z,'ballot']
                                    try:
                                        currentBallot[3]
                                    except: 
                                        continue
                                    else:
                                        if currentBallot[0]==checkables[k] and currentBallot[3]==remainingWinners[j]:
                                            modifiableVotes3 += tempFrame1.at[z,'Count']  

                                if modifiableVotes3 > gap:  # modify gap of the C_k __ W_j votes in modified_df_kj1 to become 
                                                            # W_j C_k ___ votes.

                                    check = copy.deepcopy(gap)
                                    for z in range(len(tempFrame1)): 
                                        if check>=0:
                                            currentBallot = tempFrame1.at[z,'ballot']
                                            try:
                                                currentBallot[3]
                                            except: 
                                                continue
                                            else:
                                                if currentBallot[0]==checkables[k] and currentBallot[3]==remainingWinners[j]:
                                                    if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                        tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                        check = check - tempFrame1.at[z,'Count']

                                                    else: #modify only check+1 such ballots
                                                        #take check+1 ballots from current ballot
                                                        tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                        #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                        tempFrame1.loc[len(tempFrame1)] = [modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot']), check+1]
                                                        check = -1
                                                else:
                                                    pass

                                    # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                    # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                    # level. votes modified to 2 rankings"
                                    win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota)#n-i?
                                    if remainingWinners[j] in win1:
                                        pass

#                                         print("No anomaly for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
#                                         " at the "+ str(n-i) + "-candidate level. " + remainingWinners[j] + 
#                                           " still wins after change in dropout order." )
                                    else:
                                        modifiedNum = gap - check
                                        print("MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                        " at the "+ str(n-i) + "-candidate level!!!! ")
                                        data1.write("upward MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                            " at the "+ str(n-i) + "-candidate level for election " + str(filename))
                                        data1.write("Modifying all 1- and 2- rankings and " + str(modifiedNum) + 
                                        " 3-rankings makes " + remainingWinners[j]+ " lose their seat.") 
                                        data1.write("Original winners were " + str(remainingWinners))
                                        data1.write("New winners are " + str(win1))
                                        #data1.write('Modified election is')
                                        data1.write("\n")
                                        display(tempFrame1)

                                else: 
                                    # modify all modifiableVotes_kj1 C ___ ___ W votes in reduced_df to become W_j C_k ___
                                    for z in range(len(tempFrame1)):
                                        currentBallot = tempFrame1.at[z,'ballot']
                                        try:
                                            currentBallot[3]
                                        except: 
                                            continue
                                        else:
                                            if currentBallot[0]==checkables[k] and currentBallot[3]==remainingWinners[j]:
                                                tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                gap = gap - tempFrame1.at[z,'Count']

                                    #CHECK THE 4-RANKINGS
                                    # modifiableVotes4 = sum of all ballots that start with C_k ___ __ ___ W_j  ##that is, 
                                        # ballots with C_k in first, W_j in fourth, anything else in between
                                    modifiableVotes4 = 0 # = sum of all ballots that start with 4-ranking
                                    for z in range(len(tempFrame1)):
                                        currentBallot = tempFrame1.at[z,'ballot']
                                        try:
                                            currentBallot[4]
                                        except: 
                                            continue
                                        else:
                                            if currentBallot[0]==checkables[k] and currentBallot[4]==remainingWinners[j]:
                                                modifiableVotes4 += tempFrame1.at[z,'Count']  

                                    if modifiableVotes4 > gap:  # modify gap of the C_k __ W_j votes in modified_df_kj1 to become 
                                                                # W_j C_k ___ votes.

                                        check = copy.deepcopy(gap)
                                        for z in range(len(tempFrame1)): 
                                            if check>=0:
                                                currentBallot = tempFrame1.at[z,'ballot']
                                                try:
                                                    currentBallot[4]
                                                except: 
                                                    continue
                                                else:
                                                    if currentBallot[0]==checkables[k] and currentBallot[4]==remainingWinners[j]:
                                                        if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                            tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                            check = check - tempFrame1.at[z,'Count']

                                                        else: #modify only check+1 such ballots
                                                            #take check+1 ballots from current ballot
                                                            tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                            #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                            tempFrame1.loc[len(tempFrame1)] = [modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot']), check+1]
                                                            check = -1
                                                    else:
                                                        pass

                                        # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                        # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                        # level. votes modified to 2 rankings"
                                        win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota)#n-i?
                                        if remainingWinners[j] in win1:
                                            pass

#                                             print("No anomaly for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
#                                             " at the "+ str(n-i) + "-candidate level. " + remainingWinners[j] + 
#                                               " still wins after change in dropout order." )
                                        else:
                                            modifiedNum = gap - check
                                            print("MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                            " at the "+ str(n-i) + "-candidate level!!!! ")
                                            data1.write("upward MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                            " at the "+ str(n-i) + "-candidate level for election " + str(filename))
                                            data1.write("Modifying all 1-, 2-, and 3-rankings and " + str(modifiedNum) + 
                                            " 4-rankings makes " + remainingWinners[j]+ " lose their seat.") 
                                            data1.write("Original winners were " + str(remainingWinners))
                                            data1.write("New winners are " + str(win1))
                                            data1.write("\n")
                                            print('Modified election is')
                                            display(tempFrame1)


                                    else:
                                        # modify all modifiableVotes_kj1 C ___ ___ ___W votes in reduced_df to become W_j C_k ___
                                        for z in range(len(tempFrame1)):
                                            currentBallot = tempFrame1.at[z,'ballot']
                                            try:
                                                currentBallot[4]
                                            except: 
                                                continue
                                            else:
                                                if currentBallot[0]==checkables[k] and currentBallot[4]==remainingWinners[j]:
                                                    tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                    gap = gap - tempFrame1.at[z,'Count']
                                        
                                        #CHECK THE 5-RANKINGS
                                        # modifiableVotes5 = sum of all ballots  
                                            # with C_k in first, W_j in sixth, anything else in between
                                        modifiableVotes5 = 0 # = sum of all 5-ranking ballots that start with C_k 
                                        for z in range(len(tempFrame1)):
                                            currentBallot = tempFrame1.at[z,'ballot']
                                            try:
                                                currentBallot[5]
                                            except: 
                                                continue
                                            else:
                                                if currentBallot[0]==checkables[k] and currentBallot[5]==remainingWinners[j]:
                                                    modifiableVotes5 += tempFrame1.at[z,'Count']  

                                        if modifiableVotes5 > gap:  # modify gap of the C_k __ W_j votes in modified_df_kj1 to become 
                                                                    # W_j C_k ___ votes.

                                            check = copy.deepcopy(gap)
                                            for z in range(len(tempFrame1)): #tempFrame in place of reduceFrame(frame,losers)[i]
                                                if check>=0:
                                                    currentBallot = tempFrame1.at[z,'ballot']
                                                    try:
                                                        currentBallot[5]
                                                    except: 
                                                        continue
                                                    else:
                                                        if currentBallot[0]==checkables[k] and currentBallot[5]==remainingWinners[j]:
                                                            if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                                tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                                check = check - tempFrame1.at[z,'Count']

                                                            else: #modify only check+1 such ballots
                                                                #take check+1 ballots from current ballot
                                                                tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                                #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                                tempFrame1.loc[len(tempFrame1)] = [modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot']), check+1]
                                                                check = -1
                                                        else:
                                                            pass

                                            # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                            # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                            # level. votes modified to 2 rankings"
                                            win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota) #n-i?
                                            if remainingWinners[j] in win1:
                                                pass

#                                                 print("No anomaly for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
#                                                 " at the "+ str(n-i) + "-candidate level. " + remainingWinners[j] + 
#                                                   " still wins after change in dropout order." )
                                            else:
                                                modifiedNum = gap - check
                                                print("MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                " at the "+ str(n-i) + "-candidate level!!!! ")
                                                data1.write("upward MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                            " at the "+ str(n-i) + "-candidate level for election " + str(filename))
                                                data1.write("Modifying all 1-, 2-, 3- and 4-rankings and " + str(modifiedNum) + 
                                                " 5-rankings makes " + remainingWinners[j]+ " lose their seat.") 
                                                data1.write("Original winners were " + str(remainingWinners))
                                                data1.write("New winners are " + str(win1))
                                                data1.write("\n")
                                                print('Modified election is')
                                                display(tempFrame1)


                                        else:
                                            # modify all modifiableVotes C ... W votes in reduced_df to become W_j C_k ___
                                            for z in range(len(tempFrame1)):
                                                currentBallot = tempFrame1.at[z,'ballot']
                                                try:
                                                    currentBallot[5]
                                                except: 
                                                    continue
                                                else:
                                                    if currentBallot[0]==checkables[k] and currentBallot[5]==remainingWinners[j]:
                                                        tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                        gap = gap - tempFrame1.at[z,'Count']
                                            
                                            #We chose to modify most/all of ranked votes before doing bullet votes, as we think
                                            # that is most likely to case anomalies
                                            #CHECK THE BULLET VOTES, length 1
                                              ##that is, 
                                                # ballots with just C_k in first
                                            modifiableVotesBullet1 = 0 # = sum of all bullet votes w/ length 1
                                            for z in range(len(tempFrame1)):
                                                currentBallot = tempFrame1.at[z,'ballot']
                                                if len(currentBallot) == 1:
                                                    if currentBallot[0]==checkables[k]:
                                                            modifiableVotesBullet1 += tempFrame1.at[z,'Count']  

                                            if modifiableVotesBullet1 > gap:  # modify gap of the C_k  votes in modified_df_kj1 to become 
                                                                        # W_j C_k votes.

                                                check = copy.deepcopy(gap)
                                                for z in range(len(tempFrame1)): 
                                                    if check>=0:
                                                        currentBallot = tempFrame1.at[z,'ballot']
                                                        if len(currentBallot) == 1:
                                                            if currentBallot[0]==checkables[k]:
                                                                if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                                    tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                                    check = check - tempFrame1.at[z,'Count']

                                                                else: #modify only check+1 such ballots
                                                                    #take check+1 ballots from current ballot
                                                                    tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                                    #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                                    tempFrame1.loc[len(tempFrame1)] = [modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot']), check+1]
                                                                    check = -1

                                                # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                                # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                                # level. votes modified to 2 rankings"
                                                win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota)
                                                if remainingWinners[j] in win1:
                                                    pass

#                                                     print("No anomaly for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
#                                                     " at the "+ str(n-i) + "-candidate level. " + remainingWinners[j] + 
#                                                       " still wins after change in dropout order." )
                                                else:
                                                    modifiedNum = gap - check
                                                    print("MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                    " at the "+ str(n-i) + "-candidate level!!!! ")
                                                    data1.write("upward MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                            " at the "+ str(n-i) + "-candidate level for election " + str(filename))
                                                    data1.write("Modifying all 1-, 2-, 3- and 4-rankings and " + str(modifiedNum) + 
                                                    " 1-bullet votes makes " + remainingWinners[j]+ " lose their seat.") 
                                                    data1.write("Original winners were " + str(remainingWinners))
                                                    data1.write("New winners are " + str(win1))
                                                    data1.write("\n")
                                                    print('Modified election is')
                                                    display(tempFrame1)


                                            else:
                                                # modify all modifiableVotes C_k  votes in reduced_df to become W_j C_k 
                                                for z in range(len(tempFrame1)):
                                                    currentBallot = tempFrame1.at[z,'ballot']
                                                    if len(currentBallot) == 1:
                                                        if currentBallot[0]==checkables[k]:
                                                            tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                            gap = gap - tempFrame1.at[z,'Count']

                                                #CHECK THE BULLET VOTES, length 2
                                                # modifiableVotesBullet2 = sum of all ballots that are just C_k C_i  
                                                modifiableVotesBullet2 = 0 # = sum of all bullet votes w/ length 2
                                                for z in range(len(tempFrame1)):
                                                    currentBallot = tempFrame1.at[z,'ballot']
                                                    if len(currentBallot) == 2:
                                                        if currentBallot[0]==checkables[k] and currentBallot[1]!=remainingWinners[j]: 
                                                                modifiableVotesBullet2 += tempFrame1.at[z,'Count']  

                                                if modifiableVotesBullet2 > gap:  # modify gap of the C_k C_i votes in modified to become 
                                                                            # W_j C_k C_i votes.

                                                    check = copy.deepcopy(gap)
                                                    for z in range(len(tempFrame1)): 
                                                        if check>=0:
                                                            currentBallot = tempFrame1.at[z,'ballot']
                                                            if len(currentBallot) == 2:
                                                                if currentBallot[0]==checkables[k] and currentBallot[1]!=remainingWinners[j]: 
                                                                    if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                                        tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                                        check = check - tempFrame1.at[z,'Count']

                                                                    else: #modify only check+1 such ballots
                                                                        #take check+1 ballots from current ballot
                                                                        tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                                        #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                                        tempFrame1.loc[len(tempFrame1)] = [modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot']), check+1]
                                                                        check = -1

                                                    # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                                    # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                                    # level. votes modified to 2 rankings"
                                                    win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota)#n-i?
                                                    if remainingWinners[j] in win1:
                                                        pass

#                                                         print("No anomaly for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
#                                                         " at the "+ str(n-i) + "-candidate level. " + remainingWinners[j] + 
#                                                           " still wins after change in dropout order." )
                                                    else:
                                                        modifiedNum = gap - check
                                                        print("MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                        " at the "+ str(n-i) + "-candidate level!!!! ")
                                                        data1.write("MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                        " at the "+ str(n-i) + "-candidate level!!!! ")
                                                        data1.write("Modifying all 1-, 2-, 3- and 4-rankings and " + str(modifiedNum) + 
                                                        " 1-bullet votes makes " + remainingWinners[j]+ " lose their seat.") 
                                                        data1.write("Original winners were " + str(remainingWinners))
                                                        data1.write("New winners are " + str(win1))
                                                        data1.write("\n")
                                                        
                                                        display(tempFrame1)


                                                else:
                                                    # modify all modifiableVotes C_k  votes in reduced_df to become W_j C_k 
                                                    for z in range(len(tempFrame1)):
                                                        currentBallot = tempFrame1.at[z,'ballot']
                                                        if len(currentBallot) == 2:
                                                            if currentBallot[0]==checkables[k] and currentBallot[1]!=remainingWinners[j]: #Note: should not need and
                                                                tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                                gap = gap - tempFrame1.at[z,'Count']

                                                    #CHECK THE BULLET VOTES, length 3
                                                    # modifiableVotesBullet3 = sum of all ballots that are just C_k ___ C_i  
                                                    modifiableVotesBullet3 = 0 # = sum of all bullet votes w/ length 3
                                                    for z in range(len(tempFrame1)):
                                                        currentBallot = tempFrame1.at[z,'ballot']
                                                        if len(currentBallot) == 3:
                                                            if currentBallot[0]==checkables[k] and remainingWinners[j] not in currentBallot: 
                                                                    modifiableVotesBullet3 += tempFrame1.at[z,'Count']  

                                                    if modifiableVotesBullet3 > gap:  # modify gap of the C_k C_i votes in modified to become 
                                                                                # W_j C_k C_i votes.

                                                        check = copy.deepcopy(gap)
                                                        for z in range(len(tempFrame1)): 
                                                            if check>=0:
                                                                currentBallot = tempFrame1.at[z,'ballot']
                                                                if len(currentBallot) == 3:
                                                                    if currentBallot[0]==checkables[k] and remainingWinners[j] not in currentBallot: #Note: should not need and
                                                                        if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                                            tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                                            check = check - tempFrame1.at[z,'Count']

                                                                        else: #modify only check+1 such ballots
                                                                            #take check+1 ballots from current ballot
                                                                            tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                                            #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                                            tempFrame1.loc[len(tempFrame1)] = [modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot']), check+1]
                                                                            check = -1

                                                        # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                                        # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                                        # level. votes modified to..."
                                                        win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota) #n-i?
                                                        if remainingWinners[j] in win1:
                                                            pass

#                                                             print("No anomaly for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
#                                                             " at the "+ str(n-i) + "-candidate level. " + remainingWinners[j] + 
#                                                               " still wins after change in dropout order." )
                                                        else:
                                                            modifiedNum = gap - check
                                                            print("MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                            " at the "+ str(n-i) + "-candidate level!!!! ")
                                                            #print("Modifying all 1-, 2-, 3-, 4- and 5-rankings and " + str(modifiedNum) + 
                                                            #" 3-bullet votes makes " + remainingWinners[j]+ " lose their seat.") 
                                                            #print("Original winners were " + str(remainingWinners))
                                                            #print("New winners are " + str(win1))
                                                            #print('Modified election is')
                                                            data1.write("upward MONOTONICITY ANOMALY for " + remainingWinners[j] + " with " + checkables[k] + " under " + loser + 
                                                            " at the "+ str(n-i) + "-candidate level for election " + str(filename))
                                                            data1.write("Modifying all 1-, 2-, 3-, 4- and 5-rankings and " + str(modifiedNum) + 
                                                            " 3-bullet votes makes " + remainingWinners[j]+ " lose their seat.") 
                                                            data1.write("Original winners were " + str(remainingWinners))
                                                            data1.write("New winners are " + str(win1))
                                                            data1.write("\n")
                                                            display(tempFrame1)


                                                    else:
                                                        # modify all modifiableVotes C_k  votes in reduced_df to become W_j C_k 
                                                        for z in range(len(tempFrame1)):
                                                            currentBallot = tempFrame1.at[z,'ballot']
                                                            if len(currentBallot) == 3:
                                                                if currentBallot[0]==checkables[k] and remainingWinners[j] not in currentBallot: 
                                                                    tempFrame1.at[z,'ballot'] = modifyUp(remainingWinners[j],tempFrame1.at[z,'ballot'])
                                                                    gap = gap - tempFrame1.at[z,'Count']


## downward monotonicity
#################################################################################
# STV that gives more outputs for downward mono search
def STV3(frame3,n,S):
    frame2 = frame3.copy(deep=True)
    """Inputs election, n=number of candidates, S=number of seats.  Returns winners, losers=eliminated, 
      dictionary of pre-elimination data, dictionary of winners at each step of elimination"""
    #Quota is floor of number of ballots divided by (S+1), plus 1
    winners=[]
    hopefuls=[]
    eliminatedCand=[]
    elimFrames={}
    tempWinners={}
    quota=math.floor(sum(frame2['Count'])/(S+1))+1
    
    list1=[]
    for k in range(len(frame2)):
        if frame2.at[k,'ballot']!='':
            if frame2.at[k,'ballot'][0] in list1:
                pass
            else:
                list1.append(frame2.at[k,'ballot'][0])
        if len(frame2.at[k,'ballot'])>1:
            if frame2.at[k,'ballot'][1] in list1:
                pass
            else:
                list1.append(frame2.at[k,'ballot'][1])
        if len(frame2.at[k,'ballot'])>2:
            if frame2.at[k,'ballot'][2] in list1:
                pass
            else:
                list1.append(frame2.at[k,'ballot'][2])
        if len(frame2.at[k,'ballot'])>3:
            if frame2.at[k,'ballot'][3] in list1:
                pass
            else:
                list1.append(frame2.at[k,'ballot'][3])
    cand_dict={}
    n = len(list1)
    S=1
    for i in range(n):#n
        cand_dict[i]=list1[i]
        hopefuls.append(list1[i])
    
    #Get each candidate's initial number of votes this round
    vote_counts={}
    
    for k in range(len(frame2)):
            if frame2.at[k,'ballot']!='':
                if frame2.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                else:
                    vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']
    # print(vote_counts)
    max_count=max(vote_counts.values())
    while len(winners)<S:
        
        max_count=max(vote_counts.values())
        #somebody is elected and we have to transfer their votes
        if max_count>=quota:
            #There might be multiple people elected this round; save them as a sorted dictionary
            votes_for_winners={k:vote_counts[k] for k in vote_counts.keys() if vote_counts[k]>=quota }
            votes_for_winners=dict(sorted(votes_for_winners.items(),key=lambda x: x[1], reverse=True))
            
            #If we try to elect too many people, need to drop someone who surpassed quota
            if len(winners)+len(votes_for_winners)>S:
                
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
                    if len(winners)==S:
                        return winners, eliminatedCand, elimFrames, tempWinners
                    
                    weight=truncate((vote_counts[cand]-quota)/vote_counts[cand],5)
                    
                    for k in range(len(frame2)):
                        if frame2.at[k,'ballot']!='':
                            if frame2.at[k,'ballot'][0]==cand:
                                
                                frame2.at[k,'Count']=frame2.at[k,'Count']*weight
                                for x in winners:
                                    if x in frame2.at[k,'ballot']:
                                        frame2.at[k,'ballot']=frame2.at[k,'ballot'].replace(x,'')
                            else:
                                if cand in frame2.at[k,'ballot']:
                                     frame2.at[k,'ballot']=frame2.at[k,'ballot'].replace(cand,'')
                    votes_for_winners.pop(cand)
                    vote_counts={}
                    
                    for k in range(len(frame2)):
                        if frame2.at[k,'ballot']!='':
                            if frame2.at[k,'ballot'][0] in vote_counts.keys():
                                vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                            else:
                                vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']

                    votes_for_winners={k:vote_counts[k] for k in vote_counts.keys() if vote_counts[k]>=quota }
                    votes_for_winners=dict(sorted(votes_for_winners.items(),key=lambda x: x[1], reverse=True))
                    print(vote_counts)
                    for cand in votes_for_winners.keys():
                        if cand not in winners:
                            winners.append(cand)
                            hopefuls.remove(cand)
                    if len(winners)==S:
                        return winners, eliminatedCand, elimFrames, tempWinners
                    frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
        #nobody is elected by surpassing quota, but the number
        #of candidates left equals S
        elif len(hopefuls)+len(winners)==S:
            return winners+hopefuls, eliminatedCand, elimFrames, tempWinners
        
        #remove weakest cand and transfer their votes with weight one
        else:
            min_count=min(i for i in vote_counts.values() if i>0)
            count=0
            for votes in vote_counts:
                if votes==min_count:
                    count+=1
            if count>1:
                print("tie in candidate to remove")
                return

            eliminated_cand = list(vote_counts.keys())[list(vote_counts.values()).index(min_count)] #took str() away
            
            elimFrames[len(eliminatedCand)]=frame2.copy(deep=True)
            tempWinners[len(eliminatedCand)]=copy.deepcopy(winners)
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
            vote_counts={}
           
            for k in range(len(frame2)):
                if frame2.at[k,'ballot']!='':
                    if frame2.at[k,'ballot'][0] in vote_counts.keys():
                        vote_counts[frame2.at[k,'ballot'][0]]+=frame2.iloc[k]['Count']
                    else:
                        vote_counts[frame2.at[k,'ballot'][0]]=frame2.iloc[k]['Count']
            #print(vote_counts)
            max_count=max(vote_counts.values())
            if len(hopefuls)+len(winners)==S:
                return winners+hopefuls, eliminatedCand, elimFrames, tempWinners
            frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
    return winners, eliminatedCand, elimFrames, tempWinners

#Note: this code looks for downward anomalies caused by changes in the dropout order, specifically raising
# the next eliminated candidate up in enough votes so that someone else drops out.  Also does for seat order
def reduceFrame(frame1, losers):
    """inputs an election dataframe and a list of losers.  Returns a dictionary with keys 0,1,
    2,...,i, ...,n and values that are a dataframe with i losers removed"""
    frame = frame1.copy(deep=True)
    reducedFrames={}
    for i in range(len(losers)):
        if i==0:
            reducedFrames[0] = frame.copy(deep=True) #make tempFrame same as original

        else:
            tempFrame1 = frame.copy(deep=True) #make tempFrame same as original
            for j in range(i):
                for k in range(len(frame)): #remove first i losers from tempFrame
                    if losers[j] in tempFrame1.iloc[k]['ballot']:
                        tempFrame1.at[k,'ballot']=tempFrame1.at[k,'ballot'].replace(losers[j],'')
            reducedFrames[i] = tempFrame1.copy(deep=True) 
    return reducedFrames

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

#This is the main downward anomaly program.  this one is for individual elections (spits out lots of data)
def downDropoutAnomSearch(filename, profile, voteMethod): 
    """inputs: dataframe of election, n= number of candidates, S= number of seats
    runs election to find winners/hopefuls/losers, then identifies and makes vote swaps to find 
    downward monotonicity anomalies connected to change in dropout order.  
    Returns if an anomaly exists, and how anomaly happens"""
    cand_List1=[] #make list of all candidates, only candidates listed in top 4 ranks
    for k in range(len(profile)):
        if profile.at[k,'ballot']!='':
            if profile.at[k,'ballot'][0] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][0])
        if len(profile.at[k,'ballot'])>1:
            if profile.at[k,'ballot'][1] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][1])
        if len(profile.at[k,'ballot'])>2:
            if profile.at[k,'ballot'][2] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][2])
        if len(profile.at[k,'ballot'])>3:
            if profile.at[k,'ballot'][3] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][3])
    n = len(cand_List1)
#     winner = voteMethod(profile) #get winner of election using whatever election method #, len(cand_List1), 1
#     W=winner[0]
#     #print("Winner is " + str(W))
    
#     losers = []
#     for X in cand_List1:
#         if X!=W:
#             losers.append(X)
    
    quota=math.floor(sum(profile['Count'])/(S+1))+1 #calculate quota   
    #print("Original frame is ")
    #display(frame)
    winners, losers, elimFrames, winners_dict=STV3(profile,n,1)
     #Run original STV election, 
    #print("Original winners are:")
    #print(winners)
    #returns list of
    #winners and losers (people eliminated at some point)    
   
    for i in range(len(losers)): #function removes i losers from original data frame, 
        # then searches for all possible anomalies at a given level<=n, right before each "loser" is 
        # eliminated.  outputs if anomaly occurs, and if so, how...could also output other information
        #print("")
        #print("Results at the " +str(n-i)+"-candidate level for Elimination Order anomaly:")
        
        #now have temporary dataframe with i losers removed, check for anomaly at (n-i)-cand level
        tempFrame = elimFrames[i].copy(deep=True) #actual data before ith cand is removed 
        tempWinners = copy.deepcopy(winners_dict[i])
        remainingWinners = copy.deepcopy(winners) #put in all winners
        for y in range(len(tempWinners)):
            remainingWinners.remove(tempWinners[y]) #remove people who already got seats
        # remainingWinners are the future winners who are still in the election
        loser = losers[i]
        print("The loser is " + str(loser))
        vote_counts={}
        for k in range(len(tempFrame)):
            if tempFrame.at[k,'ballot']!='':
                if tempFrame.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[tempFrame.at[k,'ballot'][0]]+=tempFrame.iloc[k]['Count']
                else:
                    vote_counts[tempFrame.at[k,'ballot'][0]]=tempFrame.iloc[k]['Count']
        
        checkables = list(vote_counts.keys())
        checkables.remove(loser)
        for j in range(len(remainingWinners)):
            checkables.remove(remainingWinners[j])
        print("The checkables are ")
        print(checkables)
        loser_gap = {} #change to loser_gap? Do for ALL candidates?
        print("The loser gaps are ")
        print(loser_gap)
        for x in range(len(vote_counts)):
            loser_gap[list(vote_counts.keys())[x]]=vote_counts[list(vote_counts.keys())[x]]-vote_counts[loser]                                                                           
        second = get_secondLow(loser_gap) #lowest should be loser: 0
        
        gap = vote_counts[second]-vote_counts[loser]
        print("The gap is " + str(gap))
        
        for k in range(len(checkables)):
            # search for C_j anomalies by modifying gap+1 C_j L or C_j votes to L C_j votes
            if (vote_counts[checkables[k]]-vote_counts[second]) <= (loser_gap[second]+1):
                print("No anomaly for " + checkables[k] + ".  Will be eliminated if modify enough votes.")
                #the above should eliminate loser and second from options
            else: #modify loser_gap+1 C_j L to L C_j votes
                tempFrame1 = tempFrame.copy(deep=True)
                modifiableVotes1 = 0 #modifiableVotes= sum of all ballots that start with C_k L
                for z in range(len(tempFrame1)):
                    currentBallot = tempFrame1.at[z,'ballot']
                    try:
                        currentBallot[1]
                    except: 
                        continue
                    else:
                        if currentBallot[0]==checkables[k] and currentBallot[1]==loser:
                            modifiableVotes1 += tempFrame1.at[z,'Count']
                print("Modifiable votes are " + str(modifiableVotes1) + " and gap is " + str(gap))
                if modifiableVotes1 > gap:
                    check = copy.deepcopy(gap)
                    for z in range(len(tempFrame1)):
                        if check>=0:
                            currentBallot = tempFrame1.at[z,'ballot']
                            try:
                                currentBallot[1]
                            except: 
                                continue
                            else:
                                if currentBallot[0]==checkables[k] and currentBallot[1]==loser:
                                    if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                        tempFrame1.at[z,'ballot'] = swapOneTwo(tempFrame1.at[z,'ballot'])
                                        check = check - tempFrame1.at[z,'Count']
                                    else: #modify only check+1 such ballots
                                        tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
                                        #now add new line to frame with modified ballot
                                        tempFrame1.loc[len(tempFrame1)] = [swapOneTwo(tempFrame1.at[z,'ballot']), check+1]
                                        check = -1
                                else:
                                    pass
                    # Run STV election on modifed election.  Check to see if W_j is in new winners list
                    # if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate level.
                    # votes modified to 1 ranking"
                    win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota) 
                    if checkables[k] in win1:
                        print("DOWNWARD MONOTONICITY ANOMALY for " + checkables[k]+". "  + "Change " + str(gap+1) +" "+ checkables[k]+loser + 
                        "__ votes to " +loser + checkables[k]+ "__ and " + checkables[k] + 
                          " becomes a winner." )
                        print("Original winners were " + str(remainingWinners))
                        print("New winners are " + str(win1))
                        print('Modified election is')
                        display(tempFrame1)
                    else:
                        print("No anomaly for " + checkables[k]+" after modifying "+ str(gap +1) + " votes from "+ 
                              checkables[k]+loser + "__ to " +loser + checkables[k]+"__. ")
                        
                else:
                        # modify all modifiableVotes C_k L votes in reduced_df to become L C_k 
                    for z in range(len(tempFrame1)):
                        currentBallot = tempFrame1.at[z,'ballot']
                        try:
                            currentBallot[1]
                        except: 
                            continue
                        else:
                            if currentBallot[0]==checkables[k] and currentBallot[1]==loser:
                                tempFrame1.at[z,'ballot'] = swapOneTwo(tempFrame1.at[z,'ballot'])
                                gap = gap - tempFrame1.at[z,'Count']

                    #CHECK THE BULLET VOTES
                    modifiableVotesBullet1 = 0 # = sum of all bullet votes w/ length 1
                    for z in range(len(tempFrame1)):
                        currentBallot = tempFrame1.at[z,'ballot']
                        if len(currentBallot) == 1:
                            if currentBallot[0]==checkables[k]:
                                modifiableVotesBullet1 += tempFrame1.at[z,'Count']  
                    print("Modifiable bullet votes are " + str(modifiableVotesBullet1) + " and gap is " + str(gap))
                    if modifiableVotesBullet1 > gap: 
                        check = copy.deepcopy(gap)
                        for z in range(len(tempFrame1)):
                            if check>=0:
                                currentBallot = tempFrame1.at[z,'ballot']
                                if len(currentBallot) == 1:
                                    if currentBallot[0]==checkables[k]:
                                        if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                            tempFrame1.at[z,'ballot'] = swapOneLoser(tempFrame1.at[z,'ballot'], loser)
                                            check = check - tempFrame1.at[z,'Count']

                                        else: #modify only check+1 such ballots
                                            #take check+1 ballots from current ballot
                                            tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                            #make new ballot with winner moved up, add line to election frame with check+1 as count
                                            tempFrame1.loc[len(tempFrame1)] = [swapOneLoser(tempFrame1.at[z,'ballot'], loser), check+1]
                                            check = -1
                                    else:
                                        pass
                        # Run STV election on modifed election.  Check to see if C_k is in new winners list
                        # if yes, report anomaly "
                        win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota) #n-i?
                        if checkables[k] in win1:
                            print("DOWNWARD MONOTONICITY ANOMALY for " + checkables[k]+". "  + "Change all "+ checkables[k]+loser + 
                            "__ and  "  + str(gap+1) + " "+ checkables[k]+ " votes to " +loser + checkables[k]+ "__ and " + checkables[k] + 
                              " becomes a winner." )
                            print("Original winners were " + str(remainingWinners))
                            print("New winners are " + str(win1))
                            print('Modified election is')
                            display(tempFrame1)
                        else:
                            print("No anomaly for " + checkables[k] + " after modifying "+ str(gap+1) + " votes from "+ 
                                  checkables[k]+loser + "__ or " +checkables[k]+ " to " +loser + checkables[k]+"__. ")
                    else:
                        print("No anomaly for " + checkables[k] +". Not enough votes to change dropout order." )

#Downard program to run over all elections (spits out data to a file)
def downDropoutAnomSearch_all(filename, profile, voteMethod): #all printing removed, add files to print
    """inputs: file name, dataframe of election, voting method
    runs IRV election to find winners/hopefuls/losers, then identifies and makes vote swaps to find 
    downward monotonicity anomalies connected to change in dropout order.  
    Returns if an anomaly exists, and how anomaly happens"""
    cand_List1=[] #make list of all candidates, only candidates listed in top 4 ranks
    for k in range(len(profile)):
        if profile.at[k,'ballot']!='':
            if profile.at[k,'ballot'][0] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][0])
        if len(profile.at[k,'ballot'])>1:
            if profile.at[k,'ballot'][1] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][1])
        if len(profile.at[k,'ballot'])>2:
            if profile.at[k,'ballot'][2] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][2])
        if len(profile.at[k,'ballot'])>3:
            if profile.at[k,'ballot'][3] in cand_List1:
                pass
            else:
                cand_List1.append(profile.at[k,'ballot'][3])
    n = len(cand_List1)
    S = 1
#     winner = voteMethod(profile) #get winner of election using whatever election method #, len(cand_List1), 1
#     W=winner[0]
#     #print("Winner is " + str(W))
    
#     losers = []
#     for X in cand_List1:
#         if X!=W:
#             losers.append(X)
    
    quota=math.floor(sum(profile['Count'])/(S+1))+1 #calculate quota   
    #print("Original frame is ")
    #display(frame)
    winners, losers, elimFrames, winners_dict=STV3(profile,n,1)
     #Run original STV election, 
    #print("Original winners are:")
    #print(winners)
    #returns list of
    #winners and losers (people eliminated at some point)    
   
    for i in range(len(losers)): #function removes i losers from original data frame, 
        # then searches for all possible anomalies at a given level<=n, right before each "loser" is 
        # eliminated.  outputs if anomaly occurs, and if so, how...could also output other information
        #print("")
        #print("Results at the " +str(n-i)+"-candidate level for Elimination Order anomaly:")
        
        #now have temporary dataframe with i losers removed, check for anomaly at (n-i)-cand level
        tempFrame = elimFrames[i].copy(deep=True) #actual data before ith cand is removed 
        tempWinners = copy.deepcopy(winners_dict[i])
        remainingWinners = copy.deepcopy(winners) #put in all winners
        for y in range(len(tempWinners)):
            remainingWinners.remove(tempWinners[y]) #remove people who already got seats
        # remainingWinners are the future winners who are still in the election
        loser = losers[i]
        #print("The loser is " + str(loser))
        vote_counts={}
        for k in range(len(tempFrame)):
            if tempFrame.at[k,'ballot']!='':
                if tempFrame.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[tempFrame.at[k,'ballot'][0]]+=tempFrame.iloc[k]['Count']
                else:
                    vote_counts[tempFrame.at[k,'ballot'][0]]=tempFrame.iloc[k]['Count']
        
        checkables = list(vote_counts.keys())
        checkables.remove(loser)
        for j in range(len(remainingWinners)):
            checkables.remove(remainingWinners[j])
        #print("The checkables are ")
        #print(checkables)
        loser_gap = {} #change to loser_gap? Do for ALL candidates?
        #print("The loser gaps are ")
        #print(loser_gap)
        for x in range(len(vote_counts)):
            loser_gap[list(vote_counts.keys())[x]]=vote_counts[list(vote_counts.keys())[x]]-vote_counts[loser]                                                                           
        second = get_secondLow(loser_gap) #lowest should be loser: 0
        
        gap = vote_counts[second]-vote_counts[loser]
        #print("The gap is " + str(gap))
        
        for k in range(len(checkables)):
            # search for C_j anomalies by modifying gap+1 C_j L or C_j votes to L C_j votes
            if (vote_counts[checkables[k]]-vote_counts[second]) <= (loser_gap[second]+1):
                pass
                #print("No anomaly for " + checkables[k] + ".  Will be eliminated if modify enough votes.")
                #the above should eliminate loser and second from options
            else: #modify loser_gap+1 C_j L to L C_j votes
                tempFrame1 = tempFrame.copy(deep=True)
                modifiableVotes1 = 0 #modifiableVotes= sum of all ballots that start with C_k L
                for z in range(len(tempFrame1)):
                    currentBallot = tempFrame1.at[z,'ballot']
                    try:
                        currentBallot[1]
                    except: 
                        continue
                    else:
                        if currentBallot[0]==checkables[k] and currentBallot[1]==loser:
                            modifiableVotes1 += tempFrame1.at[z,'Count']
                #print("Modifiable votes are " + str(modifiableVotes1) + " and gap is " + str(gap))
                if modifiableVotes1 > gap:
                    check = copy.deepcopy(gap)
                    for z in range(len(tempFrame1)):
                        if check>=0:
                            currentBallot = tempFrame1.at[z,'ballot']
                            try:
                                currentBallot[1]
                            except: 
                                continue
                            else:
                                if currentBallot[0]==checkables[k] and currentBallot[1]==loser:
                                    if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                        tempFrame1.at[z,'ballot'] = swapOneTwo(tempFrame1.at[z,'ballot'])
                                        check = check - tempFrame1.at[z,'Count']
                                    else: #modify only check+1 such ballots
                                        tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
                                        #now add new line to frame with modified ballot
                                        tempFrame1.loc[len(tempFrame1)] = [swapOneTwo(tempFrame1.at[z,'ballot']), check+1]
                                        check = -1
                                else:
                                    pass
                    # Run STV election on modifed election.  Check to see if W_j is in new winners list
                    # if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate level.
                    # votes modified to 1 ranking"
                    win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota) 
                    if checkables[k] in win1:
                        print("DOWNWARD MONOTONICITY ANOMALY in " + str(filename) + " for " +  checkables[k]+". "  + "Change " + str(gap+1) +" "+ checkables[k]+loser + 
                        "__ votes to " +loser + checkables[k]+ "__ and " + checkables[k] + 
                          " becomes a winner." )
                        print("Original winners were " + str(remainingWinners))
                        print("New winners are " + str(win1))
                        data1.write("\n")
                        data1.write("DOWNWARD MONOTONICITY ANOMALY in " + str(filename) + " for " + 
                                checkables[k]+". "  + "Change " + str(gap+1) +" "+ checkables[k]+loser + 
                        "__ votes to " +loser + checkables[k]+ "__ and " + checkables[k] + 
                          " becomes a winner." )
                        data1.write("Original winners were " + str(remainingWinners))
                        data1.write("New winners are " + str(win1))
                        data1.write("\n")
                        #print('Modified election is')
                        #display(tempFrame1)
                    else:
                        pass
                        #print("No anomaly for " + checkables[k]+" after modifying "+ str(gap +1) + " votes from "+ 
                         #     checkables[k]+loser + "__ to " +loser + checkables[k]+"__. ")
                        
                else:
                        # modify all modifiableVotes C_k L votes in reduced_df to become L C_k 
                    for z in range(len(tempFrame1)):
                        currentBallot = tempFrame1.at[z,'ballot']
                        try:
                            currentBallot[1]
                        except: 
                            continue
                        else:
                            if currentBallot[0]==checkables[k] and currentBallot[1]==loser:
                                tempFrame1.at[z,'ballot'] = swapOneTwo(tempFrame1.at[z,'ballot'])
                                gap = gap - tempFrame1.at[z,'Count']

                    #CHECK THE BULLET VOTES
                    modifiableVotesBullet1 = 0 # = sum of all bullet votes w/ length 1
                    for z in range(len(tempFrame1)):
                        currentBallot = tempFrame1.at[z,'ballot']
                        if len(currentBallot) == 1:
                            if currentBallot[0]==checkables[k]:
                                modifiableVotesBullet1 += tempFrame1.at[z,'Count']  
                    #print("Modifiable bullet votes are " + str(modifiableVotesBullet1) + " and gap is " + str(gap))
                    if modifiableVotesBullet1 > gap: 
                        check = copy.deepcopy(gap)
                        for z in range(len(tempFrame1)):
                            if check>=0:
                                currentBallot = tempFrame1.at[z,'ballot']
                                if len(currentBallot) == 1:
                                    if currentBallot[0]==checkables[k]:
                                        if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                            tempFrame1.at[z,'ballot'] = swapOneLoser(tempFrame1.at[z,'ballot'], loser)
                                            check = check - tempFrame1.at[z,'Count']

                                        else: #modify only check+1 such ballots
                                            #take check+1 ballots from current ballot
                                            tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                            #make new ballot with winner moved up, add line to election frame with check+1 as count
                                            tempFrame1.loc[len(tempFrame1)] = [swapOneLoser(tempFrame1.at[z,'ballot'], loser), check+1]
                                            check = -1
                                    else:
                                        pass
                        # Run STV election on modifed election.  Check to see if C_k is in new winners list
                        # if yes, report anomaly "
                        win1 = STV_temp(tempFrame1, len(vote_counts), S, tempWinners, quota) #n-i?
                        if checkables[k] in win1:
                            print("DOWNWARD MONOTONICITY ANOMALY in " + str(filename) + " for " +  checkables[k]+". "  + "Change all "+ checkables[k]+loser + 
                            "__ and  "  + str(gap+1) + " "+ checkables[k]+ " votes to " +loser + checkables[k]+ "__ and " + checkables[k] + 
                              " becomes a winner." )
                            print("Original winners were " + str(remainingWinners))
                            print("New winners are " + str(win1))
                            data1.write("\n")
                            data1.write("DOWNWARD MONOTONICITY ANOMALY in " + str(filename) + " for " +  checkables[k]+". "  + "Change all "+ checkables[k]+loser + 
                            "__ and  "  + str(gap+1) + " "+ checkables[k]+ " votes to " +loser + checkables[k]+ "__ and " + checkables[k] + 
                              " becomes a winner." )
                            data1.write("Original winners were " + str(remainingWinners))
                            data1.write("New winners are " + str(win1))
                            data1.write("\n")
                            #print('Modified election is')
                            #display(tempFrame1)
                        else:
                            pass
                            #print("No anomaly for " + checkables[k] + " after modifying "+ str(gap+1) + " votes from "+ 
                                  #checkables[k]+loser + "__ or " +checkables[k]+ " to " +loser + checkables[k]+"__. ")
                    else:
                        pass
                        #print("No anomaly for " + checkables[k] +". Not enough votes to change dropout order." )
##################################################################################



########################################################
##### Execute code
########################################################



##### Compare election method in code to prefvoting, etc
# cand_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
#               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
#               'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
#               'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

# base_name = '../../raw_data/preference_profiles/scotland'
# lxn_names = []

# for folder_name in reversed(os.listdir(base_name)):
# # for folder_name in ['aberdeenshire22']:
#     for file_name in os.listdir(base_name+'/'+folder_name):
#         file_path = base_name+'/'+folder_name+'/'+file_name 
        
#         # print(file_path)
#         lxn_names.append(file_path)
    
#         sys.stdout.write('\r')
#         sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
#         sys.stdout.flush()
        
#         File=open(file_path,'r')
#         lines = File.readlines()
        
#         data = createBallotDF(lines)
#         data_copy = data.copy(deep = True)
        
#         cand_num = num_cands=int(lines[0][0:lines[0].find(' ')])
        
#         my_code_winner = minimax(data_copy, cand_num)[0]
        
#         # run prefvoting method
#         ballots_2, cand_num_2, seat_num_2 = get_ballots(file_path)
#         rankings = []
#         rcounts = []
#         for ballot, count in ballots_2.items():
#             rcounts.append(count)
#             ranking = {}
#             for indx, cand in enumerate(ballot):
#                 ranking[cand] = indx+1
#             for cand in range(1, cand_num_2+1):
#                 if cand not in ballot:
#                     ranking[cand] = len(ballot)+1
#             rankings.append(ranking)
#         pv_prof = ProfileWithTies(rankings, rcounts)
#         pv_win = pv_mm(pv_prof)[0]-1
#         pv_win_let = cand_names[pv_win]
        
#         if pv_win_let != my_code_winner:
#             print(file_name)
#             print(pv_win_let, my_code_winner)
        
        
        
        
        
        
        
## run specific anomaly search
# anomaly_list = NS_buck_search_shell()
anomaly_list = LNH_search_shell(LNH_search, Borda_OM, truncBalAtL)




# lxn_names = []
# anomaly_lxns = []

# base_name = '../../raw_data/preference_profiles/scotland'

# for folder_name in os.listdir(base_name):
# # for folder_name in ['aberdeenshire22']:
#     for file_name in os.listdir(base_name+'/'+folder_name):
#         file_path = base_name+'/'+folder_name+'/'+file_name
#         # if len(file_path)>180:
#         #     print(file_path)
#         #     continue
        
#         lxn_names.append(file_path)   
#         # print(file_path)
    
#         sys.stdout.write('\r')
#         sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
#         sys.stdout.flush()
        
#         File=open(file_path,'r')
#         #print(str(filename))
#         lines=File.readlines()

#         first_space=lines[0].find(' ')
#         num_cands=int(lines[0][0:first_space])
#         if num_cands>52:
#             print("Cannot handle this many candidates in election " + str(file_name) + ".  Has " + 
#                   str(num_cands) + " candidates.")
#             continue
#         #num_seats=int(lines[0][first_space+1])  was not working for civs data because of 1.0
#             # and don't need because num-seats is always 1 for this analysis
            
#         data = createBallotDF(lines)
#         data_copy=data.copy(deep=True)

#         anomaly_data = noShowAnomSearch(data_copy, num_cands, 1)
#         if anomaly_data:
#             anomaly_lxns.append((file_path, anomaly_data))









## test all method, lnh combos
# full_results = []
# lxn_methods = [Borda_PM, Borda_OM, Borda_AVG, IRV, minimax, ranked_pairs, bucklin, plurality, smith_irv, smith_minimax, plurality_runoff]
# lnh_versions = [truncBalAtW, truncBalAtL, buryWinBal, boostLinBal]

# for method in lxn_methods:
#     for lnh in lnh_versions:
#         print(method.__name__, lnh.__name__)
#         full_results.append([method.__name__, lnh.__name__, search_shell_test(LNH_search, method, lnh)])
















###################################
##### Compare my functions to results file
###################################

# region_name = 'scotland'

# pref_folder_base = '../../raw_data/preference_profiles/'
# base_name = pref_folder_base + region_name

# current_folder = '../../results/current/'
# current_results_path = current_folder+region_name

# current_results = pd.read_csv(current_results_path+'.csv')
# lxn_list = list(current_results['file'])

# lxn_names = []
# for folder_name in os.listdir(base_name):
#     for file_name in os.listdir(base_name+'/'+folder_name):
#         file_path = base_name+'/'+folder_name+'/'+file_name
        
#         if folder_name+'/'+file_name in lxn_list:
#             current_result_indx = lxn_list.index(folder_name+'/'+file_name)
#         else:
#             # ward_word = file_name[file_name.find('ward'):file_name.find('ward')+7]
#             # current_result_indx = [i for i in range(len(current_results)) if (folder_name in lxn_list[i]) and (ward_word in lxn_list[i])][0]
#             continue
        
#         lxn_names.append(file_path)   
#         # print(file_path)
        
#         # if len(lxn_names)<75:
#         #     continue
    
#         sys.stdout.write('\r')
#         sys.stdout.write(f'Election {len(lxn_names)}'+'         ')
#         sys.stdout.flush()
        
#         File=open(file_path,'r', encoding='utf-8')
#         #print(str(filename))
#         lines=File.readlines()

#         first_space=lines[0].find(' ')
#         num_cands=int(lines[0][0:first_space])
#         if num_cands>52:
#             print("Cannot handle this many candidates in election " + str(file_name) + ".  Has " + 
#                   str(num_cands) + " candidates.")
#             continue
            
#         data = createBallotDF(lines)
        
#         cand_names = lines[-num_cands:]
#         cand_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
#                       'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
#                       'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
#                       'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
#         cand_name_dict = {}
#         for i in range(num_cands):
#             cand_name_dict[cand_letters[i]] = cand_names[i][:-1]

#         #######################################
#         ##### check election data
#         #######################################
#         # if num_cands != current_results.at[current_result_indx, 'numCands']:
#         #     print('#############################')
#         #     print('Different number of candidates')
#         #     print(num_cands, current_results.at[current_result_indx, 'numCands'])
#         #     print(folder_name +'/' + file_name)
#         #     print('#############################')
            
        
#         # my_win_let = plurality(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'plurality']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = plurality(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'plurality'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners plurality')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')
        
#         # my_win_let = IRV(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'IRV']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = IRV(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'IRV'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners IRV')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')
            
#         # my_win_let = Borda_PM(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'borda-pm']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = Borda_PM(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'borda-pm'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners Borda PM')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')
        
#         # my_win_let = Borda_OM(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'borda-om-no-uwi']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = Borda_OM(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'borda-om-no-uwi'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners Borda OM')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')
#         #     # print(breakhere)

#         # my_win_let = Borda_AVG(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'borda-avg-no-uwi']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = Borda_AVG(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'borda-avg-no-uwi'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners Borda AVG')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')

#         # my_win_let = minimax(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'minimax']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = minimax(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'minimax'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners minimax')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')

#         # my_win_let = smith_irv(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'smith_irv']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = smith_irv(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'smith_irv'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners Smith IRV')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')
            
#         # my_win_let = smith_minimax(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'smith-minimax']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = smith_minimax(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'smith-minimax'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners Smith minimax')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')

#         # my_win_let = ranked_pairs(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'ranked-pairs']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = ranked_pairs(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'ranked-pairs'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners Ranked Pairs')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')

#         my_win_let = bucklin(data, num_cands)[0]
#         my_win = cand_name_dict[my_win_let]
#         cr_win = current_results.at[current_result_indx, 'bucklin'][2:-2]
#         if my_win != cr_win:
#             print('#############################')
#             print('Different winners Bucklin')
#             print(my_win)
#             print(cr_win)
#             print(folder_name +'/' + file_name)
#             print(num_cands)
#             print('#############################')

#         # my_win_let = plurality_runoff(data, num_cands)
#         # my_win = [cand_name_dict[x] for x in my_win_let]
#         # cr_win = current_results.at[current_result_indx, 'top-two']
#         # cr_win = cr_win.split("'")
#         # cr_win = [x for x in cr_win if '(' in x]
#         # if set(my_win) != set(cr_win):
#         # # my_win_let = plurality_runoff(data, num_cands)[0]
#         # # my_win = cand_name_dict[my_win_let]
#         # # cr_win = current_results.at[current_result_indx, 'top-two'][2:-2]
#         # # if my_win != cr_win:
#         #     print('#############################')
#         #     print('Different winners plurality runoff')
#         #     print(my_win)
#         #     print(cr_win)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')
            
#         # my_smith, new_profile = restrict_to_smith(data, num_cands)
#         # my_smith = [cand_name_dict[x] for x in my_smith]
#         # cr_smith = current_results.at[current_result_indx, 'smith']
#         # cr_smith = cr_smith.split("'")
#         # cr_smith = [x for x in cr_smith if '(' in x]
#         # if set(my_smith) != set(cr_smith):
#         #     print('#############################')
#         #     print('Different Smith sets')
#         #     print(my_smith)
#         #     print(cr_smith)
#         #     print(folder_name +'/' + file_name)
#         #     print(num_cands)
#         #     print('#############################')
#         #     # print(breakhere)









