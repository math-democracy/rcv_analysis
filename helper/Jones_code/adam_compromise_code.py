
#Code written by Dave McCune and Adam Graham-Squire

import random
import pandas as pd
import math
import operator
import numpy as np
import copy


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def STVcheck(frame3,n,S):
    frame2 = frame3.copy(deep=True)
    """Inputs election, n=number of candidates, S=number of seats.  Returns winners, losers=eliminated, 
      dictionary of pre-elimination data, dictionary of winners at each step of elimination"""
    #Quota is floor of number of ballots divided by (S+1), plus 1
    winners=[]
    hopefuls=[]
    eliminatedCand=[]
    elimFrames={}
    #tempWinners={}
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
    n = len(list1)
    S = 1
    cand_dict={}
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
    #print(vote_counts)
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
                        if cand in hopefuls:
                            hopefuls.remove(cand)
                    if len(winners)==S:
                        return winners
                    
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
                    #print(vote_counts)
                    for cand in votes_for_winners.keys():
                        if cand not in winners:
                            winners.append(cand)
                            if cand in hopefuls:
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
            #tempWinners[len(eliminatedCand)]=copy.deepcopy(winners)
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
                return winners+hopefuls
            frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
    return winners
#May need to change what is returned!!!!!


#Cell 2: 

#Code written by Adam Graham-Squire

#Note: this code looks for strategic voting anomalies--specifically, when moving a losing candidate (N)
# to a higher position above another losing candidate (B) makes N a winner.  That is, B could strategically 
# vote N higher on some ballots and get their second choice winner instead of something lower
import copy

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

def swapLoserUp(string,loser): 
    """Inputs string and loser.  moves loser up to top of ballot if loser is
    on ballot, otherwise adds loser to top of ballot"""
    #netring = string.copy(deep=True) 
    if string.find(loser) == -1:
        string = loser + string
    else:
        string = loser + string.replace(loser, "")
    return string


def stratVotingSearchTotal(election, frame, n, S): 
    """inputs: dataframe of election, n= number of candidates, S= number of seats
    runs election to find winners/losers, then checks at each level of elimination if winner is at the n-1 
    position in ranking.  If so, swaps ballots B...C to LB...C to make winner drop out before next eliminated 
    candidate L. If C is now winner, anomaly occurs.  
    Prints if an anomaly exists, and how anomaly happens""" 
    quota=math.floor(sum(frame['Count'])/(S+1))+1 #calculate quota   
    winners, losers, elimFrames=STV3(frame,n,1) #Run original IRV election
     
    #print("Original winners are:")
    #print(winners)
   
    for i in range(len(losers)): #function does NOT look for Cond winner anomalies
        #print("")
        #print("Results at the " +str(n-i)+"-candidate level for Strategic Voting Total anomaly:")
        #now have temporary dataframe with i losers removed, now check for anomaly at (n-i)-cand level
        tempFrame = elimFrames[i].copy(deep=True) #actual data before ith cand is removed 
       
        loser = losers[i]
        winner = winners[0]
        vote_counts={}
        for k in range(len(tempFrame)):
            if tempFrame.at[k,'ballot']!='':
                if tempFrame.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[tempFrame.at[k,'ballot'][0]]+=tempFrame.iloc[k]['Count']
                else:
                    vote_counts[tempFrame.at[k,'ballot'][0]]=tempFrame.iloc[k]['Count']
        secondLast = get_secondLow(vote_counts) #get second to last candidate
        if secondLast != winner: #check if second to last is  NOT eventual IRV winner
            pass
            #print("No anomaly because " + str(winner) + " is not second to last place.")
        else: #check to see if moving loser up can change dropout order
            gap = vote_counts[winner]-vote_counts[loser]
            checkables = list(vote_counts.keys())
            checkables.remove(loser)
            checkables.remove(winner)
            for k in range(len(checkables)):
                if (vote_counts[checkables[k]]-vote_counts[winner])<=gap:
                    #print("No anomaly because " + str(checkables[k]) + " is too close to winner.")
                    continue
                # search for anomalies by modifying gap+1 C_k...B_j votes to L C_k ...B_j votes
                newCheckables = copy.deepcopy(checkables)
                newCheckables.remove(checkables[k])
                newCheckables.append(loser)
                for j in range(len(newCheckables)):
                    tempFrame1 = tempFrame.copy(deep=True)
                    modifiableVotes1 = 0 #modifiableVotes= sum of all ballots that start with C_k L
                    for z in range(len(tempFrame1)): #calculate number of C_k ...B_j votes
                        currentBallot = tempFrame1.at[z,'ballot']
                        try:
                            currentBallot[1]
                        except: 
                            continue
                        else:
                            if currentBallot[0]==checkables[k] and currentBallot.find(newCheckables[j])!=-1 and currentBallot.find(winner)==-1: #form C_k...B_j with no W on ballot
                                modifiableVotes1 += tempFrame1.at[z,'Count']
                            elif currentBallot[0]==checkables[k] and currentBallot.find(newCheckables[j])!=-1 and currentBallot.find(winner)!=-1 and (currentBallot.index(newCheckables[j]) < currentBallot.index(winner)): 
                            #form C_k...B_j...W
                                modifiableVotes1 += tempFrame1.at[z,'Count']
                    if modifiableVotes1 > gap: #if number of modifiable votes > gap, execute program
                        check = copy.deepcopy(gap)
                        for z in range(len(tempFrame1)):
                            if check>=0:
                                currentBallot = tempFrame1.at[z,'ballot']
                                try:
                                    currentBallot[0]
                                except: 
                                    continue
                                else:
                                    #if (currentBallot[0]==checkables[k] and currentBallot.find(newCheckables[j])!=-1 and currentBallot.find(winner)==-1) or (currentBallot[0]==checkables[k] and currentBallot.find(newCheckables[j])!=-1 and currentBallot.find(winner)!=-1 and (currentBallot.index(newCheckables[j]) < currentBallot.index(winner))):
                                    if currentBallot[0]==checkables[k] and currentBallot.find(newCheckables[j])!=-1 and (currentBallot.find(winner)==-1 or (currentBallot.find(winner)!=-1 and (currentBallot.index(newCheckables[j])) < currentBallot.index(winner))):
                                        if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                            tempFrame1.at[z,'ballot'] = swapLoserUp(tempFrame1.at[z,'ballot'],loser)
                                            check = check - tempFrame1.at[z,'Count']
                                        else: #modify only check+1 such ballots
                                            tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
                                            #now add new line to frame with modified ballot
                                            tempFrame1.loc[len(tempFrame1)] = [swapLoserUp(tempFrame1.at[z,'ballot'],loser), check+1]
                                            check = -1
                                    else:
                                        pass
                        # Run IRV election on modifed data.  Check to see if B_j is new winner
                        # if yes, report anomaly for C_k under L for B_j at (n-i)-candidate level.
                        newQuota = math.floor(sum(tempFrame1['Count'])/(S+1))+1 #calculate quota
                        win1 = STVcheck(tempFrame1, len(vote_counts), 1)
                        if newCheckables[j] in win1:
                            data1.write("\n")
                            data1.write("STRATEGIC VOTING EVENT Total in election " + str(election) + "  Change " +
                                        str(gap+1) + " " + checkables[k] + "..." + newCheckables[j] + 
                                  " (with no winner in ... votes) to " +loser + 
                                  checkables[k] + "..." + newCheckables[j] + "__ and " + newCheckables[j] +
                                  " becomes a winner.")
                            print("STRATEGIC VOTING EVENT Total in election " + str(election) + "  Change " +
                                  str(gap+1) + " " + checkables[k] + "..." + newCheckables[j] + 
                                  " (with no winner in ... votes) to " +loser + 
                                  checkables[k] + "..." + newCheckables[j] + "__ and " + newCheckables[j] +
                                  " becomes a winner.")
                            data1.write("Original winners were " + str(winner))
                            data1.write("New winners are " + str(win1))
                            data1.write("\n")
                            #print('Modified election is')
                            #display(tempFrame1)
                        elif winner in win1:
                            pass
                        else:
                            data3.write("POTENTIAL STRATEGIC VOTING EVENT Total in election " + str(election) + "  Change " +
                                        str(gap+1) +" "+ checkables[k]+loser + 
                            "__ votes to " +loser + checkables[k]+ "__ and " + loser + 
                              " could become a winner?" )
                            data3.write("Original winners were " + str(winner))
                            data3.write("New winners are " + str(win1))
                            data3.write("\n")
                            #print("No anomaly for " + checkables[k]+" after modifying "+ str(gap +1) + " votes from "+ 
                             #     checkables[k]+loser + "__ to " +loser + checkables[k]+"__. ")
#                         if newCheckables[j] in win1:
#                             print("STRATEGIC VOTING ANOMALY Total: Change " + str(gap+1) +
#                                   " "+ checkables[k] + "..." + newCheckables[j] + 
#                                   " (with no winner in ... votes) to " +loser + 
#                                   checkables[k] + "..." + newCheckables[j] + "__ and " + newCheckables[j] +
#                                   " becomes a winner.")
#                             print("Original winners were " + str(winner))
#                             print("New winners are " + str(win1))
#                             #print('Modified election is')
#                             #display(tempFrame1)
#                         else:
#                             print("No anomaly for " + checkables[k]+" after modifying "+ str(gap +1) + " votes from "+ 
#                                 checkables[k] + "..." + newCheckables[j] + " to " +
#                                   loser + checkables[k]+ "...")
                                  
                                  


                        ###END of this strategic voting check


import random
import pandas as pd
import math
import operator
import numpy as np
import copy

def IRV(frame3): #program to run IRV election
    frame2 = frame3.copy(deep=True)
    """Inputs election, n=number of candidates, S=number of seats=1.  Returns winner, 
    as a list with a single entry"""
    #Quota is floor of number of ballots divided by (S+1), plus 1
    winners=[]
    hopefuls=[]
    eliminatedCand=[]
    elimFrames={}
    tempWinners={}
    quota=math.floor(sum(frame2['Count'])/(2))+1
    
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
#     for k in range(len(frame2)):
#         if frame2.at[k,'ballot']!='':
#             if frame2.at[k,'ballot'][0] in list1:
#                 pass
#             else:
#                 list1.append(frame2.at[k,'ballot'][0])
#     if len(list1)!=n:
#         print("length of list1 is not equal to number of candidates n. Length of list1 = " +str(len(list1)) + 
#              " and n = " + str(n))
    cand_dict={}
    for i in range(len(list1)):#range(n)
        cand_dict[i]=list1[i]
        hopefuls.append(list1[i]) #create initial list of hopefuls
 
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



#Adam mod of Dave's code:
def Borda_PM_data(profile):
    
    #find candidates from profile
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
    
    print(cand_List1)
    #get number of candidates
    num_cands = len(cand_List1)
#     if len(cands_to_keep) < num_cands:
#         all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
#         updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

#         new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
#         new_profile['Count'] = pref_profile['Count']
#         pref_profile = new_profile
    
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
    print(cand_scores)
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return winners


#Adam mod of Dave's code:
def Borda_PM_mod(profile):
    
    #find candidates from profile
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
    #get number of candidates
    num_cands = len(cand_List1)
#     if len(cands_to_keep) < num_cands:
#         all_columns_but_count = [col for col in pref_profile.columns if col != 'Count']
#         updated_ranks = pref_profile[all_columns_but_count].apply(lambda row: update_rankings(row, cands_to_keep), axis=1)

#         new_profile = pd.DataFrame(updated_ranks.tolist(), columns=all_columns_but_count)
#         new_profile['Count'] = pref_profile['Count']
#         pref_profile = new_profile
    
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
    #print(cand_scores)
    max_score = max(cand_scores.values())
    winners = [cand for cand, score in cand_scores.items() if score == max_score]

    return winners


def compromiseRaw_all(election, profile, voteMethod): #LNHtruncAtW_AnomSearch_all
    """takes in pandas preference profile, number of cands and election method to get winner W. For each losing candidate L, 
    for all ballots with L ranked, truncate all ballots below L.  Rerun election
    to find winner.  If W=winner, no anomaly.  If L=winner, LNH anomaly.  If X=winner, ???"""
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
    #print(cand_List1)
    winner = voteMethod(profile) #get winner of election using whatever election method #, len(cand_List1), 1
    W=winner[0]
    #print("Winner is " + str(W))
    
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
                if ((L in curBal) and (W in curBal) and (curBal.find(L)<curBal.find(W))) or ((L in curBal) and (W not in curBal)):
                    mod_frame2.at[k,'ballot'] = moveToTop(curBal, L)
        newWinner = voteMethod(mod_frame2)[0]
        if W == newWinner:
            pass
            #print("No LNH trunc at W anomaly for " + str(L))
        elif L == newWinner:
            data1.write("\n")
            data1.write("In election " + str(election) + " , Raw COMPROMISE EVENT for " + str(L)+ 
                    "!!!! For all appropriate votes, moving " + str(L)+ " to the top makes " + str(L)+ 
                    " a winner instead of previous winner " + str(W) + ".")
            data1.write("\n")
#             print("LNH trunc at W ANOMALY for " + str(L)+ "!!!!!!!  Changing all " + str(L) + 
#                   " votes to truncate at the winner " + str(W)+ " makes " + str(L)+ " a winner.")
        else:
            data3.write("\n")
            data3.write("In election " + str(election) + 
                        " , Raw COMPROMISE EVENT is UNCLEAR for moving up " + str(L) + 
                        ". New winner is " + str(newWinner) + " and old winner was " + str(W))
            #print("LNH trunc at W anomaly is UNCLEAR for " + str(L) + ". New winner is " + str(newWinner))
        
    
File=open('Preference Profiles/american/Alaska/Alaska_08162022_HouseofRepresentativesSpecial.csv','r') #'moray17-03.blt'    NoShowAnomalyElections/edinburgh17-04.blt
lines=File.readlines() #Burlington/Burlington_03032009_Mayor.csv

first_space=lines[0].find(' ')

num_cands=int(lines[0][0:first_space])
num_seats=int(lines[0][first_space+1])

column_names=['ballot','Count']
data=pd.DataFrame(columns = column_names)
for k in range(1,len(lines)):
    if lines[k][0]=='0':
        break
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
    #pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    data = pd.concat([data, df2], ignore_index=True)
compromiseRaw(data, IRV) #Borda_PM_data

#results=Borda_PM_data(data)
#print(data)


#Run Compromise code for all
import os
import statistics
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

data1 = open("CompromiseMore_IRV_Events.txt", "w")
data3 = open("CompromiseMore_IRV_Murky.txt", "w")

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
#                 print("Cannot handle this many candidates in election " + str(filename) + ".  Has " + 
#                       str(num_cands) + " candidates.")
#                 data2.write("Cannot handle this many candidates in election " + str(filename) + ".  Has " + 
#                       str(num_cands) + " candidates which is more than 52.")
#                 data2.write("/n")
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
            compromiseRaw_all(filename, data_copy, IRV)
            stratVotingSearchOneTwo(filename, data_copy,num_cands,1)
            stratVotingSearchTotal(filename, data_copy,num_cands,1)
            print(num_elections)
            
data1.close()
#data2.close()
data3.close()
