# -*- coding: utf-8 -*-
"""
Created on 2020/12/19 下午 01:26
@author: Ivan Y.W.Chiu
"""

import pandas as pd
import numpy as np
import os, sys, time, random
from datetime import datetime

# %%
class SPCDataConfig:
    def __init__(self, start_date_str, end_date_str, ctype, cnt, data_order, sl, cl, target):
        self.start_date_str = start_date_str
        self.end_date_str = end_date_str
        self.ctype = ctype
        self.cnt = cnt
        self.data_order = data_order
        self.sl = sl
        self.cl = cl
        self.target = target
        self.dt_fmt = '%Y/%m/%d %H:%M:%S.%f'
        self.start_date_dt = datetime.strptime(self.start_date_str, self.dt_fmt)
        self.end_date_dt = datetime.strptime(self.end_date_str, self.dt_fmt)
        self.start_date_num = int(self.start_date_dt.timestamp())
        self.end_date_num = int(self.end_date_dt.timestamp())


class DataTimeGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        time_series_num = np.random.randint(self.cfg.start_date_num, self.cfg.end_date_num, self.cfg.cnt)
        time_series = [datetime.fromtimestamp(x) for x in time_series_num]
        return time_series


class RawDataGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        values = np.random.randn(self.cfg.cnt) * self.cfg.data_order
        if self.cfg.ctype == 'RANGE':
            values = np.abs(values)

        return values


class SpecGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        SPEC = self.cfg.sl
        USL = np.ones(self.cfg.cnt) * SPEC
        if self.cfg.ctype == 'RANGE':
            LSL = np.zeros(self.cfg.cnt)
        else:
            LSL = np.ones(self.cfg.cnt) * -SPEC

        return USL, LSL


class ControlLimitGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        CL = self.cfg.cl
        UCL = np.ones(self.cfg.cnt) * CL
        if self.cfg.ctype == 'RANGE':
            LCL = np.zeros(self.cfg.cnt)
        else:
            LCL = np.ones(self.cfg.cnt) * -CL

        return UCL, LCL


class TargetGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        TARGET = np.ones(self.cfg.cnt) * self.cfg.target
        return TARGET


class LotIdGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        LETTER = ['U', 'X', 'T', 'G']
        lot6 = ['L7{0:s}{1:03d}'.format(LETTER[random.randint(0, 3)], random.randint(1, 999)) for x in range(self.cfg.cnt)]
        lot2 = ['{0:02d}'.format(random.randint(1, 99)) for x in range(self.cfg.cnt)]
        itemid = ['{0:02d}'.format(random.randint(1, 25)) for x in range(self.cfg.cnt)]
        lot_info = pd.DataFrame({
            'Lot6': lot6, 'Lot2': lot2, 'Item2': itemid
        }, columns=['Lot6', 'Lot2', 'Item2'])
        lot_info["Lot_ID"] = lot_info['Lot6'].str.cat(lot_info['Lot2'].values, sep='.')
        lot_info["Item_ID"] = lot_info['Lot6'].str.cat(lot_info['Item2'].values, sep='.')
        return lot_info


class SPCDataGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        TS = DataTimeGenerator(self.cfg)
        RD = RawDataGenerator(self.cfg)
        SL = SpecGenerator(self.cfg)
        CL = ControlLimitGenerator(self.cfg)
        TG = TargetGenerator(self.cfg)
        LI = LotIdGenerator(self.cfg)

        time_series = TS.gen()
        values = RD.gen()
        USL, LSL = SL.gen()
        UCL, LCL = CL.gen()
        target = TG.gen()
        lot_info = LI.gen()

        self.df = pd.DataFrame({
            'Data_Time': time_series,
            'Lot_ID': lot_info['Lot_ID'].values,
            'Item_ID': lot_info['Item_ID'].values,
            'Value': values,
            'Target': target,
            'USL': USL,
            'UCL': UCL,
            'LCL': LCL,
            'LSL': LSL,
        })
        self.df = self.df[['Data_Time', 'Lot_ID', 'Item_ID', 'Value', 'Target', 'USL', 'UCL', 'LCL', 'LSL']]

        return self.df


# cfg = SPCDataConfig('2020/11/17 00:00:00.0', '2020/12/18 00:00:00.0', ctype='MEAN', cnt=300, data_order=0.1, sl=0.3, cl=0.2, target=0)
# SPC = SPCDataGenerator(cfg)
# SPC.gen()
# spc_df = SPC.df

# %%
# spc_df = spc_gen('2020/11/17 00:00:00.0', '2020/12/18 00:00:00.0', cnt=data_cnt, ctype=chart_type, spec=3*0.1, tighten_ratio=1.0)


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
