def IRV(frame3): #program to run STV election
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


#Cell: import data function

#Code written by Dave McCune

import random
import pandas as pd
import math
import operator
import numpy as np
import copy
import csv

def prefProfileInput(rawData): 
    """Inputs raw preference profile (in standard Scottish form) and returns pandas
    dataframe with ballot and count columns, ballots converted letters from numbers, and number of cands"""
    File=open(rawData,'r') #'moray17-03.blt'    NoShowAnomalyElections/edinburgh17-04.blt
    lines=File.readlines()

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
        data = pd.concat([data, df2], ignore_index=True)
    laterNoHarmTruncAtW(data, IRV)
    return data

#this is what I run to look for LNH anomalies over large data sets
#Run Later No Harm Truncate at W for all
import os
import statistics
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

data1 = open("LNH_TruncAtW_Events.txt", "w")
data2 = open("tooBigForLetters.txt", "w")
data3 = open("LNH_TruncAtW_Murky.txt", "w")

directory='Preference Profiles/scotland' #'Scotland data, LEAP'
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
                data2.write("Cannot handle this many candidates in election " + str(filename) + ".  Has " + 
                      str(num_cands) + " candidates which is more than 52.")
                data2.write("/n")
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
#             if num_cands>15:
#                 print("")
#                 print("Too many candidates in " + str(filename) + ". Has " + str(num_cands) + " candidates.")
#                 print("")
#                 aust3.write("Skipped " + str(filename) + ". Has " + str(num_cands) + " candidates.")
#                 aust3.write("/n")
#                 continue
#            else:
            laterNoHarmTruncAtW_all(filename, data_copy,Borda_PM_mod)
            print(num_elections)
data1.close()
data2.close()
data3.close()


#same as above, but now Truncate at L
#Run Later No Harm Truncate at W for all
import os
import statistics
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

data1 = open("LNH_TruncAtL_BordaPM_Events.txt", "w")
data3 = open("LNH_TruncAtL_Murky.txt", "w")

directory='Preference Profiles/scotland' #'Scotland data, LEAP'
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
#             if num_cands>15:
#                 print("")
#                 print("Too many candidates in " + str(filename) + ". Has " + str(num_cands) + " candidates.")
#                 print("")
#                 aust3.write("Skipped " + str(filename) + ". Has " + str(num_cands) + " candidates.")
#                 aust3.write("/n")
#                 continue
#            else:
            laterNoHarmTruncAtL_all(filename, data_copy,Borda_PM_mod)
            print(num_elections)
data1.close()
#data2.close()
data3.close()


#helper functions
def truncBalAtW(ballot, winner):
    """inputs string (ballot) and a candidate (winner), and truncates the ballot at the winner"""
    if winner in ballot:
        return ballot.split(winner, 1)[0]
    else:
        return ballot

def truncBalAtL(ballot, loser):
    """inputs string (ballot) and a candidate (winner), and truncates the ballot at the winner"""
    if loser in ballot:
        return ballot[:ballot.index(loser)+1]#ballot.split(winner, 1)[0]
    else:
        return ballot


#function for LNH Trunc at W when I want to check one election (spits out more data)
def laterNoHarmTruncAtW(profile, voteMethod): #LNHtruncAtW_AnomSearch_all
    """takes in pandas preference profile, number of cands and election method to get winner W. For each losing candidate L, 
    for all ballots with L and W ranked, where L>W, truncate all ballots at W.  Rerun election
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
    print(cand_List1)
    winner = voteMethod(profile) #get winner of election using whatever election method #, len(cand_List1), 1
    W=winner[0]
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
                if (L in curBal) and (W in curBal) and (curBal.find(L)<curBal.find(W)):
                    mod_frame2.at[k,'ballot'] = truncBalAtW(curBal, W)
        newWinner = voteMethod(mod_frame2)[0]
        if W == newWinner:
            print("No LNH trunc at W anomaly for " + str(L))
        elif L == newWinner:
            print("LNH trunc at W ANOMALY for " + str(L)+ "!!!!!!!  Changing all " + str(L) + 
                  " votes to truncate at the winner " + str(W)+ " makes " + str(L)+ " a winner.")
        else:
            print("LNH trunc at W anomaly is UNCLEAR for " + str(L) + ". New winner is " + str(newWinner))
        

#function for LNH Trunc at L when I want to check one election (spits out more data)
def laterNoHarmTruncAtL(prefProfile,voteMethod):
    """takes in raw profile and election method to get winner W. For each losing candidate L, 
    for all ballots with L ranked, truncate all ballots below L. Rerun election
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
    print(cand_List1)
    winner = voteMethod(profile) #get winner of election using whatever election method #, len(cand_List1), 1
    W=winner[0]
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
                if (L in curBal) and (curBal.find(L)<(len(curBal)+1)):
                    mod_frame2.at[k,'ballot'] = truncBalAtL(curBal, L)
        newWinner = voteMethod(mod_frame2)[0]
        if W == newWinner:
            print("No LNH trunc at L anomaly for " + str(L))
        elif L == newWinner:
            print("LNH trunc at L ANOMALY for " + str(L)+ "!!!!!!!  Changing all " + str(L) + 
                  " votes to truncate at " + str(L)+ " makes " + str(L)+ " a winner instead of " + str(W))
        else:
            print("LNH trunc at L anomaly is UNCLEAR for " + str(L) + ". New winner is " + str(newWinner) +
                " and old winner was " + str(W))


#Dave's Borda_PM code set up to take in preference profiles
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


#same Borda PM code, just set up to spit out more data if I am just looking at one election
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


#code I ran for No-show (with IRV only)
#Cell 1

#Dave's STV election code, modified to give more outputs (specifically losers)

#This code works for No-show anomalies.

import random
import pandas as pd
import math
import operator
import numpy as np
import copy


def truncate(number, digits) -> float: #truncates according to Scotland rules
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def STV3(frame3,n,S): #program to run STV election
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
#     for k in range(len(frame2)):
#         if frame2.at[k,'ballot']!='':
#             if frame2.at[k,'ballot'][0] in list1:
#                 pass
#             else:
#                 list1.append(frame2.at[k,'ballot'][0])
    if len(list1)!=n:
        print("length of list1 is not equal to number of candidates n. Length of list1 = " +str(len(list1)) + 
             " and n = " + str(n))
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
                        hopefuls.remove(cand) #remove winner from hopefuls list
                
                while len(votes_for_winners)>0:
                    
                    cand=list(votes_for_winners.keys())[0]
    
                    if cand not in winners:
                        winners.append(cand)
                        hopefuls.remove(cand)
                    if len(winners)==S:
                        return winners, eliminatedCand, elimFrames, tempWinners
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
            if len(hopefuls)+len(winners)==S:
                return winners+hopefuls, eliminatedCand, elimFrames, tempWinners
            frame2=pd.DataFrame(frame2.groupby(['ballot'],as_index=False)['Count'].sum())
    return winners, eliminatedCand, elimFrames, tempWinners


#Cell 2

#Dave's STV election code, modified to run after some candidates have been eliminated/elected.  
# Basically the same as STV3, but it only returns the winner of the (modified) election 
import random
import pandas as pd
import math
import operator
import numpy as np


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

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




#Cell 3: 

#Note: this code looks for no-show anomalies caused by changes in the dropout order, specifically removing
# some votes of the form X...H...W... that makes H a winner and W a loser (and only affects those two?)

#“There is a group of n voters who all prefer L_i to W_j (perhaps to differing levels, further explanation
# below**).  When that group of n voters show up to vote, W_j wins a seat and L_i does not.  If that group
# of voters does NOT show up to vote, L_i gets a seat and W_j does not (and we would have to assume here
# that all other winners in the election stay as winners).  Thus that group of voters would be better off
# NOT showing up to vote, because more of their favored candidates** would win if they do not show up than
# win if they DO show up.  “

#Process: identify winners, hopefuls, a loser. Choose a hopeful C_k at a given level with next dropout D.  
# For every other hopeful H_m and winner W_j, try to find enough votes of the form C_k...H_m...(W_j) to 
# remove from the election so that C_k drops out before D.  Rerun election to see if H_m is now a winner 
# if not, no anomaly.  If so, check to see if W_j is NOT a winner anymore.  Report conditional anomaly, 
# along with names of H_m, W_j, old list of winners and new list to see if other winners stay same
import copy


def noShowAnomSearch(filename, frame, n, S): 
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
                                print("")
                                print("")
                                print("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove " + str(gap+1) +" "+ checkables[k]+ 
                                "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot and " +
                                hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
                                print("Original winners were " + str(winners))
                                print("New winners are " + str(win1))
                                print('Election is ' + filename)
                                print("")
                                print("")
                                aust1.write("\n")
                                aust1.write("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove all " + checkables[k]+ 
                                "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot AND " +
                                str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] + " votes and " +
                                hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
                                aust1.write("Original winners were " + str(winners))
                                aust1.write("New winners are " + str(win1))
                                aust1.write('Election is ' + filename)
                                aust1.write("\n")
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
                                print("")
                                print("")
                                print("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove all " + checkables[k]+ 
                                "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot AND " +
                                str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] + " votes and " +
                                hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
                                print("Original winners were " + str(winners))
                                print("New winners are " + str(win1))
                                print('Election is ' + filename)
                                print("")
                                print("")
                                aust.write("\n")
                                aust1.write("NO SHOW ANOMALY for " + hopefuls[m]+". "  + "Remove all " + checkables[k]+ 
                                "..."+ hopefuls[m] + "__ votes where " + winners[j] + " is not in the ballot AND " +
                                str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] + " votes and " +
                                hopefuls[m] + " becomes a winner and " + winners[j] + " loses their seat." )
                                aust1.write("Original winners were " + str(winners))
                                aust1.write("New winners are " + str(win1))
                                aust1.write('Election is ' + filename)
                                aust1.write("\n")
                                
                            else:
                                continue
                                #print("No anomaly for " + hopefuls[m] +" after removing all " + checkables[k]+ 
                                #"..."+ hopefuls[m] + " votes where " + winners[j] + " is not in the ballot AND " +
                                #str(gap+1)+ " " +checkables[k] + "..." + hopefuls[m] + "..."+ winners[j] +
                                #" votes. ")
                     
                        
                       
                           
                        ###END of this no-show check


#Cell to check all elections for no-show
import os
import statistics
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

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


#upward monotonicity check (for IRV)
#Cell 2: Monotonicity anomaly function defined 
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


#                                                     print(remainingWinners[j]+" cannot overcome gap with "+ checkables[k] + 
#                                                           " when modified up to 5 rankings and 3 bullet votes under " + 
#                                                           loser + ". REACHED END OF CODE.")

