# -*- coding: utf-8 -*-
# """
# Created on 2020/12/19 下午 01:26
# @author: Ivan Y.W.Chiu
# """

import pandas as pd
import numpy as np
import os, sys, time, random
from datetime import datetime

# %%
class SPCDataConfig:
    def __init__(self, start_date_str, end_date_str, stage_id, ctype, cnt, data_order, sl, cl, target):
        self.start_date_str = start_date_str
        self.end_date_str = end_date_str
        self.stage_id = stage_id
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
        self.lookup_tb = pd.read_csv("param\stage_layer_table.csv")


class DataTimeGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        time_series_num = np.random.randint(self.cfg.start_date_num, self.cfg.end_date_num, self.cfg.cnt)
        time_series_num = np.sort(time_series_num)
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
        LETTER = ['W', 'X', 'Y', 'Z']
        lotid = ['A21{0:s}{0:s}{1:03d}'.format(LETTER[random.randint(0, 3)], random.randint(1, 999)) for i in range(self.cfg.cnt)]
        itemid = ['{0:02d}'.format(random.randint(1, 25)) for i in range(self.cfg.cnt)]
        lot_info = pd.DataFrame({
            'Lot': lotid, 'Item2': itemid
        }, columns=['Lot', 'Item2'])
        lot_info["Lot_ID"] = lot_info['Lot']
        lot_info["Item_ID"] = lot_info['Lot'].str.cat(lot_info['Item2'].values, sep='.')
        return lot_info

class SEqpIdGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        LETTER = ['X', 'Y', 'Z']
        SERIAL = ['001', '003', '005']
        eqpid = ['{0:s}SE{1:s}'.format(LETTER[random.randint(0, 2)], SERIAL[random.randint(0, 2)]) for i in range(self.cfg.cnt)]
        return eqpid

class CEqpIdGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self): 
        LETTER = ['Y', 'Z']
        SERIAL = ['B', 'C']
        eqpid = ['{0:s}CO{1:s}'.format(LETTER[random.randint(0, 1)], SERIAL[random.randint(0, 1)]) for i in range(self.cfg.cnt)]
        return eqpid

class MEqpIdGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self): 
        LETTER = ['W', 'X']
        SERIAL = ['20', '33']
        eqpid = ['{0:s}CD{1:s}'.format(LETTER[random.randint(0, 1)], SERIAL[random.randint(0, 1)]) for i in range(self.cfg.cnt)]
        return eqpid
        
class StageIdGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        stg_id = self.cfg.stage_id
        stage_id_list = [stg_id for i in range(self.cfg.cnt)]
        return stage_id_list


class LayerIdGenerator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.lookup_tb = self.cfg.lookup_tb
    
    def gen(self):
        layer_id = self.lookup_tb[self.lookup_tb['Stage_ID'] == self.cfg.stage_id]['Layer_ID'].tolist()[0]
        EDITION = ['1', '2', '3']
        layer_id_list = ['{0:s}-{1:s}'.format(layer_id, EDITION[random.randint(0, 2)]) for i in range(self.cfg.cnt)]
        return layer_id_list


class MaterialGenerator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.lookup_tb = self.cfg.lookup_tb
    
    def gen(self):
        material_id = self.lookup_tb[self.lookup_tb['Stage_ID'] == self.cfg.stage_id]['Material_ID'].tolist()[0]
        material_id_list = [material_id for i in range(self.cfg.cnt)]
        return material_id_list


class ProdGroupGenerator:
    def __init__(self, cfg):
        self.cfg = cfg

    def gen(self):
        PROD = ['A', 'B', 'C', 'D']
        prod_id_list = ['Prod{0:s}'.format(PROD[random.randint(0, 3)]) for i in range(self.cfg.cnt)]
        return prod_id_list


class EqpSUnit1Generator:
    def __init__(self, cfg) -> None:
        self.cfg = cfg

    def gen(self):
        SU1_ID = ['01', '02', '03', '04']
        sunit1_list = ['s#U1-{0:s}'.format(SU1_ID[random.randint(0, 3)]) for i in range(self.cfg.cnt)]
        return sunit1_list


class EqpSUnit2Generator:
    def __init__(self, cfg) -> None:
        self.cfg = cfg

    def gen(self):
        SU2_ID = ['01', '02', '03', '04']
        sunit2_list = ['s#U2-{0:s}'.format(SU2_ID[random.randint(0, 3)]) for i in range(self.cfg.cnt)]
        return sunit2_list


class EqpSRecipeGenerator:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.lookup_tb = self.cfg.lookup_tb

    def gen(self):
        layer_id = self.lookup_tb[self.lookup_tb['Stage_ID'] == self.cfg.stage_id]['Layer_ID'].tolist()[0]
        RCP_EDITION = ['H', 'I', 'J']

        s_recipe_list = ['SRCP-{0:s}-{1:s}'.format(layer_id, RCP_EDITION[random.randint(0, 2)]) for i in range(self.cfg.cnt)]
        return s_recipe_list


class EqpSSubRecipeGenerator:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.lookup_tb = self.cfg.lookup_tb

    def gen(self):
        layer_id = self.lookup_tb[self.lookup_tb['Stage_ID'] == self.cfg.stage_id]['Layer_ID'].tolist()[0]
        RCP_EDITION = ['001', '002']
        switch_position = random.randint(int(self.cfg.cnt*0.8), int(self.cfg.cnt))
        s_sub_recipe_list = []
        for i in range(self.cfg.cnt):
            if i < switch_position:
                s_sub_recipe_list.append('SRCPSUB-{0:s}-{1:s}'.format(layer_id, RCP_EDITION[0]))
            else:
                s_sub_recipe_list.append('SRCPSUB-{0:s}-{1:s}'.format(layer_id, RCP_EDITION[1]))
        return s_sub_recipe_list


# class STimeCostGenerator:
#     def __init__(self, cfg) -> None:
#         self.cfg = cfg
    
#     def gen(self):
#         np.random.randn(self.cfg.cnt)


class EqpMRecipeGenerator:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.lookup_tb = self.cfg.lookup_tb

    def gen(self):
        layer_id = self.lookup_tb[self.lookup_tb['Stage_ID'] == self.cfg.stage_id]['Layer_ID'].tolist()[0]
        RCP_EDITION = ['.003', '.004', '.005']

        s_recipe_list = ['MRCP-{0:s}-{1:s}'.format(layer_id, RCP_EDITION[random.randint(0, 2)]) for i in range(self.cfg.cnt)]
        return s_recipe_list


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
        SEQP = SEqpIdGenerator(self.cfg)
        CEQP = CEqpIdGenerator(self.cfg)
        MEQP = MEqpIdGenerator(self.cfg)
        STAGE = StageIdGenerator(self.cfg)
        LAYER = LayerIdGenerator(self.cfg)
        MATERIAL = MaterialGenerator(self.cfg)
        PROD = ProdGroupGenerator(self.cfg)
        SU1 = EqpSUnit1Generator(self.cfg)
        SU2 = EqpSUnit2Generator(self.cfg)
        SEQPRCP = EqpSRecipeGenerator(self.cfg)
        SEQPSUBRCP = EqpSSubRecipeGenerator(self.cfg)
        MEQPRCP = EqpMRecipeGenerator(self.cfg)

        # TODO:
        # s_param 

        time_series = TS.gen()
        values = RD.gen()
        USL, LSL = SL.gen()
        UCL, LCL = CL.gen()
        target = TG.gen()
        lot_info = LI.gen()
        seqp = SEQP.gen()
        ceqp = CEQP.gen()
        meqp = MEQP.gen()
        stg = STAGE.gen()
        layer = LAYER.gen()
        material = MATERIAL.gen()
        prod = PROD.gen()
        su1 = SU1.gen()
        su2 = SU2.gen()
        seqprcp = SEQPRCP.gen()
        seqpsubrcp = SEQPSUBRCP.gen()
        meqprcp = MEQPRCP.gen()

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
            'Stage_ID': stg,
            'Layer_ID': layer,
            'Prod_ID': prod,
            'Eqp_S': seqp,
            'Eqp_S_Unit1': su1,
            'Eqp_S_Unit2': su2,
            'S_Recipe': seqprcp,
            'S_SubRecipe': seqpsubrcp,
            'Eqp_C': ceqp,
            'Material_ID': material,
            'Eqp_M': meqp,
            'M_Recipe': meqprcp,
        })

        self.df = self.df[[
            'Data_Time', 'Lot_ID', 'Item_ID', 'Value', 
            'Target', 'USL', 'UCL', 'LCL', 'LSL', 
            'Stage_ID', 'Layer_ID', 'Prod_ID', 'Eqp_S', 'Eqp_S_Unit1', 'Eqp_S_Unit2',
            'S_Recipe', 'S_SubRecipe',
            'Eqp_C', 'Material_ID', 'Eqp_M', 'M_Recipe']]

        return self.df


cfg = SPCDataConfig(
    '2020/11/17 00:00:00.0', '2020/12/18 00:00:00.0', 
    stage_id='stageE11', ctype='MEAN', cnt=300, data_order=0.1, sl=0.3, cl=0.2, target=0)
SPC = SPCDataGenerator(cfg)
SPC.gen()
spc_df = SPC.df
