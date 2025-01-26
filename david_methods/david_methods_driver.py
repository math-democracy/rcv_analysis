import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
from david_methods import *
import multiprocessing
import csv
import os
import pandas as pd
import numpy as np

data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/processed_results/australia_results.csv' # output file
root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/australia/processed_data' # data (ex: /Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/australia/processed_data)

error_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/processed_results/american_error.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/processed_results/american_processed.txt'
all_data = []

error_d = []

def file_less_than_3mb(file_path):
    try:
        file_size = os.path.getsize(file_path)  # Get file size in bytes
        return file_size < 5 * 1024 * 1024  # 1 MB in bytes
    except FileNotFoundError:
        print("File not found.")
        return False
    
def read_file(filepath):
    profile = pd.read_csv(filepath)
    num_cands = profile['numCands'].iloc[0]

    columns = [c for c in profile.columns if 'rank' in c or c == 'numSeats' or c == 'numCands']
    profile = profile[columns]
    profile = profile.value_counts().reset_index(name='Count')

    rank = [c for c in columns if 'rank' in c]
    candidates = list(np.unique(profile[rank].values))

    return profile, candidates, num_cands
    
def run_voting_methods(full_path):
    profile, candidates, num_cands = read_file(full_path)
    data = {'file': full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')}
    matrix = pairwise_comparisons_matrix(profile, candidates, num_cands,None)
    grouped_data = []

    data['numCands'] = num_cands

    data['irv'] = IRV(profile, candidates, num_cands)
    data['plurality'] = plurality(profile, candidates, num_cands)
    data['plurality_runoff'] = plurality_runoff(profile, candidates, num_cands)
    data['borda_pm'] = Borda_PM(profile, candidates, num_cands)
    data['borda_om'] = Borda_OM(profile, candidates, num_cands)
    data['borda_avg_keep_uwi'] = Borda_AVG(profile, candidates, num_cands, False)
    data['borda_avg_no_uwi'] = Borda_AVG(profile, candidates, num_cands, True)
    #data['borda_trunc_points_scheme'] = Borda_trunc_points_scheme(profile, candidates, num_cands,)
    data['condorcet'] = Condorcet_winner(profile, candidates, num_cands, None, matrix)
    data['weak_condorcet'] = Weak_Condorcet_winner(profile, candidates, num_cands, None)
    data['minimix'] = minimax_winner(profile, candidates, num_cands, None, matrix)
    data['smith_set'] = Smith_set(profile, candidates, num_cands, None, matrix)
    data['bucklin'] = Bucklin(profile, candidates, num_cands)
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
        ef.write(f"{filename}, \n")

def main():
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            print(filename)
            if (filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt')):
                full_path = os.path.join(dirpath, filename)
                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_file, args=(full_path,filename))
                    p.start()
                    p.join(200)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(error_file, "a") as ef:
                            ef.write(f"{filename}, ")
                        p.terminate()
                        p.join()
                        print("\n")

if __name__ == '__main__':
    main()
            
