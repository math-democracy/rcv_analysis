import pandas as pd
import numpy as np
import csv
import os
import re
import json

############################
#      helper methods      #
############################

root_dir = '/Users/belle/Desktop/build/rcv_proposal/american' # where the data is
country = "america" # country of the dataset

data_file = '/Users/belle/Desktop/build/rcv_proposal/metadata_test2.csv' # where you want to put the summary of each election
metadata_file = '/Users/belle/Desktop/build/rcv_proposal/metadata_test2.json' # where you want to put the overall statistics

def process_files():
    data = read_folders(root_dir)
    write_to_data_file(data)

def generate_data():
    df = pd.read_csv(data_file)
    get_insights(df)
    get_summary_insights(df)


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

    # num of winners per election
    winners_per_election = df.groupby(['country', 'num_seats']).size().reset_index(name='count').groupby('country').apply(lambda x: x[['num_seats', 'count']].to_dict(orient='records')).to_dict()

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

    truncated = df['truncated'].sum()
    print(truncated)

#################################
# helper methods: process files #
#################################
    
def read_folders(root_dir):
    data = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                full_path = os.path.join(dirpath, filename)
                data.append(get_file_data(filename, full_path))

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
        "truncated": 0
    }
   
    if filename.endswith(".csv"):
        with open(full_path, 'r') as file:
            
            reader = csv.DictReader(file)
            rows = list(reader) 
            file_data["num_voters"] = len(rows)
            no_skipped = sum(1 for row in rows if not any("skipped" in cell.strip().lower() for cell in row.values()))
            one_skipped = sum(1 for row in rows if sum("skipped" in cell.strip().lower() for cell in row.values()) == 1)
            two_skipped = sum(1 for row in rows if sum("skipped" in cell.strip().lower() for cell in row.values()) == 2)
            three_skipped = sum(1 for row in rows if sum("skipped" in cell.strip().lower() for cell in row.values()) == 3)
            num_cands = 0
            num_seats = 0

            if len(rows) >= 1: 
                if country == "america": 
                    num_cands = rows[0].get("Num cands", None) 
                    num_seats = rows[0].get("Num seats", None) 
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
                    num_cands = rows[0].get("Num Cands", None) 
                    num_seats = rows[0].get("Num Seats", None) 
                if country == "scotland":
                    num_cands = rows[0].get("numCands", None) 
                    num_seats = rows[0].get("numSeats", None) 
                if country == "australia":
                    header = reader.fieldnames
                    rank_numbers = [
                        int(match.group(1))
                        for column in header
                        if (match := re.search(r"rank(\d+)", column))
                    ]
                    largest_rank_number = max(rank_numbers, default=0)
                    num_cands = largest_rank_number
                    num_seats = 0

                file_data["num_cands"] = num_cands
                file_data["num_seats"] = num_seats
                file_data["no_skipped"] = no_skipped
                file_data["one_skipped"] = one_skipped
                file_data["two_skipped"] = two_skipped
                file_data["three_skipped"] = three_skipped
        
        # test for truncation? no results.
        # df = pd.read_csv(full_path)   
        # skipped_columns = [col for col in df.columns if (df[col] == 'skipped').all()]
        # length = len(skipped_columns)
        # if length != 0:
        #     print(full_path + ": " + str(length))
        
    return file_data

def write_to_data_file(data):
    keys = data[0].keys()

    with open(data_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(keys)
        for d in data:
            row = [d.get(key, '') for key in keys]
            writer.writerow(row)

generate_data()