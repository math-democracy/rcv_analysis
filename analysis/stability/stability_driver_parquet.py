import sys
sys.path.append('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import votekit.elections as vk
import pandas as pd
import multiprocessing
import csv
import os
from datetime import datetime

num_cands_to_keep = 4

data_file = f'/Users/karenxiao/MyPythonCode/ranked_choice_voting/sample_parquets/results/ccesv3_results_top{num_cands_to_keep}.csv'
root_dir = '/Users/karenxiao/MyPythonCode/ranked_choice_voting/sample_parquets/data'

error_file = '/'.join(data_file.split('/')[:-1]) + '/ccesv3_error.txt'
processed_file = '/'.join(data_file.split('/')[:-1]) + '/ccesv3_processed.txt'
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
    
def run_voting_methods(full_path, v, model_to_select):
    # get total candidate information
    candidates = list(v.candidates)
    num_cands = len([x for x in candidates if x != 'skipped'])

    data = {'file': full_path.replace('/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/', ''),
            'model': model_to_select}
    grouped_data = []

    data['numCands'] = num_cands

    #get result of election considering all candidates
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
    data['smith'] = list(mm.Smith(prof=v,tiebreak='first_place'))
    data['smith_plurality'] = list(mm.Smith_Plurality(prof=v,tiebreak='first_place'))
    data['smith_irv'] = list(mm.Smith_IRV(prof=v,tiebreak='first_place'))
    data['smith-minimax'] = list(mm.Smith_Minimax(prof=v,tiebreak='first_place'))
    data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v,tiebreak='first_place'))
    data['bucklin'] = list(mm.Bucklin(prof=v, tiebreak='first_place'))
    data['approval'] = list(mm.Ranked_Pairs(prof=v,tiebreak='first_place'))

    # get top 4 based on plurality score
    cands_to_keep = get_cands_to_keep(v, len(v.candidates), num_cands_to_keep)

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
    data[f'top{num_cands_to_keep}_smith'] = list(mm.Smith(prof=v,cands_to_keep=cands_to_keep, tiebreak='first_place'))
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

    models = {
        "(True, True, False, False)": "TTFF",
        "(False, True, False, False)": "FTFF",
        "(True, False, False, False)": "TFFF",
        "(True, True, True, False)": "TTTF",
        "(True, True, False, True)": "TTFT",
        "(False, False, True, False)": "FFTF",
        "(False, False, True, True)": "FFTT"
    }

    for i, (model_to_select, shortcut) in enumerate(models.items()):
        print("PROCCESSING ", model_to_select, "\n")
        filtered_df = mm.process_parquet(full_path, model_to_select)
        profiles = filtered_df['profile']

        for i in range(len(profiles)):
            if i % 10 == 0:
                print(f'processing election {models[model_to_select]} #{i}')

            vk_profile = mm.v_profile_from_parq(profiles[i])
            all_data = run_voting_methods(full_path, vk_profile, model_to_select)

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
            if filename not in processed and filename not in error_d and (filename.endswith('.parquet')):
                full_path = os.path.join(dirpath, filename)
                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_file, args=(full_path,filename))
                    p.start()
                    p.join(200)

                    # if p.is_alive():
                    #     print("running... let's kill it...")
                    #     with open(error_file, "a") as ef:
                    #         ef.write(f"\"{filename}\", ")
                    #     p.terminate()
                    #     p.join()
                    #     print("\n")

if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(start_time, end_time)