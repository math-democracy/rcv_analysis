import os
from parse import parser

root_dir = '' # UPDATE TO WHERE BLT DATA IS STORED eg. /Users/belle/Desktop/build/rcv/shetland22
output_folder = '' # UPDATE TO WHERE CSV DATA SHOULD BE SAVED eg. /Users/belle/Desktop/build/rcv

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith('.blt'):
            full_path = os.path.join(dirpath, filename)
            parser(full_path, output_folder)
