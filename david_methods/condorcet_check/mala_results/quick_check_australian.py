import os
import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods3 as mm
import david_methods as dm
import pandas as pd

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/australia/processed_data'
diff_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/condorcet_check/mala_results/australia_diff.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/david_methods/condorcet_check/mala_results/australia_processed.txt'
error_d = ["BallotPaperDetails-Northcote with candidates.csv", "BallotPaperDetails-Werribee with candidates.csv", "BallotPaperDetails-Point Cook with candidates.csv", "BallotPaperDetails-Preston with Candidates.csv", "BallotPaperDetails-Melton with candidates.csv", "SB2101 LA Pref Data_NA_Upper Hunter.csv"]
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename not in error_d and filename.endswith('.csv'):
            print(filename)
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

                

