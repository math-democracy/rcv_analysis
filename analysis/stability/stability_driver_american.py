import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods3 as mm
import david_methods as dm
import votekit.elections as v
import pandas as pd
import multiprocessing
import csv
import os

num_cands_to_keep = 4

data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/new/results/american_results_top{num_cands_to_keep}.csv'
root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/american/processed_data'

error_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/new/results/supporting_files/american_error.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/new/results/supporting_files/american_processed.txt'
all_data = []

processed = []
if 'american' in data_file:
    error_d = ['Portland_D3_2024.csv', 'Portland_D2_2024.csv', 'PortlandOR_110524_Mayor.csv', 'Portland_D4_2024.csv', 'SanFrancisco_11052024_Mayor.csv', 'NewYorkCity_06222021_DEMMayorCitywide.csv']
elif 'american' in data_file:
    error_d = ['BallotPaperDetails-Werribee with candidates.csv', 'BallotPaperDetails-Point Cook with candidates.csv', 'BallotPaperDetails-Melton with candidates.csv']
else:
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
        cands_to_keep = v.Plurality(profile=profile, m=num_cands_to_keep).election_states[-1].elected
        cands_to_keep = [list(w)[0] for w in cands_to_keep]
    else:
        cands_to_keep = profile.candidates

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
    num_cands = len(candidates)

    data = {'file': full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')}
    grouped_data = []

    data['numCands'] = num_cands

    # get result of election considering all candidates
    data['plurality'] = list(mm.Plurality(prof=v))
    data['IRV'] = list(mm.IRV(prof=v))
    data['top-two'] = list(mm.TopTwo(prof=v))
    data['borda-pm'] = list(dm.Borda_PM(d_profile, candidates, num_cands))
    data['borda-om-no-uwi'] = list(dm.Borda_OM(d_profile, candidates, num_cands, False))
    data['borda-avg-no-uwi'] = list(dm.Borda_AVG(d_profile, candidates, num_cands, False))
    data['top-3-truncation'] = list(mm.Top3Truncation(prof=v))
    data['condorcet'] = list(mm.Condorcet(prof=v))
    data['minimax'] = list(mm.Minimax(prof=v))
    data['smith_plurality'] = list(mm.Smith_Plurality(prof=v))
    data['smith_irv'] = list(mm.Smith_IRV(prof=v))
    data['smith-minimax'] = list(mm.Smith_Minimax(prof=v))
    data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v))
    data['bucklin'] = list(mm.Bucklin(prof=v))
    data['approval'] = list(mm.Ranked_Pairs(prof=v))

    # get top 4 based on plurality score
    cands_to_keep = get_cands_to_keep(v, len(v.candidates), 4)
    
    print(cands_to_keep)

    data[f'top{num_cands_to_keep}_plurality'] = list(mm.Plurality(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_IRV'] = list(mm.IRV(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_top-two'] = list(mm.TopTwo(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_borda-pm'] = list(dm.Borda_PM(d_profile, cands_to_keep, num_cands))
    data[f'top{num_cands_to_keep}_borda-om-no-uwi'] = list(dm.Borda_OM(d_profile, cands_to_keep, num_cands, False))
    data[f'top{num_cands_to_keep}_borda-avg-no-uwi'] = list(dm.Borda_AVG(d_profile, cands_to_keep, num_cands, False))
    data[f'top{num_cands_to_keep}_top-3-truncation'] = list(mm.Top3Truncation(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_condorcet'] = list(mm.Condorcet(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_minimax'] = list(mm.Minimax(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_smith_plurality'] = list(mm.Smith_Plurality(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_smith_irv'] = list(mm.Smith_IRV(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_smith-minimax'] = list(mm.Smith_Minimax(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_ranked-pairs'] = list(mm.Ranked_Pairs(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_bucklin'] = list(mm.Bucklin(prof=v, cands_to_keep=cands_to_keep))
    data[f'top{num_cands_to_keep}_approval'] = list(mm.Ranked_Pairs(prof=v, cands_to_keep=cands_to_keep))
    
    # column_order = ['file','plurality',
    #                 f'top{num_cands_to_keep}_plurality','IRV',f'top{num_cands_to_keep}_IRV',
    #                 'top-two',f'top{num_cands_to_keep}_top-two',
    #                 'borda-pm',f'top{num_cands_to_keep}_borda-pm',
    #                 'top-3-truncation',f'top{num_cands_to_keep}_top-3-truncation',
    #                 'condorcet',f'top{num_cands_to_keep}_condorcet',
    #                 'minimax',f'top{num_cands_to_keep}_minimax',
    #                 'smith',f'top{num_cands_to_keep}_smith',
    #                 'smith-minimax',f'top{num_cands_to_keep}_smith-minimax',
    #                 'ranked-pairs',f'top{num_cands_to_keep}_ranked-pairs']
    # grouped_data = {k:grouped_data[k] for k in column_order}
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