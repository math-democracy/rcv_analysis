import sys
sys.path.append('/Users/belle/Desktop/build/rcv_proposal')
import multiprocessing
import main_methods as mm
import pandas as pd
import csv
import random
from collections import defaultdict
from raw_data.scotland.scotland_parser import parse_file, parse_to_csv
import os
import re

root_dir = '../../raw_data/preference_profiles/australia'
output_folder = './files2'
country = "australia"

def clean_path(path):
    return re.sub(r"/0\.[0-5]/", "/", path)  # Remove /0.x/ where x is 0-5

def run_voting_methods(full_path):
    # create profile + candidate list
    candidate = full_path.split('_')[-1].replace('.csv', '')
    filename = full_path.replace(f'_{candidate}', '')
    v_profile =  mm.v_profile(full_path)
    candidates = [candidate for candidate in v_profile.candidates if candidate != "skipped"]

    data = {'file': clean_path(filename.replace(output_folder, '')), 'candidate_cloned': candidate}

    num_cands = len(candidates)
    data['numCands'] = num_cands

    data['plurality'] = list(mm.Plurality(prof=v_profile))
    data['IRV'] = list(mm.IRV(prof=v_profile))
    data['top-two'] = list(mm.TopTwo(prof=v_profile, tiebreak="first_place"))
    data['borda-pm'] = list(mm.Borda_PM(v_profile, tiebreak="first_place"))
    data['borda-om'] = list(mm.Borda_OM(v_profile, tiebreak="first_place"))
    data['borda-avg'] = list(mm.Borda_AVG(v_profile, tiebreak="first_place"))
    data['top-3-truncation'] = list(mm.Top3Truncation(prof=v_profile))
    data['condorcet'] = list(mm.Condorcet(prof=v_profile))
    data['minimax'] = list(mm.Minimax(prof=v_profile))
    data['smith_plurality'] = list(mm.Smith_Plurality(prof=v_profile))
    data['smith_irv'] = list(mm.Smith_IRV(prof=v_profile))
    data['smith-minimax'] = list(mm.Smith_Minimax(prof=v_profile))
    data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v_profile))
    data['bucklin'] = list(mm.Bucklin(prof=v_profile))
    data['approval'] = list(mm.Ranked_Pairs(prof=v_profile))

    # if os.path.exists(full_path):
    #     os.remove(full_path)
    #     print("file deleted successfully")
    # else:
    #     print("file not found")
     
    return data

def insert_after_n(arr, n, x, percent):
    result = []
    
    for sublist in arr:
        new_sublist = sublist[:]
        amount = new_sublist[0]
        last = new_sublist[-1]
        if last == 0:
            # separate out each voter for each type of ballot
            for i in range(amount):
                new_sub_sublist = new_sublist[1:]
                for i in range(0, len(new_sub_sublist) - 1): #exclude 0 in the end
                    if new_sub_sublist[i] == n:
                        if random.random() < percent:
                            new_sub_sublist.insert(i, x)
                            break
                        else:
                            new_sub_sublist.insert(i + 1, x)
                            break
                result.append(new_sub_sublist)
    
    count_dict = defaultdict(int)

    for votes in result:
        count_dict[tuple(votes)] += 1

    res = [[count] + list(votes) for votes, count in count_dict.items()]

    return res


def process_data(file, filename, output_folder, results, percent):
    data = parse_file(file)
    print(f'processing {file}')
    num_candidates = data['num_candidates'] + 1
    candidates = []
    for c in data['candidates']:
        candidates.append(c.replace('/', ''))
    candidates.append('Cloned_Candidate')

    for index, c in enumerate(data['candidates']):
        ballots = insert_after_n(data['ballots'],  index + 1, num_candidates, percent)

        new_election = {
            "num_positions": data['num_positions'],
            "num_candidates": num_candidates,
            "ballots": ballots,
            "candidates": candidates,
        }
        c = c.replace('/', '_')
        new_output_folder = os.path.join(output_folder, str(percent))

        if not os.path.exists(new_output_folder):
            os.mkdir(new_output_folder)
        outfilepath = f'{new_output_folder}/{filename}_{c}.csv'
        print('start processing')
        parse_to_csv(new_election, outfilepath)
        print('done parsing')
        d = run_voting_methods(outfilepath)
        print('done running voting method')

        with open(results, mode='a', newline='') as file:
            writer = csv.writer(file)

            # write header if the file is empty
            if os.stat(results).st_size == 0:
                header = d.keys()
                writer.writerow(header)
            print(d)
            keys = d.keys()
            row = [d.get(key, '') for key in keys]
            writer.writerow(row)
        
        with open(f'./success_{country}.txt', "a") as ef:
            ef.write(f"{filename}, ")

def main(percent):
    # loop through data files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                print(filename)
                full_path = os.path.join(dirpath, filename)
                lowest_folder = os.path.basename(os.path.dirname(full_path))
                output = os.path.join(output_folder, lowest_folder)
                results = f'./results3/{country}_{percent}.csv'
                if not os.path.exists(output):
                    os.makedirs(output)

                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_data, args=(full_path, filename.replace('.csv', ''), output, results, percent))
                    p.start()
                    p.join(20)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(f'./error_{country}.txt', "a") as ef:
                            ef.write(f"{filename}, ")
                        p.terminate()
                        p.join()
                        print("\n")
            
if __name__ == '__main__':
    if (len(sys.argv) > 1):      
        percent = float(sys.argv[1])

        if percent > 1: 
            percent = percent / 100
        
        main(percent)
    else:
        print("Please add an argument for what percent of the cloned candidate should go above the candidate")
        sys.exit(1)

# arr = [[1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 4, 5, 6, 7, 8]]

# for i in range(20):
#     process_data('/Users/belle/Desktop/build/rcv_proposal/raw_data/preference_profiles/scotland/glasgow12/Ward7Langside_glasgow12-07-recalc.csv', 'Ward7Langside_glasgow12-07-recalc', './temp_files', 'results2.csv', 0.5)