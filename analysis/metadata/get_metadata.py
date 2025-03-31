import pandas as pd
import numpy as np
import csv
import os
import re
import json

############################
#      helper methods      #
############################

root_dir = '/Users/belle/Desktop/build/rcv/raw_data/america/processed_data' # where the data is
country = "america" # country of the dataset

data_file = './metadata_america.csv' # where you want to put the summary of each election
metadata_file = './metadata_america.json' # where you want to put the overall statistics

def process_files():
    data = read_folders(root_dir)
    # write_to_data_file(data)

def generate_data():
    df = pd.read_csv(data_file)
    get_insights(df)
    # get_summary_insights(df)


#################################
# helper methods: generate data #
#################################
def read_file(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        array = [row for row in reader]  # Convert the CSV rows to a list of lists
    return array

def get_insights(df):
    # elections per country
    elections_per_country = df['country'].value_counts().to_dict()
    elections_per_country["total"] = df.shape[0]

    # one skips vs two skips vs three skips
    
    # Calculate percentages
    df["no_skipped_percent"] = (df["no_skipped"] / df["num_voters"]) * 100
    df["one_skipped_percent"] = (df["one_skipped"] / df["num_voters"]) * 100
    df["two_skipped_percent"] = (df["two_skipped"] / df["num_voters"]) * 100
    df["three_skipped_percent"] = (df["three_skipped"] / df["num_voters"]) * 100
    
    # Generate descriptive statistics for percentage skipped categories
    percentage_columns = ["no_skipped_percent", "one_skipped_percent", "two_skipped_percent", "three_skipped_percent"]
    stats = df[percentage_columns].describe()

    # num of winners per election
    winners_per_election = df.groupby(['country', 'num_seats']).size().reset_index(name='count').groupby('country').apply(lambda x: x[['num_seats', 'count']].to_dict(orient='records')).to_dict()

    # num of candidates per election
    candidates_per_election = df.groupby(['country', 'num_cands']).size().reset_index(name='count').groupby('country').apply(lambda x: x[['num_cands', 'count']].to_dict(orient='records')).to_dict()
    aggregate_candidates = df.groupby('country')['num_cands'].describe().to_dict(orient='index')

    # descriptive statistics about voters per elections in each country
    aggregate_voters = df.groupby('country')['num_voters'].describe().to_dict(orient='index')

    # num of votes per election
    # create buckets of 1000 voters and leave only the upper bound
    df['voter_category'] = pd.cut(df['num_voters'], bins=range(0, df['num_voters'].max() + 1000, 1000), right=False)
    df['voter_category'] = df['voter_category'].apply(lambda x: x.right)
    
    # group the data together
    votes_per_election = df.groupby(['country', 'voter_category']).size().reset_index(name='voter_category_count')
    votes_per_election = votes_per_election[votes_per_election['voter_category_count'] > 0].groupby('country').apply(lambda x: x[['voter_category', 'voter_category_count']].to_dict(orient='records')).to_dict()

    # export data
    all_insights = {
        "elections_per_country": elections_per_country, 
        "skips": stats.to_dict(),
        "aggregate_candidates": aggregate_candidates,
        "candidates_per_election": candidates_per_election,
        "winners_per_election": winners_per_election, 
        "aggregate_voters": aggregate_voters,
        "votes_per_election": votes_per_election
    }
    with open(metadata_file, 'w') as json_file:
        json.dump(all_insights, json_file, indent=4)

def get_summary_insights(df):
    top_voters = df.sort_values(by='num_voters', ascending=False).head(30)
    print(top_voters)

    # df['one_skipped_p'] = df['one_skipped'] / df['num_voters']
    # skipped = df[['file_name', 'num_voters', 'one_skipped', 'one_skipped_p']]
    # top_skipped = skipped.sort_values(by='one_skipped_p', ascending=False).head(30)
    # print(top_skipped)

    # bottom_skipped = skipped.sort_values(by='one_skipped_p', ascending=True).head(30)
    # print(bottom_skipped)

    # truncated = df['truncated'].sum()
    # print(truncated)

#################################
# helper methods: process files #
#################################
    
def read_folders(root_dir):
    data = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                full_path = os.path.join(dirpath, filename)
                get_file_data(filename, full_path)

    return data

def get_file_data(filename, full_path):
    file_data = {
        "country": country,
        "file_name": filename,
        "num_voters": 0,
        "num_cands": 0,
        "num_seats": 0,
        "no_skipped": 0,
        "one_skipped": 0,
        "two_skipped": 0,
        "three_skipped": 0,
        "write_in": 0,
        "truncated": 0
    }
   
    if filename.endswith(".csv"):
        with open(full_path, 'r') as file:
            
            reader = csv.DictReader(file)
            rows = list(reader) 
            file_data["num_voters"] = len(rows)
            no_skipped = one_skipped = two_skipped = three_skipped = 0
            unique_write_ins = set()

            for row in rows:
                skipped_count = 0 
                for cell in row.values():
                    cell_value = cell.strip().lower()
                    if "skipped" in cell_value:
                        skipped_count += 1
                    if "UWI" in cell_value or "uwi" in cell_value or "Write-in" in cell_value or "Write in" in cell_value or "Write-In" in cell_value or "writein" in cell_value or "Uncertified Write In" in cell_value:
                        unique_write_ins.add(cell_value)
                
                if skipped_count == 0:
                    no_skipped += 1
                elif skipped_count == 1:
                    one_skipped += 1
                elif skipped_count == 2:
                    two_skipped += 1
                elif skipped_count == 3:
                    three_skipped += 1

            unique_write_in = len(unique_write_ins)
            
            num_cands = 0
            num_seats = 0
            largest_rank_number = 0

            if len(rows) >= 1: 
                if country == "america": 
                    num_cands = rows[0].get("numCands", None) 
                    num_seats = rows[0].get("numSeats", None) 
                    header = reader.fieldnames
                    rank_numbers = [
                        int(match.group(1))
                        for column in header
                        if (match := re.search(r"rank(\d+)", column))
                    ]
                    largest_rank_number = max(rank_numbers, default=0)

                    if largest_rank_number + 1 < int(num_cands):
                        file_data['truncated'] = 1

                if country == "civs":
                    num_cands = rows[0].get("numCands", None) 
                    num_seats = rows[0].get("numSeats", None) 
                if country == "scotland":
                    num_cands = rows[0].get("numCands", None) 
                    num_seats = rows[0].get("numSeats", None) 
                if country == "australia":
                    num_cands = rows[0].get("numCands", None) 
                    num_seats = rows[0].get("numSeats", None) 
                    header = reader.fieldnames
                    rank_numbers = [
                        int(match.group(1))
                        for column in header
                        if (match := re.search(r"rank(\d+)", column))
                    ]
                    largest_rank_number = max(rank_numbers, default=0)

                    if largest_rank_number + 1 < int(num_cands):
                        file_data['truncated'] = 1

                file_data["num_cands"] = num_cands
                file_data["num_seats"] = num_seats
                file_data["no_skipped"] = no_skipped
                file_data["one_skipped"] = one_skipped
                file_data["two_skipped"] = two_skipped
                file_data["three_skipped"] = three_skipped
                file_data["write_in"] = unique_write_in
        
       # test for truncation? no results.
        # df = pd.read_csv(full_path)   
        # skipped_columns = [col for col in df.columns if (df[col] == 'skipped').all()]
        # length = len(skipped_columns)
        # if largest_rank_number <= int(num_cands) and length != 0:
        #     print(full_path + ": " + str(length))
    write_to_data_file(file_data)
    return file_data

def write_to_data_file(data):
    keys = data.keys()

    with open(data_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if os.stat(data_file).st_size == 0:
             writer.writerow(keys)
        row = [data.get(key, '') for key in keys]
        writer.writerow(row)

generate_data()