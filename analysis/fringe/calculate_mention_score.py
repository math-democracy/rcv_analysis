import os
import multiprocessing
import pandas as pd
import json

root_dir = './raw_data/america/processed_data'
error_file = './analysis/fringe/supporting_files/america_error.txt'
output_file = './analysis/fringe/mention_scores/america_mention_scores.json'
def calculate_mention_scores(df, filename):
    rank_columns = [col for col in df.columns if col.startswith('rank')]
    num_ranks = len(rank_columns)

    mention_scores = {}
    num_cands = 0
    for index, row in df.iterrows(): 
        if index == 0:
            num_cands = row['numCands']

        #print(num_cands)
        ranked_candidates = [row[col] for col in rank_columns if (row[col] != "skipped" and row[col] != "Unknown" and row[col] != "nan")]
        # if pd.isna(row['Num Cands']):
        #     with open(error_file, "a") as ef:
        #         ef.write(f"{filename}:{index}, ")

        
        if len(ranked_candidates) == num_cands: # if all possible candidates are ranked, don't consider last place
            ranked_candidates = ranked_candidates[:-1]
        elif len(ranked_candidates) > num_cands:
            with open(error_file, "a") as ef:
                ef.write(f"{filename}:{index}, ")
        
        for candidate in ranked_candidates: 
                if candidate != "writein" and candidate != "UWI" and candidate != "Write-In" and candidate != "Write-in":
                    mention_scores[candidate] = mention_scores.get(candidate, 0) + 1
   
    return mention_scores

def process_file(file_path, filename):
    df = pd.read_csv(file_path)
    scores = calculate_mention_scores(df, filename)
    if os.path.exists(output_file):
        with open(output_file, "r") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    
    # Append new data
    data[filename] = scores
    
    with open(output_file, "a") as json_file:
        json.dump(data, json_file, indent=4)
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
    #main()
    process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/LasCruces_11052019_COUNCILORPOSITION2CITYOFLASCRUCESDISTRICT2COUNCILOR.csv','LasCruces_11052019_COUNCILORPOSITION2CITYOFLASCRUCESDISTRICT2COUNCILOR.csv')
    process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/LasCruces_11052019_COUNCILORPOSITION4CITYOFLASCRUCESDISTRICT4COUNCILOR.csv','LasCruces_11052019_COUNCILORPOSITION4CITYOFLASCRUCESDISTRICT4COUNCILOR.csv')
    process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/LasCruces_11052019_MAYORCITYOFLASCRUCES.csv','LasCruces_11052019_MAYORCITYOFLASCRUCES.csv')
    process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/SantaFe_03062018_CityCouncilDistrict4.csv','SantaFe_03062018_CityCouncilDistrict4.csv')
    process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/SantaFe_03062018_Mayor.csv','SantaFe_03062018_Mayor.csv')
                        

# process_file('/Users/belle/Desktop/build/rcv_proposal/raw_data/american/processed_data/New York City/NewYorkCity_06222021_REPBoroughPresidentRichmond.csv', 'test.csv')