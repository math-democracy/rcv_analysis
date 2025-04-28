import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
from main_methods import v_profile, Borda_AVG_Return_Full, Borda_OM_Return_Full, Borda_PM_Return_Full
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
    scores_avg = Borda_AVG_Return_Full(v, tiebreak="first_place")
    scores_om = Borda_OM_Return_Full(v, tiebreak="first_place")
    scores_pm = Borda_PM_Return_Full(v, tiebreak="first_place")

    scores_avg = {k: float(v) for k, v in sorted(scores_avg.items(), key=lambda item: float(item[1]), reverse=True)}
    scores_om = {k: float(v) for k, v in sorted(scores_om.items(), key=lambda item: float(item[1]), reverse=True)}
    scores_pm = {k: float(v) for k, v in sorted(scores_pm.items(), key=lambda item: float(item[1]), reverse=True)}

    print("AVG")
    print(scores_avg)
    print("OM")
    print(scores_om)
    print("PM")
    print(scores_pm)
    return None

calculate_borda('/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/Minneapolis/Minneapolis_11072017_PRBoardDistrict4.csv')


# processed_file = './analysis/fringe/supporting_files/america_processed.txt'

# root_dir = './raw_data/america/processed_data'
# error_file = './analysis/fringe/supporting_files/america_error.txt'
# output_file = './analysis/fringe/borda_scores/america_borda_scores.json'

# def process_file(file_path, filename):
#     print("processing: ",file_path)
#     scores = calculate_borda(file_path)
#     if os.path.exists(output_file):
#         with open(output_file, "r") as json_file:
#             try:
#                 data = json.load(json_file)
#             except json.JSONDecodeError:
#                 data = {}
#     else:
#         data = {}
    
#     data[filename] = scores
    
#     with open(output_file, "a") as json_file:
#         json.dump(data, json_file, indent=4)
    
#     with open(processed_file, "a") as ef:
#         ef.write(f"{filename}, ")
    
#     print(scores)


# def main():
#     # loop through data files
#     for dirpath, dirnames, filenames in os.walk(root_dir):
#         for filename in filenames:
#             if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
#                 file_path = os.path.join(dirpath, filename)

#                 # ensure that if it runs for more than x seconds, kill the process
#                 if __name__ == '__main__':
#                     p = multiprocessing.Process(target=process_file, args=(file_path,filename))
#                     p.start()
#                     p.join(20)

#                     if p.is_alive():
#                         print("running... let's kill it...")
#                         with open(error_file, "a") as ef:
#                             ef.write(f"{filename}, ")
#                         p.terminate()
#                         p.join()
#                         print("\n")
            
# if __name__ == '__main__':
#     #main()
#     process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/LasCruces_11052019_COUNCILORPOSITION2CITYOFLASCRUCESDISTRICT2COUNCILOR.csv','LasCruces_11052019_COUNCILORPOSITION2CITYOFLASCRUCESDISTRICT2COUNCILOR.csv')
#     process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/LasCruces_11052019_COUNCILORPOSITION4CITYOFLASCRUCESDISTRICT4COUNCILOR.csv','LasCruces_11052019_COUNCILORPOSITION4CITYOFLASCRUCESDISTRICT4COUNCILOR.csv')
#     process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/LasCruces_11052019_MAYORCITYOFLASCRUCES.csv','LasCruces_11052019_MAYORCITYOFLASCRUCES.csv')
#     process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/SantaFe_03062018_CityCouncilDistrict4.csv','SantaFe_03062018_CityCouncilDistrict4.csv')
#     process_file('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data/New Mexico/SantaFe_03062018_Mayor.csv','SantaFe_03062018_Mayor.csv')
#     #process_file('american/Cambridge, MA/Cambridge_11042003_SchoolCommittee.csv','Cambridge_11042003_SchoolCommittee.csv')