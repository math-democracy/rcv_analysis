import main_methods as mm
import os
import pandas as pd
import asyncio
from concurrent.futures import ProcessPoolExecutor
import csv

def process_csv(full_path):
    try:
        # create profile + candidate list
        v_profile =  mm.v_profile(full_path)
        candidates = list(v_profile.candidates)

        data = {'file': full_path}

        num_cands = len(candidates)
        data['numCands'] = num_cands

        data['plurality'] = list(mm.Plurality(prof=v_profile))
        data['IRV'] = list(mm.IRV(prof=v_profile))
        data['top-two'] = list(mm.TopTwo(prof=v_profile))
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
        data['smith'] = list(mm.Smith(prof=v_profile))
        return data
    except Exception as e:
        print(f"Error processing folder {full_path}: {e}")
        return {}

def process_folder(folder_path, output_folder):
    """ Process all CSVs in a folder and merge them into a single output CSV. """
    try:
        all_data = []
        
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                file_path = os.path.join(folder_path, file_name)
                result = process_csv(file_path)
                all_data.append(result)

        if all_data:
            output_file = os.path.join(output_folder, f"{os.path.basename(folder_path)}.csv")
            
            keys = all_data[0].keys()

            with open(output_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(keys)
                for vote in all_data:
                    row = [vote.get(key, '') for key in keys]
                    writer.writerow(row)
    
    except Exception as e:
        print(f"Error processing folder {folder_path}: {e}")

# async def process_all_folders(base_folder, output_folder):
#     """ Process all folders concurrently using multiprocessing. """
#     loop = asyncio.get_running_loop()
#     tasks = []

#     folder_paths = [
#         root for root, _, _ in os.walk(base_folder) if root != base_folder  # Exclude base folder itself
#     ]

#     with ProcessPoolExecutor(max_workers=min(4, len(folder_paths))) as executor:  
#         for folder_path in folder_paths:
#             task = loop.run_in_executor(executor, process_folder, folder_path, output_folder)
#             tasks.append(task)

#         await asyncio.gather(*tasks)

# if __name__ == "__main__":
#     base_folder = "/Users/belle/Desktop/build/rcv_proposal/raw_data/america/processed_data/New Mexico"
#     output_folder = "/Users/belle/Desktop/build/rcv_proposal/results/generated"
#     process_folder(base_folder, output_folder)
#     # asyncio.run(process_all_folders(base_folder, output_folder))


# folders = [
#     "/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/Alameda County/Berkeley_11042014_CityAuditor.csv",
# "/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/Alameda County/Oakland_11062018_SchoolDirectorDistrict2.csv",
# "/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/Alameda County/Oakland_11082016_CityAttorney.csv",
# "/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/Alameda County/SanLeandro_11082016_CountyCouncilDistrict4.csv",
# "/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/Alameda County/SanLeandro_11082016_CountyCouncilDistrict6.csv",
# "/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/San Francisco/SanFrancisco_11052024_Treasurer.csv",
# "/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/San Francisco/SanFrancisco_11062018_PublicDefender.csv",
# "/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/San Francisco/SanFrancisco_11082022_AssessorRecorder.csv",
# "/Users/belle/Desktop/build/rcv/raw_data/america/processed_data/San Francisco/SanFrancisco_11082022_BoardofSupervisorsD2.csv"
# ]

# all_data = []
# for f in folders:
#     data = process_csv(f)
#     all_data.append(data)

# keys = all_data[0].keys()

# with open("output.csv", mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(keys)
#     for vote in all_data:
#         row = [vote.get(key, '') for key in keys]
#         writer.writerow(row)


print(process_csv())