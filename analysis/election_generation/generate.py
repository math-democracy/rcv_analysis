## REGULAR VERSION

# import os
# import pandas as pd
# import random
# import time

# root_dir = '/Users/belle/Desktop/build/rcv_proposal/american/processed_data'
# output_folder = '/Users/belle/Desktop/build/rcv_proposal/election_generation/american_generated'

# # 1001 ballots, 10000 samples

# def process_file(file, filename):
#     df = pd.read_csv(file)
#     for i in range (10000):
#         data = []
#         for j in range(1001):
#             random_row = df.sample(n=1, replace=True)  
#             data.append(random_row)
        
#         new_election = pd.concat(data, ignore_index=True)
#         new_file_name = filename.split(".csv")[0] + "_" + str(i) + ".csv"
#         print(new_file_name)
#         output_file = os.path.join(output_folder, new_file_name)
#         new_election.to_csv(output_file, index=False)

# def main():
#     # loop through data files
#     for dirpath, dirnames, filenames in os.walk(root_dir):
#         for filename in filenames:
#             if filename.endswith('.csv'):
#                 full_path = os.path.join(dirpath, filename)
#                 process_file(full_path, filename)

# if __name__ == '__main__':
#     main()
            

## ASYNC VERSION

import os
import pandas as pd
import concurrent.futures

root_dir = '/Users/belle/Desktop/build/rcv_proposal/american/processed_data'
output_folder = '/Users/belle/Desktop/build/rcv_proposal/election_generation/american_generated'

def process_file(file, filename):
    df = pd.read_csv(file)
    for i in range(10000):
        data = []
        for j in range(1001):
            random_row = df.sample(n=1, replace=True)
            data.append(random_row)
        
        new_election = pd.concat(data, ignore_index=True)
        new_file_name = filename.split(".csv")[0] + "_" + str(i) + ".csv"
        output_file = os.path.join(output_folder, new_file_name)
        new_election.to_csv(output_file, index=False)
    print(f"Finished processing {filename}")

def main():
    # Collect all CSV files
    tasks = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                full_path = os.path.join(dirpath, filename)
                tasks.append((full_path, filename))
    
    # Process files in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_file, file, filename) for file, filename in tasks]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # To raise any exceptions that occurred
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    main()