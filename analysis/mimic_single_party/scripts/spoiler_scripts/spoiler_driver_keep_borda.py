import sys
sys.path.append('/Users/student/Desktop/MyPythonCode/rcv_proposal')
import main_methods as mm
import multiprocessing
import csv
import os

METHOD = 'borda'

root = '/Users/student/Desktop/MyPythonCode/rcv_proposal'

data_file = f'{root}/analysis/mimic_single_party/methods/tiebreaker/{METHOD}/spoiler/scotland_results.csv'
root_dir = f'{root}/analysis/mimic_single_party/condensed_elections/{METHOD}_tiebreaker/processed_data'

error_file = f'{root}/analysis/mimic_single_party/methods/tiebreaker/{METHOD}/supporting_files/spoiler_scotland_error.txt'
processed_file = f'{root}/analysis/mimic_single_party/methods/tiebreaker/{METHOD}/supporting_files/spoiler_scotland_processed.txt'
all_data = []

def run_voting_methods(full_path):
    # create profile + candidate list
    grouped_data = []
    v_profile =  mm.v_profile(full_path)
    candidates = [candidate for candidate in v_profile.candidates if candidate != "skipped"]

    data = {'file': full_path.replace(root_dir, ''), 'candidate_removed': None}

    num_cands = len(candidates)
    data['numCands'] = num_cands

    data['plurality'] = list(mm.Plurality(prof=v_profile))
    data['IRV'] = list(mm.IRV(prof=v_profile))
    data['top-two'] = list(mm.TopTwo(prof=v_profile, tiebreak="first_place"))
    data['borda-pm'] = list(mm.Borda_PM(v_profile, tiebreak="first_place"))
    data['borda-om-no-uwi'] = list(mm.Borda_OM(v_profile, tiebreak="first_place"))
    data['borda-avg-no-uwi'] = list(mm.Borda_AVG(v_profile, tiebreak="first_place"))
    data['top-3-truncation'] = list(mm.Top3Truncation(prof=v_profile))
    data['condorcet'] = list(mm.Condorcet(prof=v_profile))
    data['minimax'] = list(mm.Minimax(prof=v_profile))
    data['smith'] = list(mm.Smith(prof=v_profile))
    data['smith_plurality'] = list(mm.Smith_Plurality(prof=v_profile))
    data['smith_irv'] = list(mm.Smith_IRV(prof=v_profile))
    data['smith-minimax'] = list(mm.Smith_Minimax(prof=v_profile))
    data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v_profile))
    data['bucklin'] = list(mm.Bucklin(prof=v_profile))
    data['approval'] = list(mm.Ranked_Pairs(prof=v_profile))
    
    # check for spoiler effect by removing one candidate each time
    if len(candidates) > 1:
        print(candidates)
        for index, c in enumerate(candidates):
            new_candidates = candidates.copy()
            new_candidates.remove(c)
       
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

def process_file(full_path, filename):
    print("RUNNING ", filename, "\n")
    all_data = run_voting_methods(full_path)
    print("DONE", "\n")

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
        ef.write(f"'{filename}',\n")

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