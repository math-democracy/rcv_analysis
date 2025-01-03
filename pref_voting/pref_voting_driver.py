from pref_voting_methods import create_profile, run_voting_methods
import os
import csv
import time
import multiprocessing

data_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/american_results.csv'
root_dir = '/Users/belle/Desktop/build/rcv_proposal/american'

error_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/supporting_files/american_error.txt'
processed_file = '/Users/belle/Desktop/build/rcv_proposal/pref_voting/processed_results/supporting_files/american_processed.txt'
all_data = []

def file_less_than_3mb(file_path):
    try:
        file_size = os.path.getsize(file_path)  # Get file size in bytes
        return file_size < 5 * 1024 * 1024  # 1 MB in bytes
    except FileNotFoundError:
        print("File not found.")
        return False

def process_file(full_path, filename):
    print("RUNNING ", filename, "\n")
    profile, file_path, candidates_with_indices = create_profile(full_path)
    data = run_voting_methods(profile, file_path, candidates_with_indices)
    all_data.append(data)
    print(data, "\n")

    with open(data_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        keys = all_data[0].keys()
        row = [data.get(key, '') for key in keys]
        writer.writerow(row)

    with open(processed_file, "a") as ef:
        ef.write(f"{filename}, ")

def read_processed():
    
    processed_files = []

    with open(error_file, 'r') as file:
        content = file.read()
        processed_files += [file.strip() for file in content.split(',')]

    with open(processed_file, 'r') as file:
        content = file.read()
        processed_files += [file.strip() for file in content.split(',')]

    return processed_files

# processed_files = read_processed()
# print(processed_files)

def main():
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            print(filename)
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                # if filename not in processed_files:
                    # print("not processed")
                full_path = os.path.join(dirpath, filename)
                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_file, args=(full_path,filename))
                    p.start()
                    p.join(10)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(error_file, "a") as ef:
                            ef.write(f"{filename}, ")
                        p.terminate()
                        p.join()
                        print("\n")

if __name__ == '__main__':
    main()
            