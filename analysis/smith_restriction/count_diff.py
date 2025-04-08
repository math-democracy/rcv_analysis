import os
import sys
sys.path.append(os.path.abspath('/Users/faculty/Documents/rcv_proposal/'))
#sys.path.append(os.path.abspath('../rcv_proposal/results/current/metadata'))
#sys.path.append(os.path.abspath('../rcv_proposal/helper/Jones_code/'))
import pandas as pd
import main_methods as mm
import ast
import json
from perturbation import swap_perturb
from main_methods import v_profile
from main_methods import Smith_IRV
from main_methods import Smith_Minimax
from main_methods import Smith_Plurality
from main_methods import process_cands
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
            '''for c in winners:
                if c not in smith:
                    if row['file'] in CL_losers_elections:
                        CL_losers_elections[row['file']].append(method)
                    else:
                        CL_losers_elections[row['file']]=[method]
            '''
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
    
def dist_perturbation_hits(loc,k):
    df1 = pd.read_csv("../../results/current/"+loc+".csv",dtype=str)
    df2 = df1.copy()
    df2 = df2.drop(columns = [col for col in df1.columns if col not in ['file','smith','smith_irv','smith_plurality','smith-minimax']])
    hits = []
    for i in range(len(df1)):
        filepath = df1.loc[i,'file']
        cts=[0,0,0]
        smith_winners = ast.literal_eval(df1.loc[i,'smith'])
        if len(smith_winners)<=1:
            cts=[0,0,0]
        else:
            profile = v_profile("../../raw_data/"+loc+"/processed_data/"+filepath,to_remove = ['undervote','overvote','UWI','skipped','Skipped'])
            rest_profile = process_cands(profile,list(smith_winners))
            orig_winners = [set(ast.literal_eval(df1.loc[i,method])) for method in ['smith_irv','smith_plurality','smith-minimax']]
            for _ in range(100):
                profile = swap_perturb(rest_profile,threshold=k)
                irv_winners = Smith_IRV(profile,tiebreak='random')
                plurarity_winners = Smith_Plurality(profile,tiebreak='random')
                minimax_winners = Smith_Minimax(profile,tiebreak='random')
                if irv_winners!=orig_winners[0]:
                    cts[0]+=1
                if plurarity_winners!=orig_winners[1]:
                    cts[1]+=1
                if minimax_winners!=orig_winners[2]:
                    cts[2]+=1

        hits.append(cts)
    df2[str(k)+'_smith_irv_hit_percent'] = [hits[i][0] for i in range(len(hits))]
    df2[str(k)+'_smith_plurality_hit_percent'] = [hits[i][1] for i in range(len(hits))]
    df2[str(k)+'_smith_minimax_hit_percent'] = [hits[i][2] for i in range(len(hits))]
    df2.to_csv(str(k)+'_perturbation/dist_'+loc+'.csv')


#for loc in ['scotland']:
 #   for k in [0.1, 0.2, 0.4, 0.6, 0.8]:
 #       dist_perturbation_hits(loc,k)

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
