import sys
sys.path.append('/Users/belle/Desktop/build/rcv_proposal')
from main_methods3 import *
import multiprocessing
import csv
import os

data_file = '/Users/belle/Desktop/build/rcv_proposal/analysis/spoiler/australian_results.csv'
root_dir = '/Users/belle/Desktop/build/rcv_proposal/raw_data/australia/processed_data'

error_file = '/Users/belle/Desktop/build/rcv_proposal/analysis/spoiler/australian_error.txt'
processed_file = '/Users/belle/Desktop/build/rcv_proposal/analysis/spoiler/australian_processed.txt'
all_data = []

def run_voting_methods(full_path):
    # create profile + candidate list
    votekit_profile =  v_profile(full_path)

    # profile, file_path, candidates_with_indices, candidates = p_profile(full_path)

    # candidates_index = list(range(len(candidates)))
    candidates = list(votekit_profile.candidates)

    if 'skipped' in candidates:## remove 'skipped' from cands_to_keep
        candidates = list(filter(lambda c: c != 'skipped', candidates))

    grouped_data = []

    # calculate original winners for each method
    data = {'file': full_path.replace('/Users/belle/Desktop/build/rcv_proposal/', ''), 'candidate_removed': 'none'}
        
    data['plurality'] = Plurality(votekit_profile)
    data['IRV'] = IRV(votekit_profile)
    data['top-two'] = TopTwo(votekit_profile)
    # data['borda-pm'] = Borda_PM(votekit_profile)
    # data['borda-om'] = Borda_OM(votekit_profile)
    # data['borda-avg'] = Borda_AVG(votekit_profile)
    data['top-3-truncation'] = Top3Truncation(votekit_profile)
    data['condorcet'] = Condorcet(votekit_profile)
    data['smith'] = Smith(votekit_profile)
    data['smith-plurality'] = Smith_Plurality(votekit_profile)
    data['smith-irv'] = Smith_IRV(votekit_profile)
    data['minimax'] = Minimax(votekit_profile)
    data['smith-minimax'] = Smith_Minimax(votekit_profile)
    data['ranked-pairs'] = Ranked_Pairs(votekit_profile)
    data['bucklin'] = Bucklin(votekit_profile)
    data['approval'] = Approval(votekit_profile)
    irv_with_exp = IRV_With_Explaination(votekit_profile)
    data['irv-rank'] = irv_with_exp
    print(data)
    grouped_data.append(data)

    # # check for spoiler effect by removing one candidate each time
    if len(candidates) > 1:
        print(candidates)
        for index, c in enumerate(candidates):
            new_candidates = candidates.copy()
            new_candidates.remove(c)
            print(c)
            print(new_candidates)
       
            data = {'file': full_path.replace('/Users/belle/Desktop/build/rcv_proposal/', ''), 'candidate_removed': c}
            
            data['plurality'] = Plurality(votekit_profile, new_candidates)
            data['IRV'] = IRV(votekit_profile, new_candidates)
            data['top-two'] = TopTwo(votekit_profile, new_candidates)
            # data['borda-pm'] = Borda_PM(votekit_profile, new_candidates)
            # data['borda-om'] = Borda_OM(votekit_profile, new_candidates)
            # data['borda-avg'] = Borda_AVG(votekit_profile, new_candidates)
            data['top-3-truncation'] = Top3Truncation(votekit_profile, new_candidates)
            data['condorcet'] = Condorcet(votekit_profile, new_candidates)
            data['smith'] = Smith(votekit_profile, new_candidates)
            data['smith-plurality'] = Smith_Plurality(votekit_profile, new_candidates)
            data['smith-irv'] = Smith_IRV(votekit_profile, new_candidates)
            data['minimax'] = Minimax(votekit_profile, new_candidates)
            data['smith-minimax'] = Smith_Minimax(votekit_profile, new_candidates)
            data['ranked-pairs'] = Ranked_Pairs(votekit_profile, new_candidates)
            data['bucklin'] = Bucklin(votekit_profile, new_candidates)
            data['approval'] = Approval(votekit_profile, new_candidates)
            data['irv-rank'] = irv_with_exp

            print(data)
            grouped_data.append(data)
    
    return grouped_data

def process_file(full_path, filename):
    print("RUNNING ", full_path, "\n")
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
    error_files = ['BallotPaperDetails-Brighton with candidates.csv', 'BallotPaperDetails-Northcote with candidates.csv', 'BallotPaperDetails-Werribee with candidates.csv', 'BallotPaperDetails-Point Cook with candidates.csv', 'BallotPaperDetails-Hawthorn with candidates.csv', 'BallotPaperDetails-Preston with Candidates.csv', 'BallotPaperDetails-Melton with candidates.csv']
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename not in error_files and (filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt')):
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