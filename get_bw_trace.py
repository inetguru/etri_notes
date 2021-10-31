#!/usr/bin/env python

"""get_bwtrace_fcc.py: Generate/Sample a bandwith trace from the FCC's measurement trace ."""

__author__      = "Kim, Jong-Deok"
__copyright__   = "Copyright 2021, ETRI"

import numpy as np
import pandas as pd
import argparse
import os
from itertools import chain

def parse_fcc_trace(csv_path, target_url, nmin_samples) :
    n_count=0
    use_col = ['unit_id','dtime', 'target', 'fetch_time', 'bytes_total', 'bytes_sec']
    freader = pd.read_csv(csv_path, chunksize=10000, usecols=use_col)
    f_trace = pd.DataFrame()
    use_col.remove('target')
    #max_id = 0  # max('unit_id') = 47073261, # of records = 1294 * 10000

    for dfchunk in freader :
        #f_dfchunk = dfchunk[dfchunk['target']=='http://m.imdb.com/help/']
        f_dfchunk = dfchunk[dfchunk['target']==target_url]
        f_trace = f_trace.append(f_dfchunk[use_col], ignore_index=True)
        n_count += 1
        if n_count > 20000 :
            break

    xdf = f_trace.groupby(['unit_id']).count()['dtime'].to_frame('count')
    xdf['avg_bw'] = f_trace.groupby(['unit_id']).mean()['bytes_sec'] * 8 / 1000000
    xdf['std_bw'] = f_trace.groupby(['unit_id']).std()['bytes_sec'] * 8 / 1000000

    xdf[xdf['count'] >= nmin_samples].to_csv('ftrace.csv')
    print(n_count * 10000)
    return n_count

def generate_bw_trace(csv_path, target_url) :
    df_ids = pd.DataFrame(np.array([[8887,39876861,5521],[5787,10924,10239]]), index=[5,10], columns=['min','max','median'])
    use_col = ['unit_id','dtime', 'target', 'fetch_time', 'bytes_total', 'bytes_sec']
    freader = pd.read_csv(csv_path, chunksize=10000, usecols=use_col)
    f_trace = pd.DataFrame()    
    use_col.remove('target')
    n_count = 0 

    list_ids = list(chain.from_iterable(df_ids.values))

    for dfchunk in freader :
        filter_cond = (dfchunk.target == target_url) & dfchunk['unit_id'].isin(list_ids)
        f_trace = f_trace.append(dfchunk.loc[filter_cond][use_col], ignore_index = True)
        n_count += 1
        if n_count > 2000 :
            break

    for bw in df_ids.index :
        for col in df_ids.columns :
            filename = 'bwtrace_' + str(bw) +'Mbps_' + col
            f_trace[f_trace['unit_id'] == df_ids.at[bw, col]].to_csv(filename)
    #print(f_trace.groupby(['unit_id'])

    #df = pd.read_csv('ftrace.csv')
    return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default=os.getcwd())
    parser.add_argument('--csv_file', type=str, default='curr_webget.csv')
    parser.add_argument('--target_url', type=str, default='http://edition.cnn.com/')
    parser.add_argument('--num_min_samples', type=int, default=100)
    parser.add_argument('--target_mbps', type=float, default='5.0')
    args = parser.parse_args()

    csv_path = os.path.join(args.data_dir, args.csv_file)
    #traces = parse_fcc_trace(csv_path, args.target_url, args.num_min_samples)
    traces = generate_bw_trace(csv_path, args.target_url)