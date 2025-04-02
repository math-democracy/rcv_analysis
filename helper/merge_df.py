import pandas as pd

def merge(file1, file2, output):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    merged = pd.merge(df1, df2, on=['file'], how='inner')

    merged.to_csv(output)

merge('/Users/belle/Desktop/build/rcv_proposal/australia.csv', '/Users/belle/Desktop/build/rcv_proposal/results/current/australia.csv', './hello.csv')