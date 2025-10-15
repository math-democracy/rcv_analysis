import main_methods as mm
import os
import json
import multiprocessing

folder_path = '' # raw data folder
country = ''

def process_csv(full_path, filename):
    v_profile =  mm.v_profile(full_path)
    condorcet_loser = mm.Condorcet_Loser(prof=v_profile)
    candidates = list(v_profile.candidates)
    cands = [cand for cand in candidates if cand != 'skipped' and cand != "writein" and cand != "Write-in" and cand != "Write-In 1" and cand != "Write-In 2" and cand != "Write-In 6" and cand != "Write-In 3"]
    if (len(cands) <2):
        condorcet_loser = None

    if condorcet_loser != None:
        condorcet_loser = list(condorcet_loser)
    
    with open('australia.json', 'r') as file:
        data = json.load(file)

    data[filename] = condorcet_loser

    with open('australia.json', 'w') as file:
        json.dump(data, file, indent=2)

def main():
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt'):
                print(filename)
                full_path = os.path.join(dirpath, filename)

                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_csv, args=(full_path,filename))
                    p.start()
                    p.join(20)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(f'./error_{country}.txt', "a") as ef:
                            ef.write(f"{filename}, ")
                        p.terminate()
                        p.join()
                        print("\n")

if __name__ == '__main__':
    main()