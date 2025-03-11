import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import votekit.elections as v
import pandas as pd
import multiprocessing
import csv
import os
import json
from itertools import groupby

num_cands_to_keep = 4
METHOD = 'first_place'
data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/scotland_results_top{num_cands_to_keep}.csv'
root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data'

error_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/supporting_files/scotland_error.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/supporting_files/scotland_processed.txt'
all_data = []

processed = []
error_d = []

borda_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/borda_scores/scotland_borda_scores.json'
mention_file =  '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/fringe/mention_scores/scotland_mention_scores.json'
first_place_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/scotland_first_place_ranks.json'

with open('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/metadata/party_breakdown.json') as file:
    party_breakdown = json.load(file)
    
def get_condensed_cands(filepath, filename, method):
    if method == 'borda':
        with open(borda_file) as file:
            scores = json.load(file)
    elif method == 'mention':
        with open(mention_file) as file:
            scores = json.load(file)
    elif method == 'first_place':
        with open(first_place_file) as file:
            scores = json.load(file)

    party_info = party_breakdown[filepath]
    candidate_dict = party_info['party_dict']

    if filename in scores:
        candidate_scores = scores[filename]
    else:
        new_filename = [f for f in scores if f.endswith(filename)]
        if len(new_filename) != 1:
            candidate_scores = None
        else: 
            candidate_scores = scores[new_filename[0]]
    
    if candidate_scores:
        grouped_by_party = {i: [j[0] for j in j] for i, j in groupby(sorted(candidate_dict.items(), key = lambda x : x[1]), lambda x : x[1])}
        cands_to_keep = set()
        for party in grouped_by_party.values():
            keep = [i for i in candidate_dict.keys() if candidate_scores[i] == max(candidate_scores[title] for title in party)]
            cands_to_keep.update(keep)
    else:
        return None

    return list(cands_to_keep)
    
def get_cands_to_keep(profile, condensed_cands, num_cands, num_cands_to_keep):
    # get top4 plurality winners
        # if there are less than 5 candidates, then top4 and top5 are both the whole candidate list
    prof = mm.process_cands(profile, condensed_cands)

    if num_cands > num_cands_to_keep:
        cands_to_keep = v.Plurality(profile=prof,m=num_cands_to_keep,tiebreak='first_place').election_states[-1].elected
        cands_to_keep = [list(w)[0] for w in cands_to_keep]
    else:
        cands_to_keep = list(prof.candidates)

    return cands_to_keep
    
def run_voting_methods(full_path, filename):
    condensed_cands = get_condensed_cands(full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/',''), filename, METHOD)
    
    if condensed_cands:
        num_cands = len([x for x in condensed_cands if x != 'skipped'])
        
        # # create david-readable profile
        # columns = [c for c in df.columns if 'rank' in c]
        # d_profile = df[columns]
        # d_profile = d_profile.value_counts().reset_index(name='Count')
        
        # create votekit profile
        v =  mm.v_profile(full_path)
        print('num cands ', str(len(v.candidates)), str(num_cands))
        print('condensed_cands', condensed_cands)
        

        # get total candidate information
        # candidates = list(v.candidates)
        

        data = {'file': full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')}
        grouped_data = []

        data['numCands'] = num_cands

        # get result of election considering all candidates
        data['plurality'] = list(mm.Plurality(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['IRV'] = list(mm.IRV(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['top-two'] = list(mm.TopTwo(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['borda-pm'] = list(mm.Borda_PM(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['borda-om'] = list(mm.Borda_OM(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['borda-avg'] = list(mm.Borda_AVG(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['top-3-truncation'] = mm.Top3Truncation(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place')
        # sometimes top-3-trunc returns a list not a set
        if isinstance(data['top-3-truncation'], str):
            data['top-3-truncation'] = [data['top-3-truncation']]
        else:
            data['top-3-truncation'] = list(data['top-3-truncation'])
        data['condorcet'] = list(mm.Condorcet(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['minimax'] = list(mm.Minimax(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['smith_plurality'] = list(mm.Smith_Plurality(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['smith_irv'] = list(mm.Smith_IRV(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['smith-minimax'] = list(mm.Smith_Minimax(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['bucklin'] = list(mm.Bucklin(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))
        data['approval'] = list(mm.Ranked_Pairs(prof=v,cands_to_keep=condensed_cands,tiebreak='first_place'))

        # get top 4 based on plurality score
        cands_to_keep = get_cands_to_keep(v, condensed_cands, num_cands, num_cands_to_keep)
        print('cands_to_keep ',cands_to_keep, '\n')
        
        data[f'top{num_cands_to_keep}_plurality'] = list(mm.Plurality(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_IRV'] = list(mm.IRV(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_top-two'] = list(mm.TopTwo(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_borda-pm'] = list(mm.Borda_PM(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_borda-om'] = list(mm.Borda_OM(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_borda-avg'] = list(mm.Borda_AVG(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_top-3-truncation'] = mm.Top3Truncation(prof=v, cands_to_keep=cands_to_keep,tiebreak='first_place')
        # sometimes top-3-trunc returns a list not a set
        if isinstance(data[f'top{num_cands_to_keep}_top-3-truncation'], str):
            data[f'top{num_cands_to_keep}_top-3-truncation'] = [data[f'top{num_cands_to_keep}_top-3-truncation']]
        else:
            data[f'top{num_cands_to_keep}_top-3-truncation'] = list(data[f'top{num_cands_to_keep}_top-3-truncation'])
        data[f'top{num_cands_to_keep}_condorcet'] = list(mm.Condorcet(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_minimax'] = list(mm.Minimax(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_smith_plurality'] = list(mm.Smith_Plurality(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_smith_irv'] = list(mm.Smith_IRV(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_smith-minimax'] = list(mm.Smith_Minimax(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_ranked-pairs'] = list(mm.Ranked_Pairs(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_bucklin'] = list(mm.Bucklin(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
        data[f'top{num_cands_to_keep}_approval'] = list(mm.Ranked_Pairs(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))

        grouped_data.append(data)
        
        return grouped_data
    else:
        return None

def process_file(full_path, filename):
    print("RUNNING ", filename, "\n")
    all_data = run_voting_methods(full_path, filename)
    #print(all_data, "\n")

    if all_data:
        with open(data_file, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write the header if the file is empty
            if os.stat(data_file).st_size == 0:
                header = all_data[0].keys()
                writer.writerow(header)

            # Write each row of data
            for data in all_data:
                keys = all_data[0].keys()
                row = [data.get(key, '') for key in keys]
                writer.writerow(row)

    with open(processed_file, "a") as ef:
        ef.write(f"\"{filename}\", \n")

def main():
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            #print(filename)
            if filename not in processed and filename not in error_d and (filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt')):
                full_path = os.path.join(dirpath, filename)
                #print(full_path)
                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_file, args=(full_path,filename))
                    p.start()
                    p.join(200)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(error_file, "a") as ef:
                            ef.write(f"\"{filename}\", ")
                        p.terminate()
                        p.join()
                        print("\n")

if __name__ == '__main__':
    main()
    #process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data/aberdeenshire22/ward-14-huntly-strathbogie-and-howe-of-alford_06052022_172124.csv','ward-14-huntly-strathbogie-and-howe-of-alford_06052022_172124.csv')