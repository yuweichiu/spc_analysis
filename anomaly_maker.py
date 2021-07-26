# -*- coding: utf-8 -*-
# """
# Created on 2021/07/25
# @author: Ivan Y.W.Chiu
# """

import pandas as pd
import numpy as np
import os, sys, time, random
from datetime import datetime
import matplotlib as mpl
from spc_data_generator import SPCDataConfig, SPCDataGenerator
from spc_chart_plotter import SpcPlotter


class SimpleOneThingMeanMismatchMaker:
    def __init__(self, df, col, mismatch_ratio, item=None) -> None:
        self.df = df
        self.col = col
        self.mismatch_ratio = mismatch_ratio
        self.item = item
        self.select_item()

    def select_item(self):
        unique_item = self.df[self.col].unique().tolist()
        unique_count = len(unique_item)

        if self.item is None:
            mismatch_item_index = random.randint(0, unique_count-1)
            self.item = unique_item[mismatch_item_index]
        else:
            if self.item not in unique_item:
                raise ValueError("Item {} is found in the column {}.".format(self.item, self.col))

    def get_cl(self, df):
        ucl, lcl = df['UCL'].values[-1], df['LCL'].values[-1]
        return ucl, lcl

    def cal_tolerance(self, df, chart_type, ucl, lcl):
        if chart_type == 'MEAN':
            return (ucl-lcl)/2
        else:
            mean = df['Value'].mean()
            return ucl - mean

    def gen(self):
        ucl, lcl = self.get_cl(self.df)
        chart_type = self.df['Chart_Type'].tolist()[-1]
        tolerance = self.cal_tolerance(self.df, chart_type, ucl, lcl)

        selected_row_index = self.df[self.df[self.col] == self.item].index
        selected_value = self.df['Value'].loc[selected_row_index]
        selected_value = selected_value + tolerance*self.mismatch_ratio
        self.df['Value'].loc[selected_row_index] = selected_value
        return self.df


cfg = SPCDataConfig(
    '2020/11/17 00:00:00.0', '2020/12/18 00:00:00.0', 
    stage_id='stageE11', ctype='MEAN', cnt=300, data_order=0.1, sl=0.3, cl=0.2, target=0)
SPC = SPCDataGenerator(cfg)
SPC.gen()
spc_df = SPC.df

mismatch_maker = SimpleOneThingMeanMismatchMaker(spc_df, 'Eqp_M', 0.5)
new_spc_df = mismatch_maker.gen()

# %%
Plotter = SpcPlotter(spc_df, by_tool_col='Eqp_M', figsize=(10, 4.5), layout_rect=[0, 0, 1.5, 1])
Plotter.plot()
fig, ax = Plotter.fig, Plotter.ax

# %%
