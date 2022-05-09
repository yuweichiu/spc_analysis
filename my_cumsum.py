# -*- coding: utf-8 -*-
# """
# Created on 2021/07/25
# @author: Ivan Y.W.Chiu
# """

import pandas as pd
import numpy as np
import os, sys, time, random, logging
from datetime import datetime
from typing import Tuple, Dict, Any
from scipy.stats import chi2  # @manual
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
def _get_llr(ts: np.ndarray, change_meta: Dict[str, Any]):
    # """
    # Calculate the log likelihood ratio
    # """
    mu0: float = change_meta["mu0"]
    mu1: float = change_meta["mu1"]
    changepoint: int = change_meta["changepoint"]
    scale = np.sqrt(
        (
            np.sum((ts[: (changepoint + 1)] - mu0) ** 2)
            + np.sum((ts[(changepoint + 1) :] - mu1) ** 2)
        )
        / (len(ts) - 2)
    )
    mu_tilde, sigma_tilde = np.mean(ts), np.std(ts)

    if scale == 0:
        scale = sigma_tilde

    llr = -2 * (
        _log_llr(ts[: (changepoint + 1)], mu_tilde, sigma_tilde, mu0, scale)
        + _log_llr(ts[(changepoint + 1) :], mu_tilde, sigma_tilde, mu1, scale)
    )
    return llr

def _log_llr(
    x: np.ndarray, mu0: float, sigma0: float, mu1: float, sigma1: float
) -> float:
    # """Helper function to calculate log likelihood ratio.

    # This function calculate the log likelihood ratio of two Gaussian
    # distribution log(l(0)/l(1)).

    # Args:
    #     x: the data value.
    #     mu0: mean of model 0.
    #     sigma0: std of model 0.
    #     mu1: mean of model 1.
    #     sigma1: std of model 1.

    # Returns:
    #     the value of log likelihood ratio.
    # """

    return np.sum(
        np.log(sigma1 / sigma0)
        + 0.5 * (((x - mu1) / sigma1) ** 2 - ((x - mu0) / sigma0) ** 2)
    )


# %%
n = 0
interest_window = [150, 299]
start_point = 250
max_iter = 10
# change_direction = ['increase', 'decrease']
change_direction = ['increase']

if change_direction == 'increase':
    changepoint_func = np.argmin
else:
    changepoint_func = np.argmax

# use the middle point as initial change point to estimate mu0 and mu1
if interest_window is not None:
    ts_int = ts[interest_window[0] : interest_window[1]]
else:
    ts_int = ts

if start_point is None:
    cusum_ts = np.cumsum(ts_int - np.mean(ts_int))
    changepoint = min(changepoint_func(cusum_ts), len(ts_int) - 2)
else:
    changepoint = start_point

mu0, mu1 = None, None
while n < max_iter:
    n += 1
    mu0 = np.mean(ts_int[: changepoint+1])
    mu1 = np.mean(ts_int[changepoint+1: ])
    mean = (mu0 + mu1) / 2
    cusum_ts = np.cumsum(ts_int - mean)
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
    llr_int = _get_llr(
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
