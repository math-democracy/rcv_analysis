import sys
sys.path.append('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal')
import main_methods as mm
import votekit.elections as v
import pandas as pd
import multiprocessing
import csv
import os

num_cands_to_keep = 4

data_file = f'/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/america_results_top{num_cands_to_keep}.csv'
root_dir = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/raw_data/america/processed_data'

error_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/supporting_files/america_error.txt'
processed_file = '/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/stability/results/supporting_files/america_processed.txt'
all_data = []

processed = ["Eastpointe_11022021_CityCouncil.csv", 
"Eastpointe_11052019_CityCouncil.csv", 
"StLouisPark_11022021_CityCouncilWard3.csv", 
"StLouisPark_11022021_CityCouncilWard2.csv", 
"StLouisPark_11022021_CityCouncilWard1.csv", 
"StLouisPark_11022021_CityCouncilWard4.csv", 
"Alaska_11082022_HouseDistrict23.csv", 
"Alaska_11082022_HouseDistrict37.csv", 
"Alaska_11082022_HouseDistrict36.csv", 
"Alaska_11082022_HouseDistrict22.csv", 
"Alaska_08162022_HouseofRepresentativesSpecial.csv", 
"Alaska_11082022_HouseDistrict34.csv", 
"Alaska_11082022_HouseDistrict20.csv", 
"Alaska_11082022_HouseDistrict21.csv", 
"Alaska_11082022_HouseDistrict35.csv", 
"Alaska_11082022_HouseDistrict19.csv", 
"Alaska_11082022_HouseDistrict31.csv", 
"Alaska_11082022_HouseDistrict25.csv", 
"Alaska_11082022_HouseDistrict24.csv", 
"Alaska_11082022_HouseDistrict30.csv", 
"Alaska_11082022_HouseDistrict18.csv", 
"Alaska_11082022_HouseDistrict26.csv", 
"Alaska_11082022_HouseDistrict32.csv", 
"Alaska_11052024_StateHouseD40.csv", 
"Alaska_11082022_HouseDistrict33.csv", 
"Alaska_11082022_HouseDistrict27.csv", 
"Alaska_11082022_HouseDistrict40.csv", 
"Alaska_11052024_StateHouseD33.csv", 
"Alaska_11052024_StateHouseD27.csv", 
"Alaska_11082022_HouseDistrict1.csv", 
"Alaska_11052024_StateHouseD26.csv", 
"Alaska_11052024_StateHouseD32.csv", 
"Alaska_11052024_StateHouseD1.csv", 
"Alaska_11082022_SenateDistrictA.csv", 
"Alaska_11052024_StateSenateJ.csv", 
"Alaska_11052024_StateSenateH.csv", 
"Alaska_11082022_SenateDistrictC.csv", 
"Alaska_11052024_StateHouseD3.csv", 
"Alaska_11052024_StateHouseD24.csv", 
"Alaska_11052024_StateHouseD30.csv", 
"Alaska_11052024_StateHouseD18.csv", 
"Alaska_11082022_HouseDistrict2.csv", 
"Alaska_11082022_HouseDistrict3.csv", 
"Alaska_11052024_StateHouseD19.csv", 
"Alaska_11052024_StateHouseD31.csv", 
"Alaska_11052024_StateHouseD25.csv", 
"Alaska_11052024_StateHouseD2.csv", 
"Alaska_11082022_SenateDistrictB.csv", 
"Alaska_11082022_GovernorLieutenantGovernor.csv", 
"Alaska_11082022_SenateDistrictQ.csv", 
"Alaska_11082022_SenateDistrictF.csv", 
"Alaska_11052024_StateHouseD6.csv", 
"Alaska_11052024_StateHouseD21.csv", 
"Alaska_11052024_StateHouseD35.csv", 
"Alaska_11082022_HouseDistrict7.csv", 
"Alaska_11082022_HouseDistrict6.csv", 
"Alaska_11052024_StateHouseD34.csv", 
"Alaska_11052024_StateHouseD20.csv", 
"Alaska_11052024_StateHouseD7.csv", 
"Alaska_11082022_SenateDistrictG.csv", 
"Alaska_11082022_SenateDistrictP.csv", 
"Alaska_11052024_StateSenateL.csv", 
"Alaska_11052024_StateSenateN.csv", 
"Alaska_11082022_SenateDistrictR.csv", 
"Alaska_11082022_SenateDistrictE.csv", 
"Alaska_11052024_StateHouseD5.csv", 
"Alaska_11052024_StateHouseD36.csv", 
"Alaska_11052024_StateHouseD22.csv", 
"Alaska_11082022_HouseDistrict4.csv", 
"Alaska_11082022_HouseDistrict5.csv", 
"Alaska_11052024_StateHouseD23.csv", 
"Alaska_11052024_StateHouseD37.csv", 
"Alaska_11052024_StateHouseD4.csv", 
"Alaska_11082022_SenateDistrictD.csv", 
"Alaska_11082022_SenateDistrictS.csv", 
"Alaska_11052024_StateSenateB.csv", 
"Alaska_11082022_SenateDistrictI.csv", 
"Alaska_11052024_StateHouseD9.csv", 
"Alaska_11052024_StateHouseD12.csv", 
"Alaska_11082022_HouseDistrict8.csv", 
"Alaska_11082022_HouseDistrict9.csv", 
"Alaska_11052024_StateHouseD13.csv", 
"Alaska_11052024_StateHouseD8.csv", 
"Alaska_11082022_SenateDistrictH.csv", 
"Alaska_11082022_USRepresentative.csv", 
"Alaska_11052024_StateSenateT.csv", 
"Alaska_11082022_SenateDistrictJ.csv", 
"Alaska_11052024_StateHouseD11.csv", 
"Alaska_11052024_StateHouseD39.csv", 
"Alaska_11052024_StateHouseD38.csv", 
"Alaska_11052024_StateHouseD10.csv", 
"Alaska_11082022_SenateDistrictK.csv", 
"Alaska_11052024_StateSenateD.csv", 
"Alaska_11082022_SenateDistrictO.csv", 
"Alaska_11052024_StateHouseD28.csv", 
"Alaska_11052024_StateHouseD14.csv", 
"Alaska_11052024_StateHouseD15.csv", 
"Alaska_11052024_StateHouseD29.csv", 
"Alaska_11082022_SenateDistrictN.csv", 
"Alaska_11052024_StateSenateR.csv", 
"Alaska_11052024_StateSenateP.csv", 
"Alaska_11082022_SenateDistrictL.csv", 
"Alaska_11082022_USSenator.csv", 
"Alaska_11052024_StateHouseD17.csv", 
"Alaska_11052024_StateHouseD16.csv", 
"Alaska_11082022_SenateDistrictM.csv", 
"Alaska_11052024_StateSenateF.csv", 
"Alaska_11052024_President.csv", 
"Alaska_11082022_HouseDistrict16.csv", 
"Alaska_11082022_HouseDistrict17.csv", 
"Alaska_11082022_HouseDistrict15.csv", 
"Alaska_11082022_HouseDistrict29.csv", 
"Alaska_11082022_HouseDistrict28.csv", 
"Alaska_11082022_HouseDistrict14.csv", 
"Alaska_11082022_HouseDistrict38.csv", 
"Alaska_11082022_HouseDistrict10.csv", 
"Alaska_11082022_HouseDistrict11.csv", 
"Alaska_11082022_HouseDistrict39.csv", 
"Alaska_11052024_US_House.csv", 
"Alaska_11082022_HouseDistrict13.csv", 
"Alaska_11082022_HouseDistrict12.csv", 
"Minneapolis_11072023_CityCouncilWard12.csv", 
"Minneapolis_11072017_BoardofEstimateandTaxation.csv", 
"Minneapolis_11072017_ParkBoardAtLarge.csv", 
"Minneapolis_11072017_Ward6CityCouncil.csv", 
"Minneapolis_11072017_Mayor.csv", 
"Minneapolis_11062009_PRBoardDistrict6.csv", 
"Minneapolis_11062009_Ward10CityCouncil.csv", 
"Minneapolis_11072023_CityCouncilWard13.csv", 
"Minneapolis_11022021_BoardofEstimateandTaxationAtLarge.csv", 
"Minneapolis_11072017_Ward1CityCouncil.csv", 
"Minneapolis_11062009_PRBoardDistrict5.csv", 
"Minneapolis_11062009_PRBoardDistrict4.csv", 
"Minneapolis_11072017_Ward9CityCouncil.csv", 
"Minneapolis_11072023_CityCouncilWard10.csv", 
"Minneapolis_11062009_BoardofEstimateandTaxation.csv", 
"Minneapolis_11072017_Ward8CityCouncil.csv", 
"Minneapolis_11022021_Mayor.csv", 
"Minneapolis_11062009_PRBoardDistrict1.csv", 
"Minneapolis_11022021_ParkBoardAtLarge.csv", 
"Minneapolis_11062009_Ward11CityCouncil.csv", 
"Minneapolis_11052013_PRBoardDistrict6.csv", 
"Minneapolis_11062009_PRBoardDistrict3.csv", 
"Minneapolis_11062009_PRBoardDistrict2.csv", 
"Minneapolis_11072017_Ward7CityCouncil.csv", 
"Minneapolis_11022021_CityCouncilWard4.csv", 
"Minneapolis_11062009_Ward13CityCouncil.csv", 
"Minneapolis_11072017_Ward5CityCouncil.csv", 
"Minneapolis_11022021_CityCouncilWard10.csv", 
"Minneapolis_11022021_CityCouncilWard12.csv", 
"Minneapolis_11022021_CityCouncilWard7.csv", 
"Minneapolis_11022021_CityCouncilWard6.csv", 
"Minneapolis_11072017_Ward2CityCouncil.csv", 
"Minneapolis_11022021_CityCouncilWard13.csv", 
"Minneapolis_11072017_Ward3CityCouncil.csv", 
"Minneapolis_11022021_CityCouncilWard2.csv", 
"Minneapolis_11022021_CityCouncilWard3.csv", 
"Minneapolis_11072017_Ward4CityCouncil.csv", 
"Minneapolis_11022021_CityCouncilWard1.csv", 
"Minneapolis_11052013_Mayor.csv", 
"Minneapolis_11072023_CityCouncilWard8.csv", 
"Minneapolis_11062009_Ward12CityCouncil.csv", 
"Minneapolis_11072023_CityCouncilWard5.csv", 
"Minneapolis_11072017_PRBoardDistrict3.csv", 
"Minneapolis_11072017_PRBoardDistrict2.csv", 
"Minneapolis_08112020_Ward6CityCouncilSpecialElection.csv", 
"Minneapolis_11072023_CityCouncilWard4.csv", 
"Minneapolis_11062009_Ward7CityCouncil.csv", 
"Minneapolis_11052013_ParkRecBoardAtLarge.csv", 
"Minneapolis_11072023_CityCouncilWard6.csv", 
"Minneapolis_11062009_Ward8CityCouncil.csv", 
"Minneapolis_11062009_Mayor.csv", 
"Minneapolis_11072017_Ward12CityCouncil.csv", 
"Minneapolis_11052013_Ward9CityCouncil.csv", 
"Minneapolis_11072017_PRBoardDistrict1.csv", 
"Minneapolis_11072023_CityCouncilWard7.csv", 
"Minneapolis_11072017_PRBoardDistrict5.csv", 
"Minneapolis_11062009_Ward1CityCouncil.csv", 
"Minneapolis_11062009_Ward9CityCouncil.csv", 
"Minneapolis_11072017_PRBoardDistrict4.csv", 
"Minneapolis_11062009_MinneapolisParkRecBoard.csv", 
"Minneapolis_11072017_Ward13CityCouncil.csv", 
"Minneapolis_11022021_CityCouncilWard8.csv", 
"Minneapolis_11062009_Ward6CityCouncil.csv", 
"Minneapolis_11072017_PRBoardDistrict6.csv", 
"Minneapolis_11022021_CityCouncilWard9.csv", 
"Minneapolis_11052013_Ward13CityCouncil.csv", 
"Minneapolis_11062009_Ward4CityCouncil.csv", 
"Minneapolis_11052013_Ward5CityCouncil.csv", 
"Minneapolis_11022021_ParkBoardDistrict3.csv", 
"Minneapolis_11062009_Ward3CityCouncil.csv", 
"Minneapolis_11022021_ParkBoardDistrict1.csv", 
"Minneapolis 2013-board of estimation and taxation cvr.csv", 
"Minneapolis_11072017_Ward11CityCouncil.csv", 
"Minneapolis_11072017_Ward10CityCouncil.csv", 
"Minneapolis_11022021_ParkBoardDistrict4.csv", 
"Minneapolis_11062009_Ward2CityCouncil.csv", 
"Minneapolis_11022021_ParkBoardDistrict5.csv", 
"Minneapolis_11062009_Ward5CityCouncil.csv", 
"Minneapolis_11022021_ParkBoardDistrict6.csv", 
"PierceCounty_11042008_CountyExecutiveMember.csv", 
"PierceCounty_11032009_CountyAuditor.csv", 
"PierceCounty_11042008_CountyAssessorTreasurer.csv", 
"PierceCounty_11042008_CountyCouncilDistrict2.csv", 
]
error_d = ["Portland_D3_2024.csv", "Portland_D2_2024.csv", "PortlandOR_110524_Mayor.csv", "Portland_D4_2024.csv", "SanFrancisco_11052024_Mayor.csv", "NewYorkCity_06222021_DEMMayorCitywide.csv"]
         
def file_less_than_3mb(file_path):
    try:
        file_size = os.path.getsize(file_path)  # Get file size in bytes
        return file_size < 5 * 1024 * 1024  # 1 MB in bytes
    except FileNotFoundError:
        print("File not found.")
        return False
    
def get_cands_to_keep(profile, num_cands, num_to_keep):
    # get top4 plurality winners
        # if there are less than 5 candidates, then top4 and top5 are both the whole candidate list
    if num_cands > num_to_keep:
        cands_to_keep = v.Plurality(profile=profile, m=num_to_keep, tiebreak='random').election_states[-1].elected
        cands_to_keep = [list(w)[0] for w in cands_to_keep]
    else:
        cands_to_keep = profile.candidates

    return cands_to_keep
    
def run_voting_methods(full_path):
    df = pd.read_csv(full_path)

    # create david-readable profile
    columns = [c for c in df.columns if 'rank' in c]
    d_profile = df[columns]
    d_profile = d_profile.value_counts().reset_index(name='Count')
       
    # create votekit profile
    v =  mm.v_profile(full_path)

    # get total candidate information
    candidates = list(v.candidates)
    num_cands = len([x for x in candidates if x != 'skipped'])

    data = {'file': full_path.replace('/Users/xiaokaren/MyPythonCode/ranked_choice_voting/rcv_proposal/', '')}
    grouped_data = []

    data['numCands'] = num_cands

    # get result of election considering all candidates
    data['plurality'] = list(mm.Plurality(prof=v,tiebreak='random'))
    data['IRV'] = list(mm.IRV(prof=v,tiebreak='random'))
    data['top-two'] = list(mm.TopTwo(prof=v,tiebreak='random'))
    data['borda-pm'] = list(mm.Borda_PM(prof=v, tiebreak='random'))
    data['borda-om'] = list(mm.Borda_OM(prof=v, tiebreak='random'))
    data['borda-avg'] = list(mm.Borda_AVG(prof=v, tiebreak='random'))
    data['top-3-truncation'] = mm.Top3Truncation(prof=v,tiebreak='random')
    # sometimes top-3-trunc returns a list not a set
    if isinstance(data['top-3-truncation'], str):
        data['top-3-truncation'] = [data['top-3-truncation']]
    else:
        data['top-3-truncation'] = list(data['top-3-truncation'])
    data['condorcet'] = list(mm.Condorcet(prof=v,tiebreak='random'))
    data['minimax'] = list(mm.Minimax(prof=v,tiebreak='random'))
    data['smith_plurality'] = list(mm.Smith_Plurality(prof=v,tiebreak='random'))
    data['smith_irv'] = list(mm.Smith_IRV(prof=v,tiebreak='random'))
    data['smith-minimax'] = list(mm.Smith_Minimax(prof=v,tiebreak='random'))
    data['ranked-pairs'] = list(mm.Ranked_Pairs(prof=v,tiebreak='random'))
    data['bucklin'] = list(mm.Bucklin(prof=v, tiebreak='random'))
    data['approval'] = list(mm.Ranked_Pairs(prof=v,tiebreak='random'))

    # get top 4 based on plurality score
    cands_to_keep = get_cands_to_keep(v, len(v.candidates), num_cands_to_keep)
    
    print(cands_to_keep)

    data[f'top{num_cands_to_keep}_plurality'] = list(mm.Plurality(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_IRV'] = list(mm.IRV(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_top-two'] = list(mm.TopTwo(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_borda-pm'] = list(mm.Borda_PM(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_borda-om'] = list(mm.Borda_OM(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_borda-avg'] = list(mm.Borda_AVG(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_top-3-truncation'] = mm.Top3Truncation(prof=v, cands_to_keep=cands_to_keep,tiebreak='random')
        # sometimes top-3-trunc returns a list not a set
    if isinstance(data[f'top{num_cands_to_keep}_top-3-truncation'], str):
        data[f'top{num_cands_to_keep}_top-3-truncation'] = [data[f'top{num_cands_to_keep}_top-3-truncation']]
    else:
        data[f'top{num_cands_to_keep}_top-3-truncation'] = list(data[f'top{num_cands_to_keep}_top-3-truncation'])
    data[f'top{num_cands_to_keep}_condorcet'] = list(mm.Condorcet(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_minimax'] = list(mm.Minimax(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_smith_plurality'] = list(mm.Smith_Plurality(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_smith_irv'] = list(mm.Smith_IRV(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_smith-minimax'] = list(mm.Smith_Minimax(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_ranked-pairs'] = list(mm.Ranked_Pairs(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_bucklin'] = list(mm.Bucklin(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    data[f'top{num_cands_to_keep}_approval'] = list(mm.Ranked_Pairs(prof=v, cands_to_keep=cands_to_keep, tiebreak='random'))
    
    # column_order = ['file','plurality',
    #                 f'top{num_cands_to_keep}_plurality','IRV',f'top{num_cands_to_keep}_IRV',
    #                 'top-two',f'top{num_cands_to_keep}_top-two',
    #                 'borda-pm',f'top{num_cands_to_keep}_borda-pm',
    #                 'top-3-truncation',f'top{num_cands_to_keep}_top-3-truncation',
    #                 'condorcet',f'top{num_cands_to_keep}_condorcet',
    #                 'minimax',f'top{num_cands_to_keep}_minimax',
    #                 'smith',f'top{num_cands_to_keep}_smith',
    #                 'smith-minimax',f'top{num_cands_to_keep}_smith-minimax',
    #                 'ranked-pairs',f'top{num_cands_to_keep}_ranked-pairs']
    # grouped_data = {k:grouped_data[k] for k in column_order}
    grouped_data.append(data)
    
    return grouped_data

def process_file(full_path, filename):
    print("RUNNING ", filename, "\n")
    all_data = run_voting_methods(full_path)
    print(all_data, "\n")

    if all_data:
        with open(data_file, mode='a', newline='') as file:
            writer = csv.writer(file)

            # Write the header if the file is empty
            if os.stat(data_file).st_size == 0:
                header = all_data[0].keys()
                writer.writerow(header)

            # Write each row of data
            for data in all_data:
                keys = all_data[0].keys()
                row = [data.get(key, '') for key in keys]
                writer.writerow(row)

    with open(processed_file, "a") as ef:
        ef.write(f"\"{filename}\", \n")

def main():
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            print(filename)
            if filename not in processed and filename not in error_d and (filename.endswith('.blt') or filename.endswith('.csv') or filename.endswith('.txt')):
                full_path = os.path.join(dirpath, filename)
                if __name__ == '__main__':
                    p = multiprocessing.Process(target=process_file, args=(full_path,filename))
                    p.start()
                    p.join(200)

                    if p.is_alive():
                        print("running... let's kill it...")
                        with open(error_file, "a") as ef:
                            ef.write(f"\"{filename}\", ")
                        p.terminate()
                        p.join()
                        print("\n")

if __name__ == '__main__':
    main()