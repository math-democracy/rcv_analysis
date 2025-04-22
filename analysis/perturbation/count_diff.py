import os
import sys
sys.path.append(os.path.abspath('/Users/faculty/Documents/rcv_proposal/'))
sys.path.append('/Users/faculty/Documents/rcv_proposal/analysis/smith_restriction/')
#sys.path.append(os.path.abspath('../rcv_proposal/results/current/metadata'))
#sys.path.append(os.path.abspath('../rcv_proposal/helper/Jones_code/'))
import pandas as pd
import main_methods as mm
import ast
import json
from perturbation import swap_perturb

method_map = {"plurality": mm.Plurality,
            "IRV": mm.IRV,
            "top-two": mm.TopTwo,
            "borda-pm": mm.Borda_PM,
            "borda-om": mm.Borda_OM,
            "borda-avg": mm.Borda_AVG,
            "top-3-truncation": mm.Top3Truncation,
            "condorcet": mm.Condorcet,
            "minimax": mm.Minimax,
            "smith_plurality": mm.Smith_Plurality,
            "smith_irv": mm.Smith_IRV,
            "smith-minimax": mm.Smith_Minimax,
            "ranked-pairs": mm.Ranked_Pairs,
            "bucklin": mm.Bucklin,
            "approval": mm.Approval,
            "smith": mm.Smith
        }
'''
def count_diff(loc):
    file = "../../results/current/"+loc+".csv"
    df = pd.read_csv(file,dtype=str)
    
    #voting_methods = [c for c in df.columns if c!='file' and c!='Unnamed: 0' and c!='numCands' and 'rank' not in c]

    CL_losers_elections = {}
    different_smith_results = {}
    for _, row in df.iterrows():
        smith = [x.strip() for x in ast.literal_eval(row['smith']) if x]
        different_smith_results[row['file']] = []
        for method in method_map.keys():
            winners = [x.strip() for x in ast.literal_eval(row[method]) if x]
            for c in winners:
                if c not in smith:
                    if row['file'] in CL_losers_elections:
                        CL_losers_elections[row['file']].append(method)
                    else:
                        CL_losers_elections[row['file']]=[method]
            
            if method == 'smith_irv':
                if set(winners)!= set([x.strip() for x in ast.literal_eval(row['IRV']) if x]):
                    different_smith_results[row['file']].append(method)
            elif method =='smith_plurality':
                if set(winners)!= set([x.strip() for x in ast.literal_eval(row['plurality']) if x]):
                    different_smith_results[row['file']].append(method)
            elif method == 'smith_minimax':
                if set(winners)!= set([x.strip() for x in ast.literal_eval(row['minimax']) if x]):
                    different_smith_results[row['file']].append(method)
        if different_smith_results[row['file']]==[]:
            different_smith_results.pop(row['file'])
    #with open('CL_losers_'+loc+'.json', 'w') as f:
    #    json.dump(CL_losers_elections, f, indent=4)
    with open('Smith_diff_'+loc+'.json', 'w') as f:
        json.dump(different_smith_results, f, indent=4)

#count_diff('australia')
#count_diff('america')
#count_diff('scotland')
#count_diff('civs')

def single_perturbation_hits():
    diff={}
    for k in ['0.1','0.2','0.4','0.6','0.8']:
        diff[k] = {}
        for loc in ['scotland','australia','america','civs']:
            df1 = pd.read_csv("../../results/current/"+loc+".csv",dtype=str)
            df2 = pd.read_csv(k+"_perturbation/"+loc+".csv",dtype=str)
            diff[k][loc]={'smith_irv':0,'smith_plurality':0,'smith-minimax':0}
            for i in range(len(df1)):
                for method in ['smith_irv','smith_plurality','smith-minimax']:
                    if set(ast.literal_eval(df1.loc[i,method]))!=set(ast.literal_eval(df2.loc[i,method])):
                        diff[k][loc][method]+= 1
    with open('perturbation_diff.json', 'w') as f:
        json.dump(diff, f, indent=4)





#single_perturbation_hits()
    
'''
def dist_perturbation_hits(loc,k):
    df1 = pd.read_csv("../../results/current/"+loc+".csv",dtype=str)
    df2 = df1.copy()
    df2 = df2.drop(columns = [col for col in df1.columns if col not in ['file']+[m for m in method_map.keys()]])
    for method in method_map.keys():
         df2[str(k)+'_perturbed_'+method] = [" " for _ in range(len(df2))]
         
    for i in range(len(df2)):
        print(i)
        filepath = df1.loc[i,'file']
        profile = mm.v_profile("../../raw_data/"+loc+"/processed_data/"+filepath,to_remove = ['undervote','overvote','UWI','skipped','Skipped'])
        new_profile = swap_perturb(profile,threshold=k)
        for method in method_map.keys():
            print(method)
            new_winners = method_map[method](new_profile,tiebreak='random')
            df2.loc[i,str(k)+'_perturbed_'+method] = list(new_winners)       
    
    df2.to_csv(str(k)+'_perturbation/_single_'+loc+'.csv')
    
 

def summarize_hits():
    di={}
    
    for loc in ['america','australia','scotland']:
        di[loc]={k:{} for k in [0.1, 0.2, 0.4, 0.6, 0.8]}
        for k in [0.1, 0.2, 0.4, 0.6, 0.8]:
            df = pd.read_csv(str(k)+'_perturbation/dist_'+loc+'.csv')
            hits = [col for col in df.columns if 'hit_percent' in col]
            di[loc][k]={col:0 for col in hits}
            
            for _, row in df.iterrows():
                for col in hits:
                    if row[col]!=0:
                        di[loc][k][col]+=1
                

    with open('dist_perturbation.json', 'w') as f:
        json.dump(di, f, indent=4)

dist_perturbation_hits('america',0.2)

