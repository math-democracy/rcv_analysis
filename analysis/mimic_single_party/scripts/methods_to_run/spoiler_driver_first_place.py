import sys
sys.path.append('/Users/student/Desktop/MyPythonCode/rcv_proposal')
import main_methods as mm
import multiprocessing
import csv
import os
import json
from itertools import groupby

METHOD = 'first_place'

root = '/Users/student/Desktop/MyPythonCode/rcv_proposal'

data_file = f'{root}/analysis/mimic_single_party/methods/{METHOD}_score/spoiler/scotland_results.csv'
root_dir = './raw_data/scotland/processed_data'

error_file = f'{root}/analysis/mimic_single_party/methods/{METHOD}_score/supporting_files/spoiler_scotland_error.txt'
processed_file = f'{root}/analysis/mimic_single_party/methods/{METHOD}_score/supporting_files/spoiler_scotland_processed.txt'
all_data = []

borda_file = './analysis/fringe/borda_scores/scotland_borda_scores.json'
mention_file =  './analysis/fringe/mention_scores/scotland_mention_scores.json'
first_place_file = './analysis/first_place_analysis/scotland_first_place_ranks.json'

with open('./analysis/mimic_single_party/metadata/party_breakdown.json') as file:
    party_breakdown = json.load(file)

# method options: 'borda','mention','first_place' 
#   for each party, only keep the cand with the highest borda, mention, or first place score
def get_condensed_cands(filepath, method):
    filename = filepath.split('/')[-1]

    if method == 'borda':
        with open(borda_file) as file:
            scores = json.load(file)
    elif method == 'mention':
        with open(mention_file) as file:
            scores = json.load(file)
    elif method == 'first_place':
        with open(first_place_file) as file:
            scores = json.load(file)

    party_info = party_breakdown[filepath[2:]]
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

def run_voting_methods(full_path):
    condensed_cands = get_condensed_cands(full_path.replace(f'{root}/',''), METHOD)
    
    if condensed_cands:
        # create profile + candidate list
        grouped_data = []
        v_profile =  mm.v_profile(full_path)
        
        candidates = [candidate for candidate in condensed_cands if candidate != "skipped"]

        data = {'file': full_path.replace(root_dir, ''), 'candidate_removed': None}

        num_cands = len(candidates)
        data['numCands'] = num_cands

        data['plurality'] = list(mm.Plurality(prof=v_profile, cands_to_keep=candidates))
        data['IRV'] = list(mm.IRV(prof=v_profile, cands_to_keep=candidates))
        data['top-two'] = list(mm.TopTwo(prof=v_profile, tiebreak="first_place", cands_to_keep=candidates))
        data['borda-pm'] = list(mm.Borda_PM(v_profile, tiebreak="first_place", cands_to_keep=candidates))
        data['borda-om-no-uwi'] = list(mm.Borda_OM(v_profile, tiebreak="first_place", cands_to_keep=candidates))
        data['borda-avg-no-uwi'] = list(mm.Borda_AVG(v_profile, tiebreak="first_place", cands_to_keep=candidates))
        data['top-3-truncation'] = list(mm.Top3Truncation(prof=v_profile, cands_to_keep=candidates))
        data['condorcet'] = list(mm.Condorcet(prof=v_profile, cands_to_keep=candidates))
        data['minimax'] = list(mm.Minimax(prof=v_profile, cands_to_keep=candidates))
        data['smith'] = list(mm.Smith(prof=v_profile, cands_to_keep=candidates))
        data['smith_plurality'] = list(mm.Smith_Plurality(prof=v_profile, cands_to_keep=candidates))
        data['smith_irv'] = list(mm.Smith_IRV(prof=v_profile, cands_to_keep=candidates))
        data['smith-minimax'] = list(mm.Smith_Minimax(prof=v_profile, cands_to_keep=candidates))
        data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v_profile, cands_to_keep=candidates))
        data['bucklin'] = list(mm.Bucklin(prof=v_profile, cands_to_keep=candidates))
        data['approval'] = list(mm.Ranked_Pairs(prof=v_profile, cands_to_keep=candidates))
        
        # check for spoiler effect by removing one candidate each time
        if len(candidates) > 1:
            print(candidates)
            for index, c in enumerate(candidates):
                new_candidates = candidates.copy()
                new_candidates.remove(c)
        
                print('removed: ', c)
                print('new_candidates: ', new_candidates)
                
                data = {'file': full_path.replace(root_dir, ''), 'candidate_removed': c}
                
                data['plurality'] = list(mm.Plurality(prof=v_profile, cands_to_keep=new_candidates))
                data['IRV'] = list(mm.IRV(prof=v_profile, cands_to_keep=new_candidates))
                data['top-two'] = list(mm.TopTwo(prof=v_profile, cands_to_keep=new_candidates, tiebreak="first_place"))
                data['borda-pm'] = list(mm.Borda_PM(v_profile, cands_to_keep=new_candidates, tiebreak="first_place"))
                data['borda-om-no-uwi'] = list(mm.Borda_OM(v_profile, cands_to_keep=new_candidates, tiebreak="first_place"))
                data['borda-avg-no-uwi'] = list(mm.Borda_AVG(v_profile, cands_to_keep=new_candidates, tiebreak="first_place"))
                data['top-3-truncation'] = list(mm.Top3Truncation(prof=v_profile, cands_to_keep=new_candidates))
                data['condorcet'] = list(mm.Condorcet(prof=v_profile, cands_to_keep=new_candidates))
                data['minimax'] = list(mm.Minimax(prof=v_profile, cands_to_keep=new_candidates))
                data['smith'] = list(mm.Smith(prof=v_profile, cands_to_keep=new_candidates))
                data['smith_plurality'] = list(mm.Smith_Plurality(prof=v_profile, cands_to_keep=new_candidates))
                data['smith_irv'] = list(mm.Smith_IRV(prof=v_profile, cands_to_keep=new_candidates))
                data['smith-minimax'] = list(mm.Smith_Minimax(prof=v_profile, cands_to_keep=new_candidates))
                data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v_profile, cands_to_keep=new_candidates))
                data['bucklin'] = list(mm.Bucklin(prof=v_profile, cands_to_keep=new_candidates))
                data['approval'] = list(mm.Ranked_Pairs(prof=v_profile, cands_to_keep=new_candidates))
                # print(data)
                grouped_data.append(data)
    
        return grouped_data
    else:
        return None

def process_file(full_path, filename):
    print("RUNNING ", filename, "\n")
    all_data = run_voting_methods(full_path)
    print("DONE", "\n")

    if all_data:
        with open(data_file, mode='a', newline='') as file:
            writer = csv.writer(file)

            # write header if the file is empty
            if os.stat(data_file).st_size == 0:
                header = all_data[0].keys()
                writer.writerow(header)

            for data in all_data:
                keys = all_data[0].keys()
                row = [data.get(key, '') for key in keys]
                writer.writerow(row)

        with open(processed_file, "a") as ef:
            ef.write(f"'{filename}', \n")
    else:
        with open(error_file, "a") as ef:
            ef.write(f"'{filename}', \n")

def main():
    # loop through data files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                full_path = os.path.join(dirpath, filename)

                # ensure that if it runs for more than x seconds, kill the process
                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_file, args=(full_path,filename))
                    p.start()
                    p.join(40)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(error_file, "a") as ef:
                            ef.write(f"{filename}, ")
                        p.terminate()
                        p.join()
                        print("\n")
            
if __name__ == '__main__':
    main()
            
# process_file('/Users/belle/Desktop/build/rcv_proposal/test.csv', 'test.csv')