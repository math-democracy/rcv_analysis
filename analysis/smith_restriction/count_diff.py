import os
import sys
sys.path.append(os.path.abspath('/Users/malavikamukundan/Documents/rcv_proposal/rcv_proposal/'))
#sys.path.append(os.path.abspath('../rcv_proposal/results/current/metadata'))
#sys.path.append(os.path.abspath('../rcv_proposal/helper/Jones_code/'))
import pandas as pd
import main_methods as mm
import ast
import json
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

count_diff('australia')
count_diff('america')
count_diff('scotland')
count_diff('civs')
    


            
