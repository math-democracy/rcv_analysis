import sys
sys.path.append('/Users/belle/Desktop/build/rcv_proposal')
from main_methods3 import v_profile, Borda_AVG_Return_Full
# from david_methods import Borda_AVG_Return_Full
import os
import multiprocessing
import pandas as pd
import json

def calculate_borda(file):
    v = v_profile(file)
    df = pd.read_csv(file)
    columns = [c for c in df.columns if 'rank' in c]
    d_profile = df[columns]
    d_profile = d_profile.value_counts().reset_index(name='Count')

    candidates = list(v.candidates)
    num_cands = len(candidates)

    # scores = Borda_AVG_Return_Full(d_profile, candidates, num_cands, False)
    scores = Borda_AVG_Return_Full(v)

    scores = {k: float(v) for k, v in sorted(scores.items(), key=lambda item: float(item[1]), reverse=True)}

    return scores

# calculate_borda('/Users/belle/Desktop/build/rcv_proposal/raw_data/australia/processed_data/Australia_Victoria_LegAssembly_2022/BallotPaperDetails-Northcote with candidates.csv')


processed_file = './scotland_processed.txt'

root_dir = '/Users/belle/Desktop/build/rcv_proposal/raw_data/australia/processed_data'
error_file = './america.txt'
output_file = './scotland_mention_scores.json'

def process_file(file_path, filename):
    print("processing: ",file_path)
    scores = calculate_borda(file_path)
    if os.path.exists(output_file):
        with open(output_file, "r") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    
    data[filename] = scores
    
    with open(output_file, "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    with open(processed_file, "a") as ef:
        ef.write(f"{filename}, ")
    
    print(scores)


def main():
    # loop through data files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                file_path = os.path.join(dirpath, filename)

                # ensure that if it runs for more than x seconds, kill the process
                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_file, args=(file_path,filename))
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