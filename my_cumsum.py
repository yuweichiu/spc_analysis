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
# mpl.use('Qt5Agg')
from matplotlib import pyplot as plt
plt.ion()

mpl.rcParams.update({"font.size": "10",
                     'lines.linewidth': 1,
                     'lines.markersize': 4})

df = pd.read_csv("data/treding_data_01.csv")

# %%
ts = df['Value'].values
mean = np.mean(ts)
cusum_ts = np.cumsum(ts-mean)
# %%
fig, ax = plt.subplots(1, 1)
ax.plot(ts)
# ax.plot(mean, "-")
ax.hlines(mean, 0, 300, color=[50/255, 50/255, 50/255])
ax2 = ax.twinx()
ax2.plot(cusum_ts, 'r')

# %%
n = 0
start_point = 150
max_iter = 10
change_direction = 'upper'

if change_direction == 'upper':
    changepoint_func = np.argmin
else:
    changepoint_func = np.argmax

if start_point is None:
    cusum_ts = np.cumsum(ts - np.mean(ts))
    changepoint = min(changepoint_func(cusum_ts), len(ts) - 2)
else:
    changepoint = start_point

mu0, mu1 = None, None
while n < max_iter:
    n += 1
    mu0 = np.mean(ts[: changepoint+1])
    mu1 = np.mean(ts[changepoint+1: ])
    mean = (mu0 + mu1) / 2
    cusum_ts = np.cumsum(ts - mean)
    next_changepoint = max(1, min(changepoint_func(cusum_ts), len(ts)-2))
    if next_changepoint == changepoint:
        break
    changepoint = next_changepoint

if n == max_iter:
    logging.info("Max iteration reached and no stable changepoint found.")
    stable_changepoint = False
else:
    stable_changepoint = True

# llr in interest window
if interest_window is None:
    llr_int = np.inf
    pval_int = np.NaN
    delta_int = None
else:
    llr_int = self._get_llr(
        ts_int,
        {"mu0": mu0, "mu1": mu1, "changepoint": changepoint},
    )
    pval_int = 1 - chi2.cdf(llr_int, 2)
    delta_int = mu1 - mu0
    changepoint += interest_window[0]

# full time changepoint and mean
mu0 = np.mean(ts[: (changepoint + 1)])
mu1 = np.mean(ts[(changepoint + 1) :])

# %%
