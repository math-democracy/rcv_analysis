import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
from main_methods2 import *
import multiprocessing
import csv
import os
import pandas as pd

num_cands_to_keep = 4

data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/results/american.csv' # output file
root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/american/processed_data' # data (ex: /Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/australia/processed_data)

error_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/results/american_error.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/results/american_processed.txt'
all_data = []

error_d = []

def file_less_than_3mb(file_path):
    try:
        file_size = os.path.getsize(file_path)  # Get file size in bytes
        return file_size < 5 * 1024 * 1024  # 1 MB in bytes
    except FileNotFoundError:
        print("File not found.")
        return False
    
def get_top3(df):
    value_counts = df['rank1'].value_counts(ascending=False)

    # return the three candidates with fewest first place votes
    return list(value_counts.to_dict().keys())
    
def run_voting_methods(full_path):
    df = pd.read_csv(full_path)
       
    v =  v_profile(full_path)
    profile, file_path, candidates_with_indices, candidates = p_profile(full_path)
    candidates_index = list(range(len(candidates)))
    grouped_data = []

    data = {'file': full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')}

    value_counts = get_top3(df)
    top3 = value_counts[:3]
    data['numCands'] = len(candidates)
    #data['bottom-3-candidates'] = top3

    # get result of election considering all candidates
    ### KEY ###
    # 1 = winner has fewest first place votes
    # 2 = winner has second fewest first place votes
    # 3 = winner has third fewest first place votes
    # None = winner is not in the bottom 3
    data['plurality'] = Plurality(prof=profile, cands_to_keep=candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
    data['plurality_rank'] = value_counts.index(data['plurality']) + 1

    data['IRV'] = IRV(prof=v, cands_to_keep=candidates, candidates_with_indices=candidates_with_indices, package="votekit")
    data['IRV_rank'] = value_counts.index(data['IRV']) + 1
    
    data['top-two'] = TopTwo(prof=v, cands_to_keep=candidates)
    data['top-two_rank'] = value_counts.index(data['top-two']) + 1

    data['borda-pm'] = Borda_PM(prof=v, cands_to_keep=candidates)
    data['borda-pm_rank'] = value_counts.index(data['borda-pm']) + 1

    data['top-3-truncation'] = Top3Truncation(prof=v, cands_to_keep=candidates)
    data['top-3-truncation_rank'] = value_counts.index(data['top-3-truncation']) + 1

    data['condorcet'] = Condorcet(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['condorcet_rank'] = value_counts.index(data['condorcet']) + 1

    data['minimax'] = Minimax(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['minimax_rank'] = value_counts.index(data['minimax']) + 1

    data['smith'] = Smith(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['smith_rank'] = value_counts.index(data['smith']) + 1

    data['smith-minimax'] = Smith_minimax(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)
    data['smith-minimax_rank'] = value_counts.index(data['smith-minimax']) + 1

    data['ranked-pairs'] = Ranked_Pairs(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)
    data['ranked-pairs_rank'] = value_counts.index(data['ranked-pairs']) + 1

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
            
