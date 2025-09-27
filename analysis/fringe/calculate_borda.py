from main_methods import v_profile, Borda_AVG_Return_Full, Borda_OM_Return_Full, Borda_PM_Return_Full
import pandas as pd
import os
import json
import multiprocessing

# uses borda average scores but that can be easily changed
def calculate_borda(file):
    v = v_profile(file)
    df = pd.read_csv(file)
    columns = [c for c in df.columns if 'rank' in c]
    d_profile = df[columns]
    d_profile = d_profile.value_counts().reset_index(name='Count')

    scores_avg = Borda_AVG_Return_Full(v, tiebreak="first_place")
    # scores_om = Borda_OM_Return_Full(v, tiebreak="first_place")
    # scores_pm = Borda_PM_Return_Full(v, tiebreak="first_place")

    scores_avg = {k: float(v) for k, v in sorted(scores_avg.items(), key=lambda item: float(item[1]), reverse=True)}
    # scores_om = {k: float(v) for k, v in sorted(scores_om.items(), key=lambda item: float(item[1]), reverse=True)}
    # scores_pm = {k: float(v) for k, v in sorted(scores_pm.items(), key=lambda item: float(item[1]), reverse=True)}

    return scores_avg

# write results to a json file
def process_file(file_path, filename, processed_file, output_file):
    scores = calculate_borda(file_path)
    if os.path.exists(output_file):
        with open(output_file, "r") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                print("ERROR")
                data = {}
    else:
        data = {}
    data[filename] = scores
    
    with open(output_file, "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    with open(processed_file, "a") as ef:
        ef.write(f"{filename}, ")

def process(root_dir, processed_file, error_file, output_file):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                file_path = os.path.join(dirpath, filename)

                # ensure that if it runs for more than x seconds, kill the process
                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_file, args=(file_path,filename, processed_file, output_file))
                    p.start()
                    p.join(120)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(error_file, "a") as ef:
                            ef.write(f"{filename}, ")
                        p.terminate()
                        p.join()
                        print("\n")
                        
    
if __name__ == '__main__':
    processed_file = "" #txt file to keep track of what has been processed
    root_dir = "" # where the raw data is stored
    error_file = "" #txt file to keep track of failed files
    output_file = "" #output file location
    
    process(root_dir, processed_file, error_file, output_file)