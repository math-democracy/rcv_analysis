from main_methods2 import *
import multiprocessing
import csv
import os

num_cands_to_keep = 4

data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/stability_analysis/australia_results_top{num_cands_to_keep}.csv'
root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/australia/processed_data'

error_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/stability_analysis/processed_results/australia_error.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/stability_analysis/processed_results/australia_processed.txt'
all_data = []

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
    v =  v_profile(full_path)
    profile, file_path, candidates_with_indices, candidates = p_profile(full_path)
    candidates_index = list(range(len(candidates)))
    grouped_data = []
    data = {'file': full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')}
    
    # get result of election considering all candidates
    data['plurality'] = Plurality(prof=profile, cands_to_keep=candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
    data['IRV'] = IRV(prof=v, cands_to_keep=candidates, candidates_with_indices=candidates_with_indices, package="votekit")
    data['top-two'] = TopTwo(prof=v, cands_to_keep=candidates)
    data['borda-pm'] = Borda_PM(prof=v, cands_to_keep=candidates)
    data['top-3-truncation'] = Top3Truncation(prof=v, cands_to_keep=candidates)
    data['condorcet'] = Condorcet(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['minimax'] = Minimax(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['smith'] = Smith(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['smith-minimax'] = Smith_minimax(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)
    data['ranked-pairs'] = Ranked_Pairs(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)

    cands_to_keep = get_cands_to_keep(v, len(v.candidates), 4)
    new_candidates_index = {key: value for key, value in candidates_with_indices.items() if value in cands_to_keep}
    new_candidates_index = new_candidates_index.keys()
    
    print(cands_to_keep)
    print(list(new_candidates_index))

    data[f'top{num_cands_to_keep}_plurality'] = Plurality(prof=profile, cands_to_keep=new_candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
    data[f'top{num_cands_to_keep}_IRV'] = IRV(prof=v, cands_to_keep=cands_to_keep, candidates_with_indices=candidates_with_indices, package="votekit")
    data[f'top{num_cands_to_keep}_top-two'] = TopTwo(prof=v, cands_to_keep=cands_to_keep)
    data[f'top{num_cands_to_keep}_borda-pm'] = Borda_PM(prof=v, cands_to_keep=cands_to_keep)
    data[f'top{num_cands_to_keep}_top-3-truncation'] = Top3Truncation(prof=v, cands_to_keep=cands_to_keep)
    data[f'top{num_cands_to_keep}_condorcet'] = Condorcet(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=new_candidates_index)
    data[f'top{num_cands_to_keep}_minimax'] = Minimax(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=new_candidates_index)
    data[f'top{num_cands_to_keep}_smith'] = Smith(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=new_candidates_index)
    data[f'top{num_cands_to_keep}_smith-minimax'] = Smith_minimax(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=new_candidates_index)
    data[f'top{num_cands_to_keep}_ranked-pairs'] = Ranked_Pairs(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=new_candidates_index)

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
        ef.write(f"{filename}, ")

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
            
