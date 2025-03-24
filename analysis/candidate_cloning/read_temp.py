import pandas as pd

# Read the CSV file
df = pd.read_csv("./results2.csv")

df[["candidate_cloned", "IRV", "condorcet"]].to_csv('./test.csv')