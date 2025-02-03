import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods3 as mm
import david_methods as dm
import multiprocessing
import csv
import os
import pandas as pd

num_cands_to_keep = 4

data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/american.csv' # output file
root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/american/processed_data' # data (ex: /Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/australia/processed_data)

error_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/american_error.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/american_processed.txt'
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
    
def get_top3(df):
    value_counts = df['rank1'].value_counts(ascending=False)

    # return list of candidates in descending order of first place votes
    return list(value_counts.to_dict().keys())
    
def run_voting_methods(full_path):
    df = pd.read_csv(full_path)

    columns = [c for c in df.columns if 'rank' in c or c == 'numSeats' or c == 'numCands']
    d_profile = df[columns]
    d_profile = d_profile.value_counts().reset_index(name='Count')
       
    v =  mm.v_profile(full_path)
    profile, file_path, candidates_with_indices, candidates = mm.p_profile(full_path)
    candidates_index = list(range(len(candidates)))
    #print(candidates_index)
    grouped_data = []

    num_cands = len(candidates)

    data = {'file': full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')}

    value_counts = get_top3(df)
    
    #top3 = value_counts[:3]
    data['numCands'] = num_cands

    matrix = dm.pairwise_comparisons_matrix(d_profile, candidates, num_cands,None)

    #data['bottom-3-candidates'] = top3

    # get result of election considering all candidates
    ### KEY ###
    # 1 = winner has fewest first place votes
    # 2 = winner has second fewest first place votes
    # 3 = winner has third fewest first place votes
    # None = winner is not in the bottom 3
    data['plurality'] = mm.Plurality(prof=profile, cands_to_keep=candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
    data['plurality_rank'] = value_counts.index(data['plurality']) + 1

    data['IRV'] = mm.IRV(prof=v, cands_to_keep=candidates, candidates_with_indices=candidates_with_indices, package="votekit")
    data['IRV_rank'] = value_counts.index(data['IRV']) + 1
    
    data['top-two'] = mm.TopTwo(prof=v, cands_to_keep=candidates)
    data['top-two_rank'] = value_counts.index(data['top-two']) + 1

    data['borda-pm'] = dm.Borda_PM(d_profile, candidates, num_cands)[0]
    data['borda-pm_rank'] = value_counts.index(data['borda-pm']) + 1

    data['borda-om-no-uwi'] = dm.Borda_OM(d_profile, candidates, num_cands, False)[0]
    data['borda-om-no-uwi_rank'] = value_counts.index(data['borda-om-no-uwi']) + 1

    data['borda-avg-no-uwi'] = dm.Borda_AVG(d_profile, candidates, num_cands, False)[0]
    data['borda-avg-no-uwi_rank'] = value_counts.index(data['borda-avg-no-uwi']) + 1

    data['top-3-truncation'] = mm.Top3Truncation(prof=v, cands_to_keep=candidates)
    data['top-3-truncation_rank'] = value_counts.index(data['top-3-truncation']) + 1

    data['condorcet'] = dm.Condorcet_winner(d_profile, candidates, num_cands, None, matrix)[0]
    data['condorcet_rank'] = value_counts.index(data['condorcet']) + 1

    data['minimax'] = dm.minimax_winner(d_profile, candidates, num_cands, None, matrix)[0]
    data['minimax_rank'] = value_counts.index(data['minimax']) + 1

    data['smith'] = mm.Smith(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['smith_rank'] = value_counts.index(data['smith']) + 1

    data['smith-minimax'] = mm.Smith_minimax(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)
    data['smith-minimax_rank'] = value_counts.index(data['smith-minimax']) + 1

    data['ranked-pairs'] = mm.Ranked_Pairs(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)
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
            if filename not in processed and filename not in error_d and (filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt')):
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
            
