# -*- coding: utf-8 -*-
# """
# Created on 2021/07/25
# @author: Ivan Y.W.Chiu
# """

from cProfile import label
import pandas as pd
import numpy as np
import os, sys, time, random
from datetime import datetime
from typing import Tuple
import matplotlib as mpl
mpl.use('Qt5Agg')
from matplotlib import pyplot as plt
plt.ion()
from spc_data_generator import SPCDataConfig, SPCDataGenerator
from spc_chart_plotter import SpcPlotter
from src.anomaly_maker import SimpleOneThingMeanMismatchMaker, SimpleOneThingMeanKShiftMaker
from src.anomaly_detector import SimpleOneThingMeanMismatchDetector

mpl.rcParams.update({"font.size": "10",
                     'lines.linewidth': 1,
                     'lines.markersize': 4})


cfg = SPCDataConfig(
    '2020/11/17 00:00:00.0', '2020/12/18 00:00:00.0', 
    stage_id='stageE11', ctype='MEAN', cnt=300, data_order=0.01, sl=0.03, cl=0.025, target=0)
SPC = SPCDataGenerator(cfg)
SPC.gen()
spc_df = SPC.df.copy()

# %%
mismatch_maker = SimpleOneThingMeanKShiftMaker(spc_df, 'global', 0.333)
new_spc_df = mismatch_maker.gen()

# %%
Plotter = SpcPlotter(spc_df, figsize=(10, 4.5))
Plotter.plot()
fig, ax = Plotter.fig, Plotter.ax

Plotter = SpcPlotter(new_spc_df, figsize=(10, 4.5))
Plotter.plot()
fig1, ax1 = Plotter.fig, Plotter.ax

# %%
# import packages
from kats.consts import TimeSeriesData, TimeSeriesIterator
from kats.detectors.cusum_detection import CUSUMDetector

# %%
# detect increase
df = new_spc_df[['Data_Time', 'Value']]
df.rename(columns={'Data_Time': 'time', 'Value': 'value'}, inplace=True)

timeseries = TimeSeriesData(
    df.loc[:,['time','value']]
)
detector = CUSUMDetector(timeseries)

# run detector
# delta_std_ratio: means how much times std you want to detect for |mu0-mu1|.
change_points = detector.detector(change_directions=["increase"], delta_std_ratio=0.5)

# plot the results
fig3 = plt.figure()
plt.xticks(rotation=45)
detector.plot(change_points)
plt.show()

# %%
#CUMSUM
df['value_residule'] = df['value']-df['value'].mean()
df['value_cumsum'] = np.cumsum(df['value_residule'])

fig4, ax4 = plt.subplots(1, 1)
ax4.plot(df.index, df['value'], 'b', label='value')
ax4.plot(df.index, df['value_residule'], 'y', label='residule')
ax4.plot(df.index, np.ones(len(df))*df['value'].mean(), color='k', linestyle='--', label='mean')
ax4.legend()
fig4.savefig('output/value_residule.png', dpi=300)

# %%
ax4.plot(df.index, df['value_cumsum'], label='cusum')
ax4.legend()
fig4.savefig('output/value_cusum.png', dpi=300)

# %%
