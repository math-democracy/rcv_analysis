import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import os
import pandas as pd

filenames_col = []
borda_om = []
borda_pm = []
borda_avg = []

def process_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.csv'):
                        print(f'processing: {filename}')
                        full_path = os.path.join(dirpath, filename)
                        filenames_col.append(full_path.replace(root_dir+'/',''))

                        v = mm.v_profile(full_path)

                        try:
                            borda_pm_winner = mm.Borda_PM(prof = v, tiebreak='random')
                        except Exception as e:
                            borda_pm_winner = ['ERROR']

                        if borda_pm_winner:
                            borda_pm.append(list(borda_pm_winner))
                        else:
                            borda_pm.append(None)

                        try:
                            borda_om_winner = mm.Borda_OM(prof = v, tiebreak='random')
                        except Exception as e:
                            borda_om_winner = ['ERROR']

                        if borda_om_winner:
                            borda_om.append(list(borda_om_winner))
                        else:
                            borda_om.append(None)

                        try:
                            borda_avg_winner = mm.Borda_AVG(prof = v, tiebreak='random')
                        except Exception as e:
                            borda_avg_winner = ['ERROR']

                        if borda_avg_winner:
                            borda_avg.append(list(borda_avg_winner))
                        else:
                            borda_avg.append(None)

    if (len(filenames_col) != len(borda_om)) and (len(filenames_col) != len(borda_pm)) and (len(filenames_col) != len(borda_avg)):
        print('INCONSISTENT LENGTHS')

    df = pd.DataFrame({'file':filenames_col,'borda_pm': borda_pm, 'borda_om': borda_om, 'borda_avg': borda_avg})
    return df

root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/scotland/processed_data'
df = process_files(root_dir)

df.to_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/new_scotland.csv')
