import os
import pandas as pd

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/civs/raw_data' # UPDATE TO WHERE BLT DATA IS STORED eg. /Users/xiaokaren/MyPythonCode/ranked_choice_voting/raw/Australia_Victoria_LegAssembly_2022

processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/american/processed.txt'

count = 0

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.csv'):
            full_path = os.path.join(dirpath, filename)

            df = pd.read_csv(full_path)
            df = df.rename(columns={"Num Seats": "numSeats",
                               "Num Cands": "numCands",
                               "Num seats": "numSeats",
                               "Num cands": "numCands"})
            
            num_columns = len(df.columns)

            base_columns = list(df.columns[:-2])
            
            base_columns.append('numSeats')
            base_columns.append('numCands')

            df = df[base_columns]

            if num_columns == len(df.columns):
                print(filename)
                output_path = dirpath.replace('raw','processed')

                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                df.to_csv(output_path + '/' + filename, index=False)

                with open(processed_file, "a") as ef:
                    ef.write(f"{filename},\n")
            
