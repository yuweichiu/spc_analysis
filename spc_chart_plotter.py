# -*- coding: utf-8 -*-
"""
Created on 2020/12/19 下午 01:26
@author: Ivan Y.W.Chiu
"""

import pandas as pd
import numpy as np
import os, sys, time, random
from datetime import datetime
from spc_data_generator import spc_gen
import matplotlib as mpl
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as RT
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

line_color = [46/255, 117/255, 182/255]

# %%
################################
# Generate demo SPC chart
################################
mpl.rcParams.update({"font.size": "8",
                     'lines.linewidth': 1,
                     'lines.markersize': 4})
data_cnt = 300
stage_name = 'STAGE001_2'
groupname = '3PI03STAGE001'
chartname = 'WEIGHT'
chart_type = 'MEAN'
chart_descpt = 'STAGE001_22000.000'
spc_df = spc_gen('2020/11/17 00:00:00.0', '2020/12/18 00:00:00.0', cnt=data_cnt, ctype=chart_type, spec=3*0.1)
spc_df['Point_Values'] = spc_df['Point_Values'] * 0.1
spc_df.reset_index(inplace=True)
keylot = spc_df['Lot_ID'].values.tolist()[random.randint(int(data_cnt*0.8), data_cnt-1)]

# %%
################################
# SPC Plotter:
################################
class SPC_plotter:
    line_color = [46/255, 117/255, 182/255]
    
    def __init__(self, df, stage_name, groupname, chartname, chart_type, chart_descpt, hl_lots, figsize=(16, 5), layout_rect=[0, 0, 0.97, 1]):
        self.df = df
        self.group_name = groupname
        self.chart_name = chartname
        self.chart_type = chart_type
        self.chart_descpt = chart_descpt
        self.stage_name = stage_name
        self.hl_lots = hl_lots
        self.figsize = figsize
        self.layout_rect = layout_rect
        self.fig, self.ax = plt.subplots(1, 1, figsize=self.figsize)

    def gen_xticklabels(self):
        if len(self.df) <= 20:
            self.tick_step = 1
        elif len(self.df) > 20 and len(self.df) <= 50:
            self.tick_step = 2
        elif len(self.df) > 50 and len(self.df) <= 100:
            self.tick_step = 3
        elif len(self.df) > 100 and len(self.df) <= 300:
            self.tick_step = 4
        else:
            self.tick_step = 5

        self.tick_id = np.arange(0, len(self.df), self.tick_step)
        self.x_label = [datetime.strftime(x, '%y/%m/%d-%H:%M:%S') for x in self.df['Data_Time'][self.tick_id]]

    def plot_value(self):
        self.ax.plot(self.df['index'], self.df['Point_Values'], '-o', color=line_color)

    def set_title(self):
        self.ax.set_title('Group: [{0:s}][{1:s}][{2:s}][{3:s}]'.format(
            self.group_name, self.chart_name, self.chart_type, self.chart_descpt
            ),fontsize=8, loc='left')

    def set_xyaxis(self):
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

    def set_xrange(self):
        self.ax.set_xlim([-len(self.df)*0.01, (len(self.df)-1)*1.01])

    def set_xaxis(self):
        self.ax.set_xticks(self.tick_id)
        self.ax.set_xticklabels(self.x_label, rotation=90)

    def set_yrange(self):
        self.ylim = self.ax.get_ylim()
        if (self.df['Point_Values'].max() >= self.df['USL'].values[-1]*1.5) and\
            (self.df['Point_Values'].max() < self.df['USL'].values[-1]*2):
            self.ax.set_ylim(-self.df['Point_Values'].max() * 1.05, self.df['Point_Values'].max() * 1.05)
        elif (self.df['Point_Values'].max() >= self.df['USL'].values[-1]*2):
            self.ax.set_ylim(-self.df['USL'].values[-1] * 2, self.df['USL'].values[-1] * 2)
            self.df['Point_Values'].loc[self.df[self.df['Point_Values'] >= self.df['USL'].values[-1] * 2]] = self.df['USL'].values[-1] * 1.95

        if (self.chart_type == 'MEAN') or (self.chart_type == 'RANGE'):
            if (self.df['Point_Values'].min() <= self.df['LSL'].values[-1]*1.5) and\
                (self.df['Point_Values'].min() > self.df['LSL'].values[-1]*2):
                self.ax.set_ylim(self.df['Point_Values'].min() * 1.05, -self.df['Point_Values'].min() * 1.05)
            elif (self.df['Point_Values'].min() <= self.df['LSL'].values[-1]*2):
                self.ax.set_ylim(self.df['LSL'].values[-1] * 2, -self.df['LSL'].values[-1] * 2)
                self.df['Point_Values'].loc[self.df[self.df['Point_Values'] <= self.df['LSL'].values[-1] * 2]] = self.df['LSL'].values[-1] * 1.95
            
    def set_yaxis(self):
        ax.tick_params(axis='y', which='minor', direction="out")
        pass

    def plot_target(self):
        if self.chart_type == 'MEAN':
            self.ax.plot(self.df['index'], np.zeros(len(self.df)), ':', color=[84 / 255, 130 / 255, 53 / 255])
            self.ax.text((len(self.df) - 1) * 1.01, 0, 'Target', color=[84 / 255, 130 / 255, 53 / 255], va='center')

    def plot_cl(self):
        self.ax.plot(self.df['index'], self.df['UCL'], '--', color='r')
        self.ax.text((len(self.df)-1)*1.01, self.df['UCL'].values[-1], 'UCL', color='r', va='center')
        self.ax.plot(self.df['index'], self.df['LCL'], '--', color='r')
        self.ax.text((len(self.df) - 1) * 1.01, self.df['LCL'].values[-1], 'LCL', color='r', va='center')

    def plot_sl(self):
        pass

    def plot_ooc(self):
        pass

    def hightlight_lot(self):
        pass

    def plot(self):
        self.gen_xticklabels()
        self.plot_value()
        self.set_title()
        self.set_xyaxis()
        self.set_xrange()
        self.set_xaxis()
        self.plot_target()
        self.plot_cl()
        self.plot_sl()
        self.plot_ooc()
        self.hightlight_lot()
        plt.tight_layout(rect=self.layout_rect)
        plt.show()

Plotter = SPC_plotter(spc_df, stage_name, groupname, chartname, chart_type, chart_descpt, keylot)
Plotter.plot()


def plot_spc(spc_df, stage_name, groupname, chartname, chart_type, chart_descpt, keylot):
    keylot_id = spc_df[spc_df['Lot_ID'] == keylot].index.tolist()

    # if len(spc_df) <= 20:
    #     tick_step = 1
    # elif len(spc_df) > 20 and len(spc_df) <= 50:
    #     tick_step = 2
    # elif len(spc_df) > 50 and len(spc_df) <= 100:
    #     tick_step = 3
    # elif len(spc_df) > 100 and len(spc_df) <= 300:
    #     tick_step = 4
    # else:
    #     tick_step = 5

    # tick_id = np.arange(0, len(spc_df), tick_step)
    # x_label = [datetime.strftime(x, '%y/%m/%d-%H:%M:%S') for x in spc_df['Data_Time'][tick_id]]

    # fig, ax = plt.subplots(1, 1, figsize=(16, 4.5))
    # ax.plot(spc_df['index'], spc_df['UCL'], '--', color='r')
    # ax.text((len(spc_df)-1)*1.01, spc_df['UCL'].values[-1], 'UCL', color='r', va='center')
    # ax.plot(spc_df['index'], spc_df['LCL'], '--', color='r')
    # ax.text((len(spc_df) - 1) * 1.01, spc_df['LCL'].values[-1], 'LCL', color='r', va='center')

    # if chart_type != 'RANGE':
    #     ax.plot(spc_df['index'], np.zeros(len(spc_df)), ':', color=[84 / 255, 130 / 255, 53 / 255])
    #     ax.text((len(spc_df) - 1) * 1.01, 0, 'Target', color=[84 / 255, 130 / 255, 53 / 255], va='center')

    if (spc_df['Point_Values'].max() > spc_df['USL'].values[-1]*0.75) or\
            (spc_df['UCL'].values[-1] / spc_df['USL'].values[-1] >= 0.75) or\
            (spc_df['LCL'].values[-1] / spc_df['LSL'].values[-1] >= 0.75):
        ax.plot(spc_df['index'], spc_df['USL'], '-', color='r')
        if spc_df['UCL'].values[-1] / spc_df['USL'].values[-1] <= 0.95:
            ax.text((len(spc_df) - 1) * 1.01, spc_df['USL'].values[-1], 'USL', color='r', va='center')
        if chart_type != 'RANGE':
            ax.plot(spc_df['index'], spc_df['LSL'], '-', color='r')
            if spc_df['LCL'].values[-1] / spc_df['LSL'].values[-1] <= 0.95:
                ax.text((len(spc_df) - 1) * 1.01, spc_df['LSL'].values[-1], 'LSL', color='r', va='center')
    else:
        pass

    ooc_index = list(spc_df[(spc_df['Point_Values'] >= spc_df['UCL']) | (spc_df['Point_Values'] <= spc_df['LCL'])].index)
    # ylim = ax.get_ylim()
    # if (spc_df['Point_Values'].max() >= spc_df['USL'].values[-1]*1.5) and\
    #     (spc_df['Point_Values'].max() < spc_df['USL'].values[-1]*2):
    #     ax.set_ylim(-spc_df['Point_Values'].max() * 1.05, spc_df['Point_Values'].max() * 1.05)
    # elif (spc_df['Point_Values'].max() >= spc_df['USL'].values[-1]*2):
    #     ax.set_ylim(-spc_df['USL'].values[-1] * 2, spc_df['USL'].values[-1] * 2)
    #     spc_df['Point_Values'].loc[spc_df[spc_df['Point_Values'] >= spc_df['USL'].values[-1] * 2]] = spc_df['USL'].values[-1] * 1.95

    # if (spc_df['Point_Values'].min() <= spc_df['LSL'].values[-1]*1.5) and\
    #     (spc_df['Point_Values'].min() > spc_df['LSL'].values[-1]*2):
    #     ax.set_ylim(spc_df['Point_Values'].min() * 1.05, -spc_df['Point_Values'].min() * 1.05)
    # elif (spc_df['Point_Values'].min() <= spc_df['LSL'].values[-1]*2):
    #     ax.set_ylim(spc_df['LSL'].values[-1] * 2, -spc_df['LSL'].values[-1] * 2)
    #     spc_df['Point_Values'].loc[spc_df[spc_df['Point_Values'] <= spc_df['LSL'].values[-1] * 2]] = spc_df['LSL'].values[-1] * 1.95

    # ax.plot(spc_df['index'], spc_df['Point_Values'], '-o', color=line_color)
    ax.plot(ooc_index, spc_df['Point_Values'].loc[ooc_index], 'ro')
    # ax.set_title('Group: [{0:s}][{1:s}][{2:s}][{3:s}]'.format(groupname, chartname, chart_type, chart_descpt),
    #             fontsize=8, loc='left')
    # # ax.minorticks_on()
    # ax.tick_params(axis='y', which='minor', direction="out")
    ylim = ax.get_ylim()
    if keylot_id:
        for kl in keylot_id:
            _ = ax.add_patch(RT((kl-0.5, ylim[0]), 1, ylim[1] - ylim[0], facecolor='r', alpha=0.3))
    # ax.set_xlim([-len(spc_df)*0.01, (len(spc_df)-1)*1.01])
    # ax.xaxis.set_major_locator(MultipleLocator(tick_step))
    # ax.yaxis.set_minor_locator(AutoMinorLocator())
    # ax.tick_params(which="minor", axis="y", direction="inout")
    # xticks = [x.get_text() for x in ax.xaxis.get_ticklabels()][1:-1]
    # ax.set_xticks(tick_id)
    # ax.set_xticklabels(x_label, rotation=90)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # plt.tight_layout(rect=[0, 0, 0.97, 1])
    # plt.show()
    return fig, ax

def plot_spc(spc_df, stage_name, groupname, chartname, chart_type, chart_descpt, keylot):
    keylot_id = spc_df[spc_df['Lot_ID'] == keylot].index.tolist()

    if len(spc_df) <= 20:
        tick_step = 1
    elif len(spc_df) > 20 and len(spc_df) <= 50:
        tick_step = 2
    elif len(spc_df) > 50 and len(spc_df) <= 100:
        tick_step = 3
    elif len(spc_df) > 100 and len(spc_df) <= 300:
        tick_step = 4
    else:
        tick_step = 5

    tick_id = np.arange(0, len(spc_df), tick_step)
    x_label = [datetime.strftime(x, '%y/%m/%d-%H:%M:%S') for x in spc_df['Data_Time'][tick_id]]

    fig, ax = plt.subplots(1, 1, figsize=(16, 4.5))
    ax.plot(spc_df['index'], spc_df['UCL'], '--', color='r')
    ax.text((len(spc_df)-1)*1.01, spc_df['UCL'].values[-1], 'UCL', color='r', va='center')
    ax.plot(spc_df['index'], spc_df['LCL'], '--', color='r')
    ax.text((len(spc_df) - 1) * 1.01, spc_df['LCL'].values[-1], 'LCL', color='r', va='center')

    if chart_type != 'RANGE':
        ax.plot(spc_df['index'], np.zeros(len(spc_df)), ':', color=[84 / 255, 130 / 255, 53 / 255])
        ax.text((len(spc_df) - 1) * 1.01, 0, 'Target', color=[84 / 255, 130 / 255, 53 / 255], va='center')

    if (spc_df['Point_Values'].max() > spc_df['USL'].values[-1]*0.75) or\
            (spc_df['UCL'].values[-1] / spc_df['USL'].values[-1] >= 0.75) or\
            (spc_df['LCL'].values[-1] / spc_df['LSL'].values[-1] >= 0.75):
        ax.plot(spc_df['index'], spc_df['USL'], '-', color='r')
        if spc_df['UCL'].values[-1] / spc_df['USL'].values[-1] <= 0.95:
            ax.text((len(spc_df) - 1) * 1.01, spc_df['USL'].values[-1], 'USL', color='r', va='center')
        if chart_type != 'RANGE':
            ax.plot(spc_df['index'], spc_df['LSL'], '-', color='r')
            if spc_df['LCL'].values[-1] / spc_df['LSL'].values[-1] <= 0.95:
                ax.text((len(spc_df) - 1) * 1.01, spc_df['LSL'].values[-1], 'LSL', color='r', va='center')
    else:
        pass

    ooc_index = list(spc_df[(spc_df['Point_Values'] >= spc_df['UCL']) | (spc_df['Point_Values'] <= spc_df['LCL'])].index)
    ylim = ax.get_ylim()
    if (spc_df['Point_Values'].max() >= spc_df['USL'].values[-1]*1.5) and\
        (spc_df['Point_Values'].max() < spc_df['USL'].values[-1]*2):
        ax.set_ylim(-spc_df['Point_Values'].max() * 1.05, spc_df['Point_Values'].max() * 1.05)
    elif (spc_df['Point_Values'].max() >= spc_df['USL'].values[-1]*2):
        ax.set_ylim(-spc_df['USL'].values[-1] * 2, spc_df['USL'].values[-1] * 2)
        spc_df['Point_Values'].loc[spc_df[spc_df['Point_Values'] >= spc_df['USL'].values[-1] * 2]] = spc_df['USL'].values[-1] * 1.95

    if (spc_df['Point_Values'].min() <= spc_df['LSL'].values[-1]*1.5) and\
        (spc_df['Point_Values'].min() > spc_df['LSL'].values[-1]*2):
        ax.set_ylim(spc_df['Point_Values'].min() * 1.05, -spc_df['Point_Values'].min() * 1.05)
    elif (spc_df['Point_Values'].min() <= spc_df['LSL'].values[-1]*2):
        ax.set_ylim(spc_df['LSL'].values[-1] * 2, -spc_df['LSL'].values[-1] * 2)
        spc_df['Point_Values'].loc[spc_df[spc_df['Point_Values'] <= spc_df['LSL'].values[-1] * 2]] = spc_df['LSL'].values[-1] * 1.95

    ax.plot(spc_df['index'], spc_df['Point_Values'], '-o', color=line_color)
    ax.plot(ooc_index, spc_df['Point_Values'].loc[ooc_index], 'ro')
    ax.set_title('Group: [{0:s}][{1:s}][{2:s}][{3:s}]'.format(groupname, chartname, chart_type, chart_descpt),
                fontsize=8, loc='left')
    # ax.minorticks_on()
    ax.tick_params(axis='y', which='minor', direction="out")
    ylim = ax.get_ylim()
    if keylot_id:
        for kl in keylot_id:
            _ = ax.add_patch(RT((kl-0.5, ylim[0]), 1, ylim[1] - ylim[0], facecolor='r', alpha=0.3))
    ax.set_xlim([-len(spc_df)*0.01, (len(spc_df)-1)*1.01])
    # ax.xaxis.set_major_locator(MultipleLocator(tick_step))
    # ax.yaxis.set_minor_locator(AutoMinorLocator())
    # ax.tick_params(which="minor", axis="y", direction="inout")
    # xticks = [x.get_text() for x in ax.xaxis.get_ticklabels()][1:-1]
    ax.set_xticks(tick_id)
    ax.set_xticklabels(x_label, rotation=90)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout(rect=[0, 0, 0.97, 1])
    plt.show()
    return fig, ax
# %%
fig, ax = plot_spc(spc_df, stage_name, groupname, chartname, chart_type, chart_descpt, keylot)
fig_name = '#'.join(['chart', keylot, stage_name, groupname, chartname, chart_type])
fig.savefig('./output/{}.png'.format(fig_name), dpi=150)
