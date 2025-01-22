import os
import pandas as pd
import random

root_dir = '/Users/belle/Desktop/build/rcv_proposal/american/processed_data'
output_folder = '/Users/belle/Desktop/build/rcv_proposal/election_generation/american_generated'

# 1001 ballots, 10000 samples

def process_file(file, filename):
    df = pd.read_csv(file)
    for i in range(100):
        sample_percentage = random.uniform(0.1, 0.2)
        sampled_df = df.sample(frac=sample_percentage)
        new_file_name = filename.split(".csv")[0] + "_" + str(i) + ".csv"
        print(new_file_name)
        output_file = os.path.join(output_folder, new_file_name)
        sampled_df.to_csv(output_file, index=False)

def main():
    # loop through data files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                full_path = os.path.join(dirpath, filename)
                process_file(full_path, filename)

if __name__ == '__main__':
    main()
            