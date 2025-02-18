import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import david_methods as dm
import multiprocessing
import csv
import os
import pandas as pd

num_cands_to_keep = 4

data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/results/australia.csv' # output file
root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/australia/processed_data' # data (ex: /Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/australia/processed_data)

error_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/results/supporting_files/australia_error.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/first_place_analysis/results/supporting_files/australia_processed.txt'
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

    columns = [c for c in df.columns if 'rank' in c]
    d_profile = df[columns]
    d_profile = d_profile.value_counts().reset_index(name='Count')
       
    v =  mm.v_profile(full_path)
    candidates = list(v.candidates)
    #candidates_index = list(range(len(candidates)))
    #print(candidates_index)
    grouped_data = []

    num_cands = len(candidates)

    data = {'file': full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')}

    value_counts = get_top3(df)
    
    #top3 = value_counts[:3]
    data['numCands'] = num_cands

    #matrix = dm.pairwise_comparisons_matrix(d_profile, candidates, num_cands,None)

    #data['bottom-3-candidates'] = top3

    # get result of election considering all candidates
    ### KEY ###
    # 1 = winner has fewest first place votes
    # 2 = winner has second fewest first place votes
    # 3 = winner has third fewest first place votes
    # None = winner is not in the bottom 3
    method = 'plurality'
    data['plurality'] = list(mm.Plurality(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'IRV'
    data['IRV'] = list(mm.IRV(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"
    
    method = 'top-two'
    data['top-two'] = list(mm.TopTwo(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'borda-pm'
    data['borda-pm'] = list(mm.Borda_PM(prof=v, tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'borda-om'
    data['borda-om'] = list(mm.Borda_OM(prof=v, tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'borda-avg'
    data['borda-avg'] = list(mm.Borda_AVG(prof=v, tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'top-3-truncation'
    data['top-3-truncation'] = mm.Top3Truncation(prof=v,tiebreak='first_place')
    if isinstance(data['top-3-truncation'], str):
        data['top-3-truncation'] = [data['top-3-truncation']]
    else:
        data['top-3-truncation'] = list(data['top-3-truncation'])
        
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'condorcet'
    data['condorcet'] = list(mm.Condorcet(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'minimax'
    data['minimax'] = list(mm.Minimax(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'smith_plurality'
    data['smith_plurality'] = list(mm.Smith_Plurality(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'smith_irv'
    data['smith_irv'] = list(mm.Smith_IRV(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'smith-minimax'
    data['smith-minimax'] = list(mm.Smith_Minimax(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'ranked-pairs'
    data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'bucklin'
    data['bucklin'] = list(mm.Bucklin(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

    method = 'approval'
    data['approval'] = list(mm.Ranked_Pairs(prof=v,tiebreak='first_place'))
    if len(data[f'{method}']) == 1:
        if data[f'{method}'][0] is None:
            data[f'{method}_rank'] = None
        else:
            data[f'{method}_rank'] = value_counts.index(data[f'{method}'][0]) + 1
    else:
        data[f'{method}_rank'] = "multiple"

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
            
