# -*- coding: utf-8 -*-
# """
# Created on 2021/07/25
# @author: Ivan Y.W.Chiu
# """

import pandas as pd
import numpy as np
import os, sys, time, random
from datetime import datetime
from typing import Tuple
import matplotlib as mpl
mpl.use('Qt5Agg')
from matplotlib import pyplot as plt
from spc_data_generator import SPCDataConfig, SPCDataGenerator
from spc_chart_plotter import SpcPlotter
from src.anomaly_maker import SimpleOneThingMeanMismatchMaker
from src.anomaly_detector import SimpleOneThingMeanMismatchDetector


cfg = SPCDataConfig(
    '2020/11/17 00:00:00.0', '2020/12/18 00:00:00.0', 
    stage_id='stageE11', ctype='MEAN', cnt=300, data_order=0.1, sl=0.3, cl=0.25, target=0)
SPC = SPCDataGenerator(cfg)
SPC.gen()
spc_df = SPC.df

mismatch_maker = SimpleOneThingMeanMismatchMaker(spc_df, 'Eqp_M', 0.3)
new_spc_df = mismatch_maker.gen()

# %%
Plotter = SpcPlotter(spc_df, by_tool_col='Eqp_M', figsize=(10, 4.5), layout_rect=[0, 0, 1.5, 1])
Plotter.plot()
fig, ax = Plotter.fig, Plotter.ax

simple_detector = SimpleOneThingMeanMismatchDetector(spc_df, "Eqp_M", criteria=0.33)
mismatch_index, mismatch_ratio = simple_detector.detect()

# %%