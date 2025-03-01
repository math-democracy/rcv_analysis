import pandas as pd

original = pd.read_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/results/current/america.csv')
updated = pd.read_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/new_america.csv')

new = original.merge(updated, how='left', on='file')

print(len(original), len(updated), len(new))
if len(original) != len(new):
      print('INCONSISTENT LENGTH')
print(new.columns)
columns = ['file', 'numCands', 'plurality', 'IRV', 'top-two',
       'borda_pm', 'borda_om', 'borda_avg', 'top-3-truncation',
       'condorcet', 'minimax', 'smith_plurality', 'smith_irv', 'smith-minimax',
       'ranked-pairs', 'bucklin', 'approval', 'smith']

new = new[columns].rename(columns = {'borda_pm':'borda-pm','borda_om':'borda-om','borda_avg':'borda-avg'})
new['numCands'] = new['numCands'].astype(int)
print(new.columns)
new.to_csv('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/america_updated.csv', index=False)