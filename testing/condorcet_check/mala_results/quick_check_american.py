import os
import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods3 as mm
import david_methods as dm
import pandas as pd

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/american/processed_data'
diff_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/condorcet_check/mala_results/american_diff.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/condorcet_check/mala_results/american_processed.txt'
error_d = ["Minneapolis_11052013_Mayor.csv", 
"Portland_D1_2024.csv", 
"Portland_D3_2024.csv", 
"Portland_D2_2024.csv", 
"Portland_D4_2024.csv", 
"Oakland_11082022_Mayor.csv", 
"Oakland_11052024_CityCouncil_AtLarge.csv", 
"SanFrancisco_11022004_BoardofSupervisorsDistrict5.csv", 
"SanFrancisco_11082011_Mayor.csv", 
"SanFrancisco_11052024_Mayor.csv", 
"SanFrancisco_11022010_BoardofSupervisorsDistrict10.csv", 
"NewYorkCity_06222021_DEMCouncilMember27thCouncilDistrict.csv", 
"NewYorkCity_06222021_DEMMayorCitywide.csv", 
"NewYorkCity_06222021_DEMBoroughPresidentKings.csv", 
"NewYorkCity_06222021_DEMCouncilMember26thCouncilDistrict.csv", 
"NewYorkCity_06222021_DEMComptrollerCitywide.csv", 
"NewYorkCity_06222021_DEMCouncilMember9thCouncilDistrict.csv", 
"NewYorkCity_06222021_DEMCouncilMember7thCouncilDistrict.csv", 
"Cambridge_11082011_CityCouncil.csv", 
"Cambridge_11152019_CityCouncil.csv", 
"Cambridge_11072017_CityCouncil.csv", 
"Cambridge_11062001_CityCouncil.csv", 
"Cambridge_11032009_CityCouncil.csv", 
"Cambridge_11072023_CityCouncil.csv", 
"Cambridge_11062007_CityCouncil.csv", 
"Cambridge_11152019_SchoolCommittee.csv", 
"Cambridge_11032015_SchoolCommittee.csv", 
"Cambridge_11082011_SchoolCommittee.csv", 
"Cambridge_11072023_SchoolBoard.csv", 
"Cambridge_11052013_CityCouncil.csv", 
"Cambridge_11072017_SchoolCommittee.csv", 
"Cambridge_11032015_CityCouncil.csv", 
"Cambridge_11082005_CityCouncil.csv", 
"Cambridge_11042003_CityCouncil.csv"]

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename not in error_d and filename.endswith('.csv'):
            full_path = os.path.join(dirpath, filename)

            df = pd.read_csv(full_path)
            columns = [c for c in df.columns if 'rank' in c or c == 'numSeats' or c == 'numCands']
            d_profile = df[columns]
            d_profile = d_profile.value_counts().reset_index(name='Count')

            num_cands = df['numCands'].iloc[0]

            v =  mm.v_profile(full_path)
            candidates = list(v.candidates)
            candidates.remove('skipped')

            matrix = dm.pairwise_comparisons_matrix(d_profile, candidates, num_cands, None)
            david_c_winner = dm.Condorcet_winner(d_profile, candidates, num_cands, None, matrix)

            mala_c_winner = list(mm.Condorcet(v,candidates))

            david_m_winner = dm.minimax_winner(d_profile, candidates, num_cands, None, matrix)
            mala_m_winner = mm.Minimax(v, candidates)

            if david_c_winner != mala_c_winner:
                with open(diff_file, "a") as ef:
                    ef.write(f"{filename} -- Condorcet -- david: {david_c_winner} , mala: {mala_c_winner} \n")

            if david_m_winner != mala_m_winner:
                with open(diff_file, "a") as ef:
                    ef.write(f"{filename} -- Minimax -- david: {david_m_winner} , mala: {mala_m_winner} \n")
        
            with open(processed_file, "a") as ef:
                ef.write(f"'{filename}', \n")

                

