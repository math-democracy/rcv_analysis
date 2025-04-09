import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import votekit.elections as vk
import pandas as pd
import multiprocessing
import csv
import os

num_cands_to_keep = 4

method = 'first_place'

data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/{method}/scotland_results_top{num_cands_to_keep}.csv'
root_dir = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/{method}/processed_data'

error_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/{method}/supporting_files/scotland_error.txt'
processed_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/tiebreaker/{method}/supporting_files/scotland_processed.txt'
all_data = []

processed = []
error_d = []
         
def file_less_than_3mb(file_path):
    try:
        file_size = os.path.getsize(file_path)  # Get file size in bytes
        return file_size < 5 * 1024 * 1024  # 1 MB in bytes
    except FileNotFoundError:
        print("File not found.")
        return False
    
def get_cands_to_keep(profile, num_cands, num_cands_to_keep):
    # get top4 plurality winners
        # if there are less than 5 candidates, then top4 and top5 are both the whole candidate list
    if num_cands > num_cands_to_keep:
        cands_to_keep_set = vk.Plurality(profile=profile, m=num_cands_to_keep, tiebreak='first_place').election_states[-1].elected
        cands_to_keep_set = [list(set(f)) for f in cands_to_keep_set]
        cands_to_keep = []
        for l in cands_to_keep_set:
            for c in l:
                cands_to_keep.append(c)
    else:
        cands_to_keep = list(profile.candidates)

    return cands_to_keep
    
def run_voting_methods(full_path):
    df = pd.read_csv(full_path)

    # create david-readable profile
    columns = [c for c in df.columns if 'rank' in c]
    d_profile = df[columns]
    d_profile = d_profile.value_counts().reset_index(name='Count')
       
    # create votekit profile
    v =  mm.v_profile(full_path)

    # get total candidate information
    candidates = list(v.candidates)
    num_cands = len([x for x in candidates if x != 'skipped'])

    data = {'file': full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')}
    grouped_data = []

    data['numCands'] = num_cands

    # get result of election considering all candidates
    data['plurality'] = list(mm.Plurality(prof=v,tiebreak='first_place'))
    data['IRV'] = list(mm.IRV(prof=v,tiebreak='first_place'))
    data['top-two'] = list(mm.TopTwo(prof=v,tiebreak='first_place'))
    data['borda-pm'] = list(mm.Borda_PM(prof=v, tiebreak='first_place'))
    data['borda-om'] = list(mm.Borda_OM(prof=v, tiebreak='first_place'))
    data['borda-avg'] = list(mm.Borda_AVG(prof=v, tiebreak='first_place'))
    data['top-3-truncation'] = mm.Top3Truncation(prof=v,tiebreak='first_place')
    # sometimes top-3-trunc returns a list not a set
    if isinstance(data['top-3-truncation'], str):
        data['top-3-truncation'] = [data['top-3-truncation']]
    else:
        data['top-3-truncation'] = list(data['top-3-truncation'])
    data['condorcet'] = list(mm.Condorcet(prof=v,tiebreak='first_place'))
    data['minimax'] = list(mm.Minimax(prof=v,tiebreak='first_place'))
    data['smith'] = list(mm.Smith(prof=v, tiebreak='first_place'))
    data['smith_plurality'] = list(mm.Smith_Plurality(prof=v,tiebreak='first_place'))
    data['smith_irv'] = list(mm.Smith_IRV(prof=v,tiebreak='first_place'))
    data['smith-minimax'] = list(mm.Smith_Minimax(prof=v,tiebreak='first_place'))
    data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v,tiebreak='first_place'))
    data['bucklin'] = list(mm.Bucklin(prof=v, tiebreak='first_place'))
    data['approval'] = list(mm.Ranked_Pairs(prof=v,tiebreak='first_place'))

    # get top 4 based on plurality score
    cands_to_keep = get_cands_to_keep(v, len(v.candidates), num_cands_to_keep)
    
    print(cands_to_keep)

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
    data[f'top{num_cands_to_keep}_smith'] = list(mm.Smith(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
    data[f'top{num_cands_to_keep}_smith_plurality'] = list(mm.Smith_Plurality(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
    data[f'top{num_cands_to_keep}_smith_irv'] = list(mm.Smith_IRV(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
    data[f'top{num_cands_to_keep}_smith-minimax'] = list(mm.Smith_Minimax(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
    data[f'top{num_cands_to_keep}_ranked-pairs'] = list(mm.Ranked_Pairs(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
    data[f'top{num_cands_to_keep}_bucklin'] = list(mm.Bucklin(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
    data[f'top{num_cands_to_keep}_approval'] = list(mm.Ranked_Pairs(prof=v, cands_to_keep=cands_to_keep, tiebreak='first_place'))
    
    grouped_data.append(data)
    
    return grouped_data

def process_file(full_path, filename):
    print("RUNNING ", filename, "\n")
    all_data = run_voting_methods(full_path)
    print(all_data, "\n")

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
            print(filename)
            if filename not in processed and filename not in error_d and (filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt')):
                full_path = os.path.join(dirpath, filename)
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