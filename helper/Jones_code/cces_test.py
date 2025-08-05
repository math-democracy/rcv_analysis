import random
import pandas as pd
import math
import operator
import numpy as np
import copy
import csv
import os
import statistics
import warnings
import sys
warnings.simplefilter(action='ignore', category=FutureWarning)
import multiprocessing
import time
import traceback
import json
import pickle

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        # if isinstance(obj, np.floating):
        #     return float(obj)
        # if isinstance(obj, np.ndarray):
        #     return obj.tolist()
        return super(NpEncoder, self).default(obj)



from election_class import *
from ballot_modifications_class import *
from anomaly_search_class import *


#####TODO
## 




###############################################################################
###############################################################################
##### parameters
## github repo version
data_path = './CCES_data'
## HPC version
# data_path = '/home/aschult2/Desktop/CCES_data'
frac = 1
mp_pool_size = 6
###############################################################################
###############################################################################





####################################################
##### Functions to run searches
####################################################

def get_cces(path, model):
    cand_names=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    num_cands = int(path[path.find('cands')-1])
    
    print('reading parquet')

    df = pd.read_parquet(path, engine='pyarrow')

    print('getting model df')

    model_to_select=model
    #Now filter the dataframe by the model you want, and unpickle the preference profiles
    model_df = df[df['model'] == model_to_select].copy()
    model_df['profile'] = model_df['profile'].apply(lambda x: pickle.loads(x) if isinstance(x, bytes) else x)
    model_df.reset_index(inplace=True)

    print('getting profiles')
    # print(len(model_df))    

    lxn_list = []
    # for i in range(len(model_df)):
    for i in range(10000):
    # for i in range(3755, 3775):
        lxn_df = model_df.at[i, 'profile']
        ballot_list = []
        count_list = []
        for j in range(len(lxn_df)):
            count_list.append(lxn_df.at[j, 'Count'])
            ballot = ''
            for k in range(1,6):
                try:
                    if lxn_df.at[j, 'rank'+str(k)]=='skipped':
                        # print('break1')
                        # print(k)
                        break
                    else:
                        ballot += cand_names[int(lxn_df.at[j, 'rank'+str(k)])]
                except:
                    # print('break2')
                    # print(k)
                    break
            ballot_list.append(ballot)

        df_dict = {'ballot': ballot_list, 'Count': count_list}
        profile = pd.DataFrame(df_dict)

        lxn_list.append([i, profile, num_cands])
        
    return lxn_list


    


        


if __name__=='__main__':

    destination_base = './CCES_anom_strat_results'
    
    if not os.path.exists(destination_base):
        os.makedirs(destination_base)
        
    models = ['(True, True, False, False)',
    '(False, True, False, False)',
    '(True, False, False, False)',
    '(True, True, True, False)',
    '(True, True, False, True)',
    '(False, False, True, False)',
    '(False, False, True, True)']
    
    models = ['(False, False, True, False)']
    
    # for cces_file in os.listdir(data_path):
    for cces_file in ['Alabama_distribution1_3cands.parquet']:
        
        if 'Alabama' not in cces_file:
            continue
        
        # print(cces_file)
        for model in models:
            model_string = ''
            for char in model:
                if char in ['T','F']:
                    model_string += char
            # print(model_string)
        
            full_model_name = cces_file[:cces_file.find('.parquet')]+'_'+model_string
            # print(full_model_name)
            
            # if not os.path.exists(destination_base+'/anomalies/'+full_model_name):
            #     os.makedirs(destination_base+'/anomalies/'+full_model_name)
                
            
            lxn_list = get_cces(data_path+'/'+cces_file, model)
            
            anom_list = []
            for i, lxn in enumerate(lxn_list):
                sys.stdout.write('\r')
                sys.stdout.write('\r')
                sys.stdout.write(f'Election {i+1}'+'                      ')
                sys.stdout.flush()
                data = frac_upMonoIRV(lxn[1], 3, 1)
                if data:
                    anom_list.append(i)
                    
            
            # for i, lxn in enumerate(lxn_list):
            #     if i%1000 == 0:
            #         print(i)
            #     data = frac_downMonoIRV(lxn[1], 3, 1)
            #     if data:
            #         p1 = 'Y'
            #     else:
            #         p1 = 'N'
            #     data = frac_downMonoPR(lxn[1],3,1)
            #     if data:
            #         p2 = 'Y'
            #     else:
            #         p2 = 'N'
                
            #     # print(p1, p2)
            #     if p1 != p2:
            #         print('#############' + str(i))
            
            