#All monotonicity and compromise checks

#Cell 1

#Code written by Dave McCune and Adam Graham-Squire

import random
import pandas as pd
import math
import operator
import numpy as np
import copy


def IRV3(frame3):
    frame2 = frame3.copy(deep=True)
    """Inputs election, Returns winners, losers=eliminated candidates, 
      dictionary of pre-elimination data"""#, dictionary of winners at each step of elimination
    winners=[]
    hopefuls=[]
    eliminatedCand=[]
    elimFrames={}
    tempWinners={}
    quota=math.floor(sum(frame2['Count'])/(2))+1
    
    list1=[] #gather all the candidate names
    for k in range(len(frame2)):
        for i in range(len(frame2.at[k,'ballot'])):
            if frame2.at[k,'ballot'][i] not in list1:
                list1.append(frame2.at[k,'ballot'][i])
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
    
    max_count=max(vote_counts.values())
    while len(winners)<1:
        
        max_count=max(vote_counts.values())
        
        if max_count>=quota: #somebody is elected 
            #There might be multiple people elected this round; save them as a sorted dictionary
            votes_for_winners={k:vote_counts[k] for k in vote_counts.keys() if vote_counts[k]>=quota }
            votes_for_winners=dict(sorted(votes_for_winners.items(),key=lambda x: x[1], reverse=True))
            
            #If we try to elect too many people, error
            if len(winners)+len(votes_for_winners)>S:
                print("Error in tabulation.  Multiple winners found.")
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
                    if len(winners)==1:
                        return winners, eliminatedCand, elimFrames #, tempWinners (don't need tempWinners?)
                    
        #nobody is elected by surpassing quota, but the number
        #of candidates left equals S
        elif len(hopefuls)+len(winners)==1:
            return winners+hopefuls, eliminatedCand, elimFrames #, tempWinners
        
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
            if len(hopefuls)+len(winners)==1:
                return winners+hopefuls, eliminatedCand, elimFrames #, tempWinners
            frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
    return winners, eliminatedCand, elimFrames #, tempWinners


#Cell 2: 

#Note: this code looks for downward anomalies caused by changes in the dropout order, specifically raising
# the next eliminated candidate up in enough votes so that someone else drops out.  Also does for seat order
import copy
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

def downDropoutAnomSearch(filename, profile): #streamlined version (really only works for IRV)
    """inputs: name of election, dataframe of election, voting method
    runs election to find winners/hopefuls/losers, then identifies and makes vote swaps to find 
    downward monotonicity anomalies connected to change in dropout order.  
    Returns if an anomaly exists, and how anomaly happens"""
    cand_List1=[] #make list of all candidates, only candidates listed in top 4 ranks
    for k in range(len(profile)):
        for i in range(len(profile.at[k,'ballot'])):
            if profile.at[k,'ballot'][i] not in cand_List1:
                cand_List1.append(profile.at[k,'ballot'][i])
    n = len(cand_List1)

    
    quota=math.floor(sum(profile['Count'])/(2))+1 #calculate quota   
    
    winners, losers, elimFrames=IRV3(profile) #note that losers is list in order of dropout
   
    for i in range(len(losers)): #function removes i losers from original data frame, 
        # then searches for all possible anomalies at a given level<=n, right before each "loser" is 
        # eliminated.  outputs if anomaly occurs, and if so, how...could also output other information
        #print("")
        #print("Results at the " +str(n-i)+"-candidate level for Elimination Order anomaly:")
        
        #now have temporary dataframe with i losers removed, check for anomaly at (n-i)-cand level
        tempFrame = elimFrames[i].copy(deep=True) #actual data before ith cand is removed 
        loser = losers[i]
        
        vote_counts={}
        for k in range(len(tempFrame)):
            if tempFrame.at[k,'ballot']!='':
                if tempFrame.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[tempFrame.at[k,'ballot'][0]]+=tempFrame.iloc[k]['Count']
                else:
                    vote_counts[tempFrame.at[k,'ballot'][0]]=tempFrame.iloc[k]['Count']
        
        checkables = list(vote_counts.keys())
        checkables.remove(winners[0])
        checkables.remove(loser)
        
        loser_gap = {} 
        
        for x in range(len(vote_counts)):
            loser_gap[list(vote_counts.keys())[x]]=vote_counts[list(vote_counts.keys())[x]]-vote_counts[loser]                                                                           
        second = get_secondLow(loser_gap) #lowest should be loser: 0
        
        gap = vote_counts[second]-vote_counts[loser]
        
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
                    win1, foo1, foo2 = IRV3(tempFrame1)#win1 = IRV_check(tempFrame1) #also try win1, thing1, thing2 = IRV3(tempFrame1) 
                    #print("New winner is " + str(win1))
                    #print("Checkable is " + str(checkables[k]))
                    if checkables[k] in win1:
                        print("DOWNWARD MONOTONICITY ANOMALY for " + checkables[k]+". "  + "Change " + str(gap+1) +" "+ checkables[k]+loser + 
                        "__ votes to " +loser + checkables[k]+ "__ and " + checkables[k] + 
                          " becomes a winner." )
                        print("Original winner was " + str(winners))
                        print("New winner is " + str(win1))
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
                        win1, foo1, foo2  = IRV3(tempFrame1)#win1 = IRV_check(tempFrame1) 
                        if checkables[k] in win1:
                            print("DOWNWARD MONOTONICITY ANOMALY for " + checkables[k]+". "  + "Change all "+ checkables[k]+loser + 
                            "__ and  "  + str(gap+1) + " "+ checkables[k]+ " votes to " +loser + checkables[k]+ "__ and " + checkables[k] + 
                              " becomes a winner." )
                            print("Original winner was " + str(winners))
                            print("New winner is " + str(win1))
                            print('Modified election is')
                            display(tempFrame1)
                        else:
                            print("No anomaly for " + checkables[k] + " after modifying "+ str(gap+1) + " votes from "+ 
                                  checkables[k]+loser + "__ or " +checkables[k]+ " to " +loser + checkables[k]+"__. ")
                    else:
                        print("No anomaly for " + checkables[k] +". Not enough votes to change dropout order." )

                    ###END of this downward check


Cell 2: 

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

def truncBalAtW(ballot, winner):
    """inputs string (ballot) and a candidate (winner), and truncates the ballot at the winner"""
    if winner in ballot:
        return ballot.split(winner, 1)[0]
    else:
        return ballot

def moveToTop(ballot, loser):
    if loser in ballot:
        return str(loser) + str(ballot.replace(loser,''))
    else:
        return ballot
    """takes in a ballot and candidate, and moves that candidate to top of ballot"""

def stratVotingSearchTotal(election, frame): 
    """inputs: dataframe of election, n= number of candidates, S= number of seats
    runs election to find winners/losers, then checks at each level of elimination if winner is at the n-1 
    position in ranking.  If so, swaps ballots B...C to LB...C to make winner drop out before next eliminated 
    candidate L. If C is now winner, anomaly occurs.  
    Prints if an anomaly exists, and how anomaly happens""" 
    
    #Note about code: Should it only look for situations when moving up the loser makes the LOSER win?  Right 
    # now it allows for more than that.
    
    quota=math.floor(sum(frame['Count'])/(2))+1 #calculate quota   
    winners, losers, elimFrames=IRV3(frame) #Run original IRV election
    cand_List1=[] #make list of all candidates, only candidates listed in top 4 ranks
    for k in range(len(frame)):
        for i in range(len(frame.at[k,'ballot'])):
            if frame.at[k,'ballot'][i] not in cand_List1:
                cand_List1.append(frame.at[k,'ballot'][i])
    n = len(cand_List1)
     
    #print("Original winners are:")
    #print(winners)
   
    for i in range(len(losers)): #function does NOT look for Cond winner anomalies
        print("")
        print("Results at the " +str(n-i)+"-candidate level for Strategic Voting Total anomaly:")
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
            print("No anomaly because " + str(winner) + " is not second to last place.")
            pass
        else: #check to see if moving loser up can change dropout order
            gap = vote_counts[winner]-vote_counts[loser]
            checkables = list(vote_counts.keys())
            checkables.remove(loser)
            checkables.remove(winner)
            for k in range(len(checkables)):
                if (vote_counts[checkables[k]]-vote_counts[winner])<=gap:
                    print("No anomaly because " + str(checkables[k]) + " is too close to winner.")
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
                        newQuota = math.floor(sum(tempFrame1['Count'])/(2))+1 #calculate quota
                        win1, foo1, foo2 = IRV3(tempFrame1)
                        if newCheckables[j] in win1:
#                             #data1.write("\n")
#                             #data1.write("STRATEGIC VOTING EVENT Total in election " + str(election) + "  Change " +
#                                         str(gap+1) + " " + checkables[k] + "..." + newCheckables[j] + 
#                                   " (with no winner in ... votes) to " +loser + 
#                                   checkables[k] + "..." + newCheckables[j] + "__ and " + newCheckables[j] +
#                                   " becomes a winner.")
                            print("STRATEGIC VOTING EVENT Total in election " + str(election) + "  Change " +
                                  str(gap+1) + " " + checkables[k] + "..." + newCheckables[j] + 
                                  " (with no winner in ... votes) to " +loser + 
                                  checkables[k] + "..." + newCheckables[j] + "__ and " + newCheckables[j] +
                                  " becomes a winner.")
#                             data1.write("Original winners were " + str(winner))
#                             data1.write("New winners are " + str(win1))
#                             data1.write("\n")
                            #print('Modified election is')
                            #display(tempFrame1)
                        elif winner in win1:
                            pass
                        else:
#                             data3.write("POTENTIAL STRATEGIC VOTING EVENT Total in election " + str(election) + "  Change " +
#                                         str(gap+1) +" "+ checkables[k]+loser + 
#                             "__ votes to " +loser + checkables[k]+ "__ and " + loser + 
#                               " could become a winner?" )
#                             data3.write("Original winners were " + str(winner))
#                             data3.write("New winners are " + str(win1))
#                             data3.write("\n")
                            print("No anomaly for " + checkables[k]+" after modifying "+ str(gap +1) + " votes from "+ 
                                  checkables[k]+loser + "__ to " +loser + checkables[k]+"__. ")
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


def compromiseRaw_IRV(election, profile): #LNHtruncAtW_AnomSearch_all
    """takes in pandas preference profile and election method to get winner W. For each losing candidate L, 
    for all ballots with L and W ranked, where L>W, move L to top of ballot.  Rerun election
    to find winner.  If W=winner, no anomaly.  If L=winner, LNH anomaly.  If X=winner, ???"""
    cand_List1=[] #make list of all candidates
    for k in range(len(profile)):
        for i in range(len(profile.at[k,'ballot'])):
            if profile.at[k,'ballot'][i] not in cand_List1:
                cand_List1.append(profile.at[k,'ballot'][i])
    n = len(cand_List1)
    
    winner, foo1, foo2 = IRV3(profile)
    #winner = voteMethod(profile) #get winner of election using whatever election method #, len(cand_List1), 1
    W=winner[0] #maybe need to make this not a list?
    print("Winner is " + str(W))
    
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
        newWinner, foo1, foo2 = IRV3(mod_frame2)
        newW = newWinner[0]
        if W == newW:
            print("No compromise event for " + str(L))
        elif L == newW:
            print("")
            print("COMPROMISE EVENT for " + str(L)+ "in election: " + str(election) + " . Moving up all appropriate " + str(L) + 
                  " rankings makes " + str(L)+ " a winner instead of the old winner " + str(W) )
            print("")
        else:
            print("Compromise event is UNCLEAR for raising up " + str(L) + ". New winner is " + str(newWinner) + 
                  " and the old winner was " + str(W) )



def noShowAnomSearch(filename, frame): 
    """inputs: dataframe of election, n= number of candidates, S= number of seats
    runs election to find winners/losers/frames, then identifies and eliminates votes to find 
    No Show anomalies connected to change in dropout order.  
    outputs if an anomaly exists, and how anomaly happens""" 
    print("lets do this")
    quota=math.floor(sum(frame['Count'])/(2))+1 #calculate quota   
    winners, losers, elimFrames=IRV3(frame) #Run original STV election, 
    winner=winners[0]
    print("Original winners are: ")
    print(winners) 
    cand_List1=[]
    for k in range(len(frame)):
        for i in range(len(frame.at[k,'ballot'])):
            if frame.at[k,'ballot'][i] not in cand_List1:
                cand_List1.append(frame.at[k,'ballot'][i])
    n = len(cand_List1)
    for i in range(len(losers)): #function removes i losers from original data frame, 
        # then searches for all possible anomalies at a given level<=n, right before each "loser" is 
        # eliminated.  outputs if anomaly occurs, and if so, how
        
        #now have temporary dataframe with i losers removed, now check for anomaly at (n-i)-cand level
        tempFrame = elimFrames[i].copy(deep=True)
        #tempWinners = copy.deepcopy(winners_dict[i]) #candidates who have already won a seat at this point
        loser = losers[i] #loser is the candidate about to be eliminated
        vote_counts={}
        
        for k in range(len(tempFrame)):
            if tempFrame.at[k,'ballot']!='':
                if tempFrame.at[k,'ballot'][0] in vote_counts.keys():
                    vote_counts[tempFrame.at[k,'ballot'][0]]+=tempFrame.iloc[k]['Count']
                else:
                    vote_counts[tempFrame.at[k,'ballot'][0]]=tempFrame.iloc[k]['Count']
        print("")
        print("Out of " + str(n) + " candidates, results at the " +str(len(vote_counts))+"-candidate level for Elimination Order anomaly:")
        
        checkables = list(vote_counts.keys())
        checkables.remove(loser)#these are the candidates we want to check for anomalies, need to remove winners
        
        if winner in checkables:
            checkables.remove(winner)
        
        
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
            #all for winner, not winners[j]
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
                        if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winner not in currentBallot:
                            modifiableVotes1 += tempFrame1.at[z,'Count'] #ballots without winner on the ballot
                        if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winner in currentBallot:
                            if currentBallot.index(hopefuls[m])<currentBallot.index(winner):
                                modifiableVotes2 += tempFrame1.at[z,'Count'] #ballots where winner is ranked below
                # check if enough votes to change
                if (modifiableVotes1 + modifiableVotes2) <= (loser_gap[checkables[k]]+1): 
                    continue 
                    print("No anomaly for " + hopefuls[m] + " by removing " + checkables[k] + 
                              ".  Not enough modifiable votes to change dropout order.")

                else: #there are enough modifiable ballots to remove.  Remove them in correct order
                    
                    check = copy.deepcopy(gap)

#                     for z in range(len(tempFrame1)): #These steps remove "best" votes to cause No-show anomaly
#                         # because they are first filtered through a winner getting a seat
#                         if check >= 0:
#                             currentBallot = tempFrame1.at[z,'ballot']
#                             try:
#                                 currentBallot[0]
#                             except: 
#                                 continue
#                             else: #if C_k...H_m... with no W_j on ballot
#                                 if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and (winners[j] not in currentBallot):
#                                     for y in range(len(remainingWinners)):
#                                         if remainingWinners[y] in currentBallot:
#                                             if currentBallot.index(remainingWinners[y])<currentBallot.index(hopefuls[m]):
#                                                 if check - tempFrame1.at[z,'Count']>=-1: #remove all such ballots
#                                                     check = check - tempFrame1.at[z,'Count'] #update check
#                                                     tempFrame1.at[z,'Count'] = 0

#                                                 else: #remove check+1 such ballots
#                                                     tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
#                                                     check = -1

#                                 #if C_k...H_m...W_j
#                                 elif currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winners[j] in currentBallot:
#                                     if currentBallot.index(hopefuls[m])<currentBallot.index(winners[j]):
#                                         for y in range(len(remainingWinners)):
#                                             if remainingWinners[y] in currentBallot:
#                                                 if currentBallot.index(remainingWinners[y])<currentBallot.index(hopefuls[m]):
#                                                     if check - tempFrame1.at[z,'Count']>=-1: #remove all such ballots
#                                                         check = check - tempFrame1.at[z,'Count']
#                                                         tempFrame1.at[z,'Count'] = 0

#                                                     else: #remove check+1 such ballots
#                                                         tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
#                                                         check = -1

#                                 else:
#                                     pass
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
                                    if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winner not in currentBallot:
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

                        win1, foo1, foo2 = IRV3(tempFrame1) #n-i
                        if (hopefuls[m] in win1) and (winner not in win1):# and (set(oldWinners).issubset(set(win1))):
                            print("")
                            print("")
                            print("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove " + str(gap+1) +" "+ checkables[k]+ 
                            "..."+ hopefuls[m] + "__ votes where " + winner + " is not in the ballot and " +
                            hopefuls[m] + " becomes a winner and " + winner + " loses their seat." )
                            print("Original winners were " + str(winner))
                            print("New winners are " + str(win1))
                            print('Election is ' + filename)
                            print("")
                            print("")
#                             data1.write("\n")
#                             data1.write("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove all " + checkables[k]+ 
#                             "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot AND " +
#                             str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] + " votes and " +
#                             hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
#                             data1.write("Original winners were " + str(winners))
#                             data1.write("New winners are " + str(win1))
#                             data1.write('Election is ' + filename)
#                             data1.write("\n")
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
                                if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winner not in currentBallot:
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
                                    if currentBallot[0]==checkables[k] and hopefuls[m] in currentBallot and winner in currentBallot:
                                        if currentBallot.index(hopefuls[m])<currentBallot.index(winner):
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

                        win1, foo1, foo2 = IRV3(tempFrame1)

                        if (hopefuls[m] in win1) and (winner not in win1):# and (set(oldWinners).issubset(set(win1))):
                            print("")
                            print("")
                            print("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove all " + checkables[k]+ 
                            "..."+ hopefuls[m] + "__ votes where " + winner + " is not in the ballot AND " +
                            str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winner + " votes and " +
                            hopefuls[m] + " becomes a winner and " + winner + " loses their seat." )
                            print("Original winners were " + str(winner))
                            print("New winners are " + str(win1))
                            print('Election is ' + filename)
                            print("")
                            print("")
#                                 data1.write("\n")
#                                 data1.write("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove all " + checkables[k]+ 
#                                 "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot AND " +
#                                 str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] + " votes and " +
#                                 hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
#                                 data1.write("Original winners were " + str(winners))
#                                 data1.write("New winners are " + str(win1))
#                                 data1.write('Election is ' + filename)
#                                 data1.write("\n")

                        else:
                            continue
                            #print("No anomaly for " + hopefuls[m] +" after removing all " + checkables[k]+ 
                            #"..."+ hopefuls[m] + " votes where " + winners[j] + " is not in the ballot AND " +
                            #str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] +
                            #" votes. ")



#Upward Monotonicity anomaly function defined 
#Code written by Dave McCune and Adam Graham-Squire

#Note: this code only looks for anomalies cause by changes in the dropout order
import copy

def modifyUp(winner, ballot):
    """inputs a candidate and a ballot, and moves candidate to top of ballot if candidate is in ballot. 
    Otherwise adds candidate to top of ballot"""
    if winner in ballot:
        modified = winner + ballot.replace(winner, "")
    else:
        modified = winner + ballot
    return modified

def upwardMonoAnomSearch(filename, frame): 
    """inputs: dataframe of election, n= number of candidates, S= number of seats
    runs election to find winners/losers/prefData before candidate eliminated, tempWinners,
    then identifies and makes vote swaps to find 
    upward monotonicity anomalies.  Returns if an anomaly exists, and how anomaly happens""" 
    quota=math.floor(sum(frame['Count'])/(2))+1 #calculate quota   
    winners, losers, elimFrames=IRV3(frame) #get election data from IRV3
    winner = winners[0]
    #print("Original winners are ")
    #print(winners)
    cand_List1=[]
    for k in range(len(frame)):
        for i in range(len(frame.at[k,'ballot'])):
            if frame.at[k,'ballot'][i] not in cand_List1:
                cand_List1.append(frame.at[k,'ballot'][i])
    n = len(cand_List1)
    S = 1
    for i in range(len(losers)): #function looks at real data before ith loser drops, 
        # then searches for all possible anomalies at a given level<=n, right before each "loser" is 
        # eliminated.  outputs if anomaly occurs, and if so, how...could also output other information
#         print("")
#         print("Results at the " +str(n-i)+"-candidate level:")
        
        tempFrame = elimFrames[i].copy(deep=True) #actual data before ith cand is removed 
        #tempWinners = copy.deepcopy(winners_dict[i])
        #remainingWinners = copy.deepcopy(winners) #put in all winners
        #for y in range(len(tempWinners)):
         #   remainingWinners.remove(tempWinners[y]) #remove people who already got seats
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
        
        quota_gap[winner]=quota-vote_counts[winner]   
        loser_gap ={} #gap in votes between a candidate and the losing candidate
        for x in range(len(vote_counts)):
            loser_gap[list(vote_counts.keys())[x]]=vote_counts[list(vote_counts.keys())[x]]-vote_counts[loser]                                                                           
                                                                                    
        
        if quota_gap[winner] < 0:
            print("No anomaly for " + str(winner) + ".  Meets quota at " + str(n-i) + "-candidate level." +
                  " NOTE: THIS SHOULD NOT EVER HAPPEN.  IF YOU SEE THIS THEN THERE IS A MISTAKE")
        else:
            checkables = list(vote_counts.keys()) #list of all candidates
            checkables.remove(winner) #remove winner from checkables
            checkables.remove(loser)#remove loser/next eliminated candidate from checkables 

            #we now try to modify C_k...W_j ballots to change dropout order, see if it changes overall result 
            for k in range(len(checkables)): #choose the kth checkable = C_k
                gap = loser_gap[checkables[k]]
                if gap > quota_gap[winner]:
                    pass
#                         print("No anomaly for " + winner + " with " + checkables[k] + " under " + loser + 
#                         " at the "+ str(n-i) + "-candidate level. " + winner + 
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
                            if currentBallot[0]==checkables[k] and currentBallot[1]==winner:
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
                                    if currentBallot[0]==checkables[k] and currentBallot[1]==winner:
                                        if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                            #print("Ballot modified is " + tempFrame1.at[z,'ballot'] + " at line "+ str(z))
                                            tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                            #print("Ballot modified to " + tempFrame1.at[z,'ballot'])
                                            check = check - tempFrame1.at[z,'Count']
                                            #print("check is now " +str(check))
                                        else: #modify only check+1 such ballots
                                            #print("Ballot modified is " + tempFrame1.at[z,'ballot'] + " at line "+ str(z))
                                            tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)
                                            #now add new line to frame with modified ballot
                                            tempFrame1.loc[len(tempFrame1)] = [modifyUp(winner,tempFrame1.at[z,'ballot']), check+1]
                                            check = -1
                                    else:
                                        pass
                        # Run STV election on modifed election.  Check to see if W_j is in new winners list
                        # if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate level.
                        # votes modified to 1 ranking"
                        win1, foo1, foo2 = IRV3(tempFrame1)
                        if winner in win1:
                            pass
#                                 print("No anomaly for " + winner + " with " + checkables[k] + " under " + loser + 
#                                 " at the "+ str(n-i) + "-candidate level. " + winner + 
#                                   " still wins after change in dropout order." )
                        else:
                            modifiedNum = gap - check
#                             data1.write("upward MONOTONICITY ANOMALY for " + winner + " with " + checkables[k] + " under " + loser + 
#                                                         " at the "+ str(n-i) + "-candidate level for election " + str(filename))
                            print("MONOTONICITY ANOMALY for " + winner + " with " + checkables[k] + " under " + loser + 
                            " at the "+ str(n-i) + "-candidate level!!!! Modifying " + str(modifiedNum) +" "+checkables[k]+ winner+"_"  
                              " to " +  winner +checkables[k]+ "_ makes " + winner + " lose their seat.")
#                             data1.write("Original winners were " + str(remainingWinners))
#                             data1.write("New winners are " + str(win1))
#                             data1.write('Modified election is')
#                             data1.write("\n")
#                             display(tempFrame1)

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
                                if currentBallot[0]==checkables[k] and currentBallot[1]==winner:
                                    tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
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
                                if currentBallot[0]==checkables[k] and currentBallot[2]==winner:
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
                                        if currentBallot[0]==checkables[k] and currentBallot[2]==winner:
                                            if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                check = check - tempFrame1.at[z,'Count']

                                            else: #modify only check+1 such ballots
                                                #take check+1 ballots from current ballot
                                                tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                tempFrame1.loc[len(tempFrame1)] = [modifyUp(winner,tempFrame1.at[z,'ballot']), check+1]
                                                check = -1
                                        else:
                                            pass

                            # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                            # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                            # level. votes modified to 2 rankings"
                            win1, foo1, foo2 = IRV3(tempFrame1)
                            if winner in win1:
                                pass

                            else:
                                modifiedNum = gap - check
                                print("MONOTONICITY ANOMALY for " + winner + " with " + checkables[k] + " under " + loser + 
                                " at the "+ str(n-i) + "-candidate level!!!! Modifying " + str(modifiedNum) +" "+checkables[k]+ winner+"_"  
                                  " to " +  winner +checkables[k]+ "_ makes " + winner + " lose their seat.")
                                

                        else: 
                            # modify all modifiableVotes C ___  W votes in reduced_df to become W_j C_k ___
                            for z in range(len(tempFrame1)):
                                currentBallot = tempFrame1.at[z,'ballot']
                                try:
                                    currentBallot[2]
                                except: 
                                    continue
                                else:
                                    if currentBallot[0]==checkables[k] and currentBallot[2]==winner:
                                        tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
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
                                    if currentBallot[0]==checkables[k] and currentBallot[3]==winner:
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
                                            if currentBallot[0]==checkables[k] and currentBallot[3]==winner:
                                                if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                    tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                    check = check - tempFrame1.at[z,'Count']

                                                else: #modify only check+1 such ballots
                                                    #take check+1 ballots from current ballot
                                                    tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                    #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                    tempFrame1.loc[len(tempFrame1)] = [modifyUp(winner,tempFrame1.at[z,'ballot']), check+1]
                                                    check = -1
                                            else:
                                                pass

                                # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                # level. votes modified to 2 rankings"
                                win1, foo1, foo2 = IRV3(tempFrame1)
                                if winner in win1:
                                    pass
                                else:
                                    modifiedNum = gap - check
                                    print("MONOTONICITY ANOMALY for " + winner + " with " + checkables[k] + " under " + loser + 
                                    " at the "+ str(n-i) + "-candidate level!!!! Modifying " + str(modifiedNum) +" "+checkables[k]+ winner+"_"  
                                      " to " +  winner +checkables[k]+ "_ makes " + winner + " lose their seat.")

                            else: 
                                # modify all modifiableVotes_kj1 C ___ ___ W votes in reduced_df to become W_j C_k ___
                                for z in range(len(tempFrame1)):
                                    currentBallot = tempFrame1.at[z,'ballot']
                                    try:
                                        currentBallot[3]
                                    except: 
                                        continue
                                    else:
                                        if currentBallot[0]==checkables[k] and currentBallot[3]==winner:
                                            tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
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
                                        if currentBallot[0]==checkables[k] and currentBallot[4]==winner:
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
                                                if currentBallot[0]==checkables[k] and currentBallot[4]==winner:
                                                    if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                        tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                        check = check - tempFrame1.at[z,'Count']

                                                    else: #modify only check+1 such ballots
                                                        #take check+1 ballots from current ballot
                                                        tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                        #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                        tempFrame1.loc[len(tempFrame1)] = [modifyUp(winner,tempFrame1.at[z,'ballot']), check+1]
                                                        check = -1
                                                else:
                                                    pass

                                    # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                    # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                    # level. votes modified to 2 rankings"
                                    win1, foo1, foo2 = IRV3(tempFrame1)
                                    if winner in win1:
                                        pass

#                                             print("No anomaly for " + winner + " with " + checkables[k] + " under " + loser + 
#                                             " at the "+ str(n-i) + "-candidate level. " + winner + 
#                                               " still wins after change in dropout order." )
                                    else:
                                        modifiedNum = gap - check
                                        print("MONOTONICITY ANOMALY for " + winner + " with " + checkables[k] + " under " + loser + 
                                        " at the "+ str(n-i) + "-candidate level!!!! Modifying " + str(modifiedNum) +" "+checkables[k]+ winner+"_"  
                                          " to " +  winner +checkables[k]+ "_ makes " + winner + " lose their seat.")
                                        


                                else:
                                    # modify all modifiableVotes_kj1 C ___ ___ ___W votes in reduced_df to become W_j C_k ___
                                    for z in range(len(tempFrame1)):
                                        currentBallot = tempFrame1.at[z,'ballot']
                                        try:
                                            currentBallot[4]
                                        except: 
                                            continue
                                        else:
                                            if currentBallot[0]==checkables[k] and currentBallot[4]==winner:
                                                tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
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
                                            if currentBallot[0]==checkables[k] and currentBallot[5]==winner:
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
                                                    if currentBallot[0]==checkables[k] and currentBallot[5]==winner:
                                                        if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                            tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                            check = check - tempFrame1.at[z,'Count']

                                                        else: #modify only check+1 such ballots
                                                            #take check+1 ballots from current ballot
                                                            tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                            #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                            tempFrame1.loc[len(tempFrame1)] = [modifyUp(winner,tempFrame1.at[z,'ballot']), check+1]
                                                            check = -1
                                                    else:
                                                        pass

                                        # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                        # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                        # level. votes modified to 2 rankings"
                                        win1, foo1, foo2 = IRV3(tempFrame1)
                                        if winner in win1:
                                            pass
                                        else:
                                            modifiedNum = gap - check
                                            print("MONOTONICITY ANOMALY for " + winner + " with " + checkables[k] + " under " + loser + 
                                            " at the "+ str(n-i) + "-candidate level!!!! Modifying " + str(modifiedNum) +" "+checkables[k]+ winner+"_"  
                                              " to " +  winner +checkables[k]+ "_ makes " + winner + " lose their seat.")


                                    else:
                                        # modify all modifiableVotes C ... W votes in reduced_df to become W_j C_k ___
                                        for z in range(len(tempFrame1)):
                                            currentBallot = tempFrame1.at[z,'ballot']
                                            try:
                                                currentBallot[5]
                                            except: 
                                                continue
                                            else:
                                                if currentBallot[0]==checkables[k] and currentBallot[5]==winner:
                                                    tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
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
                                                                tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                                check = check - tempFrame1.at[z,'Count']

                                                            else: #modify only check+1 such ballots
                                                                #take check+1 ballots from current ballot
                                                                tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                                #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                                tempFrame1.loc[len(tempFrame1)] = [modifyUp(winner,tempFrame1.at[z,'ballot']), check+1]
                                                                check = -1

                                            # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                            # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                            # level. votes modified to 2 rankings"
                                            win1, foo1, foo2 = IRV3(tempFrame1)
                                            if winner in win1:
                                                pass
                                            else:
                                                modifiedNum = gap - check
                                                print("MONOTONICITY ANOMALY for " + winner + " with " + checkables[k] + " under " + loser + 
                                                " at the "+ str(n-i) + "-candidate level!!!! Modifying " + str(modifiedNum) +" "+checkables[k]+ winner+"_"  
                                                  " to " +  winner +checkables[k]+ "_ makes " + winner + " lose their seat.")


                                        else:
                                            # modify all modifiableVotes C_k  votes in reduced_df to become W_j C_k 
                                            for z in range(len(tempFrame1)):
                                                currentBallot = tempFrame1.at[z,'ballot']
                                                if len(currentBallot) == 1:
                                                    if currentBallot[0]==checkables[k]:
                                                        tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                        gap = gap - tempFrame1.at[z,'Count']

                                            #CHECK THE BULLET VOTES, length 2
                                            # modifiableVotesBullet2 = sum of all ballots that are just C_k C_i  
                                            modifiableVotesBullet2 = 0 # = sum of all bullet votes w/ length 2
                                            for z in range(len(tempFrame1)):
                                                currentBallot = tempFrame1.at[z,'ballot']
                                                if len(currentBallot) == 2:
                                                    if currentBallot[0]==checkables[k] and currentBallot[1]!=winner: 
                                                            modifiableVotesBullet2 += tempFrame1.at[z,'Count']  

                                            if modifiableVotesBullet2 > gap:  # modify gap of the C_k C_i votes in modified to become 
                                                                        # W_j C_k C_i votes.

                                                check = copy.deepcopy(gap)
                                                for z in range(len(tempFrame1)): 
                                                    if check>=0:
                                                        currentBallot = tempFrame1.at[z,'ballot']
                                                        if len(currentBallot) == 2:
                                                            if currentBallot[0]==checkables[k] and currentBallot[1]!=winner: 
                                                                if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                                    tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                                    check = check - tempFrame1.at[z,'Count']

                                                                else: #modify only check+1 such ballots
                                                                    #take check+1 ballots from current ballot
                                                                    tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                                    #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                                    tempFrame1.loc[len(tempFrame1)] = [modifyUp(winner,tempFrame1.at[z,'ballot']), check+1]
                                                                    check = -1

                                                # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                                # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                                # level. votes modified to 2 rankings"
                                                win1, foo1, foo2 = IRV3(tempFrame1)
                                                if winner in win1:
                                                    pass
                                                else:
                                                    modifiedNum = gap - check
                                                    print("MONOTONICITY ANOMALY for " + winner + " with " + checkables[k] + " under " + loser + 
                                                    " at the "+ str(n-i) + "-candidate level!!!! Modifying " + str(modifiedNum) +" "+checkables[k]+ winner+"_"  
                                                      " to " +  winner +checkables[k]+ "_ makes " + winner + " lose their seat.")


                                            else:
                                                # modify all modifiableVotes C_k  votes in reduced_df to become W_j C_k 
                                                for z in range(len(tempFrame1)):
                                                    currentBallot = tempFrame1.at[z,'ballot']
                                                    if len(currentBallot) == 2:
                                                        if currentBallot[0]==checkables[k] and currentBallot[1]!=winner: #Note: should not need and
                                                            tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                            gap = gap - tempFrame1.at[z,'Count']

                                                #CHECK THE BULLET VOTES, length 3
                                                # modifiableVotesBullet3 = sum of all ballots that are just C_k ___ C_i  
                                                modifiableVotesBullet3 = 0 # = sum of all bullet votes w/ length 3
                                                for z in range(len(tempFrame1)):
                                                    currentBallot = tempFrame1.at[z,'ballot']
                                                    if len(currentBallot) == 3:
                                                        if currentBallot[0]==checkables[k] and winner not in currentBallot: 
                                                                modifiableVotesBullet3 += tempFrame1.at[z,'Count']  

                                                if modifiableVotesBullet3 > gap:  # modify gap of the C_k C_i votes in modified to become 
                                                                            # W_j C_k C_i votes.

                                                    check = copy.deepcopy(gap)
                                                    for z in range(len(tempFrame1)): 
                                                        if check>=0:
                                                            currentBallot = tempFrame1.at[z,'ballot']
                                                            if len(currentBallot) == 3:
                                                                if currentBallot[0]==checkables[k] and winner not in currentBallot: #Note: should not need and
                                                                    if check - tempFrame1.at[z,'Count']>=0: #modify all such ballots
                                                                        tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                                        check = check - tempFrame1.at[z,'Count']

                                                                    else: #modify only check+1 such ballots
                                                                        #take check+1 ballots from current ballot
                                                                        tempFrame1.at[z,'Count'] = tempFrame1.at[z,'Count']-(check+1)  
                                                                        #make new ballot with winner moved up, add line to election frame with check+1 as count
                                                                        tempFrame1.loc[len(tempFrame1)] = [modifyUp(winner,tempFrame1.at[z,'ballot']), check+1]
                                                                        check = -1

                                                    # Run STV election on modifed_df_kj2.  Check to see if W_j is in new winners 
                                                    # list. if yes, report "no anomaly for W_j with C_k under L at (n-i)-candidate 
                                                    # level. votes modified to..."
                                                    win1, foo1, foo2 = IRV3(tempFrame1)
                                                    if winner in win1:
                                                        pass
                                                    else:
                                                        modifiedNum = gap - check
                                                        print("MONOTONICITY ANOMALY for " + winner + " with " + checkables[k] + " under " + loser + 
                                                        " at the "+ str(n-i) + "-candidate level!!!! Modifying " + str(modifiedNum) +" "+checkables[k]+ winner+"_"  
                                                          " to " +  winner +checkables[k]+ "_ makes " + winner + " lose their seat.")


                                                else:
                                                    # modify all modifiableVotes C_k  votes in reduced_df to become W_j C_k 
                                                    for z in range(len(tempFrame1)):
                                                        currentBallot = tempFrame1.at[z,'ballot']
                                                        if len(currentBallot) == 3:
                                                            if currentBallot[0]==checkables[k] and winner not in currentBallot: 
                                                                tempFrame1.at[z,'ballot'] = modifyUp(winner,tempFrame1.at[z,'ballot'])
                                                                gap = gap - tempFrame1.at[z,'Count']


#                                                     print(winner+" cannot overcome gap with "+ checkables[k] + 
#                                                           " when modified up to 5 rankings and 3 bullet votes under " + 
#                                                           loser + ". REACHED END OF CODE.")

