from pts.dataset.repository.datasets import get_dataset, dataset_recipes
from pts.dataset.utils import to_pandas
import numpy as np
import pandas as pd
from pts.dataset import ListDataset
import torch
from pts.model.simple_feedforward import SimpleFeedForwardEstimator
import pickle
import json
import random

def group_exchangerate_cv(num_ts=10, num_groups=14, context_length=15, prediction_length=10, file_name='default'):
    dataset = get_dataset("exchange_rate")
    len_sample = context_length + prediction_length
    dataset_group = [[] for i in range(num_groups)]
    train_full_data = []
    test_full_data  = []
    ret = dict()
    train_it = iter(dataset.train)
    test_it  = iter(dataset.test)
    #num_ts = int(dataset.metadata.feat_static_cat[0].cardinality)
    date_checkpoint = [
        '1994-01-01',
        '1998-01-01',
        '2002-01-01'
    ]
    for i in range(num_ts):
        train_entry = next(train_it)
        unsplit_ts    = train_entry['target']
        unsplit_start = train_entry['start']
        for ts_sample_start in range(0, len(unsplit_ts)-len_sample, prediction_length):
            for j, date_ckpt in enumerate(date_checkpoint):
                if unsplit_start < pd.Timestamp(date_ckpt):
                    sid = j
                    break
                elif unsplit_start > pd.Timestamp(date_checkpoint[-1]):
                    sid = len(date_checkpoint)
                    break
            gid = i*4+sid
            ts_slice = unsplit_ts[ts_sample_start:ts_sample_start+len_sample]
            train_full_data.append(
                {'target': ts_slice, 'start': unsplit_start, 'feat_static_cat': train_entry['feat_static_cat']}
            )
            dataset_group[gid].append(
                {'target': ts_slice, 'start': unsplit_start, 'feat_static_cat': train_entry['feat_static_cat']}
            )
            unsplit_start += pd.Timedelta('1D')*prediction_length
    #get ready the test data
    for i in range(int(num_ts*0.2)):
        test_entry = next(test_it)
        unsplit_ts    = test_entry['target']
        unsplit_start = test_entry['start']
        for ts_sample_start in range(0, len(unsplit_ts)-len_sample, prediction_length):
            ts_slice = unsplit_ts[ts_sample_start:ts_sample_start+len_sample]
            test_full_data.append(
                {'target': ts_slice, 'start': unsplit_start, 'feat_static_cat': test_entry['feat_static_cat']}
            )
    print('total number of training examples: ', len(train_full_data))
    ret['group_ratio'] = [len(i)/len(train_full_data) for i in dataset_group]
    print('ratio for each group: ', ret['group_ratio'])
    random.shuffle(train_full_data)
    ret['whole_data'] = ListDataset(
        train_full_data,
        freq=dataset.metadata.freq
    )
    random.shuffle(test_full_data)
    ret['val_data'] = ListDataset(
        test_full_data,
        freq=dataset.metadata.freq
    )
    group_data_list = []
    for group in dataset_group:
        random.shuffle(group)
        group_data_list.append(
            ListDataset(
                group,
                freq=dataset.metadata.freq
            )
        )
    ret['group_data'] = group_data_list
    with open('../dataset/'+file_name+'_data.csv', 'wb') as output:
        pickle.dump(ret, output)
    return True
