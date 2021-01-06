# -*- coding: utf-8 -*-
"""
Created on 2020/12/19 下午 01:26
@author: Ivan Y.W.Chiu
"""

import pandas as pd
import numpy as np
import os, sys, time, random
from datetime import datetime


def spc_gen(start_date, end_date, ctype='mean', cnt=300, spec=3, tighten_ratio=0.9, target=28):
    # start_date = '2020/11/17 00:00:00.0'
    # end_date = '2020/12/18 00:00:00.0'

    start_datetime = datetime.strptime(start_date, '%Y/%m/%d %H:%M:%S.%f')
    end_datetime = datetime.strptime(end_date, '%Y/%m/%d %H:%M:%S.%f')

    start_date_num = int(start_datetime.timestamp())
    end_date_num = int(end_datetime.timestamp())

    time_series_num = np.random.randint(start_date_num, end_date_num, cnt)
    time_series = [datetime.fromtimestamp(x) for x in time_series_num]

    point_value = np.random.randn(cnt)
    if ctype == 'RANGE':
        point_value = np.abs(point_value)

    SPEC = spec
    USL = np.ones(cnt)*SPEC
    LSL = np.ones(cnt)*-SPEC
    UCL = np.ones(cnt)*SPEC
    LCL = np.ones(cnt)*-SPEC

    tighten_point = random.randint(int(cnt*0.25), int(cnt*0.75))
    tighten_ratio = tighten_ratio
    UCL[tighten_point:] = SPEC*tighten_ratio
    LCL[tighten_point:] = -SPEC*tighten_ratio

    TARGET = np.ones(cnt)*target

    LETTER = ['U', 'X', 'T', 'G']
    lot6 = ['L7{0:s}{1:03d}'.format(LETTER[random.randint(0, 3)], random.randint(1, 999)) for x in range(cnt)]
    lot2 = ['{0:02d}'.format(random.randint(1, 99)) for x in range(cnt)]
    itemid = ['{0:02d}'.format(random.randint(1, 25)) for x in range(cnt)]
    lot_info = pd.DataFrame({
        'Lot6': lot6, 'Lot2': lot2, 'Item2': itemid
    }, columns=['Lot6', 'Lot2', 'Item2'])
    lot_info["Lot_ID"] = lot_info['Lot6'].str.cat(lot_info['Lot2'].values, sep='.')
    lot_info["Item_ID"] = lot_info['Lot6'].str.cat(lot_info['Item2'].values, sep='.')

    return pd.DataFrame({
        'Data_Time': time_series,
        'Lot_ID': lot_info['Lot_ID'].values,
        'Item_ID': lot_info['Item_ID'].values,
        'Point_Values': point_value,
        'Target': TARGET,
        'USL': USL,
        'UCL': UCL,
        'LCL': LCL,
        'LSL': LSL,
    }, columns=['Data_Time', 'Lot_ID', 'Item_ID', 'Point_Values', 'Target', 'USL', 'UCL', 'LCL', 'LSL'])