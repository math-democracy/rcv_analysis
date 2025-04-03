import pandas as pd

og = pd.read_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/scotland_results_top4.csv')

smith = pd.read_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/scotland_results_top4.csv')

df = og.merge(smith, on='file')

columns = ['file', 'numCands_x', 'plurality', 'IRV', 'top-two', 'borda-pm',
       'borda-om', 'borda-avg', 'top-3-truncation', 'condorcet', 'minimax',
       'smith_plurality', 'smith_irv', 'smith-minimax', 'ranked-pairs',
       'bucklin', 'approval', 'top4_plurality', 'top4_IRV', 'top4_top-two',
       'top4_borda-pm', 'top4_borda-om', 'top4_borda-avg',
       'top4_top-3-truncation', 'top4_condorcet', 'top4_minimax',
       'top4_smith_plurality', 'top4_smith_irv', 'top4_smith-minimax',
       'top4_ranked-pairs', 'top4_bucklin', 'top4_approval',
       'smith', 'top4_smith']
df = df[columns].rename(columns = {'numCands_x':'numCands'})

df.to_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/scotland_results_top4_new.csv', index=False)