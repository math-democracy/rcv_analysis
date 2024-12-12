import pandas as pd
import os
import sys

'''
NOTES: 
    New South Wales: zipped csv files
        QUESTIONS: what is preferenceMark, preferenceNumber, and drawOrder
        COLUMNS:
            Australia_NSW_Mayorals_2021: [SequenceNumber,VoteType,Venue/VoteSubType,VCBallotPaperID,PreferenceMark,PreferenceNumber,CandidateName,DrawOrder,Formality,Type]
            Australia_NSW_State_LegAssembly_2015: [District,PollingPlaceName,BPNumber,Formality,CandidateName,PrefMarking,PrefCounted]
            Australia_NSW_State_LegAssembly_2019: [District,PollingPlaceName,BPNumber,Formality,CandidateName,PrefMarking,PrefCounted]
            Australia_NSW_State_LegAssembly_2023: [District,PollingPlaceName,BPNumber,Formality,CandidateName,PrefMarking,PrefCounted]
            Australia_NSW_LegAssembly_2017_ByElections: [District,PollingPlaceName,BPNumber,Formality,CandidateName,PrefMarking,PrefCounted]
            Australia_NSW_LegAssembly_ByElections_Miscellaneous: [District,PollingPlaceName,BPNumber,Formality,CandidateName,PrefMarking,PrefCounted]

    Victoria: Excel Files
        QUESTIONS: what is this format
        COLUMNS:
            Australia_Victoria_LegAssembly_2018: 
            Australia_Victoria_LegAssembly_2022: 
'''
state = 'Victoria'

filepath = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/BallotPaperDetails-Melbourne District SE2018.xlsx - BallotPaperDetails-Melbourne Di.csv'

# TO DO: this is just what I think the literal R -> Python translation is atm, but need to update after meeting
    # gives output, but the output is different than what the R code outputs, but I was looking at the outputted rows and it seems like this is more correct than the R code
def preprocess_victoria(filepath):
    # read in excel file
    df = pd.read_excel(filepath)

    # Rename column indicating batch numbers and counts
    df.rename(columns={'Unnamed: 0': 'col1'}, inplace=True)
    
    # Remove all rows not representing a ballot
    df = df[df['col1'] != "Ballot Paper Preferences Recorded Against Candidates in Ballot Paper Order"]
    df = df[~df['col1'].str.contains("Batch No.", na=False)]
    df = df[df['col1'].notna()]
    
    # Add BPNumber column 
    df['BPNumber'] = range(1, len(df) + 1)
    df.drop(columns=['col1'], inplace=True)
    df = df[['BPNumber'] + [col for col in df.columns if col != 'BPNumber']]
    df['BPNumber'] = df['BPNumber'].astype(str)
    
    # Pivot wide to long to mimic NSW files
    df = pd.melt(df, id_vars=['BPNumber'], var_name='CandidateName', value_name='PrefCounted')
    
    # Remove rows with NaN values
    df.dropna(inplace=True)

    return df

def preprocess_nsw(filepath):
    df = pd.read_csv(filepath, sep='\t',low_memory=False)
    return df

def parse_to_csv(df, outfilepath):
    # standardize column headers
    df = df.rename(columns={'VCBallotPaperID':'BPNumber',
                            'PreferenceNumber':'PrefCounted'})

    df = df.drop(['DrawOrder','SequenceNumber','PrefMarking','PreferenceMark'], axis=1, errors='ignore')

    pivot_index = list(df.columns)
    
    pivot_index.remove('PrefCounted')
    pivot_index.remove('CandidateName')

    # drop any entries where the preference counted is NaN - these are error rows?
        # how are we dealing with these types of votes in other files
        # By doing this, we are left with only Formal votes
    df.dropna(subset='PrefCounted', inplace=True)

    num_ballots_expected = len(df['BPNumber'].unique())

    df = df.pivot(index=pivot_index, columns="PrefCounted",values='CandidateName')

    # rename rank labels to match the format "rankn" for n = {1,...,C} where C is num_candidates
    ranks = df.columns
    labels = {}
    for rank in ranks:
        label = "rank"+str(int(rank))
        labels[rank] = label

    df = df.rename(columns=labels)

    # fill skipped votes with "skipped"
    df.fillna(value='skipped',inplace=True)

    # reset indices to be columns
    df = df.reset_index()
    df.columns.name = None

    print(f'writing to {outfilepath}')
    df.to_csv(outfilepath, index=False)

    return df, num_ballots_expected

def parser(state, infilepath, output_folder):
    print(f'reading {infilepath}')
    if state == 'Victoria':
        df = preprocess_victoria(infilepath)
    else:
        df = preprocess_nsw(infilepath)

    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    outfilepath = f'{output_folder}/{infilepath.split('.')[0].split('/')[-1]}.csv'

    print(f'parsing {infilepath}')
    df, num_ballots_expected = parse_to_csv(df, outfilepath)

    # verify number of ballots is consistent
    if num_ballots_expected == len(df):
        print(f'validated num_ballots for {infilepath}')
    else:
        sys.exit(f"number of ballots is inconsistent for file: {infilepath}")


