import pandas as pd

files = ['/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/borda_score/spoiler/scotland_results.csv',
         '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/mention_score/spoiler/scotland_results.csv',
         '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/spoiler/scotland_results.csv']

files = ['/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/borda_score/stability/scotland_results_top4.csv',
         '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/mention_score/stability/scotland_results_top4.csv',
         '/Users/karenxiao/MyPythonCode/ranked_choice_voting/rcv_proposal/analysis/mimic_single_party/methods/first_place_score/stability/scotland_results_top4.csv']

entries_to_remove = ['raw_data/scotland/processed_data/e-ayrshire22/Ward8-CumnockandNewCumnock_Ward8.csv',
 'raw_data/scotland/processed_data/e-ayrshire22/Ward9-DoonValley_Ward9.csv', 
 'raw_data/scotland/processed_data/e-ayrshire22/Ward5-KilmarnockSouth_Ward5.csv', 
 'raw_data/scotland/processed_data/e-ayrshire22/Ward4-KilmarnockEastandHurlford_Ward4.csv', 
 'raw_data/scotland/processed_data/e-ayrshire22/Ward7-Ballochmyle_Ward7.csv', 
 'raw_data/scotland/processed_data/e-ayrshire22/Ward6-IrvineValley_Ward6.csv', 
 'raw_data/scotland/processed_data/renfs22/for_Ward_9_Johnstone_North_Kilbarchan_Howwood_and_Lochwinnoch_copy.csv', 
 'raw_data/scotland/processed_data/aberdeenshire22/Ward1-BanffandDistrict_ward1.csv', 
 'raw_data/scotland/processed_data/e-renfs22/Ward5‐NewtonMearnsSouthandEaglesham_ward5_copy.csv', 
 'raw_data/scotland/processed_data/n-ayrshire22/Ward08-IrvineEast_Preference-Profile-Irvine-East_copy.csv']


for f in files:
    df = pd.read_csv(f)
    df = df[~df['file'].isin(entries_to_remove)]
    df.to_csv(f, index=False)
    
