import pandas as pd

df = pd.read_csv('./metadata_america3.csv')

df = df[df['num_cands'] == 1]

print(len(df))
print(df)