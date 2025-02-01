from main_methods3 import *
import multiprocessing
import csv
import os

data_file = '/Users/belle/Desktop/build/rcv_proposal/analysis/spoiler/australian_results.csv'
root_dir = '/Users/belle/Desktop/build/rcv_proposal/civs/processed_data'

error_file = '/Users/belle/Desktop/build/rcv_proposal/analysis/spoiler/australian_error.txt'
processed_file = '/Users/belle/Desktop/build/rcv_proposal/analysis/spoiler/australian_processed.txt'
all_data = []

def run_voting_methods(full_path):
    # create profile + candidate list
    votekit_profile =  v_profile(full_path)

    profile, file_path, candidates_with_indices, candidates = p_profile(full_path)

    candidates_index = list(range(len(candidates)))
    grouped_data = []

    # calculate original winners for each method
    data = {'file': full_path.replace('/Users/belle/Desktop/build/rcv_proposal/', ''), 'candidate_removed': 'none'}
        
    data['plurality'] = Plurality(prof=profile, cands_to_keep=candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
    data['IRV'] = IRV(prof=profile, cands_to_keep=candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
    # data['top-two'] = TopTwo(prof=v, cands_to_keep=candidates)
    # data['borda-pm'] = Borda_PM(prof=v, cands_to_keep=candidates)
    # data['top-3-truncation'] = Top3Truncation(prof=v, cands_to_keep=candidates)
    data['condorcet'] = Condorcet(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['minimax'] = Minimax(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['smith'] = Smith(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['smith-minimax'] = Smith_minimax(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)
    data['ranked-pairs'] = Ranked_Pairs(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)
    print(data)
    grouped_data.append(data)

    # check for spoiler effect by removing one candidate each time
    if len(candidates) > 1:
        print(candidates)
        for index, c in enumerate(candidates):
            new_candidates = candidates.copy()
            new_candidates.remove(c)
            new_candidates_index = candidates_index.copy()
            new_candidates_index.remove(index)
            print(c)
            print(new_candidates)
            print(new_candidates_index)
       
            data = {'file': full_path.replace('/Users/belle/Desktop/build/rcv_proposal/', ''), 'candidate_removed': c}
            
            data['plurality'] = Plurality(prof=profile, cands_to_keep=new_candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
            data['IRV'] = IRV(prof=profile, cands_to_keep=new_candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
            # data['top-two'] = TopTwo(prof=v, cands_to_keep=new_candidates)
            data['borda-pm'] = Borda_PM(prof=profile, cands_to_keep=new_candidates, candidates_with_indices=candidates_with_indices)
            # data['top-3-truncation'] = Top3Truncation(prof=v, cands_to_keep=new_candidates)
            data['condorcet'] = Condorcet(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=new_candidates_index)
            data['minimax'] = Minimax(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=new_candidates_index)
            data['smith'] = Smith(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=new_candidates_index)
            # data['smith-irv'] = Smith_IRV(prof=profile, candidates_with_indices=candidates_with_indices)
            data['smith-minimax'] = Smith_minimax(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=new_candidates_index)
            data['ranked-pairs'] = Ranked_Pairs(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=new_candidates_index)
            # data['bucklin'] = Bucklin(prof=profile, candidates_with_indices=candidates_with_indices, package="pref_voting")
            print(data)
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
        ef.write(f"{filename}, ")

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
                    p.join(20)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(error_file, "a") as ef:
                            ef.write(f"{filename}, ")
                        p.terminate()
                        p.join()
                        print("\n")
            
if __name__ == '__main__':
    main()