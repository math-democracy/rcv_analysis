from main_methods2 import *
import multiprocessing
import csv
import os

data_file = '/Users/belle/Desktop/build/rcv_proposal/analysis/scotland_results.csv'
root_dir = '/Users/belle/Desktop/build/rcv_proposal/scotland/processed_data'

error_file = '/Users/belle/Desktop/build/rcv_proposal/analysis/scotland_error.txt'
processed_file = '/Users/belle/Desktop/build/rcv_proposal/analysis/scotland_processed.txt'
all_data = []

error_d = ["Ward13Garscadden-Scotstounhill_glasgow12-13.csv", "Ward12PartickWest_glasgow12-12.csv", "Ward5Govan_glasgow12-05.csv", "Ward11Hillhead_glasgow12-11.csv", "Linn_linn.csv", "govan_govan.csv", "Pollokshields_pollokshields.csv", "Bailliestonward_baillieston.csv", "Craigtonward_craigton.csv", "Canalward_canal.csv", "EastCentre_eastcentre.csv", "Hillhead_hillhead.csv", "Shettleston_shettleston.csv", "Garscadden_garscadden.csv", "Clarkston,NetherleeandWilliamwood_e-renfs17-4.csv", "Ward6Pollokshields_Ward6.csv", "Ward3GreaterPollok_Ward3.csv", "Ward5Govan_Ward5.csv", "Ward01-NorthCoast_Preference-Profile-North-Coast_copy.csv", "Ward02-GarnockValley_Preference-Profile-Garnock-Valley_copy.csv", "Ward10-Eileana'Cheo_highland17-10.csv", "Barraigh,BhatarsaighEirisgeighAgusUibhistADeas_eilean-siar12-01.csv", "Ward19-Mearns_preferenceprofile_v0001_ward-19-mearns_06052022_172124.csv", "Ward12-LeithWalk_ward12.csv", "Ward11-CityCentre_ward11.csv", "Ward16-Liberton-Gilmerton_ward16.csv", "Ward19-MotherwellSouthEastandRavenscraig_n-lanarks17-019.csv", "LeithWalkWard_edinburgh12-12.csv", "Ward12-LeithWalk_edinburgh17-12.csv", "Ward1-Almond_edinburgh17-01.csv", "Ward13GarscaddenScotstounhill_glasgow17-013.csv", "Ward1Linn_glasgow17-001.csv", "Ward19Shettleston_glasgow17-019.csv"]
def file_less_than_3mb(file_path):
    try:
        file_size = os.path.getsize(file_path)  # Get file size in bytes
        return file_size < 5 * 1024 * 1024  # 1 MB in bytes
    except FileNotFoundError:
        print("File not found.")
        return False

def run_voting_methods(full_path):
    v =  v_profile(full_path)
    profile, file_path, candidates_with_indices, candidates = p_profile(full_path)
    candidates_index = list(range(len(candidates)))
    grouped_data = []
    data = {'file': full_path.replace('/Users/belle/Desktop/build/rcv_proposal/', ''), 'candidate_removed': 'none'}
        
    data['plurality'] = Plurality(prof=profile, cands_to_keep=candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
    data['IRV'] = IRV(prof=v, cands_to_keep=candidates, candidates_with_indices=candidates_with_indices, package="votekit")
    data['top-two'] = TopTwo(prof=v, cands_to_keep=candidates)
    data['borda-pm'] = Borda_PM(prof=v, cands_to_keep=candidates)
    data['top-3-truncation'] = Top3Truncation(prof=v, cands_to_keep=candidates)
    data['condorcet'] = Condorcet(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['minimax'] = Minimax(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    data['smith'] = Smith(prof=profile, candidates_with_indices=candidates_with_indices, cands_to_keep=candidates_index)
    # data['smith-irv'] = Smith_IRV(prof=profile, candidates_with_indices=candidates_with_indices)
    data['smith-minimax'] = Smith_minimax(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)
    data['ranked-pairs'] = Ranked_Pairs(prof=profile, candidates_with_indices=candidates_with_indices,cands_to_keep=candidates_index)
    # data['bucklin'] = Bucklin(prof=profile, candidates_with_indices=candidates_with_indices, package="pref_voting")
    print(data)
    grouped_data.append(data)

    print(candidates_with_indices)

    for index, c in enumerate(candidates):
        new_candidates = candidates.copy()
        new_candidates.remove(c)
        new_candidates_index = candidates_index.copy()
        new_candidates_index.remove(index)

        print(index, c)
        print(new_candidates_index)
        print(new_candidates)
        
        data = {'file': full_path.replace('/Users/belle/Desktop/build/rcv_proposal/', ''), 'candidate_removed': c}
        
        data['plurality'] = Plurality(prof=profile, cands_to_keep=new_candidates_index, candidates_with_indices=candidates_with_indices, package="pref_voting")
        data['IRV'] = IRV(prof=v, cands_to_keep=new_candidates, candidates_with_indices=candidates_with_indices, package="votekit")
        data['top-two'] = TopTwo(prof=v, cands_to_keep=new_candidates)
        data['borda-pm'] = Borda_PM(prof=v, cands_to_keep=new_candidates)
        data['top-3-truncation'] = Top3Truncation(prof=v, cands_to_keep=new_candidates)
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
    print(all_data, "\n")

    with open(data_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write the header if the file is empty
        if os.stat(data_file).st_size == 0:
            header = all_data[0].keys()
            writer.writerow(header)

        # Write each row of data
        for data in all_data:
            keys = all_data[0].keys()
            row = [data.get(key, '') for key in keys]
            writer.writerow(row)

    with open(processed_file, "a") as ef:
        ef.write(f"{filename}, ")

def main():
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            print(filename)
            if filename in error_d and (filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt')):
                full_path = os.path.join(dirpath, filename)
                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_file, args=(full_path,filename))
                    p.start()
                    p.join(200)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(error_file, "a") as ef:
                            ef.write(f"{filename}, ")
                        p.terminate()
                        p.join()
                        print("\n")
            
if __name__ == '__main__':
    main()
            