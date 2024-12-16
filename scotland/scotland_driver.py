import os
from scotland_parser import parser

root_dir = '/Users/belle/Downloads/Scotland data, LEAP parties' # UPDATE TO WHERE BLT DATA IS STORED eg. /Users/belle/Downloads/Scotland data, LEAP parties
output_folder = '/Users/belle/Desktop/build/rcv_proposal/data' # UPDATE TO WHERE CSV DATA SHOULD BE SAVED eg. /Users/belle/Desktop/build/rcv_proposal/data

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
            full_path = os.path.join(dirpath, filename)
            parser(full_path, output_folder)
